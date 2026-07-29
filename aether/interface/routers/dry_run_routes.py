from fastapi import APIRouter

from aether.interface.api_models import (
    ActionValidationBody,
    DryRunDecisionBody,
    SandboxContextBody,
)

from aether.action.services.dry_run_service import (
    handle_dry_run_create,
    handle_list_dry_runs,
    handle_get_dry_run,
    handle_cancel_dry_run,
)

from aether.action.services.sandbox_contract_service import (
    handle_sandbox_contract_create,
)

dry_run_router = APIRouter()


@dry_run_router.post("/approvals/{approval_id}/dry-run-request")
def dry_run_request_endpoint(approval_id: str, request: ActionValidationBody | None = None):
    requested_action = request.requested_action if request else None
    context = request.context if request else None
    return handle_dry_run_create(approval_id, requested_action, context)


@dry_run_router.get("/dry-runs")
def list_dry_runs(status: str | None = None, limit: int = 50):
    return handle_list_dry_runs(status=status, limit=limit)


@dry_run_router.get("/dry-runs/{dry_run_id}")
def get_dry_run(dry_run_id: str):
    return handle_get_dry_run(dry_run_id)


@dry_run_router.post("/dry-runs/{dry_run_id}/cancel")
def cancel_dry_run(dry_run_id: str, request: DryRunDecisionBody | None = None):
    reviewer = request.reviewer if request else None
    reason = request.reason if request else None
    return handle_cancel_dry_run(dry_run_id, reviewer, reason)


@dry_run_router.post("/dry-runs/{dry_run_id}/sandbox-contract")
def sandbox_contract_endpoint(dry_run_id: str, request: SandboxContextBody | None = None):
    context = request.context if request else None
    return handle_sandbox_contract_create(dry_run_id, context)
