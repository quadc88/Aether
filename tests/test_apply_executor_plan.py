"""Tests for Apply Executor Plan Builder (Milestone 73A).

Verifies that build_apply_executor_plan produces correct plan objects
from apply_executor_contract_records. No execution, apply, rollback, evidence, or mutation occurs.
"""

from __future__ import annotations

import copy
import pytest


@pytest.fixture()
def _build():
    from aether.action.apply_executor_plan import build_apply_executor_plan
    return build_apply_executor_plan


def _make_clean_record():
    """Factory to produce a fresh approved_contract_intent AECR."""
    return {
        "apply_executor_contract_id": "aecr-001",
        "status": "approved_contract_intent",
        "contract_decision": "contract_ready",
        "decision": "approved_contract_intent",
        "reviewer": "test",
        "decision_reason": "test review",
        "decided_at": "2026-01-01T00:00:01+00:00",
        "human_authorization_id": "ha-001",
        "apply_gate_id": "ag-001",
        "verification_verdict_id": "vv-001",
        "simulation_result_id": "sim-001",
        "simulation_plan_id": "plan-1",
        "dry_run_id": "dr-1",
        "created_at": "2026-01-01T00:00:00+00:00",
        "updated_at": "2026-01-01T00:00:00+00:00",
        "contract_review_completed": True,
        "contract_intent_recorded": True,
        "confirmations_required": ["c1", "c2", "c3"],
        "confirmations_received": ["c1", "c2", "c3"],
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
        "apply_allowed": False,
        "rollback_allowed": False,
        "apply_executor_contract_persisted": True,
        "evidence_collected": False,
        "rollback_plan_attached": False,
        "metadata": {"source": "test", "session_id": "73a-test"},
        "warnings": [],
        "apply_executor_contract": {
            "decision": "contract_ready",
            "reason": "All checks passed.",
            "plan_required": True,
            "apply_executor_contract_status": "prepared",
            "human_authorization_id": "ha-001",
            "authorization_decision": "ready_for_human_authorization",
            "apply_gate_id": "ag-001",
            "verification_verdict_id": "vv-001",
            "simulation_result_id": "sim-001",
            "simulation_plan_id": "plan-1",
            "dry_run_id": "dr-1",
            "requested_action": {
                "tool_id": "test.tool",
                "action_type": "status_check",
                "name": "Test Tool",
                "parameters": {"scope": "read_only"},
                "target": "test_target",
            },
            "required_executor_confirmations": [
                "I confirm the execution gate intent was recorded.",
                "I confirm this contract does not execute the action.",
                "I confirm this contract does not authorize apply.",
                "I confirm a future executor must collect pre-execution and post-execution evidence.",
                "I confirm rollback planning is required before future apply.",
                "I understand a separate future apply executor is required.",
            ],
            "execution_statement": "Apply executor contract review required.",
            "blocking_reasons": [],
            "unresolved_risks": [],
            "recommended_next_step": "Present for review.",
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
            "warnings": ["aec warning"],
            "execution_boundary": {
                "allowed_action_type": "status_check",
                "allowed_tool_id": "test.tool",
                "allowed_target": "test_target",
                "allowed_parameters": {"scope": "read_only"},
                "forbidden_capabilities": ["shell", "subprocess"],
                "execution_scope": "contract_only_no_execution",
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
            },
            "evidence_requirements": [
                {"name": "pre_execution_state_evidence", "required": True, "satisfied": False},
                {"name": "execution_result_evidence", "required": True, "satisfied": False},
                {"name": "post_execution_verification_evidence", "required": True, "satisfied": False},
                {"name": "rollback_evidence", "required": True, "satisfied": False},
                {"name": "audit_log_evidence", "required": True, "satisfied": False},
            ],
        },
    }


@pytest.fixture()
def clean_aecr():
    return _make_clean_record()


# ======================== TESTS 1-13: REJECTION CASES ======================== #

