"""Human Apply Authorization Request Builder for Aether (Milestone 67A).

Creates a structured human_apply_authorization_request object from an apply_gate_record.
This is synthetic evaluation — it does NOT execute any apply, call executors,
or modify target state. It only evaluates the record data against readiness rules.
"""

from __future__ import annotations


# ── required readiness check names and their severities ──────────────────────

_READINESS_CHECKS = [
    ("apply_gate_record_pending", "low"),
    ("apply_gate_persisted", "low"),
    ("gate_decision_eligible", "high"),
    ("human_review_not_completed", "medium"),
    ("apply_not_authorized", "critical"),
    ("apply_not_executed", "critical"),
    ("rollback_not_executed", "critical"),
    ("execution_flags_blocked", "high"),
    ("apply_flags_blocked", "critical"),
    ("required_confirmations_present", "medium"),
    ("blocking_reasons_empty", "medium"),
]


def _check_apply_gate_record_pending(record: dict, agr: dict) -> dict:
    return {
        "name": "apply_gate_record_pending",
        "passed": record.get("status") == "pending",
        "severity": "low",
        "detail": "Apply gate record status must be pending.",
    }


def _check_apply_gate_persisted(record: dict, agr: dict) -> dict:
    return {
        "name": "apply_gate_persisted",
        "passed": record.get("apply_gate_persisted") is True,
        "severity": "low",
        "detail": "Apply gate must be persisted.",
    }


def _check_gate_decision_eligible(record: dict, agr: dict) -> dict:
    rec_dec = record.get("gate_decision")
    agr_dec = agr.get("decision") if agr else None
    return {
        "name": "gate_decision_eligible",
        "passed": rec_dec == "eligible_for_human_review" and agr_dec == "eligible_for_human_review",
        "severity": "high",
        "detail": "Both gate_decision and apply_gate_request.decision must be 'eligible_for_human_review'.",
    }


def _check_human_review_not_completed(record: dict, agr: dict) -> dict:
    return {
        "name": "human_review_not_completed",
        "passed": record.get("human_review_completed") is False,
        "severity": "medium",
        "detail": "human_review_completed must be false.",
    }


def _check_apply_not_authorized(record: dict, agr: dict) -> dict:
    rec_auth = record.get("apply_authorized")
    agr_auth = agr.get("apply_authorized") if agr else False
    return {
        "name": "apply_not_authorized",
        "passed": rec_auth is False and agr_auth is False,
        "severity": "critical",
        "detail": "Both record.apply_authorized and request.apply_authorized must be false.",
    }


def _check_apply_not_executed(record: dict, agr: dict) -> dict:
    return {
        "name": "apply_not_executed",
        "passed": record.get("apply_executed") is False,
        "severity": "critical",
        "detail": "record.apply_executed must be false.",
    }


def _check_rollback_not_executed(record: dict, agr: dict) -> dict:
    return {
        "name": "rollback_not_executed",
        "passed": record.get("rollback_executed") is False,
        "severity": "critical",
        "detail": "record.rollback_executed must be false.",
    }


def _check_execution_flags_blocked(record: dict, agr: dict) -> dict:
    rec_flds = {"execution_allowed", "tool_execution_allowed", "dry_run_execution_allowed",
                "simulation_execution_allowed", "apply_gate_execution_allowed"}
    agr_flds = {"execution_allowed", "tool_execution_allowed", "dry_run_execution_allowed",
                "simulation_execution_allowed", "apply_gate_execution_allowed"}
    all_rec = all(record.get(k) is False for k in rec_flds)
    all_agr = all(agr.get(k) is False for k in agr_flds) if agr else False
    return {
        "name": "execution_flags_blocked",
        "passed": all_rec and all_agr,
        "severity": "high",
        "detail": "All execution flags must be false in both record and request.",
    }


