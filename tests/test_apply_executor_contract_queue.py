"""Tests for Apply Executor Contract Record Store (Milestone 72A).

Verifies that apply executor contract records are created, persisted, queried, and can be
cancelled/rejected/approved_contract_intent. No apply execution, tool execution, apply,
or rollback occurs.
"""

from __future__ import annotations

import json

import pytest


@pytest.fixture()
def aec_store_dir(monkeypatch, tmp_path):
    """Redirect _ensure_exec_contract_dir to a temp directory."""
    store_dir = tmp_path / "apply_executor_contracts"
    store_dir.mkdir(parents=True, exist_ok=True)

    import aether.action.apply_executor_contract_queue as aecq_mod
    monkeypatch.setattr(aecq_mod, "_ensure_exec_contract_dir", lambda: store_dir)

    return store_dir


@pytest.fixture()
def _create(aec_store_dir):
    from aether.action.apply_executor_contract_queue import create_apply_executor_contract_record
    return create_apply_executor_contract_record


@pytest.fixture()
def _get():
    from aether.action.apply_executor_contract_queue import get_apply_executor_contract_record
    return get_apply_executor_contract_record


@pytest.fixture()
def _list():
    from aether.action.apply_executor_contract_queue import list_apply_executor_contract_records
    return list_apply_executor_contract_records


@pytest.fixture()
def _update():
    from aether.action.apply_executor_contract_queue import update_apply_executor_contract_record_status
    return update_apply_executor_contract_record_status


@pytest.fixture()
def ready_aec():
    """A fully ready apply executor contract object."""
    return {
        "contract_required": True,
        "contract_status": "prepared",
        "contract_type": "apply_executor_contract",
        "decision": "contract_ready",
        "reason": "Contract checks passed.",
        "apply_execution_gate_id": "aeg-001",
        "apply_execution_gate_record_status": "approved_execution_intent",
        "gate_decision": "ready_for_execution_gate_review",
        "human_authorization_id": "ha-001",
        "apply_gate_id": "ag-001",
        "verification_verdict_id": "vv-001",
        "simulation_result_id": "sim-001",
        "simulation_plan_id": "plan-1",
        "dry_run_id": "dr-1",
        "requested_action": {"tool_id": "test.tool", "action_type": "status_check", "target": "tgt"},
        "apply_execution_gate_snapshot": {},
        "contract_checks": [{"name": "all_pass", "passed": True, "severity": "low"}],
        "execution_boundary": {
            "allowed_action_type": "status_check",
            "allowed_tool_id": "test.tool",
            "allowed_target": "tgt",
            "allowed_parameters": {},
            "forbidden_capabilities": ["shell"],
            "execution_scope": "contract_only_no_execution",
            "execution_allowed": False,
            "apply_allowed": False,
            "tool_execution_allowed": False,
        },
        "rollback_expectation": {
            "rollback_required_before_future_apply": True,
            "rollback_plan_required": True,
            "rollback_plan_present": False,
            "rollback_verified": False,
            "rollback_allowed": False,
            "rollback_executed": False,
        },
        "evidence_requirements": [
            {"name": "pre_execution_state_evidence", "required": True, "satisfied": False},
        ],
        "required_executor_confirmations": [
            "I confirm the execution gate intent was recorded.",
            "I confirm this contract does not execute the action.",
            "I confirm this contract does not authorize apply.",
            "I confirm a future executor must collect pre-execution and post-execution evidence.",
            "I confirm rollback planning is required before future apply.",
            "I understand a separate future apply executor is required.",
        ],
        "contract_statement": "Apply executor contract is prepared.",
        "blocking_reasons": [],
        "unresolved_risks": [],
        "recommended_next_step": "Persist this contract.",
        "execution_review_completed": True,
        "execution_intent_recorded": True,
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
        "apply_executor_contract_execution_allowed": False,
        "metadata": {"source": "apply_executor_contract_builder", "schema_version": "1.0"},
        "warnings": [],
    }


