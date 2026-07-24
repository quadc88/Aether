"""Tests for Simulation Plan Builder (Milestone 59A).

Verifies that build_simulation_plan only produces a plan when the sandbox
contract is fully valid.  All execution flags remain false.
"""

from __future__ import annotations

import pytest


@pytest.fixture()
def _build():
    from aether.action.simulation_plan import build_simulation_plan
    return build_simulation_plan


# ======================== TEST 1-5: REJECTION CASES ======================== #


class TestRejectionCases:
    """Tests 1-5: Returns None when conditions not met."""

    def test_none_when_contract_is_none(self, _build):
        result = _build(sandbox_contract=None)
        assert result is None

    def test_none_when_contract_valid_false(self, _build):
        contract = {"contract_valid": False, "decision": "not_found"}
        result = _build(sandbox_contract=contract)
        assert result is None

    def test_none_when_decision_not_allow_planning(self, _build):
        contract = {
            "contract_valid": True,
            "decision": "unsafe_action_type",
            "allowed_simulation_mode": "contract_only",
            "requested_action": {},
        }
        result = _build(sandbox_contract=contract)
        assert result is None

    def test_none_when_not_contract_only_mode(self, _build):
        contract = {
            "contract_valid": True,
            "decision": "allow_simulation_planning",
            "allowed_simulation_mode": "other",
            "requested_action": {},
        }
        result = _build(sandbox_contract=contract)
        assert result is None

    def test_none_when_requested_action_missing(self, _build):
        contract = {
            "contract_valid": True,
            "decision": "allow_simulation_planning",
            "allowed_simulation_mode": "contract_only",
            "requested_action": None,
        }
        result = _build(sandbox_contract=contract)
        assert result is None


# ======================== TEST 6-8: VALID CREATION ======================== #


class TestValidPlan:
    """Tests 6-8: valid contract creates simulation_plan with correct fields."""

    @staticmethod
    def _valid_contract():
        return {
            "contract_valid": True,
            "decision": "allow_simulation_planning",
            "allowed_simulation_mode": "contract_only",
            "dry_run_id": "test-dry-run-1",
            "dry_run_status": "pending",
            "requested_action": {"tool_id": "x", "action_type": "status_check"},
            "warnings": [],
        }

    def test_valid_creation(self, _build):
        result = _build(sandbox_contract=TestValidPlan._valid_contract())
        assert result is not None
        assert result["simulation_plan_required"] is True
        assert result["simulation_plan_status"] == "pending"
        assert result["simulation_plan_type"] == "contract_only_plan"

    def test_plan_status_pending(self, _build):
        result = _build(sandbox_contract=TestValidPlan._valid_contract())
        assert result["simulation_plan_status"] == "pending"

    def test_plan_type_contract_only_plan(self, _build):
        result = _build(sandbox_contract=TestValidPlan._valid_contract())
        assert result["simulation_plan_type"] == "contract_only_plan"


# ======================== TEST 9-12: PRESERVATION & STEPS ======================== #


class TestPreservationAndSteps:
    """Tests 9-12: preserved fields and step constraints."""

    def test_requested_action_preserved(self, _build):
        ra = {"tool_id": "shell.run", "parameters": {"a": 1}}
        contract = {
            "contract_valid": True, "decision": "allow_simulation_planning",
            "allowed_simulation_mode": "contract_only",
            "dry_run_id": "did", "dry_run_status": "pending",
            "requested_action": ra, "warnings": [],
        }
        result = _build(sandbox_contract=contract)
        assert result["requested_action"]["tool_id"] == "shell.run"
        assert result["requested_action"]["parameters"]["a"] == 1

    def test_sandbox_contract_snapshot_preserved(self, _build):
        contract = TestValidPlan._valid_contract()
        contract["requested_action"] = {"tool_id": "t", "action_type": "s"}
        result = _build(sandbox_contract=contract)
        snap = result["sandbox_contract_snapshot"]
        assert snap["contract_valid"] is True
        assert snap["decision"] == "allow_simulation_planning"

    def test_simulation_steps_exist_and_no_execute(self, _build):
        result = _build(sandbox_contract=TestValidPlan._valid_contract())
        steps = result["simulation_steps"]
        assert len(steps) > 0
        for s in steps:
            assert s["executes_tool"] is False
            assert s["mutates_state"] is False

    def test_all_steps_mutates_state_false(self, _build):
        result = _build(sandbox_contract=TestValidPlan._valid_contract())
        for s in result["simulation_steps"]:
            assert s["mutates_state"] is False


# ======================== TEST 13-23: CONTENT CHECKS ======================== #


class TestContentChecks:
    """Tests 13-23: expected inputs/outputs/verification/risk/etc."""

    def test_expected_inputs_include_basics(self, _build):
        result = _build(sandbox_contract=TestValidPlan._valid_contract())
        inputs = result["expected_inputs"]
        assert "sandbox_contract" in inputs
        assert "dry_run_record_reference" in inputs

    def test_expected_outputs_included(self, _build):
        result = _build(sandbox_contract=TestValidPlan._valid_contract())
        outs = result["expected_outputs"]
        assert "simulated_observations" in outs
        assert "no_mutation_confirmation" in outs

    def test_verification_points_included(self, _build):
        result = _build(sandbox_contract=TestValidPlan._valid_contract())
        vps = result["verification_points"]
        assert "No real tools are executed." in vps
        assert "No persistent state is modified." in vps

    def test_risk_notes_includes_not_execution(self, _build):
        result = _build(sandbox_contract=TestValidPlan._valid_contract())
        notes = result["risk_notes"]
        assert "Simulation plan is not execution." in notes

    def test_observation_requirements_included(self, _build):
        result = _build(sandbox_contract=TestValidPlan._valid_contract())
        obs = result["observation_requirements"]
        assert "Capture no-mutation proof." in obs

    def test_all_flags_false(self, _build):
        result = _build(sandbox_contract=TestValidPlan._valid_contract())
        assert result["execution_allowed"] is False
        assert result["tool_execution_allowed"] is False
        assert result["dry_run_execution_allowed"] is False
        assert result["apply_allowed"] is False
        assert result["rollback_allowed"] is False

    def test_metadata_source_and_schema_version(self, _build):
        result = _build(sandbox_contract=TestValidPlan._valid_contract())
        meta = result["metadata"]
        assert meta["source"] == "simulation_plan_builder"
        assert meta["schema_version"] == "1.0"

    def test_context_session_id_copied(self, _build):
        contract = TestValidPlan._valid_contract()
        result = _build(sandbox_contract=contract, context={"session_id": "sid-99"})
        assert result["metadata"]["session_id"] == "sid-99"

    def test_sandbox_warnings_prefixed(self, _build):
        contract = TestValidPlan._valid_contract()
        contract["warnings"] = ["some warning"]
        result = _build(sandbox_contract=contract)
        assert any(w.startswith("sandbox_warning:") for w in result["warnings"])

    def test_parameter_warning_added(self, _build):
        contract = TestValidPlan._valid_contract()
        contract["requested_action"]["parameters"] = {"a": 1}
        result = _build(sandbox_contract=contract)
        assert any("Parameters" in w for w in result["warnings"])

    def test_target_warning_added(self, _build):
        contract = TestValidPlan._valid_contract()
        contract["requested_action"]["target"] = "/tmp/x"
        result = _build(sandbox_contract=contract)
        assert any("Target" in w for w in result["warnings"])
