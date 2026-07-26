"""Tests for Apply Executor Contract Builder (Milestone 71A).

Verifies that build_apply_executor_contract produces correct contract objects
from apply_execution_gate_records. No execution, apply, rollback, or mutation
occurs.
"""

from __future__ import annotations

import copy
import pytest


def _make_clean_record():
    """Factory to produce a fresh clean approved_execution_intent AEGR."""
    return {
        "apply_execution_gate_id": "aeg-001",
        "status": "approved_execution_intent",
        "gate_decision": "ready_for_execution_gate_review",
        "decision": "approved_execution_intent",
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
        "execution_review_completed": True,
        "execution_intent_recorded": True,
        "confirmations_required": [
            "I confirm human approval intent was recorded.",
            "I confirm the requested action is still desired.",
            "I confirm the target is correct.",
        ],
        "confirmations_received": [
            "I confirm human approval intent was recorded.",
            "I confirm the requested action is still desired.",
            "I confirm the target is correct.",
        ],
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
        "apply_allowed": False,
        "rollback_allowed": False,
        "apply_execution_gate_persisted": True,
        "metadata": {"source": "test", "session_id": "71a-test"},
        "warnings": [],
        "apply_execution_gate_request": {
            "decision": "ready_for_execution_gate_review",
            "reason": "All checks passed.",
            "apply_execution_gate_required": True,
            "apply_execution_gate_status": "prepared",
            "human_authorization_id": "ha-001",
            "human_authorization_record_status": "approved_intent",
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
            "required_pre_execution_confirmations": [
                "I confirm the requested action is still desired.",
                "I confirm the target is correct.",
                "I understand this does not execute the action.",
            ],
            "execution_statement": "Apply execution gate review required.",
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
            "metadata": {},
            "warnings": ["aegr warning"],
        },
    }


@pytest.fixture()
def _build():
    from aether.action.apply_executor_contract import build_apply_executor_contract
    return build_apply_executor_contract


@pytest.fixture()
def clean_aeg_record():
    return _make_clean_record()


# ======================== TESTS 1-11: REJECTION CASES ======================== #

class TestRejectionCases:
    def test_missing_record_returns_blocked(self, _build):
        c = _build(None)
        assert c["decision"] == "blocked"
        assert c["contract_required"] is False
        assert "not found" in c["reason"].lower()

    def test_pending_record_returns_blocked(self, _build):
        r = copy.deepcopy(_make_clean_record())
        r["status"] = "pending"
        c = _build(r)
        assert c["decision"] == "blocked"
        assert c["contract_required"] is False
        assert "not approved_execution_intent" in c["reason"].lower()

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

    def test_gate_decision_not_ready_returns_blocked(self, _build):
        r = copy.deepcopy(_make_clean_record())
        r["gate_decision"] = "not_ready"
        r["status"] = "approved_execution_intent"
        c = _build(r)
        assert c["decision"] == "blocked"

    def test_execution_intent_recorded_false_returns_blocked(self, _build):
        r = copy.deepcopy(_make_clean_record())
        r["execution_intent_recorded"] = False
        c = _build(r)
        assert c["decision"] == "blocked"
        assert "execution intent" in c["reason"].lower()

    def test_execution_review_completed_false_returns_blocked(self, _build):
        r = copy.deepcopy(_make_clean_record())
        r["execution_review_completed"] = False
        c = _build(r)
        assert c["decision"] == "blocked"
        assert "execution review" in c["reason"].lower()

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


# ======================== TESTS 12-17: CLEAN CONTRACT READY CASE ======================== #

class TestCleanContractReadyCase:
    def test_eligible_returns_contract_ready(self, _build, clean_aeg_record):
        c = _build(clean_aeg_record)
        assert c["decision"] == "contract_ready"
        assert c["contract_required"] is True

    def test_contract_ready_has_contract_required_true(self, _build, clean_aeg_record):
        c = _build(clean_aeg_record)
        assert c["contract_required"] is True

    def test_contract_ready_still_has_apply_authorized_false(self, _build, clean_aeg_record):
        c = _build(clean_aeg_record)
        assert c["apply_authorized"] is False

    def test_contract_ready_still_has_apply_allowed_false(self, _build, clean_aeg_record):
        c = _build(clean_aeg_record)
        assert c["apply_allowed"] is False

    def test_contract_ready_still_has_execution_allowed_false(self, _build, clean_aeg_record):
        c = _build(clean_aeg_record)
        assert c["execution_allowed"] is False

    def test_contract_ready_all_flags_false(self, _build, clean_aeg_record):
        c = _build(clean_aeg_record)
        assert c["apply_authorized"] is False
        assert c["apply_allowed"] is False
        assert c["rollback_allowed"] is False
        assert c["execution_allowed"] is False
        assert c["tool_execution_allowed"] is False
        assert c["dry_run_execution_allowed"] is False
        assert c["simulation_execution_allowed"] is False
        assert c["apply_gate_execution_allowed"] is False
        assert c["human_authorization_execution_allowed"] is False
        assert c["apply_execution_gate_execution_allowed"] is False
        assert c["apply_executor_contract_execution_allowed"] is False


