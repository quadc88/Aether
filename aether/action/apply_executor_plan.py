"""Apply Executor Plan Builder for Aether (Milestone 73A).

Builds a structured apply_executor_plan object from an approved_contract_intent
apply_executor_contract_record. This is synthetic evaluation only — it does NOT execute
any apply, call executors, collect evidence, or modify target state.
"""

from __future__ import annotations


_ALLOWED_ACTION_TYPES = (
    "status_check",
    "read_only_check",
    "inspection",
    "validation",
    "report_generation",
    "plan_review",
)

_DIRECT_EXECUTOR_KEYS = {
    "executor",
    "command",
    "shell",
    "subprocess",
    "python_code",
    "raw_code",
    "script",
    "apply_now",
    "execute_now",
}

_EVIDENCE_NAMES_REQUIRED = [
    "pre_execution_state_evidence",
    "execution_result_evidence",
    "post_execution_verification_evidence",
    "rollback_evidence",
    "audit_log_evidence",
]


_CHECK_DEFS = [
    ("apply_executor_contract_approved_intent", "low"),
    ("apply_executor_contract_persisted", "low"),
    ("contract_decision_ready", "high"),
    ("contract_review_completed", "low"),
    ("contract_intent_recorded", "low"),
    ("confirmations_received", "medium"),
    ("contract_ready", "high"),
    ("execution_boundary_present", "medium"),
    ("execution_boundary_scope_safe", "high"),
    ("evidence_requirements_declared", "medium"),
    ("evidence_not_collected", "critical"),
    ("rollback_expectation_declared", "medium"),
    ("rollback_plan_not_attached", "critical"),
    ("apply_not_authorized", "critical"),
    ("apply_not_executed", "critical"),
    ("rollback_not_executed", "critical"),
    ("execution_flags_blocked", "high"),
    ("apply_flags_blocked", "critical"),
    ("requested_action_present", "medium"),
    ("requested_action_type_allowed", "high"),
    ("target_present", "medium"),
    ("no_direct_executor_present", "critical"),
    ("blocking_reasons_empty", "medium"),
]


# --------------------------------------------------------------------------- #
# Check functions
# --------------------------------------------------------------------------- #


def _check_applied_contract_approved_intent(rg: dict, rac: dict | None) -> dict:
    return {
        "name": "apply_executor_contract_approved_intent",
        "passed": rg.get("status") == "approved_contract_intent",
        "severity": "low",
        "detail": "Apply executor contract record status must be 'approved_contract_intent'.",
    }


def _check_applied_contract_persisted(rg: dict, rac: dict | None) -> dict:
    return {
        "name": "apply_executor_contract_persisted",
        "passed": rg.get("apply_executor_contract_persisted") is True,
        "severity": "low",
        "detail": "Apply executor contract record must be persisted.",
    }


def _check_contract_decision_ready(rg: dict, rac: dict | None) -> dict:
    rec_dec = rg.get("contract_decision")
    req_dec = rac.get("decision") if rac else None
    return {
        "name": "contract_decision_ready",
        "passed": rec_dec == "contract_ready" and req_dec == "contract_ready",
        "severity": "high",
        "detail": "Both contract_decision and request.decision must be 'contract_ready'.",
    }


def _check_contract_review_completed(rg: dict, rac: dict | None) -> dict:
    return {
        "name": "contract_review_completed",
        "passed": rg.get("contract_review_completed") is True,
        "severity": "low",
        "detail": "contract_review_completed must be true.",
    }


def _check_contract_intent_recorded(rg: dict, rac: dict | None) -> dict:
    return {
        "name": "contract_intent_recorded",
        "passed": rg.get("contract_intent_recorded") is True,
        "severity": "low",
        "detail": "contract_intent_recorded must be true.",
    }


def _check_confirmations_received(rg: dict, rac: dict | None) -> dict:
    required = rg.get("confirmations_required", [])
    received = rg.get("confirmations_received", [])
    if not required:
        return {"name": "confirmations_received", "passed": len(received) > 0, "severity": "medium", "detail": "No confirmations required but confirmations received."}
    return {
        "name": "confirmations_received",
        "passed": all(c in received for c in required),
        "severity": "medium",
        "detail": "All required confirmations must be present in confirmations_received.",
    }


