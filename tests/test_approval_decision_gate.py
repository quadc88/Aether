"""Tests for Approval Decision Gate (Milestone 55A).

Verifies that validate_approval_for_action correctly checks approval record
status and matches requested actions against approved actions.
No tools are executed or records mutated.
"""

from __future__ import annotations

import pytest


@pytest.fixture()
def approval_store_dir(monkeypatch, tmp_path):
    """Redirect _approval_record_dir to a temp directory."""
    store_dir = tmp_path / "approvals"
    store_dir.mkdir(parents=True, exist_ok=True)

    import aether.action.approval_queue as aq_mod
    monkeypatch.setattr(aq_mod, "_approval_record_dir", lambda: store_dir)

    return store_dir


@pytest.fixture()
def _create(approval_store_dir):
    from aether.action.approval_queue import create_approval_record
    return create_approval_record


@pytest.fixture()
def _update():
    from aether.action.approval_queue import update_approval_record_status
    return update_approval_record_status


@pytest.fixture()
def _validate():
    from aether.action.approval_decision_gate import validate_approval_for_action
    return validate_approval_for_action


# ======================== TEST 1-3: INPUT VALIDATION ======================== #


class TestInputValidation:
    """Test 1-3: missing approval_id, missing action, not found."""

    def test_missing_approval_id(self, _validate):
        result = _validate(approval_id=None, requested_action={"tool_id": "x"})
        assert result["approval_valid"] is False
        assert result["decision"] == "missing_approval"
        assert result["reason"] == "Approval id is required."
        assert result["execution_allowed"] is False
        assert result["dry_run_allowed"] is False
        assert result["tool_execution_allowed"] is False

    def test_missing_requested_action(self, _validate):
        result = _validate(approval_id="some-id", requested_action=None)
        assert result["approval_valid"] is False
        assert result["decision"] == "invalid_request"
        assert result["reason"] == "Requested action is required."
        assert result["execution_allowed"] is False
        assert result["dry_run_allowed"] is False
        assert result["tool_execution_allowed"] is False

    def test_not_found_approval(self, _validate, _create):
        # Create a record but don't use its real id
        result = _validate(approval_id="nonexistent-id-abc", requested_action={"tool_id": "file.read"})
        assert result["approval_valid"] is False
        assert result["decision"] == "not_found"
        assert result["reason"] == "Approval record was not found."
        assert result["approval_status"] is None


# ======================== TEST 4-6: STATUS CHECKS ======================== #


class TestStatusChecks:
    """Test 4-6: pending / rejected / cancelled approvals return not_approved."""

    def test_pending_approval_returns_not_approved(self, _create, _validate):
        rec = _create({"approval_required": True, "requested_action": {"tool_id": "test.tool"}})
        result = _validate(approval_id=rec["approval_id"], requested_action={"tool_id": "test.tool"})
        assert result["approval_valid"] is False
        assert result["decision"] == "not_approved"
        assert result["approval_status"] == "pending"

    def test_rejected_approval_returns_not_approved(self, _create, _update, _validate):
        rec = _create({"approval_required": True, "requested_action": {"tool_id": "test.tool"}})
        _update(rec["approval_id"], decision="rejected")
        result = _validate(approval_id=rec["approval_id"], requested_action={"tool_id": "test.tool"})
        assert result["approval_valid"] is False
        assert result["decision"] == "not_approved"
        assert result["approval_status"] == "rejected"

    def test_cancelled_approval_returns_not_approved(self, _create, _update, _validate):
        rec = _create({"approval_required": True, "requested_action": {"tool_id": "test.tool"}})
        _update(rec["approval_id"], decision="cancelled")
        result = _validate(approval_id=rec["approval_id"], requested_action={"tool_id": "test.tool"})
        assert result["approval_valid"] is False
        assert result["decision"] == "not_approved"
        assert result["approval_status"] == "cancelled"


# ======================== TEST 7-13: ACTION MATCHING ======================== #


