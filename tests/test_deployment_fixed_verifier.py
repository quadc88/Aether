import base64
import hashlib
import importlib.util
from importlib.machinery import SourceFileLoader
import json
from pathlib import Path
import subprocess
import sys
import time

import pytest


ROOT = Path(__file__).parents[1]
VERIFIER = ROOT / "deployment/fixed_verifier/aether-release-verify"


def _canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()


def _key(tmp_path: Path, name: str) -> tuple[Path, str]:
    private = tmp_path / f"{name}.pem"
    public = tmp_path / f"{name}.der"
    subprocess.run(["/usr/bin/openssl", "genpkey", "-algorithm", "ED25519", "-out", str(private)], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    subprocess.run(["/usr/bin/openssl", "pkey", "-in", str(private), "-pubout", "-outform", "DER", "-out", str(public)], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return private, base64.b64encode(public.read_bytes()).decode()


def _sign(tmp_path: Path, private: Path, payload: bytes, name: str) -> str:
    source = tmp_path / f"{name}.signed"
    signature = tmp_path / f"{name}.sig"
    source.write_bytes(payload)
    subprocess.run(["/usr/bin/openssl", "pkeyutl", "-sign", "-rawin", "-inkey", str(private), "-in", str(source), "-out", str(signature)], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return base64.urlsafe_b64encode(signature.read_bytes()).decode().rstrip("=")


def _normal_case(tmp_path: Path) -> tuple[dict[str, Path], dict[str, object]]:
    release_private, release_public = _key(tmp_path, "release")
    approval_private, approval_public = _key(tmp_path, "approval")
    manifest = {
        "manifest_version": 1,
        "release_id_format": "r1-<64 lowercase hexadecimal manifest digest>",
        "source": {"commit": "a" * 40, "tree": "b" * 40, "root_digest": "c" * 64},
        "runtime": {"python": "/usr/bin/python3.11", "python_version": "3.11", "import_root": "/opt/aether/current/runtime/lib/python3.11/site-packages"},
        "dependencies": {"closure_status": "INCOMPLETE", "artifacts": [], "direct_requirements": [], "interpreter": "cp311", "platform": "linux_x86_64", "format_version": 1, "install_policy": "offline-only; refuse installation when closure_status is INCOMPLETE", "requirements_source": "requirements.txt", "lock_digest": "1" * 64},
        "build": {"builder": "test", "reproducible": True, "unit_bundle_digest": "2" * 64, "unit_generation_id": "g-" + "3" * 64, "dependency_lock_digest": "1" * 64},
        "files": [{"path": "a", "sha256": "4" * 64, "size": 1, "mode": "0444", "type": "regular"}],
        "units": [{"name": name, "sha256": "5" * 64, "size": 1} for name in ("aether-oas.service", "aether-oas-runtime.socket", "aether-oas-bootstrap.socket", "aether-oas-broker.socket")],
        "schema_compatibility": {"schema_before": 1, "schema_after": 1, "mode": "UNCHANGED"},
        "policy": {"release_id": "manifest-derived", "max_retained_releases": 3},
    }
    manifest_raw = _canonical(manifest)
    manifest_digest = hashlib.sha256(manifest_raw).hexdigest()
    release_id = "r1-" + manifest_digest
    approval = {"manifest_digest": manifest_digest, "release_id": release_id, "source_commit": "a" * 40, "test_evidence_digest": "6" * 64, "approval_id": "approval-1", "activation_release_policy": {}, "issued_at_utc": "2025-01-01T00:00:00+00:00", "expires_at_utc": "2030-01-01T00:00:00+00:00", "approver_policy": {}}
    anchor = {"anchor_version": 1, "anchor_id": "anchor-1", "keys": [
        {"key_id": "release-1", "role": "release", "algorithm": "Ed25519", "public_key_encoding": "base64-der-spki", "public_key": release_public, "status": "active", "not_before": "2020-01-01T00:00:00+00:00", "not_after": "2030-01-01T00:00:00+00:00"},
        {"key_id": "approval-1", "role": "approval", "algorithm": "Ed25519", "public_key_encoding": "base64-der-spki", "public_key": approval_public, "status": "active", "not_before": "2020-01-01T00:00:00+00:00", "not_after": "2030-01-01T00:00:00+00:00"},
    ], "rotation_policy": {"mode": "NORMAL", "overlap_not_before_utc": None, "overlap_expires_at_utc": None}, "revocations": []}
    anchor["anchor_fingerprint"] = hashlib.sha256(b"aether.m121a.release-trust-anchor.v1\0" + _canonical(anchor)).hexdigest()
    envelope = {"envelope_version": 1, "domain": "aether.m121a.release-manifest.v1", "manifest_version": 1, "manifest_sha256": manifest_digest, "manifest_length": len(manifest_raw), "release_id": release_id, "approval_payload": approval, "release_signature": {"role": "release", "key_id": "release-1", "algorithm": "Ed25519", "encoding": "base64url-no-padding-64-raw-bytes", "signature": _sign(tmp_path, release_private, b"aether.m121a.release-manifest.v1\0" + manifest_raw, "release")}, "approval_signature": {"role": "approval", "key_id": "approval-1", "algorithm": "Ed25519", "encoding": "base64url-no-padding-64-raw-bytes", "signature": _sign(tmp_path, approval_private, b"aether.m121a.release-approval.v1\0" + _canonical(approval), "approval")}, "rotation_signatures": []}
    paths = {"manifest": tmp_path / "manifest.json", "envelope": tmp_path / "envelope.json", "anchor": tmp_path / "anchor.json", "staging": tmp_path / "staging"}
    paths["manifest"].write_bytes(manifest_raw)
    paths["envelope"].write_bytes(_canonical(envelope))
    paths["anchor"].write_bytes(_canonical(anchor))
    return paths, {"manifest": manifest, "envelope": envelope, "anchor": anchor, "release_private": release_private, "approval_private": approval_private, "now": "2026-01-01T00:00:00+00:00"}


def _run_case(paths: dict[str, Path], *, anchor_fingerprint: str | None = None, now: str = "2026-01-01T00:00:00+00:00") -> subprocess.CompletedProcess[bytes]:
    anchor = json.loads(paths["anchor"].read_text())
    return subprocess.run([
        str(VERIFIER), "--manifest", str(paths["manifest"]), "--envelope", str(paths["envelope"]),
        "--anchor", str(paths["anchor"]), "--approved-anchor-fingerprint", anchor_fingerprint or anchor["anchor_fingerprint"],
        "--expected-source-commit", "a" * 40, "--staging", str(paths["staging"]), "--now-utc", now,
    ], check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def _rewrite_anchor(path: Path, anchor: dict[str, object]) -> None:
    payload = {key: anchor[key] for key in ("anchor_version", "anchor_id", "keys", "rotation_policy", "revocations")}
    anchor["anchor_fingerprint"] = hashlib.sha256(b"aether.m121a.release-trust-anchor.v1\0" + _canonical(payload)).hexdigest()
    path.write_bytes(_canonical(anchor))


def _verifier_module():
    loader = SourceFileLoader("fixed_verifier_test_module", str(VERIFIER))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_fixed_verifier_performs_real_ed25519_verification_and_returns_bound_evidence(tmp_path: Path):
    release_private, release_public = _key(tmp_path, "release")
    approval_private, approval_public = _key(tmp_path, "approval")
    manifest = {
        "manifest_version": 1,
        "release_id_format": "r1-<64 lowercase hexadecimal manifest digest>",
        "source": {"commit": "a" * 40, "tree": "b" * 40, "root_digest": "c" * 64},
        "runtime": {"python": "/usr/bin/python3.11", "python_version": "3.11", "import_root": "/opt/aether/current/runtime/lib/python3.11/site-packages"},
        "dependencies": {"closure_status": "INCOMPLETE", "artifacts": [], "direct_requirements": [], "interpreter": "cp311", "platform": "linux_x86_64", "format_version": 1, "install_policy": "offline-only; refuse installation when closure_status is INCOMPLETE", "requirements_source": "requirements.txt", "lock_digest": "1" * 64},
        "build": {"builder": "test", "reproducible": True, "unit_bundle_digest": "2" * 64, "unit_generation_id": "g-" + "3" * 64, "dependency_lock_digest": "1" * 64},
        "files": [{"path": "a", "sha256": "4" * 64, "size": 1, "mode": "0444", "type": "regular"}],
        "units": [{"name": name, "sha256": "5" * 64, "size": 1} for name in ("aether-oas.service", "aether-oas-runtime.socket", "aether-oas-bootstrap.socket", "aether-oas-broker.socket")],
        "schema_compatibility": {"schema_before": 1, "schema_after": 1, "mode": "UNCHANGED"},
        "policy": {"release_id": "manifest-derived", "max_retained_releases": 3},
    }
    manifest_raw = _canonical(manifest)
    manifest_digest = hashlib.sha256(manifest_raw).hexdigest()
    release_id = "r1-" + manifest_digest
    approval = {
        "manifest_digest": manifest_digest, "release_id": release_id, "source_commit": "a" * 40,
        "test_evidence_digest": "6" * 64, "approval_id": "approval-1", "activation_release_policy": {},
        "issued_at_utc": "2025-01-01T00:00:00+00:00", "expires_at_utc": "2030-01-01T00:00:00+00:00", "approver_policy": {},
    }
    anchor = {
        "anchor_version": 1, "anchor_id": "anchor-1",
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
        "release_signature": {"role": "release", "key_id": "release-1", "algorithm": "Ed25519", "encoding": "base64url-no-padding-64-raw-bytes", "signature": _sign(tmp_path, release_private, b"aether.m121a.release-manifest.v1\0" + manifest_raw, "release")},
        "approval_signature": {"role": "approval", "key_id": "approval-1", "algorithm": "Ed25519", "encoding": "base64url-no-padding-64-raw-bytes", "signature": _sign(tmp_path, approval_private, b"aether.m121a.release-approval.v1\0" + _canonical(approval), "approval")},
        "rotation_signatures": [],
    }
    paths = {"manifest": manifest_raw, "envelope": _canonical(envelope), "anchor": _canonical(anchor)}
    for name, data in paths.items():
        (tmp_path / f"{name}.json").write_bytes(data)
    result = subprocess.run([
        str(VERIFIER), "--manifest", str(tmp_path / "manifest.json"), "--envelope", str(tmp_path / "envelope.json"),
        "--anchor", str(tmp_path / "anchor.json"), "--approved-anchor-fingerprint", anchor["anchor_fingerprint"],
        "--expected-source-commit", "a" * 40, "--staging", str(tmp_path / "staging"), "--now-utc", "2026-01-01T00:00:00+00:00",
    ], check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    assert result.returncode == 0, result.stderr.decode()
    evidence = json.loads(result.stdout)
    assert evidence["release_id"] == release_id
    assert evidence["source_commit"] == "a" * 40
    assert evidence["source_tree"] == "b" * 40
    assert evidence["source_root_digest"] == "c" * 64
    assert evidence["accepted_key_ids"] == ["approval-1", "release-1"]
    assert [item["status"] for item in evidence["signature_results"]] == ["VERIFIED", "VERIFIED"]


def test_fixed_verifier_rejects_malformed_nested_schema_before_crypto(tmp_path: Path):
    manifest = {"manifest_version": 1, "release_id_format": "r1-<64 lowercase hexadecimal manifest digest>", "source": {}, "runtime": {}, "dependencies": {}, "build": {}, "files": [], "units": [], "schema_compatibility": {}, "policy": {}}
    (tmp_path / "manifest.json").write_bytes(_canonical(manifest))
    (tmp_path / "envelope.json").write_bytes(b"{}")
    (tmp_path / "anchor.json").write_bytes(b"{}")
    result = subprocess.run([
        str(VERIFIER), "--manifest", str(tmp_path / "manifest.json"), "--envelope", str(tmp_path / "envelope.json"),
        "--anchor", str(tmp_path / "anchor.json"), "--approved-anchor-fingerprint", "0" * 64,
        "--expected-source-commit", "a" * 40, "--staging", str(tmp_path / "staging"),
    ], check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    assert result.returncode != 0


@pytest.mark.parametrize("now", ["2030-01-01T00:00:00+00:00", "2031-01-01T00:00:00+00:00"])
def test_fixed_verifier_rejects_approval_at_and_after_expiry(tmp_path: Path, now: str):
    paths, _ = _normal_case(tmp_path)
    assert _run_case(paths, now=now).returncode != 0


def test_fixed_verifier_rejects_revoked_active_signers(tmp_path: Path):
    paths, values = _normal_case(tmp_path)
    values["anchor"]["revocations"] = [{"key_id": "release-1", "revoked_at_utc": "2025-12-31T00:00:00+00:00"}]
    _rewrite_anchor(paths["anchor"], values["anchor"])
    assert _run_case(paths).returncode != 0


@pytest.mark.parametrize("mutation", [
    lambda anchor: anchor["rotation_policy"].update({"overlap_not_before_utc": "2025-01-01T00:00:00+00:00"}),
    lambda anchor: anchor["rotation_policy"].update({"mode": "OVERLAP", "overlap_not_before_utc": "2025-01-01T00:00:00+00:00", "overlap_expires_at_utc": "2030-01-01T00:00:00+00:00"}),
    lambda anchor: anchor["keys"].append(dict(anchor["keys"][0])),
])
def test_fixed_verifier_rejects_invalid_rotation_and_anchor_key_shapes(tmp_path: Path, mutation):
    paths, values = _normal_case(tmp_path)
    mutation(values["anchor"])
    _rewrite_anchor(paths["anchor"], values["anchor"])
    assert _run_case(paths).returncode != 0


@pytest.mark.parametrize("mutation", [
    lambda envelope: envelope["release_signature"].update({"role": "approval"}),
    lambda envelope: envelope["release_signature"].update({"signature": "A" * 86}),
])
def test_fixed_verifier_rejects_wrong_role_and_invalid_signatures(tmp_path: Path, mutation):
    paths, values = _normal_case(tmp_path)
    mutation(values["envelope"])
    paths["envelope"].write_bytes(_canonical(values["envelope"]))
    assert _run_case(paths).returncode != 0


@pytest.mark.parametrize("field,value", [
    ("not_before", "2026-01-01T00:00:00+00:00"),
    ("not_after", "2026-01-01T00:00:00+00:00"),
])
def test_fixed_verifier_enforces_anchor_key_window_boundaries(tmp_path: Path, field: str, value: str):
    paths, values = _normal_case(tmp_path)
    values["anchor"]["keys"][0][field] = value
    _rewrite_anchor(paths["anchor"], values["anchor"])
    result = _run_case(paths)
    assert result.returncode == (1 if field == "not_after" else 0)


def test_fixed_verifier_cleans_staging_after_success(tmp_path: Path):
    paths, _ = _normal_case(tmp_path)
    assert _run_case(paths).returncode == 0
    assert list(paths["staging"].iterdir()) == []


def test_fixed_verifier_accepts_exact_four_signature_overlap_and_rejects_it_after_expiry(tmp_path: Path):
    paths, values = _normal_case(tmp_path)
    old_release_private, old_release_public = _key(tmp_path, "old-release")
    old_approval_private, old_approval_public = _key(tmp_path, "old-approval")
    for key_id, role, public_key in (("old-release", "release", old_release_public), ("old-approval", "approval", old_approval_public)):
        values["anchor"]["keys"].append({"key_id": key_id, "role": role, "algorithm": "Ed25519", "public_key_encoding": "base64-der-spki", "public_key": public_key, "status": "retired", "not_before": "2020-01-01T00:00:00+00:00", "not_after": "2030-01-01T00:00:00+00:00"})
    values["anchor"]["rotation_policy"] = {"mode": "OVERLAP", "overlap_not_before_utc": "2025-01-01T00:00:00+00:00", "overlap_expires_at_utc": "2030-01-01T00:00:00+00:00"}
    manifest_raw = paths["manifest"].read_bytes()
    approval_raw = _canonical(values["envelope"]["approval_payload"])
    values["envelope"]["rotation_signatures"] = [
        {"role": "release", "key_id": "old-release", "algorithm": "Ed25519", "encoding": "base64url-no-padding-64-raw-bytes", "signature": _sign(tmp_path, old_release_private, b"aether.m121a.release-manifest.v1\0" + manifest_raw, "old-release-signature")},
        {"role": "approval", "key_id": "old-approval", "algorithm": "Ed25519", "encoding": "base64url-no-padding-64-raw-bytes", "signature": _sign(tmp_path, old_approval_private, b"aether.m121a.release-approval.v1\0" + approval_raw, "old-approval-signature")},
    ]
    _rewrite_anchor(paths["anchor"], values["anchor"])
    paths["envelope"].write_bytes(_canonical(values["envelope"]))
    assert _run_case(paths).returncode == 0
    assert _run_case(paths, now="2030-01-01T00:00:00+00:00").returncode != 0


@pytest.mark.parametrize("stream", ["stdout", "stderr"])
def test_fixed_verifier_bounds_openssl_output(stream: str, tmp_path: Path):
    verifier = _verifier_module()
    flag = "-c"
    code = "import sys; sys.%s.write('x' * 4097); sys.%s.flush()" % (stream, stream)
    with pytest.raises(verifier.VerificationError, match="output exceeded"):
        verifier.bounded_openssl([sys.executable, flag, code], tmp_path)


def test_fixed_verifier_terminates_and_reaps_timed_out_process(tmp_path: Path):
    verifier = _verifier_module()
    with pytest.raises(verifier.VerificationError, match="timed out"):
        verifier.bounded_openssl(
            [sys.executable, "-c", "import time; time.sleep(1)"],
            tmp_path,
            time.monotonic() + 0.05,
        )
