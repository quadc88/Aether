"""Non-mutating intake records for possible future guided repair planning."""
from pathlib import Path
import json
import uuid
import yaml

from aether.action.repair_guidance_engine import create_repair_guidance, get_repair_guidance_record
from aether.time.clock import get_timezone, now_iso


DECISIONS = {"allow_repair_planning", "pause_for_clarification", "reject_repair_request", "require_human_investigation"}
SENSITIVE = ("c:/aetherdata", "backup", "original_excerpt", "proposed_excerpt", "diff", "token", "secret", "password", "api_key", "private_key", "id_rsa", "id_ed25519", ".env")
PUBLIC_UNSAFE = SENSITIVE + ("key",)


def load_aether_config(path="config/aether.yaml"):
    config_path = Path(path)
    return yaml.safe_load(config_path.read_text(encoding="utf-8")) or {} if config_path.exists() else {}


def get_guided_repair_intake_dir():
    return Path(load_aether_config().get("paths", {}).get("private_dir", "private")) / "repair_intake"


def get_guided_repair_intake_path():
    return get_guided_repair_intake_dir() / "guided_repair_intake_records.json"


def get_public_repair_intake_dir():
    return Path("docs/history/repair_intake")


def get_public_repair_intake_index_path():
    return get_public_repair_intake_dir() / "INDEX.md"


def load_guided_repair_intake_records():
    path = get_guided_repair_intake_path()
    try:
        data = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    except json.JSONDecodeError:
        data = {}
    timestamp = now_iso()
    data.setdefault("type", "guided_repair_intake_records")
    data.setdefault("version", "0.1.0")
    data.setdefault("created", timestamp)
    data.setdefault("updated", data["created"])
    data.setdefault("timezone", get_timezone())
    data.setdefault("records", [])
    return data


def save_guided_repair_intake_records(data):
    path = get_guided_repair_intake_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    data["updated"] = now_iso()
    data["timezone"] = get_timezone()
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def sanitize_target_path(path):
    value = str(path or "").replace("\\", "/")
    prefix = "C:/Aether/"
    return value[len(prefix):] if value.lower().startswith(prefix.lower()) else (value if value and ":" not in value else None)


def shorten_id(value, keep=12):
    return f"{str(value)[:keep]}…" if value and len(str(value)) > keep else value


def _sanitize_public_value(value):
    if isinstance(value, str):
        return "[redacted]" if any(term in value.lower() for term in PUBLIC_UNSAFE) else value
    if isinstance(value, list):
        return [_sanitize_public_value(item) for item in value]
    return value


def sanitize_intake_record_for_public(record):
    keys = ("id", "created", "status", "request_type", "requested_scope", "target_path", "guidance_record_id", "guidance_decision", "inferred_risk_category", "recommended_gate_chain", "required_safety_checks", "human_review_required", "intake_decision", "planning_allowed", "recommended_next_action", "public_report_path", "public_index_path")
    result = {key: record.get(key) for key in keys}
    result["id"] = shorten_id(result["id"])
    result["guidance_record_id"] = shorten_id(result["guidance_record_id"])
    result["target_path"] = sanitize_target_path(result["target_path"])
    for key, value in tuple(result.items()):
        result[key] = _sanitize_public_value(value)
    result["warnings_count"] = len(record.get("warnings", []))
    return result


def _save(record):
    data = load_guided_repair_intake_records()
    data["records"] = [item for item in data["records"] if item["id"] != record["id"]]
    data["records"].append(record)
    save_guided_repair_intake_records(data)
    return record


def get_guided_repair_intake_record(record_id):
    return next((item for item in load_guided_repair_intake_records()["records"] if item["id"] == record_id), None)


def list_guided_repair_intake_records(status=None, planning_allowed=None, target_path=None, limit=50):
    records = load_guided_repair_intake_records()["records"]
    return [item for item in records if (not status or item.get("status") == status) and (planning_allowed is None or item.get("planning_allowed") == planning_allowed) and (not target_path or item.get("target_path") == target_path)][-max(0, limit):][::-1]


