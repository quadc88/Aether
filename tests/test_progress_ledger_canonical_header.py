"""
Milestone 90B-R1-R — Canonical Header Singleton-Field Contract Tests

This test module enforces the canonical current-state header contract for
PROGRESS.md. It validates that each authorized header field occurs exactly
once and that obsolete fields are absent from the canonical header.

The canonical header is defined as the beginning of PROGRESS.md through the
first horizontal section separator before Section 1.

Historical archive content is outside this singleton-field contract.
"""
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROGRESS = ROOT / "PROGRESS.md"
import pytest


def _read_progress() -> str:
    return PROGRESS.read_text(encoding="utf-8")


def _header_block(text: str) -> str:
    """Return the canonical header: from start through first '---' separator."""
    lines = text.split("\n")
    result = []
    for line in lines:
        if line.strip() == "---":
            break
        result.append(line)
    return "\n".join(result)


def _parse_header_field(header: str, field_name: str) -> str:
    """Extract the value after **field_name:** in the canonical header block.

    Raises ValueError if the field is absent or duplicated.
    Processes one line at a time and never crosses line boundaries.
    """
    marker = f"**{field_name}:**"
    matching_lines = [
        line
        for line in header.splitlines()
        if line.startswith(marker)
    ]

    count = len(matching_lines)
    if count != 1:
        raise ValueError(
            f"Canonical header field '{field_name}' "
            f"was not found exactly once; found {count}."
        )

    return matching_lines[0][len(marker):].strip()


def _run_git(args: list[str]) -> subprocess.CompletedProcess[str]:
    """Run a git command locally without shell, remote calls, or mutation."""
    return subprocess.run(
        args, check=False, capture_output=True, text=True, cwd=ROOT
    )


def _get_all_current_work_fields(header: str) -> dict[str, str]:
    """Parse six current-work fields from the canonical header."""
    field_names = [
        "Last updated",
        "Current completed local milestone",
        "Current active milestone/module",
        "Current status",
        "Next milestone",
        "Test baseline",
    ]
    return {name: _parse_header_field(header, name) for name in field_names}


def test_header_has_one_last_updated_field():
    text = _read_progress()
    header = _header_block(text)
    assert header.count("**Last updated:**") == 1


def test_header_has_one_current_completed_milestone_field():
    text = _read_progress()
    header = _header_block(text)
    assert header.count("**Current completed local milestone:**") == 1


def test_header_has_one_current_active_milestone_field():
    text = _read_progress()
    header = _header_block(text)
    assert header.count("**Current active milestone/module:**") == 1


def test_header_has_one_current_status_field():
    text = _read_progress()
    header = _header_block(text)
    assert header.count("**Current status:**") == 1


def test_header_has_one_next_milestone_field():
    text = _read_progress()
    header = _header_block(text)
    assert header.count("**Next milestone:**") == 1


def test_header_has_one_test_baseline_field():
    text = _read_progress()
    header = _header_block(text)
    assert header.count("**Test baseline:**") == 1, (
        "Duplicate **Test baseline:** field found in canonical header"
    )


def test_header_has_one_openapi_baseline_field():
    text = _read_progress()
    header = _header_block(text)
    assert header.count("**OpenAPI baseline:**") == 1, (
        "Duplicate **OpenAPI baseline:** field found in canonical header"
    )


def test_header_has_one_git_verification_rule_field():
    text = _read_progress()
    header = _header_block(text)
    assert header.count("**Git verification rule:**") == 1, (
        "Duplicate **Git verification rule:** field found in canonical header"
    )


def test_header_has_one_current_closure_ledger_field():
    text = _read_progress()
    header = _header_block(text)
    assert header.count("**Closure durability authority:**") == 1


def test_header_has_one_current_closure_tag_field():
    text = _read_progress()
    header = _header_block(text)
    assert header.count("**Closure tag authority:**") == 1


def test_header_has_one_previous_accepted_closure_tag_field():
    text = _read_progress()
    header = _header_block(text)
    assert header.count("**Previous durable closure tag:**") == 1
    assert header.count("**Earlier accepted closure tag:**") == 1


def test_header_rejects_obsolete_or_legacy_git_fields():
    text = _read_progress()
    header = _header_block(text)
    assert "**Last accepted closure tag:**" not in header, (
        "Obsolete **Last accepted closure tag:** field must be absent from canonical header"
    )
    assert "**Latest local tag:**" not in header, (
        "Obsolete **Latest local tag:** field must be absent from canonical header"
    )
    assert "**Latest pushed GitHub/origin status:**" not in header, (
        "Obsolete **Latest pushed GitHub/origin status:** field must be absent from canonical header"
    )


