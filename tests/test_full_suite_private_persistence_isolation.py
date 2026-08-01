"""Contract tests for full-suite tests-only persistence isolation."""

from __future__ import annotations

import hashlib
import importlib
from pathlib import Path

import pytest

from aether.core import config as core_config


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REAL_DATA_ROOT = Path("/home/aether/data")
REAL_PRIVATE_ROOT = REAL_DATA_ROOT / "private"

PERSISTENCE_MODULES = (
    "aether.action.approval_queue",
    "aether.action.dry_run_queue",
    "aether.action.simulation_plan_queue",
    "aether.action.simulation_result_queue",
    "aether.action.simulation_verdict_queue",
    "aether.action.apply_gate_queue",
    "aether.action.human_authorization_queue",
    "aether.action.apply_execution_gate_queue",
    "aether.action.apply_executor_contract_queue",
    "aether.action.apply_executor_plan_queue",
    "aether.action.apply_executor_evidence_contract_queue",
    "aether.action.apply_executor_evidence_collection_plan_queue",
    "aether.action.observation_record_queue",
    "aether.identity.guard",
    "aether.action.approved_dry_run_gate",
    "aether.action.dry_run_review_gate",
    "aether.action.real_apply_approval_gate",
    "aether.action.post_apply_verification_gate",
)


def _fingerprint(root: Path) -> dict[str, tuple[int, str]]:
    if not root.exists():
        return {}
    return {
        str(path.relative_to(root)): (
            path.stat().st_size,
            hashlib.sha256(path.read_bytes()).hexdigest(),
        )
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def _assert_isolated(path: Path, isolated_root: Path) -> None:
    resolved = path.resolve()
    assert resolved.is_relative_to(isolated_root.resolve())
    assert not resolved.is_relative_to(PROJECT_ROOT.resolve())
    assert not resolved.is_relative_to(REAL_DATA_ROOT.resolve())


def test_core_config_resolves_all_persistence_paths_to_session_root(
    isolated_test_paths,
):
    getters = {
        "data_root": core_config.get_data_root,
        "private_dir": core_config.get_private_dir,
        "logs_dir": core_config.get_logs_dir,
        "timeline_dir": core_config.get_timeline_dir,
        "vault_dir": core_config.get_vault_dir,
        "vector_db_dir": core_config.get_vector_db_dir,
        "graph_db_dir": core_config.get_graph_db_dir,
        "backups_dir": core_config.get_backups_dir,
    }

    for key, getter in getters.items():
        actual = getter()
        assert actual == isolated_test_paths[key]
        _assert_isolated(actual, isolated_test_paths["data_root"])


@pytest.mark.parametrize("module_name", PERSISTENCE_MODULES)
def test_module_local_config_reference_is_isolated(
    module_name,
    isolated_test_paths,
):
    module = importlib.import_module(module_name)

    if hasattr(module, "load_aether_config"):
        private = Path(module.load_aether_config()["paths"]["private_dir"])
    else:
        assert hasattr(module, "get_private_dir")
        private = Path(module.get_private_dir())

    assert private == isolated_test_paths["private_dir"]
    _assert_isolated(private, isolated_test_paths["data_root"])


def test_low_risk_approval_record_write_cannot_drift_real_private_root(
    isolated_test_paths,
):
    approval_queue = importlib.import_module("aether.action.approval_queue")
    before = _fingerprint(REAL_PRIVATE_ROOT)
    queue_path = approval_queue.get_approval_queue_path()

    try:
        item = approval_queue.create_approval_item(
            request_text="isolation proof",
            proposed_action="record a tests-only approval item",
            verification_plan={
                "action_type": "tests_only_isolation_proof",
                "risk_level": "low",
                "requires_user_approval": False,
            },
            metadata={"milestone": "82AH-R"},
        )
        assert item["status"] == "pending"
        assert queue_path.is_file()
        _assert_isolated(queue_path, isolated_test_paths["data_root"])
        assert _fingerprint(REAL_PRIVATE_ROOT) == before
    finally:
        if queue_path.exists():
            queue_path.unlink()


def test_active_config_contains_no_real_or_repository_persistence_path(
    isolated_test_config,
):
    for name, value in isolated_test_config["paths"].items():
        resolved = Path(value).resolve()
        assert not resolved.is_relative_to(REAL_DATA_ROOT.resolve()), name
        assert not resolved.is_relative_to(PROJECT_ROOT.resolve()), name

    identity_seed = core_config.get_identity_seed_path().resolve()
    assert identity_seed == (PROJECT_ROOT / "identity" / "identity_seed.md").resolve()
