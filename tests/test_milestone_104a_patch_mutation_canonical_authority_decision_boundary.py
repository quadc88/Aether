"""Static/document lock for the read-only M104A authority decision."""

import ast
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DESIGN = ROOT / (
    "docs/architecture/"
    "MILESTONE_104A_PATCH_MUTATION_CANONICAL_AUTHORITY_DECISION_BOUNDARY.md"
)


def _design() -> str:
    return DESIGN.read_text(encoding="utf-8")


def test_selected_model_and_readiness_are_locked():
    text = _design()
    assert "MODEL_F_NO_CANONICAL_AUTHORITY_DECISION_YET" in text
    assert "D_NO_CANONICAL_MODEL_PROVEN" in text
    assert "Canonical mutation authority proven: NO" in text
    assert "Future patch authority Build: NOT JUSTIFIED / NOT AUTHORIZED" in text


def test_authority_source_of_truth_conclusion_is_locked():
    text = _design()
    assert "no single record is the source of truth for all real mutation" in text
    assert "A single\nuniversal canonical mutation authority is **NOT PROVEN**" in text
    assert "direct patch and self-modification routes remain live production callers" in text
    assert "final-real-apply is a canonical stronger workflow" not in text


def test_key_non_goals_are_locked():
    text = _design()
    for phrase in (
        "patch apply, patch rollback,\nfinal-real-apply",
        "approval semantics, routes, transactional behavior",
        "disable, quarantine, or migrate direct patch routes",
        "transactional mutation behavior",
        "redesign rollback",
        "implement Generic Act",
        "No M104B or M105 is authorized.",
    ):
        assert phrase in text


def test_generic_act_non_authorization_is_locked():
    text = _design()
    assert "Generic Act: NOT_IMPLEMENTED / NOT_AUTHORIZED / NOT_GRANTED" in text
    assert "No Generic Act dependency is needed" in text


def test_static_lock_has_no_runtime_or_mutation_imports_or_calls():
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
        {"write_text", "write_bytes", "unlink", "apply_patch_proposal", "rollback_patch_apply"}
    )
