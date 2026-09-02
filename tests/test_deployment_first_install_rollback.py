"""Behavioral locks for the isolated M125A first-install rollback foundation."""

from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone
import fcntl
import hashlib
import json
import os
from pathlib import Path

import pytest

from aether.deployment.first_install_rollback import (
    CreatedObjectRecord,
    FirstInstallRollbackFoundation,
    FirstInstallRollbackTransaction,
    PrivilegedEffectReceipt,
    PrivilegedEffectRequest,
    PrivilegedOperation,
    RollbackError,
    RollbackInterrupted,
    RollbackResult,
    RollbackStorageError,
    RollbackTransactionIdentity,
    _metadata_digest,
    make_privileged_receipt,
    rollback_manifest_digest,
)
from aether.deployment.lifecycle import create_isolated_root
from aether.deployment.manifest_schema import canonical_json_bytes


DIGEST_A = "a" * 64
DIGEST_B = "b" * 64
DIGEST_C = "c" * 64
DIGEST_D = "d" * 64
BOOT = DIGEST_A
NOW = "2026-09-02T00:00:00+00:00"
EXPIRES = "2026-09-02T00:01:00+00:00"


class FakePrivilegedAdapter:
    identity = "test-privileged-adapter"

    def __init__(self) -> None:
        self.apply_requests: list[PrivilegedEffectRequest] = []
        self.observe_requests: list[PrivilegedEffectRequest] = []

    def apply(self, request: PrivilegedEffectRequest) -> PrivilegedEffectReceipt:
        self.apply_requests.append(request)
        return make_privileged_receipt(
            request,
            adapter_identity=self.identity,
            observed_result="APPLIED",
            observed_at_utc=NOW,
            evidence_digest=DIGEST_D,
        )

    def observe(self, request: PrivilegedEffectRequest) -> PrivilegedEffectReceipt:
        self.observe_requests.append(request)
        return make_privileged_receipt(
            request,
            adapter_identity=self.identity,
            observed_result="ABSENT",
            observed_at_utc=NOW,
            evidence_digest=DIGEST_D,
        )


class FailingApplyAdapter(FakePrivilegedAdapter):
    def apply(self, request: PrivilegedEffectRequest) -> PrivilegedEffectReceipt:
        self.apply_requests.append(request)
        raise RuntimeError("adapter failed")


class UncertainObserveAdapter(FakePrivilegedAdapter):
    def observe(self, request: PrivilegedEffectRequest) -> PrivilegedEffectReceipt:
        self.observe_requests.append(request)
        return make_privileged_receipt(
            request,
            adapter_identity=self.identity,
            observed_result="PRESENT",
            observed_at_utc=NOW,
            evidence_digest=DIGEST_D,
        )


def _record(
    transaction_id: str,
    step_id: str,
    order: int,
    *,
    object_type: str,
    path: str | None = None,
    pre_existing: str = "ABSENT",
    content_digest: str = DIGEST_C,
    operation: str | None = None,
) -> CreatedObjectRecord:
    return CreatedObjectRecord(
        transaction_id=transaction_id,
        step_id=step_id,
        object_class="rollback-test-object",
        logical_target=path or operation or "privileged-target",
        root_relative_path=path,
        pre_existing_state=pre_existing,
        expected_type=object_type,
        expected_ownership_identity=f"{os.getuid()}:{os.getgid()}",
        expected_mode=None,
        expected_content_or_metadata_digest=content_digest,
        creation_evidence_digest=DIGEST_D,
        dependency_order=order,
        inverse_action="REMOVE_TRANSACTION_OBJECT",
        automatic_rollback_permitted=True,
        privileged_operation=operation,
    )


def _transaction(transaction_id: str, records: tuple[CreatedObjectRecord, ...], *, boot: str = BOOT, **flags) -> FirstInstallRollbackTransaction:
    identity = RollbackTransactionIdentity(
        transaction_id=transaction_id,
        deployment_profile="FIRST_INSTALL_LOCAL_AF_UNIX_ONLY",
        target_host_identity_digest=DIGEST_A,
        boot_digest=boot,
        source_commit="e" * 40,
        release_id="r1-" + DIGEST_B,
        manifest_digest=DIGEST_B,
        mutation_manifest_digest=DIGEST_C,
        rollback_manifest_digest=rollback_manifest_digest(records),
        authorization_digest=DIGEST_D,
        created_at_utc=NOW,
        expires_at_utc=EXPIRES,
        record_sequence=0,
    )
    return FirstInstallRollbackTransaction(identity, records, **flags)


