"""End-to-end cognitive loop contract tests for POST /chat.

Locks down the current /chat response contract, observable side effects,
and safety invariants. Tests-only milestone — no source code modified.

If these tests fail after a future code change, the /chat contract has
changed intentionally or a regression was introduced.
"""

from importlib import reload
from fastapi.testclient import TestClient


def _get_test_client():
    """Create a TestClient with a fresh api_server import.

    Each call produces a new AetherRuntime instance, avoiding state
    leakage between test classes.
    """
    import aether.interface.api_server as ap_mod
    reload(ap_mod)
    return TestClient(ap_mod.app)


CHAT_RESPONSE_CONTRACT_FIELDS = [
    "name",
    "status",
    "response",
    "response_text",
    "time",
    "working_memory_event_count",
    "session_id",
    "loop_version",
    "identity_integrity_status",
    "perception",
    "risk",
    "suggested_tool",
    "tool_execution_allowed",
    "tool_executed",
    "memory_recorded",
    "timeline_recorded",
    "warnings",
    "thinking_policy",
    "decision_type",
    "required_user_confirmation",
    "clarification_question",
    "blocked_reason",
    "policy_gate",
    "execution_allowed",
    "execution_decision",
    "execution_reason",
    "approval_request",
    "approval_required",
    "approval_status",
    "approval_type",
    "approval_record",
    "approval_id",
]

SAFETY_INVARIANTS = [
    "tool_execution_allowed",
    "tool_executed",
    "execution_allowed",
]

PERCEPTION_SUBFIELDS = [
    "type",
    "normalized_text",
    "original_length",
    "language_hint",
    "contains_question",
    "contains_command_hint",
    "risk_terms_detected",
]

RISK_SUBFIELDS = [
    "risk_level",
    "action_type",
    "confidence",
    "reasons",
]

THINKING_POLICY_SUBFIELDS = [
    "decision_type",
    "confidence",
    "reasons",
    "required_user_confirmation",
    "tool_suggestion_allowed",
    "tool_execution_allowed",
    "blocked_reason",
    "clarification_question",
    "next_step",
    "warnings",
]

POLICY_GATE_SUBFIELDS = [
    "allowed",
    "decision",
    "reason",
    "required_user_confirmation",
    "tool_execution_allowed",
    "action_execution_allowed",
    "requested_action",
    "policy_snapshot",
    "warnings",
]

TIME_SUBFIELDS = [
    "timezone",
    "now",
    "iso",
]

AWAKEN_CONTRACT_FIELDS = [
    "name",
    "status",
    "identity_seed_loaded",
    "identity_seed_length",
    "time",
    "event_recorded",
    "event",
    "working_memory",
    "message",
    "identity_integrity_status",
]


