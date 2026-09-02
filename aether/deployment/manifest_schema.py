"""Strict canonical release-manifest and signing-envelope primitives."""

from __future__ import annotations

import base64
from datetime import datetime, timezone
import hashlib
import json
import math
import re
import unicodedata
from typing import Any, Mapping


class ManifestError(ValueError):
    """Raised when a release artifact is malformed or inconsistently bound."""


MANIFEST_FIELDS = (
    "manifest_version",
    "release_id_format",
    "source",
    "runtime",
    "dependencies",
    "build",
    "files",
    "units",
    "schema_compatibility",
    "policy",
)
ENVELOPE_FIELDS = (
    "envelope_version",
    "domain",
    "manifest_version",
    "manifest_sha256",
    "manifest_length",
    "release_id",
    "approval_payload",
    "release_signature",
    "approval_signature",
    "rotation_signatures",
)
APPROVAL_FIELDS = (
    "manifest_digest",
    "release_id",
    "source_commit",
    "test_evidence_digest",
    "approval_id",
    "activation_release_policy",
    "issued_at_utc",
    "expires_at_utc",
    "approver_policy",
)
SIGNATURE_FIELDS = ("role", "key_id", "algorithm", "encoding", "signature")
ANCHOR_PAYLOAD_FIELDS = ("anchor_version", "anchor_id", "keys", "rotation_policy", "revocations")
ANCHOR_FIELDS = (*ANCHOR_PAYLOAD_FIELDS, "anchor_fingerprint")
ROTATION_POLICY_FIELDS = ("mode", "overlap_not_before_utc", "overlap_expires_at_utc")
REVOCATION_FIELDS = ("key_id", "revoked_at_utc")
MANIFEST_DOMAIN = "aether.m121a.release-manifest.v1"
APPROVAL_DOMAIN = "aether.m121a.release-approval.v1"
ANCHOR_DOMAIN = "aether.m121a.release-trust-anchor.v1"
RELEASE_ID = re.compile(r"^r1-[0-9a-f]{64}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")
BASE64URL64 = re.compile(r"^[A-Za-z0-9_-]{86}$")
PATH_COMPONENT = re.compile(r"^[^/\x00]+$")
UNIT_NAMES = (
    "aether-oas.service", "aether-oas-runtime.socket", "aether-oas-bootstrap.socket",
    "aether-oas-broker.socket",
)
MANIFEST_MAX_BYTES = 4 * 1024 * 1024
MAX_RELEASE_FILES = 10000
MAX_RELEASE_PATH_BYTES = 1024


def _validate(value: Any, depth: int = 0) -> None:
    if depth > 32:
        raise ManifestError("JSON nesting is too deep")
    if isinstance(value, Mapping):
        if len(value) > 1024:
            raise ManifestError("JSON object is too large")
        for key, child in value.items():
            if not isinstance(key, str) or len(key.encode("utf-8")) > 256:
                raise ManifestError("JSON object key is invalid")
            _validate(child, depth + 1)
    elif isinstance(value, (list, tuple)):
        if len(value) > 4096:
            raise ManifestError("JSON array is too large")
        for child in value:
            _validate(child, depth + 1)
    elif isinstance(value, float):
        if not math.isfinite(value):
            raise ManifestError("non-finite JSON value")
    elif not isinstance(value, (str, int, bool)) and value is not None:
        raise ManifestError("unsupported JSON value")


def canonical_json_bytes(value: Any) -> bytes:
    """Return the one canonical UTF-8 JSON representation used by artifacts."""

    _validate(value)
    try:
        data = json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            allow_nan=False,
        ).encode("utf-8")
        if len(data) > MANIFEST_MAX_BYTES:
            raise ManifestError("canonical artifact exceeds byte limit")
        return data
    except (TypeError, ValueError, OverflowError) as exc:
        raise ManifestError("value cannot be canonicalized") from exc


