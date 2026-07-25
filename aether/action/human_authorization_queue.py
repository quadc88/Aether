"""Human Authorization Record Store for Aether (Milestone 68A).

Manages persistent human authorization records stored under the configured private
data directory as individual JSON files named ``human_authorization_<id>.json``.

This module does NOT execute any apply, call any executor, apply changes,
or modify any system state beyond writing/reading its own files.
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone as _tz
from pathlib import Path

from aether.core.config import get_private_dir


def _ensure_human_auth_dir() -> Path:
    """Return the ``human_authorizations/`` directory inside the private data dir."""
    d = get_private_dir() / "human_authorizations"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _record_path(human_authorization_id: str) -> Path:
    """Path to a single human authorization record JSON file."""
    return _ensure_human_auth_dir() / f"human_authorization_{human_authorization_id}.json"


# --------------------------------------------------------------------------- #
# Core API
# --------------------------------------------------------------------------- #


def create_human_authorization_record(
    human_apply_authorization_request: dict,
    context: dict | None = None,
) -> dict:
    """Create and persist a new pending human authorization record.

    Args:
        human_apply_authorization_request: The structured HA request dict from build_human_apply_authorization_request().
        context: Optional metadata context (e.g. session_id).

    Returns:
        The saved human authorization record dict.
    """
    human_authorization_id = uuid.uuid4().hex
    now_iso = datetime.now(_tz.utc).isoformat()

    auth_decision = human_apply_authorization_request.get("decision")
    confirmations_required = human_apply_authorization_request.get("required_human_confirmations", [])
    verification_verdict_id = human_apply_authorization_request.get("verification_verdict_id")
    simulation_result_id = human_apply_authorization_request.get("simulation_result_id")
    simulation_plan_id = human_apply_authorization_request.get("simulation_plan_id")
    dry_run_id = human_apply_authorization_request.get("dry_run_id")
    requested_action = human_apply_authorization_request.get("requested_action")

    record: dict = {
        "human_authorization_id": human_authorization_id,
        "status": "pending",
        "human_apply_authorization_request": dict(human_apply_authorization_request),
        "authorization_decision": auth_decision if auth_decision else None,
        "apply_gate_id": human_apply_authorization_request.get("apply_gate_id"),
        "verification_verdict_id": verification_verdict_id,
        "simulation_result_id": simulation_result_id,
        "simulation_plan_id": simulation_plan_id,
        "dry_run_id": dry_run_id,
        "created_at": now_iso,
        "updated_at": now_iso,
        "decision": auth_decision,
        "decided_at": None,
        "reviewer": None,
        "decision_reason": None,
        "confirmations_required": list(confirmations_required),
        "confirmations_received": [],
        "human_authorization_persisted": True,
        "human_review_completed": False,
        "human_intent_recorded": False,
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
        "apply_allowed": False,
        "rollback_allowed": False,
        "metadata": dict(context) if context else {},
        "warnings": list(human_apply_authorization_request.get("warnings", [])),
    }

    path = _record_path(human_authorization_id)
    path.write_text(json.dumps(record, indent=2, default=str), encoding="utf-8")
    return record


def get_human_authorization_record(human_authorization_id: str) -> dict | None:
    """Read one human authorization record by id. Returns None if not found."""
    path = _record_path(human_authorization_id)
    if not path.exists():
        return None
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def list_human_authorization_records(
    status: str | None = None,
    decision: str | None = None,
    limit: int = 50,
) -> list[dict]:
    """List human authorization records, newest first.

    Args:
        status: Optional filter by status ("pending", "cancelled", "rejected", "approved_intent").
        decision: Optional filter by authorization_decision.
        limit: Maximum number of records to return.
    """
    run_dir = _ensure_human_auth_dir()
    records: list[dict] = []
    for p in run_dir.glob("human_authorization_*.json"):
        with p.open("r", encoding="utf-8") as f:
            rec = json.load(f)
        if status is not None and rec.get("status") != status:
            continue
        if decision is not None and rec.get("authorization_decision") != decision:
            continue
        records.append(rec)
    records.sort(key=lambda r: r.get("created_at", ""), reverse=True)
    return records[:limit]


def update_human_authorization_record_status(
    human_authorization_id: str,
    decision: str,
    reviewer: str | None = None,
    reason: str | None = None,
    confirmations: list[str] | None = None,
) -> dict | None:
    """Update a human authorization record's status.

    Allowed decisions: "cancelled", "rejected", "approved_intent".

    Only records with status "pending" may be transitioned.
    approved_intent requires:
      - authorization_decision == "ready_for_human_authorization"
      - required confirmations are present
      - provided confirmations cover all required items

    If already final, the original record is returned unchanged with a warning.

    Args:
        human_authorization_id: Id of the record to update.
        decision: One of cancelled / rejected / approved_intent.
        reviewer: Name/identifier of the reviewer.
        reason: Decision reason string.
        confirmations: List of confirmation strings submitted by the reviewer.

    Returns:
        The updated record dict, or None if not found.
    """
    valid_decisions = {"cancelled", "rejected", "approved_intent"}
    if decision not in valid_decisions:
        raise ValueError(f"Invalid decision: {decision}. Must be one of {valid_decisions}.")

    record = get_human_authorization_record(human_authorization_id)
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

    if decision == "approved_intent":
        # Validate approve-intent conditions
        auth_dec = record.get("authorization_decision")
        if auth_dec != "ready_for_human_authorization":
            warnings.append(
                "Cannot approve intent: authorization_decision is not ready_for_human_authorization."
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

        # Deterministic coverage check: every required confirmation must appear in provided list
        for rc in req_confirms:
            if rc not in confirmations:
                warnings.append(
                    f"Confirmation missing: '{rc}'."
                )
                record["warnings"] = warnings
                return None

        # Update for approved_intent
        record["status"] = "approved_intent"
        record["decision"] = "approved_intent"
        record["decided_at"] = now_iso
        record["reviewer"] = reviewer
        record["decision_reason"] = reason
        record["updated_at"] = now_iso
        record["human_review_completed"] = True
        record["human_intent_recorded"] = True
        record["confirmations_received"] = list(confirmations)
        record["human_authorization_persisted"] = True
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
        record["apply_allowed"] = False
        record["rollback_allowed"] = False
        record["warnings"] = warnings
        record["warnings"].append("Human intent recorded only; apply is not authorized.")
        record["warnings"].append("A separate future apply execution gate is required.")

    elif decision == "rejected":
        record["status"] = "rejected"
        record["decision"] = "rejected"
        record["decided_at"] = now_iso
        record["reviewer"] = reviewer
        record["decision_reason"] = reason
        record["updated_at"] = now_iso
        record["human_review_completed"] = True
        record["human_intent_recorded"] = False
        record["warnings"] = warnings

    elif decision == "cancelled":
        record["status"] = "cancelled"
        record["decision"] = "cancelled"
        record["decided_at"] = now_iso
        record["reviewer"] = reviewer
        record["decision_reason"] = reason
        record["updated_at"] = now_iso
        record["human_review_completed"] = False
        record["human_intent_recorded"] = False
        record["warnings"] = warnings

    path = _record_path(human_authorization_id)
    path.write_text(json.dumps(record, indent=2, default=str), encoding="utf-8")
    return record
