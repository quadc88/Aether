"""Verification Verdict Record Store for Aether (Milestone 64A).

Manages persistent verification verdict records stored under the configured private
data directory as individual JSON files named ``verification_verdict_<id>.json``.

This module does NOT execute any simulation, call any executor, apply changes,
or modify any system state beyond writing/reading its own files.
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone as _tz
from pathlib import Path

from aether.core.config import get_private_dir


def _ensure_verification_verdict_dir() -> Path:
    """Return the ``verification_verdicts/`` directory inside the private data dir."""
    d = get_private_dir() / "verification_verdicts"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _record_path(verification_verdict_id: str) -> Path:
    """Path to a single verification verdict record JSON file."""
    return _ensure_verification_verdict_dir() / f"verification_verdict_{verification_verdict_id}.json"


# --------------------------------------------------------------------------- #
# Core API
# --------------------------------------------------------------------------- #


def create_verification_verdict_record(
    verification_verdict: dict,
    context: dict | None = None,
) -> dict:
    """Create and persist a new pending verification verdict record.

    Args:
        verification_verdict: The structured verification verdict dict from build_simulation_verification_verdict().
        context: Optional metadata context (e.g. session_id).

    Returns:
        The saved verification verdict record dict.
    """
    verification_verdict_id = uuid.uuid4().hex
    now_iso = datetime.now(_tz.utc).isoformat()

    verdict_decision = verification_verdict.get("decision")

    record: dict = {
        "verification_verdict_id": verification_verdict_id,
        "status": "pending",
        "verification_verdict": dict(verification_verdict),
        "verdict_decision": verdict_decision if verdict_decision else None,
        "created_at": now_iso,
        "updated_at": now_iso,
        "decision": verdict_decision,
        "decided_at": None,
        "reviewer": None,
        "decision_reason": None,
        "verdict_persisted": True,
        "apply_authorized": False,
        "simulation_executed": False,
        "execution_allowed": False,
        "tool_execution_allowed": False,
        "dry_run_execution_allowed": False,
        "simulation_execution_allowed": False,
        "apply_allowed": False,
        "rollback_allowed": False,
        "verdict_apply_allowed": False,
        "metadata": dict(context) if context else {},
        "warnings": list(verification_verdict.get("warnings", [])),
    }

    path = _record_path(verification_verdict_id)
    path.write_text(json.dumps(record, indent=2, default=str), encoding="utf-8")
    return record


def get_verification_verdict_record(verification_verdict_id: str) -> dict | None:
    """Read one verification verdict record by id. Returns None if not found."""
    path = _record_path(verification_verdict_id)
    if not path.exists():
        return None
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def list_verification_verdict_records(
    status: str | None = None,
    decision: str | None = None,
    limit: int = 50,
) -> list[dict]:
    """List verification verdict records, newest first.

    Args:
        status: Optional filter by status ("pending", "cancelled").
        decision: Optional filter by verdict decision ("pass", "warning", "fail", "blocked").
        limit: Maximum number of records to return.
    """
    run_dir = _ensure_verification_verdict_dir()
    records: list[dict] = []
    for p in run_dir.glob("verification_verdict_*.json"):
        with p.open("r", encoding="utf-8") as f:
            rec = json.load(f)
        if status is not None and rec.get("status") != status:
            continue
        if decision is not None and rec.get("verdict_decision") != decision:
            continue
        records.append(rec)
    records.sort(key=lambda r: r.get("created_at", ""), reverse=True)
    return records[:limit]


def update_verification_verdict_record_status(
    verification_verdict_id: str,
    decision: str,
    reviewer: str | None = None,
    reason: str | None = None,
) -> dict | None:
    """Update a verification verdict record's status.

    Allowed decisions: ``"cancelled"`` only.

    Only records with status ``"pending"`` may be transitioned.
    If already cancelled, the original record is returned unchanged with a warning.

    Args:
        verification_verdict_id: Id of the record to update.
        decision: Must be "cancelled".
        reviewer: Name/identifier of the reviewer.
        reason: Decision reason string.

    Returns:
        The updated record dict, or None if not found.
    """
    valid_decisions = {"cancelled"}
    if decision not in valid_decisions:
        raise ValueError(f"Invalid decision: {decision}. Must be one of {valid_decisions}.")

    record = get_verification_verdict_record(verification_verdict_id)
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

    # Safety: ALL execution flags stay false in Milestone 64A
    record["verdict_persisted"] = True
    record["apply_authorized"] = False
    record["simulation_executed"] = False
    record["execution_allowed"] = False
    record["tool_execution_allowed"] = False
    record["dry_run_execution_allowed"] = False
    record["simulation_execution_allowed"] = False
    record["apply_allowed"] = False
    record["rollback_allowed"] = False
    record["verdict_apply_allowed"] = False
    record["warnings"] = warnings

    path = _record_path(verification_verdict_id)
    path.write_text(json.dumps(record, indent=2, default=str), encoding="utf-8")
    return record
