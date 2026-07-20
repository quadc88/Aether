"""Read-only, safe workflow tracing across Aether repair records."""
from pathlib import Path
import json
import uuid
import yaml

from aether.action.code_reviewer import get_code_review
from aether.action.repair_planner import get_repair_plan
from aether.action.repair_bridge_selector import get_repair_bridge_selection, list_repair_bridge_selections
from aether.action.review_bridge import get_review_bridge_record, list_review_bridge_records
from aether.action.self_modification_cycle import get_self_modification_session, list_self_modification_sessions
from aether.action.patch_proposal import get_patch_proposal
from aether.action.patch_review import get_patch_review, list_patch_reviews
from aether.action.patch_apply import get_patch_apply, list_patch_applies
from aether.action.patch_rollback import get_patch_rollback, list_patch_rollbacks
from aether.action.mutation_log import record_mutation
from aether.memory.timeline.recorder import record_event
from aether.memory.graph.store import add_edge
from aether.time.clock import get_timezone, now_iso

ROOT_TYPES = {"code_review", "repair_plan", "repair_bridge_selection", "review_bridge", "self_modification_session", "patch_proposal", "patch_apply", "patch_rollback"}
SENSITIVE_TERMS = ("c:/aetherdata", "backup_path", "pre_rollback", "original_excerpt", "proposed_excerpt", "patch_text", "diff_preview", "token", "secret", "password", "private_key", "api_key")


def load_aether_config(path="config/aether.yaml"):
    config_path = Path(path)
    return yaml.safe_load(config_path.read_text(encoding="utf-8")) or {} if config_path.exists() else {}


def get_repair_workflow_dir():
    return Path(load_aether_config().get("paths", {}).get("private_dir", "private")) / "repair_workflows"


def get_repair_workflow_path():
    return get_repair_workflow_dir() / "repair_workflow_reports.json"


def load_repair_workflow_reports():
    path = get_repair_workflow_path()
    try:
        data = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    except json.JSONDecodeError:
        data = {}
    timestamp = now_iso()
    data.setdefault("type", "repair_workflow_reports")
    data.setdefault("version", "0.1.0")
    data.setdefault("created", timestamp)
    data.setdefault("updated", data["created"])
    data.setdefault("timezone", get_timezone())
    data.setdefault("reports", [])
    return data


def save_repair_workflow_reports(data):
    path = get_repair_workflow_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    data["updated"] = now_iso()
    data["timezone"] = get_timezone()
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def _safe_text(value, limit=280):
    text = str(value or "")[:limit]
    return "[redacted]" if any(term in text.lower().replace("\\", "/") for term in SENSITIVE_TERMS) else text


def _safe_metadata(metadata):
    if not isinstance(metadata, dict):
        return {}
    return {str(key)[:80]: _safe_text(value, 160) for key, value in metadata.items() if not any(term in str(key).lower() for term in SENSITIVE_TERMS)}


def _record(stage, record, identifier, target_path=None, summary=None, next_step=None):
    if not record:
        return None
    return {"stage": stage, "id": identifier, "status": _safe_text(record.get("status", "unknown"), 80), "target_path": _safe_text(target_path or record.get("target_path") or record.get("normalized_path"), 300) or None, "safe_summary": _safe_text(summary or record.get("summary") or f"{stage.replace('_', ' ')} record is available."), "next_step": _safe_text(next_step or record.get("next_recommended_step") or "Inspect the next guarded workflow step.")}


def _find_first(items, **matches):
    return next((item for item in items if all(item.get(key) == value for key, value in matches.items())), None)


def _audit_report(report):
    warnings = []
    try:
        from aether.core.runtime import runtime
        runtime.working_memory.add_event(role="aether", content=f"Repair workflow traced: {report['root_type']}:{report['root_id']}", event_type="repair_workflow_traced", metadata={key: report.get(key) for key in ("id", "root_type", "root_id", "current_stage", "safety_state", "next_recommended_step")} | {"report_id": report["id"]})
    except Exception:
        warnings.append("Working Memory audit was unavailable.")
    try:
        record_event("repair_workflow", f"Repair workflow traced: {report['root_type']}", f"Aether traced repair workflow {report['id']} from {report['root_type']}:{report['root_id']}.", "normal")
    except Exception:
        warnings.append("Timeline audit was unavailable.")
    try:
        add_edge("Aether", "traced_repair_workflow", report["id"])
        add_edge(report["id"], "has_root", report["root_id"])
        add_edge(report["id"], "has_current_stage", report["current_stage"])
        add_edge(report["id"], "has_safety_state", report["safety_state"])
        for item in report["chain"]:
            if item.get("id"):
                add_edge(report["id"], "includes_stage", item["id"])
    except Exception:
        warnings.append("Graph audit was unavailable.")
    try:
        record_mutation("manual_note", "Repair workflow traced", "Aether traced a repair workflow across existing safe repair records.", milestone="Milestone 30 — Repair Workflow Tracker / Pipeline Status", risk_level="low", status=report["status"], reversible=False, rollback_available=False)
    except Exception:
        warnings.append("Mutation Log integration was unavailable.")
    return warnings


