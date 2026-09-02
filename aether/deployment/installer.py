"""Temporary-root repository installer primitives.

This module intentionally has no default host target and no shell command path.
"""

from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime, timezone
import fcntl
import hashlib
import os
from pathlib import Path
import re
import shutil
import stat
from typing import Any, Iterator, Mapping

from .lifecycle import (
    ActivationState,
    LifecycleError,
    TemporaryRootCapability,
    QuiescenceProof,
    ensure_temporary_root,
    _path_has_symlink,
    _require_capability,
    transition,
    validate_record,
    write_record,
)
from .unit_verifier import UNIT_NAMES, canonical_unit_bundle_digest, generation_id, install_generation_gate, verify_unit_bytes
from .trust_bootstrap import TrustBootstrapError, verify_candidate_before_pending
from .manifest_schema import ManifestError, canonical_json_bytes, validate_manifest


class InstallError(RuntimeError):
    """Raised when a staged installation cannot be proven safe."""


def _safe_relative(value: str) -> Path:
    path = Path(value)
    if not value or path.is_absolute() or ".." in path.parts or path == Path("."):
        raise InstallError("release path is not safe relative content")
    return path


def _write_durable_new_file(path: Path, data: bytes, mode: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o755)
    fd = os.open(
        path,
        os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
        mode,
    )
    try:
        with os.fdopen(fd, "wb") as stream:
            fd = -1
            stream.write(data)
            stream.flush()
            os.fchmod(stream.fileno(), mode)
            os.fsync(stream.fileno())
    finally:
        if fd >= 0:
            os.close(fd)
    directory_fd = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        os.fsync(directory_fd)
    finally:
        os.close(directory_fd)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _copy_regular_file(source: Path, destination_directory_fd: int, name: str) -> None:
    source_fd = os.open(source, os.O_RDONLY | os.O_NOFOLLOW)
    try:
        before = os.fstat(source_fd)
        if not stat.S_ISREG(before.st_mode) or before.st_nlink != 1:
            raise InstallError("release source is not an unambiguous regular file")
        chunks: list[bytes] = []
        remaining = before.st_size
        while remaining:
            chunk = os.read(source_fd, min(1024 * 1024, remaining))
            if not chunk:
                raise InstallError("release source changed during read")
            chunks.append(chunk)
            remaining -= len(chunk)
        after = os.fstat(source_fd)
        if (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns) != (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns):
            raise InstallError("release source changed during hashing")
    finally:
        os.close(source_fd)
    fd = os.open(name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, stat.S_IMODE(before.st_mode), dir_fd=destination_directory_fd)
    try:
        for chunk in chunks:
            view = memoryview(chunk)
            while view:
                written = os.write(fd, view)
                if written <= 0:
                    raise InstallError("release write made no progress")
                view = view[written:]
        os.fsync(fd)
        target_info = os.fstat(fd)
        if not stat.S_ISREG(target_info.st_mode) or target_info.st_nlink != 1 or target_info.st_size != before.st_size:
            raise InstallError("release target identity is ambiguous")
    finally:
        os.close(fd)
    os.fsync(destination_directory_fd)


def make_activation_record(
    *,
    transaction_id: str,
    candidate_release_id: str,
    candidate_manifest_digest: str,
    candidate_unit_generation_id: str,
    unit_bundle_digest: str,
    host_boot_id: str,
    old_release_id: str | None = None,
    old_manifest_digest: str | None = None,
    old_unit_generation_id: str | None = None,
    record_sequence: int = 0,
    activation_reason: str = "FIRST_INSTALL",
    schema_before: int = 1,
    schema_after: int = 1,
) -> dict[str, Any]:
    now = _utc_now()
    return {
        "record_version": 1,
        "state": ActivationState.CANDIDATE_PENDING.value,
        "transaction_id": transaction_id,
        "record_sequence": record_sequence,
        "previous_record_digest": None,
        "host_boot_id": host_boot_id,
        "activation_issued_at_monotonic": 0.0,
        "activation_expires_at_monotonic": 60.0,
        "activation_max_duration_seconds": 60,
        "old_release_id": old_release_id,
        "old_manifest_digest": old_manifest_digest,
        "candidate_release_id": candidate_release_id,
        "candidate_manifest_digest": candidate_manifest_digest,
        "current_link_release_id": None,
        "old_unit_generation_id": old_unit_generation_id,
        "candidate_unit_generation_id": candidate_unit_generation_id,
        "unit_bundle_digest": unit_bundle_digest,
        "quiesce_state": "NOT_STARTED",
        "schema_before": schema_before,
        "schema_after": schema_after,
        "schema_compatibility": "UNCHANGED" if schema_before == schema_after else "FORWARD_MIGRATION_REQUIRED",
        "migration_state": "NOT_STARTED",
        "readiness_result": "NOT_RUN",
        "smoke_result": "NOT_RUN",
        "commit_state": "UNCOMMITTED",
        "rollback_state": "NOT_REQUESTED",
        "activation_reason": activation_reason,
        "created_at_utc": now,
        "updated_at_utc": now,
    }


