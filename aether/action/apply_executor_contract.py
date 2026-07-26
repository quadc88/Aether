"""Apply Executor Contract Builder for Aether (Milestone 71A).

Builds a structured apply_executor_contract object from an approved_execution_intent
apply_execution_gate_record. This is synthetic evaluation only — it does NOT execute
any apply, call executors, or modify target state.
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


_CHECK_DEFS = [
    ("apply_execution_gate_approved_intent", "low"),
    ("apply_execution_gate_persisted", "low"),
    ("gate_decision_ready", "high"),
    ("execution_review_completed", "low"),
    ("execution_intent_recorded", "low"),
    ("confirmations_received", "medium"),
    ("request_ready_for_execution_gate_review", "high"),
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


def _check_apply_execution_gate_approved_intent(rg: dict, raegr: dict | None) -> dict:
    return {
        "name": "apply_execution_gate_approved_intent",
        "passed": rg.get("status") == "approved_execution_intent",
        "severity": "low",
        "detail": "Apply execution gate record status must be 'approved_execution_intent'.",
    }


def _check_apply_execution_gate_persisted(rg: dict, raegr: dict | None) -> dict:
    return {
        "name": "apply_execution_gate_persisted",
        "passed": rg.get("apply_execution_gate_persisted") is True,
        "severity": "low",
        "detail": "Apply execution gate record must be persisted.",
    }


def _check_gate_decision_ready(rg: dict, raegr: dict | None) -> dict:
    rec_dec = rg.get("gate_decision")
    req_dec = raegr.get("decision") if raegr else None
    return {
        "name": "gate_decision_ready",
        "passed": rec_dec == "ready_for_execution_gate_review" and req_dec == "ready_for_execution_gate_review",
        "severity": "high",
        "detail": "Both gate_decision and request.decision must be 'ready_for_execution_gate_review'.",
    }


def _check_execution_review_completed(rg: dict, raegr: dict | None) -> dict:
    return {
        "name": "execution_review_completed",
        "passed": rg.get("execution_review_completed") is True,
        "severity": "low",
        "detail": "execution_review_completed must be true.",
    }


def _check_execution_intent_recorded(rg: dict, raegr: dict | None) -> dict:
    return {
        "name": "execution_intent_recorded",
        "passed": rg.get("execution_intent_recorded") is True,
        "severity": "low",
        "detail": "execution_intent_recorded must be true.",
    }


def _check_confirmations_received(rg: dict, raegr: dict | None) -> dict:
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


def _check_request_ready_for_egm(rg: dict, raegr: dict | None) -> dict:
    req_dec = raegr.get("decision") if raegr else None
    return {
        "name": "request_ready_for_execution_gate_review",
        "passed": req_dec == "ready_for_execution_gate_review",
        "severity": "high",
        "detail": "The apply execution gate request decision must be 'ready_for_execution_gate_review'.",
    }


def _check_apply_not_authorized(rg: dict, raegr: dict | None) -> dict:
    return {
        "name": "apply_not_authorized",
        "passed": not rg.get("apply_authorized", False) and not (raegr and raegr.get("apply_authorized", False)),
        "severity": "critical",
        "detail": "Both record.apply_authorized and request.apply_authorized must be false.",
    }


def _check_apply_not_executed(rg: dict, raegr: dict | None) -> dict:
    return {
        "name": "apply_not_executed",
        "passed": not rg.get("apply_executed", False),
        "severity": "critical",
        "detail": "record.apply_executed must be false.",
    }


def _check_rollback_not_executed(rg: dict, raegr: dict | None) -> dict:
    return {
        "name": "rollback_not_executed",
        "passed": not rg.get("rollback_executed", False),
        "severity": "critical",
        "detail": "record.rollback_executed must be false.",
    }


def _check_execution_flags_blocked(rg: dict, raegr: dict | None) -> dict:
    rec_flags = [
        rg.get("execution_allowed"),
        rg.get("tool_execution_allowed"),
        rg.get("dry_run_execution_allowed"),
        rg.get("simulation_execution_allowed"),
        rg.get("apply_gate_execution_allowed"),
        rg.get("human_authorization_execution_allowed"),
        rg.get("apply_execution_gate_execution_allowed"),
    ]
    req_flags = []
    if raegr:
        req_flags = [
            raegr.get("execution_allowed"),
            raegr.get("tool_execution_allowed"),
            raegr.get("dry_run_execution_allowed"),
            raegr.get("simulation_execution_allowed"),
            raegr.get("apply_gate_execution_allowed"),
            raegr.get("human_authorization_execution_allowed"),
            raegr.get("apply_execution_gate_execution_allowed"),
        ]
    all_flags = rec_flags + req_flags
    return {
        "name": "execution_flags_blocked",
        "passed": all(f is False for f in all_flags),
        "severity": "high",
        "detail": "All execution flags must be false in both record and request.",
    }


def _check_apply_flags_blocked(rg: dict, raegr: dict | None) -> dict:
    rec = [rg.get("apply_allowed"), rg.get("rollback_allowed")]
    req = []
    if raegr:
        req = [raegr.get("apply_allowed"), raegr.get("rollback_allowed")]
    all_flags = rec + req
    return {
        "name": "apply_flags_blocked",
        "passed": all(f is False for f in all_flags),
        "severity": "critical",
        "detail": "All apply flags must be false in both record and request.",
    }


def _check_requested_action_present(rg: dict, raegr: dict | None) -> dict:
    return {
        "name": "requested_action_present",
        "passed": isinstance(raegr and raegr.get("requested_action"), dict),
        "severity": "medium",
        "detail": "The apply execution gate request must contain a non-null requested_action dict.",
    }


def _check_requested_action_type_allowed(rg: dict, raegr: dict | None) -> dict:
    ra = (raegr or {}).get("requested_action") or {}
    action_type = ra.get("action_type") if isinstance(ra, dict) else None
    return {
        "name": "requested_action_type_allowed",
        "passed": action_type in _ALLOWED_ACTION_TYPES,
        "severity": "high",
        "detail": f"requested_action.action_type must be one of {_ALLOWED_ACTION_TYPES}.",
    }


def _check_target_present(rg: dict, raegr: dict | None) -> dict:
    ra = (raegr or {}).get("requested_action") or {}
    if not isinstance(ra, dict):
        return {"name": "target_present", "passed": False, "severity": "medium", "detail": "requested_action.target must be a non-empty string."}
    target = ra.get("target")
    return {
        "name": "target_present",
        "passed": isinstance(target, str) and len(target) > 0,
        "severity": "medium",
        "detail": "requested_action.target must be a non-empty string.",
    }


def _check_no_direct_executor_present(rg: dict, raegr: dict | None) -> dict:
    ra = (raegr or {}).get("requested_action") or {}
    if not isinstance(ra, dict):
        return {
            "name": "no_direct_executor_present",
            "passed": True,  # Can't check for executor keys if no request
            "severity": "critical",
            "detail": "requested_action must not contain direct executor keys.",
        }
    has_executor_key = any(k in ra for k in _DIRECT_EXECUTOR_KEYS)
    return {
        "name": "no_direct_executor_present",
        "passed": not has_executor_key,
        "severity": "critical",
        "detail": "requested_action must not contain direct executor keys.",
    }


def _check_blocking_reasons_empty(rg: dict, raegr: dict | None) -> dict:
    br = raegr.get("blocking_reasons", []) if raegr else []
    return {
        "name": "blocking_reasons_empty",
        "passed": len(br) == 0,
        "severity": "medium",
        "detail": "apply_execution_gate_request blocking_reasons must be empty.",
    }


_CHECK_HARDCODED = {
    "apply_execution_gate_approved_intent": _check_apply_execution_gate_approved_intent,
    "apply_execution_gate_persisted": _check_apply_execution_gate_persisted,
    "gate_decision_ready": _check_gate_decision_ready,
    "execution_review_completed": _check_execution_review_completed,
    "execution_intent_recorded": _check_execution_intent_recorded,
    "confirmations_received": _check_confirmations_received,
    "request_ready_for_execution_gate_review": _check_request_ready_for_egm,
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


def _empty_contract(reason: str, blocking_reasons: list[str] | None = None) -> dict:
    _w = [
        "Apply executor contract does not authorize execution.",
        "Apply executor contract does not execute apply.",
        "A separate future executor is required before apply can occur.",
        "Evidence requirements are declared but not collected in this milestone.",
    ]
    return {
        "contract_required": False,
        "contract_status": "prepared",
        "contract_type": "apply_executor_contract",
        "decision": "blocked",
        "reason": reason,
        "apply_execution_gate_id": None,
        "apply_execution_gate_record_status": None,
        "gate_decision": None,
        "human_authorization_id": None,
        "apply_gate_id": None,
        "verification_verdict_id": None,
        "simulation_result_id": None,
        "simulation_plan_id": None,
        "dry_run_id": None,
        "requested_action": None,
        "apply_execution_gate_snapshot": None,
        "contract_checks": [],
        "execution_boundary": {
            "allowed_action_type": None,
            "allowed_tool_id": None,
            "allowed_target": None,
            "allowed_parameters": {},
            "forbidden_capabilities": [
                "shell", "subprocess", "raw_code_execution",
                "filesystem_mutation_without_executor",
                "network_mutation_without_executor",
                "database_mutation_without_executor",
                "identity_modification", "self_repair",
                "rollback_without_contract",
                "external_api_call_without_contract",
            ],
            "execution_scope": "blocked_or_not_ready_no_execution",
            "execution_allowed": False,
            "apply_allowed": False,
            "tool_execution_allowed": False,
        },
        "rollback_expectation": {
            "rollback_required_before_future_apply": True,
            "rollback_plan_required": True,
            "rollback_plan_present": False,
            "rollback_verified": False,
            "rollback_allowed": False,
            "rollback_executed": False,
            "rollback_note": "Rollback expectations are declared only; no rollback is executed in this milestone.",
        },
        "evidence_requirements": [
            {"name": "pre_execution_state_evidence", "required": True, "satisfied": False, "description": "Future executor must capture observable pre-execution state before apply."},
            {"name": "execution_result_evidence", "required": True, "satisfied": False, "description": "Future executor must capture observable result evidence after apply."},
            {"name": "post_execution_verification_evidence", "required": True, "satisfied": False, "description": "Future executor must verify the requested outcome using observable evidence."},
            {"name": "rollback_evidence", "required": True, "satisfied": False, "description": "Future executor must provide rollback evidence or explicitly record why rollback is unavailable."},
            {"name": "audit_log_evidence", "required": True, "satisfied": False, "description": "Future executor must persist an audit log of the attempted apply."},
        ],
        "required_executor_confirmations": [
            "I confirm the execution gate intent was recorded.",
            "I confirm this contract does not execute the action.",
            "I confirm this contract does not authorize apply.",
            "I confirm a future executor must collect pre-execution and post-execution evidence.",
            "I confirm rollback planning is required before future apply.",
            "I understand a separate future apply executor is required.",
        ],
        "contract_statement": None,
        "blocking_reasons": blocking_reasons or [],
        "unresolved_risks": [{"name": "apply_executor_contract_synthentic_only", "severity": "medium", "detail": "Contract is synthetic; no real executor exists yet."}],
        "recommended_next_step": reason,
        "execution_review_completed": False,
        "execution_intent_recorded": False,
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
        "metadata": {},
        "warnings": _w,
    }


def build_apply_executor_contract(
    apply_execution_gate_record: dict | None,
    context: dict | None = None,
) -> dict:
    """Build an apply executor contract from an apply_execution_gate_record.

    Args:
        apply_execution_gate_record: The persisted AEGR dict.
        context: Optional metadata context (e.g. session_id).

    Returns:
        A structured apply_executor_contract dict.
    """
    _meta: dict = {
        "source": "apply_executor_contract_builder",
        "schema_version": "1.0",
    }
    if context:
        if context.get("session_id"):
            _meta["session_id"] = context["session_id"]

    # --- Rule 1: missing record ---
    if apply_execution_gate_record is None:
        return _empty_contract(
            reason="Apply execution gate record was not found.",
            blocking_reasons=["Apply execution gate record was not found."],
        )

    rg = apply_execution_gate_record
    raegr = rg.get("apply_execution_gate_request")
    _warns: list[str] = list(rg.get("warnings", []))
    # Also copy warnings from the nested request with prefix
    if isinstance(raegr, dict):
        for w in raegr.get("warnings", []):
            _warns.append(f"apply_execution_gate_request_warning: {w}")

    rg_status = rg.get("status")
    rg_decision = rg.get("gate_decision")

    # --- Rule 2: status check ---
    if rg_status != "approved_execution_intent":
        return _empty_contract(
            reason="Apply execution gate record is not approved_execution_intent.",
            blocking_reasons=["Record status is not approved_execution_intent."],
        )

    # --- Rule 3: gate_decision check ---
    if rg_decision != "ready_for_execution_gate_review":
        return _empty_contract(
            reason="Apply execution gate record was not based on a ready gate request.",
            blocking_reasons=["Gate decision is not ready_for_execution_gate_review."],
        )

    # --- Rule 4: execution_intent_recorded ---
    if not rg.get("execution_intent_recorded"):
        return _empty_contract(
            reason="Execution intent has not been recorded.",
            blocking_reasons=["execution_intent_recorded is not true."],
        )

    # --- Rule 5: execution_review_completed ---
    if not rg.get("execution_review_completed"):
        return _empty_contract(
            reason="Execution review is not completed.",
            blocking_reasons=["execution_review_completed is not true."],
        )

    # --- Rule 6: apply_authorized ---
    if rg.get("apply_authorized") is True:
        return _empty_contract(
            reason="Apply execution gate record is unexpectedly marked apply-authorized.",
            blocking_reasons=["apply_authorized is true."],
        )

    # --- Rule 7: apply_executed / rollback_executed ---
    block_reasons: list[str] = []
    if rg.get("apply_executed") is True:
        block_reasons.append("apply_executed is true.")
    if rg.get("rollback_executed") is True:
        block_reasons.append("rollback_executed is true.")
    if block_reasons:
        return _empty_contract(
            reason="Apply execution gate record indicates execution already occurred.",
            blocking_reasons=block_reasons,
        )

    # --- Rule 8: missing request payload ---
    if raegr is None or not isinstance(raegr, dict):
        unresolved_risks = [{"name": "missing_apply_execution_gate_request", "severity": "high", "detail": "Apply execution gate request payload is missing or invalid."}]
        return {
            **_empty_contract("Apply execution gate request payload is missing or invalid.", []),
            "decision": "not_ready",
            "reason": "Apply execution gate request payload is missing or invalid.",
            "unresolved_risks": unresolved_risks,
            "recommended_next_step": "Regenerate the apply execution gate request and execution-intent record.",
        }

    # --- Rule 9: evaluate contract checks ---
    checks: list[dict] = []
    for check_name, _ in _CHECK_DEFS:
        fn = _CHECK_HARDCODED[check_name]
        checks.append(fn(rg, raegr))

    # --- Rule 10: decision logic ---
    has_critical_fail = any(c.get("passed") is False for c in checks if c.get("severity") == "critical")
    has_high_fail = any(c.get("passed") is False for c in checks if c.get("severity") == "high")
    has_medium_fail = any(c.get("passed") is False for c in checks if c.get("severity") == "medium")
    has_low_fail = any(c.get("passed") is False for c in checks if c.get("severity") == "low")

    if has_critical_fail or has_high_fail:
        contract_dec = "blocked"
        contract_required = False
    elif has_medium_fail or has_low_fail:
        contract_dec = "not_ready"
        contract_required = False
    else:
        contract_dec = "contract_ready"
        contract_required = True

    # --- Build unresolved_risks ---
    unresolved_risks: list[dict] = list(raegr.get("unresolved_risks", []))
    if contract_dec == "contract_ready":
        unresolved_risks.append({
            "name": "executor_contract_prepared",
            "severity": "medium",
            "detail": "Executor contract is prepared; a future record store and executor milestones are still required.",
        })

    # --- Blocking reasons ---
    blocking_reasons: list[str] = list(raegr.get("blocking_reasons", []))
    if contract_dec == "blocked":
        for c in checks:
            if c.get("passed") is False and c.get("severity") in ("critical", "high"):
                blocking_reasons.append(f"Contract check failed: {c['name']}.")

    # --- Execution boundary ---
    ra = raegr.get("requested_action", {}) or {}
    if contract_dec == "contract_ready":
        execution_boundary = {
            "allowed_action_type": ra.get("action_type"),
            "allowed_tool_id": ra.get("tool_id"),
            "allowed_target": ra.get("target"),
            "allowed_parameters": ra.get("parameters") or {},
            "forbidden_capabilities": [
                "shell", "subprocess", "raw_code_execution",
                "filesystem_mutation_without_executor",
                "network_mutation_without_executor",
                "database_mutation_without_executor",
                "identity_modification", "self_repair",
                "rollback_without_contract",
                "external_api_call_without_contract",
            ],
            "execution_scope": "contract_only_no_execution",
            "execution_allowed": False,
            "apply_allowed": False,
            "tool_execution_allowed": False,
        }
    else:
        execution_boundary = {
            "allowed_action_type": ra.get("action_type") if ra else None,
            "allowed_tool_id": ra.get("tool_id") if ra else None,
            "allowed_target": ra.get("target") if ra else None,
            "allowed_parameters": ra.get("parameters") or {},
            "forbidden_capabilities": [
                "shell", "subprocess", "raw_code_execution",
                "filesystem_mutation_without_executor",
                "network_mutation_without_executor",
                "database_mutation_without_executor",
                "identity_modification", "self_repair",
                "rollback_without_contract",
                "external_api_call_without_contract",
            ],
            "execution_scope": "blocked_or_not_ready_no_execution",
            "execution_allowed": False,
            "apply_allowed": False,
            "tool_execution_allowed": False,
        }

    # --- Rollback expectation ---
    rollback_expectation = {
        "rollback_required_before_future_apply": True,
        "rollback_plan_required": True,
        "rollback_plan_present": False,
        "rollback_verified": False,
        "rollback_allowed": False,
        "rollback_executed": False,
        "rollback_note": "Rollback expectations are declared only; no rollback is executed in this milestone.",
    }

    # --- Evidence requirements ---
    evidence_requirements = [
        {"name": "pre_execution_state_evidence", "required": True, "satisfied": False, "description": "Future executor must capture observable pre-execution state before apply."},
        {"name": "execution_result_evidence", "required": True, "satisfied": False, "description": "Future executor must capture observable result evidence after apply."},
        {"name": "post_execution_verification_evidence", "required": True, "satisfied": False, "description": "Future executor must verify the requested outcome using observable evidence."},
        {"name": "rollback_evidence", "required": True, "satisfied": False, "description": "Future executor must provide rollback evidence or explicitly record why rollback is unavailable."},
        {"name": "audit_log_evidence", "required": True, "satisfied": False, "description": "Future executor must persist an audit log of the attempted apply."},
    ]

    # --- Recommended next step ---
    step_map = {
        "contract_ready": "Persist this contract in a future contract record milestone; do not execute changes yet.",
        "not_ready": "Resolve contract readiness issues before preparing executor contract.",
        "blocked": "Resolve blocking conditions before continuing.",
    }

    # --- Required executor confirmations ---
    required_executor_confirmations = [
        "I confirm the execution gate intent was recorded.",
        "I confirm this contract does not execute the action.",
        "I confirm this contract does not authorize apply.",
        "I confirm a future executor must collect pre-execution and post-execution evidence.",
        "I confirm rollback planning is required before future apply.",
        "I understand a separate future apply executor is required.",
    ]

    # --- Contract statement ---
    contract_statement = None
    if contract_dec == "contract_ready":
        contract_statement = "Apply executor contract is prepared for future executor design. This contract does not authorize or execute apply."

    # --- Finalize warnings ---
    warnings = list(_warns)
    warnings.append("Apply executor contract does not authorize execution.")
    warnings.append("Apply executor contract does not execute apply.")
    warnings.append("A separate future executor is required before apply can occur.")
    warnings.append("Evidence requirements are declared but not collected in this milestone.")

    return {
        "contract_required": contract_required,
        "contract_status": "prepared",
        "contract_type": "apply_executor_contract",
        "decision": contract_dec,
        "reason": "" if contract_dec == "contract_ready" else "Contract checks did not pass.",
        "apply_execution_gate_id": rg.get("apply_execution_gate_id"),
        "apply_execution_gate_record_status": rg_status,
        "gate_decision": rg_decision,
        "human_authorization_id": rg.get("human_authorization_id"),
        "apply_gate_id": rg.get("apply_gate_id"),
        "verification_verdict_id": rg.get("verification_verdict_id"),
        "simulation_result_id": rg.get("simulation_result_id"),
        "simulation_plan_id": rg.get("simulation_plan_id"),
        "dry_run_id": rg.get("dry_run_id"),
        "requested_action": dict(ra) if ra else None,
        "apply_execution_gate_snapshot": dict(rg),
        "contract_checks": checks,
        "execution_boundary": execution_boundary,
        "rollback_expectation": rollback_expectation,
        "evidence_requirements": evidence_requirements,
        "required_executor_confirmations": required_executor_confirmations,
        "contract_statement": contract_statement,
        "blocking_reasons": blocking_reasons,
        "unresolved_risks": unresolved_risks,
        "recommended_next_step": step_map.get(contract_dec, "Resolve blocking conditions before continuing."),
        "execution_review_completed": rg.get("execution_review_completed", False),
        "execution_intent_recorded": rg.get("execution_intent_recorded", False),
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
        "metadata": dict(_meta),
        "warnings": warnings,
    }
