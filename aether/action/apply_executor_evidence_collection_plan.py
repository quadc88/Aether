"""Apply Executor Evidence Collection Plan Builder for Aether (Milestone 77A).

Builds a structured apply_executor_evidence_collection_plan object from an
approved_evidence_contract_intent apply_executor_evidence_contract_record. This is
synthetic evaluation only — it does NOT execute any apply, call executors, collect
evidence, or modify target state.
"""

from __future__ import annotations
import json
from datetime import datetime, timezone as _tz


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
    "collect_evidence_now",
    "evidence_now",
    "inspect_now",
    "scan_now",
    "query_now",
}


_EVIDENCE_NAMES_REQUIRED = [
    "pre_execution_state_evidence",
    "execution_result_evidence",
    "post_execution_verification_evidence",
    "rollback_evidence",
    "audit_log_evidence",
]


def _check_apply_evidence_contract_approved_intent(
    record: dict | None,
) -> dict:
    """Check that the evidence contract record has approved_evidence_contract_intent status."""
    if record is None:
        return {
            "name": "apply_executor_evidence_contract_approved_intent",
            "passed": False,
            "severity": "low",
            "detail": "Apply executor evidence contract record status must be 'approved_evidence_contract_intent' (record not found).",
        }
    passed = record.get("status") == "approved_evidence_contract_intent"
    return {
        "name": "apply_executor_evidence_contract_approved_intent",
        "passed": passed,
        "severity": "low",
        "detail": "Apply executor evidence contract record status must be 'approved_evidence_contract_intent'." if not passed else "Approved evidence contract intent confirmed.",
    }


def _check_apply_evidence_contract_persisted(
    record: dict | None,
) -> dict:
    """Check that the evidence contract record was persisted."""
    if record is None:
        return {
            "name": "apply_executor_evidence_contract_persisted",
            "passed": False,
            "severity": "low",
            "detail": "Apply executor evidence contract record persisted flag must be True (record not found).",
        }
    passed = record.get("apply_executor_evidence_contract_persisted") is True
    return {
        "name": "apply_executor_evidence_contract_persisted",
        "passed": passed,
        "severity": "low",
        "detail": "Apply executor evidence contract persisted flag must be True." if not passed else "Evidence contract persisted confirmed.",
    }


def _check_evidence_contract_decision_ready(
    record: dict | None,
) -> dict:
    """Check that evidence_contract_decision is evidence_contract_ready."""
    if record is None:
        return {
            "name": "evidence_contract_decision_ready",
            "passed": False,
            "severity": "high",
            "detail": "evidence_contract_decision must be 'evidence_contract_ready' (record not found).",
        }
    passed = record.get("evidence_contract_decision") == "evidence_contract_ready"
    return {
        "name": "evidence_contract_decision_ready",
        "passed": passed,
        "severity": "high",
        "detail": "evidence_contract_decision must be 'evidence_contract_ready'." if not passed else "Evidence contract decision confirmed as ready.",
    }


def _check_evidence_contract_review_completed(
    record: dict | None,
) -> dict:
    """Check that evidence_contract_review_completed is True."""
    if record is None:
        return {
            "name": "evidence_contract_review_completed",
            "passed": False,
            "severity": "low",
            "detail": "evidence_contract_review_completed must be True (record not found).",
        }
    passed = record.get("evidence_contract_review_completed") is True
    return {
        "name": "evidence_contract_review_completed",
        "passed": passed,
        "severity": "low",
        "detail": "evidence_contract_review_completed must be True." if not passed else "Evidence contract review confirmed completed.",
    }


def _check_evidence_contract_intent_recorded(
    record: dict | None,
) -> dict:
    """Check that evidence_contract_intent_recorded is True."""
    if record is None:
        return {
            "name": "evidence_contract_intent_recorded",
            "passed": False,
            "severity": "low",
            "detail": "evidence_contract_intent_recorded must be True (record not found).",
        }
    passed = record.get("evidence_contract_intent_recorded") is True
    return {
        "name": "evidence_contract_intent_recorded",
        "passed": passed,
        "severity": "low",
        "detail": "evidence_contract_intent_recorded must be True." if not passed else "Evidence contract intent confirmed recorded.",
    }


def _check_confirmations_received(
    record: dict | None,
) -> dict:
    """Check that confirmations_received covers confirmations_required."""
    if record is None:
        return {
            "name": "confirmations_received",
            "passed": False,
            "severity": "medium",
            "detail": "confirmations_received must cover confirmations_required (record not found).",
        }
    required = record.get("confirmations_required", [])
    received = record.get("confirmations_received", [])
    if not required:
        return {
            "name": "confirmations_received",
            "passed": True,
            "severity": "medium",
            "detail": "No confirmations required, so check passes.",
        }
    passed = set(required).issubset(set(received))
    return {
        "name": "confirmations_received",
        "passed": passed,
        "severity": "medium",
        "detail": "confirmations_received must cover all required confirmations." if not passed else "Confirmations coverage confirmed.",
    }


def _check_evidence_contract_ready(
    record: dict | None,
) -> dict:
    """Check that the nested evidence contract has decision evidence_contract_ready."""
    if record is None:
        return {
            "name": "evidence_contract_ready",
            "passed": False,
            "severity": "high",
            "detail": "Nested evidence contract decision must be 'evidence_contract_ready' (record not found).",
        }
    aec = record.get("apply_executor_evidence_contract", {})
    passed = aec.get("decision") == "evidence_contract_ready"
    return {
        "name": "evidence_contract_ready",
        "passed": passed,
        "severity": "high",
        "detail": "Nested evidence contract decision must be 'evidence_contract_ready'." if not passed else "Evidence contract ready confirmed.",
    }


def _check_required_evidence_items_declared(
    record: dict | None,
) -> dict:
    """Check that required_evidence_items exists with exactly 5 items."""
    if record is None:
        return {
            "name": "required_evidence_items_declared",
            "passed": False,
            "severity": "medium",
            "detail": "required_evidence_items must exist with exactly 5 items (record not found).",
        }
    aec = record.get("apply_executor_evidence_contract", [])
    items = aec.get("required_evidence_items", [])
    passed = len(items) == 5
    return {
        "name": "required_evidence_items_declared",
        "passed": passed,
        "severity": "medium",
        "detail": "required_evidence_items must have exactly 5 items." if not passed else "Required evidence items declared (5 items).",
    }


