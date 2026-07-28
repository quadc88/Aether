"""Dry Run Service — Thin Interface Refactor Phase 5 (Milestone 80F).

Moves Milestone 56A-57A orchestration out of api_server.py into this service module.

This module handles:
- Dry-run request creation (validate + build + persist + response shaping)
- Dry-run record CRUD (list, get, cancel)

Behavior-preserving refactor: no endpoint path, response shape, or safety changes.
"""

from aether.core.runtime import runtime

from aether.action.approval_decision_gate import (
    validate_approval_for_action as _validate_action,
)
from aether.action.dry_run_request import (
    build_dry_run_request as _build_dry_run,
)
from aether.action.dry_run_queue import (
    create_dry_run_record as _create_dr_record,
    get_dry_run_record as _get_dr,
    list_dry_run_records as _list_dr,
    update_dry_run_record_status as _update_dr,
)


def handle_dry_run_create(
    approval_id: str,
    requested_action: dict | None = None,
    context: dict | None = None,
) -> dict:
    """Validate an approval and build a dry-run request from it."""
    validation_result = _validate_action(
        approval_id=approval_id,
        requested_action=requested_action,
        context=context,
    )
    dry_run_req = _build_dry_run(validation_result, requested_action, context)

    dry_run_rec = None
    dry_run_id = None
    if dry_run_req is not None:
        dry_run_rec = _create_dr_record(dry_run_request=dry_run_req, context=context)
        dry_run_id = dry_run_rec["dry_run_id"]

    return {
        "name": "Aether",
        "status": runtime.status(),
        "approval_validation": validation_result,
        "dry_run_request": dry_run_req,
        "dry_run_record": dry_run_rec,
        "dry_run_id": dry_run_id,
        "dry_run_required": dry_run_req is not None,
        "dry_run_status": dry_run_req.get("dry_run_status") if dry_run_req else None,
        "dry_run_allowed": validation_result.get("dry_run_allowed", False),
        "execution_allowed": False,
        "tool_execution_allowed": False,
        "apply_allowed": False,
        "rollback_allowed": False,
    }


def handle_list_dry_runs(
    status: str | None = None,
    decision: str | None = None,
    limit: int = 50,
) -> dict:
    """List dry-run records."""
    records = _list_dr(status=status, limit=limit)
    return {
        "name": "Aether",
        "status": runtime.status(),
        "dry_runs": records,
        "count": len(records),
    }


def handle_get_dry_run(
    dry_run_id: str,
) -> dict:
    """Get a single dry-run record."""
    record = _get_dr(dry_run_id)
    return {
        "name": "Aether",
        "status": runtime.status(),
        "dry_run": record,
        "found": record is not None,
    }


def handle_cancel_dry_run(
    dry_run_id: str,
    reviewer: str | None = None,
    reason: str | None = None,
) -> dict:
    """Cancel a dry-run record."""
    record = _update_dr(
        dry_run_id, decision="cancelled", reviewer=reviewer, reason=reason
    )
    if record is None:
        return {
            "name": "Aether",
            "status": runtime.status(),
            "dry_run": None,
            "found": False,
            "warnings": ["Dry-run record not found."],
        }
    return {
        "name": "Aether",
        "status": runtime.status(),
        "dry_run": record,
        "found": True,
    }
