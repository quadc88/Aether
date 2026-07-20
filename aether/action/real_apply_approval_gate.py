"""Final human approval readiness records for future real applies; never applies patches."""
from pathlib import Path
import json
import uuid

import yaml

from aether.action.approval_queue import create_approval_item as create_queue_approval_item, get_approval_item
from aether.action.approved_dry_run_gate import get_approved_dry_run_gate_record, list_approved_dry_run_gate_records
from aether.action.dry_run_review_gate import get_dry_run_review_gate_record, list_dry_run_review_gate_records
from aether.action.patch_apply import get_patch_apply
from aether.action.patch_proposal import get_patch_proposal
from aether.action.mutation_log import record_mutation
from aether.memory.timeline.recorder import record_event
from aether.memory.graph.store import add_edge
from aether.time.clock import get_timezone, now_iso


SOURCE_TYPES = {"dry_run_review_gate", "approved_dry_run_gate", "patch_apply"}
DECISIONS = {"approve_real_apply", "reject_real_apply", "needs_more_review"}
SENSITIVE_TERMS = ("c:/aetherdata", "backup_path", "original_excerpt", "proposed_excerpt", "diff_preview", "patch_text", "token", "secret", "password", "api_key", "private_key", "id_rsa", "id_ed25519", ".env")


def load_aether_config(path: str = "config/aether.yaml") -> dict:
    config_path = Path(path)
    return yaml.safe_load(config_path.read_text(encoding="utf-8")) or {} if config_path.exists() else {}


def get_real_apply_approval_gate_dir() -> Path:
    return Path(load_aether_config().get("paths", {}).get("private_dir", "private")) / "real_apply_approval_gate"


def get_real_apply_approval_gate_path() -> Path:
    return get_real_apply_approval_gate_dir() / "real_apply_approval_gate_records.json"


def load_real_apply_approval_gate_records() -> dict:
    path = get_real_apply_approval_gate_path()
    try:
        data = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    except json.JSONDecodeError:
        data = {}
    timestamp = now_iso()
    data.setdefault("type", "real_apply_approval_gate_records")
    data.setdefault("version", "0.1.0")
    data.setdefault("created", timestamp)
    data.setdefault("updated", data["created"])
    data.setdefault("timezone", get_timezone())
    data.setdefault("records", [])
    return data


def save_real_apply_approval_gate_records(data: dict) -> None:
    path = get_real_apply_approval_gate_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    data["updated"] = now_iso()
    data["timezone"] = get_timezone()
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def _safe_target_path(value) -> str | None:
    path = str(value or "").replace("\\", "/")
    prefix = "C:/Aether/"
    return path[len(prefix):] if path.lower().startswith(prefix.lower()) else None


def _safe_metadata(metadata) -> dict:
    if not isinstance(metadata, dict):
        return {}
    safe = {}
    for key, value in metadata.items():
        key_text = str(key)[:80]
        value_text = str(value)[:160]
        if any(term in key_text.lower() or term in value_text.lower().replace("\\", "/") for term in SENSITIVE_TERMS):
            continue
        safe[key_text] = value_text
    return safe


def _save(record: dict) -> dict:
    data = load_real_apply_approval_gate_records()
    for index, existing in enumerate(data["records"]):
        if existing["id"] == record["id"]:
            data["records"][index] = record
            break
    else:
        data["records"].append(record)
    save_real_apply_approval_gate_records(data)
    return record


def _find_accepted_dry_run_review(proposal_id: str | None, patch_apply_id: str | None, approved_gate_id: str | None = None) -> dict | None:
    for record in list_dry_run_review_gate_records(proposal_id=proposal_id, limit=200):
        if record.get("dry_run_review_decision") != "accept":
            continue
        if patch_apply_id and record.get("patch_apply_id") != patch_apply_id:
            continue
        if approved_gate_id and record.get("approved_dry_run_gate_id") != approved_gate_id:
            continue
        return record
    return None


