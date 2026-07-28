"""Apply Execution Gate Service — Thin Interface Refactor Phase 3 (Milestone 80D).

Moves Milestone 69-70 orchestration out of api_server.py into this service module.

This module handles:
- Apply execution gate request creation (build + persist + response shaping)
- Apply execution gate record CRUD (list, get, cancel, reject, approve intent)

Behavior-preserving refactor: no endpoint path, response shape, or safety changes.
"""

from aether.core.runtime import runtime

from aether.action.apply_execution_gate_request import (
    build_apply_execution_gate_request as _build_aegr,
)
from aether.action.apply_execution_gate_queue import (
    create_apply_execution_gate_record as _create_aegr,
    get_apply_execution_gate_record as _get_aeg,
    list_apply_execution_gate_records as _list_aeg,
    update_apply_execution_gate_record_status as _update_aeg,
)
from aether.action.human_authorization_queue import (
    get_human_authorization_record as _get_ha_rec,
)


# --------------------------------------------------------------------------- #
# A. Apply Execution Gate Create
# POST /human-authorizations/{id}/apply-execution-gate-request
# --------------------------------------------------------------------------- #


def handle_apply_execution_gate_create(
    human_authorization_id: str,
    context: dict | None = None,
) -> dict:
    """Build an apply execution gate request from a human authorization record and persist it."""
    record = _get_ha_rec(human_authorization_id)
    aegr = _build_aegr(record, context)
    persisted_record = _create_aegr(aegr, context)
    apply_exec_gate_id = persisted_record["apply_execution_gate_id"]

    return {
        "name": "Aether",
        "status": runtime.status(),
        "human_authorization_record": record,
        "apply_execution_gate_request": aegr,
        "apply_execution_gate_record": persisted_record,
        "apply_execution_gate_id": apply_exec_gate_id,
        "apply_execution_gate_required": aegr.get("apply_execution_gate_required"),
        "apply_execution_gate_status": aegr.get("apply_execution_gate_status"),
        "decision": aegr.get("decision"),
        "human_review_completed": aegr.get("human_review_completed"),
        "human_intent_recorded": aegr.get("human_intent_recorded"),
        "execution_review_completed": persisted_record.get("execution_review_completed", False),
        "execution_intent_recorded": persisted_record.get("execution_intent_recorded", False),
        "apply_authorized": False,
        "apply_allowed": False,
        "rollback_allowed": False,
        "execution_allowed": False,
        "tool_execution_allowed": False,
        "dry_run_execution_allowed": False,
        "simulation_execution_allowed": False,
        "apply_gate_execution_allowed": False,
        "human_authorization_execution_allowed": False,
        "apply_execution_gate_execution_allowed": False,
    }


# --------------------------------------------------------------------------- #
# B. Apply Execution Gate Record: List
# GET /apply-execution-gates
# --------------------------------------------------------------------------- #


def handle_list_apply_execution_gates(
    status: str | None = None,
    decision: str | None = None,
    limit: int = 50,
) -> dict:
    """List apply execution gate records."""
    records = _list_aeg(status=status, decision=decision, limit=limit)
    return {
        "name": "Aether",
        "status": runtime.status(),
        "apply_execution_gates": records,
        "count": len(records),
    }


# --------------------------------------------------------------------------- #
# C. Apply Execution Gate Record: Get
# GET /apply-execution-gates/{id}
# --------------------------------------------------------------------------- #


def handle_get_apply_execution_gate(
    gate_id: str,
) -> dict:
    """Get a single apply execution gate record."""
    record = _get_aeg(gate_id)
    if record is None:
        return {
            "name": "Aether",
            "status": runtime.status(),
            "apply_execution_gate": None,
            "found": False,
        }
    return {
        "name": "Aether",
        "status": runtime.status(),
        "apply_execution_gate": record,
        "found": True,
    }


# --------------------------------------------------------------------------- #
# D. Apply Execution Gate Record: Cancel
# POST /apply-execution-gates/{id}/cancel
# --------------------------------------------------------------------------- #


def handle_cancel_apply_execution_gate(
    gate_id: str,
    reviewer: str | None = None,
    reason: str | None = None,
) -> dict:
    """Cancel an apply execution gate record."""
    record = _update_aeg(
        gate_id, decision="cancelled", reviewer=reviewer, reason=reason
    )
    if record is None:
        return {
            "name": "Aether",
            "status": runtime.status(),
            "apply_execution_gate": None,
            "found": False,
        }
    return {
        "name": "Aether",
        "status": runtime.status(),
        "apply_execution_gate": record,
        "found": True,
    }


# --------------------------------------------------------------------------- #
# E. Apply Execution Gate Record: Reject
# POST /apply-execution-gates/{id}/reject
# --------------------------------------------------------------------------- #


def handle_reject_apply_execution_gate(
    gate_id: str,
    reviewer: str | None = None,
    reason: str | None = None,
) -> dict:
    """Reject an apply execution gate record."""
    record = _update_aeg(
        gate_id, decision="rejected", reviewer=reviewer, reason=reason
    )
    if record is None:
        return {
            "name": "Aether",
            "status": runtime.status(),
            "apply_execution_gate": None,
            "found": False,
        }
    return {
        "name": "Aether",
        "status": runtime.status(),
        "apply_execution_gate": record,
        "found": True,
    }


# --------------------------------------------------------------------------- #
# F. Apply Execution Gate Record: Approve Execution Intent
# POST /apply-execution-gates/{id}/approve-execution-intent
# --------------------------------------------------------------------------- #


def handle_approve_execution_intent(
    gate_id: str,
    reviewer: str | None = None,
    reason: str | None = None,
    confirmations: list[str] | None = None,
) -> dict:
    """Approve execution intent on an apply execution gate record."""
    record = _update_aeg(
        gate_id,
        decision="approved_execution_intent",
        reviewer=reviewer,
        reason=reason,
        confirmations=confirmations,
    )
    if record is None:
        return {
            "name": "Aether",
            "status": runtime.status(),
            "apply_execution_gate": None,
            "found": False,
        }
    return {
        "name": "Aether",
        "status": runtime.status(),
        "apply_execution_gate": record,
        "found": True,
    }
