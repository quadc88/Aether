"""Root-side trust bootstrap for a candidate activation.

The candidate entrypoint consumes only the durable result produced here.  The
fixed verifier subprocess is intentionally separate from this package so a
candidate cannot replace its implementation by changing Python imports.
"""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import os
from pathlib import Path
import re
import selectors
import secrets
import stat
import subprocess
import time
from typing import Any, Mapping

from .dependency_lock import DependencyLockError, verify_dependency_closure
from .lifecycle import ensure_temporary_root
from .manifest_schema import ManifestError, canonical_json_bytes, parse_canonical_json, sha256_hex, validate_manifest
from .unit_verifier import UnitVerificationError, verify_unit_bytes


class TrustBootstrapError(RuntimeError):
    """Raised when root-side trust bootstrap cannot complete safely."""


TRUST_ANCHOR = Path("/etc/aether/release-trust-anchor.pub")
APPROVED_ANCHOR = Path("/etc/aether/release-trust-anchor.fingerprint")
APPROVED_TEST_EVIDENCE = Path("/etc/aether/release-test-evidence.sha256")
FIXED_VERIFIER = Path("/usr/libexec/aether-release-verify")
VERIFIER_DIGEST = Path("/etc/aether/release-verifier.sha256")
TRUST_EVIDENCE_ROOT = Path("/var/lib/aether/activation/trust-verification")
_DIGEST = re.compile(r"^[0-9a-f]{64}$")
_EVIDENCE_FIELDS = (
    "evidence_version", "status", "transaction_id", "release_id",
    "manifest_sha256", "source_commit", "source_tree", "source_root_digest", "approval_id",
    "approval_payload_digest", "test_evidence_digest", "anchor_fingerprint",
    "verifier_sha256", "verifier_version", "openssl_identity", "openssl_version",
    "accepted_key_ids", "signature_results", "dependency_lock_digest",
    "unit_generation_id", "unit_bundle_digest", "verified_at_utc",
)


def trust_evidence_path(root: str | Path, transaction_id: str) -> Path:
    if not re.fullmatch(r"[A-Za-z0-9_.:-]{1,128}", transaction_id):
        raise TrustBootstrapError("trust evidence transaction identity is invalid")
    base = Path(root)
    return _under(base, TRUST_EVIDENCE_ROOT) / f"{transaction_id}.json"


def _under(root: Path, path: Path) -> Path:
    return root / str(path).lstrip("/") if root != Path("/") else path


def _regular(path: Path, *, executable: bool = False) -> os.stat_result:
    try:
        info = path.lstat()
    except OSError as exc:
        raise TrustBootstrapError(f"required trust artifact is missing: {path}") from exc
    if stat.S_ISLNK(info.st_mode) or not stat.S_ISREG(info.st_mode):
        raise TrustBootstrapError(f"trust artifact is not a regular file: {path}")
    if executable and stat.S_IMODE(info.st_mode) != 0o555:
        raise TrustBootstrapError("fixed verifier mode is not exact")
    if info.st_nlink != 1:
        raise TrustBootstrapError("trust artifact has ambiguous hard-link identity")
    return info


def _owner_is_allowed(info: os.stat_result, root: Path) -> None:
    expected = 0 if root == Path("/") else os.getuid()
    if info.st_uid != expected:
        raise TrustBootstrapError("trust artifact owner is not the root operation owner")


def _read_canonical(path: Path) -> Mapping[str, Any]:
    _regular(path)
    try:
        value = parse_canonical_json(path.read_bytes())
    except (OSError, ManifestError) as exc:
        raise TrustBootstrapError(f"trust artifact is not canonical: {path}") from exc
    if not isinstance(value, Mapping):
        raise TrustBootstrapError("trust artifact is not an object")
    return value


def _read_approved_fingerprint(path: Path, root: Path) -> str:
    info = _regular(path)
    _owner_is_allowed(info, root)
    try:
        value = path.read_text(encoding="ascii")
    except (OSError, UnicodeDecodeError) as exc:
        raise TrustBootstrapError("approved anchor fingerprint is unreadable") from exc
    if not re.fullmatch(r"[0-9a-f]{64}\n?", value):
        raise TrustBootstrapError("approved anchor fingerprint is not exact")
    return value.rstrip("\n")


