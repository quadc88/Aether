"""Static scope and status lock for the finalized M127A foundation build."""

from __future__ import annotations

from pathlib import Path
import re
import subprocess


ROOT = Path(__file__).resolve().parents[1]
DOCUMENT = ROOT / "docs/architecture/MILESTONE_127A_OAS_ISOLATED_HOST_TRUST_BOOTSTRAP_AUTHORIZATION_AND_DURABLE_PUBLICATION_TRANSACTION_FOUNDATION_BUILD.md"
SUMMARY = Path("/home/aether/summaries/milestone_127A_oas_isolated_host_trust_bootstrap_authorization_and_durable_publication_transaction_foundation_build_finalization_summary.txt")
FINAL_REPOSITORY_PATHS = {
    "PROGRESS.md",
    "docs/architecture/SECURITY_ARCHITECTURE.md",
    "tests/test_security_architecture_canonization.py",
    "aether/deployment/host_trust_bootstrap.py",
    "tests/test_deployment_host_trust_bootstrap.py",
    DOCUMENT.relative_to(ROOT).as_posix(),
    Path(__file__).relative_to(ROOT).as_posix(),
}
STATUS_BEGIN = "AUTHORITATIVE_M127A_STATUS_BEGIN"
STATUS_END = "AUTHORITATIVE_M127A_STATUS_END"
CANONICAL_STATUS = {
    "M127A_AUTHORIZED": "YES", "M127A_STARTED": "YES", "M127A_FINALIZED": "YES",
    "M127A_TYPE": "BOUNDED_IMPLEMENTATION_SECURITY_TRANSACTION_FOUNDATION_BUILD",
    "DECISION_STATUS": "CURRENT", "DESIGN_STATUS": "DESIGN_PROVEN",
    "IMPLEMENTATION_STATUS": "IMPLEMENTED", "VERIFICATION_STATUS": "TEST_VERIFIED",
    "DEPLOYMENT_VERIFIED": "NO", "DEPLOYMENT_STATE": "NOT_DEPLOYED", "DEPLOYMENT_PROFILE": "ISOLATED_ROOT_ONLY",
    "ISOLATED_AUTHORITY_CONSUMPTION_IMPLEMENTED": "YES", "AUTHENTICATED_ENVELOPE_VERIFICATION_IMPLEMENTED": "YES",
    "DURABLE_BOOTSTRAP_TRANSACTION_IMPLEMENTED": "YES", "ISOLATED_FIVE_OBJECT_PUBLICATION_IMPLEMENTED": "YES",
    "TERMINAL_OBSERVATION_VERIFICATION_IMPLEMENTED": "YES", "VALID_AUTHORIZATION_CONCURRENCY_PROVEN": "YES_TEST_ONLY",
    "GENERATION_RESERVATION_SEMANTICS_PROVEN": "YES_TEST_ONLY", "FILESYSTEM_CROSS_DIRECTORY_ATOMICITY_PROVEN": "NO",
    "PRODUCTION_OS_IMAGE_BASELINE_VERIFIED": "NO", "PRODUCTION_TRUST_MATERIAL_PROVEN": "NO",
    "PRODUCTION_PRIVATE_KEYS_CREATED": "NO", "PRODUCTION_PRIVATE_KEYS_ACCESSED": "NO",
    "PRODUCTION_SIGNING_CAPABILITY_IMPLEMENTED": "NO", "TEST_ONLY_EPHEMERAL_KEYS_USED": "YES",
    "TEST_PRIVATE_KEYS_PERSISTED": "NO", "TEST_PRIVATE_KEYS_ENTERED_GIT_ARTIFACTS": "NO",
    "PRIVATE_KEYS_CREATED": "NO", "PRIVATE_KEYS_ACCESSED": "NO", "HOST_TRUST_OBJECTS_INSTALLED": "NO",
    "TRUTHFUL_OWNER_DEPLOYMENT_AUTHORITY_PROVEN": "NO", "LIVE_DEPLOYMENT_AUTHORIZED": "NO",
    "LIVE_ROLLBACK_AUTHORIZED": "NO", "TARGET_HOST_MUTATION_PERFORMED": "NO", "GENERIC_ACT_AUTHORIZED": "NO",
    "BUILD_AUTHORIZED": "YES", "PROGRESS_UPDATED": "YES", "SECURITY_ARCHITECTURE_UPDATED": "YES",
    "COMMIT_CREATED": "YES", "TAG_CREATED": "YES", "PUSH_PERFORMED": "YES", "SUCCESSOR_AUTHORIZED": "NO",
    "SUCCESSOR_NUMBER_ASSIGNED": "NO", "READY_FOR_PM_REVIEW": "NO",
}
STATE_SEQUENCE = (
    "TRUST_BOOTSTRAP_REQUESTED", "TRUST_BOOTSTRAP_VALIDATED", "PRIOR_GENERATION_RETAINED",
    "NEXT_GENERATION_STAGED", "PUBLISHING", "VERIFYING", "TRUST_SET_ACTIVE",
    "RESTORING_PRIOR_GENERATION", "TRUST_BOOTSTRAP_REVIEW_REQUIRED",
)
OBJECTS = (
    "/etc/aether/release-trust-anchor.pub",
    "/etc/aether/release-trust-anchor.fingerprint",
    "/etc/aether/release-test-evidence.sha256",
    "/etc/aether/release-verifier.sha256",
    "/usr/libexec/aether-release-verify",
)