def _check_apply_flags_blocked(record: dict, agr: dict) -> dict:
    rec_flds = {"apply_allowed", "rollback_allowed"}
    agr_flds = {"apply_allowed", "rollback_allowed"}
    all_rec = all(record.get(k) is False for k in rec_flds)
    all_agr = all(agr.get(k) is False for k in agr_flds) if agr else False
    return {
        "name": "apply_flags_blocked",
        "passed": all_rec and all_agr,
        "severity": "critical",
        "detail": "All apply flags must be false in both record and request.",
    }


def _check_required_confirmations_present(record: dict, agr: dict) -> dict:
    confs = agr.get("required_human_confirmations", []) if agr else []
    return {
        "name": "required_confirmations_present",
        "passed": len(confs) >= 5,
        "severity": "medium",
        "detail": "Apply gate request must contain at least 5 human confirmation items.",
    }


def _check_blocking_reasons_empty(record: dict, agr: dict) -> dict:
    reasons = agr.get("blocking_reasons", []) if agr else []
    return {
        "name": "blocking_reasons_empty",
        "passed": len(reasons) == 0,
        "severity": "medium",
        "detail": "apply_gate_request blocking_reasons must be empty.",
    }


_CHECK_HARDCODED = {
    "apply_gate_record_pending": _check_apply_gate_record_pending,
    "apply_gate_persisted": _check_apply_gate_persisted,
    "gate_decision_eligible": _check_gate_decision_eligible,
    "human_review_not_completed": _check_human_review_not_completed,
    "apply_not_authorized": _check_apply_not_authorized,
    "apply_not_executed": _check_apply_not_executed,
    "rollback_not_executed": _check_rollback_not_executed,
    "execution_flags_blocked": _check_execution_flags_blocked,
    "apply_flags_blocked": _check_apply_flags_blocked,
    "required_confirmations_present": _check_required_confirmations_present,
    "blocking_reasons_empty": _check_blocking_reasons_empty,
}


# ── main builder ─────────────────────────────────────────────────────────────


