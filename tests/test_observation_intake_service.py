"""Tests for Observation Intake Service (Milestone 84B).

Focused service tests using tmp_path/monkeypatch only. No test client, no
endpoint calls, no router/api_server invocation, and no writes to the real
private data directory. Persistence is isolated to a per-test temporary
store via the monkeypatched queue.get_observation_records_dir.
"""

from __future__ import annotations

import ast
import inspect
from pathlib import Path

import pytest

import aether.action.observation_record_queue as obs_queue
from aether.action.services import observation_intake_service as intake_service
from aether.action.services.observation_intake_service import (
    handle_observation_intake,
)

SERVICE_PATH = (
    Path(__file__).resolve().parent.parent
    / "aether" / "action" / "services" / "observation_intake_service.py"
)


def _valid_request(**overrides: object) -> dict:
    request = {
        "plan_step_id": "ps_intake_001",
        "collector_contract_id": "cc_intake_001",
        "evidence_items": [
            {
                "target": "/tmp/intake_output.txt",
                "observed_value": "line count = 42",
                "expected_value": "line count = 42",
            }
        ],
    }
    request.update(overrides)
    return request


def _valid_item(**overrides: object) -> dict:
    item = {
        "target": "/tmp/intake_output.txt",
        "observed_value": 42,
        "expected_value": 42,
    }
    item.update(overrides)
    return item


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


@pytest.fixture()
def save_counter(monkeypatch):
    """Wrap the service's save_observation_record with a call counter."""
    calls: list = []
    original_save = intake_service.save_observation_record

    def counting_save(observation_record: dict, context: dict | None = None) -> dict:
        calls.append(observation_record)
        return original_save(observation_record, context)

    monkeypatch.setattr(intake_service, "save_observation_record", counting_save)
    return calls


def _stored_record_ids(store_dir: Path) -> list:
    return sorted(p.name for p in store_dir.glob("observation_record_*.json"))


class TestModuleAndSignature:
    def test_module_imports_successfully(self):
        assert callable(handle_observation_intake)

    def test_public_function_exists(self):
        source = SERVICE_PATH.read_text(encoding="utf-8")
        assert "def handle_observation_intake" in source

    def test_signature_has_request_and_context_none(self):
        sig = inspect.signature(handle_observation_intake)
        params = list(sig.parameters.values())
        assert [p.name for p in params] == ["request", "context"]
        assert params[1].default is None

    def test_accepts_plain_dictionary(self, store_dir):
        result = handle_observation_intake(_valid_request())
        assert result["status"] == "completed"


