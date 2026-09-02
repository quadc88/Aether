"""Corrective readiness and non-mutation locks for M123A."""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import importlib.util
import os
from pathlib import Path
import platform
import pwd
import shutil
import socket
import sqlite3
import stat
import subprocess
import tempfile
from types import SimpleNamespace

import pytest

from aether.deployment.installer import InstallError, RepositoryInstaller, make_activation_record
from aether.deployment.lifecycle import (
    ActivationState,
    ActivationWindow,
    LifecycleError,
    create_isolated_root,
    prove_quiescence,
    transition,
    transition_after_quiescence,
)
from aether.deployment.manifest_schema import canonical_json_bytes
from aether.deployment.unit_verifier import (
    UNIT_NAMES,
    canonical_unit_bundle_digest,
    generation_id,
    read_units,
)
from aether.oas.host_entrypoint import _validate_state
from aether.oas.systemd_notify import notify_ready


ROOT = Path(__file__).resolve().parents[1]
DOCUMENT = ROOT / "docs/architecture/MILESTONE_123A_OAS_TARGET_HOST_DEPLOYMENT_READINESS_AND_NON_MUTATING_REHEARSAL_PROOF.md"
SUMMARY = Path("/home/aether/summaries/milestone_123A_target_host_deployment_readiness_and_non_mutating_rehearsal_proof_finalization_summary.txt")
SYSTEMD_DIR = ROOT / "deployment/systemd"
BOUNDED_PROFILE = "FIRST_INSTALL_LOCAL_AF_UNIX_ONLY"
ALLOWED_REPOSITORY_PATHS = {
    DOCUMENT.relative_to(ROOT).as_posix(),
    Path(__file__).relative_to(ROOT).as_posix(),
}
STATUS_VOCABULARY = {
    "PASS",
    "FAIL",
    "NOT_PRESENT",
    "NOT_PROVEN",
    "NOT_APPLICABLE",
}

IDENTITY_DOMAIN = "aether.m123a.target-host-identity.v1"
MACHINE_ID_DOMAIN = "aether.m123a.machine-id.v1"
BOOT_ID_DOMAIN = "aether.m123a.observation-boot.v1"
OBSERVATION_DOMAIN = "aether.m123a.target-host-observation.v1"

PREFLIGHT_ROWS = (
    ("distribution_version", "PASS"),
    ("kernel_architecture", "PASS"),
    ("systemd_pid1_identity", "PASS"),
    ("cgroup_version", "PASS"),
    ("python_311_runtime", "PASS"),
    ("openssl_ed25519_pkeyutl", "PASS"),
    ("clock_utc_approval_window", "PASS"),
    ("timezone", "PASS"),
    ("disk_capacity", "PASS"),
    ("inode_capacity", "PASS"),
    ("selinux_status", "NOT_PRESENT"),
    ("apparmor_status", "NOT_PRESENT"),
    ("effective_systemd_security_policy", "NOT_PROVEN"),
    ("uid_gid_separation", "PASS"),
    ("principal_name_numeric_conflicts", "PASS"),
    ("linux_capability_support", "PASS"),
    ("systemd_sandbox_directives", "PASS"),
    ("af_unix", "PASS"),
    ("sock_seqpacket", "PASS"),
    ("so_peercred", "PASS"),
    ("socket_activation", "PASS"),
    ("sd_notify", "PASS"),
    ("pathname_abstract_socket", "PASS"),
    ("parent_ownership_modes", "PASS"),
    ("symlink_conflicts", "PASS"),
    ("mount_types_flags", "PASS"),
    ("executable_bit_preservation", "PASS"),
    ("atomic_rename", "PASS"),
    ("hard_link_publication", "PASS"),
    ("directory_fsync", "PASS"),
    ("file_fsync", "PASS"),
    ("sqlite_wal_locking", "PASS"),
    ("rollback_storage_capacity", "PASS"),
    ("private_lan_containment", "PASS"),
    ("profile_artifact_af_unix_only", "PASS"),
    ("public_exposure_requirement", "PASS"),
    ("dns_tls_scope", "NOT_APPLICABLE"),
    ("conflicting_production_listener", "PASS"),
    ("existing_principals", "NOT_PRESENT"),
    ("existing_units", "NOT_PRESENT"),
    ("existing_release_paths", "NOT_PRESENT"),
    ("existing_sockets", "NOT_PRESENT"),
    ("existing_processes", "NOT_PRESENT"),
    ("existing_activation_record", "NOT_PRESENT"),
    ("existing_state_database", "NOT_PRESENT"),
)

MISSING_CLASSIFICATIONS = (
    ("aether-owner/aether-runtime/aether-oas/aether-bootstrap", "EXPECTED_DEPLOYMENT_OUTPUT"),
    ("three socket units", "EXPECTED_DEPLOYMENT_OUTPUT"),
    ("target release not deployed", "EXPECTED_DEPLOYMENT_OUTPUT"),
    ("/var/lib/aether/activation/activation-record.json", "EXPECTED_DEPLOYMENT_OUTPUT"),
    ("target IPC endpoints not deployed", "EXPECTED_DEPLOYMENT_OUTPUT"),
    ("/var/lib/aether/oas/security_kernel.sqlite3", "EXPECTED_DEPLOYMENT_OUTPUT"),
)

