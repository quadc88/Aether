"""Tests for Approval Request Builder (Milestone 52A).

Verifies that structured approval_request objects are created when
policy_gate returns require_approval or block.
"""

from __future__ import annotations

import pytest


@pytest.fixture()
def _build():
    from aether.action.approval_request import build_approval_request
    return build_approval_request


# ======================== TESTS 1-13: UNIT TESTS ======================== #


class TestNoApprovalNeeded:
    """Test 1: build_approval_request returns None when no approval is needed."""

    def test_returns_none_for_allow_decision(self, _build):
        policy_gate = {
            "allowed": True,
            "decision": "allow",
            "required_user_confirmation": False,
            "tool_execution_allowed": True,
        }
        thinking_policy = {"decision_type": "respond_only"}
        result = _build(policy_gate=policy_gate, thinking_policy=thinking_policy)
        assert result is None

    def test_returns_none_for_deny_with_no_confirm(self, _build):
        policy_gate = {
            "allowed": False,
            "decision": "deny",
            "required_user_confirmation": False,
            "tool_execution_allowed": False,
        }
        thinking_policy = {"decision_type": "respond_only", "required_user_confirmation": False}
        result = _build(policy_gate=policy_gate, thinking_policy=thinking_policy)
        assert result is None


class TestRequireApproval:
    """Test 2: require_approval gate returns approval_request with approval_required true."""

    def test_require_approval_gate(self, _build):
        policy_gate = {
            "allowed": False,
            "decision": "require_approval",
            "reason": "Human approval is required before execution.",
        }
        result = _build(policy_gate=policy_gate)
        assert result is not None
        assert result["approval_required"] is True
        assert result["approval_status"] == "pending"
        assert result["approval_type"] == "human_review"
        assert "Human approval" in result["reason"]


class TestBlockApproval:
    """Test 3: block gate returns approval_type blocked_identity_review."""

    def test_block_decision(self, _build):
        policy_gate = {
            "allowed": False,
            "decision": "block",
            "reason": "Identity integrity changed.",
        }
        result = _build(policy_gate=policy_gate)
        assert result is not None
        assert result["approval_type"] == "blocked_identity_review"
        assert result["approval_required"] is True

    def test_thinking_policy_block(self, _build):
        policy_gate = {
            "allowed": False,
            "decision": "deny",
        }
        thinking_policy = {
            "decision_type": "block",
            "blocked_reason": "Identity checksum mismatch.",
        }
        result = _build(
            policy_gate=policy_gate,
            thinking_policy=thinking_policy,
        )
        assert result is not None
        assert result["approval_type"] == "blocked_identity_review"
        assert "checksum" in result["reason"].lower() or "identity" in result["reason"].lower()


class TestInvalidPolicyApproval:
    """Test 4: invalid_policy gate returns approval_type invalid_policy_review."""

    def test_invalid_policy_decision(self, _build):
        policy_gate = {
            "allowed": False,
            "decision": "invalid_policy",
            "reason": "Missing thinking policy.",
        }
        result = _build(policy_gate=policy_gate)
        assert result is not None
        assert result["approval_type"] == "invalid_policy_review"
        assert result["approval_required"] is True


class TestHighRiskConfirmations:
    """Test 5: high risk adds high-risk confirmations."""

    def test_high_risk_adds_confirmations(self, _build):
        policy_gate = {
            "allowed": False,
            "decision": "require_approval",
            "reason": "Human approval is required.",
        }
        risk = {"risk_level": "high", "action_type": "file_delete"}
        result = _build(policy_gate=policy_gate, risk=risk)
        confirmations = result["required_confirmations"]
        assert "Confirm high-risk operation details." in confirmations
        assert "Confirm backup or rollback strategy if applicable." in confirmations


class TestIdentityConfirmation:
    """Test 6: identity_change adds identity confirmation."""

    def test_identity_action_confirms(self, _build):
        policy_gate = {
            "allowed": False,
            "decision": "require_approval",
        }
        risk = {"risk_level": "high", "action_type": "identity_change"}
        result = _build(policy_gate=policy_gate, risk=risk)
        confirmations = result["required_confirmations"]
        assert "Confirm identity seed is not modified without explicit approval." in confirmations


class TestMemoryPrivateConfirmation:
    """Test 7: destructive_memory_action adds memory/private data confirmation."""

    def test_memory_action_confirms(self, _build):
        policy_gate = {
            "allowed": False,
            "decision": "require_approval",
        }
        risk = {"risk_level": "high", "action_type": "destructive_memory_action"}
        result = _build(policy_gate=policy_gate, risk=risk)
        confirmations = result["required_confirmations"]
        assert "Confirm memory/private data target and scope." in confirmations


class TestRequestedActionPreserved:
    """Test 8: requested_action is preserved."""

    def test_requested_action_in_result(self, _build):
        policy_gate = {"allowed": False, "decision": "require_approval"}
        action = {"tool_id": "shell.run", "command": "ls -la"}
        result = _build(policy_gate=policy_gate, requested_action=action)
        assert result["requested_action"] == action


class TestMetadataFields:
    """Test 9: metadata includes schema_version and source."""

    def test_metadata_has_standard_fields(self, _build):
        policy_gate = {"allowed": False, "decision": "require_approval"}
        result = _build(policy_gate=policy_gate)
        meta = result["metadata"]
        assert meta["source"] == "approval_request_builder"
        assert meta["schema_version"] == "1.0"


class TestContextSessionId:
    """Test 10: context session_id is copied into metadata."""

    def test_session_id_from_context(self, _build):
        policy_gate = {"allowed": False, "decision": "require_approval"}
        result = _build(
            policy_gate=policy_gate,
            context={"session_id": "test-session-123"},
        )
        assert result["metadata"]["session_id"] == "test-session-123"


class TestPerceptionLanguageHint:
    """Test 11: perception language_hint is copied into metadata."""

    def test_language_hint_from_perception(self, _build):
        policy_gate = {"allowed": False, "decision": "require_approval"}
        result = _build(
            policy_gate=policy_gate,
            perception={"language_hint": "zh"},
        )
        assert result["metadata"]["language_hint"] == "zh"


class TestApprovalStatusPending:
    """Test 12: approval_status is pending."""

    def test_status_always_pending(self, _build):
        for decision in ("require_approval", "block", "invalid_policy"):
            policy_gate = {"allowed": False, "decision": decision}
            result = _build(policy_gate=policy_gate)
            assert result["approval_status"] == "pending"


class TestNoExecutionFieldsAllow:
    """Test 13: no execution fields allow action."""

    def test_approval_does_not_enable_execution(self, _build):
        policy_gate = {"allowed": False, "decision": "require_approval"}
        result = _build(policy_gate=policy_gate)
        # The approval request is just a data object — it doesn't set any
        # tool_execution_allowed, execution_allowed, or action fields.
        assert "tool_execution_allowed" not in result
        assert "execution_allowed" not in result
        assert "action_execution_allowed" not in result
