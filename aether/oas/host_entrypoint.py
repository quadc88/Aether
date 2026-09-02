"""Production OAS startup boundary for the repository deployment artifact."""

from __future__ import annotations

import hashlib
import os
from pathlib import Path
import re
import platform
import sqlite3
import stat
import sys
import sysconfig
import threading
import time
from dataclasses import dataclass
from typing import Any, Callable, Mapping

from .service import (
    OASService,
    PeerExpectation,
    ServiceIdentityContract,
)
from .socket_activation import (
    ActivationContract,
    SocketExpectation,
    EXPECTED_ENDPOINT_NAMES,
    ActivatedDescriptors,
    intake_activated_descriptors,
)
from .systemd_notify import notify_ready
from ..deployment.lifecycle import ActivationState, read_production_record, read_record
from ..deployment.dependency_lock import DependencyLockError, verify_dependency_closure, verify_installed_closure
from ..deployment.manifest_schema import ManifestError, canonical_json_bytes, parse_canonical_json, sha256_hex, validate_manifest
from ..deployment.trust_bootstrap import TrustBootstrapError, fixed_verifier_identity, trust_evidence_path, _validate_inventory
from ..deployment.unit_verifier import verify_unit_directory


PRODUCTION_ROOT = Path("/")
ACTIVATION_RECORD = Path("/var/lib/aether/activation/activation-record.json")
STATE_PATH = Path("/var/lib/aether/oas/security_kernel.sqlite3")
CURRENT_LINK = Path("/opt/aether/current")
RELEASE_ROOT = Path("/opt/aether/releases")
SOCKET_ROOT = Path("/run/aether/oas")
REQUIRED_FIXED_ENVIRONMENT = {
    "LANG": "C.UTF-8",
    "LC_ALL": "C.UTF-8",
    "TZ": "UTC",
    "HOME": "/var/empty",
}
EXPECTED_OAS_UID = 3003
EXPECTED_OAS_GID = 3003
EXPECTED_OAS_GROUPS = ()
STANDARD_IMPORT_ROOTS = (
    "/usr/lib/python311.zip",
    "/usr/lib/python3.11",
    "/usr/lib/python3.11/lib-dynload",
)


class EntrypointError(RuntimeError):
    """Raised when startup identity or environment verification fails."""


@dataclass(frozen=True, slots=True)
class RuntimeIdentitySnapshot:
    """Bounded observation of interpreter and process identity."""

    proc_self_exe: str
    sys_executable: str
    python_version: str
    abi_tag: str
    soabi: str
    machine: str
    module_path: str
    module_sha256: str
    sys_path: tuple[str, ...]
    uid: int
    gid: int
    groups: tuple[int, ...]
    capabilities: str
    authorized_import_roots: tuple[str, ...]

    def __post_init__(self) -> None:
        strings = (
            self.proc_self_exe, self.sys_executable, self.python_version,
            self.abi_tag, self.soabi, self.machine, self.module_path,
            self.module_sha256, self.capabilities,
        )
        if any(not isinstance(value, str) or not value or len(value) > 4096 for value in strings):
            raise EntrypointError("runtime identity snapshot contains an invalid string")
        if not re.fullmatch(r"[0-9a-f]{64}", self.module_sha256):
            raise EntrypointError("runtime module digest is invalid")
        if len(self.sys_path) > 64 or len(self.authorized_import_roots) > 8:
            raise EntrypointError("runtime identity snapshot is too large")
        if any(not isinstance(path, str) or len(path) > 4096 for path in self.sys_path):
            raise EntrypointError("runtime sys.path entry is invalid")
        if any(not isinstance(path, str) or not path.startswith("/") or len(path) > 4096 for path in self.authorized_import_roots):
            raise EntrypointError("runtime identity path is invalid")
        if any(not isinstance(value, int) or isinstance(value, bool) or value < 0 for value in (self.uid, self.gid, *self.groups)):
            raise EntrypointError("runtime credential identity is invalid")


