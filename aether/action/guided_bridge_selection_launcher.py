"""Guarded bridge-selection launcher for a launched guided repair plan."""
from pathlib import Path
import json
import uuid

import yaml

from aether.time.clock import get_timezone, now_iso


def load_aether_config(path="config/aether.yaml"):
    config_path = Path(path)
    return yaml.safe_load(config_path.read_text(encoding="utf-8")) or {} if config_path.exists() else {}


def get_guided_bridge_selection_launcher_dir():
    private_dir = load_aether_config().get("paths", {}).get("private_dir", "private")
    return Path(private_dir) / "bridge_selection_launcher"


def get_guided_bridge_selection_launcher_path():
    return get_guided_bridge_selection_launcher_dir() / "guided_bridge_selection_launcher_records.json"


def load_guided_bridge_selection_launcher_records():
    path = get_guided_bridge_selection_launcher_path()
    try:
        data = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    except json.JSONDecodeError:
        data = {}
    timestamp = now_iso()
    data.setdefault("type", "guided_bridge_selection_launcher_records")
    data.setdefault("version", "0.1.0")
    data.setdefault("created", timestamp)
    data.setdefault("updated", data["created"])
    data.setdefault("timezone", get_timezone())
    data.setdefault("records", [])
    return data


def save_guided_bridge_selection_launcher_records(data):
    path = get_guided_bridge_selection_launcher_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    data["updated"] = now_iso()
    data["timezone"] = get_timezone()
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def sanitize_target_path(path):
    value = str(path or "").replace("\\", "/")
    prefix = "C:/Aether/"
    return value[len(prefix):] if value.lower().startswith(prefix.lower()) else (value if value and ":" not in value else None)


def shorten_id(value, keep=12):
    return f"{str(value)[:keep]}..." if value and len(str(value)) > keep else value


def _save(record):
    data = load_guided_bridge_selection_launcher_records()
    data["records"] = [item for item in data["records"] if item.get("id") != record["id"]]
    data["records"].append(record)
    save_guided_bridge_selection_launcher_records(data)
    return record


def launch_guided_bridge_selection(
    plan_launcher_record_id,
    finding_id=None,
    proposed_excerpt=None,
    metadata=None,
):
    """Select one explicit repair-plan candidate through the existing selector."""
    from aether.action.guided_repair_plan_launcher import get_guided_repair_plan_launcher_record

    plan_launcher = get_guided_repair_plan_launcher_record(plan_launcher_record_id)
    timestamp = now_iso()
    record = {
        "id": f"guided_bridge_selection_launcher_{uuid.uuid4().hex}",
        "created": timestamp,
        "updated": timestamp,
        "timezone": get_timezone(),
        "status": "blocked",
        "plan_launcher_record_id": plan_launcher_record_id,
        "repair_plan_id": None,
        "repair_plan_status": None,
        "intake_record_id": None,
        "target_path": None,
        "finding_id": finding_id,
        "proposed_excerpt_supplied": bool(proposed_excerpt),
        "bridge_selection_id": None,
        "review_bridge_id": None,
        "self_modification_session_id": None,
        "proposal_id": None,
        "selection_status": None,
        "next_recommended_step": "Launch guided repair planning first.",
        "warnings": [],
        "metadata": metadata or {},
    }
    if not plan_launcher:
        return _save(record)

    for key in ("repair_plan_id", "repair_plan_status", "intake_record_id"):
        record[key] = plan_launcher.get(key)
    record["target_path"] = sanitize_target_path(plan_launcher.get("target_path"))

    if plan_launcher.get("status") != "launched":
        record["next_recommended_step"] = "Guided repair plan launcher must be launched before bridge selection."
    elif not record["repair_plan_id"]:
        record["next_recommended_step"] = "A completed repair plan is required before bridge selection."
    elif not finding_id:
        record["next_recommended_step"] = "Select an explicit repair finding before bridge selection."
    elif not proposed_excerpt:
        record["next_recommended_step"] = "Provide caller-authored proposed excerpt before bridge selection."
    else:
        from aether.action.repair_bridge_selector import create_bridge_from_repair_plan

        try:
            selection = create_bridge_from_repair_plan(
                record["repair_plan_id"], finding_id, proposed_excerpt,
                metadata={"source": "guided_bridge_selection_launcher", "plan_launcher_record_id": plan_launcher_record_id},
            )
        except Exception as exc:
            record["status"] = "failed"
            record["warnings"].append(f"Repair bridge selector was unavailable: {type(exc).__name__}.")
            record["next_recommended_step"] = "Inspect the repair plan before retrying bridge selection."
            return _save(record)
        record["selection_status"] = selection.get("status")
        record["bridge_selection_id"] = selection.get("id")
        record["review_bridge_id"] = selection.get("bridge_record_id")
        record["self_modification_session_id"] = selection.get("session_id")
        record["proposal_id"] = selection.get("proposal_id")
        record["target_path"] = sanitize_target_path(selection.get("target_path") or record["target_path"])
        if selection.get("status") == "bridge_created":
            record["status"] = "launched"
            record["next_recommended_step"] = "Review the generated proposal through the proposal review console."
        else:
            record["warnings"].append("Repair bridge selector did not create a bridge.")
            record["next_recommended_step"] = "Inspect the repair plan and selected finding before retrying."
    return _save(record)


def get_guided_bridge_selection_launcher_record(record_id):
    records = load_guided_bridge_selection_launcher_records()["records"]
    return next((item for item in records if item.get("id") == record_id), None)


def list_guided_bridge_selection_launcher_records(
    status=None,
    plan_launcher_record_id=None,
    repair_plan_id=None,
    target_path=None,
    limit=50,
):
    records = load_guided_bridge_selection_launcher_records()["records"]
    matched = [
        item for item in records
        if (not status or item.get("status") == status)
        and (not plan_launcher_record_id or item.get("plan_launcher_record_id") == plan_launcher_record_id)
        and (not repair_plan_id or item.get("repair_plan_id") == repair_plan_id)
        and (not target_path or item.get("target_path") == sanitize_target_path(target_path))
    ]
    return matched[-max(0, limit):][::-1]


def guided_bridge_selection_launcher_status():
    return {
        "record_count": len(load_guided_bridge_selection_launcher_records()["records"]),
        "policy": "Uses an explicit finding and caller-authored excerpt through repair bridge selection only.",
    }


def summarize_guided_bridge_selection_launcher(record_id):
    record = get_guided_bridge_selection_launcher_record(record_id)
    if not record:
        return None
    keys = (
        "id", "status", "plan_launcher_record_id", "repair_plan_id", "target_path",
        "finding_id", "proposed_excerpt_supplied", "bridge_selection_id", "review_bridge_id",
        "self_modification_session_id", "proposal_id", "selection_status",
        "next_recommended_step", "warnings",
    )
    summary = {key: record.get(key) for key in keys}
    for key in ("id", "plan_launcher_record_id", "repair_plan_id", "bridge_selection_id", "review_bridge_id", "self_modification_session_id", "proposal_id"):
        summary[key] = shorten_id(summary[key])
    summary["target_path"] = sanitize_target_path(summary["target_path"])
    return summary