@pytest.fixture()
def not_ready_aec():
    return {
        "contract_required": False,
        "contract_status": "prepared",
        "contract_type": "apply_executor_contract",
        "decision": "not_ready",
        "reason": "Not ready.",
        "apply_execution_gate_id": None,
        "apply_execution_gate_record_status": "pending",
        "gate_decision": None,
        "human_authorization_id": None,
        "apply_gate_id": None,
        "verification_verdict_id": None,
        "simulation_result_id": None,
        "simulation_plan_id": None,
        "dry_run_id": None,
        "requested_action": None,
        "apply_execution_gate_snapshot": None,
        "contract_checks": [],
        "execution_boundary": {
            "allowed_action_type": None, "allowed_tool_id": None, "allowed_target": None,
            "allowed_parameters": {},
            "forbidden_capabilities": [],
            "execution_scope": "blocked_or_not_ready_no_execution",
            "execution_allowed": False, "apply_allowed": False, "tool_execution_allowed": False,
        },
        "rollback_expectation": {},
        "evidence_requirements": [],
        "required_executor_confirmations": [],
        "contract_statement": None,
        "blocking_reasons": ["some reason"],
        "unresolved_risks": [],
        "recommended_next_step": "Resolve issues.",
        "execution_review_completed": False,
        "execution_intent_recorded": False,
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
        "apply_executor_contract_execution_allowed": False,
        "metadata": {},
        "warnings": [],
    }


@pytest.fixture()
def blocked_aec():
    return {
        "contract_required": False,
        "contract_status": "prepared",
        "contract_type": "apply_executor_contract",
        "decision": "blocked",
        "reason": "Blocked.",
        "apply_execution_gate_id": None,
        "gate_decision": None,
        "human_authorization_id": None,
        "apply_gate_id": None,
        "verification_verdict_id": None,
        "simulation_result_id": None,
        "simulation_plan_id": None,
        "dry_run_id": None,
        "requested_action": None,
        "apply_execution_gate_snapshot": None,
        "contract_checks": [],
        "execution_boundary": {
            "allowed_action_type": None, "allowed_tool_id": None, "allowed_target": None,
            "allowed_parameters": {},
            "forbidden_capabilities": [],
            "execution_scope": "blocked_or_not_ready_no_execution",
            "execution_allowed": False, "apply_allowed": False, "tool_execution_allowed": False,
        },
        "rollback_expectation": {},
        "evidence_requirements": [],
        "required_executor_confirmations": [],
        "contract_statement": None,
        "blocking_reasons": ["blocked"],
        "unresolved_risks": [],
        "recommended_next_step": "Resolve conditions.",
        "execution_review_completed": False,
        "execution_intent_recorded": False,
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
        "apply_executor_contract_execution_allowed": False,
        "metadata": {},
        "warnings": [],
    }


# ======================== TESTS 1-5: CREATION & PERSISTENCE ======================== #

class TestCreateApplyExecutorContractRecord:
    def test_creates_pending_record(self, _create, ready_aec):
        rec = _create(ready_aec, context={"session_id": "s1"})
        assert rec is not None
        assert rec["status"] == "pending"

    def test_apply_executor_contract_id_exists_and_is_unique(self, _create, ready_aec):
        r1 = _create(ready_aec, context={"sid": "a"})
        r2 = _create(ready_aec, context={"sid": "b"})
        assert r1["apply_executor_contract_id"] != r2["apply_executor_contract_id"]
        assert len(r1["apply_executor_contract_id"]) == 32

    def test_record_persisted_outside_repo(self, _create, ready_aec, aec_store_dir):
        rec = _create(ready_aec, context={"sid": "persist_test"})
        path = aec_store_dir / f"apply_executor_contract_{rec['apply_executor_contract_id']}.json"
        assert path.exists()
        data = json.loads(path.read_text())
        assert data["apply_executor_contract_id"] == rec["apply_executor_contract_id"]

    def test_get_returns_saved_record(self, _create, _get, ready_aec):
        rec = _create(ready_aec, context={"sid": "x"})
        loaded = _get(rec["apply_executor_contract_id"])
        assert loaded is not None
        assert loaded["apply_executor_contract_id"] == rec["apply_executor_contract_id"]
        assert loaded["status"] == "pending"

    def test_list_returns_records_newest_first(self, _create, _list, ready_aec):
        ids = []
        for i in range(3):
            r = _create(ready_aec, context={"i": i})
            ids.append(r["apply_executor_contract_id"])
        records = _list()
        assert len(records) == 3
        assert records[0]["apply_executor_contract_id"] == ids[2]
        assert records[-1]["apply_executor_contract_id"] == ids[0]


