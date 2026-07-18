"""Safe mock and dry-run execution framework for Aether."""

from pathlib import Path
import json
import uuid

import yaml

from aether.action.approval_queue import approval_queue_status
from aether.action.tool_planner import create_tool_invocation_plan
from aether.action.tool_registry import get_tool, register_tool
from aether.action.restricted_file_reader import read_restricted_file, seed_restricted_file_tool
from aether.action.restricted_file_browser import browse_restricted_path, search_restricted_files, seed_restricted_browser_tools
from aether.action.self_inspector import create_project_self_inspection, seed_self_inspection_tool
from aether.action.patch_proposal import create_patch_proposal, seed_patch_proposal_tool
from aether.action.patch_review import review_patch_proposal, seed_patch_review_tool
from aether.action.patch_apply import apply_patch_proposal, seed_patch_apply_tool
from aether.action.patch_rollback import rollback_patch_apply, seed_patch_rollback_tool
from aether.action.mutation_log import record_mutation, summarize_mutations
from aether.action.self_modification_cycle import create_self_modification_session, review_self_modification_session, dry_run_self_modification_session, apply_self_modification_session, rollback_self_modification_session, summarize_self_modification_session
from aether.action.changelog_exporter import export_public_changelog, export_milestone_report, export_private_changelog_report, changelog_export_status
from aether.action.code_reviewer import create_code_review, summarize_code_review, code_review_status
from aether.action.review_bridge import create_bridge_from_finding, summarize_review_bridge_record, review_bridge_status
from aether.action.repair_planner import create_repair_plan, summarize_repair_plan, repair_plan_status
from aether.time.clock import get_timezone, now_iso


