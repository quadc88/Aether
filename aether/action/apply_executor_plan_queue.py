"""Apply Executor Plan Record Store for Aether (Milestone 74A).

Manages persistent apply executor plan records stored under the configured private
data directory as individual JSON files named ``apply_executor_plan_<id>.json``.

This module does NOT execute any apply, call any executor, apply changes,
collect evidence, or attach rollback plans — only writing/reading its own files.
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone as _tz
from pathlib import Path

from aether.core.config import get_private_dir


def _ensure_exec_plan_dir() -> Path:
    """Return the ``apply_executor_plans/`` directory inside the private data dir."""
    d = get_private_dir() / "apply_executor_plans"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _record_path(apply_executor_plan_id: str) -> Path:
    """Path to a single apply executor plan record JSON file."""
    return _ensure_exec_plan_dir() / f"apply_executor_plan_{apply_executor_plan_id}.json"


# --------------------------------------------------------------------------- #
# Core API
# --------------------------------------------------------------------------- #


def create_apply_executor_plan_record(
    apply_executor_plan: dict,
    context: dict | None = None,
) -> dict:
    """Create and persist a new pending apply executor plan record.

    Args:
        apply_executor_plan: The structured plan dict from build_apply_executor_plan().
        context: Optional metadata context (e.g. session_id).

    Returns:
        The saved apply executor plan record dict.
    """
    apply_executor_plan_id = uuid.uuid4().hex
    now_iso = datetime.now(_tz.utc).isoformat()

    plan_decision = apply_executor_plan.get("decision")
    confirmations_required = apply_executor_plan.get(
        "required_plan_confirmations", []
    )

    record: dict = {
        "apply_executor_plan_id": apply_executor_plan_id,
        "status": "pending",
        "apply_executor_plan": dict(apply_executor_plan),
        "plan_decision": plan_decision if plan_decision else None,
        "apply_executor_contract_id": apply_executor_plan.get("apply_executor_contract_id"),
        "apply_execution_gate_id": apply_executor_plan.get("apply_execution_gate_id"),
        "human_authorization_id": apply_executor_plan.get("human_authorization_id"),
        "apply_gate_id": apply_executor_plan.get("apply_gate_id"),
        "verification_verdict_id": apply_executor_plan.get("verification_verdict_id"),
        "simulation_result_id": apply_executor_plan.get("simulation_result_id"),
        "simulation_plan_id": apply_executor_plan.get("simulation_plan_id"),
        "dry_run_id": apply_executor_plan.get("dry_run_id"),
        "created_at": now_iso,
        "updated_at": now_iso,
        "decision": plan_decision,
        "decided_at": None,
        "reviewer": None,
        "decision_reason": None,
        "confirmations_required": list(confirmations_required),
        "confirmations_received": [],
        "apply_executor_plan_persisted": True,
        "plan_review_completed": False,
        "plan_intent_recorded": False,
        "evidence_collected": False,
        "rollback_plan_attached": False,
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
        "apply_executor_contract_execution_allowed": False,
        "apply_executor_plan_execution_allowed": False,
        "apply_allowed": False,
        "rollback_allowed": False,
        "metadata": dict(context) if context else {},
        "warnings": list(apply_executor_plan.get("warnings", [])),
    }

    path = _record_path(apply_executor_plan_id)
    path.write_text(json.dumps(record, indent=2, default=str), encoding="utf-8")
    return record


def get_apply_executor_plan_record(
    apply_executor_plan_id: str,
) -> dict | None:
    """Read one apply executor plan record by id. Returns None if not found."""
    path = _record_path(apply_executor_plan_id)
    if not path.exists():
        return None
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def list_apply_executor_plan_records(
    status: str | None = None,
    decision: str | None = None,
    limit: int = 50,
) -> list[dict]:
    """List apply executor plan records, newest first.

    Args:
        status: Optional filter by status
            ("pending", "cancelled", "rejected", "approved_plan_intent").
        decision: Optional filter by plan_decision
            ("plan_ready", "not_ready", "blocked").
        limit: Maximum number of records to return.
    """
    run_dir = _ensure_exec_plan_dir()
    records: list[dict] = []
    for p in run_dir.glob("apply_executor_plan_*.json"):
        with p.open("r", encoding="utf-8") as f:
            rec = json.load(f)
        if status is not None and rec.get("status") != status:
            continue
        if decision is not None and rec.get("plan_decision") != decision:
            continue
        records.append(rec)
    records.sort(key=lambda r: r.get("created_at", ""), reverse=True)
    return records[:limit]


def update_apply_executor_plan_record_status(
    apply_executor_plan_id: str,
    decision: str,
    reviewer: str | None = None,
    reason: str | None = None,
    confirmations: list[str] | None = None,
) -> dict | None:
    """Update an apply executor plan record's status.

    Allowed decisions: "cancelled", "rejected", "approved_plan_intent".

    Only records with status "pending" may be transitioned.
    approved_plan_intent requires:
      - plan_decision == "plan_ready"
      - apply_executor_plan.plan_required is True
      - required confirmations are present and non-empty
      - provided confirmations cover all required items

    If already final, the original record is returned unchanged with a warning.

    Args:
        apply_executor_plan_id: Id of the record to update.
        decision: One of cancelled / rejected / approved_plan_intent.
        reviewer: Name/identifier of the reviewer.
        reason: Decision reason string.
        confirmations: List of confirmation strings submitted by the reviewer.

    Returns:
        The updated record dict, or None if not found.
    """
    valid_decisions = {"cancelled", "rejected", "approved_plan_intent"}
    if decision not in valid_decisions:
        raise ValueError(
            f"Invalid decision: {decision}. Must be one of {valid_decisions}."
        )

    record = get_apply_executor_plan_record(apply_executor_plan_id)
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

    if decision == "approved_plan_intent":
        auth_dec = record.get("plan_decision")
        if auth_dec != "plan_ready":
            warnings.append(
                "Cannot approve intent: plan_decision is not plan_ready."
            )
            record["warnings"] = warnings
            return None

        aep_req = record.get("apply_executor_plan", {})
        if not aep_req.get("plan_required"):
            warnings.append(
                "Cannot approve intent: plan_required is not true."
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

        record["status"] = "approved_plan_intent"
        record["decision"] = "approved_plan_intent"
        record["decided_at"] = now_iso
        record["reviewer"] = reviewer
        record["decision_reason"] = reason
        record["updated_at"] = now_iso
        record["plan_review_completed"] = True
        record["plan_intent_recorded"] = True
        record["confirmations_received"] = list(confirmations)
        record["apply_executor_plan_persisted"] = True
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
        record["apply_executor_contract_execution_allowed"] = False
        record["apply_executor_plan_execution_allowed"] = False
        record["apply_allowed"] = False
        record["rollback_allowed"] = False
        # These remain always false in this milestone
        record["evidence_collected"] = False
        record["rollback_plan_attached"] = False
        record["warnings"] = warnings
        record["warnings"].append(
            "Plan intent recorded only; apply is not authorized."
        )
        record["warnings"].append(
            "A separate future apply executor evidence/execution milestone is required."
        )
        record["warnings"].append(
            "Evidence has not been collected."
        )
        record["warnings"].append(
            "Rollback plan has not been attached."
        )

    elif decision == "rejected":
        record["status"] = "rejected"
        record["decision"] = "rejected"
        record["decided_at"] = now_iso
        record["reviewer"] = reviewer
        record["decision_reason"] = reason
        record["updated_at"] = now_iso
        record["plan_review_completed"] = True
        record["plan_intent_recorded"] = False
        record["evidence_collected"] = False
        record["rollback_plan_attached"] = False
        record["warnings"] = warnings

    elif decision == "cancelled":
        record["status"] = "cancelled"
        record["decision"] = "cancelled"
        record["decided_at"] = now_iso
        record["reviewer"] = reviewer
        record["decision_reason"] = reason
        record["updated_at"] = now_iso
        record["plan_review_completed"] = False
        record["plan_intent_recorded"] = False
        record["evidence_collected"] = False
        record["rollback_plan_attached"] = False
        record["warnings"] = warnings

    path = _record_path(apply_executor_plan_id)
    path.write_text(json.dumps(record, indent=2, default=str), encoding="utf-8")
    return record
