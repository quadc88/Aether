"""M127A isolated host trust-bootstrap transaction foundation.

The public boundary is raw canonical evidence plus verifier-issued typed
results.  This module has no live-host default, no caller-selected executable,
no private-key input, and no privileged adapter.  Every mutation requires the
capability issued by ``create_isolated_root``.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
import base64
import fcntl
import hashlib
import os
from pathlib import Path
import re
import shutil
import sqlite3
import stat
import subprocess
import tempfile
import time
from types import MappingProxyType
from typing import Any, Callable, Mapping, Protocol

from .lifecycle import LifecycleError, TemporaryRootCapability, _path_has_symlink, _require_capability, ensure_temporary_root
from .manifest_schema import ManifestError, canonical_json_bytes, parse_canonical_json


class HostTrustBootstrapError(RuntimeError):
    """A bounded trust-bootstrap operation failed closed."""


class HostTrustBootstrapInterrupted(HostTrustBootstrapError):
    """A deterministic failpoint stopped work after evidence was retained."""


class TrustBootstrapState(str, Enum):
    REQUESTED = "TRUST_BOOTSTRAP_REQUESTED"
    VALIDATED = "TRUST_BOOTSTRAP_VALIDATED"
    PRIOR_GENERATION_RETAINED = "PRIOR_GENERATION_RETAINED"
    NEXT_GENERATION_STAGED = "NEXT_GENERATION_STAGED"
    PUBLISHING = "PUBLISHING"
    VERIFYING = "VERIFYING"
    ACTIVE = "TRUST_SET_ACTIVE"
    RESTORING = "RESTORING_PRIOR_GENERATION"
    REVIEW_REQUIRED = "TRUST_BOOTSTRAP_REVIEW_REQUIRED"


OBJECT_PATHS = (
    "/etc/aether/release-trust-anchor.pub",
    "/etc/aether/release-trust-anchor.fingerprint",
    "/etc/aether/release-test-evidence.sha256",
    "/etc/aether/release-verifier.sha256",
    "/usr/libexec/aether-release-verify",
)
PUBLICATION_ORDER = (OBJECT_PATHS[4], OBJECT_PATHS[3], OBJECT_PATHS[0], OBJECT_PATHS[1], OBJECT_PATHS[2])
OBJECT_MODES = {path: (0o555 if path.endswith("aether-release-verify") else 0o444) for path in OBJECT_PATHS}
STATE_DB = Path("var/lib/aether/trust-bootstrap/state.sqlite3")
STATE_LOCK = Path("var/lib/aether/trust-bootstrap/state.lock")
STAGING_ROOT = Path("var/lib/aether/trust-bootstrap/staging")
AUTHORIZATION_DOMAIN = "aether.m126a.trust-bootstrap-authorization.v1"
AUTHORITY_FINGERPRINT_DOMAIN = "aether.m126a.host-bootstrap-authority-key.v1"
IMAGE_BASELINE_DOMAIN = "aether.m127a.os-image-authority-baseline.v1"
LOCAL_CONSOLE_DOMAIN = "aether.m127a.local-console-attestation.v1"
GOVERNANCE_DOMAIN = "aether.m127a.governance-scope.v1"
OPENSSL = "/usr/bin/openssl"
MAX_RECORD_BYTES = 64 * 1024
MAX_OBJECT_BYTES = 1024 * 1024
_DIGEST = re.compile(r"^[0-9a-f]{64}$")
_IDENTIFIER = re.compile(r"^[A-Za-z0-9_.:-]{1,128}$")
_BASE64URL = re.compile(r"^[A-Za-z0-9_-]+$")

AUTHORITY_SET_FIELDS = (
    "authority_set_version", "baseline_id", "authority_records",
    "minimum_accepted_authority_generation", "set_fingerprint_sha256",
    "image_baseline_manifest_digest",
)
AUTHORITY_RECORD_FIELDS = (
    "authority_id", "authority_role", "algorithm", "public_key_base64url",
    "key_fingerprint_sha256", "authority_generation", "valid_from_utc",
    "valid_until_utc", "revoked_at_utc",
)
PAYLOAD_FIELDS = (
    "payload_version", "authorization_id", "transaction_id",
    "target_host_identity_digest", "target_boot_digest", "trust_generation",
    "minimum_accepted_generation", "object_set_digest", "requested_objects",
    "mutation_scope", "local_console_attestation_digest",
    "governance_scope_digest", "bootstrap_authority_root_fingerprint",
    "bootstrap_authority_generation", "authority_set_record_digest",
    "issued_at_utc", "expires_at_utc", "nonce",
)
ENVELOPE_FIELDS = (
    "envelope_version", "payload_sha256", "authorizing_role",
    "authorizing_authority_id", "authenticated_evidence_algorithm",
    "detached_signature", "verification_key_or_trust_source", "issued_at_utc",
    "expires_at_utc", "target_host_identity_digest", "target_boot_digest",
    "bootstrap_authority_root_fingerprint", "bootstrap_authority_generation",
    "authority_set_record_digest", "trust_generation", "object_set_digest",
    "nonce", "transaction_id", "domain_separator",
)
LOCAL_FIELDS = (
    "evidence_version", "attestation_id", "target_host_identity_digest",
    "target_boot_digest", "bootstrap_authority_root_fingerprint",
    "bootstrap_authority_generation", "authority_set_record_digest",
    "local_console_authority_id", "session_class", "remote",
    "fresh_authentication", "human_confirmation_digest", "issued_at_utc",
    "expires_at_utc", "nonce", "evidence_algorithm", "authenticated_evidence",
)
GOVERNANCE_FIELDS = (
    "evidence_version", "governance_evidence_id", "milestone",
    "approved_scope_digest", "approved_policy_digest", "approved_object_set_digest",
    "approved_generation_policy_digest", "issuer_role", "issuer_authority_id",
    "issued_at_utc", "expires_at_utc", "authenticated_evidence_algorithm",
    "authenticated_evidence",
)
DURABLE_FIELDS = (
    "record_version", "transaction_id", "authorization_id", "verification_context_digest", "envelope_sha256",
    "payload_sha256", "local_console_attestation_digest", "governance_scope_digest",
    "target_host_identity_digest", "target_boot_digest",
    "bootstrap_authority_root_fingerprint", "bootstrap_authority_generation",
    "authority_set_record_digest", "trust_generation", "minimum_accepted_generation", "object_set_digest", "nonce",
    "state", "previous_record_digest", "journal_head_digest", "issued_at_utc",
    "expires_at_utc", "consumed_at_utc", "result", "failure_class",
)
TRUST_SOURCE_FIELDS = (
    "source_kind", "authority_set_path", "authority_set_record_digest",
    "authority_id", "key_fingerprint_sha256", "authority_generation",
    "image_baseline_manifest_digest",
)
OBSERVATION_FIELDS = (
    "observation_version", "transaction_id", "trust_generation", "anchor_fingerprint",
    "verifier_digest", "object_set_digest", "objects", "journal_head_digest",
    "observation_digest",
)
OBSERVED_OBJECT_FIELDS = (
    "path", "sha256", "size", "type", "mode", "owner_model", "group_model",
    "link_count", "link_identity",
)
VERIFICATION_FIELDS = (
    "verification_version", "transaction_id", "observation_digest",
    "expected_object_set_digest", "observed_object_set_digest", "verdict",
    "journal_head_digest", "verification_digest",
)
RECOVERY_OBSERVATION_FIELDS = (
    "recovery_observation_version", "transaction_id", "prior_state_digest",
    "object_set_digest", "objects", "journal_head_digest", "observation_digest",
)
RECOVERY_VERIFICATION_FIELDS = (
    "recovery_verification_version", "transaction_id", "observation_digest",
    "expected_object_set_digest", "observed_object_set_digest", "verdict",
    "journal_head_digest", "verification_digest",
)
ALLOWED_TRANSITIONS = {
    TrustBootstrapState.REQUESTED.value: {TrustBootstrapState.VALIDATED.value, TrustBootstrapState.RESTORING.value},
    TrustBootstrapState.VALIDATED.value: {TrustBootstrapState.PRIOR_GENERATION_RETAINED.value, TrustBootstrapState.RESTORING.value},
    TrustBootstrapState.PRIOR_GENERATION_RETAINED.value: {TrustBootstrapState.NEXT_GENERATION_STAGED.value, TrustBootstrapState.RESTORING.value},
    TrustBootstrapState.NEXT_GENERATION_STAGED.value: {TrustBootstrapState.PUBLISHING.value, TrustBootstrapState.RESTORING.value},
    TrustBootstrapState.PUBLISHING.value: {TrustBootstrapState.VERIFYING.value, TrustBootstrapState.RESTORING.value},
    TrustBootstrapState.VERIFYING.value: {TrustBootstrapState.ACTIVE.value, TrustBootstrapState.RESTORING.value},
    TrustBootstrapState.ACTIVE.value: set(),
    TrustBootstrapState.RESTORING.value: {TrustBootstrapState.REVIEW_REQUIRED.value},
    TrustBootstrapState.REVIEW_REQUIRED.value: set(),
}
SCHEMA_NAME = "M127A_HOST_TRUST_BOOTSTRAP"
SCHEMA_VERSION = 3
SCHEMA_TABLES = {"schema_metadata", "transactions", "generation_reservations", "audit", "prior_objects", "observations", "verifications", "recovery_observations", "recovery_verifications"}
_ISSUANCE_TOKEN = object()
_CONTEXT_TOKEN = object()
CONTEXT_SCHEMA_VERSION = 1
VERIFICATION_POLICY_VERSION = "M127A_CONTEXT_POLICY_V3"
ACCEPTED_ALGORITHMS = ("ED25519_DETACHED_SIGNATURE_V1",)


def _fail(message: str) -> None:
    raise HostTrustBootstrapError(message)


class TrustVerificationContext:
    """One process-local configuration boundary for all M127A verifiers."""

    __slots__ = (
        "_process_identity", "_binding_digest", "image_baseline_public_key",
        "expected_baseline_digest", "local_console_public_key", "governance_public_key",
    )

    @classmethod
    def create(cls, *, image_baseline_public_key: bytes, expected_baseline_digest: str, local_console_public_key: bytes, governance_public_key: bytes) -> "TrustVerificationContext":
        return cls(_CONTEXT_TOKEN, image_baseline_public_key, expected_baseline_digest, local_console_public_key, governance_public_key)

    def __init__(self, token: object, image_baseline_public_key: bytes, expected_baseline_digest: str, local_console_public_key: bytes, governance_public_key: bytes) -> None:
        if token is not _CONTEXT_TOKEN:
            raise TypeError("verification contexts are issued by TrustVerificationContext.create")
        for key in (image_baseline_public_key, local_console_public_key, governance_public_key):
            if not isinstance(key, bytes) or len(key) != 32:
                _fail("verification context key is invalid")
        object.__setattr__(self, "_process_identity", object())
        object.__setattr__(self, "image_baseline_public_key", bytes(image_baseline_public_key))
        object.__setattr__(self, "expected_baseline_digest", _digest(expected_baseline_digest, "verification context baseline digest"))
        object.__setattr__(self, "local_console_public_key", bytes(local_console_public_key))
        object.__setattr__(self, "governance_public_key", bytes(governance_public_key))
        fingerprint_input = {
            "context_schema_version": CONTEXT_SCHEMA_VERSION,
            "image_baseline_trust_domain": IMAGE_BASELINE_DOMAIN,
            "image_baseline_public_key_fingerprint": hashlib.sha256(bytes(image_baseline_public_key)).hexdigest(),
            "expected_baseline_digest": self.expected_baseline_digest,
            "local_console_trust_domain": LOCAL_CONSOLE_DOMAIN,
            "local_console_public_key_fingerprint": hashlib.sha256(bytes(local_console_public_key)).hexdigest(),
            "governance_trust_domain": GOVERNANCE_DOMAIN,
            "governance_public_key_fingerprint": hashlib.sha256(bytes(governance_public_key)).hexdigest(),
            "authorization_trust_domain": AUTHORIZATION_DOMAIN,
            "accepted_algorithms": list(ACCEPTED_ALGORITHMS),
            "verification_policy_version": VERIFICATION_POLICY_VERSION,
        }
        object.__setattr__(self, "_binding_digest", hashlib.sha256(_domain_bytes("aether.m127a.verification-context-fingerprint.v1") + _canonical_json_bytes(fingerprint_input)).hexdigest())

    @property
    def process_identity(self) -> object:
        """Opaque identity that is intentionally not durable across restart."""

        return self._process_identity

    @property
    def binding_digest(self) -> str:
        return self._binding_digest

    @property
    def durable_fingerprint(self) -> str:
        """Deterministic fingerprint for durable records and restart binding."""

        return self._binding_digest

    def __setattr__(self, name: str, value: Any) -> None:
        if hasattr(self, name):
            raise AttributeError("verification context is immutable")
        object.__setattr__(self, name, value)


def _exact(value: Any, fields: tuple[str, ...], name: str) -> dict[str, Any]:
    if not isinstance(value, Mapping) or tuple(sorted(value)) != tuple(sorted(fields)):
        _fail(f"{name} fields are not exact")
    return dict(value)


def parse_external_record(raw: bytes, fields: tuple[str, ...], name: str) -> tuple[dict[str, Any], bytes]:
    """Parse and retain one bounded canonical external record."""

    if not isinstance(raw, bytes) or not 0 < len(raw) <= MAX_RECORD_BYTES:
        _fail(f"{name} encoded size is invalid")
    if raw.startswith(b"\xef\xbb\xbf"):
        _fail(f"{name} BOM is forbidden")
    try:
        value = parse_canonical_json(raw)
    except (ManifestError, UnicodeError) as exc:
        raise HostTrustBootstrapError(f"{name} is not canonical UTF-8 JSON") from exc
    result = _exact(value, fields, name)
    if _canonical_json_bytes(result) != raw:
        _fail(f"{name} canonical bytes changed")
    return result, bytes(raw)


def _digest(value: Any, name: str) -> str:
    if not isinstance(value, str) or not _DIGEST.fullmatch(value):
        _fail(f"{name} is not a lowercase SHA-256 digest")
    return value


def _identifier(value: Any, name: str) -> str:
    if not isinstance(value, str) or not _IDENTIFIER.fullmatch(value):
        _fail(f"{name} is not bounded")
    return value


def _utc(value: Any, name: str) -> datetime:
    if not isinstance(value, str):
        _fail(f"{name} is not UTC")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise HostTrustBootstrapError(f"{name} is not UTC") from exc
    if parsed.tzinfo is None or parsed.utcoffset() != timezone.utc.utcoffset(parsed):
        _fail(f"{name} must include UTC")
    return parsed.astimezone(timezone.utc)


def _b64url(value: Any, name: str, size: int) -> bytes:
    if not isinstance(value, str) or not _BASE64URL.fullmatch(value) or "=" in value:
        _fail(f"{name} encoding is invalid")
    try:
        decoded = base64.urlsafe_b64decode(value + "===")
    except (ValueError, base64.binascii.Error) as exc:
        raise HostTrustBootstrapError(f"{name} encoding is invalid") from exc
    if len(decoded) != size or base64.urlsafe_b64encode(decoded).decode().rstrip("=") != value:
        _fail(f"{name} encoding is non-canonical")
    return decoded


def _domain_bytes(domain: str) -> bytes:
    return domain.encode("ascii") + b"\0"


def _freeze(value: Any) -> Any:
    if isinstance(value, Mapping):
        return MappingProxyType({key: _freeze(item) for key, item in value.items()})
    if isinstance(value, list):
        return tuple(_freeze(item) for item in value)
    return value


def _jsonable(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {key: _jsonable(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_jsonable(item) for item in value]
    return value


def _canonical_json_bytes(value: Any) -> bytes:
    return canonical_json_bytes(_jsonable(value))


def authority_key_fingerprint(record: Mapping[str, Any]) -> str:
    value = _exact(record, AUTHORITY_RECORD_FIELDS, "authority record")
    value.pop("key_fingerprint_sha256")
    return hashlib.sha256(_domain_bytes(AUTHORITY_FINGERPRINT_DOMAIN) + _canonical_json_bytes(value)).hexdigest()


def authority_set_fingerprint(authority_set: Mapping[str, Any]) -> str:
    value = _exact(authority_set, AUTHORITY_SET_FIELDS, "authority set")
    value.pop("set_fingerprint_sha256")
    return hashlib.sha256(_domain_bytes(AUTHORITY_FINGERPRINT_DOMAIN) + _canonical_json_bytes(value)).hexdigest()


def _fixed_openssl_verify(public_key: bytes, message: bytes, signature: bytes) -> None:
    """Use the repository-accepted fixed OpenSSL verifier without private input."""

    if not all(isinstance(value, bytes) for value in (public_key, message, signature)) or len(public_key) != 32 or len(signature) != 64 or len(message) > 256 * 1024:
        _fail("Ed25519 input bounds are invalid")
    with tempfile.TemporaryDirectory(prefix="aether-m127a-verify-") as directory:
        base = Path(directory)
        public_path = base / "public.der"
        message_path = base / "message.bin"
        signature_path = base / "signature.bin"
        public_path.write_bytes(bytes.fromhex("302a300506032b6570032100") + public_key)
        message_path.write_bytes(message)
        signature_path.write_bytes(signature)
        try:
            result = subprocess.run(
                [OPENSSL, "pkeyutl", "-verify", "-rawin", "-pubin", "-inkey", str(public_path),
                 "-in", str(message_path), "-sigfile", str(signature_path)],
                stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                cwd=str(base), env={"LC_ALL": "C", "PATH": "/usr/bin:/bin", "HOME": "/var/empty"},
                close_fds=True, check=False, timeout=2.0,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise HostTrustBootstrapError("fixed Ed25519 verifier unavailable") from exc
        if result.returncode != 0 or len(result.stdout) > 4096 or len(result.stderr) > 4096:
            _fail("Ed25519 signature is invalid")


def verify_detached_ed25519(public_key: bytes, message: bytes, signature: bytes) -> None:
    _fixed_openssl_verify(public_key, message, signature)


def authorization_signing_input(payload_raw: bytes, envelope_raw: bytes) -> bytes:
    payload, payload_bytes = parse_external_record(payload_raw, PAYLOAD_FIELDS, "authorization payload")
    envelope, _ = parse_external_record(envelope_raw, ENVELOPE_FIELDS, "authorization envelope")
    unsigned = dict(envelope)
    unsigned.pop("detached_signature")
    return _domain_bytes(AUTHORIZATION_DOMAIN) + payload_bytes + b"\0" + _canonical_json_bytes(unsigned)


class _VerifiedRecord:
    __slots__ = ("raw", "value", "record_digest", "trust_domain", "context")

    def __init__(self, token: object, raw: bytes, value: dict[str, Any], trust_domain: str, context: TrustVerificationContext) -> None:
        if token is not _ISSUANCE_TOKEN:
            raise TypeError("verified results are issued only by bounded verifiers")
        if not isinstance(context, TrustVerificationContext):
            _fail("verified result context is invalid")
        self.raw = bytes(raw)
        self.value = _freeze(value)
        self.record_digest = hashlib.sha256(self.raw).hexdigest()
        self.trust_domain = trust_domain
        self.context = context

    def __setattr__(self, name: str, value: Any) -> None:
        if hasattr(self, name):
            raise AttributeError("verified results are immutable")
        object.__setattr__(self, name, value)


class VerifiedImageBaseline(_VerifiedRecord):
    pass


class VerifiedAuthoritySet(_VerifiedRecord):
    __slots__ = ("records", "baseline_digest")

    def __init__(self, token: object, raw: bytes, value: dict[str, Any], baseline_digest: str, context: TrustVerificationContext) -> None:
        super().__init__(token, raw, value, "PREEXISTING_OS_IMAGE_AUTHORITY_SET", context)
        self.records = MappingProxyType({item["authority_id"]: _freeze(item) for item in value["authority_records"]})
        self.baseline_digest = baseline_digest


class VerifiedLocalConsoleEvidence(_VerifiedRecord):
    pass


class VerifiedGovernanceEvidence(_VerifiedRecord):
    pass


class VerifiedAuthorization(_VerifiedRecord):
    __slots__ = ("payload_raw", "payload", "envelope", "authority", "local_console", "governance")

    def __init__(self, token: object, payload_raw: bytes, payload: dict[str, Any], envelope_raw: bytes, envelope: dict[str, Any], authority: VerifiedAuthoritySet, local_console: VerifiedLocalConsoleEvidence, governance: VerifiedGovernanceEvidence, context: TrustVerificationContext) -> None:
        super().__init__(token, envelope_raw, envelope, AUTHORIZATION_DOMAIN, context)
        self.payload_raw = bytes(payload_raw)
        self.payload = _freeze(payload)
        self.envelope = _freeze(envelope)
        self.authority = authority
        self.local_console = local_console
        self.governance = governance


class ImageBaselineVerifier:
    """Explicit verifier interface for the externally authenticated image result."""

    trust_domain = IMAGE_BASELINE_DOMAIN
    __slots__ = ("context",)

    def __setattr__(self, name: str, value: Any) -> None:
        if hasattr(self, name):
            raise AttributeError("verifier context is immutable")
        object.__setattr__(self, name, value)

    def __init__(self, context: TrustVerificationContext) -> None:
        if not isinstance(context, TrustVerificationContext):
            _fail("image-baseline verifier context is invalid")
        self.context = context

    def verify(self, raw_authority_set: bytes, detached_signature: bytes) -> VerifiedImageBaseline:
        value, raw = parse_external_record(raw_authority_set, AUTHORITY_SET_FIELDS, "image authority baseline")
        if hashlib.sha256(raw).hexdigest() != self.context.expected_baseline_digest:
            _fail("image baseline digest is not approved")
        signature = _b64url(detached_signature, "image baseline signature", 64) if isinstance(detached_signature, str) else detached_signature
        verify_detached_ed25519(self.context.image_baseline_public_key, _domain_bytes(self.trust_domain) + raw, signature)
        return VerifiedImageBaseline(_ISSUANCE_TOKEN, raw, value, self.trust_domain, self.context)


class AuthoritySetVerifier:
    trust_domain = "PREEXISTING_OS_IMAGE_AUTHORITY_SET"

    def verify(self, baseline: VerifiedImageBaseline) -> VerifiedAuthoritySet:
        if not isinstance(baseline, VerifiedImageBaseline) or baseline.trust_domain != IMAGE_BASELINE_DOMAIN:
            _fail("wrong image-baseline verifier result")
        value = _exact(baseline.value, AUTHORITY_SET_FIELDS, "authority set")
        if value["authority_set_version"] != 1 or not isinstance(value["authority_records"], (list, tuple)) or not value["authority_records"]:
            _fail("authority set version or records are invalid")
        _digest(value["image_baseline_manifest_digest"], "image baseline manifest digest")
        seen: set[str] = set()
        for raw_record in value["authority_records"]:
            record = _exact(raw_record, AUTHORITY_RECORD_FIELDS, "authority record")
            authority_id = _identifier(record["authority_id"], "authority ID")
            if authority_id in seen:
                _fail("duplicate authority ID")
            seen.add(authority_id)
            if record["authority_role"] != "HOST_TRUST_BOOTSTRAP_AUTHORITY" or record["algorithm"] != "Ed25519":
                _fail("authority role or algorithm is invalid")
            _b64url(record["public_key_base64url"], "authority public key", 32)
            if record["key_fingerprint_sha256"] != authority_key_fingerprint(record):
                _fail("authority key fingerprint is invalid")
            generation = record["authority_generation"]
            if not isinstance(generation, int) or isinstance(generation, bool) or generation < 1:
                _fail("authority generation is invalid")
            start, end = _utc(record["valid_from_utc"], "authority valid-from"), _utc(record["valid_until_utc"], "authority valid-until")
            if end <= start:
                _fail("authority validity interval is invalid")
            if record["revoked_at_utc"] is not None:
                revoked = _utc(record["revoked_at_utc"], "authority revoked-at")
                if not start <= revoked <= end:
                    _fail("authority revocation interval is invalid")
        minimum = value["minimum_accepted_authority_generation"]
        if not isinstance(minimum, int) or isinstance(minimum, bool) or minimum < 1:
            _fail("minimum authority generation is invalid")
        if value["set_fingerprint_sha256"] != authority_set_fingerprint(value):
            _fail("authority set fingerprint is invalid")
        return VerifiedAuthoritySet(_ISSUANCE_TOKEN, baseline.raw, value, baseline.record_digest, baseline.context)


class _EvidenceVerifier:
    fields: tuple[str, ...]
    trust_domain: str
    marker: str
    __slots__ = ("context",)

    def __setattr__(self, name: str, value: Any) -> None:
        if hasattr(self, name):
            raise AttributeError("verifier context is immutable")
        object.__setattr__(self, name, value)

    def __init__(self, context: TrustVerificationContext) -> None:
        if not isinstance(context, TrustVerificationContext):
            _fail("evidence verifier context is invalid")
        self.context = context

    def _verify(self, raw: bytes, detached_signature: bytes) -> dict[str, Any]:
        value, exact_raw = parse_external_record(raw, self.fields, self.trust_domain)
        signature = _b64url(detached_signature, "evidence signature", 64) if isinstance(detached_signature, str) else detached_signature
        public_key = self.context.local_console_public_key if self.trust_domain == LOCAL_CONSOLE_DOMAIN else self.context.governance_public_key
        verify_detached_ed25519(public_key, _domain_bytes(self.trust_domain) + exact_raw, signature)
        if value["evidence_version"] != 1 or value["authenticated_evidence"] != self.marker:
            _fail("evidence provenance marker is invalid")
        if "target_host_identity_digest" in value:
            _digest(value["target_host_identity_digest"], "evidence host digest")
        if "target_boot_digest" in value:
            _digest(value["target_boot_digest"], "evidence boot digest")
        for field in ("issued_at_utc", "expires_at_utc"):
            _utc(value[field], f"{self.trust_domain} {field}")
        if _utc(value["expires_at_utc"], "evidence expiry") <= _utc(value["issued_at_utc"], "evidence issue"):
            _fail("evidence validity interval is invalid")
        return value


class LocalConsoleEvidenceVerifier(_EvidenceVerifier):
    fields = LOCAL_FIELDS
    trust_domain = LOCAL_CONSOLE_DOMAIN
    marker = "LOCAL_CONSOLE_VERIFIER_V1"

    def verify(self, raw: bytes, detached_signature: bytes) -> VerifiedLocalConsoleEvidence:
        value, exact_raw = parse_external_record(raw, self.fields, self.trust_domain)
        self._verify(exact_raw, detached_signature)
        if value["session_class"] != "LOCAL_CONSOLE" or value["remote"] is not False or value["fresh_authentication"] is not True:
            _fail("local-console evidence is not fresh local presence")
        for field in ("bootstrap_authority_root_fingerprint", "authority_set_record_digest", "human_confirmation_digest"):
            _digest(value[field], f"local-console {field}")
        if value["evidence_algorithm"] != "ED25519_DETACHED_SIGNATURE_V1":
            _fail("local-console evidence algorithm is invalid")
        return VerifiedLocalConsoleEvidence(_ISSUANCE_TOKEN, exact_raw, value, self.trust_domain, self.context)


class GovernanceEvidenceVerifier(_EvidenceVerifier):
    fields = GOVERNANCE_FIELDS
    trust_domain = GOVERNANCE_DOMAIN
    marker = "GOVERNANCE_VERIFIER_V1"

    def verify(self, raw: bytes, detached_signature: bytes) -> VerifiedGovernanceEvidence:
        value, exact_raw = parse_external_record(raw, self.fields, self.trust_domain)
        self._verify(exact_raw, detached_signature)
        if value["issuer_role"] != "PM_GOVERNANCE" or value["milestone"] != "M127A":
            _fail("governance issuer or milestone is invalid")
        for field in ("approved_scope_digest", "approved_policy_digest", "approved_object_set_digest", "approved_generation_policy_digest"):
            _digest(value[field], f"governance {field}")
        if value["authenticated_evidence_algorithm"] != "ED25519_DETACHED_SIGNATURE_V1":
            _fail("governance evidence algorithm is invalid")
        return VerifiedGovernanceEvidence(_ISSUANCE_TOKEN, exact_raw, value, self.trust_domain, self.context)


class AuthorizationVerifier:
    trust_domain = AUTHORIZATION_DOMAIN
    __slots__ = ("context",)

    def __init__(self, context: TrustVerificationContext) -> None:
        if not isinstance(context, TrustVerificationContext):
            _fail("authorization verifier context is invalid")
        self.context = context

    def __setattr__(self, name: str, value: Any) -> None:
        if hasattr(self, name):
            raise AttributeError("verifier context is immutable")
        object.__setattr__(self, name, value)

    def verify(self, payload_raw: bytes, envelope_raw: bytes, *, authority: VerifiedAuthoritySet, local_console: VerifiedLocalConsoleEvidence, governance: VerifiedGovernanceEvidence, target_host_identity_digest: str, target_boot_digest: str, now_utc: str, allow_expired: bool = False) -> VerifiedAuthorization:
        if not isinstance(authority, VerifiedAuthoritySet) or not isinstance(local_console, VerifiedLocalConsoleEvidence) or not isinstance(governance, VerifiedGovernanceEvidence):
            _fail("typed verified results are required")
        if authority.context is not self.context or local_console.context is not self.context or governance.context is not self.context:
            _fail("verified evidence context is not exact")
        payload, payload_bytes = parse_external_record(payload_raw, PAYLOAD_FIELDS, "authorization payload")
        envelope, envelope_bytes = parse_external_record(envelope_raw, ENVELOPE_FIELDS, "authorization envelope")
        now = _utc(now_utc, "current time")
        _digest(target_host_identity_digest, "target host identity digest")
        _digest(target_boot_digest, "target boot digest")
        if payload["payload_version"] != 1 or envelope["envelope_version"] != 1:
            _fail("authorization record version is invalid")
        if envelope["domain_separator"] != AUTHORIZATION_DOMAIN or envelope["authenticated_evidence_algorithm"] != "ED25519_DETACHED_SIGNATURE_V1":
            _fail("authorization envelope domain or algorithm is invalid")
        payload_digest = hashlib.sha256(payload_bytes).hexdigest()
        if envelope["payload_sha256"] != payload_digest:
            _fail("payload digest binding is invalid")
        for field in ("target_host_identity_digest", "target_boot_digest", "object_set_digest", "local_console_attestation_digest", "governance_scope_digest", "bootstrap_authority_root_fingerprint", "authority_set_record_digest"):
            _digest(payload[field], f"payload {field}")
        for field in ("target_host_identity_digest", "target_boot_digest", "bootstrap_authority_root_fingerprint", "authority_set_record_digest", "object_set_digest"):
            if payload[field] != {"target_host_identity_digest": target_host_identity_digest, "target_boot_digest": target_boot_digest, "bootstrap_authority_root_fingerprint": authority.value["set_fingerprint_sha256"], "authority_set_record_digest": authority.record_digest, "object_set_digest": payload["object_set_digest"]}[field]:
                _fail(f"payload {field} is not bound")
        if payload["requested_objects"] != list(OBJECT_PATHS) or payload["mutation_scope"] != "PUBLISH_EXACT_FIVE_HOST_TRUST_OBJECTS_FOR_TARGET_HOST_AND_GENERATION":
            _fail("authorization scope is not exact")
        for field in ("authorization_id", "transaction_id", "nonce"):
            _identifier(payload[field], f"payload {field}")
        for field in ("trust_generation", "minimum_accepted_generation", "bootstrap_authority_generation"):
            if not isinstance(payload[field], int) or isinstance(payload[field], bool) or payload[field] < 1:
                _fail(f"payload {field} is invalid")
        issued, expires = _utc(payload["issued_at_utc"], "payload issue"), _utc(payload["expires_at_utc"], "payload expiry")
        if expires <= issued or (not allow_expired and not issued <= now < expires):
            _fail("authorization validity interval is invalid")
        if envelope["issued_at_utc"] != payload["issued_at_utc"] or envelope["expires_at_utc"] != payload["expires_at_utc"]:
            _fail("envelope time binding is invalid")
        for field in ("target_host_identity_digest", "target_boot_digest", "bootstrap_authority_root_fingerprint", "bootstrap_authority_generation", "authority_set_record_digest", "trust_generation", "object_set_digest", "nonce", "transaction_id"):
            if envelope[field] != payload[field]:
                _fail(f"envelope {field} binding is invalid")
        source = _exact(envelope["verification_key_or_trust_source"], TRUST_SOURCE_FIELDS, "trust-source reference")
        if source["source_kind"] != "PREEXISTING_OS_IMAGE_AUTHORITY_SET" or source["authority_set_path"] != "/usr/lib/aether/host-bootstrap/authority-set.json":
            _fail("trust-source reference is invalid")
        if source["authority_set_record_digest"] != authority.record_digest or source["image_baseline_manifest_digest"] != authority.value["image_baseline_manifest_digest"]:
            _fail("trust-source baseline binding is invalid")
        authority_id = envelope["authorizing_authority_id"]
        if envelope["authorizing_role"] != "HOST_TRUST_BOOTSTRAP_AUTHORITY" or authority_id not in authority.records:
            _fail("authorizing authority is not allowlisted")
        record = authority.records[authority_id]
        if source["authority_id"] != authority_id or source["key_fingerprint_sha256"] != record["key_fingerprint_sha256"] or source["authority_generation"] != record["authority_generation"] or payload["bootstrap_authority_generation"] != record["authority_generation"]:
            _fail("authorizing authority binding is invalid")
        if record["authority_generation"] < authority.value["minimum_accepted_authority_generation"]:
            _fail("authority generation is stale")
        if record["revoked_at_utc"] is not None and _utc(record["revoked_at_utc"], "authority revocation") <= now:
            _fail("authority is revoked")
        if not _utc(record["valid_from_utc"], "authority valid-from") <= now < _utc(record["valid_until_utc"], "authority valid-until"):
            _fail("authority is outside validity")
        if local_console.trust_domain != LOCAL_CONSOLE_DOMAIN or governance.trust_domain != GOVERNANCE_DOMAIN:
            _fail("evidence trust domains are not distinct")
        if payload["local_console_attestation_digest"] != local_console.record_digest or payload["governance_scope_digest"] != governance.record_digest:
            _fail("evidence digest binding is invalid")
        local = local_console.value
        for field in ("target_host_identity_digest", "target_boot_digest", "bootstrap_authority_root_fingerprint", "bootstrap_authority_generation", "authority_set_record_digest"):
            expected = {"target_host_identity_digest": target_host_identity_digest, "target_boot_digest": target_boot_digest, "bootstrap_authority_root_fingerprint": authority.value["set_fingerprint_sha256"], "bootstrap_authority_generation": record["authority_generation"], "authority_set_record_digest": authority.record_digest}[field]
            if local[field] != expected:
                _fail(f"local-console {field} is not bound")
        if local["nonce"] != payload["nonce"] or local["issued_at_utc"] != payload["issued_at_utc"] or local["expires_at_utc"] != payload["expires_at_utc"]:
            _fail("local-console transaction binding is invalid")
        gov = governance.value
        if gov["approved_object_set_digest"] != payload["object_set_digest"]:
            _fail("governance object-set binding is invalid")
        verify_detached_ed25519(
            _b64url(record["public_key_base64url"], "authority public key", 32),
            authorization_signing_input(payload_bytes, envelope_bytes),
            _b64url(envelope["detached_signature"], "authorization signature", 64),
        )
        return VerifiedAuthorization(_ISSUANCE_TOKEN, payload_bytes, payload, envelope_bytes, envelope, authority, local_console, governance, self.context)


def object_set_digest(objects: Mapping[str, bytes]) -> str:
    if not isinstance(objects, Mapping) or set(objects) != set(OBJECT_PATHS):
        _fail("object set paths are not exact")
    descriptors = []
    for path in OBJECT_PATHS:
        data = objects[path]
        if not isinstance(data, bytes) or not 0 < len(data) <= MAX_OBJECT_BYTES or any(term in data.upper() for term in (b"PRIVATE KEY", b"BEGIN OPENSSH PRIVATE")):
            _fail("object bytes are invalid or sensitive")
        descriptors.append({"path": path, "sha256": hashlib.sha256(data).hexdigest(), "size": len(data), "mode": OBJECT_MODES[path]})
    return hashlib.sha256(_canonical_json_bytes(descriptors)).hexdigest()


def _validate_objects(objects: Mapping[str, bytes]) -> None:
    object_set_digest(objects)
    try:
        if not isinstance(parse_canonical_json(objects[OBJECT_PATHS[0]]), Mapping):
            _fail("trust anchor is not an object")
        for path in OBJECT_PATHS[1:4]:
            if not re.fullmatch(r"[0-9a-f]{64}\n", objects[path].decode("ascii")):
                _fail("trust digest object is not exact")
    except (ManifestError, UnicodeError) as exc:
        raise HostTrustBootstrapError("trust anchor or digest is not canonical") from exc
    if objects[OBJECT_PATHS[3]] != (hashlib.sha256(objects[OBJECT_PATHS[4]]).hexdigest() + "\n").encode("ascii"):
        _fail("verifier digest is not bound to verifier bytes")


@dataclass(frozen=True, slots=True)
class TerminalObservation:
    value: dict[str, Any]


@dataclass(frozen=True, slots=True)
class TerminalVerification:
    value: dict[str, Any]


class _StateLock:
    def __init__(self, path: Path, timeout: float) -> None:
        self.path, self.timeout, self.stream = path, timeout, None

    def __enter__(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        if _path_has_symlink(self.path.parent) or self.path.is_symlink():
            _fail("state lock path contains a symlink")
        self.stream = self.path.open("a+b")
        deadline = time.monotonic() + self.timeout
        while True:
            try:
                fcntl.flock(self.stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                return None
            except BlockingIOError:
                if time.monotonic() >= deadline:
                    self.stream.close()
                    self.stream = None
                    _fail("state lock acquisition timed out")
                time.sleep(0.005)

    def __exit__(self, *_: Any) -> None:
        if self.stream is not None:
            fcntl.flock(self.stream.fileno(), fcntl.LOCK_UN)
            self.stream.close()
            self.stream = None


class HostTrustBootstrapFoundation:
    """Consume one verified authorization and publish below one isolated root."""

    def __init__(self, root: str | Path, *, capability: TemporaryRootCapability, context: TrustVerificationContext, authorization_verifier: AuthorizationVerifier, target_host_identity_digest: str, target_boot_digest: str, lock_timeout_seconds: float = 0.25, fault_injector: Callable[[str], None] | None = None, now_utc: Callable[[], str] = lambda: datetime.now(timezone.utc).isoformat()) -> None:
        try:
            self.root = ensure_temporary_root(root)
            _require_capability(self.root, capability, purpose="M127A_BOOTSTRAP")
        except LifecycleError as exc:
            raise HostTrustBootstrapError("explicit isolated-root capability is required") from exc
        if not isinstance(context, TrustVerificationContext) or not isinstance(authorization_verifier, AuthorizationVerifier) or authorization_verifier.context is not context or not 0 < lock_timeout_seconds <= 10:
            _fail("bootstrap verifier or lock timeout is invalid")
        self.capability = capability
        self.context = context
        self.authorization_verifier = authorization_verifier
        _digest(target_host_identity_digest, "foundation host identity digest")
        _digest(target_boot_digest, "foundation boot digest")
        self.target_host_identity_digest = target_host_identity_digest
        self.target_boot_digest = target_boot_digest
        self.lock_timeout_seconds = lock_timeout_seconds
        self.fault_injector = fault_injector
        self.now_utc = now_utc

    @property
    def database_path(self) -> Path:
        return self.root / STATE_DB

    @property
    def lock_path(self) -> Path:
        return self.root / STATE_LOCK

    def _fault(self, point: str) -> None:
        if self.fault_injector is not None:
            try:
                self.fault_injector(point)
            except HostTrustBootstrapInterrupted:
                raise
            except Exception as exc:
                raise HostTrustBootstrapInterrupted(point) from exc

    def _connect(self) -> sqlite3.Connection:
        if _path_has_symlink(self.database_path.parent) or self.database_path.is_symlink():
            _fail("state database path contains a symlink")
        self.database_path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        connection = sqlite3.connect(self.database_path, timeout=2.0, isolation_level=None, check_same_thread=False)
        try:
            mode = connection.execute("PRAGMA journal_mode=WAL").fetchone()
            if not mode or str(mode[0]).upper() != "WAL":
                _fail("SQLite WAL mode was not established")
            connection.execute("PRAGMA synchronous=FULL")
            connection.execute("PRAGMA foreign_keys=ON")
            self._ensure_schema(connection)
            self._validate_journal(connection)
            return connection
        except Exception:
            connection.close()
            raise HostTrustBootstrapError("state database validation failed") from None

    def _ensure_schema(self, connection: sqlite3.Connection) -> None:
        connection.execute("BEGIN IMMEDIATE")
        try:
            tables = {row[0] for row in connection.execute("SELECT name FROM sqlite_master WHERE type='table'")}
            if not tables:
                connection.executescript("""
                    CREATE TABLE schema_metadata (singleton INTEGER PRIMARY KEY CHECK(singleton=1), schema_name TEXT NOT NULL, schema_version INTEGER NOT NULL, minimum_accepted_generation INTEGER NOT NULL, highest_seen_or_reserved_generation INTEGER NOT NULL, active_generation INTEGER NOT NULL, journal_head_digest TEXT);
                    CREATE TABLE transactions (transaction_id TEXT PRIMARY KEY, nonce TEXT NOT NULL UNIQUE, trust_generation INTEGER NOT NULL UNIQUE, record_json BLOB NOT NULL, record_digest TEXT NOT NULL);
                    CREATE TABLE generation_reservations (trust_generation INTEGER PRIMARY KEY, transaction_id TEXT NOT NULL UNIQUE REFERENCES transactions(transaction_id), reservation_state TEXT NOT NULL CHECK(reservation_state IN ('RESERVED','ACTIVE','BURNED')));
                    CREATE TABLE audit (sequence INTEGER PRIMARY KEY, transaction_id TEXT NOT NULL REFERENCES transactions(transaction_id), state TEXT NOT NULL, record_json BLOB NOT NULL, record_digest TEXT NOT NULL);
                    CREATE TABLE prior_objects (transaction_id TEXT NOT NULL REFERENCES transactions(transaction_id), path TEXT NOT NULL, present INTEGER NOT NULL, mode INTEGER NOT NULL, owner_model TEXT NOT NULL, group_model TEXT NOT NULL, link_count INTEGER NOT NULL, link_identity TEXT NOT NULL, content BLOB, content_digest TEXT, PRIMARY KEY(transaction_id, path));
                    CREATE TABLE observations (transaction_id TEXT PRIMARY KEY REFERENCES transactions(transaction_id), record_json BLOB NOT NULL, record_digest TEXT NOT NULL);
                    CREATE TABLE verifications (transaction_id TEXT PRIMARY KEY REFERENCES transactions(transaction_id), record_json BLOB NOT NULL, record_digest TEXT NOT NULL);
                    CREATE TABLE recovery_observations (transaction_id TEXT PRIMARY KEY REFERENCES transactions(transaction_id), record_json BLOB NOT NULL, record_digest TEXT NOT NULL);
                    CREATE TABLE recovery_verifications (transaction_id TEXT PRIMARY KEY REFERENCES transactions(transaction_id), record_json BLOB NOT NULL, record_digest TEXT NOT NULL);
                """)
                connection.execute("INSERT INTO schema_metadata VALUES(1,?,?,?,?,?,?)", (SCHEMA_NAME, SCHEMA_VERSION, 0, 0, 0, None))
            elif tables != SCHEMA_TABLES:
                _fail("SQLite schema table set is unsupported")
            columns = {
                "schema_metadata": ("singleton", "schema_name", "schema_version", "minimum_accepted_generation", "highest_seen_or_reserved_generation", "active_generation", "journal_head_digest"),
                "transactions": ("transaction_id", "nonce", "trust_generation", "record_json", "record_digest"),
                "generation_reservations": ("trust_generation", "transaction_id", "reservation_state"),
                "audit": ("sequence", "transaction_id", "state", "record_json", "record_digest"),
                "prior_objects": ("transaction_id", "path", "present", "mode", "owner_model", "group_model", "link_count", "link_identity", "content", "content_digest"),
                "observations": ("transaction_id", "record_json", "record_digest"),
                "verifications": ("transaction_id", "record_json", "record_digest"),
                "recovery_observations": ("transaction_id", "record_json", "record_digest"),
                "recovery_verifications": ("transaction_id", "record_json", "record_digest"),
            }
            for table, expected in columns.items():
                actual = tuple(row[1] for row in connection.execute(f'PRAGMA table_info("{table}")'))
                if actual != expected:
                    _fail(f"SQLite schema for {table} is unsupported")
            metadata = connection.execute("SELECT * FROM schema_metadata").fetchall()
            if len(metadata) != 1 or tuple(metadata[0])[:2] != (1, SCHEMA_NAME) or metadata[0][2] != SCHEMA_VERSION:
                _fail("SQLite schema version is unsupported")
            integrity = connection.execute("PRAGMA integrity_check").fetchone()
            if integrity is None or integrity[0] != "ok":
                _fail("SQLite integrity check failed")
            connection.commit()
        except Exception:
            connection.rollback()
            raise

    @staticmethod
    def _record_digest(record: Mapping[str, Any]) -> str:
        return hashlib.sha256(_canonical_json_bytes({key: value for key, value in record.items() if key != "journal_head_digest"})).hexdigest()

    def _validate_journal(self, connection: sqlite3.Connection) -> None:
        rows = connection.execute("SELECT sequence, transaction_id, state, record_json, record_digest FROM audit ORDER BY sequence").fetchall()
        previous: str | None = None
        last_by_transaction: dict[str, tuple[bytes, str]] = {}
        state_by_transaction: dict[str, str] = {}
        seen_digests: set[str] = set()
        for expected_sequence, row in enumerate(rows, 1):
            sequence, transaction_id, state, raw, digest = row
            if sequence != expected_sequence:
                _fail("audit ordering is broken")
            try:
                value = parse_canonical_json(bytes(raw))
            except (ManifestError, UnicodeError, TypeError, ValueError) as exc:
                raise HostTrustBootstrapError("audit record is not canonical") from exc
            _exact(value, DURABLE_FIELDS, "durable audit record")
            if digest in seen_digests or value["transaction_id"] != transaction_id or value["state"] != state or digest != self._record_digest(value) or value["journal_head_digest"] != digest or value["previous_record_digest"] != previous:
                _fail("audit digest chain is broken")
            if state not in ALLOWED_TRANSITIONS:
                _fail("unsupported state transition")
            prior_state = state_by_transaction.get(transaction_id)
            if prior_state is None and state != TrustBootstrapState.REQUESTED.value:
                _fail("audit transaction does not begin with request")
            if prior_state is not None and state not in ALLOWED_TRANSITIONS[prior_state]:
                _fail("unsupported state transition")
            seen_digests.add(digest)
            previous = digest
            last_by_transaction[transaction_id] = (bytes(raw), digest)
            state_by_transaction[transaction_id] = state
        metadata = connection.execute("SELECT journal_head_digest FROM schema_metadata WHERE singleton=1").fetchone()
        if metadata is None or metadata[0] != previous:
            _fail("schema journal head is disconnected")
        current_rows = connection.execute("SELECT transaction_id, record_json, record_digest FROM transactions").fetchall()
        if {row[0] for row in current_rows} != set(last_by_transaction):
            _fail("current transaction rows are disconnected")
        if len({parse_canonical_json(bytes(row[1]))["nonce"] for row in current_rows}) != len(current_rows) or len({parse_canonical_json(bytes(row[1]))["trust_generation"] for row in current_rows}) != len(current_rows):
            _fail("global nonce or generation uniqueness is broken")
        metadata_values = connection.execute("SELECT minimum_accepted_generation, highest_seen_or_reserved_generation, active_generation FROM schema_metadata WHERE singleton=1").fetchone()
        maximum_generation = max((parse_canonical_json(bytes(row[1]))["trust_generation"] for row in current_rows), default=0)
        minimum_generation = max((parse_canonical_json(bytes(row[1]))["minimum_accepted_generation"] for row in current_rows), default=0)
        active_generations = [parse_canonical_json(bytes(row[1]))["trust_generation"] for row in current_rows if parse_canonical_json(bytes(row[1]))["state"] == TrustBootstrapState.ACTIVE.value]
        active_generation = max(active_generations, default=0)
        if metadata_values is None or metadata_values[0] != minimum_generation or metadata_values[1] != maximum_generation or metadata_values[2] != active_generation:
            _fail("generation metadata is disconnected")
        reservations = connection.execute("SELECT trust_generation, transaction_id, reservation_state FROM generation_reservations ORDER BY trust_generation").fetchall()
        expected_reservations = {
            parse_canonical_json(bytes(row[1]))["trust_generation"]: (row[0], "ACTIVE" if parse_canonical_json(bytes(row[1]))["state"] == TrustBootstrapState.ACTIVE.value else "BURNED" if parse_canonical_json(bytes(row[1]))["state"] == TrustBootstrapState.REVIEW_REQUIRED.value else "RESERVED")
            for row in current_rows
        }
        if {row[0]: (row[1], row[2]) for row in reservations} != expected_reservations:
            _fail("generation reservations are disconnected")
        for transaction_id, raw, digest in current_rows:
            if last_by_transaction[transaction_id] != (bytes(raw), digest):
                _fail("current transaction row disagrees with journal")
            current = parse_canonical_json(bytes(raw))
            if digest != self._record_digest(current) or current["transaction_id"] != transaction_id:
                _fail("current transaction record digest is invalid")
            if current["state"] == TrustBootstrapState.ACTIVE.value:
                observation = connection.execute("SELECT record_json, record_digest FROM observations WHERE transaction_id=?", (transaction_id,)).fetchone()
                verification = connection.execute("SELECT record_json, record_digest FROM verifications WHERE transaction_id=?", (transaction_id,)).fetchone()
                if observation is None or verification is None:
                    _fail("active transaction lacks terminal observation or verification")
                observed = parse_canonical_json(bytes(observation[0]))
                verified = parse_canonical_json(bytes(verification[0]))
                _exact(observed, OBSERVATION_FIELDS, "terminal observation")
                _exact(verified, VERIFICATION_FIELDS, "terminal verification")
                if not isinstance(observed["objects"], list) or {item.get("path") for item in observed["objects"]} != set(OBJECT_PATHS) or any(not isinstance(item, Mapping) or tuple(sorted(item)) != tuple(sorted(OBSERVED_OBJECT_FIELDS)) for item in observed["objects"]):
                    _fail("terminal observation object evidence is invalid")
                if observation[1] != self._self_digest(observed, "observation_digest") or observed["observation_digest"] != self._self_digest(observed, "observation_digest") or verification[1] != self._self_digest(verified, "verification_digest") or verified["verification_digest"] != self._self_digest(verified, "verification_digest") or verified["observation_digest"] != observed["observation_digest"] or verified["verdict"] != "EXACT_SUCCESS":
                    _fail("terminal evidence is disconnected")
            elif current["state"] == TrustBootstrapState.REVIEW_REQUIRED.value:
                recovery_observation = connection.execute("SELECT record_json, record_digest FROM recovery_observations WHERE transaction_id=?", (transaction_id,)).fetchone()
                recovery_verification = connection.execute("SELECT record_json, record_digest FROM recovery_verifications WHERE transaction_id=?", (transaction_id,)).fetchone()
                if recovery_observation is None or recovery_verification is None:
                    _fail("review transaction lacks recovery evidence")
                observed = parse_canonical_json(bytes(recovery_observation[0]))
                verified = parse_canonical_json(bytes(recovery_verification[0]))
                _exact(observed, RECOVERY_OBSERVATION_FIELDS, "recovery observation")
                _exact(verified, RECOVERY_VERIFICATION_FIELDS, "recovery verification")
                if not isinstance(observed["objects"], list) or any(not isinstance(item, Mapping) or tuple(sorted(item)) != tuple(sorted(OBSERVED_OBJECT_FIELDS)) for item in observed["objects"]):
                    _fail("recovery observation object evidence is invalid")
                expected_recovery_verdict = "PRIOR_GENERATION_EXACT" if current["result"] == "PRIOR_GENERATION_RESTORED_REVIEW_REQUIRED" else "RESTORE_VERIFICATION_FAILED"
                if recovery_observation[1] != self._self_digest(observed, "observation_digest") or observed["observation_digest"] != self._self_digest(observed, "observation_digest") or recovery_verification[1] != self._self_digest(verified, "verification_digest") or verified["verification_digest"] != self._self_digest(verified, "verification_digest") or verified["observation_digest"] != observed["observation_digest"] or verified["verdict"] != expected_recovery_verdict:
                    _fail("recovery evidence is disconnected")

    def _new_record(self, authorization: VerifiedAuthorization, state: str, previous: str | None, *, result: str = "IN_PROGRESS", failure: str = "NONE", consumed: str | None = None) -> dict[str, Any]:
        payload = authorization.payload
        value = {
            "record_version": 1, "transaction_id": payload["transaction_id"], "authorization_id": payload["authorization_id"],
            "verification_context_digest": authorization.context.binding_digest,
            "envelope_sha256": authorization.record_digest, "payload_sha256": hashlib.sha256(authorization.payload_raw).hexdigest(),
            "local_console_attestation_digest": authorization.local_console.record_digest, "governance_scope_digest": authorization.governance.record_digest,
            "target_host_identity_digest": payload["target_host_identity_digest"], "target_boot_digest": payload["target_boot_digest"],
            "bootstrap_authority_root_fingerprint": payload["bootstrap_authority_root_fingerprint"], "bootstrap_authority_generation": payload["bootstrap_authority_generation"],
            "authority_set_record_digest": payload["authority_set_record_digest"], "trust_generation": payload["trust_generation"], "minimum_accepted_generation": payload["minimum_accepted_generation"],
            "object_set_digest": payload["object_set_digest"], "nonce": payload["nonce"], "state": state,
            "previous_record_digest": previous, "journal_head_digest": "", "issued_at_utc": payload["issued_at_utc"],
            "expires_at_utc": payload["expires_at_utc"], "consumed_at_utc": consumed, "result": result, "failure_class": failure,
        }
        value["journal_head_digest"] = self._record_digest(value)
        return value

    def _authorization_identity(self, authorization: VerifiedAuthorization) -> dict[str, Any]:
        payload = authorization.payload
        return {
            "transaction_id": payload["transaction_id"], "authorization_id": payload["authorization_id"],
            "verification_context_digest": authorization.context.binding_digest,
            "envelope_sha256": authorization.record_digest,
            "payload_sha256": hashlib.sha256(authorization.payload_raw).hexdigest(),
            "local_console_attestation_digest": authorization.local_console.record_digest,
            "governance_scope_digest": authorization.governance.record_digest,
            "target_host_identity_digest": payload["target_host_identity_digest"],
            "target_boot_digest": payload["target_boot_digest"],
            "bootstrap_authority_root_fingerprint": payload["bootstrap_authority_root_fingerprint"],
            "bootstrap_authority_generation": payload["bootstrap_authority_generation"],
            "authority_set_record_digest": payload["authority_set_record_digest"],
            "trust_generation": payload["trust_generation"], "minimum_accepted_generation": payload["minimum_accepted_generation"], "object_set_digest": payload["object_set_digest"],
            "nonce": payload["nonce"],
        }

    def _validate_foundation_binding(self, authorization: VerifiedAuthorization) -> None:
        if authorization.context is not self.context:
            _fail("authorization verification context is not exact")
        payload = authorization.payload
        if payload["target_host_identity_digest"] != self.target_host_identity_digest or payload["target_boot_digest"] != self.target_boot_digest:
            _fail("current target identity or boot does not match authorization")

    def _validate_consumption_time(self, authorization: VerifiedAuthorization, *, allow_expired: bool = False) -> None:
        self._validate_foundation_binding(authorization)
        payload = authorization.payload
        now = _utc(self.now_utc(), "consumption current time")
        issued, expires = _utc(payload["issued_at_utc"], "payload issue"), _utc(payload["expires_at_utc"], "payload expiry")
        if not allow_expired and not issued <= now < expires:
            _fail("authorization expired before durable intent")
        authority_id = authorization.envelope["authorizing_authority_id"]
        record = authorization.authority.records[authority_id]
        if record["authority_generation"] != payload["bootstrap_authority_generation"] or record["authority_generation"] < authorization.authority.value["minimum_accepted_authority_generation"]:
            _fail("authority generation is stale at consumption")
        if record["revoked_at_utc"] is not None and _utc(record["revoked_at_utc"], "authority revocation") <= now:
            _fail("authority is revoked at consumption")
        if not _utc(record["valid_from_utc"], "authority valid-from") <= now < _utc(record["valid_until_utc"], "authority valid-until"):
            _fail("authority is outside validity at consumption")

    def _validate_retry_identity(self, record: Mapping[str, Any], authorization: VerifiedAuthorization) -> None:
        expected = self._authorization_identity(authorization)
        for field, value in expected.items():
            if record.get(field) != value:
                _fail("conflicting transaction retry")
        if record["object_set_digest"] != authorization.payload["object_set_digest"]:
            _fail("conflicting transaction object set")

    def _append_transition(self, connection: sqlite3.Connection, record: Mapping[str, Any], *, observation: TerminalObservation | None = None, verification: TerminalVerification | None = None, recovery_observation: TerminalObservation | None = None, recovery_verification: TerminalVerification | None = None, first: bool = False, terminal: bool = False) -> str:
        value = _exact(record, DURABLE_FIELDS, "durable consumption record")
        digest = self._record_digest(value)
        if value["journal_head_digest"] != digest:
            _fail("durable record head is invalid")
        raw = _canonical_json_bytes(value)
        try:
            connection.execute("BEGIN IMMEDIATE")
            self._fault("DURING_TERMINAL_STATE_UPDATE" if terminal else "DURING_STATE_UPDATE")
            if first:
                connection.execute("INSERT INTO transactions VALUES(?,?,?,?,?)", (value["transaction_id"], value["nonce"], value["trust_generation"], raw, digest))
                connection.execute("INSERT INTO generation_reservations VALUES(?,?,?)", (value["trust_generation"], value["transaction_id"], "RESERVED"))
                connection.execute("UPDATE schema_metadata SET highest_seen_or_reserved_generation=MAX(highest_seen_or_reserved_generation, ?) WHERE singleton=1", (value["trust_generation"],))
            else:
                cursor = connection.execute("UPDATE transactions SET record_json=?, record_digest=? WHERE transaction_id=?", (raw, digest, value["transaction_id"]))
                if cursor.rowcount != 1:
                    _fail("transaction row is missing")
            if observation is not None:
                obs_raw = _canonical_json_bytes(observation.value)
                connection.execute("INSERT OR REPLACE INTO observations VALUES(?,?,?)", (value["transaction_id"], obs_raw, self._self_digest(observation.value, "observation_digest")))
            if verification is not None:
                ver_raw = _canonical_json_bytes(verification.value)
                connection.execute("INSERT OR REPLACE INTO verifications VALUES(?,?,?)", (value["transaction_id"], ver_raw, self._self_digest(verification.value, "verification_digest")))
            if recovery_observation is not None:
                obs_raw = _canonical_json_bytes(recovery_observation.value)
                connection.execute("INSERT OR REPLACE INTO recovery_observations VALUES(?,?,?)", (value["transaction_id"], obs_raw, self._self_digest(recovery_observation.value, "observation_digest")))
            if recovery_verification is not None:
                ver_raw = _canonical_json_bytes(recovery_verification.value)
                connection.execute("INSERT OR REPLACE INTO recovery_verifications VALUES(?,?,?)", (value["transaction_id"], ver_raw, self._self_digest(recovery_verification.value, "verification_digest")))
            self._fault("BETWEEN_TERMINAL_STATE_AND_AUDIT" if terminal else "BETWEEN_STATE_AND_AUDIT")
            next_sequence = connection.execute("SELECT COALESCE(MAX(sequence),0)+1 FROM audit").fetchone()[0]
            connection.execute("INSERT INTO audit VALUES(?,?,?,?,?)", (next_sequence, value["transaction_id"], value["state"], raw, digest))
            self._fault("AFTER_TERMINAL_AUDIT_BEFORE_COMMIT" if terminal else "AFTER_AUDIT_BEFORE_METADATA")
            connection.execute("UPDATE schema_metadata SET minimum_accepted_generation=MAX(minimum_accepted_generation, ?), journal_head_digest=? WHERE singleton=1", (value["minimum_accepted_generation"], digest))
            if terminal:
                reservation_state = "ACTIVE" if value["state"] == TrustBootstrapState.ACTIVE.value else "BURNED"
                connection.execute("UPDATE generation_reservations SET reservation_state=? WHERE trust_generation=? AND transaction_id=?", (reservation_state, value["trust_generation"], value["transaction_id"]))
                if value["state"] == TrustBootstrapState.ACTIVE.value:
                    connection.execute("UPDATE schema_metadata SET active_generation=MAX(active_generation, ?) WHERE singleton=1", (value["trust_generation"],))
            self._fault("AFTER_METADATA_BEFORE_COMMIT" if not terminal else "AFTER_TERMINAL_METADATA_BEFORE_COMMIT")
            connection.commit()
            return digest
        except sqlite3.IntegrityError as exc:
            connection.rollback()
            raise HostTrustBootstrapError("transaction nonce or generation conflicts") from exc
        except Exception:
            connection.rollback()
            raise

    @staticmethod
    def _self_digest(value: Mapping[str, Any], field: str) -> str:
        return hashlib.sha256(_canonical_json_bytes({key: item for key, item in value.items() if key != field})).hexdigest()

    def _path(self, absolute: str) -> Path:
        if absolute not in OBJECT_PATHS:
            _fail("object path is not allowlisted")
        path = self.root / absolute.lstrip("/")
        if self.root not in path.parents or _path_has_symlink(path.parent) or path.is_symlink():
            _fail("object path escapes the isolated root")
        return path

    def _capture_prior(self, connection: sqlite3.Connection, transaction_id: str) -> None:
        if connection.execute("SELECT COUNT(*) FROM prior_objects WHERE transaction_id=?", (transaction_id,)).fetchone()[0] == len(OBJECT_PATHS):
            return
        try:
            connection.execute("BEGIN IMMEDIATE")
            for index, absolute in enumerate(OBJECT_PATHS):
                path = self._path(absolute)
                if path.exists():
                    info = path.lstat()
                    if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1 or stat.S_IMODE(info.st_mode) != OBJECT_MODES[absolute] or info.st_uid != os.getuid():
                        _fail("prior object identity is not exact")
                    content = path.read_bytes()
                    connection.execute("INSERT INTO prior_objects VALUES(?,?,?,?,?,?,?,?,?,?)", (transaction_id, absolute, 1, stat.S_IMODE(info.st_mode), "CURRENT_USER", "CURRENT_GROUP", 1, hashlib.sha256(f"{info.st_dev}:{info.st_ino}".encode()).hexdigest(), content, hashlib.sha256(content).hexdigest()))
                else:
                    connection.execute("INSERT INTO prior_objects VALUES(?,?,?,?,?,?,?,?,?,?)", (transaction_id, absolute, 0, 0, "ABSENT", "ABSENT", 0, "", None, None))
                self._fault(f"DURING_PRIOR_CAPTURE_{index}")
            connection.commit()
        except Exception:
            connection.rollback()
            raise

    @staticmethod
    def _fsync_directory(directory: Path) -> None:
        fd = os.open(directory, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        try:
            os.fsync(fd)
        finally:
            os.close(fd)

    @staticmethod
    def _write_exclusive(path: Path, data: bytes, mode: int) -> None:
        if path.exists() or path.is_symlink():
            _fail("pre-existing durable file is ambiguous")
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC, mode)
        try:
            offset = 0
            while offset < len(data):
                offset += os.write(fd, data[offset:])
            os.fchmod(fd, mode)
            os.fsync(fd)
            info = os.fstat(fd)
            if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1 or stat.S_IMODE(info.st_mode) != mode or info.st_size != len(data):
                _fail("durable file identity is not exact")
        finally:
            os.close(fd)

    def _verify_staged(self, directory: Path, objects: Mapping[str, bytes]) -> dict[str, Path]:
        expected_names = {f"{index:02d}.object" for index in range(len(OBJECT_PATHS))}
        actual_names = {item.name for item in directory.iterdir()}
        if actual_names != expected_names:
            _fail("staging object set is not exact")
        result: dict[str, Path] = {}
        for index, absolute in enumerate(OBJECT_PATHS):
            target = directory / f"{index:02d}.object"
            info = target.lstat()
            if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1 or stat.S_IMODE(info.st_mode) != OBJECT_MODES[absolute]:
                _fail("staged object identity or mode is not exact")
            data = target.read_bytes()
            if data != objects[absolute] or hashlib.sha256(data).hexdigest() != hashlib.sha256(objects[absolute]).hexdigest():
                _fail("staged object bytes are not exact")
            result[absolute] = target
        if object_set_digest({path: result[path].read_bytes() for path in OBJECT_PATHS}) != object_set_digest(objects):
            _fail("staged object aggregate digest is not exact")
        return result

    def _stage(self, transaction_id: str, objects: Mapping[str, bytes]) -> dict[str, Path]:
        directory = self.root / STAGING_ROOT / transaction_id
        if _path_has_symlink(directory.parent) or directory.exists() or directory.is_symlink():
            _fail("staging path is pre-existing or ambiguous")
        directory.mkdir(parents=True, mode=0o700)
        os.chmod(directory, 0o700)
        result: dict[str, Path] = {}
        for index, absolute in enumerate(OBJECT_PATHS):
            target = directory / f"{index:02d}.object"
            self._write_exclusive(target, objects[absolute], OBJECT_MODES[absolute])
            result[absolute] = target
            self._fault(f"DURING_STAGE_{index}")
            self._fault(f"AFTER_STAGED_FILE_FSYNC_{index}")
        self._verify_staged(directory, objects)
        self._fsync_directory(directory)
        self._fault("AFTER_STAGING_DIRECTORY_FSYNC")
        return result

    def _publish_one(self, absolute: str, staged: Path) -> None:
        target = self._path(absolute)
        if target.exists():
            info = target.lstat()
            if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
                _fail("publication target identity is ambiguous")
        target.parent.mkdir(parents=True, exist_ok=True, mode=0o755)
        if _path_has_symlink(target.parent):
            _fail("publication parent is a symlink")
        temporary = target.with_name(f".{target.name}.tmp")
        if temporary.exists() or temporary.is_symlink():
            _fail("pre-existing publication temporary is ambiguous")
        data = staged.read_bytes()
        fd = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, OBJECT_MODES[absolute])
        try:
            with os.fdopen(fd, "wb") as stream:
                stream.write(data)
                stream.flush()
                os.fchmod(stream.fileno(), OBJECT_MODES[absolute])
                os.fsync(stream.fileno())
                fd = -1
            os.replace(temporary, target)
            self._fsync_directory(target.parent)
        finally:
            if fd >= 0:
                os.close(fd)
            temporary.unlink(missing_ok=True)

    def _observe(self, transaction_id: str, trust_generation: int, journal_head: str, expected_objects: Mapping[str, bytes]) -> TerminalObservation:
        self._fault("DURING_OBSERVATION")
        descriptors = []
        for absolute in OBJECT_PATHS:
            path = self._path(absolute)
            info = path.lstat()
            if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
                _fail("terminal observation found ambiguous object identity")
            data = path.read_bytes()
            descriptors.append({"path": absolute, "sha256": hashlib.sha256(data).hexdigest(), "size": info.st_size, "type": "regular", "mode": stat.S_IMODE(info.st_mode), "owner_model": "CURRENT_USER" if info.st_uid == os.getuid() else "UNEXPECTED", "group_model": "CURRENT_GROUP" if info.st_gid == os.getgid() else "UNEXPECTED", "link_count": info.st_nlink, "link_identity": hashlib.sha256(f"{info.st_dev}:{info.st_ino}".encode()).hexdigest()})
        anchor_fingerprint = hashlib.sha256(self._path(OBJECT_PATHS[0]).read_bytes()).hexdigest()
        value = {"observation_version": 1, "transaction_id": transaction_id, "trust_generation": trust_generation, "anchor_fingerprint": anchor_fingerprint, "verifier_digest": hashlib.sha256(self._path(OBJECT_PATHS[4]).read_bytes()).hexdigest(), "object_set_digest": object_set_digest({path: self._path(path).read_bytes() for path in OBJECT_PATHS}), "objects": descriptors, "journal_head_digest": journal_head, "observation_digest": ""}
        value["observation_digest"] = self._self_digest(value, "observation_digest")
        return TerminalObservation(_freeze(value))

    def _verify_observation(self, observation: TerminalObservation, authorization: VerifiedAuthorization, objects: Mapping[str, bytes], journal_head: str) -> TerminalVerification:
        self._fault("DURING_VERIFICATION")
        value = _exact(observation.value, OBSERVATION_FIELDS, "terminal observation")
        expected_digest = object_set_digest(objects)
        if value["transaction_id"] != authorization.payload["transaction_id"] or value["trust_generation"] != authorization.payload["trust_generation"] or value["object_set_digest"] != expected_digest or value["journal_head_digest"] != journal_head or value["observation_digest"] != self._self_digest(value, "observation_digest"):
            _fail("terminal observation does not match authorization")
        observed = {item["path"]: item for item in value["objects"]}
        if set(observed) != set(OBJECT_PATHS):
            _fail("terminal observation object set is not exact")
        for absolute in OBJECT_PATHS:
            item = observed[absolute]
            _exact(item, OBSERVED_OBJECT_FIELDS, "observed object")
            if item["sha256"] != hashlib.sha256(objects[absolute]).hexdigest() or item["size"] != len(objects[absolute]) or item["type"] != "regular" or item["mode"] != OBJECT_MODES[absolute] or item["owner_model"] != "CURRENT_USER" or item["group_model"] != "CURRENT_GROUP" or item["link_count"] != 1 or not _DIGEST.fullmatch(item["link_identity"]):
                _fail(f"terminal observation mismatch for {absolute}")
        result = {"verification_version": 1, "transaction_id": authorization.payload["transaction_id"], "observation_digest": value["observation_digest"], "expected_object_set_digest": expected_digest, "observed_object_set_digest": value["object_set_digest"], "verdict": "EXACT_SUCCESS", "journal_head_digest": journal_head, "verification_digest": ""}
        result["verification_digest"] = self._self_digest(result, "verification_digest")
        return TerminalVerification(_freeze(result))

    def bootstrap_from_raw(
        self,
        *,
        authority_raw: bytes,
        authority_signature: bytes | str,
        local_console_raw: bytes,
        local_console_signature: bytes | str,
        governance_raw: bytes,
        governance_signature: bytes | str,
        payload_raw: bytes,
        envelope_raw: bytes,
        objects: Mapping[str, bytes],
        allow_expired_existing: bool = False,
        verification_time_utc: str | None = None,
    ) -> BootstrapResult:
        """Reconstruct and reverify non-secret evidence before consuming it.

        This is the restart-safe boundary: no Python verification object is
        persisted or trusted across a process boundary.  An expired record can
        be reverified for an already durable transaction, but cannot create a
        new intent because ``bootstrap`` performs its consumption-time check.
        """

        verification_time = verification_time_utc or self.now_utc()
        baseline = ImageBaselineVerifier(self.context).verify(authority_raw, authority_signature)
        authority = AuthoritySetVerifier().verify(baseline)
        local = LocalConsoleEvidenceVerifier(self.context).verify(local_console_raw, local_console_signature)
        governance = GovernanceEvidenceVerifier(self.context).verify(governance_raw, governance_signature)
        authorization = self.authorization_verifier.verify(
            payload_raw,
            envelope_raw,
            authority=authority,
            local_console=local,
            governance=governance,
            target_host_identity_digest=self.target_host_identity_digest,
            target_boot_digest=self.target_boot_digest,
            now_utc=verification_time,
            allow_expired=allow_expired_existing,
        )
        return self.bootstrap(authorization, objects)

    def recover_from_raw(
        self,
        transaction_id: str,
        **evidence: Any,
    ) -> BootstrapResult:
        """Reverify supplied canonical evidence, then recover its frozen intent."""

        _identifier(transaction_id, "transaction ID")
        result = self.bootstrap_from_raw(allow_expired_existing=True, **evidence)
        if result.transaction_id != transaction_id:
            _fail("reconstructed authorization transaction does not match recovery")
        return result

    @staticmethod
    def _recovery_object_set_digest(descriptors: list[dict[str, Any]]) -> str:
        return hashlib.sha256(_canonical_json_bytes(descriptors)).hexdigest()

    def _recovery_descriptors(self) -> list[dict[str, Any]]:
        descriptors = []
        for absolute in OBJECT_PATHS:
            path = self._path(absolute)
            if not path.exists():
                descriptors.append({"path": absolute, "sha256": "", "size": 0, "type": "absent", "mode": 0, "owner_model": "ABSENT", "group_model": "ABSENT", "link_count": 0, "link_identity": ""})
                continue
            info = path.lstat()
            if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
                _fail("recovery observation found ambiguous object identity")
            data = path.read_bytes()
            descriptors.append({"path": absolute, "sha256": hashlib.sha256(data).hexdigest(), "size": len(data), "type": "regular", "mode": stat.S_IMODE(info.st_mode), "owner_model": "CURRENT_USER" if info.st_uid == os.getuid() else "UNEXPECTED", "group_model": "CURRENT_GROUP" if info.st_gid == os.getgid() else "UNEXPECTED", "link_count": info.st_nlink, "link_identity": hashlib.sha256(f"{info.st_dev}:{info.st_ino}".encode()).hexdigest()})
        return descriptors

    def _recovery_observe(self, transaction_id: str, prior_state_digest: str, journal_head: str) -> TerminalObservation:
        self._fault("DURING_RECOVERY_OBSERVATION")
        descriptors = self._recovery_descriptors()
        value = {"recovery_observation_version": 1, "transaction_id": transaction_id, "prior_state_digest": prior_state_digest, "object_set_digest": self._recovery_object_set_digest(descriptors), "objects": descriptors, "journal_head_digest": journal_head, "observation_digest": ""}
        value["observation_digest"] = self._self_digest(value, "observation_digest")
        return TerminalObservation(_freeze(value))

    def _recovery_verify(self, observation: TerminalObservation, transaction_id: str, journal_head: str, prior_rows: list[tuple[Any, ...]]) -> TerminalVerification:
        self._fault("DURING_RECOVERY_VERIFICATION")
        value = _exact(observation.value, RECOVERY_OBSERVATION_FIELDS, "recovery observation")
        actual = _jsonable(value["objects"])
        retained = {row[0]: row for row in prior_rows}
        if set(retained) != set(OBJECT_PATHS) or set(item.get("path") for item in actual) != set(OBJECT_PATHS):
            _fail("recovery object set is not exact")
        for item in actual:
            absolute = item["path"]
            _, present, mode, owner_model, group_model, link_count, link_identity, content, content_digest = retained[absolute]
            if present:
                if item["sha256"] != content_digest or item["size"] != len(content) or item["type"] != "regular" or item["mode"] != mode or item["owner_model"] != owner_model or item["group_model"] != group_model or item["link_count"] != link_count or not _DIGEST.fullmatch(item["link_identity"]):
                    _fail("recovery observation does not match retained prior generation")
            else:
                if item != {"path": absolute, "sha256": "", "size": 0, "type": "absent", "mode": 0, "owner_model": "ABSENT", "group_model": "ABSENT", "link_count": 0, "link_identity": ""}:
                    _fail("recovery observation does not match retained absent path")
        if value["transaction_id"] != transaction_id or value["journal_head_digest"] != journal_head or value["observation_digest"] != self._self_digest(value, "observation_digest"):
            _fail("recovery observation does not match retained prior generation")
        result = {"recovery_verification_version": 1, "transaction_id": transaction_id, "observation_digest": value["observation_digest"], "expected_object_set_digest": value["object_set_digest"], "observed_object_set_digest": value["object_set_digest"], "verdict": "PRIOR_GENERATION_EXACT", "journal_head_digest": journal_head, "verification_digest": ""}
        result["verification_digest"] = self._self_digest(result, "verification_digest")
        return TerminalVerification(_freeze(result))

    def bootstrap(self, authorization: VerifiedAuthorization, objects: Mapping[str, bytes]) -> BootstrapResult:
        if not isinstance(authorization, VerifiedAuthorization) or authorization.trust_domain != AUTHORIZATION_DOMAIN or authorization.authority.trust_domain != "PREEXISTING_OS_IMAGE_AUTHORITY_SET" or authorization.context is not self.context:
            _fail("verified authorization capability is required")
        self._validate_foundation_binding(authorization)
        _validate_objects(objects)
        if object_set_digest(objects) != authorization.payload["object_set_digest"]:
            _fail("object set is not authorization-bound")
        self._fault("BEFORE_INTENT")
        transaction_id = authorization.payload["transaction_id"]
        with _StateLock(self.lock_path, self.lock_timeout_seconds):
            if not self.database_path.exists():
                self._validate_consumption_time(authorization)
            connection = self._connect()
            try:
                existing = connection.execute("SELECT record_json, record_digest FROM transactions WHERE transaction_id=?", (transaction_id,)).fetchone()
                if existing is not None:
                    old = parse_canonical_json(bytes(existing[0]))
                    self._validate_retry_identity(old, authorization)
                    if old["state"] == TrustBootstrapState.ACTIVE.value:
                        self._clear_staging_exact(transaction_id)
                        return BootstrapResult(transaction_id, old["state"], old["result"], old["journal_head_digest"])
                    return self._recover_locked(connection, transaction_id)
                else:
                    self._validate_consumption_time(authorization)
                    metadata = connection.execute("SELECT minimum_accepted_generation, highest_seen_or_reserved_generation, active_generation FROM schema_metadata WHERE singleton=1").fetchone()
                    if authorization.payload["trust_generation"] <= max(metadata[0], metadata[1], metadata[2], authorization.payload["minimum_accepted_generation"] - 1):
                        _fail("trust generation is stale")
                previous = connection.execute("SELECT journal_head_digest FROM schema_metadata WHERE singleton=1").fetchone()[0]
                record = self._new_record(authorization, TrustBootstrapState.REQUESTED.value, previous)
                self._append_transition(connection, record, first=existing is None)
                self._fault("AFTER_TRUST_BOOTSTRAP_REQUESTED")
                record = self._new_record(authorization, TrustBootstrapState.VALIDATED.value, record["journal_head_digest"])
                self._append_transition(connection, record)
                self._fault("AFTER_TRUST_BOOTSTRAP_VALIDATED")
                self._capture_prior(connection, transaction_id)
                record = self._new_record(authorization, TrustBootstrapState.PRIOR_GENERATION_RETAINED.value, record["journal_head_digest"])
                self._append_transition(connection, record)
                self._fault("AFTER_PRIOR_GENERATION_RETAINED")
                staged = self._stage(transaction_id, objects)
                record = self._new_record(authorization, TrustBootstrapState.NEXT_GENERATION_STAGED.value, record["journal_head_digest"])
                self._append_transition(connection, record)
                self._fault("AFTER_NEXT_GENERATION_STAGED")
                self._fault("BEFORE_PUBLISHING")
                record = self._new_record(authorization, TrustBootstrapState.PUBLISHING.value, record["journal_head_digest"])
                self._append_transition(connection, record)
                for index, absolute in enumerate(PUBLICATION_ORDER):
                    self._fault(f"BEFORE_PUBLISH_{index}")
                    self._publish_one(absolute, staged[absolute])
                    self._fault(f"AFTER_PUBLISH_{index}")
                    if index == 0:
                        self._fault("BETWEEN_USR_LIBEXEC_AND_ETC_PUBLICATION")
                self._fault("AFTER_ALL_WRITES")
                record = self._new_record(authorization, TrustBootstrapState.VERIFYING.value, record["journal_head_digest"])
                self._append_transition(connection, record)
                self._fault("BEFORE_VERIFYING")
                observation = self._observe(transaction_id, authorization.payload["trust_generation"], record["journal_head_digest"], objects)
                verification = self._verify_observation(observation, authorization, objects, record["journal_head_digest"])
                self._fault("AFTER_SUCCESSFUL_VERIFICATION_BEFORE_TERMINAL_COMMIT")
                final = self._new_record(authorization, TrustBootstrapState.ACTIVE.value, record["journal_head_digest"], result="TRUST_SET_ACTIVE", consumed=self.now_utc())
                self._append_transition(connection, final, observation=observation, verification=verification, terminal=True)
                self._fault("AFTER_TERMINAL_COMMIT")
                shutil.rmtree(self.root / STAGING_ROOT / transaction_id, ignore_errors=True)
                return BootstrapResult(transaction_id, final["state"], final["result"], final["journal_head_digest"])
            finally:
                connection.close()

    def _recovery_failure_evidence(self, transaction_id: str, prior_state_digest: str, journal_head: str) -> tuple[TerminalObservation, TerminalVerification]:
        try:
            descriptors = self._recovery_descriptors()
        except HostTrustBootstrapError:
            descriptors = []
        value = {"recovery_observation_version": 1, "transaction_id": transaction_id, "prior_state_digest": prior_state_digest, "object_set_digest": self._recovery_object_set_digest(descriptors), "objects": descriptors, "journal_head_digest": journal_head, "observation_digest": ""}
        value["observation_digest"] = self._self_digest(value, "observation_digest")
        observation = TerminalObservation(_freeze(value))
        result = {"recovery_verification_version": 1, "transaction_id": transaction_id, "observation_digest": value["observation_digest"], "expected_object_set_digest": "", "observed_object_set_digest": value["object_set_digest"], "verdict": "RESTORE_VERIFICATION_FAILED", "journal_head_digest": journal_head, "verification_digest": ""}
        result["verification_digest"] = self._self_digest(result, "verification_digest")
        return observation, TerminalVerification(_freeze(result))

    def _recover_locked(self, connection: sqlite3.Connection, transaction_id: str) -> BootstrapResult:
        row = connection.execute("SELECT record_json FROM transactions WHERE transaction_id=?", (transaction_id,)).fetchone()
        if row is None:
            _fail("unknown recovery transaction")
        record = parse_canonical_json(bytes(row[0]))
        if record["verification_context_digest"] != self.context.binding_digest:
            _fail("recovery verification context is not exact")
        if record["state"] == TrustBootstrapState.ACTIVE.value or record["state"] == TrustBootstrapState.REVIEW_REQUIRED.value:
            self._clear_staging_exact(transaction_id)
            return BootstrapResult(transaction_id, record["state"], record["result"], record["journal_head_digest"])
        previous = connection.execute("SELECT journal_head_digest FROM schema_metadata WHERE singleton=1").fetchone()[0]
        restoring = dict(record)
        restoring.update({"state": TrustBootstrapState.RESTORING.value, "previous_record_digest": previous, "result": "IN_PROGRESS", "failure_class": "RECOVERY"})
        restoring["journal_head_digest"] = self._record_digest(restoring)
        restoring_digest = self._append_transition(connection, restoring)
        try:
            prior_rows = self._restore_prior(connection, transaction_id)
            observation = self._recovery_observe(transaction_id, record["journal_head_digest"], restoring_digest)
            verification = self._recovery_verify(observation, transaction_id, restoring_digest, prior_rows)
        except Exception as exc:
            observation, verification = self._recovery_failure_evidence(transaction_id, record["journal_head_digest"], restoring_digest)
            review = dict(restoring)
            review.update({"state": TrustBootstrapState.REVIEW_REQUIRED.value, "previous_record_digest": restoring_digest, "result": "ROOT_REVIEW_REQUIRED", "failure_class": type(exc).__name__[:64]})
            review["journal_head_digest"] = self._record_digest(review)
            self._append_transition(connection, review, recovery_observation=observation, recovery_verification=verification, terminal=True)
            self._clear_staging_exact(transaction_id)
            return BootstrapResult(transaction_id, review["state"], review["result"], review["journal_head_digest"])
        final = dict(restoring)
        final.update({"state": TrustBootstrapState.REVIEW_REQUIRED.value, "previous_record_digest": restoring_digest, "result": "PRIOR_GENERATION_RESTORED_REVIEW_REQUIRED", "failure_class": "RESTORED_PRIOR_REQUIRES_REVIEW"})
        final["journal_head_digest"] = self._record_digest(final)
        self._append_transition(connection, final, recovery_observation=observation, recovery_verification=verification, terminal=True)
        self._fault("AFTER_TERMINAL_COMMIT")
        return BootstrapResult(transaction_id, final["state"], final["result"], final["journal_head_digest"])

    def recover(self, transaction_id: str) -> BootstrapResult:
        _identifier(transaction_id, "transaction ID")
        with _StateLock(self.lock_path, self.lock_timeout_seconds):
            connection = self._connect()
            try:
                return self._recover_locked(connection, transaction_id)
            finally:
                connection.close()

    def _clear_staging_exact(self, transaction_id: str) -> None:
        directory = self.root / STAGING_ROOT / transaction_id
        if directory.is_symlink():
            _fail("staging directory is ambiguous during cleanup")
        if not directory.exists():
            return
        if _path_has_symlink(directory.parent):
            _fail("staging directory is ambiguous during cleanup")
        allowed_names = {f"{index:02d}.object" for index in range(len(OBJECT_PATHS))} | {f"restore-{index:02d}" for index in range(len(OBJECT_PATHS))}
        for child in directory.iterdir():
            if child.name not in allowed_names:
                _fail("unexpected staging entry is ambiguous during cleanup")
            info = child.lstat()
            if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1 or child.is_symlink():
                _fail("staging entry is ambiguous during cleanup")
            child.unlink()
        directory.rmdir()
        self._fsync_directory(directory.parent)

    def _restore_prior(self, connection: sqlite3.Connection, transaction_id: str) -> list[tuple[Any, ...]]:
        rows = connection.execute("SELECT path, present, mode, owner_model, group_model, link_count, link_identity, content, content_digest FROM prior_objects WHERE transaction_id=? ORDER BY path", (transaction_id,)).fetchall()
        if len(rows) != len(OBJECT_PATHS):
            _fail("retained prior generation is incomplete")
        for index, (absolute, present, mode, owner_model, group_model, link_count, link_identity, content, content_digest) in enumerate(reversed(rows)):
            path = self._path(absolute)
            if present:
                if owner_model != "CURRENT_USER" or group_model != "CURRENT_GROUP" or link_count != 1 or not _DIGEST.fullmatch(link_identity) or not isinstance(content, bytes) or content_digest != hashlib.sha256(content).hexdigest() or mode != OBJECT_MODES[absolute]:
                    _fail("retained prior metadata or bytes are tampered")
                staging = self.root / STAGING_ROOT / transaction_id / f"restore-{OBJECT_PATHS.index(absolute):02d}"
                if _path_has_symlink(staging.parent):
                    _fail("recovery staging parent is a symlink")
                staging.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
                os.chmod(staging.parent, 0o700)
                self._write_exclusive(staging, content, mode)
                self._publish_one(absolute, staging)
                staging.unlink(missing_ok=True)
            else:
                path.parent.mkdir(parents=True, exist_ok=True, mode=0o755)
                if path.is_symlink() or (path.exists() and (not path.is_file() or path.lstat().st_nlink != 1)):
                    _fail("partial restoration target is ambiguous")
                path.unlink(missing_ok=True)
                self._fsync_directory(path.parent)
            self._fault(f"DURING_RESTORE_{index}")
        self._clear_staging_exact(transaction_id)
        return rows


@dataclass(frozen=True, slots=True)
class BootstrapResult:
    transaction_id: str
    state: str
    result: str
    journal_head_digest: str
