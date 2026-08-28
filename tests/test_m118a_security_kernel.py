"""Focused persistence and boundary tests for the bounded M118A kernel."""

from __future__ import annotations

from dataclasses import fields, replace
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import sqlite3
import ast

import pytest

from aether.oas.security_kernel import (
    FIELD_CLASSIFICATION,
    AetherInstanceTrust,
    CorruptSchemaError,
    InvalidTransactionError,
    LifecycleTransitionError,
    OwnerLifecycleState,
    OwnerSecurityAuditEvent,
    OwnerSecurityTransaction,
    ReplayConflictError,
    SchemaVersionError,
    SecurityKernel,
    SecurityKernelIntegrityError,
    SecurityTransactionRequest,
    StaleGenerationError,
    AUDIT_EVIDENCE_VERSION,
    AUDIT_EVIDENCE_DOMAIN,
    MAX_JSON_COLLECTION_ITEMS,
    MAX_JSON_DEPTH,
    MAX_JSON_ENCODED_BYTES,
    MAX_JSON_INTEGER_DIGITS,
    MAX_JSON_KEY_BYTES,
    MAX_JSON_STRING_BYTES,
    REQUEST_DIGEST_VERSION,
    REQUEST_DIGEST_DOMAIN,
    _canonical_json,
    canonical_audit_evidence_digest,
    canonical_request_digest,
)


INSTANCE = "instance_m118a"


def _request(
    *,
    transaction_id: str,
    operation: str,
    expected_generation: int,
    payload: dict,
    idempotency_key: str | None = None,
    instance_id: str = INSTANCE,
) -> SecurityTransactionRequest:
    return SecurityTransactionRequest.build(
        transaction_id=transaction_id,
        aether_instance_id=instance_id,
        expected_trust_generation=expected_generation,
        exact_operation=operation,
        idempotency_key=idempotency_key or transaction_id,
        payload=payload,
    )


def _initialize(kernel: SecurityKernel, transaction_id: str = "tx_init") -> dict:
    return kernel.initialize_instance(
        _request(
            transaction_id=transaction_id,
            operation="initialize_instance",
            expected_generation=0,
            payload={},
        )
    )


def _transition(
    kernel: SecurityKernel,
    *,
    transaction_id: str,
    expected_generation: int,
    source: str,
    destination: str,
    resulting_generation: int,
    idempotency_key: str | None = None,
) -> dict:
    return kernel.transition_lifecycle(
        _request(
            transaction_id=transaction_id,
            operation="transition_lifecycle",
            expected_generation=expected_generation,
            idempotency_key=idempotency_key,
            payload={
                "source_state": source,
                "destination_state": destination,
                "resulting_trust_generation": resulting_generation,
            },
        )
    )


@pytest.fixture
def store_path(tmp_path: Path) -> Path:
    return tmp_path / "private" / "oas" / "security_kernel.sqlite3"


@pytest.fixture
def kernel(store_path: Path) -> SecurityKernel:
    return SecurityKernel(store_path)


def test_empty_store_initialization_and_schema_version(store_path: Path):
    assert not store_path.exists()
    kernel = SecurityKernel(store_path)
    assert store_path.is_file()
    assert kernel.migrate() == 1
    with sqlite3.connect(store_path) as connection:
        row = connection.execute(
            "SELECT schema_name, schema_version FROM schema_metadata"
        ).fetchone()
    assert row == ("oas_security_kernel", 1)


def test_migration_is_idempotent(store_path: Path):
    kernel = SecurityKernel(store_path)
    before = store_path.read_bytes()
    assert kernel.migrate() == 1
    assert store_path.read_bytes() == before


def test_schema_index_integrity_is_required(store_path: Path):
    SecurityKernel(store_path)
    with sqlite3.connect(store_path) as connection:
        connection.execute("DROP INDEX one_active_aether_instance")
        connection.commit()
    with pytest.raises(CorruptSchemaError, match="one-active-instance"):
        SecurityKernel(store_path)


