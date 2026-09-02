"""Corrective static locks for the M124A deployment-transaction proof."""

from __future__ import annotations

from pathlib import Path
import re
import subprocess


ROOT = Path(__file__).resolve().parents[1]
DOCUMENT = ROOT / "docs/architecture/MILESTONE_124A_OAS_CONTROLLED_FIRST_INSTALL_DEPLOYMENT_TRANSACTION_AUTHORIZATION_PROOF.md"
SUMMARY = Path("/home/aether/summaries/milestone_124A_controlled_first_install_deployment_transaction_authorization_proof_finalization_summary.txt")
ALLOWED_REPOSITORY_PATHS = {
    "PROGRESS.md",
    DOCUMENT.relative_to(ROOT).as_posix(),
    Path(__file__).relative_to(ROOT).as_posix(),
}

CANONICAL_STATUS = {
    "M124A_AUTHORIZED": "YES",
    "M124A_STARTED": "YES",
    "M124A_FINALIZED": "YES",
    "M124A_TYPE": "DESIGN_DISCOVERY_SECURITY_AND_OPERATIONS_CONTRACT_PROOF",
    "DECISION_STATUS": "CURRENT",
    "DESIGN_STATUS": "PARTIAL",
    "IMPLEMENTATION_STATUS": "NOT_IMPLEMENTED",
    "VERIFICATION_STATUS": "TEST_VERIFIED",
    "DEPLOYMENT_VERIFIED": "NO",
    "DEPLOYMENT_STATE": "NOT_DEPLOYED",
    "DEPLOYMENT_PROFILE": "FIRST_INSTALL_LOCAL_AF_UNIX_ONLY",
    "DEPLOYMENT_TRANSACTION_DEFINED": "YES",
    "PRODUCTION_TRUST_MATERIAL_PROVEN": "NO",
    "ROLLBACK_TO_NOT_DEPLOYED_PROVEN": "NO",
    "TARGET_READY_FOR_EXPLICIT_OWNER_DEPLOYMENT_AUTHORIZATION_REVIEW": "NO",
    "SELECTED_EXIT": "EXIT_B_PREREQUISITES_OR_RECOVERY_GAPS_REQUIRE_CORRECTION",
    "LIVE_DEPLOYMENT_AUTHORIZED": "NO",
    "TARGET_HOST_MUTATION_PERFORMED": "NO",
    "UPGRADE_AUTHORIZED": "NO",
    "SCHEMA_MIGRATION_AUTHORIZED": "NO",
    "PUBLIC_EXPOSURE_AUTHORIZED": "NO",
    "ADOPTION_AUTHORIZED": "NO",
    "AUTOMATED_RECOVERY_AUTHORIZED": "NO",
    "GENERIC_ACT_AUTHORIZED": "NO",
    "PROGRESS_UPDATED": "YES",
    "COMMIT_CREATED": "YES",
    "TAG_CREATED": "YES",
    "PUSH_PERFORMED": "YES",
    "SUCCESSOR_AUTHORIZED": "NO",
    "SUCCESSOR_NUMBER_ASSIGNED": "NO",
    "READY_FOR_PM_REVIEW": "NO",
}

STATUS_BEGIN = "AUTHORITATIVE_M124A_STATUS_BEGIN"
STATUS_END = "AUTHORITATIVE_M124A_STATUS_END"
OBSOLETE_EXIT = "EXIT_B_HOST_READINESS_GAPS_REQUIRE_CORRECTION"

STEP_FIELDS = (
    "step ID",
    "phase",
    "exact action",
    "mutation or read-only classification",
    "executing authority/principal",
    "exact target",
    "expected previous state",
    "required preconditions",
    "resulting state",
    "postcondition",
    "verification method",
    "rollback or fail-closed action",
    "automatic-rollback boundary",
    "sensitive-data classification",
    "Owner confirmation requirement",
    "durable evidence produced",
)

STEP_IDS = tuple(f"M124A-{index:02d}" for index in range(19))
PHASE_NAMES = (
    "PHASE 0 — OWNER AUTHORIZATION",
    "PHASE 1 — READ-ONLY REVALIDATION",
    "PHASE 2 — INACTIVE STAGING",
    "PHASE 3 — PRE-ACTIVATION VERIFICATION HOLD POINT",
    "PHASE 4 — EXPLICIT ACTIVATION AUTHORITY",
    "PHASE 5 — BOUNDED ACTIVATION",
    "PHASE 6 — OBSERVATION AND VERIFICATION",
    "PHASE 7 — COMMIT OR FAIL CLOSED",
    "PHASE 8 — REPORT",
)

ROLLBACK_WINDOWS = (
    "before packet consumption",
    "after packet consumption but before mutation",
    "inactive staging",
    "trust evidence before pending",
    "principal creation",
    "directory creation",
    "release publication",
    "unit publication",
    "generation gate",
    "daemon reload",
    "pending activation record",
    "current-link switch",
    "socket activation",
    "service start before readiness",
    "readiness before smoke",
    "smoke before commit",
    "commit before postcondition closure",
    "host reboot",
    "executor crash",
    "lost controlling session",
    "authorization expiry",
    "rollback failure",
    "post-commit mismatch",
)