def _foundation(tmp_path: Path, transaction_id: str, *, now: str = NOW, fault=None, boot: str = BOOT):
    root, capability = create_isolated_root(
        tmp_path,
        purpose="M125A_ROLLBACK",
        transaction_id=transaction_id,
    )
    return root, capability, FirstInstallRollbackFoundation(
        root,
        capability=capability,
        current_boot_digest=boot,
        now_utc=lambda: now,
        fault_injector=fault,
    )


def _regular_file(root: Path, transaction_id: str, relative: str, content: bytes = b"created") -> CreatedObjectRecord:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)
    os.chmod(path, 0o640)
    info = path.lstat()
    return _record(
        transaction_id,
        "file-step",
        1,
        object_type="regular",
        path=relative,
        content_digest=hashlib.sha256(content).hexdigest(),
    )


def _successful_privileged(tmp_path: Path, transaction_id: str = "tx-receipts"):
    root, capability, foundation = _foundation(tmp_path, transaction_id)
    record = _record(
        transaction_id,
        "service-stop",
        1,
        object_type="privileged",
        operation=PrivilegedOperation.STOP_SELECTED_OAS_SERVICE_SOCKET_SET.value,
    )
    transaction = _transaction(transaction_id, (record,))
    adapter = FakePrivilegedAdapter()
    assert foundation.run(transaction, adapter=adapter) is RollbackResult.ROLLED_BACK_NOT_DEPLOYED
    return root, capability, foundation, transaction, adapter


def _receipt_records(foundation: FirstInstallRollbackFoundation) -> list[dict]:
    return [json.loads(line) for line in foundation.receipt_path.read_text(encoding="ascii").splitlines()]


def _write_receipt_records(foundation: FirstInstallRollbackFoundation, records: list[dict]) -> None:
    foundation.receipt_path.write_bytes(
        b"".join(canonical_json_bytes(record) + b"\n" for record in records)
    )


def _rechain_receipt_record(record: dict, previous: str | None) -> dict:
    result = dict(record)
    result["previous_receipt_record_digest"] = previous
    result.pop("current_receipt_record_digest", None)
    result["current_receipt_record_digest"] = hashlib.sha256(canonical_json_bytes(result)).hexdigest()
    return result


def test_first_install_removes_only_transaction_objects_and_proves_final_state(tmp_path):
    root, capability, foundation = _foundation(tmp_path, "tx-files")
    record = _regular_file(root, "tx-files", "opt/aether/candidate.bin")
    transaction = _transaction("tx-files", (record,))

    result = foundation.run(transaction, adapter=FakePrivilegedAdapter())

    assert result is RollbackResult.ROLLED_BACK_NOT_DEPLOYED
    assert not (root / "opt/aether/candidate.bin").exists()
    lines = foundation.journal_path.read_text(encoding="ascii").splitlines()
    assert lines[-1].find("ROLLED_BACK_NOT_DEPLOYED") >= 0
    assert capability.transaction_id == transaction.identity.transaction_id


def test_preexisting_object_is_verified_and_never_removed(tmp_path):
    root, _capability, foundation = _foundation(tmp_path, "tx-preexisting")
    path = root / "opt/aether/preexisting.bin"
    path.parent.mkdir(parents=True)
    path.write_bytes(b"owner-data")
    record = _record(
        "tx-preexisting",
        "existing-step",
        1,
        object_type="regular",
        path="opt/aether/preexisting.bin",
        pre_existing="PRESENT",
        content_digest=hashlib.sha256(b"owner-data").hexdigest(),
    )

    assert foundation.run(_transaction("tx-preexisting", (record,)), adapter=FakePrivilegedAdapter()) is RollbackResult.ROLLED_BACK_NOT_DEPLOYED
    assert path.read_bytes() == b"owner-data"