def test_schema_column_properties_are_required(store_path: Path):
    SecurityKernel(store_path)
    with sqlite3.connect(store_path) as connection:
        connection.execute("PRAGMA writable_schema = ON")
        original = connection.execute(
            "SELECT sql FROM sqlite_master WHERE name = 'owner_security_transactions'"
        ).fetchone()[0]
        altered = original.replace("result_digest TEXT NOT NULL", "result_digest TEXT")
        connection.execute(
            "UPDATE sqlite_master SET sql = ? WHERE name = 'owner_security_transactions'",
            (altered,),
        )
        connection.execute("PRAGMA writable_schema = OFF")
        connection.commit()
    with pytest.raises(CorruptSchemaError, match="owner_security_transactions"):
        SecurityKernel(store_path)


def test_foreign_key_integrity_is_required(store_path: Path):
    SecurityKernel(store_path)
    with sqlite3.connect(store_path) as connection:
        connection.execute("PRAGMA foreign_keys = OFF")
        connection.execute(
            """
            INSERT INTO owner_security_audit_events (
                audit_event_id, transaction_id, aether_instance_id,
                trust_generation, event_kind, affected_canonical_state_reference,
                non_secret_evidence_digest, committed_result_classification,
                result, timestamp
            ) VALUES ('orphan', 'missing_tx', 'missing_instance', 1,
                      'LIFECYCLE_TRANSITION', 'missing', ?,
                      'NON_SECRET_CANONICAL_JSON', 'COMMITTED', ?)
            """,
            ("0" * 64, "2026-08-28T00:00:00+00:00"),
        )
        connection.commit()
    with pytest.raises(CorruptSchemaError, match="foreign-key"):
        SecurityKernel(store_path)


def test_concurrent_first_open_initializes_schema_once(store_path: Path):
    request = _request(
        transaction_id="tx_concurrent_init",
        operation="initialize_instance",
        expected_generation=0,
        payload={},
    )

    def invoke(_: int) -> dict:
        return SecurityKernel(store_path).initialize_instance(request)

    with ThreadPoolExecutor(max_workers=8) as pool:
        results = list(pool.map(invoke, range(8)))
    assert all(result == results[0] for result in results)
    assert len(SecurityKernel(store_path).list_audit_events()) == 1


def test_newer_schema_is_rejected_without_recreation(store_path: Path):
    SecurityKernel(store_path)
    with sqlite3.connect(store_path) as connection:
        connection.execute(
            "UPDATE schema_metadata SET schema_version = 99 WHERE schema_name = ?",
            ("oas_security_kernel",),
        )
        connection.commit()
    with pytest.raises(SchemaVersionError):
        SecurityKernel(store_path)


def test_corrupted_schema_fails_closed(store_path: Path):
    store_path.parent.mkdir(parents=True)
    store_path.write_bytes(b"not a sqlite database")
    with pytest.raises(CorruptSchemaError):
        SecurityKernel(store_path)


def test_incomplete_schema_fails_closed_without_silent_recreation(store_path: Path):
    store_path.parent.mkdir(parents=True)
    with sqlite3.connect(store_path) as connection:
        connection.execute(
            "CREATE TABLE schema_metadata (schema_name TEXT PRIMARY KEY, schema_version INTEGER)"
        )
        connection.execute(
            "INSERT INTO schema_metadata VALUES ('oas_security_kernel', 1)"
        )
        connection.commit()
    with pytest.raises(CorruptSchemaError):
        SecurityKernel(store_path)


def test_initial_canonical_instance_state(kernel: SecurityKernel):
    result = _initialize(kernel)
    state = kernel.get_instance_trust()
    assert result["lifecycle_state"] == "UNCLAIMED"
    assert result["trust_generation"] == 1
    assert isinstance(state, AetherInstanceTrust)
    assert state.to_dict()["active"] is True
    assert state.lifecycle_state is OwnerLifecycleState.UNCLAIMED


def test_instance_id_is_immutable(kernel: SecurityKernel):
    _initialize(kernel)
    with pytest.raises(ReplayConflictError):
        kernel.initialize_instance(
            _request(
                transaction_id="tx_other_instance",
                operation="initialize_instance",
                expected_generation=0,
                payload={},
                instance_id="another_instance",
            )
        )
    assert kernel.get_instance_trust().aether_instance_id == INSTANCE


