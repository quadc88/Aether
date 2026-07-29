from fastapi import APIRouter

from aether.interface.api_models import (
    ApplyGateContextBody,
    ApplyGateDecisionBody,
    VerdictContextBody,
    VerdictDecisionBody,
)
from aether.action.services.verification_verdict_service import (
    handle_verification_verdict_create,
    handle_list_verification_verdicts,
    handle_get_verification_verdict,
    handle_cancel_verification_verdict,
)
from aether.action.services.apply_gate_service import (
    handle_apply_gate_create,
    handle_list_apply_gates,
    handle_get_apply_gate,
    handle_cancel_apply_gate,
)

verification_apply_gate_router = APIRouter()


@verification_apply_gate_router.post("/simulation-results/{simulation_result_id}/verification-verdict")
def simulation_verification_verdict_endpoint(simulation_result_id: str, request: VerdictContextBody | None = None):
    context = request.context if request else None
    return handle_verification_verdict_create(simulation_result_id, context)


@verification_apply_gate_router.get("/verification-verdicts")
def list_verification_verdicts(status: str | None = None, decision: str | None = None, limit: int = 50):
    return handle_list_verification_verdicts(status, decision, limit)


@verification_apply_gate_router.get("/verification-verdicts/{verification_verdict_id}")
def get_verification_verdict(verification_verdict_id: str):
    return handle_get_verification_verdict(verification_verdict_id)


@verification_apply_gate_router.post("/verification-verdicts/{verification_verdict_id}/cancel")
def cancel_verification_verdict(verification_verdict_id: str, request: VerdictDecisionBody | None = None):
    reviewer = request.reviewer if request else None
    reason = request.reason if request else None
    return handle_cancel_verification_verdict(verification_verdict_id, reviewer, reason)


@verification_apply_gate_router.post("/verification-verdicts/{verification_verdict_id}/apply-gate-request")
def verification_verdict_apply_gate_request_endpoint(verification_verdict_id: str, request: ApplyGateContextBody | None = None):
    context = request.context if request else None
    return handle_apply_gate_create(verification_verdict_id, context)


@verification_apply_gate_router.get("/apply-gates")
def list_apply_gates(status: str | None = None, decision: str | None = None, limit: int = 50):
    return handle_list_apply_gates(status, decision, limit)


@verification_apply_gate_router.get("/apply-gates/{apply_gate_id}")
def get_apply_gate(apply_gate_id: str):
    return handle_get_apply_gate(apply_gate_id)


@verification_apply_gate_router.post("/apply-gates/{apply_gate_id}/cancel")
def cancel_apply_gate(apply_gate_id: str, request: ApplyGateDecisionBody | None = None):
    reviewer = request.reviewer if request else None
    reason = request.reason if request else None
    return handle_cancel_apply_gate(apply_gate_id, reviewer, reason)