# ======================== TESTS 18-39: CONTRACT CHECKS & CONTENT ======================== #

class TestContractChecks:
    def test_includes_all_17_checks(self, _build, clean_aeg_record):
        c = _build(clean_aeg_record)
        names = [chk["name"] for chk in c["contract_checks"]]
        expected = [
            "apply_execution_gate_approved_intent",
            "apply_execution_gate_persisted",
            "gate_decision_ready",
            "execution_review_completed",
            "execution_intent_recorded",
            "confirmations_received",
            "request_ready_for_execution_gate_review",
            "apply_not_authorized",
            "apply_not_executed",
            "rollback_not_executed",
            "execution_flags_blocked",
            "apply_flags_blocked",
            "requested_action_present",
            "requested_action_type_allowed",
            "target_present",
            "no_direct_executor_present",
            "blocking_reasons_empty",
        ]
        for name in expected:
            assert name in names, f"Missing check: {name}"

    def test_all_checks_pass_for_clean_record(self, _build, clean_aeg_record):
        c = _build(clean_aeg_record)
        for chk in c["contract_checks"]:
            assert chk["passed"] is True, f"Check {chk['name']} should pass but returned {chk}"

    def test_critical_check_failure_blocks(self, _build):
        r = copy.deepcopy(_make_clean_record())
        r["apply_execution_gate_request"]["apply_authorized"] = True
        c = _build(r)
        assert c["decision"] == "blocked"

    def test_high_check_failure_blocks(self, _build):
        r = copy.deepcopy(_make_clean_record())
        r["gate_decision"] = "blocked"
        r["status"] = "approved_execution_intent"
        c = _build(r)
        assert c["decision"] == "blocked"

    def test_medium_check_failure_returns_not_ready(self, _build):
        r = copy.deepcopy(_make_clean_record())
        r["apply_execution_gate_request"]["blocking_reasons"] = ["some block"]
        c = _build(r)
        assert c["decision"] == "not_ready"

    def test_low_check_failure_returns_not_ready(self, _build):
        r = copy.deepcopy(_make_clean_record())
        r["apply_execution_gate_persisted"] = False
        c = _build(r)
        assert c["decision"] == "not_ready"

    def test_confirmations_passed_when_covered(self, _build, clean_aeg_record):
        c = _build(clean_aeg_record)
        chk = next(chk for chk in c["contract_checks"] if chk["name"] == "confirmations_received")
        assert chk["passed"] is True

    def test_confirmations_fails_when_missing(self, _build):
        r = copy.deepcopy(_make_clean_record())
        r["confirmations_received"] = []
        c = _build(r)
        chk = next(chk for chk in c["contract_checks"] if chk["name"] == "confirmations_received")
        assert chk["passed"] is False

    def test_requested_action_present_fails_when_missing(self, _build):
        r = copy.deepcopy(_make_clean_record())
        r["apply_execution_gate_request"]["requested_action"] = None
        c = _build(r)
        chk = next(chk for chk in c["contract_checks"] if chk["name"] == "requested_action_present")
        assert chk["passed"] is False

    def test_requested_action_type_allowed_fails_for_unsafe(self, _build):
        r = copy.deepcopy(_make_clean_record())
        r["apply_execution_gate_request"]["requested_action"]["action_type"] = "file_delete"
        c = _build(r)
        chk = next(chk for chk in c["contract_checks"] if chk["name"] == "requested_action_type_allowed")
        assert chk["passed"] is False

    def test_no_direct_executor_present_fails_for_shell_command(self, _build):
        r = copy.deepcopy(_make_clean_record())
        r["apply_execution_gate_request"]["requested_action"]["command"] = "rm -rf /"
        c = _build(r)
        chk = next(chk for chk in c["contract_checks"] if chk["name"] == "no_direct_executor_present")
        assert chk["passed"] is False

    def test_target_present_fails_when_missing(self, _build):
        r = copy.deepcopy(_make_clean_record())
        r["apply_execution_gate_request"]["requested_action"]["target"] = ""
        c = _build(r)
        chk = next(chk for chk in c["contract_checks"] if chk["name"] == "target_present")
        assert chk["passed"] is False


# ======================== TEST 11: MISSING REQUEST PAYLOAD ======================== #

