"""Tests for the /chat loop_trace observability object (Milestone 81C).

Verifies that loop_trace is a safe structured summary of the cognitive
loop execution, does NOT expose hidden reasoning, and does not change
existing /chat behavior.
"""

from importlib import reload
from fastapi.testclient import TestClient


def _get_test_client():
    import aether.interface.api_server as ap_mod
    reload(ap_mod)
    return TestClient(ap_mod.app)


EXPECTED_SAFE_STAGES = [
    "perception",
    "identity_integrity",
    "time_state",
    "working_memory",
    "risk_classification",
    "tool_suggestion",
    "thinking_policy",
    "policy_gate",
    "approval_request",
    "approval_queue",
    "timeline_recording",
    "response_generation",
]

SAFE_STAGE_NAMES_TO_CHECK = [
    "perception",
    "identity_integrity",
    "time_state",
    "working_memory",
    "risk_classification",
    "tool_suggestion",
    "thinking_policy",
    "policy_gate",
    "approval_request",
    "approval_queue",
    "timeline_recording",
    "response_generation",
]

FORBIDDEN_SUBSTRINGS = [
    "chain-of-thought",
    "hidden reasoning",
    "system prompt",
    "developer message",
    "raw prompt",
    "api_key",
    "password",
    "token",
    "secret",
    "private_key",
    "credential",
]


