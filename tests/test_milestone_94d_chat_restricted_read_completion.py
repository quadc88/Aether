"""Focused contract tests for the capability-specific 94D chat resume."""

from __future__ import annotations

import ast
import threading
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from aether.action.approval_queue import (
    create_approval_record,
    get_approval_record,
    update_approval_record_status,
)
from aether.action.services import restricted_file_read_execution_service as service
from aether.action.tool_planner import parse_restricted_read_command
from aether.interface.api_models import (
    RestrictedReadChatResumeRequest,
    RestrictedReadChatResumeResponse,
)
from aether.interface.api_server import app


ROOT = Path(__file__).resolve().parents[1]
READ_TEXT = 'read file "README.md" [max_chars=12000]'


def _client() -> TestClient:
    return TestClient(app)


def _action(text: str = READ_TEXT) -> dict:
    action = parse_restricted_read_command(text)
    assert action is not None
    return action


def _record(*, status: str = "pending", session_id: str | None = None, text: str = READ_TEXT) -> dict:
    record = create_approval_record(
        {"approval_required": True, "requested_action": _action(text)},
        context={"session_id": session_id},
    )
    if status != "pending":
        update_approval_record_status(record["approval_id"], status)
    return get_approval_record(record["approval_id"])


def _resume(approval_id: str, *, text: str = READ_TEXT, session_id: str | None = None):
    return service.handle_restricted_read_chat_resume(
        RestrictedReadChatResumeRequest(
            approval_id=approval_id, request_text=text, session_id=session_id,
        )
    )


@pytest.fixture
def governed_roots(monkeypatch):
    import aether.action.restricted_file_reader as reader
    import aether.core.governance as governance

    roots = (ROOT.resolve(),)
    monkeypatch.setattr(reader, "get_restricted_file_read_approved_roots", lambda: roots)
    monkeypatch.setattr(governance, "get_restricted_file_read_approved_roots", lambda: roots)
    return roots


def _producer_result(status: str, *, verification: str, content: str | None = None, truncated: bool = False):
    return {
        "status": "completed" if verification in {"VERIFIED_SUCCESS", "VERIFIED_PARTIAL"} else "denied",
        "approval_id": "producer",
        "execution_attempt_status": "COMPLETED" if verification in {"VERIFIED_SUCCESS", "VERIFIED_PARTIAL"} else "FAILED",
        "verification_status": verification,
        "action_dispatched": True,
        "content": content,
        "truncated": truncated,
        "reason": status,
        "warnings": [],
    }


def test_phase_one_chat_does_not_dispatch(monkeypatch):
    import aether.action.services.restricted_file_read_bridge as bridge
    monkeypatch.setattr(bridge, "dispatch_restricted_read", lambda *a, **k: pytest.fail("Phase 1 dispatched"))
    data = _client().post("/chat", json={"text": READ_TEXT}).json()
    assert data["tool_executed"] is False
    assert data["tool_execution_allowed"] is False


def test_approval_creation_does_not_dispatch():
    record = _record()
    assert record["status"] == "pending"
    assert record["execution_consumed"] is False


def test_approval_transition_does_not_dispatch():
    record = _record(status="approved")
    assert record["status"] == "approved"
    assert record["execution_consumed"] is False
    assert record["tool_executed"] is False


def test_explicit_resume_is_required():
    response = _client().post("/chat", json={"text": READ_TEXT}).json()
    assert response["tool_executed"] is False
    assert response["approval_id"] is not None


def test_approved_resume_returns_verified_result(governed_roots, monkeypatch):
    import aether.identity.guard as guard
    monkeypatch.setattr(guard, "verify_identity_integrity", lambda: {"status": "verified", "changed": False})
    record = _record(status="approved")
    result = _resume(record["approval_id"])
    assert result["verification_status"] == "VERIFIED_SUCCESS"
    assert result["status"] == "completed"
    assert result["content"]
    assert result["approval_state"] == "consumed"


def test_pending_resume_is_not_attempted():
    result = _resume(_record()["approval_id"])
    assert result["status"] == "pending"
    assert result["approval_state"] == "pending"
    assert result["execution_attempt_status"] == "NOT_ATTEMPTED"
    assert result["verification_status"] is None


def test_rejected_and_cancelled_resume_are_not_verified():
    for status in ("rejected", "cancelled"):
        result = _resume(_record(status=status)["approval_id"])
        assert result["approval_state"] == status
        assert result["verification_status"] is None
        assert result["action_dispatched"] is False


def test_missing_approval_is_not_verified():
    result = _resume("missing-approval")
    assert result["approval_state"] == "missing"
    assert result["verification_status"] is None
    assert result["execution_attempt_status"] == "REJECTED"


def test_consumed_replay_is_denied(governed_roots, monkeypatch):
    import aether.identity.guard as guard
    monkeypatch.setattr(guard, "verify_identity_integrity", lambda: {"status": "verified", "changed": False})
    record = _record(status="approved")
    first = _resume(record["approval_id"])
    second = _resume(record["approval_id"])
    assert first["approval_state"] == "consumed"
    assert second["approval_state"] == "consumed"
    assert second["verification_status"] is None
    assert second["action_dispatched"] is False


