"""Dry-Run Record Store for Aether (Milestone 57A).

Manages persistent dry-run records stored under the configured private data
directory as individual JSON files named ``dry_run_<id>.json``.

This module does NOT execute any dry-run, call any executor, apply changes,
or modify any system state beyond writing/reading its own files.
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone as _tz
from pathlib import Path

from aether.core.config import get_private_dir


def _ensure_dry_run_dir() -> Path:
    """Return the ``dry_runs/`` directory inside the private data dir."""
    d = get_private_dir() / "dry_runs"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _record_path(dry_run_id: str) -> Path:
    """Path to a single dry-run record JSON file."""
    return _ensure_dry_run_dir() / f"dry_run_{dry_run_id}.json"


# --------------------------------------------------------------------------- #
# Core API
# --------------------------------------------------------------------------- #


def create_dry_run_record(
    dry_run_request: dict,
    context: dict | None = None,
) -> dict:
    """Create and persist a new pending dry-run record.

    Args:
        dry_run_request: The structured request dict from build_dry_run_request().
        context: Optional metadata context (e.g. session_id).

    Returns:
        The saved dry-run record dict.
    """
    dry_run_id = uuid.uuid4().hex
    now_iso = datetime.now(_tz.utc).isoformat()

    record: dict = {
        "dry_run_id": dry_run_id,
        "status": "pending",
        "dry_run_request": dict(dry_run_request),
        "created_at": now_iso,
        "updated_at": now_iso,
        "decision": None,
        "decided_at": None,
        "reviewer": None,
        "decision_reason": None,
        "dry_run_executed": False,
        "execution_allowed": False,
        "tool_execution_allowed": False,
        "apply_allowed": False,
        "rollback_allowed": False,
        "metadata": dict(context) if context else {},
        "warnings": [],
    }

    path = _record_path(dry_run_id)
    path.write_text(json.dumps(record, indent=2, default=str), encoding="utf-8")
    return record


def get_dry_run_record(dry_run_id: str) -> dict | None:
    """Read one dry-run record by id. Returns None if not found."""
    path = _record_path(dry_run_id)
    if not path.exists():
        return None
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def list_dry_run_records(
    status: str | None = None,
    limit: int = 50,
) -> list[dict]:
    """List dry-run records, newest first.

    Args:
        status: Optional filter by status ("pending", "cancelled").
        limit: Maximum number of records to return.
    """
    run_dir = _ensure_dry_run_dir()
    records: list[dict] = []
    for p in run_dir.glob("dry_run_*.json"):
        with p.open("r", encoding="utf-8") as f:
            rec = json.load(f)
        if status is not None and rec.get("status") != status:
            continue
        records.append(rec)
    records.sort(key=lambda r: r.get("created_at", ""), reverse=True)
    return records[:limit]


def update_dry_run_record_status(
    dry_run_id: str,
    decision: str,
    reviewer: str | None = None,
    reason: str | None = None,
) -> dict | None:
    """Update a dry-run record's status.

    Allowed decisions: ``"cancelled"`` only.

    Only records with status ``"pending"`` may be transitioned.
    If already cancelled, the original record is returned unchanged with a warning.

    Args:
        dry_run_id: Id of the record to update.
        decision: Must be "cancelled".
        reviewer: Name/identifier of the reviewer.
        reason: Decision reason string.

    Returns:
        The updated record dict, or None if not found.
    """
    valid_decisions = {"cancelled"}
    if decision not in valid_decisions:
        raise ValueError(f"Invalid decision: {decision}. Must be one of {valid_decisions}.")

    record = get_dry_run_record(dry_run_id)
    if record is None:
        return None

    warnings = list(record.get("warnings", []))

    if record["status"] != "pending":
        warnings.append(
            f"Record is already '{record['status']}'. No state change applied."
        )
        record["warnings"] = warnings
        return record

    now_iso = datetime.now(_tz.utc).isoformat()
    record["status"] = decision
    record["decision"] = decision
    record["decided_at"] = now_iso
    record["reviewer"] = reviewer
    record["decision_reason"] = reason
    record["updated_at"] = now_iso
    record["dry_run_executed"] = False
    record["execution_allowed"] = False
    record["tool_execution_allowed"] = False
    record["apply_allowed"] = False
    record["rollback_allowed"] = False
    record["warnings"] = warnings

    path = _record_path(dry_run_id)
    path.write_text(json.dumps(record, indent=2, default=str), encoding="utf-8")
    return record