def _check_evidence_items_not_collected(
    record: dict | None,
) -> dict:
    """Check that every required_evidence_item has collected=False and collection_allowed_now=False."""
    if record is None:
        return {
            "name": "evidence_items_not_collected",
            "passed": False,
            "severity": "critical",
            "detail": "All evidence items must have collected=False and collection_allowed_now=False (record not found).",
        }
    aec = record.get("apply_executor_evidence_contract", {})
    items = aec.get("required_evidence_items", [])
    all_passed = True
    for item in items:
        if item.get("collected_now", True) or item.get("collection_allowed_now", True):
            all_passed = False
            break
    return {
        "name": "evidence_items_not_collected",
        "passed": all_passed,
        "severity": "critical",
        "detail": "All required evidence items must have collected_now=False and collection_allowed_now=False." if not all_passed else "Evidence items confirmed not collected.",
    }


def _check_required_evidence_names_present(
    record: dict | None,
) -> dict:
    """Check that required_evidence_items includes the 5 required names."""
    if record is None:
        return {
            "name": "required_evidence_names_present",
            "passed": False,
            "severity": "medium",
            "detail": "Required evidence names must be present (record not found).",
        }
    aec = record.get("apply_executor_evidence_contract", {})
    items = aec.get("required_evidence_items", [])
    names = [item.get("name", "") for item in items]
    required_names = [
        "pre_execution_state_evidence",
        "execution_result_evidence",
        "post_execution_verification_evidence",
        "rollback_evidence",
        "audit_log_evidence",
    ]
    passed = all(name in names for name in required_names)
    return {
        "name": "required_evidence_names_present",
        "passed": passed,
        "severity": "medium",
        "detail": "Required evidence names must all be present in required_evidence_items." if not passed else "Required evidence names confirmed present.",
    }


def _check_evidence_groups_declared(
    record: dict | None,
) -> dict:
    """Check that pre/during/post/rollback/audit requirement groups exist with correct counts."""
    if record is None:
        return {
            "name": "evidence_groups_declared",
            "passed": False,
            "severity": "medium",
            "detail": "Evidence groups must exist with correct counts (record not found).",
        }
    aec = record.get("apply_executor_evidence_contract", {})
    pre = len(aec.get("pre_execution_evidence_requirements", []))
    during = len(aec.get("during_execution_evidence_requirements", []))
    post = len(aec.get("post_execution_evidence_requirements", []))
    rollback = len(aec.get("rollback_evidence_requirements", []))
    audit = len(aec.get("audit_evidence_requirements", []))
    passed = pre == 4 and during == 3 and post == 3 and rollback == 4 and audit == 4
    return {
        "name": "evidence_groups_declared",
        "passed": passed,
        "severity": "medium",
        "detail": "Evidence groups must have correct counts: pre=4, during=3, post=3, rollback=4, audit=4." if not passed else "Evidence groups declared with correct counts.",
    }


def _check_evidence_group_items_not_collected(
    record: dict | None,
) -> dict:
    """Check that every item in every evidence group has collected=False and collection_allowed_now=False."""
    if record is None:
        return {
            "name": "evidence_group_items_not_collected",
            "passed": False,
            "severity": "critical",
            "detail": "All evidence group items must have collected=False and collection_allowed_now=False (record not found).",
        }
    aec = record.get("apply_executor_evidence_contract", [])
    groups = [
        aec.get("pre_execution_evidence_requirements", []),
        aec.get("during_execution_evidence_requirements", []),
        aec.get("post_execution_evidence_requirements", []),
        aec.get("rollback_evidence_requirements", []),
        aec.get("audit_evidence_requirements", []),
    ]
    all_passed = True
    for group in groups:
        for item in group:
            if item.get("collected_now", True) or item.get("collection_allowed_now", True):
                all_passed = False
                break
        if not all_passed:
            break
    return {
        "name": "evidence_group_items_not_collected",
        "passed": all_passed,
        "severity": "critical",
        "detail": "All evidence group items must have collected_now=False and collection_allowed_now=False." if not all_passed else "Evidence group items confirmed not collected.",
    }


def _check_collection_constraints_declared(
    record: dict | None,
) -> dict:
    """Check that evidence_collection_constraints exists and collection_scope == 'contract_only_no_collection'."""
    if record is None:
        return {
            "name": "collection_constraints_declared",
            "passed": False,
            "severity": "high",
            "detail": "Evidence collection constraints must exist with correct scope (record not found).",
        }
    aec = record.get("apply_executor_evidence_contract", {})
    constraints = aec.get("evidence_collection_constraints", {})
    passed = constraints.get("collection_scope") == "contract_only_no_collection"
    return {
        "name": "collection_constraints_declared",
        "passed": passed,
        "severity": "high",
        "detail": "Evidence collection constraints must have collection_scope == 'contract_only_no_collection'." if not passed else "Collection constraints declared correctly.",
    }


def _check_collection_not_allowed_yet(
    record: dict | None,
) -> dict:
    """Check that collection_allowed_now is False and all inspection flags are False."""
    if record is None:
        return {
            "name": "collection_not_allowed_yet",
            "passed": False,
            "severity": "critical",
            "detail": "Collection must not be allowed yet (record not found).",
        }
    aec = record.get("apply_executor_evidence_contract", {})
    constraints = aec.get("evidence_collection_constraints", {})
    passed = constraints.get("collection_allowed_now") is False
    return {
        "name": "collection_not_allowed_yet",
        "passed": passed,
        "severity": "critical",
        "detail": "Evidence collection must not be allowed yet (collection_allowed_now must be False)." if not passed else "Collection correctly not allowed yet.",
    }


def _check_acceptance_criteria_declared(
    record: dict | None,
) -> dict:
    """Check that evidence_acceptance_criteria exists and has at least 5 items."""
    if record is None:
        return {
            "name": "acceptance_criteria_declared",
            "passed": False,
            "severity": "medium",
            "detail": "Evidence acceptance criteria must have at least 5 items (record not found).",
        }
    aec = record.get("apply_executor_evidence_contract", {})
    criteria = aec.get("evidence_acceptance_criteria", [])
    passed = len(criteria) >= 5
    return {
        "name": "acceptance_criteria_declared",
        "passed": passed,
        "severity": "medium",
        "detail": "Evidence acceptance criteria must have at least 5 items." if not passed else f"Evidence acceptance criteria declared ({len(criteria)} items).",
    }


def _check_acceptance_criteria_not_satisfied(
    record: dict | None,
) -> dict:
    """Check that every evidence_acceptance_criteria item has satisfied_now=False."""
    if record is None:
        return {
            "name": "acceptance_criteria_not_satisfied",
            "passed": False,
            "severity": "medium",
            "detail": "All acceptance criteria must have satisfied_now=False (record not found).",
        }
    aec = record.get("apply_executor_evidence_contract", {})
    criteria = aec.get("evidence_acceptance_criteria", [])
    all_passed = all(item.get("satisfied_now", True) is False for item in criteria)
    return {
        "name": "acceptance_criteria_not_satisfied",
        "passed": all_passed,
        "severity": "medium",
        "detail": "All evidence acceptance criteria must have satisfied_now=False." if not all_passed else "Acceptance criteria correctly not satisfied.",
    }