def collect_runtime_identity_snapshot(
    *, authorized_import_roots: tuple[str, ...] = (),
) -> RuntimeIdentitySnapshot:
    """Capture bounded runtime identity facts used by the startup gate."""

    try:
        proc_self_exe = str(Path(os.readlink("/proc/self/exe")).resolve())
        module_path = str(Path(__file__).resolve())
        status = Path("/proc/self/status").read_text(encoding="ascii")
        capabilities = next(line.split(":", 1)[1].strip() for line in status.splitlines() if line.startswith("CapEff:"))
    except (OSError, StopIteration, UnicodeError) as exc:
        raise EntrypointError("current runtime identity cannot be observed") from exc
    return RuntimeIdentitySnapshot(
        proc_self_exe=proc_self_exe,
        sys_executable=str(Path(sys.executable).resolve()),
        python_version=f"{sys.version_info.major}.{sys.version_info.minor}",
        abi_tag=str(sys.implementation.cache_tag),
        soabi=str(sysconfig.get_config_var("SOABI") or ""),
        machine=platform.machine(),
        module_path=module_path,
        module_sha256=hashlib.sha256(Path(module_path).read_bytes()).hexdigest(),
        sys_path=tuple(str(path) for path in sys.path),
        uid=os.getuid(),
        gid=os.getgid(),
        groups=tuple(os.getgroups()),
        capabilities=capabilities,
        authorized_import_roots=authorized_import_roots,
    )


@dataclass(frozen=True, slots=True)
class EntrypointAdapters:
    """Explicit seams for isolated startup proof; production defaults are fixed."""

    runtime_validator: Callable[..., None] | None = None
    runtime_identity_snapshot: RuntimeIdentitySnapshot | None = None
    dependency_validator: Callable[..., None] | None = None
    state_validator: Callable[..., None] | None = None
    descriptor_intake: Callable[..., ActivatedDescriptors] | None = None
    service_factory: Callable[..., OASService] | None = None


def _under(root: Path, absolute: Path) -> Path:
    return root / str(absolute).lstrip("/") if root != PRODUCTION_ROOT else absolute


def validate_environment(environment: Mapping[str, str], *, pid: int | None = None) -> dict[str, str]:
    """Snapshot only the fixed protocol inputs and ignore ambient metadata."""

    process_pid = os.getpid() if pid is None else pid
    required = {"LISTEN_PID", "LISTEN_FDS", "LISTEN_FDNAMES", "NOTIFY_SOCKET", *REQUIRED_FIXED_ENVIRONMENT}
    for key in required:
        if not isinstance(environment.get(key), str) or not environment[key]:
            raise EntrypointError(f"required environment value is missing: {key}")
    if environment["LISTEN_PID"] != str(process_pid) or environment["LISTEN_FDS"] != "3" or environment["LISTEN_FDNAMES"] != "runtime:bootstrap:broker":
        raise EntrypointError("socket activation environment is not exact")
    for key, expected in REQUIRED_FIXED_ENVIRONMENT.items():
        if environment[key] != expected:
            raise EntrypointError(f"fixed environment value is not exact: {key}")
    return {key: environment[key] for key in required}


def _release_id_from_link(root: Path) -> str:
    link = _under(root, CURRENT_LINK)
    if not link.is_symlink():
        raise EntrypointError("current release is not a symlink")
    link_info = link.lstat()
    expected_owner = 0 if root == PRODUCTION_ROOT else os.getuid()
    if link_info.st_uid != expected_owner or link_info.st_nlink != 1:
        raise EntrypointError("current release link ownership is invalid")
    target = os.readlink(link)
    if target.startswith("/") or target.count("/") != 1 or not target.startswith("releases/r1-"):
        raise EntrypointError("current release link is not a root-owned relative release link")
    release_id = target.split("/", 1)[1]
    if not re.fullmatch(r"r1-[0-9a-f]{64}", release_id):
        raise EntrypointError("current release identity is invalid")
    resolved = link.parent / target
    if resolved.resolve().parent != _under(root, RELEASE_ROOT).resolve():
        raise EntrypointError("current release escapes the release root")
    if not resolved.is_dir() or resolved.is_symlink():
        raise EntrypointError("current release directory is missing")
    return release_id


