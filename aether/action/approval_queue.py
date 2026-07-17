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