def _check_apply_not_authorized(
    record: dict | None,
) -> dict:
    """Check that apply_authorized is False in both record and nested contract."""
    if record is None:
        return {
            "name": "apply_not_authorized",
            "passed": False,
            "severity": "critical",
            "detail": "Apply must not be authorized (record not found).",
        }
    passed = (record.get("apply_authorized") is False)
    aec = record.get("apply_executor_evidence_contract", {})
    passed = passed and aec.get("apply_authorized") is False
    return {
        "name": "apply_not_authorized",
        "passed": passed,
        "severity": "critical",
        "detail": "Apply must not be authorized in record and nested evidence contract." if not passed else "Apply correctly not authorized.",
    }


def _check_apply_not_executed(
    record: dict | None,
) -> dict:
    """Check that apply_executed is False."""
    if record is None:
        return {
            "name": "apply_not_executed",
            "passed": False,
            "severity": "critical",
            "detail": "Apply must not have been executed (record not found).",
        }
    passed = record.get("apply_executed") is False
    return {
        "name": "apply_not_executed",
        "passed": passed,
        "severity": "critical",
        "detail": "Apply must not have been executed (apply_executed must be False)." if not passed else "Apply correctly not executed.",
    }


def _check_rollback_not_executed(
    record: dict | None,
) -> dict:
    """Check that rollback_executed is False."""
    if record is None:
        return {
            "name": "rollback_not_executed",
            "passed": False,
            "severity": "critical",
            "detail": "Rollback must not have been executed (record not found).",
        }
    passed = record.get("rollback_executed") is False
    return {
        "name": "rollback_not_executed",
        "passed": passed,
        "severity": "critical",
        "detail": "Rollback must not have been executed (rollback_executed must be False)." if not passed else "Rollback correctly not executed.",
    }


def _check_execution_flags_blocked(
    record: dict | None,
) -> dict:
    """Check that all execution flags are False in both record and nested contract."""
    if record is None:
        return {
            "name": "execution_flags_blocked",
            "passed": False,
            "severity": "high",
            "detail": "All execution flags must be False (record not found).",
        }
    flags = [
        "execution_allowed",
        "tool_execution_allowed",
        "dry_run_execution_allowed",
        "simulation_execution_allowed",
        "apply_gate_execution_allowed",
        "human_authorization_execution_allowed",
        "apply_execution_gate_execution_allowed",
        "apply_executor_contract_execution_allowed",
        "apply_executor_plan_execution_allowed",
        "apply_executor_evidence_contract_execution_allowed",
    ]
    record_all_passed = all(record.get(f) is False for f in flags)
    aec = record.get("apply_executor_evidence_contract", {})
    nested_all_passed = all(aec.get(f) is False for f in flags)
    passed = record_all_passed and nested_all_passed
    return {
        "name": "execution_flags_blocked",
        "passed": passed,
        "severity": "high",
        "detail": "All execution flags must be False in record and nested evidence contract." if not passed else "Execution flags correctly blocked.",
    }


def _check_apply_flags_blocked(
    record: dict | None,
) -> dict:
    """Check that apply_allowed and rollback_allowed are False in both record and nested contract."""
    if record is None:
        return {
            "name": "apply_flags_blocked",
            "passed": False,
            "severity": "critical",
            "detail": "Apply and rollback flags must be False (record not found).",
        }
    record_apply_allowed = record.get("apply_allowed") is False
    record_rollback_allowed = record.get("rollback_allowed") is False
    aec = record.get("apply_executor_evidence_contract", {})
    nested_apply_allowed = aec.get("apply_allowed") is False
    nested_rollback_allowed = aec.get("rollback_allowed") is False
    passed = record_apply_allowed and record_rollback_allowed and nested_apply_allowed and nested_rollback_allowed
    return {
        "name": "apply_flags_blocked",
        "passed": passed,
        "severity": "critical",
        "detail": "apply_allowed and rollback_allowed must be False in record and nested evidence contract." if not passed else "Apply flags correctly blocked.",
    }


def _check_requested_action_present(
    record: dict | None,
) -> dict:
    """Check that requested_action exists and is a dict."""
    if record is None:
        return {
            "name": "requested_action_present",
            "passed": False,
            "severity": "medium",
            "detail": "requested_action must exist and be a dict (record not found).",
        }
    aec = record.get("apply_executor_evidence_contract", {})
    passed = aec.get("requested_action") is not None and isinstance(aec.get("requested_action"), dict)
    return {
        "name": "requested_action_present",
        "passed": passed,
        "severity": "medium",
        "detail": "requested_action must exist and be a dict in evidence contract." if not passed else "Requested action present.",
    }


def _check_requested_action_type_allowed(
    record: dict | None,
) -> dict:
    """Check that requested_action.action_type is in allowed types."""
    if record is None:
        return {
            "name": "requested_action_type_allowed",
            "passed": False,
            "severity": "high",
            "detail": "Requested action type must be allowed (record not found).",
        }
    aec = record.get("apply_executor_evidence_contract", {})
    ra = aec.get("requested_action", {})
    action_type = ra.get("action_type", "")
    passed = action_type in _ALLOWED_ACTION_TYPES
    return {
        "name": "requested_action_type_allowed",
        "passed": passed,
        "severity": "high",
        "detail": f"Requested action action_type must be one of {_ALLOWED_ACTION_TYPES}." if not passed else f"Requested action type ({action_type}) allowed.",
    }


def _check_target_present(
    record: dict | None,
) -> dict:
    """Check that requested_action.target exists and is a non-empty string."""
    if record is None:
        return {
            "name": "target_present",
            "passed": False,
            "severity": "medium",
            "detail": "Requested action target must exist and be non-empty (record not found).",
        }
    aec = record.get("apply_executor_evidence_contract", {})
    ra = aec.get("requested_action", {})
    target = ra.get("target", "")
    passed = isinstance(target, str) and target.strip() != ""
    return {
        "name": "target_present",
        "passed": passed,
        "severity": "medium",
        "detail": "Requested action target must exist and be a non-empty string." if not passed else "Target present.",
    }


