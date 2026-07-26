"""Apply Execution Gate Request Builder for Aether (Milestone 69A).

Creates a structured apply_execution_gate_request object from a human_authorization_record.
This is synthetic evaluation — it does NOT execute any apply, call executors,
or modify target state. It only evaluates the record data against readiness rules.
"""

from __future__ import annotations


_CHECK_NAMES = [
    ("human_authorization_approved_intent", "low"),
    ("human_authorization_persisted", "low"),
    ("authorization_decision_ready", "high"),
    ("human_review_completed", "low"),
    ("human_intent_recorded", "low"),
    ("confirmations_received", "medium"),
    ("request_ready_for_human_authorization", "high"),
    ("apply_not_authorized", "critical"),
    ("apply_not_executed", "critical"),
    ("rollback_not_executed", "critical"),
    ("execution_flags_blocked", "high"),
    ("apply_flags_blocked", "critical"),
    ("requested_action_present", "medium"),
    ("blocking_reasons_empty", "medium"),
]


def _check_human_authorization_approved_intent(ha_rec: dict, haar: dict | None) -> dict:
    return {
        "name": "human_authorization_approved_intent",
        "passed": ha_rec.get("status") == "approved_intent",
        "severity": "low",
        "detail": "Human authorization record status must be approved_intent.",
    }


def _check_human_authorization_persisted(ha_rec: dict, haar: dict | None) -> dict:
    return {
        "name": "human_authorization_persisted",
        "passed": ha_rec.get("human_authorization_persisted") is True,
        "severity": "low",
        "detail": "Human authorization record must be persisted.",
    }


def _check_authorization_decision_ready(ha_rec: dict, haar: dict | None) -> dict:
    rec_dec = ha_rec.get("authorization_decision")
    req_dec = haar.get("decision") if haar else None
    return {
        "name": "authorization_decision_ready",
        "passed": rec_dec == "ready_for_human_authorization" and req_dec == "ready_for_human_authorization",
        "severity": "high",
        "detail": "Both authorization_decision and request.decision must be 'ready_for_human_authorization'.",
    }


def _check_human_review_completed(ha_rec: dict, haar: dict | None) -> dict:
    return {
        "name": "human_review_completed",
        "passed": ha_rec.get("human_review_completed") is True,
        "severity": "low",
        "detail": "human_review_completed must be true.",
    }


def _check_human_intent_recorded(ha_rec: dict, haar: dict | None) -> dict:
    return {
        "name": "human_intent_recorded",
        "passed": ha_rec.get("human_intent_recorded") is True,
        "severity": "low",
        "detail": "human_intent_recorded must be true.",
    }


def _check_confirmations_received(ha_rec: dict, haar: dict | None) -> dict:
    req = ha_rec.get("confirmations_required", [])
    rcv = ha_rec.get("confirmations_received", [])
    if not req:
        return {"name": "confirmations_received", "passed": len(rcv) > 0, "severity": "medium", "detail": "No confirmations required but confirmations received."}
    all_covered = all(r in rcv for r in req)
    return {
        "name": "confirmations_received",
        "passed": all_covered,
        "severity": "medium",
        "detail": "All required confirmations must be present in confirmations_received.",
    }


def _check_request_ready_for_human_auth(ha_rec: dict, haar: dict | None) -> dict:
    req_dec = haar.get("decision") if haar else None
    return {
        "name": "request_ready_for_human_authorization",
        "passed": req_dec == "ready_for_human_authorization",
        "severity": "high",
        "detail": "The human apply authorization request decision must be 'ready_for_human_authorization'.",
    }


def _check_apply_not_authorized(ha_rec: dict, haar: dict | None) -> dict:
    rec_auth = ha_rec.get("apply_authorized")
    req_auth = haar.get("apply_authorized") if haar else False
    return {
        "name": "apply_not_authorized",
        "passed": rec_auth is False and req_auth is False,
        "severity": "critical",
        "detail": "Both record.apply_authorized and request.apply_authorized must be false.",
    }


def _check_apply_not_executed(ha_rec: dict, haar: dict | None) -> dict:
    return {
        "name": "apply_not_executed",
        "passed": ha_rec.get("apply_executed") is False,
        "severity": "critical",
        "detail": "record.apply_executed must be false.",
    }


