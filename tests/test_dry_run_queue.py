"""Tests for Dry-Run Record Store (Milestone 57A).

Verifies that dry-run records are created, persisted, queried, and can be
cancelled.  No dry-run execution, tool execution, apply, or rollback occurs.
"""

from __future__ import annotations

import json

import pytest


@pytest.fixture()
def dry_run_store_dir(monkeypatch, tmp_path):
    """Redirect _ensure_dry_run_dir to a temp directory."""
    store_dir = tmp_path / "dry_runs"
    store_dir.mkdir(parents=True, exist_ok=True)

    import aether.action.dry_run_queue as drq_mod
    monkeypatch.setattr(drq_mod, "_ensure_dry_run_dir", lambda: store_dir)

    return store_dir


@pytest.fixture()
def _create(dry_run_store_dir):
    from aether.action.dry_run_queue import create_dry_run_record
    return create_dry_run_record


@pytest.fixture()
def _get():
    from aether.action.dry_run_queue import get_dry_run_record
    return get_dry_run_record


@pytest.fixture()
def _list():
    from aether.action.dry_run_queue import list_dry_run_records
    return list_dry_run_records


@pytest.fixture()
def _update():
    from aether.action.dry_run_queue import update_dry_run_record_status
    return update_dry_run_record_status


# ======================== TEST 1-6: CREATION & PERSISTENCE ======================== #


class TestCreateDryRunRecord:
    """Test 1: create_dry_run_record creates pending record."""

    def test_creates_pending_record(self, _create):
        req = {"dry_run_required": True, "dry_run_type": "action_simulation"}
        rec = _create(req, context={"session_id": "s1"})
        assert rec is not None
        assert rec["status"] == "pending"

    def test_dry_run_id_exists_and_is_unique(self, _create):
        req = {"dry_run_required": True}
        r1 = _create(req, context={"sid": "a"})
        r2 = _create(req, context={"sid": "b"})
        assert r1["dry_run_id"] != r2["dry_run_id"]
        assert len(r1["dry_run_id"]) == 32

    def test_record_persisted_outside_repo(self, _create, dry_run_store_dir):
        req = {"dry_run_required": True}
        rec = _create(req, context={"sid": "persist_test"})
        path = dry_run_store_dir / f"dry_run_{rec['dry_run_id']}.json"
        assert path.exists()
        data = json.loads(path.read_text())
        assert data["dry_run_id"] == rec["dry_run_id"]

    def test_get_returns_saved_record(self, _create, _get):
        req = {"dry_run_required": True}
        rec = _create(req, context={"sid": "x"})
        loaded = _get(rec["dry_run_id"])
        assert loaded is not None
        assert loaded["dry_run_id"] == rec["dry_run_id"]
        assert loaded["status"] == "pending"

    def test_list_returns_records_newest_first(self, _create, _list):
        ids = []
        for i in range(3):
            r = _create({"dry_run_required": True}, context={"i": i})
            ids.append(r["dry_run_id"])
        records = _list()
        assert len(records) == 3
        # newest first means the last-created should appear first
        assert records[0]["dry_run_id"] == ids[2]
        assert records[-1]["dry_run_id"] == ids[0]

    def test_list_filters_by_status_pending(self, _create, _list):
        _create({"dry_run_required": True}, context={"p": 1})
        pending_only = _list(status="pending")
        assert len(pending_only) >= 1


# ======================== TEST 7-10: STATUS TRANSITIONS ======================== #


class TestUpdateStatus:
    """Test 7-9: cancel + invalid decision, and already-cancelled warning."""

    def test_cancel_pending_changes_status(self, _create, _update):
        rec = _create({"dry_run_required": True})
        updated = _update(rec["dry_run_id"], decision="cancelled", reviewer="alice")
        assert updated["status"] == "cancelled"
        assert updated["decision"] == "cancelled"
        assert updated["reviewer"] == "alice"
        assert updated["decided_at"] is not None

    def test_already_cancelled_cannot_be_cancelled_again(self, _create, _update):
        rec = _create({"dry_run_required": True})
        _update(rec["dry_run_id"], decision="cancelled", reviewer="bob")
        second = _update(rec["dry_run_id"], decision="cancelled", reviewer="charlie")
        assert second["status"] == "cancelled"
        assert any("already 'cancelled'" in w for w in second.get("warnings", []))

    def test_invalid_decision_raises_value_error(self, _create, _update):
        rec = _create({"dry_run_required": True})
        with pytest.raises(ValueError, match="Invalid decision"):
            _update(rec["dry_run_id"], decision="invalid_op")


# ======================== TEST 10-14: SAFETY GUARDRAILS ======================== #


class TestSafetyGuardrails:
    """Tests 10-14: all execution flags always false."""

    def test_dry_run_executed_always_false(self, _create, _update, _get):
        rec = _create({"dry_run_required": True})
        _update(rec["dry_run_id"], decision="cancelled", reviewer="test")
        loaded = _get(rec["dry_run_id"])
        assert loaded["dry_run_executed"] is False

    def test_execution_allowed_always_false(self, _create, _update, _get):
        rec = _create({"dry_run_required": True})
        _update(rec["dry_run_id"], decision="cancelled")
        loaded = _get(rec["dry_run_id"])
        assert loaded["execution_allowed"] is False

    def test_tool_execution_allowed_always_false(self, _create, _update, _get):
        rec = _create({"dry_run_required": True})
        _update(rec["dry_run_id"], decision="cancelled")
        loaded = _get(rec["dry_run_id"])
        assert loaded["tool_execution_allowed"] is False

    def test_apply_allowed_always_false(self, _create, _update, _get):
        rec = _create({"dry_run_required": True})
        _update(rec["dry_run_id"], decision="cancelled")
        loaded = _get(rec["dry_run_id"])
        assert loaded["apply_allowed"] is False

    def test_rollback_allowed_always_false(self, _create, _update, _get):
        rec = _create({"dry_run_required": True})
        _update(rec["dry_run_id"], decision="cancelled")
        loaded = _get(rec["dry_run_id"])
        assert loaded["rollback_allowed"] is False


# ======================== TEST 15-16: EDGE CASES ======================== #


class TestEdgeCases:
    """Test 15-16: missing id returns None, metadata preserved."""

    def test_missing_dry_run_id_returns_none(self, _get):
        assert _get("nonexistent-dryrun-id-abc") is None

    def test_metadata_context_preserved(self, _create):
        ctx = {"session_id": "test-sid-99", "extra_key": "value"}
        rec = _create({"dry_run_required": True}, context=ctx)
        assert rec["metadata"]["session_id"] == "test-sid-99"
        assert rec["metadata"]["extra_key"] == "value"
