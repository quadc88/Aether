"""Tests for Observation Record Queue/Store (Milestone 83C).

Focused store tests using tmp_path/monkeypatch only. No TestClient, no
endpoint calls, no route/runtime/service invocation beyond the queue
functions under test, and no writes to the real private data directory.
"""

from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

import aether.action.observation_record_queue as obs_queue


def _valid_record(**overrides: object) -> dict:
    record = {
        "observation_id": "a" * 32,
        "observation_type": "observation_record",
        "plan_step_id": "ps_001",
        "evidence_item_id": None,
        "collector_contract_id": None,
        "target": "/tmp/test_output.txt",
        "observed_value": "line count = 42",
        "expected_value": None,
        "status": "pending",
        "observed_at": "2026-07-31T12:00:00+00:00",
        "metadata": {"source": "manual"},
        "safety_flags": {
            "tool_execution_allowed": False,
            "tool_executed": False,
            "evidence_collection_performed": False,
            "system_state_modified": False,
            "apply_performed": False,
            "rollback_performed": False,
            "persistent_write_performed": False,
            "external_side_effect_performed": False,
        },
    }
    record.update(overrides)
    return record


@pytest.fixture()
def store_dir(monkeypatch, tmp_path):
    """Redirect the queue module's store directory to a per-test tmp path."""
    d = tmp_path / "observation_records"
    d.mkdir(parents=True, exist_ok=True)

    def mock_get_observation_records_dir():
        return d

    monkeypatch.setattr(
        obs_queue, "get_observation_records_dir", mock_get_observation_records_dir
    )
    return d


def _set_created_at(path: Path, timestamp: str) -> None:
    """Rewrite the created_at field of an already-saved record file."""
    data = json.loads(path.read_text(encoding="utf-8"))
    data["created_at"] = timestamp
    path.write_text(json.dumps(data), encoding="utf-8")


class TestObservationRecordsDir:
    def test_get_observation_records_dir_uses_private_dir(self, monkeypatch, tmp_path):
        private = tmp_path / "private"

        def mock_get_private_dir():
            return private

        monkeypatch.setattr(obs_queue, "get_private_dir", mock_get_private_dir)
        result = obs_queue.get_observation_records_dir()
        assert result == private / "observation_records"
        assert result.is_dir()

    def test_directory_created_with_parents(self, store_dir):
        assert store_dir.is_dir()
        assert store_dir.name == "observation_records"


class TestSaveLoad:
    def test_save_load_round_trip(self, store_dir):
        record = _valid_record()
        saved = obs_queue.save_observation_record(record)
        loaded = obs_queue.load_observation_record(record["observation_id"])
        assert loaded == saved
        assert loaded["target"] == "/tmp/test_output.txt"

    def test_saved_filename_pattern(self, store_dir):
        record = _valid_record()
        obs_queue.save_observation_record(record)
        expected = store_dir / f"observation_record_{record['observation_id']}.json"
        assert expected.exists()

    def test_missing_load_returns_none(self, store_dir):
        assert obs_queue.load_observation_record("f" * 32) is None

    def test_save_returns_record_with_envelope_fields(self, store_dir):
        saved = obs_queue.save_observation_record(_valid_record())
        assert "created_at" in saved
        assert "updated_at" in saved
        assert saved["decision"] is None
        assert saved["decided_at"] is None
        assert saved["reviewer"] is None
        assert saved["decision_reason"] is None
        assert saved["warnings"] == []
        assert saved["context_metadata"] == {}

    def test_save_preserves_builder_fields(self, store_dir):
        record = _valid_record()
        saved = obs_queue.save_observation_record(record)
        assert saved["observation_id"] == record["observation_id"]
        assert saved["observation_type"] == "observation_record"
        assert saved["observed_at"] == record["observed_at"]
        assert saved["safety_flags"] == record["safety_flags"]

    def test_save_context_metadata(self, store_dir):
        saved = obs_queue.save_observation_record(
            _valid_record(), context={"session_id": "s1"}
        )
        assert saved["context_metadata"] == {"session_id": "s1"}

    def test_save_does_not_mutate_input_record(self, store_dir):
        record = _valid_record()
        snapshot = json.dumps(record, sort_keys=True)
        obs_queue.save_observation_record(record)
        assert json.dumps(record, sort_keys=True) == snapshot
        assert "created_at" not in record

    def test_json_round_trip_preserves_all_builder_fields(self, store_dir):
        record = _valid_record(
            observed_value={"count": 42, "tags": ["a", "b"]},
            expected_value={"count": 42},
            status="matched",
            metadata={"tolerance": 0.1},
        )
        obs_queue.save_observation_record(record)
        loaded = obs_queue.load_observation_record(record["observation_id"])
        assert loaded["observed_value"] == {"count": 42, "tags": ["a", "b"]}
        assert loaded["expected_value"] == {"count": 42}
        assert loaded["status"] == "matched"
        assert loaded["metadata"] == {"tolerance": 0.1}