def _audit(record: dict, event: str) -> list[str]:
    warnings = []
    try:
        from aether.core.runtime import runtime
        event_type = "real_apply_approval_gate_opened" if event == "opened" else "real_apply_final_decision_submitted"
        metadata = {"record_id": record["id"], "proposal_id": record.get("proposal_id"), "status": record["status"]}
        metadata.update({"source_type": record.get("source_type"), "source_id": record.get("source_id"), "dry_run_patch_apply_id": record.get("dry_run_patch_apply_id")} if event == "opened" else {"final_decision": record.get("final_decision"), "approval_item_id": record.get("approval_item_id")})
        runtime.working_memory.add_event(role="aether", content=f"Real apply approval gate {event}: {record['status']}", event_type=event_type, metadata=metadata)
    except Exception:
        warnings.append("Working Memory audit was unavailable.")
    try:
        if event == "opened":
            record_event("real_apply_approval_gate", f"Real apply approval gate opened: {record['status']}", f"Aether opened a final approval gate for proposal {record.get('proposal_id') or 'unknown'}.", "high")
        else:
            record_event("real_apply_final_decision", f"Real apply final decision: {record.get('final_decision')}", f"Human final decision was submitted for proposal {record.get('proposal_id') or 'unknown'}.", "high")
    except Exception:
        warnings.append("Timeline audit was unavailable.")
    try:
        if event == "opened":
            add_edge("Aether", "opened_real_apply_approval_gate", record["id"])
            add_edge(record["id"], "from_source", record["source_id"])
            add_edge(record["id"], "has_status", record["status"])
            if record.get("proposal_id"): add_edge(record["id"], "for_proposal", record["proposal_id"])
            if record.get("dry_run_patch_apply_id"): add_edge(record["id"], "after_dry_run_apply", record["dry_run_patch_apply_id"])
            if record.get("dry_run_review_gate_id"): add_edge(record["id"], "from_dry_run_review_gate", record["dry_run_review_gate_id"])
            if record.get("approval_item_id"): add_edge(record["id"], "created_approval_item", record["approval_item_id"])
        else:
            add_edge(record["id"], "final_decision", record.get("final_decision") or "unknown")
            add_edge(record["id"], "has_status", record["status"])
    except Exception:
        warnings.append("Graph audit was unavailable.")
    try:
        record_mutation(
            "manual_note",
            "Real apply approval gate opened" if event == "opened" else "Real apply final decision submitted",
            "Aether opened a final approval gate for future real apply without executing source changes." if event == "opened" else "A human submitted a final real-apply approval gate decision.",
            milestone="Milestone 37 — Real Apply Approval Gate",
            target_path=record.get("target_path") if event != "opened" else None,
            risk_level="high", status=record["status"], reversible=False, rollback_available=False,
        )
    except Exception:
        warnings.append("Mutation Log integration was unavailable.")
    return warnings


def open_real_apply_approval_gate(source_type: str, source_id: str, create_approval_item: bool = True, metadata: dict | None = None) -> dict:
    timestamp = now_iso()
    record = {"id": f"real_apply_approval_gate_{uuid.uuid4().hex}", "created": timestamp, "updated": timestamp, "timezone": get_timezone(), "status": "blocked", "source_type": source_type, "source_id": source_id, "dry_run_review_gate_id": None, "approved_dry_run_gate_id": None, "proposal_id": None, "patch_review_id": None, "dry_run_patch_apply_id": None, "dry_run_review_decision": None, "final_decision": None, "final_comment": None, "reviewer": None, "approval_item_id": None, "approval_item_status": None, "proposal_status": None, "target_path": None, "current_step": "dry_run_acceptance_validation", "next_recommended_step": "Only accepted dry-run reviews can enter the real-apply approval gate.", "warnings": [], "metadata": _safe_metadata(metadata)}
    review = None
    apply_record = None
    if source_type not in SOURCE_TYPES:
        record["warnings"].append("Unsupported real-apply approval gate source type.")
    elif source_type == "dry_run_review_gate":
        review = get_dry_run_review_gate_record(source_id)
        if review:
            record.update({"dry_run_review_gate_id": source_id, "approved_dry_run_gate_id": review.get("approved_dry_run_gate_id"), "proposal_id": review.get("proposal_id"), "patch_review_id": review.get("patch_review_id"), "dry_run_patch_apply_id": review.get("patch_apply_id"), "dry_run_review_decision": review.get("dry_run_review_decision")})
    elif source_type == "approved_dry_run_gate":
        gate = get_approved_dry_run_gate_record(source_id)
        if gate and gate.get("status") == "dry_run_completed":
            record.update({"approved_dry_run_gate_id": source_id, "proposal_id": gate.get("proposal_id"), "patch_review_id": gate.get("patch_review_id"), "dry_run_patch_apply_id": gate.get("patch_apply_id")})
            review = _find_accepted_dry_run_review(record["proposal_id"], record["dry_run_patch_apply_id"], source_id)
            if review: record.update({"dry_run_review_gate_id": review.get("id"), "dry_run_review_decision": review.get("dry_run_review_decision")})
    else:
        apply_record = get_patch_apply(source_id)
        if apply_record:
            record.update({"proposal_id": apply_record.get("proposal_id"), "dry_run_patch_apply_id": source_id})
            review = _find_accepted_dry_run_review(record["proposal_id"], source_id)
            if review: record.update({"dry_run_review_gate_id": review.get("id"), "approved_dry_run_gate_id": review.get("approved_dry_run_gate_id"), "patch_review_id": review.get("patch_review_id"), "dry_run_review_decision": review.get("dry_run_review_decision")})
    apply_record = apply_record or get_patch_apply(record.get("dry_run_patch_apply_id"))
    proposal = get_patch_proposal(record.get("proposal_id"))
    if proposal:
        record.update({"proposal_status": proposal.get("status"), "target_path": _safe_target_path(proposal.get("target_path") or proposal.get("normalized_path"))})
    valid = bool(review and record.get("dry_run_review_decision") == "accept" and apply_record and apply_record.get("dry_run") and apply_record.get("status") == "dry_run")
    if valid:
        record.update({"status": "opened", "current_step": "final_approval_gate_opened", "next_recommended_step": "Human must submit a final decision before any future real apply."})
        if create_approval_item:
            plan = {"risk_level": "high", "action_type": "file_modification", "requires_verification": True, "requires_user_approval": True, "reasons": ["Real apply would modify source files in a future step.", "This milestone only records approval readiness and does not apply changes."]}
            item = create_queue_approval_item("Final approval request for real apply. This gate does not execute the apply.", f"Prepare proposal {record['proposal_id']} for future real apply execution.", plan, {"source": "real_apply_approval_gate", "gate_record_id": record["id"]})
            record.update({"approval_item_id": item.get("id"), "approval_item_status": item.get("status")})
    else:
        record["warnings"].append("An accepted human dry-run review and completed dry-run apply record are required.")
    record["warnings"] += _audit(record, "opened")
    return _save(record)


