"""Tests for Apply Executor Evidence Contract Record Store (Milestone 76A)."""

from __future__ import annotations

import json
import pytest

from aether.core.config import get_private_dir


@pytest.fixture()
def aeeq_store_dir(monkeypatch, tmp_path):
    store_dir = tmp_path / "apply_executor_evidence_contracts"
    store_dir.mkdir(parents=True, exist_ok=True)
    import aether.action.apply_executor_evidence_contract_queue as aeeq_mod
    orig_ensure = aeeq_mod._ensure_evidence_contract_dir
    orig_get = aeeq_mod.get_private_dir
    def mock_ensure(): return store_dir
    def mock_get(): return store_dir
    monkeypatch.setattr(aeeq_mod, "_ensure_evidence_contract_dir", mock_ensure)
    monkeypatch.setattr(aeeq_mod, "get_private_dir", mock_get)
    yield store_dir
    for f in store_dir.iterdir(): f.unlink()


@pytest.fixture()
def create_rec(aeeq_store_dir):
    from aether.action.apply_executor_evidence_contract_queue import create_apply_executor_evidence_contract_record
    return create_apply_executor_evidence_contract_record


@pytest.fixture()
def get_rec():
    from aether.action.apply_executor_evidence_contract_queue import get_apply_executor_evidence_contract_record
    return get_apply_executor_evidence_contract_record


@pytest.fixture()
def list_rec():
    from aether.action.apply_executor_evidence_contract_queue import list_apply_executor_evidence_contract_records
    return list_apply_executor_evidence_contract_records


@pytest.fixture()
def update_rec():
    from aether.action.apply_executor_evidence_contract_queue import update_apply_executor_evidence_contract_record_status
    return update_apply_executor_evidence_contract_record_status


def make_ready():
    return {
        "evidence_contract_type": "apply_executor_evidence_contract",
        "evidence_contract_required": True,
        "decision": "evidence_contract_ready",
        "required_evidence_confirmations": ["c1", "c2", "c3"],
        "apply_executor_plan_id": "test-plan",
        "metadata": {},
        "warnings": [],
    }


class TestCreateApplyExecutorEvidenceContractRecord:
    def test_01_create_pending(self, create_rec):
        rec = create_rec(make_ready())
        assert rec is not None
        assert rec["status"] == "pending"
        assert rec["apply_executor_evidence_contract_persisted"] is True
        assert "apply_executor_evidence_contract_id" in rec

    def test_02_unique_id(self, create_rec):
        r1 = create_rec(make_ready())
        r2 = create_rec(make_ready())
        assert r1["apply_executor_evidence_contract_id"] != r2["apply_executor_evidence_contract_id"]

    def test_03_persisted_to_fs(self, create_rec, aeeq_store_dir, get_rec):
        rec = create_rec(make_ready())
        assert rec is not None
        path = aeeq_store_dir / f"apply_executor_evidence_contract_{rec['apply_executor_evidence_contract_id']}.json"
        assert path.exists()
        assert get_rec(rec["apply_executor_evidence_contract_id"]) is not None

    def test_04_get_by_id(self, create_rec, get_rec):
        rec = create_rec(make_ready())
        fetched = get_rec(rec["apply_executor_evidence_contract_id"])
        assert fetched["apply_executor_evidence_contract_id"] == rec["apply_executor_evidence_contract_id"]

    def test_05_get_none(self, get_rec):
        assert get_rec("non-existent") is None


class TestListApplyExecutorEvidenceContractRecords:
    def test_06_list_returns_records(self, create_rec, list_rec):
        create_rec(make_ready())
        create_rec(make_ready())
        recs = list_rec()
        assert len(recs) >= 2

    def test_07_filter_by_status(self, create_rec, list_rec):
        create_rec(make_ready())
        recs = list_rec(status="pending")
        assert len(recs) >= 1

    def test_08_filter_by_decision(self, create_rec, list_rec):
        create_rec(make_ready())
        recs = list_rec(decision="evidence_contract_ready")
        assert len(recs) >= 1

    def test_09_limit(self, create_rec, list_rec):
        for i in range(5):
            c = make_ready()
            c["apply_executor_plan_id"] = f"plan-{i}"
            create_rec(c)
        recs = list_rec(limit=2)
        assert len(recs) <= 2