@contextmanager
def install_lock(root: str | Path, *, capability: TemporaryRootCapability) -> Iterator[None]:
    try:
        base = _require_capability(root, capability, purpose="M122A_INSTALLER")
    except LifecycleError as exc:
        raise InstallError("installer capability is invalid") from exc
    path = base / "run/lock/aether-install.lock"
    if _path_has_symlink(path.parent):
        raise InstallError("installer lock path contains a symlink")
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o755)
    with path.open("a+", encoding="ascii") as stream:
        fcntl.flock(stream.fileno(), fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(stream.fileno(), fcntl.LOCK_UN)


class RepositoryInstaller:
    """Operate only below an explicitly supplied non-host root."""

    def __init__(self, root: str | Path, *, capability: TemporaryRootCapability | None = None) -> None:
        if capability is None:
            raise InstallError("an explicit isolated-root capability is required")
        self.root = ensure_temporary_root(root)
        try:
            _require_capability(self.root, capability, purpose="M122A_INSTALLER")
        except LifecycleError as exc:
            raise InstallError("temporary-root capability is invalid") from exc
        self.capability = capability
        self.install_root = self.root / "var/lib/aether/install"

    def stage_release(
        self,
        transaction_id: str,
        release_id: str,
        source_root: str | Path,
        *,
        manifest: Mapping[str, Any] | None = None,
        envelope: Mapping[str, Any] | None = None,
    ) -> Path:
        if not re.fullmatch(r"r1-[0-9a-f]{64}", release_id) or not re.fullmatch(r"[A-Za-z0-9_.:-]{1,128}", transaction_id):
            raise InstallError("release or transaction identity is invalid")
        try:
            _require_capability(self.root, self.capability, purpose="M122A_INSTALLER", transaction_id=transaction_id)
        except LifecycleError as exc:
            raise InstallError("transaction-bound installer capability is required") from exc
        source = Path(source_root)
        if not source.is_absolute() or source.is_symlink() or not source.is_dir() or source.resolve() == Path("/"):
            raise InstallError("explicit source directory is required")
        source = source.resolve()
        if (source / ".git").exists():
            raise InstallError("development checkout cannot be staged as a release")
        staging = self.install_root / transaction_id / "release"
        staging.mkdir(parents=True, exist_ok=False, mode=0o700)
        for path in sorted(source.rglob("*")):
            relative = path.relative_to(source)
            if path.is_symlink() or (not path.is_file() and not path.is_dir()):
                raise InstallError("release contains a symlink or special file")
            target = staging / _safe_relative(relative.as_posix())
            if path.is_dir():
                target.mkdir(mode=0o555)
                os.chmod(target, 0o555, follow_symlinks=False)
            else:
                target.parent.mkdir(parents=True, exist_ok=True, mode=0o555)
                if _path_has_symlink(target.parent):
                    raise InstallError("release destination contains a symlink")
                parent_fd = os.open(target.parent, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
                try:
                    _copy_regular_file(path, parent_fd, target.name)
                finally:
                    os.close(parent_fd)
        if manifest is not None:
            try:
                normalized = validate_manifest(manifest)
            except ManifestError as exc:
                raise InstallError("release manifest is invalid") from exc
            if normalized["release_id"] != release_id:
                raise InstallError("release ID is not manifest-derived")
            (staging / "release-manifest.json").write_bytes(canonical_json_bytes(dict(manifest)))
            os.chmod(staging / "release-manifest.json", 0o444)
        if envelope is not None:
            (staging / "release-envelope.json").write_bytes(canonical_json_bytes(dict(envelope)))
            os.chmod(staging / "release-envelope.json", 0o444)
        release_root = self.root / "opt/aether/releases"
        if _path_has_symlink(release_root):
            raise InstallError("release destination contains a symlink")
        release_root.mkdir(parents=True, exist_ok=True, mode=0o755)
        target = release_root / release_id
        if target.exists() or target.is_symlink():
            raise InstallError("release identity already exists")
        os.replace(staging, target)
        directory_fd = os.open(release_root, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
        return target

    def replace_unit_bundle(
        self,
        units: Mapping[str, bytes],
        transaction_id: str,
        *,
        activation_record: Mapping[str, Any],
        quiescence_proof: QuiescenceProof,
        current_boot_id: str,
        now: float,
        adapter_identity: str,
    ) -> tuple[str, str]:
        try:
            validate_record(activation_record)
        except LifecycleError as exc:
            raise InstallError("activation record is invalid") from exc
        if activation_record["transaction_id"] != transaction_id:
            raise InstallError("activation record transaction does not match")
        try:
            _require_capability(self.root, self.capability, purpose="M122A_INSTALLER", transaction_id=transaction_id)
        except LifecycleError as exc:
            raise InstallError("transaction-bound installer capability is required") from exc
        try:
            quiescence_proof.validate(
                activation_record,
                current_boot_id=current_boot_id,
                now=now,
                adapter_identity=adapter_identity,
            )
        except LifecycleError as exc:
            raise InstallError("unit replacement requires transaction-bound quiescence") from exc
        try:
            generation = generation_id(units)
            verify_unit_bytes(units, generation)
        except Exception as exc:
            raise InstallError("candidate unit bundle failed verification") from exc
        if activation_record["candidate_unit_generation_id"] != generation:
            raise InstallError("unit generation does not match activation record")
        staging = self.install_root / transaction_id / "units"
        staging.mkdir(parents=True, exist_ok=False, mode=0o700)
        for name in UNIT_NAMES:
            path = staging / name
            path.write_bytes(units[name])
            os.chmod(path, 0o644)
        live = self.root / "etc/systemd/system"
        if _path_has_symlink(live):
            raise InstallError("unit destination contains a symlink")
        live.mkdir(parents=True, exist_ok=True, mode=0o755)
        if _path_has_symlink(live):
            raise InstallError("unit destination contains a symlink")
        live_fd = os.open(live, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
        # Each rename is independently durable; the gate is installed last.
        try:
            for name in UNIT_NAMES:
                temporary_name = f".{name}.{transaction_id}.tmp"
                fd = os.open(temporary_name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o644, dir_fd=live_fd)
                with os.fdopen(fd, "wb") as stream:
                    stream.write(units[name])
                    stream.flush()
                    os.fsync(stream.fileno())
                os.rename(temporary_name, name, src_dir_fd=live_fd, dst_dir_fd=live_fd)
                os.fsync(live_fd)
        finally:
            os.close(live_fd)
        gate = install_generation_gate(self.root, generation, units, transaction_id, capability=self.capability)
        return generation, hashlib.sha256(gate.read_bytes()).hexdigest()

    def activate_current(self, release_id: str, *, transaction_id: str) -> Path:
        try:
            _require_capability(self.root, self.capability, purpose="M122A_INSTALLER", transaction_id=transaction_id)
        except LifecycleError as exc:
            raise InstallError("transaction-bound installer capability is required") from exc
        if not re.fullmatch(r"r1-[0-9a-f]{64}", release_id):
            raise InstallError("release identity is invalid")
        release = self.root / "opt/aether/releases" / release_id
        if not release.is_dir() or release.is_symlink():
            raise InstallError("candidate release is not a regular directory")
        current = self.root / "opt/aether/current"
        if _path_has_symlink(current.parent):
            raise InstallError("current-link parent contains a symlink")
        current.parent.mkdir(parents=True, exist_ok=True, mode=0o755)
        if _path_has_symlink(current.parent):
            raise InstallError("current-link parent contains a symlink")
        directory_fd = os.open(current.parent, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
        temporary_name = f".current.{release_id}.tmp"
        try:
            try:
                os.unlink(temporary_name, dir_fd=directory_fd)
            except FileNotFoundError:
                pass
            os.symlink(f"releases/{release_id}", temporary_name, dir_fd=directory_fd)
            os.rename(temporary_name, current.name, src_dir_fd=directory_fd, dst_dir_fd=directory_fd)
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
        return current

    def write_pending(self, record: Mapping[str, Any]) -> Path:
        if record.get("state") != ActivationState.CANDIDATE_PENDING.value:
            raise InstallError("only pending candidate records may be initially written")
        try:
            _require_capability(
                self.root,
                self.capability,
                purpose="M122A_INSTALLER",
                transaction_id=str(record["transaction_id"]),
            )
            verify_candidate_before_pending(
                self.root,
                transaction_id=str(record["transaction_id"]),
                release_id=str(record["candidate_release_id"]),
                candidate_unit_generation_id=str(record["candidate_unit_generation_id"]),
                unit_bundle_digest=str(record["unit_bundle_digest"]),
            )
        except (TrustBootstrapError, KeyError, TypeError, ValueError) as exc:
            raise InstallError("root trust verification is required before CANDIDATE_PENDING") from exc
        return write_record(self.root, record, capability=self.capability, purpose="M122A_INSTALLER")

    def install_fixed_verifier(self, source: str | Path | None = None) -> Path:
        """Install the repository verifier as an immutable isolated-root artifact."""

        try:
            _require_capability(self.root, self.capability, purpose="M122A_INSTALLER")
        except LifecycleError as exc:
            raise InstallError("installer capability is invalid") from exc
        source_path = Path(source) if source is not None else Path(__file__).resolve().parents[2] / "deployment/fixed_verifier/aether-release-verify"
        source_info = source_path.lstat()
        if source_path.is_symlink() or not stat.S_ISREG(source_info.st_mode) or source_info.st_nlink != 1:
            raise InstallError("fixed verifier source is not an unambiguous regular file")
        destination = self.root / "usr/libexec/aether-release-verify"
        if destination.exists() or destination.is_symlink():
            raise InstallError("fixed verifier destination already exists")
        try:
            _write_durable_new_file(destination, source_path.read_bytes(), 0o555)
        except (FileExistsError, OSError) as exc:
            raise InstallError("fixed verifier destination could not be durably installed") from exc
        digest = hashlib.sha256(destination.read_bytes()).hexdigest()
        approval = self.root / "etc/aether/release-verifier.sha256"
        try:
            _write_durable_new_file(approval, (digest + "\n").encode("ascii"), 0o444)
        except (FileExistsError, OSError) as exc:
            raise InstallError("fixed verifier approval could not be durably installed") from exc
        return destination
