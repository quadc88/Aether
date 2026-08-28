"""Bounded durable OAS security-state kernel.

This module owns only the durable security-state foundation. It deliberately
does not authenticate a human, issue credentials, mint source events, or expose
an API. Every canonical mutation is performed by the kernel's SQLite
transaction and its canonical audit event is committed in the same transaction.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
import copy
import hashlib
import json
from pathlib import Path
import re
import sqlite3
import time
from types import MappingProxyType
from typing import Any, Callable, Mapping

SCHEMA_VERSION = 1
SCHEMA_NAME = "oas_security_kernel"
REQUEST_DIGEST_DOMAIN = "aether.oas.security-kernel.request"
REQUEST_DIGEST_VERSION = 1
AUDIT_EVIDENCE_DOMAIN = "aether.oas.security-kernel.audit-evidence"
AUDIT_EVIDENCE_VERSION = 1
COMMITTED_RESULT_CLASSIFICATION = "NON_SECRET_CANONICAL_JSON"
MAX_JSON_DEPTH = 16
MAX_JSON_ENCODED_BYTES = 16 * 1024
MAX_JSON_COLLECTION_ITEMS = 128
MAX_JSON_KEY_BYTES = 128
MAX_JSON_STRING_BYTES = 4096
MAX_JSON_INTEGER_DIGITS = 128
_SQLITE_BUSY_TIMEOUT_MS = 10_000
_WAL_INIT_MAX_RETRY_SECONDS = 2.0
_WAL_INIT_BACKOFF_INITIAL_SECONDS = 0.005
_WAL_INIT_BACKOFF_MAX_SECONDS = 0.05
_HEX64 = re.compile(r"^[0-9a-f]{64}$")
_IDENTITY = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}$")
_OPERATION = re.compile(r"^[a-z][a-z0-9_]{0,63}$")
_SECRET_FIELD_WORDS = (
    "secret",
    "password",
    "credential",
    "passkey",
    "token",
    "assertion",
    "session",
    "signing",
    "private_key",
    "recovery_material",
)


class SecurityKernelError(Exception):
    """Base error for bounded OAS security-kernel operations."""


class SchemaVersionError(SecurityKernelError):
    """Raised when the store schema is unsupported or newer than this code."""


class CorruptSchemaError(SecurityKernelError):
    """Raised when an existing store is incomplete or malformed."""


class DatabaseUnavailableError(SecurityKernelError):
    """Raised when bounded SQLite contention prevents store availability."""


class SecurityKernelIntegrityError(SecurityKernelError):
    """Raised when committed security evidence is inconsistent or tampered."""


class InvalidTransactionError(SecurityKernelError):
    """Raised when a security transaction request is malformed."""


class ReplayConflictError(SecurityKernelError):
    """Raised when a transaction or idempotency identity is reused differently."""


class StaleGenerationError(SecurityKernelError):
    """Raised when a request is bound to an old trust generation."""


class LifecycleTransitionError(SecurityKernelError):
    """Raised when a lifecycle mutation is not an allowed bounded transition."""


class OwnerLifecycleState(str, Enum):
    UNCLAIMED = "UNCLAIMED"
    CLAIM_PENDING = "CLAIM_PENDING"
    OWNED = "OWNED"
    RECOVERY_PENDING = "RECOVERY_PENDING"


class _TransactionStatus(str, Enum):
    COMMITTED = "COMMITTED"


@dataclass(frozen=True, slots=True)
class AetherInstanceTrust:
    aether_instance_id: str
    lifecycle_state: OwnerLifecycleState
    trust_generation: int
    created_at: str
    updated_at: str
    schema_version: int
    active: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "aether_instance_id": self.aether_instance_id,
            "lifecycle_state": self.lifecycle_state.value,
            "trust_generation": self.trust_generation,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "schema_version": self.schema_version,
            "active": self.active,
        }


@dataclass(frozen=True, slots=True)
class OwnerSecurityTransaction:
    transaction_id: str
    aether_instance_id: str
    expected_trust_generation: int
    resulting_trust_generation: int
    exact_operation: str
    canonical_request_digest: str
    idempotency_key: str
    transaction_status: str
    committed_result: Mapping[str, Any]
    result_digest: str
    conflict_classification: str | None
    created_at: str
    committed_at: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "transaction_id": self.transaction_id,
            "aether_instance_id": self.aether_instance_id,
            "expected_trust_generation": self.expected_trust_generation,
            "resulting_trust_generation": self.resulting_trust_generation,
            "exact_operation": self.exact_operation,
            "canonical_request_digest": self.canonical_request_digest,
            "idempotency_key": self.idempotency_key,
            "transaction_status": self.transaction_status,
            "committed_result": copy.deepcopy(dict(self.committed_result)),
            "result_digest": self.result_digest,
            "conflict_classification": self.conflict_classification,
            "created_at": self.created_at,
            "committed_at": self.committed_at,
        }


@dataclass(frozen=True, slots=True)
class OwnerSecurityAuditEvent:
    audit_event_id: str
    transaction_id: str
    aether_instance_id: str
    trust_generation: int
    event_kind: str
    affected_canonical_state_reference: str
    non_secret_evidence_digest: str
    committed_result_classification: str
    result: str
    timestamp: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "audit_event_id": self.audit_event_id,
            "transaction_id": self.transaction_id,
            "aether_instance_id": self.aether_instance_id,
            "trust_generation": self.trust_generation,
            "event_kind": self.event_kind,
            "affected_canonical_state_reference": self.affected_canonical_state_reference,
            "non_secret_evidence_digest": self.non_secret_evidence_digest,
            "committed_result_classification": self.committed_result_classification,
            "result": self.result,
            "timestamp": self.timestamp,
        }


@dataclass(frozen=True, slots=True)
class SecurityTransactionRequest:
    transaction_id: str
    aether_instance_id: str
    expected_trust_generation: int
    exact_operation: str
    idempotency_key: str
    payload: Mapping[str, Any]
    request_digest: str

    def __post_init__(self) -> None:
        _validate_identity(self.transaction_id, "transaction_id")
        _validate_identity(self.aether_instance_id, "aether_instance_id")
        _validate_identity(self.idempotency_key, "idempotency_key")
        if (
            not isinstance(self.expected_trust_generation, int)
            or isinstance(self.expected_trust_generation, bool)
            or self.expected_trust_generation < 0
        ):
            raise InvalidTransactionError(
                "expected_trust_generation must be a non-negative integer"
            )
        if not isinstance(self.exact_operation, str) or not _OPERATION.fullmatch(
            self.exact_operation
        ):
            raise InvalidTransactionError("exact_operation is invalid")
        if not isinstance(self.payload, Mapping):
            raise InvalidTransactionError("payload must be a mapping")
        payload = copy.deepcopy(dict(self.payload))
        _canonical_json(payload, reject_secret_fields=True)
        if not isinstance(self.request_digest, str) or not _HEX64.fullmatch(
            self.request_digest
        ):
            raise InvalidTransactionError("request_digest must be lowercase SHA-256")
        object.__setattr__(self, "payload", MappingProxyType(payload))

    @classmethod
    def build(
        cls,
        *,
        transaction_id: str,
        aether_instance_id: str,
        expected_trust_generation: int,
        exact_operation: str,
        idempotency_key: str,
        payload: Mapping[str, Any],
    ) -> "SecurityTransactionRequest":
        digest = canonical_request_digest(
            transaction_id=transaction_id,
            aether_instance_id=aether_instance_id,
            expected_trust_generation=expected_trust_generation,
            exact_operation=exact_operation,
            idempotency_key=idempotency_key,
            payload=payload,
        )
        return cls(
            transaction_id=transaction_id,
            aether_instance_id=aether_instance_id,
            expected_trust_generation=expected_trust_generation,
            exact_operation=exact_operation,
            idempotency_key=idempotency_key,
            payload=payload,
            request_digest=digest,
        )


FIELD_CLASSIFICATION: Mapping[str, Mapping[str, str]] = MappingProxyType(
    {
        "aether_instance_id": {
            "owner": "OAS",
            "validation": "bounded identity string",
            "serialization": "SQLite TEXT",
            "migration": "preserve exactly",
            "retention": "durable security state",
            "secret": "NO",
        },
        "lifecycle_state": {
            "owner": "OAS",
            "validation": "OwnerLifecycleState vocabulary",
            "serialization": "uppercase TEXT",
            "migration": "preserve exact state",
            "retention": "durable security state",
            "secret": "NO",
        },
        "trust_generation": {
            "owner": "OAS",
            "validation": "positive integer",
            "serialization": "SQLite INTEGER",
            "migration": "preserve monotonic value",
            "retention": "durable security state",
            "secret": "NO",
        },
        "created_at": {
            "owner": "OAS",
            "validation": "UTC ISO-8601 text",
            "serialization": "SQLite TEXT",
            "migration": "preserve exact timestamp",
            "retention": "durable state or security history",
            "secret": "NO",
        },
        "updated_at": {
            "owner": "OAS",
            "validation": "UTC ISO-8601 text",
            "serialization": "SQLite TEXT",
            "migration": "preserve exact timestamp",
            "retention": "durable state",
            "secret": "NO",
        },
        "schema_version": {
            "owner": "OAS",
            "validation": "supported positive integer",
            "serialization": "SQLite INTEGER",
            "migration": "deterministic schema migration marker",
            "retention": "durable schema metadata",
            "secret": "NO",
        },
        "active": {
            "owner": "OAS",
            "validation": "single active marker",
            "serialization": "SQLite INTEGER 0 or 1",
            "migration": "preserve exactly",
            "retention": "durable security state",
            "secret": "NO",
        },
        "transaction_id": {
            "owner": "OAS",
            "validation": "bounded identity string, unique",
            "serialization": "SQLite TEXT",
            "migration": "preserve exactly",
            "retention": "security transaction history",
            "secret": "NO",
        },
        "expected_trust_generation": {
            "owner": "OAS",
            "validation": "non-negative integer",
            "serialization": "SQLite INTEGER",
            "migration": "preserve exactly",
            "retention": "security transaction history",
            "secret": "NO",
        },
        "resulting_trust_generation": {
            "owner": "OAS",
            "validation": "positive integer",
            "serialization": "SQLite INTEGER",
            "migration": "preserve exactly",
            "retention": "security transaction history",
            "secret": "NO",
        },
        "exact_operation": {
            "owner": "OAS",
            "validation": "bounded operation vocabulary",
            "serialization": "SQLite TEXT",
            "migration": "preserve exactly",
            "retention": "security transaction history",
            "secret": "NO",
        },
        "canonical_request_digest": {
            "owner": "OAS",
            "validation": "lowercase SHA-256",
            "serialization": "SQLite TEXT",
            "migration": "preserve exactly",
            "retention": "security transaction history",
            "secret": "NO",
        },
        "idempotency_key": {
            "owner": "OAS",
            "validation": "bounded identity string, unique per instance",
            "serialization": "SQLite TEXT",
            "migration": "preserve exactly",
            "retention": "security transaction history",
            "secret": "NO",
        },
        "transaction_status": {
            "owner": "OAS",
            "validation": "COMMITTED only in v1",
            "serialization": "SQLite TEXT",
            "migration": "preserve exact status",
            "retention": "security transaction history",
            "secret": "NO",
        },
        "committed_result": {
            "owner": "OAS",
            "validation": "bounded non-secret JSON result",
            "serialization": "canonical JSON TEXT",
            "migration": "preserve exact JSON",
            "retention": "security transaction history",
            "secret": "NO",
        },
        "result_digest": {
            "owner": "OAS",
            "validation": "lowercase SHA-256",
            "serialization": "SQLite TEXT",
            "migration": "preserve exactly",
            "retention": "security transaction history",
            "secret": "NO",
        },
        "conflict_classification": {
            "owner": "OAS",
            "validation": "bounded nullable classification",
            "serialization": "SQLite TEXT or NULL",
            "migration": "preserve exactly",
            "retention": "security transaction history",
            "secret": "NO",
        },
        "committed_at": {
            "owner": "OAS",
            "validation": "UTC ISO-8601 text",
            "serialization": "SQLite TEXT",
            "migration": "preserve exact timestamp",
            "retention": "security transaction history",
            "secret": "NO",
        },
        "audit_event_id": {
            "owner": "OAS",
            "validation": "bounded identity string, unique",
            "serialization": "SQLite TEXT",
            "migration": "preserve exactly",
            "retention": "canonical audit history",
            "secret": "NO",
        },
        "event_kind": {
            "owner": "OAS",
            "validation": "bounded event vocabulary",
            "serialization": "SQLite TEXT",
            "migration": "preserve exactly",
            "retention": "canonical audit history",
            "secret": "NO",
        },
        "affected_canonical_state_reference": {
            "owner": "OAS",
            "validation": "bounded state reference",
            "serialization": "SQLite TEXT",
            "migration": "preserve exactly",
            "retention": "canonical audit history",
            "secret": "NO",
        },
        "non_secret_evidence_digest": {
            "owner": "OAS",
            "validation": "lowercase SHA-256",
            "serialization": "SQLite TEXT",
            "migration": "preserve exactly",
            "retention": "canonical audit history",
            "secret": "NO",
        },
        "committed_result_classification": {
            "owner": "OAS",
            "validation": "NON_SECRET_CANONICAL_JSON",
            "serialization": "SQLite TEXT",
            "migration": "preserve exact classification",
            "retention": "canonical audit history",
            "secret": "NO",
        },
        "result": {
            "owner": "OAS",
            "validation": "COMMITTED result marker",
            "serialization": "SQLite TEXT",
            "migration": "preserve exact result",
            "retention": "canonical audit history",
            "secret": "NO",
        },
        "timestamp": {
            "owner": "OAS",
            "validation": "UTC ISO-8601 text",
            "serialization": "SQLite TEXT",
            "migration": "preserve exact timestamp",
            "retention": "canonical audit history",
            "secret": "NO",
        },
    }
)


_ALLOWED_TRANSITIONS = {
    (OwnerLifecycleState.UNCLAIMED, OwnerLifecycleState.CLAIM_PENDING),
    (OwnerLifecycleState.CLAIM_PENDING, OwnerLifecycleState.OWNED),
    (OwnerLifecycleState.CLAIM_PENDING, OwnerLifecycleState.UNCLAIMED),
    (OwnerLifecycleState.OWNED, OwnerLifecycleState.RECOVERY_PENDING),
    (OwnerLifecycleState.RECOVERY_PENDING, OwnerLifecycleState.OWNED),
}

_EVENT_KIND_BY_OPERATION = {
    "initialize_instance": "INSTANCE_INITIALIZED",
    "transition_lifecycle": "LIFECYCLE_TRANSITION",
    "rotate_trust_generation": "TRUST_GENERATION_ROTATED",
}


def _validate_identity(value: Any, name: str) -> None:
    if not isinstance(value, str) or not _IDENTITY.fullmatch(value):
        raise InvalidTransactionError(f"{name} must be a bounded identity string")


def _validate_secret_key(key: Any) -> None:
    if not isinstance(key, str):
        raise InvalidTransactionError("JSON object keys must be strings")
    folded = key.casefold()
    if any(word in folded for word in _SECRET_FIELD_WORDS):
        raise InvalidTransactionError(f"secret-bearing field is not allowed: {key}")


def _canonical_json(value: Any, *, reject_secret_fields: bool = False) -> str:
    def validate(item: Any, depth: int = 0) -> None:
        if isinstance(item, Mapping):
            if depth >= MAX_JSON_DEPTH:
                raise InvalidTransactionError("JSON maximum depth exceeded")
            if len(item) > MAX_JSON_COLLECTION_ITEMS:
                raise InvalidTransactionError("JSON maximum collection size exceeded")
            for key, child in item.items():
                if not isinstance(key, str):
                    raise InvalidTransactionError("JSON object keys must be strings")
                if len(key.encode("utf-8")) > MAX_JSON_KEY_BYTES:
                    raise InvalidTransactionError("JSON key exceeds maximum size")
                if reject_secret_fields:
                    _validate_secret_key(key)
                validate(child, depth + 1)
        elif isinstance(item, (list, tuple)):
            if depth >= MAX_JSON_DEPTH:
                raise InvalidTransactionError("JSON maximum depth exceeded")
            if len(item) > MAX_JSON_COLLECTION_ITEMS:
                raise InvalidTransactionError("JSON maximum collection size exceeded")
            for child in item:
                validate(child, depth + 1)
        elif isinstance(item, str):
            if len(item.encode("utf-8")) > MAX_JSON_STRING_BYTES:
                raise InvalidTransactionError("JSON string exceeds maximum size")
        elif item is None or isinstance(item, bool):
            return
        elif isinstance(item, int):
            try:
                integer_digits = len(str(abs(item)))
            except ValueError as exc:
                raise InvalidTransactionError(
                    "JSON integer representation is too large"
                ) from exc
            if integer_digits > MAX_JSON_INTEGER_DIGITS:
                raise InvalidTransactionError(
                    "JSON integer representation exceeds maximum size"
                )
        elif isinstance(item, float):
            if item != item or item in (float("inf"), float("-inf")):
                raise InvalidTransactionError("non-finite numbers are not allowed")
        else:
            raise InvalidTransactionError("value is not supported JSON data")

    validate(value)
    try:
        encoded = json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            allow_nan=False,
        )
    except (TypeError, ValueError, OverflowError) as exc:
        raise InvalidTransactionError("value is not canonical JSON") from exc
    if len(encoded.encode("utf-8")) > MAX_JSON_ENCODED_BYTES:
        raise InvalidTransactionError("JSON encoded size exceeds maximum size")
    return encoded


def canonical_request_digest(
    *,
    transaction_id: str,
    aether_instance_id: str,
    expected_trust_generation: int,
    exact_operation: str,
    idempotency_key: str,
    payload: Mapping[str, Any],
) -> str:
    material = {
        "domain": REQUEST_DIGEST_DOMAIN,
        "digest_contract_version": REQUEST_DIGEST_VERSION,
        "transaction_id": transaction_id,
        "idempotency_key": idempotency_key,
        "aether_instance_id": aether_instance_id,
        "expected_trust_generation": expected_trust_generation,
        "exact_operation": exact_operation,
        "payload": dict(payload),
    }
    encoded = _canonical_json(material, reject_secret_fields=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _result_digest(result: Mapping[str, Any]) -> str:
    return hashlib.sha256(
        _canonical_json(result, reject_secret_fields=True).encode("utf-8")
    ).hexdigest()


def canonical_audit_evidence_digest(
    *,
    audit_event_id: str,
    transaction_id: str,
    aether_instance_id: str,
    expected_trust_generation: int,
    resulting_trust_generation: int,
    exact_operation: str,
    canonical_request_digest_value: str,
    idempotency_key: str,
    committed_result_digest: str,
    event_kind: str,
    affected_canonical_state_reference: str,
    committed_result_classification: str,
    result: str,
    timestamp: str,
) -> str:
    material = {
        "domain": AUDIT_EVIDENCE_DOMAIN,
        "evidence_contract_version": AUDIT_EVIDENCE_VERSION,
        "audit_event_id": audit_event_id,
        "transaction_id": transaction_id,
        "aether_instance_id": aether_instance_id,
        "expected_trust_generation": expected_trust_generation,
        "resulting_trust_generation": resulting_trust_generation,
        "exact_operation": exact_operation,
        "canonical_request_digest": canonical_request_digest_value,
        "idempotency_key": idempotency_key,
        "committed_result_digest": committed_result_digest,
        "event_kind": event_kind,
        "affected_canonical_state_reference": affected_canonical_state_reference,
        "committed_result_classification": committed_result_classification,
        "result": result,
        "timestamp": timestamp,
    }
    encoded = _canonical_json(material, reject_secret_fields=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _audit_event_id(transaction_id: str) -> str:
    return "audit_" + hashlib.sha256(transaction_id.encode("utf-8")).hexdigest()


def _is_transient_sqlite_contention(exc: sqlite3.DatabaseError) -> bool:
    """Recognize SQLite primary BUSY/LOCKED result codes only."""

    code = getattr(exc, "sqlite_errorcode", None)
    if not isinstance(code, int):
        return False
    return (code & 0xFF) in {sqlite3.SQLITE_BUSY, sqlite3.SQLITE_LOCKED}


def _close_failed_connection(connection: sqlite3.Connection | None) -> None:
    if connection is None:
        return
    try:
        connection.close()
    except Exception:
        # Preserve the setup failure; cleanup must not mask its cause.
        pass


class SecurityKernel:
    """Explicitly bounded durable store for OAS security-state foundation."""

    def __init__(
        self,
        store_path: str | Path,
        *,
        fault_injector: Callable[[str], None] | None = None,
    ) -> None:
        if not isinstance(store_path, (str, Path)) or not str(store_path):
            raise TypeError("store_path must be explicitly supplied")
        self.store_path = Path(store_path)
        self.fault_injector = fault_injector
        self.migrate()

    def _connect(self) -> sqlite3.Connection:
        self.store_path.parent.mkdir(parents=True, exist_ok=True)
        deadline = time.monotonic() + _WAL_INIT_MAX_RETRY_SECONDS
        backoff = _WAL_INIT_BACKOFF_INITIAL_SECONDS
        while True:
            connection: sqlite3.Connection | None = None
            try:
                connection = sqlite3.connect(
                    self.store_path,
                    timeout=10.0,
                    isolation_level=None,
                    check_same_thread=False,
                )
                connection.row_factory = sqlite3.Row
                connection.execute("PRAGMA foreign_keys = ON")

                # Keep mode discovery and first-time WAL negotiation inside the
                # same bounded contention window, then restore the normal
                # connection busy timeout before returning the connection.
                remaining_ms = max(0, int((deadline - time.monotonic()) * 1000))
                connection.execute(f"PRAGMA busy_timeout = {remaining_ms}")
                journal_mode_row = connection.execute(
                    "PRAGMA journal_mode"
                ).fetchone()
                if journal_mode_row is None or not isinstance(journal_mode_row[0], str):
                    raise CorruptSchemaError("SQLite journal mode is invalid")
                if journal_mode_row[0].upper() != "WAL":
                    remaining_ms = max(0, int((deadline - time.monotonic()) * 1000))
                    connection.execute(f"PRAGMA busy_timeout = {remaining_ms}")
                    connection.execute("PRAGMA journal_mode = WAL")

                effective_mode_row = connection.execute(
                    "PRAGMA journal_mode"
                ).fetchone()
                if (
                    effective_mode_row is None
                    or not isinstance(effective_mode_row[0], str)
                    or effective_mode_row[0].upper() != "WAL"
                ):
                    raise DatabaseUnavailableError(
                        "SQLite WAL mode could not be established"
                    )
                connection.execute(f"PRAGMA busy_timeout = {_SQLITE_BUSY_TIMEOUT_MS}")
                connection.execute("PRAGMA synchronous = FULL")

                foreign_keys = connection.execute("PRAGMA foreign_keys").fetchone()
                synchronous = connection.execute("PRAGMA synchronous").fetchone()
                if foreign_keys is None or int(foreign_keys[0]) != 1:
                    raise CorruptSchemaError("SQLite foreign-key enforcement is disabled")
                if synchronous is None or int(synchronous[0]) != 2:
                    raise CorruptSchemaError("SQLite synchronous mode is not FULL")
                return connection
            except sqlite3.DatabaseError as exc:
                _close_failed_connection(connection)
                connection = None
                if not _is_transient_sqlite_contention(exc):
                    raise CorruptSchemaError(
                        "security-kernel store is not valid SQLite"
                    ) from exc
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    raise DatabaseUnavailableError(
                        "SQLite WAL initialization contention deadline exhausted"
                    ) from exc
                time.sleep(min(backoff, remaining))
                backoff = min(backoff * 2, _WAL_INIT_BACKOFF_MAX_SECONDS)
            except Exception:
                _close_failed_connection(connection)
                raise

    @staticmethod
    def _table_names(connection: sqlite3.Connection) -> set[str]:
        rows = connection.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table'"
        ).fetchall()
        return {str(row[0]) for row in rows}

    @staticmethod
    def _table_info(
        connection: sqlite3.Connection, table: str
    ) -> tuple[tuple[str, str, int, int, int | None], ...]:
        return tuple(
            (
                str(row[1]),
                str(row[2]).upper(),
                int(row[3]),
                int(row[5]),
                row[4],
            )
            for row in connection.execute(f'PRAGMA table_info("{table}")').fetchall()
        )

    @staticmethod
    def _index_signatures(
        connection: sqlite3.Connection, table: str
    ) -> list[tuple[tuple[str, ...], bool, bool]]:
        signatures = []
        for row in connection.execute(f'PRAGMA index_list("{table}")').fetchall():
            name = str(row[1])
            columns = tuple(
                str(info[2])
                for info in connection.execute(f'PRAGMA index_info("{name}")').fetchall()
            )
            signatures.append((columns, bool(row[2]), bool(row[4])))
        return signatures

    @staticmethod
    def _foreign_key_signatures(
        connection: sqlite3.Connection, table: str
    ) -> set[tuple[str, str, str]]:
        return {
            (str(row[2]), str(row[3]), str(row[4]))
            for row in connection.execute(f'PRAGMA foreign_key_list("{table}")').fetchall()
        }

    def _create_schema(self, connection: sqlite3.Connection) -> None:
        statements = (
            """
            CREATE TABLE schema_metadata (
                schema_name TEXT PRIMARY KEY,
                schema_version INTEGER NOT NULL CHECK(schema_version > 0)
            )
            """,
            """
            CREATE TABLE aether_instance_trust (
                aether_instance_id TEXT PRIMARY KEY,
                lifecycle_state TEXT NOT NULL,
                trust_generation INTEGER NOT NULL CHECK(trust_generation > 0),
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                schema_version INTEGER NOT NULL,
                active INTEGER NOT NULL CHECK(active IN (0, 1))
            )
            """,
            """
            CREATE UNIQUE INDEX one_active_aether_instance
            ON aether_instance_trust(active) WHERE active = 1
            """,
            """
            CREATE TABLE owner_security_transactions (
                transaction_id TEXT PRIMARY KEY,
                aether_instance_id TEXT NOT NULL REFERENCES aether_instance_trust(aether_instance_id),
                expected_trust_generation INTEGER NOT NULL CHECK(expected_trust_generation >= 0),
                resulting_trust_generation INTEGER NOT NULL CHECK(resulting_trust_generation > 0),
                exact_operation TEXT NOT NULL,
                canonical_request_digest TEXT NOT NULL,
                idempotency_key TEXT NOT NULL,
                transaction_status TEXT NOT NULL CHECK(transaction_status = 'COMMITTED'),
                committed_result TEXT NOT NULL,
                result_digest TEXT NOT NULL,
                conflict_classification TEXT,
                created_at TEXT NOT NULL,
                committed_at TEXT NOT NULL,
                UNIQUE(aether_instance_id, idempotency_key)
            )
            """,
            """
            CREATE TABLE owner_security_audit_events (
                audit_event_id TEXT PRIMARY KEY,
                transaction_id TEXT NOT NULL UNIQUE REFERENCES owner_security_transactions(transaction_id),
                aether_instance_id TEXT NOT NULL REFERENCES aether_instance_trust(aether_instance_id),
                    trust_generation INTEGER NOT NULL CHECK(trust_generation > 0),
                    event_kind TEXT NOT NULL,
                    affected_canonical_state_reference TEXT NOT NULL,
                    non_secret_evidence_digest TEXT NOT NULL,
                    committed_result_classification TEXT NOT NULL
                        CHECK(committed_result_classification = 'NON_SECRET_CANONICAL_JSON'),
                    result TEXT NOT NULL CHECK(result = 'COMMITTED'),
                timestamp TEXT NOT NULL
            )
            """,
        )
        for statement in statements:
            connection.execute(statement)
        connection.execute(
            "INSERT INTO schema_metadata(schema_name, schema_version) VALUES (?, ?)",
            (SCHEMA_NAME, SCHEMA_VERSION),
        )

    def _validate_schema(self, connection: sqlite3.Connection) -> None:
        tables = self._table_names(connection)
        required_tables = {
            "schema_metadata",
            "aether_instance_trust",
            "owner_security_transactions",
            "owner_security_audit_events",
        }
        user_tables = {table for table in tables if not table.startswith("sqlite_")}
        if user_tables != required_tables:
            raise CorruptSchemaError("security-kernel schema tables are altered")
        try:
            metadata = connection.execute(
                "SELECT schema_name, schema_version FROM schema_metadata"
            ).fetchall()
            if len(metadata) != 1 or metadata[0][0] != SCHEMA_NAME:
                raise CorruptSchemaError("security-kernel schema metadata is altered")
            version = int(metadata[0][1])
        except (sqlite3.DatabaseError, TypeError, ValueError) as exc:
            raise CorruptSchemaError("security-kernel schema metadata is corrupt") from exc
        if version > SCHEMA_VERSION:
            raise SchemaVersionError(
                f"security-kernel schema {version} is newer than supported {SCHEMA_VERSION}"
            )
        if version < SCHEMA_VERSION:
            raise SchemaVersionError(
                f"no deterministic migration exists from security-kernel schema {version}"
            )
        expected_columns = {
            "schema_metadata": (
                ("schema_name", "TEXT", 0, 1, None),
                ("schema_version", "INTEGER", 1, 0, None),
            ),
            "aether_instance_trust": (
                ("aether_instance_id", "TEXT", 0, 1, None),
                ("lifecycle_state", "TEXT", 1, 0, None),
                ("trust_generation", "INTEGER", 1, 0, None),
                ("created_at", "TEXT", 1, 0, None),
                ("updated_at", "TEXT", 1, 0, None),
                ("schema_version", "INTEGER", 1, 0, None),
                ("active", "INTEGER", 1, 0, None),
            ),
            "owner_security_transactions": (
                ("transaction_id", "TEXT", 0, 1, None),
                ("aether_instance_id", "TEXT", 1, 0, None),
                ("expected_trust_generation", "INTEGER", 1, 0, None),
                ("resulting_trust_generation", "INTEGER", 1, 0, None),
                ("exact_operation", "TEXT", 1, 0, None),
                ("canonical_request_digest", "TEXT", 1, 0, None),
                ("idempotency_key", "TEXT", 1, 0, None),
                ("transaction_status", "TEXT", 1, 0, None),
                ("committed_result", "TEXT", 1, 0, None),
                ("result_digest", "TEXT", 1, 0, None),
                ("conflict_classification", "TEXT", 0, 0, None),
                ("created_at", "TEXT", 1, 0, None),
                ("committed_at", "TEXT", 1, 0, None),
            ),
            "owner_security_audit_events": (
                ("audit_event_id", "TEXT", 0, 1, None),
                ("transaction_id", "TEXT", 1, 0, None),
                ("aether_instance_id", "TEXT", 1, 0, None),
                ("trust_generation", "INTEGER", 1, 0, None),
                ("event_kind", "TEXT", 1, 0, None),
                ("affected_canonical_state_reference", "TEXT", 1, 0, None),
                ("non_secret_evidence_digest", "TEXT", 1, 0, None),
                ("committed_result_classification", "TEXT", 1, 0, None),
                ("result", "TEXT", 1, 0, None),
                ("timestamp", "TEXT", 1, 0, None),
            ),
        }
        for table, columns in expected_columns.items():
            if self._table_info(connection, table) != columns:
                raise CorruptSchemaError(f"security-kernel table {table} is altered")

        if (("active",), True, True) not in self._index_signatures(
            connection, "aether_instance_trust"
        ):
            raise CorruptSchemaError("one-active-instance uniqueness is altered")
        if (("aether_instance_id", "idempotency_key"), True, False) not in self._index_signatures(
            connection, "owner_security_transactions"
        ):
            raise CorruptSchemaError("transaction idempotency uniqueness is altered")
        if (("transaction_id",), True, False) not in self._index_signatures(
            connection, "owner_security_audit_events"
        ):
            raise CorruptSchemaError("audit transaction uniqueness is altered")

        expected_foreign_keys = {
            "owner_security_transactions": {
                ("aether_instance_trust", "aether_instance_id", "aether_instance_id")
            },
            "owner_security_audit_events": {
                ("owner_security_transactions", "transaction_id", "transaction_id"),
                ("aether_instance_trust", "aether_instance_id", "aether_instance_id"),
            },
        }
        for table, expected in expected_foreign_keys.items():
            if self._foreign_key_signatures(connection, table) != expected:
                raise CorruptSchemaError(f"security-kernel foreign keys for {table} are altered")

        integrity = connection.execute("PRAGMA integrity_check").fetchone()
        if integrity is None or integrity[0] != "ok":
            raise CorruptSchemaError("SQLite integrity check failed")
        if connection.execute("PRAGMA foreign_key_check").fetchall():
            raise CorruptSchemaError("SQLite foreign-key integrity check failed")

        active_rows = connection.execute(
            "SELECT aether_instance_id, lifecycle_state, trust_generation, schema_version, active "
            "FROM aether_instance_trust"
        ).fetchall()
        try:
            active_count = sum(int(row[4]) for row in active_rows)
        except (TypeError, ValueError) as exc:
            raise CorruptSchemaError("active instance markers are invalid") from exc
        if active_count > 1:
            raise CorruptSchemaError("multiple active Aether instances exist")
        for row in active_rows:
            try:
                _validate_identity(row[0], "aether_instance_id")
                OwnerLifecycleState(row[1])
                if int(row[2]) <= 0 or int(row[3]) != SCHEMA_VERSION:
                    raise ValueError
                if int(row[4]) not in (0, 1):
                    raise ValueError
            except (InvalidTransactionError, ValueError, TypeError) as exc:
                raise CorruptSchemaError("stored instance trust state is invalid") from exc

        for row in connection.execute("SELECT * FROM owner_security_transactions"):
            self._validate_committed_record(connection, row)

    def migrate(self) -> int:
        """Initialize an empty store or validate the current schema idempotently."""
        connection = self._connect()
        try:
            connection.execute("BEGIN IMMEDIATE")
            tables = self._table_names(connection)
            if not tables:
                self._create_schema(connection)
            elif "schema_metadata" not in tables:
                raise CorruptSchemaError("existing store has no schema metadata")
            self._validate_schema(connection)
            connection.commit()
            return SCHEMA_VERSION
        except (SchemaVersionError, CorruptSchemaError):
            if connection.in_transaction:
                connection.rollback()
            raise
        except sqlite3.DatabaseError as exc:
            if connection.in_transaction:
                connection.rollback()
            if _is_transient_sqlite_contention(exc):
                raise DatabaseUnavailableError(
                    "SQLite migration contention deadline exhausted"
                ) from exc
            raise CorruptSchemaError("security-kernel schema validation failed") from exc
        except Exception:
            if connection.in_transaction:
                connection.rollback()
            raise
        finally:
            connection.close()

    def _inject(self, stage: str) -> None:
        if self.fault_injector is not None:
            self.fault_injector(stage)

    @staticmethod
    def _instance_from_row(row: sqlite3.Row) -> AetherInstanceTrust:
        try:
            state = OwnerLifecycleState(row["lifecycle_state"])
        except ValueError as exc:
            raise CorruptSchemaError("stored lifecycle state is unknown") from exc
        return AetherInstanceTrust(
            aether_instance_id=row["aether_instance_id"],
            lifecycle_state=state,
            trust_generation=int(row["trust_generation"]),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            schema_version=int(row["schema_version"]),
            active=bool(row["active"]),
        )

    @staticmethod
    def _transaction_from_row(row: sqlite3.Row) -> OwnerSecurityTransaction:
        result = json.loads(row["committed_result"])
        return OwnerSecurityTransaction(
            transaction_id=row["transaction_id"],
            aether_instance_id=row["aether_instance_id"],
            expected_trust_generation=int(row["expected_trust_generation"]),
            resulting_trust_generation=int(row["resulting_trust_generation"]),
            exact_operation=row["exact_operation"],
            canonical_request_digest=row["canonical_request_digest"],
            idempotency_key=row["idempotency_key"],
            transaction_status=row["transaction_status"],
            committed_result=MappingProxyType(result),
            result_digest=row["result_digest"],
            conflict_classification=row["conflict_classification"],
            created_at=row["created_at"],
            committed_at=row["committed_at"],
        )

    @staticmethod
    def _audit_from_row(row: sqlite3.Row) -> OwnerSecurityAuditEvent:
        return OwnerSecurityAuditEvent(
            audit_event_id=row["audit_event_id"],
            transaction_id=row["transaction_id"],
            aether_instance_id=row["aether_instance_id"],
            trust_generation=int(row["trust_generation"]),
            event_kind=row["event_kind"],
            affected_canonical_state_reference=row[
                "affected_canonical_state_reference"
            ],
            non_secret_evidence_digest=row["non_secret_evidence_digest"],
            committed_result_classification=row["committed_result_classification"],
            result=row["result"],
            timestamp=row["timestamp"],
        )

    @staticmethod
    def _validate_timestamp(value: Any) -> None:
        if not isinstance(value, str):
            raise SecurityKernelIntegrityError("stored timestamp is invalid")
        try:
            parsed = datetime.fromisoformat(value)
        except ValueError as exc:
            raise SecurityKernelIntegrityError("stored timestamp is invalid") from exc
        if parsed.tzinfo is None:
            raise SecurityKernelIntegrityError("stored timestamp has no timezone")

    @staticmethod
    def _parse_committed_result(raw: Any) -> dict[str, Any]:
        if not isinstance(raw, str):
            raise SecurityKernelIntegrityError("committed result is not text")

        def reject_constant(value: str) -> None:
            raise ValueError(value)

        try:
            result = json.loads(raw, parse_constant=reject_constant)
            if not isinstance(result, dict):
                raise ValueError("committed result must be a JSON object")
            canonical = _canonical_json(result, reject_secret_fields=True)
        except (InvalidTransactionError, TypeError, ValueError, json.JSONDecodeError) as exc:
            raise SecurityKernelIntegrityError("committed result JSON is invalid") from exc
        if canonical != raw:
            raise SecurityKernelIntegrityError("committed result JSON is not canonical")
        return result

    def _validate_committed_record(
        self,
        connection: sqlite3.Connection,
        row: sqlite3.Row,
    ) -> dict[str, Any]:
        try:
            transaction_id = row["transaction_id"]
            aether_instance_id = row["aether_instance_id"]
            idempotency_key = row["idempotency_key"]
            exact_operation = row["exact_operation"]
            _validate_identity(transaction_id, "transaction_id")
            _validate_identity(aether_instance_id, "aether_instance_id")
            _validate_identity(idempotency_key, "idempotency_key")
            if not isinstance(exact_operation, str) or not _OPERATION.fullmatch(
                exact_operation
            ):
                raise ValueError("operation")
            expected_generation = int(row["expected_trust_generation"])
            resulting_generation = int(row["resulting_trust_generation"])
            if expected_generation < 0 or resulting_generation <= 0:
                raise ValueError("generation")
            request_digest = row["canonical_request_digest"]
            result_digest = row["result_digest"]
            if not isinstance(request_digest, str) or not _HEX64.fullmatch(request_digest):
                raise ValueError("request digest")
            if not isinstance(result_digest, str) or not _HEX64.fullmatch(result_digest):
                raise ValueError("result digest")
            if row["transaction_status"] != _TransactionStatus.COMMITTED.value:
                raise ValueError("transaction status")
            self._validate_timestamp(row["created_at"])
            self._validate_timestamp(row["committed_at"])
            result = self._parse_committed_result(row["committed_result"])
        except (InvalidTransactionError, TypeError, ValueError, KeyError) as exc:
            raise SecurityKernelIntegrityError(
                "committed transaction fields are invalid"
            ) from exc

        actual_result_digest = _result_digest(result)
        if actual_result_digest != result_digest:
            raise SecurityKernelIntegrityError("committed result digest does not match")
        expected_event_kind = _EVENT_KIND_BY_OPERATION.get(exact_operation)
        if expected_event_kind is None:
            raise SecurityKernelIntegrityError("committed operation is unsupported")

        audit_rows = connection.execute(
            "SELECT * FROM owner_security_audit_events WHERE transaction_id = ?",
            (transaction_id,),
        ).fetchall()
        if len(audit_rows) != 1:
            raise SecurityKernelIntegrityError(
                "committed transaction must have exactly one audit event"
            )
        try:
            audit = self._audit_from_row(audit_rows[0])
            expected_reference = f"AetherInstanceTrust:{aether_instance_id}"
            if audit.audit_event_id != _audit_event_id(transaction_id):
                raise ValueError("audit event identity")
            if audit.transaction_id != transaction_id:
                raise ValueError("audit transaction identity")
            if audit.aether_instance_id != aether_instance_id:
                raise ValueError("audit instance identity")
            if audit.trust_generation != resulting_generation:
                raise ValueError("audit generation")
            if audit.event_kind != expected_event_kind:
                raise ValueError("audit event kind")
            if audit.affected_canonical_state_reference != expected_reference:
                raise ValueError("audit state reference")
            if audit.committed_result_classification != COMMITTED_RESULT_CLASSIFICATION:
                raise ValueError("audit result classification")
            if audit.result != _TransactionStatus.COMMITTED.value:
                raise ValueError("audit result")
            if audit.timestamp != row["committed_at"]:
                raise ValueError("audit timestamp")
            expected_evidence_digest = canonical_audit_evidence_digest(
                audit_event_id=audit.audit_event_id,
                transaction_id=transaction_id,
                aether_instance_id=aether_instance_id,
                expected_trust_generation=expected_generation,
                resulting_trust_generation=resulting_generation,
                exact_operation=exact_operation,
                canonical_request_digest_value=request_digest,
                idempotency_key=idempotency_key,
                committed_result_digest=result_digest,
                event_kind=expected_event_kind,
                affected_canonical_state_reference=expected_reference,
                committed_result_classification=COMMITTED_RESULT_CLASSIFICATION,
                result=_TransactionStatus.COMMITTED.value,
                timestamp=audit.timestamp,
            )
        except (InvalidTransactionError, TypeError, ValueError, KeyError) as exc:
            raise SecurityKernelIntegrityError(
                "committed audit fields are invalid"
            ) from exc
        if audit.non_secret_evidence_digest != expected_evidence_digest:
            raise SecurityKernelIntegrityError("audit evidence digest does not match")
        return result

    def get_instance_trust(self) -> AetherInstanceTrust | None:
        connection = self._connect()
        try:
            row = connection.execute(
                "SELECT * FROM aether_instance_trust WHERE active = 1"
            ).fetchone()
            return self._instance_from_row(row) if row else None
        finally:
            connection.close()

    def get_transaction(self, transaction_id: str) -> OwnerSecurityTransaction | None:
        _validate_identity(transaction_id, "transaction_id")
        connection = self._connect()
        try:
            row = connection.execute(
                "SELECT * FROM owner_security_transactions WHERE transaction_id = ?",
                (transaction_id,),
            ).fetchone()
            if row is None:
                return None
            self._validate_committed_record(connection, row)
            return self._transaction_from_row(row)
        finally:
            connection.close()

    def list_audit_events(self) -> list[OwnerSecurityAuditEvent]:
        connection = self._connect()
        try:
            rows = connection.execute(
                "SELECT * FROM owner_security_audit_events ORDER BY timestamp, audit_event_id"
            ).fetchall()
            transaction_rows = connection.execute(
                "SELECT * FROM owner_security_transactions"
            ).fetchall()
            transaction_ids = {row["transaction_id"] for row in transaction_rows}
            for transaction_row in transaction_rows:
                self._validate_committed_record(connection, transaction_row)
            if any(row["transaction_id"] not in transaction_ids for row in rows):
                raise SecurityKernelIntegrityError(
                    "audit event has no committed transaction"
                )
            return [self._audit_from_row(row) for row in rows]
        finally:
            connection.close()

    @staticmethod
    def _validate_request_digest(request: SecurityTransactionRequest) -> None:
        expected = canonical_request_digest(
            transaction_id=request.transaction_id,
            aether_instance_id=request.aether_instance_id,
            expected_trust_generation=request.expected_trust_generation,
            exact_operation=request.exact_operation,
            idempotency_key=request.idempotency_key,
            payload=request.payload,
        )
        if request.request_digest != expected:
            raise InvalidTransactionError("request_digest does not match canonical request")

    @staticmethod
    def _existing_matches(
        row: sqlite3.Row,
        request: SecurityTransactionRequest,
    ) -> bool:
        return all(
            (
                row["transaction_id"] == request.transaction_id,
                row["aether_instance_id"] == request.aether_instance_id,
                int(row["expected_trust_generation"])
                == request.expected_trust_generation,
                row["exact_operation"] == request.exact_operation,
                row["canonical_request_digest"] == request.request_digest,
                row["idempotency_key"] == request.idempotency_key,
            )
        )

    def _resolve_existing(
        self,
        connection: sqlite3.Connection,
        request: SecurityTransactionRequest,
        operation: str,
    ) -> dict[str, Any] | None:
        by_transaction = connection.execute(
            "SELECT * FROM owner_security_transactions WHERE transaction_id = ?",
            (request.transaction_id,),
        ).fetchone()
        if by_transaction is not None:
            recorded = self._validate_committed_record(connection, by_transaction)
            if not self._existing_matches(by_transaction, request):
                raise ReplayConflictError(
                    "transaction identity was reused with changed binding"
                )
            if by_transaction["exact_operation"] != operation:
                raise InvalidTransactionError(
                    f"operation must be {operation} for this kernel method"
                )
            return recorded

        by_idempotency = connection.execute(
            """
            SELECT * FROM owner_security_transactions
            WHERE aether_instance_id = ? AND idempotency_key = ?
            """,
            (request.aether_instance_id, request.idempotency_key),
        ).fetchone()
        if by_idempotency is not None:
            self._validate_committed_record(connection, by_idempotency)
            raise ReplayConflictError(
                "idempotency identity was reused with a different transaction"
            )
        return None

    @staticmethod
    def _require_instance(
        connection: sqlite3.Connection,
        instance_id: str,
    ) -> sqlite3.Row:
        row = connection.execute(
            "SELECT * FROM aether_instance_trust WHERE active = 1"
        ).fetchone()
        if row is None or row["aether_instance_id"] != instance_id:
            raise ReplayConflictError("aether_instance_id is not bound to this store")
        return row

    @staticmethod
    def _require_generation(row: sqlite3.Row, request: SecurityTransactionRequest) -> None:
        if request.expected_trust_generation != int(row["trust_generation"]):
            raise StaleGenerationError("request trust generation is stale")

    def _execute_mutation(
        self,
        request: SecurityTransactionRequest,
        *,
        operation: str,
        event_kind: str,
        mutator: Callable[[sqlite3.Connection, SecurityTransactionRequest, str], tuple[dict[str, Any], int]],
    ) -> dict[str, Any]:
        connection = self._connect()
        try:
            connection.execute("BEGIN IMMEDIATE")
            self._validate_request_digest(request)
            existing = self._resolve_existing(connection, request, operation)
            if existing is not None:
                connection.rollback()
                return existing
            if request.exact_operation != operation:
                raise InvalidTransactionError(
                    f"operation must be {operation} for this kernel method"
                )
            created_at = _now()
            self._inject("before_state_mutation")
            result, resulting_generation = mutator(connection, request, created_at)
            result_json = _canonical_json(result, reject_secret_fields=True)
            digest = _result_digest(result)
            connection.execute(
                """
                INSERT INTO owner_security_transactions (
                    transaction_id, aether_instance_id, expected_trust_generation,
                    resulting_trust_generation, exact_operation,
                    canonical_request_digest, idempotency_key, transaction_status,
                    committed_result, result_digest, conflict_classification,
                    created_at, committed_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, 'COMMITTED', ?, ?, NULL, ?, ?)
                """,
                (
                    request.transaction_id,
                    request.aether_instance_id,
                    request.expected_trust_generation,
                    resulting_generation,
                    request.exact_operation,
                    request.request_digest,
                    request.idempotency_key,
                    result_json,
                    digest,
                    created_at,
                    created_at,
                ),
            )
            self._inject("after_state_mutation")
            self._inject("before_audit_insert")
            audit_id = _audit_event_id(request.transaction_id)
            affected_reference = f"AetherInstanceTrust:{request.aether_instance_id}"
            evidence_digest = canonical_audit_evidence_digest(
                audit_event_id=audit_id,
                transaction_id=request.transaction_id,
                aether_instance_id=request.aether_instance_id,
                expected_trust_generation=request.expected_trust_generation,
                resulting_trust_generation=resulting_generation,
                exact_operation=request.exact_operation,
                canonical_request_digest_value=request.request_digest,
                idempotency_key=request.idempotency_key,
                committed_result_digest=digest,
                event_kind=event_kind,
                affected_canonical_state_reference=affected_reference,
                committed_result_classification=COMMITTED_RESULT_CLASSIFICATION,
                result=_TransactionStatus.COMMITTED.value,
                timestamp=created_at,
            )
            connection.execute(
                """
                INSERT INTO owner_security_audit_events (
                    audit_event_id, transaction_id, aether_instance_id,
                    trust_generation, event_kind,
                    affected_canonical_state_reference,
                    non_secret_evidence_digest, committed_result_classification,
                    result, timestamp
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'COMMITTED', ?)
                """,
                (
                    audit_id,
                    request.transaction_id,
                    request.aether_instance_id,
                    resulting_generation,
                    event_kind,
                    affected_reference,
                    evidence_digest,
                    COMMITTED_RESULT_CLASSIFICATION,
                    created_at,
                ),
            )
            self._inject("after_audit_insert")
            self._inject("before_commit")
            connection.commit()
            self._inject("after_commit")
            return result
        except Exception:
            if connection.in_transaction:
                connection.rollback()
            raise
        finally:
            connection.close()

    def initialize_instance(self, request: SecurityTransactionRequest) -> dict[str, Any]:
        """Create the first unclaimed instance state with its canonical audit."""

        def mutate(
            connection: sqlite3.Connection,
            current_request: SecurityTransactionRequest,
            timestamp: str,
        ) -> tuple[dict[str, Any], int]:
            if current_request.expected_trust_generation != 0 or current_request.payload:
                raise InvalidTransactionError("initialization request binding is invalid")
            existing = connection.execute(
                "SELECT aether_instance_id FROM aether_instance_trust WHERE active = 1"
            ).fetchone()
            if existing is not None:
                raise ReplayConflictError("store already has an active instance")
            connection.execute(
                """
                INSERT INTO aether_instance_trust (
                    aether_instance_id, lifecycle_state, trust_generation,
                    created_at, updated_at, schema_version, active
                ) VALUES (?, 'UNCLAIMED', 1, ?, ?, ?, 1)
                """,
                (
                    current_request.aether_instance_id,
                    timestamp,
                    timestamp,
                    SCHEMA_VERSION,
                ),
            )
            return {
                "aether_instance_id": current_request.aether_instance_id,
                "lifecycle_state": OwnerLifecycleState.UNCLAIMED.value,
                "trust_generation": 1,
                "operation": current_request.exact_operation,
            }, 1

        return self._execute_mutation(
            request,
            operation="initialize_instance",
            event_kind="INSTANCE_INITIALIZED",
            mutator=mutate,
        )

    def transition_lifecycle(self, request: SecurityTransactionRequest) -> dict[str, Any]:
        """Apply one allowed lifecycle transition without authenticating its initiator."""

        def mutate(
            connection: sqlite3.Connection,
            current_request: SecurityTransactionRequest,
            timestamp: str,
        ) -> tuple[dict[str, Any], int]:
            row = self._require_instance(connection, current_request.aether_instance_id)
            self._require_generation(row, current_request)
            if set(current_request.payload) != {
                "source_state", "destination_state", "resulting_trust_generation"
            }:
                raise InvalidTransactionError("lifecycle payload fields are invalid")
            try:
                source = OwnerLifecycleState(current_request.payload["source_state"])
                destination = OwnerLifecycleState(
                    current_request.payload["destination_state"]
                )
            except (KeyError, ValueError) as exc:
                raise LifecycleTransitionError("lifecycle state is unknown") from exc
            if OwnerLifecycleState(row["lifecycle_state"]) != source:
                raise LifecycleTransitionError("source lifecycle state is not current")
            if (source, destination) not in _ALLOWED_TRANSITIONS:
                raise LifecycleTransitionError("lifecycle transition is not allowed")
            expected_resulting = current_request.expected_trust_generation
            if (source, destination) in {
                (OwnerLifecycleState.UNCLAIMED, OwnerLifecycleState.CLAIM_PENDING),
                (OwnerLifecycleState.RECOVERY_PENDING, OwnerLifecycleState.OWNED),
            }:
                expected_resulting += 1
            resulting = current_request.payload["resulting_trust_generation"]
            if resulting != expected_resulting:
                raise LifecycleTransitionError("resulting trust generation is invalid")
            connection.execute(
                """
                UPDATE aether_instance_trust
                SET lifecycle_state = ?, trust_generation = ?, updated_at = ?
                WHERE active = 1 AND aether_instance_id = ?
                """,
                (
                    destination.value,
                    resulting,
                    timestamp,
                    current_request.aether_instance_id,
                ),
            )
            return {
                "aether_instance_id": current_request.aether_instance_id,
                "lifecycle_state": destination.value,
                "trust_generation": resulting,
                "operation": current_request.exact_operation,
            }, resulting

        return self._execute_mutation(
            request,
            operation="transition_lifecycle",
            event_kind="LIFECYCLE_TRANSITION",
            mutator=mutate,
        )

    def rotate_trust_generation(self, request: SecurityTransactionRequest) -> dict[str, Any]:
        """Rotate the current generation by exactly one under a valid transaction."""

        def mutate(
            connection: sqlite3.Connection,
            current_request: SecurityTransactionRequest,
            timestamp: str,
        ) -> tuple[dict[str, Any], int]:
            row = self._require_instance(connection, current_request.aether_instance_id)
            self._require_generation(row, current_request)
            if set(current_request.payload) != {"resulting_trust_generation"}:
                raise InvalidTransactionError("rotation payload fields are invalid")
            resulting = current_request.payload["resulting_trust_generation"]
            if resulting != current_request.expected_trust_generation + 1:
                raise LifecycleTransitionError("trust generation must rotate by one")
            connection.execute(
                """
                UPDATE aether_instance_trust
                SET trust_generation = ?, updated_at = ?
                WHERE active = 1 AND aether_instance_id = ?
                """,
                (resulting, timestamp, current_request.aether_instance_id),
            )
            return {
                "aether_instance_id": current_request.aether_instance_id,
                "lifecycle_state": row["lifecycle_state"],
                "trust_generation": resulting,
                "operation": current_request.exact_operation,
            }, resulting

        return self._execute_mutation(
            request,
            operation="rotate_trust_generation",
            event_kind="TRUST_GENERATION_ROTATED",
            mutator=mutate,
        )
