"""Sanitized human-readable exports for read-only repair workflow reports."""
from pathlib import Path
import json
import uuid
import yaml

from aether.action.repair_workflow_tracker import get_repair_workflow_report, list_repair_workflow_reports
from aether.action.mutation_log import record_mutation
from aether.memory.timeline.recorder import record_event
from aether.memory.graph.store import add_edge
from aether.time.clock import now_iso

PUBLIC_DIR = Path("docs/history/repair_workflows")
SENSITIVE_TERMS = ("c:/aetherdata", "backup_path", "pre_rollback_backup_path", "original_excerpt", "proposed_excerpt", "metadata", "token", "secret", "password", "api_key", "private_key", "id_rsa", "id_ed25519", ".env")


def load_aether_config(path="config/aether.yaml"):
    config_path = Path(path)
    return yaml.safe_load(config_path.read_text(encoding="utf-8")) or {} if config_path.exists() else {}


def get_public_workflow_report_dir():
    return PUBLIC_DIR


def get_private_workflow_export_dir():
    return Path(load_aether_config().get("paths", {}).get("private_dir", "private")) / "repair_workflow_exports"


def sanitize_target_path(path):
    if not path:
        return None
    text = str(path).replace("\\", "/")
    prefix = "C:/Aether/"
    if text.lower().startswith(prefix.lower()):
        return text[len(prefix):]
    return None


def shorten_id(value, keep=12):
    if not value:
        return None
    text = str(value)
    return f"{text[:keep]}..." if len(text) > keep else text


def _safe_text(value, limit=500):
    text = str(value or "")[:limit]
    return "[redacted]" if any(term in text.lower().replace("\\", "/") for term in SENSITIVE_TERMS) else text


def sanitize_workflow_report_for_public(report):
    if not report:
        return None
    safe_chain = []
    for item in report.get("chain", []):
        safe_chain.append({"stage": _safe_text(item.get("stage"), 80), "id": shorten_id(item.get("id")), "status": _safe_text(item.get("status"), 80), "target_path": sanitize_target_path(item.get("target_path")), "safe_summary": _safe_text(item.get("safe_summary")), "next_step": _safe_text(item.get("next_step"))})
    return {"id": shorten_id(report.get("id")), "created": _safe_text(report.get("created"), 32), "status": _safe_text(report.get("status"), 80), "root_type": _safe_text(report.get("root_type"), 80), "root_id": shorten_id(report.get("root_id")), "current_stage": _safe_text(report.get("current_stage"), 80), "current_stage_status": _safe_text(report.get("current_stage_status"), 80), "safety_state": _safe_text(report.get("safety_state"), 100), "next_recommended_step": _safe_text(report.get("next_recommended_step")), "target_path": sanitize_target_path(report.get("target_path")), "finding_id": shorten_id(report.get("finding_id")), "missing_links_count": len(report.get("missing_links", [])), "warnings_count": len(report.get("warnings", [])), "chain": safe_chain}


def _markdown_for_report(report):
    safe = sanitize_workflow_report_for_public(report)
    if not safe:
        return "# Repair Workflow Report\n\nWorkflow report was not found.\n"
    lines = ["# Repair Workflow Report", "", "## Summary", "", f"- Report: {safe['id']}", f"- Created: {safe['created']}", f"- Root: {safe['root_type']}: {safe['root_id']}", f"- Status: {safe['status']}", f"- Current stage: {safe['current_stage']}", f"- Safety state: {safe['safety_state']}", f"- Next step: {safe['next_recommended_step']}"]
    if safe["target_path"]:
        lines.append(f"- Target: {safe['target_path']}")
    if safe["finding_id"]:
        lines.append(f"- Finding: {safe['finding_id']}")
    lines += [f"- Missing links: {safe['missing_links_count']}", f"- Warnings: {safe['warnings_count']}", "", "## Chain", ""]
    for number, item in enumerate(safe["chain"], 1):
        target = f" — {item['target_path']}" if item["target_path"] else ""
        lines.append(f"{number}. {item['stage'].replace('_', ' ').title()} — {item['id']} ({item['status']}){target}")
    lines += ["", "## Safety Notes", "", "- Raw excerpts are excluded.", "- Backup paths are excluded.", "- Private runtime paths are excluded.", "- This report is a sanitized public summary.", ""]
    return "\n".join(lines)


def build_workflow_report_markdown(report_id):
    return _markdown_for_report(get_repair_workflow_report(report_id))


