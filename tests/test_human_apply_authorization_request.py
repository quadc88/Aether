"""Tests for Human Apply Authorization Request Builder (Milestone 67A).

Verifies that build_human_apply_authorization_request produces correct requests
from apply_gate_records. No execution, apply, or rollback occurs.
"""

from __future__ import annotations

import pytest


@pytest.fixture()
def _build():
    from aether.action.human_apply_authorization_request import build_human_apply_authorization_request
    return build_human_apply_authorization_request


@pytest.fixture()
def clean_eligible_agr():
    """Create a clean eligible apply gate request object."""
    return {
        "decision": "eligible_for_human_review",
        "reason": "All eligibility checks passed.",
        "apply_gate_required": True,
        "verification_verdict_id": "vv-001",
        "simulation_result_id": "sim-001",
        "simulation_plan_id": "plan-1",
        "dry_run_id": "dr-1",
        "requested_action": {"tool_id": "test.tool", "action_type": "status_check"},
        "eligibility_checks": [],
        "required_human_confirmations": [
            "Confirm the requested action is still desired.",
            "Confirm the target is correct.",
            "Confirm the dry-run and verification evidence are acceptable.",
            "Confirm rollback limitations are understood.",
            "Confirm this request should proceed to a future apply authorization gate.",
        ],
        "blocking_reasons": [],
        "unresolved_risks": [{"name": "real_apply_not_authorized", "severity": "medium"}],
        "recommended_next_step": "Proceed.",
        "apply_authorized": False,
        "apply_allowed": False,
        "rollback_allowed": False,
        "execution_allowed": False,
        "tool_execution_allowed": False,
        "dry_run_execution_allowed": False,
        "simulation_execution_allowed": False,
        "apply_gate_execution_allowed": False,
        "metadata": {"source": "apply_gate_request_builder", "schema_version": "1.0"},
        "warnings": [],
    }


@pytest.fixture()
def clean_ag_record(clean_eligible_agr):
    """Create a complete pending apply gate record with clean eligible agr."""
    return {
        "apply_gate_id": "ag-001",
        "status": "pending",
        "apply_gate_request": clean_eligible_agr,
        "gate_decision": "eligible_for_human_review",
        "verification_verdict_id": "vv-001",
        "simulation_result_id": "sim-001",
        "simulation_plan_id": "plan-1",
        "dry_run_id": "dr-1",
        "created_at": "2026-01-01T00:00:00+00:00",
        "updated_at": "2026-01-01T00:00:00+00:00",
        "decision": "eligible_for_human_review",
        "decided_at": None,
        "reviewer": None,
        "decision_reason": None,
        "apply_gate_persisted": True,
        "human_review_completed": False,
        "apply_authorized": False,
        "apply_executed": False,
        "rollback_executed": False,
        "simulation_executed": False,
        "execution_allowed": False,
        "tool_execution_allowed": False,
        "dry_run_execution_allowed": False,
        "simulation_execution_allowed": False,
        "apply_gate_execution_allowed": False,
        "apply_allowed": False,
        "rollback_allowed": False,
        "metadata": {},
        "warnings": [],
    }


# ======================== TESTS 1-3: MISSING/CANCELLED/APPLY_AUTH_TRUE ======================== #

class TestMissingAndBlockedCases:
    def test_missing_record_returns_blocked(self, _build):
        agr = _build(apply_gate_record=None)
        assert agr["decision"] == "blocked"
        assert agr["reason"] == "Apply gate record was not found."
        assert agr["human_authorization_required"] is False
        assert agr["apply_authorized"] is False

    def test_cancelled_record_returns_blocked(self, _build, clean_ag_record):
        clean_ag_record["status"] = "cancelled"
        agr = _build(clean_ag_record)
        assert agr["decision"] == "blocked"
        assert "not pending" in agr["reason"].lower()
        assert agr["human_authorization_required"] is False

    def test_apply_authorized_true_returns_blocked(self, _build, clean_ag_record):
        clean_ag_record["apply_authorized"] = True
        agr = _build(clean_ag_record)
        assert agr["decision"] == "blocked"
        assert "apply-authorized" in agr["reason"].lower()
        assert agr["human_authorization_required"] is False

    def test_apply_executed_true_returns_blocked(self, _build, clean_ag_record):
        clean_ag_record["apply_executed"] = True
        agr = _build(clean_ag_record)
        assert agr["decision"] == "blocked"

    def test_rollback_executed_true_returns_blocked(self, _build, clean_ag_record):
        clean_ag_record["rollback_executed"] = True
        agr = _build(clean_ag_record)
        assert agr["decision"] == "blocked"


# ======================== TESTS 4-9: GATE DECISION HANDLING ======================== #

