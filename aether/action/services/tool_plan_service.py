"""Tool Plan Service — Thin Interface Refactor Phase 7 (Milestone 80I).

Moves tool plan orchestration from api_server.py into this service module.

Behavior-preserving refactor: no endpoint path, response shape, or safety changes.
"""

from aether.core.runtime import runtime

from aether.memory.timeline.recorder import record_event
from aether.memory.graph.store import add_edge

from aether.action.tool_planner import (
    create_tool_invocation_plan,
    get_tool_plan,
    list_tool_plans,
    tool_planner_status,
)


def handle_create_action_tool_plan(
    text: str,
    proposed_action: str | None = None,
    metadata: dict | None = None,
    create_approval_if_required: bool = False,
) -> dict:
    plan = create_tool_invocation_plan(
        text=text,
        proposed_action=proposed_action,
        metadata=metadata,
        create_approval_if_required=create_approval_if_required,
    )
    decision = plan["decision"]
    tool_id = plan["candidate_tool"]["tool_id"]
    runtime.working_memory.add_event(
        role="aether",
        content=f"Tool invocation plan created: {tool_id or 'no tool'}.",
        event_type="tool_invocation_plan_created",
        metadata={
            "plan_id": plan["id"],
            "tool_id": tool_id,
            "plan_status": decision["plan_status"],
            "risk_level": decision["risk_level"],
            "requires_user_approval": decision["requires_user_approval"],
            "approval_item_created": decision["approval_item_created"],
        },
    )
    timeline_event = None
    if decision["plan_status"] in {"approval_required", "blocked", "tool_disabled"} or decision["approval_item_created"]:
        timeline_event = record_event(
            event_type="tool_planning",
            title=f"Tool invocation plan: {tool_id or 'no tool'}",
            description=f"Aether created a tool invocation plan with status {decision['plan_status']}.",
            importance="high" if decision["requires_user_approval"] or decision["plan_status"] in {"blocked", "tool_disabled"} else "normal",
        )
    warnings = []
    graph_relationships = []
    try:
        graph_relationships.append(add_edge("Aether", "created_tool_plan", plan["id"]))
        if tool_id:
            graph_relationships.append(add_edge(plan["id"], "planned_tool", tool_id))
        graph_relationships.append(add_edge(plan["id"], "has_status", decision["plan_status"]))
        if plan["approval_item"]:
            graph_relationships.append(add_edge(plan["id"], "created_approval_item", plan["approval_item"]["id"]))
        for relationship in graph_relationships:
            relationship.pop("created_new", None)
    except Exception as error:
        warnings.append(f"Graph Memory integration was unavailable: {error}")
    return {"name": "Aether", "status": runtime.status(), "plan": plan, "timeline_event": timeline_event, "graph_relationships": graph_relationships, "warnings": warnings}


def handle_get_tool_plan_status() -> dict:
    return {"name": "Aether", "status": runtime.status(), "tool_planner": tool_planner_status()}


def handle_list_action_tool_plans(limit: int = 50) -> dict:
    return {"name": "Aether", "status": runtime.status(), "plans": list_tool_plans(limit)}


def handle_get_action_tool_plan(plan_id: str) -> dict:
    return {"name": "Aether", "status": runtime.status(), "plan": get_tool_plan(plan_id)}
