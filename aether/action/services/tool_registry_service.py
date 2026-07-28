"""Tool Registry Service — Thin Interface Refactor Phase 7 (Milestone 80I).

Moves tool registry orchestration from api_server.py into this service module.

Behavior-preserving refactor: no endpoint path, response shape, or safety changes.
"""

from aether.core.runtime import runtime

from aether.memory.timeline.recorder import record_event
from aether.memory.graph.store import add_edge

from aether.action.tool_registry import (
    disable_tool,
    enable_tool,
    get_tool,
    list_tools,
    register_tool,
    search_tools,
    seed_default_tools,
    tool_registry_status,
    update_tool_policy,
)


# --------------------------------------------------------------------------- #
# Internal helpers
# --------------------------------------------------------------------------- #


def _add_tool_working_memory_event(tool: dict, event_type: str) -> None:
    runtime.working_memory.add_event(
        role="aether",
        content=f"Tool {event_type.replace('_', ' ')}: {tool['id']}",
        event_type=event_type,
        metadata={
            "tool_id": tool["id"],
            "risk_level": tool["risk_level"],
            "enabled": tool["enabled"],
            "requires_user_approval": tool["requires_user_approval"],
            "allow_auto_execute": tool["allow_auto_execute"],
        },
    )


def _add_tool_graph_relationships(tool: dict, policy_only: bool = False) -> tuple[list[dict], list[str]]:
    relationships = []
    warnings = []
    try:
        if not policy_only:
            relationships.extend(
                [
                    add_edge("Aether", "registered_tool", tool["id"]),
                    add_edge(tool["id"], "belongs_to_category", tool["category"]),
                    add_edge(tool["id"], "has_risk_level", tool["risk_level"]),
                ]
            )
        else:
            relationships.append(add_edge(tool["id"], "has_policy", tool["risk_level"]))
        for relationship in relationships:
            relationship.pop("created_new", None)
    except Exception as error:
        warnings.append(f"Graph Memory integration was unavailable: {error}")
    return relationships, warnings


def _record_tool_timeline(tool: dict, title: str, description: str) -> dict:
    return record_event(
        event_type="tool_registry",
        title=title,
        description=description,
        importance="high" if tool["risk_level"] == "high" else "normal",
    )


def _change_tool_enabled(tool_id: str, enabled: bool) -> dict:
    tool = enable_tool(tool_id) if enabled else disable_tool(tool_id)
    if tool is None:
        return {"name": "Aether", "status": runtime.status(), "tool": None, "warnings": ["Tool was not found."]}
    event_type = "tool_enabled" if enabled else "tool_disabled"
    _add_tool_working_memory_event(tool, event_type)
    timeline_event = None
    if not enabled or tool["risk_level"] == "high":
        action = "enabled" if enabled else "disabled"
        timeline_event = _record_tool_timeline(tool, f"Tool {action}: {tool['id']}", f"Aether {action} tool {tool['id']}.")
    return {"name": "Aether", "status": runtime.status(), "tool": tool, "timeline_event": timeline_event, "warnings": []}


# --------------------------------------------------------------------------- #
# Handler functions
# --------------------------------------------------------------------------- #


def handle_get_tool_registry_status() -> dict:
    return {"name": "Aether", "status": runtime.status(), "tool_registry": tool_registry_status()}


def handle_register_action_tool(
    tool_id: str,
    name: str,
    description: str,
    category: str,
    risk_level: str = "medium",
    enabled: bool = True,
    requires_verification: bool = True,
    requires_user_approval: bool = False,
    allow_auto_execute: bool = False,
    input_schema: dict | None = None,
    output_schema: dict | None = None,
    metadata: dict | None = None,
) -> dict:
    tool = register_tool(
        tool_id=tool_id,
        name=name,
        description=description,
        category=category,
        risk_level=risk_level,
        enabled=enabled,
        requires_verification=requires_verification,
        requires_user_approval=requires_user_approval,
        allow_auto_execute=allow_auto_execute,
        input_schema=input_schema,
        output_schema=output_schema,
        metadata=metadata,
    )
    _add_tool_working_memory_event(tool, "tool_registered")
    timeline_event = None
    if tool["risk_level"] == "high":
        timeline_event = _record_tool_timeline(
            tool,
            f"Tool registered: {tool['id']}",
            f"Aether registered tool {tool['id']} with risk level {tool['risk_level']}.",
        )
    graph_relationships, warnings = _add_tool_graph_relationships(tool)
    return {"name": "Aether", "status": runtime.status(), "tool": tool, "timeline_event": timeline_event, "graph_relationships": graph_relationships, "warnings": warnings}


def handle_seed_action_tools() -> dict:
    result = seed_default_tools()
    runtime.working_memory.add_event(
        role="aether",
        content=f"Tool Registry seeded with {result['created_count']} new tools.",
        event_type="tool_registry_seeded",
        metadata={"tool_count": len(result["tools"]), "created_count": result["created_count"]},
    )
    timeline_events = []
    warnings = []
    for tool in result["tools"]:
        if tool["risk_level"] == "high" and tool["id"] in result["created_tool_ids"]:
            timeline_events.append(_record_tool_timeline(tool, f"Tool registered: {tool['id']}", f"Aether registered tool {tool['id']} with risk level {tool['risk_level']}."))
        _, graph_warnings = _add_tool_graph_relationships(tool)
        warnings.extend(graph_warnings)
    return {"name": "Aether", "status": runtime.status(), "result": result, "tool_registry": tool_registry_status(), "timeline_events": timeline_events, "warnings": warnings}


def handle_list_action_tools(category: str | None = None, enabled: bool | None = None, limit: int = 100) -> dict:
    return {"name": "Aether", "status": runtime.status(), "tools": list_tools(category, enabled, limit)}


def handle_get_action_tool(tool_id: str) -> dict:
    return {"name": "Aether", "status": runtime.status(), "tool": get_tool(tool_id)}


def handle_search_action_tools(query: str, limit: int = 20) -> dict:
    return {"name": "Aether", "status": runtime.status(), "query": query, "tools": search_tools(query, limit)}


def handle_enable_action_tool(tool_id: str) -> dict:
    return _change_tool_enabled(tool_id, True)


def handle_disable_action_tool(tool_id: str) -> dict:
    return _change_tool_enabled(tool_id, False)


def handle_update_action_tool_policy(
    tool_id: str,
    risk_level: str | None = None,
    requires_verification: bool | None = None,
    requires_user_approval: bool | None = None,
    allow_auto_execute: bool | None = None,
) -> dict:
    tool = update_tool_policy(
        tool_id=tool_id,
        risk_level=risk_level,
        requires_verification=requires_verification,
        requires_user_approval=requires_user_approval,
        allow_auto_execute=allow_auto_execute,
    )
    if tool is None:
        return {"name": "Aether", "status": runtime.status(), "tool": None, "warnings": ["Tool was not found."]}
    _add_tool_working_memory_event(tool, "tool_policy_updated")
    timeline_event = None
    if tool["risk_level"] == "high":
        timeline_event = _record_tool_timeline(tool, f"Tool policy updated: {tool['id']}", f"Aether updated policy for high-risk tool {tool['id']}.")
    graph_relationships, warnings = _add_tool_graph_relationships(tool, policy_only=True)
    return {"name": "Aether", "status": runtime.status(), "tool": tool, "timeline_event": timeline_event, "graph_relationships": graph_relationships, "warnings": warnings}
