"""Verification Verdict Service — Thin Interface Refactor Phase 4 (Milestone 80E).

Moves Milestone 63-64 orchestration out of api_server.py into this service module.

This module handles:
- Verification verdict creation (build + persist + response shaping)
- Verification verdict record CRUD (list, get, cancel)

Behavior-preserving refactor: no endpoint path, response shape, or safety changes.
"""

from aether.core.runtime import runtime

from aether.action.simulation_verdict import (
    build_simulation_verification_verdict as _build_verdict,
)
from aether.action.simulation_verdict_queue import (
    create_verification_verdict_record as _create_vv_record,
    get_verification_verdict_record as _get_vv,
    list_verification_verdict_records as _list_vv,
    update_verification_verdict_record_status as _update_vv,
)
from aether.action.simulation_result_queue import (
    get_simulation_result_record as _get_srr,
)


# --------------------------------------------------------------------------- #
# A. Verification Verdict Create
# POST /simulation-results/{id}/verification-verdict
# --------------------------------------------------------------------------- #


def handle_verification_verdict_create(
    simulation_result_id: str,
    context: dict | None = None,
) -> dict:
    """Build a verification verdict from a simulation result record and persist it."""
    record = _get_srr(simulation_result_id)
    verdict = _build_verdict(record, context)

    vv_rec = None
    vv_id = None
    if verdict is not None:
        vv_rec = _create_vv_record(verification_verdict=verdict, context=context)
        vv_id = vv_rec["verification_verdict_id"]

    return {
        "name": "Aether",
        "status": runtime.status(),
        "simulation_result_record": record,
        "verification_verdict": verdict,
        "verification_verdict_record": vv_rec,
        "verification_verdict_id": vv_id,
        "verification_verdict_required": verdict.get("verification_verdict_required"),
        "verification_verdict_status": vv_rec.get("status") if vv_rec else verdict.get("verification_verdict_status"),
        "decision": verdict.get("decision"),
        "execution_allowed": False,
        "tool_execution_allowed": False,
        "dry_run_execution_allowed": False,
        "simulation_execution_allowed": False,
        "apply_allowed": False,
        "rollback_allowed": False,
        "verdict_apply_allowed": False,
        "apply_authorized": False,
    }


# --------------------------------------------------------------------------- #
# B. Verification Verdict Record: List
# GET /verification-verdicts
# --------------------------------------------------------------------------- #


def handle_list_verification_verdicts(
    status: str | None = None,
    decision: str | None = None,
    limit: int = 50,
) -> dict:
    """List verification verdict records."""
    records = _list_vv(status=status, decision=decision, limit=limit)
    return {
        "name": "Aether",
        "status": runtime.status(),
        "verification_verdicts": records,
        "count": len(records),
    }


# --------------------------------------------------------------------------- #
# C. Verification Verdict Record: Get
# GET /verification-verdicts/{id}
# --------------------------------------------------------------------------- #


def handle_get_verification_verdict(
    verification_verdict_id: str,
) -> dict:
    """Get a single verification verdict record."""
    record = _get_vv(verification_verdict_id)
    return {
        "name": "Aether",
        "status": runtime.status(),
        "verification_verdict": record,
        "found": record is not None,
    }


# --------------------------------------------------------------------------- #
# D. Verification Verdict Record: Cancel
# POST /verification-verdicts/{id}/cancel
# --------------------------------------------------------------------------- #


# --------------------------------------------------------------------------- #
# E. Verification Verdict Record: Cancel
# POST /verification-verdicts/{id}/cancel
# --------------------------------------------------------------------------- #


def handle_cancel_verification_verdict(
    verification_verdict_id: str,
    reviewer: str | None = None,
    reason: str | None = None,
) -> dict:
    """Cancel a verification verdict record."""
    record = _update_vv(
        verification_verdict_id, decision="cancelled", reviewer=reviewer, reason=reason
    )
    if record is None:
        return {
            "name": "Aether",
            "status": runtime.status(),
            "verification_verdict": None,
            "found": False,
            "warnings": ["Verification verdict record not found."],
        }
    return {
        "name": "Aether",
        "status": runtime.status(),
        "verification_verdict": record,
        "found": True,
    }
