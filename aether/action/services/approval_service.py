"""Approval Service — Thin Interface Refactor Phase 6 (Milestone 80G).

Moves approval and approval-decision-gate orchestration from api_server.py into
this service module.  Covers three endpoint groups:

1. Legacy /action/approval/* (create, status, list, get, approve, reject, cancel)
2. Milestone 54A /approvals/* (list, get, approve, reject, cancel)
3. Milestone 55A /approvals/{id}/validate-action

Behavior-preserving refactor: no endpoint path, response shape, or safety changes.
"""

from aether.core.runtime import runtime

from aether.memory.timeline.recorder import record_event
from aether.memory.graph.store import add_edge
from aether.verification.risk import verification_plan

from aether.action.approval_queue import (
    approval_queue_status,
    create_approval_item,
    get_approval_item,
    list_approval_items,
    approve_item,
    reject_item,
    cancel_item,
    get_approval_record,
    list_approval_records,
    update_approval_record_status,
)
from aether.action.approval_decision_gate import (
    validate_approval_for_action as _validate_action,
)


# --------------------------------------------------------------------------- #
# Internal helpers
# --------------------------------------------------------------------------- #


def _add_approval_working_memory_event(item: dict, event_type: str) -> None:
    runtime.working_memory.add_event(
        role="aether",
        content=f"Approval item {item['status']}: {item['id']}",
        event_type=event_type,
        metadata={
            "approval_id": item["id"],
            "action_type": item["action_type"],
            "risk_level": item["risk_level"],
            "status": item["status"],
        },
    )


def _record_approval_decision(approval_id: str, decision_reason: str, decision: str) -> dict:
    decision_functions = {"approved": approve_item, "rejected": reject_item, "cancelled": cancel_item}
    item = decision_functions[decision](approval_id, decision_reason)
    if item is None:
        return {"name": "Aether", "status": runtime.status(), "item": None, "warnings": ["Approval item was not found."]}
    if item.get("warning"):
        return {"name": "Aether", "status": runtime.status(), "item": item, "warnings": [item["warning"]]}

    _add_approval_working_memory_event(item, f"approval_item_{decision}")
    timeline_event = record_event(
        event_type="action_approval_decision",
        title=f"Approval item {decision}: {approval_id}",
        description=f"User decision recorded for approval item {approval_id}.",
        importance="high",
    )
    warnings = []
    graph_relationship = None
    try:
        graph_relationship = add_edge(approval_id, "has_decision", decision)
        graph_relationship.pop("created_new", None)
    except Exception as error:
        warnings.append(f"Graph Memory integration was unavailable: {error}")
    return {
        "name": "Aether",
        "status": runtime.status(),
        "item": item,
        "timeline_event": timeline_event,
        "graph_relationship": graph_relationship,
        "warnings": warnings,
    }


# --------------------------------------------------------------------------- #
# A. Legacy /action/approval/* endpoints
# --------------------------------------------------------------------------- #


def handle_action_approval_create(
    request_text: str,
    proposed_action: str,
    metadata: dict | None = None,
) -> dict:
    """Create a legacy approval item with timeline, graph, and working-memory events."""
    if metadata is None:
        metadata = {}
    plan = verification_plan(request_text)
    item = create_approval_item(
        request_text=request_text,
        proposed_action=proposed_action,
        verification_plan=plan,
        metadata=metadata,
    )
    _add_approval_working_memory_event(item, "approval_item_created")
    warnings = []
    timeline_event = None
    graph_relationship = None
    if item["risk_level"] == "high":
        timeline_event = record_event(
            event_type="action_approval",
            title=f"Approval item created: {item['action_type']}",
            description=f"Aether created an approval item for a {item['risk_level']}-risk action.",
            importance="high",
        )
    try:
        graph_relationship = add_edge("Aether", "created_approval_item_for", item["action_type"])
        graph_relationship.pop("created_new", None)
    except Exception as error:
        warnings.append(f"Graph Memory integration was unavailable: {error}")
    return {
        "name": "Aether",
        "status": runtime.status(),
        "item": item,
        "approval_optional": not item["requires_user_approval"],
        "queue_status": approval_queue_status(),
        "timeline_event": timeline_event,
        "graph_relationship": graph_relationship,
        "warnings": warnings,
    }


