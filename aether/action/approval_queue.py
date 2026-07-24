"""Private, JSON-backed action approval queue for Aether."""

from pathlib import Path
import json
import uuid

import yaml

from aether.time.clock import get_timezone, now, now_iso


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
        return json.load(f)


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
        records.append(rec)
    records.sort(key=lambda r: r.get("created_at", ""), reverse=True)
    return records[:limit]


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
