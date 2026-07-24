"""Tests for Simulation Plan Record Store (Milestone 60A).

Verifies that simulation plan records are created, persisted, queried, and can be
cancelled.  No simulation execution, tool execution, apply, or rollback occurs.
"""

from __future__ import annotations

import json

import pytest


@pytest.fixture()
def sim_plan_store_dir(monkeypatch, tmp_path):
    """Redirect _ensure_simulation_plan_dir to a temp directory."""
    store_dir = tmp_path / "simulation_plans"
    store_dir.mkdir(parents=True, exist_ok=True)

    import aether.action.simulation_plan_queue as spq_mod
    monkeypatch.setattr(spq_mod, "_ensure_simulation_plan_dir", lambda: store_dir)

    return store_dir


@pytest.fixture()
def _create(sim_plan_store_dir):
    from aether.action.simulation_plan_queue import create_simulation_plan_record
    return create_simulation_plan_record


@pytest.fixture()
def _get():
    from aether.action.simulation_plan_queue import get_simulation_plan_record
    return get_simulation_plan_record


@pytest.fixture()
def _list():
    from aether.action.simulation_plan_queue import list_simulation_plan_records
    return list_simulation_plan_records


@pytest.fixture()
def _update():
    from aether.action.simulation_plan_queue import update_simulation_plan_record_status
    return update_simulation_plan_record_status


# ======================== TEST 1-6: CREATION & PERSISTENCE ======================== #


class TestCreateSimulationPlanRecord:
    """Test 1: create_simulation_plan_record creates pending record."""

    def test_creates_pending_record(self, _create):
        plan = {"simulation_plan_required": True, "simulation_plan_type": "contract_only_plan"}
        rec = _create(plan, context={"session_id": "s1"})
        assert rec is not None
        assert rec["status"] == "pending"

    def test_sim_plan_id_exists_and_is_unique(self, _create):
        plan = {"simulation_plan_required": True}
        r1 = _create(plan, context={"sid": "a"})
        r2 = _create(plan, context={"sid": "b"})
        assert r1["simulation_plan_id"] != r2["simulation_plan_id"]
        assert len(r1["simulation_plan_id"]) == 32

    def test_record_persisted_outside_repo(self, _create, sim_plan_store_dir):
        plan = {"simulation_plan_required": True}
        rec = _create(plan, context={"sid": "persist_test"})
        path = sim_plan_store_dir / f"simulation_plan_{rec['simulation_plan_id']}.json"
        assert path.exists()
        data = json.loads(path.read_text())
        assert data["simulation_plan_id"] == rec["simulation_plan_id"]

    def test_get_returns_saved_record(self, _create, _get):
        plan = {"simulation_plan_required": True}
        rec = _create(plan, context={"sid": "x"})
        loaded = _get(rec["simulation_plan_id"])
        assert loaded is not None
        assert loaded["simulation_plan_id"] == rec["simulation_plan_id"]
        assert loaded["status"] == "pending"

    def test_list_returns_records_newest_first(self, _create, _list):
        ids = []
        for i in range(3):
            r = _create({"simulation_plan_required": True}, context={"i": i})
            ids.append(r["simulation_plan_id"])
        records = _list()
        assert len(records) == 3
        assert records[0]["simulation_plan_id"] == ids[2]
        assert records[-1]["simulation_plan_id"] == ids[0]

    def test_list_filters_by_status_pending(self, _create, _list):
        _create({"simulation_plan_required": True}, context={"p": 1})
        pending_only = _list(status="pending")
        assert len(pending_only) >= 1


# ======================== TEST 7-9: STATUS TRANSITIONS ======================== #


class TestUpdateStatus:
    """Test 7-9: cancel + idempotent cancel + invalid decision."""

    def test_cancel_pending_changes_status(self, _create, _update):
        rec = _create({"simulation_plan_required": True})
        updated = _update(rec["simulation_plan_id"], decision="cancelled", reviewer="alice")
        assert updated["status"] == "cancelled"
        assert updated["decision"] == "cancelled"
        assert updated["reviewer"] == "alice"
        assert updated["decided_at"] is not None

    def test_already_cancelled_cannot_be_cancelled_again(self, _create, _update):
        rec = _create({"simulation_plan_required": True})
        _update(rec["simulation_plan_id"], decision="cancelled", reviewer="bob")
        second = _update(rec["simulation_plan_id"], decision="cancelled", reviewer="charlie")
        assert second["status"] == "cancelled"
        assert any("already 'cancelled'" in w for w in second.get("warnings", []))

    def test_invalid_decision_raises_value_error(self, _create, _update):
        rec = _create({"simulation_plan_required": True})
        with pytest.raises(ValueError, match="Invalid decision"):
            _update(rec["simulation_plan_id"], decision="invalid_op")


# ======================== TEST 10-15: SAFETY GUARDRAILS ======================== #


class TestSafetyGuardrails:
    """Tests 10-15: all execution/apply/rollback flags always false."""

    def test_simulation_executed_always_false(self, _create, _update, _get):
        rec = _create({"simulation_plan_required": True})
        _update(rec["simulation_plan_id"], decision="cancelled", reviewer="test")
        loaded = _get(rec["simulation_plan_id"])
        assert loaded["simulation_executed"] is False

    def test_execution_allowed_always_false(self, _create, _update, _get):
        rec = _create({"simulation_plan_required": True})
        _update(rec["simulation_plan_id"], decision="cancelled")
        loaded = _get(rec["simulation_plan_id"])
        assert loaded["execution_allowed"] is False

    def test_tool_execution_allowed_always_false(self, _create, _update, _get):
        rec = _create({"simulation_plan_required": True})
        _update(rec["simulation_plan_id"], decision="cancelled")
        loaded = _get(rec["simulation_plan_id"])
        assert loaded["tool_execution_allowed"] is False

    def test_dry_run_execution_allowed_always_false(self, _create, _update, _get):
        rec = _create({"simulation_plan_required": True})
        _update(rec["simulation_plan_id"], decision="cancelled")
        loaded = _get(rec["simulation_plan_id"])
        assert loaded["dry_run_execution_allowed"] is False

    def test_apply_allowed_always_false(self, _create, _update, _get):
        rec = _create({"simulation_plan_required": True})
        _update(rec["simulation_plan_id"], decision="cancelled")
        loaded = _get(rec["simulation_plan_id"])
        assert loaded["apply_allowed"] is False

    def test_rollback_allowed_always_false(self, _create, _update, _get):
        rec = _create({"simulation_plan_required": True})
        _update(rec["simulation_plan_id"], decision="cancelled")
        loaded = _get(rec["simulation_plan_id"])
        assert loaded["rollback_allowed"] is False


# ======================== TEST 16-18: EDGE CASES ======================== #


class TestEdgeCases:
    """Test 16-18: missing id returns None, metadata preserved, warnings preserved."""

    def test_missing_sim_plan_id_returns_none(self, _get):
        assert _get("nonexistent-sim-plan-id-abc") is None

    def test_metadata_context_preserved(self, _create):
        ctx = {"session_id": "test-sid-99", "extra_key": "value"}
        rec = _create({"simulation_plan_required": True}, context=ctx)
        assert rec["metadata"]["session_id"] == "test-sid-99"
        assert rec["metadata"]["extra_key"] == "value"

    def test_warnings_preserved_from_plan(self, _create, _get):
        plan = {
            "simulation_plan_required": True,
            "warnings": ["sim plan warning"],
        }
        rec = _create(plan)
        loaded = _get(rec["simulation_plan_id"])
        assert loaded["simulation_plan"]["warnings"] == ["sim plan warning"]