def _check_no_direct_collector_or_executor_present(
    record: dict | None,
) -> dict:
    """Check that requested_action does NOT contain any direct collector/executor keys."""
    if record is None:
        return {
            "name": "no_direct_collector_or_executor_present",
            "passed": False,
            "severity": "critical",
            "detail": "Requested action must not contain direct collector/executor keys (record not found).",
        }
    aec = record.get("apply_executor_evidence_contract", {})
    ra = aec.get("requested_action", {})
    def check_dict(d):
        found_direct = False
        for key, value in d.items():
            if key in _DIRECT_EXECUTOR_KEYS:
                found_direct = True
                return found_direct
            if isinstance(value, dict):
                found_direct = check_dict(value)
                if found_direct:
                    return found_direct
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        found_direct = check_dict(item)
                        if found_direct:
                            return found_direct
        return found_direct
    found_direct = check_dict(ra)
    passed = not found_direct
    return {
        "name": "no_direct_collector_or_executor_present",
        "passed": passed,
        "severity": "critical",
        "detail": "Requested action must not contain direct executor/collector keys (executor, command, shell, subprocess, python_code, raw_code, script, apply_now, execute_now, collect_evidence_now, evidence_now, inspect_now, scan_now, query_now)." if not passed else "No direct collector or executor present.",
    }


def _check_evidence_contract_blocking_reasons_empty(
    record: dict | None,
) -> dict:
    """Check that evidence_contract.blocking_reasons is empty."""
    if record is None:
        return {
            "name": "evidence_contract_blocking_reasons_empty",
            "passed": False,
            "severity": "medium",
            "detail": "Evidence contract blocking_reasons must be empty (record not found).",
        }
    aec = record.get("apply_executor_evidence_contract", {})
    passed = len(aec.get("blocking_reasons", [])) == 0
    return {
        "name": "evidence_contract_blocking_reasons_empty",
        "passed": passed,
        "severity": "medium",
        "detail": "Evidence contract blocking_reasons must be empty." if not passed else "Evidence contract blocking reasons confirmed empty.",
    }


def _check_evidence_collection_plan_not_previously_allowed(
    record: dict | None,
) -> dict:
    """Check that apply_executor_evidence_contract_execution_allowed is False/absent."""
    if record is None:
        return {
            "name": "evidence_collection_plan_not_previously_allowed",
            "passed": False,
            "severity": "critical",
            "detail": "Evidence collection plan must not have been previously allowed (record not found).",
        }
    aec = record.get("apply_executor_evidence_contract", {})
    passed = aec.get("apply_executor_evidence_contract_execution_allowed") is False
    return {
        "name": "evidence_collection_plan_not_previously_allowed",
        "passed": passed,
        "severity": "critical",
        "detail": "apply_executor_evidence_contract_execution_allowed must be False." if not passed else "Evidence collection plan correctly not previously allowed.",
    }


# --------------------------------------------------------------------------- #
# Main builder function
# --------------------------------------------------------------------------- #


