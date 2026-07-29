"""Tests for Observation Record Builder (Milestone 82B)."""

from __future__ import annotations

import copy
import json

import pytest

from aether.action.observation_record import build_observation_record, VALID_STATUSES


VALID_STATUS_SAMPLE = ("pending", "matched", "mismatched", "error")


def _default_kwargs(**overrides: object) -> dict:
    kwargs = {
        "plan_step_id": "ps_001",
        "target": "/tmp/test_output.txt",
    }
    kwargs.update(overrides)
    return kwargs


def test_both_ids_missing_raises_value_error():
    with pytest.raises(ValueError, match="plan_step_id or evidence_item_id"):
        build_observation_record(target="/tmp/x")


def test_empty_target_raises_value_error():
    with pytest.raises(ValueError, match="target must be a non-empty string"):
        build_observation_record(plan_step_id="ps_001", target="")


def test_target_must_be_string():
    with pytest.raises(ValueError, match="target must be a non-empty string"):
        build_observation_record(plan_step_id="ps_001", target=42)


def test_invalid_status_raises_value_error():
    with pytest.raises(ValueError, match="Invalid status.*invalid_status"):
        build_observation_record(**_default_kwargs(status="invalid_status"))


def test_all_valid_statuses_accepted():
    for s in VALID_STATUS_SAMPLE:
        rec = build_observation_record(**_default_kwargs(status=s))
        assert rec["status"] == s


def test_default_status_is_pending():
    rec = build_observation_record(**_default_kwargs())
    assert rec["status"] == "pending"


def test_non_dict_metadata_raises_value_error():
    with pytest.raises(ValueError, match="metadata must be a dict or None"):
        build_observation_record(**_default_kwargs(metadata="not_a_dict"))


def test_non_serializable_observed_value_raises_value_error():
    with pytest.raises(ValueError, match="not JSON-serializable"):
        build_observation_record(**_default_kwargs(observed_value=object()))


def test_non_serializable_expected_value_raises_value_error():
    with pytest.raises(ValueError, match="not JSON-serializable"):
        build_observation_record(**_default_kwargs(expected_value=object()))


def test_non_serializable_metadata_value_raises_value_error():
    with pytest.raises(ValueError, match="not JSON-serializable"):
        build_observation_record(**_default_kwargs(metadata={"bad": object()}))


def test_minimal_with_plan_step_id():
    rec = build_observation_record(plan_step_id="ps_001", target="/tmp/x")
    assert rec["plan_step_id"] == "ps_001"
    assert rec["evidence_item_id"] is None
    assert rec["target"] == "/tmp/x"


def test_minimal_with_evidence_item_id():
    rec = build_observation_record(evidence_item_id="ev_001", target="/tmp/x")
    assert rec["evidence_item_id"] == "ev_001"
    assert rec["plan_step_id"] is None


def test_both_ids_provided():
    rec = build_observation_record(
        plan_step_id="ps_001", evidence_item_id="ev_001", target="/tmp/x"
    )
    assert rec["plan_step_id"] == "ps_001"
    assert rec["evidence_item_id"] == "ev_001"


def test_all_fields_populated():
    rec = build_observation_record(
        plan_step_id="ps_001",
        evidence_item_id="ev_001",
        collector_contract_id="cc_001",
        target="/tmp/test_output.txt",
        observed_value="line count = 42",
        expected_value="line count = 42",
        status="matched",
        metadata={"source": "manual", "tolerance": 0.1},
    )
    assert rec["plan_step_id"] == "ps_001"
    assert rec["evidence_item_id"] == "ev_001"
    assert rec["collector_contract_id"] == "cc_001"
    assert rec["target"] == "/tmp/test_output.txt"
    assert rec["observed_value"] == "line count = 42"
    assert rec["expected_value"] == "line count = 42"
    assert rec["status"] == "matched"
    assert rec["metadata"] == {"source": "manual", "tolerance": 0.1}


def test_returns_dict_with_observation_id():
    rec = build_observation_record(**_default_kwargs())
    assert isinstance(rec["observation_id"], str)
    assert len(rec["observation_id"]) > 0


def test_observation_type_is_observation_record():
    rec = build_observation_record(**_default_kwargs())
    assert rec["observation_type"] == "observation_record"


def test_observed_at_is_iso_timestamp():
    rec = build_observation_record(**_default_kwargs())
    assert "T" in rec["observed_at"]
    assert rec["observed_at"].endswith("+00:00") or "+" in rec["observed_at"]


def test_observed_value_defaults_to_none():
    rec = build_observation_record(**_default_kwargs())
    assert rec["observed_value"] is None


def test_expected_value_defaults_to_none():
    rec = build_observation_record(**_default_kwargs())
    assert rec["expected_value"] is None


def test_collector_contract_id_defaults_to_none():
    rec = build_observation_record(**_default_kwargs())
    assert rec["collector_contract_id"] is None


def test_metadata_defaults_to_empty_dict():
    rec = build_observation_record(**_default_kwargs())
    assert rec["metadata"] == {}


def test_safety_flags_all_false():
    rec = build_observation_record(**_default_kwargs())
    sf = rec["safety_flags"]
    assert sf["tool_execution_allowed"] is False
    assert sf["tool_executed"] is False
    assert sf["evidence_collection_performed"] is False
    assert sf["system_state_modified"] is False
    assert sf["apply_performed"] is False
    assert sf["rollback_performed"] is False
    assert sf["persistent_write_performed"] is False
    assert sf["external_side_effect_performed"] is False


def test_safety_flags_have_exactly_eight_keys():
    rec = build_observation_record(**_default_kwargs())
    assert len(rec["safety_flags"]) == 8


def test_observation_ids_are_unique():
    ids = {build_observation_record(**_default_kwargs())["observation_id"] for _ in range(100)}
    assert len(ids) == 100


def test_record_is_json_serializable():
    rec = build_observation_record(
        plan_step_id="ps_001",
        target="/tmp/x",
        observed_value=42,
        expected_value=42,
        status="matched",
        metadata={"tags": ["a", "b"]},
    )
    dumped = json.dumps(rec)
    assert isinstance(dumped, str)
    loaded = json.loads(dumped)
    assert loaded["target"] == "/tmp/x"


def test_mutating_returned_dict_does_not_affect_builder():
    rec1 = build_observation_record(**_default_kwargs())
    rec2 = build_observation_record(**_default_kwargs())
    rec1["target"] = "mutated"
    assert rec2["target"] == "/tmp/test_output.txt"