def _read_object(path: Path) -> Mapping[str, object]:
    try:
        info = path.lstat()
        if stat.S_ISLNK(info.st_mode) or not stat.S_ISREG(info.st_mode) or info.st_size > 4 * 1024 * 1024:
            raise EntrypointError(f"artifact is not a bounded regular file: {path}")
        value = parse_canonical_json(path.read_bytes())
    except (OSError, ManifestError) as exc:
        raise EntrypointError(f"artifact is missing or not canonical: {path}") from exc
    if not isinstance(value, Mapping):
        raise EntrypointError(f"artifact is not an object: {path}")
    return value


def _validate_trust_evidence(root: Path, record: Mapping[str, object], manifest: Mapping[str, object]) -> None:
    path = trust_evidence_path(root, str(record["transaction_id"]))
    evidence = _read_object(path)
    try:
        owner = path.lstat().st_uid
        expected_owner = 0 if root == PRODUCTION_ROOT else os.getuid()
        if owner != expected_owner or stat.S_IMODE(path.lstat().st_mode) != 0o444:
            raise EntrypointError("root trust evidence ownership or mode is invalid")
    except OSError as exc:
        raise EntrypointError("root trust evidence cannot be inspected") from exc
    expected = {
        "evidence_version", "status", "transaction_id", "release_id", "manifest_sha256",
        "source_commit", "source_tree", "source_root_digest", "approval_id", "approval_payload_digest",
        "test_evidence_digest", "anchor_fingerprint", "verifier_sha256",
        "verifier_version", "openssl_identity", "openssl_version", "accepted_key_ids",
        "signature_results", "dependency_lock_digest", "unit_generation_id",
        "unit_bundle_digest", "verified_at_utc",
    }
    if set(evidence) != expected or evidence["evidence_version"] != 1 or evidence["status"] != "VERIFIED":
        raise EntrypointError("root trust evidence is not exact")
    if (
        evidence["transaction_id"] != record["transaction_id"]
        or evidence["release_id"] != record["candidate_release_id"]
        or evidence["manifest_sha256"] != record["candidate_manifest_digest"]
        or evidence["manifest_sha256"] != sha256_hex(canonical_json_bytes(dict(manifest)))
        or evidence["source_commit"] != manifest["source"]["commit"]
        or evidence["source_tree"] != manifest["source"]["tree"]
        or evidence["source_root_digest"] != manifest["source"]["root_digest"]
        or evidence["dependency_lock_digest"] != manifest["dependencies"]["lock_digest"]
        or evidence["unit_generation_id"] != manifest["build"]["unit_generation_id"]
        or evidence["unit_bundle_digest"] != manifest["build"]["unit_bundle_digest"]
        or evidence["openssl_identity"] != "/usr/bin/openssl"
        or not isinstance(evidence["accepted_key_ids"], list)
        or not isinstance(evidence["signature_results"], list)
        or evidence["verifier_version"] != "aether-release-verify.v1"
    ):
        raise EntrypointError("root trust evidence is not bound to the candidate")
    try:
        datetime_value = evidence["verified_at_utc"]
        if not isinstance(datetime_value, str) or not datetime_value.endswith(("+00:00", "Z")):
            raise ValueError
        fixed_verifier, digest = fixed_verifier_identity(root)
        if evidence["verifier_sha256"] != digest or not fixed_verifier.is_file():
            raise ValueError
    except (TrustBootstrapError, ValueError) as exc:
        raise EntrypointError("root trust verifier identity is not bound") from exc


