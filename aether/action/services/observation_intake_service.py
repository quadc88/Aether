"""Observation Intake Service for Aether (Milestone 84B).

Service foundation for the Observation Intake Bridge feature line.

Implements:
- handle_observation_intake

This service is the first safe producer for the closed Observation Record
Store (Milestone 83). It accepts caller-supplied observed_value and
expected_value inputs, compares them with strict JSON-normalized equality,
and creates Observation Records through the 82B builder and the 83C queue.

The service is purely declarative and non-executing. It does NOT:
- execute tools
- collect evidence
- call executor code
- call real apply
- call rollback
- call the policy/execution gate
- invoke runtime route handlers
- invoke protected/core route functions
- make network calls
- capture observations automatically
- use an LLM or perform fuzzy/semantic matching

Persistence uses only build_observation_record and
queue.save_observation_record. No direct filesystem writes are performed.

Two-phase processing:
- Phase A (validate and prepare): the complete top-level request, every
  forbidden field, every evidence item, and every item metadata dict are
  validated; every observed/expected value is strictly JSON-normalized;
  every record is built in memory. queue.save_observation_record is never
  called in Phase A.
- Phase B (persist): only after Phase A fully succeeds, each prepared
  record is persisted in input order via queue.save_observation_record
  (without context).

Validation atomicity is guaranteed: any validation, normalization, or
builder failure in Phase A raises ValueError with zero queue saves, zero
persisted records, no partial creation, and no orphan records.

Storage-level transactionality across multiple queue saves is NOT
provided: the closed Milestone 83 queue performs per-record single-file
writes with no batch, transaction, staging, rollback, or cleanup. If a
later save raises an I/O exception after earlier saves succeeded, the
exception propagates, no completed or partial-success envelope is
returned, and no cleanup or rollback is attempted.
"""

from __future__ import annotations

import json

from aether.action.observation_record import build_observation_record
from aether.action.observation_record_queue import (
    _ensure_json_serializable,
    save_observation_record,
)

_FORBIDDEN_FIELDS = (
    "observation_id",
    "observation_type",
    "observed_at",
    "status",
    "created_at",
    "updated_at",
    "decision",
    "decided_at",
    "reviewer",
    "decision_reason",
    "warnings",
    "context_metadata",
    "new_status",
    "reason",
    "safety_flags",
)

_REQUIRED_EVIDENCE_ITEM_KEYS = ("target", "observed_value", "expected_value")


def _reject_forbidden_fields(fields: dict) -> None:
    """Reject any forbidden caller-supplied field in a request or item."""
    forbidden = [k for k in _FORBIDDEN_FIELDS if k in fields]
    if forbidden:
        raise ValueError(
            "generated/internal fields cannot be supplied by the caller: "
            + ", ".join(sorted(forbidden))
        )


def _validate_metadata(metadata: object) -> None:
    """Validate an optional metadata dict (dict or None, JSON-serializable)."""
    if metadata is not None and not isinstance(metadata, dict):
        raise ValueError("metadata must be a dict or None.")
    _ensure_json_serializable(metadata, "metadata")


def _normalized(value: object, path: str) -> str:
    """Return the strict JSON-normalized form of a value.

    Uses json.dumps(value, sort_keys=True) with no default=str. Any
    serialization failure (TypeError, ValueError, OverflowError) is
    converted to a deterministic ValueError with the original exception
    preserved as the cause.
    """
    try:
        return json.dumps(value, sort_keys=True)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError(
            f"Value at {path} is not JSON-serializable: {exc}"
        ) from exc


def _validate_evidence_item(item: object, index: int) -> None:
    """Validate a single evidence item (Phase A)."""
    if not isinstance(item, dict):
        raise ValueError(f"evidence_items[{index}] must be a dict.")

    _reject_forbidden_fields(item)

    evidence_item_id = item.get("evidence_item_id")
    if evidence_item_id is not None and (
        not isinstance(evidence_item_id, str) or not evidence_item_id
    ):
        raise ValueError(f"evidence_items[{index}].evidence_item_id must be a non-empty string.")

    target = item.get("target")
    if not isinstance(target, str) or not target:
        raise ValueError(f"evidence_items[{index}].target must be a non-empty string.")

    for key in _REQUIRED_EVIDENCE_ITEM_KEYS:
        if key not in item:
            raise ValueError(
                f"evidence_items[{index}] is missing required key: {key}"
            )

    _validate_metadata(item.get("metadata"))


def handle_observation_intake(
    request: dict,
    context: dict | None = None,
) -> dict:
    """Validate an intake request and persist one Observation Record per item.

    Args:
        request: Plain dict with plan_step_id, collector_contract_id, and a
            non-empty evidence_items list of dicts (each with target,
            observed_value, expected_value, and optional evidence_item_id
            and metadata).
        context: Accepted for signature stability only; ignored. It is not
            validated, not forwarded to queue.save_observation_record, and
            never populates context_metadata.

    Returns:
        The locked service envelope:
        {
            "name": "observation_intake",
            "status": "completed",
            "created": <count of created records>,
            "observation_records": [<full store record dicts>],
            "errors": [],
        }
        Records preserve evidence-items input order; each entry is the
        complete store shape returned by queue.save_observation_record.

    Raises:
        ValueError: If any validation, normalization, or builder preparation
            fails. Zero queue saves and zero persisted records result.
        Any persistence I/O exception propagates unwrapped after Phase A
            succeeds; earlier saved records remain on disk (no cleanup,
            no rollback, no partial-success envelope).
    """
    if not isinstance(request, dict):
        raise ValueError("request must be a dict.")

    _reject_forbidden_fields(request)

    plan_step_id = request.get("plan_step_id")
    if not isinstance(plan_step_id, str) or not plan_step_id:
        raise ValueError("plan_step_id must be a non-empty string.")

    collector_contract_id = request.get("collector_contract_id")
    if not isinstance(collector_contract_id, str) or not collector_contract_id:
        raise ValueError("collector_contract_id must be a non-empty string.")

    _validate_metadata(request.get("metadata"))

    evidence_items = request.get("evidence_items")
    if not isinstance(evidence_items, list):
        raise ValueError("evidence_items must be a non-empty list.")
    if not evidence_items:
        raise ValueError("evidence_items must be a non-empty list.")

    # Phase A: validate, normalize, compute status, and build in memory.
    prepared_records = []
    for index, item in enumerate(evidence_items):
        _validate_evidence_item(item, index)

        normalized_observed = _normalized(
            item["observed_value"],
            f"evidence_items[{index}].observed_value",
        )
        normalized_expected = _normalized(
            item["expected_value"],
            f"evidence_items[{index}].expected_value",
        )
        status = (
            "matched"
            if normalized_observed == normalized_expected
            else "mismatched"
        )

        prepared_records.append(
            build_observation_record(
                plan_step_id=plan_step_id,
                collector_contract_id=collector_contract_id,
                evidence_item_id=item.get("evidence_item_id"),
                target=item["target"],
                observed_value=item["observed_value"],
                expected_value=item["expected_value"],
                status=status,
                metadata=item.get("metadata"),
            )
        )

    # Phase B: persist each prepared record in input order (no context).
    saved_records = []
    for record in prepared_records:
        saved_records.append(save_observation_record(record))

    return {
        "name": "observation_intake",
        "status": "completed",
        "created": len(saved_records),
        "observation_records": saved_records,
        "errors": [],
    }