def test_reverse_dependency_order_is_durable(tmp_path):
    root, _capability, foundation = _foundation(tmp_path, "tx-order")
    parent = root / "created"
    child = parent / "child"
    parent.mkdir()
    os.chmod(parent, 0o750)
    parent_digest = _metadata_digest(parent, parent.lstat())
    child.write_bytes(b"child")
    parent_record = _record(
        "tx-order", "parent", 1, object_type="directory", path="created", content_digest=parent_digest
    )
    child_record = _record(
        "tx-order", "child", 2, object_type="regular", path="created/child", content_digest=hashlib.sha256(b"child").hexdigest()
    )
    assert foundation.run(_transaction("tx-order", (parent_record, child_record)), adapter=FakePrivilegedAdapter()) is RollbackResult.ROLLED_BACK_NOT_DEPLOYED
    assert not parent.exists()


def test_symlink_is_removed_without_following_target(tmp_path):
    root, _capability, foundation = _foundation(tmp_path, "tx-link")
    target = tmp_path / "outside-target"
    target.write_text("must remain", encoding="ascii")
    link = root / "link"
    link.symlink_to(target)
    record = _record(
        "tx-link", "link-step", 1, object_type="symlink", path="link", content_digest=_metadata_digest(link, link.lstat())
    )

    assert foundation.run(_transaction("tx-link", (record,)), adapter=FakePrivilegedAdapter()) is RollbackResult.ROLLED_BACK_NOT_DEPLOYED
    assert not link.exists()
    assert target.read_text(encoding="ascii") == "must remain"


def test_identity_mismatch_requires_root_review_and_preserves_object(tmp_path):
    root, _capability, foundation = _foundation(tmp_path, "tx-mismatch")
    record = _regular_file(root, "tx-mismatch", "candidate.bin")
    (root / "candidate.bin").write_bytes(b"changed")

    result = foundation.run(_transaction("tx-mismatch", (record,)), adapter=FakePrivilegedAdapter())

    assert result is RollbackResult.PARTIAL_ROLLBACK_ROOT_REVIEW_REQUIRED
    assert (root / "candidate.bin").read_bytes() == b"changed"
    assert "IDENTITY_MISMATCH" in foundation.journal_path.read_text(encoding="ascii")


def test_hard_link_identity_is_ambiguous_and_not_removed(tmp_path):
    root, _capability, foundation = _foundation(tmp_path, "tx-hardlink")
    path = root / "candidate.bin"
    path.write_bytes(b"shared")
    sibling = root / "sibling.bin"
    sibling.hardlink_to(path)
    record = _record(
        "tx-hardlink", "hardlink-step", 1, object_type="regular", path="candidate.bin", content_digest=hashlib.sha256(b"shared").hexdigest()
    )

    assert foundation.run(_transaction("tx-hardlink", (record,)), adapter=FakePrivilegedAdapter()) is RollbackResult.PARTIAL_ROLLBACK_ROOT_REVIEW_REQUIRED
    assert path.exists() and sibling.exists()


def test_symlink_parent_and_path_escape_fail_closed(tmp_path):
    root, _capability, foundation = _foundation(tmp_path, "tx-path")
    outside = tmp_path / "outside"
    outside.mkdir()
    (root / "unsafe").symlink_to(outside, target_is_directory=True)
    record = _record("tx-path", "path-step", 1, object_type="regular", path="unsafe/file", content_digest=DIGEST_C)

    assert foundation.run(_transaction("tx-path", (record,)), adapter=FakePrivilegedAdapter()) is RollbackResult.PARTIAL_ROLLBACK_ROOT_REVIEW_REQUIRED
    assert not (outside / "file").exists()


def test_privileged_effect_is_adapter_bound_and_observed(tmp_path):
    root, _capability, foundation = _foundation(tmp_path, "tx-privileged")
    record = _record(
        "tx-privileged",
        "service-stop",
        1,
        object_type="privileged",
        operation=PrivilegedOperation.STOP_SELECTED_OAS_SERVICE_SOCKET_SET.value,
    )
    adapter = FakePrivilegedAdapter()

    assert foundation.run(_transaction("tx-privileged", (record,)), adapter=adapter) is RollbackResult.ROLLED_BACK_NOT_DEPLOYED
    assert len(adapter.apply_requests) == 1
    assert len(adapter.observe_requests) == 1
    assert foundation.receipt_path.read_text(encoding="ascii").count("receipt_digest") == 2


