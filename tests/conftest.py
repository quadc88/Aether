"""Tests-only global isolation for Aether memory persistence roots."""

from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture(scope="session", autouse=True)
def isolate_memory_persistence_for_test_session(tmp_path_factory):
    """Redirect memory-module persistence to one temporary root for all tests."""

    from aether.memory.episodic import writer as episodic_writer
    from aether.memory.graph import store as graph_store
    from aether.memory.semantic import indexer as semantic_indexer
    from aether.memory.timeline import recorder as timeline_recorder

    data_root = tmp_path_factory.mktemp("aether_memory_session") / "AetherData"
    paths = {
        "data_root": data_root,
        "private_dir": data_root / "private",
        "vault_dir": data_root / "vault",
        "vector_db_dir": data_root / "vector_db",
        "timeline_dir": data_root / "timeline",
        "graph_db_dir": data_root / "graph_db",
        "logs_dir": data_root / "logs",
        "backups_dir": data_root / "backups",
    }
    repository_root = Path(__file__).resolve().parents[1]
    forbidden_roots = (
        Path("/home/aether/data").resolve(),
        repository_root.resolve(),
    )

    for path in paths.values():
        path.mkdir(parents=True, exist_ok=True)
        resolved = path.resolve()
        assert all(not resolved.is_relative_to(root) for root in forbidden_roots)

    config = {"paths": {name: str(path) for name, path in paths.items()}}

    def load_isolated_config(*_args, **_kwargs):
        return config

    patcher = pytest.MonkeyPatch()
    for module in (
        episodic_writer,
        semantic_indexer,
        timeline_recorder,
        graph_store,
    ):
        patcher.setattr(module, "load_aether_config", load_isolated_config)

    yield
    patcher.undo()