class TestObservationIdValidation:
    @pytest.mark.parametrize(
        "bad_id",
        [
            "../evil",
            "..\\evil",
            "a" * 31,
            "a" * 33,
            "A" * 32,
            "g" * 32,
            "a" * 31 + "G",
            "",
            "/etc/passwd",
            "observation_record_" + "a" * 32,
        ],
    )
    def test_invalid_ids_rejected(self, store_dir, bad_id):
        with pytest.raises(ValueError):
            obs_queue.load_observation_record(bad_id)

    def test_non_string_id_rejected(self, store_dir):
        with pytest.raises(ValueError):
            obs_queue.save_observation_record(_valid_record(observation_id=123))

    def test_valid_id_accepted(self, store_dir):
        assert obs_queue.load_observation_record("0" * 32) is None


class TestRecordValidation:
    def test_non_dict_record_rejected(self, store_dir):
        with pytest.raises(ValueError):
            obs_queue.save_observation_record("not a dict")

    def test_missing_required_key_rejected(self, store_dir):
        record = _valid_record()
        del record["target"]
        with pytest.raises(ValueError, match="missing required keys"):
            obs_queue.save_observation_record(record)

    def test_invalid_observation_type_rejected(self, store_dir):
        with pytest.raises(ValueError):
            obs_queue.save_observation_record(_valid_record(observation_type="other"))

    def test_empty_target_rejected(self, store_dir):
        with pytest.raises(ValueError):
            obs_queue.save_observation_record(_valid_record(target=""))

    def test_non_dict_metadata_rejected(self, store_dir):
        with pytest.raises(ValueError):
            obs_queue.save_observation_record(_valid_record(metadata="not a dict"))

    def test_safety_flags_true_rejected(self, store_dir):
        flags = _valid_record()["safety_flags"]
        flags["tool_executed"] = True
        with pytest.raises(ValueError, match="safety_flags must all be False"):
            obs_queue.save_observation_record(_valid_record(safety_flags=flags))

    def test_non_dict_safety_flags_rejected(self, store_dir):
        with pytest.raises(ValueError):
            obs_queue.save_observation_record(_valid_record(safety_flags=[]))

    def test_non_json_serializable_record_rejected(self, store_dir):
        with pytest.raises(ValueError, match="not JSON-serializable"):
            obs_queue.save_observation_record(_valid_record(observed_value=object()))


class TestList:
    def test_list_empty(self, store_dir):
        result = obs_queue.list_observation_records()
        assert result == {"records": [], "total": 0, "limit": 50, "offset": 0}

    def test_list_multiple_records(self, store_dir):
        for i in range(3):
            obs_queue.save_observation_record(_valid_record(observation_id=f"{i:032x}"))
        result = obs_queue.list_observation_records()
        assert result["total"] == 3
        assert len(result["records"]) == 3

    def test_list_sorted_newest_first(self, store_dir):
        ids = ["a" * 32, "b" * 32, "c" * 32]
        for oid in ids:
            obs_queue.save_observation_record(_valid_record(observation_id=oid))
        timestamps = [
            "2026-07-31T10:00:00+00:00",
            "2026-08-01T10:00:00+00:00",
            "2026-08-01T12:00:00+00:00",
        ]
        for oid, ts in zip(ids, timestamps):
            _set_created_at(store_dir / f"observation_record_{oid}.json", ts)
        result = obs_queue.list_observation_records()
        assert [r["observation_id"] for r in result["records"]] == [
            "c" * 32,
            "b" * 32,
            "a" * 32,
        ]

    def test_list_status_filter(self, store_dir):
        obs_queue.save_observation_record(_valid_record(observation_id="0" * 32, status="pending"))
        obs_queue.save_observation_record(_valid_record(observation_id="1" * 32, status="matched"))
        matched = obs_queue.list_observation_records(status="matched")
        assert matched["total"] == 1
        assert matched["records"][0]["observation_id"] == "1" * 32
        pending = obs_queue.list_observation_records(status="pending")
        assert pending["total"] == 1
        none = obs_queue.list_observation_records(status="error")
        assert none["total"] == 0

    def test_list_limit(self, store_dir):
        for i in range(5):
            obs_queue.save_observation_record(_valid_record(observation_id=f"{i:032x}"))
        result = obs_queue.list_observation_records(limit=2)
        assert len(result["records"]) == 2
        assert result["total"] == 5
        assert result["limit"] == 2

    def test_list_offset(self, store_dir):
        for i in range(5):
            obs_queue.save_observation_record(_valid_record(observation_id=f"{i:032x}"))
        first = obs_queue.list_observation_records(limit=2)
        second = obs_queue.list_observation_records(limit=2, offset=2)
        assert first["records"][0]["observation_id"] != second["records"][0]["observation_id"]
        assert len(second["records"]) == 2

    def test_list_offset_beyond_total(self, store_dir):
        obs_queue.save_observation_record(_valid_record(observation_id="0" * 32))
        result = obs_queue.list_observation_records(offset=10)
        assert result["records"] == []
        assert result["total"] == 1

    @pytest.mark.parametrize(
        "limit",
        [0, -1, 201, 1.5, "5", None, True],
    )
    def test_invalid_limit_rejected(self, store_dir, limit):
        with pytest.raises(ValueError):
            obs_queue.list_observation_records(limit=limit)

    @pytest.mark.parametrize(
        "offset",
        [-1, "x", 1.5, None, True],
    )
    def test_invalid_offset_rejected(self, store_dir, offset):
        with pytest.raises(ValueError):
            obs_queue.list_observation_records(offset=offset)


