"""Tests for Verification Verdict Record Store (Milestone 64A).

Verifies that verification verdict records are created, persisted, queried, and can be
cancelled.  No simulation execution, tool execution, apply, or rollback occurs.
"""

from __future__ import annotations

import json

import pytest


@pytest.fixture()
def vv_store_dir(monkeypatch, tmp_path):
    """Redirect _ensure_verification_verdict_dir to a temp directory."""
    store_dir = tmp_path / "verification_verdicts"
    store_dir.mkdir(parents=True, exist_ok=True)

    import aether.action.simulation_verdict_queue as vvq_mod
    monkeypatch.setattr(vvq_mod, "_ensure_verification_verdict_dir", lambda: store_dir)

    return store_dir


@pytest.fixture()
def _create(vv_store_dir):
    from aether.action.simulation_verdict_queue import create_verification_verdict_record
    return create_verification_verdict_record


@pytest.fixture()
def _get():
    from aether.action.simulation_verdict_queue import get_verification_verdict_record
    return get_verification_verdict_record


@pytest.fixture()
def _list():
    from aether.action.simulation_verdict_queue import list_verification_verdict_records
    return list_verification_verdict_records


@pytest.fixture()
def _update():
    from aether.action.simulation_verdict_queue import update_verification_verdict_record_status
    return update_verification_verdict_record_status


@pytest.fixture()
def clean_verdict():
    return {
        "decision": "pass",
        "reason": "All checks passed.",
        "simulation_result_id": "sim-001",
        "simulation_plan_id": "plan-1",
        "dry_run_id": "dr-1",
        "requested_action": {"tool_id": "test.tool", "action_type": "status_check"},
        "checks": [],
        "evidence_summary": [],
        "unresolved_risks": [],
        "blocking_reasons": [],
        "recommended_next_step": "Proceed.",
        "apply_allowed": False,
        "rollback_allowed": False,
        "execution_allowed": False,
        "tool_execution_allowed": False,
        "dry_run_execution_allowed": False,
        "simulation_execution_allowed": False,
        "verdict_apply_allowed": False,
        "metadata": {"source": "simulation_verdict_builder", "schema_version": "1.0"},
        "warnings": [],
    }


# ======================== TEST 1-5: CREATION & PERSISTENCE ======================== #

class TestCreateVerificationVerdictRecord:
    """Test 1: create_verification_verdict_record creates pending record."""

    def test_creates_pending_record(self, _create, clean_verdict):
        rec = _create(clean_verdict, context={"session_id": "s1"})
        assert rec is not None
        assert rec["status"] == "pending"

    def test_verification_verdict_id_exists_and_is_unique(self, _create, clean_verdict):
        r1 = _create(clean_verdict, context={"sid": "a"})
        r2 = _create(clean_verdict, context={"sid": "b"})
        assert r1["verification_verdict_id"] != r2["verification_verdict_id"]
        assert len(r1["verification_verdict_id"]) == 32

    def test_record_persisted_outside_repo(self, _create, clean_verdict, vv_store_dir):
        rec = _create(clean_verdict, context={"sid": "persist_test"})
        path = vv_store_dir / f"verification_verdict_{rec['verification_verdict_id']}.json"
        assert path.exists()
        data = json.loads(path.read_text())
        assert data["verification_verdict_id"] == rec["verification_verdict_id"]

    def test_get_returns_saved_record(self, _create, _get, clean_verdict):
        rec = _create(clean_verdict, context={"sid": "x"})
        loaded = _get(rec["verification_verdict_id"])
        assert loaded is not None
        assert loaded["verification_verdict_id"] == rec["verification_verdict_id"]
        assert loaded["status"] == "pending"

    def test_list_returns_records_newest_first(self, _create, _list, clean_verdict):
        ids = []
        for i in range(3):
            r = _create(clean_verdict, context={"i": i})
            ids.append(r["verification_verdict_id"])
        records = _list()
        assert len(records) == 3
        assert records[0]["verification_verdict_id"] == ids[2]
        assert records[-1]["verification_verdict_id"] == ids[0]


