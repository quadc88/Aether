"""Evidence Contract Service — Thin Interface Refactor Phase 2 (Milestone 80C).

Moves Milestone 75-76 orchestration out of api_server.py into this service module.

This module handles:
- Evidence contract creation (build + persist + response shaping)
- Evidence contract record CRUD (list, get, cancel, reject, approve intent)

Behavior-preserving refactor: no endpoint path, response shape, or safety changes.
"""

from aether.core.runtime import runtime

from aether.action.apply_executor_plan_queue import (
    get_apply_executor_plan_record as _get_aep,
)
from aether.action.apply_executor_evidence_contract import (
    build_apply_executor_evidence_contract as _build_aeecc,
)
from aether.action.apply_executor_evidence_contract_queue import (
    create_apply_executor_evidence_contract_record as _create_aeecr,
    get_apply_executor_evidence_contract_record as _get_aeec,
    list_apply_executor_evidence_contract_records as _list_aeec,
    update_apply_executor_evidence_contract_record_status as _update_aeec,
)


# --------------------------------------------------------------------------- #
# Helper: fallback contract for missing record cases
# --------------------------------------------------------------------------- #


def _build_fallback_contract() -> dict:
    """Create a default blocked evidence contract for missing record cases."""
    return {
        "evidence_contract_required": False,
        "evidence_contract_status": None,
        "contract_type": "apply_executor_evidence_contract",
        "decision": "blocked",
        "reason": "Apply executor plan record not found.",
        "apply_executor_plan_id": None,
        "apply_executor_plan_record_status": None,
        "plan_decision": None,
        "apply_executor_contract_id": None,
        "apply_execution_gate_id": None,
        "human_authorization_id": None,
        "apply_gate_id": None,
        "verification_verdict_id": None,
        "simulation_result_id": None,
        "simulation_plan_id": None,
        "dry_run_id": None,
        "requested_action": None,
        "apply_executor_plan_snapshot": None,
        "evidence_contract_checks": [],
        "required_evidence_items": [],
        "pre_execution_evidence_requirements": [],
        "during_execution_evidence_requirements": [],
        "post_execution_evidence_requirements": [],
        "rollback_evidence_requirements": [],
        "audit_evidence_requirements": [],
        "evidence_collection_constraints": {},
        "evidence_acceptance_criteria": [],
        "required_evidence_confirmations": [],
        "evidence_contract_statement": None,
        "blocking_reasons": ["Apply executor plan record not found."],
        "unresolved_risks": [{"name": "missing_apply_executor_plan", "severity": "high", "detail": "Apply executor plan record not found."}],
        "recommended_next_step": "Create or provide a valid apply executor plan record.",
        "plan_review_completed": False,
        "plan_intent_recorded": False,
        "evidence_collected": False,
        "rollback_plan_attached": False,
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
        "apply_executor_evidence_contract_execution_allowed": False,
        "metadata": {"source": "apply_executor_evidence_contract_builder", "schema_version": "1.0"},
        "warnings": [
            "Apply executor evidence contract does not authorize execution.",
            "Apply executor evidence contract does not authorize apply.",
            "Evidence requirements are declared but not collected.",
            "Rollback evidence is required but not collected in this milestone.",
            "A separate future evidence collector is required before apply can occur.",
        ],
    }


# --------------------------------------------------------------------------- #
# A. Evidence Contract Create
# POST /apply-executor-plans/{id}/evidence-contract
# --------------------------------------------------------------------------- #


def handle_evidence_contract_create(
    apply_executor_plan_id: str,
    context: dict | None = None,
) -> dict:
    """Build an apply executor evidence contract from a plan record and persist it.

    Creates a structured evidence requirements object, persists it as
    an apply executor evidence contract record per Milestone 76A safety.
    """
    plan_record = _get_aep(apply_executor_plan_id)
    if plan_record is None:
        contract = _build_fallback_contract()
        eec_record = _create_aeecr(dict(contract), context)
        return {
            "name": "Aether",
            "status": runtime.status(),
            "apply_executor_plan_record": None,
            "apply_executor_evidence_contract": contract,
            "apply_executor_evidence_contract_record": eec_record,
            "apply_executor_evidence_contract_id": eec_record.get("apply_executor_evidence_contract_id"),
            "evidence_contract_required": False,
            "evidence_contract_status": None,
            "decision": "blocked",
            "plan_review_completed": False,
            "plan_intent_recorded": False,
            "evidence_collected": False,
            "rollback_plan_attached": False,
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
            "apply_executor_evidence_contract_execution_allowed": False,
        }

    contract = _build_aeecc(plan_record, context)
    eec_record = _create_aeecr(dict(contract), context)

    return {
        "name": "Aether",
        "status": runtime.status(),
        "apply_executor_plan_record": plan_record,
        "apply_executor_evidence_contract": contract,
        "apply_executor_evidence_contract_record": eec_record,
        "apply_executor_evidence_contract_id": eec_record["apply_executor_evidence_contract_id"],
        "evidence_contract_required": contract.get("evidence_contract_required"),
        "evidence_contract_status": contract.get("evidence_contract_status"),
        "decision": contract.get("decision"),
        "plan_review_completed": contract.get("plan_review_completed"),
        "plan_intent_recorded": contract.get("plan_intent_recorded"),
        "evidence_collected": False,
        "rollback_plan_attached": False,
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
        "apply_executor_evidence_contract_execution_allowed": False,
    }


