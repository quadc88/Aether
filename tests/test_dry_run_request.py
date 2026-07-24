"""Tests for Dry-Run Request Builder (Milestone 56A).

Verifies that build_dry_run_request only produces a dry_run_request when
approval_validation is fully valid and allow_dry_run.  All execution flags
remain false.
"""

from __future__ import annotations

import pytest


@pytest.fixture()
def _build():
    from aether.action.dry_run_request import build_dry_run_request
    return build_dry_run_request


# ======================== TEST 1-5: REJECTION CASES ======================== #


class TestRejectionCases:
    """Tests 1-5: Returns None when conditions not met."""

    def test_none_when_approval_validation_is_none(self, _build):
        result = _build(approval_validation=None, requested_action={"tool_id": "x"})
        assert result is None

    def test_none_when_approval_valid_false(self, _build):
        val = {"approval_valid": False, "decision": "not_approved"}
        result = _build(approval_validation=val, requested_action={"tool_id": "x"})
        assert result is None

    def test_none_when_decision_not_allow_dry_run(self, _build):
        val = {
            "approval_valid": True,
            "decision": "action_mismatch",
            "dry_run_allowed": False,
        }
        result = _build(approval_validation=val, requested_action={"tool_id": "x"})
        assert result is None

    def test_none_when_dry_run_allowed_false(self, _build):
        val = {
            "approval_valid": True,
            "decision": "allow_dry_run",
            "dry_run_allowed": False,
        }
        result = _build(approval_validation=val, requested_action={"tool_id": "x"})
        assert result is None

    def test_none_when_requested_action_missing(self, _build):
        val = {
            "approval_valid": True,
            "decision": "allow_dry_run",
            "dry_run_allowed": True,
        }
        result = _build(approval_validation=val, requested_action=None)
        assert result is None


# ======================== TEST 6-12: VALID CREATION ======================== #


class TestValidDryRunRequest:
    """Tests 6-12: Valid approval creates dry_run_request with correct fields."""

    def test_valid_creation(self, _build):
        val = _make_valid_validation("test-aid", "approved", "shell.run")
        ra = {"tool_id": "shell.run", "action_type": "execute"}
        result = _build(approval_validation=val, requested_action=ra)
        assert result is not None
        assert result["dry_run_required"] is True
        assert result["dry_run_status"] == "pending"
        assert result["dry_run_type"] == "action_simulation"

    def test_dry_run_status_pending(self, _build):
        val = _make_valid_validation("test-aid", "approved", "shell.run")
        result = _build(approval_validation=val, requested_action={"tool_id": "shell.run"})
        assert result["dry_run_status"] == "pending"

    def test_dry_run_type_action_simulation(self, _build):
        val = _make_valid_validation("test-aid", "approved", "shell.run")
        result = _build(approval_validation=val, requested_action={"tool_id": "shell.run"})
        assert result["dry_run_type"] == "action_simulation"

    def test_execution_allowed_always_false(self, _build):
        val = _make_valid_validation("test-aid", "approved", "shell.run")
        result = _build(approval_validation=val, requested_action={"tool_id": "shell.run"})
        assert result["execution_allowed"] is False

    def test_tool_execution_allowed_always_false(self, _build):
        val = _make_valid_validation("test-aid", "approved", "shell.run")
        result = _build(approval_validation=val, requested_action={"tool_id": "shell.run"})
        assert result["tool_execution_allowed"] is False

    def test_apply_allowed_always_false(self, _build):
        val = _make_valid_validation("test-aid", "approved", "shell.run")
        result = _build(approval_validation=val, requested_action={"tool_id": "shell.run"})
        assert result["apply_allowed"] is False

    def test_rollback_allowed_always_false(self, _build):
        val = _make_valid_validation("test-aid", "approved", "shell.run")
        result = _build(approval_validation=val, requested_action={"tool_id": "shell.run"})
        assert result["rollback_allowed"] is False


# ======================== TEST 13-19: CONTENT PRESERVATION & WARNINGS ======================== #


class TestContentPreservation:
    """Tests 13-19: Fields preserved, metadata, safety checks, warnings."""

    def test_requested_action_preserved(self, _build):
        ra = {"tool_id": "shell.run", "parameters": {"arg": "a"}}
        val = _make_valid_validation("test-aid", "approved", "shell.run")
        result = _build(approval_validation=val, requested_action=ra)
        assert result["requested_action"]["tool_id"] == "shell.run"
        assert result["requested_action"]["parameters"]["arg"] == "a"

    def test_approval_validation_snapshot_preserved(self, _build):
        val = _make_valid_validation("test-aid", "approved", "shell.run")
        ra = {"tool_id": "shell.run"}
        result = _build(approval_validation=val, requested_action=ra)
        snap = result["approval_validation_snapshot"]
        assert snap["approval_id"] == "test-aid"
        assert snap["decision"] == "allow_dry_run"

    def test_metadata_source_and_schema_version(self, _build):
        val = _make_valid_validation("test-aid", "approved", "shell.run")
        result = _build(approval_validation=val, requested_action={"tool_id": "shell.run"})
        meta = result["metadata"]
        assert meta["source"] == "dry_run_request_builder"
        assert meta["schema_version"] == "1.0"

    def test_context_session_id_copied(self, _build):
        val = _make_valid_validation("test-aid", "approved", "shell.run")
        ctx = {"session_id": "test-sid-42"}
        result = _build(
            approval_validation=val,
            requested_action={"tool_id": "shell.run"},
            context=ctx,
        )
        assert result["metadata"]["session_id"] == "test-sid-42"

    def test_safety_checks_include_no_real_tool(self, _build):
        val = _make_valid_validation("test-aid", "approved", "shell.run")
        result = _build(approval_validation=val, requested_action={"tool_id": "shell.run"})
        checks = result["safety_checks"]
        assert any("real tools" in c for c in checks)
        assert any("apply remains disabled" in c for c in checks)
        assert any("no persistent state" in c for c in checks)

    def test_warning_on_execution_allowed_true(self, _build):
        val = _make_valid_validation("test-aid", "approved", "shell.run")
        val["execution_allowed"] = True
        result = _build(approval_validation=val, requested_action={"tool_id": "shell.run"})
        assert result is not None
        assert len(result["warnings"]) > 0
        assert any("execution_allowed=true" in w for w in result["warnings"])

    def test_warning_on_tool_execution_allowed_true(self, _build):
        val = _make_valid_validation("test-aid", "approved", "shell.run")
        val["tool_execution_allowed"] = True
        result = _build(approval_validation=val, requested_action={"tool_id": "shell.run"})
        assert result is not None
        assert len(result["warnings"]) > 0
        assert any("tool_execution_allowed=true" in w for w in result["warnings"])


# ======================== Helper ======================== #


def _make_valid_validation(approval_id: str, status: str, tool_id: str) -> dict:
    """Return a minimal valid approval validation dict."""
    return {
        "approval_valid": True,
        "decision": "allow_dry_run",
        "reason": "Approval is valid.",
        "approval_id": approval_id,
        "approval_status": status,
        "requested_action": {"tool_id": tool_id},
        "approval_record": None,
        "matched_fields": ["tool_id"],
        "mismatched_fields": [],
        "execution_allowed": False,
        "dry_run_allowed": True,
        "tool_execution_allowed": False,
        "warnings": [],
    }
