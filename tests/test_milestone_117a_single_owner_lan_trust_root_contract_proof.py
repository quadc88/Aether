"""Static documentation lock for the corrected M117A design proof."""

from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / (
    "docs/architecture/"
    "MILESTONE_117A_SINGLE_OWNER_LAN_TRUST_ROOT_CONTRACT_PROOF.md"
)

FORMAL_BEGIN = "AUTHORITATIVE_FORMAL_DECISION_BLOCK_BEGIN"
FORMAL_END = "AUTHORITATIVE_FORMAL_DECISION_BLOCK_END"

FORMAL_IDENTIFIERS = (
    "SELECTED_DEPLOYMENT_PROFILE",
    "SELECTED_TARGET_TRUST_ROOT_MODEL",
    "CURRENT_TRUST_ROOT_STATE",
    "ENTRY_TRUST_ROOT_MATURITY",
    "TARGET_TRUST_ROOT_MATURITY",
    "RESULT_TRUST_ROOT_MATURITY",
    "TR2_PROVEN",
    "SELECTED_BOOTSTRAP_PRESENCE_MODEL",
    "SELECTED_RECOVERY_PRESENCE_MODEL",
    "SSH_BOOTSTRAP_ALLOWED",
    "SSH_RECOVERY_ALLOWED",
    "SELECTED_AUTHORITY_BOUNDARY_MODEL",
    "SELECTED_AUTHENTICATION_TERMINATION_MODEL",
    "AETHER_RUNTIME_CAN_MINT_OWNER_EVIDENCE",
    "SELECTED_TLS_TERMINATION_MODEL",
    "PROXY_HEADERS_TRUSTED_BY_DEFAULT",
    "DIRECT_BACKEND_BYPASS_ALLOWED",
    "SELECTED_CREDENTIAL_MODEL",
    "SELECTED_WEBAUTHN_ENROLLMENT_MODEL",
    "WEBAUTHN_REGISTRATION_CEREMONY_TYPE",
    "WEBAUTHN_AUTHENTICATION_CEREMONY_TYPE",
    "WEBAUTHN_USER_PRESENCE_REQUIRED",
    "WEBAUTHN_USER_VERIFICATION_REQUIRED",
    "WEBAUTHN_ATTESTATION_POLICY",
    "SYNCED_PASSKEY_POLICY",
    "CREDENTIAL_REVOCATION_EQUALS_PHYSICAL_DEVICE_REVOCATION",
    "SELECTED_SESSION_MODEL",
    "SELECTED_CSRF_ORIGIN_MODEL",
    "ORDINARY_SESSION_CAN_ENTER_RECOVERY",
    "RECOVERY_ENTROPY",
    "SELECTED_RECOVERY_MODEL",
    "SELECTED_REVOCATION_MODEL",
    "SELECTED_AUDIT_ATOMICITY_MODEL",
    "CANONICAL_SECURITY_MUTATION_WITHOUT_AUDIT_CAN_SUCCEED",
    "SELECTED_BACKUP_MODEL",
    "SELECTED_RESTORE_MODEL",
    "SELECTED_MIGRATION_MODEL",
    "SELECTED_CLONE_MODEL",
    "GLOBAL_SPLIT_BRAIN_PREVENTION",
    "AETHER_INSTANCE_BINDING",
    "SELECTED_SOURCE_EVENT_MODEL",
    "SELECTED_CLAIM_ENROLLMENT_TRANSACTION_MODEL",
    "SELECTED_SOURCE_EVENT_CONSUMPTION_MODEL",
    "CROSS_BOUNDARY_ATOMIC_GOAL_RECEIPT",
    "AUTHENTICATED_SOURCE_EVENT_OWNER",
    "AUTHENTICATED_SOURCE_EVENT_RECEIPT_OWNER",
    "CORE_CANONICAL_GOAL_STATE_OWNER",
    "MUTATING_GOAL_OPERATIONS",
    "READ_ONLY_GOAL_OPERATION",
    "SOURCE_AUTHENTICATION_EQUALS_INTENT_INTERPRETATION",
    "GOAL_ACCEPTANCE_AUTHORIZES_ACTION",
    "ACTION_SUCCESS_PROVES_COMPLETION",
    "COMPLETION_REQUIRES_OBSERVATION_AND_VERIFICATION",
    "HUMAN_AUTHORITY_MATURITY",
    "GOAL_INTAKE_MATURITY",
    "MINIMALITY_DECISION",
    "BUILD_READINESS",
    "CORE_DRIFT_DETECTED",
    "NEXT_FRONTIER",
    "NEXT_MILESTONE_TYPE",
)


