"""Final guarded executor for one approved real patch apply and no other action."""
from pathlib import Path
import json
import uuid

import yaml

from aether.action.approval_queue import get_approval_item
from aether.action.real_apply_approval_gate import get_real_apply_approval_gate_record
from aether.action.patch_apply import apply_patch_proposal, get_patch_apply
from aether.action.patch_proposal import get_patch_proposal
from aether.action.mutation_log import record_mutation
from aether.memory.timeline.recorder import record_event
from aether.memory.graph.store import add_edge
from aether.time.clock import get_timezone, now_iso


SOURCE_TYPES = {"real_apply_approval_gate"}


def load_aether_config(path: str = "config/aether.yaml") -> dict:
    config_path = Path(path)
    return yaml.safe_load(config_path.read_text(encoding="utf-8")) or {} if config_path.exists() else {}


def get_final_real_apply_executor_dir() -> Path:
    return Path(load_aether_config().get("paths", {}).get("private_dir", "private")) / "final_real_apply_executor"


def get_final_real_apply_executor_path() -> Path:
    return get_final_real_apply_executor_dir() / "final_real_apply_executor_records.json"


def load_final_real_apply_executor_records() -> dict:
    path = get_final_real_apply_executor_path()
    try:
        data = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    except json.JSONDecodeError:
        data = {}
    timestamp = now_iso()
    data.setdefault("type", "final_real_apply_executor_records")
    data.setdefault("version", "0.1.0")
    data.setdefault("created", timestamp)
    data.setdefault("updated", data["created"])
    data.setdefault("timezone", get_timezone())
    data.setdefault("records", [])
    return data


def save_final_real_apply_executor_records(data: dict) -> None:
    path = get_final_real_apply_executor_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    data["updated"] = now_iso()
    data["timezone"] = get_timezone()
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def _safe_target_path(value) -> str | None:
    path = str(value or "").replace("\\", "/")
    prefix = "C:/Aether/"
    return path[len(prefix):] if path.lower().startswith(prefix.lower()) else None


def _safe_metadata(metadata) -> dict:
    blocked_terms = ("c:/aetherdata", "backup", "original_excerpt", "proposed_excerpt", "diff", "token", "secret", "password", "key", ".env")
    if not isinstance(metadata, dict):
        return {}
    result = {}
    for key, value in metadata.items():
        key_text, value_text = str(key)[:80], str(value)[:160]
        if not any(term in key_text.lower() or term in value_text.lower().replace("\\", "/") for term in blocked_terms):
            result[key_text] = value_text
    return result


def _save(record: dict) -> dict:
    data = load_final_real_apply_executor_records()
    for index, existing in enumerate(data["records"]):
        if existing["id"] == record["id"]:
            data["records"][index] = record
            break
    else:
        data["records"].append(record)
    save_final_real_apply_executor_records(data)
    return record


def _has_applied_record(gate_id: str, exclude_record_id: str | None = None) -> bool:
    return any(record.get("real_apply_approval_gate_id") == gate_id and record.get("status") == "applied" and record.get("id") != exclude_record_id for record in load_final_real_apply_executor_records()["records"])


def _refresh_readiness(record: dict) -> tuple[bool, list[str]]:
    warnings = []
    gate = get_real_apply_approval_gate_record(record.get("real_apply_approval_gate_id"))
    if not gate:
        return False, ["Real-apply approval gate was not found."]
    record.update({"proposal_id": gate.get("proposal_id"), "approval_item_id": gate.get("approval_item_id"), "dry_run_patch_apply_id": gate.get("dry_run_patch_apply_id")})
    proposal = get_patch_proposal(record.get("proposal_id"))
    item = get_approval_item(record.get("approval_item_id")) if record.get("approval_item_id") else None
    dry_run = get_patch_apply(record.get("dry_run_patch_apply_id")) if record.get("dry_run_patch_apply_id") else None
    record.update({"approval_item_status": item.get("status") if item else None, "proposal_status": proposal.get("status") if proposal else None, "target_path": _safe_target_path((proposal or {}).get("target_path") or (proposal or {}).get("normalized_path"))})
    if gate.get("status") != "final_approved" or gate.get("final_decision") != "approve_real_apply":
        warnings.append("Final approval gate is not approved for real apply.")
    if not record.get("proposal_id"):
        warnings.append("Approval gate has no proposal.")
    if not record.get("approval_item_id"):
        warnings.append("Approval gate has no approval queue item.")
    elif not item or item.get("status") != "approved":
        warnings.append("Human must approve the approval queue item before real apply.")
    if not dry_run or not dry_run.get("dry_run") or dry_run.get("status") != "dry_run":
        warnings.append("A completed dry-run apply record is required.")
    if not proposal or proposal.get("status") != "approved":
        warnings.append("Proposal is not currently approved for patch apply.")
    if _has_applied_record(record.get("real_apply_approval_gate_id"), record.get("id")):
        warnings.append("Real apply already executed for this gate.")
    return not warnings, warnings


