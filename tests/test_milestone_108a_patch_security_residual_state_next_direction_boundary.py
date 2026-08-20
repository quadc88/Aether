"""Static/document lock for the read-only M108A next-direction boundary."""

import ast
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DESIGN = ROOT / (
    "docs/architecture/"
    "MILESTONE_108A_PATCH_SECURITY_RESIDUAL_STATE_NEXT_DIRECTION_BOUNDARY.md"
)


def _design() -> str:
    return DESIGN.read_text(encoding="utf-8")


def test_m105b_m107b_and_f02_split_are_locked():
    text = _design()
    for phrase in (
        "F03: RESOLVED / CLOSED BY M105B",
        "F02_FINAL_WORKFLOW: ADDRESSED",
        "F02_DIRECT_PATH: HIGH / UNRESOLVED",
        "Universal F02: NOT RESOLVED",
        "Patch-security stopping point reached: YES",
    ):
        assert phrase in text


def test_remaining_severity_and_dispositions_are_locked():
    text = _design()
    for phrase in (
        "F01 direct authority divergence",
        "F04 mutation/write-record atomicity",
        "F05 reusable direct approval",
        "F06 final executor concurrency",
        "F07 audit/verification split",
        "BLOCKED_BY_CANONICAL_POLICY",
        "TOO_BROAD_CURRENTLY",
        "MONITOR",
    ):
        assert phrase in text


def test_selected_direction_and_principal_decision_are_exactly_locked():
    text = _design()
    assert (
        "MODEL_B_PATCH_SECURITY_PAUSE_RETURN_TO_CORE_ARCHITECTURE" in text
    )
    assert "B_PATCH_SECURITY_STABLE_ENOUGH_RETURN_TO_CORE" in text
    assert "GOAL_TO_PLAN_RUNTIME_CONSUMER_PROOF" in text
    assert "Next milestone type: CONSUMER_PROOF" in text
    assert "Next Build: NOT JUSTIFIED" in text


def test_generic_act_non_authorization_is_locked():
    text = _design()
    assert "Generic Act: NOT_IMPLEMENTED" in text
    assert "Generic Act integration: NOT_AUTHORIZED" in text
    assert "Generic Act authority: NOT_GRANTED" in text
    assert "Canonical patch authority: NOT PROVEN" in text


def test_static_lock_has_no_production_imports_or_mutation_calls():
    source = Path(__file__).read_text(encoding="utf-8")
    tree = ast.parse(source)
    imported_modules = {
        node.module
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom)
    }
    imported_names = {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    }
    assert not any(module and module.startswith("aether") for module in imported_modules)
    assert "aether" not in imported_names
    assert "TestClient" not in imported_names

    called_names = {
        node.func.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    }
    assert not called_names.intersection(
        {
            "write_text",
            "write_bytes",
            "unlink",
            "apply_patch_proposal",
            "rollback_patch_apply",
            "execute_final_real_apply",
            "save_patch_applies",
            "save_patch_rollbacks",
        }
    )


def test_m108a_explicitly_preserves_read_only_scope():
    text = _design()
    for phrase in (
        "does not implement a patch security fix",
        "modify patch runtime",
        "modify patch apply",
        "No `PROGRESS.md`",
        "M108A does not:",
        "commit, tag, push",
        "M108A itself authorizes no implementation",
    ):
        assert phrase in text