def test_valid_lifecycle_transitions_and_controlled_generation_rotation(
    kernel: SecurityKernel,
):
    _initialize(kernel)
    _transition(
        kernel,
        transaction_id="tx_pending",
        expected_generation=1,
        source="UNCLAIMED",
        destination="CLAIM_PENDING",
        resulting_generation=2,
    )
    _transition(
        kernel,
        transaction_id="tx_owned",
        expected_generation=2,
        source="CLAIM_PENDING",
        destination="OWNED",
        resulting_generation=2,
    )
    _transition(
        kernel,
        transaction_id="tx_recovery_pending",
        expected_generation=2,
        source="OWNED",
        destination="RECOVERY_PENDING",
        resulting_generation=2,
    )
    result = _transition(
        kernel,
        transaction_id="tx_recovered",
        expected_generation=2,
        source="RECOVERY_PENDING",
        destination="OWNED",
        resulting_generation=3,
    )
    assert result["trust_generation"] == 3
    assert kernel.get_instance_trust().lifecycle_state is OwnerLifecycleState.OWNED


def test_explicit_trust_generation_rotation(kernel: SecurityKernel):
    _initialize(kernel)
    result = kernel.rotate_trust_generation(
        _request(
            transaction_id="tx_rotate",
            operation="rotate_trust_generation",
            expected_generation=1,
            payload={"resulting_trust_generation": 2},
        )
    )
    assert result["trust_generation"] == 2
    assert kernel.get_instance_trust().trust_generation == 2


@pytest.mark.parametrize(
    ("source", "destination", "resulting"),
    [
        ("UNKNOWN", "OWNED", 1),
        ("UNCLAIMED", "OWNED", 1),
        ("OWNED", "UNCLAIMED", 1),
        ("CLAIM_PENDING", "RECOVERY_PENDING", 2),
    ],
)
def test_invalid_or_skipped_lifecycle_transitions_are_rejected(
    kernel: SecurityKernel,
    source: str,
    destination: str,
    resulting: int,
):
    _initialize(kernel)
    with pytest.raises(LifecycleTransitionError):
        _transition(
            kernel,
            transaction_id=f"tx_invalid_{source}_{destination}",
            expected_generation=1,
            source=source,
            destination=destination,
            resulting_generation=resulting,
        )


def test_wrong_source_state_and_wrong_instance_are_rejected(kernel: SecurityKernel):
    _initialize(kernel)
    with pytest.raises(LifecycleTransitionError):
        _transition(
            kernel,
            transaction_id="tx_wrong_source",
            expected_generation=1,
            source="CLAIM_PENDING",
            destination="OWNED",
            resulting_generation=1,
        )
    with pytest.raises(ReplayConflictError):
        kernel.transition_lifecycle(
            _request(
                transaction_id="tx_wrong_instance",
                operation="transition_lifecycle",
                expected_generation=1,
                payload={
                    "source_state": "UNCLAIMED",
                    "destination_state": "CLAIM_PENDING",
                    "resulting_trust_generation": 2,
                },
                instance_id="different_instance",
            )
        )


def test_stale_generation_is_rejected(kernel: SecurityKernel):
    _initialize(kernel)
    with pytest.raises(StaleGenerationError):
        _transition(
            kernel,
            transaction_id="tx_stale",
            expected_generation=9,
            source="UNCLAIMED",
            destination="CLAIM_PENDING",
            resulting_generation=10,
        )
    assert kernel.get_instance_trust().lifecycle_state is OwnerLifecycleState.UNCLAIMED


def test_missing_transaction_identity_is_rejected():
    with pytest.raises(InvalidTransactionError):
        SecurityTransactionRequest.build(
            transaction_id="",
            aether_instance_id=INSTANCE,
            expected_trust_generation=0,
            exact_operation="initialize_instance",
            idempotency_key="idempotency",
            payload={},
        )


def test_store_path_is_explicitly_required():
    with pytest.raises(TypeError, match="store_path"):
        SecurityKernel(None)