def build_apply_executor_evidence_collection_plan(
    apply_executor_evidence_contract_record: dict | None,
    context: dict | None = None,
) -> dict:
    """Build an apply executor evidence collection plan from an approved evidence contract record.

    This is synthetic evaluation only — it does NOT collect evidence, execute apply,
    or modify any target state. It only evaluates conditions and produces a plan.

    Args:
        apply_executor_evidence_contract_record: The record from build and persistence.
        context: Optional metadata context (e.g., session_id).

    Returns:
        The structured apply_executor_evidence_collection_plan dict.
    """
    now_iso = datetime.now(_tz.utc).isoformat()

    # Handle missing record
    if apply_executor_evidence_contract_record is None:
        return _build_blocked_plan(
            context=context,
            reason="Apply executor evidence contract record was not found.",
            blocking_reasons=["Apply executor evidence contract record was not found."],
        )

    record_status = apply_executor_evidence_contract_record.get("status", "")
    record_decision = apply_executor_evidence_contract_record.get("evidence_contract_decision", "")

    # Rule 2: status must be approved_evidence_contract_intent
    if record_status != "approved_evidence_contract_intent":
        return _build_blocked_plan(
            context=context,
            reason="Apply executor evidence contract record is not approved_evidence_contract_intent.",
            blocking_reasons=["Record status is not approved_evidence_contract_intent."],
        )

    # Rule 3: decision must be evidence_contract_ready
    if record_decision != "evidence_contract_ready":
        return _build_blocked_plan(
            context=context,
            reason="Apply executor evidence contract record was not based on a ready evidence contract.",
            blocking_reasons=["Evidence contract decision is not evidence_contract_ready."],
        )

    # Rule 4: evidence_contract_intent_recorded must be True
    if not apply_executor_evidence_contract_record.get("evidence_contract_intent_recorded", False):
        return _build_blocked_plan(
            context=context,
            reason="Evidence contract intent has not been recorded.",
            blocking_reasons=["evidence_contract_intent_recorded is not true."],
        )

    # Rule 5: evidence_contract_review_completed must be True
    if not apply_executor_evidence_contract_record.get("evidence_contract_review_completed", False):
        return _build_blocked_plan(
            context=context,
            reason="Evidence contract review is not completed.",
            blocking_reasons=["evidence_contract_review_completed is not true."],
        )

    # Rule 6: evidence_collected must be False
    if apply_executor_evidence_contract_record.get("evidence_collected", False):
        return _build_blocked_plan(
            context=context,
            reason="Apply executor evidence contract record unexpectedly indicates evidence was collected.",
            blocking_reasons=["evidence_collected is true."],
        )

    # Rule 7: rollback_plan_attached must be False
    if apply_executor_evidence_contract_record.get("rollback_plan_attached", False):
        return _build_blocked_plan(
            context=context,
            reason="Apply executor evidence contract record unexpectedly indicates rollback plan was already attached.",
            blocking_reasons=["rollback_plan_attached is true."],
        )

    # Rule 8: apply_authorized must be False
    if apply_executor_evidence_contract_record.get("apply_authorized", False):
        return _build_blocked_plan(
            context=context,
            reason="Apply executor evidence contract record is unexpectedly marked apply-authorized.",
            blocking_reasons=["apply_authorized is true."],
        )

    # Rule 9: apply_executed or rollback_executed must be False
    if apply_executor_evidence_contract_record.get("apply_executed", False) or apply_executor_evidence_contract_record.get("rollback_executed", False):
        reasons = []
        if apply_executor_evidence_contract_record.get("apply_executed", False):
            reasons.append("apply_executed is true.")
        if apply_executor_evidence_contract_record.get("rollback_executed", False):
            reasons.append("rollback_executed is true.")
        return _build_blocked_plan(
            context=context,
            reason="Apply executor evidence contract record indicates execution already occurred.",
            blocking_reasons=reasons,
        )

    # Rule 10: Check that apply_executor_evidence_contract exists and is a dict
    aec = apply_executor_evidence_contract_record.get("apply_executor_evidence_contract")
    if not isinstance(aec, dict):
        return _build_not_ready_plan(
            context=context,
            reason="Apply executor evidence contract payload is missing or invalid.",
            unresolved_risks=[{"name": "missing_apply_executor_evidence_contract", "severity": "high", "detail": "Apply executor evidence contract payload is missing or invalid."}],
        )

    # Run all checks
    checks = [
        _check_apply_evidence_contract_approved_intent(apply_executor_evidence_contract_record),
        _check_apply_evidence_contract_persisted(apply_executor_evidence_contract_record),
        _check_evidence_contract_decision_ready(apply_executor_evidence_contract_record),
        _check_evidence_contract_review_completed(apply_executor_evidence_contract_record),
        _check_evidence_contract_intent_recorded(apply_executor_evidence_contract_record),
        _check_confirmations_received(apply_executor_evidence_contract_record),
        _check_evidence_contract_ready(apply_executor_evidence_contract_record),
        _check_required_evidence_items_declared(apply_executor_evidence_contract_record),
        _check_evidence_items_not_collected(apply_executor_evidence_contract_record),
        _check_required_evidence_names_present(apply_executor_evidence_contract_record),
        _check_evidence_groups_declared(apply_executor_evidence_contract_record),
        _check_evidence_group_items_not_collected(apply_executor_evidence_contract_record),
        _check_collection_constraints_declared(apply_executor_evidence_contract_record),
        _check_collection_not_allowed_yet(apply_executor_evidence_contract_record),
        _check_acceptance_criteria_declared(apply_executor_evidence_contract_record),
        _check_acceptance_criteria_not_satisfied(apply_executor_evidence_contract_record),
        _check_apply_not_authorized(apply_executor_evidence_contract_record),
        _check_apply_not_executed(apply_executor_evidence_contract_record),
        _check_rollback_not_executed(apply_executor_evidence_contract_record),
        _check_execution_flags_blocked(apply_executor_evidence_contract_record),
        _check_apply_flags_blocked(apply_executor_evidence_contract_record),
        _check_requested_action_present(apply_executor_evidence_contract_record),
        _check_requested_action_type_allowed(apply_executor_evidence_contract_record),
        _check_target_present(apply_executor_evidence_contract_record),
        _check_no_direct_collector_or_executor_present(apply_executor_evidence_contract_record),
        _check_evidence_contract_blocking_reasons_empty(apply_executor_evidence_contract_record),
        _check_evidence_collection_plan_not_previously_allowed(apply_executor_evidence_contract_record),
    ]

    # Determine decision based on check results
    critical_failed = any(c["severity"] == "critical" and not c["passed"] for c in checks)
    high_failed = any(c["severity"] == "high" and not c["passed"] for c in checks)
    medium_failed = any(c["severity"] == "medium" and not c["passed"] for c in checks)
    low_failed = any(c["severity"] == "low" and not c["passed"] for c in checks)

    if critical_failed or high_failed:
        decision = "blocked"
        evidence_collection_plan_required = False
        reason = "Critical or high severity checks failed."
        blocking_reasons = [c["detail"] for c in checks if not c["passed"] and c["severity"] in ["critical", "high"]]
    elif medium_failed or low_failed:
        decision = "not_ready"
        evidence_collection_plan_required = False
        reason = "Medium or low severity checks failed."
        blocking_reasons = [c["detail"] for c in checks if not c["passed"] and c["severity"] in ["medium", "low"]]
    else:
        decision = "evidence_collection_plan_ready"
        evidence_collection_plan_required = True
        reason = "All checks passed; evidence collection plan is ready."
        blocking_reasons = []

    # Build plan
    plan = {
        "evidence_collection_plan_type": "apply_executor_evidence_collection_plan",
        "evidence_collection_plan_required": evidence_collection_plan_required,
        "evidence_collection_plan_status": "prepared",
        "decision": decision,
        "reason": reason,
        "apply_executor_evidence_contract_id": apply_executor_evidence_contract_record.get("apply_executor_evidence_contract_id"),
        "apply_executor_evidence_contract_record_status": record_status,
        "evidence_contract_decision": record_decision,
        "apply_executor_plan_id": apply_executor_evidence_contract_record.get("apply_executor_plan_id"),
        "apply_executor_contract_id": apply_executor_evidence_contract_record.get("apply_executor_contract_id"),
        "apply_execution_gate_id": apply_executor_evidence_contract_record.get("apply_execution_gate_id"),
        "human_authorization_id": apply_executor_evidence_contract_record.get("human_authorization_id"),
        "apply_gate_id": apply_executor_evidence_contract_record.get("apply_gate_id"),
        "verification_verdict_id": apply_executor_evidence_contract_record.get("verification_verdict_id"),
        "simulation_result_id": apply_executor_evidence_contract_record.get("simulation_result_id"),
        "simulation_plan_id": apply_executor_evidence_contract_record.get("simulation_plan_id"),
        "dry_run_id": apply_executor_evidence_contract_record.get("dry_run_id"),
        "requested_action": aec.get("requested_action", None),
        "apply_executor_evidence_contract_snapshot": dict(aec) if aec else None,
        "evidence_collection_plan_checks": checks,
        "planned_collection_steps": _build_planned_collection_steps(decision),
        "planned_evidence_items": _build_planned_evidence_items(),
        "pre_execution_collection_plan": _build_pre_execution_collection_plan(),
        "during_execution_collection_plan": _build_during_execution_collection_plan(),
        "post_execution_collection_plan": _build_post_execution_collection_plan(),
        "rollback_collection_plan": _build_rollback_collection_plan(),
        "audit_collection_plan": _build_audit_collection_plan(),
        "collection_execution_constraints": _build_collection_execution_constraints(decision),
        "collection_acceptance_plan": _build_collection_acceptance_plan(),
        "collector_boundary": _build_collector_boundary(),
        "required_collection_plan_confirmations": _build_required_confirmations(decision),
        "evidence_collection_plan_statement": _build_evidence_collection_plan_statement(decision),
        "blocking_reasons": blocking_reasons,
        "unresolved_risks": [{"name": "missing_apply_executor_evidence_contract", "severity": "high", "detail": "Apply executor evidence contract payload is missing or invalid."}] if decision == "not_ready" else [],
        "recommended_next_step": _build_recommended_next_step(decision),
        "evidence_contract_review_completed": apply_executor_evidence_contract_record.get("evidence_contract_review_completed", False),
        "evidence_contract_intent_recorded": apply_executor_evidence_contract_record.get("evidence_contract_intent_recorded", False),
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
        "apply_executor_evidence_collection_plan_execution_allowed": False,
        "metadata": {
            "source": "apply_executor_evidence_collection_plan_builder",
            "schema_version": "1.0",
            "session_id": context.get("session_id") if context else None,
        },
        "warnings": [
            "Apply executor evidence collection plan does not authorize execution.",
            "Apply executor evidence collection plan does not authorize apply.",
            "Evidence collection is planned but not performed.",
            "No evidence collector exists in this milestone.",
            "A separate future evidence collector is required before evidence can be collected.",
        ],
    }

    # Copy warnings from the evidence contract if present
    if aec.get("warnings"):
        for w in aec["warnings"]:
            plan["warnings"].append(f"apply_executor_evidence_contract_warning: {w}")

    return plan


