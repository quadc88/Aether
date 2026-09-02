"""Static scope and status lock for the M125A rollback foundation build."""

from __future__ import annotations

from pathlib import Path
import re
import subprocess


ROOT = Path(__file__).resolve().parents[1]
DOCUMENT = ROOT / "docs/architecture/MILESTONE_125A_OAS_FIRST_INSTALL_ROLLBACK_TO_NOT_DEPLOYED_DURABLE_TRANSACTION_FOUNDATION_BUILD.md"
SUMMARY = Path("/home/aether/summaries/milestone_125A_oas_first_install_rollback_to_not_deployed_durable_transaction_foundation_build_finalization_summary.txt")
ORIGINAL_SUMMARY = Path("/home/aether/summaries/milestone_125A_oas_first_install_rollback_to_not_deployed_durable_transaction_foundation_build_summary.txt")
PRIOR_CORRECTED_SUMMARY = Path("/home/aether/summaries/milestone_125A_corrected_oas_first_install_rollback_to_not_deployed_durable_transaction_foundation_build_summary.txt")
FINAL_REPOSITORY_PATHS = {
    "aether/deployment/first_install_rollback.py",
    "tests/test_deployment_first_install_rollback.py",
    DOCUMENT.relative_to(ROOT).as_posix(),
    Path(__file__).relative_to(ROOT).as_posix(),
    "PROGRESS.md",
}
STATUS_BEGIN = "AUTHORITATIVE_M125A_STATUS_BEGIN"
STATUS_END = "AUTHORITATIVE_M125A_STATUS_END"
CANONICAL_STATUS = {
    "M125A_AUTHORIZED": "YES",
    "M125A_STARTED": "YES",
    "M125A_FINALIZED": "YES",
    "M125A_TYPE": "BOUNDED_IMPLEMENTATION_FOUNDATION_BUILD",
    "DECISION_STATUS": "CURRENT",
    "DESIGN_STATUS": "DESIGN_PROVEN",
    "IMPLEMENTATION_STATUS": "IMPLEMENTED",
    "VERIFICATION_STATUS": "TEST_VERIFIED",
    "DEPLOYMENT_VERIFIED": "NO",
    "DEPLOYMENT_STATE": "NOT_DEPLOYED",
    "DEPLOYMENT_PROFILE": "FIRST_INSTALL_LOCAL_AF_UNIX_ONLY",
    "ROLLBACK_FOUNDATION_IMPLEMENTED": "YES",
    "ISOLATED_ROOT_ROLLBACK_PROVEN": "YES",
    "LIVE_ROLLBACK_PROVEN": "NO",
    "PRIVILEGED_ADAPTERS_IMPLEMENTED": "NO",
    "PRODUCTION_TRUST_MATERIAL_PROVEN": "NO",
    "TRUTHFUL_OWNER_DEPLOYMENT_AUTHORITY_PROVEN": "NO",
    "ROLLBACK_TO_NOT_DEPLOYED_LIVE_PROVEN": "NO",
    "SELECTED_EXIT": "EXIT_A_BOUNDED_ROLLBACK_FOUNDATION_FINALIZED",
    "BUILD_AUTHORIZED": "YES",
    "LIVE_ROLLBACK_AUTHORIZED": "NO",
    "LIVE_DEPLOYMENT_AUTHORIZED": "NO",
    "TARGET_HOST_MUTATION_PERFORMED": "NO",
    "TRUST_PROVISIONING_AUTHORIZED": "NO",
    "UPGRADE_AUTHORIZED": "NO",
    "SCHEMA_MIGRATION_AUTHORIZED": "NO",
    "ADOPTION_AUTHORIZED": "NO",
    "PUBLIC_EXPOSURE_AUTHORIZED": "NO",
    "GENERIC_ACT_AUTHORIZED": "NO",
    "PROGRESS_UPDATED": "YES",
    "COMMIT_CREATED": "YES",
    "TAG_CREATED": "YES",
    "PUSH_PERFORMED": "YES",
    "SUCCESSOR_AUTHORIZED": "NO",
    "SUCCESSOR_NUMBER_ASSIGNED": "NO",
    "READY_FOR_PM_REVIEW": "NO",
}
STEP_IDS = tuple(f"M125A-{index:02d}" for index in range(1, 15))
STEP_FIELDS = (
    "exact action", "mutation or read-only classification", "executing authority/principal", "exact target",
    "expected previous state", "required preconditions", "resulting state", "postcondition", "verification method",
    "rollback or fail-closed action", "automatic-rollback boundary", "sensitive-data classification",
    "Owner confirmation requirement", "durable evidence produced",
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


def _step_blocks(document: str) -> list[tuple[str, str]]:
    matches = list(re.finditer(r"^### (M125A-\d{2})$\n(.*?)(?=^### M125A-\d{2}$|^## |\Z)", document, re.MULTILINE | re.DOTALL))
    return [(match.group(1), match.group(2)) for match in matches]


def test_repository_scope_is_exactly_the_five_m125a_finalization_paths():
    changed_paths = _changed_paths()
    assert changed_paths == FINAL_REPOSITORY_PATHS or not changed_paths


def test_authoritative_status_is_exact_and_negative_gated_for_live_operations():
    document = DOCUMENT.read_text(encoding="utf-8")
    assert _status_map(document) == CANONICAL_STATUS
    for forbidden in (
        "M125A_TYPE: IMPLEMENTATION_AND_DURABLE_ROLLBACK_CONTRACT_PROOF",
        "ROLLBACK_TO_NOT_DEPLOYED_PROVEN:",
        "ROLLBACK_PROOF_SCOPE:",
        "TARGET_HOST_READY_FOR_DEPLOYMENT_REVIEW:",
        "AUTOMATED_RECOVERY_AUTHORIZED:",
        "M125A_FINALIZED: NO",
        "LIVE_ROLLBACK_PROVEN: YES",
        "ISOLATED_ROOT_ROLLBACK_PROVEN: NO",
        "PRIVILEGED_ADAPTERS_IMPLEMENTED: YES",
        "PRODUCTION_TRUST_MATERIAL_PROVEN: YES",
        "TRUTHFUL_OWNER_DEPLOYMENT_AUTHORITY_PROVEN: YES",
        "ROLLBACK_TO_NOT_DEPLOYED_LIVE_PROVEN: YES",
        "LIVE_ROLLBACK_AUTHORIZED: YES",
        "LIVE_DEPLOYMENT_AUTHORIZED: YES",
        "TARGET_HOST_MUTATION_PERFORMED: YES",
        "DEPLOYMENT_VERIFIED: YES",
        "SUCCESSOR_AUTHORIZED: YES",
        "SUCCESSOR_NUMBER_ASSIGNED: YES",
    ):
        assert forbidden not in document


def test_ordered_manifest_has_all_required_fields():
    document = DOCUMENT.read_text(encoding="utf-8")
    blocks = _step_blocks(document)
    assert tuple(step_id for step_id, _block in blocks) == STEP_IDS
    for _step_id, block in blocks:
        for field in STEP_FIELDS:
            assert re.search(rf"^- {re.escape(field)}:", block, re.MULTILINE)


def test_durability_and_recovery_contract_is_explicit():
    document = DOCUMENT.read_text(encoding="utf-8")
    for phrase in (
        "rollback-journal.jsonl", "rollback-receipts.jsonl", "rollback.lock", "receipt_sequence", "fsynced", "directory-fsynced",
        "does not reapply the effect", "ROOT_REVIEW_REQUIRED", "REJECTED_CONFLICT", "hard-link", "reverse dependency order",
        "isolated temporary root", "No packet", "trust provisioning",
    ):
        assert phrase in document
    assert "does not prove rollback behavior on the real target host" in document


def test_implementation_has_no_direct_host_or_shell_authority():
    source = (ROOT / "aether/deployment/first_install_rollback.py").read_text(encoding="utf-8")
    for forbidden in ("subprocess", "systemctl", "os.system", "socket.AF_INET", "account-management", "/etc/", "/usr/", "/opt/"):
        assert forbidden not in source
    assert "class PrivilegedEffectAdapter(Protocol)" in source
    assert "create_isolated_root" not in source
    assert "_require_capability" in source


def test_external_summary_is_required_and_status_bound():
    assert SUMMARY.exists()
    assert ORIGINAL_SUMMARY.exists()
    assert PRIOR_CORRECTED_SUMMARY.exists()
    summary = SUMMARY.read_text(encoding="utf-8")
    assert _status_map(summary) == CANONICAL_STATUS
    for phrase in (
        "evidence, not authority", "33 focused tests passed", "full-suite", "No host mutation",
        "aether/deployment/first_install_rollback.py", "M125A-14", "FINAL_ARTIFACT_HASHES",
        "COMMIT_CREATED: YES", "TAG_CREATED: YES", "PUSH_PERFORMED: YES",
    ):
        assert phrase in summary


def test_claim_precision_and_boundary_status_are_explicit():
    document = DOCUMENT.read_text(encoding="utf-8")
    for phrase in (
        "bounded rollback transaction foundation only inside an injected isolated temporary root",
        "does not prove rollback behavior on the real target host",
        "does not implement any privileged adapter",
        "does not prove production trust material",
        "does not prove truthful Owner deployment or activation authority",
        "M125A does not prove live transition of the target host to `NOT_DEPLOYED`",
        "canonical project deployment state",
        "not a newly observed target-host transition",
        "VERIFICATION_STATUS: TEST_VERIFIED` is not deployment verification",
        "records Git-durable closure of the bounded M125A artifact",
    ):
        assert phrase in document
