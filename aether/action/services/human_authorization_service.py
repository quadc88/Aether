"""Human Authorization Service — Thin Interface Refactor Phase 4 (Milestone 80E).

Moves Milestone 67-68 orchestration out of api_server.py into this service module.

This module handles:
- Human authorization request creation (build + persist + response shaping)
- Human authorization record CRUD (list, get, cancel, reject, approve intent)

Behavior-preserving refactor: no endpoint path, response shape, or safety changes.
"""

from aether.core.runtime import runtime

from aether.action.human_apply_authorization_request import (
    build_human_apply_authorization_request as _build_haar,
)
from aether.action.human_authorization_queue import (
    create_human_authorization_record as _create_ha_rec,
    get_human_authorization_record as _get_ha_rec,
    list_human_authorization_records as _list_ha_rec,
    update_human_authorization_record_status as _update_ha_rec,
)
from aether.action.apply_gate_queue import (
    get_apply_gate_record as _get_agr,
)


# --------------------------------------------------------------------------- #
# A. Human Authorization Create
# POST /apply-gates/{id}/human-authorization-request
# --------------------------------------------------------------------------- #


def handle_human_authorization_create(
    apply_gate_id: str,
    context: dict | None = None,
) -> dict:
    """Build a human authorization request from an apply gate record and persist it."""
    record = _get_agr(apply_gate_id)
    haar = _build_haar(record, context)

    ha_rec = None
    ha_id = None
    if haar is not None:
        ha_rec = _create_ha_rec(human_apply_authorization_request=haar, context=context)
        ha_id = ha_rec["human_authorization_id"]

    return {
        "name": "Aether",
        "status": runtime.status(),
        "apply_gate_record": record,
        "human_apply_authorization_request": haar,
        "human_authorization_record": ha_rec,
        "human_authorization_id": ha_id,
        "human_authorization_required": haar.get("human_authorization_required"),
        "human_authorization_status": ha_rec.get("status") if ha_rec else haar.get("human_authorization_status"),
        "decision": haar.get("decision"),
        "human_review_completed": False,
        "human_intent_recorded": False,
        "execution_allowed": False,
        "tool_execution_allowed": False,
        "dry_run_execution_allowed": False,
        "simulation_execution_allowed": False,
        "apply_allowed": False,
        "rollback_allowed": False,
        "apply_gate_execution_allowed": False,
        "human_authorization_execution_allowed": False,
        "apply_authorized": False,
    }


# --------------------------------------------------------------------------- #
# B. Human Authorization Record: List
# GET /human-authorizations
# --------------------------------------------------------------------------- #


def handle_list_human_authorizations(
    status: str | None = None,
    decision: str | None = None,
    limit: int = 50,
) -> dict:
    """List human authorization records."""
    records = _list_ha_rec(status=status, decision=decision, limit=limit)
    return {
        "name": "Aether",
        "status": runtime.status(),
        "human_authorizations": records,
        "count": len(records),
    }


# --------------------------------------------------------------------------- #
# C. Human Authorization Record: Get
# GET /human-authorizations/{id}
# --------------------------------------------------------------------------- #


def handle_get_human_authorization(
    human_authorization_id: str,
) -> dict:
    """Get a single human authorization record."""
    record = _get_ha_rec(human_authorization_id)
    return {
        "name": "Aether",
        "status": runtime.status(),
        "human_authorization": record,
        "found": record is not None,
    }


# --------------------------------------------------------------------------- #
# D. Human Authorization Record: Cancel
# POST /human-authorizations/{id}/cancel
# --------------------------------------------------------------------------- #


def handle_cancel_human_authorization(
    human_authorization_id: str,
    reviewer: str | None = None,
    reason: str | None = None,
) -> dict:
    """Cancel a human authorization record."""
    record = _update_ha_rec(
        human_authorization_id, decision="cancelled", reviewer=reviewer, reason=reason
    )
    if record is None:
        return {
            "name": "Aether",
            "status": runtime.status(),
            "human_authorization": None,
            "found": False,
            "warnings": ["Human authorization record not found."],
        }
    return {
        "name": "Aether",
        "status": runtime.status(),
        "human_authorization": record,
        "found": True,
    }


# --------------------------------------------------------------------------- #
# E. Human Authorization Record: Reject
# POST /human-authorizations/{id}/reject
# --------------------------------------------------------------------------- #


def handle_reject_human_authorization(
    human_authorization_id: str,
    reviewer: str | None = None,
    reason: str | None = None,
) -> dict:
    """Reject a human authorization record."""
    record = _update_ha_rec(
        human_authorization_id, decision="rejected", reviewer=reviewer, reason=reason
    )
    if record is None:
        return {
            "name": "Aether",
            "status": runtime.status(),
            "human_authorization": None,
            "found": False,
            "warnings": ["Human authorization record not found."],
        }
    return {
        "name": "Aether",
        "status": runtime.status(),
        "human_authorization": record,
        "found": True,
    }


# --------------------------------------------------------------------------- #
# F. Human Authorization Record: Approve Intent
# POST /human-authorizations/{id}/approve-intent
# --------------------------------------------------------------------------- #


def handle_approve_intent_human_authorization(
    human_authorization_id: str,
    reviewer: str | None = None,
    reason: str | None = None,
    confirmations: list[str] | None = None,
) -> dict:
    """Approve intent on a human authorization record."""
    record = _update_ha_rec(
        human_authorization_id, decision="approved_intent", reviewer=reviewer, reason=reason, confirmations=confirmations
    )
    if record is None:
        return {
            "name": "Aether",
            "status": runtime.status(),
            "human_authorization": None,
            "found": False,
            "warnings": ["Could not approve intent: record not found or conditions not met."],
        }
    return {
        "name": "Aether",
        "status": runtime.status(),
        "human_authorization": record,
        "found": True,
    }