def test_current_92a_local_state_is_consistent_across_header():
    text = _read_progress()
    header = _header_block(text)
    fields = _get_all_current_work_fields(header)

    identity_tokens = {
        "Last updated": "Milestone 95A Observation Provenance Source and Consumer-Proof Boundary Build complete locally; Milestone 94 CLOSED / GIT-DURABLE / PM-ACCEPTED externally",
        "Current completed local milestone": "Milestone 95A Observation Provenance Source and Consumer-Proof Boundary Build complete locally",
        "Current active milestone/module": "Milestone 95A Observation Provenance Source and Consumer-Proof Boundary; Milestone 95 OPEN; Milestone 94 is CLOSED / GIT-DURABLE / PM-ACCEPTED externally",
        "Current status": "Milestone 94 CLOSED / GIT-DURABLE / PM-ACCEPTED externally; Milestone 95 OPEN; Milestone 95A Observation Provenance Source and Consumer-Proof Boundary complete locally",
        "Next milestone": "human/project-manager review of Milestone 95A Observation Provenance Source and Consumer-Proof Boundary",
        "Test baseline": "2571 pre-93A full-suite baseline",
    }
    assert all(token in fields[name] for name, token in identity_tokens.items())
    assert fields["Current completed local milestone"].startswith(
        "Milestone 95A Observation Provenance Source and Consumer-Proof Boundary"
    )

    for field_name in ("Closure durability authority", "Closure tag authority"):
        value = _parse_header_field(header, field_name)
        assert "does not self-assert" in value or "separately authorized" in value
        assert not re.search(r"[0-9a-f]{40}", value)

    assert "6ecc5dd254335e8f6d0020050db0674d96a9fd05" in _parse_header_field(
        header, "M94 parent closure state"
    )
    assert _parse_header_field(header, "M94 parent objective") == "SATISFIED."
    assert _parse_header_field(header, "M94 functional obligations") == "COMPLETE."
    assert _parse_header_field(header, "M94 closure record") == "GIT-DURABLE."
    assert _parse_header_field(header, "M94 durable closure") == "CLOSED / GIT-DURABLE / PM-ACCEPTED."
    assert _parse_header_field(header, "M95 authority").startswith("OPEN;")
    assert _parse_header_field(header, "M95A status") == "COMPLETE LOCALLY / PENDING PM REVIEW."
    assert _parse_header_field(header, "M95B status") == "NOT AUTHORIZED."

    active = fields["Current active milestone/module"]
    status = fields["Current status"]
    for token in (
        "selected model B",
        "current runtime containment Model E",
        "Rule 4 physical ownership is Core Governance",
        "file.restricted_read",
        "generic /chat execution authority NO",
        "Observation call-local",
        "M95B NOT AUTHORIZED",
    ):
        assert token in active or token in status
    for token in (
        "plan_step_id NOT_CURRENTLY_PROVABLE",
        "collector_contract_id NOT_CURRENTLY_PROVABLE",
        "expected_value NOT_CURRENTLY_PROVABLE",
        "privacy-safe persistence NOT_SAFE_TO_PERSIST",
        "current proven durable consumer NONE",
        "MODEL_B_JUSTIFIED",
    ):
        assert token in status


def test_closure_sha_syntax_and_commit_exists():
    text = _read_progress()
    header = _header_block(text)
    authority = _parse_header_field(header, "Closure durability authority")
    assert "Git directly determines the commit containing the current closure ledger content" in authority
    assert "does not self-assert its own closure commit SHA" in authority
    assert not re.search(r"[0-9a-f]{40}", authority)


def test_current_closure_ledger_is_ancestor_of_head():
    text = _read_progress()
    header = _header_block(text)
    authority = _parse_header_field(header, "Closure durability authority")
    assert "Git directly determines" in authority
    assert "does not self-assert its own closure commit SHA" in authority
    assert not re.search(r"[0-9a-f]{40}", authority)


def test_current_closure_tag_name_and_resolves():
    text = _read_progress()
    header = _header_block(text)
    tag_authority = _parse_header_field(header, "Closure tag authority")
    assert "does not select or self-assert a Milestone 93 closure tag" in tag_authority
    assert "milestone-92C-rule6-governance-runtime-migration" not in tag_authority
    assert not re.search(r"[0-9a-f]{40}", tag_authority)


def test_current_closure_tag_target_matches_header():
    text = _read_progress()
    header = _header_block(text)
    tag_authority = _parse_header_field(header, "Closure tag authority")
    assert "This ledger does not select or self-assert a Milestone 93 closure tag" in tag_authority
    assert "any such tag requires separate PM authorization and Git verification" in tag_authority
    assert not re.search(r"[0-9a-f]{40}", tag_authority)


