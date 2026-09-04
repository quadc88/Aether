"""Documentation and finalization lock for the canonical security architecture."""

from hashlib import sha256
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
SECURITY = ROOT / "docs/architecture/SECURITY_ARCHITECTURE.md"
ARCHITECTURE = ROOT / "docs/ARCHITECTURE.md"
M117A = ROOT / (
    "docs/architecture/"
    "MILESTONE_117A_SINGLE_OWNER_LAN_TRUST_ROOT_CONTRACT_PROOF.md"
)
M117A_LOCK = ROOT / "tests/test_milestone_117a_single_owner_lan_trust_root_contract_proof.py"
M119A = ROOT / (
    "docs/architecture/"
    "MILESTONE_119A_OAS_SEPARATE_PRINCIPAL_RUNTIME_AND_PRIVILEGED_IPC_BOUNDARY_PROOF.md"
)
M119A_LOCK = ROOT / (
    "tests/test_milestone_119a_oas_separate_principal_runtime_and_privileged_ipc_boundary_proof.py"
)
M120A_PROTOCOL = ROOT / "aether/oas/ipc_protocol.py"
M120A_ACTIVATION = ROOT / "aether/oas/socket_activation.py"
M120A_SERVICE = ROOT / "aether/oas/service.py"
M120A_LOCK = ROOT / (
    "tests/test_m120a_oas_socket_activated_service_bounded_ipc_foundation.py"
)
M121A = ROOT / (
    "docs/architecture/"
    "MILESTONE_121A_OAS_REPOSITORY_TO_HOST_DEPLOYMENT_AND_ROLLBACK_CONTRACT_PROOF.md"
)
M121A_LOCK = ROOT / (
    "tests/test_milestone_121a_oas_repository_to_host_deployment_and_rollback_contract_proof.py"
)
README = ROOT / "README.md"
CONSTITUTION = ROOT / "docs/CONSTITUTION.md"
OAS_INIT = ROOT / "aether/oas/__init__.py"
M118A_KERNEL = ROOT / "aether/oas/security_kernel.py"
M118A_LOCK = ROOT / "tests/test_m118a_security_kernel.py"
PROGRESS = ROOT / "PROGRESS.md"
M126A = ROOT / (
    "docs/architecture/"
    "MILESTONE_126A_OAS_PRODUCTION_TRUST_MATERIAL_AND_HOST_TRUST_BOOTSTRAP_AUTHORITY_CONTRACT_PROOF.md"
)
M126A_LOCK = ROOT / (
    "tests/test_milestone_126a_oas_production_trust_material_and_host_trust_bootstrap_authority_contract_proof.py"
)
M127A = ROOT / (
    "docs/architecture/"
    "MILESTONE_127A_OAS_ISOLATED_HOST_TRUST_BOOTSTRAP_AUTHORIZATION_AND_DURABLE_PUBLICATION_TRANSACTION_FOUNDATION_BUILD.md"
)
M127A_LOCK = ROOT / (
    "tests/test_milestone_127a_oas_isolated_host_trust_bootstrap_authorization_and_durable_publication_transaction_foundation_build.py"
)
M128A = ROOT / (
    "docs/architecture/"
    "MILESTONE_128A_PRIVILEGED_HOST_TRUST_BOOTSTRAP_RUNNER_PROCESS_RECOVERY_AND_EXACT_ROOT_AUTHORITY_CONTRACT_PROOF.md"
)
M128A_LOCK = ROOT / (
    "tests/"
    "test_milestone_128a_privileged_host_trust_bootstrap_runner_process_recovery_and_exact_root_authority_contract_proof.py"
)

