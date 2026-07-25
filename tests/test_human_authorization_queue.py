"""Tests for Human Authorization Record Store (Milestone 68A).

Verifies that human authorization records are created, persisted, queried, and can be
cancelled/rejected/approved_intent. No apply execution, tool execution, apply, or rollback occurs.
"""

from __future__ import annotations

import json

import pytest


@pytest.fixture()
def ha_store_dir(monkeypatch, tmp_path):
    """Redirect _ensure_human_auth_dir to a temp directory."""
    store_dir = tmp_path / "human_authorizations"
    store_dir.mkdir(parents=True, exist_ok=True)

    import aether.action.human_authorization_queue as haq_mod
    monkeypatch.setattr(haq_mod, "_ensure_human_auth_dir", lambda: store_dir)

    return store_dir


@pytest.fixture()
def _create(ha_store_dir):
    from aether.action.human_authorization_queue import create_human_authorization_record
    return create_human_authorization_record


@pytest.fixture()
def _get():
    from aether.action.human_authorization_queue import get_human_authorization_record
    return get_human_authorization_record


@pytest.fixture()
def _list():
    from aether.action.human_authorization_queue import list_human_authorization_records
    return list_human_authorization_records


@pytest.fixture()
def _update():
    from aether.action.human_authorization_queue import update_human_authorization_record_status
    return update_human_authorization_record_status


@pytest.fixture()
def ready_haar():
    return {
        "decision": "ready_for_human_authorization",
        "reason": "Ready.",
        "human_authorization_required": True,
        "apply_gate_id": "ag-001",
        "verification_verdict_id": "vv-001",
        "simulation_result_id": "sim-001",
        "simulation_plan_id": "plan-1",
        "dry_run_id": "dr-1",
        "requested_action": {"tool_id": "test.tool", "action_type": "status_check"},
        "required_human_confirmations": [
            "I confirm the requested action is still desired.",
            "I confirm the target is correct.",
            "I reviewed the dry-run, simulation result, and verification verdict.",
            "I understand rollback may not be possible or automatic.",
            "I understand this authorization request still does not execute the action.",
            "I understand a separate future apply executor is required.",
        ],
        "blocking_reasons": [],
        "unresolved_risks": [],
        "recommended_next_step": "Present to human reviewer.",
        "apply_authorized": False,
        "apply_allowed": False,
        "rollback_allowed": False,
        "execution_allowed": False,
        "tool_execution_allowed": False,
        "dry_run_execution_allowed": False,
        "simulation_execution_allowed": False,
        "apply_gate_execution_allowed": False,
        "metadata": {"source": "human_apply_authorization_request_builder", "schema_version": "1.0"},
        "warnings": [],
    }


@pytest.fixture()
def not_ready_haar():
    return {
        "decision": "not_ready",
        "reason": "Not ready.",
        "human_authorization_required": False,
        "apply_gate_id": "ag-002",
        "verification_verdict_id": None,
        "simulation_result_id": None,
        "simulation_plan_id": None,
        "dry_run_id": None,
        "requested_action": None,
        "required_human_confirmations": [],
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
        "metadata": {},
        "warnings": [],
    }


@pytest.fixture()
def blocked_haar():
    return {
        "decision": "blocked",
        "reason": "Blocked.",
        "human_authorization_required": False,
        "apply_gate_id": "ag-003",
        "verification_verdict_id": None,
        "simulation_result_id": None,
        "simulation_plan_id": None,
        "dry_run_id": None,
        "requested_action": None,
        "required_human_confirmations": [],
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
        "metadata": {},
        "warnings": [],
    }


# ======================== TESTS 1-5: CREATION & PERSISTENCE ======================== #

class TestCreateHumanAuthorizationRecord:
    def test_creates_pending_record(self, _create, ready_haar):
        rec = _create(ready_haar, context={"session_id": "s1"})
        assert rec is not None
        assert rec["status"] == "pending"

    def test_human_authorization_id_exists_and_is_unique(self, _create, ready_haar):
        r1 = _create(ready_haar, context={"sid": "a"})
        r2 = _create(ready_haar, context={"sid": "b"})
        assert r1["human_authorization_id"] != r2["human_authorization_id"]
        assert len(r1["human_authorization_id"]) == 32

    def test_record_persisted_outside_repo(self, _create, ready_haar, ha_store_dir):
        rec = _create(ready_haar, context={"sid": "persist_test"})
        path = ha_store_dir / f"human_authorization_{rec['human_authorization_id']}.json"
        assert path.exists()
        data = json.loads(path.read_text())
        assert data["human_authorization_id"] == rec["human_authorization_id"]

    def test_get_returns_saved_record(self, _create, _get, ready_haar):
        rec = _create(ready_haar, context={"sid": "x"})
        loaded = _get(rec["human_authorization_id"])
        assert loaded is not None
        assert loaded["human_authorization_id"] == rec["human_authorization_id"]
        assert loaded["status"] == "pending"

    def test_list_returns_records_newest_first(self, _create, _list, ready_haar):
        ids = []
        for i in range(3):
            r = _create(ready_haar, context={"i": i})
            ids.append(r["human_authorization_id"])
        records = _list()
        assert len(records) == 3
        assert records[0]["human_authorization_id"] == ids[2]
        assert records[-1]["human_authorization_id"] == ids[0]


