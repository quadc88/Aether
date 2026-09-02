"""Bounded first-install rollback foundation for isolated temporary roots.

This module deliberately contains no production account management, systemd,
shell, or host-path adapter.  All filesystem effects require the capability
issued for one isolated root, and all effects outside that root are injected
through the narrow :class:`PrivilegedEffectAdapter` protocol.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import time
from typing import Any, Callable, Iterator, Mapping, Protocol

from .lifecycle import (
    LifecycleError,
    TemporaryRootCapability,
    _path_has_symlink,
    _require_capability,
    ensure_temporary_root,
)
from .manifest_schema import canonical_json_bytes, parse_canonical_json


PROFILE = "FIRST_INSTALL_LOCAL_AF_UNIX_ONLY"
DEPLOYMENT_STATE = "NOT_DEPLOYED"
ROLLBACK_JOURNAL = Path("var/lib/aether/rollback/rollback-journal.jsonl")
RECEIPT_JOURNAL = Path("var/lib/aether/rollback/rollback-receipts.jsonl")
ROLLBACK_LOCK = Path("var/lib/aether/rollback/rollback.lock")
_DIGEST = re.compile(r"^[0-9a-f]{64}$")
_TRANSACTION_ID = re.compile(r"^[A-Za-z0-9_.:-]{1,128}$")
_STEP_ID = re.compile(r"^[A-Za-z0-9_.:-]{1,128}$")
_COMMIT = re.compile(r"^[0-9a-f]{40,64}$")
_SAFE_VALUE = re.compile(r"^[A-Za-z0-9_.:/@+-]{1,256}$")
_FORBIDDEN_TERMS = (
    "password",
    "private key",
    "private_key",
    "secret",
    "credential",
    "machine-id",
    "machine_id",
    "boot_id",
    "boot-id",
)


class RollbackError(RuntimeError):
    """Base error for a rollback foundation operation."""


class RollbackInterrupted(RollbackError):
    """Injected crash point; durable evidence is intentionally retained."""


class RollbackStorageError(RollbackError):
    """Durability boundary could not be completed."""


class RollbackState(str, Enum):
    ROLLBACK_REQUESTED = "ROLLBACK_REQUESTED"
    ROLLBACK_VALIDATING = "ROLLBACK_VALIDATING"
    ROLLBACK_IN_PROGRESS = "ROLLBACK_IN_PROGRESS"
    ROLLBACK_VERIFYING = "ROLLBACK_VERIFYING"
    ROOT_REVIEW_REQUIRED = "ROOT_REVIEW_REQUIRED"
    ROLLED_BACK_NOT_DEPLOYED = "ROLLED_BACK_NOT_DEPLOYED"


class RollbackResult(str, Enum):
    ROLLED_BACK_NOT_DEPLOYED = "ROLLED_BACK_NOT_DEPLOYED"
    PARTIAL_ROLLBACK_ROOT_REVIEW_REQUIRED = "PARTIAL_ROLLBACK_ROOT_REVIEW_REQUIRED"
    REJECTED_PRECONDITION = "REJECTED_PRECONDITION"
    REJECTED_IDENTITY_MISMATCH = "REJECTED_IDENTITY_MISMATCH"
    REJECTED_CONFLICT = "REJECTED_CONFLICT"
    REJECTED_EXPIRED = "REJECTED_EXPIRED"
    REJECTED_UNSUPPORTED_PROFILE = "REJECTED_UNSUPPORTED_PROFILE"


class PrivilegedOperation(str, Enum):
    STOP_SELECTED_OAS_SERVICE_SOCKET_SET = "STOP_SELECTED_OAS_SERVICE_SOCKET_SET"
    VERIFY_SELECTED_SERVICE_SOCKET_ABSENCE = "VERIFY_SELECTED_SERVICE_SOCKET_ABSENCE"
    REMOVE_TRANSACTION_CREATED_PRINCIPAL_GROUP = "REMOVE_TRANSACTION_CREATED_PRINCIPAL_GROUP"
    VERIFY_TRANSACTION_CREATED_PRINCIPAL_GROUP_ABSENCE = "VERIFY_TRANSACTION_CREATED_PRINCIPAL_GROUP_ABSENCE"
    VERIFY_EXACT_UNIT_ABSENCE = "VERIFY_EXACT_UNIT_ABSENCE"
    VERIFY_PROCESS_ABSENCE = "VERIFY_PROCESS_ABSENCE"
    VERIFY_SOCKET_ABSENCE = "VERIFY_SOCKET_ABSENCE"


class PrivilegedRequestPhase(str, Enum):
    APPLY = "APPLY"
    OBSERVE = "OBSERVE"


def _require_digest(value: str, name: str) -> None:
    if not isinstance(value, str) or not _DIGEST.fullmatch(value):
        raise ValueError(f"{name} must be a lowercase SHA-256 digest")


def _require_no_secret(value: str, name: str) -> None:
    folded = value.casefold()
    if any(term in folded for term in _FORBIDDEN_TERMS):
        raise ValueError(f"{name} contains forbidden sensitive material")


def _require_bounded_string(value: str, name: str) -> None:
    if not isinstance(value, str) or not _SAFE_VALUE.fullmatch(value):
        raise ValueError(f"{name} is not bounded")
    _require_no_secret(value, name)


def _parse_utc(value: str, name: str) -> datetime:
    if not isinstance(value, str):
        raise ValueError(f"{name} is not UTC")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"{name} is not UTC") from exc
    if parsed.tzinfo is None or parsed.utcoffset() != timezone.utc.utcoffset(parsed):
        raise ValueError(f"{name} must include UTC")
    return parsed.astimezone(timezone.utc)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_relative_path(value: str) -> str:
    if not isinstance(value, str) or not value or value.startswith("/") or "\\" in value:
        raise ValueError("rollback path must be relative")
    parts = value.split("/")
    if any(not part or part in {".", ".."} for part in parts):
        raise ValueError("rollback path contains traversal")
    _require_no_secret(value, "rollback path")
    return value


def _digest_payload(value: Any) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


@dataclass(frozen=True, slots=True)
class RollbackTransactionIdentity:
    transaction_id: str
    deployment_profile: str
    target_host_identity_digest: str
    boot_digest: str
    source_commit: str
    release_id: str
    manifest_digest: str
    mutation_manifest_digest: str
    rollback_manifest_digest: str
    authorization_digest: str
    created_at_utc: str
    expires_at_utc: str
    record_sequence: int

    def __post_init__(self) -> None:
        if not _TRANSACTION_ID.fullmatch(self.transaction_id):
            raise ValueError("transaction ID is invalid")
        if self.deployment_profile != PROFILE:
            raise ValueError("unsupported deployment profile")
        if not _COMMIT.fullmatch(self.source_commit):
            raise ValueError("source commit is invalid")
        if not re.fullmatch(r"r1-[0-9a-f]{64}", self.release_id):
            raise ValueError("release ID is invalid")
        for name in (
            "target_host_identity_digest",
            "boot_digest",
            "manifest_digest",
            "mutation_manifest_digest",
            "rollback_manifest_digest",
            "authorization_digest",
        ):
            _require_digest(getattr(self, name), name)
        created = _parse_utc(self.created_at_utc, "created_at_utc")
        expires = _parse_utc(self.expires_at_utc, "expires_at_utc")
        if expires <= created:
            raise ValueError("rollback authorization expiry is not after creation")
        if not isinstance(self.record_sequence, int) or isinstance(self.record_sequence, bool) or self.record_sequence < 0:
            raise ValueError("record sequence is invalid")

    def as_dict(self) -> dict[str, Any]:
        return {
            "transaction_id": self.transaction_id,
            "deployment_profile": self.deployment_profile,
            "target_host_identity_digest": self.target_host_identity_digest,
            "boot_digest": self.boot_digest,
            "source_commit": self.source_commit,
            "release_id": self.release_id,
            "manifest_digest": self.manifest_digest,
            "mutation_manifest_digest": self.mutation_manifest_digest,
            "rollback_manifest_digest": self.rollback_manifest_digest,
            "authorization_digest": self.authorization_digest,
            "created_at_utc": self.created_at_utc,
            "expires_at_utc": self.expires_at_utc,
            "record_sequence": self.record_sequence,
        }


@dataclass(frozen=True, slots=True)
class CreatedObjectRecord:
    transaction_id: str
    step_id: str
    object_class: str
    logical_target: str
    root_relative_path: str | None
    pre_existing_state: str
    expected_type: str
    expected_ownership_identity: str
    expected_mode: int | None
    expected_content_or_metadata_digest: str
    creation_evidence_digest: str
    dependency_order: int
    inverse_action: str
    automatic_rollback_permitted: bool
    privileged_operation: str | None = None

    def __post_init__(self) -> None:
        if not _TRANSACTION_ID.fullmatch(self.transaction_id) or not _STEP_ID.fullmatch(self.step_id):
            raise ValueError("object transaction or step identity is invalid")
        for name in ("object_class", "logical_target", "expected_type", "expected_ownership_identity", "inverse_action"):
            _require_bounded_string(getattr(self, name), name)
        if self.root_relative_path is not None:
            _safe_relative_path(self.root_relative_path)
        if self.pre_existing_state not in {"ABSENT", "PRESENT"}:
            raise ValueError("pre-existing state is invalid")
        if self.expected_type not in {"regular", "directory", "symlink", "privileged"}:
            raise ValueError("expected object type is invalid")
        if self.expected_mode is not None and (
            not isinstance(self.expected_mode, int)
            or isinstance(self.expected_mode, bool)
            or not 0 <= self.expected_mode <= 0o7777
        ):
            raise ValueError("expected mode is invalid")
        _require_digest(self.expected_content_or_metadata_digest, "expected content or metadata digest")
        _require_digest(self.creation_evidence_digest, "creation evidence digest")
        if not isinstance(self.dependency_order, int) or isinstance(self.dependency_order, bool) or self.dependency_order < 0:
            raise ValueError("dependency ordering is invalid")
        if not isinstance(self.automatic_rollback_permitted, bool):
            raise ValueError("automatic rollback permission is invalid")
        if self.expected_type == "privileged":
            if self.root_relative_path is not None or self.privileged_operation not in {
                operation.value for operation in PrivilegedOperation
            }:
                raise ValueError("privileged object binding is invalid")
        elif self.root_relative_path is None or self.privileged_operation is not None:
            raise ValueError("filesystem object binding is invalid")
        _require_no_secret(self.logical_target, "logical target")

    def as_dict(self) -> dict[str, Any]:
        return {
            "transaction_id": self.transaction_id,
            "step_id": self.step_id,
            "object_class": self.object_class,
            "logical_target": self.logical_target,
            "root_relative_path": self.root_relative_path,
            "pre_existing_state": self.pre_existing_state,
            "expected_type": self.expected_type,
            "expected_ownership_identity": self.expected_ownership_identity,
            "expected_mode": self.expected_mode,
            "expected_content_or_metadata_digest": self.expected_content_or_metadata_digest,
            "creation_evidence_digest": self.creation_evidence_digest,
            "dependency_order": self.dependency_order,
            "inverse_action": self.inverse_action,
            "automatic_rollback_permitted": self.automatic_rollback_permitted,
            "privileged_operation": self.privileged_operation,
        }


@dataclass(frozen=True, slots=True)
class PrivilegedEffectRequest:
    transaction_id: str
    step_id: str
    operation: str
    phase: str
    boot_digest: str
    request_digest: str

    def __post_init__(self) -> None:
        if not _TRANSACTION_ID.fullmatch(self.transaction_id) or not _STEP_ID.fullmatch(self.step_id):
            raise ValueError("privileged request identity is invalid")
        if self.operation not in {operation.value for operation in PrivilegedOperation}:
            raise ValueError("privileged operation is not allowlisted")
        if self.phase not in {phase.value for phase in PrivilegedRequestPhase}:
            raise ValueError("privileged request phase is invalid")
        _require_digest(self.boot_digest, "privileged request boot digest")
        _require_digest(self.request_digest, "privileged request digest")

    @classmethod
    def create(cls, transaction_id: str, step_id: str, operation: str, phase: str, boot_digest: str) -> "PrivilegedEffectRequest":
        payload = {
            "transaction_id": transaction_id,
            "step_id": step_id,
            "operation": operation,
            "phase": phase,
            "boot_digest": boot_digest,
        }
        return cls(transaction_id, step_id, operation, phase, boot_digest, _digest_payload(payload))

    def as_dict(self) -> dict[str, Any]:
        return {
            "transaction_id": self.transaction_id,
            "step_id": self.step_id,
            "operation": self.operation,
            "phase": self.phase,
            "boot_digest": self.boot_digest,
            "request_digest": self.request_digest,
        }


@dataclass(frozen=True, slots=True)
class PrivilegedEffectReceipt:
    transaction_id: str
    step_id: str
    adapter_identity: str
    operation: str
    request_digest: str
    observed_result: str
    observed_at_utc: str
    boot_digest: str
    evidence_digest: str

    def __post_init__(self) -> None:
        if not _TRANSACTION_ID.fullmatch(self.transaction_id) or not _STEP_ID.fullmatch(self.step_id):
            raise ValueError("privileged receipt identity is invalid")
        _require_bounded_string(self.adapter_identity, "adapter identity")
        if self.operation not in {operation.value for operation in PrivilegedOperation}:
            raise ValueError("privileged receipt operation is not allowlisted")
        _require_digest(self.request_digest, "privileged receipt request digest")
        _require_bounded_string(self.observed_result, "privileged observed result")
        _parse_utc(self.observed_at_utc, "privileged receipt timestamp")
        _require_digest(self.boot_digest, "privileged receipt boot digest")
        _require_digest(self.evidence_digest, "privileged receipt evidence digest")

    def as_dict(self) -> dict[str, Any]:
        return {
            "transaction_id": self.transaction_id,
            "step_id": self.step_id,
            "adapter_identity": self.adapter_identity,
            "operation": self.operation,
            "request_digest": self.request_digest,
            "observed_result": self.observed_result,
            "observed_at_utc": self.observed_at_utc,
            "boot_digest": self.boot_digest,
            "evidence_digest": self.evidence_digest,
        }


@dataclass(frozen=True, slots=True)
class ReceiptJournalRecord:
    receipt_sequence: int
    previous_receipt_record_digest: str | None
    current_receipt_record_digest: str
    transaction_id: str
    step_id: str
    request_phase: str
    request_digest: str
    receipt_digest: str
    boot_digest: str
    adapter_identity: str
    operation: str
    observed_result: str
    observed_at_utc: str
    evidence_digest: str
    receipt: PrivilegedEffectReceipt

    def __post_init__(self) -> None:
        if not isinstance(self.receipt_sequence, int) or isinstance(self.receipt_sequence, bool) or self.receipt_sequence < 1:
            raise ValueError("receipt sequence is invalid")
        if self.previous_receipt_record_digest is not None:
            _require_digest(self.previous_receipt_record_digest, "previous receipt record digest")
        _require_digest(self.current_receipt_record_digest, "current receipt record digest")
        if not _TRANSACTION_ID.fullmatch(self.transaction_id) or not _STEP_ID.fullmatch(self.step_id):
            raise ValueError("receipt transaction or step identity is invalid")
        if self.request_phase not in {phase.value for phase in PrivilegedRequestPhase}:
            raise ValueError("receipt request phase is invalid")
        _require_digest(self.request_digest, "receipt request digest")
        _require_digest(self.receipt_digest, "receipt digest")
        _require_digest(self.boot_digest, "receipt boot digest")
        _require_bounded_string(self.adapter_identity, "receipt adapter identity")
        if self.operation not in {operation.value for operation in PrivilegedOperation}:
            raise ValueError("receipt operation is invalid")
        _require_bounded_string(self.observed_result, "receipt observed result")
        _parse_utc(self.observed_at_utc, "receipt timestamp")
        _require_digest(self.evidence_digest, "receipt evidence digest")

    def payload(self) -> dict[str, Any]:
        return {
            "receipt_sequence": self.receipt_sequence,
            "previous_receipt_record_digest": self.previous_receipt_record_digest,
            "transaction_id": self.transaction_id,
            "step_id": self.step_id,
            "request_phase": self.request_phase,
            "request_digest": self.request_digest,
            "receipt_digest": self.receipt_digest,
            "boot_digest": self.boot_digest,
            "adapter_identity": self.adapter_identity,
            "operation": self.operation,
            "observed_result": self.observed_result,
            "observed_at_utc": self.observed_at_utc,
            "evidence_digest": self.evidence_digest,
            "receipt": self.receipt.as_dict(),
        }

    def as_dict(self) -> dict[str, Any]:
        value = self.payload()
        value["current_receipt_record_digest"] = self.current_receipt_record_digest
        return value


def make_privileged_receipt(
    request: PrivilegedEffectRequest,
    *,
    adapter_identity: str,
    observed_result: str,
    observed_at_utc: str,
    evidence_digest: str,
) -> PrivilegedEffectReceipt:
    """Build a typed fixture/adapter receipt without adding an adapter."""

    return PrivilegedEffectReceipt(
        transaction_id=request.transaction_id,
        step_id=request.step_id,
        adapter_identity=adapter_identity,
        operation=request.operation,
        request_digest=request.request_digest,
        observed_result=observed_result,
        observed_at_utc=observed_at_utc,
        boot_digest=request.boot_digest,
        evidence_digest=evidence_digest,
    )


class PrivilegedEffectAdapter(Protocol):
    """Injected, narrow contract for non-filesystem rollback effects."""

    identity: str

    def apply(self, request: PrivilegedEffectRequest) -> PrivilegedEffectReceipt: ...

    def observe(self, request: PrivilegedEffectRequest) -> PrivilegedEffectReceipt: ...


@dataclass(frozen=True, slots=True)
class RollbackJournalRecord:
    transaction_identity: RollbackTransactionIdentity
    rollback_state: str
    current_inverse_step: str | None
    previous_record_digest: str | None
    current_record_digest: str
    attempt_number: int
    observation_digest: str
    failure_classification: str
    retained_evidence_digest: str
    timestamp_utc: str
    completed_inverse_steps: tuple[str, ...] = ()
    effect_receipt_digest: str | None = None

    def __post_init__(self) -> None:
        if self.rollback_state not in {state.value for state in RollbackState}:
            raise ValueError("rollback journal state is invalid")
        if self.current_inverse_step is not None and not _STEP_ID.fullmatch(self.current_inverse_step):
            raise ValueError("current inverse step is invalid")
        if self.previous_record_digest is not None:
            _require_digest(self.previous_record_digest, "previous journal digest")
        _require_digest(self.current_record_digest, "current journal digest")
        if not isinstance(self.attempt_number, int) or isinstance(self.attempt_number, bool) or self.attempt_number < 1:
            raise ValueError("journal attempt number is invalid")
        _require_digest(self.observation_digest, "journal observation digest")
        _require_bounded_string(self.failure_classification, "journal failure classification")
        _require_digest(self.retained_evidence_digest, "journal retained evidence digest")
        _parse_utc(self.timestamp_utc, "journal timestamp")
        if any(not _STEP_ID.fullmatch(step) for step in self.completed_inverse_steps):
            raise ValueError("journal completed step is invalid")
        if self.effect_receipt_digest is not None:
            _require_digest(self.effect_receipt_digest, "journal effect receipt digest")

    def payload(self) -> dict[str, Any]:
        return {
            "transaction_identity": self.transaction_identity.as_dict(),
            "rollback_state": self.rollback_state,
            "current_inverse_step": self.current_inverse_step,
            "previous_record_digest": self.previous_record_digest,
            "attempt_number": self.attempt_number,
            "observation_digest": self.observation_digest,
            "failure_classification": self.failure_classification,
            "retained_evidence_digest": self.retained_evidence_digest,
            "timestamp_utc": self.timestamp_utc,
            "completed_inverse_steps": list(self.completed_inverse_steps),
            "effect_receipt_digest": self.effect_receipt_digest,
        }

    def as_dict(self) -> dict[str, Any]:
        value = self.payload()
        value["current_record_digest"] = self.current_record_digest
        return value


@dataclass(frozen=True, slots=True)
class FirstInstallRollbackTransaction:
    identity: RollbackTransactionIdentity
    created_objects: tuple[CreatedObjectRecord, ...]
    previous_release_id: str | None = None
    schema_migration_requested: bool = False
    adoption_requested: bool = False

    def validate(self) -> None:
        if self.previous_release_id is not None or self.schema_migration_requested or self.adoption_requested:
            raise ValueError("first-install rollback does not accept upgrade, migration, or adoption")
        if any(item.transaction_id != self.identity.transaction_id for item in self.created_objects):
            raise ValueError("created object is not transaction-bound")
        step_ids = [item.step_id for item in self.created_objects]
        if len(step_ids) != len(set(step_ids)):
            raise ValueError("created object step IDs are duplicated")
        paths = [item.root_relative_path for item in self.created_objects if item.root_relative_path is not None]
        if len(paths) != len(set(paths)):
            raise ValueError("created object paths are duplicated")
        if len({item.dependency_order for item in self.created_objects}) != len(self.created_objects):
            raise ValueError("created object dependency order is ambiguous")
        if _digest_payload([item.as_dict() for item in self.created_objects]) != self.identity.rollback_manifest_digest:
            raise ValueError("rollback manifest is not transaction-bound")


def rollback_manifest_digest(created_objects: tuple[CreatedObjectRecord, ...] | list[CreatedObjectRecord]) -> str:
    """Return the digest that must be carried by the transaction identity."""

    return _digest_payload([item.as_dict() for item in created_objects])


class _RollbackStepFailure(Exception):
    def __init__(self, classification: str, message: str) -> None:
        super().__init__(message)
        self.classification = classification


def _path_for(root: Path, relative: str) -> Path:
    _safe_relative_path(relative)
    current = root
    parts = relative.split("/")
    for part in parts[:-1]:
        current = current / part
        if current.is_symlink():
            raise _RollbackStepFailure("SYMLINK_PARENT", "rollback path has a symlink parent")
    target = root.joinpath(*parts)
    if root not in target.parents:
        raise _RollbackStepFailure("PATH_ESCAPE", "rollback path escapes isolated root")
    return target


def _owner_identity(info: os.stat_result) -> str:
    return f"{info.st_uid}:{info.st_gid}"


def _file_digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _metadata_digest(path: Path, info: os.stat_result) -> str:
    children: list[str] = []
    if stat.S_ISDIR(info.st_mode):
        children = sorted(child.name for child in path.iterdir())
    return _digest_payload(
        {
            "type": "directory" if stat.S_ISDIR(info.st_mode) else "symlink" if stat.S_ISLNK(info.st_mode) else "regular",
            "mode": stat.S_IMODE(info.st_mode),
            "owner": _owner_identity(info),
            "children": children,
            "link_target": os.readlink(path) if stat.S_ISLNK(info.st_mode) else None,
        }
    )


def _observed_object_digest(path: Path, info: os.stat_result) -> str:
    if stat.S_ISREG(info.st_mode):
        if info.st_nlink != 1:
            raise _RollbackStepFailure("HARD_LINK_IDENTITY", "regular object has ambiguous hard-link identity")
        return _file_digest(path)
    return _metadata_digest(path, info)


def _receipt_digest(receipt: PrivilegedEffectReceipt) -> str:
    return _digest_payload(receipt.as_dict())


def _observation_digest(value: Any) -> str:
    return _digest_payload(value)


class _BoundedFileLock:
    def __init__(self, path: Path, timeout: float) -> None:
        self.path = path
        self.timeout = timeout
        self.stream: Any = None

    def __enter__(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        if _path_has_symlink(self.path.parent) or self.path.is_symlink():
            raise _RollbackStepFailure("SYMLINK_LOCK_PATH", "rollback lock path contains a symlink")
        try:
            self.stream = self.path.open("a+", encoding="ascii")
            deadline = time.monotonic() + self.timeout
            while True:
                try:
                    fcntl.flock(self.stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                    return None
                except BlockingIOError:
                    if time.monotonic() >= deadline:
                        self.stream.close()
                        self.stream = None
                        raise _RollbackStepFailure("LOCK_TIMEOUT", "rollback lock acquisition timed out")
                    time.sleep(0.005)
        except OSError as exc:
            if self.stream is not None:
                self.stream.close()
                self.stream = None
            raise RollbackStorageError("rollback lock cannot be acquired") from exc

    def __exit__(self, _type: Any, _value: Any, _traceback: Any) -> None:
        if self.stream is not None:
            fcntl.flock(self.stream.fileno(), fcntl.LOCK_UN)
            self.stream.close()
            self.stream = None


class FirstInstallRollbackFoundation:
    """Execute only a transaction-bound rollback below an injected root."""

    def __init__(
        self,
        root: str | Path,
        *,
        capability: TemporaryRootCapability,
        current_boot_digest: str,
        now_utc: Callable[[], str] = _utc_now,
        fault_injector: Callable[[str], None] | None = None,
        lock_timeout_seconds: float = 0.25,
    ) -> None:
        try:
            self.root = ensure_temporary_root(root)
            _require_capability(
                self.root,
                capability,
                purpose="M125A_ROLLBACK",
            )
        except LifecycleError as exc:
            raise RollbackError("rollback requires an explicit isolated-root capability") from exc
        _require_digest(current_boot_digest, "current boot digest")
        if not 0 < lock_timeout_seconds <= 10:
            raise ValueError("rollback lock timeout is invalid")
        self.capability = capability
        self.current_boot_digest = current_boot_digest
        self.now_utc = now_utc
        self.fault_injector = fault_injector
        self.lock_timeout_seconds = lock_timeout_seconds

    @property
    def journal_path(self) -> Path:
        return self.root / ROLLBACK_JOURNAL

    @property
    def receipt_path(self) -> Path:
        return self.root / RECEIPT_JOURNAL

    def _fault(self, point: str) -> None:
        if self.fault_injector is not None:
            self.fault_injector(point)

    def _append_line(self, path: Path, value: Mapping[str, Any]) -> str:
        if _path_has_symlink(path.parent) or path.is_symlink():
            raise RollbackStorageError("rollback evidence path contains a symlink")
        path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        data = canonical_json_bytes(dict(value)) + b"\n"
        try:
            fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_APPEND | os.O_NOFOLLOW, 0o600)
            with os.fdopen(fd, "ab") as stream:
                stream.write(data)
                stream.flush()
                os.fsync(stream.fileno())
            directory_fd = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
            try:
                os.fsync(directory_fd)
            finally:
                os.close(directory_fd)
        except OSError as exc:
            raise RollbackStorageError("rollback evidence was not durable") from exc
        return hashlib.sha256(data).hexdigest()

    def _read_lines(self, path: Path) -> list[dict[str, Any]]:
        if not path.exists():
            return []
        if path.is_symlink() or not path.is_file():
            raise RollbackStorageError("rollback evidence is not a regular file")
        try:
            lines = path.read_bytes().splitlines()
            values = [parse_canonical_json(line) for line in lines if line]
        except (OSError, ValueError) as exc:
            raise RollbackStorageError("rollback evidence is unreadable") from exc
        if any(not isinstance(value, dict) for value in values):
            raise RollbackStorageError("rollback evidence record is not an object")
        return values

    def _read_journal(self) -> list[dict[str, Any]]:
        values = self._read_lines(self.journal_path)
        previous: str | None = None
        for value in values:
            current = value.get("current_record_digest")
            if current != _digest_payload({key: item for key, item in value.items() if key != "current_record_digest"}):
                raise RollbackStorageError("rollback journal record digest is invalid")
            if value.get("previous_record_digest") != previous:
                raise RollbackStorageError("rollback journal chain is broken")
            previous = current
        return values

    def _read_receipts(self, transaction_id: str | None = None) -> list[ReceiptJournalRecord]:
        values = self._read_lines(self.receipt_path)
        records: list[ReceiptJournalRecord] = []
        previous: str | None = None
        expected_sequence = 1
        request_receipts: dict[tuple[str, str, str, str], str] = {}
        for value in values:
            expected_fields = {
                "receipt_sequence",
                "previous_receipt_record_digest",
                "current_receipt_record_digest",
                "transaction_id",
                "step_id",
                "request_phase",
                "request_digest",
                "receipt_digest",
                "boot_digest",
                "adapter_identity",
                "operation",
                "observed_result",
                "observed_at_utc",
                "evidence_digest",
                "receipt",
            }
            if set(value) != expected_fields:
                raise RollbackStorageError("privileged receipt record fields are not exact")
            try:
                typed_receipt = PrivilegedEffectReceipt(**value["receipt"])
                record = ReceiptJournalRecord(
                    receipt_sequence=value["receipt_sequence"],
                    previous_receipt_record_digest=value["previous_receipt_record_digest"],
                    current_receipt_record_digest=value["current_receipt_record_digest"],
                    transaction_id=value["transaction_id"],
                    step_id=value["step_id"],
                    request_phase=value["request_phase"],
                    request_digest=value["request_digest"],
                    receipt_digest=value["receipt_digest"],
                    boot_digest=value["boot_digest"],
                    adapter_identity=value["adapter_identity"],
                    operation=value["operation"],
                    observed_result=value["observed_result"],
                    observed_at_utc=value["observed_at_utc"],
                    evidence_digest=value["evidence_digest"],
                    receipt=typed_receipt,
                )
            except (TypeError, ValueError) as exc:
                raise RollbackStorageError("privileged receipt record is malformed") from exc
            if record.receipt_sequence != expected_sequence:
                raise RollbackStorageError("privileged receipt sequence is not monotonic")
            if record.previous_receipt_record_digest != previous:
                raise RollbackStorageError("privileged receipt chain is broken")
            if record.current_receipt_record_digest != _digest_payload(record.payload()):
                raise RollbackStorageError("privileged receipt record digest is invalid")
            if (
                record.transaction_id != record.receipt.transaction_id
                or record.step_id != record.receipt.step_id
                or record.request_digest != record.receipt.request_digest
                or record.receipt_digest != _receipt_digest(record.receipt)
                or record.boot_digest != record.receipt.boot_digest
                or record.adapter_identity != record.receipt.adapter_identity
                or record.operation != record.receipt.operation
                or record.observed_result != record.receipt.observed_result
                or record.observed_at_utc != record.receipt.observed_at_utc
                or record.evidence_digest != record.receipt.evidence_digest
            ):
                raise RollbackStorageError("privileged receipt record binding is invalid")
            if transaction_id is not None and record.transaction_id != transaction_id:
                raise RollbackStorageError("privileged receipt belongs to another transaction")
            key = (record.transaction_id, record.step_id, record.request_phase, record.request_digest)
            prior_digest = request_receipts.get(key)
            if prior_digest is not None and prior_digest != record.receipt_digest:
                raise RollbackStorageError("conflicting privileged receipts exist")
            request_receipts[key] = record.receipt_digest
            records.append(record)
            previous = record.current_receipt_record_digest
            expected_sequence += 1
        return records

    def _validate_journal_binding(
        self,
        journal: list[dict[str, Any]],
        transaction: FirstInstallRollbackTransaction,
    ) -> None:
        if not journal:
            return
        expected_identity = transaction.identity.as_dict()
        known_steps = {item.step_id for item in transaction.created_objects}
        previous_attempt = 0
        for value in journal:
            if set(value) != {
                "transaction_identity",
                "rollback_state",
                "current_inverse_step",
                "previous_record_digest",
                "attempt_number",
                "observation_digest",
                "failure_classification",
                "retained_evidence_digest",
                "timestamp_utc",
                "completed_inverse_steps",
                "effect_receipt_digest",
                "current_record_digest",
            }:
                raise RollbackStorageError("rollback journal record fields are not exact")
            try:
                journal_identity = RollbackTransactionIdentity(**value["transaction_identity"])
                typed = RollbackJournalRecord(
                    transaction_identity=journal_identity,
                    rollback_state=value["rollback_state"],
                    current_inverse_step=value["current_inverse_step"],
                    previous_record_digest=value["previous_record_digest"],
                    current_record_digest=value["current_record_digest"],
                    attempt_number=value["attempt_number"],
                    observation_digest=value["observation_digest"],
                    failure_classification=value["failure_classification"],
                    retained_evidence_digest=value["retained_evidence_digest"],
                    timestamp_utc=value["timestamp_utc"],
                    completed_inverse_steps=tuple(value["completed_inverse_steps"]),
                    effect_receipt_digest=value["effect_receipt_digest"],
                )
            except (TypeError, ValueError) as exc:
                raise RollbackStorageError("rollback journal record is malformed") from exc
            if typed.as_dict() != value:
                raise RollbackStorageError("rollback journal record serialization is not exact")
            if value.get("transaction_identity") != expected_identity:
                raise RollbackStorageError("rollback journal transaction identity conflicts with request")
            if value.get("current_inverse_step") is not None and value["current_inverse_step"] not in known_steps:
                raise RollbackStorageError("rollback journal references an unknown step")
            completed = value.get("completed_inverse_steps")
            if not isinstance(completed, list) or len(completed) != len(set(completed)) or any(step not in known_steps for step in completed):
                raise RollbackStorageError("rollback journal completed-step inventory is invalid")
            attempt = value.get("attempt_number")
            if not isinstance(attempt, int) or isinstance(attempt, bool) or attempt < previous_attempt or attempt > previous_attempt + 1:
                raise RollbackStorageError("rollback journal attempt sequence is invalid")
            previous_attempt = attempt
        first = journal[0]
        if first.get("rollback_state") != RollbackState.ROLLBACK_REQUESTED.value or first.get("current_inverse_step") is not None:
            raise RollbackStorageError("rollback journal does not begin with durable rollback intent")
        try:
            first_timestamp = _parse_utc(first["timestamp_utc"], "rollback intent timestamp")
            created = _parse_utc(transaction.identity.created_at_utc, "created_at_utc")
            expires = _parse_utc(transaction.identity.expires_at_utc, "expires_at_utc")
        except (KeyError, ValueError) as exc:
            raise RollbackStorageError("rollback intent timing is invalid") from exc
        if first_timestamp < created or first_timestamp >= expires:
            raise RollbackStorageError("rollback intent was not durably created inside authorization")

    def _validate_receipt_references(
        self,
        journal: list[dict[str, Any]],
        receipts: list[ReceiptJournalRecord],
    ) -> None:
        receipt_digests = {record.receipt_digest for record in receipts}
        for value in journal:
            reference = value.get("effect_receipt_digest")
            if reference is not None and reference not in receipt_digests:
                raise RollbackStorageError("rollback journal references a missing privileged receipt")

    def _validate_receipts_for_adapter(
        self,
        transaction: FirstInstallRollbackTransaction,
        receipts: list[ReceiptJournalRecord],
        adapter: PrivilegedEffectAdapter,
    ) -> RollbackResult | None:
        by_step = {record.step_id: record for record in transaction.created_objects}
        for receipt_record in receipts:
            object_record = by_step.get(receipt_record.step_id)
            if object_record is None or object_record.expected_type != "privileged":
                raise RollbackStorageError("receipt references an unknown or non-privileged step")
            try:
                phase = PrivilegedRequestPhase(receipt_record.request_phase)
            except ValueError as exc:
                raise RollbackStorageError("receipt request phase is invalid") from exc
            request = (
                self._privileged_request(transaction, object_record, phase=phase)
                if phase is PrivilegedRequestPhase.APPLY
                else self._privileged_observe_request(transaction, object_record)
            )
            try:
                self._validate_receipt(receipt_record.receipt, request, adapter)
            except _RollbackStepFailure:
                return RollbackResult.REJECTED_IDENTITY_MISMATCH
        return None

    @staticmethod
    def _receipt_for_request(
        receipts: list[ReceiptJournalRecord],
        request: PrivilegedEffectRequest,
    ) -> ReceiptJournalRecord | None:
        matches = [
            record
            for record in receipts
            if record.transaction_id == request.transaction_id
            and record.step_id == request.step_id
            and record.request_phase == request.phase
            and record.request_digest == request.request_digest
        ]
        return matches[-1] if matches else None

    def _journal_record(
        self,
        identity: RollbackTransactionIdentity,
        state: RollbackState,
        *,
        current_step: str | None,
        previous: str | None,
        attempt: int,
        completed: tuple[str, ...],
        observation_digest: str | None = None,
        failure: str = "NONE",
        retained_evidence_digest: str | None = None,
        effect_receipt_digest: str | None = None,
    ) -> RollbackJournalRecord:
        observation = observation_digest or _observation_digest(
            {"transaction_id": identity.transaction_id, "state": state.value, "step": current_step}
        )
        retained = retained_evidence_digest or _observation_digest(
            {"transaction_id": identity.transaction_id, "journal": str(self.journal_path.relative_to(self.root))}
        )
        payload = {
            "transaction_identity": identity.as_dict(),
            "rollback_state": state.value,
            "current_inverse_step": current_step,
            "previous_record_digest": previous,
            "attempt_number": attempt,
            "observation_digest": observation,
            "failure_classification": failure,
            "retained_evidence_digest": retained,
            "timestamp_utc": self.now_utc(),
            "completed_inverse_steps": list(completed),
            "effect_receipt_digest": effect_receipt_digest,
        }
        current = _digest_payload(payload)
        return RollbackJournalRecord(
            transaction_identity=identity,
            rollback_state=state.value,
            current_inverse_step=current_step,
            previous_record_digest=previous,
            current_record_digest=current,
            attempt_number=attempt,
            observation_digest=observation,
            failure_classification=failure,
            retained_evidence_digest=retained,
            timestamp_utc=payload["timestamp_utc"],
            completed_inverse_steps=completed,
            effect_receipt_digest=effect_receipt_digest,
        )

    def _append_journal(self, record: RollbackJournalRecord) -> None:
        self._append_line(self.journal_path, record.as_dict())

    def _append_receipt(self, request: PrivilegedEffectRequest, receipt: PrivilegedEffectReceipt) -> str:
        digest = _receipt_digest(receipt)
        records = self._read_receipts(request.transaction_id)
        for record in records:
            if (
                record.step_id == request.step_id
                and record.request_phase == request.phase
                and record.request_digest == request.request_digest
            ):
                if record.receipt_digest != digest:
                    raise RollbackStorageError("conflicting receipt for one request exists")
                return digest
        previous = records[-1].current_receipt_record_digest if records else None
        payload = {
            "receipt_sequence": len(records) + 1,
            "previous_receipt_record_digest": previous,
            "transaction_id": receipt.transaction_id,
            "step_id": receipt.step_id,
            "request_phase": request.phase,
            "request_digest": receipt.request_digest,
            "receipt_digest": digest,
            "boot_digest": receipt.boot_digest,
            "adapter_identity": receipt.adapter_identity,
            "operation": receipt.operation,
            "observed_result": receipt.observed_result,
            "observed_at_utc": receipt.observed_at_utc,
            "evidence_digest": receipt.evidence_digest,
            "receipt": receipt.as_dict(),
        }
        record_digest = _digest_payload(payload)
        payload["current_receipt_record_digest"] = record_digest
        self._append_line(self.receipt_path, payload)
        return digest

    def _receipts_for_step(self, transaction_id: str, step_id: str) -> list[ReceiptJournalRecord]:
        return [record for record in self._read_receipts(transaction_id) if record.step_id == step_id]

    def _validate_request(
        self,
        transaction: FirstInstallRollbackTransaction,
        *,
        require_unexpired_authorization: bool,
    ) -> RollbackResult | None:
        try:
            transaction.validate()
        except ValueError as exc:
            message = str(exc)
            if "profile" in message or "upgrade" in message or "migration" in message or "adoption" in message:
                return RollbackResult.REJECTED_UNSUPPORTED_PROFILE
            return RollbackResult.REJECTED_IDENTITY_MISMATCH
        if transaction.identity.boot_digest != self.current_boot_digest:
            return RollbackResult.REJECTED_IDENTITY_MISMATCH
        if require_unexpired_authorization:
            try:
                now = _parse_utc(self.now_utc(), "current time")
                if now >= _parse_utc(transaction.identity.expires_at_utc, "expires_at_utc"):
                    return RollbackResult.REJECTED_EXPIRED
            except ValueError:
                return RollbackResult.REJECTED_PRECONDITION
        if any(not item.automatic_rollback_permitted for item in transaction.created_objects):
            return RollbackResult.PARTIAL_ROLLBACK_ROOT_REVIEW_REQUIRED
        return None

    def _validate_existing_identity(
        self,
        journal: list[dict[str, Any]],
        transaction: FirstInstallRollbackTransaction,
    ) -> RollbackResult | None:
        if not journal:
            return None
        first = journal[0].get("transaction_identity")
        if first != transaction.identity.as_dict():
            return RollbackResult.REJECTED_CONFLICT
        if any(value.get("transaction_identity") != first for value in journal):
            raise RollbackStorageError("rollback journal contains conflicting identities")
        last = journal[-1]
        if last.get("rollback_state") == RollbackState.ROLLED_BACK_NOT_DEPLOYED.value:
            return RollbackResult.ROLLED_BACK_NOT_DEPLOYED
        if last.get("rollback_state") == RollbackState.ROOT_REVIEW_REQUIRED.value:
            return RollbackResult.PARTIAL_ROLLBACK_ROOT_REVIEW_REQUIRED
        return None

    def _validate_terminal_receipts(
        self,
        transaction: FirstInstallRollbackTransaction,
        plan: tuple[CreatedObjectRecord, ...],
        completed: tuple[str, ...],
        journal: list[dict[str, Any]],
        adapter: PrivilegedEffectAdapter,
    ) -> RollbackResult | None:
        receipts = self._read_receipts(transaction.identity.transaction_id)
        self._validate_receipt_references(journal, receipts)
        for record in plan:
            if record.expected_type != "privileged":
                continue
            if record.step_id not in completed:
                return self._root_review(
                    transaction.identity,
                    journal[-1].get("current_record_digest"),
                    int(journal[-1]["attempt_number"]),
                    completed,
                    record.step_id,
                    "PRIVILEGED_STEP_NOT_COMPLETED",
                )
            apply_request = self._privileged_request(transaction, record, phase=PrivilegedRequestPhase.APPLY)
            observe_request = self._privileged_observe_request(transaction, record)
            apply_receipt = self._receipt_for_request(receipts, apply_request)
            observe_receipt = self._receipt_for_request(receipts, observe_request)
            if apply_receipt is None and observe_receipt is None:
                return self._root_review(
                    transaction.identity,
                    journal[-1].get("current_record_digest"),
                    int(journal[-1]["attempt_number"]),
                    completed,
                    record.step_id,
                    "MISSING_EFFECT_RECEIPT",
                )
            for receipt_record, request in ((apply_receipt, apply_request), (observe_receipt, observe_request)):
                if receipt_record is not None:
                    try:
                        self._validate_receipt(receipt_record.receipt, request, adapter)
                    except _RollbackStepFailure as exc:
                        return self._root_review(
                            transaction.identity,
                            journal[-1].get("current_record_digest"),
                            int(journal[-1]["attempt_number"]),
                            completed,
                            record.step_id,
                            exc.classification,
                        )
            if observe_receipt is None or observe_receipt.receipt.observed_result != "ABSENT":
                return self._root_review(
                    transaction.identity,
                    journal[-1].get("current_record_digest"),
                    int(journal[-1]["attempt_number"]),
                    completed,
                    record.step_id,
                    "MISSING_ABSENCE_RECEIPT",
                )
        return None

    def _verify_record_identity(self, path: Path, record: CreatedObjectRecord) -> os.stat_result:
        try:
            info = path.lstat()
        except FileNotFoundError as exc:
            raise _RollbackStepFailure("MISSING_OBJECT", "expected transaction object is missing") from exc
        if record.expected_type == "regular" and (not stat.S_ISREG(info.st_mode) or info.st_nlink != 1):
            raise _RollbackStepFailure("IDENTITY_MISMATCH", "expected unlinked regular object")
        if record.expected_type == "directory" and not stat.S_ISDIR(info.st_mode):
            raise _RollbackStepFailure("IDENTITY_MISMATCH", "expected directory object")
        if record.expected_type == "symlink" and not stat.S_ISLNK(info.st_mode):
            raise _RollbackStepFailure("IDENTITY_MISMATCH", "expected symlink object")
        if record.expected_mode is not None and stat.S_IMODE(info.st_mode) != record.expected_mode:
            raise _RollbackStepFailure("IDENTITY_MISMATCH", "object mode changed")
        if _owner_identity(info) != record.expected_ownership_identity:
            raise _RollbackStepFailure("IDENTITY_MISMATCH", "object ownership changed")
        if _observed_object_digest(path, info) != record.expected_content_or_metadata_digest:
            raise _RollbackStepFailure("IDENTITY_MISMATCH", "object content or metadata changed")
        return info

    def _remove_filesystem_object(self, record: CreatedObjectRecord) -> str:
        path = _path_for(self.root, record.root_relative_path or "")
        if record.pre_existing_state == "PRESENT":
            self._verify_record_identity(path, record)
            return _observation_digest({"step": record.step_id, "result": "PREEXISTING_UNCHANGED"})
        if not path.exists() and not path.is_symlink():
            raise _RollbackStepFailure("MISSING_OBJECT", "expected transaction object is missing")
        info = self._verify_record_identity(path, record)
        if stat.S_ISDIR(info.st_mode):
            children = sorted(child.name for child in path.iterdir())
            if children:
                raise _RollbackStepFailure("UNKNOWN_OBJECT", "created directory contains an object")
            try:
                path.rmdir()
                parent_fd = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
                try:
                    os.fsync(parent_fd)
                finally:
                    os.close(parent_fd)
            except OSError as exc:
                raise _RollbackStepFailure("FILESYSTEM_FAILURE", "directory removal was not durable") from exc
        else:
            try:
                os.unlink(path)
                parent_fd = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
                try:
                    os.fsync(parent_fd)
                finally:
                    os.close(parent_fd)
            except OSError as exc:
                raise _RollbackStepFailure("FILESYSTEM_FAILURE", "object removal was not durable") from exc
        if path.exists() or path.is_symlink():
            raise _RollbackStepFailure("POSTCONDITION_FAILURE", "removed object remains visible")
        return _observation_digest({"step": record.step_id, "result": "REMOVED"})

    def _observe_filesystem_after_interruption(self, record: CreatedObjectRecord) -> str | None:
        path = _path_for(self.root, record.root_relative_path or "")
        if record.pre_existing_state == "PRESENT":
            self._verify_record_identity(path, record)
            return _observation_digest({"step": record.step_id, "result": "PREEXISTING_UNCHANGED"})
        if not path.exists() and not path.is_symlink():
            raise _RollbackStepFailure("MISSING_OBJECT", "interrupted transaction object is absent without durable removal evidence")
        try:
            self._verify_record_identity(path, record)
        except _RollbackStepFailure:
            raise
        return None

    def _validate_receipt(self, receipt: PrivilegedEffectReceipt, request: PrivilegedEffectRequest, adapter: PrivilegedEffectAdapter) -> None:
        if (
            receipt.transaction_id != request.transaction_id
            or receipt.step_id != request.step_id
            or receipt.operation != request.operation
            or receipt.request_digest != request.request_digest
            or receipt.boot_digest != request.boot_digest
            or receipt.adapter_identity != adapter.identity
        ):
            raise _RollbackStepFailure("RECEIPT_BINDING_MISMATCH", "privileged effect receipt is not bound")

    def _privileged_request(self, transaction: FirstInstallRollbackTransaction, record: CreatedObjectRecord, *, phase: PrivilegedRequestPhase) -> PrivilegedEffectRequest:
        return PrivilegedEffectRequest.create(
            transaction.identity.transaction_id,
            record.step_id,
            record.privileged_operation or "",
            phase.value,
            transaction.identity.boot_digest,
        )

    def _privileged_observe_request(
        self,
        transaction: FirstInstallRollbackTransaction,
        record: CreatedObjectRecord,
    ) -> PrivilegedEffectRequest:
        operation = {
            PrivilegedOperation.STOP_SELECTED_OAS_SERVICE_SOCKET_SET.value: PrivilegedOperation.VERIFY_SELECTED_SERVICE_SOCKET_ABSENCE.value,
            PrivilegedOperation.REMOVE_TRANSACTION_CREATED_PRINCIPAL_GROUP.value: PrivilegedOperation.VERIFY_TRANSACTION_CREATED_PRINCIPAL_GROUP_ABSENCE.value,
        }.get(record.privileged_operation or "", record.privileged_operation or "")
        return PrivilegedEffectRequest.create(
            transaction.identity.transaction_id,
            record.step_id,
            operation,
            PrivilegedRequestPhase.OBSERVE.value,
            transaction.identity.boot_digest,
        )

    def _apply_privileged(self, transaction: FirstInstallRollbackTransaction, record: CreatedObjectRecord, adapter: PrivilegedEffectAdapter) -> tuple[PrivilegedEffectReceipt, str, str]:
        request = self._privileged_request(transaction, record, phase=PrivilegedRequestPhase.APPLY)
        try:
            receipt = adapter.apply(request)
        except Exception as exc:
            raise _RollbackStepFailure("ADAPTER_FAILURE", "privileged effect adapter failed") from exc
        if not isinstance(receipt, PrivilegedEffectReceipt):
            raise _RollbackStepFailure("RECEIPT_INVALID", "adapter did not return a typed receipt")
        self._validate_receipt(receipt, request, adapter)
        if receipt.observed_result not in {"APPLIED", "ALREADY_ABSENT"}:
            raise _RollbackStepFailure("UNCERTAIN_EXTERNAL_EFFECT", "privileged effect is not safely observed")
        return receipt, _receipt_digest(receipt), receipt.evidence_digest

    def _observe_privileged(self, transaction: FirstInstallRollbackTransaction, record: CreatedObjectRecord, adapter: PrivilegedEffectAdapter) -> tuple[str, str]:
        request = self._privileged_observe_request(transaction, record)
        existing = self._receipt_for_request(self._read_receipts(transaction.identity.transaction_id), request)
        if existing is not None:
            try:
                self._validate_receipt(existing.receipt, request, adapter)
            except _RollbackStepFailure:
                raise
            if existing.receipt.observed_result != "ABSENT":
                raise _RollbackStepFailure("UNCERTAIN_EXTERNAL_EFFECT", "durable privileged absence is not proven")
            return existing.receipt_digest, existing.receipt.evidence_digest
        try:
            receipt = adapter.observe(request)
        except Exception as exc:
            raise _RollbackStepFailure("UNCERTAIN_EXTERNAL_EFFECT", "privileged observation failed") from exc
        if not isinstance(receipt, PrivilegedEffectReceipt):
            raise _RollbackStepFailure("RECEIPT_INVALID", "adapter observation was not typed")
        self._validate_receipt(receipt, request, adapter)
        if receipt.observed_result != "ABSENT":
            raise _RollbackStepFailure("UNCERTAIN_EXTERNAL_EFFECT", "privileged absence is not proven")
        return self._append_receipt(request, receipt), receipt.evidence_digest

    def _final_verify_filesystem(self, records: tuple[CreatedObjectRecord, ...]) -> list[str]:
        observations: list[str] = []
        for record in records:
            if record.expected_type == "privileged":
                continue
            path = _path_for(self.root, record.root_relative_path or "")
            if record.pre_existing_state == "PRESENT":
                self._verify_record_identity(path, record)
                observations.append(_observation_digest({"step": record.step_id, "result": "PREEXISTING_UNCHANGED"}))
            elif path.exists() or path.is_symlink():
                raise _RollbackStepFailure("POSTCONDITION_FAILURE", "transaction-created object remains")
            else:
                observations.append(_observation_digest({"step": record.step_id, "result": "ABSENT"}))
        return observations

    def _root_review(
        self,
        identity: RollbackTransactionIdentity,
        previous: str | None,
        attempt: int,
        completed: tuple[str, ...],
        step: str | None,
        classification: str,
    ) -> RollbackResult:
        record = self._journal_record(
            identity,
            RollbackState.ROOT_REVIEW_REQUIRED,
            current_step=step,
            previous=previous,
            attempt=attempt,
            completed=completed,
            failure=classification,
        )
        self._append_journal(record)
        return RollbackResult.PARTIAL_ROLLBACK_ROOT_REVIEW_REQUIRED

    def run(
        self,
        transaction: FirstInstallRollbackTransaction,
        *,
        adapter: PrivilegedEffectAdapter,
    ) -> RollbackResult:
        """Run or resume one bounded transaction; never targets the real host."""

        try:
            transaction_result = self._validate_request(
                transaction,
                require_unexpired_authorization=False,
            )
        except (ValueError, RollbackError):
            return RollbackResult.REJECTED_PRECONDITION
        if transaction_result is not None:
            return transaction_result
        if self.capability.transaction_id != transaction.identity.transaction_id:
            return RollbackResult.REJECTED_IDENTITY_MISMATCH
        if not isinstance(getattr(adapter, "identity", None), str) or not adapter.identity:
            return RollbackResult.REJECTED_PRECONDITION
        try:
            with _BoundedFileLock(self.root / ROLLBACK_LOCK, self.lock_timeout_seconds):
                journal = self._read_journal()
                receipts = self._read_receipts(transaction.identity.transaction_id)
                receipt_adapter_result = self._validate_receipts_for_adapter(transaction, receipts, adapter)
                if receipt_adapter_result is not None:
                    return receipt_adapter_result
                existing_result = self._validate_existing_identity(journal, transaction)
                if existing_result is not None:
                    if journal and journal[0].get("transaction_identity") == transaction.identity.as_dict():
                        self._validate_journal_binding(journal, transaction)
                        self._validate_receipt_references(journal, receipts)
                    return existing_result
                if journal:
                    self._validate_journal_binding(journal, transaction)
                else:
                    authorization_result = self._validate_request(
                        transaction,
                        require_unexpired_authorization=True,
                    )
                    if authorization_result is not None:
                        return authorization_result
                attempt = int(journal[-1]["attempt_number"]) + 1 if journal else 1
                previous = journal[-1].get("current_record_digest") if journal else None
                completed = tuple(journal[-1].get("completed_inverse_steps", ())) if journal else ()
                if not journal:
                    self._fault("before_rollback_intent_persistence")
                    requested = self._journal_record(
                        transaction.identity,
                        RollbackState.ROLLBACK_REQUESTED,
                        current_step=None,
                        previous=None,
                        attempt=attempt,
                        completed=(),
                        failure="REQUESTED",
                    )
                    self._append_journal(requested)
                    previous = requested.current_record_digest
                    self._fault("after_rollback_intent_persistence")
                    completed = ()
                validating = self._journal_record(
                    transaction.identity,
                    RollbackState.ROLLBACK_VALIDATING,
                    current_step=None,
                    previous=previous,
                    attempt=attempt,
                    completed=completed,
                    failure="VALIDATED_INPUT",
                )
                self._append_journal(validating)
                previous = validating.current_record_digest
                plan = tuple(sorted(transaction.created_objects, key=lambda item: item.dependency_order, reverse=True))
                by_step = {item.step_id: item for item in plan}
                current_step = journal[-1].get("current_inverse_step") if journal else None
                if current_step and current_step not in completed:
                    record = by_step.get(current_step)
                    if record is None:
                        return self._root_review(transaction.identity, previous, attempt, completed, current_step, "JOURNAL_STEP_UNKNOWN")
                    if record.expected_type == "privileged":
                        receipt_values = self._receipts_for_step(transaction.identity.transaction_id, record.step_id)
                        if receipt_values:
                            apply_receipts = [
                                value for value in receipt_values
                                if value.request_phase == PrivilegedRequestPhase.APPLY.value
                            ]
                            if apply_receipts:
                                stored_receipt = apply_receipts[-1]
                                request = self._privileged_request(transaction, record, phase=PrivilegedRequestPhase.APPLY)
                                try:
                                    self._validate_receipt(stored_receipt.receipt, request, adapter)
                                except _RollbackStepFailure as exc:
                                    return self._root_review(transaction.identity, previous, attempt, completed, current_step, exc.classification)
                                if stored_receipt.receipt.observed_result not in {"APPLIED", "ALREADY_ABSENT"}:
                                    return self._root_review(transaction.identity, previous, attempt, completed, current_step, "UNCERTAIN_EXTERNAL_EFFECT")
                            else:
                                stored_receipt = [
                                    value for value in receipt_values
                                    if value.request_phase == PrivilegedRequestPhase.OBSERVE.value
                                ][-1]
                                request = self._privileged_request(transaction, record, phase=PrivilegedRequestPhase.OBSERVE)
                                try:
                                    self._validate_receipt(stored_receipt.receipt, request, adapter)
                                except _RollbackStepFailure as exc:
                                    return self._root_review(transaction.identity, previous, attempt, completed, current_step, exc.classification)
                                if stored_receipt.receipt.observed_result != "ABSENT":
                                    return self._root_review(transaction.identity, previous, attempt, completed, current_step, "UNCERTAIN_EXTERNAL_EFFECT")
                            completed = completed + (record.step_id,)
                        else:
                            receipt_digest, evidence_digest = self._observe_privileged(transaction, record, adapter)
                            self._fault(f"after_observation_receipt_before_journal:{record.step_id}")
                            receipt = self._journal_record(
                                transaction.identity,
                                RollbackState.ROLLBACK_IN_PROGRESS,
                                current_step=record.step_id,
                                previous=previous,
                                attempt=attempt,
                                completed=completed,
                                failure="EFFECT_OBSERVED_AFTER_INTERRUPTION",
                                retained_evidence_digest=evidence_digest,
                                effect_receipt_digest=receipt_digest,
                            )
                            self._append_journal(receipt)
                            previous = receipt.current_record_digest
                            completed = completed + (record.step_id,)
                    else:
                        observed = self._observe_filesystem_after_interruption(record)
                        if observed is not None:
                            completed = completed + (record.step_id,)
                for record in plan:
                    if record.step_id in completed:
                        continue
                    progress = self._journal_record(
                        transaction.identity,
                        RollbackState.ROLLBACK_IN_PROGRESS,
                        current_step=record.step_id,
                        previous=previous,
                        attempt=attempt,
                        completed=completed,
                        failure="INVERSE_STEP_NEXT",
                    )
                    self._append_journal(progress)
                    previous = progress.current_record_digest
                    self._fault(f"before_inverse_action:{record.step_id}")
                    receipt_digest: str | None = None
                    receipt: PrivilegedEffectReceipt | None = None
                    evidence_digest: str
                    try:
                        if record.expected_type == "privileged":
                            receipt, receipt_digest, evidence_digest = self._apply_privileged(transaction, record, adapter)
                        else:
                            evidence_digest = self._remove_filesystem_object(record)
                    except _RollbackStepFailure as exc:
                        return self._root_review(transaction.identity, previous, attempt, completed, record.step_id, exc.classification)
                    self._fault(f"after_mutation_before_receipt:{record.step_id}")
                    if record.expected_type == "privileged" and receipt_digest is not None:
                        receipt_values = self._receipts_for_step(transaction.identity.transaction_id, record.step_id)
                        if not receipt_values:
                            if receipt is None:
                                raise RollbackStorageError("privileged receipt was not retained")
                            receipt_digest = self._append_receipt(
                                self._privileged_request(transaction, record, phase=PrivilegedRequestPhase.APPLY),
                                receipt,
                            )
                    self._fault(f"after_receipt_before_journal_advance:{record.step_id}")
                    completed = completed + (record.step_id,)
                    step_done = self._journal_record(
                        transaction.identity,
                        RollbackState.ROLLBACK_IN_PROGRESS,
                        current_step=record.step_id,
                        previous=previous,
                        attempt=attempt,
                        completed=completed,
                        observation_digest=evidence_digest,
                        failure="STEP_COMPLETED",
                        retained_evidence_digest=evidence_digest,
                        effect_receipt_digest=receipt_digest,
                    )
                    self._append_journal(step_done)
                    previous = step_done.current_record_digest
                verifying = self._journal_record(
                    transaction.identity,
                    RollbackState.ROLLBACK_VERIFYING,
                    current_step=None,
                    previous=previous,
                    attempt=attempt,
                    completed=completed,
                    failure="FINAL_POSTCONDITION_VERIFICATION",
                )
                self._append_journal(verifying)
                previous = verifying.current_record_digest
                self._fault("before_final_verification")
                observations = self._final_verify_filesystem(plan)
                for record in plan:
                    if record.expected_type == "privileged":
                        try:
                            receipt_digest, evidence_digest = self._observe_privileged(transaction, record, adapter)
                            self._fault(f"after_observation_receipt_before_journal:{record.step_id}")
                        except _RollbackStepFailure as exc:
                            return self._root_review(transaction.identity, previous, attempt, completed, record.step_id, exc.classification)
                        receipt = self._journal_record(
                            transaction.identity,
                            RollbackState.ROLLBACK_VERIFYING,
                            current_step=record.step_id,
                            previous=previous,
                            attempt=attempt,
                            completed=completed,
                            observation_digest=evidence_digest,
                            failure="FINAL_EFFECT_OBSERVED",
                            retained_evidence_digest=evidence_digest,
                            effect_receipt_digest=receipt_digest,
                        )
                        self._append_journal(receipt)
                        previous = receipt.current_record_digest
                        observations.append(evidence_digest)
                final_observation = _observation_digest(
                    {
                        "transaction_id": transaction.identity.transaction_id,
                        "boot_digest": transaction.identity.boot_digest,
                        "deployment_state": DEPLOYMENT_STATE,
                        "observations": observations,
                    }
                )
                journal = self._read_journal()
                terminal_result = self._validate_terminal_receipts(
                    transaction,
                    plan,
                    completed,
                    journal,
                    adapter,
                )
                if terminal_result is not None:
                    return terminal_result
                previous = journal[-1].get("current_record_digest")
                self._fault("after_final_verification_before_final_record")
                final = self._journal_record(
                    transaction.identity,
                    RollbackState.ROLLED_BACK_NOT_DEPLOYED,
                    current_step=None,
                    previous=previous,
                    attempt=attempt,
                    completed=completed,
                    observation_digest=final_observation,
                    failure="NONE",
                    retained_evidence_digest=final_observation,
                )
                self._append_journal(final)
                return RollbackResult.ROLLED_BACK_NOT_DEPLOYED
        except _RollbackStepFailure as exc:
            if exc.classification == "LOCK_TIMEOUT":
                return RollbackResult.REJECTED_CONFLICT
            return RollbackResult.REJECTED_PRECONDITION
        except RollbackStorageError:
            raise


def rollback_first_install(
    root: str | Path,
    *,
    capability: TemporaryRootCapability,
    transaction: FirstInstallRollbackTransaction,
    adapter: PrivilegedEffectAdapter,
    current_boot_digest: str,
    now_utc: Callable[[], str] = _utc_now,
    fault_injector: Callable[[str], None] | None = None,
) -> RollbackResult:
    """Convenience entry point for one isolated first-install rollback."""

    return FirstInstallRollbackFoundation(
        root,
        capability=capability,
        current_boot_digest=current_boot_digest,
        now_utc=now_utc,
        fault_injector=fault_injector,
    ).run(transaction, adapter=adapter)