class TestActionMatching:
    """Test 7-13: approved records with matching/mismatched actions."""

    def test_matching_tool_id_returns_allow_dry_run(self, _create, _update, _validate):
        req_action = {"tool_id": "shell.run", "command": "ls"}
        rec = _create({"approval_required": True, "requested_action": req_action})
        _update(rec["approval_id"], decision="approved")
        result = _validate(
            approval_id=rec["approval_id"],
            requested_action={"tool_id": "shell.run"},
        )
        assert result["approval_valid"] is True
        assert result["decision"] == "allow_dry_run"
        assert "tool_id" in result["matched_fields"]

    def test_matching_action_type_returns_valid(self, _create, _update, _validate):
        rec = _create({"approval_required": True, "requested_action": {"action_type": "read_file"}})
        _update(rec["approval_id"], decision="approved")
        result = _validate(
            approval_id=rec["approval_id"],
            requested_action={"action_type": "read_file"},
        )
        assert result["approval_valid"] is True
        assert result["decision"] == "allow_dry_run"

    def test_mismatched_tool_id(self, _create, _update, _validate):
        rec = _create({"approval_required": True, "requested_action": {"tool_id": "shell.run"}})
        _update(rec["approval_id"], decision="approved")
        result = _validate(
            approval_id=rec["approval_id"],
            requested_action={"tool_id": "file.read"},
        )
        assert result["approval_valid"] is False
        assert result["decision"] == "action_mismatch"
        assert "tool_id" in result["mismatched_fields"]

    def test_mismatched_target(self, _create, _update, _validate):
        rec = _create({"approval_required": True, "requested_action": {
            "tool_id": "file.read", "target": "/etc/hosts"
        }})
        _update(rec["approval_id"], decision="approved")
        result = _validate(
            approval_id=rec["approval_id"],
            requested_action={"tool_id": "file.read", "target": "/etc/passwd"},
        )
        assert result["approval_valid"] is False
        assert result["decision"] == "action_mismatch"
        assert "target" in result["mismatched_fields"]

    def test_parameters_mismatch(self, _create, _update, _validate):
        rec = _create({"approval_required": True, "requested_action": {
            "tool_id": "run.cmd",
            "parameters": {"arg": "a"}
        }})
        _update(rec["approval_id"], decision="approved")
        result = _validate(
            approval_id=rec["approval_id"],
            requested_action={"tool_id": "run.cmd", "parameters": {"arg": "b"}},
        )
        assert result["approval_valid"] is False
        assert result["decision"] == "action_mismatch"
        assert "parameters" in result["mismatched_fields"]

    def test_parameters_exact_match(self, _create, _update, _validate):
        rec = _create({"approval_required": True, "requested_action": {
            "tool_id": "run.cmd",
            "parameters": {"arg": "a"}
        }})
        _update(rec["approval_id"], decision="approved")
        result = _validate(
            approval_id=rec["approval_id"],
            requested_action={"tool_id": "run.cmd", "parameters": {"arg": "a"}},
        )
        assert result["approval_valid"] is True
        assert result["decision"] == "allow_dry_run"
        assert "parameters" in result["matched_fields"]

    def test_no_approved_requested_action(self, _create, _update, _validate):
        rec = _create({"approval_required": True, "requested_action": None})
        _update(rec["approval_id"], decision="approved")
        result = _validate(
            approval_id=rec["approval_id"],
            requested_action={"tool_id": "test"},
        )
        assert result["approval_valid"] is False
        assert result["decision"] == "action_mismatch"


# ======================== TEST 14-20: SAFETY & EDGE CASES ======================== #


class TestSafetyAndEdgeCases:
    """Test 14-20: execution fields always false, warnings, no mutation."""

    def test_valid_still_no_execution(self, _create, _update, _validate):
        rec = _create({"approval_required": True, "requested_action": {"tool_id": "x"}})
        _update(rec["approval_id"], decision="approved")
        result = _validate(approval_id=rec["approval_id"], requested_action={"tool_id": "x"})
        assert result["approval_valid"] is True
        assert result["execution_allowed"] is False
        assert result["tool_execution_allowed"] is False
        assert result["dry_run_allowed"] is True

    def test_matched_fields_populated(self, _create, _update, _validate):
        rec = _create({"approval_required": True, "requested_action": {
            "tool_id": "shell.run", "action_type": "execute", "name": "ls"
        }})
        _update(rec["approval_id"], decision="approved")
        result = _validate(approval_id=rec["approval_id"], requested_action={
            "tool_id": "shell.run", "action_type": "execute"
        })
        assert len(result["matched_fields"]) > 0

    def test_mismatched_fields_populated(self, _create, _update, _validate):
        rec = _create({"approval_required": True, "requested_action": {
            "tool_id": "shell.run", "target": "/tmp"
        }})
        _update(rec["approval_id"], decision="approved")
        result = _validate(approval_id=rec["approval_id"], requested_action={
            "tool_id": "file.read", "target": "/var"
        })
        assert len(result["mismatched_fields"]) > 0

    def test_extra_requested_action_fields_produce_warning(self, _create, _update, _validate):
        rec = _create({"approval_required": True, "requested_action": {"tool_id": "x"}})
        _update(rec["approval_id"], decision="approved")
        result = _validate(approval_id=rec["approval_id"], requested_action={
            "tool_id": "x", "extra_field": "should_warn"
        })
        assert any("Extra field" in w for w in result.get("warnings", []))

    def test_validation_does_not_mutate_record(self, _create, _update, _validate):
        from aether.action.approval_queue import get_approval_record as _get
        rec = _create({"approval_required": True, "requested_action": {"tool_id": "y"}})
        _update(rec["approval_id"], decision="approved")
        before = dict(_get(rec["approval_id"]))
        _validate(approval_id=rec["approval_id"], requested_action={"tool_id": "y"})
        after = dict(_get(rec["approval_id"]))
        assert after["status"] == "approved"  # unchanged
        assert after["updated_at"] == before["updated_at"]  # not modified by validation