def _text() -> str:
    return RECORD.read_text(encoding="utf-8")


def _formal(text: str) -> str:
    assert text.count(FORMAL_BEGIN) == 1
    assert text.count(FORMAL_END) == 1
    start = text.index(FORMAL_BEGIN)
    end = text.index(FORMAL_END) + len(FORMAL_END)
    return text[start:end]


def _assert_required(text: str, *markers: str) -> None:
    for marker in markers:
        assert marker in text, marker


def test_m117a_has_one_complete_formal_decision_block():
    text = _text()
    formal = _formal(text)
    for identifier in FORMAL_IDENTIFIERS:
        assert text.count(f"{identifier}:") == 1, identifier
        assert f"{identifier}:" in formal, identifier
    _assert_required(
        formal,
        "SELECTED_DEPLOYMENT_PROFILE:\nDEPLOYMENT_PROFILE_B_SINGLE_OWNER_LOCAL_NETWORK",
        "SELECTED_TARGET_TRUST_ROOT_MODEL:\nTRUST_ROOT_MODEL_J_HYBRID_BOOTSTRAP_AND_AUTHENTICATED_CHANNEL",
        "ENTRY_TRUST_ROOT_MATURITY:\nTR1_TRUST_ROOT_REQUIREMENTS_IDENTIFIED",
        "RESULT_TRUST_ROOT_MATURITY:\nTR2_BOUNDED_TRUST_ROOT_CONTRACT_PROVEN_DESIGN_ONLY",
        "TR2_PROVEN:\nYES",
        "BUILD_READINESS:\nBOUNDED_TRUST_ROOT_BUILD_JUSTIFIED_FOR_PM_REVIEW",
        "MINIMALITY_DECISION:\nMINIMAL_CONTRACT_PROVEN_FOR_BOUNDED_SINGLE_OWNER_LAN_DESIGN",
    )


def test_m117a_locks_lineage_scope_and_frozen_direction():
    text = _text()
    _assert_required(
        text,
        "M116A finalized the truthful negative/current-state trust-root decision.",
        "M117A begins a new Project-Owner-requirements-derived single-owner LAN trust-root contract frontier.",
        "M116A was not a partial production implementation milestone.",
        "No M116B continuation was required.",
        "M117A remains design/discovery/security-contract proof only.",
        "OWNER <-> AETHER INSTANCE",
        "one Aether Instance has exactly one true Owner",
        "DEPLOYMENT_PROFILE_B_SINGLE_OWNER_LOCAL_NETWORK",
        "TRUST_ROOT_MODEL_J_HYBRID_BOOTSTRAP_AND_AUTHENTICATED_CHANNEL",
        "NO_AUTHENTICATED_OWNER_SOURCE_EXISTS",
        "HA1_REQUIRED_FIELDS_IDENTIFIED_BUT_SEMANTICS_INCOMPLETE",
        "GI2_CANONICAL_OWNER_PROVEN_ENTRY_CONTRACT_INCOMPLETE",
        "No production authentication",
        "No successor milestone number is assigned",
    )


