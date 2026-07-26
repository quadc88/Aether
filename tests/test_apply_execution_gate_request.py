"""Tests for Apply Execution Gate Request Builder (Milestone 69A).

Verifies that build_apply_execution_gate_request produces correct requests
from human_authorization_records. No execution, apply, or rollback occurs.
"""

from __future__ import annotations

import pytest


@pytest.fixture()
def _build():
    from aether.action.apply_execution_gate_request import build_apply_execution_gate_request
    return build_apply_execution_gate_request


@pytest.fixture()
def ready_haar():
    return {
        "decision": "ready_for_human_authorization",
        "reason": "Ready.",
        "human_authorization_required": True,
        "apply_gate_id": "ag-001",
        "verification_verdict_id": "vv-001",
        "simulation_result_id": "sim-001",
        "simulation_plan_id": "plan-1",
        "dry_run_id": "dr-1",
        "requested_action": {"tool_id": "test.tool", "action_type": "status_check"},
        "required_human_confirmations": [
            "c1", "c2", "c3", "c4", "c5", "c6",
        ],
        "blocking_reasons": [],
        "unresolved_risks": [],
        "recommended_next_step": "Proceed.",
        "apply_authorized": False,
        "apply_allowed": False,
        "rollback_allowed": False,
        "execution_allowed": False,
        "tool_execution_allowed": False,
        "dry_run_execution_allowed": False,
        "simulation_execution_allowed": False,
        "apply_gate_execution_allowed": False,
        "human_authorization_execution_allowed": False,
        "metadata": {"source": "human_apply_authorization_request_builder", "schema_version": "1.0"},
        "warnings": [],
    }


@pytest.fixture()
def not_ready_haar():
    return {
        "decision": "not_ready",
        "reason": "Not ready.",
        "human_authorization_required": False,
        "apply_gate_id": None,
        "verification_verdict_id": None,
        "simulation_result_id": None,
        "simulation_plan_id": None,
        "dry_run_id": None,
        "requested_action": None,
        "required_human_confirmations": [],
        "blocking_reasons": ["some reason"],
        "unresolved_risks": [],
        "recommended_next_step": "Resolve issues.",
        "apply_authorized": False,
        "apply_allowed": False,
        "rollback_allowed": False,
        "execution_allowed": False,
        "tool_execution_allowed": False,
        "dry_run_execution_allowed": False,
        "simulation_execution_allowed": False,
        "apply_gate_execution_allowed": False,
        "human_authorization_execution_allowed": False,
        "metadata": {},
        "warnings": [],
    }


@pytest.fixture()
def blocked_haar():
    return {
        "decision": "blocked",
        "reason": "Blocked.",
        "human_authorization_required": False,
        "apply_gate_id": None,
        "verification_verdict_id": None,
        "simulation_result_id": None,
        "simulation_plan_id": None,
        "dry_run_id": None,
        "requested_action": None,
        "required_human_confirmations": [],
        "blocking_reasons": ["blocked"],
        "unresolved_risks": [],
        "recommended_next_step": "Resolve conditions.",
        "apply_authorized": False,
        "apply_allowed": False,
        "rollback_allowed": False,
        "execution_allowed": False,
        "tool_execution_allowed": False,
        "dry_run_execution_allowed": False,
        "simulation_execution_allowed": False,
        "apply_gate_execution_allowed": False,
        "human_authorization_execution_allowed": False,
        "metadata": {},
        "warnings": [],
    }


@pytest.fixture()
def clean_ha_rec(ready_haar):
    """A fully compliant approved_intent human authorization record."""
    import copy
    return {
        "human_authorization_id": "ha-001",
        "status": "approved_intent",
        "human_apply_authorization_request": dict(ready_haar),
        "authorization_decision": "ready_for_human_authorization",
        "apply_gate_id": "ag-001",
        "verification_verdict_id": "vv-001",
        "simulation_result_id": "sim-001",
        "simulation_plan_id": "plan-1",
        "dry_run_id": "dr-1",
        "created_at": "2026-01-01T00:00:00+00:00",
        "updated_at": "2026-01-01T00:00:00+00:00",
        "decision": "approved_intent",
        "decided_at": "2026-01-01T00:00:01+00:00",
        "reviewer": "test",
        "decision_reason": "approved",
        "confirmations_required": ["c1", "c2", "c3", "c4", "c5", "c6"],
        "confirmations_received": ["c1", "c2", "c3", "c4", "c5", "c6"],
        "human_authorization_persisted": True,
        "human_review_completed": True,
        "human_intent_recorded": True,
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
        "apply_allowed": False,
        "rollback_allowed": False,
        "metadata": {},
        "warnings": [],
    }


