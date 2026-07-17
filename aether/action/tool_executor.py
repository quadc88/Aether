"""Safe mock and dry-run execution framework for Aether."""

from pathlib import Path
import json
import uuid

import yaml

from aether.action.approval_queue import approval_queue_status
from aether.action.tool_planner import create_tool_invocation_plan
from aether.action.tool_registry import get_tool, register_tool
from aether.action.restricted_file_reader import read_restricted_file, seed_restricted_file_tool
from aether.time.clock import get_timezone, now_iso


SANDBOX_TOOL_IDS = {
    "echo.test",
    "file.preview_read",
    "web.search.mock",
    "shell.plan_only",
    "memory.write.dry_run",
    "approval.status",
    "file.restricted_read",
}


def load_aether_config(path: str = "config/aether.yaml") -> dict:
    config_path = Path(path)
    if not config_path.exists():
        return {}
    with config_path.open("r", encoding="utf-8") as file:
        return yaml.safe_load(file) or {}


def get_execution_dir() -> Path:
    private_dir = load_aether_config().get("paths", {}).get("private_dir", "private")
    return Path(private_dir) / "tool_executions"


def get_execution_log_path() -> Path:
    return get_execution_dir() / "tool_executions.json"


def _new_execution_log() -> dict:
    timestamp = now_iso()
    return {
        "type": "tool_execution_log",
        "version": "0.1.0",
        "created": timestamp,
        "updated": timestamp,
        "timezone": get_timezone(),
        "executions": [],
    }


def load_execution_log() -> dict:
    path = get_execution_log_path()
    if not path.exists():
        return _new_execution_log()
    try:
        log = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return _new_execution_log()
    log.setdefault("type", "tool_execution_log")
    log.setdefault("version", "0.1.0")
    log.setdefault("created", now_iso())
    log.setdefault("updated", log["created"])
    log.setdefault("timezone", get_timezone())
    log.setdefault("executions", [])
    return log


def save_execution_log(log: dict) -> None:
    path = get_execution_log_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    log["updated"] = now_iso()
    log["timezone"] = get_timezone()
    path.write_text(json.dumps(log, indent=2, ensure_ascii=False), encoding="utf-8")


def seed_sandbox_tools() -> dict:
    definitions = [
        ("echo.test", "Echo Test", "Return the supplied payload without external effects.", "sandbox", "low", False, False, True),
        ("file.preview_read", "Preview File Read", "Return a dry-run preview for a file path without reading it.", "file", "medium", True, False, False),
        ("web.search.mock", "Mock Web Search", "Return mock search results without network access.", "web", "low", False, False, True),
        ("shell.plan_only", "Shell Plan Only", "Return a command plan without executing it.", "system", "high", True, True, False),
        ("memory.write.dry_run", "Memory Write Dry Run", "Preview a memory write without storing memory.", "memory", "medium", True, False, False),
        ("approval.status", "Approval Status", "Read the current action approval queue status.", "action", "low", False, False, True),
    ]
    tools = []
    created_count = 0
    for tool_id, name, description, category, risk_level, requires_verification, requires_user_approval, allow_auto_execute in definitions:
        if get_tool(tool_id) is None:
            created_count += 1
        tools.append(register_tool(
            tool_id=tool_id,
            name=name,
            description=description,
            category=category,
            risk_level=risk_level,
            requires_verification=requires_verification,
            requires_user_approval=requires_user_approval,
            allow_auto_execute=allow_auto_execute,
        ))
    restricted_file_tool = seed_restricted_file_tool()
    return {"tools": tools, "created_count": created_count, "restricted_file_tool": restricted_file_tool}


def _safe_result(tool_id: str, payload: dict) -> dict:
    if tool_id == "echo.test":
        return {"echo": payload}
    if tool_id == "file.preview_read":
        return {"preview": f"Would preview-read file: {payload.get('path', '')}"}
    if tool_id == "web.search.mock":
        query = payload.get("query", "")
        return {
            "query": query,
            "results": [
                {"title": f"Mock result for {query}", "source": "sandbox", "snippet": "No internet access was used."},
                {"title": "Aether sandbox result", "source": "sandbox", "snippet": "Mock data only."},
            ],
        }
    if tool_id == "shell.plan_only":
        return {"command_plan": payload.get("command", ""), "message": "Command was not executed."}
    if tool_id == "memory.write.dry_run":
        return {"would_write": payload, "message": "No memory was written."}
    if tool_id == "approval.status":
        return {"approval_queue": approval_queue_status()}
    if tool_id == "file.restricted_read":
        return read_restricted_file(
            path=payload.get("path", ""),
            max_chars=payload.get("max_chars", 12000),
            metadata=payload.get("metadata"),
        )
    raise ValueError("Unsupported sandbox tool.")


def execute_tool(
    text: str,
    tool_id: str | None = None,
    input_payload: dict | None = None,
    proposed_action: str | None = None,
    create_approval_if_required: bool = False,
    dry_run: bool = True,
    metadata: dict | None = None,
) -> dict:
    payload = input_payload or {}
    plan = create_tool_invocation_plan(
        text=text,
        tool_id=tool_id,
        proposed_action=proposed_action,
        create_approval_if_required=create_approval_if_required,
        metadata=metadata,
    )
    selected_tool_id = tool_id or plan["candidate_tool"]["tool_id"]
    tool = get_tool(selected_tool_id) if selected_tool_id else None
    status = "success"
    result = None
    error = None

    if selected_tool_id is None:
        status = "no_tool_matched"
        error = "No tool matched the request."
    elif tool is None:
        status = "tool_not_found"
        error = f"Tool {selected_tool_id} is not registered."
    elif not tool["enabled"]:
        status = "tool_disabled"
        error = f"Tool {selected_tool_id} is disabled."
    elif selected_tool_id not in SANDBOX_TOOL_IDS:
        status = "blocked"
        error = "Tool execution is blocked in sandbox mode."
    elif plan["decision"]["requires_user_approval"]:
        status = "approval_required"
        error = "User approval is required before execution."
    else:
        try:
            result = _safe_result(selected_tool_id, payload)
            if selected_tool_id == "file.restricted_read" and result["status"] != "success":
                status = result["status"]
                error = result["reason"]
        except Exception as exception:
            status = "failed"
            error = str(exception)

    timestamp = now_iso()
    execution = {
        "id": f"tool_execution_{uuid.uuid4().hex}",
        "created": timestamp,
        "updated": timestamp,
        "timezone": get_timezone(),
        "tool_id": selected_tool_id,
        "request_text": text,
        "proposed_action": proposed_action or text,
        "plan": plan,
        "input": payload,
        "status": status,
        "result": result,
        "error": error,
        "dry_run": dry_run,
        "approval_id": plan["approval_item"]["id"] if plan["approval_item"] else None,
        "metadata": metadata or {},
    }
    log = load_execution_log()
    log["executions"].append(execution)
    save_execution_log(log)
    return execution


def list_executions(limit: int = 50) -> list[dict]:
    executions = list(load_execution_log()["executions"])
    executions.sort(key=lambda execution: execution.get("created", ""), reverse=True)
    return executions[: max(0, limit)]


def get_execution(execution_id: str) -> dict | None:
    for execution in load_execution_log()["executions"]:
        if execution.get("id") == execution_id:
            return execution
    return None


def tool_executor_status() -> dict:
    log = load_execution_log()
    return {
        "execution_log_path": str(get_execution_log_path()),
        "execution_count": len(log["executions"]),
        "created": log.get("created"),
        "updated": log.get("updated"),
        "timezone": log.get("timezone"),
    }
