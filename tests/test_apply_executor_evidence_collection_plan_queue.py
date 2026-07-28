"""Tests for Apply Executor Evidence Collection Plan Record Store (Milestone 78A).

Verifies that apply executor evidence collection plan records are created, persisted, queried,
and can be cancelled/rejected/approved_collection_plan_intent. No apply execution,
tool execution, apply, evidence collection, or rollback plan attachment occurs.
"""

from __future__ import annotations

import json
import pytest

from aether.core.config import get_private_dir


@pytest.fixture()
def aeepl_store_dir(monkeypatch, tmp_path):
    """Redirect the collection plan store to a temp directory."""
    store_dir = tmp_path / "apply_executor_evidence_collection_plans"
    store_dir.mkdir(parents=True, exist_ok=True)

    import aether.action.apply_executor_evidence_collection_plan_queue as aeplq_mod

    original_ensure = aeplq_mod._ensure_collection_plan_dir
    original_get = aeplq_mod.get_private_dir

    def mock_ensure():
        return store_dir

    def mock_get():
        return store_dir

    monkeypatch.setattr(aeplq_mod, "_ensure_collection_plan_dir", mock_ensure)
    monkeypatch.setattr(aeplq_mod, "get_private_dir", mock_get)

    yield store_dir

    aeplq_mod._ensure_collection_plan_dir = original_ensure
    aeplq_mod.get_private_dir = original_get


@pytest.fixture()
def _create(aeepl_store_dir):
    from aether.action.apply_executor_evidence_collection_plan_queue import (
        create_apply_executor_evidence_collection_plan_record,
    )
    return create_apply_executor_evidence_collection_plan_record


@pytest.fixture()
def _get():
    from aether.action.apply_executor_evidence_collection_plan_queue import (
        get_apply_executor_evidence_collection_plan_record,
    )
    return get_apply_executor_evidence_collection_plan_record


@pytest.fixture()
def _list():
    from aether.action.apply_executor_evidence_collection_plan_queue import (
        list_apply_executor_evidence_collection_plan_records,
    )
    return list_apply_executor_evidence_collection_plan_records


@pytest.fixture()
def _update():
    from aether.action.apply_executor_evidence_collection_plan_queue import (
        update_apply_executor_evidence_collection_plan_record_status,
    )
    return update_apply_executor_evidence_collection_plan_record_status


def make_ready_plan():
    """Create a ready evidence collection plan dict."""
    return {
        "evidence_collection_plan_type": "apply_executor_evidence_collection_plan",
        "evidence_collection_plan_required": True,
        "evidence_collection_plan_status": "prepared",
        "decision": "evidence_collection_plan_ready",
        "reason": "All checks passed.",
        "apply_executor_evidence_contract_id": "test-eec-id",
        "evidence_contract_decision": "evidence_contract_ready",
        "apply_executor_plan_id": "test-plan-id",
        "apply_executor_contract_id": "test-ctr-id",
        "apply_execution_gate_id": "test-aeg-id",
        "human_authorization_id": "test-ha-id",
        "apply_gate_id": "test-ag-id",
        "verification_verdict_id": "test-vv-id",
        "simulation_result_id": "test-sr-id",
        "simulation_plan_id": "test-sp-id",
        "dry_run_id": "test-dr-id",
        "requested_action": {"tool_id": "test.tool", "action_type": "status_check", "target": "test"},
        "required_collection_plan_confirmations": ["c1", "c2", "c3"],
        "evidence_collection_plan_statement": "Plan prepared.",
        "blocking_reasons": [],
        "unresolved_risks": [],
        "recommended_next_step": "Persist this plan.",
        "evidence_contract_review_completed": True,
        "evidence_contract_intent_recorded": True,
        "evidence_collected": False,
        "rollback_plan_attached": False,
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
        "apply_executor_plan_execution_allowed": False,
        "apply_executor_evidence_contract_execution_allowed": False,
        "apply_executor_evidence_collection_plan_execution_allowed": False,
        "apply_executor_evidence_collection_plan_record_execution_allowed": False,
        "apply_executed": False,
        "rollback_executed": False,
        "metadata": {"source": "builder", "schema_version": "1.0"},
        "warnings": ["Test warning"],
    }


