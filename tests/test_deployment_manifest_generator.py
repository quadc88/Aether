from pathlib import Path

import pytest

from aether.deployment.manifest_generator import ManifestGenerationError, file_entry, generate_manifest
from aether.deployment.unit_verifier import UNIT_NAMES


def test_file_entry_binds_digest_size_mode_and_relative_path(tmp_path: Path):
    path = tmp_path / "artifact"
    path.write_bytes(b"artifact")
    entry = file_entry(path, tmp_path)
    assert entry["path"] == "artifact"
    assert entry["size"] == 8
    assert len(entry["sha256"]) == 64


def test_manifest_generation_binds_git_and_dependency_identity(tmp_path: Path):
    (tmp_path / "artifact").write_bytes(b"artifact")
    units = {name: b"[Unit]\n" for name in UNIT_NAMES}
    manifest = generate_manifest(
        tmp_path,
        unit_bytes=units,
        dependencies={
            "closure_status": "INCOMPLETE",
            "artifacts": [],
            "direct_requirements": [],
            "interpreter": "cp311",
            "platform": "linux_x86_64",
            "format_version": 1,
            "install_policy": "offline-only; refuse installation when closure_status is INCOMPLETE",
            "requirements_source": "requirements.txt",
            "lock_digest": "a" * 64,
        },
        git_metadata={"commit": "b" * 40, "tree": "c" * 40},
    )
    assert manifest["source"]["commit"] == "b" * 40
    assert manifest["build"]["dependency_lock_digest"] == "a" * 64
    assert manifest["build"]["unit_generation_id"].startswith("g-")


def test_file_entry_rejects_symlink_and_hardlink_inputs(tmp_path: Path):
    source = tmp_path / "source"
    source.write_bytes(b"source")
    link = tmp_path / "link"
    link.symlink_to(source)
    with pytest.raises(ManifestGenerationError):
        file_entry(link, tmp_path)
    hardlink = tmp_path / "hardlink"
    hardlink.hardlink_to(source)
    with pytest.raises(ManifestGenerationError):
        file_entry(source, tmp_path)
