from fastapi import APIRouter

from aether.interface.api_models import (
    ApplyExecGateDecisionBody,
    HumanAuthContextBody,
    HumanAuthDecisionBody,
)
from aether.action.services.human_authorization_service import (
    handle_human_authorization_create,
    handle_list_human_authorizations,
    handle_get_human_authorization,
    handle_cancel_human_authorization,
    handle_reject_human_authorization,
    handle_approve_intent_human_authorization,
)
from aether.action.services.apply_execution_gate_service import (
    handle_apply_execution_gate_create,
    handle_list_apply_execution_gates,
    handle_get_apply_execution_gate,
    handle_cancel_apply_execution_gate,
    handle_reject_apply_execution_gate,
    handle_approve_execution_intent,
)


authorization_execution_gate_router = APIRouter()


@authorization_execution_gate_router.post("/apply-gates/{apply_gate_id}/human-authorization-request")
def apply_gate_human_authorization_request_endpoint(apply_gate_id: str, request: HumanAuthContextBody | None = None):
    context = request.context if request else None
    return handle_human_authorization_create(apply_gate_id, context)


@authorization_execution_gate_router.get("/human-authorizations")
def list_human_authorizations(status: str | None = None, decision: str | None = None, limit: int = 50):
    return handle_list_human_authorizations(status, decision, limit)


@authorization_execution_gate_router.get("/human-authorizations/{human_authorization_id}")
def get_human_authorization(human_authorization_id: str):
    return handle_get_human_authorization(human_authorization_id)


@authorization_execution_gate_router.post("/human-authorizations/{human_authorization_id}/cancel")
def cancel_human_authorization(human_authorization_id: str, request: HumanAuthDecisionBody | None = None):
    reviewer = request.reviewer if request else None
    reason = request.reason if request else None
    return handle_cancel_human_authorization(human_authorization_id, reviewer, reason)


@authorization_execution_gate_router.post("/human-authorizations/{human_authorization_id}/reject")
def reject_human_authorization(human_authorization_id: str, request: HumanAuthDecisionBody | None = None):
    reviewer = request.reviewer if request else None
    reason = request.reason if request else None
    return handle_reject_human_authorization(human_authorization_id, reviewer, reason)


@authorization_execution_gate_router.post("/human-authorizations/{human_authorization_id}/approve-intent")
def approve_intent_human_authorization(human_authorization_id: str, request: HumanAuthDecisionBody | None = None):
    reviewer = request.reviewer if request else None
    reason = request.reason if request else None
    confirmations = request.confirmations if request else None
    return handle_approve_intent_human_authorization(human_authorization_id, reviewer, reason, confirmations)


@authorization_execution_gate_router.post(
    "/human-authorizations/{human_authorization_id}/apply-execution-gate-request"
)
def human_auth_apply_execution_gate_request_endpoint(human_authorization_id: str, request: HumanAuthContextBody | None = None):
    context = request.context if request else None
    return handle_apply_execution_gate_create(human_authorization_id, context)


@authorization_execution_gate_router.get("/apply-execution-gates")
def list_apply_execution_gates(
    status: str | None = None,
    decision: str | None = None,
    limit: int = 50,
):
    return handle_list_apply_execution_gates(status, decision, limit)


@authorization_execution_gate_router.get("/apply-execution-gates/{apply_execution_gate_id}")
def get_apply_execution_gate(apply_execution_gate_id: str):
    return handle_get_apply_execution_gate(apply_execution_gate_id)


@authorization_execution_gate_router.post("/apply-execution-gates/{apply_execution_gate_id}/cancel")
def cancel_apply_execution_gate(apply_execution_gate_id: str, request: ApplyExecGateDecisionBody | None = None):
    reviewer = request.reviewer if request else None
    reason = request.reason if request else None
    return handle_cancel_apply_execution_gate(apply_execution_gate_id, reviewer, reason)


@authorization_execution_gate_router.post("/apply-execution-gates/{apply_execution_gate_id}/reject")
def reject_apply_execution_gate(apply_execution_gate_id: str, request: ApplyExecGateDecisionBody | None = None):
    reviewer = request.reviewer if request else None
    reason = request.reason if request else None
    return handle_reject_apply_execution_gate(apply_execution_gate_id, reviewer, reason)


@authorization_execution_gate_router.post(
    "/apply-execution-gates/{apply_execution_gate_id}/approve-execution-intent"
)
def approve_execution_intent_apply_gate(apply_execution_gate_id: str, request: ApplyExecGateDecisionBody | None = None):
    reviewer = request.reviewer if request else None
    reason = request.reason if request else None
    confirmations = request.confirmations if request else None
    return handle_approve_execution_intent(apply_execution_gate_id, reviewer, reason, confirmations)