@pytest.mark.parametrize(
    "fault_point",
    (
        "before_rollback_intent_persistence",
        "after_rollback_intent_persistence",
        "before_final_verification",
        "after_final_verification_before_final_record",
    ),
)
def test_injected_crash_points_preserve_durable_evidence_and_resume(tmp_path, fault_point):
    fired = False

    def fault(point: str) -> None:
        nonlocal fired
        if point == fault_point and not fired:
            fired = True
            raise RollbackInterrupted(point)

    root, capability, first = _foundation(tmp_path, "tx-crash", fault=fault)
    record = _record("tx-crash", "service-stop", 1, object_type="privileged", operation=PrivilegedOperation.STOP_SELECTED_OAS_SERVICE_SOCKET_SET.value)
    transaction = _transaction("tx-crash", (record,))
    adapter = FakePrivilegedAdapter()
    with pytest.raises(RollbackInterrupted):
        first.run(transaction, adapter=adapter)

    resumed = FirstInstallRollbackFoundation(
        root,
        capability=capability,
        current_boot_digest=BOOT,
        now_utc=lambda: NOW,
    ).run(transaction, adapter=adapter)
    assert resumed is RollbackResult.ROLLED_BACK_NOT_DEPLOYED


def test_crash_after_receipt_does_not_reapply_privileged_effect(tmp_path):
    fired = False

    def fault(point: str) -> None:
        nonlocal fired
        if point == "after_mutation_before_receipt:service-stop" and not fired:
            fired = True
            raise RollbackInterrupted(point)

    root, capability, first = _foundation(tmp_path, "tx-receipt", fault=fault)
    record = _record("tx-receipt", "service-stop", 1, object_type="privileged", operation=PrivilegedOperation.STOP_SELECTED_OAS_SERVICE_SOCKET_SET.value)
    transaction = _transaction("tx-receipt", (record,))
    adapter = FakePrivilegedAdapter()
    with pytest.raises(RollbackInterrupted):
        first.run(transaction, adapter=adapter)
    assert len(adapter.apply_requests) == 1
    assert not first.receipt_path.exists()

    resumed = FirstInstallRollbackFoundation(root, capability=capability, current_boot_digest=BOOT, now_utc=lambda: NOW).run(transaction, adapter=adapter)
    assert resumed is RollbackResult.ROLLED_BACK_NOT_DEPLOYED
    assert len(adapter.apply_requests) == 1


def test_expiry_boot_and_capability_identity_are_rejected_without_mutation(tmp_path):
    root, capability, foundation = _foundation(tmp_path, "tx-rejected", now=EXPIRES)
    record = _regular_file(root, "tx-rejected", "candidate.bin")
    transaction = _transaction("tx-rejected", (record,))
    assert foundation.run(transaction, adapter=FakePrivilegedAdapter()) is RollbackResult.REJECTED_EXPIRED
    assert (root / "candidate.bin").exists()

    _root2, _capability2, boot_mismatch = _foundation(tmp_path, "tx-boot", boot=DIGEST_B)
    boot_record = _record("tx-boot", "file", 1, object_type="regular", path="missing", content_digest=DIGEST_C)
    assert boot_mismatch.run(_transaction("tx-boot", (boot_record,)), adapter=FakePrivilegedAdapter()) is RollbackResult.REJECTED_IDENTITY_MISMATCH

    other_root, other_capability, other_foundation = _foundation(tmp_path, "tx-other")
    other_record = _record("tx-other", "file", 1, object_type="regular", path="missing", content_digest=DIGEST_C)
    wrong_transaction = _transaction("tx-wrong", (other_record,))
    assert other_foundation.run(wrong_transaction, adapter=FakePrivilegedAdapter()) is RollbackResult.REJECTED_IDENTITY_MISMATCH
    assert capability.root == root
    assert other_capability.root == other_root