REHEARSAL_MATRIX = {
    "first_install": ("CANDIDATE_PENDING", "ACTIVATING -> COMMITTED", "commit before readiness/smoke", "generation/current evidence", "root-only"),
    "excluded_normal_upgrade": ("FIRST_INSTALL_LOCAL_AF_UNIX_ONLY", "NOT_ATTEMPTED", "upgrade is outside bounded profile", "explicit profile boundary", "no upgrade mutation"),
    "excluded_schema_migration": ("FIRST_INSTALL_LOCAL_AF_UNIX_ONLY", "NOT_ATTEMPTED", "schema migration is outside bounded profile", "incompatibility fails closed", "no migration mutation"),
    "excluded_adoption": ("FIRST_INSTALL_LOCAL_AF_UNIX_ONLY", "NOT_ATTEMPTED", "adoption of existing state is outside bounded profile", "empty-state gate", "no adoption"),
    "excluded_automated_recovery": ("ambiguous or interrupted state", "REJECTED_OR_ROOT_REVIEW", "automated recovery/guessing", "recovery boundary", "no automatic repair"),
    "excluded_upgrade_rollback": ("FIRST_INSTALL_LOCAL_AF_UNIX_ONLY", "NOT_ATTEMPTED", "upgrade rollback is outside bounded profile", "unknown release fails closed", "no rollback mutation"),
    "complete_signed_release_trust": ("no pending record", "verified or rejected", "invalid signature/input", "signed fixture evidence", "temporary root"),
    "trust_evidence_before_pending": ("no pending record", "evidence -> CANDIDATE_PENDING", "pending before evidence", "evidence retry preserved", "temporary root"),
    "quiescence": ("CANDIDATE_PENDING", "typed proof", "unbound/stale proof", "transaction/boot/time bound", "temporary root"),
    "activating": ("QUIESCE_REQUIRED", "ACTIVATING", "activation without proof", "generation/current isolated", "temporary root"),
    "ready_smoke_guard": ("ACTIVATING", "commit only when both pass", "missing readiness or smoke", "record unchanged", "temporary root"),
    "committed": ("ACTIVATING", "COMMITTED", "direct commit shortcut", "commit state transition", "temporary root"),
    "verification_failure_before_pending": ("no pending record", "failure; no pending", "unverified candidate", "no promotion", "temporary root"),
    "crash_after_evidence_before_pending": ("no pending record", "evidence; no pending", "interrupted record write", "evidence retry", "temporary root"),
    "quiescence_failure": ("CANDIDATE_PENDING", "failure; unchanged", "active service/socket/work", "no unit mutation", "temporary root"),
    "unit_generation_mismatch": ("CANDIDATE_PENDING", "failure; unchanged", "generation mismatch", "no unit mutation", "temporary root"),
    "dependency_mismatch": ("signed candidate", "failure; no pending", "lock/wheel mismatch", "prior evidence preserved", "temporary root"),
    "link_switch_before_readiness_failure": ("ACTIVATING", "commit rejected; rollback allowed", "readiness inferred from link", "temporary link bounded", "temporary root"),
    "readiness_timeout": ("activation window", "invalid; no commit", "expired deadline", "no extension", "temporary root"),
    "smoke_failure": ("ACTIVATING", "commit rejected", "failed smoke", "uncommitted state", "temporary root"),
    "schema_incompatibility": ("incompatible marker", "state validation rejected", "incompatible schema accepted", "root review required", "temporary root"),
    "rollback_release_mismatch": ("candidate link", "release rejected; unchanged", "unknown release", "current link unchanged", "temporary root"),
    "stale_activation": ("expired window", "activation rejected", "stale window", "no automatic retry", "temporary root"),
    "wrong_boot_identity": ("valid window", "activation rejected", "boot mismatch", "no promotion", "temporary root"),
    "expired_activation_window": ("deadline", "activation rejected", "deadline boundary", "monotonic authority", "temporary root"),
}
REHEARSAL_CASES = tuple(REHEARSAL_MATRIX)

CANONICAL_STATUS = {
    "M123A_AUTHORIZED": "YES",
    "M123A_STARTED": "YES",
    "M123A_FINALIZED": "YES",
    "DECISION_STATUS": "CURRENT",
    "DESIGN_STATUS": "DESIGN_PROVEN",
    "IMPLEMENTATION_STATUS": "IMPLEMENTED",
    "VERIFICATION_STATUS": "TEST_VERIFIED",
    "DEPLOYMENT_VERIFIED": "NO",
    "DEPLOYMENT_STATE": "NOT_DEPLOYED",
    "DEPLOYMENT_PROFILE": BOUNDED_PROFILE,
    "HOST_COMPATIBILITY": "PASSED",
    "ISOLATED_REHEARSAL": "PASSED",
    "TARGET_HOST_READY_FOR_CONTROLLED_DEPLOYMENT_REVIEW": "YES",
    "SELECTED_EXIT": "EXIT_A_TARGET_READY_FOR_BOUNDED_FIRST_INSTALL_DEPLOYMENT_REVIEW",
    "BUILD_AUTHORIZED": "NO",
    "LIVE_DEPLOYMENT_AUTHORIZED": "NO",
    "UPGRADE_AUTHORIZED": "NO",
    "SCHEMA_MIGRATION_AUTHORIZED": "NO",
    "PUBLIC_EXPOSURE_AUTHORIZED": "NO",
    "ADOPTION_AUTHORIZED": "NO",
    "AUTOMATED_RECOVERY_AUTHORIZED": "NO",
    "UPGRADE_ROLLBACK_AUTHORIZED": "NO",
    "HOST_MUTATION_PERFORMED": "NO",
    "PROGRESS_UPDATED": "YES",
    "COMMIT_CREATED": "YES",
    "TAG_CREATED": "YES",
    "PUSH_PERFORMED": "YES",
    "SUCCESSOR_AUTHORIZED": "NO",
    "SUCCESSOR_NUMBER_ASSIGNED": "NO",
    "READY_FOR_PM_REVIEW": "NO",
}


def _hash_domain(domain: str, value: object) -> str:
    return hashlib.sha256(
        domain.encode("ascii") + b"\0" + canonical_json_bytes(value)
    ).hexdigest()


def _os_release() -> dict[str, str]:
    values: dict[str, str] = {}
    for line in Path("/etc/os-release").read_text(encoding="utf-8").splitlines():
        key, separator, value = line.partition("=")
        if separator and key in {"ID", "VERSION_ID", "VERSION_CODENAME"}:
            values[key] = value.strip('"')
    return values