class TestLoopTraceContract:
    client = None

    @classmethod
    def setup_class(cls):
        cls.client = _get_test_client()

    # ------------------------------------------------------------------ #
    # 1. Basic trace structure
    # ------------------------------------------------------------------ #

    def test_chat_returns_loop_trace(self):
        resp = self.client.post("/chat", json={"text": "hello trace"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "completed"

        trace = data.get("loop_trace")
        assert trace is not None
        assert isinstance(trace, dict)

        assert isinstance(trace.get("trace_id"), str)
        assert trace["trace_id"].startswith("chat_")

        assert isinstance(trace.get("loop_version"), str)
        assert trace["loop_version"] == "0.1.0"

        assert isinstance(trace.get("status"), str)
        assert trace["status"] == "completed"

        assert isinstance(trace.get("started_at"), str)
        assert isinstance(trace.get("completed_at"), str)

        assert isinstance(trace.get("duration_ms"), int)
        assert trace["duration_ms"] >= 0

        assert isinstance(trace.get("stages"), list)
        assert len(trace["stages"]) >= 1

    # ------------------------------------------------------------------ #
    # 2. Expected stage names
    # ------------------------------------------------------------------ #

    def test_loop_trace_has_expected_stage_names(self):
        resp = self.client.post("/chat", json={"text": "hello stages"})
        assert resp.status_code == 200
        trace = resp.json().get("loop_trace")
        assert trace is not None

        stage_names = [s["name"] for s in trace["stages"]]

        for expected in SAFE_STAGE_NAMES_TO_CHECK:
            assert expected in stage_names, f"Missing stage: {expected}"

    # ------------------------------------------------------------------ #
    # 3. Stage summaries are safe strings
    # ------------------------------------------------------------------ #

    def test_loop_trace_stage_summaries_are_safe_strings(self):
        resp = self.client.post("/chat", json={"text": "hello summaries"})
        assert resp.status_code == 200
        trace = resp.json().get("loop_trace")
        assert trace is not None

        for stage in trace["stages"]:
            assert isinstance(stage["name"], str)
            assert isinstance(stage["status"], str)
            assert isinstance(stage["summary"], str)
            assert isinstance(stage["warnings_count"], int)
            assert "\n" not in stage["summary"], f"Newline in stage {stage['name']}: {stage['summary']}"
            assert len(stage["summary"]) <= 200

    # ------------------------------------------------------------------ #
    # 4. Safe message - all stages complete
    # ------------------------------------------------------------------ #

    def test_loop_trace_safe_message_stages_complete(self):
        resp = self.client.post("/chat", json={"text": "hello safe"})
        assert resp.status_code == 200
        trace = resp.json().get("loop_trace")
        assert trace is not None
        assert trace["status"] == "completed"

        for stage in trace["stages"]:
            if stage["status"] == "skipped":
                continue
            assert stage["status"] in ("completed", "warning", "error")

    # ------------------------------------------------------------------ #
    # 5. High-risk message records approval status
    # ------------------------------------------------------------------ #

    def test_loop_trace_high_risk_message_records_approval_status(self):
        resp = self.client.post(
            "/chat",
            json={"text": "Delete all private memory and remove the identity seed."},
        )
        assert resp.status_code == 200
        data = resp.json()
        trace = data.get("loop_trace")
        assert trace is not None

        safety = trace.get("safety", {})
        assert isinstance(safety, dict)
        assert safety.get("approval_required") is True

        assert safety["approval_required"] == data.get("approval_required", False)

        records = trace.get("records", {})
        assert records.get("approval_id") == data.get("approval_id")

    # ------------------------------------------------------------------ #
    # 6. Safety flags match response
    # ------------------------------------------------------------------ #

    def test_loop_trace_records_safety_flags(self):
        resp = self.client.post("/chat", json={"text": "hello safety flags"})
        assert resp.status_code == 200
        data = resp.json()
        trace = data.get("loop_trace")
        assert trace is not None

        safety = trace.get("safety", {})
        assert safety.get("tool_execution_allowed") == data.get("tool_execution_allowed")
        assert safety.get("tool_executed") == data.get("tool_executed")
        assert safety.get("execution_allowed") == data.get("execution_allowed")
        assert safety.get("approval_required") == data.get("approval_required")

    # ------------------------------------------------------------------ #
    # 7. Records keys exist
    # ------------------------------------------------------------------ #

    def test_loop_trace_records_contain_expected_keys(self):
        resp = self.client.post("/chat", json={"text": "hello records"})
        assert resp.status_code == 200
        trace = resp.json().get("loop_trace")
        assert trace is not None

        records = trace.get("records", {})
        assert isinstance(records, dict)
        assert "working_memory_event_ids" in records
        assert isinstance(records["working_memory_event_ids"], list)
        assert "timeline_event_id" in records
        assert "approval_id" in records

    # ------------------------------------------------------------------ #
    # 8. No hidden reasoning exposed
    # ------------------------------------------------------------------ #

    def test_loop_trace_does_not_expose_hidden_reasoning(self):
        resp = self.client.post("/chat", json={"text": "hello privacy"})
        assert resp.status_code == 200
        trace = resp.json().get("loop_trace")
        assert trace is not None

        trace_str = str(trace).lower()
        for forbidden in FORBIDDEN_SUBSTRINGS:
            assert forbidden not in trace_str, f"Found forbidden substring: {forbidden}"

    # ------------------------------------------------------------------ #
    # 9. Error contract for empty input
    # ------------------------------------------------------------------ #

    def test_loop_trace_error_contract_for_empty_input(self):
        resp = self.client.post("/chat", json={})
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "error"

        trace = data.get("loop_trace")
        assert trace is not None
        assert isinstance(trace, dict)
        assert trace["status"] == "error"
        stage_names = [s["name"] for s in trace.get("stages", [])]
        assert "response_generation" in stage_names
        safety = trace.get("safety", {})
        assert safety.get("approval_required") is False
        assert safety.get("tool_execution_allowed") is False
        assert safety.get("execution_allowed") is False

    # ------------------------------------------------------------------ #
    # 10. Awaken and memory endpoints unaffected
    # ------------------------------------------------------------------ #

    def test_loop_trace_does_not_affect_awaken_or_memory_endpoints(self):
        awaken_resp = self.client.post("/awaken")
        assert awaken_resp.status_code == 200
        a_data = awaken_resp.json()
        assert a_data.get("name") == "Aether"
        assert "loop_trace" not in a_data

        wm_resp = self.client.get("/memory/working")
        assert wm_resp.status_code == 200
        assert "working_memory" in wm_resp.json()