def test_state_and_audit_commit_atomically(kernel: SecurityKernel):
    _initialize(kernel)
    _transition(
        kernel,
        transaction_id="tx_atomic",
        expected_generation=1,
        source="UNCLAIMED",
        destination="CLAIM_PENDING",
        resulting_generation=2,
    )
    transaction = kernel.get_transaction("tx_atomic")
    events = kernel.list_audit_events()
    assert transaction.transaction_status == "COMMITTED"
    assert len(events) == 2
    assert events[-1].transaction_id == "tx_atomic"
    assert events[-1].non_secret_evidence_digest != transaction.result_digest
    assert events[-1].committed_result_classification == "NON_SECRET_CANONICAL_JSON"
    assert events[-1].non_secret_evidence_digest == canonical_audit_evidence_digest(
        audit_event_id=events[-1].audit_event_id,
        transaction_id=transaction.transaction_id,
        aether_instance_id=transaction.aether_instance_id,
        expected_trust_generation=transaction.expected_trust_generation,
        resulting_trust_generation=transaction.resulting_trust_generation,
        exact_operation=transaction.exact_operation,
        canonical_request_digest_value=transaction.canonical_request_digest,
        idempotency_key=transaction.idempotency_key,
        committed_result_digest=transaction.result_digest,
        event_kind=events[-1].event_kind,
        affected_canonical_state_reference=events[-1].affected_canonical_state_reference,
        committed_result_classification=events[-1].committed_result_classification,
        result=events[-1].result,
        timestamp=events[-1].timestamp,
    )


def test_request_digest_binds_every_required_request_field():
    base = {
        "transaction_id": "tx_digest",
        "idempotency_key": "idem_digest",
        "aether_instance_id": INSTANCE,
        "expected_trust_generation": 1,
        "exact_operation": "transition_lifecycle",
        "payload": {"value": "one"},
    }
    original = canonical_request_digest(**base)
    assert REQUEST_DIGEST_DOMAIN == "aether.oas.security-kernel.request"
    assert REQUEST_DIGEST_VERSION == 1
    variants = {
        "transaction_id": "tx_digest_changed",
        "idempotency_key": "idem_digest_changed",
        "aether_instance_id": "instance_changed",
        "expected_trust_generation": 2,
        "exact_operation": "rotate_trust_generation",
        "payload": {"value": "two"},
    }
    for field, value in variants.items():
        candidate = dict(base)
        candidate[field] = value
        assert canonical_request_digest(**candidate) != original, field


def test_audit_evidence_digest_binds_every_required_event_field():
    base = {
        "audit_event_id": "audit_event",
        "transaction_id": "tx_event",
        "aether_instance_id": INSTANCE,
        "expected_trust_generation": 1,
        "resulting_trust_generation": 2,
        "exact_operation": "transition_lifecycle",
        "canonical_request_digest_value": "1" * 64,
        "idempotency_key": "idem_event",
        "committed_result_digest": "2" * 64,
        "event_kind": "LIFECYCLE_TRANSITION",
        "affected_canonical_state_reference": f"AetherInstanceTrust:{INSTANCE}",
        "committed_result_classification": "NON_SECRET_CANONICAL_JSON",
        "result": "COMMITTED",
        "timestamp": "2026-08-28T00:00:00+00:00",
    }
    original = canonical_audit_evidence_digest(**base)
    assert AUDIT_EVIDENCE_DOMAIN == "aether.oas.security-kernel.audit-evidence"
    assert AUDIT_EVIDENCE_VERSION == 1
    variants = {
        "audit_event_id": "audit_event_changed",
        "transaction_id": "tx_event_changed",
        "aether_instance_id": "instance_changed",
        "expected_trust_generation": 3,
        "resulting_trust_generation": 4,
        "exact_operation": "rotate_trust_generation",
        "canonical_request_digest_value": "3" * 64,
        "idempotency_key": "idem_event_changed",
        "committed_result_digest": "4" * 64,
        "event_kind": "TRUST_GENERATION_ROTATED",
        "affected_canonical_state_reference": "AetherInstanceTrust:other",
        "committed_result_classification": "OTHER",
        "result": "REJECTED",
        "timestamp": "2026-08-28T00:00:01+00:00",
    }
    for field, value in variants.items():
        candidate = dict(base)
        candidate[field] = value
        assert canonical_audit_evidence_digest(**candidate) != original, field