# ======================== TESTS 6-9: LIST FILTERS ======================== #

class TestListFilters:
    def test_list_filters_by_status_pending(self, _create, _list, ready_aec):
        _create(ready_aec, context={"p": 1})
        pending_only = _list(status="pending")
        assert len(pending_only) >= 1

    def test_list_filters_by_decision_contract_ready(self, _create, _list, ready_aec):
        _create(ready_aec, context={"d": "ready"})
        ready_records = _list(decision="contract_ready")
        assert len(ready_records) >= 1
        for r in ready_records:
            assert r["contract_decision"] == "contract_ready"

    def test_list_filters_by_decision_not_ready(self, _create, _list, not_ready_aec):
        _create(not_ready_aec, context={"d": "nr"})
        nr_records = _list(decision="not_ready")
        assert len(nr_records) >= 1

    def test_list_filters_by_decision_blocked(self, _create, _list, blocked_aec):
        _create(blocked_aec, context={"d": "blk"})
        blk_records = _list(decision="blocked")
        assert len(blk_records) >= 1


# ======================== TESTS 10-12: STATUS TRANSITIONS ======================== #

class TestUpdateStatus:
    def test_cancel_pending_changes_status(self, _create, _update, ready_aec):
        rec = _create(ready_aec)
        updated = _update(rec["apply_executor_contract_id"], decision="cancelled", reviewer="alice")
        assert updated["status"] == "cancelled"
        assert updated["decision"] == "cancelled"
        assert updated["reviewer"] == "alice"

    def test_reject_pending_changes_status(self, _create, _update, ready_aec):
        rec = _create(ready_aec)
        updated = _update(
            rec["apply_executor_contract_id"],
            decision="rejected", reviewer="bob", reason="too risky"
        )
        assert updated["status"] == "rejected"
        assert updated["decision"] == "rejected"
        assert updated["reviewer"] == "bob"
        assert updated["decision_reason"] == "too risky"

    def test_approved_contract_intent_pending_ready_changes_status(self, _create, _update, ready_aec):
        rec = _create(ready_aec)
        confirmed = list(ready_aec["required_executor_confirmations"])
        updated = _update(
            rec["apply_executor_contract_id"],
            decision="approved_contract_intent",
            reviewer="carol", reason="approved after review", confirmations=confirmed
        )
        assert updated["status"] == "approved_contract_intent"
        assert updated["decision"] == "approved_contract_intent"
        assert updated["reviewer"] == "carol"
        assert updated["decision_reason"] == "approved after review"
        assert len(updated["confirmations_received"]) >= 1


# ======================== TESTS 13-15: APPROVED CONTRACT INTENT REQUIREMENTS ======================== #

class TestApprovedIntentRequirements:
    def test_approved_contract_intent_requires_contract_ready(self, _create, _update, not_ready_aec):
        rec = _create(not_ready_aec)
        result = _update(rec["apply_executor_contract_id"], decision="approved_contract_intent", reviewer="test", confirmations=[])
        assert result is None

    def test_approved_contract_intent_requires_confirmations(self, _create, _update, ready_aec):
        rec = _create(ready_aec)
        result = _update(rec["apply_executor_contract_id"], decision="approved_contract_intent", reviewer="test", confirmations=[])
        assert result is None

    def test_approved_contract_intent_saves_confirmations_received(self, _create, _update, ready_aec):
        rec = _create(ready_aec)
        confirmed = list(ready_aec["required_executor_confirmations"])
        updated = _update(
            rec["apply_executor_contract_id"],
            decision="approved_contract_intent", reviewer="test", confirmations=confirmed
        )
        assert len(updated["confirmations_received"]) == len(confirmed)
        for c in confirmed:
            assert c in updated["confirmations_received"]