class TestUpdateApplyExecutorEvidenceContractRecordStatus:
    def test_10_cancel_pending(self, create_rec, update_rec):
        rec = create_rec(make_ready())
        updated = update_rec(rec["apply_executor_evidence_contract_id"], "cancelled", reviewer="test")
        assert updated["status"] == "cancelled"

    def test_11_reject_pending(self, create_rec, update_rec):
        rec = create_rec(make_ready())
        updated = update_rec(rec["apply_executor_evidence_contract_id"], "rejected", reviewer="test")
        assert updated["status"] == "rejected"

    def test_12_approve_ready(self, create_rec, update_rec):
        rec = create_rec(make_ready())
        updated = update_rec(rec["apply_executor_evidence_contract_id"], "approved_evidence_contract_intent", reviewer="test", confirmations=["c1", "c2", "c3"])
        assert updated["status"] == "approved_evidence_contract_intent"

    def test_13_final_status_unchanged(self, create_rec, update_rec):
        rec = create_rec(make_ready())
        updated1 = update_rec(rec["apply_executor_evidence_contract_id"], "approved_evidence_contract_intent", reviewer="test", confirmations=["c1", "c2", "c3"])
        assert updated1["status"] == "approved_evidence_contract_intent"
        updated2 = update_rec(rec["apply_executor_evidence_contract_id"], "rejected", reviewer="test2")
        assert updated2["status"] == "approved_evidence_contract_intent"

    def test_14_approve_requires_ready_decision(self, create_rec, update_rec):
        bad = make_ready()
        bad["decision"] = "not_ready"
        rec = create_rec(bad)
        updated = update_rec(rec["apply_executor_evidence_contract_id"], "approved_evidence_contract_intent", reviewer="test", confirmations=["c1", "c2", "c3"])
        assert updated is None

    def test_14_requires_evidence_contract_required_true(self, create_rec, update_rec):
        bad = make_ready()
        bad["evidence_contract_required"] = False
        rec = create_rec(bad)
        updated = update_rec(rec["apply_executor_evidence_contract_id"], "approved_evidence_contract_intent", reviewer="test", confirmations=["c1", "c2", "c3"])
        assert updated is None

    def test_15_requires_confirmations(self, create_rec, update_rec):
        rec = create_rec(make_ready())
        updated = update_rec(rec["apply_executor_evidence_contract_id"], "approved_evidence_contract_intent", reviewer="test", confirmations=[])
        assert updated is None

    def test_15_requires_all_confirmations(self, create_rec, update_rec):
        rec = create_rec(make_ready())
        updated = update_rec(rec["apply_executor_evidence_contract_id"], "approved_evidence_contract_intent", reviewer="test", confirmations=["c1"])
        assert updated is None

    def test_16_invalid_decision_raises(self, create_rec, update_rec):
        rec = create_rec(make_ready())
        from pytest import raises
        with raises(ValueError):
            update_rec(rec["apply_executor_evidence_contract_id"], "invalid", reviewer="test")

    def test_17_record_flags_all_false(self, create_rec, update_rec):
        rec = create_rec(make_ready())
        assert rec["evidence_collected"] is False
        assert rec["apply_authorized"] is False
        approved = update_rec(rec["apply_executor_evidence_contract_id"], "approved_evidence_contract_intent", reviewer="test", confirmations=["c1", "c2", "c3"])
        assert approved["evidence_collected"] is False
        assert approved["apply_authorized"] is False

    def test_18_metadata_preserved(self, create_rec):
        rec = create_rec(make_ready(), context={"session": "test"})
        assert rec["metadata"] == {"session": "test"}

    def test_19_warnings_preserved(self, create_rec):
        w = make_ready()
        w["warnings"] = ["w1", "w2"]
        rec = create_rec(w)
        assert rec["warnings"] == ["w1", "w2"]

    def test_20_id_format(self, create_rec):
        rec = create_rec(make_ready())
        assert isinstance(rec["apply_executor_evidence_contract_id"], str)
        assert len(rec["apply_executor_evidence_contract_id"]) == 32
