"""Simulation Plan Service — Thin Interface Refactor Phase 5 (Milestone 80F).

Moves Milestone 59A-60A orchestration out of api_server.py into this service module.

This module handles:
- Simulation plan creation (build from sandbox contract + persist + response shaping)
- Simulation plan record CRUD (list, get, cancel)

Behavior-preserving refactor: no endpoint path, response shape, or safety changes.
"""

from aether.core.runtime import runtime

from aether.action.dry_run_queue import (
    get_dry_run_record as _get_dr,
)
from aether.action.dry_run_sandbox_contract import (
    build_dry_run_sandbox_contract as _build_contract,
)
from aether.action.simulation_plan import (
    build_simulation_plan as _build_plan,
)
from aether.action.simulation_plan_queue import (
    create_simulation_plan_record as _create_sp_record,
    get_simulation_plan_record as _get_sp,
    list_simulation_plan_records as _list_sp,
    update_simulation_plan_record_status as _update_sp,
)


def handle_simulation_plan_create(
    dry_run_id: str,
    context: dict | None = None,
) -> dict:
    """Build a simulation plan from a dry-run record via a sandbox contract."""
    dr_record = _get_dr(dry_run_id) if dry_run_id else None
    contract = _build_contract(dr_record, context)
    sim_plan = _build_plan(contract, context)

    sim_rec = None
    sim_plan_id = None
    if sim_plan is not None:
        sim_rec = _create_sp_record(simulation_plan=sim_plan, context=context)
        sim_plan_id = sim_rec["simulation_plan_id"]

    return {
        "name": "Aether",
        "status": runtime.status(),
        "sandbox_contract": contract,
        "simulation_plan": sim_plan,
        "simulation_plan_record": sim_rec,
        "simulation_plan_id": sim_plan_id,
        "simulation_plan_required": sim_plan is not None,
        "simulation_plan_status": sim_plan.get("simulation_plan_status") if sim_plan else None,
        "execution_allowed": False,
        "tool_execution_allowed": False,
        "dry_run_execution_allowed": False,
        "apply_allowed": False,
        "rollback_allowed": False,
    }


def handle_list_simulation_plans(
    status: str | None = None,
    decision: str | None = None,
    limit: int = 50,
) -> dict:
    """List simulation plan records."""
    records = _list_sp(status=status, limit=limit)
    return {
        "name": "Aether",
        "status": runtime.status(),
        "simulation_plans": records,
        "count": len(records),
    }


def handle_get_simulation_plan(
    simulation_plan_id: str,
) -> dict:
    """Get a single simulation plan record."""
    record = _get_sp(simulation_plan_id)
    return {
        "name": "Aether",
        "status": runtime.status(),
        "simulation_plan": record,
        "found": record is not None,
    }


def handle_cancel_simulation_plan(
    simulation_plan_id: str,
    reviewer: str | None = None,
    reason: str | None = None,
) -> dict:
    """Cancel a simulation plan record."""
    record = _update_sp(
        simulation_plan_id, decision="cancelled", reviewer=reviewer, reason=reason
    )
    if record is None:
        return {
            "name": "Aether",
            "status": runtime.status(),
            "simulation_plan": None,
            "found": False,
            "warnings": ["Simulation plan record not found."],
        }
    return {
        "name": "Aether",
        "status": runtime.status(),
        "simulation_plan": record,
        "found": True,
    }