def guided_repair_intake_status():
    return {"record_count": len(load_guided_repair_intake_records()["records"]), "policy": "Planning-only intake; never creates repair plans, proposals, or patch actions."}


def summarize_guided_repair_intake(record_id):
    record = get_guided_repair_intake_record(record_id)
    return sanitize_intake_record_for_public(record) if record else None

def open_guided_repair_intake(request_type, requested_scope, target_path=None, requester="human", guidance_record_id=None, create_guidance_if_missing=False, export_public=False, export_index=False, export_private=False, metadata=None):
    from aether.action.repair_guidance_engine import get_repair_guidance_record
    t = now_iso(); g = get_repair_guidance_record(guidance_record_id) if guidance_record_id else None
    r = {"id": "guided_repair_intake_" + uuid.uuid4().hex, "created": t, "updated": t, "timezone": get_timezone(), "status": "blocked", "request_type": request_type, "requested_scope": requested_scope, "target_path": sanitize_target_path(target_path), "requester": requester, "guidance_record_id": guidance_record_id, "guidance_decision": None, "inferred_risk_category": None, "recommended_gate_chain": [], "required_safety_checks": [], "proceed_allowed": False, "human_review_required": True, "intake_decision": None, "intake_comment": None, "intake_reviewer": None, "planning_allowed": False, "planning_block_reason": "Repair guidance is required before intake can proceed.", "recommended_next_action": "Generate repair guidance first.", "public_report_path": None, "public_index_path": None, "private_export_path": None, "warnings": [], "metadata": metadata or {}}
    if not request_type or not requested_scope: r.update({"planning_block_reason": "Invalid repair intake request.", "recommended_next_action": "Clarify repair request before intake."})
    elif not g:
        r["planning_block_reason"] = "Repair guidance record was not found." if guidance_record_id else r["planning_block_reason"]
    else: r.update({"status": "opened", "guidance_record_id": g.get("id"), "guidance_decision": g.get("guidance_decision"), "inferred_risk_category": g.get("inferred_risk_category"), "recommended_gate_chain": g.get("recommended_gate_chain", []), "required_safety_checks": g.get("required_safety_checks", []), "proceed_allowed": bool(g.get("proceed_allowed")), "human_review_required": bool(g.get("human_review_required")), "planning_block_reason": "Awaiting human intake decision.", "recommended_next_action": "Submit a human intake decision before repair planning."})
    _save(r)
    exports = (
        (export_public, "public_report_path", lambda: export_guided_repair_intake_report(r["id"])),
        (export_index, "public_index_path", export_guided_repair_intake_index),
        (export_private, "private_export_path", lambda: export_private_guided_repair_intake_record(r["id"])),
    )
    for enabled, path_key, exporter in exports:
        if not enabled:
            continue
        try:
            result = exporter()
            if result.get("status") == "exported":
                r[path_key] = result.get(path_key)
            else:
                r["warnings"].append("Export was not completed.")
        except Exception as exc:
            r["warnings"].append(f"Export unavailable: {type(exc).__name__}.")
    return _save(r)

