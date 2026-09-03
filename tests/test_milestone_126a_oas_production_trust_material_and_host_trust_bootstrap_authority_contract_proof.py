"""Structural security lock for the corrected M126A design proof."""

from __future__ import annotations

from pathlib import Path
import re
import subprocess


ROOT = Path(__file__).resolve().parents[1]
DOCUMENT = ROOT / "docs/architecture/MILESTONE_126A_OAS_PRODUCTION_TRUST_MATERIAL_AND_HOST_TRUST_BOOTSTRAP_AUTHORITY_CONTRACT_PROOF.md"
ORIGINAL_SUMMARY = Path("/home/aether/summaries/milestone_126A_oas_production_trust_material_and_host_trust_bootstrap_authority_contract_proof_summary.txt")
CORRECTED_SUMMARY = Path("/home/aether/summaries/milestone_126A_corrected_oas_production_trust_material_and_host_trust_bootstrap_authority_contract_proof_summary.txt")
SECOND_CORRECTIVE_SUMMARY = Path("/home/aether/summaries/milestone_126A_second_corrective_oas_production_trust_material_and_host_trust_bootstrap_authority_contract_proof_summary.txt")
FINALIZATION_PATHS = {
    "PROGRESS.md",
    "docs/architecture/SECURITY_ARCHITECTURE.md",
    "tests/test_security_architecture_canonization.py",
    DOCUMENT.relative_to(ROOT).as_posix(),
    Path(__file__).relative_to(ROOT).as_posix(),
}
STATUS_BEGIN = "AUTHORITATIVE_M126A_STATUS_BEGIN"
STATUS_END = "AUTHORITATIVE_M126A_STATUS_END"
CANONICAL_STATUS = {
    "M126A_AUTHORIZED": "YES",
    "M126A_STARTED": "YES",
    "M126A_FINALIZED": "YES",
    "M126A_TYPE": "DESIGN_DISCOVERY_SECURITY_AND_OPERATIONS_CONTRACT_PROOF",
    "DECISION_STATUS": "CURRENT",
    "DESIGN_STATUS": "DESIGN_PROVEN",
    "IMPLEMENTATION_STATUS": "NOT_IMPLEMENTED",
    "VERIFICATION_STATUS": "TEST_VERIFIED",
    "DEPLOYMENT_VERIFIED": "NO",
    "DEPLOYMENT_STATE": "NOT_DEPLOYED",
    "DEPLOYMENT_PROFILE": "FIRST_INSTALL_LOCAL_AF_UNIX_ONLY",
    "TRUST_MATERIAL_CONTRACT_PROVEN": "YES",
    "TRUST_BOOTSTRAP_AUTHORITY_MODEL_SELECTED": "YES",
    "BOOTSTRAP_AUTHORITY_ROOT_MODEL": "BOOTSTRAP_AUTHORITY_ROOT_MODEL_A_OS_IMAGE_PROVISIONING_BASELINE",
    "PRE_INSTANCE_MODEL": "PRE_INSTANCE_MODEL_B_HOST_RELEASE_TRUST_BEFORE_EXPLICIT_INSTANCE_BINDING",
    "PRODUCTION_TRUST_MATERIAL_PROVEN": "NO",
    "PRIVATE_KEYS_CREATED": "NO",
    "PRIVATE_KEYS_ACCESSED": "NO",
    "HOST_TRUST_OBJECTS_INSTALLED": "NO",
    "TRUST_BOOTSTRAP_IMPLEMENTED": "NO",
    "TRUTHFUL_OWNER_DEPLOYMENT_AUTHORITY_PROVEN": "NO",
    "LIVE_DEPLOYMENT_AUTHORIZED": "NO",
    "LIVE_ROLLBACK_AUTHORIZED": "NO",
    "TARGET_HOST_MUTATION_PERFORMED": "NO",
    "BUILD_READINESS": "BOUNDED_TRUST_BOOTSTRAP_BUILD_JUSTIFIED_FOR_PM_REVIEW",
    "SELECTED_EXIT": "EXIT_A_BOUNDED_TRUST_BOOTSTRAP_BUILD_JUSTIFIED_FOR_PM_REVIEW",
    "PROGRESS_UPDATED": "YES",
    "COMMIT_CREATED": "YES",
    "TAG_CREATED": "YES",
    "PUSH_PERFORMED": "YES",
    "SUCCESSOR_AUTHORIZED": "NO",
    "SUCCESSOR_NUMBER_ASSIGNED": "NO",
    "READY_FOR_PM_REVIEW": "NO",
}
TRUST_OBJECTS = (
    "/etc/aether/release-trust-anchor.pub",
    "/etc/aether/release-trust-anchor.fingerprint",
    "/etc/aether/release-test-evidence.sha256",
    "/etc/aether/release-verifier.sha256",
    "/usr/libexec/aether-release-verify",
)
BOOTSTRAP_AUTHORITY_ROOT_MODEL = "BOOTSTRAP_AUTHORITY_ROOT_MODEL_A_OS_IMAGE_PROVISIONING_BASELINE"
PRE_INSTANCE_MODEL = "PRE_INSTANCE_MODEL_B_HOST_RELEASE_TRUST_BEFORE_EXPLICIT_INSTANCE_BINDING"
AUTHORITY_SET_PATH = "/usr/lib/aether/host-bootstrap/authority-set.json"
AUTHORITY_WRAPPER_FIELDS = (
    "authority_set_version", "baseline_id", "authority_records",
    "minimum_accepted_authority_generation", "set_fingerprint_sha256",
    "image_baseline_manifest_digest",
)
AUTHORITY_RECORD_FIELDS = (
    "authority_id", "authority_role", "algorithm", "public_key_base64url",
    "key_fingerprint_sha256", "authority_generation", "valid_from_utc",
    "valid_until_utc", "revoked_at_utc",
)
TRUST_SOURCE_REFERENCE_FIELDS = (
    "source_kind", "authority_set_path", "authority_set_record_digest",
    "authority_id", "key_fingerprint_sha256", "authority_generation",
    "image_baseline_manifest_digest",
)
PAYLOAD_FIELDS = (
    "payload_version", "authorization_id", "transaction_id",
    "target_host_identity_digest", "target_boot_digest",
    "trust_generation", "minimum_accepted_generation", "object_set_digest",
    "requested_objects", "mutation_scope", "local_console_attestation_digest",
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
    "authority_set_record_digest",
    "trust_generation", "object_set_digest", "nonce", "transaction_id",
    "domain_separator",
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
    "record_version", "transaction_id", "authorization_id", "envelope_sha256",
    "payload_sha256", "local_console_attestation_digest", "governance_scope_digest",
    "target_host_identity_digest", "target_boot_digest",
    "bootstrap_authority_root_fingerprint", "bootstrap_authority_generation",
    "authority_set_record_digest",
    "trust_generation", "object_set_digest", "nonce", "state",
    "previous_record_digest", "journal_head_digest", "issued_at_utc",
    "expires_at_utc", "consumed_at_utc", "result", "failure_class",
)
STATE_SEQUENCE = (
    "TRUST_BOOTSTRAP_REQUESTED",
    "TRUST_BOOTSTRAP_VALIDATED",
    "PRIOR_GENERATION_RETAINED",
    "NEXT_GENERATION_STAGED",
    "PUBLISHING",
    "VERIFYING",
    "TRUST_SET_ACTIVE",
    "RESTORING_PRIOR_GENERATION",
    "TRUST_BOOTSTRAP_REVIEW_REQUIRED",
)


