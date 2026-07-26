"""Tests for Apply Execution Gate Record Store (Milestone 70A).

Verifies that apply execution gate records are created, persisted, queried, and can be
cancelled/rejected/approved_execution_intent. No apply execution, tool execution, apply,
or rollback occurs.
"""

from __future__ import annotations

import json

import pytest


@pytest.fixture()
def aeg_store_dir(monkeypatch, tmp_path):
    """Redirect _ensure_apply_exec_gate_dir to a temp directory."""
    store_dir = tmp_path / "apply_execution_gates"
    store_dir.mkdir(parents=True, exist_ok=True)

    import aether.action.apply_execution_gate_queue as aegq_mod
    monkeypatch.setattr(aegq_mod, "_ensure_apply_exec_gate_dir", lambda: store_dir)

    return store_dir


@pytest.fixture()
def _create(aeg_store_dir):
    from aether.action.apply_execution_gate_queue import create_apply_execution_gate_record
    return create_apply_execution_gate_record


@pytest.fixture()
def _get():
    from aether.action.apply_execution_gate_queue import get_apply_execution_gate_record
    return get_apply_execution_gate_record


@pytest.fixture()
def _list():
    from aether.action.apply_execution_gate_queue import list_apply_execution_gate_records
    return list_apply_execution_gate_records


@pytest.fixture()
def _update():
    from aether.action.apply_execution_gate_queue import update_apply_execution_gate_record_status
    return update_apply_execution_gate_record_status


@pytest.fixture()
def ready_aegr():
    """A fully ready apply execution gate request."""
    return {
        "decision": "ready_for_execution_gate_review",
        "reason": "All checks passed.",
        "apply_execution_gate_required": True,
        "apply_execution_gate_status": "prepared",
        "human_authorization_id": "ha-001",
        "human_authorization_record_status": "approved_intent",
        "authorization_decision": "ready_for_human_authorization",
        "apply_gate_id": "ag-001",
        "verification_verdict_id": "vv-001",
        "simulation_result_id": "sim-001",
        "simulation_plan_id": "plan-1",
        "dry_run_id": "dr-1",
        "requested_action": {"tool_id": "test.tool", "action_type": "status_check"},
        "required_pre_execution_confirmations": [
            "I confirm human approval intent was recorded.",
            "I confirm the requested action is still desired.",
            "I confirm the target is correct.",
            "I understand this execution gate request still does not execute the action.",
            "I understand a separate future apply executor is required.",
            "I understand rollback may not be possible or automatic.",
        ],
        "execution_statement": "Apply execution gate review is required.",
        "blocking_reasons": [],
        "unresolved_risks": [],
        "recommended_next_step": "Present for review.",
        "human_review_completed": True,
        "human_intent_recorded": True,
        "apply_authorized": False,
        "apply_allowed": False,
        "rollback_allowed": False,
        "execution_allowed": False,
        "tool_execution_allowed": False,
        "dry_run_execution_allowed": False,
        "simulation_execution_allowed": False,
        "apply_gate_execution_allowed": False,
        "human_authorization_execution_allowed": False,
        "apply_execution_gate_execution_allowed": False,
        "metadata": {"source": "apply_execution_gate_request_builder", "schema_version": "1.0"},
        "warnings": [],
    }


@pytest.fixture()
def not_ready_aegr():
    return {
        "decision": "not_ready",
        "reason": "Not ready.",
        "apply_execution_gate_required": False,
        "apply_execution_gate_status": "prepared",
        "human_authorization_id": None,
        "human_authorization_record_status": "pending",
        "authorization_decision": "not_ready",
        "apply_gate_id": None,
        "verification_verdict_id": None,
        "simulation_result_id": None,
        "simulation_plan_id": None,
        "dry_run_id": None,
        "requested_action": None,
        "required_pre_execution_confirmations": [],
        "execution_statement": None,
        "blocking_reasons": ["some reason"],
        "unresolved_risks": [],
        "recommended_next_step": "Resolve issues.",
        "apply_authorized": False,
        "apply_allowed": False,
        "rollback_allowed": False,
        "execution_allowed": False,
        "tool_execution_allowed": False,
        "dry_run_execution_allowed": False,
        "simulation_execution_allowed": False,
        "apply_gate_execution_allowed": False,
        "human_authorization_execution_allowed": False,
        "apply_execution_gate_execution_allowed": False,
        "metadata": {},
        "warnings": [],
    }