# ======================== TESTS 6-9: LIST FILTERS ======================== #

class TestListFilters:
    def test_list_filters_by_status_pending(self, _create, _list, ready_haar):
        _create(ready_haar, context={"p": 1})
        pending_only = _list(status="pending")
        assert len(pending_only) >= 1

    def test_list_filters_by_decision_ready(self, _create, _list, ready_haar):
        _create(ready_haar, context={"d": "ready"})
        ready_records = _list(decision="ready_for_human_authorization")
        assert len(ready_records) >= 1
        for r in ready_records:
            assert r["authorization_decision"] == "ready_for_human_authorization"

    def test_list_filters_by_decision_not_ready(self, _create, _list, not_ready_haar):
        _create(not_ready_haar, context={"d": "nr"})
        nr_records = _list(decision="not_ready")
        assert len(nr_records) >= 1

    def test_list_filters_by_decision_blocked(self, _create, _list, blocked_haar):
        _create(blocked_haar, context={"d": "blk"})
        blk_records = _list(decision="blocked")
        assert len(blk_records) >= 1


# ======================== TESTS 10-12: STATUS TRANSITIONS ======================== #

class TestUpdateStatus:
    def test_cancel_pending_changes_status(self, _create, _update, ready_haar):
        rec = _create(ready_haar)
        updated = _update(rec["human_authorization_id"], decision="cancelled", reviewer="alice")
        assert updated["status"] == "cancelled"
        assert updated["decision"] == "cancelled"
        assert updated["reviewer"] == "alice"

    def test_reject_pending_changes_status(self, _create, _update, ready_haar):
        rec = _create(ready_haar)
        updated = _update(rec["human_authorization_id"], decision="rejected", reviewer="bob", reason="too risky")
        assert updated["status"] == "rejected"
        assert updated["decision"] == "rejected"
        assert updated["reviewer"] == "bob"
        assert updated["decision_reason"] == "too risky"

    def test_approved_intent_pending_ready_changes_status(self, _create, _update, ready_haar):
        rec = _create(ready_haar)
        confirmed = list(ready_haar["required_human_confirmations"])
        updated = _update(rec["human_authorization_id"], decision="approved_intent", reviewer="carol", reason="approved after review", confirmations=confirmed)
        assert updated["status"] == "approved_intent"
        assert updated["decision"] == "approved_intent"
        assert updated["reviewer"] == "carol"
        assert updated["decision_reason"] == "approved after review"
        assert len(updated["confirmations_received"]) >= 1


# ======================== TESTS 13-15: APPROVED_INTENT REQUIREMENTS ======================== #

class TestApprovedIntentRequirements:
    def test_approved_intent_requires_ready_decision(self, _create, _update, not_ready_haar):
        rec = _create(not_ready_haar)
        result = _update(rec["human_authorization_id"], decision="approved_intent", reviewer="test", confirmations=[])
        assert result is None

    def test_approved_intent_requires_confirmations(self, _create, _update, ready_haar):
        rec = _create(ready_haar)
        result = _update(rec["human_authorization_id"], decision="approved_intent", reviewer="test", confirmations=[])
        assert result is None

    def test_approved_intent_saves_confirmations_received(self, _create, _update, ready_haar):
        rec = _create(ready_haar)
        confirmed = list(ready_haar["required_human_confirmations"])
        updated = _update(rec["human_authorization_id"], decision="approved_intent", reviewer="test", confirmations=confirmed)
        assert len(updated["confirmations_received"]) == len(confirmed)
        for c in confirmed:
            assert c in updated["confirmations_received"]


# ======================== TEST 16-17: FINAL STATE & INVALID ======================== #