def _changed_paths() -> set[str]:
    lines = subprocess.run(
        ["git", "status", "--short", "--untracked-files=all"],
        cwd=ROOT, check=True, capture_output=True, text=True,
    ).stdout.splitlines()
    return {line[3:] for line in lines if len(line) >= 4 and line[:2] in {" M", "??", "A ", "AM"}}


def _status_map(text: str) -> dict[str, str]:
    assert text.count(STATUS_BEGIN) == text.count(STATUS_END) == 1
    block = text[text.index(STATUS_BEGIN):text.index(STATUS_END)]
    result: dict[str, str] = {}
    for line in block.splitlines()[1:]:
        if line.strip():
            key, separator, value = line.strip().partition(":")
            assert separator and key not in result
            result[key] = value.strip()
    return result


def _field_block(document: str, heading: str) -> tuple[str, ...]:
    start = document.index(heading)
    start = document.index("```text", start) + len("```text\n")
    end = document.index("```", start)
    return tuple(line.strip() for line in document[start:end].splitlines() if line.strip())


def test_finalization_scope_is_exactly_seven_authorized_paths():
    assert _changed_paths() == FINAL_REPOSITORY_PATHS or not _changed_paths()
    document = DOCUMENT.read_text(encoding="utf-8")
    for path in FINAL_REPOSITORY_PATHS:
        assert path in document


def test_authoritative_status_is_exact_and_finalized():
    document = DOCUMENT.read_text(encoding="utf-8")
    assert _status_map(document) == CANONICAL_STATUS
    assert "M127A_FINALIZED: NO" not in document
    assert "DEPLOYMENT_VERIFIED: YES" not in document
    assert "TARGET_HOST_MUTATION_PERFORMED: YES" not in document
    assert "PROGRESS_UPDATED: NO" not in document
    assert "COMMIT_CREATED: NO" not in document
    assert "TAG_CREATED: NO" not in document
    assert "PUSH_PERFORMED: NO" not in document
    assert "TRUST_BOOTSTRAP_AUTHORIZATION_PROVEN:" not in document
    assert "READY_FOR_PM_REVIEW: YES" not in document


def test_authenticated_records_and_state_machine_are_closed_and_ordered():
    document = DOCUMENT.read_text(encoding="utf-8")
    assert _field_block(document, "### 5.1 TrustBootstrapAuthorizationPayload") == (
        "payload_version", "authorization_id", "transaction_id", "target_host_identity_digest", "target_boot_digest",
        "trust_generation", "minimum_accepted_generation", "object_set_digest", "requested_objects", "mutation_scope",
        "local_console_attestation_digest", "governance_scope_digest", "bootstrap_authority_root_fingerprint",
        "bootstrap_authority_generation", "authority_set_record_digest", "issued_at_utc", "expires_at_utc", "nonce",
    )
    assert _field_block(document, "### 5.2 TrustBootstrapAuthorizationEnvelope") == (
        "envelope_version", "payload_sha256", "authorizing_role", "authorizing_authority_id",
        "authenticated_evidence_algorithm", "detached_signature", "verification_key_or_trust_source", "issued_at_utc",
        "expires_at_utc", "target_host_identity_digest", "target_boot_digest", "bootstrap_authority_root_fingerprint",
        "bootstrap_authority_generation", "authority_set_record_digest", "trust_generation", "object_set_digest", "nonce",
        "transaction_id", "domain_separator",
    )
    assert _field_block(document, "### 5.3 LocalConsoleAttestationEvidence")[-1] == "authenticated_evidence"
    assert _field_block(document, "### 5.4 GovernanceScopeEvidence")[-1] == "authenticated_evidence"
    assert "verification_context_digest" in _field_block(document, "### 5.5 DurableConsumptionRecord")
    positions = [document.index(state) for state in STATE_SEQUENCE]
    assert positions == sorted(positions)
    for object_path in OBJECTS:
        assert object_path in document