@pytest.mark.parametrize("failure_stage", ["before_state_mutation", "after_state_mutation"])
def test_state_failure_rolls_back_state_transaction_and_audit(
    store_path: Path,
    failure_stage: str,
):
    kernel = SecurityKernel(store_path)
    _initialize(kernel)

    def fail(stage: str) -> None:
        if stage == failure_stage:
            raise RuntimeError("forced state failure")

    failing = SecurityKernel(store_path, fault_injector=fail)
    with pytest.raises(RuntimeError, match="forced state failure"):
        _transition(
            failing,
            transaction_id=f"tx_state_failure_{failure_stage}",
            expected_generation=1,
            source="UNCLAIMED",
            destination="CLAIM_PENDING",
            resulting_generation=2,
        )
    assert kernel.get_instance_trust().lifecycle_state is OwnerLifecycleState.UNCLAIMED
    assert kernel.get_instance_trust().trust_generation == 1
    assert len(kernel.list_audit_events()) == 1


def test_audit_failure_rolls_back_canonical_state(store_path: Path):
    kernel = SecurityKernel(store_path)
    _initialize(kernel)

    def fail(stage: str) -> None:
        if stage == "before_audit_insert":
            raise RuntimeError("forced audit failure")

    with pytest.raises(RuntimeError, match="forced audit failure"):
        _transition(
            SecurityKernel(store_path, fault_injector=fail),
            transaction_id="tx_audit_failure",
            expected_generation=1,
            source="UNCLAIMED",
            destination="CLAIM_PENDING",
            resulting_generation=2,
        )
    assert kernel.get_instance_trust().lifecycle_state is OwnerLifecycleState.UNCLAIMED
    assert len(kernel.list_audit_events()) == 1


def test_failure_after_commit_is_durable_and_retry_has_no_second_audit(
    store_path: Path,
):
    kernel = SecurityKernel(store_path)
    _initialize(kernel)
    request = _request(
        transaction_id="tx_after_commit",
        operation="transition_lifecycle",
        expected_generation=1,
        payload={
            "source_state": "UNCLAIMED",
            "destination_state": "CLAIM_PENDING",
            "resulting_trust_generation": 2,
        },
    )

    def fail(stage: str) -> None:
        if stage == "after_commit":
            raise RuntimeError("simulated post-commit crash")

    with pytest.raises(RuntimeError, match="simulated post-commit crash"):
        SecurityKernel(store_path, fault_injector=fail).transition_lifecycle(request)
    reopened = SecurityKernel(store_path)
    assert reopened.get_instance_trust().lifecycle_state is OwnerLifecycleState.CLAIM_PENDING
    assert reopened.transition_lifecycle(request) == {
        "aether_instance_id": INSTANCE,
        "lifecycle_state": "CLAIM_PENDING",
        "trust_generation": 2,
        "operation": "transition_lifecycle",
    }
    assert len(reopened.list_audit_events()) == 2


def test_identical_retry_returns_recorded_result_without_duplicate_audit(kernel: SecurityKernel):
    _initialize(kernel)
    request = _request(
        transaction_id="tx_retry",
        operation="transition_lifecycle",
        expected_generation=1,
        payload={
            "source_state": "UNCLAIMED",
            "destination_state": "CLAIM_PENDING",
            "resulting_trust_generation": 2,
        },
    )
    first = kernel.transition_lifecycle(request)
    second = kernel.transition_lifecycle(request)
    assert first == second
    assert len(kernel.list_audit_events()) == 2


@pytest.mark.parametrize("change", ["digest", "operation"])
def test_reused_transaction_identity_with_changed_binding_rejects(
    kernel: SecurityKernel,
    change: str,
):
    _initialize(kernel)
    request = _request(
        transaction_id="tx_changed_binding",
        operation="transition_lifecycle",
        expected_generation=1,
        payload={
            "source_state": "UNCLAIMED",
            "destination_state": "CLAIM_PENDING",
            "resulting_trust_generation": 2,
        },
    )
    kernel.transition_lifecycle(request)
    if change == "digest":
        changed_payload = {
            "source_state": "UNCLAIMED",
            "destination_state": "CLAIM_PENDING",
            "resulting_trust_generation": 3,
        }
        changed = replace(
            request,
            payload=changed_payload,
            request_digest=canonical_request_digest(
                transaction_id=request.transaction_id,
                aether_instance_id=request.aether_instance_id,
                expected_trust_generation=request.expected_trust_generation,
                exact_operation=request.exact_operation,
                idempotency_key=request.idempotency_key,
                payload=changed_payload,
            ),
        )
    else:
        changed_operation = "rotate_trust_generation"
        changed = replace(
            request,
            exact_operation=changed_operation,
            request_digest=canonical_request_digest(
                transaction_id=request.transaction_id,
                aether_instance_id=request.aether_instance_id,
                expected_trust_generation=request.expected_trust_generation,
                exact_operation=changed_operation,
                idempotency_key=request.idempotency_key,
                payload=request.payload,
            ),
        )
    with pytest.raises(ReplayConflictError):
        kernel.transition_lifecycle(changed)
    assert len(kernel.list_audit_events()) == 2