@pytest.fixture()
def blocked_aegr():
    return {
        "decision": "blocked",
        "reason": "Blocked.",
        "apply_execution_gate_required": False,
        "apply_execution_gate_status": "prepared",
        "human_authorization_id": None,
        "authorization_decision": "blocked",
        "apply_gate_id": None,
        "verification_verdict_id": None,
        "simulation_result_id": None,
        "simulation_plan_id": None,
        "dry_run_id": None,
        "requested_action": None,
        "required_pre_execution_confirmations": [],
        "execution_statement": None,
        "blocking_reasons": ["blocked"],
        "unresolved_risks": [],
        "recommended_next_step": "Resolve conditions.",
        "apply_authorized": False,
        "apply_allowed": False,
        "rollback_allowed": False,
        "execution_allowed": False,
        "tool_execution_allowed": False,
        "dry_run_execution_allowed": False,
        "simulation_execution_allowed": False,
        "apply_gate_execution_allowed": False,
        "human_authorization_execution_allowed": False,
        "apply_execution_gate_execution_allowed": False,
        "metadata": {},
        "warnings": [],
    }


# ======================== TESTS 1-5: CREATION & PERSISTENCE ======================== #

class TestCreateApplyExecutionGateRecord:
    def test_creates_pending_record(self, _create, ready_aegr):
        rec = _create(ready_aegr, context={"session_id": "s1"})
        assert rec is not None
        assert rec["status"] == "pending"

    def test_apply_execution_gate_id_exists_and_is_unique(self, _create, ready_aegr):
        r1 = _create(ready_aegr, context={"sid": "a"})
        r2 = _create(ready_aegr, context={"sid": "b"})
        assert r1["apply_execution_gate_id"] != r2["apply_execution_gate_id"]
        assert len(r1["apply_execution_gate_id"]) == 32

    def test_record_persisted_outside_repo(self, _create, ready_aegr, aeg_store_dir):
        rec = _create(ready_aegr, context={"sid": "persist_test"})
        path = aeg_store_dir / f"apply_execution_gate_{rec['apply_execution_gate_id']}.json"
        assert path.exists()
        data = json.loads(path.read_text())
        assert data["apply_execution_gate_id"] == rec["apply_execution_gate_id"]

    def test_get_returns_saved_record(self, _create, _get, ready_aegr):
        rec = _create(ready_aegr, context={"sid": "x"})
        loaded = _get(rec["apply_execution_gate_id"])
        assert loaded is not None
        assert loaded["apply_execution_gate_id"] == rec["apply_execution_gate_id"]
        assert loaded["status"] == "pending"

    def test_list_returns_records_newest_first(self, _create, _list, ready_aegr):
        ids = []
        for i in range(3):
            r = _create(ready_aegr, context={"i": i})
            ids.append(r["apply_execution_gate_id"])
        records = _list()
        assert len(records) == 3
        assert records[0]["apply_execution_gate_id"] == ids[2]
        assert records[-1]["apply_execution_gate_id"] == ids[0]


# ======================== TESTS 6-9: LIST FILTERS ======================== #

class TestListFilters:
    def test_list_filters_by_status_pending(self, _create, _list, ready_aegr):
        _create(ready_aegr, context={"p": 1})
        pending_only = _list(status="pending")
        assert len(pending_only) >= 1

    def test_list_filters_by_decision_ready(self, _create, _list, ready_aegr):
        _create(ready_aegr, context={"d": "ready"})
        ready_records = _list(decision="ready_for_execution_gate_review")
        assert len(ready_records) >= 1
        for r in ready_records:
            assert r["gate_decision"] == "ready_for_execution_gate_review"

    def test_list_filters_by_decision_not_ready(self, _create, _list, not_ready_aegr):
        _create(not_ready_aegr, context={"d": "nr"})
        nr_records = _list(decision="not_ready")
        assert len(nr_records) >= 1

    def test_list_filters_by_decision_blocked(self, _create, _list, blocked_aegr):
        _create(blocked_aegr, context={"d": "blk"})
        blk_records = _list(decision="blocked")
        assert len(blk_records) >= 1