def _validate_state(root: Path, record: Mapping[str, object], compatibility: Mapping[str, object]) -> None:
    path = _under(root, STATE_PATH)
    try:
        info = path.lstat()
        expected_owner = 3003 if root == PRODUCTION_ROOT else os.getuid()
        if stat.S_ISLNK(info.st_mode) or not stat.S_ISREG(info.st_mode) or info.st_uid != expected_owner or stat.S_IMODE(info.st_mode) != 0o600:
            raise EntrypointError("canonical state path is not a regular file")
        uri = f"file:{path}?mode=ro"
        with sqlite3.connect(uri, uri=True) as connection:
            if connection.execute("PRAGMA integrity_check").fetchone() != ("ok",):
                raise EntrypointError("canonical state integrity check failed")
            tables = {
                row[0]
                for row in connection.execute("SELECT name FROM sqlite_master WHERE type='table'")
            }
            expected_tables = {
                "schema_metadata", "aether_instance_trust",
                "owner_security_transactions", "owner_security_audit_events",
            }
            if tables != expected_tables:
                raise EntrypointError("canonical state schema is not exact")
            metadata = connection.execute("SELECT schema_name, schema_version FROM schema_metadata").fetchall()
            if metadata != [("oas_security_kernel", int(compatibility["schema_after"]))]:
                raise EntrypointError("canonical state schema marker is not exact")
    except (OSError, sqlite3.DatabaseError, KeyError, TypeError, ValueError) as exc:
        if isinstance(exc, EntrypointError):
            raise
        raise EntrypointError("canonical state is missing or unreadable") from exc
    record_mode = record["schema_compatibility"]
    manifest_mode = compatibility["mode"]
    expected_record_mode = "UNCHANGED" if manifest_mode in {"UNCHANGED", "CODE_UPGRADE"} else "FORWARD_MIGRATION_REQUIRED"
    if record_mode != expected_record_mode or record["schema_before"] != compatibility["schema_before"] or record["schema_after"] != compatibility["schema_after"]:
        raise EntrypointError("schema compatibility is not transaction-bound")
    migration = record["migration_state"]
    if expected_record_mode == "UNCHANGED" and migration != "NOT_STARTED":
        raise EntrypointError("unexpected migration marker")
    if expected_record_mode == "FORWARD_MIGRATION_REQUIRED" and migration not in {"STARTED", "COMMITTED"}:
        raise EntrypointError("forward migration marker is invalid")


