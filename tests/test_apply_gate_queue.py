"""Tests for Apply Gate Record Store (Milestone 66A).

Verifies that apply gate records are created, persisted, queried, and can be
cancelled.  No apply execution, tool execution, apply, or rollback occurs.
"""

from __future__ import annotations

import json

import pytest


@pytest.fixture()
def ag_store_dir(monkeypatch, tmp_path):
    """Redirect _ensure_apply_gate_dir to a temp directory."""
    store_dir = tmp_path / "apply_gates"
    store_dir.mkdir(parents=True, exist_ok=True)

    import aether.action.apply_gate_queue as agq_mod
    monkeypatch.setattr(agq_mod, "_ensure_apply_gate_dir", lambda: store_dir)

    return store_dir


@pytest.fixture()
def _create(ag_store_dir):
    from aether.action.apply_gate_queue import create_apply_gate_record
    return create_apply_gate_record


@pytest.fixture()
def _get():
    from aether.action.apply_gate_queue import get_apply_gate_record
    return get_apply_gate_record


@pytest.fixture()
def _list():
    from aether.action.apply_gate_queue import list_apply_gate_records
    return list_apply_gate_records


@pytest.fixture()
def _update():
    from aether.action.apply_gate_queue import update_apply_gate_record_status
    return update_apply_gate_record_status


@pytest.fixture()
def clean_agr():
    return {
        "decision": "eligible_for_human_review",
        "reason": "All eligibility checks passed.",
        "verification_verdict_id": "vv-001",
        "simulation_result_id": "sim-001",
        "simulation_plan_id": "plan-1",
        "dry_run_id": "dr-1",
        "requested_action": {"tool_id": "test.tool", "action_type": "status_check"},
        "eligibility_checks": [],
        "required_human_confirmations": [],
        "blocking_reasons": [],
        "unresolved_risks": [],
        "recommended_next_step": "Proceed.",
        "apply_authorized": False,
        "apply_allowed": False,
        "rollback_allowed": False,
        "execution_allowed": False,
        "tool_execution_allowed": False,
        "dry_run_execution_allowed": False,
        "simulation_execution_allowed": False,
        "metadata": {"source": "apply_gate_request_builder", "schema_version": "1.0"},
        "warnings": [],
    }


# ======================== TEST 1-5: CREATION & PERSISTENCE ======================== #

class TestCreateApplyGateRecord:
    def test_creates_pending_record(self, _create, clean_agr):
        rec = _create(clean_agr, context={"session_id": "s1"})
        assert rec is not None
        assert rec["status"] == "pending"

    def test_apply_gate_id_exists_and_is_unique(self, _create, clean_agr):
        r1 = _create(clean_agr, context={"sid": "a"})
        r2 = _create(clean_agr, context={"sid": "b"})
        assert r1["apply_gate_id"] != r2["apply_gate_id"]
        assert len(r1["apply_gate_id"]) == 32

    def test_record_persisted_outside_repo(self, _create, clean_agr, ag_store_dir):
        rec = _create(clean_agr, context={"sid": "persist_test"})
        path = ag_store_dir / f"apply_gate_{rec['apply_gate_id']}.json"
        assert path.exists()
        data = json.loads(path.read_text())
        assert data["apply_gate_id"] == rec["apply_gate_id"]

    def test_get_returns_saved_record(self, _create, _get, clean_agr):
        rec = _create(clean_agr, context={"sid": "x"})
        loaded = _get(rec["apply_gate_id"])
        assert loaded is not None
        assert loaded["apply_gate_id"] == rec["apply_gate_id"]
        assert loaded["status"] == "pending"

    def test_list_returns_records_newest_first(self, _create, _list, clean_agr):
        ids = []
        for i in range(3):
            r = _create(clean_agr, context={"i": i})
            ids.append(r["apply_gate_id"])
        records = _list()
        assert len(records) == 3
        assert records[0]["apply_gate_id"] == ids[2]
        assert records[-1]["apply_gate_id"] == ids[0]


# ======================== TEST 6-9: LIST FILTERS ======================== #

class TestListFilters:
    def test_list_filters_by_status_pending(self, _create, _list, clean_agr):
        _create(clean_agr, context={"p": 1})
        pending_only = _list(status="pending")
        assert len(pending_only) >= 1

    def test_list_filters_by_decision_eligible(self, _create, _list, clean_agr):
        agr = dict(clean_agr)
        agr["decision"] = "eligible_for_human_review"
        _create(agr, context={"d": "eligible"})
        eligible_records = _list(decision="eligible_for_human_review")
        assert len(eligible_records) >= 1
        for r in eligible_records:
            assert r["gate_decision"] == "eligible_for_human_review"

    def test_list_filters_by_decision_not_eligible(self, _create, _list):
        agr = {
            "decision": "not_eligible",
            "reason": "Not eligible.",
            "metadata": {},
            "warnings": [],
        }
        _create(agr)
        ne_records = _list(decision="not_eligible")
        assert len(ne_records) >= 1

    def test_list_filters_by_decision_blocked(self, _create, _list):
        agr = {
            "decision": "blocked",
            "reason": "Blocked.",
            "metadata": {},
            "warnings": [],
        }
        _create(agr)
        blocked_records = _list(decision="blocked")
        assert len(blocked_records) >= 1


# ======================== TEST 10-12: STATUS TRANSITIONS ======================== #