def submit_guided_repair_intake_decision(
    intake_record_id,
    decision,
    comment=None,
    reviewer="human",
    metadata=None,
):
    """Record a human intake decision without creating a repair plan."""
    from datetime import datetime
    try:
        from zoneinfo import ZoneInfo
        now = datetime.now(ZoneInfo("Asia/Kuala_Lumpur")).isoformat()
    except Exception:
        now = datetime.now().isoformat()

    allowed = {
        "allow_repair_planning",
        "pause_for_clarification",
        "reject_repair_request",
        "require_human_investigation",
    }

    data = load_guided_repair_intake_records()
    records = data.setdefault("records", [])

    target = None
    for record in records:
        if record.get("id") == intake_record_id:
            target = record
            break

    if not target:
        return {
            "id": intake_record_id,
            "status": "blocked",
            "planning_allowed": False,
            "intake_decision": decision,
            "warnings": ["Guided repair intake record was not found."],
            "recommended_next_action": "Open a guided repair intake before submitting a decision.",
        }

    if target.get("status") != "opened":
        return {
            "id": target.get("id"),
            "status": "blocked",
            "planning_allowed": bool(target.get("planning_allowed")),
            "intake_decision": target.get("intake_decision"),
            "warnings": ["Intake decision can only be submitted once while status is opened."],
            "recommended_next_action": target.get("recommended_next_action"),
        }

    if decision not in allowed:
        return {
            "id": target.get("id"),
            "status": "blocked",
            "planning_allowed": False,
            "intake_decision": decision,
            "warnings": ["Invalid guided repair intake decision."],
            "recommended_next_action": "Use an allowed intake decision.",
        }

    target["updated"] = now
    target["status"] = "decision_recorded"
    target["intake_decision"] = decision
    target["intake_comment"] = comment
    target["intake_reviewer"] = reviewer or "human"
    target["metadata"] = target.get("metadata") or {}
    if metadata:
        target["metadata"]["decision_metadata"] = metadata

    if decision == "allow_repair_planning":
        target["planning_allowed"] = True
        target["planning_block_reason"] = None
        target["recommended_next_action"] = "Open repair planning in a future step using this intake record as context."
    elif decision == "pause_for_clarification":
        target["planning_allowed"] = False
        target["planning_block_reason"] = "Repair scope requires clarification."
        target["recommended_next_action"] = "Clarify repair scope before planning."
    elif decision == "reject_repair_request":
        target["planning_allowed"] = False
        target["planning_block_reason"] = "Repair request was rejected."
        target["recommended_next_action"] = "Do not plan this repair request."
    elif decision == "require_human_investigation":
        target["planning_allowed"] = False
        target["planning_block_reason"] = "Human investigation is required."
        target["recommended_next_action"] = "Human investigation is required before repair planning."

    save_guided_repair_intake_records(data)
    return target

def _bool_text(value):
    return "yes" if bool(value) else "no"


def export_guided_repair_intake_report(
    intake_record_id,
    output_dir="docs/history/repair_intake",
    metadata=None,
):
    """Export a sanitized public guided repair intake report."""
    record = get_guided_repair_intake_record(intake_record_id)
    if not record:
        return {
            "status": "blocked",
            "record_id": intake_record_id,
            "warnings": ["Guided repair intake record was not found."],
        }

    safe = sanitize_intake_record_for_public(record)
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / (intake_record_id + ".md")

    chain = safe.get("recommended_gate_chain") or []
    checks = safe.get("required_safety_checks") or []

    lines = [
        "# Guided Repair Intake Record",
        "",
        "## Summary",
        "",
        f"- Intake: {shorten_id(safe.get('id'))}",
        f"- Request type: {safe.get('request_type') or ''}",
        f"- Scope: {safe.get('requested_scope') or ''}",
        f"- Target: {safe.get('target_path') or ''}",
        f"- Guidance: {shorten_id(safe.get('guidance_record_id'))}",
        f"- Guidance decision: {safe.get('guidance_decision') or ''}",
        f"- Inferred risk: {safe.get('inferred_risk_category') or ''}",
        f"- Human review required: {_bool_text(safe.get('human_review_required'))}",
        f"- Intake decision: {safe.get('intake_decision') or ''}",
        f"- Planning allowed: {_bool_text(safe.get('planning_allowed'))}",
        "",
        "## Recommended Gate Chain",
        "",
    ]

    if chain:
        for i, item in enumerate(chain, 1):
            lines.append(f"{i}. {item}")
    else:
        lines.append("- No gate chain recorded.")

    lines += [
        "",
        "## Required Safety Checks",
        "",
    ]

    if checks:
        for item in checks:
            lines.append(f"- {item}")
    else:
        lines.append("- No safety checks recorded.")

    lines += [
        "",
        "## Safety Notes",
        "",
        "- This intake does not create a repair plan.",
        "- This intake does not create a patch proposal.",
        "- This intake does not apply or rollback changes.",
        "- Raw excerpts are excluded.",
        "- Backup paths are excluded.",
        "- Private runtime paths are excluded.",
        "",
    ]

    out_path.write_text("\n".join(lines), encoding="utf-8")

    data = load_guided_repair_intake_records()
    for item in data.get("records", []):
        if item.get("id") == intake_record_id:
            item["public_report_path"] = str(out_path).replace("\\", "/")
            break
    save_guided_repair_intake_records(data)

    return {
        "status": "exported",
        "record_id": intake_record_id,
        "public_report_path": str(out_path).replace("\\", "/"),
    }