def test_durability_and_recovery_claims_are_explicit():
    document = DOCUMENT.read_text(encoding="utf-8")
    for phrase in (
        "state.sqlite3", "SQLite WAL", "synchronous=FULL", "audit table", "prior-generation retention",
        "exact prior bytes", "reverse publication order", "ROOT_REVIEW_REQUIRED", "filesystem-atomic",
        "does not make the five-object publication filesystem-atomic", "Identical completed retry",
        "conflicting retry", "Expiry prevents a new mutation intent", "terminal observation",
        "TrustVerificationContext", "verification_context_digest", "AFTER_STAGED_FILE_FSYNC",
        "AFTER_STAGING_DIRECTORY_FSYNC", "RecoveryObservation", "RecoveryVerification",
        "DURING_TERMINAL_STATE_UPDATE", "BETWEEN_TERMINAL_STATE_AND_AUDIT", "AFTER_TERMINAL_AUDIT_BEFORE_COMMIT",
        "M127A is finalized as a bounded isolated-root implementation foundation",
        "Git-durable, committed, tagged, and pushed",
    ):
        assert phrase in document
    assert "does not install trust objects on a real host" in document
    assert "VERIFICATION_STATUS: TEST_VERIFIED" in document


def test_implementation_has_no_shell_or_privileged_adapter_authority():
    source = (ROOT / "aether/deployment/host_trust_bootstrap.py").read_text(encoding="utf-8")
    for forbidden in ("systemctl", "os.system", "socket.AF_INET", "Popen", "BEGIN PRIVATE KEY"):
        assert forbidden not in source
    assert "genpkey" not in source
    assert '"-sign"' not in source
    assert "_ephemeral_key" not in source
    assert "create_isolated_root" in source
    assert "_require_capability" in source
    assert "verify_detached_ed25519" in source
    assert 'OPENSSL = "/usr/bin/openssl"' in source
    assert "subprocess.run" in source
    assert "journal_mode=WAL" in source
    assert "BEGIN IMMEDIATE" in source
    assert "_validate_consumption_time" in source
    assert "_validate_retry_identity" in source
    assert "_fsync_directory" in source
    assert "_write_exclusive" in source
    assert "recovery_observations" in source
    assert "recovery_verifications" in source


def test_no_private_key_pem_or_live_completion_claims_are_present():
    document = DOCUMENT.read_text(encoding="utf-8")
    assert not re.search(r"-----BEGIN [A-Z ]+-----", document)
    for phrase in ("PRIVATE_KEYS_CREATED: YES", "PRIVATE_KEYS_ACCESSED: YES", "PRODUCTION_PRIVATE_KEYS_CREATED: YES", "PRODUCTION_PRIVATE_KEYS_ACCESSED: YES", "PRODUCTION_SIGNING_CAPABILITY_IMPLEMENTED: YES", "M127A_FINALIZED: NO", "LIVE_DEPLOYMENT_AUTHORIZED: YES", "HOST_TRUST_OBJECTS_INSTALLED: YES", "PRODUCTION_OS_IMAGE_BASELINE_VERIFIED: YES"):
        assert phrase not in document


def test_external_summary_is_required_and_status_bound():
    assert SUMMARY.exists()
    summary = SUMMARY.read_text(encoding="utf-8")
    assert _status_map(summary) == CANONICAL_STATUS
    for phrase in (
        "evidence, not authority", "PM finalization authorization", "state.sqlite3", "TEST_VERIFIED",
        "TEST_ONLY_EPHEMERAL_KEYS_USED: YES", "TEST_PRIVATE_KEYS_PERSISTED: NO",
        "TEST_PRIVATE_KEYS_ENTERED_GIT_ARTIFACTS: NO", "FINAL_ARTIFACT_HASHES",
        "READY_FOR_PM_REVIEW: NO", "M127A_FINALIZED: YES",
    ):
        assert phrase in summary


def test_finalized_behavioral_matrices_are_present_without_bypass():
    source = (ROOT / "aether/deployment/host_trust_bootstrap.py").read_text(encoding="utf-8")
    tests = (ROOT / "tests/test_deployment_host_trust_bootstrap.py").read_text(encoding="utf-8")
    document = DOCUMENT.read_text(encoding="utf-8")
    for phrase in (
        "arbitrary_verifier", "wrong_context", "every_signed_envelope_field", "every_local_console_field",
        "every_governance_field", "AFTER_STAGED_FILE_FSYNC_4", "BETWEEN_USR_LIBEXEC_AND_ETC_PUBLICATION",
        "AFTER_TERMINAL_AUDIT_BEFORE_COMMIT", "ThreadPoolExecutor", "changed_columns", "symlink",
    ):
        assert phrase in source or phrase in tests
    assert "monkeypatch" not in tests
    assert "TEST_ONLY_EPHEMERAL_KEYS_USED: YES" in document
    assert "PRODUCTION_SIGNING_CAPABILITY_IMPLEMENTED: NO" in document


