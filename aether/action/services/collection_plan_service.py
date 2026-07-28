"""Collection Plan Service — Thin Interface Refactor Phase 1 (Milestone 80B).

Moves Milestone 77-79 orchestration out of api_server.py into this service module.

This module handles:
- Evidence collection plan creation (build + persist + response shaping)
- Evidence collection plan record CRUD (list, get, reject, cancel, approve intent)
- Collector contract creation (build + response shaping, no persist)

Behavior-preserving refactor: no endpoint path, response shape, or safety changes.
"""

from aether.core.runtime import runtime

from aether.action.apply_executor_evidence_collection_plan import (
    build_apply_executor_evidence_collection_plan as _build_aeecp,
)
from aether.action.apply_executor_evidence_collector_contract import (
    build_apply_executor_evidence_collector_contract as _build_aeecp_collector,
)
from aether.action.apply_executor_evidence_contract_queue import (
    get_apply_executor_evidence_contract_record as _get_aeec,
)
from aether.action.apply_executor_evidence_collection_plan_queue import (
    create_apply_executor_evidence_collection_plan_record as _create_aeecp,
    get_apply_executor_evidence_collection_plan_record as _get_aeecp,
    list_apply_executor_evidence_collection_plan_records as _list_aeecp,
    update_apply_executor_evidence_collection_plan_record_status as _update_aeecp,
)


# --------------------------------------------------------------------------- #
# A. Evidence Collection Plan Create
# POST /apply-executor-evidence-contracts/{id}/evidence-collection-plan
# --------------------------------------------------------------------------- #


def handle_evidence_collection_plan_create(
    apply_executor_evidence_contract_id: str,
    context: dict | None = None,
) -> dict:
    """Build an apply executor evidence collection plan from an evidence contract record.

    Creates a structured evidence collection plan object without collecting evidence
    or authorizing execution per Milestone 77A safety.
    """
    record = _get_aeec(apply_executor_evidence_contract_id)
    if record is None:
        plan = _build_aeecp(None, context)
        return {
            "name": "Aether",
            "status": runtime.status(),
            "apply_executor_evidence_contract_record": None,
            "apply_executor_evidence_collection_plan": plan,
            "evidence_collection_plan_required": plan.get("evidence_collection_plan_required"),
            "evidence_collection_plan_status": plan.get("evidence_collection_plan_status"),
            "decision": plan.get("decision"),
            "evidence_contract_review_completed": record.get("evidence_contract_review_completed") if record else False,
            "evidence_contract_intent_recorded": record.get("evidence_contract_intent_recorded") if record else False,
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
            "apply_executor_evidence_collection_plan_execution_allowed": False,
        }

    plan = _build_aeecp(record, context)
    rec = _create_aeecp(plan, context)

    return {
        "name": "Aether",
        "status": runtime.status(),
        "apply_executor_evidence_contract_record": record,
        "apply_executor_evidence_collection_plan": plan,
        "apply_executor_evidence_collection_plan_record": rec,
        "apply_executor_evidence_collection_plan_id": rec["apply_executor_evidence_collection_plan_id"],
        "evidence_collection_plan_required": plan.get("evidence_collection_plan_required"),
        "evidence_collection_plan_status": plan.get("evidence_collection_plan_status"),
        "decision": plan.get("decision"),
        "evidence_contract_review_completed": record.get("evidence_contract_review_completed", False),
        "evidence_contract_intent_recorded": record.get("evidence_contract_intent_recorded", False),
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
        "apply_executor_evidence_collection_plan_execution_allowed": False,
    }


# --------------------------------------------------------------------------- #
# B. Evidence Collection Plan Record: List
# GET /apply-executor-evidence-collection-plans
# --------------------------------------------------------------------------- #


def handle_list_collection_plans(
    status: str | None = None,
    decision: str | None = None,
    limit: int = 50,
) -> dict:
    """List apply executor evidence collection plan records."""
    records = _list_aeecp(status=status, decision=decision, limit=limit)
    return {
        "name": "Aether",
        "status": runtime.status(),
        "apply_executor_evidence_collection_plans": records,
        "count": len(records),
    }


# --------------------------------------------------------------------------- #
# C. Evidence Collection Plan Record: Get
# GET /apply-executor-evidence-collection-plans/{id}
# --------------------------------------------------------------------------- #


def handle_get_collection_plan(
    collection_plan_id: str,
) -> dict:
    """Get a single apply executor evidence collection plan record."""
    record = _get_aeecp(collection_plan_id)
    return {
        "name": "Aether",
        "status": runtime.status(),
        "apply_executor_evidence_collection_plan": record,
        "found": record is not None,
    }


# --------------------------------------------------------------------------- #
# D. Evidence Collection Plan Record: Reject
# POST /apply-executor-evidence-collection-plans/{id}/reject
# --------------------------------------------------------------------------- #