def _read_approved_digest(path: Path, root: Path) -> str:
    info = _regular(path)
    _owner_is_allowed(info, root)
    try:
        value = path.read_text(encoding="ascii")
    except (OSError, UnicodeDecodeError) as exc:
        raise TrustBootstrapError("approved test evidence digest is unreadable") from exc
    if not re.fullmatch(r"[0-9a-f]{64}\n?", value):
        raise TrustBootstrapError("approved test evidence digest is not exact")
    return value.rstrip("\n")


def fixed_verifier_identity(root: str | Path = "/") -> tuple[Path, str]:
    base = Path(root).resolve()
    path = _under(base, FIXED_VERIFIER)
    info = _regular(path, executable=True)
    _owner_is_allowed(info, base)
    digest = sha256_hex(path.read_bytes())
    digest_path = _under(base, VERIFIER_DIGEST)
    digest_info = _regular(digest_path)
    _owner_is_allowed(digest_info, base)
    try:
        approved = digest_path.read_text(encoding="ascii")
    except (OSError, UnicodeDecodeError) as exc:
        raise TrustBootstrapError("fixed verifier digest approval is unreadable") from exc
    if not re.fullmatch(r"[0-9a-f]{64}\n?", approved) or approved.rstrip("\n") != digest:
        raise TrustBootstrapError("fixed verifier identity is not approved")
    return path, digest


def _validate_inventory(release: Path, manifest: Mapping[str, Any], *, root: Path | None = None) -> None:
    try:
        release_info = release.lstat()
    except OSError as exc:
        raise TrustBootstrapError("release root is unavailable") from exc
    if stat.S_ISLNK(release_info.st_mode) or not stat.S_ISDIR(release_info.st_mode):
        raise TrustBootstrapError("release root is not a regular directory")
    if root is not None:
        if _has_symlink_parent(release, root):
            raise TrustBootstrapError("release path contains a symlink")
        _owner_is_allowed(release_info, root)
    listed = {item["path"]: item for item in manifest["files"]}
    expected = set(listed) | {"release-manifest.json", "release-envelope.json"}
    expected_directories = {
        str(parent)
        for relative in expected
        for parent in Path(relative).parents
        if str(parent) != "."
    }
    actual: set[str] = set()
    for path in sorted(release.rglob("*")):
        relative = path.relative_to(release).as_posix()
        if path.is_symlink() or _has_symlink_parent(path, release):
            raise TrustBootstrapError("release inventory contains a symlink")
        if path.is_file():
            info = path.lstat()
            if info.st_nlink != 1:
                raise TrustBootstrapError("release inventory contains a hard link")
            if root is not None:
                _owner_is_allowed(info, root)
            actual.add(relative)
        elif path.is_dir():
            if relative not in expected_directories:
                    raise TrustBootstrapError("release inventory contains an unlisted directory")
        else:
            raise TrustBootstrapError("release inventory contains a special file")
    if actual != expected:
        raise TrustBootstrapError("release inventory has an extra or omitted path")
    for relative, item in listed.items():
        path = release / relative
        info = _regular(path)
        if root is not None:
            _owner_is_allowed(info, root)
        if info.st_size != item["size"] or stat.S_IMODE(info.st_mode) != int(item["mode"], 8) or sha256_hex(path.read_bytes()) != item["sha256"]:
            raise TrustBootstrapError(f"release inventory entry is not exact: {relative}")
    for relative in ("release-manifest.json", "release-envelope.json"):
        info = _regular(release / relative)
        if root is not None:
            _owner_is_allowed(info, root)
        if stat.S_IMODE(info.st_mode) != 0o444:
            raise TrustBootstrapError(f"release metadata mode is not exact: {relative}")
    entries = [dict(listed[path]) for path in sorted(listed)]
    root_digest = sha256_hex(b"".join(canonical_json_bytes(entry) + b"\0" for entry in entries))
    if root_digest != manifest["source"]["root_digest"]:
        raise TrustBootstrapError("release source root digest is not exact")