class TestGateDecisions:
    def test_missing_agr_returns_not_ready(self, _build):
        rec = {
            "apply_gate_id": "no-agr-id", "status": "pending",
            "apply_gate_request": None, "gate_decision": None,
            "apply_authorized": False, "apply_executed": False, "rollback_executed": False,
        }
        agr = _build(rec)
        assert agr["decision"] == "not_ready"

    def test_not_eligible_returns_not_ready(self, _build):
        agr_req = {
            "decision": "not_eligible", "required_human_confirmations": [],
            "blocking_reasons": [], "unresolved_risks": [],
            "apply_authorized": False, "execution_allowed": False,
            "tool_execution_allowed": False, "apply_allowed": False,
            "metadata": {}, "warnings": [],
        }
        rec = {
            "apply_gate_id": "ne-agr", "status": "pending",
            "apply_gate_request": agr_req, "gate_decision": "not_eligible",
            "apply_authorized": False, "apply_executed": False, "rollback_executed": False,
            "apply_gate_persisted": True, "human_review_completed": False,
            "execution_allowed": False, "tool_execution_allowed": False,
            "dry_run_execution_allowed": False, "simulation_execution_allowed": False,
            "apply_gate_execution_allowed": False, "apply_allowed": False, "rollback_allowed": False,
            "metadata": {}, "warnings": [],
        }
        agr = _build(rec)
        assert agr["decision"] == "not_ready"

    def test_blocked_gate_returns_blocked(self, _build):
        agr_req = {
            "decision": "blocked", "required_human_confirmations": [],
            "blocking_reasons": ["some_block"], "unresolved_risks": [],
            "apply_authorized": False, "execution_allowed": False,
            "tool_execution_allowed": False, "apply_allowed": False,
            "metadata": {}, "warnings": [],
        }
        rec = {
            "apply_gate_id": "blk-agr", "status": "pending",
            "apply_gate_request": agr_req, "gate_decision": "blocked",
            "apply_authorized": False, "apply_executed": False, "rollback_executed": False,
            "apply_gate_persisted": True, "human_review_completed": False,
            "execution_allowed": False, "tool_execution_allowed": False,
            "dry_run_execution_allowed": False, "simulation_execution_allowed": False,
            "apply_gate_execution_allowed": False, "apply_allowed": False, "rollback_allowed": False,
            "metadata": {}, "warnings": [],
        }
        agr = _build(rec)
        assert agr["decision"] == "blocked"

    def test_unknown_gate_decision_returns_blocked(self, _build):
        agr_req = {
            "decision": "unknown_xyz", "required_human_confirmations": [],
            "blocking_reasons": [], "unresolved_risks": [],
            "apply_authorized": False, "execution_allowed": False,
            "tool_execution_allowed": False, "apply_allowed": False,
            "metadata": {}, "warnings": [],
        }
        rec = {
            "apply_gate_id": "unk-agr", "status": "pending",
            "apply_gate_request": agr_req, "gate_decision": "unknown_xyz",
            "apply_authorized": False, "apply_executed": False, "rollback_executed": False,
            "apply_gate_persisted": True, "human_review_completed": False,
            "execution_allowed": False, "tool_execution_allowed": False,
            "dry_run_execution_allowed": False, "simulation_execution_allowed": False,
            "apply_gate_execution_allowed": False, "apply_allowed": False, "rollback_allowed": False,
            "metadata": {}, "warnings": [],
        }
        agr = _build(rec)
        assert agr["decision"] == "blocked"


# ======================== TEST 10-15: CLEAN ELIGIBLE CASE ======================== #

class TestCleanEligible:
    def test_eligible_returns_ready_for_human_authorization(self, _build, clean_ag_record):
        agr = _build(clean_ag_record)
        assert agr["decision"] == "ready_for_human_authorization"
        assert agr["human_authorization_required"] is True

    def test_ready_still_has_human_review_completed_false(self, _build, clean_ag_record):
        agr = _build(clean_ag_record)
        assert agr["human_review_completed"] is False

    def test_ready_still_has_apply_authorized_false(self, _build, clean_ag_record):
        agr = _build(clean_ag_record)
        assert agr["apply_authorized"] is False

    def test_ready_still_has_apply_allowed_false(self, _build, clean_ag_record):
        agr = _build(clean_ag_record)
        assert agr["apply_allowed"] is False

    def test_ready_all_flags_false(self, _build, clean_ag_record):
        agr = _build(clean_ag_record)
        assert agr["execution_allowed"] is False
        assert agr["tool_execution_allowed"] is False
        assert agr["dry_run_execution_allowed"] is False
        assert agr["simulation_execution_allowed"] is False
        assert agr["apply_gate_execution_allowed"] is False
        assert agr["human_authorization_execution_allowed"] is False


# ======================== TEST 16-17: READINESS CHECKS ======================== #

class TestReadinessChecks:
    def test_includes_all_11_checks(self, _build, clean_ag_record):
        agr = _build(clean_ag_record)
        names = [c["name"] for c in agr["readiness_checks"]]
        expected = [
            "apply_gate_record_pending", "apply_gate_persisted", "gate_decision_eligible",
            "human_review_not_completed", "apply_not_authorized", "apply_not_executed",
            "rollback_not_executed", "execution_flags_blocked", "apply_flags_blocked",
            "required_confirmations_present", "blocking_reasons_empty",
        ]
        for name in expected:
            assert name in names, f"Missing check: {name}"

    def test_all_checks_pass_for_clean_record(self, _build, clean_ag_record):
        agr = _build(clean_ag_record)
        for c in agr["readiness_checks"]:
            assert c["passed"] is True, f"Check {c['name']} should pass but returned {c}"