class TestFinalStates:
    def test_final_record_cannot_be_changed_again(self, _create, _update, ready_haar):
        rec = _create(ready_haar)
        _update(rec["human_authorization_id"], decision="cancelled", reviewer="alice")
        second = _update(rec["human_authorization_id"], decision="rejected", reviewer="bob")
        assert second is not None  # Returns unchanged record with warning
        assert second["status"] == "cancelled"  # Status unchanged

    def test_invalid_decision_raises_value_error(self, _create, _update, ready_haar):
        rec = _create(ready_haar)
        with pytest.raises(ValueError, match="Invalid decision"):
            _update(rec["human_authorization_id"], decision="invalid_op")


# ======================== TESTS 18-24: LIFECYCLE FIELD CHANGES ======================== #

class TestLifecycleFields:
    def test_human_authorization_persisted_true_on_creation(self, _create, ready_haar):
        rec = _create(ready_haar)
        assert rec["human_authorization_persisted"] is True

    def test_human_review_completed_false_on_creation(self, _create, ready_haar):
        rec = _create(ready_haar)
        assert rec["human_review_completed"] is False

    def test_human_intent_recorded_false_on_creation(self, _create, ready_haar):
        rec = _create(ready_haar)
        assert rec["human_intent_recorded"] is False

    def test_approved_intent_sets_human_review_completed_true(self, _create, _update, ready_haar):
        rec = _create(ready_haar)
        confirmed = list(ready_haar["required_human_confirmations"])
        updated = _update(rec["human_authorization_id"], decision="approved_intent", reviewer="test", confirmations=confirmed)
        assert updated["human_review_completed"] is True
        assert updated["human_intent_recorded"] is True

    def test_approved_intent_sets_human_intent_recorded_true(self, _create, _update, ready_haar):
        rec = _create(ready_haar)
        confirmed = list(ready_haar["required_human_confirmations"])
        updated = _update(rec["human_authorization_id"], decision="approved_intent", reviewer="test", confirmations=confirmed)
        assert updated["human_intent_recorded"] is True

    def test_rejected_sets_human_review_completed_true_intent_false(self, _create, _update, ready_haar):
        rec = _create(ready_haar)
        updated = _update(rec["human_authorization_id"], decision="rejected", reviewer="test")
        assert updated["human_review_completed"] is True
        assert updated["human_intent_recorded"] is False

    def test_cancelled_keeps_both_false(self, _create, _update, ready_haar):
        rec = _create(ready_haar)
        updated = _update(rec["human_authorization_id"], decision="cancelled", reviewer="test")
        assert updated["human_review_completed"] is False
        assert updated["human_intent_recorded"] is False


# ======================== TESTS 25-36: SAFETY GUARDRAILS ======================== #