def build_workflow_index_markdown(limit=100):
    reports = [sanitize_workflow_report_for_public(report) for report in list_repair_workflow_reports(limit=limit)]
    lines = ["# Aether Repair Workflow Dashboard", "", "This dashboard is generated from sanitized repair workflow tracker reports.", "", "## Summary", "", f"- Generated: {now_iso()}", f"- Reports included: {len(reports)}", "", "## Workflows", "", "| Created | Report | Root | Current Stage | Safety State | Next Step |", "|---|---|---|---|---|---|"]
    for report in reports:
        lines.append(f"| {report['created'][:10]} | {report['id']} | {report['root_type']}:{report['root_id']} | {report['current_stage']} | {report['safety_state']} | {report['next_recommended_step']} |")
    return "\n".join(lines) + "\n"


def _public_output_path(output_path):
    root = PUBLIC_DIR.resolve()
    path = Path(output_path).resolve()
    if path != root and not path.is_relative_to(root):
        return None
    return path


def _audit_export(result, export_type):
    warnings = []
    try:
        from aether.core.runtime import runtime
        runtime.working_memory.add_event(role="aether", content=f"Repair workflow export: {export_type}", event_type="repair_workflow_exported", metadata={key: result.get(key) for key in ("id", "report_id", "output_path", "public", "status")} | {"export_type": export_type})
    except Exception:
        warnings.append("Working Memory audit was unavailable.")
    try:
        record_event("repair_workflow_export", f"Repair workflow export: {export_type}", f"Aether exported a repair workflow {export_type}.", "high" if result.get("public") else "normal")
    except Exception:
        warnings.append("Timeline audit was unavailable.")
    try:
        add_edge("Aether", "exported_repair_workflow", result["id"])
        add_edge(result["id"], "has_type", export_type)
        add_edge(result["id"], "has_status", result["status"])
        if result.get("report_id"):
            add_edge(result["id"], "documents_workflow", result["report_id"])
        if result.get("public") and result.get("project_relative_path"):
            add_edge(result["id"], "writes_file", result["project_relative_path"])
    except Exception:
        warnings.append("Graph audit was unavailable.")
    if result.get("public") and result.get("status") == "success":
        try:
            record_mutation("manual_note", "Repair workflow report exported", "Aether exported a sanitized human-readable repair workflow report.", milestone="Milestone 31 — Workflow Report Export / Human Repair Dashboard", target_path=result.get("project_relative_path"), risk_level="medium", status=result["status"], reversible=True, rollback_available=False)
        except Exception:
            warnings.append("Mutation Log integration was unavailable.")
    return warnings


def _result(export_type, report_id=None, public=True):
    return {"id": f"repair_workflow_export_{uuid.uuid4().hex}", "export_type": export_type, "report_id": report_id, "status": "failed", "public": public, "output_path": None, "project_relative_path": None, "warnings": []}


def export_workflow_report(report_id, output_dir="docs/history/repair_workflows", metadata=None):
    result = _result("report", report_id, True)
    report = get_repair_workflow_report(report_id)
    output = _public_output_path(Path(output_dir) / f"{report_id}.md")
    if not report:
        result["warnings"].append("Workflow report was not found.")
    elif not output:
        result["warnings"].append("Public output path must remain under docs/history/repair_workflows.")
    else:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(_markdown_for_report(report), encoding="utf-8")
        result.update({"status": "success", "output_path": str(output), "project_relative_path": output.relative_to(Path.cwd()).as_posix()})
    result["warnings"] += _audit_export(result, "report")
    return result


def export_workflow_index(output_path="docs/history/repair_workflows/INDEX.md", limit=100, metadata=None):
    result = _result("index", None, True)
    output = _public_output_path(output_path)
    if not output:
        result["warnings"].append("Public output path must remain under docs/history/repair_workflows.")
    else:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(build_workflow_index_markdown(limit), encoding="utf-8")
        result.update({"status": "success", "output_path": str(output), "project_relative_path": output.relative_to(Path.cwd()).as_posix()})
    result["warnings"] += _audit_export(result, "index")
    return result


def export_private_workflow_report(report_id, metadata=None):
    result = _result("private", report_id, False)
    report = get_repair_workflow_report(report_id)
    if not report:
        result["warnings"].append("Workflow report was not found.")
    else:
        output = get_private_workflow_export_dir() / f"{report_id}.json"
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(sanitize_workflow_report_for_public(report), indent=2, ensure_ascii=False), encoding="utf-8")
        result.update({"status": "success", "output_path": str(output)})
    result["warnings"] += _audit_export(result, "private")
    return result


def repair_workflow_export_status():
    return {"public_report_dir": str(get_public_workflow_report_dir()), "private_export_dir": str(get_private_workflow_export_dir()), "policy": "Public exports exclude private runtime paths, metadata, excerpts, backups, credentials, and secrets."}