# --------------------------------------------------------------------------- #
# B. Evidence Contract Record: List
# GET /apply-executor-evidence-contracts
# --------------------------------------------------------------------------- #


def handle_list_evidence_contracts(
    status: str | None = None,
    decision: str | None = None,
    limit: int = 50,
) -> dict:
    """List apply executor evidence contract records."""
    records = _list_aeec(status=status, decision=decision, limit=limit)
    return {
        "name": "Aether",
        "status": runtime.status(),
        "apply_executor_evidence_contracts": records,
        "count": len(records),
    }


# --------------------------------------------------------------------------- #
# C. Evidence Contract Record: Get
# GET /apply-executor-evidence-contracts/{id}
# --------------------------------------------------------------------------- #


def handle_get_evidence_contract(
    evidence_contract_id: str,
) -> dict:
    """Get a single apply executor evidence contract record."""
    record = _get_aeec(evidence_contract_id)
    if record is None:
        return {
            "name": "Aether",
            "status": runtime.status(),
            "apply_executor_evidence_contract": None,
            "found": False,
        }
    return {
        "name": "Aether",
        "status": runtime.status(),
        "apply_executor_evidence_contract": record,
        "found": True,
    }


# --------------------------------------------------------------------------- #
# D. Evidence Contract Record: Cancel
# POST /apply-executor-evidence-contracts/{id}/cancel
# --------------------------------------------------------------------------- #


def handle_cancel_evidence_contract(
    evidence_contract_id: str,
    reviewer: str | None = None,
    reason: str | None = None,
) -> dict:
    """Cancel an apply executor evidence contract record."""
    record = _update_aeec(
        evidence_contract_id, decision="cancelled", reviewer=reviewer, reason=reason
    )
    if record is None:
        return {
            "name": "Aether",
            "status": runtime.status(),
            "apply_executor_evidence_contract": None,
            "found": False,
            "warnings": ["Evidence contract record not found."],
        }
    return {
        "name": "Aether",
        "status": runtime.status(),
        "apply_executor_evidence_contract": record,
        "found": True,
    }


# --------------------------------------------------------------------------- #
# E. Evidence Contract Record: Reject
# POST /apply-executor-evidence-contracts/{id}/reject
# --------------------------------------------------------------------------- #


def handle_reject_evidence_contract(
    evidence_contract_id: str,
    reviewer: str | None = None,
    reason: str | None = None,
) -> dict:
    """Reject an apply executor evidence contract record."""
    record = _update_aeec(
        evidence_contract_id, decision="rejected", reviewer=reviewer, reason=reason
    )
    if record is None:
        return {
            "name": "Aether",
            "status": runtime.status(),
            "apply_executor_evidence_contract": None,
            "found": False,
            "warnings": ["Evidence contract record not found."],
        }
    return {
        "name": "Aether",
        "status": runtime.status(),
        "apply_executor_evidence_contract": record,
        "found": True,
    }


# --------------------------------------------------------------------------- #
# F. Evidence Contract Record: Approve Evidence Contract Intent
# POST /apply-executor-evidence-contracts/{id}/approve-evidence-contract-intent
# --------------------------------------------------------------------------- #


def handle_approve_evidence_contract_intent(
    evidence_contract_id: str,
    reviewer: str | None = None,
    reason: str | None = None,
    confirmations: list[str] | None = None,
) -> dict:
    """Approve evidence contract intent on an apply executor evidence contract record."""
    record = _update_aeec(
        evidence_contract_id,
        decision="approved_evidence_contract_intent",
        reviewer=reviewer,
        reason=reason,
        confirmations=confirmations,
    )
    if record is None:
        return {
            "name": "Aether",
            "status": runtime.status(),
            "apply_executor_evidence_contract": None,
            "found": False,
            "warnings": ["Evidence contract record not found."],
        }
    return {
        "name": "Aether",
        "status": runtime.status(),
        "apply_executor_evidence_contract": record,
        "found": True,
    }