# ======================== TEST 6-8: LIST FILTERS ======================== #

class TestListFilters:
    """Test 6-8: list filters by status and decision."""

    def test_list_filters_by_status_pending(self, _create, _list, clean_verdict):
        _create(clean_verdict, context={"p": 1})
        pending_only = _list(status="pending")
        assert len(pending_only) >= 1

    def test_list_filters_by_decision_pass(self, _create, _list, clean_verdict):
        verdict = dict(clean_verdict)
        verdict["decision"] = "pass"
        _create(verdict, context={"d": "pass"})
        pass_records = _list(decision="pass")
        assert len(pass_records) >= 1
        for r in pass_records:
            assert r["verdict_decision"] == "pass"

    def test_list_filters_by_decision_warning(self, _create, _list):
        verdict = {
            "decision": "warning",
            "reason": "Some medium check failed.",
            "checks": [],
            "metadata": {},
            "warnings": [],
        }
        _create(verdict)
        warning_records = _list(decision="warning")
        assert len(warning_records) >= 1

    def test_list_filters_by_decision_fail(self, _create, _list):
        verdict = {
            "decision": "fail",
            "reason": "High check failed.",
            "checks": [],
            "metadata": {},
            "warnings": [],
        }
        _create(verdict)
        fail_records = _list(decision="fail")
        assert len(fail_records) >= 1

    def test_list_filters_by_decision_blocked(self, _create, _list):
        verdict = {
            "decision": "blocked",
            "reason": "Record not found.",
            "checks": [],
            "metadata": {},
            "warnings": [],
        }
        _create(verdict)
        blocked_records = _list(decision="blocked")
        assert len(blocked_records) >= 1


# ======================== TEST 9-11: STATUS TRANSITIONS ======================== #

class TestUpdateStatus:
    """Test 9-11: cancel + idempotent cancel + invalid decision."""

    def test_cancel_pending_changes_status(self, _create, _update, clean_verdict):
        rec = _create(clean_verdict)
        updated = _update(rec["verification_verdict_id"], decision="cancelled", reviewer="alice")
        assert updated["status"] == "cancelled"
        assert updated["decision"] == "cancelled"
        assert updated["reviewer"] == "alice"
        assert updated["decided_at"] is not None

    def test_already_cancelled_cannot_be_cancelled_again(self, _create, _update, clean_verdict):
        rec = _create(clean_verdict)
        _update(rec["verification_verdict_id"], decision="cancelled", reviewer="bob")
        second = _update(rec["verification_verdict_id"], decision="cancelled", reviewer="charlie")
        assert second["status"] == "cancelled"
        assert any("already 'cancelled'" in w for w in second.get("warnings", []))

    def test_invalid_decision_raises_value_error(self, _create, _update, clean_verdict):
        rec = _create(clean_verdict)
        with pytest.raises(ValueError, match="Invalid decision"):
            _update(rec["verification_verdict_id"], decision="invalid_op")


# ======================== TEST 12-21: SAFETY GUARDRAILS ======================== #