class TestMissingRequestPayload:
    def test_missing_request_payload_returns_not_ready(self, _build):
        r = copy.deepcopy(_make_clean_record())
        r["apply_execution_gate_request"] = None
        c = _build(r)
        assert c["decision"] == "not_ready"
        assert c["contract_required"] is False


# ======================== TESTS 30-45: BOUNDARY, ROLLBACK, EVIDENCE, CONTENT ======================== #

class TestBoundaryRollbackEvidenceContent:
    def test_execution_boundary_exists_for_ready(self, _build, clean_aeg_record):
        c = _build(clean_aeg_record)
        assert c["execution_boundary"] is not None
        assert c["execution_boundary"]["execution_scope"] == "contract_only_no_execution"

    def test_execution_boundary_for_blocked(self, _build):
        c = _build(None)
        assert c["execution_boundary"] is not None
        assert c["execution_boundary"]["execution_scope"] == "blocked_or_not_ready_no_execution"

    def test_execution_boundary_forbidden_capabilities(self, _build, clean_aeg_record):
        c = _build(clean_aeg_record)
        fc = c["execution_boundary"]["forbidden_capabilities"]
        assert "shell" in fc
        assert "subprocess" in fc
        assert "identity_modification" in fc
        assert "self_repair" in fc

    def test_rollback_expectation_exists(self, _build, clean_aeg_record):
        c = _build(clean_aeg_record)
        re_obj = c["rollback_expectation"]
        assert re_obj["rollback_required_before_future_apply"] is True
        assert re_obj["rollback_plan_required"] is True
        assert re_obj["rollback_plan_present"] is False
        assert re_obj["rollback_verified"] is False
        assert re_obj["rollback_allowed"] is False
        assert re_obj["rollback_executed"] is False

    def test_evidence_requirements_all_5_names(self, _build, clean_aeg_record):
        c = _build(clean_aeg_record)
        er = c["evidence_requirements"]
        names = [e["name"] for e in er]
        expected_names = [
            "pre_execution_state_evidence",
            "execution_result_evidence",
            "post_execution_verification_evidence",
            "rollback_evidence",
            "audit_log_evidence",
        ]
        for n in expected_names:
            assert n in names, f"Missing evidence: {n}"

    def test_all_evidence_satisfied_false(self, _build, clean_aeg_record):
        c = _build(clean_aeg_record)
        for e in c["evidence_requirements"]:
            assert e["satisfied"] is False

    def test_required_executor_confirmations_included(self, _build, clean_aeg_record):
        c = _build(clean_aeg_record)
        rc = c["required_executor_confirmations"]
        assert len(rc) >= 6
        assert any("execution gate intent" in l.lower() for l in rc)
        assert any("separate future apply executor" in l.lower() for l in rc)

    def test_contract_statement_present_only_for_ready(self, _build, clean_aeg_record):
        c = _build(clean_aeg_record)
        assert c["contract_statement"] is not None
        assert "does not authorize or execute apply" in c["contract_statement"]

    def test_contract_statement_none_for_blocked(self, _build):
        c = _build(None)
        assert c["contract_statement"] is None

    def test_recommended_next_step_for_ready(self, _build, clean_aeg_record):
        c = _build(clean_aeg_record)
        step = c["recommended_next_step"]
        assert "persist" in step.lower()
        assert "do not execute" in step.lower() or "not execute" in step.lower()

    def test_metadata_source_schema_version_session_id(self, _build, clean_aeg_record):
        c = _build(clean_aeg_record, context={"session_id": "71a-sid"})
        meta = c["metadata"]
        assert meta["source"] == "apply_executor_contract_builder"
        assert meta["schema_version"] == "1.0"
        assert meta["session_id"] == "71a-sid"

    def test_warnings_include_no_execution_authorization(self, _build, clean_aeg_record):
        c = _build(clean_aeg_record)
        warns_text = " ".join(c["warnings"])
        assert "does not authorize execution" in warns_text

    def test_request_warnings_copied_with_prefix(self, _build, clean_aeg_record):
        c = _build(clean_aeg_record)
        warns_text = " ".join(c["warnings"])
        assert "apply_execution_gate_request_warning:" in warns_text

    def test_requested_action_copied(self, _build, clean_aeg_record):
        c = _build(clean_aeg_record)
        ra = c["requested_action"]
        assert ra is not None
        assert ra["tool_id"] == "test.tool"

    def test_link_ids_copied(self, _build, clean_aeg_record):
        c = _build(clean_aeg_record)
        assert c["apply_execution_gate_id"] == "aeg-001"
        assert c["human_authorization_id"] == "ha-001"
        assert c["apply_gate_id"] == "ag-001"
        assert c["verification_verdict_id"] == "vv-001"
        assert c["simulation_result_id"] == "sim-001"
        assert c["simulation_plan_id"] == "plan-1"
        assert c["dry_run_id"] == "dr-1"