def _check_contract_ready(rg: dict, rac: dict | None) -> dict:
    req_dec = rac.get("decision") if rac else None
    return {
        "name": "contract_ready",
        "passed": req_dec == "contract_ready",
        "severity": "high",
        "detail": "The executor contract decision must be 'contract_ready'.",
    }


def _check_execution_boundary_present(rg: dict, rac: dict | None) -> dict:
    eb = rac.get("execution_boundary") if rac else None
    return {
        "name": "execution_boundary_present",
        "passed": isinstance(eb, dict),
        "severity": "medium",
        "detail": "Executor contract must have an execution_boundary dict.",
    }


def _check_execution_boundary_scope_safe(rg: dict, rac: dict | None) -> dict:
    eb = rac.get("execution_boundary", {}) if rac else {}
    if not isinstance(eb, dict):
        return {"name": "execution_boundary_scope_safe", "passed": False, "severity": "high", "detail": "execution_boundary scope must be 'contract_only_no_execution'."}
    return {
        "name": "execution_boundary_scope_safe",
        "passed": eb.get("execution_scope") == "contract_only_no_execution",
        "severity": "high",
        "detail": "execution_boundary.execution_scope must be 'contract_only_no_execution'.",
    }


def _check_evidence_requirements_declared(rg: dict, rac: dict | None) -> dict:
    er = rac.get("evidence_requirements", []) if rac else []
    names = [e.get("name") for e in er] if isinstance(er, list) else []
    return {
        "name": "evidence_requirements_declared",
        "passed": all(n in names for n in _EVIDENCE_NAMES_REQUIRED),
        "severity": "medium",
        "detail": f"Evidence requirements must include all {_EVIDENCE_NAMES_REQUIRED}.",
    }


def _check_evidence_not_collected(rg: dict, rac: dict | None) -> dict:
    all_false = (not rg.get("evidence_collected"))
    req_satisfied = all(not e.get("satisfied") for e in (rac.get("evidence_requirements", []) if rac else [])) if isinstance(rac, dict) else False
    return {
        "name": "evidence_not_collected",
        "passed": all_false and req_satisfied,
        "severity": "critical",
        "detail": "Evidence must not be collected in this milestone.",
    }


def _check_rollback_expectation_declared(rg: dict, rac: dict | None) -> dict:
    re_obj = rac.get("rollback_expectation") if rac else None
    if not isinstance(re_obj, dict):
        return {"name": "rollback_expectation_declared", "passed": False, "severity": "medium", "detail": "Executor contract must have rollback_expectation."}
    return {
        "name": "rollback_expectation_declared",
        "passed": re_obj.get("rollback_plan_required") is True,
        "severity": "medium",
        "detail": "rollback_expectation.rollback_plan_required must be true.",
    }


def _check_rollback_plan_not_attached(rg: dict, rac: dict | None) -> dict:
    not_attached = not rg.get("rollback_plan_attached")
    plan_not_present = False
    if isinstance(rac, dict):
        re_obj = rac.get("rollback_expectation", {})
        if isinstance(re_obj, dict):
            plan_not_present = not re_obj.get("rollback_plan_present")
    return {
        "name": "rollback_plan_not_attached",
        "passed": not_attached and plan_not_present,
        "severity": "critical",
        "detail": "Neither record nor contract indicates rollback plan is attached.",
    }


def _check_apply_not_authorized(rg: dict, rac: dict | None) -> dict:
    return {
        "name": "apply_not_authorized",
        "passed": not rg.get("apply_authorized", False) and not (rac and rac.get("apply_authorized", False)),
        "severity": "critical",
        "detail": "Both record.apply_authorized and contract.apply_authorized must be false.",
    }


def _check_apply_not_executed(rg: dict, rac: dict | None) -> dict:
    return {
        "name": "apply_not_executed",
        "passed": not rg.get("apply_executed", False),
        "severity": "critical",
        "detail": "record.apply_executed must be false.",
    }


def _check_rollback_not_executed(rg: dict, rac: dict | None) -> dict:
    return {
        "name": "rollback_not_executed",
        "passed": not rg.get("rollback_executed", False),
        "severity": "critical",
        "detail": "record.rollback_executed must be false.",
    }