def test_upgrade_migration_and_adoption_are_out_of_scope(tmp_path):
    _root, _capability, foundation = _foundation(tmp_path, "tx-scope")
    record = _record("tx-scope", "file", 1, object_type="regular", path="missing", content_digest=DIGEST_C)
    for flags in ({"previous_release_id": "r1-" + DIGEST_A}, {"schema_migration_requested": True}, {"adoption_requested": True}):
        transaction = _transaction("tx-scope", (record,), **flags)
        assert foundation.run(transaction, adapter=FakePrivilegedAdapter()) is RollbackResult.REJECTED_UNSUPPORTED_PROFILE


def test_corrupt_journal_and_receipt_are_storage_failures(tmp_path):
    _root, _capability, foundation = _foundation(tmp_path, "tx-storage")
    foundation.journal_path.parent.mkdir(parents=True)
    foundation.journal_path.write_text('{"not":"a valid chain"}\n', encoding="ascii")
    record = _record("tx-storage", "file", 1, object_type="regular", path="missing", content_digest=DIGEST_C)
    with pytest.raises(RollbackStorageError):
        foundation.run(_transaction("tx-storage", (record,)), adapter=FakePrivilegedAdapter())


def test_lock_timeout_is_bounded(tmp_path):
    root, _capability, foundation = _foundation(tmp_path, "tx-lock")
    record = _record("tx-lock", "file", 1, object_type="regular", path="missing", content_digest=DIGEST_C)
    lock_path = root / "var/lib/aether/rollback/rollback.lock"
    lock_path.parent.mkdir(parents=True)
    with lock_path.open("a+") as holder:
        fcntl.flock(holder.fileno(), fcntl.LOCK_EX)
        bounded = FirstInstallRollbackFoundation(root, capability=foundation.capability, current_boot_digest=BOOT, now_utc=lambda: NOW, lock_timeout_seconds=0.01)
        assert bounded.run(_transaction("tx-lock", (record,)), adapter=FakePrivilegedAdapter()) is RollbackResult.REJECTED_CONFLICT
        fcntl.flock(holder.fileno(), fcntl.LOCK_UN)


def test_storage_write_failure_is_not_mapped_to_success(tmp_path, monkeypatch):
    _root, _capability, foundation = _foundation(tmp_path, "tx-write")
    record = _record("tx-write", "file", 1, object_type="regular", path="missing", content_digest=DIGEST_C)

    def fail(*_args, **_kwargs):
        raise RollbackStorageError("injected storage failure")

    monkeypatch.setattr(foundation, "_append_line", fail)
    with pytest.raises(RollbackStorageError):
        foundation.run(_transaction("tx-write", (record,)), adapter=FakePrivilegedAdapter())


def test_receipt_binding_and_typed_request_are_closed():
    request = PrivilegedEffectRequest.create("tx", "step", PrivilegedOperation.VERIFY_PROCESS_ABSENCE.value, "OBSERVE", BOOT)
    receipt = make_privileged_receipt(
        request,
        adapter_identity="adapter",
        observed_result="ABSENT",
        observed_at_utc=NOW,
        evidence_digest=DIGEST_D,
    )
    assert receipt.request_digest == request.request_digest
    with pytest.raises(ValueError):
        make_privileged_receipt(request, adapter_identity="contains-secret", observed_result="ABSENT", observed_at_utc=NOW, evidence_digest=DIGEST_D)
    with pytest.raises(ValueError):
        PrivilegedEffectRequest.create("tx", "step", "RUN_SHELL", "OBSERVE", BOOT)


def test_constructor_rejects_non_isolated_or_wrong_capability(tmp_path):
    with pytest.raises(RollbackError):
        FirstInstallRollbackFoundation("/tmp", capability=object(), current_boot_digest=BOOT)  # type: ignore[arg-type]