def handle_action_approval_status() -> dict:
    """Get legacy approval queue status."""
    return {"name": "Aether", "status": runtime.status(), "approval_queue": approval_queue_status()}


def handle_list_action_approvals(status: str | None = None, limit: int = 50) -> dict:
    """List legacy approval items."""
    return {"name": "Aether", "status": runtime.status(), "items": list_approval_items(status, limit)}


def handle_get_action_approval(approval_id: str) -> dict:
    """Get a single legacy approval item."""
    return {"name": "Aether", "status": runtime.status(), "item": get_approval_item(approval_id)}


def handle_approve_action_approval(approval_id: str, decision_reason: str = "") -> dict:
    """Approve a legacy approval item."""
    return _record_approval_decision(approval_id, decision_reason, "approved")


def handle_reject_action_approval(approval_id: str, decision_reason: str = "") -> dict:
    """Reject a legacy approval item."""
    return _record_approval_decision(approval_id, decision_reason, "rejected")


def handle_cancel_action_approval(approval_id: str, decision_reason: str = "") -> dict:
    """Cancel a legacy approval item."""
    return _record_approval_decision(approval_id, decision_reason, "cancelled")


# --------------------------------------------------------------------------- #
# B. Milestone 54A /approvals/* endpoints  (individual-file record store)
# --------------------------------------------------------------------------- #


def handle_list_approvals(status: str | None = None, decision: str | None = None, limit: int = 50) -> dict:
    """List approval records (individual-file store)."""
    records = list_approval_records(status=status, limit=limit)
    return {
        "name": "Aether",
        "status": runtime.status(),
        "approvals": records,
        "count": len(records),
    }


def handle_get_approval(approval_id: str) -> dict:
    """Get a single approval record."""
    record = get_approval_record(approval_id)
    return {
        "name": "Aether",
        "status": runtime.status(),
        "approval": record,
        "found": record is not None,
    }


def _handle_approval_record_decision(approval_id: str, decision: str, reviewer: str | None = None, reason: str | None = None) -> dict:
    """Update an approval record's status (approve / reject / cancel)."""
    record = update_approval_record_status(
        approval_id, decision=decision, reviewer=reviewer, reason=reason
    )
    if record is None:
        return {
            "name": "Aether",
            "status": runtime.status(),
            "approval": None,
            "found": False,
            "warnings": ["Approval record not found."],
        }
    return {
        "name": "Aether",
        "status": runtime.status(),
        "approval": record,
        "found": True,
    }


def handle_approve_approval(approval_id: str, reviewer: str | None = None, reason: str | None = None) -> dict:
    """Approve an approval record."""
    return _handle_approval_record_decision(approval_id, "approved", reviewer, reason)


def handle_reject_approval(approval_id: str, reviewer: str | None = None, reason: str | None = None) -> dict:
    """Reject an approval record."""
    return _handle_approval_record_decision(approval_id, "rejected", reviewer, reason)


def handle_cancel_approval(approval_id: str, reviewer: str | None = None, reason: str | None = None) -> dict:
    """Cancel an approval record."""
    return _handle_approval_record_decision(approval_id, "cancelled", reviewer, reason)


# --------------------------------------------------------------------------- #
# C. Milestone 55A — Approval Decision Gate
# POST /approvals/{approval_id}/validate-action
# --------------------------------------------------------------------------- #


def handle_validate_action(
    approval_id: str,
    requested_action: dict | None = None,
    context: dict | None = None,
) -> dict:
    """Validate a requested action against an approved approval record."""
    result = _validate_action(
        approval_id=approval_id,
        requested_action=requested_action,
        context=context,
    )
    return {
        "name": "Aether",
        "status": runtime.status(),
        **result,
    }