def _audit(record: dict, event: str) -> list[str]:
    warnings = []
    try:
        from aether.core.runtime import runtime
        if event == "opened":
            metadata = {"record_id": record["id"], "proposal_id": record.get("proposal_id"), "real_apply_approval_gate_id": record.get("real_apply_approval_gate_id"), "approval_item_id": record.get("approval_item_id"), "status": record["status"]}
            event_type = "final_real_apply_executor_opened"
        else:
            metadata = {"record_id": record["id"], "proposal_id": record.get("proposal_id"), "real_patch_apply_id": record.get("real_patch_apply_id"), "real_apply_status": record.get("real_apply_status"), "rollback_available": record.get("rollback_available"), "status": record["status"]}
            event_type = "final_real_apply_completed"
        runtime.working_memory.add_event(role="aether", content=f"Final real apply executor {event}: {record['status']}", event_type=event_type, metadata=metadata)
    except Exception:
        warnings.append("Working Memory audit was unavailable.")
    try:
        if event == "opened":
            record_event("final_real_apply_executor", f"Final real apply executor opened: {record['status']}", f"Aether opened final real apply executor for proposal {record.get('proposal_id') or 'unknown'}.", "high")
        elif record.get("status") == "applied":
            record_event("final_real_apply", "Final real apply completed", f"Aether performed a real apply for proposal {record.get('proposal_id') or 'unknown'} after all gates passed.", "critical")
    except Exception:
        warnings.append("Timeline audit was unavailable.")
    try:
        if event == "opened":
            add_edge("Aether", "opened_final_real_apply_executor", record["id"])
            add_edge(record["id"], "has_status", record["status"])
            if record.get("proposal_id"): add_edge(record["id"], "for_proposal", record["proposal_id"])
            if record.get("real_apply_approval_gate_id"): add_edge(record["id"], "from_real_apply_approval_gate", record["real_apply_approval_gate_id"])
            if record.get("approval_item_id"): add_edge(record["id"], "uses_approval_item", record["approval_item_id"])
        elif record.get("real_patch_apply_id"):
            add_edge(record["id"], "created_real_patch_apply", record["real_patch_apply_id"])
            add_edge(record["id"], "has_real_apply_status", record.get("real_apply_status") or "unknown")
            if record.get("rollback_available") and record.get("proposal_id"): add_edge(record["id"], "rollback_available", record["proposal_id"])
    except Exception:
        warnings.append("Graph audit was unavailable.")
    try:
        record_mutation(
            "manual_note" if event == "opened" else "patch_applied",
            "Final real apply executor opened" if event == "opened" else "Final real apply completed",
            "Aether opened the final real apply executor after validating approval readiness." if event == "opened" else "Aether performed a real patch apply after final human approval and approval queue validation.",
            milestone="Milestone 38 — Final Real Apply Executor", target_path=record.get("target_path") if event != "opened" else None,
            risk_level="high", status=record["status"], reversible=event != "opened" and bool(record.get("rollback_available")), rollback_available=event != "opened" and bool(record.get("rollback_available")),
        )
    except Exception:
        warnings.append("Mutation Log integration was unavailable.")
    return warnings