def _validate_runtime_identity(
    root: Path,
    manifest: Mapping[str, object],
    snapshot: RuntimeIdentitySnapshot | None = None,
) -> None:
    runtime = manifest["runtime"]
    if runtime["python"] != "/usr/bin/python3.11" or runtime["python_version"] not in {"3.11", "3.11.0"} or runtime["import_root"] != "/opt/aether/current/runtime/lib/python3.11/site-packages":
        raise EntrypointError("interpreter or import-root identity is not exact")
    expected_import_root = str(runtime["import_root"])
    expected_imports = (expected_import_root, *STANDARD_IMPORT_ROOTS)
    interpreter = _under(root, Path("/usr/bin/python3.11"))
    launcher = _under(root, Path("/opt/aether/current/runtime/bin/python"))
    try:
        interpreter_info = interpreter.lstat()
        launcher_info = launcher.lstat()
        expected_owner = 0 if root == PRODUCTION_ROOT else os.getuid()
        if stat.S_ISLNK(interpreter_info.st_mode) or not stat.S_ISREG(interpreter_info.st_mode) or interpreter_info.st_nlink != 1 or interpreter_info.st_uid != expected_owner or stat.S_IMODE(interpreter_info.st_mode) != 0o755:
            raise EntrypointError("verified interpreter identity is invalid")
        if not stat.S_ISLNK(launcher_info.st_mode) or os.readlink(launcher) != "../../../../../usr/bin/python3.11" or launcher.resolve() != interpreter.resolve():
            raise EntrypointError("runtime launcher identity is invalid")
    except OSError as exc:
        raise EntrypointError("verified interpreter cannot be inspected") from exc
    import_root = _under(root, Path("/opt/aether/current/runtime/lib/python3.11/site-packages"))
    try:
        if import_root.is_symlink() or not import_root.is_dir() or _under(root, Path("/opt/aether/current/runtime/lib/python3.11")).is_symlink():
            raise EntrypointError("verified import root is missing")
        for import_path in expected_imports:
            path = _under(root, Path(import_path))
            if path.is_symlink():
                raise EntrypointError("verified standard import root is invalid")
    except OSError as exc:
        raise EntrypointError("verified import root cannot be inspected") from exc
    module = import_root / "aether/oas/host_entrypoint.py"
    if not module.is_file() or module.is_symlink():
        raise EntrypointError("verified host module identity is invalid")
    try:
        module_info = module.lstat()
        expected_owner = 0 if root == PRODUCTION_ROOT else os.getuid()
        if not stat.S_ISREG(module_info.st_mode) or module_info.st_nlink != 1 or module_info.st_uid != expected_owner:
            raise EntrypointError("verified host module identity is ambiguous")
    except OSError as exc:
        raise EntrypointError("verified host module cannot be inspected") from exc
    observed = snapshot
    if observed is None and root == PRODUCTION_ROOT:
        observed = collect_runtime_identity_snapshot(
            authorized_import_roots=expected_imports
        )
    if observed is not None:
        if not isinstance(observed, RuntimeIdentitySnapshot):
            raise EntrypointError("runtime identity snapshot type is invalid")
        expected_module = f"{expected_import_root}/aether/oas/host_entrypoint.py"
        if (
            observed.proc_self_exe != "/usr/bin/python3.11"
            or observed.sys_executable != "/usr/bin/python3.11"
            or observed.python_version not in {"3.11", "3.11.0"}
            or observed.abi_tag != "cpython-311"
            or observed.soabi not in {"cpython-311-x86_64-linux-gnu", "cpython-311"}
            or observed.machine != "x86_64"
            or observed.module_path != expected_module
            or observed.module_sha256 != hashlib.sha256(module.read_bytes()).hexdigest()
            or observed.authorized_import_roots != expected_imports
            or observed.sys_path != expected_imports
            or observed.capabilities != "0000000000000000"
            or observed.uid != EXPECTED_OAS_UID
            or observed.gid != EXPECTED_OAS_GID
            or observed.groups != EXPECTED_OAS_GROUPS
        ):
            raise EntrypointError("current process runtime identity is not exact")


def _validate_dependency_closure(root: Path, manifest: Mapping[str, object]) -> None:
    dependencies = manifest["dependencies"]
    if dependencies["closure_status"] != "COMPLETE" or not dependencies["artifacts"]:
        raise EntrypointError("dependency closure is incomplete")
    release_id = _release_id_from_link(root)
    release = _under(root, RELEASE_ROOT / release_id)
    lock = release / "deployment/requirements.lock.json"
    wheelhouse = release / "deployment/wheelhouse"
    if not lock.is_file() or not wheelhouse.is_dir():
        raise EntrypointError("installed dependency lock or wheelhouse is missing")
    try:
        if sha256_hex(lock.read_bytes()) != dependencies["lock_digest"]:
            raise EntrypointError("installed dependency lock is not transaction-bound")
        verify_dependency_closure(lock, wheelhouse)
        verify_installed_closure(lock, _under(root, Path("/opt/aether/current/runtime/lib/python3.11/site-packages")))
    except (OSError, DependencyLockError, KeyError, TypeError, ValueError) as exc:
        if isinstance(exc, EntrypointError):
            raise
        raise EntrypointError("installed dependency closure is not exact") from exc