APPROVED_M117A_HASH = "a56d3d433cd787f7ee902c0861953b604fd20861d3e9adabcd5adcaefee9673b"
APPROVED_M117A_LOCK_HASH = "b6c150821b9d996fe2f6982c2062b937d3c5bcc9381a152598d0446c88e19d85"
APPROVED_M119A_HASH = "2f6d36d503a41aec1513605cfc26bd77755aa0d0fd821683b2a783513193646b"
APPROVED_M119A_LOCK_HASH = "780dd0da75733f8443abe4817f90d95526dbddc477c1e420bd843357b0a17e50"
APPROVED_M120A_PROTOCOL_HASH = "81f1d99304831270179ca809e45b58cb96fb5b28b771f6ed00f2dbcc7843e923"
APPROVED_M120A_ACTIVATION_HASH = "dbbe229118bfa2b54f32ad24537acc62ca57843fa0fb6230ba23a9cd57985709"
APPROVED_M120A_SERVICE_HASH = "da654853f2a0177d5d219afd8ff2279b05b598d07beeb143286f85ad052bb771"
APPROVED_M120A_LOCK_HASH = "a98e0947ca7466d485e53c14e8560bbee6876277fcc9c27911bee1e225e6c6a9"
APPROVED_M121A_HASH = "0c3f81f9f8486f912ba28546fd6e23457a88ef4e75f2d9c66628e24f05ff48eb"
ORIGINAL_M121A_LOCK_HASH = "6f670e78a3eec5c4ac386822f120c0a24ac557ba09ae946d9d33614dabd39d5c"
APPROVED_M121A_LOCK_HASH = "32fe0862b6ac8dad5b243772630d4d33ffb30258702b7b8ed0df522ea08dd087"
APPROVED_M126A_HASH = "96cba30eb249dde365ecd1a3fa81d1fa631e5ec71d886dff4f4c90aff678d16a"
APPROVED_M126A_LOCK_HASH = "0251de280e32e3063810e655f56fac62637f9bf3c89b5e93dc23a40ce968ef47"
APPROVED_M127A_IMPLEMENTATION_HASH = "e5a0092e6c7af0edf298ca2d126d9e1a924e46a943a162521354574dd405b168"
APPROVED_M127A_BEHAVIORAL_HASH = "970096e76a63c322cbe4fb4309cbdc504d1ab1c35b890d46cfe86f28b18260f3"
APPROVED_M127A_DOCUMENT_HASH = "401e12e097ed5aa9b87617fa74e1d2c705523f3a1f6047f1cbc73353425ef3de"
APPROVED_M127A_LOCK_HASH = "b7ca3c13c52dad5b3dfe320ec5273a9b2cf3134cc1213d544cc1f6050c79634f"
BASELINE_PROTECTED_HASHES = {
    README: "5357e53635c7467332129048155b39ac9282d6aff268f5f910594a5b26d72cad",
    CONSTITUTION: "0055748f683bf753b3471a0317b68677752c312d4030b12fbc71684fd3af3ee1",
    ARCHITECTURE: "49d98d7530bfc88a9070aa620115af99fd0414f36de67910719f496844347065",
    M117A: "a56d3d433cd787f7ee902c0861953b604fd20861d3e9adabcd5adcaefee9673b",
    M117A_LOCK: "b6c150821b9d996fe2f6982c2062b937d3c5bcc9381a152598d0446c88e19d85",
    OAS_INIT: "a4cb03845a5676f48f5328392ccbf2637fd98052be84b9e5213448e91947dd54",
    M118A_KERNEL: "ef02d191d11ad6acf7f93710bc02deea284f336237310822655f6988451d8589",
    M118A_LOCK: "89ccd391f0270df07b7173307ab25d31ab7787448cd001ddeef2d0732c5e7117",
}

PRECEDENCE = """CONSTITUTION
    >
ARCHITECTURE
    >
SECURITY_ARCHITECTURE
    >
CURRENT IMPLEMENTATION"""

STATUS_VALUES = {
    "DECISION_STATUS": "PROPOSED | CURRENT | SUPERSEDED | REJECTED",
    "DESIGN_STATUS": "UNDEFINED | PARTIAL | DESIGN_PROVEN",
    "IMPLEMENTATION_STATUS": "NOT_IMPLEMENTED | PARTIALLY_IMPLEMENTED | IMPLEMENTED",
    "VERIFICATION_STATUS": "NOT_VERIFIED | TEST_VERIFIED | DEPLOYMENT_VERIFIED",
}

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


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _normalized(text: str) -> str:
    return " ".join(text.split())


