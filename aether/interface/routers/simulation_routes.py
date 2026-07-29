from fastapi import APIRouter

from aether.interface.api_models import (
    SandboxContextBody,
    SimPlanDecisionBody,
    SimResultBody,
    SimResultDecisionBody,
)

from aether.action.services.simulation_plan_service import (
    handle_simulation_plan_create,
    handle_list_simulation_plans,
    handle_get_simulation_plan,
    handle_cancel_simulation_plan,
)
from aether.action.services.simulation_result_service import (
    handle_simulation_result_create,
    handle_list_simulation_results,
    handle_get_simulation_result,
    handle_cancel_simulation_result,
)

simulation_router = APIRouter()


@simulation_router.post("/dry-runs/{dry_run_id}/simulation-plan")
def simulation_plan_endpoint(dry_run_id: str, request: SandboxContextBody | None = None):
    context = request.context if request else None
    return handle_simulation_plan_create(dry_run_id, context)


@simulation_router.post("/simulation-plans/{simulation_plan_id}/simulation-result")
def simulation_result_endpoint(simulation_plan_id: str, request: SimResultBody | None = None):
    context = request.context if request else None
    return handle_simulation_result_create(simulation_plan_id, context)


@simulation_router.get("/simulation-results")
def list_simulation_results(status: str | None = None, limit: int = 50):
    return handle_list_simulation_results(status=status, limit=limit)


@simulation_router.get("/simulation-results/{simulation_result_id}")
def get_simulation_result(simulation_result_id: str):
    return handle_get_simulation_result(simulation_result_id)


@simulation_router.post("/simulation-results/{simulation_result_id}/cancel")
def cancel_simulation_result(simulation_result_id: str, request: SimResultDecisionBody | None = None):
    reviewer = request.reviewer if request else None
    reason = request.reason if request else None
    return handle_cancel_simulation_result(simulation_result_id, reviewer, reason)


@simulation_router.get("/simulation-plans")
def list_sim_plans(status: str | None = None, limit: int = 50):
    return handle_list_simulation_plans(status=status, limit=limit)


@simulation_router.get("/simulation-plans/{simulation_plan_id}")
def get_sim_plan(simulation_plan_id: str):
    return handle_get_simulation_plan(simulation_plan_id)


@simulation_router.post("/simulation-plans/{simulation_plan_id}/cancel")
def cancel_sim_plan(simulation_plan_id: str, request: SimPlanDecisionBody | None = None):
    reviewer = request.reviewer if request else None
    reason = request.reason if request else None
    return handle_cancel_simulation_plan(simulation_plan_id, reviewer, reason)