def test_resumed_fourth_corrective_valid_concurrency_and_generation_contract_is_locked():
    source = (ROOT / "aether/deployment/host_trust_bootstrap.py").read_text(encoding="utf-8")
    tests = (ROOT / "tests/test_deployment_host_trust_bootstrap.py").read_text(encoding="utf-8")
    document = DOCUMENT.read_text(encoding="utf-8")
    for phrase in (
        "CONTEXT_SCHEMA_VERSION", "VERIFICATION_POLICY_VERSION", "durable_fingerprint",
        "process_identity", "generation_reservations", "highest_seen_or_reserved_generation",
        "active_generation", "RESERVED", "BURNED", "bootstrap_from_raw", "allow_expired",
        "BEFORE_INTENT", "test_context_has_distinct_process_identity_and_restart_stable_durable_fingerprint",
        "test_fresh_context_raw_evidence_reconstruction_allows_only_identical_expired_intent",
        "test_concurrency_identical_transaction_uses_separate_foundations_and_one_commit",
        "test_concurrency_same_transaction_conflicts_have_one_exact_winner",
        "test_concurrency_resume_and_two_recovery_callers_have_one_terminal_review",
        "test_valid_same_nonce_competition_arbitrates_after_both_authorizations_verify",
        "test_valid_same_generation_competition_reserves_one_generation",
        "test_valid_lower_then_higher_generation_preserves_history_and_advances_active_set",
        "test_valid_higher_then_lower_generation_is_stale_without_intent_or_regression",
        "test_valid_burned_generation_cannot_be_reused_before_later_generation_activates",
        "_ephemeral_key",
        "_sign_ephemeral",
        "private_paths",
        "pkeyutl",
        "genpkey",
        "_dynamic_authorization(bundle",
        "test_complete_failpoint_matrix_has_exact_restart_outcome",
        "test_each_terminal_evidence_json_field_corruption_targets_intended_table",
        "test_recovery_evidence_bytes_and_digest_corruption_are_independent",
        "test_each_staged_identity_condition_reaches_its_named_rejection",
        "--deselect=tests/test_milestone_124a_oas_controlled_first_install_deployment_transaction_authorization_proof.py::test_repository_scope_is_exactly_the_two_m124a_artifacts",
        "--deselect=tests/test_milestone_125a_oas_first_install_rollback_to_not_deployed_durable_transaction_foundation_build.py::test_repository_scope_is_exactly_the_five_m125a_finalization_paths",
        "--deselect=tests/test_milestone_126a_oas_production_trust_material_and_host_trust_bootstrap_authority_contract_proof.py::test_finalization_repository_scope_is_exactly_five_paths",
        "claim-to-test", "evidence, not authority",
    ):
        assert phrase in source or phrase in tests or phrase in document or phrase in SUMMARY.read_text(encoding="utf-8")
    assert "secrets.token_bytes" not in source
    assert "maximum_trust_generation" not in source
    assert "state in {" not in tests
    assert "--ignore=" not in SUMMARY.read_text(encoding="utf-8")


def test_test_only_signing_is_confined_and_no_private_material_or_bypass_exists():
    source = (ROOT / "aether/deployment/host_trust_bootstrap.py").read_text(encoding="utf-8")
    tests = (ROOT / "tests/test_deployment_host_trust_bootstrap.py").read_text(encoding="utf-8")
    document = DOCUMENT.read_text(encoding="utf-8")
    for artifact in (source, tests, document):
        assert not re.search(r"-----BEGIN [A-Z ]*PRIVATE KEY-----", artifact)
    assert "genpkey" in tests and "pkeyutl" in tests
    assert "_ephemeral_key" not in source
    assert "_sign_ephemeral" not in source
    assert "monkeypatch" not in tests
    assert "TEST_ONLY_EPHEMERAL_KEYS_USED: YES" in document
    assert "TEST_PRIVATE_KEYS_PERSISTED: NO" in document
    assert "PRODUCTION_SIGNING_CAPABILITY_IMPLEMENTED: NO" in document


def test_untracked_artifacts_have_no_trailing_whitespace_or_conflict_markers():
    for relative in FINAL_REPOSITORY_PATHS:
        data = (ROOT / relative).read_bytes()
        assert all(not line.rstrip(b"\r\n").endswith((b" ", b"\t")) for line in data.splitlines())
        assert not re.search(rb"^(<<<<<<<|=======|>>>>>>>)", data, re.MULTILINE)
