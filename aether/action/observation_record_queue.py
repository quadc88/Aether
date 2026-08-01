"""Observation Record Queue/Store for Aether (Milestone 83C).

Manages persistent observation records stored under the configured private
data directory as individual JSON files named
``observation_record_<observation_id>.json``.

This is a pure declarative record store. It does NOT:
- observe anything
- collect evidence
- execute tools
- perform apply/rollback
- invoke endpoints, routers, or services
- modify the ObservationRecord builder

Create/get/list plus update_status/cancel are implemented. update_status and
cancel transition lifecycle fields on persisted records (Milestone 83E).
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone as _tz
from pathlib import Path

from aether.core.config import get_private_dir
from aether.action.observation_record import VALID_STATUSES


OBSERVATION_RECORD_ID_PATTERN = re.compile(r"^[0-9a-f]{32}$")
OBSERVATION_RECORDS_DIR_NAME = "observation_records"
OBSERVATION_RECORD_FILE_PREFIX = "observation_record_"

_REQUIRED_OBSERVATION_RECORD_KEYS = (
    "observation_id",
    "observation_type",
    "plan_step_id",
    "evidence_item_id",
    "collector_contract_id",
    "target",
    "observed_value",
    "expected_value",
    "status",
    "observed_at",
    "metadata",
    "safety_flags",
)


def get_observation_records_dir() -> Path:
    """Return the ``observation_records/`` directory inside the private data dir."""
    d = get_private_dir() / OBSERVATION_RECORDS_DIR_NAME
    d.mkdir(parents=True, exist_ok=True)
    return d


def _validate_observation_id(observation_id: str) -> str:
    """Validate an observation_id: exactly 32 lowercase hex characters.

    Prevents path traversal by validating before any path construction.
    """
    if not isinstance(observation_id, str):
        raise ValueError("observation_id must be a string.")
    if not OBSERVATION_RECORD_ID_PATTERN.fullmatch(observation_id):
        raise ValueError(
            "observation_id must be exactly 32 lowercase hexadecimal characters."
        )
    return observation_id


def _record_path(observation_id: str) -> Path:
    """Path to a single observation record JSON file."""
    validated = _validate_observation_id(observation_id)
    return (
        get_observation_records_dir()
        / f"{OBSERVATION_RECORD_FILE_PREFIX}{validated}.json"
    )


def _ensure_json_serializable(value: object, path: str = "") -> None:
    """Raise ValueError if value cannot be strictly JSON-serialized.

    Strict check (no default=str) keeps consistency with the Observation
    Record builder's own serializability expectations.
    """
    try:
        json.dumps(value)
    except (TypeError, OverflowError, ValueError) as exc:
        raise ValueError(
            f"Value at {path} is not JSON-serializable: {exc}"
        ) from exc


def _validate_observation_record(record: dict) -> None:
    """Validate a record dict before persistence. Does not mutate the record."""
    if not isinstance(record, dict):
        raise ValueError("observation_record must be a dict.")

    missing = [k for k in _REQUIRED_OBSERVATION_RECORD_KEYS if k not in record]
    if missing:
        raise ValueError(
            "observation_record is missing required keys: "
            + ", ".join(sorted(missing))
        )

    _validate_observation_id(record["observation_id"])

    if record["observation_type"] != "observation_record":
        raise ValueError("observation_type must be 'observation_record'.")

    target = record["target"]
    if not isinstance(target, str) or not target:
        raise ValueError("target must be a non-empty string.")

    if not isinstance(record["metadata"], dict):
        raise ValueError("metadata must be a dict.")

    safety_flags = record["safety_flags"]
    if not isinstance(safety_flags, dict):
        raise ValueError("safety_flags must be a dict.")
    true_flags = [k for k, v in safety_flags.items() if v is not False]
    if true_flags:
        raise ValueError(
            "safety_flags must all be False; found truthy values for: "
            + ", ".join(sorted(true_flags))
        )

    _ensure_json_serializable(record, "observation_record")


def save_observation_record(
    observation_record: dict,
    context: dict | None = None,
) -> dict:
    """Validate and persist an observation record; returns the saved dict.

    The builder-generated observation fields are preserved unchanged.
    Queue envelope fields are added on top of the record.
    """
    _validate_observation_record(observation_record)
    now_iso = datetime.now(_tz.utc).isoformat()

    saved = dict(observation_record)
    saved["created_at"] = now_iso
    saved["updated_at"] = now_iso
    saved["decision"] = None
    saved["decided_at"] = None
    saved["reviewer"] = None
    saved["decision_reason"] = None
    saved["warnings"] = []
    saved["context_metadata"] = dict(context) if context else {}

    path = _record_path(saved["observation_id"])
    path.write_text(json.dumps(saved, indent=2, default=str), encoding="utf-8")
    return saved


def load_observation_record(observation_id: str) -> dict | None:
    """Read one observation record by id. Returns None if not found."""
    path = _record_path(observation_id)
    if not path.exists():
        return None
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def list_observation_records(
    status: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> dict:
    """List observation records, newest first.

    Args:
        status: Optional filter by record status
            ("pending", "matched", "mismatched", "error").
        limit: Maximum number of records to return (1..200).
        offset: Number of records to skip (>= 0).

    Returns:
        A dict with "records", "total", "limit", and "offset".
    """
    if isinstance(limit, bool) or not isinstance(limit, int):
        raise ValueError("limit must be an integer.")
    if limit < 1 or limit > 200:
        raise ValueError("limit must be in the range 1..200.")
    if isinstance(offset, bool) or not isinstance(offset, int):
        raise ValueError("offset must be an integer.")
    if offset < 0:
        raise ValueError("offset must be >= 0.")

    store_dir = get_observation_records_dir()
    records: list[dict] = []
    for p in store_dir.glob(f"{OBSERVATION_RECORD_FILE_PREFIX}*.json"):
        with p.open("r", encoding="utf-8") as f:
            rec = json.load(f)
        if status is not None and rec.get("status") != status:
            continue
        records.append(rec)
    records.sort(key=lambda r: r.get("created_at", ""), reverse=True)
    total = len(records)
    return {
        "records": records[offset : offset + limit],
        "total": total,
        "limit": limit,
        "offset": offset,
    }


def update_observation_record_status(
    observation_id: str,
    status: str,
    reviewer: str | None = None,
    reason: str | None = None,
    context: dict | None = None,
) -> dict | None:
    """Update the status of a persisted observation record.

    Loads the record, applies the lifecycle transition, and persists it.
    Returns the updated record dict; returns None when the record does not
    exist. Raises ValueError for an invalid status.

    The record must currently be "pending"; non-pending records are returned
    unchanged with a warning recorded in ``warnings`` (in memory only — the
    warning is intentionally not persisted).
    """
    if status not in VALID_STATUSES:
        raise ValueError(
            f"Invalid status '{status}'. Must be one of: "
            + ", ".join(sorted(VALID_STATUSES))
            + "."
        )

    path = _record_path(observation_id)
    record = load_observation_record(observation_id)
    if record is None:
        return None

    if record.get("status") != "pending":
        record.setdefault("warnings", []).append(
            f"status not updated: record is not pending (status='{record.get('status')}')"
        )
        return record

    now_iso = datetime.now(_tz.utc).isoformat()
    record["status"] = status
    record["updated_at"] = now_iso
    record["decision"] = status
    record["decided_at"] = now_iso
    record["reviewer"] = reviewer
    record["decision_reason"] = reason
    if context is not None:
        record["context_metadata"] = dict(context)
    path.write_text(json.dumps(record, indent=2, default=str), encoding="utf-8")
    return record


def cancel_observation_record(
    observation_id: str,
    reviewer: str | None = None,
    reason: str | None = None,
    context: dict | None = None,
) -> dict | None:
    """Cancel a pending observation record (thin wrapper around the status update).

    Transitions the record to "cancelled" with decision set to "cancelled" and
    decision_reason set to the supplied reason. Returns the updated record
    dict; returns None when the record does not exist.
    """
    return update_observation_record_status(
        observation_id,
        "cancelled",
        reviewer=reviewer,
        reason=reason,
        context=context,
    )