def test_changed_payload_with_stale_digest_is_rejected(kernel: SecurityKernel):
    _initialize(kernel)
    request = _request(
        transaction_id="tx_stale_payload_digest",
        operation="transition_lifecycle",
        expected_generation=1,
        payload={
            "source_state": "UNCLAIMED",
            "destination_state": "CLAIM_PENDING",
            "resulting_trust_generation": 2,
        },
    )
    changed = replace(
        request,
        payload={
            "source_state": "UNCLAIMED",
            "destination_state": "CLAIM_PENDING",
            "resulting_trust_generation": 3,
        },
    )
    with pytest.raises(InvalidTransactionError, match="does not match"):
        kernel.transition_lifecycle(changed)
    assert len(kernel.list_audit_events()) == 1


def test_duplicate_idempotency_identity_rejects(kernel: SecurityKernel):
    _initialize(kernel)
    first = _request(
        transaction_id="tx_idempotency_one",
        operation="transition_lifecycle",
        expected_generation=1,
        idempotency_key="same_idempotency",
        payload={
            "source_state": "UNCLAIMED",
            "destination_state": "CLAIM_PENDING",
            "resulting_trust_generation": 2,
        },
    )
    kernel.transition_lifecycle(first)
    second = _request(
        transaction_id="tx_idempotency_two",
        operation="transition_lifecycle",
        expected_generation=1,
        idempotency_key="same_idempotency",
        payload={
            "source_state": "UNCLAIMED",
            "destination_state": "CLAIM_PENDING",
            "resulting_trust_generation": 2,
        },
    )
    with pytest.raises(ReplayConflictError):
        kernel.transition_lifecycle(second)


def test_committed_state_and_audit_survive_reopen(store_path: Path):
    kernel = SecurityKernel(store_path)
    _initialize(kernel)
    _transition(
        kernel,
        transaction_id="tx_reopen",
        expected_generation=1,
        source="UNCLAIMED",
        destination="CLAIM_PENDING",
        resulting_generation=2,
    )
    reopened = SecurityKernel(store_path)
    assert reopened.get_instance_trust().to_dict()["trust_generation"] == 2
    assert [event.transaction_id for event in reopened.list_audit_events()] == [
        "tx_init",
        "tx_reopen",
    ]