# ======================== TESTS 16-17: FINAL STATE & INVALID ======================== #

class TestFinalStates:
    def test_final_record_cannot_be_changed_again(self, _create, _update, ready_aec):
        rec = _create(ready_aec)
        _update(rec["apply_executor_contract_id"], decision="cancelled", reviewer="alice")
        second = _update(rec["apply_executor_contract_id"], decision="rejected", reviewer="bob")
        assert second is not None
        assert second["status"] == "cancelled"

    def test_invalid_decision_raises_value_error(self, _create, _update, ready_aec):
        rec = _create(ready_aec)
        with pytest.raises(ValueError, match="Invalid decision"):
            _update(rec["apply_executor_contract_id"], decision="invalid_op")


# ======================== TESTS 18-26: LIFECYCLE FIELD CHANGES ======================== #

class TestLifecycleFields:
    def test_apply_executor_contract_persisted_true_on_creation(self, _create, ready_aec):
        rec = _create(ready_aec)
        assert rec["apply_executor_contract_persisted"] is True

    def test_contract_review_completed_false_on_creation(self, _create, ready_aec):
        rec = _create(ready_aec)
        assert rec["contract_review_completed"] is False

    def test_contract_intent_recorded_false_on_creation(self, _create, ready_aec):
        rec = _create(ready_aec)
        assert rec["contract_intent_recorded"] is False

    def test_evidence_collected_false_on_creation(self, _create, ready_aec):
        rec = _create(ready_aec)
        assert rec["evidence_collected"] is False

    def test_rollback_plan_attached_false_on_creation(self, _create, ready_aec):
        rec = _create(ready_aec)
        assert rec["rollback_plan_attached"] is False

    def test_approved_contract_intent_sets_contract_review_completed_true(self, _create, _update, ready_aec):
        rec = _create(ready_aec)
        confirmed = list(ready_aec["required_executor_confirmations"])
        updated = _update(
            rec["apply_executor_contract_id"],
            decision="approved_contract_intent", reviewer="test", confirmations=confirmed
        )
        assert updated["contract_review_completed"] is True

    def test_approved_contract_intent_sets_contract_intent_recorded_true(self, _create, _update, ready_aec):
        rec = _create(ready_aec)
        confirmed = list(ready_aec["required_executor_confirmations"])
        updated = _update(
            rec["apply_executor_contract_id"],
            decision="approved_contract_intent", reviewer="test", confirmations=confirmed
        )
        assert updated["contract_intent_recorded"] is True

    def test_rejected_sets_contract_review_completed_true_intent_false(self, _create, _update, ready_aec):
        rec = _create(ready_aec)
        updated = _update(rec["apply_executor_contract_id"], decision="rejected", reviewer="test")
        assert updated["contract_review_completed"] is True
        assert updated["contract_intent_recorded"] is False

    def test_cancelled_keeps_both_false(self, _create, _update, ready_aec):
        rec = _create(ready_aec)
        updated = _update(rec["apply_executor_contract_id"], decision="cancelled", reviewer="test")
        assert updated["contract_review_completed"] is False
        assert updated["contract_intent_recorded"] is False


# ======================== TESTS 25-40: SAFETY GUARDRAILS ======================== #