class TestCognitiveLoopContract:
    client = None

    @classmethod
    def setup_class(cls):
        cls.client = _get_test_client()

    # ------------------------------------------------------------------ #
    # 1. Safe message full contract
    # ------------------------------------------------------------------ #

    def test_chat_safe_message_returns_full_contract(self):
        resp = self.client.post("/chat", json={"text": "hello world"})
        assert resp.status_code == 200
        data = resp.json()

        for key in CHAT_RESPONSE_CONTRACT_FIELDS:
            assert key in data, f"Missing field: {key}"

        assert data["name"] == "Aether"
        assert data["status"] == "completed"
        assert isinstance(data["response_text"], str)
        assert isinstance(data["response"], str)
        assert isinstance(data["time"], dict)
        for sub in TIME_SUBFIELDS:
            assert sub in data["time"], f"Missing time.{sub}"

        assert isinstance(data["identity_integrity_status"], (dict, type(None)))
        assert isinstance(data["perception"], (dict, type(None)))
        if isinstance(data["perception"], dict):
            for sub in PERCEPTION_SUBFIELDS:
                assert sub in data["perception"], f"Missing perception.{sub}"

        assert isinstance(data["risk"], dict)
        for sub in RISK_SUBFIELDS:
            assert sub in data["risk"], f"Missing risk.{sub}"

        assert isinstance(data["warnings"], list)
        assert isinstance(data["thinking_policy"], dict)
        assert isinstance(data["policy_gate"], dict)
        assert isinstance(data["execution_decision"], str)
        assert isinstance(data["execution_reason"], str)
        assert isinstance(data["working_memory_event_count"], int)

        assert data["approval_required"] is False
        assert data["approval_id"] is None
        assert data["approval_record"] is None
        assert data["tool_execution_allowed"] is False
        assert data["tool_executed"] is False
        assert data["execution_allowed"] is False
        assert data["memory_recorded"] is True
        assert data["timeline_recorded"] is True

    # ------------------------------------------------------------------ #
    # 2. Empty input error contract
    # ------------------------------------------------------------------ #

    def test_chat_empty_input_returns_error_contract(self):
        resp = self.client.post("/chat", json={})
        assert resp.status_code == 200
        data = resp.json()

        assert data["status"] == "error"

        for key in CHAT_RESPONSE_CONTRACT_FIELDS:
            assert key in data, f"Missing field in error response: {key}"

        assert isinstance(data["response"], str)
        assert len(data["response"]) > 0
        assert data["response_text"] is None
        assert isinstance(data["warnings"], list)
        assert len(data["warnings"]) > 0

        assert data["perception"] is None
        assert data["memory_recorded"] is False
        assert data["timeline_recorded"] is False
        assert data["tool_execution_allowed"] is False
        assert data["tool_executed"] is False
        assert data["execution_allowed"] is False
        assert data["approval_required"] is False
        assert data["approval_id"] is None

    # ------------------------------------------------------------------ #
    # 3. High-risk message exposes verification and approval
    # ------------------------------------------------------------------ #

    def test_chat_high_risk_message_exposes_verification_and_approval_contract(self):
        resp = self.client.post(
            "/chat",
            json={"text": "Delete all private memory and remove the identity seed."},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "completed"

        risk = data.get("risk", {})
        assert isinstance(risk, dict)
        assert risk.get("risk_level") == "high"
        for sub in RISK_SUBFIELDS:
            assert sub in risk, f"Missing risk.{sub}"

        assert data["approval_required"] is True
        assert data["approval_request"] is not None
        assert isinstance(data["approval_request"], dict)
        assert data["approval_record"] is not None
        assert isinstance(data["approval_record"], dict)
        assert data["approval_record"].get("status") == "pending"
        assert data["approval_id"] is not None

        approval_resp = self.client.get(f"/approvals/{data['approval_id']}")
        assert approval_resp.status_code == 200
        approval_data = approval_resp.json()
        assert approval_data.get("approval", {}).get("approval_id") == data["approval_id"]

    # ------------------------------------------------------------------ #
    # 4. Tool suggestion without execution
    # ------------------------------------------------------------------ #

    def test_chat_tool_like_request_suggests_tool_without_execution(self):
        resp = self.client.post("/chat", json={"text": "search files"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "completed"

        suggested = data.get("suggested_tool")
        assert suggested is not None, "Expected suggested_tool for 'search files'"
        assert isinstance(suggested, dict)
        assert "tool_id" in suggested
        assert data["tool_execution_allowed"] is False
        assert data["tool_executed"] is False
        assert data["execution_allowed"] is False

    # ------------------------------------------------------------------ #
    # 5. Working memory side effects
    # ------------------------------------------------------------------ #

    def test_chat_safe_message_records_working_memory_events(self):
        resp = self.client.post("/chat", json={"text": "hello memory contract"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["memory_recorded"] is True
        assert isinstance(data["working_memory_event_count"], int)
        assert data["working_memory_event_count"] > 0

        wm_resp = self.client.get("/memory/working")
        assert wm_resp.status_code == 200
        wm_data = wm_resp.json()
        assert "working_memory" in wm_data
        wm = wm_data["working_memory"]
        assert "event_count" in wm
        assert wm["event_count"] >= 2

        recent = wm.get("recent_events", [])
        assert isinstance(recent, list)
        if recent:
            types = [e.get("type") for e in recent if e.get("type")]
            assert "chat_input" in types
            assert "chat_response" in types

    # ------------------------------------------------------------------ #
    # 6. Timeline side effects
    # ------------------------------------------------------------------ #

    def test_chat_records_timeline_event(self):
        resp = self.client.post("/chat", json={"text": "hello timeline contract"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["timeline_recorded"] is True

        tl_resp = self.client.get("/memory/timeline/list")
        assert tl_resp.status_code == 200
        tl_data = tl_resp.json()
        assert "events" in tl_data
        events = tl_data["events"]
        assert isinstance(events, list)
        assert len(events) > 0

        chat_input_events = [
            e for e in events if e.get("type") == "chat_input"
        ]
        assert len(chat_input_events) >= 1

    # ------------------------------------------------------------------ #
    # 7. Session ID and metadata passthrough
    # ------------------------------------------------------------------ #

    def test_chat_accepts_session_id_and_metadata(self):
        resp = self.client.post(
            "/chat",
            json={
                "text": "hello session contract",
                "session_id": "test-session-81b",
                "metadata": {"source": "81b-contract-test"},
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "completed"
        assert data["session_id"] == "test-session-81b"

    # ------------------------------------------------------------------ #
    # 8. Safety invariants for safe and high-risk inputs
    # ------------------------------------------------------------------ #

    def test_chat_safety_invariants_for_safe_input(self):
        resp = self.client.post("/chat", json={"text": "hello safety contract"})
        assert resp.status_code == 200
        data = resp.json()

        for flag in SAFETY_INVARIANTS:
            assert data[flag] is False, f"{flag} should be False"

        for key in ("apply_id", "rollback_id", "execution_id"):
            assert key not in data, f"Unexpected key: {key}"

    def test_chat_safety_invariants_for_high_risk_input(self):
        resp = self.client.post(
            "/chat",
            json={"text": "Delete all private memory and remove the identity seed."},
        )
        assert resp.status_code == 200
        data = resp.json()

        for flag in SAFETY_INVARIANTS:
            assert data[flag] is False, f"{flag} should be False"

        for key in ("apply_id", "rollback_id", "execution_id"):
            assert key not in data, f"Unexpected key: {key}"

    # ------------------------------------------------------------------ #
    # 9. Awaken then chat preserves identity contract
    # ------------------------------------------------------------------ #

    def test_awaken_then_chat_preserves_identity_contract(self):
        client2 = _get_test_client()

        awaken_resp = client2.post("/awaken")
        assert awaken_resp.status_code == 200
        a_data = awaken_resp.json()

        for key in AWAKEN_CONTRACT_FIELDS:
            assert key in a_data, f"Missing awaken field: {key}"
        assert a_data["name"] == "Aether"

        chat_resp = client2.post("/chat", json={"text": "hello after awaken"})
        assert chat_resp.status_code == 200
        c_data = chat_resp.json()

        for key in CHAT_RESPONSE_CONTRACT_FIELDS:
            assert key in c_data, f"Missing chat field after awaken: {key}"
        assert c_data["name"] == "Aether"
        assert isinstance(c_data["identity_integrity_status"], (dict, type(None)))

        assert c_data["tool_execution_allowed"] is False
        assert c_data["tool_executed"] is False
        assert c_data["execution_allowed"] is False

    # ------------------------------------------------------------------ #
    # 10. No apply/rollback side effects
    # ------------------------------------------------------------------ #

    def test_chat_no_apply_or_rollback_side_effects(self):
        resp = self.client.post("/chat", json={"text": "hello no apply rollback"})
        assert resp.status_code == 200
        data = resp.json()

        assert data["tool_executed"] is False
        assert data["execution_allowed"] is False
        assert data["tool_execution_allowed"] is False

        for key in ("apply_id", "rollback_id", "execution_id", "mutation_id"):
            assert key not in data, f"Unexpected pipeline key: {key}"