@pytest.mark.parametrize(
    ("tamper_sql", "expected_error"),
    [
        (
            "UPDATE owner_security_transactions SET committed_result = '{' WHERE transaction_id = ?",
            SecurityKernelIntegrityError,
        ),
        (
            "UPDATE owner_security_transactions SET result_digest = ? WHERE transaction_id = ?",
            SecurityKernelIntegrityError,
        ),
        (
            "DELETE FROM owner_security_audit_events WHERE transaction_id = ?",
            SecurityKernelIntegrityError,
        ),
        (
            "UPDATE owner_security_audit_events SET trust_generation = 999 WHERE transaction_id = ?",
            SecurityKernelIntegrityError,
        ),
        (
            "UPDATE owner_security_audit_events SET event_kind = 'WRONG' WHERE transaction_id = ?",
            SecurityKernelIntegrityError,
        ),
        (
            "UPDATE owner_security_audit_events SET non_secret_evidence_digest = ? WHERE transaction_id = ?",
            SecurityKernelIntegrityError,
        ),
        (
            "UPDATE owner_security_audit_events SET aether_instance_id = 'other_instance' WHERE transaction_id = ?",
            SecurityKernelIntegrityError,
        ),
        (
            "UPDATE owner_security_transactions SET aether_instance_id = 'other_instance' WHERE transaction_id = ?",
            SecurityKernelIntegrityError,
        ),
    ],
)
def test_tampered_committed_evidence_fails_closed(
    store_path: Path,
    tamper_sql: str,
    expected_error: type[Exception],
):
    kernel = SecurityKernel(store_path)
    _initialize(kernel)
    request = _request(
        transaction_id="tx_tamper",
        operation="transition_lifecycle",
        expected_generation=1,
        payload={
            "source_state": "UNCLAIMED",
            "destination_state": "CLAIM_PENDING",
            "resulting_trust_generation": 2,
        },
    )
    kernel.transition_lifecycle(request)
    with sqlite3.connect(store_path) as connection:
        connection.execute("PRAGMA foreign_keys = OFF")
        if "result_digest = ?" in tamper_sql:
            connection.execute(tamper_sql, ("0" * 64, request.transaction_id))
        elif "non_secret_evidence_digest = ?" in tamper_sql:
            connection.execute(tamper_sql, ("0" * 64, request.transaction_id))
        else:
            connection.execute(tamper_sql, (request.transaction_id,))
        connection.commit()
    with pytest.raises(expected_error):
        kernel.transition_lifecycle(request)


def test_committed_result_tampering_is_detected_on_direct_read(store_path: Path):
    kernel = SecurityKernel(store_path)
    _initialize(kernel)
    request = _request(
        transaction_id="tx_read_tamper",
        operation="transition_lifecycle",
        expected_generation=1,
        payload={
            "source_state": "UNCLAIMED",
            "destination_state": "CLAIM_PENDING",
            "resulting_trust_generation": 2,
        },
    )
    kernel.transition_lifecycle(request)
    with sqlite3.connect(store_path) as connection:
        connection.execute(
            "UPDATE owner_security_transactions SET committed_result = ? WHERE transaction_id = ?",
            ('{"tampered":true}', request.transaction_id),
        )
        connection.commit()
    with pytest.raises(SecurityKernelIntegrityError):
        kernel.get_transaction(request.transaction_id)


def test_concurrent_duplicate_requests_commit_once(store_path: Path):
    kernel = SecurityKernel(store_path)
    _initialize(kernel)
    request = _request(
        transaction_id="tx_concurrent",
        operation="transition_lifecycle",
        expected_generation=1,
        payload={
            "source_state": "UNCLAIMED",
            "destination_state": "CLAIM_PENDING",
            "resulting_trust_generation": 2,
        },
    )

    def invoke(_: int) -> dict:
        return SecurityKernel(store_path).transition_lifecycle(request)

    with ThreadPoolExecutor(max_workers=8) as pool:
        results = list(pool.map(invoke, range(8)))
    assert all(result == results[0] for result in results)
    assert len(SecurityKernel(store_path).list_audit_events()) == 2


def test_records_have_non_secret_serialization_boundaries(kernel: SecurityKernel):
    _initialize(kernel)
    _transition(
        kernel,
        transaction_id="tx_serialization",
        expected_generation=1,
        source="UNCLAIMED",
        destination="CLAIM_PENDING",
        resulting_generation=2,
    )
    instance = kernel.get_instance_trust().to_dict()
    transaction = kernel.get_transaction("tx_serialization").to_dict()
    audit = kernel.list_audit_events()[-1].to_dict()
    encoded = json.dumps([instance, transaction, audit], sort_keys=True)
    assert "password" not in encoded
    assert "private_key" not in encoded
    assert all(spec["secret"] == "NO" for spec in FIELD_CLASSIFICATION.values())
    model_fields = {
        field.name
        for model in (AetherInstanceTrust, OwnerSecurityTransaction, OwnerSecurityAuditEvent)
        for field in fields(model)
    }
    assert model_fields <= set(FIELD_CLASSIFICATION)


def test_secret_bearing_request_fields_are_rejected():
    with pytest.raises(InvalidTransactionError, match="secret-bearing"):
        SecurityTransactionRequest.build(
            transaction_id="tx_secret",
            aether_instance_id=INSTANCE,
            expected_trust_generation=0,
            exact_operation="initialize_instance",
            idempotency_key="id_secret",
            payload={"password": "never persist"},
        )


