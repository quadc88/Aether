"""Focused M105B tests for rollback expected-current-state binding."""

from pathlib import Path

import pytest

from aether.action import patch_apply, patch_rollback


_UNSET = object()


@pytest.fixture
def rollback_context(monkeypatch, tmp_path):
    target = tmp_path / "target.py"
    backup_root = tmp_path / "patch_backups"
    backup_root.mkdir()
    saved = []
    events = []
    edges = []
    mutations = []
    apply_record = {}

    monkeypatch.setattr(patch_rollback, "get_patch_backup_dir", lambda: backup_root)
    monkeypatch.setattr(patch_rollback, "get_patch_apply", lambda _apply_id: apply_record)
    monkeypatch.setattr(
        patch_rollback,
        "read_restricted_file",
        lambda *_args, **_kwargs: {
            "status": "success",
            "content": target.read_text(encoding="utf-8"),
            "normalized_path": str(target),
        },
    )
    monkeypatch.setattr(patch_rollback, "load_patch_rollbacks", lambda: {"rollbacks": []})
    monkeypatch.setattr(patch_rollback, "save_patch_rollbacks", lambda data: saved.append(data))
    monkeypatch.setattr(patch_rollback, "record_event", lambda *args: events.append(args))
    monkeypatch.setattr(patch_rollback, "add_edge", lambda *args: edges.append(args))
    monkeypatch.setattr(
        patch_rollback,
        "record_patch_rollback_mutation",
        lambda record: mutations.append(record),
    )

    def prepare(current="applied text", backup="original text", expected=_UNSET):
        target.write_text(current, encoding="utf-8")
        backup_path = backup_root / "apply_backup_target.py"
        backup_path.write_text(backup, encoding="utf-8")
        apply_record.clear()
        apply_record.update(
            {
                "proposal_id": "proposal-1",
                "target_path": str(target),
                "normalized_path": str(target),
                "backup_path": str(backup_path),
                "status": "success",
                "applied": True,
                "original_hash_after": (
                    patch_rollback.sha256_text(current)
                    if expected is _UNSET
                    else expected
                ),
            }
        )
        saved.clear()
        events.clear()
        edges.clear()
        mutations.clear()
        return target, backup_path

    return prepare, saved, events, edges, mutations


def test_matching_state_allows_real_rollback(rollback_context):
    prepare, saved, _events, _edges, mutations = rollback_context
    target, _backup_path = prepare()

    result = patch_rollback.rollback_patch_apply("apply-1", dry_run=False)

    assert result["status"] == "success"
    assert result["rolled_back"] is True
    assert target.read_text(encoding="utf-8") == "original text"
    assert result["checks"][-1]["name"] == "expected_current_state"
    assert saved[-1]["rollbacks"][-1]["status"] == "success"
    assert mutations == [result]


def test_stale_state_is_rejected_before_restore(rollback_context):
    prepare, saved, _events, _edges, _mutations = rollback_context
    target, _backup_path = prepare(
        current="intervening text",
        expected=patch_rollback.sha256_text("applied text"),
    )
    original = target.read_text(encoding="utf-8")

    result = patch_rollback.rollback_patch_apply("apply-1", dry_run=False)

    assert result["status"] == "blocked"
    assert "does not match" in result["warnings"][-1]
    assert target.read_text(encoding="utf-8") == original
    assert result["pre_rollback_backup_path"] is None
    assert saved[-1]["rollbacks"][-1]["status"] == "blocked"


@pytest.mark.parametrize("expected", [None, "", "not-a-sha256", "g" * 64])
def test_missing_or_invalid_expected_hash_fails_closed(rollback_context, expected):
    prepare, saved, _events, _edges, _mutations = rollback_context
    target, _backup_path = prepare(expected=expected)
    original = target.read_text(encoding="utf-8")

    result = patch_rollback.rollback_patch_apply("apply-1", dry_run=False)

    assert result["status"] == "blocked"
    assert "no valid expected post-write hash" in result["warnings"][-1]
    assert target.read_text(encoding="utf-8") == original
    assert result["pre_rollback_backup_path"] is None
    assert saved[-1]["rollbacks"][-1]["status"] == "blocked"