def _status_block(text: str) -> str:
    assert text.count(STATUS_BEGIN) == 1
    assert text.count(STATUS_END) == 1
    start = text.index(STATUS_BEGIN)
    finish = text.index(STATUS_END, start)
    assert finish > start
    return text[start:finish]


def _status_map(text: str) -> dict[str, str]:
    parsed: dict[str, str] = {}
    for line in _status_block(text).splitlines()[1:]:
        stripped = line.strip()
        if not stripped:
            continue
        key, separator, value = stripped.partition(":")
        assert separator, f"status line is not key/value: {stripped}"
        assert key not in parsed, f"duplicate status key: {key}"
        parsed[key] = value.strip()
    return parsed


def _step_blocks(document: str) -> dict[str, str]:
    matches = list(re.finditer(r"^### (M124A-\d{2})$\n(.*?)(?=^### M124A-\d{2}$|^## |\Z)", document, re.MULTILINE | re.DOTALL))
    assert tuple(match.group(1) for match in matches) == STEP_IDS
    return {match.group(1): match.group(2) for match in matches}


def _step_map(block: str) -> dict[str, str]:
    parsed: dict[str, str] = {}
    for line in block.splitlines():
        if not line.startswith("- "):
            continue
        key, separator, value = line[2:].partition(":")
        assert separator, f"manifest line is not key/value: {line}"
        assert key not in parsed, f"duplicate manifest field: {key}"
        parsed[key] = value.strip()
    return parsed


def _rollback_blocks(document: str) -> dict[str, str]:
    matches = list(re.finditer(r"^### Rollback window: (.*?)$\n(.*?)(?=^### Rollback window: |^## |\Z)", document, re.MULTILINE | re.DOTALL))
    return {match.group(1): match.group(2) for match in matches}


