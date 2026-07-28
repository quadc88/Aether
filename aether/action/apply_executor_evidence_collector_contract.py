"""Apply Executor Evidence Collector Contract Builder for Aether (Milestone 79A).

Builds a structured apply_executor_evidence_collector_contract from an approved
collection plan record. This is declarative only — does NOT collect evidence,
execute tools, authorize apply, or modify state.

All safety flags remain false per the Aether safety chain.
"""

from __future__ import annotations
from datetime import datetime, timezone as _tz

_DIRECTOR_EXECUTOR_KEYS = {
    "executor",
    "command",
    "shell",
    "subprocess",
    "python_code",
    "raw_code",
    "script",
    "apply_now",
    "execute_now",
    "collect_evidence_now",
    "evidence_now",
    "inspect_now",
    "scan_now",
    "query_now",
}

_ALLOWED_ACTION_TYPES = (
    "status_check",
    "read_only_check",
    "inspection",
    "validation",
    "report_generation",
    "plan_review",
)


# --------------------------------------------------------------------------- #
# Check helper functions (safe defaults: missing = False/empty)
# --------------------------------------------------------------------------- #

def _get(record: dict, key: str, default=None):
    """Safely get a value, returning default if missing."""
    return record.get(key, default)


def _check_apply_not_authorized(record: dict | None) -> dict:
    if record is None:
        return {"name": "apply_not_authorized", "passed": False, "severity": "critical",
                "detail": "Apply must not be authorized (record not found)."}
    rec_auth = _get(record, "apply_authorized") is False
    aecp = _get(record, "apply_executor_evidence_collection_plan", {})
    plan_auth = _get(aecp, "apply_authorized") is True
    return {"name": "apply_not_authorized", "passed": rec_auth and not plan_auth,
            "severity": "critical", "detail": "Apply must not be authorized." if not (rec_auth and not plan_auth) else "Apply correctly not authorized."}


def _check_execution_not_authorized(record: dict | None) -> dict:
    if record is None:
        return {"name": "execution_not_authorized", "passed": False, "severity": "critical",
                "detail": "Execution must not be authorized (record not found)."}
    rec_auth = _get(record, "execution_allowed") is False
    aecp = _get(record, "apply_executor_evidence_collection_plan", {})
    plan_auth = _get(aecp, "execution_allowed") is True
    return {"name": "execution_not_authorized", "passed": rec_auth and not plan_auth,
            "severity": "critical", "detail": "Execution must not be authorized." if not (rec_auth and not plan_auth) else "Execution correctly not authorized."}


def _check_collection_plan_record_approved_intent(record: dict | None) -> dict:
    if record is None:
        return {"name": "collection_plan_record_approved_intent", "passed": False, "severity": "low",
                "detail": "Collection plan record status must be 'approved_collection_plan_intent' (record not found)."}
    passed = _get(record, "status") == "approved_collection_plan_intent"
    return {"name": "collection_plan_record_approved_intent", "passed": passed,
            "severity": "low", "detail": "Status must be 'approved_collection_plan_intent.'" if not passed else "Approved collection plan intent confirmed."}


def _check_collection_plan_record_persisted(record: dict | None) -> dict:
    if record is None:
        return {"name": "collection_plan_record_persisted", "passed": False, "severity": "low",
                "detail": "Collection plan record persisted flag must be True (record not found)."}
    passed = _get(record, "apply_executor_evidence_collection_plan_persisted") is True
    return {"name": "collection_plan_record_persisted", "passed": passed,
            "severity": "low", "detail": "Collection plan persisted flag must be True." if not passed else "Collection plan persisted confirmed."}


def _check_collection_plan_decision_ready(record: dict | None) -> dict:
    if record is None:
        return {"name": "collection_plan_decision_ready", "passed": False, "severity": "high",
                "detail": "Evidence collection plan decision must be 'evidence_collection_plan_ready' (record not found)."}
    passed = _get(record, "evidence_collection_plan_decision") == "evidence_collection_plan_ready"
    return {"name": "collection_plan_decision_ready", "passed": passed,
            "severity": "high", "detail": "Evidence collection plan decision must be 'evidence_collection_plan_ready.'" if not passed else "Evidence collection plan decision confirmed ready."}


def _check_collection_plan_review_completed(record: dict | None) -> dict:
    if record is None:
        return {"name": "collection_plan_review_completed", "passed": False, "severity": "low",
                "detail": "collection_plan_review_completed must be True (record not found)."}
    passed = _get(record, "evidence_collection_plan_review_completed") is True
    return {"name": "collection_plan_review_completed", "passed": passed,
            "severity": "low", "detail": "collection_plan_review_completed must be True." if not passed else "Plan review confirmed completed."}