def _check_execution_flags_blocked(rg: dict, rac: dict | None) -> dict:
    rec_keys = ["execution_allowed", "tool_execution_allowed", "dry_run_execution_allowed",
                 "simulation_execution_allowed", "apply_gate_execution_allowed",
                 "human_authorization_execution_allowed", "apply_execution_gate_execution_allowed",
                 "apply_executor_contract_execution_allowed"]
    rec_flags = [rg.get(k, False) is False for k in rec_keys]
    req_flags = []
    if rac:
        req_keys = ["execution_allowed", "tool_execution_allowed", "dry_run_execution_allowed",
                     "simulation_execution_allowed", "apply_gate_execution_allowed",
                     "human_authorization_execution_allowed", "apply_execution_gate_execution_allowed",
                     "apply_executor_contract_execution_allowed"]
        req_flags = [rac.get(k, False) is False for k in req_keys]
    return {
        "name": "execution_flags_blocked",
        "passed": all(rec_flags) and all(req_flags),
        "severity": "high",
        "detail": "All execution flags must be false in both record and contract.",
    }


def _check_apply_flags_blocked(rg: dict, rac: dict | None) -> dict:
    rec = [rg.get("apply_allowed"), rg.get("rollback_allowed")]
    req = []
    if rac:
        req = [rac.get("apply_allowed"), rac.get("rollback_allowed")]
    all_flags = [f is False for f in rec + req]
    return {
        "name": "apply_flags_blocked",
        "passed": all(all_flags),
        "severity": "critical",
        "detail": "All apply flags must be false in both record and contract.",
    }


def _check_requested_action_present(rg: dict, rac: dict | None) -> dict:
    ra = rac.get("requested_action") if isinstance(rac, dict) else None
    if not isinstance(ra, dict):
        return {"name": "requested_action_present", "passed": False, "severity": "medium", "detail": "requested_action must be a dict."}
    return {
        "name": "requested_action_present",
        "passed": isinstance(ra, dict),
        "severity": "medium",
        "detail": "The executor contract must contain a non-null requested_action dict.",
    }


def _check_requested_action_type_allowed(rg: dict, rac: dict | None) -> dict:
    ra = (rac or {}).get("requested_action") or {}
    if not isinstance(ra, dict):
        return {"name": "requested_action_type_allowed", "passed": False, "severity": "high", "detail": f"action_type must be one of {_ALLOWED_ACTION_TYPES}."}
    action_type = ra.get("action_type")
    return {
        "name": "requested_action_type_allowed",
        "passed": action_type in _ALLOWED_ACTION_TYPES,
        "severity": "high",
        "detail": f"requested_action.action_type must be one of {_ALLOWED_ACTION_TYPES}.",
    }


def _check_target_present(rg: dict, rac: dict | None) -> dict:
    ra = (rac or {}).get("requested_action") or {}
    if not isinstance(ra, dict):
        return {"name": "target_present", "passed": False, "severity": "medium", "detail": "requested_action.target must be a non-empty string."}
    target = ra.get("target")
    return {
        "name": "target_present",
        "passed": isinstance(target, str) and len(target) > 0,
        "severity": "medium",
        "detail": "requested_action.target must be a non-empty string.",
    }


def _check_no_direct_executor_present(rg: dict, rac: dict | None) -> dict:
    ra = (rac or {}).get("requested_action") or {}
    if not isinstance(ra, dict):
        return {
            "name": "no_direct_executor_present", "passed": True,
            "severity": "critical", "detail": "requested_action must not contain direct executor keys.",
        }
    has_executor_key = any(k in ra for k in _DIRECT_EXECUTOR_KEYS)
    return {
        "name": "no_direct_executor_present",
        "passed": not has_executor_key,
        "severity": "critical",
        "detail": "requested_action must not contain direct executor keys.",
    }


def _check_blocking_reasons_empty(rg: dict, rac: dict | None) -> dict:
    br = rac.get("blocking_reasons", []) if rac else []
    return {
        "name": "blocking_reasons_empty",
        "passed": len(br) == 0,
        "severity": "medium",
        "detail": "executor contract blocking_reasons must be empty.",
    }


