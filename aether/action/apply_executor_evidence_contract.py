"""Apply Executor Evidence Contract Builder (Milestone 75A).

Builds a structured apply_executor_evidence_contract object from an approved_plan_intent
apply_executor_plan_record. This is a declarative evidence requirements object only — it
does NOT collect evidence, execute tools, authorize apply, or persist records.
"""

from __future__ import annotations


def build_apply_executor_evidence_contract(
    apply_executor_plan_record: dict | None, context: dict | None = None,
) -> dict:
    """Build an apply_executor_evidence_contract object from an approved plan record.

    Returns a contract object that declares required evidence obligations without
    collecting evidence or authorizing execution.

    All safety-critical flags (apply_authorized, execution_allowed, evidence_collected,
    rollback_plan_attached, etc.) remain False per Milestone 75A hard safety invariants.
    """
    # Shared default values for safe fallback
    default_record: dict = {
        "evidence_contract_required": False,
        "evidence_contract_status": None,
        "contract_type": "apply_executor_evidence_contract",
        "decision": "blocked",
        "reason": "No plan record provided.",
        "apply_executor_plan_id": None,
        "apply_executor_plan_record_status": None,
        "plan_decision": None,
        "apply_executor_contract_id": None,
        "apply_execution_gate_id": None,
        "human_authorization_id": None,
        "apply_gate_id": None,
        "verification_verdict_id": None,
        "simulation_result_id": None,
        "simulation_plan_id": None,
        "dry_run_id": None,
        "requested_action": None,
        "apply_executor_plan_snapshot": None,
        "evidence_contract_checks": [],
        "required_evidence_items": [],
        "pre_execution_evidence_requirements": [],
        "during_execution_evidence_requirements": [],
        "post_execution_evidence_requirements": [],
        "rollback_evidence_requirements": [],
        "audit_evidence_requirements": [],
        "evidence_collection_constraints": {},
        "evidence_acceptance_criteria": [],
        "required_evidence_confirmations": [],
        "evidence_contract_statement": None,
        "blocking_reasons": [],
        "unresolved_risks": [],
        "recommended_next_step": None,
        "plan_review_completed": False,
        "plan_intent_recorded": False,
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
        "apply_executor_evidence_contract_execution_allowed": False,
        "metadata": {},
        "warnings": [
            "Apply executor evidence contract does not authorize execution.",
            "Apply executor evidence contract does not authorize apply.",
            "Evidence requirements are declared but not collected.",
            "Rollback evidence is required but not collected in this milestone.",
            "A separate future evidence collector is required before apply can occur.",
        ],
    }

    if apply_executor_plan_record is None:
        return _apply_fallback(default_record, "Apply executor plan record was not found.", context)

    # Rule 2: status must be approved_plan_intent
    status = apply_executor_plan_record.get("status")
    if status != "approved_plan_intent":
        return _apply_fallback(
            default_record,
            "Apply executor plan record is not approved_plan_intent.",
            context,
            blocking_reasons=["Record status is not approved_plan_intent."],
        )

    # Rule 3: plan_decision must be plan_ready
    plan_decision = apply_executor_plan_record.get("plan_decision")
    if plan_decision != "plan_ready":
        return _apply_fallback(
            default_record,
            "Apply executor plan record was not based on a ready plan.",
            context,
            blocking_reasons=["Plan decision is not plan_ready."],
        )

    # Rule 4: plan_intent_recorded must be True
    if not apply_executor_plan_record.get("plan_intent_recorded"):
        return _apply_fallback(
            default_record,
            "Plan intent has not been recorded.",
            context,
            blocking_reasons=["plan_intent_recorded is not true."],
        )

    # Rule 5: plan_review_completed must be True
    if not apply_executor_plan_record.get("plan_review_completed"):
        return _apply_fallback(
            default_record,
            "Plan review is not completed.",
            context,
            blocking_reasons=["plan_review_completed is not true."],
        )

    # Rule 6: evidence_collected must be False
    if apply_executor_plan_record.get("evidence_collected"):
        return _apply_fallback(
            default_record,
            "Apply executor plan record unexpectedly indicates evidence was collected.",
            context,
            blocking_reasons=["evidence_collected is true."],
        )

    # Rule 7: rollback_plan_attached must be False
    if apply_executor_plan_record.get("rollback_plan_attached"):
        return _apply_fallback(
            default_record,
            "Apply executor plan record unexpectedly indicates rollback plan was already attached.",
            context,
            blocking_reasons=["rollback_plan_attached is true."],
        )

    # Rule 8: apply_authorized must be False
    if apply_executor_plan_record.get("apply_authorized"):
        return _apply_fallback(
            default_record,
            "Apply executor plan record is unexpectedly marked apply-authorized.",
            context,
            blocking_reasons=["apply_authorized is true."],
        )

    # Rule 9: apply_executed and rollback_executed must be False
    if apply_executor_plan_record.get("apply_executed"):
        return _apply_fallback(
            default_record,
            "Apply executor plan record indicates execution already occurred.",
            context,
            blocking_reasons=["apply_executed is true."],
        )
    if apply_executor_plan_record.get("rollback_executed"):
        return _apply_fallback(
            default_record,
            "Apply executor plan record indicates execution already occurred.",
            context,
            blocking_reasons=["rollback_executed is true."],
        )

    # Get the nested apply_executor_plan dict
    apply_executor_plan = apply_executor_plan_record.get("apply_executor_plan")
    if not isinstance(apply_executor_plan, dict):
        # Rule 10: missing/invalid plan -> not_ready
        contract = default_record.copy()
        contract.update({
            "decision": "not_ready",
            "reason": "Apply executor plan payload is missing or invalid.",
            "evidence_contract_required": False,
            "unresolved_risks": [{
                "name": "missing_apply_executor_plan",
                "severity": "high",
                "detail": "Apply executor plan payload is missing or invalid.",
            }],
            "recommended_next_step": "Regenerate the apply executor plan and plan-intent record.",
        })
        # Add metadata
        if context and "session_id" in context:
            contract["metadata"] = {"source": "apply_executor_evidence_contract_builder", "schema_version": "1.0", "session_id": context["session_id"]}
        else:
            contract["metadata"] = {"source": "apply_executor_evidence_contract_builder", "schema_version": "1.0"}
        return contract

    # -----------------------------------------------------------------
    # Evaluate evidence_contract_checks (Rules 11)
    # -----------------------------------------------------------------
    checks: list[dict] = []

    # Check: apply_executor_plan_approved_intent (low)
    checks.append({
        "name": "apply_executor_plan_approved_intent",
        "passed": status == "approved_plan_intent",
        "severity": "low",
        "detail": "Apply executor plan record status is approved_plan_intent.",
    })

    # Check: apply_executor_plan_persisted (low)
    persisted = apply_executor_plan_record.get("apply_executor_plan_persisted")
    checks.append({
        "name": "apply_executor_plan_persisted",
        "passed": persisted is True,
        "severity": "low",
        "detail": "Apply executor plan record is persisted.",
    })

    # Check: plan_decision_ready (high)
    checks.append({
        "name": "plan_decision_ready",
        "passed": plan_decision == "plan_ready",
        "severity": "high",
        "detail": "Plan decision is plan_ready.",
    })

    # Check: plan_review_completed (low)
    checks.append({
        "name": "plan_review_completed",
        "passed": apply_executor_plan_record.get("plan_review_completed") is True,
        "severity": "low",
        "detail": "Plan review is completed.",
    })

    # Check: plan_intent_recorded (low)
    checks.append({
        "name": "plan_intent_recorded",
        "passed": apply_executor_plan_record.get("plan_intent_recorded") is True,
        "severity": "low",
        "detail": "Plan intent is recorded.",
    })

    # Check: confirmations_received (medium) — verify confirmations_received covers confirmations_required
    confirmations_received = apply_executor_plan_record.get("confirmations_received", []) or []
    confirmations_required = apply_executor_plan_record.get("confirmations_required", []) or []
    checks.append({
        "name": "confirmations_received",
        "passed": all(c in confirmations_received for c in confirmations_required) and len(confirmations_required) > 0,
        "severity": "medium",
        "detail": "All required confirmations have been received.",
    })

    # Check: plan_ready (high) — nested plan decision
    checks.append({
        "name": "plan_ready",
        "passed": apply_executor_plan.get("decision") == "plan_ready",
        "severity": "high",
        "detail": "Nested apply_executor_plan decision is plan_ready.",
    })

    # Check: ordered_execution_steps_declared (medium)
    ordered_steps = apply_executor_plan.get("ordered_execution_steps", [])
    checks.append({
        "name": "ordered_execution_steps_declared",
        "passed": isinstance(ordered_steps, list) and len(ordered_steps) == 6,
        "severity": "medium",
        "detail": "Ordered execution steps declared with exactly 6 steps.",
    })

    # Check: evidence_capture_plan_declared (medium)
    evidence_plan = apply_executor_plan.get("evidence_capture_plan", [])
    checks.append({
        "name": "evidence_capture_plan_declared",
        "passed": isinstance(evidence_plan, list) and len(evidence_plan) == 5,
        "severity": "medium",
        "detail": "Evidence capture plan declared with exactly 5 items.",
    })

    # Check: evidence_capture_plan_not_collected (critical)
    checks.append({
        "name": "evidence_capture_plan_not_collected",
        "passed": all(
            not item.get("collected_now", False) and not item.get("collection_allowed_now", False)
            for item in evidence_plan
        ),
        "severity": "critical",
        "detail": "No evidence capture plan items indicate collection is allowed or performed now.",
    })

    # Check: required_evidence_names_present (medium)
    required_evidence_names = [
        "pre_execution_state_evidence",
        "execution_result_evidence",
        "post_execution_verification_evidence",
        "rollback_evidence",
        "audit_log_evidence",
    ]
    present_names = [item.get("name") for item in evidence_plan if isinstance(item, dict)]
    checks.append({
        "name": "required_evidence_names_present",
        "passed": all(name in present_names for name in required_evidence_names),
        "severity": "medium",
        "detail": f"All required evidence names present: {required_evidence_names}.",
    })

    # Check: rollback_plan_requirement_declared (medium)
    rollback_req = apply_executor_plan.get("rollback_plan_requirement", {})
    checks.append({
        "name": "rollback_plan_requirement_declared",
        "passed": isinstance(rollback_req, dict) and rollback_req.get("rollback_required_before_future_apply") is True,
        "severity": "medium",
        "detail": "Rollback plan requirement declared with required_before_future_apply true.",
    })

    # Check: rollback_plan_not_attached (critical)
    checks.append({
        "name": "rollback_plan_not_attached",
        "passed": apply_executor_plan_record.get("rollback_plan_attached") is False and rollback_req.get("rollback_plan_attached") is False,
        "severity": "critical",
        "detail": "Rollback plan is not attached in record or requirement.",
    })

    # Check: apply_not_authorized (critical)
    checks.append({
        "name": "apply_not_authorized",
        "passed": apply_executor_plan_record.get("apply_authorized") is False and apply_executor_plan.get("apply_authorized") is False,
        "severity": "critical",
        "detail": "Apply is not authorized in record or plan.",
    })

    # Check: apply_not_executed (critical)
    checks.append({
        "name": "apply_not_executed",
        "passed": apply_executor_plan_record.get("apply_executed") is False,
        "severity": "critical",
        "detail": "Apply was not executed.",
    })

    # Check: rollback_not_executed (critical)
    checks.append({
        "name": "rollback_not_executed",
        "passed": apply_executor_plan_record.get("rollback_executed") is False,
        "severity": "critical",
        "detail": "Rollback was not executed.",
    })

    # Check: execution_flags_blocked (high) — all execution flags false in both record and plan
    record_exec_flags = [
        apply_executor_plan_record.get("execution_allowed"),
        apply_executor_plan_record.get("tool_execution_allowed"),
        apply_executor_plan_record.get("dry_run_execution_allowed"),
        apply_executor_plan_record.get("simulation_execution_allowed"),
        apply_executor_plan_record.get("apply_gate_execution_allowed"),
        apply_executor_plan_record.get("human_authorization_execution_allowed"),
        apply_executor_plan_record.get("apply_execution_gate_execution_allowed"),
        apply_executor_plan_record.get("apply_executor_contract_execution_allowed"),
        apply_executor_plan_record.get("apply_executor_plan_execution_allowed"),
    ]
    plan_exec_flags = [
        apply_executor_plan.get("execution_allowed"),
        apply_executor_plan.get("tool_execution_allowed"),
        apply_executor_plan.get("dry_run_execution_allowed"),
        apply_executor_plan.get("simulation_execution_allowed"),
        apply_executor_plan.get("apply_gate_execution_allowed"),
        apply_executor_plan.get("human_authorization_execution_allowed"),
        apply_executor_plan.get("apply_execution_gate_execution_allowed"),
        apply_executor_plan.get("apply_executor_contract_execution_allowed"),
        apply_executor_plan.get("apply_executor_plan_execution_allowed"),
    ]
    all_exec_flags = [f is False for f in (record_exec_flags + plan_exec_flags)]
    checks.append({
        "name": "execution_flags_blocked",
        "passed": all(all_exec_flags),
        "severity": "high",
        "detail": "All execution flags are false in record and plan.",
    })

    # Check: apply_flags_blocked (critical) — apply and rollback flags false in both
    record_apply_flags = [
        apply_executor_plan_record.get("apply_allowed"),
        apply_executor_plan_record.get("rollback_allowed"),
    ]
    plan_apply_flags = [
        apply_executor_plan.get("apply_allowed"),
        apply_executor_plan.get("rollback_allowed"),
    ]
    all_apply_flags = [f is False for f in (record_apply_flags + plan_apply_flags)]
    checks.append({
        "name": "apply_flags_blocked",
        "passed": all(all_apply_flags),
        "severity": "critical",
        "detail": "All apply/rollback flags are false in record and plan.",
    })

    # Check: requested_action_present (medium)
    requested_action = apply_executor_plan.get("requested_action")
    checks.append({
        "name": "requested_action_present",
        "passed": isinstance(requested_action, dict),
        "severity": "medium",
        "detail": "Requested action is present and a dict.",
    })

    # Check: requested_action_type_allowed (high)
    allowed_action_types = {
        "status_check", "read_only_check", "inspection", "validation",
        "report_generation", "plan_review",
    }
    act_type = requested_action.get("action_type") if isinstance(requested_action, dict) else None
    checks.append({
        "name": "requested_action_type_allowed",
        "passed": act_type in allowed_action_types,
        "severity": "high",
        "detail": f"Requested action type {act_type} is allowed.",
    })

    # Check: target_present (medium)
    target = requested_action.get("target") if isinstance(requested_action, dict) else ""
    checks.append({
        "name": "target_present",
        "passed": isinstance(target, str) and target.strip() != "",
        "severity": "medium",
        "detail": "Requested action target is a non-empty string.",
    })

    # Check: no_direct_executor_present (critical) — forbid dangerous keys
    forbidden_keys = {
        "executor", "command", "shell", "subprocess", "python_code",
        "raw_code", "script", "apply_now", "execute_now",
        "collect_evidence_now", "evidence_now",
    }
    has_forbidden = any(k in requested_action for k in forbidden_keys) if isinstance(requested_action, dict) else False
    checks.append({
        "name": "no_direct_executor_present",
        "passed": not has_forbidden,
        "severity": "critical",
        "detail": "Requested action contains no direct executor or evidence-collection commands.",
    })

    # Check: plan_blocking_reasons_empty (medium)
    plan_blocking = apply_executor_plan.get("blocking_reasons", []) or []
    checks.append({
        "name": "plan_blocking_reasons_empty",
        "passed": len(plan_blocking) == 0,
        "severity": "medium",
        "detail": "Plan has no blocking reasons.",
    })

    # Check: evidence_contract_not_previously_allowed (critical)
    checks.append({
        "name": "evidence_contract_not_previously_allowed",
        "passed": not apply_executor_plan.get("apply_executor_evidence_contract_execution_allowed", False),
        "severity": "critical",
        "detail": "Evidence contract execution has not been previously allowed.",
    })

    # -----------------------------------------------------------------
    # Determine decision based on check results (Rule 12)
    # -----------------------------------------------------------------
    critical_checks = [c for c in checks if c["severity"] == "critical"]
    high_checks = [c for c in checks if c["severity"] == "high"]
    medium_checks = [c for c in checks if c["severity"] == "medium"]
    low_checks = [c for c in checks if c["severity"] == "low"]

    any_critical_fail = any(not c["passed"] for c in critical_checks)
    any_high_fail = any(not c["passed"] for c in high_checks)
    any_medium_fail = any(not c["passed"] for c in medium_checks)
    any_low_fail = any(not c["passed"] for c in low_checks)

    if any_critical_fail or any_high_fail:
        decision = "blocked"
        evidence_contract_required = False
        reason = "Evidence contract failed critical or high checks."
        blocking_reasons = [c["detail"] for c in checks if not c["passed"] and c["severity"] in ("critical", "high")]
        recommended_next_step = "Resolve blocking conditions before continuing."
    elif any_medium_fail or any_low_fail:
        decision = "not_ready"
        evidence_contract_required = False
        reason = "Evidence contract failed medium or low checks."
        blocking_reasons = [c["detail"] for c in checks if not c["passed"] and c["severity"] in ("medium", "low")]
        recommended_next_step = "Resolve evidence contract readiness issues before preparing evidence contract."
    else:
        decision = "evidence_contract_ready"
        evidence_contract_required = True
        reason = "All evidence contract checks passed."
        blocking_reasons = []
        recommended_next_step = "Persist this evidence contract in a future evidence contract record milestone; do not collect evidence or execute changes yet."

    # Build the final evidence contract dict
    contract: dict = default_record.copy()
    contract.update({
        "decision": decision,
        "reason": reason,
        "evidence_contract_required": evidence_contract_required,
        "evidence_contract_status": "prepared" if decision == "evidence_contract_ready" else None,
        "apply_executor_plan_id": apply_executor_plan_record.get("apply_executor_plan_id"),
        "apply_executor_plan_record_status": status,
        "plan_decision": plan_decision,
        "apply_executor_contract_id": apply_executor_plan.get("apply_executor_contract_id"),
        "apply_execution_gate_id": apply_executor_plan.get("apply_execution_gate_id"),
        "human_authorization_id": apply_executor_plan.get("human_authorization_id"),
        "apply_gate_id": apply_executor_plan.get("apply_gate_id"),
        "verification_verdict_id": apply_executor_plan.get("verification_verdict_id"),
        "simulation_result_id": apply_executor_plan.get("simulation_result_id"),
        "simulation_plan_id": apply_executor_plan.get("simulation_plan_id"),
        "dry_run_id": apply_executor_plan.get("dry_run_id"),
        "requested_action": requested_action,
        "apply_executor_plan_snapshot": apply_executor_plan,
        "evidence_contract_checks": checks,
        "blocking_reasons": blocking_reasons,
        "recommended_next_step": recommended_next_step,
        "plan_review_completed": apply_executor_plan_record.get("plan_review_completed"),
        "plan_intent_recorded": apply_executor_plan_record.get("plan_intent_recorded"),
    })

    # Required evidence items (Rule 13)
    contract["required_evidence_items"] = [
        {
            "name": name,
            "required": True,
            "collected": False,
            "collection_allowed_now": False,
            "source_plan_item": None,
            "description": f"Required evidence item for {name}.",
            "acceptance_criteria": [
                "Evidence item name matches required evidence contract.",
                "Evidence captured by future authorized evidence collector only.",
                "Evidence timestamped and linked to apply_executor_plan_id.",
                "Evidence not collected by this contract builder.",
                "Evidence collection does not imply apply authorization.",
            ],
            "failure_policy": "Evidence collection not permitted; must be deferred to future evidence collector.",
        }
        for name in required_evidence_names
    ]

    # Evidence requirement groups (Rules 14-18)
    contract["pre_execution_evidence_requirements"] = [
        {"name": "requested_action_snapshot", "required": True, "collected": False, "collection_allowed_now": False, "description": "Snapshot of requested action before execution."},
        {"name": "target_state_before_apply", "required": True, "collected": False, "collection_allowed_now": False, "description": "Target system state before any apply."},
        {"name": "permission_state_snapshot", "required": True, "collected": False, "collection_allowed_now": False, "description": "Authorization and permission state snapshot."},
        {"name": "rollback_precondition_snapshot", "required": True, "collected": False, "collection_allowed_now": False, "description": "Rollback preconditions snapshot."},
    ]
    contract["during_execution_evidence_requirements"] = [
        {"name": "executor_attempt_log", "required": True, "collected": False, "collection_allowed_now": False, "description": "Log of executor attempts."},
        {"name": "tool_call_boundary_log", "required": True, "collected": False, "collection_allowed_now": False, "description": "Boundary of tool calls."},
        {"name": "execution_result_raw_output", "required": True, "collected": False, "collection_allowed_now": False, "description": "Raw output of execution."},
    ]
    contract["post_execution_evidence_requirements"] = [
        {"name": "target_state_after_apply", "required": True, "collected": False, "collection_allowed_now": False, "description": "Target state after apply."},
        {"name": "verification_result_after_apply", "required": True, "collected": False, "collection_allowed_now": False, "description": "Verification result after apply."},
        {"name": "user_visible_outcome_summary", "required": True, "collected": False, "collection_allowed_now": False, "description": "Summary of user-visible outcome."},
    ]
    contract["rollback_evidence_requirements"] = [
        {"name": "rollback_plan_snapshot", "required": True, "collected": False, "collection_allowed_now": False, "description": "Rollback plan snapshot."},
        {"name": "rollback_trigger_conditions", "required": True, "collected": False, "collection_allowed_now": False, "description": "Conditions that trigger rollback."},
        {"name": "rollback_execution_log_placeholder", "required": True, "collected": False, "collection_allowed_now": False, "description": "Placeholder for rollback execution log."},
        {"name": "rollback_verification_result_placeholder", "required": True, "collected": False, "collection_allowed_now": False, "description": "Placeholder for rollback verification result."},
    ]
    contract["audit_evidence_requirements"] = [
        {"name": "apply_executor_plan_record_snapshot", "required": True, "collected": False, "collection_allowed_now": False, "description": "Snapshot of apply executor plan record."},
        {"name": "apply_executor_contract_record_snapshot", "required": True, "collected": False, "collection_allowed_now": False, "description": "Snapshot of apply executor contract record."},
        {"name": "approval_chain_snapshot", "required": True, "collected": False, "collection_allowed_now": False, "description": "Snapshot of approval chain."},
        {"name": "final_audit_summary_placeholder", "required": True, "collected": False, "collection_allowed_now": False, "description": "Placeholder for final audit summary."},
    ]

    # Evidence collection constraints (Rule 19)
    if decision == "evidence_contract_ready":
        contract["evidence_collection_constraints"] = {
            "collection_scope": "contract_only_no_collection",
            "collection_allowed_now": False,
            "execution_allowed": False,
            "apply_allowed": False,
            "tool_execution_allowed": False,
            "filesystem_inspection_allowed": False,
            "network_inspection_allowed": False,
            "database_inspection_allowed": False,
            "external_api_call_allowed": False,
            "forbidden_collection_methods": [
                "shell", "subprocess", "raw_code_execution", "filesystem_scan",
                "network_probe", "database_query", "external_api_call",
                "identity_modification", "self_repair", "apply_execution", "rollback_execution"
            ],
        }
    else:
        contract["evidence_collection_constraints"] = {
            "collection_scope": "blocked_or_not_ready_contract_only_no_collection",
            "collection_allowed_now": False,
            "execution_allowed": False,
            "apply_allowed": False,
            "tool_execution_allowed": False,
            "filesystem_inspection_allowed": False,
            "network_inspection_allowed": False,
            "database_inspection_allowed": False,
            "external_api_call_allowed": False,
            "forbidden_collection_methods": [
                "shell", "subprocess", "raw_code_execution", "filesystem_scan",
                "network_probe", "database_query", "external_api_call",
                "identity_modification", "self_repair", "apply_execution", "rollback_execution"
            ],
        }

    # Evidence acceptance criteria (Rule 20)
    contract["evidence_acceptance_criteria"] = [
        {"criterion": "Evidence item names must match the required evidence contract.", "required": True, "satisfied_now": False},
        {"criterion": "Evidence must be captured by a future authorized evidence collector only.", "required": True, "satisfied_now": False},
        {"criterion": "Evidence must be timestamped and linked to the correct apply_executor_plan_id.", "required": True, "satisfied_now": False},
        {"criterion": "Evidence must not be collected by this contract builder.", "required": True, "satisfied_now": False},
        {"criterion": "Evidence collection must not imply apply authorization.", "required": True, "satisfied_now": False},
    ]

    # Required evidence confirmations (Rule 21)
    if decision == "evidence_contract_ready":
        contract["required_evidence_confirmations"] = [
            "I confirm the plan intent was recorded.",
            "I confirm this evidence contract does not collect evidence.",
            "I confirm this evidence contract does not authorize apply.",
            "I confirm this evidence contract does not authorize execution.",
            "I confirm rollback evidence is required before future apply.",
            "I understand a separate future evidence collector is required.",
        ]
    else:
        contract["required_evidence_confirmations"] = []

    # Evidence contract statement (Rule 22)
    if decision == "evidence_contract_ready":
        contract["evidence_contract_statement"] = (
            "Apply executor evidence contract is prepared for future evidence collection design. "
            "This contract does not collect evidence, authorize execution, or execute apply."
        )
    else:
        contract["evidence_contract_statement"] = None

    # Metadata (Rule 24)
    metadata: dict = {
        "source": "apply_executor_evidence_contract_builder",
        "schema_version": "1.0",
    }
    if context and "session_id" in context:
        metadata["session_id"] = context["session_id"]
    contract["metadata"] = metadata

    return contract