def submit_real_apply_final_decision(gate_record_id: str, decision: str, comment: str | None = None, reviewer: str | None = "human", metadata: dict | None = None) -> dict:
    record = get_real_apply_approval_gate_record(gate_record_id)
    if not record:
        return {"id": gate_record_id, "status": "blocked", "warnings": ["Real-apply approval gate record was not found."]}
    force = bool((metadata or {}).get("force_decision"))
    if record.get("status") != "opened" and not force:
        record["status"] = "blocked"; record["warnings"].append("Final decision can only be submitted to an open gate.")
    elif decision not in DECISIONS:
        record["status"] = "blocked"; record["warnings"].append("Invalid final real-apply decision.")
    else:
        status = {"approve_real_apply": "final_approved", "reject_real_apply": "final_rejected", "needs_more_review": "opened"}[decision]
        next_step = {"approve_real_apply": "Future milestone may execute real apply only after re-validating this gate and approval record.", "reject_real_apply": "Stop this proposal or return to revision.", "needs_more_review": "Inspect proposal, dry-run result, and workflow before deciding."}[decision]
        step = {"approve_real_apply": "final_approval_completed", "reject_real_apply": "final_approval_rejected", "needs_more_review": "final_approval_paused"}[decision]
        item = get_approval_item(record.get("approval_item_id")) if record.get("approval_item_id") else None
        record.update({"status": status, "final_decision": decision, "final_comment": str(comment or "")[:300], "reviewer": reviewer or "human", "approval_item_status": item.get("status") if item else record.get("approval_item_status"), "current_step": step, "next_recommended_step": next_step})
    record["updated"] = now_iso()
    record["warnings"] += _audit(record, "submitted")
    return _save(record)


def get_real_apply_approval_gate_record(record_id: str) -> dict | None:
    return next((record for record in load_real_apply_approval_gate_records()["records"] if record["id"] == record_id), None)


def list_real_apply_approval_gate_records(status: str | None = None, proposal_id: str | None = None, limit: int = 50) -> list[dict]:
    records = [record for record in load_real_apply_approval_gate_records()["records"] if (not status or record.get("status") == status) and (not proposal_id or record.get("proposal_id") == proposal_id)]
    return records[-max(0, limit):][::-1]


def real_apply_approval_gate_status() -> dict:
    data = load_real_apply_approval_gate_records()
    return {"record_count": len(data["records"]), "created": data["created"], "updated": data["updated"], "timezone": data["timezone"], "policy": "Records final human readiness only; it never runs a real apply, dry-run, or rollback."}


def summarize_real_apply_approval_gate(record_id: str) -> dict | None:
    record = get_real_apply_approval_gate_record(record_id)
    if not record:
        return None
    keys = ("id", "status", "source_type", "source_id", "dry_run_review_gate_id", "approved_dry_run_gate_id", "proposal_id", "patch_review_id", "dry_run_patch_apply_id", "dry_run_review_decision", "final_decision", "reviewer", "approval_item_id", "approval_item_status", "proposal_status", "target_path", "current_step", "next_recommended_step", "warnings")
    return {key: record.get(key) for key in keys}
