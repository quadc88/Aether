"""Structural lock for the fifth targeted corrective, design-only M128A proof."""

from __future__ import annotations

from hashlib import sha256
from pathlib import Path
import re
import subprocess


ROOT = Path(__file__).resolve().parents[1]
DOCUMENT = ROOT / (
    "docs/architecture/"
    "MILESTONE_128A_PRIVILEGED_HOST_TRUST_BOOTSTRAP_RUNNER_PROCESS_RECOVERY_AND_EXACT_ROOT_AUTHORITY_CONTRACT_PROOF.md"
)
INITIAL_SUMMARY = Path(
    "/home/aether/summaries/"
    "milestone_128A_privileged_host_trust_bootstrap_runner_process_recovery_and_exact_root_authority_contract_proof_summary.txt"
)
FIRST_CORRECTIVE_SUMMARY = Path(
    "/home/aether/summaries/"
    "milestone_128A_corrected_privileged_host_trust_bootstrap_runner_process_recovery_and_exact_root_authority_contract_proof_summary.txt"
)
SECOND_CORRECTIVE_SUMMARY = Path(
    "/home/aether/summaries/"
    "milestone_128A_second_corrective_privileged_host_trust_bootstrap_runner_process_recovery_and_exact_root_authority_contract_proof_summary.txt"
)
THIRD_CORRECTIVE_SUMMARY = Path(
    "/home/aether/summaries/"
    "milestone_128A_third_corrective_privileged_host_trust_bootstrap_runner_process_recovery_and_exact_root_authority_contract_proof_summary.txt"
)
FOURTH_TARGETED_CORRECTIVE_SUMMARY = Path(
    "/home/aether/summaries/"
    "milestone_128A_fourth_targeted_corrective_privileged_host_trust_bootstrap_runner_process_recovery_and_exact_root_authority_contract_proof_summary.txt"
)
FIFTH_TARGETED_CORRECTIVE_SUMMARY = Path(
    "/home/aether/summaries/"
    "milestone_128A_fifth_targeted_corrective_privileged_host_trust_bootstrap_runner_process_recovery_and_exact_root_authority_contract_proof_summary.txt"
)
FINALIZATION_SUMMARY = Path(
    "/home/aether/summaries/"
    "milestone_128A_privileged_host_trust_bootstrap_runner_process_recovery_and_exact_root_authority_contract_proof_finalization_summary.txt"
)
RECOVERY_SUMMARY = Path(
    "/home/aether/summaries/"
    "milestone_128A_finalization_recovery_and_git_closure_summary.txt"
)
M124A_SCOPE_LOCK = ROOT / (
    "tests/"
    "test_milestone_124a_oas_controlled_first_install_deployment_transaction_authorization_proof.py"
)
M127_IMPLEMENTATION = ROOT / "aether/deployment/host_trust_bootstrap.py"
M127_BEHAVIOR = ROOT / "tests/test_deployment_host_trust_bootstrap.py"
M127_DOCUMENT = ROOT / (
    "docs/architecture/"
    "MILESTONE_127A_OAS_ISOLATED_HOST_TRUST_BOOTSTRAP_AUTHORIZATION_AND_DURABLE_PUBLICATION_TRANSACTION_FOUNDATION_BUILD.md"
)
M127_LOCK = ROOT / (
    "tests/"
    "test_milestone_127a_oas_isolated_host_trust_bootstrap_authorization_and_durable_publication_transaction_foundation_build.py"
)

FINAL_REPOSITORY_PATHS = {
    "PROGRESS.md",
    "docs/architecture/SECURITY_ARCHITECTURE.md",
    "tests/test_security_architecture_canonization.py",
    DOCUMENT.relative_to(ROOT).as_posix(),
    Path(__file__).relative_to(ROOT).as_posix(),
    M124A_SCOPE_LOCK.relative_to(ROOT).as_posix(),
}

PROTECTED_M127_HASHES = {
    M127_IMPLEMENTATION: "e5a0092e6c7af0edf298ca2d126d9e1a924e46a943a162521354574dd405b168",
    M127_BEHAVIOR: "970096e76a63c322cbe4fb4309cbdc504d1ab1c35b890d46cfe86f28b18260f3",
    M127_DOCUMENT: "401e12e097ed5aa9b87617fa74e1d2c705523f3a1f6047f1cbc73353425ef3de",
    M127_LOCK: "b7ca3c13c52dad5b3dfe320ec5273a9b2cf3134cc1213d544cc1f6050c79634f",
}

PRESERVED_SUMMARY_HASHES = {
    INITIAL_SUMMARY: "a403178d94a73834586234ccdab03b307a06f61495cdb1dafc921d347c4e305a",
    FIRST_CORRECTIVE_SUMMARY: "4cc7e84634809de94df19b7326dde9f76116a58e07ec71c859de5d323400fbe6",
    SECOND_CORRECTIVE_SUMMARY: "93b21ecfcb4be5a18d5c754494e07b60eb9d17e96dd6025d98769bacf8abce75",
    FOURTH_TARGETED_CORRECTIVE_SUMMARY: "4c88c29578bae8cf3c8c263bcde9237935035962f8d788ecd17a6bc40645b5a7",
}

