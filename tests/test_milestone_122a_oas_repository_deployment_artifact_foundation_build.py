"""Behavioral locks for the repository-only M122A deployment artifact build."""

from __future__ import annotations

import json
from pathlib import Path
import re
import socket
import threading
from types import SimpleNamespace

import pytest

from aether.deployment.evidence_collector import collect_evidence
from aether.deployment.installer import InstallError, RepositoryInstaller, make_activation_record
from aether.deployment.lifecycle import ActivationState, LifecycleError, create_isolated_root, transition, write_record
from aether.deployment.manifest_schema import (
    ManifestError,
    canonical_json_bytes,
    parse_canonical_json,
    release_id_for_digest,
)
from aether.deployment.unit_verifier import (
    UNIT_NAMES,
    generation_id,
    verify_unit_directory,
)
from aether.oas.host_entrypoint import validate_environment
from aether.oas.systemd_notify import NotificationError, notify_ready


ROOT = Path(__file__).resolve().parents[1]
UNIT_DIR = ROOT / "deployment/systemd"
M122A_STATUS = {
    "M122A_AUTHORIZED": "YES",
    "M122A_STARTED": "YES",
    "M122A_FINALIZED": "YES",
    "DECISION_STATUS": "CURRENT",
    "DESIGN_STATUS": "DESIGN_PROVEN",
    "IMPLEMENTATION_STATUS": "IMPLEMENTED",
    "VERIFICATION_STATUS": "TEST_VERIFIED",
    "DEPLOYMENT_VERIFIED": "NO",
    "SELECTED_EXIT": "EXIT_A",
    "BUILD_AUTHORIZED": "YES",
    "HOST_MUTATION_PERFORMED": "NO",
    "PROGRESS_UPDATED": "YES",
    "COMMIT_CREATED": "YES",
    "TAG_CREATED": "YES",
    "PUSH_PERFORMED": "YES",
    "SUCCESSOR_AUTHORIZED": "NO",
    "SUCCESSOR_NUMBER_ASSIGNED": "NO",
    "READY_FOR_PM_REVIEW": "NO",
}


def _authoritative_m122a_status(document: str) -> str:
    section = document[document.index("## 6. Authoritative Status") :]
    match = re.search(r"```text\n(.*?)\n```", section, re.DOTALL)
    assert match is not None
    return match.group(1)


def test_four_units_are_complete_ordered_and_generation_bound():
    generation, digest = verify_unit_directory(UNIT_DIR)
    assert generation.startswith("g-") and len(generation) == 66
    assert digest == generation[2:]
    assert UNIT_NAMES == (
        "aether-oas.service",
        "aether-oas-runtime.socket",
        "aether-oas-bootstrap.socket",
        "aether-oas-broker.socket",
    )
    service = (UNIT_DIR / UNIT_NAMES[0]).read_text(encoding="utf-8")
    assert "Sockets=aether-oas-runtime.socket aether-oas-bootstrap.socket aether-oas-broker.socket" in service
    assert "ExecStart=/opt/aether/current/runtime/bin/python -I -B -S -c" in service
    assert "READY=1" not in service


def test_canonical_json_rejects_duplicate_and_noncanonical_artifacts():
    data = canonical_json_bytes({"z": 1, "a": "x"})
    assert data == b'{"a":"x","z":1}'
    assert parse_canonical_json(data) == {"a": "x", "z": 1}
    with pytest.raises(ManifestError):
        parse_canonical_json(b'{"a":1,"a":2}')
    with pytest.raises(ManifestError):
        parse_canonical_json(b'{"z":1,"a":"x"}')
    assert release_id_for_digest("a" * 64) == "r1-" + "a" * 64


def test_activation_cannot_commit_without_readiness_and_smoke(tmp_path: Path):
    record = make_activation_record(
        transaction_id="tx_first",
        candidate_release_id="r1-" + "a" * 64,
        candidate_manifest_digest="b" * 64,
        candidate_unit_generation_id="g-" + "c" * 64,
        unit_bundle_digest="d" * 64,
        host_boot_id="boot",
    )
    root, capability = create_isolated_root(
        tmp_path, purpose="M122A_LIFECYCLE", transaction_id="tx_first"
    )
    write_record(root, record, capability=capability)
    with pytest.raises(LifecycleError):
        transition(record, ActivationState.COMMITTED)
    pending = transition(record, ActivationState.QUIESCE_REQUIRED, quiesce_state="PROVEN")
    activating = transition(
        pending,
        ActivationState.ACTIVATING,
        activation_issued_at_monotonic=1.0,
        activation_expires_at_monotonic=2.0,
        current_link_release_id=record["candidate_release_id"],
    )
    ready = dict(activating, readiness_result="PASSED", smoke_result="PASSED")
    committed = transition(ready, ActivationState.COMMITTED)
    assert committed["commit_state"] == "COMMITTED"


