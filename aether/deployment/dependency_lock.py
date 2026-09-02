"""Offline dependency-closure verification for the repository artifact."""

from __future__ import annotations

import hashlib
import json
import base64
import csv
from pathlib import Path
import re
from typing import Any
from zipfile import BadZipFile, ZipFile

from .manifest_schema import canonical_json_bytes


class DependencyLockError(ValueError):
    """Raised when the pinned offline dependency closure is unusable."""


def verify_dependency_closure(lock_path: str | Path, wheelhouse: str | Path) -> dict[str, Any]:
    lock = Path(lock_path)
    directory = Path(wheelhouse)
    try:
        raw = lock.read_bytes()
        value = json.loads(raw.decode("utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise DependencyLockError("dependency lock is unreadable") from exc
    expected = {"artifacts", "blockers", "closure_status", "direct_requirements", "format_version", "install_policy", "interpreter", "platform", "requirements_source"}
    if set(value) != expected or value["format_version"] != 1 or value["closure_status"] != "COMPLETE":
        raise DependencyLockError("dependency lock is not complete and exact")
    if canonical_json_bytes(value) not in {raw, raw.rstrip(b"\n")}:
        raise DependencyLockError("dependency lock is not canonical")
    if value["blockers"] != [] or value["install_policy"] != "offline-only; refuse installation when closure_status is INCOMPLETE":
        raise DependencyLockError("dependency lock policy is invalid")
    artifacts = value["artifacts"]
    if not isinstance(artifacts, list) or not artifacts:
        raise DependencyLockError("dependency artifact list is empty")
    seen: set[str] = set()
    direct = {}
    for requirement in value["direct_requirements"]:
        match = re.fullmatch(r"([A-Za-z0-9_.-]+)==([A-Za-z0-9_.-]+)", requirement)
        if not match:
            raise DependencyLockError("direct requirement is not exact")
        normalized = _normalize_name(match.group(1))
        if normalized in direct:
            raise DependencyLockError("duplicate direct requirement")
        direct[normalized] = match.group(2)
    records: dict[str, dict[str, Any]] = {}
    for artifact in artifacts:
        fields = {"name", "normalized_name", "version", "filename", "sha256", "size", "provenance_url", "index_host", "classification", "parents", "requires_dist", "python_tag", "abi_tag", "platform_tag", "marker", "metadata_sha256", "wheel_metadata_sha256", "record_sha256"}
        if not isinstance(artifact, dict) or set(artifact) != fields:
            raise DependencyLockError("dependency artifact record is not exact")
        filename = artifact["filename"]
        if not isinstance(filename, str) or not re.fullmatch(r"[A-Za-z0-9_.+-]+\.whl", filename) or filename in seen:
            raise DependencyLockError("dependency filename is invalid or duplicated")
        seen.add(filename)
        normalized_name = _normalize_name(artifact["name"])
        if artifact["normalized_name"] != normalized_name or normalized_name in records:
            raise DependencyLockError("dependency normalized project is duplicated or incorrect")
        records[normalized_name] = artifact
        if artifact["marker"] not in {"python_version == '3.11'", "python_version == '3.11' and platform_machine == 'x86_64'"}:
            raise DependencyLockError("dependency marker is outside the fixed target")
        if artifact["classification"] not in {"direct", "transitive"} or not isinstance(artifact["parents"], list) or not all(isinstance(parent, str) for parent in artifact["parents"]):
            raise DependencyLockError("dependency graph classification is invalid")
        if not isinstance(artifact["sha256"], str) or not re.fullmatch(r"[0-9a-f]{64}", artifact["sha256"]):
            raise DependencyLockError("dependency digest is invalid")
        if not isinstance(artifact["size"], int) or artifact["size"] < 1:
            raise DependencyLockError("dependency size is invalid")
        path = directory / filename
        if path.is_symlink() or not path.is_file():
            raise DependencyLockError(f"dependency wheel is missing: {filename}")
        data = path.read_bytes()
        if len(data) != artifact["size"] or hashlib.sha256(data).hexdigest() != artifact["sha256"]:
            raise DependencyLockError(f"dependency wheel digest mismatch: {filename}")
        _verify_wheel_metadata(data, artifact)
    if set(direct) - set(records) or any(records[name]["version"] != version for name, version in direct.items()):
        raise DependencyLockError("direct requirements are not resolved exactly")
    for name, artifact in records.items():
        if artifact["classification"] == "direct" and name not in direct:
            raise DependencyLockError("unlisted direct dependency classification")
        for parent in artifact["parents"]:
            if parent not in records:
                raise DependencyLockError("dependency parent is not in the closure")
    actual = {path.name for path in directory.iterdir() if path.is_file() and path.name.endswith(".whl")}
    if actual != seen:
        raise DependencyLockError("wheelhouse contains an unlisted or missing wheel")
    return {"closure_status": "COMPLETE", "artifact_count": len(artifacts), "filenames": sorted(seen)}


def verify_installed_closure(lock_path: str | Path, import_root: str | Path) -> dict[str, Any]:
    """Verify the installed site-packages tree against the pinned projects."""

    lock = Path(lock_path)
    root = Path(import_root)
    try:
        value = json.loads(lock.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise DependencyLockError("dependency lock is unreadable") from exc
    if value.get("closure_status") != "COMPLETE" or not root.is_dir() or root.is_symlink():
        raise DependencyLockError("installed dependency closure is incomplete")
    expected = {
        _normalize_name(artifact["name"]): artifact["version"]
        for artifact in value.get("artifacts", [])
        if isinstance(artifact, dict) and "name" in artifact and "version" in artifact
    }
    dist_infos = sorted(path for path in root.iterdir() if path.is_dir() and path.name.endswith(".dist-info"))
    if len(dist_infos) != len(expected):
        raise DependencyLockError("installed dependency project set is not exact")
    seen: set[str] = set()
    recorded: set[str] = set()
    for dist_info in dist_infos:
        metadata_path = dist_info / "METADATA"
        record_path = dist_info / "RECORD"
        try:
            metadata = metadata_path.read_text(encoding="utf-8")
            with record_path.open("r", encoding="utf-8", newline="") as stream:
                rows = list(csv.reader(stream))
        except (OSError, UnicodeDecodeError, csv.Error) as exc:
            raise DependencyLockError("installed dependency metadata is unreadable") from exc
        name = next((line.split(": ", 1)[1] for line in metadata.splitlines() if line.startswith("Name: ")), "")
        version = next((line.split(": ", 1)[1] for line in metadata.splitlines() if line.startswith("Version: ")), "")
        normalized = _normalize_name(name)
        if normalized in seen or expected.get(normalized) != version:
            raise DependencyLockError("installed dependency identity is not exact")
        seen.add(normalized)
        for row in rows:
            if len(row) != 3 or not row[0] or row[0].startswith("/") or ".." in Path(row[0]).parts:
                raise DependencyLockError("installed RECORD entry is unsafe")
            relative = Path(row[0])
            path = root / relative
            if not path.is_file() or path.is_symlink():
                raise DependencyLockError("installed RECORD file is missing")
            recorded.add(relative.as_posix())
            data = path.read_bytes()
            if row[1]:
                try:
                    algorithm, encoded = row[1].split("=", 1)
                    if algorithm != "sha256":
                        raise ValueError
                    expected_digest = base64.urlsafe_b64decode(encoded + "==")
                except (ValueError, base64.binascii.Error) as exc:
                    raise DependencyLockError("installed RECORD digest is invalid") from exc
                if hashlib.sha256(data).digest() != expected_digest or len(data) != int(row[2]):
                    raise DependencyLockError("installed RECORD digest mismatch")
            elif row[2] and len(data) != int(row[2]):
                raise DependencyLockError("installed RECORD size mismatch")
    actual = {
        path.relative_to(root).as_posix()
        for path in root.rglob("*")
        if path.is_file() and not path.is_symlink()
    }
    if actual != recorded:
        raise DependencyLockError("installed site-packages contains an extra or omitted file")
    return {"closure_status": "COMPLETE", "project_count": len(seen), "projects": sorted(seen)}


def _normalize_name(name: str) -> str:
    if not isinstance(name, str) or not re.fullmatch(r"[A-Za-z0-9_.-]+", name):
        raise DependencyLockError("dependency name is invalid")
    return re.sub(r"[-_.]+", "-", name).casefold()


def _verify_wheel_metadata(data: bytes, artifact: dict[str, Any]) -> None:
    try:
        with ZipFile(__import__("io").BytesIO(data)) as wheel:
            names = wheel.namelist()
            if any(name.startswith("/") or ".." in Path(name).parts for name in names):
                raise DependencyLockError("wheel contains traversal")
            metadata_name = next(name for name in names if name.endswith(".dist-info/METADATA"))
            wheel_name = next(name for name in names if name.endswith(".dist-info/WHEEL"))
            record_name = next(name for name in names if name.endswith(".dist-info/RECORD"))
            metadata = wheel.read(metadata_name)
            wheel_metadata = wheel.read(wheel_name)
            record = wheel.read(record_name)
    except (BadZipFile, OSError, StopIteration) as exc:
        raise DependencyLockError("wheel metadata is unreadable") from exc
    if hashlib.sha256(metadata).hexdigest() != artifact["metadata_sha256"] or hashlib.sha256(wheel_metadata).hexdigest() != artifact["wheel_metadata_sha256"] or hashlib.sha256(record).hexdigest() != artifact["record_sha256"]:
        raise DependencyLockError(f"wheel metadata digest mismatch: {artifact['filename']}")
    headers = metadata.decode("utf-8", errors="strict").splitlines()
    declared_name = next((line.split(": ", 1)[1] for line in headers if line.startswith("Name: ")), "")
    declared_version = next((line.split(": ", 1)[1] for line in headers if line.startswith("Version: ")), "")
    declared_requires = [line.split(": ", 1)[1] for line in headers if line.startswith("Requires-Dist: ") and "extra ==" not in line and "python_version < \"3.11\"" not in line and "python_version < '3.11'" not in line and "platform_system == 'Windows'" not in line]
    if _normalize_name(declared_name) != artifact["normalized_name"] or declared_version != artifact["version"] or declared_requires != artifact["requires_dist"]:
        raise DependencyLockError(f"wheel METADATA does not match lock: {artifact['filename']}")
    wheel_text = wheel_metadata.decode("utf-8", errors="strict")
    if "Root-Is-Purelib: true" not in wheel_text and artifact["platform_tag"] == "any":
        raise DependencyLockError("pure wheel metadata is inconsistent")
    if not record:
        raise DependencyLockError("wheel RECORD is empty")