def _check_collection_plan_intent_recorded(record: dict | None) -> dict:
    if record is None:
        return {"name": "collection_plan_intent_recorded", "passed": False, "severity": "low",
                "detail": "collection_plan_intent_recorded must be True (record not found)."}
    passed = _get(record, "evidence_collection_plan_intent_recorded") is True
    return {"name": "collection_plan_intent_recorded", "passed": passed,
            "severity": "low", "detail": "collection_plan_intent_recorded must be True." if not passed else "Plan intent confirmed recorded."}


def _check_confirmations_received(record: dict | None) -> dict:
    if record is None:
        return {"name": "confirmations_received", "passed": False, "severity": "medium",
                "detail": "confirmations_received must cover confirmations_required (record not found)."}
    required = _get(record, "confirmations_required", [])
    received = _get(record, "confirmations_received", [])
    if not required:
        return {"name": "confirmations_received", "passed": True, "severity": "medium",
                "detail": "No confirmations required, so check passes."}
    passed = set(required).issubset(set(received))
    return {"name": "confirmations_received", "passed": passed,
            "severity": "medium", "detail": "confirmations_received must cover all required confirmations." if not passed else "Confirmations coverage confirmed."}


def _check_nested_collection_plan_ready(record: dict | None) -> dict:
    if record is None:
        return {"name": "nested_collection_plan_ready", "passed": False, "severity": "high",
                "detail": "Nested collection plan decision must be 'evidence_collection_plan_ready' (record not found)."}
    aecp = _get(record, "apply_executor_evidence_collection_plan", {})
    passed = _get(aecp, "decision") == "evidence_collection_plan_ready"
    return {"name": "nested_collection_plan_ready", "passed": passed,
            "severity": "high", "detail": "Nested collection plan decision must be 'evidence_collection_plan_ready.'" if not passed else "Nested collection plan confirmed ready."}


def _check_planned_collection_steps_declared(record: dict | None) -> dict:
    if record is None:
        return {"name": "planned_collection_steps_declared", "passed": False, "severity": "medium",
                "detail": "planned_collection_steps must exist (record not found)."}
    aecp = _get(record, "apply_executor_evidence_collection_plan", {})
    steps = _get(aecp, "planned_collection_steps", [])
    passed = len(steps) >= 6
    return {"name": "planned_collection_steps_declared", "passed": passed,
            "severity": "medium", "detail": f"planned_collection_steps must have at least 6 items (got {len(steps)})." if not passed else f"Planned collection steps declared ({len(steps)} steps)."}


def _check_planned_evidence_items_declared(record: dict | None) -> dict:
    if record is None:
        return {"name": "planned_evidence_items_declared", "passed": False, "severity": "medium",
                "detail": "planned_evidence_items must exist (record not found)."}
    aecp = _get(record, "apply_executor_evidence_collection_plan", {})
    items = _get(aecp, "planned_evidence_items", [])
    passed = len(items) == 5
    return {"name": "planned_evidence_items_declared", "passed": passed,
            "severity": "medium", "detail": "planned_evidence_items must have exactly 5 items." if not passed else f"Planned evidence items declared ({len(items)} items)."}


def _check_collection_groups_declared(record: dict | None) -> dict:
    if record is None:
        return {"name": "collection_groups_declared", "passed": False, "severity": "medium",
                "detail": "Collection groups must exist (record not found)."}
    aecp = _get(record, "apply_executor_evidence_collection_plan", {})
    pre = len(_get(aecp, "pre_execution_collection_plan", []))
    dur = len(_get(aecp, "during_execution_collection_plan", []))
    post = len(_get(aecp, "post_execution_collection_plan", []))
    roll = len(_get(aecp, "rollback_collection_plan", []))
    audit = len(_get(aecp, "audit_collection_plan", []))
    passed = pre >= 4 and dur >= 3 and post >= 3 and roll >= 4 and audit >= 4
    return {"name": "collection_groups_declared", "passed": passed,
            "severity": "medium", "detail": "Collection groups must have minimum counts (pre>=4, during>=3, post>=3, rollback>=4, audit>=4)." if not passed else "Collection groups declared with sufficient counts."}


def _check_collection_constraints_declared(record: dict | None) -> dict:
    if record is None:
        return {"name": "collection_constraints_declared", "passed": False, "severity": "high",
                "detail": "collection_execution_constraints must exist (record not found)."}
    aecp = _get(record, "apply_executor_evidence_collection_plan", {})
    constraints = _get(aecp, "collection_execution_constraints", {})
    passed = _get(constraints, "contract_scope") == "contract_only_no_collection"
    return {"name": "collection_constraints_declared", "passed": passed,
            "severity": "high", "detail": "collection_execution_constraints must have contract_scope == 'contract_only_no_collection.'" if not passed else "Collection constraints declared correctly."}


