"""Static/document lock for the read-only M106A priority boundary."""

import ast
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DESIGN = ROOT / (
    "docs/architecture/"
    "MILESTONE_106A_REMAINING_PATCH_HIGH_RISK_FIX_PRIORITY_BOUNDARY.md"
)


def _design() -> str:
    return DESIGN.read_text(encoding="utf-8")


def test_decision_selection_and_m105b_closure_are_locked():
    text = _design()
    assert "E_NO_NEXT_INDEPENDENT_HIGH_FIX_PROVEN" in text
    assert "Selected finding: NONE" in text
    assert "MODEL_F_NO_NEXT_INDEPENDENT_BUILD" in text
    assert "M105B F03: CLOSED / RESOLVED" in text
    assert "F03 is CLOSED." in text


def test_generic_act_non_authorization_is_locked():
    text = _design()
    assert "Generic Act: NOT_IMPLEMENTED / NOT_AUTHORIZED / NOT_GRANTED" in text
    assert "Canonical patch route: NOT SELECTED / NOT PROVEN" in text


def test_key_non_goals_are_locked():
    text = _design()
    for phrase in (
        "implement a security fix",
        "modify patch runtime",
        "choose a canonical patch route",
        "change approval semantics",
        "add transactional mutation behavior",
        "reopen F03",
        "Do not implement F01, F02, F04, F05, F06, or F07",
        "No M106B or M107 is authorized.",
    ):
        assert phrase in text


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
        }
    )
