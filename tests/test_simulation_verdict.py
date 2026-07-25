"""Tests for Simulation Verification Verdict Builder (Milestone 63A).

Verifies that build_simulation_verification_verdict produces correct verdicts
from simulation_result_records. No execution, apply, or rollback occurs.
"""

from __future__ import annotations

import pytest


@pytest.fixture()
def _build():
    from aether.action.simulation_verdict import build_simulation_verification_verdict
    return build_simulation_verification_verdict


# ======================== TEST 1: MISSING RECORD → BLOCKED ========================


class TestMissingRecord:
    """Test 1: missing record returns blocked verdict, not None."""

    def test_missing_record_returns_blocked_not_none(self, _build):
        v = _build(simulation_result_record=None)
        assert v is not None
        assert v["decision"] == "blocked"
        assert v["reason"] == "Simulation result record was not found."
        assert v["simulation_result_id"] is None
        assert v["blocking_reasons"] == ["Simulation result record was not found."]
        assert v["recommended_next_step"] == "Create or provide a valid simulation result record."
        assert v["apply_allowed"] is False
        assert v["rollback_allowed"] is False
        assert v["execution_allowed"] is False
        assert v["tool_execution_allowed"] is False
        assert v["dry_run_execution_allowed"] is False
        assert v["simulation_execution_allowed"] is False
        assert v["verdict_apply_allowed"] is False

# ======================== TEST 2: CANCELLED RECORD → BLOCKED ========================


class TestCancelledRecord:
    """Test 2: cancelled record returns blocked."""

    @staticmethod
    def _clean_record():
        sim_obj = {
            "simulation_result_status": "prepared",
            "simulation_result_type": "synthetic_contract_only_result",
            "simulated_observations": [{"name": "x", "real_world_observation": False}],
            "verification_evidence": [
                {"name": "no_real_tool_execution"},
                {"name": "no_state_mutation"},
                {"name": "no_rollback"},
                {"name": "simulation_plan_not_execution"},
            ],
            "risk_findings": [
                {"name": "synthetic_result_only"},
                {"name": "future_execution_requires_new_milestone"},
            ],
            "no_mutation_proof": {
                "mutation_checked": True,
                "filesystem_mutated": False,
                "network_called": False,
                "database_written": False,
                "identity_modified": False,
                "private_memory_modified": False,
                "target_state_modified": False,
                "apply_performed": False,
                "rollback_performed": False,
            },
            "execution_allowed": False,
            "tool_execution_allowed": False,
            "dry_run_execution_allowed": False,
            "simulation_execution_allowed": False,
            "apply_allowed": False,
            "rollback_allowed": False,
            "warnings": [],
        }
        return {
            "simulation_result_id": "abc123",
            "status": "cancelled",
            "simulation_result": sim_obj,
            "result_persisted": True,
            "simulation_executed": False,
            "execution_allowed": False,
            "tool_execution_allowed": False,
            "apply_allowed": False,
            "rollback_allowed": False,
            "dry_run_execution_allowed": False,
            "simulation_execution_allowed": False,
        }

    def test_cancelled_record_returns_blocked(self, _build):
        rec = self._clean_record()
        v = _build(rec)
        assert v["decision"] == "blocked"
        assert v["reason"] == "Simulation result record is not pending."
        assert v["simulation_result_record_status"] == "cancelled"
        assert "Record status is not pending." in v["blocking_reasons"]

# ======================== TEST 3: SIMULATION_EXECUTED TRUE → BLOCKED ========================


class TestSimulationExecutedTrue:
    """Test 3: simulation_executed true returns blocked."""

    @staticmethod
    def _executed_record():
        r = TestCancelledRecord._clean_record()
        r["status"] = "pending"
        r["simulation_executed"] = True
        return r

    def test_sim_executed_true_returns_blocked(self, _build):
        rec = self._executed_record()
        v = _build(rec)
        assert v["decision"] == "blocked"
        assert v["reason"] == "Simulation result record is unexpectedly marked executed."
        assert "simulation_executed is true." in v["blocking_reasons"]

# ======================== TESTS 4-6: INVALID SIMULATION_RESULT → FAIL ========================