def _check_collection_not_allowed_yet(record: dict | None) -> dict:
    if record is None:
        return {"name": "collection_not_allowed_yet", "passed": False, "severity": "critical",
                "detail": "Collection must not be allowed yet (record not found)."}
    aecp = _get(record, "apply_executor_evidence_collection_plan", {})
    constraints = _get(aecp, "collection_execution_constraints", {})
    passed = _get(constraints, "collection_allowed_now") is False
    return {"name": "collection_not_allowed_yet", "passed": passed,
            "severity": "critical", "detail": "Collection must not be allowed yet (collection_allowed_now must be False)." if not passed else "Collection correctly not allowed yet."}


def _check_collector_boundary_declares_no_collector(record: dict | None) -> dict:
    if record is None:
        return {"name": "collector_boundary_declares_no_collector", "passed": False, "severity": "critical",
                "detail": "Collector boundary must declare no collector (record not found)."}
    aecp = _get(record, "apply_executor_evidence_collection_plan", {})
    boundary = _get(aecp, "collector_boundary", {})
    passed = _get(boundary, "collector_exists") is False
    return {"name": "collector_boundary_declares_no_collector", "passed": passed,
            "severity": "critical", "detail": "Collector boundary must indicate collector_exists is False." if not passed else "Boundary correctly declares no collector."}


def _check_acceptance_plan_declared(record: dict | None) -> dict:
    if record is None:
        return {"name": "acceptance_plan_declared", "passed": False, "severity": "medium",
                "detail": "collection_acceptance_plan must exist (record not found)."}
    aecp = _get(record, "apply_executor_evidence_collection_plan", {})
    criteria = _get(aecp, "collection_acceptance_plan", [])
    passed = len(criteria) >= 5
    return {"name": "acceptance_plan_declared", "passed": passed,
            "severity": "medium", "detail": "collection_acceptance_plan must have at least 5 items." if not passed else f"Acceptance plan declared ({len(criteria)} items)."}


def _check_evidence_not_collected(record: dict | None) -> dict:
    if record is None:
        return {"name": "evidence_not_collected", "passed": False, "severity": "critical",
                "detail": "Evidence must not be collected (record not found)."}
    passed = _get(record, "evidence_collected") is False
    return {"name": "evidence_not_collected", "passed": passed,
            "severity": "critical", "detail": "evidence_collected must be False." if not passed else "Evidence correctly not collected."}


def _check_rollback_plan_not_attached(record: dict | None) -> dict:
    if record is None:
        return {"name": "rollback_plan_not_attached", "passed": False, "severity": "critical",
                "detail": "Rollback plan must not be attached (record not found)."}
    passed = _get(record, "rollback_plan_attached") is False
    return {"name": "rollback_plan_not_attached", "passed": passed,
            "severity": "critical", "detail": "rollback_plan_attached must be False." if not passed else "Rollback plan correctly not attached."}


def _check_requested_action_present(record: dict | None) -> dict:
    if record is None:
        return {"name": "requested_action_present", "passed": False, "severity": "medium",
                "detail": "requested_action must exist (record not found)."}
    aecp = _get(record, "apply_executor_evidence_collection_plan", {})
    ra = _get(aecp, "requested_action")
    passed = ra is not None and isinstance(ra, dict)
    return {"name": "requested_action_present", "passed": passed,
            "severity": "medium", "detail": "requested_action must exist and be a dict in collection plan." if not passed else "Requested action present."}


def _check_requested_action_type_allowed(record: dict | None) -> dict:
    if record is None:
        return {"name": "requested_action_type_allowed", "passed": False, "severity": "high",
                "detail": "Requested action type must be allowed (record not found)."}
    aecp = _get(record, "apply_executor_evidence_collection_plan", {})
    ra = _get(aecp, "requested_action", {})
    action_type = _get(ra, "action_type", "")
    passed = action_type in _ALLOWED_ACTION_TYPES
    return {"name": "requested_action_type_allowed", "passed": passed,
            "severity": "high", "detail": f"Requested action action_type must be one of {_ALLOWED_ACTION_TYPES}." if not passed else f"Requested action type ({action_type}) allowed."}