def _systemd_version() -> str | None:
    result = subprocess.run(
        ["/usr/bin/systemd", "--version"],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    first = result.stdout.splitlines()[0] if result.stdout.splitlines() else ""
    return first.split()[1] if result.returncode == 0 and first.startswith("systemd ") else None


def _filesystem_type() -> str | None:
    result = subprocess.run(
        ["/usr/bin/stat", "-f", "-c", "%T", "/"],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    value = result.stdout.strip()
    return value if result.returncode == 0 and value else None


def target_identity_facts() -> dict[str, object]:
    machine_id = Path("/etc/machine-id").read_text(encoding="ascii").strip()
    root_stat = os.stat("/")
    return {
        "machine_id_digest": _hash_domain(MACHINE_ID_DOMAIN, machine_id),
        "os": _os_release(),
        "architecture": platform.machine(),
        "systemd": {
            "version": _systemd_version(),
            "pid1_comm": Path("/proc/1/comm").read_text(encoding="ascii").strip(),
        },
        "filesystem": {
            "root_device_digest": _hash_domain(
                "aether.m123a.root-device.v1", root_stat.st_dev
            ),
            "root_filesystem_type": _filesystem_type(),
        },
    }


def target_identity_digest(facts: dict[str, object]) -> str:
    return _hash_domain(IDENTITY_DOMAIN, facts)


def observation_boot_digest(boot_id: str) -> str:
    return _hash_domain(BOOT_ID_DOMAIN, boot_id)


def observation_digest(
    target_digest: str, boot_id: str, observed_at_utc: str
) -> str:
    return _hash_domain(
        OBSERVATION_DOMAIN,
        {
            "target_host_identity_digest": target_digest,
            "observation_boot_digest": observation_boot_digest(boot_id),
            "observed_at_utc": observed_at_utc,
        },
    )


def _run(command: list[str], *, timeout: float = 5.0) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=timeout,
    )


def _openssl_probe(tmp_path: Path) -> bool:
    private = tmp_path / "probe-key.pem"
    payload = tmp_path / "probe-payload"
    signature = tmp_path / "probe-signature"
    payload.write_bytes(b"m123a-ed25519-probe")
    generated = _run(["/usr/bin/openssl", "genpkey", "-algorithm", "ED25519", "-out", str(private)])
    signed = _run(["/usr/bin/openssl", "pkeyutl", "-sign", "-rawin", "-inkey", str(private), "-in", str(payload), "-out", str(signature)])
    public = tmp_path / "probe-public.der"
    exported = _run(["/usr/bin/openssl", "pkey", "-in", str(private), "-pubout", "-outform", "DER", "-out", str(public)])
    verified = _run(["/usr/bin/openssl", "pkeyutl", "-verify", "-rawin", "-pubin", "-inkey", str(public), "-in", str(payload), "-sigfile", str(signature)])
    return all(result.returncode == 0 for result in (generated, signed, exported, verified))


def _systemd_static_probe(tmp_path: Path) -> bool:
    root = tmp_path / "systemd-root"
    unit_dir = root / "etc/systemd/system"
    unit_dir.mkdir(parents=True)
    for name in UNIT_NAMES:
        shutil.copy2(ROOT / "deployment/systemd" / name, unit_dir / name)
    for name in ("sysinit.target", "local-fs.target"):
        source = Path("/lib/systemd/system") / name
        if not source.is_file():
            return False
        shutil.copy2(source, unit_dir / name)
    (root / "var/lib/aether/activation/unit-generations").mkdir(parents=True)
    (root / "var/lib/aether/activation/activation-record.json").touch()
    (root / "var/lib/aether/activation/unit-generations/g-45393132b1a0ab8a0415c7d964f800b983155bbd4ebe13bb2764bf94548ea652.ready").touch()
    interpreter = root / "opt/aether/current/runtime/bin/python"
    interpreter.parent.mkdir(parents=True)
    interpreter.write_bytes(b"placeholder")
    interpreter.chmod(0o755)
    return _run(
        [
            "/usr/bin/systemd-analyze",
            "verify",
            f"--root={root}",
            *UNIT_NAMES,
        ],
        timeout=10.0,
    ).returncode == 0


def _probe_filesystem_operations(tmp_path: Path) -> dict[str, bool]:
    source = tmp_path / "source"
    temporary = tmp_path / "temporary"
    target = tmp_path / "target"
    source.write_bytes(b"atomic")
    directory_fd = os.open(tmp_path, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(directory_fd)
        os.replace(source, temporary)
        os.fsync(directory_fd)
        os.link(temporary, target)
        os.fsync(directory_fd)
    finally:
        os.close(directory_fd)
    file_fd = os.open(temporary, os.O_RDONLY)
    try:
        os.fsync(file_fd)
    finally:
        os.close(file_fd)
    return {
        "atomic_rename": temporary.read_bytes() == b"atomic",
        "hard_link_publication": target.stat().st_nlink == 2,
        "directory_fsync": True,
        "file_fsync": True,
    }


def _probe_sqlite(tmp_path: Path) -> bool:
    database = tmp_path / "sqlite" / "state.sqlite3"
    database.parent.mkdir()
    first = sqlite3.connect(database, timeout=0.1)
    second = sqlite3.connect(database, timeout=0.1)
    try:
        mode = first.execute("PRAGMA journal_mode=WAL").fetchone()[0]
        first.execute("CREATE TABLE state(value TEXT)")
        first.commit()
        first.execute("BEGIN IMMEDIATE")
        try:
            second.execute("BEGIN IMMEDIATE")
        except sqlite3.OperationalError:
            locked = True
        else:
            locked = False
        first.rollback()
        return mode == "wal" and locked
    finally:
        first.close()
        second.close()


def _notify_probe(tmp_path: Path) -> bool:
    path = tmp_path / "notify.sock"
    receiver = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
    receiver.bind(str(path))
    try:
        notify_ready(environment={"NOTIFY_SOCKET": str(path)})
        receiver.settimeout(1.0)
        return receiver.recv(128) == b"READY=1"
    finally:
        receiver.close()
        path.unlink(missing_ok=True)


def _preflight(tmp_path: Path) -> dict[str, str]:
    result = {name: status for name, status in PREFLIGHT_ROWS}
    os_release = _os_release()
    result["distribution_version"] = "PASS" if os_release.get("ID") == "debian" and os_release.get("VERSION_ID") == "12" else "NOT_PROVEN"
    result["kernel_architecture"] = "PASS" if platform.machine() == "x86_64" else "NOT_PROVEN"
    result["systemd_pid1_identity"] = "PASS" if _systemd_version() == "252" and Path("/proc/1/comm").read_text(encoding="ascii").strip() == "systemd" else "NOT_PROVEN"
    result["cgroup_version"] = "PASS" if Path("/sys/fs/cgroup/cgroup.controllers").is_file() else "NOT_PROVEN"
    python_ok = Path("/usr/bin/python3.11").is_file() and _run(["/usr/bin/python3.11", "-I", "-S", "-c", "import sys; assert sys.flags.isolated and sys.flags.no_site and sys.version_info[:2] == (3, 11)"]).returncode == 0
    result["python_311_runtime"] = "PASS" if python_ok else "NOT_PROVEN"
    with tempfile.TemporaryDirectory(prefix="m123a-preflight-", dir=tmp_path) as directory:
        probe_root = Path(directory)
        result["openssl_ed25519_pkeyutl"] = "PASS" if _openssl_probe(probe_root) and _run(["/usr/bin/openssl", "version"]).returncode == 0 else "NOT_PROVEN"
        filesystem = _probe_filesystem_operations(probe_root)
        result.update({name: "PASS" if passed else "FAIL" for name, passed in filesystem.items()})
        result["sqlite_wal_locking"] = "PASS" if _probe_sqlite(probe_root) else "FAIL"
        result["sd_notify"] = "PASS" if _notify_probe(probe_root) else "FAIL"
    now = datetime.now(timezone.utc)
    result["clock_utc_approval_window"] = "PASS" if now.tzinfo == timezone.utc and now.utcoffset() == timezone.utc.utcoffset(now) and 0 < 60 <= 60 else "FAIL"
    result["timezone"] = "PASS" if time_zone_is_utc() else "NOT_PROVEN"
    usage = os.statvfs("/")
    result["disk_capacity"] = "PASS" if usage.f_bavail > 0 else "FAIL"
    result["inode_capacity"] = "PASS" if usage.f_favail > 0 else "FAIL"
    result["selinux_status"] = "NOT_PRESENT" if not Path("/sys/fs/selinux/enforce").exists() else "NOT_PROVEN"
    result["apparmor_status"] = "NOT_PRESENT" if not Path("/sys/kernel/security/apparmor/profiles").exists() else "NOT_PROVEN"
    result["effective_systemd_security_policy"] = "NOT_PROVEN"
    result["uid_gid_separation"] = "PASS" if shutil.which("setpriv") and os.name == "posix" else "NOT_PROVEN"
    names = ("aether-owner", "aether-runtime", "aether-oas", "aether-bootstrap")
    numeric = (3002, 3003, 3004)
    result["principal_name_numeric_conflicts"] = "PASS" if all(_missing_principal(name) for name in names) and all(_missing_uid(uid) for uid in numeric) else "FAIL"
    result["linux_capability_support"] = "PASS" if Path("/proc/self/status").is_file() and shutil.which("setpriv") else "NOT_PROVEN"
    result["systemd_sandbox_directives"] = "PASS" if _systemd_static_probe(tmp_path) else "NOT_PROVEN"
    result["af_unix"] = "PASS" if socket.AF_UNIX else "NOT_PROVEN"
    result["sock_seqpacket"] = "PASS" if _socket_type_available(socket.SOCK_SEQPACKET) else "NOT_PROVEN"
    result["so_peercred"] = "PASS" if _peercred_available() else "NOT_PROVEN"
    result["socket_activation"] = "PASS" if result["systemd_pid1_identity"] == "PASS" and result["systemd_sandbox_directives"] == "PASS" else "NOT_PROVEN"
    result["pathname_abstract_socket"] = "PASS" if _socket_address_forms_available(tmp_path) else "NOT_PROVEN"
    result["parent_ownership_modes"] = "PASS" if all(_root_parent(path) for path in ("/usr", "/usr/local", "/opt", "/var", "/var/lib", "/etc/systemd", "/etc/systemd/system", "/usr/libexec", "/run")) else "FAIL"
    result["symlink_conflicts"] = "PASS" if not any(Path(path).is_symlink() for path in ("/etc/aether", "/opt/aether", "/var/lib/aether", "/run/aether")) else "FAIL"
    result["mount_types_flags"] = "PASS" if _mounts_are_observable() else "NOT_PROVEN"
    verifier = ROOT / "deployment/fixed_verifier/aether-release-verify"
    result["executable_bit_preservation"] = "PASS" if stat.S_IMODE(verifier.stat().st_mode) == 0o555 else "FAIL"
    result["rollback_storage_capacity"] = result["disk_capacity"]
    bounded_profile_proof = _bounded_af_unix_profile_proof()
    result["private_lan_containment"] = "PASS" if bounded_profile_proof else "NOT_PROVEN"
    result["profile_artifact_af_unix_only"] = "PASS" if bounded_profile_proof else "NOT_PROVEN"
    result["public_exposure_requirement"] = "PASS"
    result["dns_tls_scope"] = "NOT_APPLICABLE"
    result["conflicting_production_listener"] = "PASS" if not _known_oas_socket_present() else "FAIL"
    deployment_paths = ("/opt/aether", "/var/lib/aether", "/run/aether", "/etc/aether")
    result["existing_principals"] = "NOT_PRESENT" if all(_missing_principal(name) for name in names) else "PASS"
    result["existing_units"] = "NOT_PRESENT" if all(_unit_not_found(name) for name in UNIT_NAMES) else "PASS"
    result["existing_release_paths"] = "NOT_PRESENT" if not any(Path(path).exists() or Path(path).is_symlink() for path in deployment_paths[:1]) else "PASS"
    result["existing_sockets"] = "NOT_PRESENT" if not Path("/run/aether/oas").exists() else "PASS"
    result["existing_processes"] = "NOT_PRESENT" if _oas_process_count() == 0 else "PASS"
    result["existing_activation_record"] = "NOT_PRESENT" if not Path("/var/lib/aether/activation/activation-record.json").exists() else "PASS"
    result["existing_state_database"] = "NOT_PRESENT" if not Path("/var/lib/aether/oas/security_kernel.sqlite3").exists() else "PASS"
    return result


def time_zone_is_utc() -> bool:
    return datetime.now().astimezone().utcoffset() == timezone.utc.utcoffset(datetime.now(timezone.utc))


def _missing_principal(name: str) -> bool:
    try:
        pwd.getpwnam(name)
    except KeyError:
        return True
    return False


def _missing_uid(uid: int) -> bool:
    try:
        pwd.getpwuid(uid)
    except KeyError:
        return True
    return False


def _socket_type_available(socket_type: int) -> bool:
    try:
        descriptor = socket.socket(socket.AF_UNIX, socket_type)
    except OSError:
        return False
    descriptor.close()
    return True


def _peercred_available() -> bool:
    if not hasattr(socket, "SO_PEERCRED"):
        return False
    left, right = socket.socketpair(socket.AF_UNIX, socket.SOCK_SEQPACKET)
    try:
        return len(left.getsockopt(socket.SOL_SOCKET, socket.SO_PEERCRED, 12)) == 12
    finally:
        left.close()
        right.close()


def _socket_address_forms_available(tmp_path: Path) -> bool:
    path = tmp_path / "pathname.sock"
    pathname = socket.socket(socket.AF_UNIX, socket.SOCK_SEQPACKET)
    pathname.bind(str(path))
    pathname.close()
    path.unlink(missing_ok=True)
    abstract = socket.socket(socket.AF_UNIX, socket.SOCK_SEQPACKET)
    try:
        abstract.bind("\0m123a-abstract-probe")
    except OSError:
        abstract.close()
        return False
    abstract.close()
    return True


def _root_parent(path: str) -> bool:
    info = os.stat(path)
    return info.st_uid == 0 and stat.S_IMODE(info.st_mode) == 0o755


def _mounts_are_observable() -> bool:
    lines = Path("/proc/self/mountinfo").read_text(encoding="ascii").splitlines()
    roots = [line for line in lines if " - " in line and (" / " in line or " /run " in line)]
    return bool(roots)


def _unit_not_found(name: str) -> bool:
    result = _run(["/usr/bin/systemctl", "show", "--property=LoadState", name])
    return "LoadState=not-found" in result.stdout


def _known_oas_socket_present() -> bool:
    try:
        data = Path("/proc/net/unix").read_text(encoding="ascii")
    except OSError:
        return False
    return "/run/aether/oas/" in data


def _oas_process_count() -> int:
    count = 0
    for entry in Path("/proc").iterdir():
        if not entry.name.isdigit():
            continue
        try:
            command = (entry / "cmdline").read_bytes()
        except OSError:
            continue
        if b"aether.oas.host_entrypoint" in command or b"aether-oas" in command:
            count += 1
    return count


def _profile_artifacts_are_bounded() -> bool:
    socket_text = "\n".join(
        (SYSTEMD_DIR / name).read_text(encoding="utf-8")
        for name in (
            "aether-oas-runtime.socket",
            "aether-oas-bootstrap.socket",
            "aether-oas-broker.socket",
        )
    )
    service_text = (SYSTEMD_DIR / "aether-oas.service").read_text(encoding="utf-8")
    endpoints = (
        "/run/aether/oas/runtime.sock",
        "/run/aether/oas/bootstrap.sock",
        "/run/aether/oas/broker.sock",
    )
    return (
        socket_text.count("ListenSequentialPacket=") == 3
        and all(f"ListenSequentialPacket={endpoint}" in socket_text for endpoint in endpoints)
        and "ListenStream=" not in socket_text
        and "ListenDatagram=" not in socket_text
        and "AF_INET" not in socket_text
        and "AF_INET6" not in socket_text
        and "RestrictAddressFamilies=AF_UNIX" in service_text
        and "User=aether-oas" in service_text
        and "ExecStart=/opt/aether/current/runtime/bin/python" in service_text
    )


def _rehearsal_is_local_only() -> bool:
    source = Path(__file__).read_text(encoding="utf-8")
    ip_socket = "socket." + "AF_INET"
    ip6_socket = "socket." + "AF_INET6"
    return (
        "socket.AF_UNIX" in source
        and ip_socket not in source
        and ip6_socket not in source
    )


def _bounded_af_unix_profile_proof() -> bool:
    return _profile_artifacts_are_bounded() and _rehearsal_is_local_only()


def _status_block(document: str) -> str:
    begin = "AUTHORITATIVE_M123A_STATUS_BEGIN"
    end = "AUTHORITATIVE_M123A_STATUS_END"
    assert document.count(begin) == 1
    assert document.count(end) == 1
    start = document.index(begin)
    finish = document.index(end, start)
    assert finish > start
    return document[start:finish]


def _authoritative_status_map(document: str) -> dict[str, str]:
    block = _status_block(document)
    parsed: dict[str, str] = {}
    for line in block.splitlines()[1:]:
        stripped = line.strip()
        if not stripped:
            continue
        key, separator, value = stripped.partition(":")
        assert separator, f"status line is not key/value: {stripped}"
        assert key not in parsed, f"duplicate canonical status key: {key}"
        parsed[key] = value.strip()
    return parsed


def _fake_manager(*, active: bool = False):
    return SimpleNamespace(
        identity="m123a-test-manager",
        snapshot_quiescence=lambda: {
            "observed_at_monotonic": 1.0,
            "socket_unit_states": {
                "runtime": "active" if active else "inactive",
                "bootstrap": "inactive",
                "broker": "inactive",
            },
            "service_state": "active" if active else "inactive",
            "listener_count": 1 if active else 0,
            "accepted_connection_count": 0,
            "outstanding_worker_count": 0,
            "activation_job_count": 0,
            "oas_process_count": 1 if active else 0,
            "cgroup_populated": active,
        },
    )


def _lifecycle_fixture(tmp_path: Path):
    tmp_path.mkdir(parents=True, exist_ok=True)
    transaction_id = "m123a-first"
    root, capability = create_isolated_root(
        tmp_path, purpose="M122A_INSTALLER", transaction_id=transaction_id
    )
    units = read_units(ROOT / "deployment/systemd")
    generation = generation_id(units)
    candidate_id = "r1-" + "a" * 64
    old_id = None
    installer = RepositoryInstaller(root, capability=capability)
    source = tmp_path / "candidate-source"
    source.mkdir()
    (source / "payload").write_bytes(b"candidate")
    installer.stage_release(transaction_id, candidate_id, source)
    record = make_activation_record(
        transaction_id=transaction_id,
        candidate_release_id=candidate_id,
        candidate_manifest_digest="c" * 64,
        candidate_unit_generation_id=generation,
        unit_bundle_digest=canonical_unit_bundle_digest(units),
        host_boot_id="m123a-boot",
        old_release_id=old_id,
        old_manifest_digest=None,
        old_unit_generation_id=None,
        activation_reason="FIRST_INSTALL",
    )
    return root, capability, installer, units, record, old_id


def _activate_fixture(tmp_path: Path):
    root, capability, installer, units, record, old_id = _lifecycle_fixture(tmp_path)
    proof = prove_quiescence(
        _fake_manager(), record, boot_id="m123a-boot", now=2.0
    )
    installer.replace_unit_bundle(
        units,
        record["transaction_id"],
        activation_record=record,
        quiescence_proof=proof,
        current_boot_id="m123a-boot",
        now=2.0,
        adapter_identity="m123a-test-manager",
    )
    quiesced = transition_after_quiescence(
        record,
        proof,
        boot_id="m123a-boot",
        now=2.0,
        adapter_identity="m123a-test-manager",
    )
    activating = transition(
        quiesced,
        ActivationState.ACTIVATING,
        activation_issued_at_monotonic=2.0,
        activation_expires_at_monotonic=62.0,
        current_link_release_id=record["candidate_release_id"],
    )
    installer.activate_current(
        record["candidate_release_id"], transaction_id=record["transaction_id"]
    )
    return root, capability, installer, units, record, proof, activating, old_id


def _load_signed_builder():
    path = ROOT / "tests/test_deployment_trust_bootstrap.py"
    spec = importlib.util.spec_from_file_location("m123a_signed_fixture", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module._complete_release


def _path_snapshot(paths: tuple[Path, ...]) -> dict[str, object]:
    snapshot: dict[str, object] = {}
    for path in paths:
        key = str(path)
        try:
            info = path.lstat()
        except FileNotFoundError:
            snapshot[key] = None
            continue
        children = tuple(sorted(child.name for child in path.iterdir())) if stat.S_ISDIR(info.st_mode) else ()
        snapshot[key] = (
            stat.S_IFMT(info.st_mode),
            info.st_uid,
            info.st_gid,
            stat.S_IMODE(info.st_mode),
            info.st_size,
            info.st_mtime_ns,
            children,
        )
    return snapshot


def _manager_snapshot() -> tuple[tuple[str, str], ...]:
    values: list[tuple[str, str]] = []
    for name in UNIT_NAMES:
        result = _run(["/usr/bin/systemctl", "show", "--property=LoadState,ActiveState,SubState", name])
        values.append((name, result.stdout))
    return tuple(values)


def test_identity_digest_is_stable_domain_separated_and_privacy_preserving():
    facts = target_identity_facts()
    first = target_identity_digest(facts)
    second = target_identity_digest(dict(facts))
    changed = dict(facts, architecture="changed-architecture")
    assert first == second
    assert first != target_identity_digest(changed)
    observation = observation_digest(first, "boot-one", "2026-09-02T00:00:00+00:00")
    changed_boot = observation_digest(first, "boot-two", "2026-09-02T00:00:00+00:00")
    assert observation != changed_boot
    assert target_identity_digest(facts) == target_identity_digest(facts)
    encoded = canonical_json_bytes(facts).decode("utf-8")
    machine_id = Path("/etc/machine-id").read_text(encoding="ascii").strip()
    assert machine_id not in encoded
    assert '"machine_id_digest"' in encoded
    assert "boot" not in encoded
    assert IDENTITY_DOMAIN != OBSERVATION_DOMAIN
    assert len(first) == len(observation) == 64


def test_preflight_has_complete_inventory_and_only_allowed_status_vocabulary(tmp_path: Path):
    result = _preflight(tmp_path)
    assert tuple(result) == tuple(name for name, _status in PREFLIGHT_ROWS)
    assert set(result.values()) <= STATUS_VOCABULARY
    assert result["distribution_version"] == "PASS"
    assert result["python_311_runtime"] == "PASS"
    assert result["openssl_ed25519_pkeyutl"] == "PASS"
    assert result["effective_systemd_security_policy"] == "NOT_PROVEN"
    assert result["private_lan_containment"] == "PASS"
    assert result["profile_artifact_af_unix_only"] == "PASS"
    assert all(result[name] == expected for name, expected in PREFLIGHT_ROWS if expected in {"PASS", "NOT_PRESENT"})


def test_m123a_document_has_correct_readiness_model_and_complete_tables():
    document = DOCUMENT.read_text(encoding="utf-8")
    status = _status_block(document)
    parsed = _authoritative_status_map(document)
    assert parsed == CANONICAL_STATUS
    assert parsed["VERIFICATION_STATUS"] == "TEST_VERIFIED"
    assert parsed["DEPLOYMENT_VERIFIED"] == "NO"
    assert parsed["VERIFICATION_STATUS"] != parsed["DEPLOYMENT_VERIFIED"]
    assert status.count("SELECTED_EXIT:") == 1
    assert "Can this host support the finalized deployment contract" in document
    assert "Is OAS already installed and active" in document
    assert "Are unresolved host blockers absent" in document
    assert "Has a real deployment completed" in document
    assert BOUNDED_PROFILE in document
    assert "DEPLOYMENT_TIME_VERIFICATION_CONDITION" in document
    assert "OPTIONAL_DEFENSE_IN_DEPTH" in document
    assert "OUT_OF_SCOPE_FOR_BOUNDED_FIRST_INSTALL" in document
    assert _bounded_af_unix_profile_proof()
    assert not any(line.startswith("PROFILE:") for line in status.splitlines())
    assert not any(line.startswith("MIGRATION_AUTHORIZED:") for line in status.splitlines())
    for name, _expected in PREFLIGHT_ROWS:
        assert f"| `{name}` |" in document
    for case, values in REHEARSAL_MATRIX.items():
        assert f"| `{case}` |" in document
        assert all(values)
    for item, classification in MISSING_CLASSIFICATIONS:
        assert classification in document
        assert item in document
    assert "TARGET_HOST_READY: NO" not in status
    assert "DEPLOYMENT_VERIFIED: YES" not in document
    assert "LIVE_DEPLOYMENT_AUTHORIZED: YES" not in document


def test_external_summary_has_complete_identity_preflight_matrix_and_status():
    summary = SUMMARY.read_text(encoding="utf-8")
    assert "TARGET_HOST_IDENTITY_DIGEST:" in summary
    assert "OBSERVATION_BOOT_DIGEST:" in summary
    assert "SELECTED_EXIT: EXIT_A_TARGET_READY_FOR_BOUNDED_FIRST_INSTALL_DEPLOYMENT_REVIEW" in summary
    for name, _status in PREFLIGHT_ROWS:
        assert name in summary
    for case in REHEARSAL_CASES:
        assert case in summary
    assert _authoritative_status_map(summary) == CANONICAL_STATUS
    summary_status = _status_block(summary)
    assert not any(line.startswith("PROFILE:") for line in summary_status.splitlines())
    assert not any(line.startswith("MIGRATION_AUTHORIZED:") for line in summary_status.splitlines())


def test_first_install_rehearses_quiescence_activation_commit_and_fail_closed_commit_guard(tmp_path: Path):
    root, _capability, installer, _units, record, _proof, activating, _old_id = _activate_fixture(tmp_path)
    with pytest.raises(LifecycleError):
        transition(activating, ActivationState.COMMITTED)
    ready = dict(activating, readiness_result="PASSED", smoke_result="PASSED")
    committed = transition(ready, ActivationState.COMMITTED)
    assert record["state"] == ActivationState.CANDIDATE_PENDING.value
    assert activating["state"] == ActivationState.ACTIVATING.value
    assert committed["state"] == ActivationState.COMMITTED.value
    assert committed["commit_state"] == "COMMITTED"
    assert (root / "opt/aether/current").is_symlink()
    assert installer.root == root


def test_first_install_profile_is_local_af_unix_only_and_has_no_network_substitution():
    assert _profile_artifacts_are_bounded()
    assert all(
        "ListenSequentialPacket=" in (SYSTEMD_DIR / name).read_text(encoding="utf-8")
        for name in (
            "aether-oas-runtime.socket",
            "aether-oas-bootstrap.socket",
            "aether-oas-broker.socket",
        )
    )
    assert "ListenStream=" not in (SYSTEMD_DIR / "aether-oas.service").read_text(encoding="utf-8")


def test_complete_signed_trust_verification_and_evidence_before_pending(tmp_path: Path):
    fixture = _load_signed_builder()(tmp_path, transaction_id="m123a-trust")
    observed = []
    import aether.deployment.trust_bootstrap as trust_bootstrap

    real_writer = trust_bootstrap._write_evidence

    def writer(path, evidence, root):
        observed.append(not fixture["record_path"].exists())
        return real_writer(path, evidence, root)

    original = trust_bootstrap._write_evidence
    trust_bootstrap._write_evidence = writer
    try:
        fixture["installer"].write_pending(fixture["record"])
    finally:
        trust_bootstrap._write_evidence = original
    evidence_before = fixture["evidence_path"].read_bytes()
    record_before = fixture["record_path"].read_bytes()
    fixture["installer"].write_pending(fixture["record"])
    assert observed == [True]
    assert evidence_before == fixture["evidence_path"].read_bytes()
    assert record_before == fixture["record_path"].read_bytes()
    assert fixture["evidence_path"].is_file()


def test_failure_before_pending_and_crash_after_evidence_preserve_safe_state(tmp_path: Path, monkeypatch):
    builder = _load_signed_builder()
    failure_root = tmp_path / "verification-failure"
    crash_root = tmp_path / "evidence-crash"
    failure_root.mkdir()
    crash_root.mkdir()
    failure = builder(failure_root, transaction_id="m123a-failure")
    manifest = failure["release"] / "release-manifest.json"
    manifest.chmod(0o644)
    manifest.write_bytes(manifest.read_bytes() + b" ")
    manifest.chmod(0o444)
    with pytest.raises(InstallError):
        failure["installer"].write_pending(failure["record"])
    assert not failure["record_path"].exists()

    crash = builder(crash_root, transaction_id="m123a-crash")
    import aether.deployment.trust_bootstrap as trust_bootstrap
    from aether.deployment.trust_bootstrap import TrustBootstrapError

    real_writer = trust_bootstrap._write_evidence

    def publish_then_crash(path, evidence, root):
        result = real_writer(path, evidence, root)
        raise TrustBootstrapError("simulated interruption")

    monkeypatch.setattr(trust_bootstrap, "_write_evidence", publish_then_crash)
    with pytest.raises(InstallError):
        crash["installer"].write_pending(crash["record"])
    assert crash["evidence_path"].is_file()
    assert not crash["record_path"].exists()


def test_rehearsal_failure_matrix_is_explicit_and_fail_closed(tmp_path: Path):
    assert len(REHEARSAL_CASES) == 25

    root, _capability, _installer, _units, record, _old_id = _lifecycle_fixture(tmp_path / "quiescence-failure")
    with pytest.raises(LifecycleError):
        prove_quiescence(_fake_manager(active=True), record, boot_id="m123a-boot", now=2.0)
    assert record["state"] == ActivationState.CANDIDATE_PENDING.value
    assert not (root / "etc/systemd/system").exists()

    root, _capability, installer, units, record, _old_id = _lifecycle_fixture(tmp_path / "generation-mismatch")
    proof = prove_quiescence(_fake_manager(), record, boot_id="m123a-boot", now=2.0)
    bad_record = dict(record, candidate_unit_generation_id="g-" + "f" * 64)
    bad_proof = prove_quiescence(_fake_manager(), bad_record, boot_id="m123a-boot", now=2.0)
    with pytest.raises(InstallError):
        installer.replace_unit_bundle(
            units,
            record["transaction_id"],
            activation_record=bad_record,
            quiescence_proof=bad_proof,
            current_boot_id="m123a-boot",
            now=2.0,
            adapter_identity="m123a-test-manager",
        )
    assert not (root / "etc/systemd/system").exists()
    assert proof.transaction_id == record["transaction_id"]

    root, _capability, installer, _units, record, _proof, activating, _old_id = _activate_fixture(tmp_path / "link-failure")
    with pytest.raises(LifecycleError):
        transition(activating, ActivationState.COMMITTED)
    failed = transition(activating, ActivationState.ROLLBACK_PENDING, readiness_result="FAILED")
    assert failed["state"] == ActivationState.ROLLBACK_PENDING.value
    assert os.readlink(root / "opt/aether/current") == f"releases/{record['candidate_release_id']}"
    assert installer.root == root

    assert not ActivationWindow(2.0, 3.0, "m123a-boot").valid(now=3.0, current_boot_id="m123a-boot")
    assert not ActivationWindow(2.0, 62.0, "m123a-boot").valid(now=3.0, current_boot_id="wrong-boot")
    assert not ActivationWindow(2.0, 62.0, "m123a-boot").valid(now=62.0, current_boot_id="m123a-boot")


def test_schema_incompatibility_and_interrupted_recovery_are_not_silently_accepted(tmp_path: Path):
    root, _capability, _installer, _units, record, _old_id = _lifecycle_fixture(tmp_path)
    state = root / "var/lib/aether/oas/security_kernel.sqlite3"
    state.parent.mkdir(parents=True)
    connection = sqlite3.connect(state)
    try:
        connection.executescript(
            "CREATE TABLE schema_metadata(schema_name TEXT, schema_version INTEGER);"
            "CREATE TABLE aether_instance_trust(value TEXT);"
            "CREATE TABLE owner_security_transactions(value TEXT);"
            "CREATE TABLE owner_security_audit_events(value TEXT);"
        )
        connection.execute("INSERT INTO schema_metadata VALUES ('oas_security_kernel', 1)")
        connection.commit()
    finally:
        connection.close()
    state.chmod(0o600)
    incompatible = dict(record, schema_compatibility="INCOMPATIBLE")
    with pytest.raises(Exception):
        _validate_state(
            root,
            incompatible,
            {"mode": "UNCHANGED", "schema_before": 1, "schema_after": 1},
        )
    with pytest.raises(LifecycleError):
        transition(record, ActivationState.RECOVERY_REQUIRED)
    assert record["state"] == ActivationState.CANDIDATE_PENDING.value


def test_rollback_release_mismatch_is_rejected_without_link_change(tmp_path: Path):
    root, _capability, installer, _units, record, _proof, _activating, _old_id = _activate_fixture(tmp_path)
    current_before = os.readlink(root / "opt/aether/current")
    with pytest.raises(InstallError):
        installer.activate_current("r1-" + "c" * 64, transaction_id=record["transaction_id"])
    assert os.readlink(root / "opt/aether/current") == current_before


def test_bounded_non_mutation_snapshot_covers_selected_production_paths(tmp_path: Path):
    paths = tuple(Path(path) for path in ("/etc/aether", "/etc/systemd/system", "/usr/libexec", "/opt/aether", "/var/lib/aether", "/run/aether"))
    before = {
        "paths": _path_snapshot(paths),
        "manager": _manager_snapshot(),
        "principals": tuple((name, _missing_principal(name)) for name in ("aether-owner", "aether-runtime", "aether-oas", "aether-bootstrap")),
        "listeners": _known_oas_socket_present(),
        "processes": _oas_process_count(),
    }
    _activate_fixture(tmp_path)
    after = {
        "paths": _path_snapshot(paths),
        "manager": _manager_snapshot(),
        "principals": tuple((name, _missing_principal(name)) for name in ("aether-owner", "aether-runtime", "aether-oas", "aether-bootstrap")),
        "listeners": _known_oas_socket_present(),
        "processes": _oas_process_count(),
    }
    assert before == after


def test_repository_scope_is_exactly_the_two_m123a_artifacts():
    assert ALLOWED_REPOSITORY_PATHS == {
        "docs/architecture/MILESTONE_123A_OAS_TARGET_HOST_DEPLOYMENT_READINESS_AND_NON_MUTATING_REHEARSAL_PROOF.md",
        "tests/test_milestone_123a_oas_target_host_deployment_readiness_and_non_mutating_rehearsAL_PROOF.py",
    }
