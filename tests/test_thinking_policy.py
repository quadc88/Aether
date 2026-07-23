"""Tests for thinking policy layer (Milestone 49A)."""

from __future__ import annotations

from aether.thinking.policy import decide_chat_policy


class TestIdentityChanged:
    def test_block_on_identity_changed(self):
        result = decide_chat_policy(
            perception={"normalized_text": "hello"},
            risk={"risk_level": "low", "action_type": "general_request"},
            identity_integrity_status={"status": "changed"},
        )
        assert result["decision_type"] == "block"
        assert result["required_user_confirmation"] is True
        assert result["tool_execution_allowed"] is False
        assert result["blocked_reason"] is not None
        assert result["tool_suggestion_allowed"] is False

    def test_block_even_with_tool_and_medium_risk(self):
        """Rule 1 overrides all lower-priority rules."""
        result = decide_chat_policy(
            perception={"normalized_text": "edit file x.py"},
            risk={"risk_level": "medium", "action_type": "file_edit"},
            suggested_tool={"tool_id": "file.edit"},
            identity_integrity_status={"status": "changed"},
        )
        assert result["decision_type"] == "block"


class TestIdentityMissingOrFailed:
    def test_require_approval_when_missing(self):
        result = decide_chat_policy(
            perception={"normalized_text": "hello"},
            risk={"risk_level": "low", "action_type": "general_request"},
            identity_integrity_status={"status": "missing"},
        )
        assert result["decision_type"] == "require_approval"
        assert result["required_user_confirmation"] is True

    def test_require_approval_when_failed(self):
        result = decide_chat_policy(
            perception={"normalized_text": "hello"},
            risk={"risk_level": "low", "action_type": "general_request"},
            identity_integrity_status={"status": "failed"},
        )
        assert result["decision_type"] == "require_approval"


class TestEmptyInput:
    def test_ask_clarification_for_empty_text(self):
        result = decide_chat_policy(
            perception={"normalized_text": ""},
            risk={"risk_level": "low", "action_type": "general_request"},
        )
        assert result["decision_type"] == "ask_clarification"
        assert result["clarification_question"] is not None

    def test_ask_clarification_for_whitespace_only(self):
        result = decide_chat_policy(
            perception={"normalized_text": "   "},
            risk={"risk_level": "low", "action_type": "general_request"},
        )
        assert result["decision_type"] == "ask_clarification"


class TestSecretRiskTerms:
    def test_require_approval_on_password_term(self):
        result = decide_chat_policy(
            perception={
                "normalized_text": "reset my password please",
                "risk_terms_detected": ["password"],
            },
            risk={"risk_level": "low", "action_type": "general_request"},
        )
        assert result["decision_type"] == "require_approval"
        assert result["tool_execution_allowed"] is False

    def test_require_approval_on_token_term(self):
        result = decide_chat_policy(
            perception={
                "normalized_text": "check my api token",
                "risk_terms_detected": ["token"],
            },
            risk={"risk_level": "low", "action_type": "general_request"},
        )
        assert result["decision_type"] == "require_approval"

    def test_no_secret_flags_without_risk_terms(self):
        result = decide_chat_policy(
            perception={"normalized_text": "tell me a joke", "risk_terms_detected": []},
            risk={"risk_level": "low", "action_type": "general_request"},
        )
        # Low-risk no secrets → respond_only
        assert result["decision_type"] in ("respond_only", "suggest_tool")


class TestHighRisk:
    def test_high_risk_requires_approval(self):
        result = decide_chat_policy(
            perception={"normalized_text": "delete this file"},
            risk={"risk_level": "high", "action_type": "file_delete"},
        )
        assert result["decision_type"] == "require_approval"
        assert result["required_user_confirmation"] is True

    def test_high_risk_override_over_memoed_tool(self):
        result = decide_chat_policy(
            perception={"normalized_text": "edit config.yaml"},
            risk={"risk_level": "high", "action_type": "file_edit"},
            suggested_tool={"tool_id": "file.edit"},
        )
        assert result["decision_type"] == "require_approval"


class TestMediumRiskWithTool:
    def test_medium_risk_tool_requires_approval(self):
        result = decide_chat_policy(
            perception={"normalized_text": "edit the README"},
            risk={"risk_level": "medium", "action_type": "file_edit"},
            suggested_tool={"tool_id": "file.edit"},
        )
        assert result["decision_type"] == "require_approval"
        assert result["tool_suggestion_allowed"] is True
        assert result["tool_execution_allowed"] is False


class TestLowRiskWithTool:
    def test_low_risk_tool_suggests_but_not_executes(self):
        result = decide_chat_policy(
            perception={"normalized_text": "what time is it"},
            risk={"risk_level": "low", "action_type": "general_request"},
            suggested_tool={"tool_id": "clock.time"},
        )
        assert result["decision_type"] == "suggest_tool"
        assert result["tool_suggestion_allowed"] is True
        assert result["tool_execution_allowed"] is False


class TestNoToolShortInput:
    def test_short_input_no_tool_asks_clarification(self):
        result = decide_chat_policy(
            perception={"normalized_text": "hi"},
            risk={"risk_level": "low", "action_type": "general_request"},
            suggested_tool=None,
        )
        assert result["decision_type"] == "ask_clarification"
        assert len("hi") < 10


class TestDefaultRespondOnly:
    def test_normal_conversation_respond_only(self):
        result = decide_chat_policy(
            perception={"normalized_text": "Tell me about the weather today."},
            risk={"risk_level": "low", "action_type": "general_request"},
            suggested_tool=None,
        )
        assert result["decision_type"] == "respond_only"
        assert result["tool_execution_allowed"] is False
        assert result["required_user_confirmation"] is False


class TestHardRules:
    def test_tool_execution_always_false(self):
        """tool_execution_allowed must ALWAYS be false in Milestone 49A."""
        for status in ("verified", "changed", "missing", "failed", None):
            for risk_level in ("low", "medium", "high"):
                for has_tool in (True, False):
                    tool = {"tool_id": "test.tool"} if has_tool else None
                    result = decide_chat_policy(
                        perception={"normalized_text": "test input", "risk_terms_detected": []},
                        risk={"risk_level": risk_level, "action_type": "general_request"},
                        suggested_tool=tool,
                        identity_integrity_status={"status": status} if status else None,
                    )
                    assert result["tool_execution_allowed"] is False, (
                        f"Failed for status={status}, risk={risk_level}, tool={has_tool}"
                    )

    def test_decision_has_all_fields(self):
        result = decide_chat_policy(
            perception={"normalized_text": "hello"},
            risk={"risk_level": "low", "action_type": "general_request"},
        )
        expected_keys = {
            "decision_type", "confidence", "reasons",
            "required_user_confirmation", "tool_suggestion_allowed",
            "tool_execution_allowed", "blocked_reason",
            "clarification_question", "next_step", "warnings",
        }
        assert set(result.keys()) >= expected_keys


class TestConfidenceLevels:
    def test_identity_issues_have_high_confidence(self):
        for status in ("changed", "missing", "failed"):
            r = decide_chat_policy(
                perception={"normalized_text": "x"},
                risk={"risk_level": "low", "action_type": "general_request"},
                identity_integrity_status={"status": status},
            )
            assert r["confidence"] == "high"

    def test_default_has_medium_confidence(self):
        r = decide_chat_policy(
            perception={"normalized_text": "hello world this is a normal sentence"},
            risk={"risk_level": "low", "action_type": "general_request"},
        )
        assert r["confidence"] in ("medium", "low")