def _check_target_present(record: dict | None) -> dict:
    if record is None:
        return {"name": "target_present", "passed": False, "severity": "medium",
                "detail": "Requested action target must exist and be non-empty (record not found)."}
    aecp = _get(record, "apply_executor_evidence_collection_plan", {})
    ra = _get(aecp, "requested_action", {})
    target = _get(ra, "target", "")
    passed = isinstance(target, str) and target.strip() != ""
    return {"name": "target_present", "passed": passed,
            "severity": "medium", "detail": "Requested action target must exist and be a non-empty string." if not passed else "Target present."}


def _check_no_direct_collector_or_executor_command(record: dict | None) -> dict:
    if record is None:
        return {"name": "no_direct_collector_or_executor_command", "passed": False, "severity": "critical",
                "detail": "Requested action must not contain collector/executor keys (record not found)."}
    aecp = _get(record, "apply_executor_evidence_collection_plan", {})
    ra = _get(aecp, "requested_action", {})
    def check_dict(d):
        for key, value in d.items():
            if key in _DIRECTOR_EXECUTOR_KEYS:
                return True
            if isinstance(value, dict):
                if check_dict(value):
                    return True
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict) and check_dict(item):
                        return True
        return False
    found = check_dict(ra)
    passed = not found
    return {"name": "no_direct_collector_or_executor_command", "passed": passed,
            "severity": "critical", "detail": "Requested action must not contain direct collector/executor keys." if found else "No direct collector or executor present."}


def _check_all_execution_flags_blocked(record: dict | None) -> dict:
    if record is None:
        return {"name": "all_execution_flags_blocked", "passed": False, "severity": "high",
                "detail": "All execution flags must be False (record not found)."}
    flags = [
        "execution_allowed", "tool_execution_allowed", "dry_run_execution_allowed",
        "simulation_execution_allowed", "apply_gate_execution_allowed",
        "human_authorization_execution_allowed", "apply_execution_gate_execution_allowed",
        "apply_executor_contract_execution_allowed", "apply_executor_plan_execution_allowed",
        "apply_executor_evidence_contract_execution_allowed",
        "apply_executor_evidence_collection_plan_execution_allowed",
        "apply_executor_evidence_collection_plan_record_execution_allowed",
        "apply_executor_evidence_collector_contract_execution_allowed",
    ]
    rec_passed = all(_get(record, f) in (False, None) for f in flags)
    aecp = _get(record, "apply_executor_evidence_collection_plan", {})
    plan_passed = all(_get(aecp, f) in (False, None) for f in flags)
    passed = rec_passed and plan_passed
    return {"name": "all_execution_flags_blocked", "passed": passed,
            "severity": "high", "detail": "All execution flags must be False in record and collection plan." if not passed else "Execution flags correctly blocked."}


def _check_all_apply_flags_blocked(record: dict | None) -> dict:
    if record is None:
        return {"name": "all_apply_flags_blocked", "passed": False, "severity": "critical",
                "detail": "apply_allowed and rollback_allowed must be False (record not found)."}
    rec_pass = (_get(record, "apply_allowed") in (False, None)) and (_get(record, "rollback_allowed") in (False, None))
    aecp = _get(record, "apply_executor_evidence_collection_plan", {})
    plan_pass = (_get(aecp, "apply_allowed") in (False, None)) and (_get(aecp, "rollback_allowed") in (False, None))
    passed = rec_pass and plan_pass
    return {"name": "all_apply_flags_blocked", "passed": passed,
            "severity": "critical", "detail": "apply_allowed and rollback_allowed must be False in record and collection plan." if not passed else "Apply flags correctly blocked."}


def _check_previous_blocking_reasons_empty(record: dict | None) -> dict:
    if record is None:
        return {"name": "previous_blocking_reasons_empty", "passed": False, "severity": "medium",
                "detail": "blocking_reasons must be empty (record not found)."}
    aecp = _get(record, "apply_executor_evidence_collection_plan", {})
    passed = len(_get(aecp, "blocking_reasons", [])) == 0
    return {"name": "previous_blocking_reasons_empty", "passed": passed,
            "severity": "medium", "detail": "blocking_reasons must be empty." if not passed else "Blocking reasons confirmed empty."}


# --------------------------------------------------------------------------- #
# Main builder
# --------------------------------------------------------------------------- #

