"""Focused M107B tests for the final-only reviewed-base execution guard."""

from __future__ import annotations

import ast
from pathlib import Path
from types import SimpleNamespace

import pytest

from aether.action import final_real_apply_executor as executor
from aether.action.patch_apply import sha256_text


ROOT = Path(__file__).resolve().parents[1]
TARGET = "C:/Aether/tests/guard_target.py"
NORMALIZED_TARGET = TARGET


@pytest.fixture
def readiness_env(monkeypatch):
    content = "prefix\noriginal excerpt\nsuffix\n"
    state = SimpleNamespace(
        content=content,
        access_status="success",
        dry_run={
            "id": "patch_apply_linked",
            "proposal_id": "proposal-1",
            "target_path": TARGET,
            "normalized_path": NORMALIZED_TARGET,
            "dry_run": True,
            "status": "dry_run",
            "original_hash_before": sha256_text(content),
        },
        proposal={
            "id": "proposal-1",
            "status": "approved",
            "target_path": TARGET,
            "normalized_path": NORMALIZED_TARGET,
        },
        gate={
            "id": "gate-1",
            "status": "final_approved",
            "final_decision": "approve_real_apply",
            "proposal_id": "proposal-1",
            "approval_item_id": "approval-1",
            "dry_run_patch_apply_id": "patch_apply_linked",
        },
        item={"id": "approval-1", "status": "approved"},
        dry_runs={},
        apply_calls=[],
        saved=[],
    )
    state.dry_runs[state.dry_run["id"]] = state.dry_run

    monkeypatch.setattr(
        executor,
        "get_real_apply_approval_gate_record",
        lambda _record_id: state.gate,
    )
    monkeypatch.setattr(
        executor,
        "get_patch_proposal",
        lambda _proposal_id: state.proposal,
    )
    monkeypatch.setattr(
        executor,
        "get_approval_item",
        lambda _approval_id: state.item,
    )
    monkeypatch.setattr(
        executor,
        "get_patch_apply",
        lambda apply_id: state.dry_runs.get(apply_id),
    )
    monkeypatch.setattr(executor, "normalize_path", lambda value: value)
    monkeypatch.setattr(
        executor,
        "read_restricted_file",
        lambda *_args, **_kwargs: {
            "status": state.access_status,
            "content": state.content if state.access_status == "success" else None,
        },
    )
    monkeypatch.setattr(
        executor,
        "load_final_real_apply_executor_records",
        lambda: {"records": []},
    )
    monkeypatch.setattr(executor, "_audit", lambda *_args, **_kwargs: [])
    monkeypatch.setattr(
        executor,
        "_save",
        lambda record: state.saved.append(record) or record,
    )

    def fake_apply(*_args, **_kwargs):
        state.apply_calls.append((_args, _kwargs))
        return {
            "id": "real-apply-1",
            "status": "success",
            "applied": True,
            "backup_path": "backup-1",
            "proposal_status": "approved",
            "warnings": [],
        }

    monkeypatch.setattr(executor, "apply_patch_proposal", fake_apply)
    record = {
        "id": "executor-1",
        "status": "ready",
        "real_apply_approval_gate_id": "gate-1",
        "proposal_id": None,
        "approval_item_id": None,
        "approval_item_status": None,
        "dry_run_patch_apply_id": None,
        "real_patch_apply_id": None,
        "real_apply_status": None,
        "rollback_available": False,
        "backup_created": False,
        "proposal_status": None,
        "target_path": None,
        "warnings": [],
    }
    monkeypatch.setattr(
        executor,
        "get_final_real_apply_executor_record",
        lambda _record_id: record,
    )
    return state, record


def _refresh(state, record):
    ready, warnings = executor._refresh_readiness(record)
    return ready, warnings


def test_matching_reviewed_base_preserves_existing_final_flow(readiness_env):
    state, record = readiness_env

    result = executor.execute_final_real_apply(record["id"])

    assert state.apply_calls
    assert result["status"] == "applied"
    assert result["real_patch_apply_id"] == "real-apply-1"


def test_surrounding_content_change_fails_closed_before_mutation(readiness_env):
    state, record = readiness_env
    state.content = "prefix\nchanged surrounding content\noriginal excerpt\nsuffix\n"

    result = executor.execute_final_real_apply(record["id"])

    assert result["status"] == "blocked"
    assert state.apply_calls == []
    assert result["real_patch_apply_id"] is None
    assert any("does not match" in warning for warning in result["warnings"])


def test_missing_linked_dry_run_record_fails_closed(readiness_env):
    state, record = readiness_env
    state.gate["dry_run_patch_apply_id"] = "missing-dry-run"

    ready, warnings = _refresh(state, record)

    assert not ready
    assert any("exact linked dry-run" in warning for warning in warnings)