class TestInvalidSimulationResult:
    """Tests 4-6: missing result, invalid status, invalid type → fail."""

    @staticmethod
    def _pending_clean_record():
        sim_obj = {
            "simulation_result_status": "prepared",
            "simulation_result_type": "synthetic_contract_only_result",
            "simulated_observations": [{"name": "x", "real_world_observation": False}],
            "verification_evidence": [
                {"name": "no_real_tool_execution"},
                {"name": "no_state_mutation"},
                {"name": "no_rollback"},
                {"name": "simulation_plan_not_execution"},
            ],
            "risk_findings": [
                {"name": "synthetic_result_only"},
                {"name": "future_execution_requires_new_milestone"},
            ],
            "no_mutation_proof": {
                "mutation_checked": True,
                "filesystem_mutated": False,
                "network_called": False,
                "database_written": False,
                "identity_modified": False,
                "private_memory_modified": False,
                "target_state_modified": False,
                "apply_performed": False,
                "rollback_performed": False,
            },
            "execution_allowed": False,
            "tool_execution_allowed": False,
            "dry_run_execution_allowed": False,
            "simulation_execution_allowed": False,
            "apply_allowed": False,
            "rollback_allowed": False,
            "warnings": [],
        }
        return {
            "simulation_result_id": "xyz789",
            "status": "pending",
            "simulation_result": sim_obj,
            "result_persisted": True,
            "simulation_executed": False,
            "execution_allowed": False,
            "tool_execution_allowed": False,
            "apply_allowed": False,
            "rollback_allowed": False,
            "dry_run_execution_allowed": False,
            "simulation_execution_allowed": False,
        }

    def test_missing_simulation_result_returns_fail(self, _build):
        rec = dict(self._pending_clean_record())
        rec["simulation_result"] = None
        v = _build(rec)
        assert v["decision"] == "fail"
        assert v["reason"] == "Simulation result payload is missing or invalid."

    def test_invalid_result_status_returns_fail(self, _build):
        rec = dict(self._pending_clean_record())
        rec["simulation_result"]["simulation_result_status"] = "invalid"
        v = _build(rec)
        assert v["decision"] == "fail"
        assert v["reason"] == "Simulation result status is not prepared."

    def test_invalid_result_type_returns_fail(self, _build):
        rec = dict(self._pending_clean_record())
        rec["simulation_result"]["simulation_result_type"] = "other_type"
        v = _build(rec)
        assert v["decision"] == "fail"
        assert v["reason"] == "Unsupported simulation result type."

# ======================== TEST 7: VALID CLEAN RECORD → PASS ========================


class TestValidRecord:
    """Tests 7-10: pass verdict with all flags false."""

    def _clean_record(self):
        return {
            "simulation_result_id": "valid-id-001",
            "status": "pending",
            "simulation_result": {
                "simulation_result_status": "prepared",
                "simulation_result_type": "synthetic_contract_only_result",
                "simulation_plan_id": "plan-1",
                "dry_run_id": "dr-1",
                "requested_action": {"tool_id": "test.tool", "action_type": "status_check"},
                "simulated_observations": [
                    {"name": "obs1", "real_world_observation": False},
                    {"name": "obs2", "real_world_observation": False},
                ],
                "verification_evidence": [
                    {"name": "no_real_tool_execution"},
                    {"name": "no_state_mutation"},
                    {"name": "no_rollback"},
                    {"name": "simulation_plan_not_execution"},
                ],
                "risk_findings": [
                    {"name": "synthetic_result_only"},
                    {"name": "future_execution_requires_new_milestone"},
                ],
                "no_mutation_proof": {
                    "mutation_checked": True,
                    "filesystem_mutated": False,
                    "network_called": False,
                    "database_written": False,
                    "identity_modified": False,
                    "private_memory_modified": False,
                    "target_state_modified": False,
                    "apply_performed": False,
                    "rollback_performed": False,
                },
                "execution_allowed": False,
                "tool_execution_allowed": False,
                "dry_run_execution_allowed": False,
                "simulation_execution_allowed": False,
                "apply_allowed": False,
                "rollback_allowed": False,
                "warnings": ["some warning"],
            },
            "result_persisted": True,
            "simulation_executed": False,
            "execution_allowed": False,
            "tool_execution_allowed": False,
            "apply_allowed": False,
            "rollback_allowed": False,
            "dry_run_execution_allowed": False,
            "simulation_execution_allowed": False,
        }

    def test_valid_clean_record_returns_pass(self, _build):
        rec = self._clean_record()
        v = _build(rec)
        assert v["decision"] == "pass"
        assert v["verification_verdict_required"] is True

    def test_pass_verdict_still_has_apply_allowed_false(self, _build):
        rec = self._clean_record()
        v = _build(rec)
        assert v["apply_allowed"] is False
        assert v["verdict_apply_allowed"] is False

    def test_pass_verdict_all_execution_flags_false(self, _build):
        rec = self._clean_record()
        v = _build(rec)
        assert v["execution_allowed"] is False
        assert v["tool_execution_allowed"] is False
        assert v["dry_run_execution_allowed"] is False
        assert v["simulation_execution_allowed"] is False
        assert v["rollback_allowed"] is False