def trace_repair_workflow(root_type, root_id, metadata=None):
    timestamp = now_iso()
    report = {"id": f"repair_workflow_{uuid.uuid4().hex}", "created": timestamp, "updated": timestamp, "timezone": get_timezone(), "status": "tracked", "root_type": root_type, "root_id": root_id, "code_review_id": None, "repair_plan_id": None, "repair_bridge_selection_id": None, "review_bridge_id": None, "self_modification_session_id": None, "patch_proposal_id": None, "patch_review_id": None, "patch_apply_id": None, "patch_rollback_id": None, "current_stage": "unknown", "current_stage_status": "unknown", "next_recommended_step": "Inspect missing workflow links.", "safety_state": "unknown", "target_path": None, "finding_id": None, "chain": [], "missing_links": [], "warnings": [], "metadata": _safe_metadata(metadata)}
    if root_type not in ROOT_TYPES:
        report.update({"status": "blocked", "current_stage": "blocked", "current_stage_status": "blocked", "safety_state": "blocked", "next_recommended_step": "Use a supported repair workflow root type."})
        report["warnings"].append("Unsupported workflow root type.")
    else:
        records = {"code_review": get_code_review(root_id) if root_type == "code_review" else None, "repair_plan": get_repair_plan(root_id) if root_type == "repair_plan" else None, "repair_bridge_selection": get_repair_bridge_selection(root_id) if root_type == "repair_bridge_selection" else None, "review_bridge": get_review_bridge_record(root_id) if root_type == "review_bridge" else None, "self_modification_session": get_self_modification_session(root_id) if root_type == "self_modification_session" else None, "patch_proposal": get_patch_proposal(root_id) if root_type == "patch_proposal" else None, "patch_apply": get_patch_apply(root_id) if root_type == "patch_apply" else None, "patch_rollback": get_patch_rollback(root_id) if root_type == "patch_rollback" else None}
        if not records[root_type]:
            report.update({"status": "blocked", "current_stage": "blocked", "current_stage_status": "blocked", "safety_state": "blocked", "next_recommended_step": "Inspect the supplied workflow root identifier."})
            report["warnings"].append("Workflow root record was not found.")
        else:
            selection = records["repair_bridge_selection"]
            bridge = records["review_bridge"]
            session = records["self_modification_session"]
            proposal = records["patch_proposal"]
            apply = records["patch_apply"]
            rollback = records["patch_rollback"]
            plan = records["repair_plan"]
            review = None
            if selection:
                plan = get_repair_plan(selection.get("repair_plan_id")); bridge = get_review_bridge_record(selection.get("bridge_record_id")); session = get_self_modification_session(selection.get("session_id")); proposal = get_patch_proposal(selection.get("proposal_id"))
            if bridge:
                session = session or get_self_modification_session(bridge.get("session_id")); proposal = proposal or get_patch_proposal(bridge.get("proposal_id")); records["code_review"] = records["code_review"] or get_code_review(bridge.get("review_report_id"))
            if plan:
                records["code_review"] = records["code_review"] or get_code_review(plan.get("review_report_id"))
            if session:
                proposal = proposal or get_patch_proposal(session.get("proposal_id")); review = get_patch_review(session.get("review_id")); apply = apply or get_patch_apply(session.get("apply_id")); rollback = rollback or get_patch_rollback(session.get("rollback_id"))
            if apply:
                proposal = proposal or get_patch_proposal(apply.get("proposal_id"))
            if rollback:
                apply = apply or get_patch_apply(rollback.get("apply_id")); proposal = proposal or get_patch_proposal((apply or {}).get("proposal_id"))
            if proposal:
                review = review or _find_first(list_patch_reviews(proposal.get("id"), 100), proposal_id=proposal.get("id"))
                apply = apply or _find_first(list_patch_applies(proposal.get("id"), 100), proposal_id=proposal.get("id"))
                session = session or _find_first(list_self_modification_sessions(limit=1000), proposal_id=proposal.get("id"))
            if apply:
                rollback = rollback or _find_first(list_patch_rollbacks(apply.get("id"), 100), apply_id=apply.get("id"))
            if session:
                bridge = bridge or _find_first(list_review_bridge_records(limit=1000), session_id=session.get("id"))
            if bridge:
                selection = selection or _find_first(list_repair_bridge_selections(limit=1000), bridge_record_id=bridge.get("id"))
            if selection:
                plan = plan or get_repair_plan(selection.get("repair_plan_id"))
            if plan:
                records["code_review"] = records["code_review"] or get_code_review(plan.get("review_report_id"))
            ordered = [("code_review", records["code_review"]), ("repair_plan", plan), ("repair_bridge_selection", selection), ("review_bridge", bridge), ("self_modification_session", session), ("patch_proposal", proposal), ("patch_review", review), ("patch_apply", apply), ("patch_rollback", rollback)]
            for stage, item in ordered:
                if item:
                    identifier = item.get("id")
                    report[f"{stage}_id"] = identifier
                    report["chain"].append(_record(stage, item, identifier))
            report["finding_id"] = (selection or bridge or {}).get("finding_id")
            report["target_path"] = _safe_text((proposal or session or bridge or selection or {}).get("target_path") or (proposal or session or bridge or selection or {}).get("normalized_path"), 300) or None
            direct_links = {"repair_bridge_selection": ["repair_plan_id", "bridge_record_id", "session_id", "proposal_id"], "review_bridge": ["review_report_id", "session_id", "proposal_id"], "self_modification_session": ["proposal_id"], "patch_apply": ["proposal_id"], "patch_rollback": ["apply_id"]}
            root_record = records[root_type]
            for field in direct_links.get(root_type, []):
                if root_record.get(field) and not any(item.get("id") == root_record.get(field) for item in report["chain"]):
                    report["missing_links"].append(field)
            if rollback and rollback.get("status") == "success":
                report.update({"current_stage": "patch_rollback", "current_stage_status": rollback.get("status"), "safety_state": "rolled_back", "next_recommended_step": "Review mutation log and decide whether a new proposal is needed."})
            elif apply and apply.get("status") == "success" and apply.get("applied"):
                report.update({"current_stage": "patch_apply", "current_stage_status": apply.get("status"), "safety_state": "applied_with_rollback_available" if apply.get("backup_path") else "unknown", "next_recommended_step": "Verify behavior or rollback if needed."})
            elif review and review.get("proposal_status_after") == "approved":
                report.update({"current_stage": "patch_review", "current_stage_status": review.get("status"), "safety_state": "safe_pending_dry_run", "next_recommended_step": "Run dry-run apply before real apply."})
            elif proposal:
                report.update({"current_stage": "patch_proposal", "current_stage_status": proposal.get("status"), "safety_state": "safe_pending_human_review", "next_recommended_step": "Human should review the generated patch proposal."})
            elif session:
                report.update({"current_stage": "self_modification_session", "current_stage_status": session.get("status"), "safety_state": "safe_pending_human_review", "next_recommended_step": "Human should review the generated patch proposal."})
            elif report["missing_links"]:
                report.update({"status": "incomplete", "current_stage": "unknown", "current_stage_status": "incomplete", "safety_state": "incomplete", "next_recommended_step": "Inspect missing workflow links."})
            else:
                latest = report["chain"][-1]
                report.update({"current_stage": latest["stage"], "current_stage_status": latest["status"], "safety_state": "safe_pending_human_review", "next_recommended_step": "Inspect the next guarded workflow step."})
    report["warnings"] += _audit_report(report)
    data = load_repair_workflow_reports(); data["reports"].append(report); save_repair_workflow_reports(data)
    return report


def get_repair_workflow_report(report_id):
    return next((report for report in load_repair_workflow_reports()["reports"] if report["id"] == report_id), None)


def list_repair_workflow_reports(status=None, root_type=None, limit=50):
    reports = [report for report in load_repair_workflow_reports()["reports"] if (not status or report["status"] == status) and (not root_type or report["root_type"] == root_type)]
    return reports[-max(0, limit):][::-1]


def repair_workflow_status():
    data = load_repair_workflow_reports()
    return {"report_count": len(data["reports"]), "created": data["created"], "updated": data["updated"], "timezone": data["timezone"]}


def summarize_repair_workflow(report_id):
    report = get_repair_workflow_report(report_id)
    if not report:
        return None
    return {key: report.get(key) for key in ("id", "status", "root_type", "root_id", "code_review_id", "repair_plan_id", "repair_bridge_selection_id", "review_bridge_id", "self_modification_session_id", "patch_proposal_id", "patch_review_id", "patch_apply_id", "patch_rollback_id", "current_stage", "current_stage_status", "safety_state", "next_recommended_step", "target_path", "finding_id", "chain", "missing_links", "warnings")}