def _validate_release_units(release: Path, manifest: Mapping[str, Any], record: Mapping[str, Any], *, root: Path | None = None) -> None:
    units: dict[str, bytes] = {}
    for item in manifest["units"]:
        path = release / "deployment/systemd" / item["name"]
        info = _regular(path)
        if root is not None:
            _owner_is_allowed(info, root)
        data = path.read_bytes()
        if info.st_size != item["size"] or sha256_hex(data) != item["sha256"]:
            raise TrustBootstrapError("release unit inventory is not exact")
        units[item["name"]] = data
    try:
        generation = verify_unit_bytes(units, manifest["build"]["unit_generation_id"])
    except (UnitVerificationError, KeyError, TypeError, ValueError) as exc:
        raise TrustBootstrapError("release unit bundle is invalid") from exc
    if generation != record.get("candidate_unit_generation_id") or manifest["build"]["unit_bundle_digest"] != record.get("unit_bundle_digest"):
        raise TrustBootstrapError("release unit bundle is not transaction-bound")


def _has_symlink_parent(path: Path, root: Path) -> bool:
    current = path.parent
    while current != root and root in current.parents:
        if current.is_symlink():
            return True
        current = current.parent
    return False


def _terminate_and_reap(process: subprocess.Popen[bytes]) -> None:
    try:
        process.terminate()
    except OSError:
        pass
    try:
        process.wait(timeout=0.2)
    except subprocess.TimeoutExpired:
        try:
            process.kill()
        except OSError:
            pass
        try:
            process.wait(timeout=1.0)
        except subprocess.TimeoutExpired as exc:
            raise TrustBootstrapError("fixed verifier process could not be reaped") from exc


def _bounded_verifier_process(argv: list[str], *, cwd: Path) -> tuple[int, bytes, bytes]:
    try:
        process = subprocess.Popen(
            argv,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env={"LC_ALL": "C", "PATH": "/usr/bin:/bin", "HOME": "/var/empty"},
            cwd=str(cwd),
            close_fds=True,
        )
    except OSError as exc:
        raise TrustBootstrapError("fixed verifier could not execute") from exc
    selector = selectors.DefaultSelector()
    output = {"stdout": bytearray(), "stderr": bytearray()}
    deadline = time.monotonic() + 10.0
    terminated = False
    try:
        for name, stream in (("stdout", process.stdout), ("stderr", process.stderr)):
            if stream is None:
                raise TrustBootstrapError("fixed verifier pipe is unavailable")
            os.set_blocking(stream.fileno(), False)
            selector.register(stream, selectors.EVENT_READ, name)
        while selector.get_map():
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                _terminate_and_reap(process)
                terminated = True
                raise TrustBootstrapError("fixed verifier timed out")
            for key, _mask in selector.select(min(remaining, 0.1)):
                stream = key.fileobj
                name = key.data
                try:
                    chunk = os.read(stream.fileno(), 4097)
                except BlockingIOError:
                    continue
                if not chunk:
                    selector.unregister(stream)
                    stream.close()
                    continue
                output[name].extend(chunk)
                if len(output[name]) > 4096:
                    _terminate_and_reap(process)
                    terminated = True
                    raise TrustBootstrapError("fixed verifier output exceeded its bound")
        try:
            returncode = process.wait(timeout=max(0.0, deadline - time.monotonic()))
        except subprocess.TimeoutExpired:
            _terminate_and_reap(process)
            terminated = True
            raise TrustBootstrapError("fixed verifier timed out")
        return returncode, bytes(output["stdout"]), bytes(output["stderr"])
    finally:
        selector.close()
        if process.poll() is None and not terminated:
            _terminate_and_reap(process)
        for stream in (process.stdout, process.stderr):
            if stream is not None and not stream.closed:
                stream.close()


def _run_fixed_verifier(path: Path, *, manifest: Path, envelope: Path, anchor: Path, approved: str, source_commit: str, staging: Path) -> Mapping[str, Any]:
    if staging.exists() and staging.is_symlink():
        raise TrustBootstrapError("fixed verifier staging path contains a symlink")
    staging.mkdir(parents=True, exist_ok=True, mode=0o700)
    os.chmod(staging, 0o700)
    argv = [
        str(path), "--manifest", str(manifest), "--envelope", str(envelope),
        "--anchor", str(anchor), "--approved-anchor-fingerprint", approved,
        "--expected-source-commit", source_commit, "--staging", str(staging),
    ]
    returncode, stdout, stderr = _bounded_verifier_process(argv, cwd=staging)
    if returncode != 0 or stderr:
        raise TrustBootstrapError("fixed verifier rejected the release")
    try:
        value = parse_canonical_json(stdout)
    except ManifestError as exc:
        raise TrustBootstrapError("fixed verifier output is not canonical") from exc
    expected = {
        "release_id", "manifest_sha256", "source_commit", "source_tree", "source_root_digest", "approval_id",
        "approval_payload_digest", "anchor_fingerprint", "test_evidence_digest",
        "openssl_identity", "openssl_version", "accepted_key_ids", "signature_results",
    }
    if not isinstance(value, Mapping) or set(value) != expected:
        raise TrustBootstrapError("fixed verifier output fields are not exact")
    return dict(value)