# ======================== TESTS 10-12: STATUS TRANSITIONS ======================== #

class TestUpdateStatus:
    def test_cancel_pending_changes_status(self, _create, _update, ready_aegr):
        rec = _create(ready_aegr)
        updated = _update(rec["apply_execution_gate_id"], decision="cancelled", reviewer="alice")
        assert updated["status"] == "cancelled"
        assert updated["decision"] == "cancelled"
        assert updated["reviewer"] == "alice"

    def test_reject_pending_changes_status(self, _create, _update, ready_aegr):
        rec = _create(ready_aegr)
        updated = _update(
            rec["apply_execution_gate_id"],
            decision="rejected",
            reviewer="bob",
            reason="too risky",
        )
        assert updated["status"] == "rejected"
        assert updated["decision"] == "rejected"
        assert updated["reviewer"] == "bob"
        assert updated["decision_reason"] == "too risky"

    def test_approved_execution_intent_pending_ready_changes_status(
        self, _create, _update, ready_aegr
    ):
        rec = _create(ready_aegr)
        confirmed = list(ready_aegr["required_pre_execution_confirmations"])
        updated = _update(
            rec["apply_execution_gate_id"],
            decision="approved_execution_intent",
            reviewer="carol",
            reason="approved after review",
            confirmations=confirmed,
        )
        assert updated["status"] == "approved_execution_intent"
        assert updated["decision"] == "approved_execution_intent"
        assert updated["reviewer"] == "carol"
        assert updated["decision_reason"] == "approved after review"
        assert len(updated["confirmations_received"]) >= 1


# ======================== TESTS 13-15: APPROVED_EXECUTION_INTENT REQUIREMENTS ======================== #

class TestApprovedIntentRequirements:
    def test_approved_execution_intent_requires_ready_decision(self, _create, _update, not_ready_aegr):
        rec = _create(not_ready_aegr)
        result = _update(
            rec["apply_execution_gate_id"],
            decision="approved_execution_intent",
            reviewer="test",
            confirmations=[],
        )
        assert result is None

    def test_approved_execution_intent_requires_confirmations(self, _create, _update, ready_aegr):
        rec = _create(ready_aegr)
        result = _update(
            rec["apply_execution_gate_id"],
            decision="approved_execution_intent",
            reviewer="test",
            confirmations=[],
        )
        assert result is None

    def test_approved_execution_intent_saves_confirmations_received(self, _create, _update, ready_aegr):
        rec = _create(ready_aegr)
        confirmed = list(ready_aegr["required_pre_execution_confirmations"])
        updated = _update(
            rec["apply_execution_gate_id"],
            decision="approved_execution_intent",
            reviewer="test",
            confirmations=confirmed,
        )
        assert len(updated["confirmations_received"]) == len(confirmed)
        for c in confirmed:
            assert c in updated["confirmations_received"]


# ======================== TEST 16-17: FINAL STATE & INVALID ======================== #

class TestFinalStates:
    def test_final_record_cannot_be_changed_again(self, _create, _update, ready_aegr):
        rec = _create(ready_aegr)
        _update(rec["apply_execution_gate_id"], decision="cancelled", reviewer="alice")
        second = _update(rec["apply_execution_gate_id"], decision="rejected", reviewer="bob")
        assert second is not None
        assert second["status"] == "cancelled"

    def test_invalid_decision_raises_value_error(self, _create, _update, ready_aegr):
        rec = _create(ready_aegr)
        with pytest.raises(ValueError, match="Invalid decision"):
            _update(rec["apply_execution_gate_id"], decision="invalid_op")


# ======================== TESTS 18-24: LIFECYCLE FIELD CHANGES ======================== #