def test_started_rollback_resumes_after_authorization_expiry(tmp_path):
    fired = False

    def fault(point: str) -> None:
        nonlocal fired
        if point == "after_rollback_intent_persistence" and not fired:
            fired = True
            raise RollbackInterrupted(point)

    root, capability, first = _foundation(tmp_path, "tx-expiry-resume", fault=fault)
    record = _record(
        "tx-expiry-resume", "service-stop", 1, object_type="privileged", operation=PrivilegedOperation.STOP_SELECTED_OAS_SERVICE_SOCKET_SET.value
    )
    transaction = _transaction("tx-expiry-resume", (record,))
    adapter = FakePrivilegedAdapter()
    with pytest.raises(RollbackInterrupted):
        first.run(transaction, adapter=adapter)

    resumed = FirstInstallRollbackFoundation(
        root,
        capability=capability,
        current_boot_digest=BOOT,
        now_utc=lambda: "2026-09-02T00:02:00+00:00",
    ).run(transaction, adapter=adapter)
    assert resumed is RollbackResult.ROLLED_BACK_NOT_DEPLOYED
    assert len(adapter.apply_requests) == 1


def test_retry_rejects_changed_authorization_and_manifest_scope(tmp_path):
    fired = False

    def fault(point: str) -> None:
        nonlocal fired
        if point == "after_rollback_intent_persistence" and not fired:
            fired = True
            raise RollbackInterrupted(point)

    root, capability, first = _foundation(tmp_path, "tx-frozen", fault=fault)
    record = _record("tx-frozen", "service-stop", 1, object_type="privileged", operation=PrivilegedOperation.STOP_SELECTED_OAS_SERVICE_SOCKET_SET.value)
    transaction = _transaction("tx-frozen", (record,))
    with pytest.raises(RollbackInterrupted):
        first.run(transaction, adapter=FakePrivilegedAdapter())

    changed_authorization = replace(
        transaction,
        identity=replace(transaction.identity, authorization_digest=DIGEST_C),
    )
    assert FirstInstallRollbackFoundation(root, capability=capability, current_boot_digest=BOOT, now_utc=lambda: NOW).run(
        changed_authorization, adapter=FakePrivilegedAdapter()
    ) is RollbackResult.REJECTED_CONFLICT

    extra = _record("tx-frozen", "extra", 2, object_type="privileged", operation=PrivilegedOperation.VERIFY_PROCESS_ABSENCE.value)
    added = _transaction("tx-frozen", (record, extra))
    removed = _transaction("tx-frozen", ())
    changed_operation = _transaction(
        "tx-frozen",
        (_record("tx-frozen", "service-stop", 1, object_type="privileged", operation=PrivilegedOperation.VERIFY_PROCESS_ABSENCE.value),),
    )
    runner = FirstInstallRollbackFoundation(root, capability=capability, current_boot_digest=BOOT, now_utc=lambda: NOW)
    assert runner.run(added, adapter=FakePrivilegedAdapter()) is RollbackResult.REJECTED_CONFLICT
    assert runner.run(removed, adapter=FakePrivilegedAdapter()) is RollbackResult.REJECTED_CONFLICT
    assert runner.run(changed_operation, adapter=FakePrivilegedAdapter()) is RollbackResult.REJECTED_CONFLICT


def test_missing_object_and_unknown_directory_child_never_prove_not_deployed(tmp_path):
    _root, _capability, foundation = _foundation(tmp_path, "tx-missing")
    missing = _record("tx-missing", "missing", 1, object_type="regular", path="missing.bin")
    assert foundation.run(_transaction("tx-missing", (missing,)), adapter=FakePrivilegedAdapter()) is RollbackResult.PARTIAL_ROLLBACK_ROOT_REVIEW_REQUIRED

    root, _capability, child_foundation = _foundation(tmp_path, "tx-unknown-child")
    directory = root / "directory"
    directory.mkdir()
    os.chmod(directory, 0o750)
    directory_digest = _metadata_digest(directory, directory.lstat())
    (directory / "unknown").write_bytes(b"unknown")
    directory_record = _record("tx-unknown-child", "directory", 1, object_type="directory", path="directory", content_digest=directory_digest)
    assert child_foundation.run(_transaction("tx-unknown-child", (directory_record,)), adapter=FakePrivilegedAdapter()) is RollbackResult.PARTIAL_ROLLBACK_ROOT_REVIEW_REQUIRED
    assert (directory / "unknown").exists()


