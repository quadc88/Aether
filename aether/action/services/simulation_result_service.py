"""Simulation Result Service — Thin Interface Refactor Phase 5 (Milestone 80F).

Moves Milestone 61A-62A orchestration out of api_server.py into this service module.

This module handles:
- Simulation result creation (build + persist + response shaping)
- Simulation result record CRUD (list, get, cancel)

Behavior-preserving refactor: no endpoint path, response shape, or safety changes.
"""

from aether.core.runtime import runtime

from aether.action.simulation_plan_queue import (
    get_simulation_plan_record as _get_sp,
)
from aether.action.simulation_result import (
    build_simulation_result as _build_result,
)
from aether.action.simulation_result_queue import (
    create_simulation_result_record as _create_srr,
    get_simulation_result_record as _get_srr,
    list_simulation_result_records as _list_srr,
    update_simulation_result_record_status as _update_srr,
)


def handle_simulation_result_create(
    simulation_plan_id: str,
    context: dict | None = None,
) -> dict:
    """Build a simulation result from a simulation plan record and persist it."""
    record = _get_sp(simulation_plan_id)
    sim_result = _build_result(record, context)

    sim_rec = None
    sim_result_id = None
    if sim_result is not None:
        sim_rec = _create_srr(simulation_result=sim_result, context=context)
        sim_result_id = sim_rec["simulation_result_id"]

    return {
        "name": "Aether",
        "status": runtime.status(),
        "simulation_plan_record": record,
        "simulation_result": sim_result,
        "simulation_result_record": sim_rec,
        "simulation_result_id": sim_result_id,
        "simulation_result_required": sim_result is not None,
        "simulation_result_status": sim_rec.get("status") if sim_rec else (sim_result.get("simulation_result_status") if sim_result else None),
        "execution_allowed": False,
        "tool_execution_allowed": False,
        "dry_run_execution_allowed": False,
        "simulation_execution_allowed": False,
        "apply_allowed": False,
        "rollback_allowed": False,
    }


def handle_list_simulation_results(
    status: str | None = None,
    decision: str | None = None,
    limit: int = 50,
) -> dict:
    """List simulation result records."""
    records = _list_srr(status=status, limit=limit)
    return {
        "name": "Aether",
        "status": runtime.status(),
        "simulation_results": records,
        "count": len(records),
    }


def handle_get_simulation_result(
    simulation_result_id: str,
) -> dict:
    """Get a single simulation result record."""
    record = _get_srr(simulation_result_id)
    return {
        "name": "Aether",
        "status": runtime.status(),
        "simulation_result": record,
        "found": record is not None,
    }


def handle_cancel_simulation_result(
    simulation_result_id: str,
    reviewer: str | None = None,
    reason: str | None = None,
) -> dict:
    """Cancel a simulation result record."""
    record = _update_srr(
        simulation_result_id, decision="cancelled", reviewer=reviewer, reason=reason
    )
    if record is None:
        return {
            "name": "Aether",
            "status": runtime.status(),
            "simulation_result": None,
            "found": False,
            "warnings": ["Simulation result record not found."],
        }
    return {
        "name": "Aether",
        "status": runtime.status(),
        "simulation_result": record,
        "found": True,
    }