def _validate_release_artifacts(
    root: Path,
    record: Mapping[str, object],
    release_id: str,
) -> Mapping[str, object]:
    release = _under(root, RELEASE_ROOT / release_id)
    manifest = _read_object(release / "release-manifest.json")
    try:
        normalized = validate_manifest(manifest)
    except ManifestError as exc:
        raise EntrypointError("release manifest is invalid") from exc
    manifest_bytes = (release / "release-manifest.json").read_bytes()
    if normalized["release_id"] != release_id or sha256_hex(manifest_bytes) != record["candidate_manifest_digest"]:
        raise EntrypointError("release manifest identity is not bound to activation record")
    try:
        _validate_inventory(release, manifest, root=root)
    except TrustBootstrapError as exc:
        raise EntrypointError("release inventory is not exact") from exc
    if normalized["build"]["unit_bundle_digest"] != record["unit_bundle_digest"]:
        raise EntrypointError("manifest unit bundle is not bound to activation record")
    _validate_trust_evidence(root, record, manifest)
    try:
        expected_generation, digest = verify_unit_directory(_under(root, Path("/etc/systemd/system")), record["candidate_unit_generation_id"])
    except Exception as exc:
        raise EntrypointError("unit generation verification failed") from exc
    if digest != record["unit_bundle_digest"]:
        raise EntrypointError("unit bundle digest is not bound to activation record")
    unit_dir = _under(root, Path("/etc/systemd/system"))
    for item in manifest["units"]:
        path = unit_dir / item["name"]
        try:
            info = path.lstat()
            if stat.S_ISLNK(info.st_mode) or not stat.S_ISREG(info.st_mode) or stat.S_IMODE(info.st_mode) != 0o644 or info.st_uid != (0 if root == PRODUCTION_ROOT else os.getuid()) or info.st_size != item["size"] or sha256_hex(path.read_bytes()) != item["sha256"]:
                raise EntrypointError("installed unit inventory is not exact")
        except OSError as exc:
            raise EntrypointError("installed unit inventory cannot be inspected") from exc
    gate = _under(root, Path("var/lib/aether/activation/unit-generations") / f"{expected_generation}.ready")
    gate_data = _read_object(gate)
    try:
        gate_info = gate.lstat()
        expected_owner = 0 if root == PRODUCTION_ROOT else os.getuid()
        if gate_info.st_uid != expected_owner or gate_info.st_nlink != 1 or stat.S_IMODE(gate_info.st_mode) != 0o444:
            raise EntrypointError("unit generation gate ownership or mode is invalid")
    except OSError as exc:
        raise EntrypointError("unit generation gate cannot be inspected") from exc
    if gate_data.get("status") != "VERIFIED" or gate_data.get("transaction_id") != record["transaction_id"] or gate_data.get("generation_id") != expected_generation or gate_data.get("unit_bundle_digest") != digest:
        raise EntrypointError("unit generation gate is not transaction-bound")
    return normalized


