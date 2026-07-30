from fastapi import APIRouter

from aether.action.services.executor_contract_service import (
    handle_approve_contract_intent,
    handle_cancel_executor_contract,
    handle_executor_contract_create,
    handle_get_executor_contract,
    handle_list_executor_contracts,
    handle_reject_executor_contract,
)
from aether.action.services.executor_plan_service import (
    handle_approve_executor_plan_intent,
    handle_cancel_executor_plan,
    handle_executor_plan_create,
    handle_get_executor_plan,
    handle_list_executor_plans,
    handle_reject_executor_plan,
)
from aether.interface.api_models import ApplyExecGateDecisionBody


executor_router = APIRouter()


@executor_router.post("/apply-execution-gates/{apply_execution_gate_id}/executor-contract")
def apply_executor_contract_endpoint(
    apply_execution_gate_id: str, request: ApplyExecGateDecisionBody | None = None
):
    return handle_executor_contract_create(apply_execution_gate_id)


@executor_router.get("/apply-executor-contracts")
def list_apply_executor_contracts(
    status: str | None = None,
    decision: str | None = None,
    limit: int = 50,
):
    return handle_list_executor_contracts(status, decision, limit)


@executor_router.get("/apply-executor-contracts/{apply_executor_contract_id}")
def get_apply_executor_contract(apply_executor_contract_id: str):
    return handle_get_executor_contract(apply_executor_contract_id)


@executor_router.post("/apply-executor-contracts/{apply_executor_contract_id}/cancel")
def cancel_apply_executor_contract(
    apply_executor_contract_id: str,
    request: ApplyExecGateDecisionBody | None = None,
):
    reviewer = request.reviewer if request else None
    reason = request.reason if request else None
    return handle_cancel_executor_contract(apply_executor_contract_id, reviewer, reason)


@executor_router.post("/apply-executor-contracts/{apply_executor_contract_id}/reject")
def reject_apply_executor_contract(
    apply_executor_contract_id: str,
    request: ApplyExecGateDecisionBody | None = None,
):
    reviewer = request.reviewer if request else None
    reason = request.reason if request else None
    return handle_reject_executor_contract(apply_executor_contract_id, reviewer, reason)


@executor_router.post(
    "/apply-executor-contracts/{apply_executor_contract_id}/approve-contract-intent"
)
def approve_contract_intent_executor(
    apply_executor_contract_id: str,
    request: ApplyExecGateDecisionBody | None = None,
):
    reviewer = request.reviewer if request else None
    reason = request.reason if request else None
    confirmations = request.confirmations if request else None
    return handle_approve_contract_intent(
        apply_executor_contract_id, reviewer, reason, confirmations
    )


@executor_router.post(
    "/apply-executor-contracts/{apply_executor_contract_id}/executor-plan"
)
def apply_executor_plan_endpoint(
    apply_executor_contract_id: str,
    request: ApplyExecGateDecisionBody | None = None,
):
    return handle_executor_plan_create(apply_executor_contract_id)


@executor_router.get("/apply-executor-plans")
def list_apply_executor_plans(
    status: str | None = None,
    decision: str | None = None,
    limit: int = 50,
):
    return handle_list_executor_plans(status, decision, limit)


@executor_router.get("/apply-executor-plans/{apply_executor_plan_id}")
def get_apply_executor_plan(apply_executor_plan_id: str):
    return handle_get_executor_plan(apply_executor_plan_id)


@executor_router.post("/apply-executor-plans/{apply_executor_plan_id}/cancel")
def cancel_apply_executor_plan(
    apply_executor_plan_id: str,
    request: ApplyExecGateDecisionBody | None = None,
):
    reviewer = request.reviewer if request else None
    reason = request.reason if request else None
    return handle_cancel_executor_plan(apply_executor_plan_id, reviewer, reason)


@executor_router.post("/apply-executor-plans/{apply_executor_plan_id}/reject")
def reject_apply_executor_plan(
    apply_executor_plan_id: str,
    request: ApplyExecGateDecisionBody | None = None,
):
    reviewer = request.reviewer if request else None
    reason = request.reason if request else None
    return handle_reject_executor_plan(apply_executor_plan_id, reviewer, reason)


@executor_router.post(
    "/apply-executor-plans/{apply_executor_plan_id}/approve-plan-intent"
)
def approve_plan_intent_executor(
    apply_executor_plan_id: str,
    request: ApplyExecGateDecisionBody | None = None,
):
    reviewer = request.reviewer if request else None
    reason = request.reason if request else None
    confirmations = request.confirmations if request else None
    return handle_approve_executor_plan_intent(
        apply_executor_plan_id, reviewer, reason, confirmations
    )