class TestLifecycleFields:
    def test_apply_execution_gate_persisted_true_on_creation(self, _create, ready_aegr):
        rec = _create(ready_aegr)
        assert rec["apply_execution_gate_persisted"] is True

    def test_execution_review_completed_false_on_creation(self, _create, ready_aegr):
        rec = _create(ready_aegr)
        assert rec["execution_review_completed"] is False

    def test_execution_intent_recorded_false_on_creation(self, _create, ready_aegr):
        rec = _create(ready_aegr)
        assert rec["execution_intent_recorded"] is False

    def test_approved_execution_intent_sets_execution_review_completed_true(
        self, _create, _update, ready_aegr
    ):
        rec = _create(ready_aegr)
        confirmed = list(ready_aegr["required_pre_execution_confirmations"])
        updated = _update(
            rec["apply_execution_gate_id"],
            decision="approved_execution_intent",
            reviewer="test",
            confirmations=confirmed,
        )
        assert updated["execution_review_completed"] is True

    def test_approved_execution_intent_sets_execution_intent_recorded_true(
        self, _create, _update, ready_aegr
    ):
        rec = _create(ready_aegr)
        confirmed = list(ready_aegr["required_pre_execution_confirmations"])
        updated = _update(
            rec["apply_execution_gate_id"],
            decision="approved_execution_intent",
            reviewer="test",
            confirmations=confirmed,
        )
        assert updated["execution_intent_recorded"] is True

    def test_rejected_sets_execution_review_completed_true_intent_false(
        self, _create, _update, ready_aegr
    ):
        rec = _create(ready_aegr)
        updated = _update(rec["apply_execution_gate_id"], decision="rejected", reviewer="test")
        assert updated["execution_review_completed"] is True
        assert updated["execution_intent_recorded"] is False

    def test_cancelled_keeps_both_false(self, _create, _update, ready_aegr):
        rec = _create(ready_aegr)
        updated = _update(rec["apply_execution_gate_id"], decision="cancelled", reviewer="test")
        assert updated["execution_review_completed"] is False
        assert updated["execution_intent_recorded"] is False


# ======================== TESTS 25-37: SAFETY GUARDRAILS ======================== #