def test_m117a_locks_presence_boundary_and_authentication_termination():
    text = _text()
    _assert_required(
        text,
        "BOOTSTRAP_PRESENCE_A_COMMAND_RUNS_ON_HOST",
        "BOOTSTRAP_PRESENCE_B_PRIVILEGED_TTY_WITH_CALLER_ASSERTED_LOCALITY",
        "BOOTSTRAP_PRESENCE_C_OS_ATTESTED_LOCAL_CONSOLE_PRIVILEGED_IPC",
        "BOOTSTRAP_PRESENCE_D_NO_TRUTHFUL_LOCAL_BOOTSTRAP_PROVEN",
        "RECOVERY_PRESENCE_A_AUTHENTICATED_BROWSER_SESSION",
        "RECOVERY_PRESENCE_B_COMMAND_RUNS_ON_HOST",
        "RECOVERY_PRESENCE_C_OS_ATTESTED_LOCAL_CONSOLE_PLUS_OFFLINE_MATERIAL",
        "RECOVERY_PRESENCE_D_NO_TRUTHFUL_LOCAL_RECOVERY_PROVEN",
        "active OS-recognized local console or local seat",
        "non-remote",
        "kernel-supplied PID, UID, GID",
        "aether-local-presence",
        "SSH sessions",
        "SSH port forwarding",
        "remote pseudo-terminals",
        "caller-supplied locality flags",
        "REJECT_BEFORE_MUTATION",
        "host kernel and host root",
        "ordinary authenticated browser session cannot enter",
        "AUTHORITY_BOUNDARY_A_SAME_PROCESS_MODULE",
        "AUTHORITY_BOUNDARY_B_SEPARATE_PROCESS_SAME_OS_PRINCIPAL",
        "AUTHORITY_BOUNDARY_C_SEPARATE_OS_PRINCIPAL_RESTRICTED_IPC_PROTECTED_AUTHORITY_MATERIAL",
        "AUTH_TERMINATION_A_ORDINARY_AETHER_RUNTIME",
        "AUTH_TERMINATION_B_OWNER_AUTHORITY_SERVICE",
        "AUTH_TERMINATION_C_NO_COMPLETE_TERMINATION_CONTRACT_PROVEN",
        "WebAuthn registration challenge",
        "authority-signing private key",
        "no raw reusable handle",
    )


def test_m117a_locks_tls_credentials_sessions_and_usability():
    text = _text()
    _assert_required(
        text,
        "TLS_MODEL_A_DIRECT_TLS_TERMINATION_AT_OWNER_AUTHORITY_SERVICE",
        "TLS_MODEL_B_PROTECTED_TRUSTED_PROXY_TO_RESTRICTED_AUTH_BACKEND",
        "TLS_MODEL_C_NO_COMPLETE_TLS_TRUST_BOUNDARY_PROVEN",
        "direct TLS termination at OAS",
        "Forwarded",
        "X-Forwarded-For",
        "X-Forwarded-Proto",
        "Direct backend requests are rejected",
        "CREDENTIAL_MODEL_A_SYNCED_WEBAUTHN_PASSKEY_ALLOWED",
        "CREDENTIAL_MODEL_B_DEVICE_BOUND_WEBAUTHN_CREDENTIAL_REQUIRED",
        "CREDENTIAL_MODEL_C_HARDWARE_SECURITY_KEY_REQUIRED",
        "CREDENTIAL_MODEL_D_EXPLICIT_MIXED_WEBAUTHN_PROFILE",
        "CREDENTIAL_MODEL_E_NO_COMPLETE_CREDENTIAL_PROFILE_PROVEN",
        "backup-eligibility",
        "lost phone -> revoke only that phone",
        "split-horizon",
        "RP ID",
        "http://192.168.x.x",
        "Secure",
        "HttpOnly",
        "SameSite=Strict",
        "CSRF",
        "Fetch Metadata",
        "AUTHENTICATED_BROWSER_SESSION",
        "CROSS_SITE_REQUEST",
        "OWNER_AUTHORIZATION",
    )


