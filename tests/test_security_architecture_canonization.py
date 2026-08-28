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
README = ROOT / "README.md"
CONSTITUTION = ROOT / "docs/CONSTITUTION.md"

APPROVED_M117A_HASH = "a56d3d433cd787f7ee902c0861953b604fd20861d3e9adabcd5adcaefee9673b"
APPROVED_M117A_LOCK_HASH = "b6c150821b9d996fe2f6982c2062b937d3c5bcc9381a152598d0446c88e19d85"
APPROVED_M119A_HASH = "2f6d36d503a41aec1513605cfc26bd77755aa0d0fd821683b2a783513193646b"
APPROVED_M119A_LOCK_HASH = "780dd0da75733f8443abe4817f90d95526dbddc477c1e420bd843357b0a17e50"
BASELINE_PROTECTED_HASHES = {
    README: "5357e53635c7467332129048155b39ac9282d6aff268f5f910594a5b26d72cad",
    CONSTITUTION: "0055748f683bf753b3471a0317b68677752c312d4030b12fbc71684fd3af3ee1",
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
    traceability = text[text.index("The M119A evidence reference is:"):]
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