def build_human_apply_authorization_request(
    apply_gate_record: dict | None,
    context: dict | None = None,
) -> dict:
    """Build a human apply authorization request from an apply gate record.

    Returns a dict. Never returns None — even for missing records
    a blocked request is returned.

    Args:
        apply_gate_record: The saved apply gate record dict.
        context: Optional metadata context (e.g. session_id).

    Returns:
        Human apply authorization request dict.
    """
    _meta: dict = {
        "source": "human_apply_authorization_request_builder",
        "schema_version": "1.0",
    }
    if context and isinstance(context, dict):
        sid = context.get("session_id")
        if sid:
            _meta["session_id"] = sid

    _warns: list[str] = []

    def _empty_request(
        decision: str,
        reason: str,
        gate_status: str | None = None,
        gate_decision: str | None = None,
        ag_id: str | None = None,
        vv_id: str | None = None,
        sr_id: str | None = None,
        sp_id: str | None = None,
        dr_id: str | None = None,
        requested_action=None,
        snapshot=None,
        checks: list[dict] | None = None,
        blocking_reasons: list[str] | None = None,
        unresolved_risks: list[dict] | None = None,
        next_step: str = "",
        extra_wins: list[str] | None = None,
    ) -> dict:
        if extra_wins is None:
            extra_wins = []
        warnings = list(_warns) + list(extra_wins)
        warnings.append("Human authorization request does not authorize apply.")
        warnings.append("No real-world action was executed.")
        warnings.append("A separate future authorization record and apply executor are required.")
        return {
            "human_authorization_required": False,
            "human_authorization_status": "prepared",
            "human_authorization_type": "explicit_human_apply_authorization",
            "decision": decision,
            "reason": reason,
            "apply_gate_id": ag_id,
            "apply_gate_record_status": gate_status,
            "gate_decision": gate_decision,
            "verification_verdict_id": vv_id,
            "simulation_result_id": sr_id,
            "simulation_plan_id": sp_id,
            "dry_run_id": dr_id,
            "requested_action": requested_action,
            "apply_gate_snapshot": snapshot,
            "readiness_checks": checks or [],
            "required_human_confirmations": [],
            "authorization_statement": None,
            "blocking_reasons": blocking_reasons or [],
            "unresolved_risks": unresolved_risks or [],
            "recommended_next_step": next_step,
            "human_review_completed": False,
            "apply_authorized": False,
            "apply_allowed": False,
            "rollback_allowed": False,
            "execution_allowed": False,
            "tool_execution_allowed": False,
            "dry_run_execution_allowed": False,
            "simulation_execution_allowed": False,
            "apply_gate_execution_allowed": False,
            "human_authorization_execution_allowed": False,
            "metadata": dict(_meta),
            "warnings": warnings,
        }

    # --- Rule 1: missing record ---
    if apply_gate_record is None:
        return _empty_request(
            decision="blocked",
            reason="Apply gate record was not found.",
            blocking_reasons=["Apply gate record was not found."],
            next_step="Create or provide a valid apply gate record.",
        )

    record = apply_gate_record
    ag_id = record.get("apply_gate_id")
    rec_status = record.get("status")

    # Extract link fields from nested apply_gate_request
    agr_obj = record.get("apply_gate_request")
    if agr_obj and isinstance(agr_obj, dict):
        verdict_id = agr_obj.get("verification_verdict_id")
        sim_result_id = agr_obj.get("simulation_result_id")
        sim_plan_id = agr_obj.get("simulation_plan_id")
        dry_run_id = agr_obj.get("dry_run_id")
        requested_action = agr_obj.get("requested_action")
        gate_decision = agr_obj.get("decision")
    else:
        verdict_id = None
        sim_result_id = None
        sim_plan_id = None
        dry_run_id = None
        requested_action = None
        gate_decision = None

    # --- Rule 2: status != pending ---
    if rec_status != "pending":
        return _empty_request(
            decision="blocked",
            reason="Apply gate record is not pending.",
            gate_status=rec_status,
            gate_decision=gate_decision,
            ag_id=ag_id,
            vv_id=verdict_id,
            sr_id=sim_result_id,
            sp_id=sim_plan_id,
            dr_id=dry_run_id,
            requested_action=requested_action,
            snapshot=dict(agr_obj) if agr_obj else None,
            blocking_reasons=["Record status is not pending."],
            next_step="Use a pending apply gate record or create a new one.",
        )

    # --- Rule 3: apply_authorized is True ---
    if record.get("apply_authorized") is True:
        return _empty_request(
            decision="blocked",
            reason="Apply gate record is unexpectedly marked apply-authorized.",
            gate_status=rec_status,
            gate_decision=gate_decision,
            ag_id=ag_id,
            vv_id=verdict_id,
            sr_id=sim_result_id,
            sp_id=sim_plan_id,
            dr_id=dry_run_id,
            requested_action=requested_action,
            snapshot=dict(agr_obj) if agr_obj else None,
            blocking_reasons=["apply_authorized is true."],
            next_step="Resolve the apply_authorized flag before continuing.",
        )

    # --- Rule 4: apply_executed or rollback_executed ---
    block_reasons: list[str] = []
    if record.get("apply_executed") is True:
        block_reasons.append("apply_executed is true.")
    if record.get("rollback_executed") is True:
        block_reasons.append("rollback_executed is true.")
    if block_reasons:
        return _empty_request(
            decision="blocked",
            reason="Apply gate record indicates execution already occurred.",
            gate_status=rec_status,
            gate_decision=gate_decision,
            ag_id=ag_id,
            vv_id=verdict_id,
            sr_id=sim_result_id,
            sp_id=sim_plan_id,
            dr_id=dry_run_id,
            requested_action=requested_action,
            snapshot=dict(agr_obj) if agr_obj else None,
            blocking_reasons=block_reasons,
            next_step="Resolve the execution flags before continuing.",
        )

    # --- Rule 5: missing/invalid apply_gate_request ---
    if agr_obj is None or not isinstance(agr_obj, dict):
        return _empty_request(
            decision="not_ready",
            reason="Apply gate request payload is missing or invalid.",
            gate_status=rec_status,
            gate_decision=gate_decision,
            ag_id=ag_id,
            vv_id=verdict_id,
            sr_id=sim_result_id,
            sp_id=sim_plan_id,
            dr_id=dry_run_id,
            unresolved_risks=[{
                "name": "missing_apply_gate_request",
                "severity": "high",
                "detail": "Apply gate request payload is missing or not a dict.",
            }],
            next_step="Regenerate the apply gate request.",
        )

    # --- Rule 6: gate_decision must be eligible_for_human_review ---
    if gate_decision == "not_eligible":
        unresolved = list(agr_obj.get("unresolved_risks", []))
        return _empty_request(
            decision="not_ready",
            reason="Apply gate record is not eligible for human authorization.",
            gate_status=rec_status,
            gate_decision=gate_decision,
            ag_id=ag_id,
            vv_id=verdict_id,
            sr_id=sim_result_id,
            sp_id=sim_plan_id,
            dr_id=dry_run_id,
            requested_action=requested_action,
            snapshot=dict(agr_obj),
            unresolved_risks=unresolved,
            blocking_reasons=["Apply gate decision is not_eligible."],
            next_step="Resolve readiness issues before requesting human authorization.",
        )
    elif gate_decision == "blocked":
        unresolved = list(agr_obj.get("unresolved_risks", []))
        return _empty_request(
            decision="blocked",
            reason="Apply gate record is blocked.",
            gate_status=rec_status,
            gate_decision=gate_decision,
            ag_id=ag_id,
            vv_id=verdict_id,
            sr_id=sim_result_id,
            sp_id=sim_plan_id,
            dr_id=dry_run_id,
            requested_action=requested_action,
            snapshot=dict(agr_obj),
            unresolved_risks=unresolved,
            blocking_reasons=["Apply gate decision is blocked."],
            next_step="Resolve blocking conditions before continuing.",
        )
    elif gate_decision != "eligible_for_human_review":
        unresolved = list(agr_obj.get("unresolved_risks", []))
        return _empty_request(
            decision="blocked",
            reason="Unsupported apply gate decision.",
            gate_status=rec_status,
            gate_decision=gate_decision,
            ag_id=ag_id,
            vv_id=verdict_id,
            sr_id=sim_result_id,
            sp_id=sim_plan_id,
            dr_id=dry_run_id,
            requested_action=requested_action,
            snapshot=dict(agr_obj),
            unresolved_risks=unresolved,
            blocking_reasons=[f"Unsupported gate decision: {gate_decision!r}."],
            next_step="Resolve blocking conditions before continuing.",
        )

    # --- Rule 7: evaluate readiness checks for eligible gate ---
    checks: list[dict] = []
    for check_name, _ in _READINESS_CHECKS:
        fn = _CHECK_HARDCODED[check_name]
        check_result = fn(record, agr_obj)
        checks.append(check_result)

    # --- Copy warnings from apply_gate_request with prefix ---
    agr_warnings = agr_obj.get("warnings", [])
    for w in agr_warnings:
        _warns.append(f"apply_gate_request_warning: {w}")

    # --- Rule 8: decision logic ---
    has_critical_fail = any(c.get("passed") is False for c in checks if c.get("severity") == "critical")
    has_high_fail = any(c.get("passed") is False for c in checks if c.get("severity") == "high")
    has_medium_fail = any(c.get("passed") is False for c in checks if c.get("severity") == "medium")
    has_low_fail = any(c.get("passed") is False for c in checks if c.get("severity") == "low")

    if has_critical_fail or has_high_fail:
        auth_decision = "blocked"
        human_auth_required = False
    elif has_medium_fail or has_low_fail:
        auth_decision = "not_ready"
        human_auth_required = False
    else:
        auth_decision = "ready_for_human_authorization"
        human_auth_required = True

    # --- Build unresolved_risks ---
    unresolved_risks: list[dict] = list(agr_obj.get("unresolved_risks", []))
    if auth_decision == "ready_for_human_authorization":
        unresolved_risks.append({
            "name": "human_review_not_performed",
            "severity": "medium",
            "detail": "Human authorization has not yet been obtained.",
        })

    # --- Build blocking_reasons ---
    blocking_reasons: list[str] = list(agr_obj.get("blocking_reasons", []))
    if auth_decision == "blocked":
        if has_critical_fail:
            for c in checks:
                if c.get("passed") is False and c.get("severity") == "critical":
                    blocking_reasons.append(f"Critical readiness check failed: {c['name']}.")
        if has_high_fail:
            for c in checks:
                if c.get("passed") is False and c.get("severity") == "high":
                    blocking_reasons.append(f"High readiness check failed: {c['name']}.")

    # --- recommended_next_step ---
    step_map = {
        "ready_for_human_authorization": "Present this request to a human reviewer in a future authorization record milestone; do not apply changes yet.",
        "not_ready": "Resolve readiness issues before requesting human authorization.",
        "blocked": "Resolve blocking conditions before continuing.",
    }

    # --- required_human_confirmations ---
    confirmations = [
        "I confirm the requested action is still desired.",
        "I confirm the target is correct.",
        "I reviewed the dry-run, simulation result, and verification verdict.",
        "I understand rollback may not be possible or automatic.",
        "I understand this authorization request still does not execute the action.",
        "I understand a separate future apply executor is required.",
    ]

    # --- authorization_statement ---
    auth_statement = None
    if auth_decision == "ready_for_human_authorization":
        auth_statement = "Human authorization is required before any future apply executor may be considered. This request does not authorize or execute apply."

    # Finalize warnings
    warnings = list(_warns)
    warnings.append("Human authorization request does not authorize apply.")
    warnings.append("No real-world action was executed.")
    warnings.append("A separate future authorization record and apply executor are required.")

    return {
        "human_authorization_required": human_auth_required,
        "human_authorization_status": "prepared",
        "human_authorization_type": "explicit_human_apply_authorization",
        "decision": auth_decision,
        "reason": _build_ready_fallback_reason(checks) if auth_decision == "ready_for_human_authorization" else ("Readiness checks did not pass." if auth_decision == "not_ready" else "Blocking conditions present."),
        "apply_gate_id": ag_id,
        "apply_gate_record_status": rec_status,
        "gate_decision": gate_decision,
        "verification_verdict_id": verdict_id,
        "simulation_result_id": sim_result_id,
        "simulation_plan_id": sim_plan_id,
        "dry_run_id": dry_run_id,
        "requested_action": dict(requested_action) if requested_action else None,
        "apply_gate_snapshot": dict(agr_obj),
        "readiness_checks": checks,
        "required_human_confirmations": confirmations,
        "authorization_statement": auth_statement,
        "blocking_reasons": blocking_reasons,
        "unresolved_risks": unresolved_risks,
        "recommended_next_step": step_map.get(auth_decision, "Resolve blocking conditions before continuing."),
        "human_review_completed": False,
        "apply_authorized": False,
        "apply_allowed": False,
        "rollback_allowed": False,
        "execution_allowed": False,
        "tool_execution_allowed": False,
        "dry_run_execution_allowed": False,
        "simulation_execution_allowed": False,
        "apply_gate_execution_allowed": False,
        "human_authorization_execution_allowed": False,
        "metadata": dict(_meta),
        "warnings": warnings,
    }


def _build_ready_fallback_reason(checks: list[dict]) -> str:
    """If every check passes, return ready reason; otherwise return first fail detail."""
    failed = [c for c in checks if c.get("passed") is False]
    if not failed:
        return "All readiness checks passed. Request qualifies for human authorization review."
    return failed[0]["detail"]
