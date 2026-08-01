"""Tests for Observation Record Service (Milestone 83C).

Focused service tests using tmp_path/monkeypatch only. No TestClient, no
endpoint calls, no router/api_server invocation, and no writes to the real
private data directory.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

import aether.action.observation_record_queue as obs_queue
from aether.action.services.observation_record_service import (
    handle_cancel_observation_record,
    handle_create_observation_record,
    handle_get_observation_record,
    handle_list_observation_records,
    handle_update_observation_record_status,
)


def _valid_request(**overrides: object) -> dict:
    request = {
        "plan_step_id": "ps_001",
        "target": "/tmp/test_output.txt",
        "observed_value": "line count = 42",
        "status": "pending",
    }
    request.update(overrides)
    return request


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


class TestCreate:
    def test_create_valid_request(self, store_dir):
        result = handle_create_observation_record(_valid_request())
        assert result["name"] == "Aether"
        assert "status" in result
        assert result["created"] is True
        assert result["observation_id"]
        assert isinstance(result["observation_record"], dict)

    def test_created_record_persisted_in_queue(self, store_dir):
        result = handle_create_observation_record(_valid_request())
        loaded = obs_queue.load_observation_record(result["observation_id"])
        assert loaded == result["observation_record"]

    def test_safety_flags_all_false(self, store_dir):
        result = handle_create_observation_record(_valid_request())
        flags = result["observation_record"]["safety_flags"]
        assert set(flags.keys()) == {
            "tool_execution_allowed",
            "tool_executed",
            "evidence_collection_performed",
            "system_state_modified",
            "apply_performed",
            "rollback_performed",
            "persistent_write_performed",
            "external_side_effect_performed",
        }
        assert all(v is False for v in flags.values())

    def test_builder_generated_fields_present(self, store_dir):
        result = handle_create_observation_record(_valid_request())
        record = result["observation_record"]
        assert record["observation_id"] == result["observation_id"]
        assert record["observation_type"] == "observation_record"
        assert "T" in record["observed_at"]
        assert isinstance(record["safety_flags"], dict)

    def test_create_with_all_fields(self, store_dir):
        result = handle_create_observation_record(
            _valid_request(
                evidence_item_id="ev_001",
                observed_value={"count": 7},
                expected_value={"count": 7},
                status="matched",
                collector_contract_id="cc_001",
                metadata={"source": "manual"},
            )
        )
        record = result["observation_record"]
        assert record["evidence_item_id"] == "ev_001"
        assert record["observed_value"] == {"count": 7}
        assert record["expected_value"] == {"count": 7}
        assert record["status"] == "matched"
        assert record["collector_contract_id"] == "cc_001"
        assert record["metadata"] == {"source": "manual"}

    def test_default_status_pending(self, store_dir):
        result = handle_create_observation_record(
            _valid_request(status="pending")
        )
        assert result["observation_record"]["status"] == "pending"

    def test_reject_user_supplied_observation_id(self, store_dir):
        with pytest.raises(ValueError, match="generated/internal fields"):
            handle_create_observation_record(_valid_request(observation_id="a" * 32))

    def test_reject_user_supplied_observation_type(self, store_dir):
        with pytest.raises(ValueError, match="generated/internal fields"):
            handle_create_observation_record(
                _valid_request(observation_type="observation_record")
            )

    def test_reject_user_supplied_observed_at(self, store_dir):
        with pytest.raises(ValueError, match="generated/internal fields"):
            handle_create_observation_record(
                _valid_request(observed_at="2026-07-31T12:00:00+00:00")
            )

    def test_reject_user_supplied_safety_flags(self, store_dir):
        with pytest.raises(ValueError, match="generated/internal fields"):
            handle_create_observation_record(_valid_request(safety_flags={}))

    def test_reject_non_dict_request(self, store_dir):
        with pytest.raises(ValueError, match="request must be a dict"):
            handle_create_observation_record("not a dict")

    def test_reject_empty_target(self, store_dir):
        with pytest.raises(ValueError, match="target must be a non-empty string"):
            handle_create_observation_record(_valid_request(target=""))

    def test_reject_non_string_target(self, store_dir):
        with pytest.raises(ValueError, match="target must be a non-empty string"):
            handle_create_observation_record(_valid_request(target=42))

    def test_reject_missing_both_ids(self, store_dir):
        with pytest.raises(ValueError, match="plan_step_id or evidence_item_id"):
            handle_create_observation_record(_valid_request(plan_step_id=None))

    def test_reject_invalid_status(self, store_dir):
        with pytest.raises(ValueError, match="Invalid status"):
            handle_create_observation_record(_valid_request(status="invalid_status"))

    def test_reject_non_dict_metadata(self, store_dir):
        with pytest.raises(ValueError, match="metadata must be a dict or None"):
            handle_create_observation_record(_valid_request(metadata="not a dict"))

    def test_reject_non_json_serializable_observed_value(self, store_dir):
        with pytest.raises(ValueError, match="not JSON-serializable"):
            handle_create_observation_record(_valid_request(observed_value=object()))

    def test_reject_non_json_serializable_expected_value(self, store_dir):
        with pytest.raises(ValueError, match="not JSON-serializable"):
            handle_create_observation_record(_valid_request(expected_value=object()))


class TestGet:
    def test_get_found(self, store_dir):
        created = handle_create_observation_record(_valid_request())
        result = handle_get_observation_record(created["observation_id"])
        assert result["found"] is True
        assert result["observation_record"]["observation_id"] == created["observation_id"]
        assert result["name"] == "Aether"

    def test_get_missing(self, store_dir):
        result = handle_get_observation_record("f" * 32)
        assert result["found"] is False
        assert result["observation_record"] is None


class TestList:
    def test_list_empty(self, store_dir):
        result = handle_list_observation_records()
        assert result["observation_records"] == []
        assert result["count"] == 0
        assert result["total"] == 0
        assert result["limit"] == 50
        assert result["offset"] == 0

    def test_list_multiple(self, store_dir):
        handle_create_observation_record(_valid_request(plan_step_id="ps_001"))
        handle_create_observation_record(_valid_request(plan_step_id="ps_002"))
        result = handle_list_observation_records()
        assert result["count"] == 2
        assert result["total"] == 2

    def test_list_status_filter(self, store_dir):
        handle_create_observation_record(_valid_request(plan_step_id="ps_001", status="pending"))
        handle_create_observation_record(
            _valid_request(plan_step_id="ps_002", status="matched")
        )
        matched = handle_list_observation_records(status="matched")
        assert matched["total"] == 1
        assert matched["observation_records"][0]["status"] == "matched"

    def test_list_limit(self, store_dir):
        for i in range(4):
            handle_create_observation_record(_valid_request(plan_step_id=f"ps_{i}"))
        result = handle_list_observation_records(limit=2)
        assert result["count"] == 2
        assert result["total"] == 4

    def test_list_offset(self, store_dir):
        for i in range(4):
            handle_create_observation_record(_valid_request(plan_step_id=f"ps_{i}"))
        first = handle_list_observation_records(limit=2)
        second = handle_list_observation_records(limit=2, offset=2)
        first_ids = {r["observation_id"] for r in first["observation_records"]}
        second_ids = {r["observation_id"] for r in second["observation_records"]}
        assert first_ids.isdisjoint(second_ids)

    @pytest.mark.parametrize("limit", [0, -1, 201, 1.5, "5", True])
    def test_invalid_limit_rejected(self, store_dir, limit):
        with pytest.raises(ValueError):
            handle_list_observation_records(limit=limit)

    @pytest.mark.parametrize("offset", [-1, "x", 1.5, True])
    def test_invalid_offset_rejected(self, store_dir, offset):
        with pytest.raises(ValueError):
            handle_list_observation_records(offset=offset)


class TestScope:
    def test_update_cancel_functions_in_service_module(self):
        service_path = (
            Path(__file__).resolve().parent.parent
            / "aether" / "action" / "services" / "observation_record_service.py"
        )
        source = service_path.read_text(encoding="utf-8")
        assert "def handle_create_observation_record" in source
        assert "def handle_get_observation_record" in source
        assert "def handle_list_observation_records" in source
        assert "def handle_update_observation_record_status" in source
        assert "def handle_cancel_observation_record" in source


class TestUpdateStatusService:
    def test_update_status_valid(self, store_dir):
        created = handle_create_observation_record(_valid_request())
        result = handle_update_observation_record_status(
            created["observation_id"],
            {
                "new_status": "matched",
                "reviewer": "human_001",
                "reason": "manual audit matched reason",
            },
        )
        assert result["found"] is True
        assert result["updated"] is True
        assert result["observation_record"]["status"] == "matched"
        assert result["observation_record"]["decision"] == "matched"
        assert result["observation_record"]["decision_reason"] == "manual audit matched reason"
        assert result["observation_record"]["decision"] != result["observation_record"]["decision_reason"]
        assert result["name"] == "Aether"

    def test_update_status_persisted(self, store_dir):
        created = handle_create_observation_record(_valid_request())
        handle_update_observation_record_status(
            created["observation_id"],
            {
                "new_status": "error",
                "reviewer": "system",
                "reason": "manual audit error reason",
            },
        )
        loaded = obs_queue.load_observation_record(created["observation_id"])
        assert loaded["status"] == "error"
        assert loaded["decision"] == "error"
        assert loaded["decision_reason"] == "manual audit error reason"
        assert loaded["reviewer"] == "system"

    def test_update_status_not_found(self, store_dir):
        result = handle_update_observation_record_status("f" * 32, {"new_status": "matched"})
        assert result["found"] is False
        assert result["updated"] is False
        assert result["observation_record"] is None

    def test_update_status_invalid_new_status_raises(self, store_dir):
        created = handle_create_observation_record(_valid_request())
        with pytest.raises(ValueError, match="Invalid status"):
            handle_update_observation_record_status(
                created["observation_id"], {"new_status": "not_a_status"}
            )

    def test_update_status_non_pending_not_updated(self, store_dir):
        created = handle_create_observation_record(
            _valid_request(status="matched")
        )
        result = handle_update_observation_record_status(
            created["observation_id"], {"new_status": "error"}
        )
        assert result["found"] is True
        assert result["updated"] is False
        assert result["observation_record"]["status"] == "matched"

    def test_update_status_reject_non_dict_request(self, store_dir):
        created = handle_create_observation_record(_valid_request())
        with pytest.raises(ValueError, match="request must be a dict"):
            handle_update_observation_record_status(created["observation_id"], "x")

    def test_update_status_reject_non_string_reviewer(self, store_dir):
        created = handle_create_observation_record(_valid_request())
        with pytest.raises(ValueError, match="reviewer must be a string"):
            handle_update_observation_record_status(
                created["observation_id"], {"new_status": "matched", "reviewer": 7}
            )

    def test_update_status_reject_non_string_reason(self, store_dir):
        created = handle_create_observation_record(_valid_request())
        with pytest.raises(ValueError, match="reason must be a string"):
            handle_update_observation_record_status(
                created["observation_id"], {"new_status": "matched", "reason": []}
            )


class TestCancelService:
    def test_cancel_valid(self, store_dir):
        created = handle_create_observation_record(_valid_request())
        result = handle_cancel_observation_record(
            created["observation_id"],
            {"reviewer": "human_001", "reason": "manual audit cancel reason"},
        )
        assert result["found"] is True
        assert result["cancelled"] is True
        assert result["observation_record"]["status"] == "cancelled"
        assert result["observation_record"]["decision"] == "cancelled"
        assert result["observation_record"]["decision_reason"] == "manual audit cancel reason"
        assert result["observation_record"]["decision"] != result["observation_record"]["decision_reason"]
        assert result["name"] == "Aether"

    def test_cancel_persisted(self, store_dir):
        created = handle_create_observation_record(_valid_request())
        handle_cancel_observation_record(
            created["observation_id"],
            {"reviewer": "human_001", "reason": "manual audit cancel reason"},
        )
        loaded = obs_queue.load_observation_record(created["observation_id"])
        assert loaded["status"] == "cancelled"
        assert loaded["decision"] == "cancelled"
        assert loaded["decision_reason"] == "manual audit cancel reason"
        assert loaded["reviewer"] == "human_001"
        assert loaded["decision"] != loaded["decision_reason"]

    def test_cancel_not_found(self, store_dir):
        result = handle_cancel_observation_record("f" * 32)
        assert result["found"] is False
        assert result["cancelled"] is False
        assert result["observation_record"] is None

    def test_cancel_requires_no_request(self, store_dir):
        created = handle_create_observation_record(_valid_request())
        result = handle_cancel_observation_record(created["observation_id"])
        assert result["cancelled"] is True

    def test_cancel_non_pending_not_cancelled(self, store_dir):
        created = handle_create_observation_record(_valid_request(status="error"))
        result = handle_cancel_observation_record(created["observation_id"])
        assert result["found"] is True
        assert result["cancelled"] is False
        assert result["observation_record"]["status"] == "error"

    def test_cancel_reject_non_dict_request(self, store_dir):
        created = handle_create_observation_record(_valid_request())
        with pytest.raises(ValueError, match="request must be a dict"):
            handle_cancel_observation_record(created["observation_id"], "x")


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
                        pytest.fail("Service tests must not import TestClient")

    def test_no_endpoint_invocation_calls(self, this_tree):
        forbidden = ["client.get(", "client.post(", "client.put(", "client.delete("]
        for node in ast.walk(this_tree):
            if isinstance(node, ast.Call):
                func = ast.unparse(node.func)
                for f in forbidden:
                    if f in func:
                        pytest.fail(f"Service tests must not call endpoints: {func}")

    def test_no_route_router_api_server_calls(self, this_tree):
        forbidden = [
            "include_router(",
            "app.",
            "runtime.process_chat(",
            "classify_risk(",
            "handle_awaken(",
            "root(",
        ]
        for node in ast.walk(this_tree):
            if isinstance(node, ast.Call):
                func = ast.unparse(node.func)
                for f in forbidden:
                    if f in func:
                        pytest.fail(f"Service tests must not call {f}")

    def test_no_real_private_path_string(self):
        path = Path(__file__)
        source = path.read_text(encoding="utf-8")
        real_data = "/home/aether" + "/data"
        assert real_data not in source, (
            "Service tests must not reference the real private data path"
        )
