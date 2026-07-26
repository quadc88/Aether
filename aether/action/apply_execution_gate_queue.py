"""Apply Execution Gate Record Store for Aether (Milestone 70A).

Manages persistent apply execution gate records stored under the configured private
data directory as individual JSON files named ``apply_execution_gate_<id>.json``.

This module does NOT execute any apply, call any executor, apply changes,
or modify any system state beyond writing/reading its own files.
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone as _tz
from pathlib import Path

from aether.core.config import get_private_dir


def _ensure_apply_exec_gate_dir() -> Path:
    """Return the ``apply_execution_gates/`` directory inside the private data dir."""
    d = get_private_dir() / "apply_execution_gates"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _record_path(apply_execution_gate_id: str) -> Path:
    """Path to a single apply execution gate record JSON file."""
    return _ensure_apply_exec_gate_dir() / f"apply_execution_gate_{apply_execution_gate_id}.json"


# --------------------------------------------------------------------------- #
# Core API
# --------------------------------------------------------------------------- #


def create_apply_execution_gate_record(
    apply_execution_gate_request: dict,
    context: dict | None = None,
) -> dict:
    """Create and persist a new pending apply execution gate record.

    Args:
        apply_execution_gate_request: The structured AEGR dict from
            build_apply_execution_gate_request().
        context: Optional metadata context (e.g. session_id).

    Returns:
        The saved apply execution gate record dict.
    """
    apply_execution_gate_id = uuid.uuid4().hex
    now_iso = datetime.now(_tz.utc).isoformat()

    gate_decision = apply_execution_gate_request.get("decision")
    confirmations_required = apply_execution_gate_request.get(
        "required_pre_execution_confirmations", []
    )

    record: dict = {
        "apply_execution_gate_id": apply_execution_gate_id,
        "status": "pending",
        "apply_execution_gate_request": dict(apply_execution_gate_request),
        "gate_decision": gate_decision if gate_decision else None,
        "human_authorization_id": apply_execution_gate_request.get("human_authorization_id"),
        "apply_gate_id": apply_execution_gate_request.get("apply_gate_id"),
        "verification_verdict_id": apply_execution_gate_request.get("verification_verdict_id"),
        "simulation_result_id": apply_execution_gate_request.get("simulation_result_id"),
        "simulation_plan_id": apply_execution_gate_request.get("simulation_plan_id"),
        "dry_run_id": apply_execution_gate_request.get("dry_run_id"),
        "created_at": now_iso,
        "updated_at": now_iso,
        "decision": gate_decision,
        "decided_at": None,
        "reviewer": None,
        "decision_reason": None,
        "confirmations_required": list(confirmations_required),
        "confirmations_received": [],
        "apply_execution_gate_persisted": True,
        "execution_review_completed": False,
        "execution_intent_recorded": False,
        "apply_authorized": False,
        "apply_executed": False,
        "rollback_executed": False,
        "simulation_executed": False,
        "execution_allowed": False,
        "tool_execution_allowed": False,
        "dry_run_execution_allowed": False,
        "simulation_execution_allowed": False,
        "apply_gate_execution_allowed": False,
        "human_authorization_execution_allowed": False,
        "apply_execution_gate_execution_allowed": False,
        "apply_allowed": False,
        "rollback_allowed": False,
        "metadata": dict(context) if context else {},
        "warnings": list(apply_execution_gate_request.get("warnings", [])),
    }

    path = _record_path(apply_execution_gate_id)
    path.write_text(json.dumps(record, indent=2, default=str), encoding="utf-8")
    return record


def get_apply_execution_gate_record(
    apply_execution_gate_id: str,
) -> dict | None:
    """Read one apply execution gate record by id. Returns None if not found."""
    path = _record_path(apply_execution_gate_id)
    if not path.exists():
        return None
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def list_apply_execution_gate_records(
    status: str | None = None,
    decision: str | None = None,
    limit: int = 50,
) -> list[dict]:
    """List apply execution gate records, newest first.

    Args:
        status: Optional filter by status
            ("pending", "cancelled", "rejected", "approved_execution_intent").
        decision: Optional filter by gate_decision
            ("ready_for_execution_gate_review", "not_ready", "blocked").
        limit: Maximum number of records to return.
    """
    run_dir = _ensure_apply_exec_gate_dir()
    records: list[dict] = []
    for p in run_dir.glob("apply_execution_gate_*.json"):
        with p.open("r", encoding="utf-8") as f:
            rec = json.load(f)
        if status is not None and rec.get("status") != status:
            continue
        if decision is not None and rec.get("gate_decision") != decision:
            continue
        records.append(rec)
    records.sort(key=lambda r: r.get("created_at", ""), reverse=True)
    return records[:limit]


def update_apply_execution_gate_record_status(
    apply_execution_gate_id: str,
    decision: str,
    reviewer: str | None = None,
    reason: str | None = None,
    confirmations: list[str] | None = None,
) -> dict | None:
    """Update an apply execution gate record's status.

    Allowed decisions: "cancelled", "rejected", "approved_execution_intent".

    Only records with status "pending" may be transitioned.
    approved_execution_intent requires:
      - gate_decision == "ready_for_execution_gate_review"
      - apply_execution_gate_request.apply_execution_gate_required is True
      - required confirmations are present and non-empty
      - provided confirmations cover all required items

    If already final, the original record is returned unchanged with a warning.

    Args:
        apply_execution_gate_id: Id of the record to update.
        decision: One of cancelled / rejected / approved_execution_intent.
        reviewer: Name/identifier of the reviewer.
        reason: Decision reason string.
        confirmations: List of confirmation strings submitted by the reviewer.

    Returns:
        The updated record dict, or None if not found.
    """
    valid_decisions = {"cancelled", "rejected", "approved_execution_intent"}
    if decision not in valid_decisions:
        raise ValueError(
            f"Invalid decision: {decision}. Must be one of {valid_decisions}."
        )

    record = get_apply_execution_gate_record(apply_execution_gate_id)
    if record is None:
        return None

    warnings = list(record.get("warnings", []))

    if record["status"] not in ("pending",):
        warnings.append(
            f"Record is already '{record['status']}'. No state change applied."
        )
        record["warnings"] = warnings
        return record

    now_iso = datetime.now(_tz.utc).isoformat()

    if decision == "approved_execution_intent":
        auth_dec = record.get("gate_decision")
        if auth_dec != "ready_for_execution_gate_review":
            warnings.append(
                "Cannot approve intent: gate_decision is not ready_for_execution_gate_review."
            )
            record["warnings"] = warnings
            return None

        aegr_req = record.get("apply_execution_gate_request", {})
        if not aegr_req.get("apply_execution_gate_required"):
            warnings.append(
                "Cannot approve intent: apply_execution_gate_required is not true."
            )
            record["warnings"] = warnings
            return None

        req_confirms = record.get("confirmations_required", [])
        if not req_confirms:
            warnings.append(
                "Cannot approve intent: no confirmations were required."
            )
            record["warnings"] = warnings
            return None

        if confirmations is None or len(confirmations) == 0:
            warnings.append(
                "Cannot approve intent: no confirmations provided."
            )
            record["warnings"] = warnings
            return None

        for rc in req_confirms:
            if rc not in confirmations:
                warnings.append(f"Confirmation missing: '{rc}'.")
                record["warnings"] = warnings
                return None

        record["status"] = "approved_execution_intent"
        record["decision"] = "approved_execution_intent"
        record["decided_at"] = now_iso
        record["reviewer"] = reviewer
        record["decision_reason"] = reason
        record["updated_at"] = now_iso
        record["execution_review_completed"] = True
        record["execution_intent_recorded"] = True
        record["confirmations_received"] = list(confirmations)
        record["apply_execution_gate_persisted"] = True
        record["apply_authorized"] = False
        record["apply_executed"] = False
        record["rollback_executed"] = False
        record["simulation_executed"] = False
        record["execution_allowed"] = False
        record["tool_execution_allowed"] = False
        record["dry_run_execution_allowed"] = False
        record["simulation_execution_allowed"] = False
        record["apply_gate_execution_allowed"] = False
        record["human_authorization_execution_allowed"] = False
        record["apply_execution_gate_execution_allowed"] = False
        record["apply_allowed"] = False
        record["rollback_allowed"] = False
        record["warnings"] = warnings
        record["warnings"].append(
            "Execution intent recorded only; apply is not authorized."
        )
        record["warnings"].append(
            "A separate future apply executor contract is required."
        )

    elif decision == "rejected":
        record["status"] = "rejected"
        record["decision"] = "rejected"
        record["decided_at"] = now_iso
        record["reviewer"] = reviewer
        record["decision_reason"] = reason
        record["updated_at"] = now_iso
        record["execution_review_completed"] = True
        record["execution_intent_recorded"] = False
        record["warnings"] = warnings

    elif decision == "cancelled":
        record["status"] = "cancelled"
        record["decision"] = "cancelled"
        record["decided_at"] = now_iso
        record["reviewer"] = reviewer
        record["decision_reason"] = reason
        record["updated_at"] = now_iso
        record["execution_review_completed"] = False
        record["execution_intent_recorded"] = False
        record["warnings"] = warnings

    path = _record_path(apply_execution_gate_id)
    path.write_text(json.dumps(record, indent=2, default=str), encoding="utf-8")
    return record