class TestUpdateStatus:
    def test_cancel_pending_changes_status(self, _create, _update, clean_agr):
        rec = _create(clean_agr)
        updated = _update(rec["apply_gate_id"], decision="cancelled", reviewer="alice")
        assert updated["status"] == "cancelled"
        assert updated["decision"] == "cancelled"
        assert updated["reviewer"] == "alice"
        assert updated["decided_at"] is not None

    def test_already_cancelled_cannot_be_cancelled_again(self, _create, _update, clean_agr):
        rec = _create(clean_agr)
        _update(rec["apply_gate_id"], decision="cancelled", reviewer="bob")
        second = _update(rec["apply_gate_id"], decision="cancelled", reviewer="charlie")
        assert second["status"] == "cancelled"
        assert any("already 'cancelled'" in w for w in second.get("warnings", []))

    def test_invalid_decision_raises_value_error(self, _create, _update, clean_agr):
        rec = _create(clean_agr)
        with pytest.raises(ValueError, match="Invalid decision"):
            _update(rec["apply_gate_id"], decision="invalid_op")


# ======================== TEST 13-25: SAFETY GUARDRAILS ======================== #

class TestSafetyGuardrails:
    def test_apply_gate_persisted_true(self, _create, clean_agr):
        rec = _create(clean_agr)
        assert rec["apply_gate_persisted"] is True

    def test_human_review_completed_always_false(self, _create, _update, _get, clean_agr):
        rec = _create(clean_agr)
        _update(rec["apply_gate_id"], decision="cancelled", reviewer="test")
        loaded = _get(rec["apply_gate_id"])
        assert loaded["human_review_completed"] is False

    def test_apply_authorized_always_false(self, _create, _update, _get, clean_agr):
        rec = _create(clean_agr)
        _update(rec["apply_gate_id"], decision="cancelled")
        loaded = _get(rec["apply_gate_id"])
        assert loaded["apply_authorized"] is False

    def test_apply_executed_always_false(self, _create, _update, _get, clean_agr):
        rec = _create(clean_agr)
        _update(rec["apply_gate_id"], decision="cancelled")
        loaded = _get(rec["apply_gate_id"])
        assert loaded["apply_executed"] is False

    def test_rollback_executed_always_false(self, _create, _update, _get, clean_agr):
        rec = _create(clean_agr)
        _update(rec["apply_gate_id"], decision="cancelled")
        loaded = _get(rec["apply_gate_id"])
        assert loaded["rollback_executed"] is False

    def test_simulation_executed_always_false(self, _create, _update, _get, clean_agr):
        rec = _create(clean_agr)
        _update(rec["apply_gate_id"], decision="cancelled")
        loaded = _get(rec["apply_gate_id"])
        assert loaded["simulation_executed"] is False

    def test_execution_allowed_always_false(self, _create, _update, _get, clean_agr):
        rec = _create(clean_agr)
        _update(rec["apply_gate_id"], decision="cancelled")
        loaded = _get(rec["apply_gate_id"])
        assert loaded["execution_allowed"] is False

    def test_tool_execution_allowed_always_false(self, _create, _update, _get, clean_agr):
        rec = _create(clean_agr)
        _update(rec["apply_gate_id"], decision="cancelled")
        loaded = _get(rec["apply_gate_id"])
        assert loaded["tool_execution_allowed"] is False

    def test_dry_run_execution_allowed_always_false(self, _create, _update, _get, clean_agr):
        rec = _create(clean_agr)
        _update(rec["apply_gate_id"], decision="cancelled")
        loaded = _get(rec["apply_gate_id"])
        assert loaded["dry_run_execution_allowed"] is False

    def test_simulation_execution_allowed_always_false(self, _create, _update, _get, clean_agr):
        rec = _create(clean_agr)
        _update(rec["apply_gate_id"], decision="cancelled")
        loaded = _get(rec["apply_gate_id"])
        assert loaded["simulation_execution_allowed"] is False

    def test_apply_gate_execution_allowed_always_false(self, _create, _update, _get, clean_agr):
        rec = _create(clean_agr)
        _update(rec["apply_gate_id"], decision="cancelled")
        loaded = _get(rec["apply_gate_id"])
        assert loaded["apply_gate_execution_allowed"] is False

    def test_apply_allowed_always_false(self, _create, _update, _get, clean_agr):
        rec = _create(clean_agr)
        _update(rec["apply_gate_id"], decision="cancelled")
        loaded = _get(rec["apply_gate_id"])
        assert loaded["apply_allowed"] is False

    def test_rollback_allowed_always_false(self, _create, _update, _get, clean_agr):
        rec = _create(clean_agr)
        _update(rec["apply_gate_id"], decision="cancelled")
        loaded = _get(rec["apply_gate_id"])
        assert loaded["rollback_allowed"] is False


# ======================== TEST 26-28: EDGE CASES ======================== #

class TestEdgeCases:
    def test_missing_agr_id_returns_none(self, _get):
        assert _get("nonexistent-agr-id-abc") is None

    def test_metadata_context_preserved(self, _create, clean_agr):
        ctx = {"session_id": "test-sid-99", "extra_key": "value"}
        rec = _create(clean_agr, context=ctx)
        assert rec["metadata"]["session_id"] == "test-sid-99"
        assert rec["metadata"]["extra_key"] == "value"

    def test_warnings_preserved_from_agr(self, _create, _get, clean_agr):
        agr = dict(clean_agr)
        agr["warnings"] = ["ag warning"]
        rec = _create(agr)
        loaded = _get(rec["apply_gate_id"])
        assert "ag warning" in loaded["warnings"]


# ======================== TEST 29: ELIGIBLE FOR HUMAN REVIEW STILL NO AUTH ======================== #

class TestEligibleGateSafety:
    def test_eligible_for_human_review_still_has_apply_authorized_false(self, _create, _get, _update, clean_agr):
        rec = _create(clean_agr)
        _update(rec["apply_gate_id"], decision="cancelled")
        loaded = _get(rec["apply_gate_id"])
        assert loaded["apply_authorized"] is False
