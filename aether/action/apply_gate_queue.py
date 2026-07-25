"""Apply Gate Record Store for Aether (Milestone 66A).

Manages persistent apply gate records stored under the configured private
data directory as individual JSON files named ``apply_gate_<id>.json``.

This module does NOT execute any apply, call any executor, apply changes,
or modify any system state beyond writing/reading its own files.
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone as _tz
from pathlib import Path

from aether.core.config import get_private_dir


def _ensure_apply_gate_dir() -> Path:
    """Return the ``apply_gates/`` directory inside the private data dir."""
    d = get_private_dir() / "apply_gates"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _record_path(apply_gate_id: str) -> Path:
    """Path to a single apply gate record JSON file."""
    return _ensure_apply_gate_dir() / f"apply_gate_{apply_gate_id}.json"


# --------------------------------------------------------------------------- #
# Core API
# --------------------------------------------------------------------------- #


def create_apply_gate_record(
    apply_gate_request: dict,
    context: dict | None = None,
) -> dict:
    """Create and persist a new pending apply gate record.

    Args:
        apply_gate_request: The structured apply gate request dict from build_apply_gate_request().
        context: Optional metadata context (e.g. session_id).

    Returns:
        The saved apply gate record dict.
    """
    apply_gate_id = uuid.uuid4().hex
    now_iso = datetime.now(_tz.utc).isoformat()

    gate_decision = apply_gate_request.get("decision")

    # Extract link fields from apply_gate_request
    verification_verdict_id = apply_gate_request.get("verification_verdict_id")
    simulation_result_id = apply_gate_request.get("simulation_result_id")
    simulation_plan_id = apply_gate_request.get("simulation_plan_id")
    dry_run_id = apply_gate_request.get("dry_run_id")

    record: dict = {
        "apply_gate_id": apply_gate_id,
        "status": "pending",
        "apply_gate_request": dict(apply_gate_request),
        "gate_decision": gate_decision if gate_decision else None,
        "verification_verdict_id": verification_verdict_id,
        "simulation_result_id": simulation_result_id,
        "simulation_plan_id": simulation_plan_id,
        "dry_run_id": dry_run_id,
        "created_at": now_iso,
        "updated_at": now_iso,
        "decision": gate_decision,
        "decided_at": None,
        "reviewer": None,
        "decision_reason": None,
        "apply_gate_persisted": True,
        "human_review_completed": False,
        "apply_authorized": False,
        "apply_executed": False,
        "rollback_executed": False,
        "simulation_executed": False,
        "execution_allowed": False,
        "tool_execution_allowed": False,
        "dry_run_execution_allowed": False,
        "simulation_execution_allowed": False,
        "apply_gate_execution_allowed": False,
        "apply_allowed": False,
        "rollback_allowed": False,
        "metadata": dict(context) if context else {},
        "warnings": list(apply_gate_request.get("warnings", [])),
    }

    path = _record_path(apply_gate_id)
    path.write_text(json.dumps(record, indent=2, default=str), encoding="utf-8")
    return record


def get_apply_gate_record(apply_gate_id: str) -> dict | None:
    """Read one apply gate record by id. Returns None if not found."""
    path = _record_path(apply_gate_id)
    if not path.exists():
        return None
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def list_apply_gate_records(
    status: str | None = None,
    decision: str | None = None,
    limit: int = 50,
) -> list[dict]:
    """List apply gate records, newest first.

    Args:
        status: Optional filter by status ("pending", "cancelled").
        decision: Optional filter by gate_decision.
        limit: Maximum number of records to return.
    """
    run_dir = _ensure_apply_gate_dir()
    records: list[dict] = []
    for p in run_dir.glob("apply_gate_*.json"):
        with p.open("r", encoding="utf-8") as f:
            rec = json.load(f)
        if status is not None and rec.get("status") != status:
            continue
        if decision is not None and rec.get("gate_decision") != decision:
            continue
        records.append(rec)
    records.sort(key=lambda r: r.get("created_at", ""), reverse=True)
    return records[:limit]


def update_apply_gate_record_status(
    apply_gate_id: str,
    decision: str,
    reviewer: str | None = None,
    reason: str | None = None,
) -> dict | None:
    """Update an apply gate record's status.

    Allowed decisions: ``"cancelled"`` only.

    Only records with status ``"pending"`` may be transitioned.
    If already cancelled, the original record is returned unchanged with a warning.

    Args:
        apply_gate_id: Id of the record to update.
        decision: Must be "cancelled".
        reviewer: Name/identifier of the reviewer.
        reason: Decision reason string.

    Returns:
        The updated record dict, or None if not found.
    """
    valid_decisions = {"cancelled"}
    if decision not in valid_decisions:
        raise ValueError(f"Invalid decision: {decision}. Must be one of {valid_decisions}.")

    record = get_apply_gate_record(apply_gate_id)
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

    # Safety: ALL execution flags stay false in Milestone 66A
    record["apply_gate_persisted"] = True
    record["human_review_completed"] = False
    record["apply_authorized"] = False
    record["apply_executed"] = False
    record["rollback_executed"] = False
    record["simulation_executed"] = False
    record["execution_allowed"] = False
    record["tool_execution_allowed"] = False
    record["dry_run_execution_allowed"] = False
    record["simulation_execution_allowed"] = False
    record["apply_gate_execution_allowed"] = False
    record["apply_allowed"] = False
    record["rollback_allowed"] = False
    record["warnings"] = warnings

    path = _record_path(apply_gate_id)
    path.write_text(json.dumps(record, indent=2, default=str), encoding="utf-8")
    return record
