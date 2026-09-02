import pytest

from aether.deployment.installer import make_activation_record
from aether.deployment.lifecycle import (
    ActivationState,
    LifecycleError,
    authorize_temporary_root,
    create_isolated_root,
    prove_quiescence,
    validate_record,
)


class FakeManager:
    identity = "fake"

    def snapshot_quiescence(self):
        return {
            "observed_at_monotonic": 1.0,
            "socket_unit_states": {
                "runtime": "inactive",
                "bootstrap": "inactive",
                "broker": "inactive",
            },
            "service_state": "inactive",
            "listener_count": 0,
            "accepted_connection_count": 0,
            "outstanding_worker_count": 0,
            "activation_job_count": 0,
            "oas_process_count": 0,
            "cgroup_populated": False,
        }


def test_quiescence_is_transaction_bound():
    record = make_activation_record(
        transaction_id="tx",
        candidate_release_id="r1-" + "a" * 64,
        candidate_manifest_digest="b" * 64,
        candidate_unit_generation_id="g-" + "c" * 64,
        unit_bundle_digest="d" * 64,
        host_boot_id="boot",
    )
    proof = prove_quiescence(FakeManager(), record, boot_id="boot", now=1.0)
    proof.validate(record, current_boot_id="boot", now=1.0, adapter_identity="fake")
    other = dict(record, transaction_id="other")
    with pytest.raises(LifecycleError):
        proof.validate(other, current_boot_id="boot", now=1.0, adapter_identity="fake")


def test_quiescence_expires_from_observation_not_validation_time():
    record = make_activation_record(
        transaction_id="tx",
        candidate_release_id="r1-" + "a" * 64,
        candidate_manifest_digest="b" * 64,
        candidate_unit_generation_id="g-" + "c" * 64,
        unit_bundle_digest="d" * 64,
        host_boot_id="boot",
    )
    proof = prove_quiescence(FakeManager(), record, boot_id="boot", now=1.0)
    with pytest.raises(LifecycleError):
        proof.validate(record, current_boot_id="boot", now=61.0, adapter_identity="fake")


def test_isolated_root_capability_is_factory_only_and_sentinel_bound(tmp_path):
    with pytest.raises(LifecycleError):
        authorize_temporary_root(tmp_path)
    root, capability = create_isolated_root(
        tmp_path, purpose="M122A_LIFECYCLE", transaction_id="tx_capability"
    )
    sentinel = root / ".aether-temporary-root"
    original = sentinel.read_text(encoding="utf-8")
    sentinel.write_text(original.replace("tx_capability", "tx_tampered"), encoding="utf-8")
    with pytest.raises(LifecycleError):
        from aether.deployment.lifecycle import _require_capability
        _require_capability(root, capability, purpose="M122A_LIFECYCLE")


def test_isolated_root_rejects_protected_parent_and_malformed_snapshot(tmp_path):
    with pytest.raises(LifecycleError):
        create_isolated_root("/etc", purpose="M122A_LIFECYCLE", transaction_id="tx")
    record = make_activation_record(
        transaction_id="tx",
        candidate_release_id="r1-" + "a" * 64,
        candidate_manifest_digest="b" * 64,
        candidate_unit_generation_id="g-" + "c" * 64,
        unit_bundle_digest="d" * 64,
        host_boot_id="boot",
    )
    class MalformedManager:
        identity = "fake"

        def snapshot_quiescence(self):
            return {"observed_at_monotonic": 1.0, "socket_unit_states": {}}

    with pytest.raises(LifecycleError):
        prove_quiescence(MalformedManager(), record, boot_id="boot", now=1.0)


def test_activating_record_requires_a_positive_bounded_window():
    record = make_activation_record(
        transaction_id="tx_window",
        candidate_release_id="r1-" + "a" * 64,
        candidate_manifest_digest="b" * 64,
        candidate_unit_generation_id="g-" + "c" * 64,
        unit_bundle_digest="d" * 64,
        host_boot_id="boot",
    )
    activating = dict(
        record,
        state=ActivationState.ACTIVATING.value,
        quiesce_state="PROVEN",
        activation_issued_at_monotonic=1.0,
        activation_expires_at_monotonic=1.0,
        current_link_release_id=record["candidate_release_id"],
        commit_state="UNCOMMITTED",
    )
    with pytest.raises(LifecycleError):
        validate_record(activating)