def test_receipt_record_contains_a_complete_chain_and_terminal_absence_receipt(tmp_path):
    _root, _capability, foundation, transaction, _adapter = _successful_privileged(tmp_path)
    records = _receipt_records(foundation)
    assert [record["receipt_sequence"] for record in records] == [1, 2]
    assert records[0]["previous_receipt_record_digest"] is None
    assert records[1]["previous_receipt_record_digest"] == records[0]["current_receipt_record_digest"]
    assert {record["request_phase"] for record in records} == {"APPLY", "OBSERVE"}
    assert {record["transaction_id"] for record in records} == {transaction.identity.transaction_id}
    assert records[1]["observed_result"] == "ABSENT"


@pytest.mark.parametrize("tamper", ("record_digest", "broken_chain", "reordered"))
def test_receipt_chain_tampering_is_rejected(tmp_path, tamper):
    _root, _capability, foundation, _transaction_value, adapter = _successful_privileged(tmp_path, "tx-chain")
    records = _receipt_records(foundation)
    if tamper == "record_digest":
        records[0]["current_receipt_record_digest"] = DIGEST_C
    elif tamper == "broken_chain":
        records[1]["previous_receipt_record_digest"] = DIGEST_C
    else:
        records.reverse()
    _write_receipt_records(foundation, records)
    with pytest.raises(RollbackStorageError):
        foundation.run(_transaction_value, adapter=adapter)


def test_conflicting_duplicate_receipt_is_rejected(tmp_path):
    _root, _capability, foundation, transaction, adapter = _successful_privileged(tmp_path, "tx-duplicate")
    records = _receipt_records(foundation)
    request = PrivilegedEffectRequest.create(
        transaction.identity.transaction_id,
        "service-stop",
        PrivilegedOperation.STOP_SELECTED_OAS_SERVICE_SOCKET_SET.value,
        "APPLY",
        BOOT,
    )
    receipt = make_privileged_receipt(
        request,
        adapter_identity=adapter.identity,
        observed_result="APPLIED",
        observed_at_utc="2026-09-02T00:00:01+00:00",
        evidence_digest=DIGEST_C,
    )
    duplicate = {
        "receipt_sequence": 3,
        "previous_receipt_record_digest": records[-1]["current_receipt_record_digest"],
        "transaction_id": receipt.transaction_id,
        "step_id": receipt.step_id,
        "request_phase": request.phase,
        "request_digest": receipt.request_digest,
        "receipt_digest": hashlib.sha256(canonical_json_bytes(receipt.as_dict())).hexdigest(),
        "boot_digest": receipt.boot_digest,
        "adapter_identity": receipt.adapter_identity,
        "operation": receipt.operation,
        "observed_result": receipt.observed_result,
        "observed_at_utc": receipt.observed_at_utc,
        "evidence_digest": receipt.evidence_digest,
        "receipt": receipt.as_dict(),
    }
    duplicate["current_receipt_record_digest"] = hashlib.sha256(canonical_json_bytes(duplicate)).hexdigest()
    records.append(duplicate)
    _write_receipt_records(foundation, records)
    with pytest.raises(RollbackStorageError):
        foundation.run(transaction, adapter=adapter)


def test_missing_or_truncated_receipt_prevents_terminal_success(tmp_path):
    _root, _capability, foundation, transaction, adapter = _successful_privileged(tmp_path, "tx-truncated")
    records = _receipt_records(foundation)
    _write_receipt_records(foundation, records[:1])
    with pytest.raises(RollbackStorageError):
        foundation.run(transaction, adapter=adapter)


def test_identical_durable_receipt_retry_is_idempotent(tmp_path):
    _root, _capability, foundation, transaction, adapter = _successful_privileged(tmp_path, "tx-idempotent")
    before = foundation.receipt_path.read_bytes()
    apply_count = len(adapter.apply_requests)
    observe_count = len(adapter.observe_requests)
    assert foundation.run(transaction, adapter=adapter) is RollbackResult.ROLLED_BACK_NOT_DEPLOYED
    assert foundation.receipt_path.read_bytes() == before
    assert len(adapter.apply_requests) == apply_count
    assert len(adapter.observe_requests) == observe_count


