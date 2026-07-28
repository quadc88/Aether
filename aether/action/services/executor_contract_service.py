"""Executor Contract Service — Thin Interface Refactor Phase 3 (Milestone 80D).

Moves Milestone 71-72 orchestration out of api_server.py into this service module.

This module handles:
- Executor contract creation (build + persist + response shaping)
- Executor contract record CRUD (list, get, cancel, reject, approve contract intent)

Behavior-preserving refactor: no endpoint path, response shape, or safety changes.
"""

from aether.core.runtime import runtime

from aether.action.apply_executor_contract import (
    build_apply_executor_contract as _build_aec,
)
from aether.action.apply_executor_contract_queue import (
    create_apply_executor_contract_record as _create_aecri,
    get_apply_executor_contract_record as _get_aecr,
    list_apply_executor_contract_records as _list_aecr,
    update_apply_executor_contract_record_status as _update_aecr,
)
from aether.action.apply_execution_gate_queue import (
    get_apply_execution_gate_record as _get_aeg,
)


# --------------------------------------------------------------------------- #
# A. Executor Contract Create
# POST /apply-execution-gates/{id}/executor-contract
# --------------------------------------------------------------------------- #


def handle_executor_contract_create(
    apply_execution_gate_id: str,
    context: dict | None = None,
) -> dict:
    """Build an apply executor contract from an execution gate record and persist it."""
    aeg_record = _get_aeg(apply_execution_gate_id)
    contract = _build_aec(aeg_record, context)
    persisted = _create_aecri(contract, context)

    return {
        "name": "Aether",
        "status": runtime.status(),
        "apply_execution_gate_record": aeg_record,
        "apply_executor_contract": contract,
        "apply_executor_contract_record": persisted,
        "apply_executor_contract_id": persisted.get("apply_executor_contract_id"),
        "contract_required": contract.get("contract_required"),
        "contract_status": contract.get("contract_status"),
        "decision": contract.get("decision"),
        "contract_review_completed": persisted.get("contract_review_completed", False),
        "contract_intent_recorded": persisted.get("contract_intent_recorded", False),
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
    }


# --------------------------------------------------------------------------- #
# B. Executor Contract Record: List
# GET /apply-executor-contracts
# --------------------------------------------------------------------------- #


def handle_list_executor_contracts(
    status: str | None = None,
    decision: str | None = None,
    limit: int = 50,
) -> dict:
    """List apply executor contract records."""
    records = _list_aecr(status=status, decision=decision, limit=limit)
    return {
        "name": "Aether",
        "status": runtime.status(),
        "apply_executor_contracts": records,
        "count": len(records),
    }


# --------------------------------------------------------------------------- #
# C. Executor Contract Record: Get
# GET /apply-executor-contracts/{id}
# --------------------------------------------------------------------------- #


def handle_get_executor_contract(
    contract_id: str,
) -> dict:
    """Get a single apply executor contract record."""
    record = _get_aecr(contract_id)
    if record is None:
        return {
            "name": "Aether",
            "status": runtime.status(),
            "apply_executor_contract": None,
            "found": False,
        }
    return {
        "name": "Aether",
        "status": runtime.status(),
        "apply_executor_contract": record,
        "found": True,
    }


# --------------------------------------------------------------------------- #
# D. Executor Contract Record: Cancel
# POST /apply-executor-contracts/{id}/cancel
# --------------------------------------------------------------------------- #


def handle_cancel_executor_contract(
    contract_id: str,
    reviewer: str | None = None,
    reason: str | None = None,
) -> dict:
    """Cancel an apply executor contract record."""
    record = _update_aecr(
        contract_id, decision="cancelled", reviewer=reviewer, reason=reason
    )
    if record is None:
        return {
            "name": "Aether",
            "status": runtime.status(),
            "apply_executor_contract": None,
            "found": False,
        }
    return {
        "name": "Aether",
        "status": runtime.status(),
        "apply_executor_contract": record,
        "found": True,
    }


# --------------------------------------------------------------------------- #
# E. Executor Contract Record: Reject
# POST /apply-executor-contracts/{id}/reject
# --------------------------------------------------------------------------- #


def handle_reject_executor_contract(
    contract_id: str,
    reviewer: str | None = None,
    reason: str | None = None,
) -> dict:
    """Reject an apply executor contract record."""
    record = _update_aecr(
        contract_id, decision="rejected", reviewer=reviewer, reason=reason
    )
    if record is None:
        return {
            "name": "Aether",
            "status": runtime.status(),
            "apply_executor_contract": None,
            "found": False,
        }
    return {
        "name": "Aether",
        "status": runtime.status(),
        "apply_executor_contract": record,
        "found": True,
    }


# --------------------------------------------------------------------------- #
# F. Executor Contract Record: Approve Contract Intent
# POST /apply-executor-contracts/{id}/approve-contract-intent
# --------------------------------------------------------------------------- #


def handle_approve_contract_intent(
    contract_id: str,
    reviewer: str | None = None,
    reason: str | None = None,
    confirmations: list[str] | None = None,
) -> dict:
    """Approve contract intent on an apply executor contract record."""
    record = _update_aecr(
        contract_id,
        decision="approved_contract_intent",
        reviewer=reviewer,
        reason=reason,
        confirmations=confirmations,
    )
    if record is None:
        return {
            "name": "Aether",
            "status": runtime.status(),
            "apply_executor_contract": None,
            "found": False,
        }
    return {
        "name": "Aether",
        "status": runtime.status(),
        "apply_executor_contract": record,
        "found": True,
    }
