"""Offline verification of the complete four-unit OAS generation."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import stat
from typing import Mapping

from .lifecycle import TemporaryRootCapability, _path_has_symlink, _require_capability


class UnitVerificationError(ValueError):
    """Raised when unit bytes or a generation gate are not exact."""


UNIT_NAMES = (
    "aether-oas.service",
    "aether-oas-runtime.socket",
    "aether-oas-bootstrap.socket",
    "aether-oas-broker.socket",
)
SOCKET_ORDER = ("runtime", "bootstrap", "broker")
GENERATION = re.compile(r"^g-[0-9a-f]{64}$")
_SERVICE_DIRECTIVES = {
    "Sockets", "User",
    "Group", "SupplementaryGroups", "ExecStart", "WorkingDirectory", "Environment", "UMask",
    "Type", "NotifyAccess", "NoNewPrivileges", "PrivateTmp", "PrivateDevices", "ProtectSystem",
    "ProtectHome", "ReadOnlyPaths", "ReadWritePaths", "RestrictAddressFamilies",
    "RestrictSUIDSGID", "CapabilityBoundingSet", "AmbientCapabilities", "LockPersonality",
    "ProtectKernelTunables", "ProtectKernelModules", "ProtectKernelLogs", "ProtectControlGroups",
    "ProtectClock", "RestrictNamespaces", "RestrictRealtime", "SystemCallArchitectures", "LimitCORE",
    "LimitNOFILE", "FileDescriptorStoreMax", "TasksMax", "MemoryMax", "CPUQuota", "Restart",
    "RestartSec", "TimeoutStartSec", "TimeoutStopSec", "StandardOutput", "StandardError",
}
_SOCKET_UNIT_DIRECTIVES = {"Description", "Before", "PartOf", "ConditionPathExists"}
_SOCKET_DIRECTIVES = {
    "ListenSequentialPacket", "SocketUser", "SocketGroup", "SocketMode", "Backlog", "Accept",
    "DirectoryMode", "RemoveOnStop", "Service", "FileDescriptorName",
}


def canonical_unit_bundle_digest(units: Mapping[str, bytes]) -> str:
    if tuple(units) != UNIT_NAMES:
        raise UnitVerificationError("unit bundle names are not exact and ordered")
    # The generation token is normalized before hashing. This avoids a
    # cryptographic self-reference while retaining a digest of every byte and
    # the exact generation-bearing condition in the generated files.
    material = b"".join(
        name.encode("utf-8") + b"\0" + re.sub(
            rb"g-[0-9a-f]{64}", b"g-<generation>", units[name]
        ) + b"\0"
        for name in UNIT_NAMES
    )
    return hashlib.sha256(material).hexdigest()


def generation_id(units: Mapping[str, bytes]) -> str:
    return "g-" + canonical_unit_bundle_digest(units)


def _parse(text: str) -> dict[str, dict[str, list[str]]]:
    sections: dict[str, dict[str, list[str]]] = {}
    current: str | None = None
    for line in text.splitlines():
        if not line.strip():
            continue
        if line.startswith("[") and line.endswith("]"):
            current = line[1:-1]
            if current in sections or current not in {"Unit", "Service", "Socket", "Install"}:
                raise UnitVerificationError("duplicate unit section")
            sections[current] = {}
        elif current is None or "=" not in line:
            raise UnitVerificationError("invalid unit syntax")
        else:
            key, value = line.split("=", 1)
            sections[current].setdefault(key, []).append(value)
    return sections


def _one(sections: dict[str, dict[str, list[str]]], section: str, key: str) -> str:
    values = sections.get(section, {}).get(key)
    if values is None or len(values) != 1:
        raise UnitVerificationError(f"unit directive {section}.{key} is not singular")
    return values[0]


def verify_unit_bytes(units: Mapping[str, bytes], expected_generation: str | None = None) -> str:
    if tuple(units) != UNIT_NAMES or any(not isinstance(value, bytes) for value in units.values()):
        raise UnitVerificationError("complete unit set is required")
    service = _parse(units[UNIT_NAMES[0]].decode("utf-8"))
    if set(service.get("Unit", {})) != {"Description", "Requires", "After", "ConditionPathExists", "AssertPathExists", "StartLimitIntervalSec", "StartLimitBurst", "StartLimitAction"}:
        raise UnitVerificationError("service Unit directives are not complete")
    if set(service.get("Service", {})) != _SERVICE_DIRECTIVES:
        raise UnitVerificationError("service directives are not complete")
    if set(service.get("Install", {})):
        raise UnitVerificationError("service must not be independently enabled")
    if _one(service, "Service", "Sockets") != "aether-oas-runtime.socket aether-oas-bootstrap.socket aether-oas-broker.socket":
        raise UnitVerificationError("service socket order is not exact")
    if _one(service, "Service", "ExecStart") != '/opt/aether/current/runtime/bin/python -I -B -S -c \'import sys; sys.path.insert(0,"/opt/aether/current/runtime/lib/python3.11/site-packages"); from aether.oas.host_entrypoint import main; raise SystemExit(main())\'':
        raise UnitVerificationError("service ExecStart is not exact")
    for key, expected in (("User", "aether-oas"), ("Group", "aether-oas"), ("Type", "notify"), ("NotifyAccess", "main"), ("LimitNOFILE", "512"), ("FileDescriptorStoreMax", "0"), ("RestrictAddressFamilies", "AF_UNIX"), ("RestrictNamespaces", "yes")):
        if _one(service, "Service", key) != expected:
            raise UnitVerificationError(f"service directive {key} is not exact")
    if _one(service, "Unit", "Requires") != "aether-oas-runtime.socket aether-oas-bootstrap.socket aether-oas-broker.socket":
        raise UnitVerificationError("service dependencies are incomplete")
    condition_values = service.get("Unit", {}).get("ConditionPathExists", [])
    if len(condition_values) != 2 or not any(value.endswith("activation-record.json") for value in condition_values):
        raise UnitVerificationError("service activation conditions are incomplete")
    generation = expected_generation or generation_id(units)
    if not GENERATION.fullmatch(generation):
        raise UnitVerificationError("generation ID is invalid")
    gate = f"/var/lib/aether/activation/unit-generations/{generation}.ready"
    if gate not in condition_values:
        raise UnitVerificationError("service generation condition is not exact")
    for role, unit_name in zip(SOCKET_ORDER, UNIT_NAMES[1:]):
        section = _parse(units[unit_name].decode("utf-8"))
        if set(section.get("Unit", {})) != _SOCKET_UNIT_DIRECTIVES or set(section.get("Socket", {})) != _SOCKET_DIRECTIVES:
            raise UnitVerificationError("socket directives are not complete")
        if _one(section, "Socket", "Service") != "aether-oas.service":
            raise UnitVerificationError("socket service binding is invalid")
        if _one(section, "Socket", "FileDescriptorName") != role:
            raise UnitVerificationError("socket descriptor name is invalid")
        if _one(section, "Socket", "ListenSequentialPacket") != f"/run/aether/oas/{role}.sock":
            raise UnitVerificationError("socket path is invalid")
        if _one(section, "Socket", "SocketUser") != "aether-oas":
            raise UnitVerificationError("socket owner is invalid")
        conditions = section.get("Unit", {}).get("ConditionPathExists", [])
        if set(conditions) != {
            "/var/lib/aether/activation/activation-record.json",
            gate,
        }:
            raise UnitVerificationError("socket generation condition is invalid")
    return generation


def read_units(unit_dir: str | Path) -> dict[str, bytes]:
    directory = Path(unit_dir)
    result: dict[str, bytes] = {}
    for name in UNIT_NAMES:
        path = directory / name
        if not path.is_file() or path.is_symlink():
            raise UnitVerificationError(f"unit is missing or not regular: {name}")
        result[name] = path.read_bytes()
    return result


def verify_unit_directory(unit_dir: str | Path, expected_generation: str | None = None) -> tuple[str, str]:
    units = read_units(unit_dir)
    generation = verify_unit_bytes(units, expected_generation)
    return generation, canonical_unit_bundle_digest(units)


def generation_gate_payload(generation: str, units: Mapping[str, bytes], transaction_id: str) -> bytes:
    if not GENERATION.fullmatch(generation) or not transaction_id or tuple(units) != UNIT_NAMES:
        raise UnitVerificationError("generation gate identity is invalid")
    if generation_id(units) != generation:
        raise UnitVerificationError("generation does not match unit bytes")
    payload = {
        "generation_id": generation,
        "unit_bundle_digest": canonical_unit_bundle_digest(units),
        "unit_hashes": {name: hashlib.sha256(units[name]).hexdigest() for name in UNIT_NAMES},
        "transaction_id": transaction_id,
        "status": "VERIFIED",
    }
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")


def install_generation_gate(
    root: str | Path,
    generation: str,
    units: Mapping[str, bytes],
    transaction_id: str,
    *,
    capability: TemporaryRootCapability,
) -> Path:
    try:
        base = _require_capability(root, capability, purpose="M122A_INSTALLER", transaction_id=transaction_id)
    except Exception as exc:
        raise UnitVerificationError("temporary-root capability is required") from exc
    verify_unit_bytes(units, generation)
    directory = base / "var/lib/aether/activation/unit-generations"
    if _path_has_symlink(directory):
        raise UnitVerificationError("generation gate directory contains a symlink")
    directory.mkdir(parents=True, exist_ok=True, mode=0o755)
    if _path_has_symlink(directory):
        raise UnitVerificationError("generation gate directory contains a symlink")
    target = directory / f"{generation}.ready"
    if target.exists() or target.is_symlink():
        raise UnitVerificationError("generation gate already exists")
    temporary_name = f".{generation}.{transaction_id}.tmp"
    data = generation_gate_payload(generation, units, transaction_id)
    directory_fd = os.open(directory, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
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
            os.fchmod(stream.fileno(), 0o444)
        os.rename(temporary_name, target.name, src_dir_fd=directory_fd, dst_dir_fd=directory_fd)
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
