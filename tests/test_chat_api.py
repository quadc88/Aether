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


class TestPolicyGateInApiResponse:
    """Tests 14-17: Policy gate fields in /chat API response (Milestone 51A)."""

    @classmethod
    def setup_class(cls):
        cls.client = _get_test_client()

    def test_chat_response_includes_policy_gate(self):
        """Test 14: /chat response includes policy_gate."""
        resp = self.client.post("/chat", json={"text": "hello from api"})
        data = resp.json()
        assert "policy_gate" in data
        assert data["policy_gate"] is not None
        assert isinstance(data["policy_gate"], dict)

    def test_chat_response_includes_execution_allowed(self):
        """Test 15: /chat response includes execution_allowed."""
        resp = self.client.post("/chat", json={"text": "check execution flag"})
        data = resp.json()
        assert "execution_allowed" in data
        assert data["execution_allowed"] is False

    def test_legacy_message_still_works_with_gate(self):
        """Test 16: legacy message still works with policy gate fields."""
        resp = self.client.post("/chat", json={"message": "legacy policy check"})
        data = resp.json()
        assert data["status"] == "completed"
        assert "policy_gate" in data
        assert data["execution_allowed"] is False

    def test_allow_tool_execution_true_does_not_bypass_gate(self):
        """Test 17: allow_tool_execution true in request does NOT bypass policy gate."""
        resp = self.client.post(
            "/chat",
            json={
                "text": "this should still be blocked",
                "allow_tool_execution": True,
            },
        )
        data = resp.json()
        assert data["execution_allowed"] is False
        assert data["tool_execution_allowed"] is False
        assert data["policy_gate"]["allowed"] is False


class TestApprovalRequestInApiResponse:
    """Tests 19-22: Approval request fields in /chat API response (Milestone 52A)."""

    @classmethod
    def setup_class(cls):
        cls.client = _get_test_client()

    def test_chat_response_includes_approval_request_fields(self):
        """Test 19: /chat response includes approval_request fields."""
        resp = self.client.post("/chat", json={"text": "hello from api"})
        data = resp.json()
        assert "approval_request" in data
        assert "approval_required" in data
        assert "approval_status" in data
        assert "approval_type" in data

    def test_chat_high_risk_memory_deletion_returns_approval_required_true(self):
        """Test 20: /chat high-risk memory deletion returns approval_required true."""
        resp = self.client.post("/chat", json={
            "text": "Delete all private memory and remove the identity seed.",
        })
        data = resp.json()
        assert data["approval_required"] is True
        assert data["approval_status"] == "pending"
        assert data["approval_request"] is not None

    def test_chat_normal_safe_input_returns_approval_required_false(self):
        """Test 21: /chat normal safe input returns approval_required false."""
        resp = self.client.post("/chat", json={"text": "hello world normal input"})
        data = resp.json()
        assert data["approval_required"] is False

    def test_chat_legacy_message_still_works(self):
        """Test 22: /chat legacy message still works."""
        resp = self.client.post("/chat", json={"message": "legacy msg milestone 52a"})
        data = resp.json()
        assert data["status"] == "completed"
        assert "approval_request" in data


class TestApprovalQueueAPI:
    """Tests 24-30: Approval queue endpoints (Milestone 54A)."""

    @classmethod
    def setup_class(cls):
        cls.client = _get_test_client()

    def test_high_risk_chat_response_includes_approval_id(self):
        """Test 21: /chat high-risk response includes approval_id."""
        resp = self.client.post("/chat", json={
            "text": "Delete all private memory and remove the identity seed.",
        })
        data = resp.json()
        assert data["status"] == "completed"
        assert data["approval_required"] is True
        assert data["approval_id"] is not None

    def test_high_risk_chat_response_includes_approval_record(self):
        """Test 22: /chat high-risk response includes approval_record."""
        resp = self.client.post("/chat", json={
            "text": "Delete all private memory and remove the identity seed.",
        })
        data = resp.json()
        assert data["approval_record"] is not None
        assert data["approval_record"]["status"] == "pending"

    def test_normal_chat_approval_id_is_none(self):
        """Test 23: /chat normal request has approval_id None."""
        resp = self.client.post("/chat", json={"text": "hello world"})
        data = resp.json()
        assert data["approval_id"] is None
        assert data["approval_record"] is None

    def test_get_approvals_lists_records(self):
        """Test 24: GET /approvals returns records list."""
        # First create a record via /chat
        self.client.post("/chat", json={
            "text": "Delete all private memory and remove the identity seed.",
        })
        resp = self.client.get("/approvals")
        data = resp.json()
        assert "approvals" in data
        assert "count" in data
        assert data["count"] >= 1

    def test_get_approval_by_id(self):
        """Test 25: GET /approvals/{id} reads record."""
        resp = self.client.post("/chat", json={
            "text": "Delete all private memory and remove the identity seed.",
        })
        data = resp.json()
        aid = data["approval_id"]
        resp2 = self.client.get(f"/approvals/{aid}")
        d2 = resp2.json()
        assert d2["found"] is True
        assert d2["approval"]["approval_id"] == aid

    def test_approve_changes_status_only(self):
        """Test 26: POST /approvals/{id}/approve changes status only."""
        # Create via /chat
        resp = self.client.post("/chat", json={
            "text": "Delete all private memory and remove the identity seed.",
        })
        aid = resp.json()["approval_id"]
        resp2 = self.client.post(
            f"/approvals/{aid}/approve",
            json={"reviewer": "alice", "reason": "reviewed"},
        )
        d2 = resp2.json()
        assert d2["approval"]["status"] == "approved"
        assert d2["approval"]["decision"] == "approved"

    def test_reject_changes_status_only(self):
        """Test 27: POST /approvals/{id}/reject changes status only."""
        resp = self.client.post("/chat", json={
            "text": "Delete all private memory and remove the identity seed.",
        })
        aid = resp.json()["approval_id"]
        resp2 = self.client.post(
            f"/approvals/{aid}/reject",
            json={"reviewer": "bob", "reason": "too risky"},
        )
        d2 = resp2.json()
        assert d2["approval"]["status"] == "rejected"

    def test_cancel_changes_status_only(self):
        """Test 28: POST /approvals/{id}/cancel changes status only."""
        resp = self.client.post("/chat", json={
            "text": "Delete all private memory and remove the identity seed.",
        })
        aid = resp.json()["approval_id"]
        resp2 = self.client.post(
            f"/approvals/{aid}/cancel",
            json={"reviewer": "carol"},
        )
        d2 = resp2.json()
        assert d2["approval"]["status"] == "cancelled"

    def test_approve_endpoint_does_not_execute_tools(self):
        """Test 29: approve does not set execution_allowed or tool_executed."""
        resp = self.client.post("/chat", json={
            "text": "Delete all private memory and remove the identity seed.",
        })
        aid = resp.json()["approval_id"]
        resp2 = self.client.post(f"/approvals/{aid}/approve")
        d2 = resp2.json()["approval"]
        assert d2["execution_allowed_after_decision"] is False
        assert d2["tool_executed"] is False

    def test_legacy_message_still_works(self):
        """Test 30: Legacy message still works with approval fields."""
        resp = self.client.post("/chat", json={"message": "legacy msg milestone 54a"})
        data = resp.json()
        assert data["status"] == "completed"
        assert "approval_id" in data