def test_implementation_commit_is_ancestor_of_closure_commit():
    text = _read_progress()
    header = _header_block(text)
    closure_authority = _parse_header_field(header, "Closure durability authority")
    tag_authority = _parse_header_field(header, "Closure tag authority")
    previous_tag = _parse_header_field(header, "Previous durable closure tag")
    earlier_tag = _parse_header_field(header, "Earlier accepted closure tag")
    assert "Git directly determines" in closure_authority
    assert "does not self-assert its own closure commit SHA" in closure_authority
    assert "does not select or self-assert a Milestone 93 closure tag" in tag_authority
    assert "milestone-92C-rule6-governance-runtime-migration" in previous_tag
    assert "3641c0c98fad993b1b4b5b8719dbf1cfd7117abc" in previous_tag
    assert "milestone-92B-rule6-governance-migration-boundary" in earlier_tag
    assert "22d819b6bd3a305536c0beba57f670a5433fe21e" in earlier_tag


def test_previous_accepted_closure_tag_is_consistent():
    text = _read_progress()
    header = _header_block(text)
    prev_value = _parse_header_field(header, "Previous durable closure tag")
    earlier_value = _parse_header_field(header, "Earlier accepted closure tag")

    assert "milestone-92C-rule6-governance-runtime-migration" in prev_value, (
        f"Expected milestone-92C tag, got: {prev_value}"
    )
    assert "3641c0c98fad993b1b4b5b8719dbf1cfd7117abc" in prev_value, (
        f"Expected milestone-92C SHA, got: {prev_value}"
    )
    assert "milestone-92B-rule6-governance-migration-boundary" in earlier_value, (
        f"Expected milestone-92B tag, got: {earlier_value}"
    )
    assert "22d819b6bd3a305536c0beba57f670a5433fe21e" in earlier_value, (
        f"Expected milestone-92B SHA, got: {earlier_value}"
    )


def test_historical_archive_boundary():
    text = _read_progress()

    # Verify first --- exists
    lines = text.split("\n")
    first_sep_idx = None
    for i, line in enumerate(lines):
        if line.strip() == "---":
            first_sep_idx = i
            break
    assert first_sep_idx is not None, "No first --- separator found in PROGRESS.md"

    # Verify canonical header before first separator
    header = _header_block(text)
    assert len(header) > 0

    # Verify ## 12. Historical Milestone Archive appears exactly once
    archive_heading = "## 12. Historical Milestone Archive"
    assert text.count(archive_heading) == 1, (
        f"Expected exactly one '{archive_heading}', found {text.count(archive_heading)}"
    )

    # Verify archive heading occurs AFTER the first ---
    archive_idx = text.index(archive_heading)
    assert archive_idx > first_sep_idx, (
        "Historical archive heading must appear after the first --- separator"
    )

    # Verify archive disclaimer exists
    disclaimer = "This section is a historical archive. It does not override the canonical current-state block in the header."
    assert disclaimer in text, "Archive disclaimer text not found"

    # Verify canonical header is parsed independently
    assert header.count(archive_heading) == 0, (
        "Archive heading should not appear in canonical header"
    )


def test_pipeline_maturity_records_current_state():
    text = _read_progress()
    header = _header_block(text)
    maturity = _parse_header_field(header, "Pipeline maturity")

    required_tokens = [
        "Milestone 91B",
        "Rule 5",
        "Governance",
        "finalized",
        "Milestone 91",
        "CLOSED",
        "Milestone 92B finalized",
        "Rule 6 Governance migration boundary committed, tagged, pushed, and remotely verified",
        "Rule 6 Governance Runtime Migration closure state complete",
        "Candidate A-F deferred",
    ]
    for token in required_tokens:
        assert token in maturity, f"Pipeline maturity missing required token: {token}"

    required_durable_suffix = (
        "Milestone 92B finalized; Rule 6 Governance migration boundary committed, "
        "tagged, pushed, and remotely verified; Rule 4, Rule 5, and Rule 6 are "
        "Core Governance-owned; Rule 7 is a Thinking Soft Decision Signal; Rule 6 "
        "Governance Runtime Migration closure state complete; "
        "implementation durable; Milestone 92C CLOSED; Candidate A-F deferred."
    )
    stale_r2_suffix = (
        "Milestone 91B finalized; Rule 5 Governance-only ownership; "
        "Milestone 91 CLOSED; Milestone 92A canonical-ledger reconciliation "
        "and parser repair finalized, committed, tagged, and pushed; "
        "Milestone 92A-R2 post-finalization baseline-lock and ledger correction "
        "COMPLETE locally; uncommitted; untagged; unpushed; not finalized; "
        "pending independent audit/final closure; no known blockers; "
        "Milestone 92 functional capability not started; "
        "Milestone 92B not started; Rule 6 migration not started."
    )

    assert maturity.endswith(required_durable_suffix)
    assert not maturity.endswith(stale_r2_suffix)