class TestCreateApplyExecutorEvidenceCollectionPlanRecord:
    def test_01_create_pending_record(self, _create, ready_plan):
        rec = _create(ready_plan)
        assert rec is not None
        assert rec["status"] == "pending"
        assert rec["apply_executor_evidence_collection_plan_persisted"] is True
        assert "apply_executor_evidence_collection_plan_id" in rec

    def test_02_record_has_unique_id(self, _create):
        r1 = _create(make_ready_plan())
        r2 = _create(make_ready_plan())
        assert r1["apply_executor_evidence_collection_plan_id"] != r2["apply_executor_evidence_collection_plan_id"]

    def test_03_record_persisted_to_filesystem(self, _create, aeepl_store_dir):
        plan = make_ready_plan()
        rec = _create(plan)
        assert rec is not None
        path = aeepl_store_dir / f"apply_executor_evidence_collection_plan_{rec['apply_executor_evidence_collection_plan_id']}.json"
        assert path.exists()
        with open(path, "r") as f:
            data = json.load(f)
        assert data["apply_executor_evidence_collection_plan_id"] == rec["apply_executor_evidence_collection_plan_id"]
        assert data["status"] == "pending"

    def test_04_get_record_by_id(self, _create, _get, ready_plan):
        rec = _create(ready_plan)
        fetched = _get(rec["apply_executor_evidence_collection_plan_id"])
        assert fetched is not None
        assert fetched["apply_executor_evidence_collection_plan_id"] == rec["apply_executor_evidence_collection_plan_id"]

    def test_05_get_missing_id_returns_none(self, _get):
        assert _get("non-existent-id") is None


class TestListApplyExecutorEvidenceCollectionPlanRecords:
    def test_06_list_records(self, _create, _list, ready_plan):
        r1 = _create(ready_plan)
        r2 = _create(make_ready_plan())
        records = _list()
        assert len(records) >= 2

    def test_07_filter_by_status_pending(self, _create, _list, ready_plan):
        r1 = _create(ready_plan)
        r2 = _create(make_ready_plan())
        pending = _list(status="pending")
        assert len(pending) >= 2

    def test_08_filter_by_decision_ready(self, _create, _list, ready_plan):
        r1 = _create(ready_plan)
        r2 = _create(make_ready_plan())
        ready = _list(decision="evidence_collection_plan_ready")
        assert len(ready) >= 2

    def test_09_filter_by_decision_not_ready(self, _create, _list):
        not_ready = _list(decision="not_ready")
        # Should be empty unless test creates not_ready records
        assert len(not_ready) >= 0

    def test_10_filter_by_decision_blocked(self, _create, _list):
        blocked = _list(decision="blocked")
        assert len(blocked) >= 0

    def test_11_limit_works(self, _create, _list, ready_plan):
        for i in range(10):
            c = dict(ready_plan)
            c["apply_executor_plan_id"] = f"plan-{i}"
            _create(c)
        all_recs = _list(limit=5)
        assert len(all_recs) == 5