def _write_evidence(path: Path, evidence: Mapping[str, Any], root: Path) -> Path:
    if set(evidence) != set(_EVIDENCE_FIELDS):
        raise TrustBootstrapError("trust evidence fields are not exact")
    data = canonical_json_bytes(dict(evidence))
    if _has_symlink_parent(path, root):
        raise TrustBootstrapError("trust evidence parent contains a symlink")
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o755)
    os.chmod(path.parent, 0o755)
    if path.exists() or path.is_symlink():
        existing_info, existing = _stable_existing_evidence(path, root)
        _owner_is_allowed(existing_info, root)
        if stat.S_IMODE(existing_info.st_mode) != 0o444:
            raise TrustBootstrapError("trust evidence mode is not exact")
        stable_fields = set(_EVIDENCE_FIELDS) - {"verified_at_utc"}
        if any(existing.get(field) != evidence.get(field) for field in stable_fields):
            raise TrustBootstrapError("trust evidence conflict cannot be overwritten")
        return path
    temporary = path.with_name(f".{path.name}.tmp-{os.getpid()}-{secrets.token_hex(8)}")
    try:
        fd = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o444)
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
            os.fchmod(stream.fileno(), 0o444)
        os.link(temporary, path)
        os.unlink(temporary)
        created_info = path.lstat()
        _owner_is_allowed(created_info, root)
        if stat.S_IMODE(created_info.st_mode) != 0o444:
            raise TrustBootstrapError("trust evidence mode is not exact")
        directory_fd = os.open(path.parent, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
    except FileExistsError:
        try:
            if path.exists():
                _existing_info, existing = _stable_existing_evidence(path, root)
                stable_fields = set(_EVIDENCE_FIELDS) - {"verified_at_utc"}
                if not any(existing.get(field) != evidence.get(field) for field in stable_fields):
                    return path
        finally:
            temporary.unlink(missing_ok=True)
        raise TrustBootstrapError("trust evidence conflict cannot be overwritten")
    except OSError as exc:
        temporary.unlink(missing_ok=True)
        raise TrustBootstrapError("trust evidence could not be durably written") from exc
    return path


def _stable_existing_evidence(path: Path, root: Path) -> tuple[os.stat_result, Mapping[str, Any]]:
    """Wait out the internal hard-link publication window before reading."""

    deadline = time.monotonic() + 1.0
    while True:
        try:
            info = path.lstat()
        except OSError as exc:
            raise TrustBootstrapError("trust evidence cannot be inspected") from exc
        if info.st_nlink == 1:
            _regular(path)
            return info, _read_canonical(path)
        if time.monotonic() >= deadline:
            raise TrustBootstrapError("trust evidence has ambiguous hard-link identity")
        time.sleep(0.001)


def verify_candidate_before_pending(
    root: str | Path,
    *,
    transaction_id: str,
    release_id: str,
    candidate_unit_generation_id: str | None = None,
    unit_bundle_digest: str | None = None,
    expected_source_commit: str | None = None,
) -> Mapping[str, Any]:
    """Verify trust and persist its proof before a pending record is allowed."""

    base = ensure_temporary_root(root) if Path(root) != Path("/") else Path("/")
    release = _under(base, Path("/opt/aether/releases") / release_id)
    manifest_path = release / "release-manifest.json"
    envelope_path = release / "release-envelope.json"
    anchor_path = _under(base, TRUST_ANCHOR)
    evidence_path = trust_evidence_path(base, transaction_id)
    manifest = _read_canonical(manifest_path)
    try:
        normalized = validate_manifest(manifest)
    except ManifestError as exc:
        raise TrustBootstrapError("candidate manifest is invalid") from exc
    if normalized["release_id"] != release_id or sha256_hex(manifest_path.read_bytes()) != release_id[3:]:
        raise TrustBootstrapError("candidate release identity is not manifest-derived")
    if expected_source_commit is not None and manifest["source"]["commit"] != expected_source_commit:
        raise TrustBootstrapError("candidate source identity is not expected")
    _validate_inventory(release, manifest, root=base)
    _validate_release_units(
        release,
        manifest,
        {"candidate_unit_generation_id": candidate_unit_generation_id or normalized["build"]["unit_generation_id"], "unit_bundle_digest": unit_bundle_digest or normalized["build"]["unit_bundle_digest"]},
        root=base,
    )
    anchor = _read_canonical(anchor_path)
    _owner_is_allowed(_regular(anchor_path), base)
    approved = _read_approved_fingerprint(_under(base, APPROVED_ANCHOR), base)
    verifier, verifier_digest = fixed_verifier_identity(base)
    staging = _under(base, Path("var/lib/aether/install") / transaction_id / "verify")
    result = _run_fixed_verifier(
        verifier, manifest=manifest_path, envelope=envelope_path, anchor=anchor_path,
        approved=approved, source_commit=manifest["source"]["commit"], staging=staging,
    )
    if (
        result["release_id"] != release_id
        or result["manifest_sha256"] != release_id[3:]
        or result["source_commit"] != manifest["source"]["commit"]
        or result["source_tree"] != manifest["source"]["tree"]
        or result["source_root_digest"] != manifest["source"]["root_digest"]
        or result["anchor_fingerprint"] != approved
    ):
        raise TrustBootstrapError("fixed verifier result is not transaction-bound")
    if result["test_evidence_digest"] != _read_approved_digest(_under(base, APPROVED_TEST_EVIDENCE), base):
        raise TrustBootstrapError("approval test evidence is not independently approved")
    dependencies = manifest["dependencies"]
    if dependencies["closure_status"] == "COMPLETE":
        lock_path = release / "deployment/requirements.lock.json"
        wheelhouse = release / "deployment/wheelhouse"
        if not lock_path.is_file() or not wheelhouse.is_dir():
            raise TrustBootstrapError("candidate dependency closure artifacts are missing")
        try:
            if sha256_hex(lock_path.read_bytes()) != dependencies["lock_digest"]:
                raise TrustBootstrapError("dependency lock digest is not bound to the manifest")
            verify_dependency_closure(lock_path, wheelhouse)
        except (DependencyLockError, KeyError, TypeError, ValueError) as exc:
            raise TrustBootstrapError("candidate dependency closure is not complete") from exc
    evidence = {
        "evidence_version": 1,
        "status": "VERIFIED",
        "transaction_id": transaction_id,
        "release_id": release_id,
        "manifest_sha256": release_id[3:],
        "source_commit": manifest["source"]["commit"],
        "source_tree": manifest["source"]["tree"],
        "source_root_digest": manifest["source"]["root_digest"],
        "approval_id": result["approval_id"],
        "approval_payload_digest": result["approval_payload_digest"],
        "test_evidence_digest": result["test_evidence_digest"],
        "anchor_fingerprint": approved,
        "verifier_sha256": verifier_digest,
        "verifier_version": "aether-release-verify.v1",
        "openssl_identity": result["openssl_identity"],
        "openssl_version": result["openssl_version"],
        "accepted_key_ids": result["accepted_key_ids"],
        "signature_results": result["signature_results"],
        "dependency_lock_digest": manifest["dependencies"]["lock_digest"],
        "unit_generation_id": manifest["build"]["unit_generation_id"],
        "unit_bundle_digest": manifest["build"]["unit_bundle_digest"],
        "verified_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    if evidence_path.exists():
        existing = _read_canonical(evidence_path)
        if set(existing) != set(_EVIDENCE_FIELDS):
            raise TrustBootstrapError("existing trust evidence fields are not exact")
        try:
            verified_at = datetime.fromisoformat(str(existing["verified_at_utc"]).replace("Z", "+00:00"))
            if verified_at.tzinfo is None or verified_at.utcoffset() != timezone.utc.utcoffset(verified_at):
                raise ValueError
        except (TypeError, ValueError) as exc:
            raise TrustBootstrapError("existing trust evidence timestamp is invalid") from exc
        stable_fields = set(_EVIDENCE_FIELDS) - {"verified_at_utc"}
        if any(existing[field] != evidence[field] for field in stable_fields):
            raise TrustBootstrapError("trust evidence conflict cannot be overwritten")
        evidence["verified_at_utc"] = existing["verified_at_utc"]
    _write_evidence(evidence_path, evidence, base)
    return evidence