def build_apply_executor_evidence_collector_contract(
    apply_executor_evidence_collection_plan_record: dict | None,
    context: dict | None = None,
) -> dict:
    """Build an apply executor evidence collector contract from an approved collection plan record."""
    now_iso = datetime.now(_tz.utc).isoformat()

    # Rule 1: Missing record
    if apply_executor_evidence_collection_plan_record is None:
        return _build_blocked_collector_contract(
            context=context, reason="Apply executor evidence collection plan record was not found.",
            blocking_reasons=["Apply executor evidence collection plan record was not found."])

    # Basic validation
    record = apply_executor_evidence_collection_plan_record
    if _get(record, "status") != "approved_collection_plan_intent":
        return _build_blocked_collector_contract(context=context,
            reason="Record status is not approved_collection_plan_intent.",
            blocking_reasons=["Record status is not approved_collection_plan_intent."])
    if _get(record, "evidence_collection_plan_decision") != "evidence_collection_plan_ready":
        return _build_blocked_collector_contract(context=context,
            reason="Collection plan was not ready.",
            blocking_reasons=["Evidence collection plan decision is not evidence_collection_plan_ready."])
    if not _get(record, "evidence_collection_plan_intent_recorded"):
        return _build_blocked_collector_contract(context=context,
            reason="Collection plan intent has not been recorded.",
            blocking_reasons=["evidence_collection_plan_intent_recorded is not true."])
    if not _get(record, "evidence_collection_plan_review_completed"):
        return _build_blocked_collector_contract(context=context,
            reason="Collection plan review is not completed.",
            blocking_reasons=["evidence_collection_plan_review_completed is not true."])

    # Unsafe flags check
    unsafe = ["evidence_collected", "rollback_plan_attached", "apply_authorized",
              "apply_allowed", "execution_allowed", "tool_execution_allowed",
              "apply_executed", "rollback_executed"]
    for flag in unsafe:
        if _get(record, flag):
            return _build_blocked_collector_contract(context=context,
                reason=f"Unsafe flag '{flag}' is true.",
                blocking_reasons=[f"{flag} is true."])

    # Check nested plan exists
    aecp = _get(record, "apply_executor_evidence_collection_plan", {})
    if not isinstance(aecp, dict):
        return _build_not_ready_collector_contract(context=context,
            reason="Collection plan payload is missing or invalid.",
            unresolved_risks=[{"name": "missing_collection_plan_payload",
                               "severity": "high",
                               "detail": "Collection plan payload is missing or invalid."}])

    # Run checks
    checks = [
        _check_collection_plan_record_approved_intent(record),
        _check_collection_plan_record_persisted(record),
        _check_collection_plan_decision_ready(record),
        _check_collection_plan_review_completed(record),
        _check_collection_plan_intent_recorded(record),
        _check_confirmations_received(record),
        _check_nested_collection_plan_ready(record),
        _check_planned_collection_steps_declared(record),
        _check_planned_evidence_items_declared(record),
        _check_collection_groups_declared(record),
        _check_collection_constraints_declared(record),
        _check_collection_not_allowed_yet(record),
        _check_collector_boundary_declares_no_collector(record),
        _check_acceptance_plan_declared(record),
        _check_apply_not_authorized(record),
        _check_execution_not_authorized(record),
        _check_evidence_not_collected(record),
        _check_rollback_plan_not_attached(record),
        _check_requested_action_present(record),
        _check_requested_action_type_allowed(record),
        _check_target_present(record),
        _check_no_direct_collector_or_executor_command(record),
        _check_all_execution_flags_blocked(record),
        _check_all_apply_flags_blocked(record),
        _check_previous_blocking_reasons_empty(record),
    ]

    # Determine decision
    crit_failed = any(c["severity"] == "critical" and not c["passed"] for c in checks)
    high_failed = any(c["severity"] == "high" and not c["passed"] for c in checks)
    med_failed = any(c["severity"] == "medium" and not c["passed"] for c in checks)
    low_failed = any(c["severity"] == "low" and not c["passed"] for c in checks)

    if crit_failed or high_failed:
        decision = "blocked"
        required = False
        reason = "Critical or high severity checks failed."
        blocking = [c["detail"] for c in checks if not c["passed"] and c["severity"] in ["critical", "high"]]
    elif med_failed or low_failed:
        decision = "not_ready"
        required = False
        reason = "Medium or low severity checks failed."
        blocking = [c["detail"] for c in checks if not c["passed"] and c["severity"] in ["medium", "low"]]
    else:
        decision = "collector_contract_ready"
        required = True
        reason = "All checks passed; collector contract is ready."
        blocking = []

    if decision == "collector_contract_ready":
        statement = ("Apply executor evidence collector contract is prepared for future "
                     "collector implementation. This contract does not collect evidence, "
                     "authorize execution, or execute apply.")
    else:
        statement = None

    return {
        "collector_contract_type": "apply_executor_evidence_collector_contract",
        "collector_contract_required": required,
        "collector_contract_status": "prepared",
        "decision": decision,
        "reason": reason,
        "apply_executor_evidence_collection_plan_id": _get(record, "apply_executor_evidence_collection_plan_id"),
        "apply_executor_evidence_collection_plan_record_status": _get(record, "status"),
        "evidence_collection_plan_decision": _get(record, "evidence_collection_plan_decision"),
        "apply_executor_evidence_contract_id": _get(record, "apply_executor_evidence_contract_id"),
        "apply_executor_plan_id": _get(record, "apply_executor_plan_id"),
        "apply_executor_contract_id": _get(record, "apply_executor_contract_id"),
        "apply_execution_gate_id": _get(record, "apply_execution_gate_id"),
        "human_authorization_id": _get(record, "human_authorization_id"),
        "apply_gate_id": _get(record, "apply_gate_id"),
        "verification_verdict_id": _get(record, "verification_verdict_id"),
        "simulation_result_id": _get(record, "simulation_result_id"),
        "simulation_plan_id": _get(record, "simulation_plan_id"),
        "dry_run_id": _get(record, "dry_run_id"),
        "requested_action": _get(aecp, "requested_action"),
        "apply_executor_evidence_collection_plan_snapshot": dict(aecp) if aecp else None,
        "collector_contract_checks": checks,
        "collector_boundary": {"collector_exists": False, "collector_authorized": False,
                               "collector_execution_allowed": False, "collection_allowed_now": False,
                               "requires_future_collector_implementation": True,
                               "boundary_note": "No evidence collector exists or runs in this milestone."},
        "collector_permission_model": {"can_collect_evidence_now": False, "can_inspect_filesystem_now": False,
                                       "can_inspect_network_now": False, "can_query_database_now": False,
                                       "can_call_external_api_now": False, "can_execute_tools_now": False,
                                       "can_apply_changes_now": False, "can_rollback_now": False,
                                       "future_permissions_require_separate_authorization": True},
        "collector_input_requirements": [
            {"name": "approved_collection_plan_intent", "description": "Collection plan record approved"},
            {"name": "persisted_collection_plan_record", "description": "Persisted plan record"},
            {"name": "planned_evidence_items", "description": "Planned evidence items from plan"},
            {"name": "execution_constraints", "description": "Collection execution constraints"},
            {"name": "future_collector_authorization", "description": "Future explicit authorization required"},
        ],
        "collector_output_requirements": [
            {"name": "evidence_package_record", "description": "Package of collected evidence"},
            {"name": "pre_execution_evidence", "description": "Pre-execution state evidence"},
            {"name": "execution_result_evidence", "description": "Execution result evidence"},
            {"name": "post_execution_verification_evidence", "description": "Post-execution verification"},
            {"name": "rollback_evidence", "description": "Rollback-related evidence"},
            {"name": "audit_log_evidence", "description": "Audit log evidence"},
        ],
        "collector_forbidden_actions": ["shell", "subprocess", "raw_code_execution", "filesystem_scan",
                                        "network_probe", "database_query", "external_api_call",
                                        "identity_modification", "self_repair", "apply_execution",
                                        "rollback_execution", "evidence_collection_now"],
        "collector_allowed_future_actions": ["prepare_evidence_collection_request",
                                            "present_collector_contract_for_review",
                                            "persist_collector_contract_in_future_record_store"],
        "collector_execution_constraints": {"contract_scope": "contract_only_no_collection",
                                            "collection_allowed_now": False,
                                            "execution_allowed": False, "apply_allowed": False,
                                            "tool_execution_allowed": False,
                                            "requires_future_collector": True,
                                            "requires_future_collector_contract_record": True,
                                            "requires_future_human_authorization": True},
        "collector_acceptance_criteria": [{"criterion": "Contract reviewed by responsible party",
                                          "required": True, "satisfied_now": False},
                                         {"criterion": "Evidence collection methodology verified",
                                          "required": True, "satisfied_now": False},
                                         {"criterion": "Security boundaries defined",
                                          "required": True, "satisfied_now": False},
                                         {"criterion": "Audit logging requirements established",
                                          "required": True, "satisfied_now": False},
                                         {"criterion": "Future implementation path approved",
                                          "required": True, "satisfied_now": False}] if decision == "collector_contract_ready" else [],
        "required_collector_contract_confirmations": [
            "I confirm this collector contract does not collect evidence.",
            "I confirm this collector contract does not authorize apply.",
            "I confirm this collector contract does not authorize execution.",
            "I confirm no evidence collector exists in this milestone.",
            "I understand a future collector contract record milestone is required.",
            "I understand a separate future evidence collector milestone is required."
        ] if decision == "collector_contract_ready" else [],
        "collector_contract_statement": statement,
        "blocking_reasons": blocking,
        "unresolved_risks": [{"name": "missing_collection_plan_payload", "severity": "high",
                              "detail": "Collection plan payload is missing or invalid."}] if decision == "not_ready" else [],
        "recommended_next_step": ("Persist this collector contract in a future collector contract record "
                                 "milestone; do not execute any collection or apply operations." if decision == "collector_contract_ready"
                                 else "Resolve collector contract readiness issues before persisting contract." if decision == "not_ready"
                                 else "Resolve blocking conditions before proceeding."),
        "evidence_collection_plan_review_completed": _get(record, "evidence_collection_plan_review_completed", False),
        "evidence_collection_plan_intent_recorded": _get(record, "evidence_collection_plan_intent_recorded", False),
        "evidence_collected": False, "rollback_plan_attached": False, "apply_authorized": False,
        "apply_allowed": False, "rollback_allowed": False, "execution_allowed": False,
        "tool_execution_allowed": False, "dry_run_execution_allowed": False, "simulation_execution_allowed": False,
        "apply_gate_execution_allowed": False, "human_authorization_execution_allowed": False,
        "apply_execution_gate_execution_allowed": False, "apply_executor_contract_execution_allowed": False,
        "apply_executor_plan_execution_allowed": False, "apply_executor_evidence_contract_execution_allowed": False,
        "apply_executor_evidence_collection_plan_execution_allowed": False,
        "apply_executor_evidence_collection_plan_record_execution_allowed": False,
        "apply_executor_evidence_collector_contract_execution_allowed": False,
        "apply_executed": False, "rollback_executed": False,
        "metadata": {"source": "apply_executor_evidence_collector_contract_builder",
                     "schema_version": "1.0", "session_id": _get(context, "session_id") if context else None},
        "warnings": [
            "Apply executor evidence collector contract does not authorize execution.",
            "Apply executor evidence collector contract does not authorize apply.",
            "Evidence collection is not performed in this milestone.",
            "No evidence collector exists in this milestone.",
            "A separate future evidence collector is required before evidence can be collected.",
        ],
    }