_CHECK_HARDCODED = {
    "apply_executor_contract_approved_intent": _check_applied_contract_approved_intent,
    "apply_executor_contract_persisted": _check_applied_contract_persisted,
    "contract_decision_ready": _check_contract_decision_ready,
    "contract_review_completed": _check_contract_review_completed,
    "contract_intent_recorded": _check_contract_intent_recorded,
    "confirmations_received": _check_confirmations_received,
    "contract_ready": _check_contract_ready,
    "execution_boundary_present": _check_execution_boundary_present,
    "execution_boundary_scope_safe": _check_execution_boundary_scope_safe,
    "evidence_requirements_declared": _check_evidence_requirements_declared,
    "evidence_not_collected": _check_evidence_not_collected,
    "rollback_expectation_declared": _check_rollback_expectation_declared,
    "rollback_plan_not_attached": _check_rollback_plan_not_attached,
    "apply_not_authorized": _check_apply_not_authorized,
    "apply_not_executed": _check_apply_not_executed,
    "rollback_not_executed": _check_rollback_not_executed,
    "execution_flags_blocked": _check_execution_flags_blocked,
    "apply_flags_blocked": _check_apply_flags_blocked,
    "requested_action_present": _check_requested_action_present,
    "requested_action_type_allowed": _check_requested_action_type_allowed,
    "target_present": _check_target_present,
    "no_direct_executor_present": _check_no_direct_executor_present,
    "blocking_reasons_empty": _check_blocking_reasons_empty,
}


# --------------------------------------------------------------------------- #
# Stub ordered_execution_steps / evidence_capture_plan helpers
# --------------------------------------------------------------------------- #


def _stub_ordered_steps(decision: str) -> list[dict]:
    base_names = [
        ("pre_execution_state_capture", "before", "Capture observable pre-execution state."),
        ("executor_boundary_revalidation", "during", "Revalidate executor boundary constraints before attempt."),
        ("apply_attempt_placeholder", "during", "Placeholder for future apply attempt; not executable now."),
        ("post_execution_state_capture", "after", "Capture observable post-execution state."),
        ("outcome_verification", "after", "Verify requested outcome against observed evidence."),
        ("audit_record_preparation", "audit", "Prepare persistent audit record of the attempted apply."),
    ]
    purpose_map = {
        "blocked": "Plan blocked; no execution permitted at this stage.",
        "not_ready": "Plan not ready; resolve readiness issues before attempting execution.",
        "plan_ready": "Future executor should execute these steps in order.",
    }
    purp = purpose_map.get(decision, "Blocked or not_ready.")
    steps = []
    for i, (name, stage, default_desc) in enumerate(base_names, 1):
        desc = default_desc
        if name == "apply_attempt_placeholder":
            desc += " allowed_to_execute_now=false."
        steps.append({
            "step_number": i,
            "name": name,
            "purpose": purp,
            "allowed_to_execute_now": False,
            "requires_future_executor": True,
            "required_evidence": [f"{name}_evidence"],
            "rollback_related": name == "apply_attempt_placeholder" or name.startswith("rollback"),
        })
    return steps


def _stub_evidence_plan() -> list[dict]:
    return [
        {"name": "pre_execution_state_evidence", "capture_stage": "before", "required": True, "collected_now": False, "collection_allowed_now": False, "description": "Capture observable state before any future executor attempt."},
        {"name": "execution_result_evidence", "capture_stage": "during", "required": True, "collected_now": False, "collection_allowed_now": False, "description": "Capture intermediate execution observations."},
        {"name": "post_execution_verification_evidence", "capture_stage": "after", "required": True, "collected_now": False, "collection_allowed_now": False, "description": "Capture observable state after executor attempt for verification."},
        {"name": "rollback_evidence", "capture_stage": "rollback", "required": True, "collected_now": False, "collection_allowed_now": False, "description": "Capture evidence if rollback is required."},
        {"name": "audit_log_evidence", "capture_stage": "audit", "required": True, "collected_now": False, "collection_allowed_now": False, "description": "Persist a complete audit log of the attempted apply."},
    ]


# --------------------------------------------------------------------------- #
# Stub blocked/noise helper
# --------------------------------------------------------------------------- #