def test_m117a_locks_lifecycle_claim_recovery_revocation_and_audit():
    text = _text()
    _assert_required(
        text,
        "UNCLAIMED -> CLAIM_PENDING -> OWNED",
        "OWNED -> RECOVERY_PENDING -> OWNED",
        "CLAIM_PENDING -> UNCLAIMED",
        "RECOVERY_PENDING -> OWNED unchanged",
        "Claim Token",
        "at least 128 bits of entropy",
        "SECURITY_STATE_COMMIT",
        "CANONICAL_SECURITY_AUDIT_COMMIT",
        "ONE_ATOMIC_SECURITY_TRANSACTION",
        "External syslog",
        "In-memory audit is never sufficient",
        "revoke-one credential",
        "revoke-all sessions",
        "recovery-material rotation",
        "BACKUP != RESTORE",
        "BACKUP != CLONE_AUTHORIZATION",
        "RESTORE != MIGRATION",
        "CLONE_OR_FORK != SAME_ACTIVE_AETHER_IDENTITY",
        "AETHER_IDENTITY_CONTINUITY_REQUIRES_EXPLICIT_RESTORE_OR_MIGRATION_SEMANTICS",
        "GLOBAL SPLIT-BRAIN PREVENTION",
        "Isolated simultaneous restores may both run",
        "AetherInstanceTrust",
        "ClaimTokenRecord",
        "OwnerCredential",
        "OwnerSession",
        "RecoveryRecord",
        "AuthChallenge",
        "AuthenticatedSourceEvent",
        "OwnerSecurityAuditEvent",
    )


def test_m117a_locks_two_phase_claim_and_core_source_event_receipt():
    text = _text()
    formal = _formal(text)
    _assert_required(
        text,
        "Bootstrap Phase 1 creates one immutable instance identity",
        "Phase 1 creates no Owner\ncredential, no Owner session, and no `OWNED` state",
        "Bootstrap Phase 2 is completed through the OAS-owned browser listener",
        "atomically consumes the Claim\nToken and registration challenge",
        "Phase 2 cannot create the pending transaction or proceed without the Phase 1\ntransaction",
        "Core Coordination is the atomic owner for source-event receipt\nand the operation-specific result",
        "If either receipt or Goal transition fails, neither\ncommits",
        "OAS cannot commit Goal state, and Core cannot mint or sign a\nsource event",
        "Event issuance by OAS is not event consumption",
        "CLAIM_ENROLLMENT_MODEL_A_TWO_PHASE_PENDING_THEN_ATOMIC_COMPLETION",
        "SOURCE_EVENT_CONSUMPTION_MODEL_B_CORE_ATOMIC_RECEIPT_AND_BOUND_OPERATION_RESULT",
        "REQUIRED_IN_CORE_COORDINATION_OPERATION_RESULT_TRANSACTION",
    )
    _assert_required(
        formal,
        "SELECTED_CLAIM_ENROLLMENT_TRANSACTION_MODEL:\n"
        "CLAIM_ENROLLMENT_MODEL_A_TWO_PHASE_PENDING_THEN_ATOMIC_COMPLETION",
        "SELECTED_SOURCE_EVENT_CONSUMPTION_MODEL:\n"
        "SOURCE_EVENT_CONSUMPTION_MODEL_B_CORE_ATOMIC_RECEIPT_AND_BOUND_OPERATION_RESULT",
        "CROSS_BOUNDARY_ATOMIC_GOAL_RECEIPT:\n"
        "REQUIRED_IN_CORE_COORDINATION_OPERATION_RESULT_TRANSACTION",
    )
    assert "first credential only within one durable OAS transaction" not in text
    assert "source-event issue/consume" not in text