def _build_blocked_collector_contract(context: dict | None, reason: str,
                                     blocking_reasons: list[str]) -> dict:
    return {
        "collector_contract_type": "apply_executor_evidence_collector_contract",
        "collector_contract_required": False, "collector_contract_status": "blocked",
        "decision": "blocked", "reason": reason,
        "apply_executor_evidence_collection_plan_id": None,
        "apply_executor_evidence_collection_plan_record_status": None,
        "evidence_collection_plan_decision": None,
        "apply_executor_evidence_contract_id": None, "apply_executor_plan_id": None,
        "apply_executor_contract_id": None, "apply_execution_gate_id": None,
        "human_authorization_id": None, "apply_gate_id": None, "verification_verdict_id": None,
        "simulation_result_id": None, "simulation_plan_id": None, "dry_run_id": None,
        "requested_action": None, "apply_executor_evidence_collection_plan_snapshot": None,
        "collector_contract_checks": [],
        "collector_boundary": {"collector_exists": False, "collector_authorized": False,
                               "collector_execution_allowed": False, "collection_allowed_now": False,
                               "requires_future_collector_implementation": True,
                               "boundary_note": "No evidence collector exists or runs in this milestone."},
        "collector_permission_model": {"can_collect_evidence_now": False, "can_inspect_filesystem_now": False,
                                       "can_inspect_network_now": False, "can_query_database_now": False,
                                       "can_call_external_api_now": False, "can_execute_tools_now": False,
                                       "can_apply_changes_now": False, "can_rollback_now": False,
                                       "future_permissions_require_separate_authorization": True},
        "collector_input_requirements": [], "collector_output_requirements": [],
        "collector_forbidden_actions": [], "collector_allowed_future_actions": [],
        "collector_execution_constraints": {"contract_scope": "contract_only_no_collection",
                                            "collection_allowed_now": False, "execution_allowed": False,
                                            "apply_allowed": False, "tool_execution_allowed": False,
                                            "requires_future_collector": True,
                                            "requires_future_collector_contract_record": True,
                                            "requires_future_human_authorization": True},
        "collector_acceptance_criteria": [], "required_collector_contract_confirmations": [],
        "collector_contract_statement": None,
        "blocking_reasons": blocking_reasons,
        "unresolved_risks": [{"name": "missing_collection_plan_payload", "severity": "high",
                              "detail": "Collection plan payload is missing or invalid."}],
        "recommended_next_step": "Resolve blocking conditions before proceeding.",
        "evidence_collection_plan_review_completed": False, "evidence_collection_plan_intent_recorded": False,
        "evidence_collected": False, "rollback_plan_attached": False, "apply_authorized": False,
        "apply_allowed": False, "rollback_allowed": False, "execution_allowed": False,
        "tool_execution_allowed": False, "dry_run_execution_allowed": False, "simulation_execution_allowed": False,
        "apply_gate_execution_allowed": False, "human_authorization_execution_allowed": False,
        "apply_execution_gate_execution_allowed": False, "apply_executor_contract_execution_allowed": False,
        "apply_executor_plan_execution_allowed": False, "apply_executor_evidence_contract_execution_allowed": False,
        "apply_executor_evidence_collection_plan_execution_allowed": False,
        "apply_executor_evidence_collection_plan_record_execution_allowed": False,
        "apply_executor_evidence_collector_contract_execution_allowed": False,
        "apply_executed": False, "rollback_executed": False,
        "metadata": {"source": "apply_executor_evidence_collector_contract_builder",
                     "schema_version": "1.0", "session_id": _get(context, "session_id") if context else None},
        "warnings": [],
    }