def test_full_suite_and_canonical_counts_match_header():
    text = _read_progress()
    header = _header_block(text)
    status = _parse_header_field(header, "Current status")
    baseline = _parse_header_field(header, "Test baseline")
    section7 = text.split("## 7. Current Test Baseline\n", 1)[1].split(
        "\n---\n", 1
    )[0]
    current_section7, historical_section7 = section7.split(
        "HISTORICAL BASELINE PROVENANCE", 1
    )

    for token in (
        "Milestone 94 CLOSED / GIT-DURABLE / PM-ACCEPTED externally",
        "Milestone 95 OPEN",
        "**M95A:** Observation Provenance Source and Consumer-Proof Boundary",
        "**M95A status:** COMPLETE LOCALLY / PENDING PM REVIEW",
        "**M95B:** NOT AUTHORIZED",
        "**Selected model:** MODEL_B_JUSTIFIED",
        "**Current proven durable consumer:** NONE",
        "M95_PROVENANCE_FOUNDATION_REQUIRED_BEFORE_RUNTIME",
        "**Full current result:** 2968/2968 passed, 0 failures, 0 errors",
    ):
        assert token in status or token in current_section7
    for token in (
        "95A design-lock:** 8 passed",
        "M94 closure lock:** 8 passed",
        "Observation regression family:** 472 passed",
        "Rule migration family:** 177 passed",
        "OpenAPI family:** 653 passed",
        "Full current result:** 2968/2968 passed, 0 failures, 0 errors",
    ):
        assert token in current_section7
    assert "Historical full suite:** 2499" in historical_section7
    assert "Historical Progress accounting:** 322" in historical_section7
    assert "M89A-R3 HISTORICAL_BASELINE_ACCOUNTING" in historical_section7
    assert "M92A-R2 HISTORICAL_RECORDED_BASELINE_WITH_SELECTOR_PROVENANCE_NOT_PRESERVED" in historical_section7
    assert "Full candidate: 2952 passed" not in status
    assert "Full candidate: 2952 passed" not in baseline


def test_92a_vs_functional_92_terminology_contract():
    text = _read_progress()
    header = _header_block(text)
    active = _parse_header_field(header, "Current active milestone/module")
    status = _parse_header_field(header, "Current status")
    section10 = text.split("## 10. Next Recommended Milestone\n", 1)[1].split(
        "\n---\n", 1
    )[0]

    assert "Milestone 95A Observation Provenance Source and Consumer-Proof Boundary" in active
    assert "Milestone 94 is CLOSED / GIT-DURABLE / PM-ACCEPTED externally" in active
    assert "Milestone 95 OPEN" in active
    assert "selected model B" in active
    assert "M95B NOT AUTHORIZED" in status
    for token in (
        "MODEL_B_JUSTIFIED",
        "current runtime containment Model E",
        "generic /chat execution authority NO",
        "Observation call-local",
        "no runtime bridge",
        "no Observation Intake caller",
        "no persistent Observation Record",
        "Verification Aggregation",
        "Critic",
        "Repair",
        "Learning",
    ):
        assert token in status

    for token in (
        "Milestone 94 CLOSED / GIT-DURABLE / PM-ACCEPTED externally",
        "Milestone 95 OPEN",
        "Milestone 95A Observation Provenance Source and Consumer-Proof Boundary Build complete locally",
        "M95A status COMPLETE LOCALLY / PENDING PM REVIEW",
        "M95B NOT AUTHORIZED",
        "selected model B",
        "current runtime containment Model E",
        "Observation call-local",
        "No M95B implementation is authorized",
    ):
        assert token in section10
    assert "At the Milestone 92C closure boundary" in section10
    assert "current Rule 4 physical ownership is Core Governance" in section10
    assert "Milestone 94 OPEN" not in "\n".join((active, status, section10))
    assert "Milestone 95" in "\n".join((active, status, section10))

    for stale in (
        "no functional milestone is selected",
        "no functional milestone is started",
        "Milestone 93 not started",
        "Milestone 93A not started",
        "Milestone 93A finalization is not yet committed",
        "commit/tag/push: none",
        "PM authorization is required before finalization",
        "Git finalization is not authorized",
        "not committed",
        "not tagged",
        "not pushed",
    ):
        assert stale not in section10, f"Stale Section 10 phrase found: {stale}"
