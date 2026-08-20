"""Static/document lock for the read-only M103A security review."""

import ast
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DESIGN = ROOT / (
    "docs/architecture/"
    "MILESTONE_103A_PATCH_APPLY_AUTHORITY_SECURITY_REVIEW_BOUNDARY.md"
)


def _design() -> str:
    return DESIGN.read_text(encoding="utf-8")


def test_m103a_decision_and_model_are_locked():
    text = _design()
    assert "B_REAL_PATCH_AUTHORITY_GAP_BUT_NO_BUILD_YET" in text
    assert "MODEL_F_SECURITY_GAP_REAL_BUT_BUILD_BOUNDARY_NOT_READY" in text
    assert "Future patch authority Build: NOT JUSTIFIED / NOT AUTHORIZED" in text


def test_high_level_findings_are_locked():
    text = _design()
    for finding in (
        "M103A-F01",
        "M103A-F02",
        "M103A-F03",
        "M103A-F04",
    ):
        assert finding in text
    assert "Critical findings: `0`." in text
    assert "High findings: `4`." in text
    assert "Medium findings: `3`." in text
    assert "Can direct patch apply mutate a real target with `dry_run=False`? **YES.**" in text
    assert "Can direct patch apply bypass it? **YES.**" in text
    assert "its intended policy classification is **NOT PROVEN**" in text


def test_non_goals_and_forbidden_builds_are_locked():
    text = _design()
    for phrase in (
        "modify patch apply, patch rollback, or final-real-apply",
        "create a mutation authority binding",
        "reuse `RestrictedReadAuthorityBinding`",
        "implement Generic Act",
        "Do not silently consume legacy approvals",
        "do not modify:",
        "No M103B or M104 is authorized.",
    ):
        assert phrase in text


def test_generic_act_and_observation_authority_are_locked():
    text = _design()
    assert "Generic Act: `NOT_IMPLEMENTED`." in text
    assert "Generic Act integration: `NOT_AUTHORIZED`." in text
    assert "Generic Act authority: `NOT_GRANTED`." in text
    assert "Durable Observation change: NOT AUTHORIZED" in text
    assert "No current consumer justifies adding durable Observation persistence" in text


def test_static_lock_has_no_runtime_or_testclient_imports():
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
    assert not called_names.intersection({"write_text", "unlink", "write_bytes"})
