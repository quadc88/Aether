"""Static/document lock for the read-only M105A selection boundary."""

import ast
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DESIGN = ROOT / (
    "docs/architecture/"
    "MILESTONE_105A_PATCH_MUTATION_INDEPENDENT_SECURITY_FIX_SELECTION_BOUNDARY.md"
)


def _design() -> str:
    return DESIGN.read_text(encoding="utf-8")


def test_decision_candidate_and_model_are_locked():
    text = _design()
    assert "A_INDEPENDENT_PATCH_SECURITY_BUILD_JUSTIFIED" in text
    assert "CAND_E_ROLLBACK_STALE_REPLAY_PROTECTION" in text
    assert "MODEL_E_ROLLBACK_EXPECTED_STATE_BINDING" in text
    assert "Future Build: JUSTIFIED FOR PM REVIEW" in text


def test_independence_requirement_is_locked():
    text = _design()
    assert "Canonical-route decision required: NO" in text
    assert "F03 only" in text
    assert "It does\nnot decide whether the apply came" in text
    assert "add a new persisted field" in text


def test_non_goals_are_locked():
    text = _design()
    for phrase in (
        "does not modify patch apply",
        "modify direct patch apply or final-real-apply",
        "choose a canonical patch mutation route",
        "change approval semantics or approval consumption",
        "add transactional mutation logic",
        "redesign rollback",
        "implement Generic Act",
        "No implementation is authorized by M105A.",
        "No M105B or M106 is authorized.",
    ):
        assert phrase in text


def test_generic_act_non_authorization_is_locked():
    text = _design()
    assert "Generic Act: NOT_IMPLEMENTED / NOT_AUTHORIZED / NOT_GRANTED" in text
    assert "Do NOT reuse `RestrictedReadAuthorityBinding`" not in text
    assert "reuse `RestrictedReadAuthorityBinding`, `RestrictedReadScope`" in text


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
        {"write_text", "write_bytes", "unlink", "apply_patch_proposal", "rollback_patch_apply"}
    )