# ======================== TEST 11-12: CHECKS LIST AND ALL PASS ========================


class TestChecksList:
    """Tests 11-12: checks list includes all required checks; all pass for clean record."""

    def test_checks_list_includes_all_required(self, _build):
        rec = TestValidRecord()._clean_record()
        v = _build(rec)
        check_names = [c["name"] for c in v["checks"]]
        expected = [
            "record_pending", "result_persisted", "simulation_not_executed",
            "tool_execution_blocked", "apply_blocked", "rollback_blocked",
            "observations_are_synthetic", "no_mutation_proof_clean",
            "verification_evidence_present", "risk_findings_present",
        ]
        for name in expected:
            assert name in check_names, f"Missing check: {name}"

    def test_all_checks_pass_for_clean_record(self, _build):
        rec = TestValidRecord()._clean_record()
        v = _build(rec)
        for c in v["checks"]:
            assert c["passed"] is True, f"Check {c['name']} should pass but returned {c}"

# ======================== TEST 13-14: SEVERITY-BASED DECISION ========================


class TestSeverityDecisions:
    """Tests 13-14: high/critical fail → fail; medium/low fail → warning."""

    def _minimal_record(self, **overrides):
        base = TestValidRecord()._clean_record()
        if overrides:
            sim = base["simulation_result"]
            for k, val in overrides.items():
                sim[k] = val
        return base

    def test_critical_fail_applies_to_fail_decision(self, _build):
        # apply_blocked is critical — break it
        rec = self._minimal_record(apply_allowed=True)
        v = _build(rec)
        assert v["decision"] == "fail"
        apply_check = next(c for c in v["checks"] if c["name"] == "apply_blocked")
        assert apply_check["passed"] is False

    def test_high_fail_results_in_fail_decision(self, _build):
        # tool_execution_blocked is high — break it
        rec = self._minimal_record(tool_execution_allowed=True)
        v = _build(rec)
        assert v["decision"] == "fail"
        tc = next(c for c in v["checks"] if c["name"] == "tool_execution_blocked")
        assert tc["passed"] is False

    def test_medium_fail_results_in_warning_decision(self, _build):
        # verification_evidence_present is medium — remove one evidence entry
        rec = self._minimal_record(verification_evidence=[
            {"name": "no_real_tool_execution"},
            # missing no_state_mutation, no_rollback, simulation_plan_not_execution
        ])
        v = _build(rec)
        assert v["decision"] == "warning"

    def test_low_fail_results_in_warning_decision(self, _build):
        # result_persisted is low — break it
        rec = dict(TestValidRecord()._clean_record())
        rec["result_persisted"] = False
        v = _build(rec)
        assert v["decision"] == "warning"

# ======================== TESTS 15-18: CHECK-SPECIFIC FAILURE ========================


