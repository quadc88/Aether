"""Tests for Policy Enforcement Gate (Milestone 51A).

Verifies that the central execution gate blocks all tool/action
execution unless thinking_policy explicitly allows it.
"""

from __future__ import annotations

import pytest


@pytest.fixture()
def _gate():
    from aether.action.policy_gate import enforce_policy_gate
    return enforce_policy_gate


# ======================== PART D-1 TO 9: POLICY GATE UNIT TESTS ======================== #


class TestMissingPolicy:
    """Test 1: Missing thinking_policy → invalid_policy, allowed false."""

    def test_missing_thinking_policy_returns_invalid_policy(self, _gate):
        result = _gate(thinking_policy=None)
        assert result["allowed"] is False
        assert result["decision"] == "invalid_policy"
        assert result["reason"] == "Missing thinking policy."
        assert result["required_user_confirmation"] is True
        assert result["tool_execution_allowed"] is False
        assert result["action_execution_allowed"] is False


class TestBlockDecision:
    """Test 2: decision_type block → block, allowed false."""

    def test_block_decision_type(self, _gate):
        policy = {
            "decision_type": "block",
            "blocked_reason": "Identity integrity changed.",
            "required_user_confirmation": True,
            "tool_execution_allowed": False,
        }
        result = _gate(thinking_policy=policy)
        assert result["allowed"] is False
        assert result["decision"] == "block"
        assert result["reason"] == "Identity integrity changed."
        assert result["required_user_confirmation"] is True
        assert result["tool_execution_allowed"] is False
        assert result["action_execution_allowed"] is False

    def test_block_without_blocked_reason(self, _gate):
        policy = {
            "decision_type": "block",
            "required_user_confirmation": True,
            "tool_execution_allowed": False,
        }
        result = _gate(thinking_policy=policy)
        assert result["decision"] == "block"
        assert result["reason"] == "Policy blocked this action."


class TestRequireApprovalDecision:
    """Test 3: decision_type require_approval → require_approval, allowed false."""

    def test_require_approval_decision(self, _gate):
        policy = {
            "decision_type": "require_approval",
            "required_user_confirmation": True,
            "tool_execution_allowed": False,
        }
        result = _gate(thinking_policy=policy)
        assert result["allowed"] is False
        assert result["decision"] == "require_approval"
        assert result["reason"] == "Human approval is required before execution."
        assert result["required_user_confirmation"] is True
        assert result["tool_execution_allowed"] is False
        assert result["action_execution_allowed"] is False


class TestDenyWhenToolNotAllowed:
    """Test 4 & 5: tool_execution_allowed not True → deny, allowed false."""

    def test_suggest_tool_but_no_execution(self, _gate):
        policy = {
            "decision_type": "suggest_tool",
            "required_user_confirmation": False,
            "tool_execution_allowed": False,
        }
        result = _gate(thinking_policy=policy)
        assert result["allowed"] is False
        assert result["decision"] == "deny"
        assert result["reason"] == "Tool execution is not allowed by policy."
        assert result["tool_execution_allowed"] is False
        assert result["action_execution_allowed"] is False

    def test_respond_only_with_no_execution(self, _gate):
        policy = {
            "decision_type": "respond_only",
            "required_user_confirmation": False,
            "tool_execution_allowed": False,
        }
        result = _gate(thinking_policy=policy)
        assert result["allowed"] is False
        assert result["decision"] == "deny"
        assert result["tool_execution_allowed"] is False
        assert result["action_execution_allowed"] is False

    def test_ask_clarification_with_no_execution(self, _gate):
        policy = {
            "decision_type": "ask_clarification",
            "required_user_confirmation": False,
            "tool_execution_allowed": False,
        }
        result = _gate(thinking_policy=policy)
        assert result["allowed"] is False
        assert result["decision"] == "deny"


class TestAllowWhenExplicitlyAllowed:
    """Test 6: Artificial policy with tool_execution_allowed true → allow."""

    def test_tool_execution_allowed_true(self, _gate):
        policy = {
            "decision_type": "respond_only",
            "required_user_confirmation": False,
            "tool_execution_allowed": True,
        }
        result = _gate(thinking_policy=policy)
        assert result["allowed"] is True
        assert result["decision"] == "allow"
        assert result["reason"] == "Policy allows execution."
        assert result["required_user_confirmation"] is False
        assert result["tool_execution_allowed"] is True
        assert result["action_execution_allowed"] is True


class TestActionPreservation:
    """Test 7: requested_action is preserved in response."""

    def test_requested_action_preserved(self, _gate):
        policy = {
            "decision_type": "respond_only",
            "required_user_confirmation": False,
            "tool_execution_allowed": False,
        }
        action = {"tool_id": "file.restricted_read", "path": "/etc/hosts"}
        result = _gate(thinking_policy=policy, requested_action=action)
        assert result["requested_action"] == action


class TestPolicySnapshot:
    """Test 8: policy_snapshot is preserved."""

    def test_policy_snapshot_preserved(self, _gate):
        policy = {
            "decision_type": "require_approval",
            "required_user_confirmation": True,
            "tool_execution_allowed": False,
            "confidence": "high",
        }
        result = _gate(thinking_policy=policy)
        snapshot = result["policy_snapshot"]
        assert snapshot["decision_type"] == "require_approval"
        assert snapshot["confidence"] == "high"
        assert snapshot is not policy

    def test_policy_snapshot_with_missing_policy(self, _gate):
        result = _gate(thinking_policy=None)
        assert result["policy_snapshot"] is None


class TestActionExecutionAllowedMirrors:
    """Test 9: action_execution_allowed mirrors allowed true only when allowed."""

    def test_action_execution_allowed_false_when_denied(self, _gate):
        policy = {
            "decision_type": "require_approval",
            "required_user_confirmation": True,
            "tool_execution_allowed": False,
        }
        result = _gate(thinking_policy=policy)
        assert result["action_execution_allowed"] is False
        assert result["allowed"] is False

    def test_action_execution_allowed_true_when_allowed(self, _gate):
        policy = {
            "decision_type": "respond_only",
            "tool_execution_allowed": True,
        }
        result = _gate(thinking_policy=policy)
        assert result["action_execution_allowed"] is True
        assert result["allowed"] is True

    def test_action_execution_allowed_false_on_missing_policy(self, _gate):
        result = _gate(thinking_policy=None)
        assert result["action_execution_allowed"] is False
        assert result["allowed"] is False