CANONICAL_STATUS = {
    "M128A_AUTHORIZED": "YES",
    "M128A_STARTED": "YES",
    "M128A_FINALIZED": "YES",
    "M128A_TYPE": "DESIGN_DISCOVERY_SECURITY_AND_OPERATIONS_CONTRACT_PROOF",
    "DECISION_STATUS": "CURRENT",
    "DESIGN_STATUS": "DESIGN_PROVEN",
    "IMPLEMENTATION_STATUS": "NOT_IMPLEMENTED",
    "VERIFICATION_STATUS": "TEST_VERIFIED",
    "DEPLOYMENT_VERIFIED": "NO",
    "DEPLOYMENT_STATE": "NOT_DEPLOYED",
    "CURRENT_HOST_DEPLOYMENT_READY": "NO",
    "CURRENT_PROBE_HOST_LANDLOCK_STATUS": "UNSUPPORTED_EOPNOTSUPP",
    "CURRENT_PROBE_HOST_SUCCESS_PATH_RUNNABLE": "NO",
    "PRIVILEGED_RUNNER_IMPLEMENTED": "NO",
    "PROCESS_INDEPENDENT_RECOVERY_IMPLEMENTED": "NO",
    "EXACT_REAL_ROOT_BINDING_IMPLEMENTED": "NO",
    "PRODUCTION_OS_PROVENANCE_VERIFIED": "NO",
    "PRODUCTION_TRUST_MATERIAL_PROVEN": "NO",
    "PRODUCTION_PRIVATE_KEYS_CREATED": "NO",
    "PRODUCTION_PRIVATE_KEYS_ACCESSED": "NO",
    "HOST_TRUST_OBJECTS_INSTALLED": "NO",
    "LIVE_DEPLOYMENT_AUTHORIZED": "NO",
    "LIVE_ROLLBACK_AUTHORIZED": "NO",
    "TARGET_HOST_MUTATION_PERFORMED": "NO",
    "GENERIC_ACT_AUTHORIZED": "NO",
    "BUILD_AUTHORIZED": "NO",
    "PROGRESS_UPDATED": "YES",
    "SECURITY_ARCHITECTURE_UPDATED": "YES",
    "COMMIT_CREATED": "YES",
    "TAG_CREATED": "YES",
    "PUSH_PERFORMED": "YES",
    "SUCCESSOR_AUTHORIZED": "NO",
    "SUCCESSOR_NUMBER_ASSIGNED": "NO",
    "READY_FOR_PM_REVIEW": "NO",
}


def _text() -> str:
    return DOCUMENT.read_text(encoding="utf-8")


def _flat(text: str) -> str:
    return " ".join(text.split())


