"""Tests for Dry-Run Sandbox Contract (Milestone 58A).

Verifies that build_dry_run_sandbox_contract correctly checks dry-run record
status and requested_action type.  No execution flags are ever enabled.
"""

from __future__ import annotations

import pytest


@pytest.fixture()
def _build():
    from aether.action.dry_run_sandbox_contract import build_dry_run_sandbox_contract
    return build_dry_run_sandbox_contract


# ======================== TEST 1-5: REJECTION CASES ======================== #


class TestRejectionCases:
    """Tests 1-5: various reasons to reject a contract."""

    def test_not_found_when_record_missing(self, _build):
        result = _build(dry_run_record=None)
        assert result["contract_valid"] is False
        assert result["decision"] == "not_found"
        assert result["reason"] == "Dry-run record was not found."
        assert result["execution_allowed"] is False
        assert result["dry_run_execution_allowed"] is False

    def test_invalid_record_when_no_dry_run_request(self, _build):
        rec = {"dry_run_id": "x", "status": "pending"}
        result = _build(dry_run_record=rec)
        assert result["contract_valid"] is False
        assert result["decision"] == "invalid_record"
        assert result["dry_run_status"] == "pending"

    def test_not_pending_when_cancelled(self, _build):
        rec = {"dry_run_id": "x", "status": "cancelled", "dry_run_request": {"requested_action": {"tool_id": "t"}}}
        result = _build(dry_run_record=rec)
        assert result["contract_valid"] is False
        assert result["decision"] == "not_pending"
        assert result["dry_run_status"] == "cancelled"

    def test_invalid_record_when_dry_run_executed_true(self, _build):
        req = {"requested_action": {"tool_id": "t"}}
        rec = {"dry_run_id": "x", "status": "pending", "dry_run_request": req, "dry_run_executed": True}
        result = _build(dry_run_record=rec)
        assert result["contract_valid"] is False
        assert result["decision"] == "invalid_record"
        assert result["reason"] == "Dry-run record is already marked executed."

    def test_invalid_record_when_no_requested_action(self, _build):
        rec = {"dry_run_id": "x", "status": "pending", "dry_run_request": {"some_field": 1}}
        result = _build(dry_run_record=rec)
        assert result["contract_valid"] is False
        assert result["decision"] == "invalid_record"
        assert result["reason"] == "Requested action is missing from dry-run request."


# ======================== TEST 6-9: ACTION TYPE CHECKS ======================== #


class TestActionTypeChecks:
    """Tests 6-9: unsafe vs allowed action types."""

    def test_unsafe_action_type(self, _build):
        ra = {"action_type": "file_delete", "tool_id": "t"}
        req = {"requested_action": ra}
        rec = {"dry_run_id": "x", "status": "pending", "dry_run_request": req}
        result = _build(dry_run_record=rec)
        assert result["contract_valid"] is False
        assert result["decision"] == "unsafe_action_type"

    def test_allowed_status_check(self, _build):
        ra = {"action_type": "status_check", "tool_id": "t"}
        req = {"requested_action": ra}
        rec = {"dry_run_id": "x", "status": "pending", "dry_run_request": req}
        result = _build(dry_run_record=rec)
        assert result["contract_valid"] is True
        assert result["decision"] == "allow_simulation_planning"

    def test_allowed_read_only_check(self, _build):
        ra = {"action_type": "read_only_check", "tool_id": "t"}
        req = {"requested_action": ra}
        rec = {"dry_run_id": "x", "status": "pending", "dry_run_request": req}
        result = _build(dry_run_record=rec)
        assert result["contract_valid"] is True
        assert result["decision"] == "allow_simulation_planning"

    def test_allowed_inspection(self, _build):
        ra = {"action_type": "inspection", "tool_id": "t"}
        req = {"requested_action": ra}
        rec = {"dry_run_id": "x", "status": "pending", "dry_run_request": req}
        result = _build(dry_run_record=rec)
        assert result["contract_valid"] is True
        assert result["decision"] == "allow_simulation_planning"


# ======================== TEST 10-14: SAFETY FLAGS ======================== #