def _build_not_ready_collector_contract(context: dict | None, reason: str,
                                        unresolved_risks: list[dict]) -> dict:
    return {
        "collector_contract_type": "apply_executor_evidence_collector_contract",
        "collector_contract_required": False, "collector_contract_status": "not_ready",
        "decision": "not_ready", "reason": reason,
        "apply_executor_evidence_collection_plan_id": None,
        "apply_executor_evidence_collection_plan_record_status": None,
        "evidence_collection_plan_decision": None,
        "apply_executor_evidence_contract_id": None, "apply_executor_plan_id": None,
        "apply_executor_contract_id": None, "apply_execution_gate_id": None,
        "human_authorization_id": None, "apply_gate_id": None, "verification_verdict_id": None,
        "simulation_result_id": None, "simulation_plan_id": None, "dry_run_id": None,
        "requested_action": None, "apply_executor_evidence_collection_plan_snapshot": None,
        "collector_contract_checks": [],
        "collector_boundary": {"collector_exists": False, "collector_authorized": False,
                               "collector_execution_allowed": False, "collection_allowed_now": False,
                               "requires_future_collector_implementation": True,
                               "boundary_note": "No evidence collector exists or runs in this milestone."},
        "collector_permission_model": {"can_collect_evidence_now": False, "can_inspect_filesystem_now": False,
                                       "can_inspect_network_now": False, "can_query_database_now": False,
                                       "can_call_external_api_now": False, "can_execute_tools_now": False,
                                       "can_apply_changes_now": False, "can_rollback_now": False,
                                       "future_permissions_require_separate_authorization": True},
        "collector_input_requirements": [], "collector_output_requirements": [],
        "collector_forbidden_actions": [], "collector_allowed_future_actions": [],
        "collector_execution_constraints": {"contract_scope": "contract_only_no_collection",
                                            "collection_allowed_now": False, "execution_allowed": False,
                                            "apply_allowed": False, "tool_execution_allowed": False,
                                            "requires_future_collector": True,
                                            "requires_future_collector_contract_record": True,
                                            "requires_future_human_authorization": True},
        "collector_acceptance_criteria": [], "required_collector_contract_confirmations": [],
        "collector_contract_statement": None,
        "blocking_reasons": [], "unresolved_risks": unresolved_risks,
        "recommended_next_step": "Resolve readiness issues before proceeding.",
        "evidence_collection_plan_review_completed": False, "evidence_collection_plan_intent_recorded": False,
        "evidence_collected": False, "rollback_plan_attached": False, "apply_authorized": False,
        "apply_allowed": False, "rollback_allowed": False, "execution_allowed": False,
        "tool_execution_allowed": False, "dry_run_execution_allowed": False, "simulation_execution_allowed": False,
        "apply_gate_execution_allowed": False, "human_authorization_execution_allowed": False,
        "apply_execution_gate_execution_allowed": False, "apply_executor_contract_execution_allowed": False,
        "apply_executor_plan_execution_allowed": False, "apply_executor_evidence_contract_execution_allowed": False,
        "apply_executor_evidence_collection_plan_execution_allowed": False,
        "apply_executor_evidence_collection_plan_record_execution_allowed": False,
        "apply_executor_evidence_collector_contract_execution_allowed": False,
        "apply_executed": False, "rollback_executed": False,
        "metadata": {"source": "apply_executor_evidence_collector_contract_builder",
                     "schema_version": "1.0", "session_id": _get(context, "session_id") if context else None},
        "warnings": [],
    }