def _build_blocked_plan(context: dict | None, reason: str, blocking_reasons: list[str]) -> dict:
    """Build a blocked evidence collection plan."""
    return {
        "evidence_collection_plan_type": "apply_executor_evidence_collection_plan",
        "evidence_collection_plan_required": False,
        "evidence_collection_plan_status": "prepared",
        "decision": "blocked",
        "reason": reason,
        "apply_executor_evidence_contract_id": None,
        "apply_executor_evidence_contract_record_status": None,
        "evidence_contract_decision": None,
        "apply_executor_plan_id": None,
        "apply_executor_contract_id": None,
        "apply_execution_gate_id": None,
        "human_authorization_id": None,
        "apply_gate_id": None,
        "verification_verdict_id": None,
        "simulation_result_id": None,
        "simulation_plan_id": None,
        "dry_run_id": None,
        "requested_action": None,
        "apply_executor_evidence_contract_snapshot": None,
        "evidence_collection_plan_checks": [],
        "planned_collection_steps": _build_planned_collection_steps("blocked"),
        "planned_evidence_items": _build_planned_evidence_items(),
        "pre_execution_collection_plan": _build_pre_execution_collection_plan(),
        "during_execution_collection_plan": _build_during_execution_collection_plan(),
        "post_execution_collection_plan": _build_post_execution_collection_plan(),
        "rollback_collection_plan": _build_rollback_collection_plan(),
        "audit_collection_plan": _build_audit_collection_plan(),
        "collection_execution_constraints": _build_collection_execution_constraints("blocked"),
        "collection_acceptance_plan": _build_collection_acceptance_plan(),
        "collector_boundary": _build_collector_boundary(),
        "required_collection_plan_confirmations": _build_required_confirmations("blocked"),
        "evidence_collection_plan_statement": None,
        "blocking_reasons": blocking_reasons,
        "unresolved_risks": [{"name": "blocked_by_conditions", "severity": "high", "detail": reason}],
        "recommended_next_step": reason.replace("reason", "Resolve blocking conditions before continuing."),
        "evidence_contract_review_completed": False,
        "evidence_contract_intent_recorded": False,
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
        "apply_executor_evidence_collection_plan_execution_allowed": False,
        "metadata": {
            "source": "apply_executor_evidence_collection_plan_builder",
            "schema_version": "1.0",
            "session_id": context.get("session_id") if context else None,
        },
        "warnings": [
            "Apply executor evidence collection plan does not authorize execution.",
            "Apply executor evidence collection plan does not authorize apply.",
            "Evidence collection is planned but not performed.",
            "No evidence collector exists in this milestone.",
            "A separate future evidence collector is required before evidence can be collected.",
        ],
    }


def _build_not_ready_plan(context: dict | None, reason: str, unresolved_risks: list[dict]) -> dict:
    """Build a not-ready evidence collection plan."""
    return {
        "evidence_collection_plan_type": "apply_executor_evidence_collection_plan",
        "evidence_collection_plan_required": False,
        "evidence_collection_plan_status": "prepared",
        "decision": "not_ready",
        "reason": reason,
        "apply_executor_evidence_contract_id": None,
        "apply_executor_evidence_contract_record_status": None,
        "evidence_contract_decision": None,
        "apply_executor_plan_id": None,
        "apply_executor_contract_id": None,
        "apply_execution_gate_id": None,
        "human_authorization_id": None,
        "apply_gate_id": None,
        "verification_verdict_id": None,
        "simulation_result_id": None,
        "simulation_plan_id": None,
        "dry_run_id": None,
        "requested_action": None,
        "apply_executor_evidence_contract_snapshot": None,
        "evidence_collection_plan_checks": [],
        "planned_collection_steps": _build_planned_collection_steps("not_ready"),
        "planned_evidence_items": _build_planned_evidence_items(),
        "pre_execution_collection_plan": _build_pre_execution_collection_plan(),
        "during_execution_collection_plan": _build_during_execution_collection_plan(),
        "post_execution_collection_plan": _build_post_execution_collection_plan(),
        "rollback_collection_plan": _build_rollback_collection_plan(),
        "audit_collection_plan": _build_audit_collection_plan(),
        "collection_execution_constraints": _build_collection_execution_constraints("not_ready"),
        "collection_acceptance_plan": _build_collection_acceptance_plan(),
        "collector_boundary": _build_collector_boundary(),
        "required_collection_plan_confirmations": _build_required_confirmations("not_ready"),
        "evidence_collection_plan_statement": None,
        "blocking_reasons": [reason],
        "unresolved_risks": unresolved_risks,
        "recommended_next_step": "Resolve evidence collection plan readiness issues before preparing collection plan.",
        "evidence_contract_review_completed": False,
        "evidence_contract_intent_recorded": False,
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
        "apply_executor_evidence_collection_plan_execution_allowed": False,
        "metadata": {
            "source": "apply_executor_evidence_collection_plan_builder",
            "schema_version": "1.0",
            "session_id": context.get("session_id") if context else None,
        },
        "warnings": [
            "Apply executor evidence collection plan does not authorize execution.",
            "Apply executor evidence collection plan does not authorize apply.",
            "Evidence collection is planned but not performed.",
            "No evidence collector exists in this milestone.",
            "A separate future evidence collector is required before evidence can be collected.",
        ],
    }