def _apply_fallback(
    default: dict, reason: str, context: dict | None = None,
    blocking_reasons: list[str] | None = None, unresolved_risks: list[dict] | None = None,
    recommended_next_step: str | None = None,
) -> dict:
    """Create a fallback blocked evidence contract when preconditions fail."""
    contract = default.copy()
    contract["reason"] = reason
    contract["decision"] = "blocked"
    contract["evidence_contract_required"] = False
    if blocking_reasons:
        contract["blocking_reasons"] = blocking_reasons
    else:
        contract["blocking_reasons"] = [reason]
    if recommended_next_step:
        contract["recommended_next_step"] = recommended_next_step
    else:
        contract["recommended_next_step"] = "Resolve blocking conditions before continuing."
    if unresolved_risks:
        contract["unresolved_risks"] = unresolved_risks
    else:
        contract["unresolved_risks"] = [{"name": "evidence_contract_blocked", "severity": "high", "detail": reason}]
    # Add metadata from context if available
    if context and "session_id" in context:
        contract["metadata"] = {"source": "apply_executor_evidence_contract_builder", "schema_version": "1.0", "session_id": context["session_id"]}
    else:
        contract["metadata"] = {"source": "apply_executor_evidence_contract_builder", "schema_version": "1.0"}
    return contract
