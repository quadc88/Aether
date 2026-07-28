"""Tool Execution Service — Thin Interface Refactor Phase 7 (Milestone 80I).

Moves tool execution orchestration from api_server.py into this service module.
Also exposes record helpers used by file and self-inspection endpoints that
remain in api_server.py until future milestones.

Behavior-preserving refactor: no endpoint path, response shape, or safety changes.
"""

from aether.core.runtime import runtime

from aether.memory.timeline.recorder import record_event
from aether.memory.graph.store import add_edge

from aether.action.tool_executor import (
    execute_tool,
    get_execution,
    list_executions,
    seed_sandbox_tools,
    tool_executor_status,
)


# --------------------------------------------------------------------------- #
# Shared record helpers (also used by file/self-inspection endpoints in api_server)
# --------------------------------------------------------------------------- #


def record_restricted_file_access(access: dict) -> tuple[dict | None, list[dict], list[str]]:
    runtime.working_memory.add_event(
        role="aether",
        content=f"Restricted file read attempted: {access['path']} ({access['status']}).",
        event_type="restricted_file_read_attempted",
        metadata={
            "access_id": access["id"],
            "path": access["path"],
            "status": access["status"],
            "allowed": access["allowed"],
            "reason": access["reason"],
        },
    )
    timeline_event = record_event(
        event_type="file_access",
        title=f"Restricted file read: {access['status']}",
        description=f"Aether attempted restricted file read for {access['path']} with status {access['status']}.",
        importance="high" if access["status"] == "blocked" else "normal",
    )
    warnings = []
    graph_relationships = []
    try:
        graph_relationships.extend(
            [
                add_edge("Aether", "attempted_file_access", access["id"]),
                add_edge(access["id"], "has_status", access["status"]),
                add_edge(access["id"], "target_path", access["normalized_path"]),
            ]
        )
        for relationship in graph_relationships:
            relationship.pop("created_new", None)
    except Exception as error:
        warnings.append(f"Graph Memory integration was unavailable: {error}")
    return timeline_event, graph_relationships, warnings


def record_self_inspection_report(report: dict) -> tuple[dict, list[dict], list[str]]:
    runtime.working_memory.add_event(
        role="aether",
        content=f"Project self-inspection report created: {report['id']} ({report['status']}).",
        event_type="self_inspection_report_created",
        metadata={
            "report_id": report["id"], "status": report["status"],
            "files_read": report["summary"]["files_read"], "endpoint_count": report["summary"]["endpoint_count"],
            "warning_count": len(report["warnings"]),
        },
    )
    timeline_event = record_event(
        event_type="self_inspection",
        title="Project self-inspection report created",
        description=f"Aether created project self-inspection report {report['id']} with status {report['status']}.",
        importance="high" if report["status"] in {"failed", "blocked"} else "normal",
    )
    warnings = []
    graph_relationships = []
    try:
        graph_relationships.extend(
            [
                add_edge("Aether", "created_self_inspection_report", report["id"]),
                add_edge(report["id"], "inspected_project", "Aether"),
                add_edge(report["id"], "has_status", report["status"]),
            ]
        )
        for relationship in graph_relationships:
            relationship.pop("created_new", None)
    except Exception as error:
        warnings.append(f"Graph Memory integration was unavailable: {error}")
    return timeline_event, graph_relationships, warnings


# --------------------------------------------------------------------------- #
# Handler functions
# --------------------------------------------------------------------------- #


def handle_seed_action_sandbox_tools() -> dict:
    result = seed_sandbox_tools()
    runtime.working_memory.add_event(
        role="aether",
        content=f"Sandbox tools seeded: {result['created_count']} new tools.",
        event_type="sandbox_tools_seeded",
        metadata={"tool_count": len(result["tools"]), "created_count": result["created_count"]},
    )
    return {"name": "Aether", "status": runtime.status(), "result": result}


def handle_execute_action_tool(
    text: str,
    tool_id: str | None = None,
    input_payload: dict | None = None,
    proposed_action: str | None = None,
    create_approval_if_required: bool = False,
    dry_run: bool = True,
    metadata: dict | None = None,
) -> dict:
    execution = execute_tool(
        text=text,
        tool_id=tool_id,
        input_payload=input_payload,
        proposed_action=proposed_action,
        create_approval_if_required=create_approval_if_required,
        dry_run=dry_run,
        metadata=metadata,
    )
    runtime.working_memory.add_event(
        role="aether",
        content=f"Tool execution attempted: {execution['tool_id'] or 'no tool'} ({execution['status']}).",
        event_type="tool_execution_attempted",
        metadata={
            "execution_id": execution["id"],
            "tool_id": execution["tool_id"],
            "status": execution["status"],
            "dry_run": execution["dry_run"],
            "requires_user_approval": execution["plan"]["decision"]["requires_user_approval"],
        },
    )
    file_access_audit = None
    if execution["tool_id"] == "file.restricted_read" and isinstance(execution["result"], dict) and "id" in execution["result"]:
        file_access_audit = record_restricted_file_access(execution["result"])
    self_inspection_audit = None
    if execution["tool_id"] == "project.self_inspect" and isinstance(execution["result"], dict) and "id" in execution["result"]:
        self_inspection_audit = record_self_inspection_report(execution["result"])
    timeline_event = None
    if (
        execution["status"] in {"blocked", "approval_required", "failed"}
        or not execution["dry_run"]
        or execution["tool_id"] not in {"echo.test", "file.preview_read", "web.search.mock", "shell.plan_only", "memory.write.dry_run", "approval.status"}
    ):
        timeline_event = record_event(
            event_type="tool_execution",
            title=f"Tool execution attempt: {execution['tool_id']}",
            description=f"Aether attempted tool execution with status {execution['status']}.",
            importance="high" if execution["status"] in {"blocked", "approval_required", "failed"} else "normal",
        )
    warnings = []
    graph_relationships = []
    try:
        graph_relationships.extend(
            [
                add_edge("Aether", "attempted_tool_execution", execution["id"]),
                add_edge(execution["id"], "used_tool", execution["tool_id"] or "no_tool"),
                add_edge(execution["id"], "has_status", execution["status"]),
            ]
        )
        for relationship in graph_relationships:
            relationship.pop("created_new", None)
    except Exception as error:
        warnings.append(f"Graph Memory integration was unavailable: {error}")
    return {"name": "Aether", "status": runtime.status(), "execution": execution, "timeline_event": timeline_event, "file_access_audit": file_access_audit, "self_inspection_audit": self_inspection_audit, "graph_relationships": graph_relationships, "warnings": warnings}


def handle_get_tool_executor_status() -> dict:
    return {"name": "Aether", "status": runtime.status(), "tool_executor": tool_executor_status()}


def handle_list_action_tool_executions(limit: int = 50) -> dict:
    return {"name": "Aether", "status": runtime.status(), "executions": list_executions(limit)}


def handle_get_action_tool_execution(execution_id: str) -> dict:
    return {"name": "Aether", "status": runtime.status(), "execution": get_execution(execution_id)}
