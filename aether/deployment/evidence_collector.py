"""Bounded, redacted repository/isolated-root evidence collection."""

from __future__ import annotations

import hashlib
import os
from pathlib import Path
import stat
from typing import Any, Mapping

from .lifecycle import TemporaryRootCapability, _path_has_symlink, _require_capability
from .unit_verifier import UNIT_NAMES, read_units


class EvidenceError(ValueError):
    """Raised when evidence input is unsafe or exceeds its bounded shape."""


EVIDENCE_CLASSES = (
    "host", "systemd", "trust", "release", "files", "runtime", "principals",
    "state", "sockets", "process", "access", "readiness", "lifecycle", "logging", "review",
)
_FORBIDDEN = ("private", "secret", "password", "token", "credential", "signature", "key_material", "cookie", "authorization")


def _safe_value(value: Any, depth: int = 0) -> Any:
    if depth > 8:
        raise EvidenceError("evidence nesting is too deep")
    if isinstance(value, Mapping):
        if len(value) > 128:
            raise EvidenceError("evidence object is too large")
        result: dict[str, Any] = {}
        for key, child in value.items():
            if not isinstance(key, str) or any(word in key.casefold() for word in _FORBIDDEN):
                raise EvidenceError("secret-bearing evidence field is forbidden")
            result[key] = _safe_value(child, depth + 1)
        return result
    if isinstance(value, (list, tuple)):
        if len(value) > 256:
            raise EvidenceError("evidence collection is too large")
        return [_safe_value(child, depth + 1) for child in value]
    if isinstance(value, (str, int, bool)) or value is None:
        if isinstance(value, str):
            if len(value.encode("utf-8")) > 4096:
                raise EvidenceError("evidence string is too large")
            folded = value.casefold()
            if "-----begin" in folded or any(word in folded for word in ("password=", "token=", "secret=", "private key")):
                raise EvidenceError("secret-bearing evidence value is forbidden")
        return value
    raise EvidenceError("unsupported evidence value")


def _file_facts(path: Path, root: Path) -> dict[str, Any]:
    relative = path.relative_to(root).as_posix()
    if _path_has_symlink(path):
        raise EvidenceError("evidence path contains a symlink")
    info = path.lstat()
    if stat.S_ISLNK(info.st_mode) or not stat.S_ISREG(info.st_mode):
        raise EvidenceError("evidence path is not a regular file")
    data = path.read_bytes()
    return {"path": relative, "sha256": hashlib.sha256(data).hexdigest(), "size": len(data), "mode": stat.S_IMODE(info.st_mode), "type": "regular"}


def collect_evidence(
    root: str | Path,
    *,
    facts: Mapping[str, Any] | None = None,
    capability: TemporaryRootCapability | None = None,
) -> dict[str, Any]:
    """Collect bounded local artifact facts without asserting host deployment."""

    if capability is None:
        raise EvidenceError("an explicit isolated-root capability is required")
    try:
        base = _require_capability(root, capability, purpose="M122A_EVIDENCE")
    except Exception as exc:
        raise EvidenceError("temporary-root capability is required") from exc
    unit_dir = base / "etc/systemd/system"
    if _path_has_symlink(unit_dir):
        raise EvidenceError("evidence unit directory contains a symlink")
    files = []
    if unit_dir.is_dir():
        for name in UNIT_NAMES:
            path = unit_dir / name
            if path.exists():
                files.append(_file_facts(path, base))
    evidence = {
        "evidence_version": 1,
        "scope": "repository-or-isolated-root",
        "status": "NOT_VERIFIED",
        "deployment_verified": False,
        "classes": list(EVIDENCE_CLASSES),
        "files": files,
        "facts": dict(facts or {}),
        "limitations": ["No live host, systemd, principal, readiness, or deployment evidence is collected."],
    }
    return _safe_value(evidence)
