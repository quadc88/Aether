"""Tests-only global isolation for Aether persistence roots."""

from __future__ import annotations

import importlib
import sys
from pathlib import Path
from types import ModuleType

import pytest


_PATH_GETTERS = {
    "get_data_root": "data_root",
    "get_private_dir": "private_dir",
    "get_logs_dir": "logs_dir",
    "get_timeline_dir": "timeline_dir",
    "get_vault_dir": "vault_dir",
    "get_vector_db_dir": "vector_db_dir",
    "get_graph_db_dir": "graph_db_dir",
    "get_backups_dir": "backups_dir",
}

_PERSISTENCE_MODULES_TO_PRELOAD = (
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
    "aether.identity.guard",
    "aether.action.approved_dry_run_gate",
    "aether.action.dry_run_review_gate",
    "aether.action.real_apply_approval_gate",
    "aether.action.post_apply_verification_gate",
)


@pytest.fixture(scope="session")
def isolated_test_paths(tmp_path_factory) -> dict[str, Path]:
    """Create the single isolated persistence tree used by the test session."""

    data_root = tmp_path_factory.mktemp("aether_persistence_session") / "AetherData"
    paths = {
        "data_root": data_root,
        "private_dir": data_root / "private",
        "vault_dir": data_root / "vault",
        "vector_db_dir": data_root / "vector_db",
        "timeline_dir": data_root / "timeline",
        "graph_db_dir": data_root / "graph_db",
        "logs_dir": data_root / "logs",
        "backups_dir": data_root / "backups",
        "docs_history_dir": data_root / "docs_history",
        "patch_target_dir": data_root / "patch_targets",
        "mutation_log_dir": data_root / "mutation_logs",
    }
    forbidden_roots = (
        Path("/home/aether/data").resolve(),
        Path(__file__).resolve().parents[1],
    )

    for path in paths.values():
        path.mkdir(parents=True, exist_ok=True)
        resolved = path.resolve()
        assert all(not resolved.is_relative_to(root) for root in forbidden_roots)

    return paths


@pytest.fixture(scope="session")
def isolated_test_config(isolated_test_paths) -> dict:
    """Return the shared fake config consumed by persistence modules in tests."""

    return {
        "paths": {
            name: str(path)
            for name, path in isolated_test_paths.items()
        }
    }


def _patch_config_symbols(
    patcher: pytest.MonkeyPatch,
    module: ModuleType,
    config: dict,
    paths: dict[str, Path],
    *,
    force: bool,
) -> None:
    """Patch config symbols retained locally by one imported Aether module."""

    def should_patch(value) -> bool:
        return (
            force
            or getattr(value, "_aether_test_isolated_config", False)
            or getattr(value, "__module__", "").startswith("aether.")
        )

    if hasattr(module, "load_aether_config") and should_patch(
        module.load_aether_config
    ):
        def load_isolated_config(*_args, **_kwargs):
            return config

        load_isolated_config._aether_test_isolated_config = True
        patcher.setattr(module, "load_aether_config", load_isolated_config)

    for attribute, path_key in _PATH_GETTERS.items():
        if not hasattr(module, attribute):
            continue
        current = getattr(module, attribute)
        is_core_getter = (
            module.__name__ == "aether.core.config"
            or getattr(current, "__module__", "") == "aether.core.config"
            or getattr(current, "_aether_test_isolated_config", False)
        )
        if not is_core_getter:
            continue

        def get_isolated_path(_path=paths[path_key]):
            return _path

        get_isolated_path._aether_test_isolated_config = True
        patcher.setattr(module, attribute, get_isolated_path)


def _loaded_aether_modules() -> list[ModuleType]:
    """Return a stable snapshot of imported Aether modules."""

    return [
        module
        for name, module in list(sys.modules.items())
        if name == "aether" or name.startswith("aether.")
        if isinstance(module, ModuleType)
    ]


@pytest.fixture(scope="session", autouse=True)
def isolate_persistence_for_test_session(
    isolated_test_config,
    isolated_test_paths,
):
    """Redirect central and already-imported Aether persistence for all tests."""

    from aether.core import config as core_config

    patcher = pytest.MonkeyPatch()
    core_config.clear_cache()

    for module_name in _PERSISTENCE_MODULES_TO_PRELOAD:
        importlib.import_module(module_name)

    for module in _loaded_aether_modules():
        _patch_config_symbols(
            patcher,
            module,
            isolated_test_config,
            isolated_test_paths,
            force=True,
        )

    yield

    patcher.undo()
    core_config.clear_cache()