def test_receipt_adapter_boot_and_request_mismatch_are_rejected(tmp_path):
    _root, _capability, foundation, transaction, adapter = _successful_privileged(tmp_path, "tx-receipt-binding")
    different_adapter = FakePrivilegedAdapter()
    different_adapter.identity = "different-adapter"
    assert foundation.run(transaction, adapter=different_adapter) is RollbackResult.REJECTED_IDENTITY_MISMATCH

    records = _receipt_records(foundation)
    receipt = dict(records[0]["receipt"])
    receipt["boot_digest"] = DIGEST_C
    records[0]["boot_digest"] = DIGEST_C
    records[0]["receipt"] = receipt
    records[0]["receipt_digest"] = hashlib.sha256(canonical_json_bytes(receipt)).hexdigest()
    records[0] = _rechain_receipt_record(records[0], None)
    records[1] = _rechain_receipt_record(records[1], records[0]["current_receipt_record_digest"])
    _write_receipt_records(foundation, records)
    assert foundation.run(transaction, adapter=adapter) is RollbackResult.REJECTED_IDENTITY_MISMATCH

    records = _receipt_records(foundation)
    receipt = dict(records[0]["receipt"])
    receipt["boot_digest"] = BOOT
    receipt["request_digest"] = DIGEST_C
    records[0]["boot_digest"] = BOOT
    records[0]["request_digest"] = DIGEST_C
    records[0]["receipt"] = receipt
    records[0]["receipt_digest"] = hashlib.sha256(canonical_json_bytes(receipt)).hexdigest()
    records[0] = _rechain_receipt_record(records[0], None)
    records[1] = _rechain_receipt_record(records[1], records[0]["current_receipt_record_digest"])
    _write_receipt_records(foundation, records)
    assert foundation.run(transaction, adapter=adapter) is RollbackResult.REJECTED_IDENTITY_MISMATCH


def test_final_verification_requires_absence_and_uncertain_effect_fails_closed(tmp_path):
    _root, _capability, foundation, transaction, _adapter = _successful_privileged(tmp_path, "tx-no-absence")
    records = _receipt_records(foundation)
    _write_receipt_records(foundation, records[:1])
    with pytest.raises(RollbackStorageError):
        foundation.run(transaction, adapter=FakePrivilegedAdapter())

    _root2, _capability2, uncertain_foundation = _foundation(tmp_path, "tx-uncertain")
    uncertain_record = _record("tx-uncertain", "service-stop", 1, object_type="privileged", operation=PrivilegedOperation.STOP_SELECTED_OAS_SERVICE_SOCKET_SET.value)
    uncertain_transaction = _transaction("tx-uncertain", (uncertain_record,))
    assert uncertain_foundation.run(uncertain_transaction, adapter=UncertainObserveAdapter()) is RollbackResult.PARTIAL_ROLLBACK_ROOT_REVIEW_REQUIRED


def test_adapter_failure_and_fsync_failure_are_not_success(tmp_path, monkeypatch):
    _root, _capability, foundation = _foundation(tmp_path, "tx-adapter-failure")
    record = _record("tx-adapter-failure", "service-stop", 1, object_type="privileged", operation=PrivilegedOperation.STOP_SELECTED_OAS_SERVICE_SOCKET_SET.value)
    assert foundation.run(_transaction("tx-adapter-failure", (record,)), adapter=FailingApplyAdapter()) is RollbackResult.PARTIAL_ROLLBACK_ROOT_REVIEW_REQUIRED

    _root2, _capability2, fsync_foundation = _foundation(tmp_path, "tx-fsync")
    fsync_record = _record("tx-fsync", "file", 1, object_type="regular", path="missing", content_digest=DIGEST_C)
    original_fsync = os.fsync

    def fail_fsync(_fd: int) -> None:
        raise OSError("injected fsync failure")

    monkeypatch.setattr(os, "fsync", fail_fsync)
    with pytest.raises(RollbackStorageError):
        fsync_foundation.run(_transaction("tx-fsync", (fsync_record,)), adapter=FakePrivilegedAdapter())
    monkeypatch.setattr(os, "fsync", original_fsync)
