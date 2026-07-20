"""Safe human-facing console for existing Aether patch proposals."""
from pathlib import Path
import json
import uuid
import yaml

from aether.action.repair_workflow_tracker import get_repair_workflow_report
from aether.action.self_modification_cycle import get_self_modification_session
from aether.action.patch_proposal import get_patch_proposal
from aether.action.patch_review import DECISIONS, list_patch_reviews, review_patch_proposal
from aether.action.mutation_log import record_mutation
from aether.memory.timeline.recorder import record_event
from aether.memory.graph.store import add_edge
from aether.time.clock import get_timezone, now_iso

SOURCE_TYPES = {"repair_workflow", "self_modification_session", "patch_proposal"}
SENSITIVE_TERMS = ("c:/aetherdata", "backup_path", "pre_rollback", "original_excerpt", "proposed_excerpt", "patch_text", "diff_preview", "token", "secret", "password", "api_key", "private_key", "id_rsa", "id_ed25519", ".env")


def load_aether_config(path="config/aether.yaml"):
    config_path = Path(path)
    return yaml.safe_load(config_path.read_text(encoding="utf-8")) or {} if config_path.exists() else {}


def get_proposal_review_console_dir():
    return Path(load_aether_config().get("paths", {}).get("private_dir", "private")) / "proposal_review_console"


def get_proposal_review_console_path():
    return get_proposal_review_console_dir() / "proposal_review_console_records.json"


def load_proposal_review_console_records():
    path = get_proposal_review_console_path()
    try:
        data = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    except json.JSONDecodeError:
        data = {}
    timestamp = now_iso()
    data.setdefault("type", "proposal_review_console_records")
    data.setdefault("version", "0.1.0")
    data.setdefault("created", timestamp)
    data.setdefault("updated", data["created"])
    data.setdefault("timezone", get_timezone())
    data.setdefault("records", [])
    return data


def save_proposal_review_console_records(data):
    path = get_proposal_review_console_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    data["updated"] = now_iso()
    data["timezone"] = get_timezone()
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def _safe_text(value, limit=300):
    text = str(value or "")[:limit]
    return "[redacted]" if any(term in text.lower().replace("\\", "/") for term in SENSITIVE_TERMS) else text


def _safe_target_path(path):
    text = str(path or "").replace("\\", "/")
    prefix = "C:/Aether/"
    return text[len(prefix):] if text.lower().startswith(prefix.lower()) else None


def _safe_metadata(metadata):
    if not isinstance(metadata, dict):
        return {}
    return {str(key)[:80]: _safe_text(value, 160) for key, value in metadata.items() if not any(term in str(key).lower() for term in SENSITIVE_TERMS)}


def _proposal_summary(proposal):
    if not proposal:
        return None
    return {"proposal_id": proposal.get("id"), "proposal_status": proposal.get("status"), "target_path": _safe_target_path(proposal.get("target_path") or proposal.get("normalized_path")), "risk_level": proposal.get("risk_level"), "created": str(proposal.get("created", ""))[:32], "requires_user_approval": bool(proposal.get("requires_user_approval")), "proposed_change_summary": _safe_text(proposal.get("proposed_change_summary")), "review_exists": bool(list_patch_reviews(proposal.get("id"), 1)), "next_recommended_step": "Human should submit an explicit review decision before any dry-run or apply."}


def _save_record(record):
    data = load_proposal_review_console_records()
    for index, item in enumerate(data["records"]):
        if item["id"] == record["id"]:
            data["records"][index] = record
            break
    else:
        data["records"].append(record)
    save_proposal_review_console_records(data)
    return record