def test_dry_run_flag_must_be_true(readiness_env):
    state, record = readiness_env
    state.dry_run["dry_run"] = 1

    ready, warnings = _refresh(state, record)

    assert not ready
    assert any("not a dry-run" in warning for warning in warnings)


def test_dry_run_status_must_be_completed_dry_run(readiness_env):
    state, record = readiness_env
    state.dry_run["status"] = "success"

    ready, warnings = _refresh(state, record)

    assert not ready
    assert any("not completed" in warning for warning in warnings)


def test_missing_original_hash_fails_closed(readiness_env):
    state, record = readiness_env
    state.dry_run.pop("original_hash_before")

    ready, warnings = _refresh(state, record)

    assert not ready
    assert any("missing or malformed" in warning for warning in warnings)


def test_empty_original_hash_fails_closed(readiness_env):
    state, record = readiness_env
    state.dry_run["original_hash_before"] = ""

    ready, warnings = _refresh(state, record)

    assert not ready
    assert any("missing or malformed" in warning for warning in warnings)


@pytest.mark.parametrize(
    "malformed_hash",
    (
        "0" * 63,
        "0" * 65,
        "g" * 64,
        "A" * 64,
    ),
)
def test_noncanonical_hash_fails_closed(readiness_env, malformed_hash):
    state, record = readiness_env
    state.dry_run["original_hash_before"] = malformed_hash

    ready, warnings = _refresh(state, record)

    assert not ready
    assert any("missing or malformed" in warning for warning in warnings)


def test_dry_run_and_final_targets_must_match(readiness_env):
    state, record = readiness_env
    state.dry_run["normalized_path"] = "C:/Aether/tests/other_target.py"

    ready, warnings = _refresh(state, record)

    assert not ready
    assert any("does not match" in warning for warning in warnings)


def test_unreadable_current_target_fails_closed(readiness_env):
    state, record = readiness_env
    state.access_status = "blocked"

    ready, warnings = _refresh(state, record)

    assert not ready
    assert any("could not be read safely" in warning for warning in warnings)


def test_hash_mismatch_never_dispatches_real_mutation(readiness_env):
    state, record = readiness_env
    state.content = "a different current target\n"

    result = executor.execute_final_real_apply(record["id"])

    assert state.apply_calls == []
    assert result["status"] == "blocked"
    assert result["real_apply_status"] is None


def test_guard_failure_emits_no_successful_apply_record(readiness_env):
    state, record = readiness_env
    state.content = "stale\n"

    result = executor.execute_final_real_apply(record["id"])

    assert state.apply_calls == []
    assert result["real_patch_apply_id"] is None
    assert result["status"] != "applied"


def test_exact_linked_record_wins_when_multiple_dry_runs_exist(readiness_env):
    state, record = readiness_env
    newer = dict(state.dry_run)
    newer.update(
        id="patch_apply_newer",
        original_hash_before=sha256_text("newer content\n"),
    )
    state.dry_runs["patch_apply_newer"] = newer
    state.gate["dry_run_patch_apply_id"] = "patch_apply_linked"

    ready, warnings = _refresh(state, record)

    assert ready
    assert warnings == []


def test_byte_identical_restoration_passes_current_state_guard(readiness_env):
    state, record = readiness_env
    state.content = "changed temporarily\n"
    state.content = "prefix\noriginal excerpt\nsuffix\n"

    ready, warnings = _refresh(state, record)

    assert ready
    assert warnings == []


def test_excerpt_only_success_cannot_bypass_reviewed_base_mismatch(readiness_env):
    state, record = readiness_env
    state.content = "changed\noriginal excerpt\n"

    result = executor.execute_final_real_apply(record["id"])

    assert state.apply_calls == []
    assert result["status"] == "blocked"


def test_existing_approval_status_is_consumed_without_new_approval_semantics(
    readiness_env,
):
    state, record = readiness_env
    state.item["status"] = "pending"

    ready, warnings = _refresh(state, record)

    assert not ready
    assert any("approval queue item" in warning for warning in warnings)
    assert "approval_item_id" in record


def test_direct_patch_apply_has_no_final_executor_dependency():
    source = (ROOT / "aether/action/patch_apply.py").read_text(encoding="utf-8")

    assert "final_real_apply_executor" not in source
    assert "apply_patch_proposal" in source
    assert "dry_run" in source


def test_rollback_expected_state_contract_remains_present():
    source = (ROOT / "aether/action/patch_rollback.py").read_text(encoding="utf-8")

    assert "original_hash_after" in source
    assert "final_real_apply_executor" not in source


def test_no_new_persistence_or_generic_act_semantics_are_introduced():
    source = (ROOT / "aether/action/final_real_apply_executor.py").read_text(
        encoding="utf-8"
    )
    tree = ast.parse(source)
    imported_modules = {
        node.module
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom)
    }

    assert "aether.action.generic_act" not in imported_modules
    assert "reviewed_base_hash" not in source
    assert "schema_version" not in source
