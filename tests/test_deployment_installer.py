from pathlib import Path

import pytest

from aether.deployment.installer import InstallError, RepositoryInstaller
from aether.deployment.lifecycle import create_isolated_root
from aether.deployment.trust_bootstrap import fixed_verifier_identity


def test_installer_issues_only_for_an_isolated_root(tmp_path: Path):
    root, capability = create_isolated_root(
        tmp_path, purpose="M122A_INSTALLER", transaction_id="tx_installer"
    )
    installer = RepositoryInstaller(root, capability=capability)
    assert installer.root == root
    with pytest.raises(InstallError):
        RepositoryInstaller("/")
    with pytest.raises(InstallError):
        RepositoryInstaller(root)


def test_installer_rejects_transaction_mismatch_and_source_links(tmp_path: Path):
    root, capability = create_isolated_root(
        tmp_path, purpose="M122A_INSTALLER", transaction_id="tx_install"
    )
    installer = RepositoryInstaller(root, capability=capability)
    source = tmp_path / "source"
    source.mkdir()
    (source / "payload").write_bytes(b"payload")
    with pytest.raises(InstallError):
        installer.stage_release("wrong", "r1-" + "a" * 64, source)
    (source / "link").symlink_to(source / "payload")
    with pytest.raises(InstallError):
        installer.stage_release("tx_install", "r1-" + "a" * 64, source)


def test_installer_rejects_symlinked_mutation_directories(tmp_path: Path):
    root, capability = create_isolated_root(
        tmp_path, purpose="M122A_INSTALLER", transaction_id="tx_lock"
    )
    outside = tmp_path / "outside"
    outside.mkdir()
    (root / "run").symlink_to(outside, target_is_directory=True)
    with pytest.raises(InstallError):
        from aether.deployment.installer import install_lock
        with install_lock(root, capability=capability):
            pass


def test_installer_installs_and_pins_the_fixed_verifier(tmp_path: Path):
    root, capability = create_isolated_root(
        tmp_path, purpose="M122A_INSTALLER", transaction_id="tx_verifier"
    )
    installer = RepositoryInstaller(root, capability=capability)
    path = installer.install_fixed_verifier()
    identified, digest = fixed_verifier_identity(root)
    assert identified == path
    assert len(digest) == 64
    assert path.stat().st_mode & 0o777 == 0o555


def test_pending_write_requires_root_trust_proof(tmp_path: Path):
    root, capability = create_isolated_root(
        tmp_path, purpose="M122A_INSTALLER", transaction_id="tx_pending"
    )
    installer = RepositoryInstaller(root, capability=capability)
    record = {
        "state": "CANDIDATE_PENDING",
        "transaction_id": "tx_pending",
        "candidate_release_id": "r1-" + "a" * 64,
    }
    with pytest.raises(InstallError, match="root trust verification"):
        installer.write_pending(record)


def test_pending_write_persists_only_after_trust_verification(monkeypatch, tmp_path: Path):
    root, capability = create_isolated_root(
        tmp_path, purpose="M122A_INSTALLER", transaction_id="tx_pending_order"
    )
    installer = RepositoryInstaller(root, capability=capability)
    events = []
    monkeypatch.setattr(
        "aether.deployment.installer.verify_candidate_before_pending",
        lambda *_args, **_kwargs: events.append("trust"),
    )
    monkeypatch.setattr(
        "aether.deployment.installer.write_record",
        lambda *_args, **_kwargs: events.append("record") or root / "record.json",
    )
    record = {
        "state": "CANDIDATE_PENDING", "transaction_id": "tx_pending_order",
        "candidate_release_id": "r1-" + "a" * 64,
        "candidate_unit_generation_id": "g-" + "b" * 64,
        "unit_bundle_digest": "c" * 64,
    }
    assert installer.write_pending(record) == root / "record.json"
    assert events == ["trust", "record"]