class TestSafetyGuardrails:
    def test_evidence_collected_always_false(self, _create, _update, _get, ready_aec):
        rec = _create(ready_aec)
        _update(rec["apply_executor_contract_id"], decision="approved_contract_intent", reviewer="test", confirmations=list(ready_aec["required_executor_confirmations"]))
        assert _get(rec["apply_executor_contract_id"])["evidence_collected"] is False

    def test_rollback_plan_attached_always_false(self, _create, _update, _get, ready_aec):
        rec = _create(ready_aec)
        _update(rec["apply_executor_contract_id"], decision="approved_contract_intent", reviewer="test", confirmations=list(ready_aec["required_executor_confirmations"]))
        assert _get(rec["apply_executor_contract_id"])["rollback_plan_attached"] is False

    def test_apply_authorized_always_false(self, _create, _update, _get, ready_aec):
        rec = _create(ready_aec)
        _update(rec["apply_executor_contract_id"], decision="approved_contract_intent", reviewer="test", confirmations=list(ready_aec["required_executor_confirmations"]))
        assert _get(rec["apply_executor_contract_id"])["apply_authorized"] is False

    def test_apply_executed_always_false(self, _create, _update, _get, ready_aec):
        rec = _create(ready_aec)
        _update(rec["apply_executor_contract_id"], decision="approved_contract_intent", reviewer="test", confirmations=list(ready_aec["required_executor_confirmations"]))
        assert _get(rec["apply_executor_contract_id"])["apply_executed"] is False

    def test_rollback_executed_always_false(self, _create, _update, _get, ready_aec):
        rec = _create(ready_aec)
        _update(rec["apply_executor_contract_id"], decision="approved_contract_intent", reviewer="test", confirmations=list(ready_aec["required_executor_confirmations"]))
        assert _get(rec["apply_executor_contract_id"])["rollback_executed"] is False

    def test_simulation_executed_always_false(self, _create, _update, _get, ready_aec):
        rec = _create(ready_aec)
        _update(rec["apply_executor_contract_id"], decision="approved_contract_intent", reviewer="test", confirmations=list(ready_aec["required_executor_confirmations"]))
        assert _get(rec["apply_executor_contract_id"])["simulation_executed"] is False

    def test_execution_allowed_always_false(self, _create, _update, _get, ready_aec):
        rec = _create(ready_aec)
        _update(rec["apply_executor_contract_id"], decision="approved_contract_intent", reviewer="test", confirmations=list(ready_aec["required_executor_confirmations"]))
        assert _get(rec["apply_executor_contract_id"])["execution_allowed"] is False

    def test_tool_execution_allowed_always_false(self, _create, _update, _get, ready_aec):
        rec = _create(ready_aec)
        _update(rec["apply_executor_contract_id"], decision="approved_contract_intent", reviewer="test", confirmations=list(ready_aec["required_executor_confirmations"]))
        assert _get(rec["apply_executor_contract_id"])["tool_execution_allowed"] is False

    def test_dry_run_execution_allowed_always_false(self, _create, _update, _get, ready_aec):
        rec = _create(ready_aec)
        _update(rec["apply_executor_contract_id"], decision="approved_contract_intent", reviewer="test", confirmations=list(ready_aec["required_executor_confirmations"]))
        assert _get(rec["apply_executor_contract_id"])["dry_run_execution_allowed"] is False

    def test_simulation_execution_allowed_always_false(self, _create, _update, _get, ready_aec):
        rec = _create(ready_aec)
        _update(rec["apply_executor_contract_id"], decision="approved_contract_intent", reviewer="test", confirmations=list(ready_aec["required_executor_confirmations"]))
        assert _get(rec["apply_executor_contract_id"])["simulation_execution_allowed"] is False

    def test_apply_gate_execution_allowed_always_false(self, _create, _update, _get, ready_aec):
        rec = _create(ready_aec)
        _update(rec["apply_executor_contract_id"], decision="approved_contract_intent", reviewer="test", confirmations=list(ready_aec["required_executor_confirmations"]))
        assert _get(rec["apply_executor_contract_id"])["apply_gate_execution_allowed"] is False

    def test_human_authorization_execution_allowed_always_false(self, _create, _update, _get, ready_aec):
        rec = _create(ready_aec)
        _update(rec["apply_executor_contract_id"], decision="approved_contract_intent", reviewer="test", confirmations=list(ready_aec["required_executor_confirmations"]))
        assert _get(rec["apply_executor_contract_id"])["human_authorization_execution_allowed"] is False

    def test_apply_execution_gate_execution_allowed_always_false(self, _create, _update, _get, ready_aec):
        rec = _create(ready_aec)
        _update(rec["apply_executor_contract_id"], decision="approved_contract_intent", reviewer="test", confirmations=list(ready_aec["required_executor_confirmations"]))
        assert _get(rec["apply_executor_contract_id"])["apply_execution_gate_execution_allowed"] is False

    def test_apply_executor_contract_execution_allowed_always_false(self, _create, _update, _get, ready_aec):
        rec = _create(ready_aec)
        _update(rec["apply_executor_contract_id"], decision="approved_contract_intent", reviewer="test", confirmations=list(ready_aec["required_executor_confirmations"]))
        assert _get(rec["apply_executor_contract_id"])["apply_executor_contract_execution_allowed"] is False

    def test_apply_allowed_always_false(self, _create, _update, _get, ready_aec):
        rec = _create(ready_aec)
        _update(rec["apply_executor_contract_id"], decision="approved_contract_intent", reviewer="test", confirmations=list(ready_aec["required_executor_confirmations"]))
        assert _get(rec["apply_executor_contract_id"])["apply_allowed"] is False

    def test_rollback_allowed_always_false(self, _create, _update, _get, ready_aec):
        rec = _create(ready_aec)
        _update(rec["apply_executor_contract_id"], decision="approved_contract_intent", reviewer="test", confirmations=list(ready_aec["required_executor_confirmations"]))
        assert _get(rec["apply_executor_contract_id"])["rollback_allowed"] is False