def _sha256(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def _assert_required(text: str, *markers: str) -> None:
    for marker in markers:
        assert marker in text, marker


def _section(text: str, heading: str, next_heading: str) -> str:
    start = text.index(heading)
    end = text.index(next_heading, start)
    return text[start:end]


def _authoritative_m122a_status(text: str) -> str:
    start = text.index("M122A is a separately authorized repository-only deployment artifact Build")
    fence_start = text.index("```text\n", start) + len("```text\n")
    fence_end = text.index("\n```", fence_start)
    return text[fence_start:fence_end]


def test_security_architecture_exists_and_has_required_structure():
    assert SECURITY.is_file()
    text = _text(SECURITY)
    required = (
        "# Aether Security Architecture",
        "## 1. Purpose, Authority, and Scope",
        "## 2. Authority Precedence and Conflict Resolution",
        "## 3. Orthogonal Security Status Dimensions",
        "## 4. Current Deployment and Trust Assumptions",
        "## 5. Security and Authority Taxonomy",
        "## 6. Architectural Trust Boundaries",
        "## 7. Owner Trust-Root Lifecycle",
        "## 8. Authentication Channel Architecture",
        "## 9. Canonical Security State and Audit",
        "## 10. Authenticated Source Evidence Boundary",
        "## 11. Recovery, Revocation, and Higher Assurance",
        "## 12. Backup, Restore, Migration, Clone, and Split-Brain",
        "## 13. Relationship to the Aether Execution Chain",
        "## 14. Current Security Status Matrix",
        "## 15. Current Implemented Security Surface",
        "## 16. Future and Unproven Security Frontiers",
        "## 17. Security Architecture Evolution Rules",
        "## 18. Milestone and Evidence Traceability",
    )
    _assert_required(text, *required)
    assert "Document role: CANONICAL LIVING SECURITY-DOMAIN ARCHITECTURE\n" in text
    assert "PHASE 1 DOCUMENTATION PASS" not in text


def test_authority_precedence_and_historical_boundary_are_exact():
    text = _text(SECURITY)
    precedence = _section(
        text,
        "## 2. Authority Precedence and Conflict Resolution",
        "## 3. Orthogonal Security Status Dimensions",
    )
    _assert_required(precedence, PRECEDENCE)
    normalized = _normalized(precedence)
    _assert_required(
        normalized,
        "The Constitution is the highest technology-independent authority.",
        "canonical for the security domain but remains subordinate",
        "Current implementation must conform to all higher authorities",
        "IMMUTABLE HISTORICAL EVIDENCE + DECISION PROVENANCE + TRACEABILITY RECORDS",
        "PROGRESS.md` is a project-status ledger, not an architecture authority source.",
    )
    assert "MILESTONE > SECURITY_ARCHITECTURE" not in text


def test_status_dimensions_are_orthogonal_and_bounded():
    text = _text(SECURITY)
    dimensions = _section(
        text,
        "## 3. Orthogonal Security Status Dimensions",
        "## 4. Current Deployment and Trust Assumptions",
    )
    for dimension, values in STATUS_VALUES.items():
        assert f"{dimension}:\n{values}" in dimensions
    normalized = _normalized(dimensions)
    _assert_required(
        normalized,
        "CURRENT does not imply DESIGN_STATUS: DESIGN_PROVEN",
        "DESIGN_STATUS: DESIGN_PROVEN does not imply IMPLEMENTATION_STATUS: IMPLEMENTED",
        "IMPLEMENTATION_STATUS: IMPLEMENTED does not imply VERIFICATION_STATUS: TEST_VERIFIED",
        "VERIFICATION_STATUS: TEST_VERIFIED does not imply VERIFICATION_STATUS: DEPLOYMENT_VERIFIED",
        "MILESTONE_FINALIZED does not imply LIVE_SECURITY_PROVEN",
        "`TEST_VERIFIED` means only that explicitly identified tests passed",
        "It is not runtime security proof or deployment security proof.",
        "host, OS, configuration, network boundary, permission boundary, evidence time",
        "No single combined maturity or security-status field replaces these dimensions.",
    )
    assert "RUNTIME_VERIFICATION_STATUS" not in text


def test_m117a_target_statuses_remain_design_only():
    text = _text(SECURITY)
    matrix = _section(
        text,
        "## 14. Current Security Status Matrix",
        "## 15. Current Implemented Security Surface",
    )
    rows = [line for line in matrix.splitlines() if line.startswith("| ")]
    assert len(rows) >= 17
    target_rows = [line for line in rows if "| CURRENT | DESIGN_PROVEN | NOT_IMPLEMENTED | NOT_VERIFIED |" in line]
    assert len(target_rows) >= 13
    _assert_required(
        matrix,
        "one Owner per Aether Instance",
        "hybrid bootstrap plus authenticated channel",
        "WebAuthn registration/authentication separation",
        "OAS AuthenticatedSourceEvent issuance",
        "Core receipt and Goal operation transactions",
        "absolute global split-brain prevention",
        "| CURRENT | PARTIAL | NOT_IMPLEMENTED | NOT_VERIFIED |",
    )


def test_m118a_status_rows_and_boundary_claims_are_distinct():
    text = _text(SECURITY)
    matrix = _section(
        text,
        "## 14. Current Security Status Matrix",
        "## 15. Current Implemented Security Surface",
    )

    def row_for(capability: str) -> list[str]:
        row = next(
            line for line in matrix.splitlines()
            if line.startswith(f"| {capability} |")
        )
        return [part.strip() for part in row.split("|")[1:-1]]

    full_target = row_for("canonical security state plus audit atomicity")
    bounded_kernel = row_for(
        "bounded canonical OAS security-kernel state plus audit atomicity"
    )
    code_boundary = row_for("ordinary-runtime direct OAS mutation boundary")
    assert full_target[3:5] == ["NOT_IMPLEMENTED", "NOT_VERIFIED"]
    assert bounded_kernel[3:5] == ["IMPLEMENTED", "TEST_VERIFIED"]
    assert code_boundary[2:5] == ["PARTIAL", "IMPLEMENTED", "TEST_VERIFIED"]
    assert "DEPLOYMENT_VERIFIED" not in matrix

    implementation = _section(
        text,
        "## 15. Current Implemented Security Surface",
        "## 16. Future and Unproven Security Frontiers",
    )
    _assert_required(
        _normalized(implementation),
        "repository-wide AST lock",
        "empty public package surface",
        "explicit store path",
        "static code/dependency boundary only",
        "not OS, process, deployment, credential, or malicious same-process isolation",
        "complete transaction request",
        "complete versioned non-secret audit-evidence digest",
        "exactly one consistent audit event",
        "fixed depth",
        "encoded-size",
        "collection",
        "key",
        "string",
        "integer limits",
    )

    traceability = text[text.index("## 18. Milestone and Evidence Traceability"):]
    status_block = traceability[traceability.index("M118A - Owner Authority Service"):]
    assert "M118A_AUTHORIZED: YES" in status_block
    assert "M118A_STARTED: YES" in status_block
    assert "M118A_FINALIZED: YES" in status_block


def test_m119a_integration_preserves_unimplemented_boundary_and_final_traceability():
    text = _text(SECURITY)
    normalized = _normalized(text)
    _assert_required(
        normalized,
        "M119A is the current, PM-accepted design decision",
        "selected overall model is Model D",
        "root-owned, systemd-activated AF_UNIX owner broker",
        "`aether-owner`, `aether-runtime`, `aether-oas`, `aether-bootstrap`, and `root`",
        "SO_PEERCRED",
        "fresh PAM authentication",
        "one-use confirmation nonce",
        "instance/generation-bound authorization context",
        "Systemd owns and activates the runtime, bootstrap, broker, and owner-broker sockets",
        "bounded allowlisted operations",
        "M119A remains design proof only",
        "IMPLEMENTATION_STATUS: NOT_IMPLEMENTED",
        "VERIFICATION_STATUS: TEST_VERIFIED",
        "DEPLOYMENT_VERIFIED: NO",
        "A future Build remains separately authorized only for PM review",
    )
    traceability = text[
        text.index("The M119A evidence reference is:"):
        text.index("The M118A implementation boundary is:")
    ]
    _assert_required(
        traceability,
        "MILESTONE_119A_OAS_SEPARATE_PRINCIPAL_RUNTIME_AND_PRIVILEGED_IPC_BOUNDARY_PROOF.md",
        APPROVED_M119A_HASH,
        "test_milestone_119a_oas_separate_principal_runtime_and_privileged_ipc_boundary_proof.py",
        APPROVED_M119A_LOCK_HASH,
        "Selected exit: EXIT_A",
        "M119A_FINALIZED: YES",
        "DECISION_STATUS: CURRENT",
        "PM_ACCEPTED: YES",
        "BUILD_AUTHORIZED: NO",
        "SUCCESSOR_NUMBER_ASSIGNED: NO",
    )
    assert "M119A_FINALIZED: NO" not in traceability
    assert "IMPLEMENTATION_STATUS: IMPLEMENTED" not in traceability


def test_m119a_finalized_artifact_hashes_and_protected_evidence_are_stable():
    assert _sha256(M119A) == APPROVED_M119A_HASH
    assert _sha256(M119A_LOCK) == APPROVED_M119A_LOCK_HASH


def test_m120a_status_rows_and_scope_are_bounded():
    text = _text(SECURITY)
    matrix = _section(
        text,
        "## 14. Current Security Status Matrix",
        "## 15. Current Implemented Security Surface",
    )

    def row_for(capability: str) -> list[str]:
        row = next(
            line for line in matrix.splitlines()
            if line.startswith(f"| {capability} |")
        )
        return [part.strip() for part in row.split("|")[1:-1]]

    for capability in (
        "bounded canonical OAS IPC framing",
        "exact systemd socket-activation descriptor intake",
        "bounded OAS runtime service foundation",
        "bootstrap and broker fail-closed operation boundary",
    ):
        statuses = row_for(capability)
        assert statuses[1:5] == [
            "CURRENT",
            "DESIGN_PROVEN",
            "IMPLEMENTED",
            "TEST_VERIFIED",
        ]
        assert "DEPLOYMENT_VERIFIED" not in statuses

    implementation = _normalized(
        _section(
            text,
            "## 15. Current Implemented Security Surface",
            "## 16. Future and Unproven Security Frontiers",
        )
    )
    _assert_required(
        implementation,
        "fails closed when Linux `/proc/net/unix` identity evidence is unavailable, malformed, oversized, or non-matching",
        "portable pathname checks are not treated as equivalent Linux kernel proof",
        "32-active/64-queued request admission",
        "Shutdown cancels queued work",
        "executor's non-waiting cancellation API",
        "A worker that cannot be interrupted remains explicitly outstanding",
        "Known receive and response I/O use the remaining budget",
        "typed deadline failures are classified without exception-string matching",
        "never reports a successful status after expiry",
        "slow underlying read may remain an outstanding worker beyond a bounded shutdown call",
    )

    traceability = _normalized(
        text[text.index("The M120A implementation boundary is:"):]
    )
    _assert_required(
        traceability,
        "M120A_AUTHORIZED: YES",
        "M120A_STARTED: YES",
        "M120A_FINALIZED: YES",
        "IMPLEMENTATION_STATUS: IMPLEMENTED",
        "VERIFICATION_STATUS: TEST_VERIFIED",
        "DEPLOYMENT_VERIFIED: NO",
        "M120A is limited to bounded IPC/service mechanics",
        "Owner authentication",
        "live systemd or OS principal deployment",
        "Core receipt integration",
        "generalized Tool-Operation-Capability authority",
    )


def test_m120a_artifact_hashes_are_stable():
    assert _sha256(M120A_PROTOCOL) == APPROVED_M120A_PROTOCOL_HASH
    assert _sha256(M120A_ACTIVATION) == APPROVED_M120A_ACTIVATION_HASH
    assert _sha256(M120A_SERVICE) == APPROVED_M120A_SERVICE_HASH
    assert _sha256(M120A_LOCK) == APPROVED_M120A_LOCK_HASH


def test_m121a_contract_is_canonized_without_promoting_implementation_or_deployment():
    text = _text(SECURITY)
    normalized = _normalized(text)
    matrix = _section(
        text,
        "## 14. Current Security Status Matrix",
        "## 15. Current Implemented Security Surface",
    )
    row = next(
        line for line in matrix.splitlines()
        if line.startswith("| repository-to-host activation and rollback contract |")
    )
    assert [part.strip() for part in row.split("|")[1:-1]][1:5] == [
        "CURRENT",
        "DESIGN_PROVEN",
        "NOT_IMPLEMENTED",
        "TEST_VERIFIED",
    ]
    _assert_required(
        normalized,
        "M121A canonizes a repository-to-host deployment and rollback contract as design and discovery evidence only.",
        "one root-owned authoritative activation record",
        "versioned and signed release identity",
        "pre-replacement quiescence",
        "generation-specific gates",
        "bounded monotonic activation deadlines",
        "fail-closed readiness and smoke checks",
        "No M121A production entrypoint, manifest, verifier, unit bundle, installer, lifecycle tool, host artifact, or deployment has been implemented or verified.",
        "`EXIT_A` does not authorize implementation, host mutation, readiness, or deployment verification.",
    )
    traceability = text[text.index("The M121A evidence reference is:") :]
    _assert_required(
        traceability,
        "MILESTONE_121A_OAS_REPOSITORY_TO_HOST_DEPLOYMENT_AND_ROLLBACK_CONTRACT_PROOF.md",
        APPROVED_M121A_HASH,
        "test_milestone_121a_oas_repository_to_host_deployment_and_rollback_contract_proof.py",
        APPROVED_M121A_LOCK_HASH,
        "PM disposition: APPROVE_M121A_FINALIZATION",
        "M121A_AUTHORIZED: YES",
        "M121A_STARTED: YES",
        "M121A_FINALIZED: YES",
        "SELECTED_EXIT: EXIT_A",
        "IMPLEMENTATION_STATUS: NOT_IMPLEMENTED",
        "VERIFICATION_STATUS: TEST_VERIFIED",
        "DEPLOYMENT_VERIFIED: NO",
        "BUILD_AUTHORIZED: NO",
        "PM_ACCEPTED: YES",
        "SUCCESSOR_AUTHORIZED: NO",
    )


def test_m121a_artifacts_are_byte_stable():
    assert _sha256(M121A) == APPROVED_M121A_HASH
    assert _sha256(M121A_LOCK) == APPROVED_M121A_LOCK_HASH


def test_m126a_finalized_contract_is_canonized_without_promoting_implementation_or_deployment():
    text = _text(SECURITY)
    matrix = _section(
        text,
        "## 14. Current Security Status Matrix",
        "## 15. Current Implemented Security Surface",
    )
    row = next(
        line for line in matrix.splitlines()
        if line.startswith("| production trust material and host trust-bootstrap authority contract |")
    )
    assert [part.strip() for part in row.split("|")[1:-1]][1:5] == [
        "CURRENT",
        "DESIGN_PROVEN",
        "NOT_IMPLEMENTED",
        "TEST_VERIFIED",
    ]
    traceability = text[text.index("The M126A evidence reference is:"):]
    _assert_required(
        traceability,
        "MILESTONE_126A_OAS_PRODUCTION_TRUST_MATERIAL_AND_HOST_TRUST_BOOTSTRAP_AUTHORITY_CONTRACT_PROOF.md",
        "tests/test_milestone_126a_oas_production_trust_material_and_host_trust_bootstrap_authority_contract_proof.py",
        "M126A_AUTHORIZED: YES",
        "M126A_STARTED: YES",
        "M126A_FINALIZED: YES",
        "DECISION_STATUS: CURRENT",
        "DESIGN_STATUS: DESIGN_PROVEN",
        "IMPLEMENTATION_STATUS: NOT_IMPLEMENTED",
        "VERIFICATION_STATUS: TEST_VERIFIED",
        "DEPLOYMENT_VERIFIED: NO",
        "PRODUCTION_TRUST_MATERIAL_PROVEN: NO",
        "HOST_TRUST_OBJECTS_INSTALLED: NO",
        "TRUST_BOOTSTRAP_IMPLEMENTED: NO",
        "BUILD_AUTHORIZED: NO",
        "SUCCESSOR_AUTHORIZED: NO",
        "PROGRESS_UPDATED: YES",
        "COMMIT_CREATED: YES",
        "TAG_CREATED: YES",
        "PUSH_PERFORMED: YES",
    )
    assert "M126A_FINALIZED: NO" not in traceability
    assert _normalized(M126A.read_text(encoding="utf-8")).find("M126A_FINALIZED: YES") >= 0
    assert _sha256(M126A) == APPROVED_M126A_HASH
    assert _sha256(M126A_LOCK) == APPROVED_M126A_LOCK_HASH


def test_m127a_finalized_implementation_is_canonized_without_promoting_deployment():
    text = _text(SECURITY)
    matrix = _section(
        text,
        "## 14. Current Security Status Matrix",
        "## 15. Current Implemented Security Surface",
    )
    row = next(
        line for line in matrix.splitlines()
        if line.startswith("| isolated host trust-bootstrap authorization and durable publication transaction foundation |")
    )
    assert [part.strip() for part in row.split("|")[1:-1]][1:5] == [
        "CURRENT",
        "DESIGN_PROVEN",
        "IMPLEMENTED",
        "TEST_VERIFIED",
    ]
    traceability = text[text.index("The M127A implementation and finalization evidence reference is:"):]
    _assert_required(
        traceability,
        "MILESTONE_127A_OAS_ISOLATED_HOST_TRUST_BOOTSTRAP_AUTHORIZATION_AND_DURABLE_PUBLICATION_TRANSACTION_FOUNDATION_BUILD.md",
        APPROVED_M127A_DOCUMENT_HASH,
        "aether/deployment/host_trust_bootstrap.py",
        APPROVED_M127A_IMPLEMENTATION_HASH,
        "tests/test_deployment_host_trust_bootstrap.py",
        APPROVED_M127A_BEHAVIORAL_HASH,
        "tests/test_milestone_127a_oas_isolated_host_trust_bootstrap_authorization_and_durable_publication_transaction_foundation_build.py",
        APPROVED_M127A_LOCK_HASH,
        "VALID_AUTHORIZATION_CONCURRENCY_PROVEN: YES_TEST_ONLY",
        "GENERATION_RESERVATION_SEMANTICS_PROVEN: YES_TEST_ONLY",
        "TEST_ONLY_EPHEMERAL_KEYS_USED: YES",
        "TEST_PRIVATE_KEYS_PERSISTED: NO",
        "PRODUCTION_SIGNING_CAPABILITY_IMPLEMENTED: NO",
        "PRODUCTION_TRUST_MATERIAL_PROVEN: NO",
        "DEPLOYMENT_VERIFIED: NO",
        "TARGET_HOST_MUTATION_PERFORMED: NO",
        "GENERIC_ACT_AUTHORIZED: NO",
        "SUCCESSOR_AUTHORIZED: NO",
        "SUCCESSOR_NUMBER_ASSIGNED: NO",
        "M127A_FINALIZED: YES",
        "READY_FOR_PM_REVIEW: NO",
    )
    _assert_required(
        _normalized(text),
        "context-bound authenticated authorization verification",
        "SQLite WAL/FULL state",
        "RESERVED/ACTIVE/BURNED",
        "terminal Observation and Verification",
        "prior-generation restoration",
        "fail-closed retry, concurrency, and corruption handling",
        "M127A remains isolated-root-only",
        "truthful Owner deployment authority",
        "cross-directory filesystem atomicity",
        "no Generic Act authority",
    )
    assert "M127A_FINALIZED: NO" not in traceability
    assert _sha256(M127A) == APPROVED_M127A_DOCUMENT_HASH
    assert _sha256(M127A_LOCK) == APPROVED_M127A_LOCK_HASH
    assert _sha256(ROOT / "aether/deployment/host_trust_bootstrap.py") == APPROVED_M127A_IMPLEMENTATION_HASH
    assert _sha256(ROOT / "tests/test_deployment_host_trust_bootstrap.py") == APPROVED_M127A_BEHAVIORAL_HASH


def test_m128a_finalized_contract_is_canonized_without_live_security_claims():
    text = _text(SECURITY)
    section = text[
        text.index("### M128A Finalized Privileged Host Trust-Bootstrap Contract"):
        text.index("The post-finalization correction state is explicit:")
    ]
    _assert_required(
        _normalized(section),
        "M128A is finalized design/discovery/security/operations evidence only",
        "privileged runner is an OS/deployment organ, not Aether, OAS, Owner, or an intent interpreter",
        "admitter is transport only and cannot mint bootstrap authorization",
        "M126A evidence remains the cryptographic authority",
        "root possession is not authorization",
        "complete sealed raw evidence and exact bytes for the five fixed objects",
        "`authorization_detached_signature` must exactly equal the signature encoded in `authorization_envelope_raw`",
        "MOUNT_NAMESPACE_POLICY: PID1_INITIAL_HOST_MOUNT_NAMESPACE_REQUIRED",
        "SYSTEMD_PRIVATE_NETWORK_NAMESPACE: NOT_SELECTED",
        "SYSTEMD_PRIVATE_MOUNT_NAMESPACE: FORBIDDEN",
        "pre-opened-dirfd plus irreversible Landlock model",
        "Landlock ABI 3 or newer",
        "irreversible TSYNC seccomp",
        "SQLite is the sole canonical durable transaction and audit authority",
        "Terminal success requires both Observation and Verification",
        "current probe host does not support Landlock",
        "not deployment-ready",
        "No Build, deployment, host mutation, or successor is authorized",
        "M128A Git closure is a two-commit transaction",
        "INITIAL_FINALIZATION_COMMIT: 02d47587826c8abc9db30b2031419b133573c34c",
        "FINALIZATION_RECOVERY_COMMIT: THIS_COMMIT",
        "INITIAL_FINALIZATION_SCOPE: FIVE_PATHS",
        "FINALIZATION_RECOVERY_SCOPE: SIX_PATHS",
        "The final tag targets the recovery commit",
        "historical M124A finalization commit is `3aaff2a8ec188650ecb4e132a74d6ef92d3245a6`",
        "test governance only, not implementation or scope expansion",
        "M128A_FINALIZED: YES",
        "DECISION_STATUS: CURRENT",
        "DESIGN_STATUS: DESIGN_PROVEN",
        "IMPLEMENTATION_STATUS: NOT_IMPLEMENTED",
        "VERIFICATION_STATUS: TEST_VERIFIED",
        "DEPLOYMENT_VERIFIED: NO",
        "CURRENT_PROBE_HOST_LANDLOCK_STATUS: UNSUPPORTED_EOPNOTSUPP",
        "CURRENT_PROBE_HOST_SUCCESS_PATH_RUNNABLE: NO",
        "CURRENT_HOST_DEPLOYMENT_READY: NO",
        "BUILD_AUTHORIZED: NO",
        "SUCCESSOR_AUTHORIZED: NO",
        "SUCCESSOR_NUMBER_ASSIGNED: NO",
    )
    assert M128A.is_file()
    assert M128A_LOCK.is_file()
    for forbidden in (
        "LIVE_RUNNER_IMPLEMENTED: YES",
        "LIVE_ADMITTER_IMPLEMENTED: YES",
        "DEPLOYMENT_VERIFIED: YES",
        "CURRENT_HOST_DEPLOYMENT_READY: YES",
        "BUILD_AUTHORIZED: YES",
        "GENERIC_ACT_AUTHORIZED: YES",
        "SUCCESSOR_AUTHORIZED: YES",
        "M128A_IMPLEMENTED: YES",
        "M128A_DEPLOYED: YES",
        "completion without Observation and Verification",
        "Tool-Operation-Capability expansion",
        "multi-instance runtime",
        "multi-agent runtime",
        "public Internet",
    ):
        assert forbidden not in section


def test_m122a_successor_artifact_boundary_is_distinct_and_non_deployed():
    text = _text(SECURITY)
    status = _authoritative_m122a_status(text)
    for field, value in M122A_STATUS.items():
        matches = re.findall(rf"^{re.escape(field)}: .*$", status, re.MULTILINE)
        assert matches == [f"{field}: {value}"]
    _assert_required(
        text,
        "M122A is a separately authorized repository-only deployment artifact Build",
        "M122A_AUTHORIZED: YES",
        "M122A_FINALIZED: YES",
        "IMPLEMENTATION_STATUS: IMPLEMENTED",
        "VERIFICATION_STATUS: TEST_VERIFIED",
        "SELECTED_EXIT: EXIT_A",
        "DEPLOYMENT_VERIFIED: NO",
        "HOST_MUTATION_PERFORMED: NO",
        "SUCCESSOR_AUTHORIZED: NO",
        ORIGINAL_M121A_LOCK_HASH,
        APPROVED_M121A_LOCK_HASH,
        "MILESTONE_122A_OAS_REPOSITORY_DEPLOYMENT_ARTIFACT_FOUNDATION_BUILD.md",
        "76901b6fb619776e0fbc53c5a30995faa5bcf070",
        "milestone-122A-oas-repository-deployment-artifact-foundation",
        "metadata consistency only",
        "no implementation or deployment state",
    )


def test_current_implementation_truth_is_not_promoted():
    text = _text(SECURITY)
    normalized_text = _normalized(text)
    implementation = _section(
        text,
        "## 15. Current Implemented Security Surface",
        "## 16. Future and Unproven Security Frontiers",
    )
    _assert_required(
        normalized_text,
        "no authenticated Owner source",
        "no authenticated or deployment-verified OAS boundary",
        "no WebAuthn",
        "no live TLS Owner channel",
        "no deployed OS-principal boundary",
        "no live recovery ceremony",
        "no AuthenticatedSourceEvent issuance",
        "no Core receipt integration",
        "HA1 remains incomplete",
        "GI2 remains incomplete",
        "no Generic Act authority",
        "no generalized Tool-Operation-Capability security architecture",
        "no unrestricted Action authority",
        "existing bounded governance, policy, approval, restricted-read, and action-control mechanisms",
        "no public Internet",
        "no multi-instance runtime",
        "no multi-agent runtime expansion",
        "not OS, process, deployment, credential, or malicious same-process isolation",
    )
    _assert_required(
        _normalized(implementation),
        "127.0.0.1:8000",
        "identity-seed SHA-256 integrity state",
        "tool execution disabled",
        "pending review structures",
        "do not establish a truthful human source",
    )


def test_targeted_correction_preserves_evidence_precedence_and_tool_boundary():
    text = _text(SECURITY)
    normalized = _normalized(text)
    traceability = _normalized(
        text[text.index("## 18. Milestone and Evidence Traceability"):]
    )
    _assert_required(
        normalized,
        "M117A is frozen design evidence and decision provenance supporting the current bounded single-owner LAN trust-root direction.",
        "M117A is not another layer in the current authority precedence chain.",
        "Current normative authority comes from the Constitution, Architecture, and the subordinate canonical Security Architecture.",
        "M117A remains immutable historical evidence and traceability.",
        "A later authorized decision may supersede a current security design without rewriting M117A.",
        "No generalized Tool-Operation-Capability security architecture is currently established.",
        "No Generic Act authority exists.",
        "Existing bounded policy, approval, restricted-read, and action-control mechanisms remain current implementation facts.",
        "Those bounded mechanisms are not the future Tool Security frontier.",
        "The future Tool-Operation-Capability frontier remains separate and unproven.",
        "Owner authentication does not grant authority to tools, operations, capabilities, or Generic Act.",
        "bounded governance, policy, approval, restricted-read, and action controls",
        "not Owner authentication or generalized Tool authority",
    )
    _assert_required(
        traceability,
        "M118A_AUTHORIZED: YES",
        "M118A_STARTED: YES",
        "M118A_FINALIZED: YES",
        "generalized Tool-Operation-Capability authority",
    )
    assert "PHASE 1 DOCUMENTATION PASS" not in text
    assert "frozen design authority" not in text
    assert "no Tool / Operation / Capability authority" not in text
    assert "no Tool / Operation / Capability controls" not in text
    assert "M117A is the frozen design authority" not in text


def test_m118a_boundary_is_explicit_and_finalized():
    text = _text(SECURITY)
    traceability = text[text.index("## 18. Milestone and Evidence Traceability"):]
    _assert_required(
        traceability,
        "M118A - Owner Authority Service Durable Security Kernel Foundation Build",
        "M118A_AUTHORIZED: YES",
        "M118A_STARTED: YES",
        "M118A_FINALIZED: YES",
        "M118A in scope:",
        "M118A out of scope:",
        "canonical durable OAS security-state foundation",
        "OwnerSecurityAuditEvent",
        "AuthenticatedSourceEventReceipt",
        "WebAuthn;",
        "real signing keys;",
        "Core Coordination or Goal Intake integration;",
        "Generic Act;",
        "public Internet;",
        "multi-instance runtime;",
        "multi-agent runtime.",
        "preceding canonization gate did not start M118A",
    )


def test_m118a_post_finalization_correction_state_is_distinct():
    text = _text(SECURITY)
    normalized = _normalized(text)
    _assert_required(
        text,
        "The original finalized M118A commit and annotated tag remain immutable historical",
        "M118A_FINAL_COMMIT: a5188ae7e3aa1454bac1c21e5c5081e441687397",
        "M118A_FINAL_TAG: milestone-118A-oas-durable-security-kernel-foundation",
        "M118A_FINAL_TAG_OBJECT: 297a3620664eb025f8aeb1516fd435a94a85bea7",
        "M118A_FINAL_TAG_PEELED_TARGET: a5188ae7e3aa1454bac1c21e5c5081e441687397",
        "The bounded corrective pass was PM-accepted and is finalized by the corrective\nGit closure.",
        "M118A_CONCURRENCY_CORRECTION_PENDING_PM_REVIEW: NO",
    )
    _assert_required(
        normalized,
        "PM acceptance was initially held after a reproducible concurrent first-open",
        "WAL negotiation is not itself a canonical security-state transaction.",
        "Transient SQLite contention is not store corruption.",
        "The code/dependency separation remains a static boundary only; it is not OS/process isolation.",
        "Deployment verification remains `NO`.",
    )
    correction = text[text.index("The post-finalization correction state is explicit:"):]
    _assert_required(
        correction,
        "M118A_GIT_FINALIZED: YES",
        "M118A_PM_ACCEPTED: YES",
        "M118A_CONCURRENCY_DEFECT_CONFIRMED: YES",
        "M118A_CONCURRENCY_CORRECTION_IMPLEMENTED_LOCALLY: YES",
        "M118A_CONCURRENCY_CORRECTION_TEST_VERIFIED: YES",
        "M118A_CONCURRENCY_CORRECTION_GIT_DURABLE: YES",
        "DEPLOYMENT_VERIFIED: NO",
        "PROGRESS_UPDATED: YES",
        "COMMIT_CREATED: YES",
        "TAG_CREATED: YES",
        "PUSH_PERFORMED: YES",
        "SUCCESSOR_MILESTONE_AUTHORIZED: NO",
    )
    assert "M118A_PM_ACCEPTED: NO" not in correction
    assert "M118A_CONCURRENCY_CORRECTION_GIT_DURABLE: NO" not in correction


def test_architecture_integration_is_minimal_and_milestone_is_unchanged():
    architecture = _text(ARCHITECTURE)
    integration = architecture[architecture.index("## 19. Security and Authority Architecture"):]
    normalized = _normalized(integration)
    _assert_required(
        normalized,
        "Security and Authority Architecture",
        _normalized(PRECEDENCE),
        "docs/architecture/SECURITY_ARCHITECTURE.md",
        "canonical living architecture for the security and authority domain",
        "subordinate to the Constitution and this overall Architecture",
        "one persistent digital mind",
        "The Owner is the human authority boundary",
        "OAS",
        "ordinary runtime is not an Owner-evidence issuer",
        "Core Coordination owns canonical cognitive Goal state",
        "Authentication is not intent interpretation",
        "Goal acceptance is not Action authorization",
        "Action success is not completion",
        "Observation plus Verification is the completion boundary",
        "Security decision, design, implementation, and verification status are separate",
        "Milestone architecture documents remain immutable historical evidence",
    )
    assert architecture.count("## 19. Security and Authority Architecture") == 1
    assert "MILESTONE_117A_SINGLE_OWNER_LAN_TRUST_ROOT_CONTRACT_PROOF" not in integration


def test_no_protected_document_or_m117a_artifact_was_modified():
    assert _sha256(M117A) == APPROVED_M117A_HASH
    assert _sha256(M117A_LOCK) == APPROVED_M117A_LOCK_HASH
    for path, expected in BASELINE_PROTECTED_HASHES.items():
        assert _sha256(path) == expected, path


def test_gate_is_documentation_only_and_has_no_unapproved_security_claims():
    source = _text(Path(__file__))
    assert not re.search(r"from\s+aether|import\s+aether", source)
    assert "sub" + "process" not in source
    text = _text(SECURITY)
    _assert_required(
        _normalized(text),
        "not a production security implementation",
        "not a deployed trust boundary",
        "authentication-facing OAS remains unimplemented",
        "Static M117A tests verify documentation structure only",
        "separately authorized M118A implementation was historically finalized by the Git closure",
    )
    assert "DEPLOYMENT_STATUS" not in text
    assert "PROPOSAL_ONLY" not in text
    assert "M118A_STARTED: NO" not in text
    assert "M118A_FINALIZED: YES" in text
    assert "M117A_FINALIZED: YES_DESIGN_ONLY" not in text