def test_malformed_grammar_is_not_verified():
    record = _record(status="approved")
    result = _resume(record["approval_id"], text='read file "README.md" extra')
    assert result["verification_status"] is None
    assert result["action_dispatched"] is False


def test_target_replacement_fails_binding():
    record = _record(status="approved")
    result = _resume(record["approval_id"], text='read file "docs/README.md" [max_chars=12000]')
    assert result["verification_status"] is None
    assert "binding" in result["reason"].lower()


def test_max_chars_replacement_fails_binding():
    record = _record(status="approved")
    result = _resume(record["approval_id"], text='read file "README.md" [max_chars=81]')
    assert result["verification_status"] is None
    assert result["action_dispatched"] is False


def test_session_binding_mismatch_fails_closed():
    record = _record(status="approved", session_id="session-a")
    result = _resume(record["approval_id"], session_id="session-b")
    assert result["verification_status"] is None
    assert result["action_dispatched"] is False


def test_fresh_governance_is_called_at_execution_time(governed_roots, monkeypatch):
    import aether.core.coordination as coordination
    import aether.identity.guard as guard
    calls = []
    monkeypatch.setattr(guard, "verify_identity_integrity", lambda: {"status": "verified", "changed": False})
    import aether.core.governance as governance
    original = governance.authorize_restricted_read_execution
    def wrapped(*args, **kwargs):
        calls.append(kwargs)
        return original(*args, **kwargs)
    monkeypatch.setattr(governance, "authorize_restricted_read_execution", wrapped)
    record = _record(status="approved")
    _resume(record["approval_id"])
    assert len(calls) == 1
    assert calls[0]["approval_evidence"]["approval_valid"] is True


def test_current_risk_denial_prevents_dispatch(governed_roots, monkeypatch):
    import aether.core.coordination as coordination
    import aether.identity.guard as guard
    monkeypatch.setattr(guard, "verify_identity_integrity", lambda: {"status": "verified", "changed": False})
    monkeypatch.setattr(coordination, "classify_risk", lambda text: {"risk_level": "high", "action_type": "blocked"})
    result = _resume(_record(status="approved")["approval_id"])
    assert result["verification_status"] is None
    assert result["action_dispatched"] is False


def test_only_restricted_read_capability_is_constructed():
    source = Path(service.__file__).read_text(encoding="utf-8")
    assert 'capability_id="file.restricted_read"' in source
    assert "tool_id" not in source


def test_existing_strategy_c_bridge_is_reached(governed_roots, monkeypatch):
    import aether.core.coordination as coordination
    import aether.action.services.restricted_file_read_bridge as bridge
    import aether.identity.guard as guard
    calls = []
    monkeypatch.setattr(guard, "verify_identity_integrity", lambda: {"status": "verified", "changed": False})
    original = coordination.dispatch_restricted_read
    def wrapped(*args, **kwargs):
        calls.append((args, kwargs))
        return original(*args, **kwargs)
    monkeypatch.setattr(coordination, "dispatch_restricted_read", wrapped)
    _resume(_record(status="approved")["approval_id"])
    assert len(calls) == 1


def test_generic_execute_tool_path_is_not_called():
    assert "execute_tool" not in Path(service.__file__).read_text(encoding="utf-8")


def test_generic_tool_service_is_not_called():
    assert "tool_service" not in Path(service.__file__).read_text(encoding="utf-8")


