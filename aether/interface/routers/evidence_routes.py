from fastapi import APIRouter

from aether.interface.api_models import (
    ApprovalIntentBody,
    EvidenceContractApproveBody,
    EvidenceContractBody,
    EvidenceContractDecisionBody,
    PlanDecisionBody,
)
from aether.action.services.collection_plan_service import (
    handle_evidence_collection_plan_create,
    handle_list_collection_plans,
    handle_get_collection_plan,
    handle_reject_collection_plan,
    handle_cancel_collection_plan,
    handle_approve_collection_plan_intent,
    handle_collector_contract_create,
)
from aether.action.services.evidence_contract_service import (
    handle_evidence_contract_create,
    handle_list_evidence_contracts,
    handle_get_evidence_contract,
    handle_cancel_evidence_contract,
    handle_reject_evidence_contract,
    handle_approve_evidence_contract_intent,
)


evidence_router = APIRouter()


@evidence_router.post("/apply-executor-plans/{apply_executor_plan_id}/evidence-contract")
def apply_executor_evidence_contract(
    apply_executor_plan_id: str, request: EvidenceContractBody | None = None,
):
    context = request.context if request and request.context else None
    return handle_evidence_contract_create(apply_executor_plan_id, context)


@evidence_router.get("/apply-executor-evidence-contracts")
def list_apply_executor_evidence_contracts(
    status: str | None = None,
    decision: str | None = None,
    limit: int = 50,
):
    return handle_list_evidence_contracts(status, decision, limit)


@evidence_router.get("/apply-executor-evidence-contracts/{apply_executor_evidence_contract_id}")
def get_apply_executor_evidence_contract(apply_executor_evidence_contract_id: str):
    return handle_get_evidence_contract(apply_executor_evidence_contract_id)


@evidence_router.post("/apply-executor-evidence-contracts/{apply_executor_evidence_contract_id}/cancel")
def cancel_apply_executor_evidence_contract(
    apply_executor_evidence_contract_id: str,
    request: EvidenceContractDecisionBody | None = None,
):
    reviewer = request.reviewer if request else None
    reason = request.reason if request else None
    return handle_cancel_evidence_contract(apply_executor_evidence_contract_id, reviewer, reason)


@evidence_router.post("/apply-executor-evidence-contracts/{apply_executor_evidence_contract_id}/reject")
def reject_apply_executor_evidence_contract(
    apply_executor_evidence_contract_id: str,
    request: EvidenceContractDecisionBody | None = None,
):
    reviewer = request.reviewer if request else None
    reason = request.reason if request else None
    return handle_reject_evidence_contract(apply_executor_evidence_contract_id, reviewer, reason)


@evidence_router.post("/apply-executor-evidence-contracts/{apply_executor_evidence_contract_id}/approve-evidence-contract-intent")
def approve_evidence_contract_intent(
    apply_executor_evidence_contract_id: str,
    request: EvidenceContractApproveBody,
):
    return handle_approve_evidence_contract_intent(
        apply_executor_evidence_contract_id,
        reviewer=request.reviewer,
        reason=request.reason,
        confirmations=request.confirmations,
    )


@evidence_router.post("/apply-executor-evidence-contracts/{apply_executor_evidence_contract_id}/evidence-collection-plan")
def evidence_collection_plan(
    apply_executor_evidence_contract_id: str,
    request: EvidenceContractBody | None = None,
):
    """Build an apply executor evidence collection plan from an evidence contract record.

    This endpoint creates a structured evidence collection plan object without
    collecting evidence or authorizing execution per Milestone 77A safety.
    """
    context = request.context if request and request.context else None
    return handle_evidence_collection_plan_create(apply_executor_evidence_contract_id, context)


@evidence_router.post("/apply-executor-evidence-collection-plans/{id}/collector-contract")
def collector_contract(id: str, request: dict | None = None):
    """Build an apply executor evidence collector contract from a collection plan record.

    This endpoint returns a structured collector contract without collecting evidence,
    authorizing execution, or modifying state per Milestone 79A safety.
    """
    context = request.get("context") if request and request.get("context") else None
    return handle_collector_contract_create(id, context)


@evidence_router.get("/apply-executor-evidence-collection-plans")
def list_evidence_collection_plans(
    status: str | None = None,
    decision: str | None = None,
    limit: int = 50,
):
    return handle_list_collection_plans(status, decision, limit)


@evidence_router.get("/apply-executor-evidence-collection-plans/{id}")
def get_evidence_collection_plan(id: str):
    return handle_get_collection_plan(id)


@evidence_router.post("/apply-executor-evidence-collection-plans/{id}/reject")
def reject_evidence_collection_plan(id: str, request: PlanDecisionBody | None = None):
    reviewer = request.reviewer if request else None
    reason = request.reason if request else None
    return handle_reject_collection_plan(id, reviewer, reason)


@evidence_router.post("/apply-executor-evidence-collection-plans/{id}/cancel")
def cancel_evidence_collection_plan(id: str, request: PlanDecisionBody | None = None):
    reviewer = request.reviewer if request else None
    reason = request.reason if request else None
    return handle_cancel_collection_plan(id, reviewer, reason)


@evidence_router.post("/apply-executor-evidence-collection-plans/{id}/approve-collection-plan-intent")
def approve_evidence_collection_plan_intent(id: str, request: ApprovalIntentBody | None = None):
    reviewer = request.reviewer if request else None
    reason = request.reason if request else None
    confirmations = request.confirmations if request else None
    return handle_approve_collection_plan_intent(id, reviewer, reason, confirmations)
