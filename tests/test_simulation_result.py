"""Tests for Simulation Result Builder (Milestone 61A).

Verifies that build_simulation_result only produces a synthetic result when
the simulation_plan_record meets all preconditions.  All execution flags
remain false.  No real-world observation occurs.
"""

from __future__ import annotations

import pytest


@pytest.fixture()
def _build():
    from aether.action.simulation_result import build_simulation_result
    return build_simulation_result


# ======================== TEST 1-6: REJECTION CASES ======================== #


class TestRejectionCases:
    """Tests 1-6: Returns None when conditions not met."""

    def test_none_when_record_is_none(self, _build):
        assert _build(simulation_plan_record=None) is None

    def test_none_when_status_cancelled(self, _build):
        rec = {"status": "cancelled", "simulation_executed": False, "simulation_plan": {}}
        assert _build(simulation_plan_record=rec) is None

    def test_none_when_simulation_executed_true(self, _build):
        plan = {"simulation_plan_status": "pending", "simulation_plan_type": "contract_only_plan"}
        rec = {"status": "pending", "simulation_executed": True, "simulation_plan": plan}
        assert _build(simulation_plan_record=rec) is None

    def test_none_when_simulation_plan_missing(self, _build):
        rec = {"status": "pending", "simulation_executed": False}
        assert _build(simulation_plan_record=rec) is None

    def test_none_when_plan_status_not_pending(self, _build):
        plan = {"simulation_plan_status": "cancelled", "simulation_plan_type": "contract_only_plan"}
        rec = {"status": "pending", "simulation_executed": False, "simulation_plan": plan}
        assert _build(simulation_plan_record=rec) is None

    def test_none_when_plan_type_not_contract_only(self, _build):
        plan = {"simulation_plan_status": "pending", "simulation_plan_type": "other"}
        rec = {"status": "pending", "simulation_executed": False, "simulation_plan": plan}
        assert _build(simulation_plan_record=rec) is None


# ======================== TEST 7-12: VALID CREATION ======================== #


class TestValidResult:
    """Tests 7-12: valid record creates simulation_result with correct fields."""

    @staticmethod
    def _valid_record():
        plan = {
            "simulation_plan_id": "sp-1",
            "simulation_plan_status": "pending",
            "simulation_plan_type": "contract_only_plan",
            "dry_run_id": "dr-1",
            "requested_action": {"tool_id": "test.tool"},
            "expected_outputs": ["x"],
            "verification_points": ["y"],
            "warnings": [],
        }
        return {
            "simulation_plan_id": "sp-1", "status": "pending",
            "simulation_executed": False, "simulation_plan": plan,
        }

    def test_valid_creates_result(self, _build):
        r = _build(simulation_plan_record=self._valid_record())
        assert r is not None
        assert r["simulation_result_required"] is True
        assert r["simulation_result_status"] == "prepared"
        assert r["simulation_result_type"] == "synthetic_contract_only_result"

    def test_plan_snapshot_preserved(self, _build):
        plan = self._valid_record()["simulation_plan"]
        r = _build(simulation_plan_record=self._valid_record())
        assert r["simulation_plan_snapshot"] is not None
        assert r["simulation_plan_snapshot"]["dry_run_id"] == "dr-1"

    def test_requested_action_copied(self, _build):
        ra = {"tool_id": "t", "action_type": "s"}
        rec = self._valid_record()
        rec["simulation_plan"]["requested_action"] = ra
        r = _build(simulation_plan_record=rec)
        assert r["requested_action"]["tool_id"] == "t"

    def test_dry_run_id_copied(self, _build):
        r = _build(simulation_plan_record=self._valid_record())
        assert r["dry_run_id"] == "dr-1"

    def test_simulated_observations_exist(self, _build):
        r = _build(simulation_plan_record=self._valid_record())
        assert len(r["simulated_observations"]) >= 3
        assert all(o.get("real_world_observation") is False for o in r["simulated_observations"])

    def test_verification_evidence_includes_required(self, _build):
        r = _build(simulation_plan_record=self._valid_record())
        names = [e["name"] for e in r["verification_evidence"]]
        assert "no_real_tool_execution" in names
        assert "no_state_mutation" in names


# ======================== TEST 13-25: CONTENT CHECKS ======================== #


class TestContentChecks:
    """Tests 13-25: observations, proof, risk, metadata, warnings."""

    def test_no_mutation_proof_has_all_false(self, _build):
        r = _build(simulation_plan_record=TestValidResult._valid_record())
        p = r["no_mutation_proof"]
        assert p["filesystem_mutated"] is False
        assert p["network_called"] is False
        assert p["database_written"] is False
        assert p["identity_modified"] is False
        assert p["private_memory_modified"] is False
        assert p["target_state_modified"] is False
        assert p["apply_performed"] is False
        assert p["rollback_performed"] is False

    def test_risk_findings_include_synth_only(self, _build):
        r = _build(simulation_plan_record=TestValidResult._valid_record())
        names = [f["name"] for f in r["risk_findings"]]
        assert "synthetic_result_only" in names
        assert "future_execution_requires_new_milestone" in names

    def test_parameters_risk_finding_added(self, _build):
        rec = TestValidResult._valid_record()
        rec["simulation_plan"]["requested_action"]["parameters"] = {"key": "val"}
        r = _build(simulation_plan_record=rec)
        names = [f["name"] for f in r["risk_findings"]]
        assert "parameters_not_executed" in names

    def test_target_risk_finding_added(self, _build):
        rec = TestValidResult._valid_record()
        rec["simulation_plan"]["requested_action"]["target"] = "/tmp/x"
        r = _build(simulation_plan_record=rec)
        names = [f["name"] for f in r["risk_findings"]]
        assert "target_not_modified" in names

    def test_all_flags_false(self, _build):
        r = _build(simulation_plan_record=TestValidResult._valid_record())
        assert r["execution_allowed"] is False
        assert r["tool_execution_allowed"] is False
        assert r["dry_run_execution_allowed"] is False
        assert r["simulation_execution_allowed"] is False
        assert r["apply_allowed"] is False
        assert r["rollback_allowed"] is False

    def test_metadata_source_and_schema_version(self, _build):
        r = _build(simulation_plan_record=TestValidResult._valid_record())
        assert r["metadata"]["source"] == "simulation_result_builder"
        assert r["metadata"]["schema_version"] == "1.0"

    def test_context_session_id_copied(self, _build):
        rec = TestValidResult._valid_record()
        r = _build(simulation_plan_record=rec, context={"session_id": "sid-42"})
        assert r["metadata"]["session_id"] == "sid-42"

    def test_simulation_plan_warnings_prefixed(self, _build):
        rec = TestValidResult._valid_record()
        rec["simulation_plan"]["warnings"] = ["plan_warn"]
        r = _build(simulation_plan_record=rec)
        assert any("simulation_plan_warning:" in w for w in r["warnings"])

    def test_synthetic_and_no_target_warnings(self, _build):
        r = _build(simulation_plan_record=TestValidResult._valid_record())
        assert any("Synthetic result only" in w for w in r["warnings"])
        assert any("No target system was contacted" in w for w in r["warnings"])