class TestRejectionCases:
    def test_missing_record_returns_blocked(self, _build):
        c = _build(None)
        assert c["decision"] == "blocked"
        assert c["plan_required"] is False
        assert "not found" in c["reason"].lower()

    def test_pending_record_returns_blocked(self, _build):
        r = copy.deepcopy(_make_clean_record())
        r["status"] = "pending"
        c = _build(r)
        assert c["decision"] == "blocked"
        assert c["plan_required"] is False
        assert "not approved_contract_intent" in c["reason"].lower()

    def test_rejected_record_returns_blocked(self, _build):
        r = copy.deepcopy(_make_clean_record())
        r["status"] = "rejected"
        c = _build(r)
        assert c["decision"] == "blocked"

    def test_cancelled_record_returns_blocked(self, _build):
        r = copy.deepcopy(_make_clean_record())
        r["status"] = "cancelled"
        c = _build(r)
        assert c["decision"] == "blocked"

    def test_contract_decision_not_ready_returns_blocked(self, _build):
        r = copy.deepcopy(_make_clean_record())
        r["contract_decision"] = "not_ready"
        r["status"] = "approved_contract_intent"
        c = _build(r)
        assert c["decision"] == "blocked"

    def test_contract_intent_recorded_false_returns_blocked(self, _build):
        r = copy.deepcopy(_make_clean_record())
        r["contract_intent_recorded"] = False
        c = _build(r)
        assert c["decision"] == "blocked"
        assert "contract intent" in c["reason"].lower()

    def test_contract_review_completed_false_returns_blocked(self, _build):
        r = copy.deepcopy(_make_clean_record())
        r["contract_review_completed"] = False
        c = _build(r)
        assert c["decision"] == "blocked"
        assert "contract review" in c["reason"].lower()

    def test_evidence_collected_true_returns_blocked(self, _build):
        r = copy.deepcopy(_make_clean_record())
        r["evidence_collected"] = True
        c = _build(r)
        assert c["decision"] == "blocked"
        assert "evidence" in c["reason"].lower()

    def test_rollback_plan_attached_true_returns_blocked(self, _build):
        r = copy.deepcopy(_make_clean_record())
        r["rollback_plan_attached"] = True
        c = _build(r)
        assert c["decision"] == "blocked"
        assert "rollback plan" in c["reason"].lower() or "rollback_plan_attached" in c["reason"].lower()

    def test_apply_authorized_true_returns_blocked(self, _build):
        r = copy.deepcopy(_make_clean_record())
        r["apply_authorized"] = True
        c = _build(r)
        assert c["decision"] == "blocked"
        assert "apply" in c["reason"].lower()

    def test_apply_executed_true_returns_blocked(self, _build):
        r = copy.deepcopy(_make_clean_record())
        r["apply_executed"] = True
        c = _build(r)
        assert c["decision"] == "blocked"

    def test_rollback_executed_true_returns_blocked(self, _build):
        r = copy.deepcopy(_make_clean_record())
        r["rollback_executed"] = True
        c = _build(r)
        assert c["decision"] == "blocked"

    def test_missing_contract_payload_returns_not_ready(self, _build):
        r = copy.deepcopy(_make_clean_record())
        r["apply_executor_contract"] = None
        c = _build(r)
        assert c["decision"] == "not_ready"
        assert c["plan_required"] is False


# ======================== TESTS 14-21: CLEAN PLAN READY CASE ======================== #