class TestIsolation:
    def test_no_writes_outside_store_dir(self, store_dir, tmp_path):
        obs_queue.save_observation_record(_valid_record(observation_id="0" * 32))
        files = [p for p in tmp_path.rglob("*") if p.is_file()]
        assert files, "expected at least one saved file"
        for p in files:
            assert p.is_relative_to(store_dir), f"write escaped store dir: {p}"


class TestUpdateStatus:
    def test_update_pending_to_matched(self, store_dir):
        obs_queue.save_observation_record(_valid_record(observation_id="0" * 32))
        result = obs_queue.update_observation_record_status("0" * 32, "matched")
        assert result["status"] == "matched"
        loaded = obs_queue.load_observation_record("0" * 32)
        assert loaded["status"] == "matched"

    def test_update_sets_lifecycle_fields(self, store_dir):
        obs_queue.save_observation_record(_valid_record(observation_id="0" * 32))
        result = obs_queue.update_observation_record_status(
            "0" * 32,
            "matched",
            reviewer="human_001",
            reason="manual audit matched reason",
            context={"session_id": "s1"},
        )
        assert result["reviewer"] == "human_001"
        assert result["decision"] == "matched"
        assert result["decision_reason"] == "manual audit matched reason"
        assert result["decision"] != result["decision_reason"]
        assert result["decided_at"] is not None
        assert result["updated_at"] is not None
        assert result["context_metadata"] == {"session_id": "s1"}
        loaded = obs_queue.load_observation_record("0" * 32)
        assert loaded["status"] == "matched"
        assert loaded["decision"] == "matched"
        assert loaded["decision_reason"] == "manual audit matched reason"
        assert loaded["reviewer"] == "human_001"

    def test_update_invalid_status_raises(self, store_dir):
        with pytest.raises(ValueError, match="Invalid status"):
            obs_queue.update_observation_record_status("0" * 32, "not_a_status")

    def test_update_missing_record_returns_none(self, store_dir):
        result = obs_queue.update_observation_record_status("f" * 32, "matched")
        assert result is None

    def test_update_non_pending_returns_unchanged_record(self, store_dir):
        obs_queue.save_observation_record(_valid_record(observation_id="0" * 32, status="matched"))
        result = obs_queue.update_observation_record_status("0" * 32, "error")
        assert result["status"] == "matched"
        assert obs_queue.load_observation_record("0" * 32)["status"] == "matched"

    def test_update_non_pending_warning_in_memory_only(self, store_dir):
        obs_queue.save_observation_record(_valid_record(observation_id="0" * 32, status="error"))
        result = obs_queue.update_observation_record_status("0" * 32, "matched")
        assert any("not pending" in w for w in result.get("warnings", []))
        loaded = obs_queue.load_observation_record("0" * 32)
        assert loaded.get("warnings") in (None, [])

    def test_update_preserves_immutable_fields(self, store_dir):
        obs_queue.save_observation_record(_valid_record(observation_id="0" * 32))
        before = obs_queue.load_observation_record("0" * 32)
        after = obs_queue.update_observation_record_status("0" * 32, "matched")
        assert after["observation_id"] == before["observation_id"]
        assert after["observed_at"] == before["observed_at"]
        assert after["safety_flags"] == before["safety_flags"]
        assert after["created_at"] == before["created_at"]
        assert after["observation_type"] == "observation_record"

    def test_update_context_metadata_replaced_only_when_context_given(self, store_dir):
        obs_queue.save_observation_record(_valid_record(observation_id="0" * 32))
        obs_queue.update_observation_record_status(
            "0" * 32, "matched", context={"session_id": "s1"}
        )
        obs_queue.save_observation_record(_valid_record(observation_id="1" * 32))
        obs_queue.update_observation_record_status("1" * 32, "matched")
        first = obs_queue.load_observation_record("0" * 32)
        second = obs_queue.load_observation_record("1" * 32)
        assert first["context_metadata"] == {"session_id": "s1"}
        assert second["context_metadata"] == {}