class TestServiceImportBoundary:
    @pytest.fixture(scope="class")
    def service_tree(self):
        return ast.parse(SERVICE_PATH.read_text(encoding="utf-8"))

    def test_no_forbidden_imports(self, service_tree):
        forbidden_prefixes = (
            "aether.interface",
            "fastapi.testclient",
            "starlette.testclient",
            "re" + "quests",
            "ht" + "tpx",
            "ur" + "llib",
            "aether.action.policy_gate",
            "importl" + "ib",
        )
        for node in ast.walk(service_tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    assert not alias.name.startswith(forbidden_prefixes), alias.name
            elif isinstance(node, ast.ImportFrom):
                assert node.module is not None
                assert not node.module.startswith(forbidden_prefixes), node.module

    def test_only_allowed_aether_imports(self, service_tree):
        allowed_modules = {
            "json",
            "aether.action.observation_record",
            "aether.action.observation_record_queue",
        }
        for node in ast.walk(service_tree):
            if isinstance(node, ast.ImportFrom):
                if node.module == "__future__":
                    continue
                assert node.module in allowed_modules, node.module
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    assert alias.name in allowed_modules, alias.name

    def test_no_forbidden_module_names_in_source(self):
        source = SERVICE_PATH.read_text(encoding="utf-8")
        for forbidden in (
            "fastapi",
            "Test" + "Client",
            "clie" + "nt.",
            "get_private" + "_dir",
            ".write_" + "text(",
            ".write_" + "bytes(",
            "open(",
            "json." + "dump(",
            "__import" + "__",
            "eval(",
            "exec(",
            "sub" + "process",
            "pytest.sk" + "ip",
            "pytest.xfa" + "il",
            "/home/aether/da" + "ta",
        ):
            assert forbidden not in source, forbidden

    def test_no_route_router_runtime_calls(self, service_tree):
        forbidden_calls = (
            "include_router(",
            "app.",
            "runtime.process_chat(",
            "classify_risk(",
            "handle_awaken(",
            "root(",
            "update_observation_record_status(",
            "cancel_observation_record(",
        )
        for node in ast.walk(service_tree):
            if isinstance(node, ast.Call):
                func = ast.unparse(node.func)
                for f in forbidden_calls:
                    assert f not in func, func


class TestSuccessfulIntake:
    def test_matched_single_envelope_exact(self, store_dir):
        result = handle_observation_intake(_valid_request())
        assert set(result.keys()) == {
            "name",
            "status",
            "created",
            "observation_records",
            "errors",
        }
        assert result["name"] == "observation_intake"
        assert result["status"] == "completed"
        assert result["created"] == 1
        assert result["errors"] == []

    def test_matched_record_status_and_decision(self, store_dir):
        result = handle_observation_intake(_valid_request())
        record = result["observation_records"][0]
        assert record["status"] == "matched"
        assert record["decision"] is None
        assert record["observation_type"] == "observation_record"
        assert record["plan_step_id"] == "ps_intake_001"
        assert record["collector_contract_id"] == "cc_intake_001"

    def test_complete_store_shape_returned(self, store_dir):
        result = handle_observation_intake(_valid_request())
        record = result["observation_records"][0]
        for key in (
            "observation_id",
            "observation_type",
            "plan_step_id",
            "evidence_item_id",
            "collector_contract_id",
            "target",
            "observed_value",
            "expected_value",
            "status",
            "observed_at",
            "metadata",
            "safety_flags",
            "created_at",
            "updated_at",
            "decision",
            "decided_at",
            "reviewer",
            "decision_reason",
            "warnings",
            "context_metadata",
        ):
            assert key in record, key

    def test_returned_equals_persisted(self, store_dir):
        result = handle_observation_intake(_valid_request())
        record = result["observation_records"][0]
        loaded = obs_queue.load_observation_record(record["observation_id"])
        assert loaded == record

    def test_safety_flags_all_false(self, store_dir):
        result = handle_observation_intake(_valid_request())
        flags = result["observation_records"][0]["safety_flags"]
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

    def test_mismatched_single(self, store_dir):
        request = _valid_request(
            evidence_items=[
                _valid_item(expected_value="different")
            ]
        )
        result = handle_observation_intake(request)
        assert result["created"] == 1
        record = result["observation_records"][0]
        assert record["status"] == "mismatched"
        assert record["decision"] is None
        assert record["observed_value"] == 42
        assert record["expected_value"] == "different"

    def test_mixed_multiple_items_preserve_order(self, store_dir):
        request = _valid_request(
            evidence_items=[
                _valid_item(target="/tmp/a.txt", observed_value=1, expected_value=1),
                _valid_item(target="/tmp/b.txt", observed_value=1, expected_value=2),
                _valid_item(target="/tmp/c.txt", observed_value="x", expected_value="x"),
            ]
        )
        result = handle_observation_intake(request)
        assert result["created"] == 3
        statuses = [r["status"] for r in result["observation_records"]]
        assert statuses == ["matched", "mismatched", "matched"]
        targets = [r["target"] for r in result["observation_records"]]
        assert targets == ["/tmp/a.txt", "/tmp/b.txt", "/tmp/c.txt"]
        for record in result["observation_records"]:
            loaded = obs_queue.load_observation_record(record["observation_id"])
            assert loaded == record

    def test_evidence_item_id_and_item_metadata_mapped(self, store_dir):
        request = _valid_request(
            evidence_items=[
                _valid_item(
                    evidence_item_id="ev_intake_001",
                    metadata={"source": "manual"},
                )
            ]
        )
        record = handle_observation_intake(request)["observation_records"][0]
        assert record["evidence_item_id"] == "ev_intake_001"
        assert record["metadata"] == {"source": "manual"}

    def test_absent_item_metadata_uses_builder_default(self, store_dir):
        request = _valid_request(evidence_items=[_valid_item()])
        record = handle_observation_intake(request)["observation_records"][0]
        assert record["metadata"] == {}


class TestStrictJsonEquality:
    @pytest.mark.parametrize(
        ("observed", "expected"),
        [
            ({"a": 1, "b": 2}, {"b": 2, "a": 1}),
            ({"a": {"x": 1, "y": 2}}, {"a": {"y": 2, "x": 1}}),
            ([[1, 2], [3, 4]], [[1, 2], [3, 4]]),
            (None, None),
            ({"a": None}, {"a": None}),
            ({"a": [1, 2, {"b": True}]}, {"a": [1, 2, {"b": True}]}),
            (1.5, 1.5),
            ("same", "same"),
        ],
    )
    def test_equal_values_match(self, store_dir, observed, expected):
        request = _valid_request(
            evidence_items=[_valid_item(observed_value=observed, expected_value=expected)]
        )
        result = handle_observation_intake(request)
        assert result["observation_records"][0]["status"] == "matched"

    @pytest.mark.parametrize(
        ("observed", "expected"),
        [
            (["a", "b"], ["b", "a"]),
            ("1", 1),
            (True, 1),
            (False, 0),
            (1, 1.0),
            (1, True),
            (0, False),
            ({"a": 1}, {"a": 1.0}),
            ([1], [1.0]),
            ("1.0", 1.0),
        ],
    )
    def test_different_values_mismatch(self, store_dir, observed, expected):
        request = _valid_request(
            evidence_items=[_valid_item(observed_value=observed, expected_value=expected)]
        )
        result = handle_observation_intake(request)
        assert result["observation_records"][0]["status"] == "mismatched"

    @pytest.mark.parametrize(
        "value",
        [
            {1, 2},
            b"bytes",
            object(),
            {"nested": object()},
            [{"deep": {1, 2}}],
        ],
    )
    def test_non_serializable_values_raise_value_error(self, store_dir, value):
        request = _valid_request(
            evidence_items=[_valid_item(observed_value=value, expected_value=value)]
        )
        with pytest.raises(ValueError, match="not JSON-serializable"):
            handle_observation_intake(request)
        assert _stored_record_ids(store_dir) == []


class TestTopLevelValidation:
    def test_non_dict_request(self, store_dir):
        with pytest.raises(ValueError, match="request must be a dict"):
            handle_observation_intake("not a dict")

    def test_missing_plan_step_id(self, store_dir):
        request = _valid_request()
        del request["plan_step_id"]
        with pytest.raises(ValueError, match="plan_step_id must be a non-empty string"):
            handle_observation_intake(request)

    @pytest.mark.parametrize("plan_step_id", ["", 42, None, [], {}])
    def test_invalid_plan_step_id(self, store_dir, plan_step_id):
        with pytest.raises(ValueError, match="plan_step_id must be a non-empty string"):
            handle_observation_intake(_valid_request(plan_step_id=plan_step_id))

    def test_missing_collector_contract_id(self, store_dir):
        request = _valid_request()
        del request["collector_contract_id"]
        with pytest.raises(ValueError, match="collector_contract_id must be a non-empty string"):
            handle_observation_intake(request)

    @pytest.mark.parametrize("collector_contract_id", ["", 42, None, [], {}])
    def test_invalid_collector_contract_id(self, store_dir, collector_contract_id):
        with pytest.raises(
            ValueError, match="collector_contract_id must be a non-empty string"
        ):
            handle_observation_intake(
                _valid_request(collector_contract_id=collector_contract_id)
            )

    def test_missing_evidence_items(self, store_dir):
        request = _valid_request()
        del request["evidence_items"]
        with pytest.raises(ValueError, match="evidence_items must be a non-empty list"):
            handle_observation_intake(request)

    @pytest.mark.parametrize("evidence_items", ["items", 42, {}, ({"target": "t"},)])
    def test_invalid_evidence_items_container(self, store_dir, evidence_items):
        with pytest.raises(ValueError, match="evidence_items must be a non-empty list"):
            handle_observation_intake(_valid_request(evidence_items=evidence_items))

    def test_empty_evidence_items(self, store_dir):
        with pytest.raises(ValueError, match="evidence_items must be a non-empty list"):
            handle_observation_intake(_valid_request(evidence_items=[]))

    def test_invalid_top_level_metadata_type(self, store_dir):
        with pytest.raises(ValueError, match="metadata must be a dict or None"):
            handle_observation_intake(_valid_request(metadata="not a dict"))

    def test_non_serializable_top_level_metadata(self, store_dir):
        with pytest.raises(ValueError, match="not JSON-serializable"):
            handle_observation_intake(_valid_request(metadata={"bad": object()}))

    def test_empty_top_level_metadata_accepted(self, store_dir):
        result = handle_observation_intake(_valid_request(metadata={}))
        assert result["created"] == 1

    def test_top_level_metadata_none_accepted(self, store_dir):
        result = handle_observation_intake(_valid_request(metadata=None))
        assert result["created"] == 1


class TestEvidenceItemValidation:
    @pytest.mark.parametrize("item", ["not a dict", 42, None, ["x"]])
    def test_evidence_item_not_a_dict(self, store_dir, item):
        with pytest.raises(ValueError, match="must be a dict"):
            handle_observation_intake(_valid_request(evidence_items=[item]))

    def test_missing_target(self, store_dir):
        item = _valid_item()
        del item["target"]
        with pytest.raises(ValueError, match="target must be a non-empty string"):
            handle_observation_intake(_valid_request(evidence_items=[item]))

    @pytest.mark.parametrize("target", ["", 42, None, [], {}])
    def test_invalid_target(self, store_dir, target):
        with pytest.raises(ValueError, match="target must be a non-empty string"):
            handle_observation_intake(
                _valid_request(evidence_items=[_valid_item(target=target)])
            )

    def test_missing_observed_value(self, store_dir):
        item = _valid_item()
        del item["observed_value"]
        with pytest.raises(ValueError, match="missing required key: observed_value"):
            handle_observation_intake(_valid_request(evidence_items=[item]))

    def test_missing_expected_value(self, store_dir):
        item = _valid_item()
        del item["expected_value"]
        with pytest.raises(ValueError, match="missing required key: expected_value"):
            handle_observation_intake(_valid_request(evidence_items=[item]))

    def test_observed_value_none_is_valid(self, store_dir):
        result = handle_observation_intake(
            _valid_request(
                evidence_items=[
                    _valid_item(observed_value=None, expected_value=None)
                ]
            )
        )
        assert result["observation_records"][0]["status"] == "matched"

    @pytest.mark.parametrize("evidence_item_id", ["", 42, [], {}])
    def test_invalid_evidence_item_id(self, store_dir, evidence_item_id):
        with pytest.raises(
            ValueError, match="evidence_item_id must be a non-empty string"
        ):
            handle_observation_intake(
                _valid_request(
                    evidence_items=[_valid_item(evidence_item_id=evidence_item_id)]
                )
            )

    def test_evidence_item_id_absent_is_valid(self, store_dir):
        result = handle_observation_intake(
            _valid_request(evidence_items=[_valid_item()])
        )
        assert result["observation_records"][0]["evidence_item_id"] is None

    def test_invalid_item_metadata_type(self, store_dir):
        with pytest.raises(ValueError, match="metadata must be a dict or None"):
            handle_observation_intake(
                _valid_request(evidence_items=[_valid_item(metadata="not a dict")])
            )

    def test_non_serializable_item_metadata(self, store_dir):
        with pytest.raises(ValueError, match="not JSON-serializable"):
            handle_observation_intake(
                _valid_request(evidence_items=[_valid_item(metadata={"bad": object()})])
            )

    def test_empty_item_metadata_accepted(self, store_dir):
        result = handle_observation_intake(
            _valid_request(evidence_items=[_valid_item(metadata={})])
        )
        assert result["observation_records"][0]["metadata"] == {}


class TestForbiddenFields:
    @pytest.mark.parametrize(
        "field, value",
        [
            ("observation_id", "a" * 32),
            ("observation_type", "observation_record"),
            ("observed_at", "2026-08-01T00:00:00+00:00"),
            ("status", "matched"),
            ("created_at", "2026-08-01T00:00:00+00:00"),
            ("updated_at", "2026-08-01T00:00:00+00:00"),
            ("decision", "matched"),
            ("decided_at", "2026-08-01T00:00:00+00:00"),
            ("reviewer", "human_001"),
            ("decision_reason", "reason"),
            ("warnings", []),
            ("context_metadata", {}),
            ("new_status", "matched"),
            ("reason", "reason"),
            ("safety_flags", {}),
        ],
    )
    def test_forbidden_top_level_field_rejected(self, store_dir, save_counter, field, value):
        with pytest.raises(ValueError, match="generated/internal fields"):
            handle_observation_intake(_valid_request(**{field: value}))
        assert save_counter == []
        assert _stored_record_ids(store_dir) == []

    @pytest.mark.parametrize(
        "field, value",
        [
            ("observation_id", "a" * 32),
            ("observation_type", "observation_record"),
            ("observed_at", "2026-08-01T00:00:00+00:00"),
            ("status", "matched"),
            ("created_at", "2026-08-01T00:00:00+00:00"),
            ("updated_at", "2026-08-01T00:00:00+00:00"),
            ("decision", "matched"),
            ("decided_at", "2026-08-01T00:00:00+00:00"),
            ("reviewer", "human_001"),
            ("decision_reason", "reason"),
            ("warnings", []),
            ("context_metadata", {}),
            ("new_status", "matched"),
            ("reason", "reason"),
            ("safety_flags", {}),
        ],
    )
    def test_forbidden_item_field_rejected(self, store_dir, save_counter, field, value):
        with pytest.raises(ValueError, match="generated/internal fields"):
            handle_observation_intake(
                _valid_request(evidence_items=[_valid_item(**{field: value})])
            )
        assert save_counter == []
        assert _stored_record_ids(store_dir) == []

    def test_forbidden_names_inside_metadata_not_rejected(self, store_dir):
        result = handle_observation_intake(
            _valid_request(
                metadata={"status": "not-a-status", "decision": "x"},
                evidence_items=[
                    _valid_item(
                        metadata={"safety_flags": "ok", "observed_at": "opaque"}
                    )
                ],
            )
        )
        record = result["observation_records"][0]
        assert record["metadata"] == {"safety_flags": "ok", "observed_at": "opaque"}
        assert record["status"] == "matched"


class TestUnknownNonForbiddenFields:
    def test_unknown_top_level_field_tolerated(self, store_dir):
        result = handle_observation_intake(
            _valid_request(extra_future_field={"anything": True})
        )
        assert result["created"] == 1
        record = result["observation_records"][0]
        assert "extra_future_field" not in record

    def test_unknown_item_field_tolerated(self, store_dir):
        result = handle_observation_intake(
            _valid_request(
                evidence_items=[_valid_item(custom_future_field="ignored")]
            )
        )
        assert result["created"] == 1
        record = result["observation_records"][0]
        assert "custom_future_field" not in record

    def test_unknown_fields_not_persisted(self, store_dir):
        result = handle_observation_intake(
            _valid_request(
                future_top_level={"x": 1},
                evidence_items=[_valid_item(future_item_field=[1, 2])],
            )
        )
        record = result["observation_records"][0]
        loaded = obs_queue.load_observation_record(record["observation_id"])
        assert loaded == record
        assert "future_top_level" not in loaded
        assert "future_item_field" not in loaded

    def test_unknown_fields_do_not_affect_status_or_envelope(self, store_dir):
        result = handle_observation_intake(
            _valid_request(
                future_top_level="x",
                evidence_items=[
                    _valid_item(future_item_field="y", expected_value="different")
                ],
            )
        )
        assert result["status"] == "completed"
        assert result["created"] == 1
        assert result["errors"] == []
        assert result["observation_records"][0]["status"] == "mismatched"


class TestTopLevelMetadataPolicy:
    def test_top_level_metadata_validated(self, store_dir):
        with pytest.raises(ValueError):
            handle_observation_intake(_valid_request(metadata=["not", "dict"]))

    def test_top_level_metadata_not_copied_into_record_metadata(self, store_dir):
        result = handle_observation_intake(
            _valid_request(metadata={"top": "meta"})
        )
        record = result["observation_records"][0]
        assert record["metadata"] == {}

    def test_top_level_metadata_not_copied_into_context_metadata(self, store_dir):
        result = handle_observation_intake(
            _valid_request(metadata={"top": "meta"})
        )
        record = result["observation_records"][0]
        assert record["context_metadata"] == {}

    def test_per_item_metadata_persisted_as_record_metadata(self, store_dir):
        result = handle_observation_intake(
            _valid_request(
                metadata={"top": "meta"},
                evidence_items=[
                    _valid_item(metadata={"item": "meta"}),
                    _valid_item(target="/tmp/second.txt"),
                ],
            )
        )
        records = result["observation_records"]
        assert records[0]["metadata"] == {"item": "meta"}
        assert records[1]["metadata"] == {}

    def test_top_level_metadata_does_not_affect_matching(self, store_dir):
        result = handle_observation_intake(
            _valid_request(
                metadata={"anything": True},
                evidence_items=[
                    _valid_item(expected_value="different"),
                ],
            )
        )
        assert result["observation_records"][0]["status"] == "mismatched"


class TestContextPolicy:
    def test_context_accepted(self, store_dir):
        result = handle_observation_intake(
            _valid_request(), context={"source": "scheduler"}
        )
        assert result["status"] == "completed"

    def test_context_not_forwarded_to_queue(self, store_dir):
        result = handle_observation_intake(
            _valid_request(), context={"source": "scheduler"}
        )
        assert result["observation_records"][0]["context_metadata"] == {}

    def test_context_does_not_affect_matching(self, store_dir):
        result = handle_observation_intake(
            _valid_request(
                evidence_items=[
                    _valid_item(observed_value={"k": 1}, expected_value={"k": 1}),
                ]
            ),
            context={"observed_value": "spoof", "expected_value": "spoof"},
        )
        record = result["observation_records"][0]
        assert record["status"] == "matched"
        assert record["observed_value"] == {"k": 1}

    def test_context_does_not_affect_record_metadata(self, store_dir):
        result = handle_observation_intake(
            _valid_request(
                evidence_items=[_valid_item(metadata={"m": 1})],
            ),
            context={"metadata": "spoof"},
        )
        record = result["observation_records"][0]
        assert record["metadata"] == {"m": 1}

    def test_context_none_and_dict_equivalent_semantic_content(self, store_dir):
        without = handle_observation_intake(_valid_request())
        with_context = handle_observation_intake(
            _valid_request(), context={"k": "v"}
        )
        rec_a = without["observation_records"][0]
        rec_b = with_context["observation_records"][0]
        assert rec_a["status"] == rec_b["status"] == "matched"
        for key in (
            "plan_step_id",
            "collector_contract_id",
            "evidence_item_id",
            "target",
            "observed_value",
            "expected_value",
            "status",
            "metadata",
            "context_metadata",
        ):
            assert rec_a[key] == rec_b[key], key


class TestValidationAtomicity:
    def test_invalid_first_item_zero_saves(self, store_dir, save_counter):
        request = _valid_request(
            evidence_items=[
                _valid_item(target=""),
                _valid_item(target="/tmp/ok.txt"),
            ]
        )
        with pytest.raises(ValueError):
            handle_observation_intake(request)
        assert save_counter == []
        assert _stored_record_ids(store_dir) == []

    def test_invalid_middle_item_zero_saves(self, store_dir, save_counter):
        request = _valid_request(
            evidence_items=[
                _valid_item(target="/tmp/ok.txt"),
                _valid_item(status="matched"),
                _valid_item(target="/tmp/ok2.txt"),
            ]
        )
        with pytest.raises(ValueError, match="generated/internal fields"):
            handle_observation_intake(request)
        assert save_counter == []
        assert _stored_record_ids(store_dir) == []

    def test_invalid_final_item_zero_saves(self, store_dir, save_counter):
        request = _valid_request(
            evidence_items=[
                _valid_item(target="/tmp/ok.txt"),
                _valid_item(target=""),
            ]
        )
        with pytest.raises(ValueError):
            handle_observation_intake(request)
        assert save_counter == []
        assert _stored_record_ids(store_dir) == []

    def test_later_non_serializable_value_zero_saves(self, store_dir, save_counter):
        request = _valid_request(
            evidence_items=[
                _valid_item(target="/tmp/ok.txt"),
                _valid_item(observed_value=object()),
            ]
        )
        with pytest.raises(ValueError, match="not JSON-serializable"):
            handle_observation_intake(request)
        assert save_counter == []
        assert _stored_record_ids(store_dir) == []

    def test_builder_preparation_failure_zero_saves(self, store_dir, save_counter, monkeypatch):
        def failing_build(**kwargs):
            raise ValueError("builder preparation failure")

        monkeypatch.setattr(intake_service, "build_observation_record", failing_build)
        with pytest.raises(ValueError, match="builder preparation failure"):
            handle_observation_intake(_valid_request())
        assert save_counter == []
        assert _stored_record_ids(store_dir) == []

    def test_saves_begin_only_after_all_validation(self, store_dir, save_counter):
        result = handle_observation_intake(
            _valid_request(
                evidence_items=[
                    _valid_item(target="/tmp/ok.txt"),
                    _valid_item(target="/tmp/ok2.txt"),
                ]
            )
        )
        assert len(save_counter) == 2
        assert result["created"] == 2


class TestPersistenceFailureBehavior:
    def test_save_failure_propagates_no_completed_envelope(
        self, store_dir, monkeypatch
    ):
        def failing_save(observation_record: dict, context: dict | None = None):
            raise OSError("simulated disk failure")

        monkeypatch.setattr(intake_service, "save_observation_record", failing_save)
        with pytest.raises(OSError, match="simulated disk failure"):
            handle_observation_intake(_valid_request())

    def test_mid_persist_failure_propagates_without_cleanup(
        self, store_dir, monkeypatch
    ):
        original_save = intake_service.save_observation_record
        calls = {"count": 0}

        def flaky_save(observation_record: dict, context: dict | None = None):
            calls["count"] += 1
            if calls["count"] == 2:
                raise OSError("simulated second-save failure")
            return original_save(observation_record, context)

        monkeypatch.setattr(intake_service, "save_observation_record", flaky_save)
        request = _valid_request(
            evidence_items=[
                _valid_item(target="/tmp/first.txt"),
                _valid_item(target="/tmp/second.txt"),
            ]
        )
        with pytest.raises(OSError, match="simulated second-save failure"):
            handle_observation_intake(request)
        assert len(_stored_record_ids(store_dir)) == 1
        assert calls["count"] == 2


class TestStatusAndMilestone83Compatibility:
    def test_intake_creates_only_matched_or_mismatched(self, store_dir):
        result = handle_observation_intake(
            _valid_request(
                evidence_items=[
                    _valid_item(expected_value="different"),
                    _valid_item(),
                ]
            )
        )
        for record in result["observation_records"]:
            assert record["status"] in ("matched", "mismatched")
            assert record["status"] not in (
                "pending",
                "error",
                "cancelled",
                "completed",
            )
            assert record["decision"] is None

    def test_queue_lifecycle_decision_remains_none(self, store_dir):
        result = handle_observation_intake(_valid_request())
        record = result["observation_records"][0]
        loaded = obs_queue.load_observation_record(record["observation_id"])
        assert loaded["status"] == "matched"
        assert loaded["decision"] is None
        assert loaded["decided_at"] is None
        assert loaded["reviewer"] is None
        assert loaded["decision_reason"] is None

    def test_valid_statuses_unchanged(self):
        from aether.action.observation_record import VALID_STATUSES

        assert VALID_STATUSES == frozenset(
            {"pending", "matched", "mismatched", "error", "cancelled"}
        )

    def test_update_cancel_lifecycle_still_operates_on_pending_records(self, store_dir):
        from aether.action.services.observation_record_service import (
            handle_cancel_observation_record,
            handle_create_observation_record,
            handle_update_observation_record_status,
        )

        created = handle_create_observation_record(
            {
                "plan_step_id": "ps_83",
                "target": "/tmp/m83.txt",
                "observed_value": "v",
                "status": "pending",
            }
        )
        assert created["observation_record"]["status"] == "pending"
        updated = handle_update_observation_record_status(
            created["observation_id"],
            {"new_status": "matched", "reviewer": "human_001", "reason": "audit"},
        )
        assert updated["updated"] is True
        assert updated["observation_record"]["decision"] == "matched"
        cancelled = handle_cancel_observation_record("f" * 32)
        assert cancelled["cancelled"] is False
        assert cancelled["found"] is False


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
                    if alias.name == "Test" + "Client":
                        pytest.fail("Service tests must not import the test client")
            elif isinstance(node, ast.ImportFrom):
                if node.module in ("fastapi.testclient", "starlette.testclient"):
                    pytest.fail("Service tests must not import the test client")

    def test_no_endpoint_invocation_calls(self, this_tree):
        forbidden = [
            "clie" + "nt.get(",
            "clie" + "nt.post(",
            "clie" + "nt.put(",
            "clie" + "nt.delete(",
        ]
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
            "runtime.process_ch" + "at(",
            "classif" + "y_risk(",
            "handle_awak" + "en(",
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