SANDBOX_TOOL_IDS = {
    "echo.test",
    "file.preview_read",
    "web.search.mock",
    "shell.plan_only",
    "memory.write.dry_run",
    "approval.status",
    "file.restricted_read",
    "file.restricted_browse",
    "file.restricted_search",
    "project.self_inspect",
    "file.patch_proposal",
    "file.patch_review",
    "file.patch_apply",
    "file.patch_rollback",
    "project.mutation_log.record", "project.mutation_log.summary",
    "project.self_modification.create", "project.self_modification.review", "project.self_modification.dry_run", "project.self_modification.apply", "project.self_modification.rollback", "project.self_modification.summary",
    "project.changelog.export_public", "project.changelog.export_milestone", "project.changelog.export_private", "project.changelog.status",
    "project.code_review.create", "project.code_review.summary", "project.code_review.status",
    "project.review_bridge.create", "project.review_bridge.summary", "project.review_bridge.status",
    "project.repair_plan.create", "project.repair_plan.summary", "project.repair_plan.status",
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
    browser_tools = seed_restricted_browser_tools()
    self_inspection_tool = seed_self_inspection_tool()
    patch_proposal_tool = seed_patch_proposal_tool()
    patch_review_tool = seed_patch_review_tool()
    patch_apply_tool = seed_patch_apply_tool()
    patch_rollback_tool = seed_patch_rollback_tool()
    return {"tools": tools, "created_count": created_count, "restricted_file_tool": restricted_file_tool, "browser_tools": browser_tools, "self_inspection_tool": self_inspection_tool, "patch_proposal_tool": patch_proposal_tool, "patch_review_tool": patch_review_tool, "patch_apply_tool": patch_apply_tool, "patch_rollback_tool": patch_rollback_tool}


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
    if tool_id == "file.restricted_browse":
        return browse_restricted_path(
            path=payload.get("path", "C:/Aether"), max_depth=payload.get("max_depth", 3),
            max_entries=payload.get("max_entries", 200), include_files=payload.get("include_files", True),
            include_dirs=payload.get("include_dirs", True), metadata=payload.get("metadata"),
        )
    if tool_id == "file.restricted_search":
        return search_restricted_files(
            query=payload.get("query", ""), root=payload.get("root", "C:/Aether"),
            max_results=payload.get("max_results", 50), metadata=payload.get("metadata"),
        )
    if tool_id == "project.self_inspect":
        return create_project_self_inspection(
            root=payload.get("root", "C:/Aether"), max_files_to_read=payload.get("max_files_to_read", 20),
            max_chars_per_file=payload.get("max_chars_per_file", 6000), metadata=payload.get("metadata"),
        )
    if tool_id == "file.patch_proposal":
        return create_patch_proposal(payload.get("target_path", ""), payload.get("request_text", ""), payload.get("proposed_change_summary", ""), payload.get("proposed_excerpt", ""), payload.get("reason", ""), payload.get("original_excerpt"), payload.get("create_approval_if_required", False), payload.get("metadata"))
    if tool_id == "file.patch_review":
        return review_patch_proposal(payload.get("proposal_id", ""), payload.get("decision", ""), payload.get("review_reason", ""), payload.get("reviewer", "user"), payload.get("metadata"))
    if tool_id == "file.patch_apply":
        return apply_patch_proposal(payload.get("proposal_id", ""), payload.get("dry_run", True), payload.get("metadata"))
    if tool_id == "file.patch_rollback":
        return rollback_patch_apply(payload.get("apply_id", ""), payload.get("dry_run", True), payload.get("metadata"))
    if tool_id == "project.mutation_log.record": return record_mutation(**payload)
    if tool_id == "project.mutation_log.summary": return summarize_mutations(payload.get("limit", 100))
    if tool_id == "project.self_modification.create": return create_self_modification_session(payload.get("goal", ""),payload.get("target_path", ""),payload.get("proposed_change_summary", ""),payload.get("proposed_excerpt", ""),payload.get("reason", ""),payload.get("original_excerpt"),payload.get("create_approval_if_required", False),payload.get("metadata"))
    if tool_id == "project.self_modification.review": return review_self_modification_session(payload.get("session_id", ""),payload.get("decision", ""),payload.get("review_reason", ""),payload.get("reviewer", "user"),payload.get("metadata"))
    if tool_id == "project.self_modification.dry_run": return dry_run_self_modification_session(payload.get("session_id", ""),payload.get("metadata"))
    if tool_id == "project.self_modification.apply": return apply_self_modification_session(payload.get("session_id", ""),payload.get("metadata"))
    if tool_id == "project.self_modification.rollback": return rollback_self_modification_session(payload.get("session_id", ""),payload.get("metadata"))
    if tool_id == "project.self_modification.summary": return summarize_self_modification_session(payload.get("session_id", ""))
    if tool_id == "project.changelog.export_public": return export_public_changelog(payload.get("output_path", "docs/history/CHANGELOG.md"),payload.get("milestone"),payload.get("limit",200),payload.get("metadata"))
    if tool_id == "project.changelog.export_milestone": return export_milestone_report(payload.get("milestone", ""),payload.get("output_dir", "docs/history/milestones"),payload.get("metadata"))
    if tool_id == "project.changelog.export_private": return export_private_changelog_report(payload.get("milestone"),payload.get("limit",500),payload.get("metadata"))
    if tool_id == "project.changelog.status": return changelog_export_status()
    if tool_id == "project.code_review.create": return create_code_review(payload.get("scope", ""),payload.get("target_paths"),payload.get("max_files",20),payload.get("max_chars_per_file",12000),payload.get("include_tests",True),payload.get("metadata"))
    if tool_id == "project.code_review.summary": return summarize_code_review(payload.get("report_id", ""))
    if tool_id == "project.code_review.status": return code_review_status()
    if tool_id == "project.review_bridge.create": return create_bridge_from_finding(payload.get("report_id", ""),payload.get("finding_id", ""),payload.get("proposed_excerpt", ""),payload.get("original_excerpt"),payload.get("proposed_change_summary"),payload.get("reason"),payload.get("create_approval_if_required",False),payload.get("metadata"))
    if tool_id == "project.review_bridge.summary": return summarize_review_bridge_record(payload.get("record_id", ""))
    if tool_id == "project.review_bridge.status": return review_bridge_status()
    if tool_id == "project.repair_plan.create": return create_repair_plan(payload.get("review_report_id", ""),payload.get("scope"),payload.get("include_deferred",True),payload.get("max_findings",50),payload.get("metadata"))
    if tool_id == "project.repair_plan.summary": return summarize_repair_plan(payload.get("plan_id", ""))
    if tool_id == "project.repair_plan.status": return repair_plan_status()
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
            if selected_tool_id in {"file.restricted_read", "file.restricted_browse", "file.restricted_search"} and result["status"] != "success":
                status = result["status"]
                error = result["reason"]
            if selected_tool_id == "project.self_inspect" and result["status"] in {"blocked", "failed"}:
                status = result["status"]
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
