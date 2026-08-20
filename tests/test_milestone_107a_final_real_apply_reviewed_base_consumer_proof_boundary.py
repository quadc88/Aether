"""Static/document lock for the read-only M107A consumer-proof boundary."""

import ast
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DESIGN = ROOT / (
    "docs/architecture/"
    "MILESTONE_107A_FINAL_REAL_APPLY_REVIEWED_BASE_CONSUMER_PROOF_BOUNDARY.md"
)


def _design() -> str:
    return DESIGN.read_text(encoding="utf-8")


def test_selected_final_only_model_and_non_universal_scope_are_locked():
    text = _design()
    assert "MODEL_A_FINAL_REVIEWED_BASE_EXECUTION_GUARD" in text
    assert "A_FINAL_ONLY_REVIEWED_BASE_BUILD_JUSTIFIED" in text
    assert "Future Build: JUSTIFIED FOR PM REVIEW" in text
    assert "Actual Build: NOT STARTED" in text
    assert "Universal F02 closure: NOT CLAIMED" in text
    assert "direct apply remains outside this final-only contract" in text


def test_existing_hash_source_and_exact_consumer_linkage_are_locked():
    text = _design()
    for phrase in (
        "dry-run `original_hash_before`",
        "dry_run_patch_apply_id",
        "dry_run is True",
        "status == \"dry_run\"",
        "64-character lowercase hexadecimal",
        "existing UTF-8 SHA-256",
        "before the real apply call",
    ):
        assert phrase in text


def test_no_new_persistence_or_universal_authority_is_locked():
    text = _design()
    for phrase in (
        "persistence impact: NONE",
        "schema migration: NONE",
        "API/OpenAPI impact: NONE",
        "canonical patch authority: NOT PROVEN / UNCHANGED",
        "proposal-time hash\npersistence",
        "Do not implement the guard during M107A.",
    ):
        assert phrase in text


def test_stale_base_and_fail_closed_scenarios_are_locked():
    text = _design()
    for phrase in (
        "Hash mismatch; final apply is blocked before mutation",
        "Fail closed before mutation",
        "The guard does not solve F06 claim/mutation atomicity",
        "must not fall back to excerpt-only acceptance",
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


def test_m107a_forbidden_runtime_files_are_documented():
    text = _design()
    for path in (
        "aether/action/patch_apply.py",
        "aether/action/patch_rollback.py",
        "aether/action/real_apply_approval_gate.py",
        "aether/action/final_real_apply_executor.py",
        "PROGRESS.md",
    ):
        assert path in text
