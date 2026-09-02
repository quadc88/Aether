"""Deterministic repository manifest generation."""

from __future__ import annotations

import hashlib
import os
from pathlib import Path
import subprocess
import stat
import re
from typing import Any, Iterable, Mapping

from .manifest_schema import canonical_json_bytes, release_id_for_digest, sha256_hex, validate_manifest
from .unit_verifier import UNIT_NAMES, canonical_unit_bundle_digest, generation_id


class ManifestGenerationError(ValueError):
    """Raised when a deterministic source inventory cannot be produced."""


def _relative_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            raise ManifestGenerationError(f"symlink is not a release input: {path}")
        if path.is_file():
            files.append(path)
        elif not path.is_dir():
            raise ManifestGenerationError(f"special release input: {path}")
    return files


def file_entry(path: Path, root: Path) -> dict[str, Any]:
    info_before = path.lstat()
    if not stat.S_ISREG(info_before.st_mode) or info_before.st_nlink != 1:
        raise ManifestGenerationError("release input is not an unambiguous regular file")
    data = path.read_bytes()
    info_after = path.lstat()
    if (info_before.st_dev, info_before.st_ino, info_before.st_size, info_before.st_mtime_ns) != (info_after.st_dev, info_after.st_ino, info_after.st_size, info_after.st_mtime_ns):
        raise ManifestGenerationError("release input changed during hashing")
    relative = path.relative_to(root).as_posix()
    if relative.startswith("../") or relative == "..":
        raise ManifestGenerationError("release path escapes source root")
    return {
        "path": relative,
        "sha256": hashlib.sha256(data).hexdigest(),
        "size": len(data),
        "mode": f"{path.stat().st_mode & 0o7777:04o}",
        "type": "regular",
    }


def _git_metadata(root: Path) -> dict[str, str]:
    try:
        clean = subprocess.run(["git", "-C", str(root), "status", "--porcelain=v1", "--untracked-files=all"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=5, check=True).stdout
        if clean:
            raise ManifestGenerationError("dirty Git checkout cannot be a release source")
        commit = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=5, check=True).stdout.strip()
        tree = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD^{tree}"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=5, check=True).stdout.strip()
    except (OSError, subprocess.SubprocessError) as exc:
        raise ManifestGenerationError("source Git identity is unavailable") from exc
    if not commit or not tree:
        raise ManifestGenerationError("source Git identity is empty")
    return {"commit": commit, "tree": tree}


def generate_manifest(
    source_root: str | Path,
    *,
    unit_bytes: Mapping[str, bytes],
    dependencies: Mapping[str, Any],
    runtime: Mapping[str, Any] | None = None,
    schema_compatibility: Mapping[str, Any] | None = None,
    policy: Mapping[str, Any] | None = None,
    git_metadata: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    root = Path(source_root).resolve()
    if not root.is_dir() or root == Path("/"):
        raise ManifestGenerationError("explicit source root is required")
    if tuple(unit_bytes) != UNIT_NAMES:
        raise ManifestGenerationError("all four ordered units are required")
    source_identity = dict(git_metadata or _git_metadata(root))
    if not re.fullmatch(r"[0-9a-f]{40,64}", str(source_identity.get("commit", ""))) or not re.fullmatch(r"[0-9a-f]{40,64}", str(source_identity.get("tree", ""))):
        raise ManifestGenerationError("source commit and tree are required")
    if "lock_digest" not in dependencies or not re.fullmatch(r"[0-9a-f]{64}", str(dependencies["lock_digest"])):
        raise ManifestGenerationError("dependency lock digest is required")
    entries = [file_entry(path, root) for path in _relative_files(root)]
    unit_entries = [
        {"name": name, "sha256": hashlib.sha256(unit_bytes[name]).hexdigest(), "size": len(unit_bytes[name])}
        for name in UNIT_NAMES
    ]
    bundle_digest = canonical_unit_bundle_digest(unit_bytes)
    manifest: dict[str, Any] = {
        "manifest_version": 1,
        "release_id_format": "r1-<64 lowercase hexadecimal manifest digest>",
        "source": {"commit": source_identity["commit"], "tree": source_identity["tree"], "root_digest": sha256_hex(b"".join(canonical_json_bytes(entry) + b"\0" for entry in entries))},
        "runtime": dict(runtime or {"python": "/usr/bin/python3.11", "python_version": "3.11", "import_root": "/opt/aether/current/runtime/lib/python3.11/site-packages"}),
        "dependencies": dict(dependencies),
        "build": {"builder": "aether-repository-build", "reproducible": True, "unit_bundle_digest": bundle_digest, "unit_generation_id": generation_id(unit_bytes), "dependency_lock_digest": dependencies["lock_digest"]},
        "files": entries,
        "units": unit_entries,
        "schema_compatibility": dict(schema_compatibility or {"schema_before": 1, "schema_after": 1, "mode": "UNCHANGED"}),
        "policy": dict(policy or {"release_id": "manifest-derived", "max_retained_releases": 3}),
    }
    validate_manifest(manifest)
    return manifest


def write_manifest(path: str | Path, manifest: Mapping[str, Any]) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(canonical_json_bytes(dict(manifest)))
