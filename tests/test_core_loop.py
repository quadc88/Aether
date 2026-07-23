"""Tests for core chat loop (Milestone 48B).

All imports use the explicit module path pattern:
    import aether.core.loop as core_loop
to avoid `aether.core` not exposing `loop` as an attribute at import time.
"""

from unittest import mock

import pytest


@pytest.fixture()
def patched_core_loop(monkeypatch):
    """Return the core_loop module with mocks applied in-place.

    This fixture patches identity verification, timeline recording, and
    tool inference so that no filesystem I/O or guard state is needed.
    Safe summary is returned for identity checks.
    """
    import aether.core.loop as core_loop

    safe_summary = {
        "status": "not_initialized",
        "current_sha256": "",
        "known_sha256": "",
        "changed": False,
        "updated": None,
        "warnings": ["Guard not initialized."],
    }

    monkeypatch.setattr(
        core_loop, "verify_identity_integrity", lambda *a, **k: safe_summary
    )
    monkeypatch.setattr(core_loop, "record_event", lambda *a, **k: {"id": "test_evt"})
    monkeypatch.setattr(core_loop, "time_state", lambda: {"timezone": "UTC", "now": "00:00:00", "iso": "2026-01-01T00:00:00+00:00"})

    # Patch tool_planner since _suggest_tool imports it at runtime
    import aether.action.tool_planner as tpl
    monkeypatch.setattr(tpl, "infer_candidate_tool", lambda *a, **k: {"candidate_tool": {}})

    return core_loop


class TestCoreLoopStructure:
    def test_returns_required_fields(self, patched_core_loop):
        from aether.memory.working.store import WorkingMemory

        wm = WorkingMemory()
        result = patched_core_loop.run_core_chat_loop(
            text="hello there",
            working_memory=wm,
            session_id="test-1",
        )

        required_keys = {
            "status", "session_id", "loop_version", "time",
            "identity_integrity_status", "perception", "risk",
            "suggested_tool", "tool_execution_allowed",
            "tool_executed", "response_text",
            "memory_recorded", "timeline_recorded", "warnings",
            "thinking_policy", "decision_type",
            "required_user_confirmation", "clarification_question",
            "blocked_reason",
            # Policy Enforcement Gate (Milestone 51A)
            "policy_gate", "execution_allowed", "execution_decision", "execution_reason",
        }
        assert set(result.keys()) >= required_keys

    def test_tool_executed_is_false(self, patched_core_loop):
        result = patched_core_loop.run_core_chat_loop(text="run python script")
        assert result["tool_executed"] is False

    def test_tool_execution_not_allowed(self, patched_core_loop):
        result = patched_core_loop.run_core_chat_loop(text="test")
        assert result["tool_execution_allowed"] is False

    def test_response_not_empty(self, patched_core_loop):
        result = patched_core_loop.run_core_chat_loop(text="how are you")
        assert len(result["response_text"]) > 0
        assert "Aether received" in result["response_text"]

    def test_has_risk_result(self, patched_core_loop):
        result = patched_core_loop.run_core_chat_loop(text="what time is it")
        assert result["risk"] is not None
        assert "risk_level" in result["risk"]

    def test_perception_structured(self, patched_core_loop):
        result = patched_core_loop.run_core_chat_loop(text="你好吗？")
        perception = result["perception"]
        assert perception["type"] == "text"
        assert perception["language_hint"] in ("zh", "mixed")
        assert perception["contains_question"] is True

    def test_memory_recorded_true(self, patched_core_loop):
        from aether.memory.working.store import WorkingMemory

        wm = WorkingMemory()
        result = patched_core_loop.run_core_chat_loop(text="test", working_memory=wm)
        assert result["memory_recorded"] is True

    def test_empty_input_error(self, patched_core_loop):
        result = patched_core_loop.run_core_chat_loop(text="   ")
        assert result["status"] == "error"
        assert result["memory_recorded"] is False

    def test_identity_integrity_included(self, patched_core_loop):
        result = patched_core_loop.run_core_chat_loop(text="verify my identity")
        assert "identity_integrity_status" in result


class TestSuggestToolShapeCompatibility:
    """_suggest_tool must handle both top-level and nested tool_id shapes."""

    def test_handles_top_level_tool_id(self, monkeypatch):
        import aether.core.loop as core_loop
        from aether.memory.working.store import WorkingMemory

        fake_suggestion = {
            "tool_id": "test.tool",
            "name": "Test Tool",
            "match_confidence": "likely",
        }
        import aether.action.tool_planner as tpl
        monkeypatch.setattr(tpl, "infer_candidate_tool", lambda *a, **k: fake_suggestion)

        result = core_loop.run_core_chat_loop(
            text="do the thing", working_memory=WorkingMemory(),
        )
        assert result["suggested_tool"] is not None
        assert result["suggested_tool"]["tool_id"] == "test.tool"

    def test_handles_nested_candidate_tool(self, monkeypatch):
        import aether.core.loop as core_loop
        from aether.memory.working.store import WorkingMemory

        fake_suggestion = {
            "candidate_tool": {
                "tool_id": "nested.tool",
                "name": "Nested Tool",
            }
        }
        import aether.action.tool_planner as tpl
        monkeypatch.setattr(tpl, "infer_candidate_tool", lambda *a, **k: fake_suggestion)

        result = core_loop.run_core_chat_loop(
            text="do something", working_memory=WorkingMemory(),
        )
        assert result["suggested_tool"] is not None
        assert result["suggested_tool"]["tool_id"] == "nested.tool"

    def test_returns_none_when_no_tool_id(self, monkeypatch):
        import aether.core.loop as core_loop

        fake_suggestion = {"unknown_key": "value"}
        import aether.action.tool_planner as tpl
        monkeypatch.setattr(tpl, "infer_candidate_tool", lambda *a, **k: fake_suggestion)

        result = core_loop.run_core_chat_loop(text="test")
        assert result["suggested_tool"] is None


class TestPolicyGateIntegration:
    """Tests 10-13: Policy enforcement gate in core loop (Milestone 51A)."""

    def test_core_loop_includes_policy_gate(self, patched_core_loop):
        result = patched_core_loop.run_core_chat_loop(text="hello world")
        assert "policy_gate" in result
        assert result["policy_gate"] is not None
        assert isinstance(result["policy_gate"], dict)

    def test_execution_allowed_false_by_default(self, patched_core_loop):
        result = patched_core_loop.run_core_chat_loop(text="hello world")
        assert result["execution_allowed"] is False
        assert result["tool_execution_allowed"] is False

    def test_high_risk_memory_deletion_returns_require_approval_or_block(self, patched_core_loop):
        result = patched_core_loop.run_core_chat_loop(
            text="Delete all private memory and remove the identity seed."
        )
        assert result["status"] == "completed"
        assert result["execution_decision"] in ("require_approval", "block", "deny")

    def test_tool_suggesting_low_risk_returns_deny(self, patched_core_loop):
        result = patched_core_loop.run_core_chat_loop(
            text="what time is it"
        )
        assert result["status"] == "completed"
        # tool_execution_allowed is always False in current policy
        assert result["execution_decision"] == "deny"
        assert result["execution_allowed"] is False


class TestNoToolExecutionEvenWhenAllowed:
    def test_force_no_execution(self, patched_core_loop):
        # Even with allow_tool_execution=True, nothing should execute
        result = patched_core_loop.run_core_chat_loop(
            text="delete all files",
            allow_tool_execution=True,
        )
        assert result["tool_executed"] is False
        assert result["tool_execution_allowed"] is False