def open_final_real_apply_executor(source_type: str, source_id: str, metadata: dict | None = None) -> dict:
    timestamp = now_iso()
    record = {"id": f"final_real_apply_executor_{uuid.uuid4().hex}", "created": timestamp, "updated": timestamp, "timezone": get_timezone(), "status": "blocked", "source_type": source_type, "source_id": source_id, "real_apply_approval_gate_id": source_id if source_type == "real_apply_approval_gate" else None, "proposal_id": None, "approval_item_id": None, "approval_item_status": None, "dry_run_patch_apply_id": None, "real_patch_apply_id": None, "real_apply_status": None, "rollback_available": False, "backup_created": False, "proposal_status": None, "target_path": None, "current_step": "final_readiness_validation", "next_recommended_step": "Use a final-approved real-apply approval gate.", "warnings": [], "metadata": _safe_metadata(metadata)}
    if source_type not in SOURCE_TYPES:
        record["warnings"].append("Unsupported final real apply executor source type.")
    else:
        ready, warnings = _refresh_readiness(record)
        record["warnings"] += warnings
        if ready:
            record.update({"status": "ready", "current_step": "final_real_apply_ready", "next_recommended_step": "Human may explicitly execute final real apply. This will modify source files and create backup."})
        elif record.get("approval_item_id") and record.get("approval_item_status") != "approved":
            record["next_recommended_step"] = "Human must approve the approval queue item before real apply."
    record["warnings"] += _audit(record, "opened")
    return _save(record)


def execute_final_real_apply(executor_record_id: str, metadata: dict | None = None) -> dict:
    record = get_final_real_apply_executor_record(executor_record_id)
    if not record:
        return {"id": executor_record_id, "status": "blocked", "warnings": ["Final real apply executor record was not found."]}
    if record.get("status") != "ready" and not bool((metadata or {}).get("force_execute")):
        return {"id": executor_record_id, "status": "blocked", "warnings": ["Final real apply executor is not ready."]}
    else:
        ready, warnings = _refresh_readiness(record)
        if not ready:
            record["status"] = "blocked"; record["warnings"] += warnings
        else:
            result = apply_patch_proposal(record["proposal_id"], False, {**_safe_metadata(metadata), "source": "final_real_apply_executor", "executor_record_id": executor_record_id, "real_apply_approval_gate_id": record["real_apply_approval_gate_id"]})
            record.update({"real_patch_apply_id": result.get("id"), "real_apply_status": result.get("status"), "backup_created": bool(result.get("backup_path")), "rollback_available": bool(result.get("backup_path")) and bool(result.get("applied")), "proposal_status": result.get("proposal_status") or record.get("proposal_status")})
            record["warnings"] += [str(warning)[:240] for warning in result.get("warnings", [])]
            if result.get("status") == "success" and result.get("applied"):
                record.update({"status": "applied", "current_step": "real_apply_completed", "next_recommended_step": "Verify behavior. Rollback is available if needed."})
            else:
                record.update({"status": "blocked" if result.get("status") == "blocked" else "failed", "current_step": "real_apply_not_completed", "next_recommended_step": "Inspect the safe warnings and resolve the failed gate before retrying."})
    record["updated"] = now_iso()
    record["warnings"] += _audit(record, "completed")
    return _save(record)


def get_final_real_apply_executor_record(record_id: str) -> dict | None:
    return next((record for record in load_final_real_apply_executor_records()["records"] if record["id"] == record_id), None)


def list_final_real_apply_executor_records(status: str | None = None, proposal_id: str | None = None, limit: int = 50) -> list[dict]:
    records = [record for record in load_final_real_apply_executor_records()["records"] if (not status or record.get("status") == status) and (not proposal_id or record.get("proposal_id") == proposal_id)]
    return records[-max(0, limit):][::-1]


def final_real_apply_executor_status() -> dict:
    data = load_final_real_apply_executor_records()
    return {"record_count": len(data["records"]), "created": data["created"], "updated": data["updated"], "timezone": data["timezone"], "policy": "Only an explicit execute after approved final gate and approval item may call the restricted patch apply flow."}


def summarize_final_real_apply_executor(record_id: str) -> dict | None:
    record = get_final_real_apply_executor_record(record_id)
    if not record:
        return None
    keys = ("id", "status", "source_type", "source_id", "real_apply_approval_gate_id", "proposal_id", "approval_item_id", "approval_item_status", "dry_run_patch_apply_id", "real_patch_apply_id", "real_apply_status", "rollback_available", "backup_created", "proposal_status", "target_path", "current_step", "next_recommended_step", "warnings")
    return {key: record.get(key) for key in keys}