class TestSafetyGuardrails:
    def _make_flags_false_test(self, record_key, expected_val, description):
        def test_fn(_create, _update, _get, ready_haar):
            rec = _create(ready_haar)
            _update(rec["human_authorization_id"], decision="approved_intent", reviewer="test",
                    confirmations=list(ready_haar["required_human_confirmations"]))
            loaded = _get(rec["human_authorization_id"])
            assert loaded[record_key] == expected_val, f"{description}: expected {expected_val}, got {loaded[record_key]}"
            # Also verify after cancel
            _update(rec["human_authorization_id"], decision="cancelled", reviewer="test2")
            loaded2 = _get(rec["human_authorization_id"])
            assert loaded2[record_key] == expected_val, f"{description} (after cancel): expected {expected_val}"
        return test_fn

    def test_apply_authorized_always_false(self, _create, _update, _get, ready_haar):
        rec = _create(ready_haar)
        _update(rec["human_authorization_id"], decision="approved_intent", reviewer="test", confirmations=list(ready_haar["required_human_confirmations"]))
        assert _get(rec["human_authorization_id"])["apply_authorized"] is False

    def test_apply_executed_always_false(self, _create, _update, _get, ready_haar):
        rec = _create(ready_haar)
        _update(rec["human_authorization_id"], decision="approved_intent", reviewer="test", confirmations=list(ready_haar["required_human_confirmations"]))
        assert _get(rec["human_authorization_id"])["apply_executed"] is False

    def test_rollback_executed_always_false(self, _create, _update, _get, ready_haar):
        rec = _create(ready_haar)
        _update(rec["human_authorization_id"], decision="approved_intent", reviewer="test", confirmations=list(ready_haar["required_human_confirmations"]))
        assert _get(rec["human_authorization_id"])["rollback_executed"] is False

    def test_simulation_executed_always_false(self, _create, _update, _get, ready_haar):
        rec = _create(ready_haar)
        _update(rec["human_authorization_id"], decision="approved_intent", reviewer="test", confirmations=list(ready_haar["required_human_confirmations"]))
        assert _get(rec["human_authorization_id"])["simulation_executed"] is False

    def test_execution_allowed_always_false(self, _create, _update, _get, ready_haar):
        rec = _create(ready_haar)
        _update(rec["human_authorization_id"], decision="approved_intent", reviewer="test", confirmations=list(ready_haar["required_human_confirmations"]))
        assert _get(rec["human_authorization_id"])["execution_allowed"] is False

    def test_tool_execution_allowed_always_false(self, _create, _update, _get, ready_haar):
        rec = _create(ready_haar)
        _update(rec["human_authorization_id"], decision="approved_intent", reviewer="test", confirmations=list(ready_haar["required_human_confirmations"]))
        assert _get(rec["human_authorization_id"])["tool_execution_allowed"] is False

    def test_dry_run_execution_allowed_always_false(self, _create, _update, _get, ready_haar):
        rec = _create(ready_haar)
        _update(rec["human_authorization_id"], decision="approved_intent", reviewer="test", confirmations=list(ready_haar["required_human_confirmations"]))
        assert _get(rec["human_authorization_id"])["dry_run_execution_allowed"] is False

    def test_simulation_execution_allowed_always_false(self, _create, _update, _get, ready_haar):
        rec = _create(ready_haar)
        _update(rec["human_authorization_id"], decision="approved_intent", reviewer="test", confirmations=list(ready_haar["required_human_confirmations"]))
        assert _get(rec["human_authorization_id"])["simulation_execution_allowed"] is False

    def test_apply_gate_execution_allowed_always_false(self, _create, _update, _get, ready_haar):
        rec = _create(ready_haar)
        _update(rec["human_authorization_id"], decision="approved_intent", reviewer="test", confirmations=list(ready_haar["required_human_confirmations"]))
        assert _get(rec["human_authorization_id"])["apply_gate_execution_allowed"] is False

    def test_human_authorization_execution_allowed_always_false(self, _create, _update, _get, ready_haar):
        rec = _create(ready_haar)
        _update(rec["human_authorization_id"], decision="approved_intent", reviewer="test", confirmations=list(ready_haar["required_human_confirmations"]))
        assert _get(rec["human_authorization_id"])["human_authorization_execution_allowed"] is False

    def test_apply_allowed_always_false(self, _create, _update, _get, ready_haar):
        rec = _create(ready_haar)
        _update(rec["human_authorization_id"], decision="approved_intent", reviewer="test", confirmations=list(ready_haar["required_human_confirmations"]))
        assert _get(rec["human_authorization_id"])["apply_allowed"] is False

    def test_rollback_allowed_always_false(self, _create, _update, _get, ready_haar):
        rec = _create(ready_haar)
        _update(rec["human_authorization_id"], decision="approved_intent", reviewer="test", confirmations=list(ready_haar["required_human_confirmations"]))
        assert _get(rec["human_authorization_id"])["rollback_allowed"] is False


# ======================== TEST 37: MISSING ID ======================== #

class TestMissingId:
    def test_missing_id_returns_none(self, _get):
        assert _get("nonexistent-ha-id-abc") is None


# ======================== TESTS 38-40: CONTENT ======================== #

class TestContentPreservation:
    def test_metadata_context_preserved(self, _create, ready_haar):
        ctx = {"session_id": "test-sid-99"}
        rec = _create(ready_haar, context=ctx)
        assert rec["metadata"]["session_id"] == "test-sid-99"

    def test_warnings_preserved_from_haar(self, _create, _get, ready_haar):
        haar = dict(ready_haar)
        haar["warnings"] = ["ha warning"]
        rec = _create(haar)
        loaded = _get(rec["human_authorization_id"])
        assert "ha warning" in loaded["warnings"]

    def test_approved_intent_warning_no_apply_authorized(self, _create, _update, ready_haar):
        rec = _create(ready_haar)
        confirmed = list(ready_haar["required_human_confirmations"])
        updated = _update(rec["human_authorization_id"], decision="approved_intent", reviewer="test", confirmations=confirmed)
        warns_text = " ".join(updated["warnings"])
        assert "apply is not authorized" in warns_text.lower()
        assert "separate future apply execution gate" in warns_text.lower() or "apply is not authorized" in warns_text.lower()