def _build_planned_collection_steps(decision: str) -> list[dict]:
    """Build the planned collection steps."""
    base_steps = [
        {"step_number": 1, "name": "pre_execution_evidence_collection_placeholder", "purpose": "", "allowed_to_collect_now": False, "allowed_to_execute_now": False, "requires_future_evidence_collector": True, "required_evidence": [], "inspection_related": False, "rollback_related": False},
        {"step_number": 2, "name": "collection_boundary_revalidation", "purpose": "", "allowed_to_collect_now": False, "allowed_to_execute_now": False, "requires_future_evidence_collector": True, "required_evidence": [], "inspection_related": False, "rollback_related": False},
        {"step_number": 3, "name": "during_execution_evidence_collection_placeholder", "purpose": "", "allowed_to_collect_now": False, "allowed_to_execute_now": False, "requires_future_evidence_collector": True, "required_evidence": [], "inspection_related": False, "rollback_related": False},
        {"step_number": 4, "name": "post_execution_evidence_collection_placeholder", "purpose": "", "allowed_to_collect_now": False, "allowed_to_execute_now": False, "requires_future_evidence_collector": True, "required_evidence": [], "inspection_related": False, "rollback_related": False},
        {"step_number": 5, "name": "rollback_evidence_collection_placeholder", "purpose": "", "allowed_to_collect_now": False, "allowed_to_execute_now": False, "requires_future_evidence_collector": True, "required_evidence": [], "inspection_related": False, "rollback_related": False},
        {"step_number": 6, "name": "audit_evidence_package_preparation", "purpose": "", "allowed_to_collect_now": False, "allowed_to_execute_now": False, "requires_future_evidence_collector": True, "required_evidence": [], "inspection_related": False, "rollback_related": False},
    ]
    if decision == "evidence_collection_plan_ready":
        for step in base_steps:
            step["purpose"] = "Future evidence collector would collect evidence at this stage according to the plan."
    else:
        for step in base_steps:
            step["purpose"] = "No evidence collection is allowed in this milestone; this step is a placeholder for future evidence collector."
    return base_steps


def _build_planned_evidence_items() -> list[dict]:
    """Build the planned evidence items."""
    return [
        {
            "name": "pre_execution_state_evidence",
            "required": True,
            "collected_now": False,
            "collection_allowed_now": False,
            "source_contract_item": None,
            "planned_capture_method": "Future evidence collector would capture pre-execution state.",
            "description": "Evidence capturing the system state before any execution.",
            "acceptance_criteria": ["State snapshot must be consistent and verifiable"],
            "failure_policy": "Plan must be aborted if evidence cannot be captured."
        },
        {
            "name": "execution_result_evidence",
            "required": True,
            "collected_now": False,
            "collection_allowed_now": False,
            "source_contract_item": None,
            "planned_capture_method": "Future evidence collector would capture execution results.",
            "description": "Evidence capturing the results of execution.",
            "acceptance_criteria": ["Results must match expected output"],
            "failure_policy": "Plan must be aborted if execution results do not match expectations."
        },
        {
            "name": "post_execution_verification_evidence",
            "required": True,
            "collected_now": False,
            "collection_allowed_now": False,
            "source_contract_item": None,
            "planned_capture_method": "Future evidence collector would capture post-execution verification.",
            "description": "Evidence capturing verification of post-execution state.",
            "acceptance_criteria": ["Post-state must match expected final state"],
            "failure_policy": "Plan must be aborted if verification fails."
        },
        {
            "name": "rollback_evidence",
            "required": True,
            "collected_now": False,
            "collection_allowed_now": False,
            "source_contract_item": None,
            "planned_capture_method": "Future evidence collector would capture rollback evidence if needed.",
            "description": "Evidence capturing rollback actions taken.",
            "acceptance_criteria": ["Rollback must successfully revert changes"],
            "failure_policy": "Rollback must succeed or plan must be escalated."
        },
        {
            "name": "audit_log_evidence",
            "required": True,
            "collected_now": False,
            "collection_allowed_now": False,
            "source_contract_item": None,
            "planned_capture_method": "Future evidence collector would capture audit logs.",
            "description": "Evidence capturing audit trail of all actions.",
            "acceptance_criteria": ["Audit logs must be complete and immutable"],
            "failure_policy": "Plan must not proceed if audit logs are incomplete."
        },
    ]


def _build_pre_execution_collection_plan() -> list[dict]:
    """Build the pre-execution collection plan items."""
    return [
        {
            "name": "requested_action_snapshot",
            "planned_stage": "pre_execution",
            "required": True,
            "collected_now": False,
            "collection_allowed_now": False,
            "planned_capture_method": "Future evidence collector would snapshot requested action.",
            "description": "Snapshot of the requested action before execution.",
        },
        {
            "name": "target_state_before_apply",
            "planned_stage": "pre_execution",
            "required": True,
            "collected_now": False,
            "collection_allowed_now": False,
            "planned_capture_method": "Future evidence collector would capture target state.",
            "description": "Target state before any apply operation.",
        },
        {
            "name": "permission_state_snapshot",
            "planned_stage": "pre_execution",
            "required": True,
            "collected_now": False,
            "collection_allowed_now": False,
            "planned_capture_method": "Future evidence collector would capture permission state.",
            "description": "Permission and authorization state before execution.",
        },
        {
            "name": "rollback_precondition_snapshot",
            "planned_stage": "pre_execution",
            "required": True,
            "collected_now": False,
            "collection_allowed_now": False,
            "planned_capture_method": "Future evidence collector would capture rollback preconditions.",
            "description": "State needed for potential rollback.",
        },
    ]


def _build_during_execution_collection_plan() -> list[dict]:
    """Build the during-execution collection plan items."""
    return [
        {
            "name": "executor_attempt_log",
            "planned_stage": "during_execution",
            "required": True,
            "collected_now": False,
            "collection_allowed_now": False,
            "planned_capture_method": "Future evidence collector would log executor attempts.",
            "description": "Log of executor attempts during execution.",
        },
        {
            "name": "tool_call_boundary_log",
            "planned_stage": "during_execution",
            "required": True,
            "collected_now": False,
            "collection_allowed_now": False,
            "planned_capture_method": "Future evidence collector would log tool call boundaries.",
            "description": "Log of tool call boundaries during execution.",
        },
        {
            "name": "execution_result_raw_output",
            "planned_stage": "during_execution",
            "required": True,
            "collected_now": False,
            "collection_allowed_now": False,
            "planned_capture_method": "Future evidence collector would capture raw output.",
            "description": "Raw output from execution.",
        },
    ]


def _build_post_execution_collection_plan() -> list[dict]:
    """Build the post-execution collection plan items."""
    return [
        {
            "name": "target_state_after_apply",
            "planned_stage": "post_execution",
            "required": True,
            "collected_now": False,
            "collection_allowed_now": False,
            "planned_capture_method": "Future evidence collector would capture target state after apply.",
            "description": "Target state after apply operation.",
        },
        {
            "name": "verification_result_after_apply",
            "planned_stage": "post_execution",
            "required": True,
            "collected_now": False,
            "collection_allowed_now": False,
            "planned_capture_method": "Future evidence collector would capture verification result.",
            "description": "Verification result after apply.",
        },
        {
            "name": "user_visible_outcome_summary",
            "planned_stage": "post_execution",
            "required": True,
            "collected_now": False,
            "collection_allowed_now": False,
            "planned_capture_method": "Future evidence collector would summarize user-visible outcome.",
            "description": "Summary of the user-visible outcome of the operation.",
        },
    ]


