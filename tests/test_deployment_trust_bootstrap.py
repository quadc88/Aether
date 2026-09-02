import base64
import hashlib
import json
import os
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import shutil
import subprocess

import pytest

from aether.deployment.installer import InstallError, RepositoryInstaller, make_activation_record
from aether.deployment.lifecycle import create_isolated_root
from aether.deployment.manifest_generator import generate_manifest
from aether.deployment.unit_verifier import UNIT_NAMES, read_units
from aether.deployment.trust_bootstrap import (
    TrustBootstrapError,
    _write_evidence,
    fixed_verifier_identity,
    trust_evidence_path,
)
import aether.deployment.trust_bootstrap as trust_bootstrap


ROOT = Path(__file__).parents[1]


def _canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()


def _replace(path: Path, data: bytes) -> None:
    mode = path.stat().st_mode & 0o777
    os.chmod(path, mode | 0o600)
    path.write_bytes(data)
    os.chmod(path, mode)


def _write_anchor(fixture: dict[str, object], *, approved: bool = True) -> None:
    anchor = fixture["anchor"]
    payload = {key: anchor[key] for key in ("anchor_version", "anchor_id", "keys", "rotation_policy", "revocations")}
    anchor["anchor_fingerprint"] = hashlib.sha256(b"aether.m121a.release-trust-anchor.v1\0" + _canonical(payload)).hexdigest()
    root = fixture["root"]
    anchor_path = root / "etc/aether/release-trust-anchor.pub"
    _replace(anchor_path, _canonical(anchor))
    if approved:
        _replace(root / "etc/aether/release-trust-anchor.fingerprint", (anchor["anchor_fingerprint"] + "\n").encode("ascii"))


