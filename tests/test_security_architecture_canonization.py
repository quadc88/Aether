"""Documentation-only lock for the pre-M118A security architecture gate."""

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
README = ROOT / "README.md"
CONSTITUTION = ROOT / "docs/CONSTITUTION.md"
PROGRESS = ROOT / "PROGRESS.md"

APPROVED_M117A_HASH = "a56d3d433cd787f7ee902c0861953b604fd20861d3e9adabcd5adcaefee9673b"
APPROVED_M117A_LOCK_HASH = "b6c150821b9d996fe2f6982c2062b937d3c5bcc9381a152598d0446c88e19d85"
BASELINE_PROTECTED_HASHES = {
    README: "5357e53635c7467332129048155b39ac9282d6aff268f5f910594a5b26d72cad",
    CONSTITUTION: "0055748f683bf753b3471a0317b68677752c312d4030b12fbc71684fd3af3ee1",
    PROGRESS: "3ecbeae560f00fde4d1eb2ef51e64d4a1ab839d036a522445a94b252d40b999c",
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
    assert len(target_rows) >= 14
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
        "no production OAS",
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
        "M118A_AUTHORIZED: YES_NOT_STARTED",
        "M118A_STARTED: NO",
        "generalized Tool-Operation-Capability authority",
    )
    assert "PHASE 1 DOCUMENTATION PASS" not in text
    assert "frozen design authority" not in text
    assert "no Tool / Operation / Capability authority" not in text
    assert "no Tool / Operation / Capability controls" not in text
    assert "M117A is the frozen design authority" not in text


def test_m118a_boundary_is_explicit_and_not_started():
    text = _text(SECURITY)
    traceability = text[text.index("## 18. Milestone and Evidence Traceability"):]
    _assert_required(
        traceability,
        "M118A - Owner Authority Service Durable Security Kernel Foundation Build",
        "M118A_AUTHORIZED: YES_NOT_STARTED",
        "M118A_STARTED: NO",
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
        "This canonization gate does not start M118A.",
    )


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
        text,
        "not a production security implementation",
        "not a deployed trust boundary",
        "No production OAS durable security store",
        "Static M117A tests verify documentation structure only",
        "No M118A artifact",
    )
    assert "DEPLOYMENT_STATUS" not in text
    assert "PROPOSAL_ONLY" not in text
    assert "M118A_STARTED: YES" not in text
    assert "M117A_FINALIZED: YES_DESIGN_ONLY" not in text
