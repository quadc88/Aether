"""Hardening tests for the /chat loop_trace observability object (Milestone 81D).

Verifies that loop_trace stage summaries do NOT leak user input, metadata,
session_id, perception normalized_text, or approval record raw content.
No source code is tested or modified — tests only.
"""

from importlib import reload
from fastapi.testclient import TestClient


def _get_test_client():
    import aether.interface.api_server as ap_mod
    reload(ap_mod)
    return TestClient(ap_mod.app)


HIGHRISK_TEXT = "Delete all private memory and remove the identity seed."


class TestLoopTraceHardening:
    client = None

    @classmethod
    def setup_class(cls):
        cls.client = _get_test_client()

    def _summaries(self, payload: dict) -> list[str]:
        resp = self.client.post("/chat", json=payload)
        assert resp.status_code == 200
        trace = resp.json().get("loop_trace")
        assert trace is not None, "loop_trace must exist"
        assert isinstance(trace.get("stages"), list)
        return [s.get("summary", "") for s in trace["stages"]]

    def test_loop_trace_does_not_include_user_text(self):
        summaries = self._summaries({"text": "hello there user text should not appear in summaries 987654"})
        combined = " ".join(summaries)
        assert "hello there user text" not in combined
        assert "987654" not in combined

    def test_loop_trace_does_not_include_normalized_text(self):
        resp = self.client.post("/chat", json={"text": "check normalized text exclusion"})
        assert resp.status_code == 200
        data = resp.json()
        normalized = data.get("perception", {}).get("normalized_text", "")
        trace = data.get("loop_trace", {})
        trace_str = str(trace)
        assert normalized not in trace_str, f"normalized_text leaked into trace: {normalized}"

    def test_loop_trace_does_not_include_metadata_values(self):
        summaries = self._summaries({
            "text": "hello with metadata",
            "metadata": {"source": "81d-hardening", "client": "test-tool"},
        })
        combined = " ".join(summaries)
        assert "81d-hardening" not in combined
        assert "test-tool" not in combined

    def test_loop_trace_does_not_include_session_id(self):
        summaries = self._summaries({
            "text": "hello with session",
            "session_id": "81d-session-9876",
        })
        combined = " ".join(summaries)
        assert "81d-session-9876" not in combined

    def test_loop_trace_summaries_are_tightly_truncated(self):
        summaries = self._summaries({"text": "hello trace"})
        for s in summaries:
            assert len(s) <= 120, f"Summary exceeds 120 chars: {s[:50]}... ({len(s)} chars)"

    def test_loop_trace_stage_count_matches_expected_minimum(self):
        resp = self.client.post("/chat", json={"text": "hello trace"})
        assert resp.status_code == 200
        trace = resp.json().get("loop_trace")
        assert trace is not None
        assert len(trace["stages"]) >= 12

    def test_loop_trace_high_risk_summary_does_not_dump_approval_record(self):
        resp = self.client.post("/chat", json={"text": HIGHRISK_TEXT})
        assert resp.status_code == 200
        data = resp.json()
        trace = data.get("loop_trace")
        assert trace is not None
        trace_str = str(trace)
        raw_record = data.get("approval_record") or {}
        if raw_record:
            record_str = str(raw_record)
            assert record_str not in trace_str, "Raw approval record leaked into loop_trace"
