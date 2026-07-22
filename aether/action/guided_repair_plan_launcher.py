"""Safe launcher for repair planning approved by guided repair intake."""
from pathlib import Path
import json
import uuid

import yaml

from aether.time.clock import get_timezone, now_iso


def load_aether_config(path="config/aether.yaml"):
    config_path = Path(path)
    return yaml.safe_load(config_path.read_text(encoding="utf-8")) or {} if config_path.exists() else {}


def get_guided_repair_plan_launcher_dir():
    private_dir = load_aether_config().get("paths", {}).get("private_dir", "private")
    return Path(private_dir) / "repair_plan_launcher"


def get_guided_repair_plan_launcher_path():
    return get_guided_repair_plan_launcher_dir() / "guided_repair_plan_launcher_records.json"


def load_guided_repair_plan_launcher_records():
    path = get_guided_repair_plan_launcher_path()
    try:
        data = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    except json.JSONDecodeError:
        data = {}
    timestamp = now_iso()
    data.setdefault("type", "guided_repair_plan_launcher_records")
    data.setdefault("version", "0.1.0")
    data.setdefault("created", timestamp)
    data.setdefault("updated", data["created"])
    data.setdefault("timezone", get_timezone())
    data.setdefault("records", [])
    return data


def save_guided_repair_plan_launcher_records(data):
    path = get_guided_repair_plan_launcher_path()
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
    data = load_guided_repair_plan_launcher_records()
    data["records"] = [item for item in data["records"] if item.get("id") != record["id"]]
    data["records"].append(record)
    save_guided_repair_plan_launcher_records(data)
    return record


def launch_guided_repair_plan(
    intake_record_id,
    review_report_id=None,
    create_repair_plan=True,
    metadata=None,
):
    """Create a launcher record after enforcing the guided intake gate."""
    from aether.action.guided_repair_intake import get_guided_repair_intake_record

    intake = get_guided_repair_intake_record(intake_record_id)
    timestamp = now_iso()
    record = {
        "id": f"guided_repair_plan_launcher_{uuid.uuid4().hex}",
        "created": timestamp,
        "updated": timestamp,
        "timezone": get_timezone(),
        "status": "blocked",
        "intake_record_id": intake_record_id,
        "request_type": None,
        "requested_scope": None,
        "target_path": None,
        "guidance_record_id": None,
        "guidance_decision": None,
        "inferred_risk_category": None,
        "recommended_gate_chain": [],
        "required_safety_checks": [],
        "intake_decision": None,
        "planning_allowed": False,
        "review_report_id": review_report_id,
        "adapter_status": "intake_gate_pending",
        "adapter_required": True,
        "adapter_warning": None,
        "repair_plan_id": None,
        "repair_plan_status": None,
        "planning_summary": None,
        "next_recommended_step": "Open guided repair intake first.",
        "warnings": [],
        "metadata": metadata or {},
    }
    if not intake:
        return _save(record)

    for key in (
        "request_type", "requested_scope", "guidance_record_id", "guidance_decision",
        "inferred_risk_category", "recommended_gate_chain", "required_safety_checks",
        "intake_decision", "planning_allowed",
    ):
        record[key] = intake.get(key)
    record["target_path"] = sanitize_target_path(intake.get("target_path"))

    if intake.get("status") != "decision_recorded":
        record["next_recommended_step"] = "Submit guided repair intake decision before planning."
    elif intake.get("intake_decision") != "allow_repair_planning":
        record["next_recommended_step"] = "Repair planning is not allowed by the intake decision."
    elif intake.get("planning_allowed") is not True:
        record["next_recommended_step"] = "Planning is blocked by guided repair intake."
    elif not create_repair_plan:
        record["adapter_status"] = "launch_not_requested"
        record["next_recommended_step"] = "Set create_repair_plan true to launch planning."
    elif not review_report_id:
        record["adapter_status"] = "missing_review_report"
        record["adapter_warning"] = "Repair planner requires a code review report before guided planning can launch."
        record["warnings"].append(record["adapter_warning"])
        record["next_recommended_step"] = "Run restricted code review or provide an existing review_report_id before launching repair planning."
    else:
        from aether.action.repair_planner import create_repair_plan

        try:
            plan = create_repair_plan(
                review_report_id,
                scope=record["requested_scope"],
                metadata={"source": "guided_repair_plan_launcher", "intake_record_id": intake_record_id},
            )
        except Exception as exc:
            record["status"] = "failed"
            record["adapter_status"] = "planner_failed"
            record["adapter_warning"] = f"Repair planner was unavailable: {type(exc).__name__}."
            record["warnings"].append(record["adapter_warning"])
            record["next_recommended_step"] = "Inspect the supplied code review report before retrying planning."
            return _save(record)
        record["adapter_required"] = False
        record["adapter_status"] = "planner_called"
        record["repair_plan_status"] = plan.get("status")
        record["planning_summary"] = plan.get("summary")
        if plan.get("status") == "blocked":
            record["adapter_status"] = "planner_blocked"
            record["adapter_warning"] = "The supplied code review report could not launch repair planning."
            record["warnings"].append(record["adapter_warning"])
            record["next_recommended_step"] = "Provide a compatible code review report before repair planning."
        else:
            record["status"] = "launched"
            record["repair_plan_id"] = plan.get("id")
            record["adapter_status"] = "repair_plan_created"
            record["next_recommended_step"] = "Review the repair plan before bridge selection."
    return _save(record)


def get_guided_repair_plan_launcher_record(record_id):
    records = load_guided_repair_plan_launcher_records()["records"]
    return next((item for item in records if item.get("id") == record_id), None)


def list_guided_repair_plan_launcher_records(
    status=None,
    intake_record_id=None,
    target_path=None,
    limit=50,
):
    records = load_guided_repair_plan_launcher_records()["records"]
    matched = [
        item for item in records
        if (not status or item.get("status") == status)
        and (not intake_record_id or item.get("intake_record_id") == intake_record_id)
        and (not target_path or item.get("target_path") == sanitize_target_path(target_path))
    ]
    return matched[-max(0, limit):][::-1]


def guided_repair_plan_launcher_status():
    return {
        "record_count": len(load_guided_repair_plan_launcher_records()["records"]),
        "policy": "Launches planning only after approved guided intake; no patch actions.",
    }


def summarize_guided_repair_plan_launcher(record_id):
    record = get_guided_repair_plan_launcher_record(record_id)
    if not record:
        return None
    keys = (
        "id", "status", "intake_record_id", "target_path", "guidance_decision",
        "inferred_risk_category", "intake_decision", "planning_allowed",
        "review_report_id", "adapter_status", "adapter_required", "adapter_warning",
        "repair_plan_id", "repair_plan_status", "next_recommended_step", "warnings",
    )
    summary = {key: record.get(key) for key in keys}
    summary["id"] = shorten_id(summary["id"])
    summary["intake_record_id"] = shorten_id(summary["intake_record_id"])
    summary["repair_plan_id"] = shorten_id(summary["repair_plan_id"])
    summary["review_report_id"] = shorten_id(summary["review_report_id"])
    summary["target_path"] = sanitize_target_path(summary["target_path"])
    return summary
