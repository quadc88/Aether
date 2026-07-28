"""Executor Plan Service — Thin Interface Refactor Phase 2 (Milestone 80C).

Moves Milestone 73-74 orchestration out of api_server.py into this service module.

This module handles:
- Executor plan creation (build + persist + response shaping)
- Executor plan record CRUD (list, get, cancel, reject, approve plan intent)

Behavior-preserving refactor: no endpoint path, response shape, or safety changes.
"""

from aether.core.runtime import runtime

from aether.action.apply_executor_plan import (
    build_apply_executor_plan as _build_aep,
)
from aether.action.apply_executor_plan_queue import (
    create_apply_executor_plan_record as _create_aepr,
    get_apply_executor_plan_record as _get_aep,
    list_apply_executor_plan_records as _list_aep,
    update_apply_executor_plan_record_status as _update_aep,
)
from aether.action.apply_executor_contract_queue import (
    get_apply_executor_contract_record as _get_aecr,
)


# --------------------------------------------------------------------------- #
# A. Executor Plan Create
# POST /apply-executor-contracts/{id}/executor-plan
# --------------------------------------------------------------------------- #


def handle_executor_plan_create(
    apply_executor_contract_id: str,
    context: dict | None = None,
) -> dict:
    """Build an apply executor plan from a contract record and persist it."""
    aecr_record = _get_aecr(apply_executor_contract_id)
    plan = _build_aep(aecr_record, context)
    persisted = _create_aepr(plan, context)

    return {
        "name": "Aether",
        "status": runtime.status(),
        "apply_executor_contract_record": aecr_record,
        "apply_executor_plan": plan,
        "apply_executor_plan_record": persisted,
        "apply_executor_plan_id": persisted.get("apply_executor_plan_id"),
        "plan_required": plan.get("plan_required"),
        "plan_status": plan.get("plan_status"),
        "decision": plan.get("decision"),
        "contract_review_completed": aecr_record.get("contract_review_completed") if aecr_record else False,
        "contract_intent_recorded": aecr_record.get("contract_intent_recorded") if aecr_record else False,
        "plan_review_completed": persisted.get("plan_review_completed", False),
        "plan_intent_recorded": persisted.get("plan_intent_recorded", False),
        "evidence_collected": persisted.get("evidence_collected", False),
        "rollback_plan_attached": persisted.get("rollback_plan_attached", False),
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
        "apply_executor_contract_execution_allowed": False,
        "apply_executor_plan_execution_allowed": False,
    }


# --------------------------------------------------------------------------- #
# B. Executor Plan Record: List
# GET /apply-executor-plans
# --------------------------------------------------------------------------- #


def handle_list_executor_plans(
    status: str | None = None,
    decision: str | None = None,
    limit: int = 50,
) -> dict:
    """List apply executor plan records."""
    records = _list_aep(status=status, decision=decision, limit=limit)
    return {
        "name": "Aether",
        "status": runtime.status(),
        "apply_executor_plans": records,
        "count": len(records),
    }


# --------------------------------------------------------------------------- #
# C. Executor Plan Record: Get
# GET /apply-executor-plans/{id}
# --------------------------------------------------------------------------- #


def handle_get_executor_plan(
    plan_id: str,
) -> dict:
    """Get a single apply executor plan record."""
    record = _get_aep(plan_id)
    if record is None:
        return {
            "name": "Aether",
            "status": runtime.status(),
            "apply_executor_plan": None,
            "found": False,
        }
    return {
        "name": "Aether",
        "status": runtime.status(),
        "apply_executor_plan": record,
        "found": True,
    }


# --------------------------------------------------------------------------- #
# D. Executor Plan Record: Cancel
# POST /apply-executor-plans/{id}/cancel
# --------------------------------------------------------------------------- #


def handle_cancel_executor_plan(
    plan_id: str,
    reviewer: str | None = None,
    reason: str | None = None,
) -> dict:
    """Cancel an apply executor plan record."""
    record = _update_aep(
        plan_id, decision="cancelled", reviewer=reviewer, reason=reason
    )
    if record is None:
        return {
            "name": "Aether",
            "status": runtime.status(),
            "apply_executor_plan": None,
            "found": False,
        }
    return {
        "name": "Aether",
        "status": runtime.status(),
        "apply_executor_plan": record,
        "found": True,
    }


# --------------------------------------------------------------------------- #
# E. Executor Plan Record: Reject
# POST /apply-executor-plans/{id}/reject
# --------------------------------------------------------------------------- #


def handle_reject_executor_plan(
    plan_id: str,
    reviewer: str | None = None,
    reason: str | None = None,
) -> dict:
    """Reject an apply executor plan record."""
    record = _update_aep(
        plan_id, decision="rejected", reviewer=reviewer, reason=reason
    )
    if record is None:
        return {
            "name": "Aether",
            "status": runtime.status(),
            "apply_executor_plan": None,
            "found": False,
        }
    return {
        "name": "Aether",
        "status": runtime.status(),
        "apply_executor_plan": record,
        "found": True,
    }


# --------------------------------------------------------------------------- #
# F. Executor Plan Record: Approve Plan Intent
# POST /apply-executor-plans/{id}/approve-plan-intent
# --------------------------------------------------------------------------- #


def handle_approve_executor_plan_intent(
    plan_id: str,
    reviewer: str | None = None,
    reason: str | None = None,
    confirmations: list[str] | None = None,
) -> dict:
    """Approve plan intent on an apply executor plan record."""
    record = _update_aep(
        plan_id,
        decision="approved_plan_intent",
        reviewer=reviewer,
        reason=reason,
        confirmations=confirmations,
    )
    if record is None:
        return {
            "name": "Aether",
            "status": runtime.status(),
            "apply_executor_plan": None,
            "found": False,
        }
    return {
        "name": "Aether",
        "status": runtime.status(),
        "apply_executor_plan": record,
        "found": True,
    }