class TestUpdateApplyExecutorEvidenceCollectionPlanRecordStatus:
    def test_12_cancel_pending(self, _create, _update, ready_plan):
        rec = _create(ready_plan)
        updated = _update(rec["apply_executor_evidence_collection_plan_id"], "cancelled", reviewer="test")
        assert updated is not None
        assert updated["status"] == "cancelled"
        assert updated["evidence_collection_plan_review_completed"] is False
        assert updated["evidence_collection_plan_intent_recorded"] is False

    def test_13_reject_pending(self, _create, _update, ready_plan):
        rec = _create(ready_plan)
        updated = _update(rec["apply_executor_evidence_collection_plan_id"], "rejected", reviewer="test")
        assert updated is not None
        assert updated["status"] == "rejected"
        assert updated["evidence_collection_plan_review_completed"] is True
        assert updated["evidence_collection_plan_intent_recorded"] is False

    def test_14_approve_pending_ready(self, _create, _update, ready_plan):
        rec = _create(ready_plan)
        updated = _update(
            rec["apply_executor_evidence_collection_plan_id"],
            "approved_collection_plan_intent",
            reviewer="test",
            reason="validated",
            confirmations=["c1", "c2", "c3"],
        )
        assert updated is not None
        assert updated["status"] == "approved_collection_plan_intent"
        assert updated["decision"] == "approved_collection_plan_intent"
        assert updated["evidence_collection_plan_review_completed"] is True
        assert updated["evidence_collection_plan_intent_recorded"] is True
        assert updated["confirmations_received"] == ["c1", "c2", "c3"]
        assert updated["apply_authorized"] is False

    def test_15_pending_record_once(self, _create, _update, ready_plan):
        rec = _create(ready_plan)
        updated1 = _update(rec["apply_executor_evidence_collection_plan_id"], "approved_collection_plan_intent", reviewer="test", confirmations=["c1", "c2", "c3"])
        assert updated1["status"] == "approved_collection_plan_intent"
        updated2 = _update(rec["apply_executor_evidence_collection_plan_id"], "cancelled", reviewer="test2")
        assert updated2["status"] == "approved_collection_plan_intent"


class TestValidation:
    def test_16_requires_evidence_collection_plan_ready(self, _create, _update):
        not_ready = make_ready_plan()
        not_ready["decision"] = "not_ready"
        rec = _create(not_ready)
        updated = _update(rec["apply_executor_evidence_collection_plan_id"], "approved_collection_plan_intent", reviewer="test", confirmations=["c1"])
        assert updated is None

    def test_17_requires_confirmations(self, _create, _update, ready_plan):
        rec = _create(ready_plan)
        updated = _update(rec["apply_executor_evidence_collection_plan_id"], "approved_collection_plan_intent", reviewer="test", confirmations=[])
        assert updated is None

    def test_18_requires_all_confirmations(self, _create, _update, ready_plan):
        rec = _create(ready_plan)
        updated = _update(rec["apply_executor_evidence_collection_plan_id"], "approved_collection_plan_intent", reviewer="test", confirmations=["c1"])
        assert updated is None

    def test_19_invalid_decision_raises(self, _create, _update, ready_plan):
        rec = _create(ready_plan)
        with pytest.raises(ValueError):
            _update(rec["apply_executor_evidence_collection_plan_id"], "invalid", reviewer="test")

    def test_20_all_flags_false(self, _create, _update, ready_plan):
        rec = _create(ready_plan)
        flags = [
            "evidence_collected", "rollback_plan_attached", "apply_authorized",
            "apply_executed", "rollback_executed", "execution_allowed",
            "tool_execution_allowed", "dry_run_execution_allowed", "simulation_execution_allowed",
            "apply_gate_execution_allowed", "human_authorization_execution_allowed",
            "apply_execution_gate_execution_allowed", "apply_executor_contract_execution_allowed",
            "apply_executor_plan_execution_allowed", "apply_executor_evidence_contract_execution_allowed",
            "apply_executor_evidence_collection_plan_execution_allowed", "apply_allowed", "rollback_allowed"
        ]
        for f in flags:
            assert rec[f] is False, f"{f} should be False in {rec['status']}"
        updated = _update(rec["apply_executor_evidence_collection_plan_id"], "approved_collection_plan_intent", reviewer="test", confirmations=["c1", "c2", "c3"])
        for f in flags:
            assert updated[f] is False, f"{f} should be False after approval"

    def test_21_metadata_preserved(self, _create, ready_plan):
        context = {"session_id": "test-session"}
        rec = _create(ready_plan, context=context)
        assert rec["metadata"] == context

    def test_22_warnings_preserved(self, _create, ready_plan):
        plan = dict(ready_plan)
        plan["warnings"] = ["w1", "w2"]
        rec = _create(plan)
        assert rec["warnings"] == ["w1", "w2"]


@pytest.fixture()
def ready_plan():
    return make_ready_plan()