def _empty_plan(reason: str, blocking_reasons: list[str] | None = None) -> dict:
    warnings = [
        "Apply executor plan does not authorize execution.",
        "Apply executor plan does not execute apply.",
        "Evidence capture is planned but not performed.",
        "Rollback plan is required but not attached in this milestone.",
        "A separate future executor is required before apply can occur.",
    ]
    return {
        "plan_required": False,
        "plan_status": "prepared",
        "plan_type": "apply_executor_plan",
        "decision": "blocked",
        "reason": reason,
        "apply_executor_contract_id": None,
        "apply_executor_contract_record_status": None,
        "contract_decision": None,
        "apply_execution_gate_id": None,
        "human_authorization_id": None,
        "apply_gate_id": None,
        "verification_verdict_id": None,
        "simulation_result_id": None,
        "simulation_plan_id": None,
        "dry_run_id": None,
        "requested_action": None,
        "apply_executor_contract_snapshot": None,
        "plan_checks": [],
        "ordered_execution_steps": _stub_ordered_steps("blocked"),
        "evidence_capture_plan": _stub_evidence_plan(),
        "rollback_plan_requirement": {
            "rollback_required_before_future_apply": True,
            "rollback_plan_required": True,
            "rollback_plan_attached": False,
            "rollback_verified": False,
            "rollback_allowed": False,
            "rollback_executed": False,
            "rollback_note": "Rollback plan is required before future apply; no rollback plan is attached or executed in this milestone.",
        },
        "executor_constraints": {
            "execution_scope": "blocked_or_not_ready_plan_only_no_execution",
            "allowed_action_type": None,
            "allowed_tool_id": None,
            "allowed_target": None,
            "forbidden_capabilities": [
                "shell", "subprocess", "raw_code_execution",
                "filesystem_mutation_without_executor",
                "network_mutation_without_executor",
                "database_mutation_without_executor",
                "identity_modification", "self_repair",
                "rollback_without_contract",
                "external_api_call_without_contract",
            ],
            "execution_allowed": False,
            "apply_allowed": False,
            "tool_execution_allowed": False,
            "evidence_collection_allowed": False,
            "rollback_allowed": False,
        },
        "required_plan_confirmations": [
            "I confirm the contract intent was recorded.",
            "I confirm this plan does not execute the action.",
            "I confirm this plan does not authorize apply.",
            "I confirm evidence capture is planned but not performed.",
            "I confirm rollback planning is required before future apply.",
            "I understand a separate future apply executor is required.",
        ],
        "plan_statement": None,
        "blocking_reasons": blocking_reasons or [],
        "unresolved_risks": [{"name": "apply_executor_plan_synthentic_only", "severity": "medium", "detail": "Plan is synthetic; no real executor exists yet."}],
        "recommended_next_step": reason,
        "contract_review_completed": False,
        "contract_intent_recorded": False,
        "evidence_collected": False,
        "rollback_plan_attached": False,
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
        "apply_executor_contract_execution_allowed": False,
        "apply_executor_plan_execution_allowed": False,
        "metadata": {},
        "warnings": warnings,
    }