def export_guided_repair_intake_index(
    output_path="docs/history/repair_intake/INDEX.md",
    limit=100,
    metadata=None,
):
    """Export a sanitized public guided repair intake dashboard."""
    records = list_guided_repair_intake_records(limit=limit)
    out_path = Path(output_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        "# Aether Guided Repair Intake Dashboard",
        "",
        "This dashboard is generated from sanitized guided repair intake records.",
        "",
        "## Summary",
        "",
        f"- Records included: {len(records)}",
        "",
        "## Intake Records",
        "",
        "| Created | Intake | Target | Risk | Guidance Decision | Intake Decision | Planning Allowed |",
        "|---|---|---|---|---|---|---|",
    ]

    for record in records:
        safe = sanitize_intake_record_for_public(record)
        created = str(safe.get("created") or "")[:10]
        lines.append(
            "| "
            + created
            + " | "
            + str(shorten_id(safe.get("id")) or "")
            + " | "
            + str(safe.get("target_path") or "")
            + " | "
            + str(safe.get("inferred_risk_category") or "")
            + " | "
            + str(safe.get("guidance_decision") or "")
            + " | "
            + str(safe.get("intake_decision") or "")
            + " | "
            + _bool_text(safe.get("planning_allowed"))
            + " |"
        )

    lines.append("")
    out_path.write_text("\n".join(lines), encoding="utf-8")

    data = load_guided_repair_intake_records()
    for item in data.get("records", []):
        item["public_index_path"] = str(out_path).replace("\\", "/")
    save_guided_repair_intake_records(data)

    return {
        "status": "exported",
        "public_index_path": str(out_path).replace("\\", "/"),
        "record_count": len(records),
    }

def export_private_guided_repair_intake_record(
    intake_record_id,
    metadata=None,
):
    """Export a private sanitized guided repair intake record.

    This still excludes raw excerpts, backup paths, secrets, and full source content.
    """
    record = get_guided_repair_intake_record(intake_record_id)
    if not record:
        return {
            "status": "blocked",
            "record_id": intake_record_id,
            "warnings": ["Guided repair intake record was not found."],
        }

    safe = sanitize_intake_record_for_public(record)

    export_dir = get_guided_repair_intake_dir() / "exports"
    export_dir.mkdir(parents=True, exist_ok=True)
    export_path = export_dir / (intake_record_id + ".json")

    private_payload = {
        "type": "guided_repair_intake_private_export",
        "version": "0.1.0",
        "record": safe,
        "metadata": metadata or {},
    }

    export_path.write_text(
        json.dumps(private_payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    data = load_guided_repair_intake_records()
    for item in data.get("records", []):
        if item.get("id") == intake_record_id:
            item["private_export_path"] = str(export_path).replace("\\", "/")
            break
    save_guided_repair_intake_records(data)

    return {
        "status": "exported",
        "record_id": intake_record_id,
        "private_export_path": str(export_path).replace("\\", "/"),
    }