def _changed_paths() -> set[str]:
    lines = subprocess.run(
        ["git", "status", "--short", "--untracked-files=all"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.splitlines()
    return {
        line[3:]
        for line in lines
        if len(line) >= 4 and line[:2] in {" M", "??", "A ", "AM"}
    }


def _section(text: str, heading: str, next_heading: str) -> str:
    start = text.index(heading)
    end = text.index(next_heading, start)
    return text[start:end]


def _status_map(text: str) -> dict[str, str]:
    begin = "AUTHORITATIVE_M128A_STATUS_BEGIN"
    end = "AUTHORITATIVE_M128A_STATUS_END"
    assert text.count(begin) == text.count(end) == 1
    block = text[text.index(begin) : text.index(end)]
    result: dict[str, str] = {}
    for line in block.splitlines()[1:]:
        if line.strip():
            key, separator, value = line.strip().partition(":")
            assert separator and key not in result
            result[key] = value.strip()
    return result


def _code_block_after(section: str, marker: str) -> list[str]:
    start = section.index("```", section.index(marker))
    body = section[start:].split("```", 2)[1]
    return [line.strip() for line in body.splitlines() if line.strip() and line.strip() != "text"]


def _sha256(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def test_scope_title_and_all_summaries_are_preserved():
    text = _text()
    assert _changed_paths() == FINAL_REPOSITORY_PATHS or not _changed_paths()
    assert text.startswith(
        "# M128A Privileged Host Trust-Bootstrap Runner, Process-Recovery, and Exact-Root Authority Contract Proof\n"
    )
    assert "Document role: DESIGN / DISCOVERY / SECURITY / OPERATIONS CONTRACT PROOF ONLY." in text
    for summary, expected in {
        **PRESERVED_SUMMARY_HASHES,
        THIRD_CORRECTIVE_SUMMARY: None,
        FOURTH_TARGETED_CORRECTIVE_SUMMARY: "4c88c29578bae8cf3c8c263bcde9237935035962f8d788ecd17a6bc40645b5a7",
        FIFTH_TARGETED_CORRECTIVE_SUMMARY: "3631a4147d001bec413974f9b3da9ed11ce7f40182e723f59374b4c6b6205e29",
        FINALIZATION_SUMMARY: None,
        RECOVERY_SUMMARY: None,
    }.items():
        assert str(summary) in text
        if expected is not None:
            assert _sha256(summary) == expected


def test_status_exit_and_negative_finalization_state_are_structured():
    text = _text()
    assert _status_map(text) == CANONICAL_STATUS
    assert text.count("SELECTED_EXIT: EXIT_A") == 1
    assert "EXIT_A_MEANING: BOUNDED_PRIVILEGED_RUNNER_BUILD_JUSTIFIED_FOR_PM_REVIEW" in text
    assert "SELECTED_EXIT: EXIT_B" not in text
    assert "SELECTED_EXIT: EXIT_C" not in text
    assert "M128A_FINALIZED: NO" not in text
    assert "BUILD_AUTHORIZED: YES" not in text
    assert "PROGRESS_UPDATED: YES" in text
    assert "SECURITY_ARCHITECTURE_UPDATED: YES" in text
    assert "COMMIT_CREATED: YES" in text
    assert "TAG_CREATED: YES" in text
    assert "PUSH_PERFORMED: YES" in text
    assert "READY_FOR_PM_REVIEW: NO" in text


def test_two_commit_recovery_scope_and_historical_m124a_gate_are_structured():
    text = _flat(_text())
    for marker in (
        "INITIAL_FINALIZATION_COMMIT: 02d47587826c8abc9db30b2031419b133573c34c",
        "FINALIZATION_RECOVERY_COMMIT: THIS_COMMIT",
        "INITIAL_FINALIZATION_SCOPE: FIVE_PATHS",
        "FINALIZATION_RECOVERY_SCOPE: SIX_PATHS",
        "FINAL_TAG_TARGET: FINALIZATION_RECOVERY_COMMIT",
        "The additional path is a historical test-governance correction",
        "not M128A production implementation or scope expansion",
        "3846 passed, 1 failed, 9 warnings",
        "historical M124A live-worktree scope assertion",
        "checking the immutable M124A finalization commit directly",
        "final tag and branch push remain conditional",
    ):
        assert marker in text
    assert "3aaff2a8ec188650ecb4e132a74d6ef92d3245a6" in text


def test_landlock_host_precondition_and_exit_a_scope_are_explicit():
    text = _flat(_text())
    for marker in (
        "LANDLOCK_MINIMUM_ABI: 3",
        "CURRENT_PROBE_HOST_LANDLOCK_STATUS: UNSUPPORTED_EOPNOTSUPP",
        "CURRENT_PROBE_HOST_SUCCESS_PATH_RUNNABLE: NO",
        "LANDLOCK_UNSUPPORTED_BEHAVIOR: FAIL_CLOSED_BEFORE_DURABLE_INTENT",
        "TARGET_BUILD_PROFILE_REQUIRES_LANDLOCK_ABI_3_OR_NEWER: YES",
        "CURRENT_HOST_DEPLOYMENT_READY: NO",
        "current probe host cannot execute the successful privileged-runner path",
        "compatible kernel and host profile",
        "compatible isolated test host or VM",
        "not a substitute for testing the successful Landlock path",
        "does not imply current-host deployment readiness",
        "does not imply runtime security proof",
        "does not imply successful Landlock enforcement on this host",
        "does not silently fall back to DAC, systemd, a partial Landlock policy, or an unconfined service",
        "Landlock and seccomp enforcement are not implemented or deployment-verified",
        "Exact real-host binding remains design-only",
    ):
        assert marker in text


def test_governance_precedence_and_execution_loop_are_preserved():
    text = _flat(_text())
    for marker in (
        "CONSTITUTION > ARCHITECTURE > SECURITY_ARCHITECTURE > CURRENT MILESTONE AUTHORIZATION > CURRENT IMPLEMENTATION",
        "Aether remains one persistent digital mind.",
        "AUTHENTICATION != INTENT_INTERPRETATION",
        "GOAL_ACCEPTANCE != ACTION_AUTHORIZATION",
        "ACTION_SUCCESS != COMPLETION",
        "COMPLETION REQUIRES OBSERVATION AND VERIFICATION",
        "Receive -> Understand -> Think -> Plan -> Act -> Observe -> Verify -> Critic -> Repair -> Learn -> Report",
        "AETHER_CORE_CANNOT_MINT_BOOTSTRAP_AUTHORIZATION: YES",
        "Tool-Operation-Capability security remains a separate future frontier",
    ):
        assert marker in text


def test_exactly_one_evidence_model_and_complete_binary_bundle():
    text = _text()
    section = _section(text, "## 3. Selected Evidence-Carriage Model", "## 4. Selected Runner")
    assert text.count("SELECTED_EVIDENCE_CARRIAGE_MODEL:") == 1
    assert "SELECTED_EVIDENCE_CARRIAGE_MODEL: MODEL_A_SELF_CONTAINED_SEALED_BUNDLE" in section
    assert "MODEL_B_IMMUTABLE_ARTIFACT_REFERENCES: NOT_SELECTED" in section
    for marker in (
        "16 fixed ASCII bytes",
        "unsigned 16-bit big-endian",
        "unsigned 64-bit big-endian integer",
        "sorted by field name byte order",
        "trailer: SHA-256",
        "no duplicate field",
        "no unknown entry",
        "MAX_RECORD_BYTES: 64 * 1024",
        "MAX_OBJECT_BYTES: 1024 * 1024",
        "MAX_OBJECT_COUNT: 5",
        "MAX_BUNDLE_BYTES:",
        "fixed verifier executable may exceed 64 KiB",
    ):
        assert marker in section
    fields = _code_block_after(section, "exact entries are")
    required = {
        "authority_set_raw", "image_baseline_signature", "local_console_raw",
        "local_console_signature", "governance_raw", "governance_signature",
        "authorization_payload_raw", "authorization_envelope_raw",
        "authorization_detached_signature", "target_host_identity_digest",
        "target_boot_digest", "transaction_id", "authorization_id", "nonce",
        "trust_generation", "minimum_accepted_generation", "requested_object_set",
        "mutation_scope", "object_set_digest", "issued_at_utc", "expires_at_utc",
        "verification_context_fingerprint",
    }
    assert required <= set(fields)
    for index in range(5):
        assert {f"object_{index}_{suffix}" for suffix in ("path", "bytes", "size", "sha256")} <= set(fields)
    assert len(fields) == len(set(fields))
    assert "validity_state" not in fields
    assert "revocation_state" not in fields


def test_runner_service_policy_is_plain_oneshot_and_network_closed():
    raw = _section(_text(), "## 4. Selected Runner", "## 5.")
    text = _flat(raw)
    policy = "\n".join(_code_block_after(raw, "The future unit policy is"))
    for marker in (
        "SELECTED_PROCESS_RESTRICTION_MODEL: MODEL_D_INITIAL_NAMESPACE_PREOPENED_DIRFDS_PLUS_IRREVERSIBLE_LANDLOCK_AND_SECCOMP",
        "SYSTEMD_FILESYSTEM_CONFINEMENT: NONE",
        "INPROCESS_FILESYSTEM_CONFINEMENT: PREOPENED_DIRFDS_PLUS_IRREVERSIBLE_LANDLOCK",
        "POST_START_EXEC_RULE: FIXED_NATIVE_PROCESS_INSTALLS_IRREVERSIBLE_SECCOMP_FILTER",
        "POST_START_PROCESS_CREATION_RULE: FIXED_NATIVE_PROCESS_DENIES_FORK_VFORK_CLONE_CLONE3",
        "SERVICE_TYPE: Type=oneshot",
        "DESCRIPTOR_POLICY: NO_INHERITED_DESCRIPTORS",
        "CLIENT_SOCKET: NONE",
        "Type=oneshot",
        "ExecStart=/usr/libexec/aether-host-trust-bootstrap-runner",
        "RestrictAddressFamilies=AF_UNIX",
        "IPAddressDeny=any",
        "SystemCallFilter=@system-service",
        "SystemCallFilter=~fork vfork clone clone3 socket socketpair connect bind listen accept accept4 sendto sendmsg recvfrom recvmsg",
        "SystemCallErrorNumber=EPERM",
        "prctl(PR_SET_NO_NEW_PRIVS, 1)",
        "SECCOMP_SET_MODE_FILTER",
        "SECCOMP_FILTER_FLAG_TSYNC",
        "NoNewPrivs: 1",
        "Seccomp: 2",
        "returns `EPERM` for `execve`, `execveat`, `fork`, `vfork`, `clone`, and `clone3`",
        "before durable SQLite intent or ingress disposition",
        "Restart=no",
        "TimeoutStartSec=120s",
        "no `NOTIFY_SOCKET` dependency",
        "clears `NOTIFY_SOCKET`",
        "no notification descriptor",
        "service completion",
        "No private network namespace is required",
        "No private mount namespace is permitted",
        "Failure to establish any required cgroup-BPF or syscall restriction fails closed",
    ):
        assert marker in text
    assert "SystemCallFilter=~execve" not in raw
    assert "SystemCallFilter=~execve" not in _text()
    assert "PrivateNetwork=yes" not in policy
    assert "documented implicit allow-list behavior for `execve()` and `execveat()`" in text
    assert "execve` and `execveat` are denied after service startup" not in text
    for directive in (
        "NoExecPaths=", "ExecPaths=", "ReadWritePaths=", "ReadOnlyPaths=",
        "InaccessiblePaths=", "BindPaths=", "BindReadOnlyPaths=",
        "TemporaryFileSystem=", "RootDirectory=", "RootImage=", "PrivateMounts=",
        "PrivateTmp=", "PrivateDevices=", "ProtectSystem=", "ProtectHome=",
        "PrivateNetwork=",
    ):
        assert directive not in policy
    assert "ExecStart=/usr/libexec/aether-host-trust-bootstrap-runner" in policy


def test_selected_models_are_unique_and_process_lifecycle_is_coherent():
    text = _text()
    assert text.count("SELECTED_PROCESS_RESTRICTION_MODEL:") == 1
    assert text.count("SELECTED_NAMESPACE_MODEL:") == 1
    assert text.count("SELECTED_ADMITTER_MODEL:") == 1
    assert text.count("SELECTED_INGRESS_MODEL:") == 1
    assert "MODEL_B_OS_CONSTRUCTED_PRIVATE_SERVICE_NAMESPACE" not in text
    assert "NAMESPACE_MAPPING_RECORD: JSON" not in text
    assert "SystemCallFilter=~execve" not in text
    assert "execve` and `execveat` are denied after service startup" not in text
    assert "fixed process performs the named Landlock" in text
    assert "SELECTED_PROCESS_RESTRICTION_MODEL: MODEL_D_INITIAL_NAMESPACE_PREOPENED_DIRFDS_PLUS_IRREVERSIBLE_LANDLOCK_AND_SECCOMP" in text
    assert "SYSTEMD_FILESYSTEM_CONFINEMENT: NONE" in text
    assert "MOUNT_NAMESPACE_RELATION: MUST_BE_EQUAL" in text
    assert "FIXED_PATH_RELATION: SERVICE_PATH_EQUALS_HOST_PATH" in text
    assert "SYSTEMD_PRIVATE_NETWORK_NAMESPACE: NOT_SELECTED" in text
    assert "SYSTEMD_PRIVATE_MOUNT_NAMESPACE: FORBIDDEN" in text
    assert "PrivateNetwork=yes" not in text
    assert "PrivateMounts=yes" not in text


def test_namespace_source_and_model_a_relationship_are_concrete():
    text = _text()
    section = _flat(_section(text, "## 5. Concrete Initial-Host Namespace Evidence", "## 6. Exact Root"))
    assert text.count("SELECTED_NAMESPACE_MODEL:") == 1
    for marker in (
        "MODEL_A_KERNEL_SELF_ATTESTED_INITIAL_HOST_MOUNT_NAMESPACE",
        "NAMESPACE_EQUALITY_TO_PID1: REQUIRED",
        "NAMESPACE_EVIDENCE_PRODUCER: LINUX_KERNEL_PROCFS_AND_STATX",
        "The Linux kernel is the only namespace-fact producer",
        "procfs namespace handles",
        "producer_principal: kernel",
        "consumer_principal: root-owned fixed runner",
        "start_order: systemd policy -> ExecStart -> filter transition -> kernel facts -> bundle read",
        "HOST_MOUNT_NAMESPACE: /proc/1/ns/mnt",
        "SERVICE_MOUNT_NAMESPACE: /proc/self/ns/mnt",
        "MOUNT_NAMESPACE_RELATION: MUST_BE_EQUAL",
        "FIXED_PATH_RELATION: SERVICE_PATH_EQUALS_HOST_PATH",
        "/usr/lib/aether/os-image/host-trust-bootstrap-path-policy.json",
        "approved OS/image package digest",
        "boot_id",
        "current boot ID",
        "/proc/self/mountinfo",
        "/proc/self/exe",
        "cgroup membership",
        "host_facts: /proc/1/ns/mnt",
        "service_facts: /proc/self/ns/mnt",
        "boot_binding: exact boot_id stored with the SQLite transaction",
        "unit_binding: /proc/self/cgroup",
        "executable_binding: /proc/self/exe",
        "PID 1 custom writer",
        "no cryptographic namespace-evidence key lifecycle",
        "no pre-start helper",
        "There is no runtime namespace record",
        "caller-created",
        "container-created",
        "chroot-created",
        "bind-substituted",
        "remounted",
        "Inequality with PID 1 is rejected",
    ):
        assert marker in section
    for path in ("/etc/aether", "/usr/libexec", "/var/lib/aether/trust-bootstrap"):
        assert path in section
    assert "PID 1 writes" not in section
    assert "manager_signature" not in section
    assert "namespace-evidence.json" not in section


def test_admitter_model_and_inbox_permissions_are_separated():
    text = _text()
    section = _flat(_section(text, "## 8. Selected Admitter Privilege Model", "## 9. Sealed Inbox"))
    assert text.count("SELECTED_ADMITTER_MODEL:") == 1
    for marker in (
        "SELECTED_ADMITTER_MODEL: MODEL_B_ROOT_ONE_SHOT_CONFINED_ADMITTER",
        "MODEL_A_NON_ROOT_ADMITTER: NOT_SELECTED",
        "MODEL_C_REVIEWED_ROOT_OPERATOR_IMPORT: NOT_SELECTED",
        "aether-host-trust-bootstrap-admitter.service",
        "/usr/libexec/aether-host-trust-bootstrap-admitter",
        "User=root",
        "Group=root",
        "SELECTED_INGRESS_MODEL: MODEL_A_M126A_OFFLINE_BUNDLE_ON_VERIFIED_READ_ONLY_MEDIA",
        "INGRESS_PRODUCER: M126A_HOST_BOOTSTRAP_AUTHORITY_OFFLINE_BUNDLE_EXPORTER",
        "INGRESS_MOUNT_MECHANISM: SYSTEMD_FIXED_READ_ONLY_BLOCK_DEVICE_MOUNT",
        "INGRESS_INVOCATION_AUTHORITY: LOCAL_CONSOLE_ROOT_OPERATOR_REQUEST_PLUS_M126A_EVIDENCE",
        "/usr/lib/aether/os-image/host-trust-bootstrap-import-policy.json",
        "/dev/disk/by-id/aether-host-trust-bootstrap-import",
        "MOUNT_PATH: /run/aether-host-trust-bootstrap/import",
        "BUNDLE_PATH: /run/aether-host-trust-bootstrap/import/import.bundle",
        "MOUNT_OPTIONS: ro,nosuid,nodev,noexec",
        "The ingress producer is a future controlled offline bundle exporter",
        "separately governed M126A custody",
        "exact target host identity and boot identity",
        "physically presents that media",
        "active non-remote local console",
        "root-owned systemd manager",
        "start permission is only invocation control",
        "no systemd-manager IPC",
        "major and minor identity",
        "filesystem UUID/type",
        "writable remount",
        "changed bundle digest",
        "/run/aether-host-trust-bootstrap/import/import.bundle",
        "SystemCallErrorNumber=EPERM",
        "CapabilityBoundingSet=",
        "NoNewPrivileges=yes",
        "separate fixed service",
        "Root possession is not authorization",
        "cannot mint signatures",
        "cannot edit a ready file",
    ):
        assert marker in section
    assert "aether-host-trust-bootstrap-admitter" in section
    assert "ordinary Aether runtime and OAS runtime have no access" in section
    policy = "\n".join(_code_block_after(section, "The confined admitter policy is filesystem-neutral at the unit level"))
    for directive in (
        "NoExecPaths=", "ExecPaths=", "ReadWritePaths=", "ReadOnlyPaths=",
        "InaccessiblePaths=", "BindPaths=", "BindReadOnlyPaths=",
        "TemporaryFileSystem=", "RootDirectory=", "RootImage=", "PrivateMounts=",
        "PrivateTmp=", "PrivateDevices=", "ProtectSystem=", "ProtectHome=",
        "PrivateNetwork=",
    ):
        assert directive not in policy


def test_ingress_is_single_explicit_source_and_invocation_lifecycle():
    section = _flat(_section(_text(), "## 8. Selected Admitter Privilege Model", "## 9. Sealed Inbox"))
    assert section.count("SELECTED_INGRESS_MODEL:") == 1
    assert "SELECTED_INGRESS_MODEL: MODEL_A_M126A_OFFLINE_BUNDLE_ON_VERIFIED_READ_ONLY_MEDIA" in section
    assert section.count("INGRESS_PRODUCER:") == 1
    assert section.count("INGRESS_MOUNT_MECHANISM:") == 1
    assert section.count("INGRESS_INVOCATION_AUTHORITY:") == 1
    assert "approved source" not in section
    assert "OS-mounted offline bundle" in section
    assert "source bytes" in section
    assert "source digest" in section
    assert "exact M126A signature" in section
    assert "Ordinary Aether and OAS have no systemd-manager IPC" in section
    assert "cannot make unsigned or incorrectly bound bytes valid" in section
    assert "Media replacement" in section
    assert "before inbox disposition" in section


def test_inbox_bundle_sequence_and_raw_evidence_handoff_are_complete():
    text = _flat(_text())
    inbox = _flat(_section(_text(), "## 9. Sealed Inbox Transaction", "## 10. Complete Raw Evidence"))
    for marker in (
        "/var/lib/aether/trust-bootstrap/inbox/",
        "root:root",
        "0700",
        "exclusive creation",
        "no-follow",
        "regular-file",
        "fsync the temporary file",
        "atomically rename",
        "<transaction_id>.ready",
        "fsync the inbox directory",
        "partial",
        "archive",
        "Archive movement is not an atomic commit with SQLite",
        "ADMISSION_MODEL: ONE_SEALED_READY_CANDIDATE",
        "Zero candidates is a no-op",
        "Multiple non-identical ready candidates",
        "Byte-identical",
        "Extra files",
    ):
        assert marker in inbox
    evidence = _flat(_section(_text(), "## 10. Complete Raw Evidence", "## 11. One Canonical"))
    for marker in (
        "authority_set_raw", "image_baseline_signature", "local_console_raw",
        "local_console_signature", "governance_raw", "governance_signature",
        "authorization_payload_raw", "authorization_envelope_raw",
        "authorization detached signature", "exact object bytes",
        "target boot", "transaction ID", "authorization ID", "nonce",
        "trust generation", "minimum generation", "object-set digest",
        "issued/expiry times", "signature domains", "verification context",
        "current trusted time", "revocation",
        "target_boot_digest",
        "validity_state` and `revocation_state` cannot be trusted",
        "does not create a signature",
        "does not import a key",
        "does not normalize",
    ):
        assert marker in evidence
    assert "authorization_detached_signature` |" in evidence
    assert "must exactly equal the detached signature encoded in the envelope" in evidence
    assert "no second source is trusted" in evidence
    assert "authorization_detached_signature can differ" not in evidence


def test_bundle_signature_consistency_is_a_pre_intent_invariant():
    text = _flat(_text())
    equality = "authorization_detached_signature` | must exactly equal the detached signature encoded in the envelope"
    assert text.count(equality) == 1
    assert "mismatch must fail closed before durable intent" in text
    assert "detached signature encoded in `authorization_envelope_raw`" in text
    assert "second source is trusted" in text


def test_sqlite_is_the_only_canonical_ledger():
    text = _text()
    section = _flat(_section(text, "## 11. One Canonical Durable SQLite Ledger", "## 12. Process-Crash"))
    for marker in (
        "CANONICAL_DURABLE_LEDGER: SQLITE_ONLY",
        "STATE_AND_AUDIT_AUTHORITY: state.sqlite3",
        "FILE_BASED_PHASE_AUTHORITY: NONE",
        "state.sqlite3-wal",
        "state.sqlite3-shm",
        "state.lock",
        "synchronous=FULL",
        "previous_audit_digest",
        "audit_head_digest",
        "There is no `journal.jsonl`",
        "no dual authority",
        "derived, read-only, non-authoritative, regenerable",
        "cannot authorize recovery or mutation",
        "does not recreate a damaged database",
    ):
        assert marker in section
    assert "journal.jsonl" not in section.replace("There is no `journal.jsonl`", "")


def test_recovery_reboot_and_generation_contracts_are_distinct():
    text = _text()
    recovery = _flat(_section(text, "## 12. Process-Crash", "## 13. Inbox"))
    generation = _flat(_section(text, "## 14. Generation Admission", "## 15. Cross-Directory"))
    for marker in (
        "TemporaryRootCapability", "state.lock", "BEGIN IMMEDIATE",
        "After every publication effect", "Changed boot", "never silently resumes forward activation",
        "restoration/review only", "TRUST_BOOTSTRAP_REVIEW_REQUIRED",
        "same-boot crash", "Changed-boot recovery", "after `TRUST_SET_ACTIVE` commit",
    ):
        assert marker in recovery
    cases = (
        "GENERATION_CASE_1_IDENTICAL_TRANSACTION_RETRY",
        "GENERATION_CASE_2_DIFFERENT_TRANSACTION_SAME_NONCE",
        "GENERATION_CASE_3_DIFFERENT_TRANSACTION_SAME_GENERATION",
        "GENERATION_CASE_4_LOWER_THEN_HIGHER_AFTER_TERMINAL",
        "GENERATION_CASE_5_HIGHER_THEN_STALE_LOWER",
        "GENERATION_CASE_6_MULTIPLE_READY_CANDIDATES",
        "GENERATION_CASE_7_NEW_CANDIDATE_DURING_NONTERMINAL_TRANSACTION",
        "GENERATION_CASE_8_RECOVERY_WITH_NEW_CANDIDATE_PRESENT",
        "GENERATION_CASE_9_BURNED_THEN_HIGHER",
    )
    for case in cases:
        assert generation.count(case) == 1
    for marker in (
        "first exact reservation commit wins",
        "active_generation` identifies the current highest active generation",
        "burned generation is never reused",
        "two historical successful records",
        "no lower mutation or metadata regression",
    ):
        assert marker in generation


def test_inbox_crash_matrix_has_all_ten_orderings():
    section = _flat(_section(_text(), "## 13. Inbox, SQLite, and Archive Crash Ordering", "## 14. Generation Admission"))
    for index, marker in enumerate(
        (
            "INBOX_CASE_1_BEFORE_TEMP_FSYNC", "INBOX_CASE_2_AFTER_TEMP_FSYNC_BEFORE_RENAME",
            "INBOX_CASE_3_AFTER_RENAME_BEFORE_INBOX_DIR_FSYNC", "INBOX_CASE_4_READY_BEFORE_SQLITE_DISPOSITION",
            "INBOX_CASE_5_AFTER_REJECTION_BEFORE_ARCHIVE", "INBOX_CASE_6_AFTER_ACCEPTANCE_INTENT_BEFORE_ARCHIVE",
            "INBOX_CASE_7_AFTER_ARCHIVE_RENAME_BEFORE_DIR_FSYNC", "INBOX_CASE_8_AFTER_ARCHIVE_FSYNC",
            "INBOX_CASE_9_RECOVERY_WITH_READY_AND_ARCHIVE_COPIES", "INBOX_CASE_10_SQLITE_STATE_WITH_MISSING_TRANSPORT",
        ),
        start=1,
    ):
        assert section.count(marker) == 1
    assert "SQLite remains the sole phase and audit authority" in section
    assert "No archive rename is atomic with SQLite" in section


def test_terminal_publication_and_failure_matrices_are_complete():
    text = _text()
    publication = _flat(_section(text, "## 15. Cross-Directory Publication", "## 16. Authority Separation"))
    threat = _section(text, "## 17. Threat and Failure Matrix", "## 18. Limitations")
    for marker in (
        "same-directory rename", "directory fsync", "mixed set is unusable",
        "Cross-directory atomicity between the two directories and SQLite is explicitly not proven",
        "TERMINAL_OBSERVATION_COMMIT", "TERMINAL_VERIFICATION_COMMIT",
        "CANONICAL_AUDIT_COMMIT", "TRUST_SET_ACTIVE_STATE_COMMIT",
        "ONE_ATOMIC_SQLITE_TRANSACTION", "Terminal ACTIVE requires atomic Observation and Verification",
        "Observation alone", "independently reopens",
    ):
        assert marker in publication
    for marker in (
        "unauthorized service invocation", "forged runner or admitter identity",
        "namespace inequality with PID 1", "procfs namespace fact unavailable",
        "boot identity mismatch", "fixed-path device/inode/filesystem drift",
        "bind/remount/overlay substitution", "executable or unit-policy digest mismatch",
        "unsupported or incomplete Landlock ABI", "Landlock rule installation failure",
        "seccomp installation failure", "unexpected open descriptor", "unexpected child or process",
        "filesystem authority outside selected rule set", "changed path identity after restriction",
        "incomplete raw evidence", "object byte substitution", "ready-file ambiguity",
        "boot identity mismatch", "network/socket policy drift",
        "SQLite corruption or WAL/SHM loss", "partial publication or failed restoration",
    ):
        assert f"| {marker} |" in threat


def test_model_d_ordering_authority_sets_and_path_independence_are_explicit():
    text = _text()
    section = _flat(_section(text, "### 4.1 Model D startup sequence", "## 5. Concrete"))
    ordered = (
        "It opens only the exact required root-owned paths",
        "It records the exact expected device, inode, filesystem, owner, mode, and mount facts",
        "It sets PR_SET_NO_NEW_PRIVS",
        "It installs a Landlock ruleset",
        "It installs the irreversible TSYNC seccomp filter",
        "It closes every unnecessary descriptor",
        "Only after all restrictions succeed may it read the bundle or open SQLite",
    )
    positions = [section.index(marker) for marker in ordered]
    assert positions == sorted(positions)
    for marker in (
        "LANDLOCK_MINIMUM_ABI: 3",
        "LANDLOCK_REQUIRED_HANDLED_ACCESS_FS:",
        "RUNNER_READ_HANDLES:", "RUNNER_WRITE_HANDLES:", "RUNNER_PATH_INPUT: NONE",
        "ADMITTER_READ_HANDLES:", "ADMITTER_WRITE_HANDLES:", "ADMITTER_PATH_INPUT: NONE",
        "ADMITTER_FORBIDDEN:", "fixed native control flow",
        "RESOLVE_BENEATH | RESOLVE_NO_SYMLINKS",
        "Landlock rules are file-hierarchy rules, not exact filename ACLs",
        "Seccomp BPF may check architecture",
    ):
        assert marker in section


def test_negative_boundaries_and_protected_m127a_hashes_hold():
    text = _flat(_text())
    for marker in (
        "AETHER_CORE_CANNOT_MINT_BOOTSTRAP_AUTHORIZATION: YES",
        "OAS_RUNTIME_CANNOT_MINT_BOOTSTRAP_AUTHORIZATION: YES",
        "OAS_RUNTIME_CANNOT_GAIN_ROOT_MUTATION_AUTHORITY: YES",
        "RUNNER_CANNOT_INTERPRET_GOALS: YES",
        "RUNNER_CANNOT_AUTHORIZE_GENERAL_ACTION: YES",
        "ADMITTER_CANNOT_MINT_BOOTSTRAP_AUTHORIZATION: YES",
        "GENERIC_ACT_AUTHORIZED: NO",
        "production private keys",
        "production trust material",
        "real host trust object",
        "production implementation",
        "public Internet exposure",
        "multi-instance runtime",
        "multi-agent runtime",
        "Tool-Operation-Capability expansion",
    ):
        assert marker in text
    for path, expected in PROTECTED_M127_HASHES.items():
        assert _sha256(path) == expected
    assert not re.search(r"^(<<<<<<<|=======|>>>>>>>)$", _text(), re.MULTILINE)
    assert not re.search(r"[ \t]+$", _text(), re.MULTILINE)
    assert "service-start permission is not bootstrap authorization.\nservice-start permission" not in _text()
    assert "There is no `journal.jsonl`\nThere is no" not in _text()