def _check_rollback_not_executed(ha_rec: dict, haar: dict | None) -> dict:
    return {
        "name": "rollback_not_executed",
        "passed": ha_rec.get("rollback_executed") is False,
        "severity": "critical",
        "detail": "record.rollback_executed must be false.",
    }


def _check_execution_flags_blocked(ha_rec: dict, haar: dict | None) -> dict:
    rec_flds = {"execution_allowed", "tool_execution_allowed", "dry_run_execution_allowed",
                "simulation_execution_allowed", "apply_gate_execution_allowed", "human_authorization_execution_allowed"}
    req_flds = {"execution_allowed", "tool_execution_allowed", "dry_run_execution_allowed",
                "simulation_execution_allowed", "apply_gate_execution_allowed", "human_authorization_execution_allowed"}
    all_rec = all(ha_rec.get(k) is False for k in rec_flds)
    all_req = all(haar.get(k) is False for k in req_flds) if haar else False
    return {
        "name": "execution_flags_blocked",
        "passed": all_rec and all_req,
        "severity": "high",
        "detail": "All execution flags must be false in both record and request.",
    }


def _check_apply_flags_blocked(ha_rec: dict, haar: dict | None) -> dict:
    rec_flds = {"apply_allowed", "rollback_allowed"}
    req_flds = {"apply_allowed", "rollback_allowed"}
    all_rec = all(ha_rec.get(k) is False for k in rec_flds)
    all_req = all(haar.get(k) is False for k in req_flds) if haar else False
    return {
        "name": "apply_flags_blocked",
        "passed": all_rec and all_req,
        "severity": "critical",
        "detail": "All apply flags must be false in both record and request.",
    }


def _check_requested_action_present(ha_rec: dict, haar: dict | None) -> dict:
    ra = haar.get("requested_action") if haar else None
    return {
        "name": "requested_action_present",
        "passed": ra is not None and isinstance(ra, dict),
        "severity": "medium",
        "detail": "The apply gate request must contain a non-null requested_action dict.",
    }


def _check_blocking_reasons_empty(ha_rec: dict, haar: dict | None) -> dict:
    reasons = haar.get("blocking_reasons", []) if haar else []
    return {
        "name": "blocking_reasons_empty",
        "passed": len(reasons) == 0,
        "severity": "medium",
        "detail": "human_apply_authorization_request blocking_reasons must be empty.",
    }


_CHECK_HARDCODED = {
    "human_authorization_approved_intent": _check_human_authorization_approved_intent,
    "human_authorization_persisted": _check_human_authorization_persisted,
    "authorization_decision_ready": _check_authorization_decision_ready,
    "human_review_completed": _check_human_review_completed,
    "human_intent_recorded": _check_human_intent_recorded,
    "confirmations_received": _check_confirmations_received,
    "request_ready_for_human_authorization": _check_request_ready_for_human_auth,
    "apply_not_authorized": _check_apply_not_authorized,
    "apply_not_executed": _check_apply_not_executed,
    "rollback_not_executed": _check_rollback_not_executed,
    "execution_flags_blocked": _check_execution_flags_blocked,
    "apply_flags_blocked": _check_apply_flags_blocked,
    "requested_action_present": _check_requested_action_present,
    "blocking_reasons_empty": _check_blocking_reasons_empty,
}