def _audit_open(record):
    warnings = []
    try:
        from aether.core.runtime import runtime
        runtime.working_memory.add_event(role="aether", content=f"Proposal review console opened: {record['status']}", event_type="proposal_review_console_opened", metadata={key: record.get(key) for key in ("id", "source_type", "source_id", "proposal_id", "status")} | {"record_id": record["id"]})
    except Exception:
        warnings.append("Working Memory audit was unavailable.")
    try:
        record_event("proposal_review_console", f"Proposal review console opened: {record['status']}", f"Aether opened a human review console for proposal {record.get('proposal_id') or 'unknown'}.", "normal")
    except Exception:
        warnings.append("Timeline audit was unavailable.")
    try:
        add_edge("Aether", "opened_proposal_review_console", record["id"])
        add_edge(record["id"], "from_source", record["source_id"])
        add_edge(record["id"], "has_status", record["status"])
        if record.get("proposal_id"): add_edge(record["id"], "reviews_proposal", record["proposal_id"])
        if record.get("self_modification_session_id"): add_edge(record["id"], "for_self_modification_session", record["self_modification_session_id"])
        if record.get("workflow_report_id"): add_edge(record["id"], "from_repair_workflow", record["workflow_report_id"])
    except Exception:
        warnings.append("Graph audit was unavailable.")
    try:
        record_mutation("manual_note", "Proposal review console opened", "Aether opened a safe human proposal review console.", milestone="Milestone 32 — Human Proposal Review Console", risk_level="low", status=record["status"], reversible=False, rollback_available=False)
    except Exception:
        warnings.append("Mutation Log integration was unavailable.")
    return warnings


def _audit_submit(record):
    warnings = []
    try:
        from aether.core.runtime import runtime
        runtime.working_memory.add_event(role="aether", content=f"Proposal review submitted: {record.get('review_decision')}", event_type="proposal_review_submitted", metadata={key: record.get(key) for key in ("id", "proposal_id", "review_decision", "patch_review_id", "status")} | {"record_id": record["id"], "decision": record.get("review_decision")})
    except Exception:
        warnings.append("Working Memory audit was unavailable.")
    try:
        decision = record.get("review_decision") or "unknown"
        record_event("proposal_review", f"Proposal review submitted: {decision}", f"Human review was submitted for proposal {record.get('proposal_id') or 'unknown'}.", "high" if decision in {"approve", "reject"} else "normal")
    except Exception:
        warnings.append("Timeline audit was unavailable.")
    try:
        if record.get("patch_review_id"): add_edge(record["id"], "created_patch_review", record["patch_review_id"])
        if record.get("review_decision"): add_edge(record["id"], "review_decision", record["review_decision"])
        add_edge(record["id"], "has_status", record["status"])
    except Exception:
        warnings.append("Graph audit was unavailable.")
    try:
        record_mutation("manual_note", "Human proposal review submitted", "A human submitted a proposal review decision through the proposal review console.", milestone="Milestone 32 — Human Proposal Review Console", target_path=record.get("target_path"), risk_level="medium", status=record["status"], reversible=False, rollback_available=False)
    except Exception:
        warnings.append("Mutation Log integration was unavailable.")
    return warnings


def open_proposal_review_console(source_type, source_id, metadata=None):
    timestamp = now_iso()
    record = {"id": f"proposal_review_console_{uuid.uuid4().hex}", "created": timestamp, "updated": timestamp, "timezone": get_timezone(), "status": "opened", "source_type": source_type, "source_id": source_id, "workflow_report_id": None, "self_modification_session_id": None, "proposal_id": None, "patch_review_id": None, "proposal_status": None, "review_decision": None, "review_comment": None, "target_path": None, "safe_proposal_summary": None, "current_step": "console_opened", "next_recommended_step": "Human should submit an explicit review decision before any dry-run or apply.", "warnings": [], "metadata": _safe_metadata(metadata)}
    proposal = None
    if source_type not in SOURCE_TYPES:
        record.update({"status": "blocked", "current_step": "source_validation", "next_recommended_step": "Use a supported console source type."})
        record["warnings"].append("Unsupported console source type.")
    elif source_type == "repair_workflow":
        workflow = get_repair_workflow_report(source_id)
        if not workflow:
            record["status"] = "blocked"; record["warnings"].append("Repair workflow report was not found.")
        else:
            record["workflow_report_id"] = source_id; record["self_modification_session_id"] = workflow.get("self_modification_session_id"); record["proposal_id"] = workflow.get("patch_proposal_id"); proposal = get_patch_proposal(record["proposal_id"])
    elif source_type == "self_modification_session":
        session = get_self_modification_session(source_id)
        if not session:
            record["status"] = "blocked"; record["warnings"].append("Self-modification session was not found.")
        else:
            record["self_modification_session_id"] = source_id; record["proposal_id"] = session.get("proposal_id"); proposal = get_patch_proposal(record["proposal_id"])
    else:
        record["proposal_id"] = source_id; proposal = get_patch_proposal(source_id)
    if record["status"] == "opened" and not proposal:
        record["status"] = "blocked"; record["warnings"].append("Patch proposal was not found for the supplied source.")
    if proposal:
        record["proposal_status"] = proposal.get("status"); record["target_path"] = _safe_target_path(proposal.get("target_path") or proposal.get("normalized_path")); record["safe_proposal_summary"] = _proposal_summary(proposal)
    record["warnings"] += _audit_open(record)
    return _save_record(record)