# ======================== TESTS 1-11: REJECTION CASES ======================== #

class TestRejectionCases:
    def test_missing_record_returns_blocked(self, _build):
        agr = _build(None)
        assert agr["decision"] == "blocked"
        assert agr["apply_execution_gate_required"] is False

    def test_pending_record_returns_blocked(self, _build, clean_ha_rec):
        clean_ha_rec["status"] = "pending"
        agr = _build(clean_ha_rec)
        assert agr["decision"] == "blocked"
        assert "not approved_intent" in agr["reason"].lower()

    def test_rejected_record_returns_blocked(self, _build, clean_ha_rec):
        clean_ha_rec["status"] = "rejected"
        agr = _build(clean_ha_rec)
        assert agr["decision"] == "blocked"

    def test_cancelled_record_returns_blocked(self, _build, clean_ha_rec):
        clean_ha_rec["status"] = "cancelled"
        agr = _build(clean_ha_rec)
        assert agr["decision"] == "blocked"

    def test_auth_decision_not_ready_returns_blocked(self, _build, clean_ha_rec):
        clean_ha_rec["authorization_decision"] = "not_ready"
        agr = _build(clean_ha_rec)
        assert agr["decision"] == "blocked"

    def test_human_intent_not_recorded_returns_blocked(self, _build, clean_ha_rec):
        clean_ha_rec["human_intent_recorded"] = False
        agr = _build(clean_ha_rec)
        assert agr["decision"] == "blocked"

    def test_human_review_not_completed_returns_blocked(self, _build, clean_ha_rec):
        clean_ha_rec["human_review_completed"] = False
        agr = _build(clean_ha_rec)
        assert agr["decision"] == "blocked"

    def test_apply_authorized_true_returns_blocked(self, _build, clean_ha_rec):
        clean_ha_rec["apply_authorized"] = True
        agr = _build(clean_ha_rec)
        assert agr["decision"] == "blocked"

    def test_apply_executed_true_returns_blocked(self, _build, clean_ha_rec):
        clean_ha_rec["apply_executed"] = True
        agr = _build(clean_ha_rec)
        assert agr["decision"] == "blocked"

    def test_rollback_executed_true_returns_blocked(self, _build, clean_ha_rec):
        clean_ha_rec["rollback_executed"] = True
        agr = _build(clean_ha_rec)
        assert agr["decision"] == "blocked"

    def test_missing_haar_returns_not_ready(self, _build, clean_ha_rec):
        clean_ha_rec["human_apply_authorization_request"] = None
        agr = _build(clean_ha_rec)
        assert agr["decision"] == "not_ready"


# ======================== TESTS 12-17: CLEAN READY CASE ======================== #

class TestCleanReadyCase:
    def test_eligible_returns_ready_for_execution_gate_review(self, _build, clean_ha_rec):
        agr = _build(clean_ha_rec)
        assert agr["decision"] == "ready_for_execution_gate_review"
        assert agr["apply_execution_gate_required"] is True

    def test_ready_still_has_apply_authorized_false(self, _build, clean_ha_rec):
        agr = _build(clean_ha_rec)
        assert agr["apply_authorized"] is False

    def test_ready_still_has_apply_allowed_false(self, _build, clean_ha_rec):
        agr = _build(clean_ha_rec)
        assert agr["apply_allowed"] is False

    def test_ready_still_all_flags_false(self, _build, clean_ha_rec):
        agr = _build(clean_ha_rec)
        assert agr["execution_allowed"] is False
        assert agr["tool_execution_allowed"] is False
        assert agr["dry_run_execution_allowed"] is False
        assert agr["simulation_execution_allowed"] is False
        assert agr["apply_gate_execution_allowed"] is False
        assert agr["human_authorization_execution_allowed"] is False
        assert agr["apply_execution_gate_execution_allowed"] is False


# ======================== TESTS 18-19: PRE_EXECUTION CHECKS ======================== #