def validate_activation(
    root: str | Path = PRODUCTION_ROOT,
    *,
    now: float | None = None,
    boot_id: str | None = None,
    runtime_validator: Callable[..., None] = _validate_runtime_identity,
    runtime_identity_snapshot: RuntimeIdentitySnapshot | None = None,
    dependency_validator: Callable[..., None] = _validate_dependency_closure,
    state_validator: Callable[..., None] = _validate_state,
) -> dict:
    raw_root = Path(root)
    base = raw_root.resolve()
    if base == Path("/") and raw_root != PRODUCTION_ROOT:
        raise EntrypointError("real host root must be explicitly selected")
    record = read_production_record() if base == Path("/") else read_record(base)
    state = ActivationState(record["state"])
    if state == ActivationState.ACTIVATING:
        current = _release_id_from_link(base)
        if current != record["candidate_release_id"] or record["current_link_release_id"] != current or record["commit_state"] != "UNCOMMITTED":
            raise EntrypointError("candidate activation identity is not authorized")
        if now is None:
            now = time.monotonic()
        current_boot = boot_id or Path("/proc/sys/kernel/random/boot_id").read_text(encoding="ascii").strip()
        if current_boot != record["host_boot_id"] or not record["activation_issued_at_monotonic"] < now < record["activation_expires_at_monotonic"]:
            raise EntrypointError("candidate activation window is stale or expired")
    elif state == ActivationState.COMMITTED:
        current = _release_id_from_link(base)
        if record["commit_state"] != "COMMITTED" or record["current_link_release_id"] != current or current != record["candidate_release_id"]:
            raise EntrypointError("committed release identity is inconsistent")
    else:
        raise EntrypointError("activation record does not authorize startup")
    manifest = _validate_release_artifacts(
        base,
        record,
        record["candidate_release_id"],
    )
    try:
        if runtime_validator is _validate_runtime_identity:
            runtime_validator(base, manifest, runtime_identity_snapshot)
        else:
            runtime_validator(base, manifest)
        dependency_validator(base, manifest)
        state_validator(base, record, manifest["schema_compatibility"])
    except EntrypointError:
        raise
    except Exception as exc:
        raise EntrypointError("canonical state verification failed") from exc
    return record


def activation_contract(root: str | Path = PRODUCTION_ROOT) -> ActivationContract:
    base = Path(root)
    paths = {
        role: _under(base, SOCKET_ROOT / f"{role}.sock")
        for role in EXPECTED_ENDPOINT_NAMES
    }
    return ActivationContract(tuple(SocketExpectation(role, str(paths[role]), 3003, {"runtime": 3002, "bootstrap": 3004, "broker": 0}[role], 0o660) for role in EXPECTED_ENDPOINT_NAMES))


def identity_contract() -> ServiceIdentityContract:
    return ServiceIdentityContract(
        runtime=PeerExpectation("aether-runtime", 3002, 3002),
        bootstrap=PeerExpectation("aether-bootstrap", 3004, 3004),
        broker=PeerExpectation("root-broker", 0, 0),
    )


def run_entrypoint(
    root: str | Path = PRODUCTION_ROOT,
    *,
    environment: dict[str, str] | None = None,
    shutdown_event: threading.Event | None = None,
    notifier=notify_ready,
    adapters: EntrypointAdapters | None = None,
) -> int:
    env = dict(os.environ) if environment is None else environment
    protocol = validate_environment(env)
    base = Path(root)
    selected = adapters or EntrypointAdapters()
    if base.resolve() == Path("/") and (environment is not None or shutdown_event is not None or notifier is not notify_ready or adapters is not None):
        raise EntrypointError("production entrypoint test seams are not permitted")
    runtime_validator = selected.runtime_validator or _validate_runtime_identity
    dependency_validator = selected.dependency_validator or _validate_dependency_closure
    state_validator = selected.state_validator or _validate_state
    descriptor_intake = selected.descriptor_intake or intake_activated_descriptors
    service_factory = selected.service_factory or OASService
    record = validate_activation(
        base,
        runtime_validator=runtime_validator,
        runtime_identity_snapshot=selected.runtime_identity_snapshot,
        dependency_validator=dependency_validator,
        state_validator=state_validator,
    )
    # Do not allow ambient manager metadata to become application input.
    if environment is None:
        os.environ.clear()
        os.environ.update(protocol)
    descriptors: ActivatedDescriptors | None = None
    service: OASService | None = None
    try:
        descriptors = descriptor_intake(activation_contract(base), environment=protocol)
        service = service_factory(_under(base, STATE_PATH), descriptors, identity_contract())
        service.start()
        notifier(environment=protocol)
        event = shutdown_event or threading.Event()
        if shutdown_event is None:
            service.serve_forever(shutdown_event=event)
        else:
            event.wait()
        return 0
    except Exception:
        raise
    finally:
        if service is not None:
            service.shutdown()
        elif descriptors is not None:
            descriptors.close()


def main() -> int:
    return run_entrypoint()