class TestSafetyFlags:
    """Tests 10-14: ALL execution/apply/rollback flags always false."""

    @staticmethod
    def _valid_rec(action_type="status_check"):
        ra = {"action_type": action_type, "tool_id": "t"}
        return {"dry_run_id": "x", "status": "pending", "dry_run_request": {"requested_action": ra}}

    def test_dry_run_execution_allowed_false(self, _build):
        result = _build(dry_run_record=TestSafetyFlags._valid_rec())
        assert result["contract_valid"] is True
        assert result["dry_run_execution_allowed"] is False

    def test_execution_allowed_false(self, _build):
        result = _build(dry_run_record=TestSafetyFlags._valid_rec())
        assert result["execution_allowed"] is False

    def test_tool_execution_allowed_false(self, _build):
        result = _build(dry_run_record=TestSafetyFlags._valid_rec())
        assert result["tool_execution_allowed"] is False

    def test_apply_allowed_false(self, _build):
        result = _build(dry_run_record=TestSafetyFlags._valid_rec())
        assert result["apply_allowed"] is False

    def test_rollback_allowed_false(self, _build):
        result = _build(dry_run_record=TestSafetyFlags._valid_rec())
        assert result["rollback_allowed"] is False


# ======================== TEST 15-23: CONTENT CHECKS ======================== #


class TestContentPreservation:
    """Tests 15-23: sandbox requirements, observations, warnings, metadata."""

    @staticmethod
    def _valid_rec(action_type="status_check"):
        ra = {"action_type": action_type, "tool_id": "t"}
        return {"dry_run_id": "x", "status": "pending", "dry_run_request": {"requested_action": ra}}

    def test_sandbox_requirements_include_isolation(self, _build):
        result = _build(dry_run_record=TestContentPreservation._valid_rec())
        checks = result["sandbox_requirements"]
        assert any("isolated sandbox" in c.lower() or "no real external tools" in c.lower() for c in checks)
        assert any("persistent state" in c.lower() for c in checks)

    def test_expected_observations_included(self, _build):
        result = _build(dry_run_record=TestContentPreservation._valid_rec())
        obs = result["expected_observations"]
        assert "simulation_plan" in obs
        assert "verification_points" in obs

    def test_forbidden_operations_included(self, _build):
        result = _build(dry_run_record=TestContentPreservation._valid_rec())
        forb = result["forbidden_operations"]
        assert "network_call" in forb
        assert "identity_seed_modification" in forb

    def test_preconditions_included(self, _build):
        result = _build(dry_run_record=TestContentPreservation._valid_rec())
        pre = result["preconditions"]
        assert "Dry-run record exists." in pre
        assert "Approval validation snapshot exists." in pre

    def test_postconditions_included(self, _build):
        result = _build(dry_run_record=TestContentPreservation._valid_rec())
        post = result["postconditions"]
        assert "No target state was modified." in post
        assert "Dry-run execution flag remains false." in post

    def test_metadata_source_and_schema_version(self, _build):
        result = _build(dry_run_record=TestContentPreservation._valid_rec())
        meta = result["metadata"]
        assert meta["source"] == "dry_run_sandbox_contract_builder"
        assert meta["schema_version"] == "1.0"

    def test_context_session_id_copied(self, _build):
        ctx = {"session_id": "test-sid-42"}
        result = _build(dry_run_record=TestContentPreservation._valid_rec(), context=ctx)
        assert result["metadata"]["session_id"] == "test-sid-42"

    def test_parameters_warning_added(self, _build):
        rec = TestContentPreservation._valid_rec()
        rec["dry_run_request"]["requested_action"]["parameters"] = {"arg": "x"}
        result = _build(dry_run_record=rec)
        assert any("Parameters" in w for w in result.get("warnings", []))

    def test_target_warning_added(self, _build):
        rec = TestContentPreservation._valid_rec()
        rec["dry_run_request"]["requested_action"]["target"] = "/tmp/x"
        result = _build(dry_run_record=rec)
        assert any("Target" in w for w in result.get("warnings", []))


# ======================== TEST 24: REQUESTED_ACTION PRESERVED ======================== #


class TestRequestPreserved:
    """Test 24: requested_action is preserved in the contract."""

    def test_requested_action_preserved(self, _build):
        ra = {"action_type": "status_check", "tool_id": "project.test", "name": "My Tool"}
        rec = {"dry_run_id": "x", "status": "pending", "dry_run_request": {"requested_action": ra}}
        result = _build(dry_run_record=rec)
        assert result["requested_action"]["tool_id"] == "project.test"
        assert result["requested_action"]["name"] == "My Tool"