class TestPreExecutionChecks:
    def test_includes_all_14_checks(self, _build, clean_ha_rec):
        agr = _build(clean_ha_rec)
        names = [c["name"] for c in agr["pre_execution_checks"]]
        expected = [
            "human_authorization_approved_intent",
            "human_authorization_persisted",
            "authorization_decision_ready",
            "human_review_completed",
            "human_intent_recorded",
            "confirmations_received",
            "request_ready_for_human_authorization",
            "apply_not_authorized",
            "apply_not_executed",
            "rollback_not_executed",
            "execution_flags_blocked",
            "apply_flags_blocked",
            "requested_action_present",
            "blocking_reasons_empty",
        ]
        for name in expected:
            assert name in names, f"Missing check: {name}"

    def test_all_checks_pass_for_clean_record(self, _build, clean_ha_rec):
        agr = _build(clean_ha_rec)
        for c in agr["pre_execution_checks"]:
            assert c["passed"] is True, f"Check {c['name']} should pass but returned {c}"


# ======================== TESTS 20-23: SEVERITY-BASED DECISIONS ======================== #

class TestSeverityDecisions:
    def test_critical_failure_blocks(self, _build):
        ha_rec = {
            "human_authorization_id": "test",
            "status": "approved_intent",
            "authorization_decision": "ready_for_human_authorization",
            "human_intent_recorded": True,
            "human_review_completed": True,
            "apply_authorized": True,  # Critical fail
            "apply_executed": False,
            "rollback_executed": False,
            "human_authorization_persisted": True,
            "apply_allowed": False,
            "rollback_allowed": False,
            "execution_allowed": False,
            "tool_execution_allowed": False,
            "dry_run_execution_allowed": False,
            "simulation_execution_allowed": False,
            "apply_gate_execution_allowed": False,
            "human_authorization_execution_allowed": False,
            "confirmations_required": ["c1"],
            "confirmations_received": ["c1"],
            "human_apply_authorization_request": {
                "decision": "ready_for_human_authorization",
                "requested_action": {"tool_id": "t"},
                "blocking_reasons": [],
                "apply_authorized": False,
                "apply_allowed": False,
                "rollback_allowed": False,
                "execution_allowed": False,
                "tool_execution_allowed": False,
                "dry_run_execution_allowed": False,
                "simulation_execution_allowed": False,
                "apply_gate_execution_allowed": False,
                "human_authorization_execution_allowed": False,
                "metadata": {},
                "warnings": [],
            },
            "metadata": {},
            "warnings": [],
        }
        agr = _build(ha_rec)
        assert agr["decision"] == "blocked"

    def test_high_failure_blocks(self, _build):
        ha_rec = {
            "human_authorization_id": "test",
            "status": "approved_intent",
            "authorization_decision": "blocked",  # High severity fail
            "human_intent_recorded": True,
            "human_review_completed": True,
            "apply_authorized": False,
            "apply_executed": False,
            "rollback_executed": False,
            "human_authorization_persisted": True,
            "apply_allowed": False,
            "rollback_allowed": False,
            "execution_allowed": False,
            "tool_execution_allowed": False,
            "dry_run_execution_allowed": False,
            "simulation_execution_allowed": False,
            "apply_gate_execution_allowed": False,
            "human_authorization_execution_allowed": False,
            "confirmations_required": ["c1"],
            "confirmations_received": ["c1"],
            "human_apply_authorization_request": {
                "decision": "blocked",
                "requested_action": {"tool_id": "t"},
                "blocking_reasons": [],
                "apply_authorized": False,
                "apply_allowed": False,
                "rollback_allowed": False,
                "execution_allowed": False,
                "tool_execution_allowed": False,
                "dry_run_execution_allowed": False,
                "simulation_execution_allowed": False,
                "apply_gate_execution_allowed": False,
                "human_authorization_execution_allowed": False,
                "metadata": {},
                "warnings": [],
            },
            "metadata": {},
            "warnings": [],
        }
        agr = _build(ha_rec)
        assert agr["decision"] == "blocked"

    def test_medium_failure_returns_not_ready(self, _build):
        ha_rec = {
            "human_authorization_id": "test",
            "status": "approved_intent",
            "authorization_decision": "ready_for_human_authorization",
            "human_intent_recorded": True,
            "human_review_completed": True,
            "apply_authorized": False,
            "apply_executed": False,
            "rollback_executed": False,
            "human_authorization_persisted": True,
            "apply_allowed": False,
            "rollback_allowed": False,
            "execution_allowed": False,
            "tool_execution_allowed": False,
            "dry_run_execution_allowed": False,
            "simulation_execution_allowed": False,
            "apply_gate_execution_allowed": False,
            "human_authorization_execution_allowed": False,
            "confirmations_required": ["c1"],
            "confirmations_received": ["c1"],
            "human_apply_authorization_request": {
                "decision": "ready_for_human_authorization",
                "requested_action": {"tool_id": "t"},
                "blocking_reasons": ["some_block"],  # Medium severity fail
                "apply_authorized": False,
                "apply_allowed": False,
                "rollback_allowed": False,
                "execution_allowed": False,
                "tool_execution_allowed": False,
                "dry_run_execution_allowed": False,
                "simulation_execution_allowed": False,
                "apply_gate_execution_allowed": False,
                "human_authorization_execution_allowed": False,
                "metadata": {},
                "warnings": [],
            },
            "metadata": {},
            "warnings": [],
        }
        agr = _build(ha_rec)
        assert agr["decision"] == "not_ready"

    def test_low_failure_returns_not_ready(self, _build):
        ha_rec = {
            "human_authorization_id": "test",
            "status": "approved_intent",
            "authorization_decision": "ready_for_human_authorization",
            "human_intent_recorded": True,
            "human_review_completed": True,
            "apply_authorized": False,
            "apply_executed": False,
            "rollback_executed": False,
            "human_authorization_persisted": False,  # Low severity fail
            "apply_allowed": False,
            "rollback_allowed": False,
            "execution_allowed": False,
            "tool_execution_allowed": False,
            "dry_run_execution_allowed": False,
            "simulation_execution_allowed": False,
            "apply_gate_execution_allowed": False,
            "human_authorization_execution_allowed": False,
            "confirmations_required": ["c1"],
            "confirmations_received": ["c1"],
            "human_apply_authorization_request": {
                "decision": "ready_for_human_authorization",
                "requested_action": {"tool_id": "t"},
                "blocking_reasons": [],
                "apply_authorized": False,
                "apply_allowed": False,
                "rollback_allowed": False,
                "execution_allowed": False,
                "tool_execution_allowed": False,
                "dry_run_execution_allowed": False,
                "simulation_execution_allowed": False,
                "apply_gate_execution_allowed": False,
                "human_authorization_execution_allowed": False,
                "metadata": {},
                "warnings": [],
            },
            "metadata": {},
            "warnings": [],
        }
        agr = _build(ha_rec)
        assert agr["decision"] == "not_ready"