def test_installer_rejects_host_root_and_produces_gate_in_temporary_root(tmp_path: Path):
    with pytest.raises(InstallError):
        RepositoryInstaller("/")
    units = {name: (UNIT_DIR / name).read_bytes() for name in UNIT_NAMES}
    generation = generation_id(units)
    record = make_activation_record(
        transaction_id="tx_units",
        candidate_release_id="r1-" + "a" * 64,
        candidate_manifest_digest="b" * 64,
        candidate_unit_generation_id=generation,
        unit_bundle_digest=__import__("hashlib").sha256(b"units").hexdigest(),
        host_boot_id="boot",
    )
    root, capability = create_isolated_root(
        tmp_path, purpose="M122A_INSTALLER", transaction_id="tx_units"
    )
    installer = RepositoryInstaller(root, capability=capability)
    manager = SimpleNamespace(
        identity="fake",
        snapshot_quiescence=lambda: {
            "observed_at_monotonic": 1.0,
            "socket_unit_states": {
                name: "inactive" for name in ("runtime", "bootstrap", "broker")
            },
            "service_state": "inactive",
            "listener_count": 0,
            "accepted_connection_count": 0,
            "outstanding_worker_count": 0,
            "activation_job_count": 0,
            "oas_process_count": 0,
            "cgroup_populated": False,
        },
    )
    from aether.deployment.lifecycle import prove_quiescence
    proof = prove_quiescence(manager, record, boot_id="boot", now=1.0)
    generation, gate_digest = installer.replace_unit_bundle(
        units,
        "tx_units",
        activation_record=record,
        quiescence_proof=proof,
        current_boot_id="boot",
        now=1.0,
        adapter_identity="fake",
    )
    assert generation == generation_id(units)
    assert len(gate_digest) == 64
    gate = root / "var/lib/aether/activation/unit-generations" / f"{generation}.ready"
    assert json.loads(gate.read_text(encoding="utf-8"))["status"] == "VERIFIED"


def test_environment_snapshots_protocol_and_ignores_manager_metadata():
    environment = {
        "LISTEN_PID": "123",
        "LISTEN_FDS": "3",
        "LISTEN_FDNAMES": "runtime:bootstrap:broker",
        "NOTIFY_SOCKET": "@aether-notify",
        "LANG": "C.UTF-8",
        "LC_ALL": "C.UTF-8",
        "TZ": "UTC",
        "HOME": "/var/empty",
        "INVOCATION_ID": "ambient",
        "PATH": "/poisoned",
    }
    snapshot = validate_environment(environment, pid=123)
    assert snapshot["NOTIFY_SOCKET"] == "@aether-notify"
    assert "INVOCATION_ID" not in snapshot
    with pytest.raises(Exception):
        validate_environment({**environment, "LISTEN_FDS": "2"}, pid=123)


def test_native_notification_uses_datagram_and_never_subprocess(tmp_path: Path):
    path = tmp_path / "notify.sock"
    receiver = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
    receiver.bind(str(path))
    try:
        notify_ready(environment={"NOTIFY_SOCKET": str(path)})
        receiver.settimeout(1.0)
        assert receiver.recv(128) == b"READY=1"
    finally:
        receiver.close()
        path.unlink(missing_ok=True)
    with pytest.raises(NotificationError):
        notify_ready(environment={"NOTIFY_SOCKET": "relative.sock"})


def test_evidence_is_explicitly_non_deployment_and_redacted(tmp_path: Path):
    root, capability = create_isolated_root(
        tmp_path, purpose="M122A_EVIDENCE", transaction_id="tx_evidence"
    )
    evidence = collect_evidence(
        root, capability=capability, facts={"collector": "test"}
    )
    encoded = json.dumps(evidence)
    assert evidence["status"] == "NOT_VERIFIED"
    assert "DEPLOYMENT_VERIFIED" not in encoded
    assert "private" not in encoded.casefold()


def test_fixed_verifier_is_the_only_authority_and_has_no_project_imports():
    verifier = ROOT / "deployment/fixed_verifier/aether-release-verify"
    executables = sorted(
        path for path in ROOT.glob("deployment/**/aether-release-verify") if path.is_file()
    )
    assert executables == [verifier]
    text = verifier.read_text(encoding="utf-8")
    assert "from aether" not in text
    assert "import aether" not in text
    assert "subprocess.run" not in text
    assert "Popen" in text
    production = list((ROOT / "aether").rglob("*.py"))
    assert all("release_verifier" not in path.read_text(encoding="utf-8") for path in production)
    assert verifier.stat().st_mode & 0o111


def test_m122a_status_is_finalized_and_ready_for_summary_review_only():
    document = (ROOT / "docs/architecture/MILESTONE_122A_OAS_REPOSITORY_DEPLOYMENT_ARTIFACT_FOUNDATION_BUILD.md").read_text(encoding="utf-8")
    status = _authoritative_m122a_status(document)
    for field, value in M122A_STATUS.items():
        matches = re.findall(rf"^{re.escape(field)}: .*$", status, re.MULTILINE)
        assert matches == [f"{field}: {value}"]
    assert "76901b6fb619776e0fbc53c5a30995faa5bcf070" in document
    assert "milestone-122A-oas-repository-deployment-artifact-foundation" in document
    assert "metadata consistency only" in document
    assert "no implementation or deployment state" in document