def test_field_classification_covers_all_persisted_domain_fields():
    persisted = {
        field.name
        for model in (AetherInstanceTrust, OwnerSecurityTransaction, OwnerSecurityAuditEvent)
        for field in fields(model)
    }
    assert persisted <= set(FIELD_CLASSIFICATION)


def test_canonical_json_accepts_exact_resource_limits():
    assert len(_canonical_json("x" * MAX_JSON_STRING_BYTES).encode("utf-8")) <= MAX_JSON_ENCODED_BYTES
    assert len(_canonical_json({"k" * MAX_JSON_KEY_BYTES: 1})) > 0
    assert len(_canonical_json([None] * MAX_JSON_COLLECTION_ITEMS)) > 0
    assert len(_canonical_json(10 ** MAX_JSON_INTEGER_DIGITS - 1)) > 0
    nested: object = "x"
    for _ in range(MAX_JSON_DEPTH):
        nested = [nested]
    assert len(_canonical_json(nested)) > 0
    exact_size = [
        "x" * 4095,
        "x" * 4092,
        "x" * 4092,
        "x" * 4092,
    ]
    assert len(_canonical_json(exact_size).encode("utf-8")) == MAX_JSON_ENCODED_BYTES


@pytest.mark.parametrize(
    "value",
    [
        "x" * (MAX_JSON_STRING_BYTES + 1),
        {"k" * (MAX_JSON_KEY_BYTES + 1): 1},
        [None] * (MAX_JSON_COLLECTION_ITEMS + 1),
        10 ** MAX_JSON_INTEGER_DIGITS,
    ],
)
def test_canonical_json_rejects_resource_limit_overruns(value):
    with pytest.raises(InvalidTransactionError):
        _canonical_json(value)


def test_canonical_json_rejects_depth_and_encoded_size_overruns():
    nested: object = "x"
    for _ in range(MAX_JSON_DEPTH + 1):
        nested = [nested]
    with pytest.raises(InvalidTransactionError, match="depth"):
        _canonical_json(nested)
    oversized = [
        "x" * 4096,
        "x" * 4092,
        "x" * 4092,
        "x" * 4092,
    ]
    with pytest.raises(InvalidTransactionError, match="encoded size"):
        _canonical_json(oversized)
    with pytest.raises(InvalidTransactionError, match="finite"):
        _canonical_json(float("nan"))


def test_oas_module_has_no_ordinary_runtime_or_api_import_boundary_break():
    root = Path(__file__).resolve().parents[1]
    production_root = root / "aether"
    oas_root = production_root / "oas"
    for source_path in production_root.rglob("*.py"):
        if oas_root in source_path.parents:
            continue
        tree = ast.parse(source_path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported = [alias.name for alias in node.names]
                assert not any(name == "aether.oas" or name.startswith("aether.oas.") for name in imported), source_path
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                assert not (
                    module == "aether.oas"
                    or module.startswith("aether.oas.")
                    or (module == "aether" and any(alias.name == "oas" for alias in node.names))
                ), source_path

    for source_path in oas_root.glob("*.py"):
        tree = ast.parse(source_path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported = [alias.name for alias in node.names]
                assert not any(name.startswith("aether") for name in imported), source_path
            elif isinstance(node, ast.ImportFrom):
                assert not (node.module or "").startswith("aether"), source_path


def test_oas_public_package_does_not_expose_mutation_surface():
    import aether.oas as package

    assert package.__all__ == ()
    assert not hasattr(package, "SecurityKernel")
    assert not hasattr(package, "SecurityTransactionRequest")
    assert not hasattr(package, "canonical_request_digest")


def test_oas_kernel_does_not_expose_out_of_scope_security_surfaces():
    import aether.oas.security_kernel as module

    public_names = set(module.__dict__)
    assert not {
        "WebAuthn", "TLS", "OwnerSession", "ClaimToken", "RecoveryRecord",
        "AuthenticatedSourceEvent", "GenericAct",
    } & public_names
    assert not hasattr(module, "issue_authentication")
    assert not hasattr(module, "mint_source_event")
    assert not hasattr(module, "authorize_action")