def _changed_paths() -> set[str]:
    lines = subprocess.run(
        ["git", "status", "--short", "--untracked-files=all"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.splitlines()
    return {line[3:] for line in lines if len(line) >= 4 and line[:2] in {" M", "??", "A ", "AM"}}


def _status_map(text: str) -> dict[str, str]:
    assert text.count(STATUS_BEGIN) == text.count(STATUS_END) == 1
    block = text[text.index(STATUS_BEGIN):text.index(STATUS_END)]
    result: dict[str, str] = {}
    for line in block.splitlines()[1:]:
        if not line.strip():
            continue
        key, separator, value = line.strip().partition(":")
        assert separator
        assert key not in result
        result[key] = value.strip()
    return result


def _text_block(document: str, heading: str) -> tuple[str, ...]:
    start = document.index(heading)
    start = document.index("```text", start) + len("```text\n")
    end = document.index("```", start)
    return tuple(line.strip() for line in document[start:end].splitlines() if line.strip())


def _code_block_after(document: str, anchor: str) -> tuple[str, ...]:
    start = document.index(anchor)
    start = document.index("```text", start) + len("```text\n")
    end = document.index("```", start)
    return tuple(line.strip() for line in document[start:end].splitlines() if line.strip())


def _contains(text: str, phrase: str) -> bool:
    return " ".join(phrase.split()) in " ".join(text.split())


def test_finalization_repository_scope_is_exactly_five_paths():
    document = DOCUMENT.read_text(encoding="utf-8")
    for path in FINALIZATION_PATHS:
        assert f"`{path}`" in document or path in document
    changed_paths = _changed_paths()
    assert changed_paths == FINALIZATION_PATHS or not changed_paths


def test_authoritative_status_is_exact_and_negative_gated():
    document = DOCUMENT.read_text(encoding="utf-8")
    assert _status_map(document) == CANONICAL_STATUS
    assert document.count("SELECTED_AUTHORITY_MODEL:") == 1
    assert document.count("SELECTED_EXIT: EXIT_A_BOUNDED_TRUST_BOOTSTRAP_BUILD_JUSTIFIED_FOR_PM_REVIEW") == 1
    for forbidden in (
        "PRIVATE_KEYS_CREATED: YES", "PRIVATE_KEYS_ACCESSED: YES",
        "HOST_TRUST_OBJECTS_INSTALLED: YES", "TRUST_BOOTSTRAP_IMPLEMENTED: YES",
        "TRUTHFUL_OWNER_DEPLOYMENT_AUTHORITY_PROVEN: YES",
        "LIVE_DEPLOYMENT_AUTHORIZED: YES", "LIVE_ROLLBACK_AUTHORIZED: YES",
        "TARGET_HOST_MUTATION_PERFORMED: YES",
        "SUCCESSOR_AUTHORIZED: YES", "SUCCESSOR_NUMBER_ASSIGNED: YES",
    ):
        assert forbidden not in document


def test_authenticated_records_are_separate_and_exactly_structured():
    document = DOCUMENT.read_text(encoding="utf-8")
    assert _text_block(document, "### 5.1 TrustBootstrapAuthorizationPayload") == PAYLOAD_FIELDS
    assert _text_block(document, "### 5.2 TrustBootstrapAuthorizationEnvelope") == ENVELOPE_FIELDS
    assert _text_block(document, "### 5.3 LocalConsoleAttestationEvidence") == LOCAL_FIELDS
    assert _text_block(document, "### 5.4 GovernanceScopeEvidence") == GOVERNANCE_FIELDS
    assert _text_block(document, "### 5.5 DurableConsumptionRecord") == DURABLE_FIELDS
    for phrase in (
        "TrustBootstrapAuthorizationPayload",
        "TrustBootstrapAuthorizationEnvelope",
        "LocalConsoleAttestationEvidence",
        "GovernanceScopeEvidence",
        "DurableConsumptionRecord",
        "ED25519_DETACHED_SIGNATURE_V1",
        "aether.m126a.trust-bootstrap-authorization.v1",
        "canonical payload digest",
        "PUBLISH_EXACT_FIVE_HOST_TRUST_OBJECTS_FOR_TARGET_HOST_AND_GENERATION",
    ):
        assert _contains(document, phrase)


def test_bootstrap_authority_root_is_selected_and_structurally_defined():
    document = DOCUMENT.read_text(encoding="utf-8")
    comparison = document[document.index("### 3.2 Bootstrap-authority root model comparison"):document.index("### 3.3 Selected bootstrap-authority root contract")]
    assert comparison.count("**SELECTED**") == 1
    assert BOOTSTRAP_AUTHORITY_ROOT_MODEL in comparison
    root = document[document.index("### 3.3 Selected bootstrap-authority root contract"):document.index("## 4. Trust Roles and Separation")]
    assert AUTHORITY_SET_PATH in root
    assert _code_block_after(root, "The authority-set record is canonical") == AUTHORITY_WRAPPER_FIELDS
    assert _code_block_after(root, "Each authority record has exactly these fields") == AUTHORITY_RECORD_FIELDS
    envelope = document[document.index("### 5.2 TrustBootstrapAuthorizationEnvelope"):document.index("### 5.3 LocalConsoleAttestationEvidence")]
    assert _code_block_after(envelope, "verification_key_or_trust_source` is a structured reference") == TRUST_SOURCE_REFERENCE_FIELDS
    assert "PREEXISTING_OS_IMAGE_AUTHORITY_SET" in envelope
    for phrase in (
        "pre-Aether OS/image provisioning baseline",
        "32-byte raw Ed25519 public key",
        "aether.m126a.host-bootstrap-authority-key.v1",
        "independent host-security approver",
        "OS/image provisioning approver",
        "baseline membership",
        "valid signature under a key",
        "is not in this independently authenticated baseline fails closed",
        "Candidate, OAS, ordinary runtime",
        "root possession cannot supply or replace this trust source",
    ):
        assert _contains(root, phrase)
    local = document[document.index("### 5.3 LocalConsoleAttestationEvidence"):document.index("### 5.4 GovernanceScopeEvidence")]
    assert _contains(local, "local-console record is authenticated by the separate OS-attested local-seat mechanism")


def test_bootstrap_authority_key_domain_and_lifecycle_are_complete():
    document = DOCUMENT.read_text(encoding="utf-8")
    lifecycle = document[document.index("### 11.1 Bootstrap-authority verification-key lifecycle"):document.index("Trust generation is a monotonically increasing")]
    assert lifecycle.count("| Lifecycle stage |") == 1
    for phrase in (
        "distinct trust domain", "HOST_TRUST_BOOTSTRAP_AUTHORITY",
        "aether.m126a.trust-bootstrap-authorization.v1",
        "cannot authorize release signing, release approval, Owner authentication, deployment, activation, rollback, Generic Act",
        "Initial approval", "Introduction", "Identity and validity", "Normal use",
        "Planned rotation", "Revocation", "Compromise response", "Loss and recovery",
        "Offline backup", "Host replacement", "Replay state", "Retirement",
        "no dual-acceptance signing overlap", "old key cannot authorize its own replacement",
        "root cannot rotate it by possession alone", "fresh verified OS/image baseline",
        "fresh OS-attested local-console human ceremony",
    ):
        assert _contains(lifecycle, phrase)


def test_pre_instance_model_is_bounded_before_owner_instance_binding():
    document = DOCUMENT.read_text(encoding="utf-8")
    section = document[document.index("### Release trust versus Owner trust"):document.index("## 14. Complete Release Verification Chain")]
    assert PRE_INSTANCE_MODEL in section
    for phrase in (
        "EMPTY_HOST", "VERIFIED_OS_IMAGE_AUTHORITY_BASELINE",
        "TRUST_SET_ACTIVE_FOR_TARGET_HOST_AND_GENERATION",
        "CANDIDATE_RELEASE_PROVENANCE_MAY_BE_VERIFIED",
        "M124A_DEPLOYMENT_PACKET_BINDS_VERIFIED_RELEASE_AND_EXACT_HOST_TRUST_GENERATION",
        "PACKET_BINDS_EXPLICIT_AETHER_INSTANCE_ID_AND_TRUTHFUL_OWNER_DEPLOYMENT_AUTHORITY",
        "host trust set authenticates software provenance only",
        "does not authenticate an Owner, create an Aether Instance, authorize deployment, or activate software",
        "exact non-null Aether Instance ID",
        "current truthful Owner source remains unimplemented and unproven",
    ):
        assert _contains(section, phrase)
    payload_fields = _text_block(document, "### 5.1 TrustBootstrapAuthorizationPayload")
    assert "aether_instance_id" not in payload_fields
    assert "owner_authorization_digest" not in payload_fields


def test_envelope_verification_and_authority_rejection_are_ordered():
    document = DOCUMENT.read_text(encoding="utf-8")
    verification = document[document.index("### 5.6 Envelope verification before mutation intent"):]
    ordered = (
        "Parse the payload, envelope, local-console evidence, and governance evidence",
        "Recompute `payload_sha256`",
        "require the exact role, authority identifier, algorithm, domain",
        "Verify the local-console evidence and the governance evidence independently",
        "Bind every copied envelope field to the payload",
        "Verify the target host identity, current boot, unused transaction/nonce",
        "Confirm that no durable intent exists for this transaction",
        "Only then persist `TRUST_BOOTSTRAP_REQUESTED`",
    )
    positions = [verification.index(phrase) for phrase in ordered]
    assert positions == sorted(positions)
    for phrase in (
        "bare digest", "unsigned JSON", "unknown or ambiguous signing authority",
        "PM-only evidence", "root-only evidence", "candidate verification keys",
        "ordinary-runtime evidence", "OAS evidence",
        "No key, signature, credential, or live source is created or accessed during M126A",
    ):
        assert _contains(document, phrase)


def test_role_and_object_ownership_are_not_collapsed():
    document = DOCUMENT.read_text(encoding="utf-8")
    for phrase in (
        "Owner | Provides future instance/host-specific deployment and activation authorization",
        "Project Manager / governance approval | Approves milestone scope and security policy only",
        "Host trust-bootstrap authority | Validates the OS-attested local-console operator evidence",
        "Root trust-bootstrap executor | Verifies the envelope and performs only the exact bounded filesystem mutation",
        "Fixed host verifier | Verifies release artifacts only after its own identity is independently established",
        "it must not recursively establish its own trust",
        "Source authority", "Policy approval", "Transaction authorization",
        "Mutation executor", "Postcondition verifier",
        "The host trust-bootstrap authority authenticates the envelope; it is not the mutation executor.",
    ):
        assert _contains(document, phrase)
    object_section = document[document.index("## 7. The Five Fixed Host Trust Objects"):document.index("## 8. Initial Bootstrap Ceremony")]
    assert object_section.count("| **NEVER**") == 5
    for path in TRUST_OBJECTS:
        assert path in object_section
    assert object_section.count("Root trust-bootstrap executor") >= 5


def test_fixed_verifier_uses_an_independent_preexisting_trust_base():
    document = DOCUMENT.read_text(encoding="utf-8")
    for phrase in (
        "PREEXISTING_OS_ROOT_TRUST_BASE", "exact executable bytes", "approved SHA-256",
        "hard-link identity", "interpreter or native-executable identity",
        "library/dependency policy", "fixed argv contract", "fixed environment contract",
        "does not execute the candidate fixed verifier",
        "Only after the independent digest and execution boundary pass",
        "The fixed verifier verifies release signatures and approval signatures only",
        "OS, kernel, root filesystem", "No protection from compromise of that base is claimed",
    ):
        assert _contains(document, phrase)


def test_expiry_resume_and_cross_directory_state_machine_are_structural():
    document = DOCUMENT.read_text(encoding="utf-8")
    states = _text_block(document, "## 9. Cross-Directory Publication, Rotation, and Recovery")
    assert states[:len(STATE_SEQUENCE)] == STATE_SEQUENCE
    for phrase in (
        "NEW TRANSACTION", "STARTED TRANSACTION",
        "Expiry before `TRUST_BOOTSTRAP_REQUESTED` prevents every mutation",
        "After wall-clock expiry, an identical retry may resume only this frozen transaction",
        "Resume cannot expand scope, change objects, change generation, change authority, or begin a new transaction",
        "Expired authority never starts a new mutation",
        "an already-started transaction is not stranded solely because wall-clock expiry occurred after durable intent",
        "Between `/usr/libexec` and `/etc` publication",
        "After all writes, before `VERIFYING`",
        "After state/audit commit",
        "Prior bytes unavailable or changed",
        "Conflicting retry",
    ):
        assert _contains(document, phrase)
    assert "atomic five-object publication is made" in document
    assert "five-object publication is not filesystem-atomic" in document


def test_prior_generation_retention_journal_and_recovery_requirements_exist():
    document = DOCUMENT.read_text(encoding="utf-8")
    for phrase in (
        "exact prior five-object bytes", "paths, owner/mode/link identity",
        "prior trust generation", "prior trust-set digest", "prior anchor fingerprint",
        "prior verifier digest", "recovery transaction binding", "root-only",
        "outside candidate control", "transaction-bound", "directory-fsynced",
        "immutable to ordinary runtime and OAS",
        "previous_record_digest", "authorization_digest", "envelope_digest",
        "payload_digest", "fsync_result", "record_digest",
        "reverse publication order", "Automatic restoration is prohibited",
        "terminal Observation and Verification", "no partial restoration is active",
    ):
        assert _contains(document, phrase)


def test_state_audit_and_filesystem_atomicity_are_distinguished():
    document = DOCUMENT.read_text(encoding="utf-8")
    for phrase in (
        "Filesystem publication is a multi-step mutation",
        "is not atomic across `/etc/aether` and `/usr/libexec`",
        "/var/lib/aether/trust-bootstrap/state.sqlite3",
        "owned by the fixed root trust-bootstrap executor",
        "may commit atomically in one durable state-store transaction",
        "does not make filesystem writes atomic",
        "`TRUST_SET_ACTIVE` may be committed only after terminal Observation and Verification",
        "later observation is ambiguous or differs, release acceptance fails closed immediately",
        "External logs are asynchronous copies and remain non-authoritative",
        "The terminal Observation record and terminal Verification record are required",
    ):
        assert _contains(document, phrase)


def test_release_trust_owner_trust_and_identity_rule_are_separate():
    document = DOCUMENT.read_text(encoding="utf-8")
    for phrase in (
        "software supply-chain release trust separately from the M117A",
        "It does not authenticate the Owner",
        "establish the Owner trust root",
        "A clone or fork must receive a new Aether Instance ID and a new Owner trust root",
        "Copying the five host objects does not authorize the clone or fork",
        "A new release anchor is required only when the release-trust policy or custody requires it",
        "Host trust generation and Owner trust generation remain separate namespaces",
        "PRE_INSTANCE_MODEL_B_HOST_RELEASE_TRUST_BEFORE_EXPLICIT_INSTANCE_BINDING",
        "host trust set authenticates software provenance only",
        "exact non-null Aether Instance ID",
        "Copying host trust objects does not authorize an instance",
    ):
        assert _contains(document, phrase)
    payload_fields = _text_block(document, "### 5.1 TrustBootstrapAuthorizationPayload")
    assert "aether_instance_id" not in payload_fields


def test_build_boundary_and_negative_implementation_claims_are_explicit():
    document = DOCUMENT.read_text(encoding="utf-8")
    for phrase in (
        "M126A does not generate, search for, import, display, copy, install, rotate, or",
        "No production code is changed", "PRIVATE_KEYS_CREATED: NO",
        "PRIVATE_KEYS_ACCESSED: NO", "HOST_TRUST_OBJECTS_INSTALLED: NO",
        "TRUST_BOOTSTRAP_IMPLEMENTED: NO", "TARGET_HOST_MUTATION_PERFORMED: NO",
        "create production keys", "create test private keys", "sign artifacts",
        "implement the live Owner authority source", "install real host objects",
        "implement live root/systemd helpers", "deploy OAS",
        "prove production trust custody or truthful Owner deployment authority",
        "It does not authorize a Build", "This record does not assign a successor milestone",
    ):
        assert _contains(document, phrase)
    assert not re.search(r"-----BEGIN [A-Z ]+-----", document)


def test_original_and_corrected_external_summaries_preserve_status_and_scope():
    document = DOCUMENT.read_text(encoding="utf-8")
    assert ORIGINAL_SUMMARY.exists()
    assert CORRECTED_SUMMARY.exists()
    assert SECOND_CORRECTIVE_SUMMARY.exists()
    corrected = CORRECTED_SUMMARY.read_text(encoding="utf-8")
    second = SECOND_CORRECTIVE_SUMMARY.read_text(encoding="utf-8")
    corrected_status = _status_map(corrected)
    assert corrected_status["M126A_FINALIZED"] == "NO"
    assert corrected_status["TRUST_MATERIAL_CONTRACT_PROVEN"] == "YES"
    assert corrected_status["READY_FOR_PM_REVIEW"] == "YES"
    pre_finalization_status = dict(CANONICAL_STATUS)
    pre_finalization_status["DECISION_STATUS"] = "PM_REVIEW_PENDING"
    for key in ("M126A_FINALIZED", "PROGRESS_UPDATED", "COMMIT_CREATED", "TAG_CREATED", "PUSH_PERFORMED"):
        pre_finalization_status[key] = "NO"
    pre_finalization_status["READY_FOR_PM_REVIEW"] = "YES"
    assert _status_map(second) == pre_finalization_status
    assert "EXTERNAL_SUMMARY_PATH: /home/aether/summaries/milestone_126A_corrected_oas_production_trust_material_and_host_trust_bootstrap_authority_contract_proof_summary.txt" in corrected
    assert "EXTERNAL_SUMMARY_PATH: /home/aether/summaries/milestone_126A_second_corrective_oas_production_trust_material_and_host_trust_bootstrap_authority_contract_proof_summary.txt" in second
    assert "evidence, not authority" in corrected
    assert "M126A_FINALIZED: YES" in document
    assert "PROGRESS_UPDATED: YES" in document
    assert "COMMIT_CREATED: YES" in document
    assert "TAG_CREATED: YES" in document
    assert "PUSH_PERFORMED: YES" in document
    for text in (second,):
        assert BOOTSTRAP_AUTHORITY_ROOT_MODEL in text
        assert PRE_INSTANCE_MODEL in text
        assert AUTHORITY_SET_PATH in text
        assert "MODEL_A_OFFLINE_PRODUCTION_SIGNING_PLUS_SEPARATE_LOCAL_CONSOLE_HOST_TRUST_BOOTSTRAP" in text
        assert "/etc/aether/release-trust-anchor.pub" in text
        assert "/usr/libexec/aether-release-verify" in text
        assert "PRIVATE_KEYS_ACCESSED: NO" in text
        assert "PROGRESS_UPDATED: NO" in text
        assert "COMMIT_CREATED: NO" in text
        assert "TAG_CREATED: NO" in text
        assert "PUSH_PERFORMED: NO" in text
        assert not re.search(r"-----BEGIN [A-Z ]+-----", text)


def test_document_section_numbers_and_subheadings_are_unique_and_ordered():
    document = DOCUMENT.read_text(encoding="utf-8")
    section_numbers = [int(match.group(1)) for match in re.finditer(r"^## (\d+)\.", document, re.MULTILINE)]
    assert section_numbers == list(range(1, 20))
    assert len(section_numbers) == len(set(section_numbers))
    subheadings = re.findall(r"^### ([^\n]+)$", document, re.MULTILINE)
    assert len(subheadings) == len(set(subheadings))
    assert document.count("### 6.1 Private-Key Boundary") == 1
    assert document.count("### 15.1 Public evidence and sensitive-data classification") == 1
    assert document.count("### 15.2 Public evidence contents and digest limits") == 1