# ======================== TEST 41: MISSING ID ======================== #

class TestMissingId:
    def test_missing_id_returns_none(self, _get):
        assert _get("nonexistent-aecr-id-abc") is None


# ======================== TESTS 42-46: CONTENT & WARNINGS ======================== #

class TestContentWarnings:
    def test_metadata_context_preserved(self, _create, ready_aec):
        ctx = {"session_id": "test-sid-99"}
        rec = _create(ready_aec, context=ctx)
        assert rec["metadata"]["session_id"] == "test-sid-99"

    def test_warnings_preserved_from_aec(self, _create, _get, ready_aec):
        aec = dict(ready_aec)
        aec["warnings"] = ["aec warning"]
        rec = _create(aec)
        loaded = _get(rec["apply_executor_contract_id"])
        assert "aec warning" in loaded["warnings"]

    def test_approved_contract_intent_warning_no_apply_authorized(self, _create, _update, ready_aec):
        rec = _create(ready_aec)
        confirmed = list(ready_aec["required_executor_confirmations"])
        updated = _update(
            rec["apply_executor_contract_id"],
            decision="approved_contract_intent", reviewer="test", confirmations=confirmed
        )
        warns_text = " ".join(updated["warnings"])
        assert "apply is not authorized" in warns_text.lower()

    def test_approved_contract_intent_warning_future_plan_required(self, _create, _update, ready_aec):
        rec = _create(ready_aec)
        confirmed = list(ready_aec["required_executor_confirmations"])
        updated = _update(
            rec["apply_executor_contract_id"],
            decision="approved_contract_intent", reviewer="test", confirmations=confirmed
        )
        warns_text = " ".join(updated["warnings"])
        assert "future apply executor plan is required" in warns_text.lower()

    def test_approved_contract_intent_warning_evidence_not_collected(self, _create, _update, ready_aec):
        rec = _create(ready_aec)
        confirmed = list(ready_aec["required_executor_confirmations"])
        updated = _update(
            rec["apply_executor_contract_id"],
            decision="approved_contract_intent", reviewer="test", confirmations=confirmed
        )
        warns_text = " ".join(updated["warnings"])
        assert "Evidence has not been collected" in warns_text