class TestSafetyGuardrails:
    def test_apply_authorized_always_false(self, _create, _update, _get, ready_aegr):
        rec = _create(ready_aegr)
        _update(rec["apply_execution_gate_id"], decision="approved_execution_intent", reviewer="test",
                confirmations=list(ready_aegr["required_pre_execution_confirmations"]))
        assert _get(rec["apply_execution_gate_id"])["apply_authorized"] is False

    def test_apply_executed_always_false(self, _create, _update, _get, ready_aegr):
        rec = _create(ready_aegr)
        _update(rec["apply_execution_gate_id"], decision="approved_execution_intent", reviewer="test",
                confirmations=list(ready_aegr["required_pre_execution_confirmations"]))
        assert _get(rec["apply_execution_gate_id"])["apply_executed"] is False

    def test_rollback_executed_always_false(self, _create, _update, _get, ready_aegr):
        rec = _create(ready_aegr)
        _update(rec["apply_execution_gate_id"], decision="approved_execution_intent", reviewer="test",
                confirmations=list(ready_aegr["required_pre_execution_confirmations"]))
        assert _get(rec["apply_execution_gate_id"])["rollback_executed"] is False

    def test_simulation_executed_always_false(self, _create, _update, _get, ready_aegr):
        rec = _create(ready_aegr)
        _update(rec["apply_execution_gate_id"], decision="approved_execution_intent", reviewer="test",
                confirmations=list(ready_aegr["required_pre_execution_confirmations"]))
        assert _get(rec["apply_execution_gate_id"])["simulation_executed"] is False

    def test_execution_allowed_always_false(self, _create, _update, _get, ready_aegr):
        rec = _create(ready_aegr)
        _update(rec["apply_execution_gate_id"], decision="approved_execution_intent", reviewer="test",
                confirmations=list(ready_aegr["required_pre_execution_confirmations"]))
        assert _get(rec["apply_execution_gate_id"])["execution_allowed"] is False

    def test_tool_execution_allowed_always_false(self, _create, _update, _get, ready_aegr):
        rec = _create(ready_aegr)
        _update(rec["apply_execution_gate_id"], decision="approved_execution_intent", reviewer="test",
                confirmations=list(ready_aegr["required_pre_execution_confirmations"]))
        assert _get(rec["apply_execution_gate_id"])["tool_execution_allowed"] is False

    def test_dry_run_execution_allowed_always_false(self, _create, _update, _get, ready_aegr):
        rec = _create(ready_aegr)
        _update(rec["apply_execution_gate_id"], decision="approved_execution_intent", reviewer="test",
                confirmations=list(ready_aegr["required_pre_execution_confirmations"]))
        assert _get(rec["apply_execution_gate_id"])["dry_run_execution_allowed"] is False

    def test_simulation_execution_allowed_always_false(self, _create, _update, _get, ready_aegr):
        rec = _create(ready_aegr)
        _update(rec["apply_execution_gate_id"], decision="approved_execution_intent", reviewer="test",
                confirmations=list(ready_aegr["required_pre_execution_confirmations"]))
        assert _get(rec["apply_execution_gate_id"])["simulation_execution_allowed"] is False

    def test_apply_gate_execution_allowed_always_false(self, _create, _update, _get, ready_aegr):
        rec = _create(ready_aegr)
        _update(rec["apply_execution_gate_id"], decision="approved_execution_intent", reviewer="test",
                confirmations=list(ready_aegr["required_pre_execution_confirmations"]))
        assert _get(rec["apply_execution_gate_id"])["apply_gate_execution_allowed"] is False

    def test_human_authorization_execution_allowed_always_false(self, _create, _update, _get, ready_aegr):
        rec = _create(ready_aegr)
        _update(rec["apply_execution_gate_id"], decision="approved_execution_intent", reviewer="test",
                confirmations=list(ready_aegr["required_pre_execution_confirmations"]))
        assert _get(rec["apply_execution_gate_id"])["human_authorization_execution_allowed"] is False

    def test_apply_execution_gate_execution_allowed_always_false(self, _create, _update, _get, ready_aegr):
        rec = _create(ready_aegr)
        _update(rec["apply_execution_gate_id"], decision="approved_execution_intent", reviewer="test",
                confirmations=list(ready_aegr["required_pre_execution_confirmations"]))
        assert _get(rec["apply_execution_gate_id"])["apply_execution_gate_execution_allowed"] is False

    def test_apply_allowed_always_false(self, _create, _update, _get, ready_aegr):
        rec = _create(ready_aegr)
        _update(rec["apply_execution_gate_id"], decision="approved_execution_intent", reviewer="test",
                confirmations=list(ready_aegr["required_pre_execution_confirmations"]))
        assert _get(rec["apply_execution_gate_id"])["apply_allowed"] is False

    def test_rollback_allowed_always_false(self, _create, _update, _get, ready_aegr):
        rec = _create(ready_aegr)
        _update(rec["apply_execution_gate_id"], decision="approved_execution_intent", reviewer="test",
                confirmations=list(ready_aegr["required_pre_execution_confirmations"]))
        assert _get(rec["apply_execution_gate_id"])["rollback_allowed"] is False


# ======================== TEST 38: MISSING ID ======================== #

class TestMissingId:
    def test_missing_id_returns_none(self, _get):
        assert _get("nonexistent-aeg-id-abc") is None


# ======================== TESTS 39-41: CONTENT ======================== #

class TestContentPreservation:
    def test_metadata_context_preserved(self, _create, ready_aegr):
        ctx = {"session_id": "test-sid-99"}
        rec = _create(ready_aegr, context=ctx)
        assert rec["metadata"]["session_id"] == "test-sid-99"

    def test_warnings_preserved_from_aegr(self, _create, _get, ready_aegr):
        aegr = dict(ready_aegr)
        aegr["warnings"] = ["aeg warning"]
        rec = _create(aegr)
        loaded = _get(rec["apply_execution_gate_id"])
        assert "aeg warning" in loaded["warnings"]

    def test_approved_execution_intent_warning_no_apply_authorized(self, _create, _update, ready_aegr):
        rec = _create(ready_aegr)
        confirmed = list(ready_aegr["required_pre_execution_confirmations"])
        updated = _update(
            rec["apply_execution_gate_id"],
            decision="approved_execution_intent",
            reviewer="test",
            confirmations=confirmed,
        )
        warns_text = " ".join(updated["warnings"])
        assert "apply is not authorized" in warns_text.lower()
