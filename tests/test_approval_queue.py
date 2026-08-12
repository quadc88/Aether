"""Tests for Approval Queue Record Store (Milestone 54A).

Verifies that individual approval records are created, persisted, queried, and their
status can be updated via approve/reject/cancel.  No tools are executed.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest


@pytest.fixture()
def approval_store_dir(monkeypatch, tmp_path):
    """Redirect _approval_record_dir to a temp directory."""
    store_dir = tmp_path / "approvals"
    store_dir.mkdir(parents=True, exist_ok=True)

    import aether.action.approval_queue as aq_mod
    monkeypatch.setattr(aq_mod, "_approval_record_dir", lambda: store_dir)

    return store_dir


@pytest.fixture()
def _create(approval_store_dir):
    from aether.action.approval_queue import create_approval_record
    return create_approval_record


@pytest.fixture()
def _get():
    from aether.action.approval_queue import get_approval_record
    return get_approval_record


@pytest.fixture()
def _list():
    from aether.action.approval_queue import list_approval_records
    return list_approval_records


@pytest.fixture()
def _update():
    from aether.action.approval_queue import update_approval_record_status
    return update_approval_record_status


# ======================== TEST 1-6: CREATION & PERSISTENCE ======================== #


class TestCreateApprovalRecord:
    """Test 1: create_approval_record creates a pending record."""

    def test_creates_pending_record(self, _create):
        req = {"approval_required": True, "risk_level": "high"}
        rec = _create(req, context={"session_id": "s1"})
        assert rec is not None
        assert rec["status"] == "pending"

    def test_approval_id_exists_and_is_unique(self, _create):
        r1 = _create({"approval_required": True}, context={"session_id": "a"})
        r2 = _create({"approval_required": True}, context={"session_id": "b"})
        assert r1["approval_id"] != r2["approval_id"]
        assert len(r1["approval_id"]) == 32

    def test_record_persisted_outside_repo(self, _create, approval_store_dir):
        rec = _create({"approval_required": True}, context={"session_id": "persist_test"})
        path = approval_store_dir / f"approval_{rec['approval_id']}.json"
        assert path.exists()
        data = json.loads(path.read_text())
        assert data["approval_id"] == rec["approval_id"]

    def test_get_returns_saved_record(self, _create, _get):
        rec = _create({"approval_required": True}, context={"sid": "x"})
        loaded = _get(rec["approval_id"])
        assert loaded is not None
        assert loaded["approval_id"] == rec["approval_id"]
        assert loaded["status"] == "pending"

    def test_list_returns_records_newest_first(self, _create, _list):
        ids = []
        for i in range(3):
            r = _create({"approval_required": True}, context={"i": i})
            ids.append(r["approval_id"])
        records = _list()
        assert len(records) == 3
        assert records[0]["approval_id"] == ids[2]
        assert records[-1]["approval_id"] == ids[0]

    def test_list_filters_by_status_pending(self, _create, _list):
        _create({"approval_required": True}, context={"p": 1})
        pending_only = _list(status="pending")
        assert len(pending_only) >= 1


# ======================== TEST 7-10: STATUS TRANSITIONS ======================== #


class TestUpdateStatus:
    """Test 7-10: approve / reject / cancel transitions."""

    def test_approve_pending_changes_status(self, _create, _update):
        rec = _create({"approval_required": True})
        updated = _update(rec["approval_id"], decision="approved", reviewer="alice")
        assert updated["status"] == "approved"
        assert updated["decision"] == "approved"
        assert updated["reviewer"] == "alice"
        assert updated["decided_at"] is not None

    def test_reject_pending_changes_status(self, _create, _update):
        rec = _create({"approval_required": True})
        updated = _update(rec["approval_id"], decision="rejected", reason="too risky")
        assert updated["status"] == "rejected"
        assert updated["decision"] == "rejected"
        assert updated["decision_reason"] == "too risky"

    def test_cancel_pending_changes_status(self, _create, _update):
        rec = _create({"approval_required": True})
        updated = _update(rec["approval_id"], decision="cancelled")
        assert updated["status"] == "cancelled"
        assert updated["decision"] == "cancelled"

    def test_approved_record_cannot_be_approved_again(self, _create, _update):
        rec = _create({"approval_required": True})
        _update(rec["approval_id"], decision="approved", reviewer="bob")
        second = _update(rec["approval_id"], decision="approved", reviewer="charlie")
        assert second["status"] == "approved"
        assert any("already 'approved'" in w for w in second.get("warnings", []))


# ======================== TEST 11-12: SAFETY GUARDRAILS ======================== #


class TestSafetyGuardrails:
    """Test 11-12: execution_allowed_after_decision always false, tool_executed always false."""

    def test_execution_allowed_after_decision_is_false(self, _create, _update, _get):
        rec = _create({"approval_required": True, "risk_level": "high"})
        _update(rec["approval_id"], decision="approved", reviewer="alice")
        loaded = _get(rec["approval_id"])
        assert loaded["execution_allowed_after_decision"] is False

    def test_tool_executed_always_false(self, _create, _update, _get):
        rec = _create({"approval_required": True})
        _update(rec["approval_id"], decision="approved")
        loaded = _get(rec["approval_id"])
        assert loaded["tool_executed"] is False


# ======================== TEST 13-15: EDGE CASES ======================== #


class TestEdgeCases:
    """Test 13-15: missing id returns None, invalid decision rejected, metadata preserved."""

    def test_missing_approval_id_returns_none(self, _get):
        assert _get("nonexistent-id-abc") is None

    def test_invalid_decision_raises_value_error(self, _create, _update):
        rec = _create({"approval_required": True})
        with pytest.raises(ValueError, match="Invalid decision"):
            _update(rec["approval_id"], decision="invalid_op")

    def test_metadata_context_preserved(self, _create):
        ctx = {"session_id": "test-sid-99", "extra_key": "value"}
        rec = _create({"approval_required": True}, context=ctx)
        assert rec["metadata"]["session_id"] == "test-sid-99"
        assert rec["metadata"]["extra_key"] == "value"

    def test_new_record_has_consumption_defaults(self, _create):
        rec = _create({"approval_required": True})
        assert rec["requested_action_fingerprint"] is None
        assert rec["execution_consumed"] is False
        assert rec["consumed_by_execution_attempt"] is None

    def test_exact_read_fingerprint_is_persisted(self, _create):
        action = {"tool_id": "file.restricted_read", "action_type": "restricted_file_read",
                  "name": "Restricted File Read", "target": "/tmp/x.py",
                  "permission_class": "read_only", "parameters": {"max_chars": 1}}
        rec = _create({"approval_required": True, "requested_action": action})
        assert len(rec["requested_action_fingerprint"]) == 64

    def test_legacy_record_is_normalized_by_get(self, _create, _get, approval_store_dir):
        rec = _create({"approval_required": True})
        path = approval_store_dir / f"approval_{rec['approval_id']}.json"
        data = json.loads(path.read_text())
        for key in ("requested_action_fingerprint", "execution_consumed", "consumed_by_execution_attempt"):
            data.pop(key)
        path.write_text(json.dumps(data))
        loaded = _get(rec["approval_id"])
        assert loaded["execution_consumed"] is False

    def test_claim_requires_approved_record(self, _create, _update):
        from aether.action.approval_queue import claim_approval_for_execution
        rec = _create({"approval_required": True})
        result = claim_approval_for_execution(rec["approval_id"], "attempt-1")
        assert result["claimed"] is False

    def test_claim_marks_approved_record_consumed(self, _create, _update, _get):
        from aether.action.approval_queue import claim_approval_for_execution
        rec = _create({"approval_required": True})
        _update(rec["approval_id"], "approved")
        result = claim_approval_for_execution(rec["approval_id"], "attempt-1")
        assert result["claimed"] is True
        assert _get(rec["approval_id"])["execution_consumed"] is True

    def test_second_claim_is_rejected(self, _create, _update):
        from aether.action.approval_queue import claim_approval_for_execution
        rec = _create({"approval_required": True})
        _update(rec["approval_id"], "approved")
        claim_approval_for_execution(rec["approval_id"], "attempt-1")
        assert claim_approval_for_execution(rec["approval_id"], "attempt-2")["claimed"] is False

    def test_claim_keeps_attempt_identity(self, _create, _update):
        from aether.action.approval_queue import claim_approval_for_execution
        rec = _create({"approval_required": True})
        _update(rec["approval_id"], "approved")
        claim_approval_for_execution(rec["approval_id"], "attempt-1")
        assert claim_approval_for_execution(rec["approval_id"], "attempt-2")["reason"]

    def test_claim_does_not_change_generic_execution_flags(self, _create, _update, _get):
        from aether.action.approval_queue import claim_approval_for_execution
        rec = _create({"approval_required": True})
        _update(rec["approval_id"], "approved")
        claim_approval_for_execution(rec["approval_id"], "attempt-1")
        saved = _get(rec["approval_id"])
        assert saved["execution_allowed_after_decision"] is False
        assert saved["tool_executed"] is False

        source = Path(__file__).parents[1].joinpath(
            "aether/action/approval_queue.py"
        ).read_text(encoding="utf-8")
        assert 'if os.name == "posix":' in source
        assert "fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)" in source
        assert 'elif os.name == "nt":' in source
        assert "msvcrt.locking(lock_file.fileno(), msvcrt.LK_LOCK, 1)" in source
        assert "raise OSError(f\"Unsupported platform for approval claim: {os.name}\")" in source
        assert "fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)" in source
        assert "msvcrt.locking(lock_file.fileno(), msvcrt.LK_UNLCK, 1)" in source