class TestCleanPlanReadyCase:
    def test_eligible_returns_plan_ready(self, _build, clean_aecr):
        c = _build(clean_aecr)
        assert c["decision"] == "plan_ready"
        assert c["plan_required"] is True

    def test_plan_ready_has_plan_required_true(self, _build, clean_aecr):
        c = _build(clean_aecr)
        assert c["plan_required"] is True

    def test_plan_ready_still_has_apply_authorized_false(self, _build, clean_aecr):
        c = _build(clean_aecr)
        assert c["apply_authorized"] is False

    def test_plan_ready_still_has_apply_allowed_false(self, _build, clean_aecr):
        c = _build(clean_aecr)
        assert c["apply_allowed"] is False

    def test_plan_ready_still_has_execution_allowed_false(self, _build, clean_aecr):
        c = _build(clean_aecr)
        assert c["execution_allowed"] is False

    def test_plan_ready_still_has_evidence_collected_false(self, _build, clean_aecr):
        c = _build(clean_aecr)
        assert c["evidence_collected"] is False

    def test_plan_ready_still_has_rollback_plan_attached_false(self, _build, clean_aecr):
        c = _build(clean_aecr)
        assert c["rollback_plan_attached"] is False

    def test_plan_ready_all_flags_false(self, _build, clean_aecr):
        c = _build(clean_aecr)
        flags = [
            "apply_authorized", "apply_allowed", "rollback_allowed", "execution_allowed",
            "tool_execution_allowed", "dry_run_execution_allowed", "simulation_execution_allowed",
            "apply_gate_execution_allowed", "human_authorization_execution_allowed",
            "apply_execution_gate_execution_allowed", "apply_executor_contract_execution_allowed",
            "apply_executor_plan_execution_allowed", "evidence_collected", "rollback_plan_attached",
        ]
        for fk in flags:
            assert c[fk] is False, f"{fk} should be false"


# ======================== TESTS 22-39: PLAN CHECKS & CONTENT ======================== #

class TestPlanChecks:
    def test_includes_all_23_checks(self, _build, clean_aecr):
        c = _build(clean_aecr)
        names = [chk["name"] for chk in c["plan_checks"]]
        expected = [
            "apply_executor_contract_approved_intent", "apply_executor_contract_persisted",
            "contract_decision_ready", "contract_review_completed", "contract_intent_recorded",
            "confirmations_received", "contract_ready", "execution_boundary_present",
            "execution_boundary_scope_safe", "evidence_requirements_declared",
            "evidence_not_collected", "rollback_expectation_declared", "rollback_plan_not_attached",
            "apply_not_authorized", "apply_not_executed", "rollback_not_executed",
            "execution_flags_blocked", "apply_flags_blocked",
            "requested_action_present", "requested_action_type_allowed",
            "target_present", "no_direct_executor_present", "blocking_reasons_empty",
        ]
        for name in expected:
            assert name in names, f"Missing check: {name}"

    def test_all_checks_pass_for_clean_record(self, _build, clean_aecr):
        c = _build(clean_aecr)
        for chk in c["plan_checks"]:
            assert chk["passed"] is True, f"Check {chk['name']} should pass but got {chk}"

    def test_critical_check_failure_blocks(self, _build):
        r = copy.deepcopy(_make_clean_record())
        r["apply_executor_contract"]["apply_authorized"] = True
        c = _build(r)
        assert c["decision"] == "blocked"

    def test_high_check_failure_blocks(self, _build):
        r = copy.deepcopy(_make_clean_record())
        r["contract_decision"] = "blocked"
        r["status"] = "approved_contract_intent"
        c = _build(r)
        assert c["decision"] == "blocked"

    def test_medium_check_failure_returns_not_ready(self, _build):
        r = copy.deepcopy(_make_clean_record())
        r["apply_executor_contract"]["blocking_reasons"] = ["some block"]
        c = _build(r)
        assert c["decision"] == "not_ready"

    def test_low_check_failure_returns_not_ready(self, _build):
        r = copy.deepcopy(_make_clean_record())
        r["apply_executor_contract_persisted"] = False
        c = _build(r)
        assert c["decision"] == "not_ready"

    def test_confirmations_passed_when_covered(self, _build, clean_aecr):
        c = _build(clean_aecr)
        chk = next(chk for chk in c["plan_checks"] if chk["name"] == "confirmations_received")
        assert chk["passed"] is True

    def test_confirmations_fails_when_missing(self, _build):
        r = copy.deepcopy(_make_clean_record())
        r["confirmations_received"] = []
        c = _build(r)
        chk = next(chk for chk in c["plan_checks"] if chk["name"] == "confirmations_received")
        assert chk["passed"] is False

    def test_evidence_requirements_declared_fails_when_missing(self, _build):
        r = copy.deepcopy(_make_clean_record())
        r["apply_executor_contract"]["evidence_requirements"] = []
        c = _build(r)
        chk = next(chk for chk in c["plan_checks"] if chk["name"] == "evidence_requirements_declared")
        assert chk["passed"] is False

    def test_evidence_not_collected_fails_when_satisfied(self, _build):
        r = copy.deepcopy(_make_clean_record())
        r["apply_executor_contract"]["evidence_requirements"][0]["satisfied"] = True
        c = _build(r)
        chk = next(chk for chk in c["plan_checks"] if chk["name"] == "evidence_not_collected")
        assert chk["passed"] is False

    def test_rollback_expectation_declared_fails_when_missing(self, _build):
        r = copy.deepcopy(_make_clean_record())
        del r["apply_executor_contract"]["rollback_expectation"]
        c = _build(r)
        chk = next(chk for chk in c["plan_checks"] if chk["name"] == "rollback_expectation_declared")
        assert chk["passed"] is False

    def test_rollback_plan_not_attached_fails_when_present(self, _build):
        r = copy.deepcopy(_make_clean_record())
        r["apply_executor_contract"]["rollback_expectation"]["rollback_plan_present"] = True
        c = _build(r)
        chk = next(chk for chk in c["plan_checks"] if chk["name"] == "rollback_plan_not_attached")
        assert chk["passed"] is False

    def test_requested_action_present_fails_when_missing(self, _build):
        r = copy.deepcopy(_make_clean_record())
        r["apply_executor_contract"]["requested_action"] = None
        c = _build(r)
        chk = next(chk for chk in c["plan_checks"] if chk["name"] == "requested_action_present")
        assert chk["passed"] is False

    def test_requested_action_type_allowed_fails_for_unsafe(self, _build):
        r = copy.deepcopy(_make_clean_record())
        r["apply_executor_contract"]["requested_action"]["action_type"] = "file_delete"
        c = _build(r)
        chk = next(chk for chk in c["plan_checks"] if chk["name"] == "requested_action_type_allowed")
        assert chk["passed"] is False

    def test_no_direct_executor_present_fails_for_shell_command(self, _build):
        r = copy.deepcopy(_make_clean_record())
        r["apply_executor_contract"]["requested_action"]["command"] = "rm -rf /"
        c = _build(r)
        chk = next(chk for chk in c["plan_checks"] if chk["name"] == "no_direct_executor_present")
        assert chk["passed"] is False

    def test_target_present_fails_when_missing(self, _build):
        r = copy.deepcopy(_make_clean_record())
        r["apply_executor_contract"]["requested_action"]["target"] = ""
        c = _build(r)
        chk = next(chk for chk in c["plan_checks"] if chk["name"] == "target_present")
        assert chk["passed"] is False


