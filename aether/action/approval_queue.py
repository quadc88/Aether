"""Private, JSON-backed action approval queue for Aether."""

from pathlib import Path
import json
import uuid
import hashlib
import os
import tempfile

import yaml

from aether.time.clock import get_timezone, now, now_iso


def restricted_read_fingerprint(action: dict | None) -> str | None:
    if not isinstance(action, dict):
        return None
    parameters = action.get("parameters")
    from aether.action.tool_planner import normalize_restricted_read_target
    if (
        set(action) != {"tool_id", "action_type", "name", "target", "permission_class", "parameters"}
        or
        action.get("tool_id") != "file.restricted_read"
        or action.get("action_type") != "restricted_file_read"
        or action.get("name") != "Restricted File Read"
        or action.get("permission_class") != "read_only"
        or not isinstance(action.get("target"), str)
        or action["target"] != normalize_restricted_read_target(action["target"])
        or not isinstance(parameters, dict)
        or set(parameters) != {"max_chars"}
        or not isinstance(parameters["max_chars"], int)
        or isinstance(parameters["max_chars"], bool)
        or not 0 <= parameters["max_chars"] <= 12000
    ):
        return None
    material = {
        "capability_id": "file.restricted_read",
        "max_chars": parameters["max_chars"],
        "permission_class": "read_only",
        "target": action["target"],
    }
    encoded = json.dumps(material, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _normalize_approval_record(record: dict) -> dict:
    record.setdefault("requested_action_fingerprint", None)
    record.setdefault("execution_consumed", False)
    record.setdefault("consumed_by_execution_attempt", None)
    return record


def load_aether_config(path: str = "config/aether.yaml") -> dict:
    config_path = Path(path)
    if not config_path.exists():
        return {}
    with config_path.open("r", encoding="utf-8") as file:
        return yaml.safe_load(file) or {}


def get_approval_dir() -> Path:
    private_dir = load_aether_config().get("paths", {}).get("private_dir", "private")
    return Path(private_dir) / "approvals"


def get_approval_queue_path() -> Path:
    return get_approval_dir() / "approval_queue.json"


def _new_queue() -> dict:
    timestamp = now_iso()
    return {
        "type": "action_approval_queue",
        "version": "0.1.0",
        "created": timestamp,
        "updated": timestamp,
        "timezone": get_timezone(),
        "items": [],
    }


def load_queue() -> dict:
    queue_path = get_approval_queue_path()
    if not queue_path.exists():
        return _new_queue()
    try:
        queue = json.loads(queue_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return _new_queue()

    queue.setdefault("type", "action_approval_queue")
    queue.setdefault("version", "0.1.0")
    queue.setdefault("created", now_iso())
    queue.setdefault("updated", queue["created"])
    queue.setdefault("timezone", get_timezone())
    queue.setdefault("items", [])
    return queue


def save_queue(queue: dict) -> None:
    queue_path = get_approval_queue_path()
    queue_path.parent.mkdir(parents=True, exist_ok=True)
    queue["updated"] = now_iso()
    queue["timezone"] = get_timezone()
    queue_path.write_text(json.dumps(queue, indent=2, ensure_ascii=False), encoding="utf-8")


def create_approval_item(
    request_text: str,
    proposed_action: str,
    verification_plan: dict,
    metadata: dict | None = None,
) -> dict:
    queue = load_queue()
    timestamp = now_iso()
    approval_id = f"approval_{now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
    action_type = verification_plan.get("action_type", "general_request")
    risk_level = verification_plan.get("risk_level", "low")
    requires_approval = bool(verification_plan.get("requires_user_approval", False))
    reason = (
        f"{risk_level.capitalize()}-risk {action_type.replace('_', ' ')} requires explicit user approval."
        if requires_approval
        else "Approval was optionally requested for this action."
    )
    item = {
        "id": approval_id,
        "created": timestamp,
        "updated": timestamp,
        "timezone": get_timezone(),
        "status": "pending",
        "action_type": action_type,
        "risk_level": risk_level,
        "request_text": request_text,
        "proposed_action": proposed_action,
        "verification_plan": verification_plan,
        "requires_user_approval": requires_approval,
        "reason": reason,
        "metadata": metadata or {},
        "decision_time": None,
        "decision_reason": None,
    }
    queue["items"].append(item)
    save_queue(queue)
    return item


def list_approval_items(status: str | None = None, limit: int = 50) -> list[dict]:
    items = load_queue()["items"]
    if status:
        items = [item for item in items if item.get("status") == status]
    items.sort(key=lambda item: item.get("created", ""), reverse=True)
    return items[: max(0, limit)]


def get_approval_item(approval_id: str) -> dict | None:
    for item in load_queue()["items"]:
        if item.get("id") == approval_id:
            return item
    return None


def _decide_item(approval_id: str, status: str, decision_reason: str) -> dict | None:
    queue = load_queue()
    for item in queue["items"]:
        if item.get("id") != approval_id:
            continue
        if item.get("status") != "pending":
            result = dict(item)
            result["warning"] = f"Approval item is already {item.get('status')}."
            return result
        item["status"] = status
        item["updated"] = now_iso()
        item["decision_time"] = item["updated"]
        item["decision_reason"] = decision_reason
        save_queue(queue)
        return item
    return None


def approve_item(approval_id: str, decision_reason: str = "") -> dict | None:
    return _decide_item(approval_id, "approved", decision_reason)


def reject_item(approval_id: str, decision_reason: str = "") -> dict | None:
    return _decide_item(approval_id, "rejected", decision_reason)


def cancel_item(approval_id: str, decision_reason: str = "") -> dict | None:
    return _decide_item(approval_id, "cancelled", decision_reason)


def approval_queue_status() -> dict:
    queue = load_queue()
    counts = {status: 0 for status in ("pending", "approved", "rejected", "cancelled")}
    for item in queue["items"]:
        status = item.get("status")
        if status in counts:
            counts[status] += 1
    return {
        "approval_queue_path": str(get_approval_queue_path()),
        "item_count": len(queue["items"]),
        "pending_count": counts["pending"],
        "approved_count": counts["approved"],
        "rejected_count": counts["rejected"],
        "cancelled_count": counts["cancelled"],
        "created": queue.get("created"),
        "updated": queue.get("updated"),
        "timezone": queue.get("timezone"),
    }


# ===================================================================== #
# Approval Record Store (Milestone 54A)
# ===================================================================== #
# Individual JSON files under private_dir/approvals/
# Distinct from the legacy approval_queue.json single-file store above.
# ===================================================================== #

from datetime import datetime, timezone as _tz


def _approval_record_dir() -> Path:
    """Return the approvals/ directory under the configured private data dir."""
    config = load_aether_config()
    paths = config.get("paths", {})
    private_val = paths.get("private_dir", "")
    if not private_val:
        base = get_approval_dir().parent
    else:
        base = Path(private_val)
    rec_dir = base / "approvals"
    rec_dir.mkdir(parents=True, exist_ok=True)
    return rec_dir


def create_approval_record(
    approval_request: dict,
    context: dict | None = None,
) -> dict:
    """Create and persist a new pending approval record as an individual JSON file.

    Args:
        approval_request: The structured request dict from the approval builder.
        context: Optional metadata context (e.g. session_id).

    Returns:
        The saved approval record dict.
    """
    approval_id = uuid.uuid4().hex
    now_iso_str = datetime.now(_tz.utc).isoformat()

    record: dict = {
        "approval_id": approval_id,
        "status": "pending",
        "approval_request": dict(approval_request),
        "created_at": now_iso_str,
        "updated_at": now_iso_str,
        "decision": None,
        "decided_at": None,
        "reviewer": None,
        "decision_reason": None,
        "execution_allowed_after_decision": False,
        "tool_executed": False,
        "metadata": dict(context) if context else {},
        "warnings": [],
        "requested_action_fingerprint": restricted_read_fingerprint(
            approval_request.get("requested_action")
        ),
        "execution_consumed": False,
        "consumed_by_execution_attempt": None,
    }

    path = _approval_record_dir() / f"approval_{approval_id}.json"
    path.write_text(json.dumps(record, indent=2, default=str), encoding="utf-8")
    return record


def get_approval_record(approval_id: str) -> dict | None:
    """Read one approval record by id. Returns None if not found."""
    path = _approval_record_dir() / f"approval_{approval_id}.json"
    if not path.exists():
        return None
    with path.open("r", encoding="utf-8") as f:
        return _normalize_approval_record(json.load(f))


def list_approval_records(
    status: str | None = None,
    limit: int = 50,
) -> list[dict]:
    """List approval records, newest first.

    Args:
        status: Optional filter by status.
        limit: Maximum number of records to return.
    """
    rec_dir = _approval_record_dir()
    records: list[dict] = []
    for p in rec_dir.glob("approval_*.json"):
        with p.open("r", encoding="utf-8") as f:
            rec = json.load(f)
        if status is not None and rec.get("status") != status:
            continue
        records.append(_normalize_approval_record(rec))
    records.sort(key=lambda r: r.get("created_at", ""), reverse=True)
    return records[:limit]


def claim_approval_for_execution(approval_id: str, execution_attempt_id: str) -> dict:
    """Atomically consume one approved record for one execution attempt."""
    directory = _approval_record_dir()
    record_path = directory / f"approval_{approval_id}.json"
    lock_path = directory / f"approval_{approval_id}.lock"
    result = {
        "claimed": False,
        "approval_id": approval_id,
        "execution_attempt_id": execution_attempt_id,
        "reason": "Approval could not be claimed.",
    }
    directory.mkdir(parents=True, exist_ok=True)
    lock_file = None
    lock_platform = None
    lock_acquired = False
    try:
        lock_file = lock_path.open("a+")
        if os.name == "posix":
            import fcntl
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
            lock_platform = "posix"
            lock_acquired = True
        elif os.name == "nt":
            import msvcrt
            lock_file.seek(0)
            msvcrt.locking(lock_file.fileno(), msvcrt.LK_LOCK, 1)
            lock_platform = "nt"
            lock_acquired = True
        else:
            raise OSError(f"Unsupported platform for approval claim: {os.name}")
        if not record_path.exists():
            result["reason"] = "Approval record was not found."
            return result
        record = _normalize_approval_record(json.loads(record_path.read_text(encoding="utf-8")))
        if record.get("status") != "approved":
            result["reason"] = "Approval record is not approved."
            return result
        if record.get("execution_consumed") or record.get("consumed_by_execution_attempt") is not None:
            result["reason"] = "Approval record has already been consumed."
            return result
        record["execution_consumed"] = True
        record["consumed_by_execution_attempt"] = execution_attempt_id
        record["updated_at"] = datetime.now(_tz.utc).isoformat()
        fd, temporary_name = tempfile.mkstemp(prefix=f"approval_{approval_id}.", suffix=".tmp", dir=directory)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as temporary:
                json.dump(record, temporary, indent=2, default=str)
                temporary.flush()
                os.fsync(temporary.fileno())
            os.replace(temporary_name, record_path)
        finally:
            if os.path.exists(temporary_name):
                os.unlink(temporary_name)
        result.update(claimed=True, reason="Approval claimed.", record=record)
        return result
    except (OSError, ValueError, json.JSONDecodeError):
        result["reason"] = "Approval claim failed safely."
        return result
    finally:
        if lock_file is not None:
            if lock_acquired and lock_platform == "posix":
                import fcntl
                fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)
            elif lock_acquired and lock_platform == "nt":
                import msvcrt
                lock_file.seek(0)
                msvcrt.locking(lock_file.fileno(), msvcrt.LK_UNLCK, 1)
            lock_file.close()


def update_approval_record_status(
    approval_id: str,
    decision: str,
    reviewer: str | None = None,
    reason: str | None = None,
) -> dict | None:
    """Update an approval record's status.

    Allowed decisions: ``"approved"``, ``"rejected"``, ``"cancelled"``.

    Only records with status ``"pending"`` may be transitioned.
    If already decided, the original record is returned unchanged with a warning.

    Args:
        approval_id: Id of the record to update.
        decision: One of approved / rejected / cancelled.
        reviewer: Name/identifier of the reviewer.
        reason: Decision reason string.

    Returns:
        The updated record dict, or None if not found.
    """
    valid_decisions = {"approved", "rejected", "cancelled"}
    if decision not in valid_decisions:
        raise ValueError(f"Invalid decision: {decision}. Must be one of {valid_decisions}.")

    record = get_approval_record(approval_id)
    if record is None:
        return None

    warnings = list(record.get("warnings", []))

    if record["status"] != "pending":
        warnings.append(
            f"Record is already '{record['status']}'. No state change applied."
        )
        record["warnings"] = warnings
        return record

    now_iso_str = datetime.now(_tz.utc).isoformat()
    record["status"] = decision
    record["decision"] = decision
    record["decided_at"] = now_iso_str
    record["reviewer"] = reviewer
    record["decision_reason"] = reason
    record["updated_at"] = now_iso_str
    record["execution_allowed_after_decision"] = False
    record["tool_executed"] = False
    record["warnings"] = warnings

    path = _approval_record_dir() / f"approval_{approval_id}.json"
    path.write_text(json.dumps(record, indent=2, default=str), encoding="utf-8")
    return record