def build_apply_executor_plan(
    apply_executor_contract_record: dict | None,
    context: dict | None = None,
) -> dict:
    """Build an apply executor plan from an apply_executor_contract_record.

    Args:
        apply_executor_contract_record: The persisted AE-CR dict.
        context: Optional metadata context (e.g. session_id).

    Returns:
        A structured apply_executor_plan dict.
    """
    _meta: dict = {
        "source": "apply_executor_plan_builder",
        "schema_version": "1.0",
    }
    if context:
        if context.get("session_id"):
            _meta["session_id"] = context["session_id"]

    # --- Rule 1: missing record ---
    if apply_executor_contract_record is None:
        return _empty_plan(
            reason="Apply executor contract record was not found.",
            blocking_reasons=["Apply executor contract record was not found."],
        )

    rg = apply_executor_contract_record
    rac = rg.get("apply_executor_contract")

    _warns: list[str] = list(rg.get("warnings", []))
    if isinstance(rac, dict):
        for w in rac.get("warnings", []):
            _warns.append(f"apply_executor_contract_warning: {w}")

    rg_status = rg.get("status")
    rg_contract_dec = rg.get("contract_decision")

    # --- Rule 2: status check ---
    if rg_status != "approved_contract_intent":
        return _empty_plan(
            reason="Apply executor contract record is not approved_contract_intent.",
            blocking_reasons=["Record status is not approved_contract_intent."],
        )

    # --- Rule 3: contract_decision check ---
    if rg_contract_dec != "contract_ready":
        return _empty_plan(
            reason="Apply executor contract record was not based on a ready contract.",
            blocking_reasons=["Contract decision is not contract_ready."],
        )

    # --- Rule 4: contract_intent_recorded ---
    if not rg.get("contract_intent_recorded"):
        return _empty_plan(
            reason="Contract intent has not been recorded.",
            blocking_reasons=["contract_intent_recorded is not true."],
        )

    # --- Rule 5: contract_review_completed ---
    if not rg.get("contract_review_completed"):
        return _empty_plan(
            reason="Contract review is not completed.",
            blocking_reasons=["contract_review_completed is not true."],
        )

    # --- Rule 6: evidence_collected ---
    if rg.get("evidence_collected") is True:
        return _empty_plan(
            reason="Apply executor contract record unexpectedly indicates evidence was collected.",
            blocking_reasons=["evidence_collected is true."],
        )

    # --- Rule 7: rollback_plan_attached ---
    if rg.get("rollback_plan_attached") is True:
        return _empty_plan(
            reason="Apply executor contract record unexpectedly indicates rollback plan was already attached.",
            blocking_reasons=["rollback_plan_attached is true."],
        )

    # --- Rule 8: apply_authorized ---
    if rg.get("apply_authorized") is True:
        return _empty_plan(
            reason="Apply executor contract record is unexpectedly marked apply-authorized.",
            blocking_reasons=["apply_authorized is true."],
        )

    # --- Rule 9: apply_executed / rollback_executed ---
    block_reasons: list[str] = []
    if rg.get("apply_executed") is True:
        block_reasons.append("apply_executed is true.")
    if rg.get("rollback_executed") is True:
        block_reasons.append("rollback_executed is true.")
    if block_reasons:
        return _empty_plan(
            reason="Apply executor contract record indicates execution already occurred.",
            blocking_reasons=block_reasons,
        )

    # --- Rule 10: missing contract payload ---
    if rac is None or not isinstance(rac, dict):
        unresolved_risks = [{"name": "missing_apply_executor_contract", "severity": "high", "detail": "Executor contract payload is missing or invalid."}]
        return {
            **_empty_plan("Executor contract payload is missing or invalid.", []),
            "decision": "not_ready",
            "reason": "Executor contract payload is missing or invalid.",
            "unresolved_risks": unresolved_risks,
            "recommended_next_step": "Regenerate the apply executor contract and contract-intent record.",
        }

    # --- Rule 11: evaluate plan checks ---
    checks: list[dict] = []
    for check_name, _ in _CHECK_DEFS:
        fn = _CHECK_HARDCODED[check_name]
        checks.append(fn(rg, rac))

    # --- Rule 12: decision logic ---
    has_critical_fail = any(c.get("passed") is False for c in checks if c.get("severity") == "critical")
    has_high_fail = any(c.get("passed") is False for c in checks if c.get("severity") == "high")
    has_medium_fail = any(c.get("passed") is False for c in checks if c.get("severity") == "medium")
    has_low_fail = any(c.get("passed") is False for c in checks if c.get("severity") == "low")

    if has_critical_fail or has_high_fail:
        plan_dec = "blocked"
        plan_required = False
    elif has_medium_fail or has_low_fail:
        plan_dec = "not_ready"
        plan_required = False
    else:
        plan_dec = "plan_ready"
        plan_required = True

    # --- Build unresolved_risks ---
    unresolved_risks: list[dict] = list(rac.get("unresolved_risks", []))
    if plan_dec == "plan_ready":
        unresolved_risks.append({
            "name": "executor_plan_prepared",
            "severity": "medium",
            "detail": "Executor plan is prepared; a future record store and executor milestones are still required.",
        })

    # --- Blocking reasons ---
    blocking_reasons: list[str] = list(rac.get("blocking_reasons", []))
    if plan_dec == "blocked":
        for c in checks:
            if c.get("passed") is False and c.get("severity") in ("critical", "high"):
                blocking_reasons.append(f"Plan check failed: {c['name']}.")

    # --- Ordered execution steps ---
    ordered_execution_steps = _stub_ordered_steps(plan_dec)

    # --- Evidence capture plan ---
    evidence_capture_plan = _stub_evidence_plan()

    # --- Rollback plan requirement ---
    rollback_plan_requirement = {
        "rollback_required_before_future_apply": True,
        "rollback_plan_required": True,
        "rollback_plan_attached": False,
        "rollback_verified": False,
        "rollback_allowed": False,
        "rollback_executed": False,
        "rollback_note": "Rollback plan is required before future apply; no rollback plan is attached or executed in this milestone.",
    }

    # --- Executor constraints ---
    ra = rac.get("requested_action") or {}
    act_type = ra.get("action_type") if isinstance(ra, dict) else None
    tool_id = ra.get("tool_id") if isinstance(ra, dict) else None
    target = ra.get("target") if isinstance(ra, dict) else None

    executor_constraints = {
        "execution_scope": "plan_only_no_execution" if plan_dec == "plan_ready" else "blocked_or_not_ready_plan_only_no_execution",
        "allowed_action_type": act_type,
        "allowed_tool_id": tool_id,
        "allowed_target": target,
        "forbidden_capabilities": [
            "shell", "subprocess", "raw_code_execution",
            "filesystem_mutation_without_executor",
            "network_mutation_without_executor",
            "database_mutation_without_executor",
            "identity_modification", "self_repair",
            "rollback_without_contract",
            "external_api_call_without_contract",
        ],
        "execution_allowed": False,
        "apply_allowed": False,
        "tool_execution_allowed": False,
        "evidence_collection_allowed": False,
        "rollback_allowed": False,
    }

    # --- Recommended next step ---
    step_map = {
        "plan_ready": "Persist this plan in a future plan record milestone; do not execute changes yet.",
        "not_ready": "Resolve plan readiness issues before preparing executor plan.",
        "blocked": "Resolve blocking conditions before continuing.",
    }

    # --- Required plan confirmations ---
    required_plan_confirmations = [
        "I confirm the contract intent was recorded.",
        "I confirm this plan does not execute the action.",
        "I confirm this plan does not authorize apply.",
        "I confirm evidence capture is planned but not performed.",
        "I confirm rollback planning is required before future apply.",
        "I understand a separate future apply executor is required.",
    ]

    # --- Plan statement ---
    plan_statement = None
    if plan_dec == "plan_ready":
        plan_statement = "Apply executor plan is prepared for future executor design. This plan does not authorize or execute apply."

    # --- Finalize warnings ---
    warnings = list(_warns)
    warnings.append("Apply executor plan does not authorize execution.")
    warnings.append("Apply executor plan does not execute apply.")
    warnings.append("Evidence capture is planned but not performed.")
    warnings.append("Rollback plan is required but not attached in this milestone.")
    warnings.append("A separate future executor is required before apply can occur.")

    return {
        "plan_required": plan_required,
        "plan_status": "prepared",
        "plan_type": "apply_executor_plan",
        "decision": plan_dec,
        "reason": "" if plan_dec == "plan_ready" else "Plan checks did not pass.",
        "apply_executor_contract_id": rg.get("apply_executor_contract_id"),
        "apply_executor_contract_record_status": rg_status,
        "contract_decision": rg_contract_dec,
        "apply_execution_gate_id": rg.get("apply_execution_gate_id"),
        "human_authorization_id": rg.get("human_authorization_id"),
        "apply_gate_id": rg.get("apply_gate_id"),
        "verification_verdict_id": rg.get("verification_verdict_id"),
        "simulation_result_id": rg.get("simulation_result_id"),
        "simulation_plan_id": rg.get("simulation_plan_id"),
        "dry_run_id": rg.get("dry_run_id"),
        "requested_action": dict(ra) if isinstance(ra, dict) else None,
        "apply_executor_contract_snapshot": dict(rg),
        "plan_checks": checks,
        "ordered_execution_steps": ordered_execution_steps,
        "evidence_capture_plan": evidence_capture_plan,
        "rollback_plan_requirement": rollback_plan_requirement,
        "executor_constraints": executor_constraints,
        "required_plan_confirmations": required_plan_confirmations,
        "plan_statement": plan_statement,
        "blocking_reasons": blocking_reasons,
        "unresolved_risks": unresolved_risks,
        "recommended_next_step": step_map.get(plan_dec, "Resolve blocking conditions before continuing."),
        "contract_review_completed": rg.get("contract_review_completed", False),
        "contract_intent_recorded": rg.get("contract_intent_recorded", False),
        "evidence_collected": False,
        "rollback_plan_attached": False,
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
        "apply_executor_contract_execution_allowed": False,
        "apply_executor_plan_execution_allowed": False,
        "metadata": dict(_meta),
        "warnings": warnings,
    }