def submit_proposal_review(console_record_id, decision, comment=None, reviewer="human", create_approval_if_required=False, metadata=None):
    record = get_proposal_review_console_record(console_record_id)
    if not record:
        return {"id": console_record_id, "status": "blocked", "warnings": ["Proposal review console record was not found."]}
    if record.get("status") == "reviewed" and not (metadata or {}).get("force_review"):
        record["status"] = "blocked"; record["warnings"].append("Console record has already been reviewed.")
    elif not record.get("proposal_id"):
        record["status"] = "blocked"; record["warnings"].append("Console record has no patch proposal.")
    elif decision not in DECISIONS:
        record["status"] = "blocked"; record["warnings"].append("Invalid patch review decision.")
    else:
        review = review_patch_proposal(record["proposal_id"], decision, comment or "", reviewer or "human", {**_safe_metadata(metadata), "source": "proposal_review_console", "console_record_id": console_record_id, "approval_requested": bool(create_approval_if_required)})
        record.update({"patch_review_id": review.get("id"), "review_decision": decision, "review_comment": _safe_text(comment, 300), "proposal_status": review.get("proposal_status_after") or record.get("proposal_status"), "status": "reviewed" if review.get("status") == "success" else "blocked", "current_step": "human_review_completed" if review.get("status") == "success" else "review_blocked"})
        steps = {"approve": "Run a dry-run apply before any real apply.", "request_changes": "Revise the proposal before review.", "reject": "Stop this proposal or create a new proposal."}
        record["next_recommended_step"] = steps.get(decision, "Inspect the proposal status before continuing.")
        record["warnings"] += [_safe_text(warning, 240) for warning in review.get("warnings", [])]
    record["updated"] = now_iso()
    record["warnings"] += _audit_submit(record)
    return _save_record(record)


def get_proposal_review_console_record(record_id):
    return next((record for record in load_proposal_review_console_records()["records"] if record["id"] == record_id), None)


def list_proposal_review_console_records(status=None, proposal_id=None, limit=50):
    records = [record for record in load_proposal_review_console_records()["records"] if (not status or record["status"] == status) and (not proposal_id or record.get("proposal_id") == proposal_id)]
    return records[-max(0, limit):][::-1]


def proposal_review_console_status():
    data = load_proposal_review_console_records()
    return {"record_count": len(data["records"]), "created": data["created"], "updated": data["updated"], "timezone": data["timezone"], "policy": "Console opens safe summaries and submits only explicit patch-review decisions; it never applies patches."}


def summarize_proposal_review_console(record_id):
    record = get_proposal_review_console_record(record_id)
    if not record:
        return None
    return {key: record.get(key) for key in ("id", "status", "source_type", "source_id", "workflow_report_id", "self_modification_session_id", "proposal_id", "patch_review_id", "proposal_status", "review_decision", "target_path", "safe_proposal_summary", "current_step", "next_recommended_step", "warnings")}