def _changed_paths() -> set[str]:
    lines = subprocess.run(
        ["git", "status", "--short", "--untracked-files=all"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.splitlines()
    return {line[3:] for line in lines if len(line) >= 4 and line[:2] in {" M", "??", "A ", "AM"}}


def test_repository_scope_is_exactly_the_two_m124a_artifacts():
    assert _changed_paths() == ALLOWED_REPOSITORY_PATHS


def test_authoritative_status_is_exact_and_uses_only_the_m124a_schema():
    document = DOCUMENT.read_text(encoding="utf-8")
    assert _status_map(document) == CANONICAL_STATUS
    assert document.count(STATUS_BEGIN) == document.count(STATUS_END) == 1
    assert OBSOLETE_EXIT not in document
    assert "EXIT_A_TARGET_READY_FOR_BOUNDED_FIRST_INSTALL_DEPLOYMENT_REVIEW" not in document
    assert "Owner/PM" not in document
    assert "PM/Owner" not in document
    assert "TEST_VERIFIED" in document
    assert "DEPLOYMENT_VERIFIED: YES" not in document
    assert "LIVE_DEPLOYMENT_AUTHORIZED: YES" not in document
    assert "TARGET_HOST_MUTATION_PERFORMED: YES" not in document
    assert "M124A_FINALIZED: YES" in document
    assert "DECISION_STATUS: CURRENT" in document
    assert "READY_FOR_PM_REVIEW: NO" in document
    assert "finalization authorizes deployment" not in document


def test_trust_material_availability_is_separated_from_installed_target_state():
    document = DOCUMENT.read_text(encoding="utf-8")
    required_paths = (
        "/etc/aether/release-trust-anchor.pub",
        "/etc/aether/release-trust-anchor.fingerprint",
        "/etc/aether/release-test-evidence.sha256",
        "/etc/aether/release-verifier.sha256",
        "/usr/libexec/aether-release-verify",
    )
    for path in required_paths:
        assert path in document
        assert "NOT_PRESENT" in document
    for phrase in (
        "PRODUCTION_SIGNING_AUTHORITY_PROVEN: NO",
        "PRODUCTION_PUBLIC_TRUST_ANCHOR_PROVEN: NO",
        "PRODUCTION_SIGNED_CANDIDATE_PROVEN: NO",
        "PRODUCTION_TRUST_MATERIAL_PROVEN: NO",
        "INSTALLED_TARGET_HOST_TRUST_STATE",
        "does not prove global unavailability",
        "does not prove global",
        "Trust bootstrap",
        "outside the candidate-controlled deployment transaction",
    ):
        assert re.search(r"\s+".join(re.escape(part) for part in phrase.split()), document)
    assert "candidate-supplied" in document
    assert "test, development, or self-approved key" in document
    assert "private keys" in document


def test_owner_project_manager_executor_and_runtime_authority_are_distinct():
    document = DOCUMENT.read_text(encoding="utf-8")
    for phrase in (
        "### Project Manager",
        "### Owner",
        "### Root transaction executor",
        "### Ordinary Aether runtime",
        "cannot mint Owner authentication evidence",
        "Root possession is not Owner intent",
        "receives no root or deployment authority",
        "OWNER_DEPLOYMENT_AUTHORIZATION_SOURCE_PROVEN: NO",
        "OWNER_ACTIVATION_CONFIRMATION_SOURCE_PROVEN: NO",
        "M124A does not implement Human Authority",
    ):
        assert re.search(r"\s+".join(re.escape(part) for part in phrase.split()), document)
    assert "Owner/PM" not in document
    assert "Project Manager approval of milestone scope is separate" in document


def test_manifest_has_all_required_fields_for_every_ordered_step():
    document = DOCUMENT.read_text(encoding="utf-8")
    blocks = _step_blocks(document)
    assert len(blocks) == 19
    for step_id, block in blocks.items():
        fields = _step_map(block)
        assert tuple(fields) == STEP_FIELDS
        assert fields["step ID"] == f"`{step_id}`"
        assert fields["mutation or read-only classification"] in {
            "`READ_ONLY`", "`MUTATION`", "`MUTATION` followed by `READ_ONLY`",
        }
        assert fields["executing authority/principal"]
        assert fields["expected previous state"]
        assert fields["required preconditions"]
        assert fields["postcondition"]
        assert fields["verification method"]
        assert fields["rollback or fail-closed action"]
        assert fields["automatic-rollback boundary"]
        assert fields["sensitive-data classification"]
        assert fields["Owner confirmation requirement"]
        assert fields["durable evidence produced"]


def test_corrected_phase_sequence_and_hold_points_are_locked():
    document = DOCUMENT.read_text(encoding="utf-8")
    positions = [document.index(f"### {phase}") for phase in PHASE_NAMES]
    assert positions == sorted(positions)
    for phrase in (
        "PHASE 3 — PRE-ACTIVATION VERIFICATION HOLD POINT",
        "PHASE 4 — EXPLICIT ACTIVATION AUTHORITY",
        "second exact Owner confirmation",
        "The original packet explicitly covers the final Phase 3 digest",
        "Root, systemd, OAS, Project Manager, and the candidate cannot self-confirm",
        "durable trust evidence before pending state",
        "effective systemd security properties",
        "exact initial schema",
        "PHASE 7 — COMMIT OR FAIL CLOSED",
        "PHASE 8 — REPORT",
    ):
        assert re.search(r"\s+".join(re.escape(part) for part in phrase.split()), document)


def test_rollback_matrix_has_every_required_field_and_proves_global_gap():
    document = DOCUMENT.read_text(encoding="utf-8")
    blocks = _rollback_blocks(document)
    assert tuple(blocks) == ROLLBACK_WINDOWS
    required = (
        "starting state",
        "objects that may exist",
        "exact durable evidence",
        "automatic rollback available",
        "implementation/API supporting automatic rollback",
        "exact safe removal sequence",
        "identity and unchanged-object checks",
        "evidence that must be retained",
        "manual privileged review requirement",
        "terminal state",
        "whether NOT_DEPLOYED is actually proven",
        "forbidden success claim",
    )
    for block in blocks.values():
        for field in required:
            assert re.search(rf"^- {re.escape(field)}:", block, re.MULTILINE)
        assert "automatic rollback available: `NO`" in block
    assert "ROLLBACK_TO_NOT_DEPLOYED_PROVEN: NO" in document
    assert re.search(
        r"\s+".join(
            re.escape(part)
            for part in "Fail closed is not equivalent to `DEPLOYMENT_STATE: NOT_DEPLOYED`".split()
        ),
        document,
    )
    assert "Manual privileged review is disposition evidence only;" in document
    assert "not automatic rollback proof" in document
    assert "root review" in document
    assert "proof" in document


def test_no_deployment_authority_or_candidate_trust_substitution_is_claimed():
    document = DOCUMENT.read_text(encoding="utf-8")
    forbidden = (
        "LIVE_DEPLOYMENT_AUTHORIZED: YES",
        "TARGET_HOST_MUTATION_PERFORMED: YES",
        "PRODUCTION_TRUST_MATERIAL_PROVEN: YES",
        "ROLLBACK_TO_NOT_DEPLOYED_PROVEN: YES",
        "candidate-controlled trust bootstrap",
        "candidate-supplied trust anchor",
    )
    for phrase in forbidden:
        assert phrase not in document
    assert "No packet is accepted" in document
    assert "No successor number" in document


def test_corrected_external_summary_is_required_and_status_matches():
    summary = SUMMARY.read_text(encoding="utf-8")
    assert _status_map(summary) == CANONICAL_STATUS
    assert OBSOLETE_EXIT not in summary
    for phrase in (
        "evidence, not authority",
        "M124A_FINALIZED: YES",
        "LIVE_DEPLOYMENT_AUTHORIZED: NO",
        "TARGET_HOST_MUTATION_PERFORMED: NO",
        "TRUST_PROVISIONING_AUTHORIZED: NO",
        "SUCCESSOR_AUTHORIZED: NO",
        "COMMAND_EXIT_CODES_AND_COUNTS",
        "M124A static lock",
        "M123A immutable lock",
        "M122A signed-release and trust tests",
        "protected M121A hash verification",
        "FINAL_COMMIT:",
        "ANNOTATED_TAG:",
    ):
        assert phrase in summary