class TestCheckSpecificFailures:
    """Tests 15-18: specific checks fail when conditions violated."""

    def test_observations_are_synthetic_fails_if_any_real(self, _build):
        rec = TestValidRecord()._clean_record()
        rec["simulation_result"]["simulated_observations"].append(
            {"name": "real_obs", "real_world_observation": True}
        )
        v = _build(rec)
        obs_check = next(c for c in v["checks"] if c["name"] == "observations_are_synthetic")
        assert obs_check["passed"] is False

    def test_no_mutation_proof_clean_fails_if_filesystem_mutated(self, _build):
        rec = TestValidRecord()._clean_record()
        rec["simulation_result"]["no_mutation_proof"]["filesystem_mutated"] = True
        v = _build(rec)
        mpc = next(c for c in v["checks"] if c["name"] == "no_mutation_proof_clean")
        assert mpc["passed"] is False

    def test_verification_evidence_present_fails_if_missing(self, _build):
        rec = TestValidRecord()._clean_record()
        rec["simulation_result"]["verification_evidence"] = []
        v = _build(rec)
        ve = next(c for c in v["checks"] if c["name"] == "verification_evidence_present")
        assert ve["passed"] is False

    def test_risk_findings_present_fails_if_missing(self, _build):
        rec = TestValidRecord()._clean_record()
        rec["simulation_result"]["risk_findings"] = []
        v = _build(rec)
        rf = next(c for c in v["checks"] if c["name"] == "risk_findings_present")
        assert rf["passed"] is False

# ======================== TESTS 19-23: EVIDENCE, RISKS, BLOCKING, NEXT_STEP ========================


class TestEvidenceRisksBlocking:
    """Tests 19-23: evidence_summary, unresolved_risks, blocking_reasons, next_step."""

    def test_evidence_summary_includes_no_real_tool_execution(self, _build):
        rec = TestValidRecord()._clean_record()
        v = _build(rec)
        names = [e["name"] for e in v["evidence_summary"]]
        assert "no_real_tool_execution" in names

    def test_unresolved_risks_empty_for_pass(self, _build):
        rec = TestValidRecord()._clean_record()
        v = _build(rec)
        assert v["decision"] == "pass"
        # For pass verdict, only real_apply risk is included
        risk_names = [r["name"] for r in v["unresolved_risks"]]
        assert "real_apply_not_authorized" in risk_names

    def test_real_apply_not_authorized_included_for_pass(self, _build):
        rec = TestValidRecord()._clean_record()
        v = _build(rec)
        assert v["decision"] == "pass"
        risk_names = [r["name"] for r in v["unresolved_risks"]]
        assert "real_apply_not_authorized" in risk_names

    def test_blocking_reasons_empty_for_pass(self, _build):
        rec = TestValidRecord()._clean_record()
        v = _build(rec)
        assert v["decision"] == "pass"
        assert v["blocking_reasons"] == []

    def test_recommended_next_step_for_pass_mentions_future(self, _build):
        rec = TestValidRecord()._clean_record()
        v = _build(rec)
        assert "future" in v["recommended_next_step"]
        assert "do not apply" in v["recommended_next_step"] or "do not apply" in v["recommended_next_step"].lower()

# ======================== TESTS 24-29: METADATA, WARNINGS, FIELDS ========================


class TestMetadataWarningsFields:
    """Tests 24-29: metadata, warnings, requested_action, ids."""

    def test_metadata_source_and_schema_version(self, _build):
        rec = TestValidRecord()._clean_record()
        v = _build(rec, context={"session_id": "test-sid"})
        meta = v["metadata"]
        assert meta["source"] == "simulation_verdict_builder"
        assert meta["schema_version"] == "1.0"

    def test_context_session_id_copied(self, _build):
        rec = TestValidRecord()._clean_record()
        v = _build(rec, context={"session_id": "manual-63a-session"})
        assert v["metadata"]["session_id"] == "manual-63a-session"

    def test_warnings_include_no_apply_authorization(self, _build):
        rec = TestValidRecord()._clean_record()
        v = _build(rec)
        warns_text = " ".join(v["warnings"])
        assert "does not authorize apply" in warns_text

    def test_simulation_result_warnings_copied_with_prefix(self, _build):
        rec = TestValidRecord()._clean_record()
        rec["simulation_result"]["warnings"] = ["custom warning 1"]
        v = _build(rec)
        assert any("simulation_result_warning: custom warning 1" in w for w in v["warnings"])

    def test_requested_action_copied(self, _build):
        rec = TestValidRecord()._clean_record()
        req = rec["simulation_result"]["requested_action"]
        assert req is not None
        assert req["tool_id"] == "test.tool"

    def test_dry_run_id_and_sim_plan_id_copied(self, _build):
        rec = TestValidRecord()._clean_record()
        v = _build(rec)
        assert v["simulation_plan_id"] == "plan-1"
        assert v["dry_run_id"] == "dr-1"
