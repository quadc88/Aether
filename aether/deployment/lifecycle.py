"""Pure activation-record state machine and crash-safe JSON persistence."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import hashlib
import json
import math
import os
from pathlib import Path
import re
import secrets
import stat
import tempfile
import time
from typing import Any, Mapping, Protocol

from .manifest_schema import canonical_json_bytes


class LifecycleError(ValueError):
    """Raised when an activation record or transition is unsafe."""


class ActivationState(str, Enum):
    NO_DEPLOYMENT = "NO_DEPLOYMENT"
    CANDIDATE_PENDING = "CANDIDATE_PENDING"
    QUIESCE_REQUIRED = "QUIESCE_REQUIRED"
    ACTIVATING = "ACTIVATING"
    COMMITTED = "COMMITTED"
    ROLLBACK_PENDING = "ROLLBACK_PENDING"
    RECOVERY_REQUIRED = "RECOVERY_REQUIRED"


RECORD_FIELDS = (
    "record_version", "state", "transaction_id", "record_sequence",
    "previous_record_digest", "host_boot_id", "activation_issued_at_monotonic",
    "activation_expires_at_monotonic", "activation_max_duration_seconds",
    "old_release_id", "old_manifest_digest", "candidate_release_id",
    "candidate_manifest_digest", "current_link_release_id", "old_unit_generation_id",
    "candidate_unit_generation_id", "unit_bundle_digest", "quiesce_state", "schema_before",
    "schema_after", "schema_compatibility", "migration_state", "readiness_result",
    "smoke_result", "commit_state", "rollback_state", "activation_reason",
    "created_at_utc", "updated_at_utc",
)
_DIGEST = re.compile(r"^[0-9a-f]{64}$")
_RELEASE = re.compile(r"^r1-[0-9a-f]{64}$")
_GENERATION = re.compile(r"^g-[0-9a-f]{64}$")
ACTIVATION_MAX_DURATION_SECONDS = 60
_CAPABILITY_TOKEN = object()
_CAPABILITY_REGISTRY: dict[str, tuple[object, Path, str, str, float, float]] = {}
CAPABILITY_LIFETIME_SECONDS = 300.0
_REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
_PROTECTED_ROOTS = {
    "/", "/boot", "/dev", "/etc", "/home", "/lib", "/lib64", "/opt",
    "/proc", "/root", "/run", "/sbin", "/srv", "/sys", "/usr", "/var",
}


def _is_protected_host_path(path: Path) -> bool:
    """Treat the filesystem root as exact-only while protecting its children."""

    return any(
        path == protected or (protected != Path("/") and protected in path.parents)
        for protected in map(Path, _PROTECTED_ROOTS)
    )


class TemporaryRootCapability:
    """Process-local authority for a caller-selected isolated root."""

    __slots__ = ("_root", "_token", "_pid", "_identity", "_purpose", "_transaction_id", "_created_at", "_expires_at")

    def __init__(
        self,
        root: Path,
        token: object,
        identity: str,
        purpose: str,
        transaction_id: str,
        created_at: float,
        expires_at: float,
    ) -> None:
        if token is not _CAPABILITY_TOKEN:
            raise TypeError("temporary-root capabilities are issued by create_isolated_root")
        self._root = root
        self._token = token
        self._pid = os.getpid()
        self._identity = identity
        self._purpose = purpose
        self._transaction_id = transaction_id
        self._created_at = created_at
        self._expires_at = expires_at

    @property
    def root(self) -> Path:
        return self._root

    @property
    def identity(self) -> str:
        return self._identity

    @property
    def purpose(self) -> str:
        return self._purpose

    @property
    def transaction_id(self) -> str:
        return self._transaction_id

    def __reduce__(self) -> Any:
        raise TypeError("temporary-root capabilities are not serializable")


def _path_has_symlink(path: Path) -> bool:
    current = Path(path.anchor or "/")
    for part in path.parts[1:] if path.is_absolute() else path.parts:
        current /= part
        try:
            if current.is_symlink():
                return True
        except OSError as exc:
            raise LifecycleError("temporary root cannot be inspected") from exc
    return False


def authorize_temporary_root(root: str | Path) -> TemporaryRootCapability:
    """Reject direct issuance; use the explicit isolated-root factory."""

    raise LifecycleError("capabilities are issued only by create_isolated_root")


def create_isolated_root(
    parent: str | Path = "/tmp",
    *,
    purpose: str,
    transaction_id: str,
    lifetime_seconds: float = CAPABILITY_LIFETIME_SECONDS,
) -> tuple[Path, TemporaryRootCapability]:
    """Create a fresh isolated root and issue its process-local capability."""

    if not re.fullmatch(r"[A-Za-z0-9_.:-]{1,64}", purpose) or not re.fullmatch(r"[A-Za-z0-9_.:-]{1,128}", transaction_id):
        raise LifecycleError("capability purpose or transaction is invalid")
    if not math.isfinite(lifetime_seconds) or not 0 < lifetime_seconds <= CAPABILITY_LIFETIME_SECONDS:
        raise LifecycleError("capability lifetime is invalid")
    base = Path(parent)
    if not base.is_absolute() or _path_has_symlink(base):
        raise LifecycleError("isolated-root parent is unsafe")
    if _is_protected_host_path(base):
        if base != Path("/tmp") and not str(base).startswith("/tmp/"):
            raise LifecycleError("isolated-root parent is protected")
    if base == _REPOSITORY_ROOT or _REPOSITORY_ROOT in base.parents:
        raise LifecycleError("repository checkout cannot contain an isolated root")
    try:
        parent_info = base.stat()
    except OSError as exc:
        raise LifecycleError("isolated-root parent is unavailable") from exc
    parent_mode = stat.S_IMODE(parent_info.st_mode)
    if not stat.S_ISDIR(parent_info.st_mode) or (parent_mode & 0o022 and not (parent_mode & 0o1000 and parent_mode & 0o002)):
        raise LifecycleError("isolated-root parent mode is unsafe")
    try:
        root = Path(tempfile.mkdtemp(prefix="aether-m122a-", dir=base))
        os.chmod(root, 0o700)
    except OSError as exc:
        raise LifecycleError("isolated root cannot be created") from exc
    identity = secrets.token_urlsafe(32)
    created = time.monotonic()
    expires = created + lifetime_seconds
    sentinel_value = {
        "version": 1,
        "identity": identity,
        "root": str(root),
        "purpose": purpose,
        "transaction_id": transaction_id,
        "created_at_monotonic": created,
        "expires_at_monotonic": expires,
    }
    sentinel = root / ".aether-temporary-root"
    try:
        fd = os.open(sentinel, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
        with os.fdopen(fd, "wb") as stream:
            stream.write(canonical_json_bytes(sentinel_value))
            stream.flush()
            os.fsync(stream.fileno())
        directory_fd = os.open(root, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
    except OSError as exc:
        raise LifecycleError("isolated-root sentinel cannot be created") from exc
    _CAPABILITY_REGISTRY[identity] = (_CAPABILITY_TOKEN, root, purpose, transaction_id, created, expires)
    return root, TemporaryRootCapability(root, _CAPABILITY_TOKEN, identity, purpose, transaction_id, created, expires)


def _require_capability(
    root: str | Path,
    capability: TemporaryRootCapability,
    *,
    purpose: str | None = None,
    transaction_id: str | None = None,
) -> Path:
    if not isinstance(capability, TemporaryRootCapability) or capability._token is not _CAPABILITY_TOKEN:
        raise LifecycleError("temporary-root capability is required")
    if capability._pid != os.getpid() or capability._expires_at <= time.monotonic():
        raise LifecycleError("temporary-root capability is process-bound")
    registered = _CAPABILITY_REGISTRY.get(capability._identity)
    if registered is None or registered[0] is not capability._token or registered[1:] != (
        capability._root, capability._purpose, capability._transaction_id, capability._created_at, capability._expires_at
    ):
        raise LifecycleError("temporary-root capability identity is not registered")
    if purpose is not None and capability._purpose != purpose:
        raise LifecycleError("temporary-root capability purpose does not match")
    if transaction_id is not None and capability._transaction_id != transaction_id:
        raise LifecycleError("temporary-root capability transaction does not match")
    base = ensure_temporary_root(root)
    if base != capability.root:
        raise LifecycleError("temporary-root capability does not match root")
    info = base.stat()
    if info.st_uid not in {os.getuid(), 0} or stat.S_IMODE(info.st_mode) != 0o700:
        raise LifecycleError("temporary-root ownership or mode is unsafe")
    sentinel = base / ".aether-temporary-root"
    try:
        value = json.loads(sentinel.read_text(encoding="utf-8"))
        expected = {
            "version": 1,
            "identity": capability._identity,
            "root": str(base),
            "purpose": capability._purpose,
            "transaction_id": capability._transaction_id,
            "created_at_monotonic": capability._created_at,
            "expires_at_monotonic": capability._expires_at,
        }
        if sentinel.is_symlink() or value != expected or stat.S_IMODE(sentinel.stat().st_mode) != 0o600:
            raise LifecycleError("temporary-root sentinel is invalid")
    except OSError as exc:
        raise LifecycleError("temporary-root sentinel is unreadable") from exc
    return base


def record_digest(record: Mapping[str, Any]) -> str:
    return hashlib.sha256(canonical_json_bytes(dict(record))).hexdigest()


def canonical_record_bytes(record: Mapping[str, Any]) -> bytes:
    validate_record(record)
    return canonical_json_bytes(dict(record))


def validate_record(record: Mapping[str, Any]) -> None:
    if not isinstance(record, Mapping) or set(record) != set(RECORD_FIELDS):
        raise LifecycleError("activation record fields are not exact")
    if record["record_version"] != 1 or not isinstance(record["state"], str):
        raise LifecycleError("activation record version or state is invalid")
    try:
        state = ActivationState(record["state"])
    except ValueError as exc:
        raise LifecycleError("activation record state is invalid") from exc
    if not isinstance(record["transaction_id"], str) or not re.fullmatch(r"[A-Za-z0-9_.:-]{1,128}", record["transaction_id"]):
        raise LifecycleError("transaction identity is invalid")
    if not isinstance(record["record_sequence"], int) or isinstance(record["record_sequence"], bool) or record["record_sequence"] < 0:
        raise LifecycleError("record sequence is invalid")
    previous = record["previous_record_digest"]
    if previous is not None and (not isinstance(previous, str) or not _DIGEST.fullmatch(previous)):
        raise LifecycleError("previous record digest is invalid")
    for field, pattern in (("old_release_id", _RELEASE), ("candidate_release_id", _RELEASE), ("old_unit_generation_id", _GENERATION), ("candidate_unit_generation_id", _GENERATION)):
        value = record[field]
        if value is not None and (not isinstance(value, str) or not pattern.fullmatch(value)):
            raise LifecycleError(f"{field} is invalid")
    for field in ("old_manifest_digest", "candidate_manifest_digest", "unit_bundle_digest"):
        value = record[field]
        if value is not None and (not isinstance(value, str) or not _DIGEST.fullmatch(value)):
            raise LifecycleError(f"{field} is invalid")
    if record["activation_max_duration_seconds"] != ACTIVATION_MAX_DURATION_SECONDS:
        raise LifecycleError("activation duration policy is invalid")
    issued = record["activation_issued_at_monotonic"]
    expires = record["activation_expires_at_monotonic"]
    if not isinstance(issued, (int, float)) or isinstance(issued, bool) or not math.isfinite(issued) or not isinstance(expires, (int, float)) or isinstance(expires, bool) or not math.isfinite(expires) or expires < issued or expires - issued > ACTIVATION_MAX_DURATION_SECONDS or (state == ActivationState.ACTIVATING and expires <= issued):
        raise LifecycleError("activation monotonic window is invalid")
    if state == ActivationState.NO_DEPLOYMENT:
        if any(record[field] is not None for field in ("old_release_id", "old_manifest_digest", "old_unit_generation_id")):
            raise LifecycleError("NO_DEPLOYMENT has old identity")
    if state == ActivationState.COMMITTED and record["commit_state"] != "COMMITTED":
        raise LifecycleError("committed state has not committed state")
    if state == ActivationState.ACTIVATING and record["commit_state"] != "UNCOMMITTED":
        raise LifecycleError("activating state must be uncommitted")


def transition(
    record: Mapping[str, Any],
    target: ActivationState | str,
    *,
    root_trust_verified: bool = False,
    **updates: Any,
) -> dict[str, Any]:
    validate_record(record)
    target_state = ActivationState(target)
    current = ActivationState(record["state"])
    allowed = {
        (ActivationState.NO_DEPLOYMENT, ActivationState.CANDIDATE_PENDING),
        (ActivationState.COMMITTED, ActivationState.CANDIDATE_PENDING),
        (ActivationState.CANDIDATE_PENDING, ActivationState.QUIESCE_REQUIRED),
        (ActivationState.QUIESCE_REQUIRED, ActivationState.ACTIVATING),
        (ActivationState.ACTIVATING, ActivationState.COMMITTED),
        (ActivationState.ACTIVATING, ActivationState.ROLLBACK_PENDING),
        (ActivationState.ROLLBACK_PENDING, ActivationState.COMMITTED),
        (ActivationState.RECOVERY_REQUIRED, ActivationState.CANDIDATE_PENDING),
    }
    if (current, target_state) not in allowed:
        raise LifecycleError(f"transition {current.value}->{target_state.value} is not allowed")
    if target_state == ActivationState.CANDIDATE_PENDING and root_trust_verified is not True:
        raise LifecycleError("CANDIDATE_PENDING requires root trust verification")
    result = dict(record)
    result.update(updates)
    result["state"] = target_state.value
    if target_state == ActivationState.ACTIVATING:
        if result["quiesce_state"] != "PROVEN" or result["commit_state"] != "UNCOMMITTED":
            raise LifecycleError("activation requires proven quiescence and uncommitted state")
    if target_state == ActivationState.COMMITTED:
        if result["readiness_result"] != "PASSED" or result["smoke_result"] != "PASSED":
            raise LifecycleError("commit requires readiness and smoke evidence")
        result["commit_state"] = "COMMITTED"
        result["rollback_state"] = "NOT_REQUESTED"
    if target_state == ActivationState.ROLLBACK_PENDING:
        result["rollback_state"] = "PENDING"
    validate_record(result)
    return result


def ensure_temporary_root(root: str | Path) -> Path:
    raw = Path(root)
    if not raw.is_absolute():
        raise LifecycleError("temporary root must be absolute")
    path = raw.resolve(strict=False)
    if _is_protected_host_path(path):
        raise LifecycleError("protected host root is forbidden")
    if path == _REPOSITORY_ROOT or _REPOSITORY_ROOT in path.parents:
        raise LifecycleError("repository checkout is not an isolated root")
    if _path_has_symlink(raw):
        raise LifecycleError("symlinked temporary roots are forbidden")
    return path


def activation_record_path(root: str | Path) -> Path:
    return ensure_temporary_root(root) / "var/lib/aether/activation/activation-record.json"


def _production_activation_record_path() -> Path:
    """Fixed read-only path used only by the explicit production entrypoint."""

    return Path("/var/lib/aether/activation/activation-record.json")


def write_record(
    root: str | Path,
    record: Mapping[str, Any],
    *,
    capability: TemporaryRootCapability,
    purpose: str = "M122A_LIFECYCLE",
) -> Path:
    base = _require_capability(root, capability, purpose=purpose, transaction_id=str(record.get("transaction_id")))
    target = activation_record_path(base)
    data = canonical_record_bytes(record)
    if _path_has_symlink(target.parent):
        raise LifecycleError("activation record parent contains a symlink")
    target.parent.mkdir(parents=True, exist_ok=True, mode=0o755)
    if _path_has_symlink(target.parent):
        raise LifecycleError("activation record parent contains a symlink")
    temporary_name = f".{target.name}.{record['transaction_id']}.tmp"
    directory_fd = os.open(target.parent, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
    try:
        fd = os.open(
            temporary_name,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
            0o444,
            dir_fd=directory_fd,
        )
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.rename(temporary_name, target.name, src_dir_fd=directory_fd, dst_dir_fd=directory_fd)
        os.chmod(target.name, 0o444, dir_fd=directory_fd, follow_symlinks=False)
        os.fsync(directory_fd)
    except Exception:
        try:
            os.unlink(temporary_name, dir_fd=directory_fd)
        except FileNotFoundError:
            pass
        raise
    finally:
        os.close(directory_fd)
    return target


def _read_record_at(path: Path) -> dict[str, Any]:
    if path.is_symlink() or not path.is_file():
        raise LifecycleError("activation record is missing or not regular")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise LifecycleError("activation record is unreadable") from exc
    if not isinstance(value, dict):
        raise LifecycleError("activation record is not an object")
    validate_record(value)
    if canonical_record_bytes(value) != path.read_bytes():
        raise LifecycleError("activation record is not canonical")
    return value


def read_record(root: str | Path) -> dict[str, Any]:
    return _read_record_at(activation_record_path(root))


def read_production_record() -> dict[str, Any]:
    return _read_record_at(_production_activation_record_path())


@dataclass(frozen=True, slots=True)
class ActivationWindow:
    issued: float
    expires: float
    boot_id: str

    def valid(self, *, now: float, current_boot_id: str) -> bool:
        return current_boot_id == self.boot_id and self.issued < now < self.expires and self.expires - self.issued <= ACTIVATION_MAX_DURATION_SECONDS


@dataclass(frozen=True, slots=True)
class QuiescenceProof:
    """Closed, canonical, time- and identity-bound quiescence evidence."""

    proof_version: int
    transaction_id: str
    activation_record_digest: str
    old_release_id: str | None
    old_unit_generation_id: str | None
    observation_boot_id: str
    observed_at_monotonic: float
    expires_at_monotonic: float
    socket_unit_states: tuple[tuple[str, str], ...]
    service_state: str
    listener_count: int
    accepted_connection_count: int
    outstanding_worker_count: int
    activation_job_count: int
    oas_process_count: int
    cgroup_populated: bool
    system_manager_adapter_identity: str
    canonical_proof_digest: str

    SOCKET_NAMES = ("runtime", "bootstrap", "broker")

    def _payload(self) -> dict[str, Any]:
        return {
            "proof_version": self.proof_version,
            "transaction_id": self.transaction_id,
            "activation_record_digest": self.activation_record_digest,
            "old_release_id": self.old_release_id,
            "old_unit_generation_id": self.old_unit_generation_id,
            "observation_boot_id": self.observation_boot_id,
            "observed_at_monotonic": self.observed_at_monotonic,
            "expires_at_monotonic": self.expires_at_monotonic,
            "socket_unit_states": dict(self.socket_unit_states),
            "service_state": self.service_state,
            "listener_count": self.listener_count,
            "accepted_connection_count": self.accepted_connection_count,
            "outstanding_worker_count": self.outstanding_worker_count,
            "activation_job_count": self.activation_job_count,
            "oas_process_count": self.oas_process_count,
            "cgroup_populated": self.cgroup_populated,
            "system_manager_adapter_identity": self.system_manager_adapter_identity,
        }

    @classmethod
    def from_snapshot(
        cls,
        *,
        record: Mapping[str, Any],
        snapshot: Mapping[str, Any],
        adapter_identity: str,
        boot_id: str,
        now: float,
        lifetime_seconds: float = ACTIVATION_MAX_DURATION_SECONDS,
    ) -> "QuiescenceProof":
        if not math.isfinite(lifetime_seconds) or not 0 < lifetime_seconds <= ACTIVATION_MAX_DURATION_SECONDS:
            raise LifecycleError("quiescence proof lifetime is invalid")
        states = snapshot.get("socket_unit_states")
        if not isinstance(states, Mapping) or tuple(states) != cls.SOCKET_NAMES:
            raise LifecycleError("quiescence socket names are not exact")
        observed = snapshot.get("observed_at_monotonic")
        if not isinstance(observed, (int, float)) or isinstance(observed, bool) or not math.isfinite(observed):
            raise LifecycleError("quiescence observation time is invalid")
        counts = {
            field: snapshot.get(field)
            for field in (
                "listener_count", "accepted_connection_count", "outstanding_worker_count",
                "activation_job_count", "oas_process_count",
            )
        }
        if any(not isinstance(value, int) or isinstance(value, bool) or value < 0 for value in counts.values()):
            raise LifecycleError("quiescence counters are invalid")
        if not isinstance(snapshot.get("cgroup_populated"), bool):
            raise LifecycleError("quiescence cgroup state is invalid")
        proof = cls(
            proof_version=1,
            transaction_id=str(record["transaction_id"]),
            activation_record_digest=record_digest(record),
            old_release_id=record["old_release_id"],
            old_unit_generation_id=record["old_unit_generation_id"],
            observation_boot_id=boot_id,
            observed_at_monotonic=float(observed),
            expires_at_monotonic=float(observed) + lifetime_seconds,
            socket_unit_states=tuple((name, str(states[name])) for name in cls.SOCKET_NAMES),
            service_state=str(snapshot["service_state"]),
            listener_count=counts["listener_count"],
            accepted_connection_count=counts["accepted_connection_count"],
            outstanding_worker_count=counts["outstanding_worker_count"],
            activation_job_count=counts["activation_job_count"],
            oas_process_count=counts["oas_process_count"],
            cgroup_populated=snapshot["cgroup_populated"],
            system_manager_adapter_identity=adapter_identity,
            canonical_proof_digest="",
        )
        object.__setattr__(proof, "canonical_proof_digest", hashlib.sha256(canonical_json_bytes(proof._payload())).hexdigest())
        return proof

    def validate(
        self,
        record: Mapping[str, Any],
        *,
        current_boot_id: str,
        now: float,
        adapter_identity: str,
    ) -> None:
        if self.proof_version != 1 or self.transaction_id != record.get("transaction_id"):
            raise LifecycleError("quiescence proof identity is invalid")
        if self.activation_record_digest != record_digest(record):
            raise LifecycleError("quiescence proof record digest is stale")
        if self.old_release_id != record.get("old_release_id") or self.old_unit_generation_id != record.get("old_unit_generation_id"):
            raise LifecycleError("quiescence proof old identity is stale")
        if self.observation_boot_id != current_boot_id or self.system_manager_adapter_identity != adapter_identity:
            raise LifecycleError("quiescence proof boot or adapter identity is invalid")
        if not self.observed_at_monotonic <= now < self.expires_at_monotonic or self.expires_at_monotonic - self.observed_at_monotonic > ACTIVATION_MAX_DURATION_SECONDS:
            raise LifecycleError("quiescence proof is stale, future-dated, or unbounded")
        if hashlib.sha256(canonical_json_bytes(self._payload())).hexdigest() != self.canonical_proof_digest:
            raise LifecycleError("quiescence proof digest is invalid")
        if self.service_state != "inactive":
            raise LifecycleError("quiescence proof identity or service state is invalid")
        if self.socket_unit_states != tuple((name, "inactive") for name in self.SOCKET_NAMES):
            raise LifecycleError("quiescence proof has active socket units")
        if min(self.listener_count, self.accepted_connection_count, self.outstanding_worker_count, self.activation_job_count, self.oas_process_count) != 0 or self.cgroup_populated:
            raise LifecycleError("quiescence proof contains outstanding OAS work")


class SystemManagerAdapter(Protocol):
    identity: str

    def snapshot_quiescence(self) -> Mapping[str, Any]: ...


def prove_quiescence(
    adapter: SystemManagerAdapter,
    record: Mapping[str, Any],
    *,
    boot_id: str,
    now: float,
) -> QuiescenceProof:
    """Convert one manager snapshot into typed, transaction-bound evidence."""

    try:
        identity = getattr(adapter, "identity")
        if not isinstance(identity, str) or not identity:
            raise LifecycleError("system manager adapter identity is invalid")
        proof = QuiescenceProof.from_snapshot(
            record=record,
            snapshot=adapter.snapshot_quiescence(),
            adapter_identity=identity,
            boot_id=boot_id,
            now=now,
        )
        proof.validate(record, current_boot_id=boot_id, now=now, adapter_identity=identity)
        return proof
    except (AttributeError, KeyError, TypeError, ValueError, LifecycleError) as exc:
        if isinstance(exc, LifecycleError):
            raise
        raise LifecycleError("quiescence snapshot is malformed") from exc


def transition_after_quiescence(
    record: Mapping[str, Any], proof: QuiescenceProof, *, boot_id: str, now: float, adapter_identity: str
) -> dict[str, Any]:
    """Advance a candidate only from proof bound to the same transaction."""

    proof.validate(record, current_boot_id=boot_id, now=now, adapter_identity=adapter_identity)
    if record.get("state") != ActivationState.CANDIDATE_PENDING.value:
        raise LifecycleError("quiescence is only entered from a pending candidate")
    return transition(record, ActivationState.QUIESCE_REQUIRED, quiesce_state="PROVEN")
