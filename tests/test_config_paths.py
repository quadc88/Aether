"""Tests for config path resolver (Milestone 48A).

Requires: pytest, pyyaml, fastapi.
Install dependencies first: pip install -r requirements.txt
Then run: python3 -m pytest tests/ -v
"""

from pathlib import Path
from unittest import mock

import pytest

import yaml


@pytest.fixture()
def temp_config(tmp_path: Path):
    """Write a minimal aether.yaml under tmp_path and patch cache."""
    from aether.core import config

    prev_root = config._PROJECT_ROOT
    prev_cfg = config._CONFIG
    prev_cfg_path = config._CONFIG_PATH

    # Write config
    cfg_dir = tmp_path / "config"
    cfg_dir.mkdir(parents=True, exist_ok=True)
    cfg = {
        "project": {"name": "Aether", "version": "0.1.0"},
        "paths": {
            "data_root": str(tmp_path / "AetherData"),
            "private_dir": str(tmp_path / "AetherData" / "private"),
            "logs_dir": str(tmp_path / "AetherData" / "logs"),
            "timeline_dir": str(tmp_path / "AetherData" / "timeline"),
            "vault_dir": str(tmp_path / "AetherData" / "vault"),
            "vector_db_dir": str(tmp_path / "AetherData" / "vector_db"),
            "graph_db_dir": str(tmp_path / "AetherData" / "graph_db"),
            "backups_dir": str(tmp_path / "AetherData" / "backups"),
            "identity_seed": "identity/identity_seed.md",
        },
    }
    (cfg_dir / "aether.yaml").write_text(yaml.safe_dump(cfg), encoding="utf-8")

    try:
        config._PROJECT_ROOT = None
        config._CONFIG = None
        config._CONFIG_PATH = None
        yield tmp_path, cfg
    finally:
        config._PROJECT_ROOT = prev_root
        config._CONFIG = prev_cfg
        config._CONFIG_PATH = prev_cfg_path


class TestProjectRoot:
    def test_get_project_root_returns_path(self):
        from aether.core.config import get_project_root

        root = get_project_root()
        assert isinstance(root, Path)
        assert (root / "config" / "aether.yaml").exists()


class TestResolvePath:
    def test_absolute_paths_returned_directly(self):
        from aether.core.config import resolve_path

        result = resolve_path("/tmp/aether")
        assert result == Path("/tmp/aether")

    def test_relative_resolved_against_project_root(self):
        from aether.core.config import resolve_path, get_project_root

        result = resolve_path("identity/identity_seed.md")
        expected = get_project_root() / "identity" / "identity_seed.md"
        assert result == expected.resolve()


class TestDataRoot:
    def test_get_data_root_from_config(self, temp_config):
        from aether.core.config import get_data_root, clear_cache

        clear_cache()
        root = get_data_root()
        assert isinstance(root, Path)
        # The Windows-style paths in the real config resolve to that directory
        assert root.is_absolute()


class TestConfigPaths:
    def test_private_dir_is_absolute(self, temp_config):
        from aether.core.config import get_private_dir, clear_cache

        clear_cache()
        pdir = get_private_dir()
        assert isinstance(pdir, Path)
        assert pdir.is_absolute()

    def test_timeline_dir_is_absolute(self, temp_config):
        from aether.core.config import get_timeline_dir, clear_cache

        clear_cache()
        td = get_timeline_dir()
        assert isinstance(td, Path)
        assert td.is_absolute()

    def test_vault_dir_is_absolute(self, temp_config):
        from aether.core.config import get_vault_dir, clear_cache

        clear_cache()
        vd = get_vault_dir()
        assert isinstance(vd, Path)
        assert vd.is_absolute()

    def test_graph_db_dir_is_absolute(self, temp_config):
        from aether.core.config import get_graph_db_dir, clear_cache

        clear_cache()
        gd = get_graph_db_dir()
        assert isinstance(gd, Path)
        assert gd.is_absolute()

    def test_vector_db_dir_is_absolute(self, temp_config):
        from aether.core.config import get_vector_db_dir, clear_cache

        clear_cache()
        vd = get_vector_db_dir()
        assert isinstance(vd, Path)
        assert vd.is_absolute()

    def test_backups_dir_is_absolute(self, temp_config):
        from aether.core.config import get_backups_dir, clear_cache

        clear_cache()
        bd = get_backups_dir()
        assert isinstance(bd, Path)
        assert bd.is_absolute()

    def test_logs_dir_is_absolute(self, temp_config):
        from aether.core.config import get_logs_dir, clear_cache

        clear_cache()
        ld = get_logs_dir()
        assert isinstance(ld, Path)
        assert ld.is_absolute()


class TestIdentitySeedPath:
    def test_identity_seed_path_relative_to_root(self):
        from aether.core.config import get_identity_seed_path, get_project_root

        isp = get_identity_seed_path()
        expected = get_project_root() / "identity" / "identity_seed.md"
        assert isp == expected


class TestEnsureDir:
    def test_creates_directory(self, tmp_path):
        from aether.core.config import ensure_dir

        new_dir = tmp_path / "new_subdir"
        result = ensure_dir(new_dir)
        assert result.exists()
        assert result.is_dir()

    def test_does_not_fail_on_existing_dir(self, tmp_path):
        from aether.core.config import ensure_dir

        existing = tmp_path / "existing"
        existing.mkdir()
        result = ensure_dir(existing)
        assert result.exists()