# ======================== TESTS 18-21: SEVERITY-BASED DECISIONS ======================== #

class TestSeverityDecisions:
    def _make_rec(self, **overrides):
        base = {
            "apply_gate_id": "sev-test", "status": "pending",
            "apply_gate_request": {
                "decision": "eligible_for_human_review", "required_human_confirmations": [
                    "confirm 1", "confirm 2", "confirm 3", "confirm 4", "confirm 5",
                ], "blocking_reasons": [], "unresolved_risks": [],
                "apply_authorized": False, "execution_allowed": False,
                "tool_execution_allowed": False, "dry_run_execution_allowed": False,
                "simulation_execution_allowed": False, "apply_gate_execution_allowed": False,
                "apply_allowed": False, "rollback_allowed": False,
                "metadata": {}, "warnings": [],
            },
            "gate_decision": "eligible_for_human_review",
            "apply_authorized": False, "apply_executed": False, "rollback_executed": False,
            "apply_gate_persisted": True, "human_review_completed": False,
            "execution_allowed": False, "tool_execution_allowed": False,
            "dry_run_execution_allowed": False, "simulation_execution_allowed": False,
            "apply_gate_execution_allowed": False, "apply_allowed": False, "rollback_allowed": False,
            "metadata": {}, "warnings": [],
        }
        base.update(overrides)
        return base

    def test_critical_failure_blocks(self, _build):
        rec = self._make_rec(apply_authorized=True)
        agr = _build(rec)
        assert agr["decision"] == "blocked"

    def test_high_failure_blocks(self, _build):
        # Break gate_decision_eligible by changing gate_decision
        rec = self._make_rec(gate_decision="blocked")
        agr = _build(rec)
        assert agr["decision"] == "blocked"

    def test_medium_failure_returns_not_ready(self, _build):
        # Break blocking_reasons_empty
        rec = self._make_rec(**{"apply_gate_request.blocking_reasons": ["some_reason"]})
        rec["apply_gate_request"]["blocking_reasons"] = ["some_reason"]
        agr = _build(rec)
        assert agr["decision"] == "not_ready"

    def test_low_failure_returns_not_ready(self, _build):
        # Break apply_gate_persisted
        rec = self._make_rec(apply_gate_persisted=False)
        agr = _build(rec)
        assert agr["decision"] == "not_ready"


# ======================== TESTS 22-30: CONTENT CHECKS ======================== #

class TestContentChecks:
    def test_required_human_confirmations_included(self, _build, clean_ag_record):
        agr = _build(clean_ag_record)
        confs = agr["required_human_confirmations"]
        assert len(confs) >= 6
        assert any("I confirm the requested action" in c for c in confs)
        assert any("separate future apply executor" in c for c in confs)

    def test_authorization_statement_only_for_ready(self, _build, clean_ag_record):
        agr = _build(clean_ag_record)
        assert agr["authorization_statement"] is not None
        assert "Human authorization is required" in agr["authorization_statement"]

    def test_authorization_statement_none_for_blocked(self, _build):
        agr = _build(None)
        assert agr["authorization_statement"] is None

    def test_recommended_next_step_for_ready(self, _build, clean_ag_record):
        agr = _build(clean_ag_record)
        step = agr["recommended_next_step"]
        assert "human reviewer" in step.lower() or "human" in step.lower()
        assert "do not apply" in step.lower() or "not apply" in step.lower()

    def test_metadata_source_and_schema_version(self, _build, clean_ag_record):
        agr = _build(clean_ag_record)
        meta = agr["metadata"]
        assert meta["source"] == "human_apply_authorization_request_builder"
        assert meta["schema_version"] == "1.0"

    def test_context_session_id_copied(self, _build, clean_ag_record):
        agr = _build(clean_ag_record, context={"session_id": "manual-67a-sid"})
        assert agr["metadata"]["session_id"] == "manual-67a-sid"

    def test_warnings_include_no_apply_authorization(self, _build, clean_ag_record):
        agr = _build(clean_ag_record)
        warns_text = " ".join(agr["warnings"])
        assert "does not authorize apply" in warns_text

    def test_apply_gate_request_warnings_copied_with_prefix(self, _build, clean_ag_record):
        clean_ag_record["apply_gate_request"]["warnings"] = ["custom agr warning"]
        agr = _build(clean_ag_record)
        assert any("apply_gate_request_warning: custom agr warning" in w for w in agr["warnings"])

    def test_requested_action_copied(self, _build, clean_ag_record):
        agr = _build(clean_ag_record)
        ra = agr["requested_action"]
        assert ra is not None
        assert ra["tool_id"] == "test.tool"

    def test_link_ids_copied(self, _build, clean_ag_record):
        agr = _build(clean_ag_record)
        assert agr["verification_verdict_id"] == "vv-001"
        assert agr["simulation_result_id"] == "sim-001"
        assert agr["simulation_plan_id"] == "plan-1"
        assert agr["dry_run_id"] == "dr-1"