# ======================== TESTS 24-26: SPECIFIC CHECK BEHAVIORS ======================== #

class TestSpecificChecks:
    def test_confirmations_received_passes_when_covered(self, _build, clean_ha_rec):
        agr = _build(clean_ha_rec)
        chk = next(c for c in agr["pre_execution_checks"] if c["name"] == "confirmations_received")
        assert chk["passed"] is True

    def test_confirmations_received_fails_when_missing(self, _build):
        import copy
        ha_rec = copy.deepcopy(_get_clean())
        ha_rec["confirmations_received"] = []  # Missing confirmations
        agr = _build(ha_rec)
        chk = next(c for c in agr["pre_execution_checks"] if c["name"] == "confirmations_received")
        assert chk["passed"] is False
        assert agr["decision"] == "not_ready"

    def test_requested_action_present_fails_when_missing(self, _build):
        import copy
        ha_rec = copy.deepcopy(_get_clean())
        ha_rec["human_apply_authorization_request"]["requested_action"] = None
        agr = _build(ha_rec)
        chk = next(c for c in agr["pre_execution_checks"] if c["name"] == "requested_action_present")
        assert chk["passed"] is False
        assert agr["decision"] == "not_ready"

    def test_blocking_reasons_empty_fails_when_present(self, _build):
        import copy
        ha_rec = copy.deepcopy(_get_clean())
        ha_rec["human_apply_authorization_request"]["blocking_reasons"] = ["some_block"]
        agr = _build(ha_rec)
        chk = next(c for c in agr["pre_execution_checks"] if c["name"] == "blocking_reasons_empty")
        assert chk["passed"] is False