def handle_reject_collection_plan(
    collection_plan_id: str,
    reviewer: str | None = None,
    reason: str | None = None,
) -> dict:
    """Reject an apply executor evidence collection plan record."""
    record = _update_aeecp(
        collection_plan_id, decision="rejected", reviewer=reviewer, reason=reason
    )
    if record is None:
        return {
            "name": "Aether",
            "status": runtime.status(),
            "apply_executor_evidence_collection_plan": None,
            "found": False,
            "warnings": ["Apply executor evidence collection plan not found."],
        }
    return {
        "name": "Aether",
        "status": runtime.status(),
        "apply_executor_evidence_collection_plan": record,
        "found": True,
    }


# --------------------------------------------------------------------------- #
# E. Evidence Collection Plan Record: Cancel
# POST /apply-executor-evidence-collection-plans/{id}/cancel
# --------------------------------------------------------------------------- #


def handle_cancel_collection_plan(
    collection_plan_id: str,
    reviewer: str | None = None,
    reason: str | None = None,
) -> dict:
    """Cancel an apply executor evidence collection plan record."""
    record = _update_aeecp(
        collection_plan_id, decision="cancelled", reviewer=reviewer, reason=reason
    )
    if record is None:
        return {
            "name": "Aether",
            "status": runtime.status(),
            "apply_executor_evidence_collection_plan": None,
            "found": False,
            "warnings": ["Apply executor evidence collection plan not found."],
        }
    return {
        "name": "Aether",
        "status": runtime.status(),
        "apply_executor_evidence_collection_plan": record,
        "found": True,
    }


# --------------------------------------------------------------------------- #
# F. Evidence Collection Plan Record: Approve Collection Plan Intent
# POST /apply-executor-evidence-collection-plans/{id}/approve-collection-plan-intent
# --------------------------------------------------------------------------- #


def handle_approve_collection_plan_intent(
    collection_plan_id: str,
    reviewer: str | None = None,
    reason: str | None = None,
    confirmations: list[str] | None = None,
) -> dict:
    """Approve collection plan intent on an apply executor evidence collection plan record."""
    record = _update_aeecp(
        collection_plan_id,
        decision="approved_collection_plan_intent",
        reviewer=reviewer,
        reason=reason,
        confirmations=confirmations,
    )
    if record is None:
        return {
            "name": "Aether",
            "status": runtime.status(),
            "apply_executor_evidence_collection_plan": None,
            "found": False,
            "warnings": ["Apply executor evidence collection plan not found or approval not possible."],
        }
    return {
        "name": "Aether",
        "status": runtime.status(),
        "apply_executor_evidence_collection_plan": record,
        "found": True,
    }


# --------------------------------------------------------------------------- #
# G. Collector Contract Create
# POST /apply-executor-evidence-collection-plans/{id}/collector-contract
# --------------------------------------------------------------------------- #


def handle_collector_contract_create(
    collection_plan_id: str,
    context: dict | None = None,
) -> dict:
    """Build an apply executor evidence collector contract from a collection plan record.

    Returns a structured collector contract without collecting evidence,
    authorizing execution, or modifying state per Milestone 79A safety.
    """
    record = _get_aeecp(collection_plan_id)
    if record is None:
        contract = _build_aeecp_collector(None, context)
        return {
            "name": "Aether",
            "status": runtime.status(),
            "apply_executor_evidence_collection_plan_record": None,
            "apply_executor_evidence_collector_contract": contract,
            "collector_contract_required": contract.get("collector_contract_required"),
            "collector_contract_status": contract.get("collector_contract_status"),
            "decision": contract.get("decision"),
            "evidence_collection_plan_review_completed": record.get("evidence_collection_plan_review_completed") if record else False,
            "evidence_collection_plan_intent_recorded": record.get("evidence_collection_plan_intent_recorded") if record else False,
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
            "apply_executor_evidence_collection_plan_execution_allowed": False,
            "apply_executor_evidence_collection_plan_record_execution_allowed": False,
            "apply_executor_evidence_collector_contract_execution_allowed": False,
            "apply_executed": False,
            "rollback_executed": False,
        }

    contract = _build_aeecp_collector(record, context)

    return {
        "name": "Aether",
        "status": runtime.status(),
        "apply_executor_evidence_collection_plan_record": record,
        "apply_executor_evidence_collector_contract": contract,
        "collector_contract_required": contract.get("collector_contract_required"),
        "collector_contract_status": contract.get("collector_contract_status"),
        "decision": contract.get("decision"),
        "evidence_collection_plan_review_completed": record.get("evidence_collection_plan_review_completed", False),
        "evidence_collection_plan_intent_recorded": record.get("evidence_collection_plan_intent_recorded", False),
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
        "apply_executor_evidence_collection_plan_execution_allowed": False,
        "apply_executor_evidence_collection_plan_record_execution_allowed": False,
        "apply_executor_evidence_collector_contract_execution_allowed": False,
        "apply_executed": False,
        "rollback_executed": False,
    }