def build_apply_execution_gate_request(
    human_authorization_record: dict | None,
    context: dict | None = None,
) -> dict:
    """Build an apply execution gate request from a human authorization record.

    Returns a dict. Never returns None — even for missing records
    a blocked request is returned.

    Args:
        human_authorization_record: The saved human authorization record dict.
        context: Optional metadata context (e.g. session_id).

    Returns:
        Apply execution gate request dict.
    """
    _meta: dict = {
        "source": "apply_execution_gate_request_builder",
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
        ha_status: str | None = None,
        auth_dec: str | None = None,
        ha_id: str | None = None,
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
        warnings.append("Apply execution gate request does not authorize execution.")
        warnings.append("No real-world action was executed.")
        warnings.append("A separate future executor is required before apply can occur.")
        return {
            "apply_execution_gate_required": False,
            "apply_execution_gate_status": "prepared",
            "apply_execution_gate_type": "final_pre_execution_gate",
            "decision": decision,
            "reason": reason,
            "human_authorization_id": ha_id,
            "human_authorization_record_status": ha_status,
            "authorization_decision": auth_dec,
            "apply_gate_id": ag_id,
            "verification_verdict_id": vv_id,
            "simulation_result_id": sr_id,
            "simulation_plan_id": sp_id,
            "dry_run_id": dr_id,
            "requested_action": requested_action,
            "human_authorization_snapshot": snapshot,
            "pre_execution_checks": checks or [],
            "required_pre_execution_confirmations": [],
            "execution_statement": None,
            "blocking_reasons": blocking_reasons or [],
            "unresolved_risks": unresolved_risks or [],
            "recommended_next_step": next_step,
            "human_review_completed": False,
            "human_intent_recorded": False,
            "apply_authorized": False,
            "apply_allowed": False,
            "rollback_allowed": False,
            "execution_allowed": False,
            "tool_execution_allowed": False,
            "dry_run_execution_allowed": False,
            "simulation_execution_allowed": False,
            "apply_gate_execution_allowed": False,
            "human_authorization_execution_allowed": False,
            "apply_execution_gate_execution_allowed": False,
            "metadata": dict(_meta),
            "warnings": warnings,
        }

    # --- Rule 1: missing record ---
    if human_authorization_record is None:
        return _empty_request(
            decision="blocked",
            reason="Human authorization record was not found.",
            blocking_reasons=["Human authorization record was not found."],
            next_step="Create or provide a valid human authorization record.",
        )

    ha_rec = human_authorization_record
    ha_id_val = ha_rec.get("human_authorization_id")
    ha_status = ha_rec.get("status")

    # Extract fields from nested human_apply_authorization_request
    haar_obj = ha_rec.get("human_apply_authorization_request")
    is_haar_missing = haar_obj is None or not isinstance(haar_obj, dict)

    if not is_haar_missing:
        ag_id_val = haar_obj.get("apply_gate_id")
        vv_id_val = haar_obj.get("verification_verdict_id")
        sr_id_val = haar_obj.get("simulation_result_id")
        sp_id_val = haar_obj.get("simulation_plan_id")
        dr_id_val = haar_obj.get("dry_run_id")
        requested_action = haar_obj.get("requested_action")
        auth_dec = haar_obj.get("decision")
    else:
        ag_id_val = None
        vv_id_val = None
        sr_id_val = None
        sp_id_val = None
        dr_id_val = None
        requested_action = None
        auth_dec = None

    # --- Rule 2: status != approved_intent ---
    if ha_status != "approved_intent":
        return _empty_request(
            decision="blocked",
            reason="Human authorization record is not approved_intent.",
            ha_status=ha_status,
            auth_dec=auth_dec,
            ha_id=ha_id_val,
            ag_id=ag_id_val,
            vv_id=vv_id_val,
            sr_id=sr_id_val,
            sp_id=sp_id_val,
            dr_id=dr_id_val,
            requested_action=requested_action,
            snapshot=dict(haar_obj) if haar_obj else None,
            blocking_reasons=["Record status is not approved_intent."],
            next_step="Record human approval intent before requesting execution gate review.",
        )

    # --- Rule 3: missing/invalid haar (moved before authorization_decision check) ---
    if is_haar_missing:
        return _empty_request(
            decision="not_ready",
            reason="Human apply authorization request payload is missing or invalid.",
            ha_status=ha_status,
            auth_dec=auth_dec,
            ha_id=ha_id_val,
            ag_id=ag_id_val,
            vv_id=vv_id_val,
            sr_id=sr_id_val,
            sp_id=sp_id_val,
            dr_id=dr_id_val,
            unresolved_risks=[{
                "name": "missing_human_authorization_request",
                "severity": "high",
                "detail": "Human apply authorization request payload is missing or not a dict.",
            }],
            next_step="Regenerate the human authorization request and approval-intent record.",
        )

    # --- Rule 3: authorization_decision not ready ---
    if auth_dec != "ready_for_human_authorization":
        return _empty_request(
            decision="blocked",
            reason="Human authorization record was not based on a ready authorization request.",
            ha_status=ha_status,
            auth_dec=auth_dec,
            ha_id=ha_id_val,
            ag_id=ag_id_val,
            vv_id=vv_id_val,
            sr_id=sr_id_val,
            sp_id=sp_id_val,
            dr_id=dr_id_val,
            requested_action=requested_action,
            snapshot=dict(haar_obj) if haar_obj else None,
            blocking_reasons=["Authorization decision is not ready_for_human_authorization."],
            next_step="Record human approval intent before requesting execution gate review.",
        )

    # --- Rule 4: human_intent_recorded not True ---
    if ha_rec.get("human_intent_recorded") is not True:
        return _empty_request(
            decision="blocked",
            reason="Human intent has not been recorded.",
            ha_status=ha_status,
            auth_dec=auth_dec,
            ha_id=ha_id_val,
            ag_id=ag_id_val,
            vv_id=vv_id_val,
            sr_id=sr_id_val,
            sp_id=sp_id_val,
            dr_id=dr_id_val,
            requested_action=requested_action,
            snapshot=dict(haar_obj) if haar_obj else None,
            blocking_reasons=["human_intent_recorded is not true."],
            next_step="Record human approval intent before requesting execution gate review.",
        )

    # --- Rule 5: human_review_completed not True ---
    if ha_rec.get("human_review_completed") is not True:
        return _empty_request(
            decision="blocked",
            reason="Human review is not completed.",
            ha_status=ha_status,
            auth_dec=auth_dec,
            ha_id=ha_id_val,
            ag_id=ag_id_val,
            vv_id=vv_id_val,
            sr_id=sr_id_val,
            sp_id=sp_id_val,
            dr_id=dr_id_val,
            requested_action=requested_action,
            snapshot=dict(haar_obj) if haar_obj else None,
            blocking_reasons=["human_review_completed is not true."],
            next_step="Record human approval intent before requesting execution gate review.",
        )

    # --- Rule 6: apply_authorized is True ---
    if ha_rec.get("apply_authorized") is True:
        return _empty_request(
            decision="blocked",
            reason="Human authorization record is unexpectedly marked apply-authorized.",
            ha_status=ha_status,
            auth_dec=auth_dec,
            ha_id=ha_id_val,
            ag_id=ag_id_val,
            vv_id=vv_id_val,
            sr_id=sr_id_val,
            sp_id=sp_id_val,
            dr_id=dr_id_val,
            requested_action=requested_action,
            snapshot=dict(haar_obj) if haar_obj else None,
            blocking_reasons=["apply_authorized is true."],
            next_step="Resolve the apply_authorized flag before continuing.",
        )

    # --- Rule 7: apply_executed or rollback_executed ---
    block_reasons: list[str] = []
    if ha_rec.get("apply_executed") is True:
        block_reasons.append("apply_executed is true.")
    if ha_rec.get("rollback_executed") is True:
        block_reasons.append("rollback_executed is true.")
    if block_reasons:
        return _empty_request(
            decision="blocked",
            reason="Human authorization record indicates execution already occurred.",
            ha_status=ha_status,
            auth_dec=auth_dec,
            ha_id=ha_id_val,
            ag_id=ag_id_val,
            vv_id=vv_id_val,
            sr_id=sr_id_val,
            sp_id=sp_id_val,
            dr_id=dr_id_val,
            requested_action=requested_action,
            snapshot=dict(haar_obj) if haar_obj else None,
            blocking_reasons=block_reasons,
            next_step="Resolve the execution flags before continuing.",
        )

    # --- Rule 9: evaluate pre-execution checks ---
    checks: list[dict] = []
    for check_name, _ in _CHECK_NAMES:
        fn = _CHECK_HARDCODED[check_name]
        check_result = fn(ha_rec, haar_obj)
        checks.append(check_result)

    # --- Copy warnings from haar with prefix ---
    haar_warnings = haar_obj.get("warnings", [])
    for w in haar_warnings:
        _warns.append(f"human_authorization_request_warning: {w}")

    # --- Rule 10: decision logic ---
    has_critical_fail = any(c.get("passed") is False for c in checks if c.get("severity") == "critical")
    has_high_fail = any(c.get("passed") is False for c in checks if c.get("severity") == "high")
    has_medium_fail = any(c.get("passed") is False for c in checks if c.get("severity") == "medium")
    has_low_fail = any(c.get("passed") is False for c in checks if c.get("severity") == "low")

    if has_critical_fail or has_high_fail:
        gate_dec = "blocked"
        exec_gate_required = False
    elif has_medium_fail or has_low_fail:
        gate_dec = "not_ready"
        exec_gate_required = False
    else:
        gate_dec = "ready_for_execution_gate_review"
        exec_gate_required = True

    # --- Build unresolved_risks ---
    unresolved_risks: list[dict] = list(haar_obj.get("unresolved_risks", []))
    if gate_dec == "ready_for_execution_gate_review":
        unresolved_risks.append({
            "name": "execute_gate_required",
            "severity": "medium",
            "detail": "A future apply execution gate and executor are still required.",
        })

    # --- Build blocking_reasons ---
    blocking_reasons: list[str] = list(haar_obj.get("blocking_reasons", []))
    if gate_dec == "blocked":
        if has_critical_fail:
            for c in checks:
                if c.get("passed") is False and c.get("severity") == "critical":
                    blocking_reasons.append(f"Critical pre-execution check failed: {c['name']}.")
        if has_high_fail:
            for c in checks:
                if c.get("passed") is False and c.get("severity") == "high":
                    blocking_reasons.append(f"High pre-execution check failed: {c['name']}.")

    # --- recommended_next_step ---
    step_map = {
        "ready_for_execution_gate_review": "Present this request to a future apply execution gate record milestone; do not execute changes yet.",
        "not_ready": "Resolve pre-execution readiness issues before requesting execution gate review.",
        "blocked": "Resolve blocking conditions before continuing.",
    }

    # --- required_pre_execution_confirmations ---
    confirmations = [
        "I confirm human approval intent was recorded.",
        "I confirm the requested action is still desired.",
        "I confirm the target is correct.",
        "I understand this execution gate request still does not execute the action.",
        "I understand a separate future apply executor is required.",
        "I understand rollback may not be possible or automatic.",
    ]

    # --- execution_statement ---
    execution_statement = None
    if gate_dec == "ready_for_execution_gate_review":
        execution_statement = "Apply execution gate review is required before any future executor may be considered. This request does not authorize or execute apply."

    # Finalize warnings
    warnings = list(_warns)
    warnings.append("Apply execution gate request does not authorize execution.")
    warnings.append("No real-world action was executed.")
    warnings.append("A separate future executor is required before apply can occur.")

    return {
        "apply_execution_gate_required": exec_gate_required,
        "apply_execution_gate_status": "prepared",
        "apply_execution_gate_type": "final_pre_execution_gate",
        "decision": gate_dec,
        "reason": _build_ready_fallback_reason(checks) if gate_dec == "ready_for_execution_gate_review" else ("Pre-execution checks did not pass." if gate_dec == "not_ready" else "Blocking conditions present."),
        "human_authorization_id": ha_id_val,
        "human_authorization_record_status": ha_status,
        "authorization_decision": auth_dec,
        "apply_gate_id": ag_id_val,
        "verification_verdict_id": vv_id_val,
        "simulation_result_id": sr_id_val,
        "simulation_plan_id": sp_id_val,
        "dry_run_id": dr_id_val,
        "requested_action": dict(requested_action) if requested_action else None,
        "human_authorization_snapshot": dict(haar_obj),
        "pre_execution_checks": checks,
        "required_pre_execution_confirmations": confirmations,
        "execution_statement": execution_statement,
        "blocking_reasons": blocking_reasons,
        "unresolved_risks": unresolved_risks,
        "recommended_next_step": step_map.get(gate_dec, "Resolve blocking conditions before continuing."),
        "human_review_completed": ha_rec.get("human_review_completed", False),
        "human_intent_recorded": ha_rec.get("human_intent_recorded", False),
        "apply_authorized": False,
        "apply_allowed": False,
        "rollback_allowed": False,
        "execution_allowed": False,
        "tool_execution_allowed": False,
        "dry_run_execution_allowed": False,
        "simulation_execution_allowed": False,
        "apply_gate_execution_allowed": False,
        "human_authorization_execution_allowed": False,
        "apply_execution_gate_execution_allowed": False,
        "metadata": dict(_meta),
        "warnings": warnings,
    }


def _build_ready_fallback_reason(checks: list[dict]) -> str:
    """If every check passes, return ready reason; otherwise return first fail detail."""
    failed = [c for c in checks if c.get("passed") is False]
    if not failed:
        return "All pre-execution checks passed. Record qualifies for execution gate review."
    return failed[0]["detail"]