def _get_clean():
    import copy
    return {
        "human_authorization_id": "ha-001", "status": "approved_intent",
        "human_apply_authorization_request": {
            "decision": "ready_for_human_authorization",
            "requested_action": {"tool_id": "t"},
            "blocking_reasons": [],
            "apply_authorized": False, "apply_allowed": False, "rollback_allowed": False,
            "execution_allowed": False, "tool_execution_allowed": False,
            "dry_run_execution_allowed": False, "simulation_execution_allowed": False,
            "apply_gate_execution_allowed": False, "human_authorization_execution_allowed": False,
            "metadata": {}, "warnings": [],
        },
        "authorization_decision": "ready_for_human_authorization",
        "apply_gate_id": "ag-001", "verification_verdict_id": "vv-001",
        "simulation_result_id": "sim-001", "simulation_plan_id": "plan-1", "dry_run_id": "dr-1",
        "human_review_completed": True, "human_intent_recorded": True,
        "apply_authorized": False, "apply_executed": False, "rollback_executed": False,
        "human_authorization_persisted": True, "apply_allowed": False, "rollback_allowed": False,
        "execution_allowed": False, "tool_execution_allowed": False,
        "dry_run_execution_allowed": False, "simulation_execution_allowed": False,
        "apply_gate_execution_allowed": False, "human_authorization_execution_allowed": False,
        "confirmations_required": ["c1"], "confirmations_received": ["c1"],
        "metadata": {}, "warnings": [],
    }


# ======================== TESTS 27-35: CONTENT CHECKS ======================== #

class TestContentChecks:
    def test_required_pre_execution_confirmations_included(self, _build, clean_ha_rec):
        agr = _build(clean_ha_rec)
        confs = agr["required_pre_execution_confirmations"]
        assert len(confs) >= 6
        assert any("human approval intent" in c.lower() for c in confs)
        assert any("separate future apply executor" in c.lower() for c in confs)

    def test_execution_statement_present_only_for_ready(self, _build, clean_ha_rec):
        agr = _build(clean_ha_rec)
        assert agr["execution_statement"] is not None
        assert "Apply execution gate review is required" in agr["execution_statement"]
        assert "does not authorize or execute apply" in agr["execution_statement"]

    def test_execution_statement_none_for_blocked(self, _build):
        agr = _build(None)
        assert agr["execution_statement"] is None

    def test_recommended_next_step_for_ready(self, _build, clean_ha_rec):
        agr = _build(clean_ha_rec)
        step = agr["recommended_next_step"]
        assert "execution gate" in step.lower()
        assert "do not execute" in step.lower() or "not execute" in step.lower()

    def test_metadata_source_and_schema_version(self, _build, clean_ha_rec):
        agr = _build(clean_ha_rec)
        meta = agr["metadata"]
        assert meta["source"] == "apply_execution_gate_request_builder"
        assert meta["schema_version"] == "1.0"

    def test_context_session_id_copied(self, _build, clean_ha_rec):
        agr = _build(clean_ha_rec, context={"session_id": "manual-69a-sid"})
        assert agr["metadata"]["session_id"] == "manual-69a-sid"

    def test_warnings_include_no_execution_authorization(self, _build, clean_ha_rec):
        agr = _build(clean_ha_rec)
        warns_text = " ".join(agr["warnings"])
        assert "does not authorize execution" in warns_text

    def test_haar_warnings_copied_with_prefix(self, _build, clean_ha_rec):
        import copy
        ha_rec = copy.deepcopy(clean_ha_rec)
        ha_rec["human_apply_authorization_request"]["warnings"] = ["custom ha warning"]
        agr = _build(ha_rec)
        assert any(
            "human_authorization_request_warning: custom ha warning" in w
            for w in agr["warnings"]
        )

    def test_requested_action_copied(self, _build, clean_ha_rec):
        agr = _build(clean_ha_rec)
        ra = agr["requested_action"]
        assert ra is not None
        assert ra["tool_id"] == "test.tool"

    def test_link_ids_copied(self, _build, clean_ha_rec):
        agr = _build(clean_ha_rec)
        assert agr["apply_gate_id"] == "ag-001"
        assert agr["verification_verdict_id"] == "vv-001"
        assert agr["simulation_result_id"] == "sim-001"
        assert agr["simulation_plan_id"] == "plan-1"
        assert agr["dry_run_id"] == "dr-1"