def _key(tmp_path: Path, name: str) -> tuple[Path, str]:
    private = tmp_path / f"{name}.pem"
    public = tmp_path / f"{name}.der"
    subprocess.run(["/usr/bin/openssl", "genpkey", "-algorithm", "ED25519", "-out", str(private)], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    subprocess.run(["/usr/bin/openssl", "pkey", "-in", str(private), "-pubout", "-outform", "DER", "-out", str(public)], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return private, base64.b64encode(public.read_bytes()).decode()


def _sign(tmp_path: Path, private: Path, payload: bytes, name: str) -> str:
    source = tmp_path / f"{name}.payload"
    signature = tmp_path / f"{name}.signature"
    source.write_bytes(payload)
    subprocess.run(["/usr/bin/openssl", "pkeyutl", "-sign", "-rawin", "-inkey", str(private), "-in", str(source), "-out", str(signature)], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return base64.urlsafe_b64encode(signature.read_bytes()).decode().rstrip("=")


def _evidence(transaction_id: str) -> dict[str, object]:
    return {
        "evidence_version": 1,
        "status": "VERIFIED",
        "transaction_id": transaction_id,
        "release_id": "r1-" + "a" * 64,
        "manifest_sha256": "a" * 64,
        "source_commit": "b" * 40,
        "source_tree": "c" * 40,
        "source_root_digest": "d" * 64,
        "approval_id": "approval-1",
        "approval_payload_digest": "f" * 64,
        "test_evidence_digest": "c" * 64,
        "anchor_fingerprint": "d" * 64,
        "verifier_sha256": "e" * 64,
        "verifier_version": "aether-release-verify.v1",
        "openssl_identity": "/usr/bin/openssl",
        "openssl_version": "OpenSSL 3.0.0",
        "accepted_key_ids": ["release-1", "approval-1"],
        "signature_results": [
            {"role": "release", "key_id": "release-1", "status": "VERIFIED"},
            {"role": "approval", "key_id": "approval-1", "status": "VERIFIED"},
        ],
        "dependency_lock_digest": "1" * 64,
        "unit_generation_id": "g-" + "2" * 64,
        "unit_bundle_digest": "3" * 64,
        "verified_at_utc": "2026-01-01T00:00:00+00:00",
    }


def test_trust_evidence_is_immutable_and_retry_idempotent(tmp_path: Path):
    root, _capability = create_isolated_root(tmp_path, purpose="M122A_EVIDENCE", transaction_id="tx-trust")
    path = trust_evidence_path(root, "tx-trust")
    evidence = _evidence("tx-trust")
    assert _write_evidence(path, evidence, root) == path
    assert _write_evidence(path, evidence, root) == path
    with pytest.raises(TrustBootstrapError, match="conflict"):
        _write_evidence(path, {**evidence, "approval_id": "different"}, root)


def test_fixed_verifier_identity_rejects_unpinned_or_wrong_mode(tmp_path: Path):
    root, capability = create_isolated_root(tmp_path, purpose="M122A_INSTALLER", transaction_id="tx-trust")
    from aether.deployment.installer import RepositoryInstaller
    path = RepositoryInstaller(root, capability=capability).install_fixed_verifier()
    fixed_verifier_identity(root)
    path.chmod(0o755)
    with pytest.raises(TrustBootstrapError, match="mode"):
        fixed_verifier_identity(root)


def test_identical_concurrent_evidence_writers_are_idempotent(tmp_path: Path):
    root, _capability = create_isolated_root(tmp_path, purpose="M122A_EVIDENCE", transaction_id="tx-concurrent")
    path = trust_evidence_path(root, "tx-concurrent")
    evidence = _evidence("tx-concurrent")
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(lambda _: _write_evidence(path, evidence, root), range(2)))
    assert results == [path, path]
    assert len(list(path.parent.glob("*.tmp-*"))) == 0


def _complete_release(tmp_path: Path, transaction_id: str = "tx-e2e") -> dict[str, object]:
    root, capability = create_isolated_root(tmp_path, purpose="M122A_INSTALLER", transaction_id=transaction_id)
    installer = RepositoryInstaller(root, capability=capability)
    installer.install_fixed_verifier()

    source = tmp_path / "release-source"
    unit_source = source / "deployment/systemd"
    unit_source.mkdir(parents=True)
    units = read_units(ROOT / "deployment/systemd")
    for name, data in units.items():
        (unit_source / name).write_bytes(data)
    module = source / "runtime/lib/python3.11/site-packages/aether/oas/host_entrypoint.py"
    module.parent.mkdir(parents=True)
    shutil.copy2(ROOT / "aether/oas/host_entrypoint.py", module)
    repository_lock = ROOT / "deployment/requirements.lock.json"
    lock_value = json.loads(repository_lock.read_text(encoding="utf-8"))
    lock_path = source / "deployment/requirements.lock.json"
    lock_path.write_bytes(repository_lock.read_bytes())
    wheelhouse = source / "deployment/wheelhouse"
    wheelhouse.mkdir()
    for wheel in (ROOT / "deployment/wheelhouse").glob("*.whl"):
        shutil.copy2(wheel, wheelhouse / wheel.name)
    dependencies = {
        key: lock_value[key]
        for key in ("closure_status", "artifacts", "direct_requirements", "interpreter", "platform", "format_version", "install_policy", "requirements_source")
    }
    dependencies["lock_digest"] = hashlib.sha256(lock_path.read_bytes()).hexdigest()
    manifest = generate_manifest(
        source, unit_bytes=units, dependencies=dependencies,
        git_metadata={"commit": "a" * 40, "tree": "b" * 40},
    )
    manifest_raw = _canonical(manifest)
    manifest_digest = hashlib.sha256(manifest_raw).hexdigest()
    release_id = "r1-" + manifest_digest
    release = root / "opt/aether/releases" / release_id
    shutil.copytree(source, release)
    (release / "release-manifest.json").write_bytes(manifest_raw)
    os.chmod(release / "release-manifest.json", 0o444)

    release_private, release_public = _key(tmp_path, "e2e-release")
    approval_private, approval_public = _key(tmp_path, "e2e-approval")
    approval = {
        "manifest_digest": manifest_digest, "release_id": release_id, "source_commit": "a" * 40,
        "test_evidence_digest": "6" * 64, "approval_id": "e2e-approval", "activation_release_policy": {},
        "issued_at_utc": "2025-01-01T00:00:00+00:00", "expires_at_utc": "2030-01-01T00:00:00+00:00", "approver_policy": {},
    }
    anchor = {
        "anchor_version": 1, "anchor_id": "e2e-anchor",
        "keys": [
            {"key_id": "release-1", "role": "release", "algorithm": "Ed25519", "public_key_encoding": "base64-der-spki", "public_key": release_public, "status": "active", "not_before": "2020-01-01T00:00:00+00:00", "not_after": "2030-01-01T00:00:00+00:00"},
            {"key_id": "approval-1", "role": "approval", "algorithm": "Ed25519", "public_key_encoding": "base64-der-spki", "public_key": approval_public, "status": "active", "not_before": "2020-01-01T00:00:00+00:00", "not_after": "2030-01-01T00:00:00+00:00"},
        ],
        "rotation_policy": {"mode": "NORMAL", "overlap_not_before_utc": None, "overlap_expires_at_utc": None},
        "revocations": [],
    }
    anchor["anchor_fingerprint"] = hashlib.sha256(b"aether.m121a.release-trust-anchor.v1\0" + _canonical(anchor)).hexdigest()
    envelope = {
        "envelope_version": 1, "domain": "aether.m121a.release-manifest.v1", "manifest_version": 1,
        "manifest_sha256": manifest_digest, "manifest_length": len(manifest_raw), "release_id": release_id,
        "approval_payload": approval,
        "release_signature": {"role": "release", "key_id": "release-1", "algorithm": "Ed25519", "encoding": "base64url-no-padding-64-raw-bytes", "signature": _sign(tmp_path, release_private, b"aether.m121a.release-manifest.v1\0" + manifest_raw, "e2e-release")},
        "approval_signature": {"role": "approval", "key_id": "approval-1", "algorithm": "Ed25519", "encoding": "base64url-no-padding-64-raw-bytes", "signature": _sign(tmp_path, approval_private, b"aether.m121a.release-approval.v1\0" + _canonical(approval), "e2e-approval")},
        "rotation_signatures": [],
    }
    (release / "release-envelope.json").write_bytes(_canonical(envelope))
    os.chmod(release / "release-envelope.json", 0o444)
    etc = root / "etc/aether"
    etc.mkdir(parents=True, exist_ok=True)
    (etc / "release-trust-anchor.pub").write_bytes(_canonical(anchor))
    os.chmod(etc / "release-trust-anchor.pub", 0o444)
    (etc / "release-trust-anchor.fingerprint").write_text(anchor["anchor_fingerprint"] + "\n", encoding="ascii")
    os.chmod(etc / "release-trust-anchor.fingerprint", 0o444)
    (etc / "release-test-evidence.sha256").write_text("6" * 64 + "\n", encoding="ascii")
    os.chmod(etc / "release-test-evidence.sha256", 0o444)

    generation = manifest["build"]["unit_generation_id"]
    record = make_activation_record(
        transaction_id=transaction_id, candidate_release_id=release_id,
        candidate_manifest_digest=manifest_digest,
        candidate_unit_generation_id=generation,
        unit_bundle_digest=manifest["build"]["unit_bundle_digest"], host_boot_id="boot",
    )
    return {
        "root": root, "capability": capability, "installer": installer,
        "release": release, "release_id": release_id, "manifest": manifest,
        "manifest_digest": manifest_digest, "envelope": envelope, "anchor": anchor,
        "record": record, "evidence_path": trust_evidence_path(root, transaction_id),
        "record_path": root / "var/lib/aether/activation/activation-record.json",
    }


@pytest.fixture
def complete_release(tmp_path: Path) -> dict[str, object]:
    return _complete_release(tmp_path)


def test_signed_isolated_release_verifies_before_pending_record_is_written(complete_release):
    fixture = complete_release
    observed_before_evidence = []
    real_write_evidence = trust_bootstrap._write_evidence

    def write_evidence(path, evidence, root):
        observed_before_evidence.append(not fixture["record_path"].exists())
        return real_write_evidence(path, evidence, root)

    trust_bootstrap._write_evidence = write_evidence
    try:
        fixture["installer"].write_pending(fixture["record"])
    finally:
        trust_bootstrap._write_evidence = real_write_evidence
    evidence = json.loads(fixture["evidence_path"].read_text(encoding="utf-8"))
    assert observed_before_evidence == [True]
    assert set(evidence) == set(trust_bootstrap._EVIDENCE_FIELDS)
    assert evidence["status"] == "VERIFIED"
    assert evidence["transaction_id"] == fixture["record"]["transaction_id"]
    assert evidence["release_id"] == fixture["release_id"]
    assert evidence["manifest_sha256"] == fixture["manifest_digest"]
    assert evidence["source_commit"] == fixture["manifest"]["source"]["commit"]
    assert evidence["source_tree"] == fixture["manifest"]["source"]["tree"]
    assert evidence["source_root_digest"] == fixture["manifest"]["source"]["root_digest"]
    assert evidence["dependency_lock_digest"] == fixture["manifest"]["dependencies"]["lock_digest"]
    assert evidence["unit_generation_id"] == fixture["manifest"]["build"]["unit_generation_id"]
    assert evidence["unit_bundle_digest"] == fixture["manifest"]["build"]["unit_bundle_digest"]
    assert evidence["accepted_key_ids"] == ["approval-1", "release-1"]
    assert json.loads(fixture["record_path"].read_text(encoding="utf-8"))["state"] == "CANDIDATE_PENDING"


def test_complete_signed_release_retry_revalidates_and_preserves_evidence(complete_release, monkeypatch):
    fixture = complete_release
    calls = []
    real_run = trust_bootstrap._run_fixed_verifier

    def run(*args, **kwargs):
        calls.append(1)
        return real_run(*args, **kwargs)

    monkeypatch.setattr(trust_bootstrap, "_run_fixed_verifier", run)
    fixture["installer"].write_pending(fixture["record"])
    evidence_before = fixture["evidence_path"].read_bytes()
    record_before = fixture["record_path"].read_bytes()
    fixture["installer"].write_pending(fixture["record"])
    assert len(calls) == 2
    assert fixture["evidence_path"].read_bytes() == evidence_before
    assert fixture["record_path"].read_bytes() == record_before


def test_revocation_after_evidence_fails_retry_without_overwrite(complete_release):
    fixture = complete_release
    fixture["installer"].write_pending(fixture["record"])
    evidence_before = fixture["evidence_path"].read_bytes()
    record_before = fixture["record_path"].read_bytes()
    fixture["anchor"]["revocations"] = [{"key_id": "release-1", "revoked_at_utc": "2025-01-01T00:00:00+00:00"}]
    _write_anchor(fixture)
    with pytest.raises(InstallError):
        fixture["installer"].write_pending(fixture["record"])
    assert fixture["evidence_path"].read_bytes() == evidence_before
    assert fixture["record_path"].read_bytes() == record_before


def _changed_anchor_without_approval(fixture):
    fixture["anchor"]["anchor_id"] = "changed-anchor"
    _replace(fixture["root"] / "etc/aether/release-trust-anchor.pub", _canonical(fixture["anchor"]))


def _changed_approved_anchor(fixture):
    _replace(fixture["root"] / "etc/aether/release-trust-anchor.fingerprint", ("0" * 64 + "\n").encode("ascii"))


def _changed_test_evidence(fixture):
    _replace(fixture["root"] / "etc/aether/release-test-evidence.sha256", ("7" * 64 + "\n").encode("ascii"))


def _changed_verifier(fixture):
    path = fixture["root"] / "usr/libexec/aether-release-verify"
    _replace(path, path.read_bytes() + b"\n")


def _changed_verifier_digest(fixture):
    _replace(fixture["root"] / "etc/aether/release-verifier.sha256", ("0" * 64 + "\n").encode("ascii"))


def _changed_envelope(fixture):
    envelope = fixture["envelope"]
    envelope["approval_payload"]["approval_id"] = "changed-approval"
    _replace(fixture["release"] / "release-envelope.json", _canonical(envelope))


def _changed_manifest(fixture):
    manifest = dict(fixture["manifest"])
    manifest["source"] = dict(manifest["source"], commit="d" * 40)
    _replace(fixture["release"] / "release-manifest.json", _canonical(manifest))


def _changed_source_identity(fixture):
    _changed_manifest(fixture)


def _changed_lock(fixture):
    path = fixture["release"] / "deployment/requirements.lock.json"
    _replace(path, path.read_bytes()[:-1] + (b"0" if path.read_bytes()[-1:] != b"0" else b"1"))


def _changed_wheel(fixture):
    path = next((fixture["release"] / "deployment/wheelhouse").glob("*.whl"))
    data = bytearray(path.read_bytes())
    data[-1] ^= 1
    _replace(path, bytes(data))


def _changed_unit(fixture):
    path = fixture["release"] / "deployment/systemd/aether-oas.service"
    data = bytearray(path.read_bytes())
    data[-1] = ord("\n") if data[-1] != ord("\n") else ord(" ")
    _replace(path, bytes(data))


def _changed_generation(fixture):
    fixture["changed_record"] = dict(fixture["record"], candidate_unit_generation_id="g-" + "f" * 64)


def _changed_transaction(fixture):
    fixture["changed_record"] = dict(fixture["record"], transaction_id="tx-changed")


@pytest.mark.parametrize("change", [
    _changed_anchor_without_approval, _changed_approved_anchor,
    _changed_test_evidence, _changed_verifier, _changed_verifier_digest,
    _changed_envelope, _changed_manifest, _changed_source_identity,
    _changed_lock, _changed_wheel, _changed_unit, _changed_generation,
    _changed_transaction,
], ids=[
    "anchor", "approved-anchor", "test-evidence", "verifier", "verifier-digest",
    "envelope", "manifest", "source-identity", "lock", "wheel", "unit",
    "generation", "transaction",
])
def test_changed_trust_input_cannot_reuse_existing_evidence(complete_release, change):
    fixture = complete_release
    fixture["installer"].write_pending(fixture["record"])
    evidence_before = fixture["evidence_path"].read_bytes()
    record_before = fixture["record_path"].read_bytes()
    change(fixture)
    record = fixture.get("changed_record", fixture["record"])
    with pytest.raises(InstallError):
        fixture["installer"].write_pending(record)
    assert fixture["evidence_path"].read_bytes() == evidence_before
    assert fixture["record_path"].read_bytes() == record_before


def test_concurrent_complete_verification_has_one_final_evidence_and_pending_record(complete_release):
    fixture = complete_release

    def verify():
        return trust_bootstrap.verify_candidate_before_pending(
            fixture["root"], transaction_id=fixture["record"]["transaction_id"],
            release_id=fixture["release_id"],
            candidate_unit_generation_id=fixture["record"]["candidate_unit_generation_id"],
            unit_bundle_digest=fixture["record"]["unit_bundle_digest"],
        )

    with ThreadPoolExecutor(max_workers=2) as pool:
        list(pool.map(lambda _index: verify(), range(2)))
    fixture["installer"].write_pending(fixture["record"])
    assert fixture["evidence_path"].is_file()
    assert len(list(fixture["evidence_path"].parent.glob("*.tmp-*"))) == 0
    assert json.loads(fixture["record_path"].read_text(encoding="utf-8"))["state"] == "CANDIDATE_PENDING"


def test_failure_before_evidence_publication_leaves_no_pending_record(complete_release, monkeypatch):
    fixture = complete_release

    def fail(*_args, **_kwargs):
        raise TrustBootstrapError("publication failure")

    monkeypatch.setattr(trust_bootstrap, "_write_evidence", fail)
    with pytest.raises(InstallError):
        fixture["installer"].write_pending(fixture["record"])
    assert not fixture["evidence_path"].exists()
    assert not fixture["record_path"].exists()


def test_failure_after_durable_evidence_is_retryable_before_pending_record(complete_release, monkeypatch):
    fixture = complete_release
    real_write = trust_bootstrap._write_evidence
    calls = []
    real_run = trust_bootstrap._run_fixed_verifier

    def run(*args, **kwargs):
        calls.append(1)
        return real_run(*args, **kwargs)

    def publish_then_fail(path, evidence, root):
        result = real_write(path, evidence, root)
        raise TrustBootstrapError("record persistence interruption")

    monkeypatch.setattr(trust_bootstrap, "_write_evidence", publish_then_fail)
    monkeypatch.setattr(trust_bootstrap, "_run_fixed_verifier", run)
    with pytest.raises(InstallError):
        fixture["installer"].write_pending(fixture["record"])
    assert fixture["evidence_path"].is_file()
    assert not fixture["record_path"].exists()
    monkeypatch.setattr(trust_bootstrap, "_write_evidence", real_write)
    fixture["installer"].write_pending(fixture["record"])
    assert calls == [1, 1]
    assert fixture["record_path"].is_file()


def test_trust_change_after_crash_cannot_reuse_durable_evidence(complete_release, monkeypatch):
    fixture = complete_release
    real_write = trust_bootstrap._write_evidence

    def publish_then_fail(path, evidence, root):
        result = real_write(path, evidence, root)
        raise TrustBootstrapError("record persistence interruption")

    monkeypatch.setattr(trust_bootstrap, "_write_evidence", publish_then_fail)
    with pytest.raises(InstallError):
        fixture["installer"].write_pending(fixture["record"])
    monkeypatch.setattr(trust_bootstrap, "_write_evidence", real_write)
    _replace(fixture["root"] / "etc/aether/release-test-evidence.sha256", ("7" * 64 + "\n").encode("ascii"))
    with pytest.raises(InstallError):
        fixture["installer"].write_pending(fixture["record"])
    assert not fixture["record_path"].exists()


def _missing_wheel(fixture):
    next((fixture["release"] / "deployment/wheelhouse").glob("*.whl")).unlink()


def _extra_wheel(fixture):
    (fixture["release"] / "deployment/wheelhouse/extra.whl").write_bytes(b"extra")


def _changed_dependency_wheel(fixture):
    path = next((fixture["release"] / "deployment/wheelhouse").glob("*.whl"))
    data = bytearray(path.read_bytes())
    data[-1] ^= 1
    _replace(path, bytes(data))


def _changed_dependency_lock(fixture):
    path = fixture["release"] / "deployment/requirements.lock.json"
    data = bytearray(path.read_bytes())
    data[-1] = ord(" ") if data[-1] != ord(" ") else ord("\n")
    _replace(path, bytes(data))


def _missing_release_lock(fixture):
    (fixture["release"] / "deployment/requirements.lock.json").unlink()


@pytest.mark.parametrize("change", [
    _missing_wheel, _extra_wheel, _changed_dependency_wheel,
    _changed_dependency_lock, _missing_release_lock, _missing_release_lock,
], ids=["missing-wheel", "extra-wheel", "changed-wheel", "changed-lock", "missing-release-lock", "no-checkout-fallback"])
def test_complete_dependency_closure_rejects_changed_or_incomplete_release(change, complete_release):
    fixture = complete_release
    change(fixture)
    with pytest.raises(InstallError):
        fixture["installer"].write_pending(fixture["record"])
    assert not fixture["evidence_path"].exists()
    assert not fixture["record_path"].exists()
