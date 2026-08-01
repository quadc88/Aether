"""Observation Record Service for Aether (Milestone 83C).

Service foundation for the Observation Record Store feature line.

Implements create/get/list plus update_status/cancel:
- handle_create_observation_record
- handle_get_observation_record
- handle_list_observation_records
- handle_update_observation_record_status
- handle_cancel_observation_record

Router/API endpoints belong to the 83D/83E milestones.

This module must not import from the interface layer. Request payloads are
plain dicts; the router will convert its Pydantic request models to dicts
before calling this service.
"""

from __future__ import annotations

import json

from aether.core.runtime import runtime

from aether.action.observation_record import VALID_STATUSES, build_observation_record
from aether.action.observation_record_queue import (
    _ensure_json_serializable,
    cancel_observation_record,
    load_observation_record,
    list_observation_records,
    save_observation_record,
    update_observation_record_status,
)

_FORBIDDEN_CREATE_KEYS = (
    "observation_id",
    "observation_type",
    "observed_at",
    "safety_flags",
)


def _validate_create_request(request: dict) -> None:
    """Validate a create request payload at the service boundary."""
    if not isinstance(request, dict):
        raise ValueError("request must be a dict.")

    forbidden = [k for k in _FORBIDDEN_CREATE_KEYS if k in request]
    if forbidden:
        raise ValueError(
            "generated/internal fields cannot be supplied by the caller: "
            + ", ".join(sorted(forbidden))
        )

    target = request.get("target")
    if not isinstance(target, str) or not target:
        raise ValueError("target must be a non-empty string.")

    plan_step_id = request.get("plan_step_id")
    evidence_item_id = request.get("evidence_item_id")
    if not plan_step_id and not evidence_item_id:
        raise ValueError(
            "At least one of plan_step_id or evidence_item_id must be provided."
        )

    status = request.get("status", "pending")
    if status not in VALID_STATUSES:
        raise ValueError(
            f"Invalid status '{status}'. Must be one of: "
            + ", ".join(sorted(VALID_STATUSES))
            + "."
        )

    metadata = request.get("metadata")
    if metadata is not None and not isinstance(metadata, dict):
        raise ValueError("metadata must be a dict or None.")

    _ensure_json_serializable(request.get("observed_value"), "observed_value")
    _ensure_json_serializable(request.get("expected_value"), "expected_value")
    _ensure_json_serializable(metadata, "metadata")


def _validate_list_bounds(limit: int, offset: int) -> None:
    """Validate list pagination bounds (same bounds as the queue/store module)."""
    if isinstance(limit, bool) or not isinstance(limit, int):
        raise ValueError("limit must be an integer.")
    if limit < 1 or limit > 200:
        raise ValueError("limit must be in the range 1..200.")
    if isinstance(offset, bool) or not isinstance(offset, int):
        raise ValueError("offset must be an integer.")
    if offset < 0:
        raise ValueError("offset must be >= 0.")


def handle_create_observation_record(
    request: dict,
    context: dict | None = None,
) -> dict:
    """Validate a create request, build a record via the 82B builder, and persist it."""
    _validate_create_request(request)

    record = build_observation_record(
        plan_step_id=request.get("plan_step_id"),
        evidence_item_id=request.get("evidence_item_id"),
        target=request["target"],
        observed_value=request.get("observed_value"),
        expected_value=request.get("expected_value"),
        status=request.get("status", "pending"),
        collector_contract_id=request.get("collector_contract_id"),
        metadata=request.get("metadata"),
    )

    safety_flags = record["safety_flags"]
    true_flags = [k for k, v in safety_flags.items() if v is not False]
    if true_flags:
        raise ValueError(
            "safety_flags must all be False; found truthy values for: "
            + ", ".join(sorted(true_flags))
        )

    saved = save_observation_record(record, context)
    return {
        "name": "Aether",
        "status": runtime.status(),
        "observation_record": saved,
        "observation_id": saved["observation_id"],
        "created": True,
    }


def handle_get_observation_record(observation_id: str) -> dict:
    """Get a single observation record."""
    record = load_observation_record(observation_id)
    return {
        "name": "Aether",
        "status": runtime.status(),
        "observation_record": record,
        "found": record is not None,
    }


def handle_list_observation_records(
    status: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> dict:
    """List observation records with optional status filter and pagination."""
    _validate_list_bounds(limit, offset)
    result = list_observation_records(status=status, limit=limit, offset=offset)
    return {
        "name": "Aether",
        "status": runtime.status(),
        "observation_records": result["records"],
        "count": len(result["records"]),
        "total": result["total"],
        "limit": result["limit"],
        "offset": result["offset"],
    }


def _validate_reviewer_reason(request: dict) -> None:
    """Validate lifecycle request payloads at the service boundary."""
    if not isinstance(request, dict):
        raise ValueError("request must be a dict.")
    for key in ("reviewer", "reason"):
        if key in request and request[key] is not None and not isinstance(request[key], str):
            raise ValueError(f"{key} must be a string or None.")


def handle_update_observation_record_status(
    observation_id: str,
    request: dict,
    context: dict | None = None,
) -> dict:
    """Update the status of an observation record lifecycle request."""
    _validate_reviewer_reason(request)
    new_status = request.get("new_status")
    if new_status not in VALID_STATUSES:
        raise ValueError(
            f"Invalid status '{new_status}'. Must be one of: "
            + ", ".join(sorted(VALID_STATUSES))
            + "."
        )

    record = update_observation_record_status(
        observation_id,
        new_status,
        reviewer=request.get("reviewer"),
        reason=request.get("reason"),
        context=context,
    )
    if not record:
        return {
            "name": "Aether",
            "status": runtime.status(),
            "observation_record": None,
            "found": False,
            "updated": False,
        }
    return {
        "name": "Aether",
        "status": runtime.status(),
        "observation_record": record,
        "found": True,
        "updated": record.get("status") == new_status,
    }


def handle_cancel_observation_record(
    observation_id: str,
    request: dict | None = None,
    context: dict | None = None,
) -> dict:
    """Cancel a pending observation record lifecycle request."""
    payload = request if request is not None else {}
    _validate_reviewer_reason(payload)

    record = cancel_observation_record(
        observation_id,
        reviewer=payload.get("reviewer"),
        reason=payload.get("reason"),
        context=context,
    )
    if not record:
        return {
            "name": "Aether",
            "status": runtime.status(),
            "observation_record": None,
            "found": False,
            "cancelled": False,
        }
    return {
        "name": "Aether",
        "status": runtime.status(),
        "observation_record": record,
        "found": True,
        "cancelled": record.get("status") == "cancelled",
    }