# ======================== TESTS 38-58: STEPS, EVIDENCE, BOUNDARY, CONTENT ======================== #

class TestStepsEvidenceBoundaryContent:
    def test_ordered_execution_steps_exists_and_has_6_steps(self, _build, clean_aecr):
        c = _build(clean_aecr)
        steps = c["ordered_execution_steps"]
        assert len(steps) == 6

    def test_ordered_execution_steps_names(self, _build, clean_aecr):
        c = _build(clean_aecr)
        names = [s["name"] for s in c["ordered_execution_steps"]]
        expected = [
            "pre_execution_state_capture", "executor_boundary_revalidation",
            "apply_attempt_placeholder", "post_execution_state_capture",
            "outcome_verification", "audit_record_preparation",
        ]
        for n in expected:
            assert n in names, f"Missing step: {n}"

    def test_all_ordered_steps_not_executable_now(self, _build, clean_aecr):
        c = _build(clean_aecr)
        for s in c["ordered_execution_steps"]:
            assert s["allowed_to_execute_now"] is False

    def test_all_ordered_steps_require_future_executor(self, _build, clean_aecr):
        c = _build(clean_aecr)
        for s in c["ordered_execution_steps"]:
            assert s["requires_future_executor"] is True

    def test_apply_attempt_placeholder_not_executable(self, _build, clean_aecr):
        c = _build(clean_aecr)
        placeholder = next(s for s in c["ordered_execution_steps"] if s["name"] == "apply_attempt_placeholder")
        assert placeholder["allowed_to_execute_now"] is False

    def test_evidence_capture_plan_exists_and_has_5_items(self, _build, clean_aecr):
        c = _build(clean_aecr)
        assert len(c["evidence_capture_plan"]) == 5

    def test_all_evidence_collection_allowed_false(self, _build, clean_aecr):
        c = _build(clean_aecr)
        for e in c["evidence_capture_plan"]:
            assert e["collection_allowed_now"] is False
            assert e["collected_now"] is False

    def test_rollback_plan_requirement_exists_and_false(self, _build, clean_aecr):
        c = _build(clean_aecr)
        rp = c["rollback_plan_requirement"]
        assert rp["rollback_required_before_future_apply"] is True
        assert rp["rollback_plan_required"] is True
        assert rp["rollback_plan_attached"] is False
        assert rp["rollback_verified"] is False
        assert rp["rollback_allowed"] is False
        assert rp["rollback_executed"] is False

    def test_executor_constraints_ready(self, _build, clean_aecr):
        c = _build(clean_aecr)
        ec = c["executor_constraints"]
        assert ec["execution_scope"] == "plan_only_no_execution"
        fc = ec["forbidden_capabilities"]
        assert "shell" in fc
        assert "self_repair" in fc

    def test_executor_constraints_blocked(self, _build):
        c = _build(None)
        ec = c["executor_constraints"]
        assert ec["execution_scope"] == "blocked_or_not_ready_plan_only_no_execution"

    def test_required_plan_confirmations_included(self, _build, clean_aecr):
        c = _build(clean_aecr)
        rc = c["required_plan_confirmations"]
        assert len(rc) >= 6
        assert any("contract intent" in l.lower() for l in rc)
        assert any("separate future apply executor" in l.lower() for l in rc)

    def test_plan_statement_present_only_for_plan_ready(self, _build, clean_aecr):
        c = _build(clean_aecr)
        assert c["plan_statement"] is not None
        assert "does not authorize or execute apply" in c["plan_statement"]

    def test_plan_statement_none_for_blocked(self, _build):
        c = _build(None)
        assert c["plan_statement"] is None

    def test_recommended_next_step_for_ready(self, _build, clean_aecr):
        c = _build(clean_aecr)
        step = c["recommended_next_step"]
        assert "persist" in step.lower()
        assert "do not execute" in step.lower() or "not execute" in step.lower()

    def test_metadata_source_schema_version_session_id(self, _build, clean_aecr):
        c = _build(clean_aecr, context={"session_id": "73a-sid"})
        meta = c["metadata"]
        assert meta["source"] == "apply_executor_plan_builder"
        assert meta["schema_version"] == "1.0"
        assert meta["session_id"] == "73a-sid"

    def test_warnings_include_all_expected(self, _build, clean_aecr):
        c = _build(clean_aecr)
        warns_text = " ".join(c["warnings"])
        assert "does not authorize execution" in warns_text
        assert "does not execute apply" in warns_text
        assert "Evidence capture is planned" in warns_text
        assert "Rollback plan is required" in warns_text
        assert "separate future executor" in warns_text

    def test_contract_warnings_copied_with_prefix(self, _build, clean_aecr):
        c = _build(clean_aecr)
        warns_text = " ".join(c["warnings"])
        assert "apply_executor_contract_warning:" in warns_text

    def test_requested_action_copied(self, _build, clean_aecr):
        c = _build(clean_aecr)
        ra = c["requested_action"]
        assert ra is not None
        assert ra["tool_id"] == "test.tool"

    def test_link_ids_copied(self, _build, clean_aecr):
        c = _build(clean_aecr)
        assert c["apply_executor_contract_id"] == "aecr-001"
        assert c["human_authorization_id"] == "ha-001"
        assert c["apply_gate_id"] == "ag-001"
        assert c["verification_verdict_id"] == "vv-001"
        assert c["simulation_result_id"] == "sim-001"
        assert c["simulation_plan_id"] == "plan-1"
        assert c["dry_run_id"] == "dr-1"
        assert c["apply_execution_gate_id"] is None  # not stored on AE-CR directly
