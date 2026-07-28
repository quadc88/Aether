"""Apply Gate Service — Thin Interface Refactor Phase 4 (Milestone 80E).

Moves Milestone 65-66 orchestration out of api_server.py into this service module.

This module handles:
- Apply gate request creation (build + persist + response shaping)
- Apply gate record CRUD (list, get, cancel)

Behavior-preserving refactor: no endpoint path, response shape, or safety changes.
"""

from aether.core.runtime import runtime

from aether.action.apply_gate_request import (
    build_apply_gate_request as _build_agr,
)
from aether.action.apply_gate_queue import (
    create_apply_gate_record as _create_agr_rec,
    get_apply_gate_record as _get_agr,
    list_apply_gate_records as _list_agr,
    update_apply_gate_record_status as _update_agr,
)
from aether.action.simulation_verdict_queue import (
    get_verification_verdict_record as _get_vv,
)


# --------------------------------------------------------------------------- #
# A. Apply Gate Create
# POST /verification-verdicts/{id}/apply-gate-request
# --------------------------------------------------------------------------- #


def handle_apply_gate_create(
    verification_verdict_id: str,
    context: dict | None = None,
) -> dict:
    """Build an apply gate request from a verification verdict record and persist it."""
    record = _get_vv(verification_verdict_id)
    agr = _build_agr(record, context)

    ag_rec = None
    ag_id = None
    if agr is not None:
        ag_rec = _create_agr_rec(apply_gate_request=agr, context=context)
        ag_id = ag_rec["apply_gate_id"]

    return {
        "name": "Aether",
        "status": runtime.status(),
        "verification_verdict_record": record,
        "apply_gate_request": agr,
        "apply_gate_record": ag_rec,
        "apply_gate_id": ag_id,
        "apply_gate_required": agr.get("apply_gate_required"),
        "apply_gate_status": ag_rec.get("status") if ag_rec else agr.get("apply_gate_status"),
        "decision": agr.get("decision"),
        "execution_allowed": False,
        "tool_execution_allowed": False,
        "dry_run_execution_allowed": False,
        "simulation_execution_allowed": False,
        "apply_allowed": False,
        "rollback_allowed": False,
        "apply_gate_execution_allowed": False,
        "apply_authorized": False,
    }


# --------------------------------------------------------------------------- #
# B. Apply Gate Record: List
# GET /apply-gates
# --------------------------------------------------------------------------- #


def handle_list_apply_gates(
    status: str | None = None,
    decision: str | None = None,
    limit: int = 50,
) -> dict:
    """List apply gate records."""
    records = _list_agr(status=status, decision=decision, limit=limit)
    return {
        "name": "Aether",
        "status": runtime.status(),
        "apply_gates": records,
        "count": len(records),
    }


# --------------------------------------------------------------------------- #
# C. Apply Gate Record: Get
# GET /apply-gates/{id}
# --------------------------------------------------------------------------- #


def handle_get_apply_gate(
    apply_gate_id: str,
) -> dict:
    """Get a single apply gate record."""
    record = _get_agr(apply_gate_id)
    return {
        "name": "Aether",
        "status": runtime.status(),
        "apply_gate": record,
        "found": record is not None,
    }


# --------------------------------------------------------------------------- #
# D. Apply Gate Record: Cancel
# POST /apply-gates/{id}/cancel
# --------------------------------------------------------------------------- #


# --------------------------------------------------------------------------- #
# E. Apply Gate Record: Cancel
# POST /apply-gates/{id}/cancel
# --------------------------------------------------------------------------- #


def handle_cancel_apply_gate(
    apply_gate_id: str,
    reviewer: str | None = None,
    reason: str | None = None,
) -> dict:
    """Cancel an apply gate record."""
    record = _update_agr(
        apply_gate_id, decision="cancelled", reviewer=reviewer, reason=reason
    )
    if record is None:
        return {
            "name": "Aether",
            "status": runtime.status(),
            "apply_gate": None,
            "found": False,
            "warnings": ["Apply gate record not found."],
        }
    return {
        "name": "Aether",
        "status": runtime.status(),
        "apply_gate": record,
        "found": True,
    }