def test_m117a_locks_webauthn_registration_authentication_and_goal_operation_classes():
    text = _text()
    formal = _formal(text)
    _assert_required(
        text,
        "Phase 2 is a WebAuthn\nregistration ceremony, not an authentication assertion",
        "valid, unexpired, instance-bound, generation-bound `CLAIM_PENDING`",
        "OAS issues and owns a registration\nchallenge",
        "expected ceremony type\nis `webauthn.create`",
        "stored\nregistration challenge to match exactly",
        "origin to match\nexactly",
        "RP ID hash to match the configured instance-hostname policy",
        "unique credential ID",
        "valid public key and supported algorithm",
        "user-presence and user-verification policy",
        "Attestation is optional and is not used\nto claim physical-device identity",
        "WebAuthn authentication occurs only later",
        "expected type is\n`webauthn.get`",
        "Registration and authentication use separate OAS challenge records",
        "A registration\nchallenge cannot satisfy an authentication ceremony",
        "an authentication\nchallenge cannot register a credential",
        "AuthenticatedSourceEventReceipt",
        "OWNER: CORE_COORDINATION",
        "OAS must not own or mutate this receipt",
        "Unique event and\nnonce constraints prevent a second canonical operation",
        "CORE_SOURCE_EVENT_RECEIPT_COMMIT",
        "BOUND_CANONICAL_GOAL_MUTATION_COMMIT",
        "ONE_ATOMIC_CORE_COORDINATION_TRANSACTION",
        "GET_GOAL_STATUS",
        "BOUND_GOAL_STATUS_RESULT_SNAPSHOT_OR_DIGEST_COMMIT",
        "ONE_ATOMIC_CORE_COORDINATION_READ_RECEIPT_TRANSACTION",
        "This read receipt performs no Goal transition",
        "Failure before commit records neither the receipt nor the\nstatus result",
        "`GET_GOAL_STATUS` cannot create, revise, accept",
    )
    _assert_required(
        formal,
        "SELECTED_SOURCE_EVENT_CONSUMPTION_MODEL:\n"
        "SOURCE_EVENT_CONSUMPTION_MODEL_B_CORE_ATOMIC_RECEIPT_AND_BOUND_OPERATION_RESULT",
        "MUTATING_GOAL_OPERATIONS:\nPROPOSE_GOAL | ACCEPT_GOAL",
        "READ_ONLY_GOAL_OPERATION:\nGET_GOAL_STATUS",
        "AUTHENTICATED_SOURCE_EVENT_RECEIPT_OWNER:\nCORE_COORDINATION",
    )
    assert "first WebAuthn assertion" not in text
    assert "all records are OAS-owned" not in text.lower()
    assert "every record is owned and validated by OAS" not in text.lower()
    assert "OAS consumes AuthenticatedSourceEvent for Goal state" not in text
    assert "every source event requires a Goal transition" not in text.lower()
    assert "GET_GOAL_STATUS causes a Goal mutation" not in text


def test_m117a_hard_gate_matrix_is_complete_and_proven_by_design():
    text = _text()
    start = text.index("## 22. Complete Hard-Gate Matrix")
    end = text.index("## 23. Authorized Exit", start)
    matrix = text[start:end]
    assert "PARTIAL" not in matrix
    assert "NOT_PROVEN" not in matrix
    assert matrix.count("PROVEN_BY_DESIGN") == 22
    _assert_required(
        matrix,
        "truthful local privileged bootstrap presence",
        "truthful local privileged recovery presence",
        "direct backend bypass fails closed",
        "canonical security mutation plus audit commit atomic",
        "minimal data contract",
        "authenticated source event",
        "no Generic Act or generic identity registry",
    )


def test_m117a_rejects_old_boundary_and_unsupported_claims():
    text = _text()
    assert "AUTHORITY_BOUNDARY_C_AUTHENTICATED_OWNER_SOURCE_EVENT_TO_CORE_COORDINATION" not in text
    assert "ABSENT" not in text
    assert "UNRESOLVED" not in text
    assert "TR2_PROVEN:\nNO" not in text
    assert "TR2_PROVEN:\nINSUFFICIENT_EVIDENCE" not in text
    assert "BUILD_READINESS:\nBUILD_NOT_JUSTIFIED" not in text
    assert "PRODUCTION_IMPLEMENTATION_PERFORMED:\nYES" not in text
    assert "M117B_AUTHORIZED:\nYES" not in text
    assert "M118_AUTHORIZED:\nYES" not in text


def test_m117a_static_lock_is_documentation_only():
    source = Path(__file__).read_text(encoding="utf-8")
    forbidden = (
        "import " + "aether",
        "Test" + "Client",
        "uvi" + "corn",
        "sub" + "process",
        "sock" + "et",
    )
    for marker in forbidden:
        assert marker not in source
    assert not re.search(r"from\s+aether|import\s+aether", source)