class TestSafetyGuardrails:
    """Tests 12-21: verdict_persisted true, all execution flags always false."""

    def test_verdict_persisted_true(self, _create, clean_verdict):
        rec = _create(clean_verdict)
        assert rec["verdict_persisted"] is True

    def test_simulation_executed_always_false(self, _create, _update, _get, clean_verdict):
        rec = _create(clean_verdict)
        _update(rec["verification_verdict_id"], decision="cancelled", reviewer="test")
        loaded = _get(rec["verification_verdict_id"])
        assert loaded["simulation_executed"] is False

    def test_apply_authorized_always_false(self, _create, _update, _get, clean_verdict):
        rec = _create(clean_verdict)
        _update(rec["verification_verdict_id"], decision="cancelled")
        loaded = _get(rec["verification_verdict_id"])
        assert loaded["apply_authorized"] is False

    def test_execution_allowed_always_false(self, _create, _update, _get, clean_verdict):
        rec = _create(clean_verdict)
        _update(rec["verification_verdict_id"], decision="cancelled")
        loaded = _get(rec["verification_verdict_id"])
        assert loaded["execution_allowed"] is False

    def test_tool_execution_allowed_always_false(self, _create, _update, _get, clean_verdict):
        rec = _create(clean_verdict)
        _update(rec["verification_verdict_id"], decision="cancelled")
        loaded = _get(rec["verification_verdict_id"])
        assert loaded["tool_execution_allowed"] is False

    def test_dry_run_execution_allowed_always_false(self, _create, _update, _get, clean_verdict):
        rec = _create(clean_verdict)
        _update(rec["verification_verdict_id"], decision="cancelled")
        loaded = _get(rec["verification_verdict_id"])
        assert loaded["dry_run_execution_allowed"] is False

    def test_simulation_execution_allowed_always_false(self, _create, _update, _get, clean_verdict):
        rec = _create(clean_verdict)
        _update(rec["verification_verdict_id"], decision="cancelled")
        loaded = _get(rec["verification_verdict_id"])
        assert loaded["simulation_execution_allowed"] is False

    def test_apply_allowed_always_false(self, _create, _update, _get, clean_verdict):
        rec = _create(clean_verdict)
        _update(rec["verification_verdict_id"], decision="cancelled")
        loaded = _get(rec["verification_verdict_id"])
        assert loaded["apply_allowed"] is False

    def test_rollback_allowed_always_false(self, _create, _update, _get, clean_verdict):
        rec = _create(clean_verdict)
        _update(rec["verification_verdict_id"], decision="cancelled")
        loaded = _get(rec["verification_verdict_id"])
        assert loaded["rollback_allowed"] is False

    def test_verdict_apply_allowed_always_false(self, _create, _update, _get, clean_verdict):
        rec = _create(clean_verdict)
        _update(rec["verification_verdict_id"], decision="cancelled")
        loaded = _get(rec["verification_verdict_id"])
        assert loaded["verdict_apply_allowed"] is False


# ======================== TEST 22-24: EDGE CASES ======================== #

class TestEdgeCases:
    """Test 22-24: missing id returns None, metadata preserved, warnings preserved."""

    def test_missing_vv_id_returns_none(self, _get):
        assert _get("nonexistent-vv-id-abc") is None

    def test_metadata_context_preserved(self, _create, clean_verdict):
        ctx = {"session_id": "test-sid-99", "extra_key": "value"}
        rec = _create(clean_verdict, context=ctx)
        assert rec["metadata"]["session_id"] == "test-sid-99"
        assert rec["metadata"]["extra_key"] == "value"

    def test_warnings_preserved_from_verdict(self, _create, _get, clean_verdict):
        verdict = dict(clean_verdict)
        verdict["warnings"] = ["verdict warning"]
        rec = _create(verdict)
        loaded = _get(rec["verification_verdict_id"])
        assert "verdict warning" in loaded["warnings"]


# ======================== TEST 25: PASS VERDICT STILL HAS APPLY_AUTHORIZED FALSE ======================== #

class TestPassVerdictSafety:
    """Test 25: pass verdict still has apply_authorized false."""

    def test_pass_verdict_still_has_apply_authorized_false(self, _create, _get, _update):
        verdict = {
            "decision": "pass",
            "reason": "All checks passed.",
            "checks": [],
            "metadata": {},
            "warnings": [],
        }
        rec = _create(verdict)
        _update(rec["verification_verdict_id"], decision="cancelled")
        loaded = _get(rec["verification_verdict_id"])
        assert loaded["apply_authorized"] is False
