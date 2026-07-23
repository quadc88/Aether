"""Shared configuration and path resolver for Aether.

Reads config/aether.yaml once and provides resolved pathlib.Path objects
for all data directories. Supports both Windows absolute paths (e.g. C:/AetherData)
and relative paths. Does not silently fall back to repo-relative defaults.
"""

from __future__ import annotations

import hashlib
import os
from pathlib import Path
from typing import Optional

import yaml


_PROJECT_ROOT: Optional[Path] = None
_CONFIG: Optional[dict] = None
_CONFIG_PATH: Optional[Path] = None


def _determine_project_root() -> Path:
    """Return the project root directory.

    Searches upwards from this file's location, then falls back to
    the current working directory.
    """
    candidates: list[Path] = []

    file_dir = Path(__file__).resolve().parent.parent.parent
    candidates.append(file_dir)

    cwd = Path.cwd()
    if cwd != file_dir:
        candidates.append(cwd)

    for candidate in candidates:
        if (candidate / "config" / "aether.yaml").exists():
            return candidate

    return candidates[0]


def get_project_root() -> Path:
    """Return the project root path (cached)."""
    global _PROJECT_ROOT
    if _PROJECT_ROOT is None:
        _PROJECT_ROOT = _determine_project_root()
    return _PROJECT_ROOT


def load_aether_config(path: Optional[str] = None) -> dict:
    """Load and cache aether.yaml configuration.

    Args:
        path: Absolute or relative path to config file. If None, uses
              ``config/aether.yaml`` relative to the project root.

    Returns:
        Parsed YAML as a dict. Returns empty dict if file not found.
    """
    global _CONFIG, _CONFIG_PATH

    if _CONFIG is not None and _CONFIG_PATH is not None:
        resolved = Path(path) if path else get_project_root() / "config" / "aether.yaml"
        if resolved.resolve() == _CONFIG_PATH.resolve():
            return _CONFIG

    config_path = Path(path) if path else get_project_root() / "config" / "aether.yaml"
    _CONFIG_PATH = config_path.resolve()

    if not config_path.exists():
        _CONFIG = {}
        return _CONFIG

    with config_path.open("r", encoding="utf-8") as f:
        _CONFIG = yaml.safe_load(f) or {}

    return _CONFIG


def resolve_path(value: str, base: Optional[Path] = None) -> Path:
    """Resolve a path value from config into an absolute Path.

    Rules:
    - If value is an absolute path (e.g. C:/AetherData), use it directly.
    - If value is relative, resolve it against *base* if provided,
      otherwise resolve against the project root.
    - Does NOT silently fall back to repo-relative paths when config
      explicitly defines an absolute path.

    Args:
        value: Path string from config.
        base: Optional base directory for relative paths.

    Returns:
        Resolved absolute pathlib.Path.
    """
    if value is None:
        return get_project_root()

    path = Path(value)

    # Windows absolute check: e.g. C:/AetherData
    if path.is_absolute():
        return path

    # Relative path — resolve against base or project root
    if base is not None:
        return (base / path).resolve()
    return (get_project_root() / path).resolve()


def _get_paths_section() -> dict:
    """Return the ``paths`` section from config, or empty dict."""
    config = load_aether_config()
    return config.get("paths", {})


def get_data_root() -> Path:
    """Return the configured data_root path (absolute)."""
    paths = _get_paths_section()
    value = paths.get("data_root", "")
    if not value:
        return get_project_root()
    return resolve_path(value)


def get_private_dir() -> Path:
    """Return the configured private_dir path (absolute)."""
    paths = _get_paths_section()
    value = paths.get("private_dir", "")
    if not value:
        return get_data_root() / "private"
    return resolve_path(value)


def get_logs_dir() -> Path:
    """Return the configured logs_dir path (absolute)."""
    paths = _get_paths_section()
    value = paths.get("logs_dir", "")
    if not value:
        return get_data_root() / "logs"
    return resolve_path(value)


def get_timeline_dir() -> Path:
    """Return the configured timeline_dir path (absolute)."""
    paths = _get_paths_section()
    value = paths.get("timeline_dir", "")
    if not value:
        return get_data_root() / "timeline"
    return resolve_path(value)


def get_vault_dir() -> Path:
    """Return the configured vault_dir path (absolute)."""
    paths = _get_paths_section()
    value = paths.get("vault_dir", "")
    if not value:
        return get_data_root() / "vault"
    return resolve_path(value)


def get_vector_db_dir() -> Path:
    """Return the configured vector_db_dir path (absolute)."""
    paths = _get_paths_section()
    value = paths.get("vector_db_dir", "")
    if not value:
        return get_data_root() / "vector_db"
    return resolve_path(value)


def get_graph_db_dir() -> Path:
    """Return the configured graph_db_dir path (absolute)."""
    paths = _get_paths_section()
    value = paths.get("graph_db_dir", "")
    if not value:
        return get_data_root() / "graph_db"
    return resolve_path(value)


def get_backups_dir() -> Path:
    """Return the configured backups_dir path (absolute)."""
    paths = _get_paths_section()
    value = paths.get("backups_dir", "")
    if not value:
        return get_data_root() / "backups"
    return resolve_path(value)


def get_identity_seed_path() -> Path:
    """Return the configured identity_seed path (relative to project root)."""
    paths = _get_paths_section()
    value = paths.get("identity_seed", "identity/identity_seed.md")
    return get_project_root() / value


def ensure_dir(path: Path, *, create: bool = True) -> Path:
    """Return a directory path, optionally creating it.

    Args:
        path: Directory to ensure exists.
        create: If True, call mkdir(parents=True, exist_ok=True).

    Returns:
        The (possibly created) directory Path.
    """
    if create:
        path.mkdir(parents=True, exist_ok=True)
    return path


def clear_cache() -> None:
    """Clear cached project root and config. For testing only."""
    global _PROJECT_ROOT, _CONFIG, _CONFIG_PATH
    _PROJECT_ROOT = None
    _CONFIG = None
    _CONFIG_PATH = None