def parse_canonical_json(raw: bytes | bytearray | memoryview) -> Any:
    """Parse JSON while rejecting duplicates and non-canonical encodings."""

    if not isinstance(raw, (bytes, bytearray, memoryview)):
        raise ManifestError("JSON input must be bytes")
    data = bytes(raw)

    def pairs(items: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in items:
            if key in result:
                raise ManifestError("duplicate JSON field")
            result[key] = value
        return result

    try:
        value = json.loads(data.decode("utf-8"), object_pairs_hook=pairs, parse_constant=_constant)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ManifestError("invalid JSON") from exc
    if canonical_json_bytes(value) != data:
        raise ManifestError("JSON is not canonical")
    return value


def _constant(value: str) -> None:
    raise ManifestError(f"non-finite JSON value: {value}")


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def release_id_for_digest(digest: str) -> str:
    if not isinstance(digest, str) or not HEX64.fullmatch(digest):
        raise ManifestError("manifest digest must be lowercase SHA-256")
    return "r1-" + digest


def _exact_fields(value: Mapping[str, Any], expected: tuple[str, ...], name: str) -> None:
    if not isinstance(value, Mapping) or tuple(sorted(value)) != tuple(sorted(expected)):
        raise ManifestError(f"{name} fields are not exact")


def _string(value: Any, pattern: re.Pattern[str], name: str) -> str:
    if not isinstance(value, str) or not pattern.fullmatch(value):
        raise ManifestError(f"{name} is invalid")
    return value


def _digest(value: Any, name: str) -> str:
    return _string(value, HEX64, name)


def _safe_path(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value or len(value.encode("utf-8")) > MAX_RELEASE_PATH_BYTES or value.startswith("/") or "\\" in value:
        raise ManifestError(f"{name} is invalid")
    parts = value.split("/")
    if any(part in {"", ".", ".."} or not PATH_COMPONENT.fullmatch(part) for part in parts):
        raise ManifestError(f"{name} is invalid")
    return value


def _bounded_int(value: Any, name: str, maximum: int = 1 << 40) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 0 or value > maximum:
        raise ManifestError(f"{name} is invalid")
    return value


def validate_rotation_policy(value: Mapping[str, Any]) -> dict[str, Any]:
    """Validate the closed anchor rotation policy shape."""

    _exact_fields(value, ROTATION_POLICY_FIELDS, "rotation policy")
    if value["mode"] not in {"NORMAL", "OVERLAP"}:
        raise ManifestError("rotation policy mode is invalid")
    for field in ("overlap_not_before_utc", "overlap_expires_at_utc"):
        timestamp = value[field]
        if timestamp is not None:
            _parse_utc(timestamp)
    start = value["overlap_not_before_utc"]
    end = value["overlap_expires_at_utc"]
    if value["mode"] == "NORMAL":
        if start is not None or end is not None:
            raise ManifestError("normal rotation policy cannot have an overlap window")
    elif not isinstance(start, str) or not isinstance(end, str) or _parse_utc(end) <= _parse_utc(start):
        raise ManifestError("overlap rotation policy window is invalid")
    return dict(value)


def validate_revocations(value: Any, *, known_key_ids: set[str] | None = None) -> list[dict[str, Any]]:
    """Validate typed, closed revocation records."""

    if not isinstance(value, list) or len(value) > 1024:
        raise ManifestError("revocations must be a bounded array")
    result: list[dict[str, Any]] = []
    seen: set[str] = set()
    for item in value:
        _exact_fields(item, REVOCATION_FIELDS, "revocation")
        key_id = item["key_id"]
        if not isinstance(key_id, str) or not re.fullmatch(r"[A-Za-z0-9_.:-]{1,128}", key_id) or key_id in seen:
            raise ManifestError("revocation key ID is invalid or duplicated")
        if known_key_ids is not None and key_id not in known_key_ids:
            raise ManifestError("revocation references an unknown key")
        _parse_utc(item["revoked_at_utc"])
        seen.add(key_id)
        result.append(dict(item))
    return result


def _validate_file_entries(entries: Any, name: str) -> None:
    if not isinstance(entries, list) or not entries or len(entries) > MAX_RELEASE_FILES:
        raise ManifestError(f"manifest {name} must be a bounded non-empty array")
    paths: list[str] = []
    for entry in entries:
        if not isinstance(entry, Mapping):
            raise ManifestError(f"{name} entry is not an object")
        _exact_fields(entry, ("path", "sha256", "size", "mode", "type"), f"{name} entry")
        paths.append(_safe_path(entry["path"], f"{name} path"))
        _digest(entry["sha256"], f"{name} digest")
        _bounded_int(entry["size"], f"{name} size")
        _string(entry["mode"], re.compile(r"^[0-7]{4}$"), f"{name} mode")
        if entry["type"] != "regular":
            raise ManifestError(f"{name} entry type is invalid")
    normalized = [unicodedata.normalize("NFKC", path).casefold() for path in paths]
    if paths != sorted(paths) or len(normalized) != len(set(normalized)):
        raise ManifestError(f"{name} paths are not unique and ordered")


def _validate_nested_manifest(manifest: Mapping[str, Any]) -> None:
    _exact_fields(manifest["source"], ("commit", "tree", "root_digest"), "source")
    _string(manifest["source"]["commit"], re.compile(r"^[0-9a-f]{40,64}$"), "source commit")
    _string(manifest["source"]["tree"], re.compile(r"^[0-9a-f]{40,64}$"), "source tree")
    _digest(manifest["source"]["root_digest"], "source root digest")
    _exact_fields(manifest["runtime"], ("python", "python_version", "import_root"), "runtime")
    _string(manifest["runtime"]["python"], re.compile(r"^/[A-Za-z0-9_./-]+$"), "runtime python")
    _string(manifest["runtime"]["python_version"], re.compile(r"^3\.11(?:\.[0-9]+)?$"), "runtime version")
    _string(manifest["runtime"]["import_root"], re.compile(r"^/[A-Za-z0-9_./-]+$"), "runtime import root")
    dependencies = manifest["dependencies"]
    _exact_fields(dependencies, ("closure_status", "artifacts", "direct_requirements", "interpreter", "platform", "format_version", "install_policy", "requirements_source", "lock_digest"), "dependencies")
    if dependencies["closure_status"] not in {"COMPLETE", "INCOMPLETE"} or not isinstance(dependencies["artifacts"], list) or not isinstance(dependencies["direct_requirements"], list):
        raise ManifestError("dependency closure is malformed")
    if dependencies["closure_status"] == "COMPLETE" and not dependencies["artifacts"]:
        raise ManifestError("complete dependency closure has no artifacts")
    if dependencies["interpreter"] != "cp311" or dependencies["platform"] != "linux_x86_64" or dependencies["format_version"] != 1 or dependencies["install_policy"] != "offline-only; refuse installation when closure_status is INCOMPLETE":
        raise ManifestError("dependency policy is not exact")
    if not isinstance(dependencies["requirements_source"], str) or not dependencies["requirements_source"]:
        raise ManifestError("dependency source is invalid")
    _digest(dependencies["lock_digest"], "dependency lock digest")
    for artifact in dependencies["artifacts"]:
        _exact_fields(artifact, ("name", "normalized_name", "version", "filename", "sha256", "size", "provenance_url", "index_host", "classification", "parents", "requires_dist", "python_tag", "abi_tag", "platform_tag", "marker", "metadata_sha256", "wheel_metadata_sha256", "record_sha256"), "dependency artifact")
        for field in ("name", "normalized_name", "version", "filename", "marker", "provenance_url", "index_host", "classification", "python_tag", "abi_tag", "platform_tag"):
            if not isinstance(artifact[field], str) or not artifact[field] or len(artifact[field]) > 512:
                raise ManifestError("dependency artifact identity is invalid")
        if artifact["normalized_name"] != re.sub(r"[-_.]+", "-", artifact["name"]).casefold() or artifact["classification"] not in {"direct", "transitive"} or not isinstance(artifact["parents"], list) or not isinstance(artifact["requires_dist"], list):
            raise ManifestError("dependency artifact graph metadata is invalid")
        _digest(artifact["sha256"], "dependency artifact digest")
        for field in ("metadata_sha256", "wheel_metadata_sha256", "record_sha256"):
            _digest(artifact[field], f"dependency {field}")
        _bounded_int(artifact["size"], "dependency artifact size")
    _exact_fields(manifest["build"], ("builder", "reproducible", "unit_bundle_digest", "unit_generation_id", "dependency_lock_digest"), "build")
    if not isinstance(manifest["build"]["builder"], str) or manifest["build"]["reproducible"] is not True:
        raise ManifestError("build identity is invalid")
    _digest(manifest["build"]["unit_bundle_digest"], "unit bundle digest")
    _string(manifest["build"]["unit_generation_id"], re.compile(r"^g-[0-9a-f]{64}$"), "unit generation ID")
    _digest(manifest["build"]["dependency_lock_digest"], "build dependency lock digest")
    if manifest["build"]["dependency_lock_digest"] != manifest["dependencies"]["lock_digest"]:
        raise ManifestError("build and dependency lock digests do not match")
    _validate_file_entries(manifest["files"], "files")
    units = manifest["units"]
    if not isinstance(units, list) or any(not isinstance(item, Mapping) for item in units) or [item.get("name") for item in units] != list(UNIT_NAMES):
        raise ManifestError("unit inventory is incomplete or unordered")
    for item in units:
        _exact_fields(item, ("name", "sha256", "size"), "unit entry")
        _digest(item["sha256"], "unit digest")
        _bounded_int(item["size"], "unit size", 1024 * 1024)
    _exact_fields(manifest["schema_compatibility"], ("schema_before", "schema_after", "mode"), "schema compatibility")
    for field in ("schema_before", "schema_after"):
        _bounded_int(manifest["schema_compatibility"][field], field, 1000)
    if manifest["schema_compatibility"]["mode"] not in {"UNCHANGED", "CODE_UPGRADE", "SCHEMA_UPGRADE"}:
        raise ManifestError("schema compatibility mode is invalid")
    _exact_fields(manifest["policy"], ("release_id", "max_retained_releases"), "policy")
    if manifest["policy"]["release_id"] != "manifest-derived":
        raise ManifestError("release identity policy is invalid")
    _bounded_int(manifest["policy"]["max_retained_releases"], "release retention", 100)


def validate_manifest(manifest: Mapping[str, Any]) -> dict[str, Any]:
    _exact_fields(manifest, MANIFEST_FIELDS, "manifest")
    if manifest["manifest_version"] != 1:
        raise ManifestError("unsupported manifest version")
    if manifest["release_id_format"] != "r1-<64 lowercase hexadecimal manifest digest>":
        raise ManifestError("release ID format is not exact")
    for field in ("source", "runtime", "dependencies", "build", "schema_compatibility", "policy"):
        if not isinstance(manifest[field], Mapping):
            raise ManifestError(f"manifest {field} must be an object")
    _validate_nested_manifest(manifest)
    payload = dict(manifest)
    digest = sha256_hex(canonical_json_bytes(payload))
    return payload | {"manifest_sha256": digest, "release_id": release_id_for_digest(digest)}


def canonical_manifest_bytes(manifest: Mapping[str, Any]) -> bytes:
    validate_manifest(manifest)
    return canonical_json_bytes(dict(manifest))


def signature_bytes(signature: str) -> bytes:
    if not isinstance(signature, str) or not BASE64URL64.fullmatch(signature):
        raise ManifestError("signature encoding is invalid")
    if "=" in signature:
        raise ManifestError("signature padding is forbidden")
    try:
        decoded = base64.urlsafe_b64decode(signature + "==")
    except (ValueError, base64.binascii.Error) as exc:
        raise ManifestError("signature is not base64url") from exc
    if len(decoded) != 64:
        raise ManifestError("signature must decode to 64 bytes")
    return decoded


def validate_signature(value: Mapping[str, Any], expected_role: str) -> dict[str, Any]:
    _exact_fields(value, SIGNATURE_FIELDS, "signature")
    if value["role"] != expected_role or value["algorithm"] != "Ed25519":
        raise ManifestError("signature role or algorithm is invalid")
    if value["encoding"] != "base64url-no-padding-64-raw-bytes":
        raise ManifestError("signature encoding contract is invalid")
    if not isinstance(value["key_id"], str) or not re.fullmatch(r"[A-Za-z0-9_.:-]{1,128}", value["key_id"]):
        raise ManifestError("signature key ID is invalid")
    signature_bytes(value["signature"])
    return dict(value)


def validate_envelope(envelope: Mapping[str, Any], manifest: Mapping[str, Any], manifest_bytes: bytes) -> dict[str, Any]:
    _exact_fields(envelope, ENVELOPE_FIELDS, "envelope")
    if envelope["envelope_version"] != 1 or envelope["domain"] != MANIFEST_DOMAIN:
        raise ManifestError("envelope version or domain is invalid")
    manifest_digest = sha256_hex(manifest_bytes)
    if envelope["manifest_version"] != manifest.get("manifest_version"):
        raise ManifestError("envelope manifest version mismatch")
    if envelope["manifest_sha256"] != manifest_digest or envelope["manifest_length"] != len(manifest_bytes):
        raise ManifestError("envelope manifest binding mismatch")
    if envelope["release_id"] != release_id_for_digest(manifest_digest):
        raise ManifestError("envelope release ID mismatch")
    approval = envelope["approval_payload"]
    _exact_fields(approval, APPROVAL_FIELDS, "approval payload")
    if approval["manifest_digest"] != manifest_digest or approval["release_id"] != envelope["release_id"]:
        raise ManifestError("approval payload binding mismatch")
    if not isinstance(approval["source_commit"], str) or not re.fullmatch(r"[0-9a-f]{40,64}", approval["source_commit"]):
        raise ManifestError("approval source commit is invalid")
    if not isinstance(approval["test_evidence_digest"], str) or not HEX64.fullmatch(approval["test_evidence_digest"]):
        raise ManifestError("approval evidence digest is invalid")
    if not isinstance(approval["approval_id"], str) or not approval["approval_id"]:
        raise ManifestError("approval ID is invalid")
    for field in ("activation_release_policy", "approver_policy"):
        if not isinstance(approval[field], Mapping):
            raise ManifestError(f"approval {field} must be an object")
    for field in ("issued_at_utc", "expires_at_utc"):
        _parse_utc(approval[field])
    if not isinstance(envelope["rotation_signatures"], list) or len(envelope["rotation_signatures"]) > 2:
        raise ManifestError("rotation signatures must be an array")
    validate_signature(envelope["release_signature"], "release")
    validate_signature(envelope["approval_signature"], "approval")
    signature_ids = {
        envelope["release_signature"]["key_id"],
        envelope["approval_signature"]["key_id"],
    }
    if len(signature_ids) != 2:
        raise ManifestError("primary signing keys must be distinct")
    for item in envelope["rotation_signatures"]:
        if not isinstance(item, Mapping):
            raise ManifestError("rotation signature is not an object")
        if item.get("role") not in {"release", "approval"}:
            raise ManifestError("rotation signature role is invalid")
        validate_signature(item, item["role"])
        signature_ids.add(item["key_id"])
    if envelope["rotation_signatures"] and {
        item["role"] for item in envelope["rotation_signatures"]
    } != {"release", "approval"}:
        raise ManifestError("rotation signatures must contain one signature per role")
    if len(signature_ids) != 2 + len(envelope["rotation_signatures"]):
        raise ManifestError("signing keys must be distinct")
    return dict(envelope)


def _parse_utc(value: Any) -> datetime:
    if not isinstance(value, str):
        raise ManifestError("UTC value is invalid")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ManifestError("UTC value is invalid") from exc
    if parsed.tzinfo is None or parsed.utcoffset() != timezone.utc.utcoffset(parsed):
        raise ManifestError("UTC value must include UTC timezone")
    return parsed