def test_backup_validation_remains_enforced(rollback_context, tmp_path):
    prepare, _saved, _events, _edges, _mutations = rollback_context
    target, _backup_path = prepare()
    outside_backup = tmp_path / "outside_backup.py"
    outside_backup.write_text("original text", encoding="utf-8")
    # The expected state must not bypass the existing private backup-root rule.
    from aether.action import patch_rollback as rollback_module

    rollback_module.get_patch_apply("apply-1")["backup_path"] = str(outside_backup)

    result = rollback_module.rollback_patch_apply("apply-1", dry_run=False)

    assert result["status"] == "blocked"
    assert "backup path is not allowed" in result["warnings"][-1]
    assert target.read_text(encoding="utf-8") == "applied text"


def test_matching_state_remains_eligible_for_dry_run(rollback_context):
    prepare, _saved, _events, _edges, _mutations = rollback_context
    target, _backup_path = prepare()
    original = target.read_text(encoding="utf-8")

    result = patch_rollback.rollback_patch_apply("apply-1", dry_run=True)

    assert result["status"] == "dry_run"
    assert result["rolled_back"] is False
    assert target.read_text(encoding="utf-8") == original


def test_stale_dry_run_is_truthfully_blocked_without_write(rollback_context):
    prepare, _saved, _events, _edges, _mutations = rollback_context
    target, _backup_path = prepare(
        current="intervening text",
        expected=patch_rollback.sha256_text("applied text"),
    )
    original = target.read_text(encoding="utf-8")

    result = patch_rollback.rollback_patch_apply("apply-1", dry_run=True)

    assert result["status"] == "blocked"
    assert target.read_text(encoding="utf-8") == original
    assert result["pre_rollback_backup_path"] is None


def test_hash_uses_patch_apply_utf8_sha256_convention(rollback_context):
    prepare, _saved, _events, _edges, _mutations = rollback_context
    current = "applied é text\n"
    expected = patch_apply.sha256_text(current)
    target, _backup_path = prepare(current=current, backup="original\n", expected=expected)

    result = patch_rollback.rollback_patch_apply("apply-1", dry_run=True)

    assert result["status"] == "dry_run"
    assert result["current_hash_before"] == expected
    assert result["current_hash_before"] == patch_rollback.sha256_text(target.read_text(encoding="utf-8"))


def test_unrelated_content_change_is_detected_even_when_excerpt_would_remain(rollback_context):
    prepare, _saved, _events, _edges, _mutations = rollback_context
    target, _backup_path = prepare(
        current="prefix preserved excerpt suffix changed",
        backup="original",
        expected=patch_rollback.sha256_text("prefix preserved excerpt suffix"),
    )

    result = patch_rollback.rollback_patch_apply("apply-1", dry_run=False)

    assert result["status"] == "blocked"
    assert target.read_text(encoding="utf-8") == "prefix preserved excerpt suffix changed"


def test_success_preserves_existing_audit_and_result_behavior(rollback_context):
    prepare, _saved, events, edges, mutations = rollback_context
    prepare()

    result = patch_rollback.rollback_patch_apply("apply-1", dry_run=False)

    assert result["status"] == "success"
    assert events and events[0][0] == "patch_rollback"
    assert len(edges) == 4
    assert mutations == [result]


def test_failure_does_not_fabricate_successful_rollback_record(rollback_context):
    prepare, saved, _events, _edges, _mutations = rollback_context
    target, _backup_path = prepare(
        current="stale",
        expected=patch_rollback.sha256_text("applied text"),
    )

    result = patch_rollback.rollback_patch_apply("apply-1", dry_run=False)

    assert result["status"] == "blocked"
    assert saved[-1]["rollbacks"][-1]["rolled_back"] is False
    assert saved[-1]["rollbacks"][-1]["status"] != "success"
    assert target.read_text(encoding="utf-8") == "stale"


def test_build_does_not_add_approval_or_generic_act_semantics():
    source = Path(patch_rollback.__file__).read_text(encoding="utf-8").lower()

    assert "approval_queue" not in source
    assert "approval_id" not in source
    assert "generic act" not in source
    assert "expected_hash_after" not in source
    assert "rollback_expected_hash" not in source