class TestCancel:
    def test_cancel_pending_record(self, store_dir):
        obs_queue.save_observation_record(_valid_record(observation_id="0" * 32))
        result = obs_queue.cancel_observation_record(
            "0" * 32, reviewer="human_001", reason="manual audit cancel reason"
        )
        assert result["status"] == "cancelled"
        assert result["decision"] == "cancelled"
        assert result["reviewer"] == "human_001"
        assert result["decision_reason"] == "manual audit cancel reason"
        assert result["decision"] != result["decision_reason"]
        loaded = obs_queue.load_observation_record("0" * 32)
        assert loaded["status"] == "cancelled"
        assert loaded["decision"] == "cancelled"
        assert loaded["decision_reason"] == "manual audit cancel reason"
        assert loaded["reviewer"] == "human_001"
        assert loaded["decision"] != loaded["decision_reason"]

    def test_cancel_missing_record_returns_none(self, store_dir):
        result = obs_queue.cancel_observation_record("f" * 32)
        assert result is None

    def test_cancel_non_pending_unchanged(self, store_dir):
        obs_queue.save_observation_record(_valid_record(observation_id="0" * 32, status="matched"))
        result = obs_queue.cancel_observation_record("0" * 32)
        assert result["status"] == "matched"
        assert obs_queue.load_observation_record("0" * 32)["status"] == "matched"

    def test_cancel_after_update_unchanged(self, store_dir):
        obs_queue.save_observation_record(_valid_record(observation_id="0" * 32))
        obs_queue.update_observation_record_status("0" * 32, "matched")
        result = obs_queue.cancel_observation_record("0" * 32)
        assert result["status"] == "matched"
        assert obs_queue.load_observation_record("0" * 32)["status"] == "matched"

    def test_list_status_filter_cancelled(self, store_dir):
        obs_queue.save_observation_record(_valid_record(observation_id="0" * 32))
        obs_queue.save_observation_record(_valid_record(observation_id="1" * 32))
        obs_queue.cancel_observation_record("0" * 32)
        result = obs_queue.list_observation_records(status="cancelled")
        assert result["total"] == 1
        assert result["records"][0]["observation_id"] == "0" * 32


class TestNoInvocationSelfCheck:
    """Parse this file and assert it does not violate boundary rules."""

    @pytest.fixture(scope="class")
    def this_tree(self):
        path = Path(__file__)
        source = path.read_text(encoding="utf-8")
        return ast.parse(source)

    def test_no_testclient_import(self, this_tree):
        for node in ast.walk(this_tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name == "TestClient":
                        pytest.fail("Queue tests must not import TestClient")

    def test_no_endpoint_invocation_calls(self, this_tree):
        forbidden = ["client.get(", "client.post(", "client.put(", "client.delete("]
        for node in ast.walk(this_tree):
            if isinstance(node, ast.Call):
                func = ast.unparse(node.func)
                for f in forbidden:
                    if f in func:
                        pytest.fail(f"Queue tests must not call endpoints: {func}")

    def test_no_builder_or_service_calls(self, this_tree):
        forbidden = [
            "build_observation_record(",
            "handle_create_observation_record(",
            "handle_get_observation_record(",
            "handle_list_observation_records(",
            "runtime.process_chat(",
            "classify_risk(",
            "handle_awaken(",
        ]
        for node in ast.walk(this_tree):
            if isinstance(node, ast.Call):
                func = ast.unparse(node.func)
                for f in forbidden:
                    if f in func:
                        pytest.fail(f"Queue tests must not call {f}")

    def test_module_exposes_update_cancel_functions(self):
        assert hasattr(obs_queue, "update_observation_record_status")
        assert hasattr(obs_queue, "cancel_observation_record")

    def test_no_real_private_path_string(self):
        path = Path(__file__)
        source = path.read_text(encoding="utf-8")
        real_data = "/home/aether" + "/data"
        assert real_data not in source, (
            "Queue tests must not reference the real private data path"
        )
