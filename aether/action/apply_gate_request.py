"""Apply Gate Request Builder for Aether (Milestone 65A).

Creates a structured apply_gate_request object from a verification_verdict_record.
This is synthetic evaluation — it does NOT execute any apply, call executors,
or modify target state. It only evaluates the record data against eligibility rules.
"""

from __future__ import annotations


# ── required eligibility check names and their severities ──────────────────────

_CHECK_NAMES = [
    ("verdict_record_pending", "low"),
    ("verdict_persisted", "low"),
    ("verdict_decision_pass", "high"),
    ("apply_not_authorized_yet", "critical"),
    ("apply_flags_blocked", "critical"),
    ("execution_flags_blocked", "high"),
    ("unresolved_risks_only_real_apply", "medium"),
    ("blocking_reasons_empty", "medium"),
]


def _check_verdict_record_pending(
    verdict_record: dict, vv: dict
) -> dict:
    return {
        "name": "verdict_record_pending",
        "passed": verdict_record.get("status") == "pending",
        "severity": "low",
        "detail": "Verification verdict record status must be pending.",
    }


def _check_verdict_persisted(verdict_record: dict, vv: dict) -> dict:
    return {
        "name": "verdict_persisted",
        "passed": verdict_record.get("verdict_persisted") is True,
        "severity": "low",
        "detail": "Verdict must be persisted.",
    }


def _check_verdict_decision_pass(verdict_record: dict, vv: dict) -> dict:
    rec_dec = verdict_record.get("verdict_decision")
    vv_dec = vv.get("decision")
    return {
        "name": "verdict_decision_pass",
        "passed": rec_dec == "pass" and vv_dec == "pass",
        "severity": "high",
        "detail": "Both verdict_decision and verification_verdict.decision must be 'pass'.",
    }


def _check_apply_not_authorized_yet(verdict_record: dict, vv: dict) -> dict:
    return {
        "name": "apply_not_authorized_yet",
        "passed": (
            verdict_record.get("apply_authorized") is False
            and vv.get("apply_allowed") is False
        ),
        "severity": "critical",
        "detail": "Both record.apply_authorized and verdict.apply_allowed must be false.",
    }


def _check_apply_flags_blocked(verdict_record: dict, vv: dict) -> dict:
    rec_flds = {
        "apply_allowed", "verdict_apply_allowed",
    }
    vv_flds = {
        "apply_allowed", "verdict_apply_allowed",
    }
    all_rec = all(verdict_record.get(k) is False for k in rec_flds)
    all_vv = all(vv.get(k) is False for k in vv_flds)
    return {
        "name": "apply_flags_blocked",
        "passed": all_rec and all_vv,
        "severity": "critical",
        "detail": "All apply flags must be false in both record and verdict.",
    }


def _check_execution_flags_blocked(verdict_record: dict, vv: dict) -> dict:
    rec_flds = {
        "execution_allowed", "tool_execution_allowed",
        "dry_run_execution_allowed", "simulation_execution_allowed",
    }
    vv_flds = {
        "execution_allowed", "tool_execution_allowed",
        "dry_run_execution_allowed", "simulation_execution_allowed",
    }
    all_rec = all(verdict_record.get(k) is False for k in rec_flds)
    all_vv = all(vv.get(k) is False for k in vv_flds)
    return {
        "name": "execution_flags_blocked",
        "passed": all_rec and all_vv,
        "severity": "high",
        "detail": "All execution flags must be false in both record and verdict.",
    }


def _check_unresolved_risks_only_real_apply(verdict_record: dict, vv: dict) -> dict:
    risks = vv.get("unresolved_risks", [])
    if not risks:
        return {
            "name": "unresolved_risks_only_real_apply",
            "passed": True,
            "severity": "medium",
            "detail": "No unresolved risks present.",
        }
    allowed = {"real_apply_not_authorized"}
    all_ok = all(r.get("name") in allowed for r in risks)
    return {
        "name": "unresolved_risks_only_real_apply",
        "passed": all_ok,
        "severity": "medium",
        "detail": "Only real_apply_not_authorized risks are allowed as unresolved." if all_ok else "Unexpected unresolved risks found.",
    }


def _check_blocking_reasons_empty(verdict_record: dict, vv: dict) -> dict:
    reasons = vv.get("blocking_reasons", [])
    return {
        "name": "blocking_reasons_empty",
        "passed": len(reasons) == 0,
        "severity": "medium",
        "detail": "verification_verdict blocking_reasons must be empty.",
    }


