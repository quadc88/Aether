"""API-level tests for /chat endpoint (Milestone 48B response fix).

Tests the HTTP request/response shape without spinning up the server.
Uses FastAPI TestClient.
"""

from fastapi.testclient import TestClient

# Import the app module so we can create a TestClient instance.
# Do NOT use conftest.py — import here so fixtures in test_core_loop.py don't conflict.
import sys


def _get_test_client():
    """Create a TestClient that imports api_server fresh each time.

    api_server creates a module-level `runtime = AetherRuntime()`.  Wrapping
    the import in a function means any cached state from previous tests is
    avoided when pytest re-imports the module.
    """
    from importlib import reload
    # Force re-import so runtime is fresh (not pre-awakened with stale guard)
    import aether.interface.api_server as ap_mod
    reload(ap_mod)
    return TestClient(ap_mod.app)


class TestChatEndpoint:
    client = None

    @classmethod
    def setup_class(cls):
        cls.client = _get_test_client()

    def test_accepts_text_field(self):
        """POST /chat with {\"text\": ...} returns core-loop fields."""
        resp = self.client.post("/chat", json={"text": "hello from text"})
        data = resp.json()

        assert data["status"] == "completed"
        assert "response_text" in data or data.get("response")
        assert "working_memory_event_count" in data

    def test_accepts_legacy_message_field(self):
        """Legacy POST /chat with {\"message\": ...} must NOT return 422."""
        resp = self.client.post("/chat", json={"message": "hello legacy"})
        data = resp.json()

        assert resp.status_code == 200
        assert data["status"] == "completed"

    def test_returns_core_loop_fields(self):
        """Response must include structured core-loop skeleton fields."""
        resp = self.client.post("/chat", json={"text": "field check"})
        data = resp.json()

        required = [
            "status",
            "session_id",
            "loop_version",
            "time",
            "identity_integrity_status",
            "perception",
            "risk",
            "suggested_tool",
            "tool_execution_allowed",
            "tool_executed",
            "response_text",
            "memory_recorded",
            "timeline_recorded",
            "warnings",
            "working_memory_event_count",
            "thinking_policy",
            "decision_type",
        ]
        missing = [f for f in required if f not in data]
        assert not missing, f"Missing core-loop fields: {missing}"

    def test_tool_execution_not_allowed(self):
        """tool_execution_allowed must be False even if request sends True."""
        resp = self.client.post(
            "/chat",
            json={
                "text": "test flag",
                "allow_tool_execution": True,
            },
        )
        data = resp.json()
        assert data["tool_execution_allowed"] is False

    def test_tool_executed_is_false(self):
        """tool_executed must always be False in this milestone."""
        resp = self.client.post("/chat", json={"text": "test exec"})
        data = resp.json()
        assert data["tool_executed"] is False

    def test_missing_both_text_and_message_returns_error(self):
        """Empty body should produce safe error, NOT 422."""
        resp = self.client.post("/chat", json={})
        data = resp.json()
        assert resp.status_code == 200
        assert data["status"] == "error"
        assert len(data.get("warnings", [])) > 0

    def test_perception_includes_type(self):
        """Perception dict must have type, language_hint etc."""
        resp = self.client.post("/chat", json={"text": "你好吗？"})
        data = resp.json()
        perception = data.get("perception")
        assert perception is not None
        assert perception["type"] == "text"
        assert perception["language_hint"] in ("zh", "mixed")

    def test_risk_present(self):
        """Risk classification must be present."""
        resp = self.client.post("/chat", json={"text": "test risk"})
        data = resp.json()
        assert data.get("risk") is not None
        assert "risk_level" in data["risk"]

    def test_thinking_policy_in_response(self):
        """Response must include thinking_policy and decision_type."""
        resp = self.client.post("/chat", json={"text": "hello"})
        data = resp.json()
        assert "thinking_policy" in data
        assert "decision_type" in data
        tp = data["thinking_policy"]
        assert tp["tool_execution_allowed"] is False

    def test_legacy_message_works_with_thinking_policy(self):
        """Legacy message field should still produce a full response."""
        resp = self.client.post("/chat", json={"message": "legacy msg"})
        data = resp.json()
        assert data["status"] == "completed"
        assert "thinking_policy" in data
        assert data["thinking_policy"]["tool_execution_allowed"] is False