def test_concurrent_resume_has_one_claim_and_dispatch(governed_roots, monkeypatch):
    import aether.core.coordination as coordination
    import aether.identity.guard as guard
    monkeypatch.setattr(guard, "verify_identity_integrity", lambda: {"status": "verified", "changed": False})
    claims = []
    original = coordination.claim_approval_for_execution
    def wrapped(*args, **kwargs):
        result = original(*args, **kwargs)
        claims.append(result["claimed"])
        return result
    monkeypatch.setattr(coordination, "claim_approval_for_execution", wrapped)
    approval_id = _record(status="approved")["approval_id"]
    results = []
    threads = [threading.Thread(target=lambda: results.append(_resume(approval_id))) for _ in range(2)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    assert sum(claims) == 1
    assert sum(result["action_dispatched"] for result in results) == 1


def test_out_of_root_access_is_denied(governed_roots, monkeypatch):
    record = _record(status="approved", text='read file "README.md"')
    result = _resume(record["approval_id"], text='read file "/tmp/not-approved.txt"')
    assert result["verification_status"] is None
    assert result["content"] is None


def test_missing_root_configuration_is_denied(monkeypatch):
    import aether.core.governance as governance
    monkeypatch.setattr(governance, "get_restricted_file_read_approved_roots", lambda: ())
    result = _resume(_record(status="approved")["approval_id"])
    assert result["verification_status"] is None
    assert result["content"] is None


def test_privacy_denial_returns_no_content(monkeypatch):
    monkeypatch.setattr(service, "handle_restricted_file_read_execution", lambda request: _producer_result("privacy", verification="DENIED", content="secret"))
    result = _resume(_record(status="approved")["approval_id"])
    assert result["verification_status"] == "DENIED"
    assert result["content"] is None


def test_internal_error_returns_no_content(monkeypatch):
    monkeypatch.setattr(service, "handle_restricted_file_read_execution", lambda request: _producer_result("internal", verification="INTERNAL_ERROR", content="unsafe"))
    result = _resume(_record(status="approved")["approval_id"])
    assert result["status"] == "error"
    assert result["verification_status"] == "INTERNAL_ERROR"
    assert result["content"] is None


def test_not_found_is_truthful(monkeypatch):
    monkeypatch.setattr(service, "handle_restricted_file_read_execution", lambda request: _producer_result("missing", verification="NOT_FOUND", content="wrong"))
    result = _resume(_record(status="approved")["approval_id"])
    assert result["verification_status"] == "NOT_FOUND"
    assert result["content"] is None


def test_changed_during_read_is_truthful(monkeypatch):
    monkeypatch.setattr(service, "handle_restricted_file_read_execution", lambda request: _producer_result("changed", verification="CHANGED_DURING_READ", content="wrong"))
    result = _resume(_record(status="approved")["approval_id"])
    assert result["verification_status"] == "CHANGED_DURING_READ"
    assert result["content"] is None


def test_partial_result_preserves_truncation(monkeypatch):
    monkeypatch.setattr(service, "handle_restricted_file_read_execution", lambda request: _producer_result("partial", verification="VERIFIED_PARTIAL", content="bounded", truncated=True))
    result = _resume(_record(status="approved")["approval_id"])
    assert result["status"] == "completed"
    assert result["content"] == "bounded"
    assert result["truncated"] is True


def test_success_result_preserves_bounded_content(monkeypatch):
    monkeypatch.setattr(service, "handle_restricted_file_read_execution", lambda request: _producer_result("success", verification="VERIFIED_SUCCESS", content="bounded"))
    result = _resume(_record(status="approved")["approval_id"])
    assert result["verification_status"] == "VERIFIED_SUCCESS"
    assert result["content"] == "bounded"
    assert result["truncated"] is False


def test_successful_producer_creates_call_local_observation(governed_roots, monkeypatch):
    import aether.core.coordination as coordination
    import aether.action.services.restricted_file_read_bridge as bridge
    import aether.identity.guard as guard
    seen = []
    monkeypatch.setattr(guard, "verify_identity_integrity", lambda: {"status": "verified", "changed": False})
    original = coordination.dispatch_restricted_read
    def wrapped(*args, **kwargs):
        result = original(*args, **kwargs)
        seen.append(result.get("observation"))
        return result
    monkeypatch.setattr(coordination, "dispatch_restricted_read", wrapped)
    _resume(_record(status="approved")["approval_id"])
    assert len(seen) == 1
    assert seen[0].__class__.__name__ == "RestrictedReadObservation"


def test_no_persistent_observation_record_is_created(governed_roots, monkeypatch, isolated_test_paths):
    import aether.identity.guard as guard
    monkeypatch.setattr(guard, "verify_identity_integrity", lambda: {"status": "verified", "changed": False})
    _resume(_record(status="approved")["approval_id"])
    assert not (isolated_test_paths["private_dir"] / "observation_records").exists()


def test_observation_intake_is_not_called():
    source = Path(service.__file__).read_text(encoding="utf-8")
    assert "handle_observation_intake" not in source


def test_capability_statuses_are_not_translated_to_observation_statuses():
    source = Path(service.__file__).read_text(encoding="utf-8")
    assert "matched" not in source
    assert "mismatched" not in source


def test_generic_chat_execution_authority_remains_absent():
    source = Path(ROOT / "aether/core/loop.py").read_text(encoding="utf-8")
    assert "dispatch_restricted_read" not in source
    assert "execute_tool" not in source


def test_ordinary_chat_behavior_remains_unchanged():
    data = _client().post("/chat", json={"text": "hello ordinary chat"}).json()
    assert data["status"] == "completed"
    assert data["approval_id"] is None
    assert data["tool_executed"] is False


def test_other_tool_like_requests_remain_non_executing():
    data = _client().post("/chat", json={"text": "run command safely"}).json()
    assert data["tool_executed"] is False
    assert data["tool_execution_allowed"] is False


def test_resume_models_and_openapi_boundary_are_exact():
    from aether.interface.api_server import app
    spec = app.openapi()
    assert len(spec["paths"]) == 306
    assert len(spec["components"]["schemas"]) == 112
    operation = spec["paths"]["/chat/restricted-read/resume"]["post"]
    assert operation["operationId"] == "resume_restricted_read_chat"
    assert "execute_approved_read" in {
        method["operationId"]
        for path in spec["paths"].values()
        for method in path.values()
        if isinstance(method, dict) and "operationId" in method
    }
    assert set(RestrictedReadChatResumeRequest.model_fields) == {"approval_id", "request_text", "session_id"}
    assert "approval_state" in RestrictedReadChatResumeResponse.model_fields