_CHECK_HARDCODED = {
    "verdict_record_pending": _check_verdict_record_pending,
    "verdict_persisted": _check_verdict_persisted,
    "verdict_decision_pass": _check_verdict_decision_pass,
    "apply_not_authorized_yet": _check_apply_not_authorized_yet,
    "apply_flags_blocked": _check_apply_flags_blocked,
    "execution_flags_blocked": _check_execution_flags_blocked,
    "unresolved_risks_only_real_apply": _check_unresolved_risks_only_real_apply,
    "blocking_reasons_empty": _check_blocking_reasons_empty,
}


# ── main builder ─────────────────────────────────────────────────────────────


def build_apply_gate_request(
    verification_verdict_record: dict | None,
    context: dict | None = None,
) -> dict:
    """Build an apply gate request from a verification verdict record.

    Returns a dict. Never returns None — even for missing records
    a blocked request is returned.

    Args:
        verification_verdict_record: The saved verification verdict record dict.
        context: Optional metadata context (e.g. session_id).

    Returns:
        Apply gate request dict.
    """
    # --- safe baseline ---
    _meta: dict = {
        "source": "apply_gate_request_builder",
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
        verdict_status: str | None = None,
        verdict_decision: str | None = None,
        sim_result_id: str | None = None,
        sim_plan_id: str | None = None,
        dry_run_id: str | None = None,
        requested_action=None,
        verdict_snapshot=None,
        checks: list[dict] | None = None,
        blocking_reasons: list[str] | None = None,
        unresolved_risks: list[dict] | None = None,
        next_step: str = "",
        extra_wins: list[str] | None = None,
    ) -> dict:
        if extra_wins is None:
            extra_wins = []
        warnings = list(_warns) + list(extra_wins)
        warnings.append("Apply gate request does not authorize apply.")
        warnings.append("No real-world action was executed.")
        warnings.append("Human review is required before any future apply authorization.")
        return {
            "apply_gate_required": False,
            "apply_gate_status": "prepared",
            "apply_gate_type": "human_authorization_gate",
            "decision": decision,
            "reason": reason,
            "verification_verdict_id": None if verification_verdict_record is None else verification_verdict_record.get("verification_verdict_id"),
            "verification_verdict_record_status": verdict_status,
            "verification_verdict_decision": verdict_decision,
            "simulation_result_id": sim_result_id,
            "simulation_plan_id": sim_plan_id,
            "dry_run_id": dry_run_id,
            "requested_action": requested_action,
            "verification_verdict_snapshot": verdict_snapshot,
            "eligibility_checks": checks or [],
            "required_human_confirmations": [],
            "blocking_reasons": blocking_reasons or [],
            "unresolved_risks": unresolved_risks or [],
            "recommended_next_step": next_step,
            "apply_authorized": False,
            "apply_allowed": False,
            "rollback_allowed": False,
            "execution_allowed": False,
            "tool_execution_allowed": False,
            "dry_run_execution_allowed": False,
            "simulation_execution_allowed": False,
            "apply_gate_execution_allowed": False,
            "metadata": dict(_meta),
            "warnings": warnings,
        }

    # --- Rule 1: missing record ---
    if verification_verdict_record is None:
        return _empty_request(
            decision="blocked",
            reason="Verification verdict record was not found.",
            blocking_reasons=["Verification verdict record was not found."],
            next_step="Create or provide a valid verification verdict record.",
        )

    record = verification_verdict_record
    vv_id = record.get("verification_verdict_id")
    rec_status = record.get("status")

    # Extract link fields from nested verification_verdict
    verif_obj = record.get("verification_verdict")
    if verif_obj and isinstance(verif_obj, dict):
        sim_result_id = verif_obj.get("simulation_result_id")
        sim_plan_id = verif_obj.get("simulation_plan_id")
        dry_run_id = verif_obj.get("dry_run_id")
        requested_action = verif_obj.get("requested_action")
        verdict_decision = verif_obj.get("decision")
    else:
        sim_result_id = None
        sim_plan_id = None
        dry_run_id = None
        requested_action = None
        verdict_decision = None

    # --- Rule 2: status != pending ---
    if rec_status != "pending":
        return _empty_request(
            decision="blocked",
            reason="Verification verdict record is not pending.",
            verdict_status=rec_status,
            verdict_decision=verdict_decision,
            sim_result_id=sim_result_id,
            sim_plan_id=sim_plan_id,
            dry_run_id=dry_run_id,
            requested_action=requested_action,
            verdict_snapshot=dict(verif_obj) if verif_obj else None,
            blocking_reasons=["Record status is not pending."],
            next_step="Use a pending verification verdict record or create a new one.",
        )

    # --- Rule 3: apply_authorized is True ---
    if record.get("apply_authorized") is True:
        return _empty_request(
            decision="blocked",
            reason="Verification verdict record is unexpectedly marked apply-authorized.",
            verdict_status=rec_status,
            verdict_decision=verdict_decision,
            sim_result_id=sim_result_id,
            sim_plan_id=sim_plan_id,
            dry_run_id=dry_run_id,
            requested_action=requested_action,
            verdict_snapshot=dict(verif_obj) if verif_obj else None,
            blocking_reasons=["apply_authorized is true."],
            next_step="Resolve the apply_authorized flag before continuing.",
        )

    # --- Rule 4: missing/invalid verification_verdict ---
    if verif_obj is None or not isinstance(verif_obj, dict):
        return _empty_request(
            decision="not_eligible",
            reason="Verification verdict payload is missing or invalid.",
            verdict_status=rec_status,
            sim_result_id=sim_result_id,
            sim_plan_id=sim_plan_id,
            dry_run_id=dry_run_id,
            requested_action=requested_action,
            unresolved_risks=[{
                "name": "missing_verdict_payload",
                "severity": "high",
                "detail": "Verification verdict payload is missing or not a dict.",
            }],
            next_step="Regenerate the verification verdict.",
        )

    # --- Rule 5: verdict decision must be "pass" ---
    decision = verif_obj.get("decision")
    if decision == "warning":
        unresolved = list(verif_obj.get("unresolved_risks", []))
        return _empty_request(
            decision="not_eligible",
            reason="Verification verdict has warnings and is not eligible for apply review.",
            verdict_status=rec_status,
            verdict_decision=decision,
            sim_result_id=sim_result_id,
            sim_plan_id=sim_plan_id,
            dry_run_id=dry_run_id,
            requested_action=requested_action,
            verdict_snapshot=dict(verif_obj),
            unresolved_risks=unresolved,
            blocking_reasons=["Verification verdict decision is warning."],
            next_step="Resolve unresolved risks before requesting apply authorization.",
        )
    elif decision == "fail":
        unresolved = list(verif_obj.get("unresolved_risks", []))
        return _empty_request(
            decision="blocked",
            reason="Verification verdict failed.",
            verdict_status=rec_status,
            verdict_decision=decision,
            sim_result_id=sim_result_id,
            sim_plan_id=sim_plan_id,
            dry_run_id=dry_run_id,
            requested_action=requested_action,
            verdict_snapshot=dict(verif_obj),
            unresolved_risks=unresolved,
            blocking_reasons=["Verification verdict decision is fail."],
            next_step="Resolve blocking conditions before continuing.",
        )
    elif decision == "blocked":
        unresolved = list(verif_obj.get("unresolved_risks", []))
        return _empty_request(
            decision="blocked",
            reason="Verification verdict is blocked.",
            verdict_status=rec_status,
            verdict_decision=decision,
            sim_result_id=sim_result_id,
            sim_plan_id=sim_plan_id,
            dry_run_id=dry_run_id,
            requested_action=requested_action,
            verdict_snapshot=dict(verif_obj),
            unresolved_risks=unresolved,
            blocking_reasons=["Verification verdict decision is blocked."],
            next_step="Resolve blocking conditions before continuing.",
        )
    elif decision != "pass":
        unresolved = list(verif_obj.get("unresolved_risks", []))
        return _empty_request(
            decision="blocked",
            reason="Unsupported verification verdict decision.",
            verdict_status=rec_status,
            verdict_decision=decision,
            sim_result_id=sim_result_id,
            sim_plan_id=sim_plan_id,
            dry_run_id=dry_run_id,
            requested_action=requested_action,
            verdict_snapshot=dict(verif_obj),
            unresolved_risks=unresolved,
            blocking_reasons=[f"Unsupported verdict decision: {decision!r}."],
            next_step="Resolve blocking conditions before continuing.",
        )

    # --- Rule 6: evaluate eligibility checks for pass verdict ---
    checks: list[dict] = []
    for check_name, _ in _CHECK_NAMES:
        fn = _CHECK_HARDCODED[check_name]
        check_result = fn(record, verif_obj)
        checks.append(check_result)

    # --- Copy warnings from verification_verdict with prefix ---
    sim_warnings = verif_obj.get("warnings", [])
    for w in sim_warnings:
        _warns.append(f"verification_verdict_warning: {w}")

    # --- Rule 7: decision logic for pass verdict ---
    has_critical_fail = any(c.get("passed") is False for c in checks if c.get("severity") == "critical")
    has_high_fail = any(c.get("passed") is False for c in checks if c.get("severity") == "high")
    has_medium_fail = any(c.get("passed") is False for c in checks if c.get("severity") == "medium")
    has_low_fail = any(c.get("passed") is False for c in checks if c.get("severity") == "low")

    if has_critical_fail or has_high_fail:
        gate_decision = "blocked"
        apply_gate_required = False
    elif has_medium_fail or has_low_fail:
        gate_decision = "not_eligible"
        apply_gate_required = False
    else:
        gate_decision = "eligible_for_human_review"
        apply_gate_required = True

    # --- Build unresolved_risks ---
    unresolved_risks: list[dict] = list(verif_obj.get("unresolved_risks", []))
    if gate_decision in ("eligible_for_human_review", "not_eligible"):
        unresolved_risks.append({
            "name": "real_apply_not_authorized",
            "severity": "medium",
            "detail": "Apply gate request does not authorize real-world apply.",
        })

    # --- Build blocking_reasons ---
    blocking_reasons: list[str] = list(verif_obj.get("blocking_reasons", []))
    if gate_decision == "blocked":
        if has_critical_fail:
            for c in checks:
                if c.get("passed") is False and c.get("severity") == "critical":
                    blocking_reasons.append(f"Critical check failed: {c['name']}.")
        if has_high_fail:
            for c in checks:
                if c.get("passed") is False and c.get("severity") == "high":
                    blocking_reasons.append(f"High check failed: {c['name']}.")

    # --- recommended_next_step ---
    step_map = {
        "eligible_for_human_review": "Present this apply gate request to a human reviewer in a future apply authorization milestone; do not apply changes yet.",
        "not_eligible": "Resolve unresolved risks before requesting apply authorization.",
        "blocked": "Resolve blocking conditions before continuing.",
    }

    # --- required_human_confirmations ---
    confirmations = [
        "Confirm the requested action is still desired.",
        "Confirm the target is correct.",
        "Confirm the dry-run and verification evidence are acceptable.",
        "Confirm rollback limitations are understood.",
        "Confirm this request should proceed to a future apply authorization gate.",
    ]

    # Finalize warnings
    warnings = list(_warns)
    warnings.append("Apply gate request does not authorize apply.")
    warnings.append("No real-world action was executed.")
    warnings.append("Human review is required before any future apply authorization.")

    return {
        "apply_gate_required": apply_gate_required,
        "apply_gate_status": "prepared",
        "apply_gate_type": "human_authorization_gate",
        "decision": gate_decision,
        "reason": _build_pass_fallback_reason(checks) if gate_decision == "eligible_for_human_review" else ("Eligibility checks did not pass." if gate_decision == "not_eligible" else "Blocking conditions present."),
        "verification_verdict_id": vv_id,
        "verification_verdict_record_status": rec_status,
        "verification_verdict_decision": verdict_decision,
        "simulation_result_id": sim_result_id,
        "simulation_plan_id": sim_plan_id,
        "dry_run_id": dry_run_id,
        "requested_action": dict(requested_action) if requested_action else None,
        "verification_verdict_snapshot": dict(verif_obj),
        "eligibility_checks": checks,
        "required_human_confirmations": confirmations,
        "blocking_reasons": blocking_reasons,
        "unresolved_risks": unresolved_risks,
        "recommended_next_step": step_map.get(gate_decision, "Resolve blocking conditions before continuing."),
        "apply_authorized": False,
        "apply_allowed": False,
        "rollback_allowed": False,
        "execution_allowed": False,
        "tool_execution_allowed": False,
        "dry_run_execution_allowed": False,
        "simulation_execution_allowed": False,
        "apply_gate_execution_allowed": False,
        "metadata": dict(_meta),
        "warnings": warnings,
    }


def _build_pass_fallback_reason(checks: list[dict]) -> str:
    """If every check passes, return pass reason; otherwise return first fail detail."""
    failed = [c for c in checks if c.get("passed") is False]
    if not failed:
        return "All eligibility checks passed. Record qualifies for human review."
    return failed[0]["detail"]