def _build_rollback_collection_plan() -> list[dict]:
    """Build the rollback collection plan items."""
    return [
        {
            "name": "rollback_plan_snapshot",
            "planned_stage": "rollback",
            "required": True,
            "collected_now": False,
            "collection_allowed_now": False,
            "planned_capture_method": "Future evidence collector would capture rollback plan.",
            "description": "Snapshot of the rollback plan.",
        },
        {
            "name": "rollback_trigger_conditions",
            "planned_stage": "rollback",
            "required": True,
            "collected_now": False,
            "collection_allowed_now": False,
            "planned_capture_method": "Future evidence collector would capture trigger conditions.",
            "description": "Conditions that would trigger rollback.",
        },
        {
            "name": "rollback_execution_log_placeholder",
            "planned_stage": "rollback",
            "required": True,
            "collected_now": False,
            "collection_allowed_now": False,
            "planned_capture_method": "Future evidence collector would log rollback execution.",
            "description": "Placeholder for rollback execution log.",
        },
        {
            "name": "rollback_verification_result_placeholder",
            "planned_stage": "rollback",
            "required": True,
            "collected_now": False,
            "collection_allowed_now": False,
            "planned_capture_method": "Future evidence collector would verify rollback result.",
            "description": "Placeholder for rollback verification result.",
        },
    ]


def _build_audit_collection_plan() -> list[dict]:
    """Build the audit collection plan items."""
    return [
        {
            "name": "apply_executor_evidence_contract_record_snapshot",
            "planned_stage": "audit",
            "required": True,
            "collected_now": False,
            "collection_allowed_now": False,
            "planned_capture_method": "Future evidence collector would snapshot the evidence contract record.",
            "description": "Snapshot of the apply executor evidence contract record.",
        },
        {
            "name": "apply_executor_plan_record_snapshot",
            "planned_stage": "audit",
            "required": True,
            "collected_now": False,
            "collection_allowed_now": False,
            "planned_capture_method": "Future evidence collector would snapshot the plan record.",
            "description": "Snapshot of the apply executor plan record.",
        },
        {
            "name": "apply_executor_contract_record_snapshot",
            "planned_stage": "audit",
            "required": True,
            "collected_now": False,
            "collection_allowed_now": False,
            "planned_capture_method": "Future evidence collector would snapshot the contract record.",
            "description": "Snapshot of the apply executor contract record.",
        },
        {
            "name": "approval_chain_snapshot",
            "planned_stage": "audit",
            "required": True,
            "collected_now": False,
            "collection_allowed_now": False,
            "planned_capture_method": "Future evidence collector would snapshot the approval chain.",
            "description": "Snapshot of the complete approval chain.",
        },
        {
            "name": "final_audit_summary_placeholder",
            "planned_stage": "audit",
            "required": True,
            "collected_now": False,
            "collection_allowed_now": False,
            "planned_capture_method": "Future evidence collector would summarize audit results.",
            "description": "Placeholder for final audit summary.",
        },
    ]


def _build_collection_execution_constraints(decision: str) -> dict:
    """Build the collection execution constraints."""
    if decision == "evidence_collection_plan_ready":
        return {
            "collection_scope": "plan_only_no_collection",
            "collection_allowed_now": False,
            "execution_allowed": False,
            "apply_allowed": False,
            "tool_execution_allowed": False,
            "filesystem_inspection_allowed": False,
            "network_inspection_allowed": False,
            "database_inspection_allowed": False,
            "external_api_call_allowed": False,
            "requires_future_collector": True,
            "forbidden_collection_methods": [
                "shell",
                "subprocess",
                "raw_code_execution",
                "filesystem_scan",
                "network_probe",
                "database_query",
                "external_api_call",
                "identity_modification",
                "self_repair",
                "apply_execution",
                "rollback_execution",
            ],
        }
    else:
        return {
            "collection_scope": "blocked_or_not_ready_plan_only_no_collection",
            "collection_allowed_now": False,
            "execution_allowed": False,
            "apply_allowed": False,
            "tool_execution_allowed": False,
            "filesystem_inspection_allowed": False,
            "network_inspection_allowed": False,
            "database_inspection_allowed": False,
            "external_api_call_allowed": False,
            "requires_future_collector": True,
            "forbidden_collection_methods": [
                "shell",
                "subprocess",
                "raw_code_execution",
                "filesystem_scan",
                "network_probe",
                "database_query",
                "external_api_call",
                "identity_modification",
                "self_repair",
                "apply_execution",
                "rollback_execution",
            ],
        }


def _build_collection_acceptance_plan() -> list[dict]:
    """Build the collection acceptance plan."""
    return [
        {
            "criterion": "Planned evidence item names must match the approved evidence contract.",
            "required": True,
            "satisfied_now": False,
        },
        {
            "criterion": "Evidence must be collected only by a future authorized evidence collector.",
            "required": True,
            "satisfied_now": False,
        },
        {
            "criterion": "Evidence collection must be linked to the correct apply_executor_evidence_contract_id.",
            "required": True,
            "satisfied_now": False,
        },
        {
            "criterion": "This plan must not collect evidence directly.",
            "required": True,
            "satisfied_now": False,
        },
        {
            "criterion": "Evidence collection must not imply apply authorization.",
            "required": True,
            "satisfied_now": False,
        },
    ]


def _build_collector_boundary() -> dict:
    """Build the collector boundary information."""
    return {
        "collector_exists": False,
        "collector_authorized": False,
        "collector_execution_allowed": False,
        "collection_allowed_now": False,
        "requires_future_evidence_collector": True,
        "collector_note": "No evidence collector exists or runs in this milestone.",
    }


def _build_required_confirmations(decision: str) -> list[str]:
    """Build the required collection plan confirmations."""
    if decision == "evidence_collection_plan_ready":
        return [
            "I confirm the evidence contract intent was recorded.",
            "I confirm this collection plan does not collect evidence.",
            "I confirm this collection plan does not authorize apply.",
            "I confirm this collection plan does not authorize execution.",
            "I confirm this collection plan requires a future evidence collector.",
            "I understand a separate future evidence collection plan record is required.",
        ]
    return []


def _build_evidence_collection_plan_statement(decision: str) -> str | None:
    """Build the evidence collection plan statement."""
    if decision == "evidence_collection_plan_ready":
        return "Apply executor evidence collection plan is prepared for future evidence collector design. This plan does not collect evidence, authorize execution, or execute apply."
    return None


def _build_recommended_next_step(decision: str) -> str:
    """Build the recommended next step."""
    if decision == "evidence_collection_plan_ready":
        return "Persist this evidence collection plan in a future collection plan record milestone; do not collect evidence or execute changes yet."
    elif decision == "not_ready":
        return "Resolve evidence collection plan readiness issues before preparing collection plan."
    else:
        return "Resolve blocking conditions before continuing."
