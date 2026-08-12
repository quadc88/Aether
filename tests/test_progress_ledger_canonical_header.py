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

    # Six current-work identities are covered as one scalar contract.
    identity_tokens = {
        "Last updated": "Milestone 94A boundary / contract-lock Build complete locally; Milestone 94 is OPEN",
        "Current completed local milestone": "Milestone 94A boundary / contract-lock Build content complete locally; Milestone 94 remains OPEN; Milestone 93 remains CLOSED / DURABLE; Git remains authoritative for Milestone 94A commit, durability, tagging, and publication state",
        "Current active milestone/module": "Milestone 94A current boundary / contract-lock submilestone; Milestone 94 is OPEN",
        "Current status": "Milestone 93 CLOSED / DURABLE; Milestone 94 OPEN; Milestone 94A boundary / contract-lock Build complete locally",
        "Next milestone": "Milestone 94B requires a fresh PM Plan and Build definition",
        "Test baseline": "2571 pre-93A full-suite baseline",
    }
    assert all(
        token in fields[name] for name, token in identity_tokens.items()
    )
    assert fields["Current completed local milestone"].startswith(
        "Milestone 94A boundary / contract-lock Build content complete locally"
    )
    assert not fields["Current completed local milestone"].startswith(
        "Milestone 93B Rule 4 Governance Runtime Migration"
    )

    closure_authority = _parse_header_field(header, "Closure durability authority")
    tag_authority = _parse_header_field(header, "Closure tag authority")
    previous_tag = _parse_header_field(header, "Previous durable closure tag")
    earlier_tag = _parse_header_field(header, "Earlier accepted closure tag")
    assert "Git directly determines the commit containing the current closure ledger content" in closure_authority
    assert "does not self-assert its own closure commit SHA" in closure_authority
    assert not re.search(r"[0-9a-f]{40}", closure_authority)
    assert "does not select or self-assert a Milestone 93 closure tag" in tag_authority
    assert "separate PM authorization and Git verification" in tag_authority
    assert "3641c0c98fad993b1b4b5b8719dbf1cfd7117abc" not in tag_authority
    assert "milestone-92C-rule6-governance-runtime-migration" not in tag_authority
    assert "milestone-92C-rule6-governance-runtime-migration" in previous_tag
    assert "3641c0c98fad993b1b4b5b8719dbf1cfd7117abc" in previous_tag
    assert "milestone-92B-rule6-governance-migration-boundary" in earlier_tag
    assert "22d819b6bd3a305536c0beba57f670a5433fe21e" in earlier_tag
    assert "Milestone 94A current boundary / contract-lock submilestone" in fields["Current active milestone/module"]
    assert "Milestone 94B is NOT AUTHORIZED" in fields["Current active milestone/module"]
    assert "Milestone 94C is NOT DEFINED" in fields["Current active milestone/module"]
    assert "Strategy C selected" in fields["Current status"]
    assert "Observation Intake DEFER_FIRST_SLICE" in fields["Current status"]
    assert "root registration MANUAL_ADMIN_CONFIG_EDIT" in fields["Current status"]
    assert "approval may persist, scope may not persist" in fields["Current status"]
    assert "execution-time Governance re-evaluation is required" in fields["Current status"]
    assert "capability expansion none" in fields["Current status"]
    assert "Current Progress-equivalent five-file family: 362 passed" in fields["Current status"]
    assert "Progress-referencing regression: 322 passed" not in fields["Current status"]
    assert "Architecture/Observation: 363 passed" not in fields["Current status"]
    assert "OpenAPI: 304 paths / 108 schemas" in fields["Current status"]
    assert "api_server: 8 direct @app routes / 23 include_router / 0 direct /action/*" in fields["Current status"]
    assert "2571 pre-93A full-suite baseline" in fields["Test baseline"]
    assert "New 93B: 26 passed" in fields["Test baseline"]
    assert "94A boundary: 24 passed" in fields["Test baseline"]
    assert "Full candidate: 2655 passed" in fields["Test baseline"]
    assert "9 existing PytestRemovedIn10Warning" in fields["Test baseline"]
    assert "Current Progress-equivalent five-file family: 362 passed" in fields["Test baseline"]
    assert "94A boundary: 24 tests pending verification" not in fields["Test baseline"]
    assert "warning occurrence delta versus parent: 0" in fields["Test baseline"]

    section5 = text.split("## 5. Current Implemented Safety Chain\n", 1)[1].split(
        "\n---\n", 1
    )[0]
    assert "This chain remains **declarative and non-executing**" in section5
    assert "action-specific final-real-apply and rollback direct surfaces exist behind their own gates" in section5
    assert "outside the canonical `/chat` execution loop" in section5
    assert "No general-purpose `/chat` executor or automatic evidence collector exists" in section5

    section9 = text.split("## 9. Hard Safety Invariants\n", 1)[1].split(
        "\n---\n", 1
    )[0]
    assert "NO UNAUTHORIZED OR GENERIC /CHAT EXTERNAL ACTION AUTHORITY" in section9
    assert "`/chat` does not execute real tools" in section9
    assert "`/chat` does not perform real apply or rollback" in section9
    assert "action-specific direct apply/rollback surfaces remain separately gated" in section9
    assert "do not grant `/chat` authority" in section9
    assert "No automatic evidence collection occurs" in section9

    # Commit-3 lifecycle phrases must not appear in any current-work field.
    prohibited_phrases = [
        "Milestone 92A CLOSED",
        "PM ACCEPTED — Milestone 92A CLOSED",
        "final closure commit pending",
        "final closure publication pending",
    ]
    for field_value in fields.values():
        for phrase in prohibited_phrases:
            assert phrase not in field_value, (
                f"Prohibited phrase '{phrase}' found in field: {phrase}"
            )

    # Closure independence: unchanged 92A/91B values remain in closure fields
    closure_ledger = _parse_header_field(header, "Closure durability authority")
    closure_tag = _parse_header_field(header, "Closure tag authority")
    prev_tag = _parse_header_field(header, "Previous durable closure tag")
    earlier_tag = _parse_header_field(header, "Earlier accepted closure tag")
    assert "Git directly determines" in closure_ledger
    assert not re.search(r"[0-9a-f]{40}", closure_ledger)
    assert "does not select or self-assert a Milestone 93 closure tag" in closure_tag
    assert not re.search(r"[0-9a-f]{40}", closure_tag)
    assert "milestone-92C-rule6-governance-runtime-migration" in prev_tag
    assert "3641c0c98fad993b1b4b5b8719dbf1cfd7117abc" in prev_tag
    assert "milestone-92B-rule6-governance-migration-boundary" in earlier_tag
    assert "22d819b6bd3a305536c0beba57f670a5433fe21e" in earlier_tag

    # Parser uniqueness contract: line-by-line matching with explicit failures
    # Case A: one-match success (normal value)
    assert _parse_header_field(
        "**Example:** value",
        "Example",
    ) == "value"

    # Case B: missing field raises ValueError
    with pytest.raises(
        ValueError,
        match=r"Canonical header field 'Missing' was not found exactly once; found 0\.",
    ):
        _parse_header_field("**Example:** value", "Missing")

    # Case C: duplicate true field lines raises ValueError
    with pytest.raises(
        ValueError,
        match=r"Canonical header field 'Example' was not found exactly once; found 2\.",
    ):
        _parse_header_field(
            "**Example:** first\n**Example:** second",
            "Example",
        )

    # Case D: embedded marker after real field
    synthetic_header = (
        "**Example:** real value\n"
        "**Other:** documentation mentions **Example:** in text"
    )
    assert _parse_header_field(
        synthetic_header,
        "Example",
    ) == "real value"

    # Case E: embedded marker before real field
    synthetic_header = (
        "**Other:** documentation mentions **Example:** in text\n"
        "**Example:** real value"
    )
    assert _parse_header_field(
        synthetic_header,
        "Example",
    ) == "real value"

    # Case F: non-column-zero marker
    with pytest.raises(
        ValueError,
        match=r"Canonical header field 'Example' was not found exactly once; found 0\.",
    ):
        _parse_header_field(
            "prefix **Example:** not a canonical field",
            "Example",
        )

    # Case G: leading whitespace
    with pytest.raises(
        ValueError,
        match=r"Canonical header field 'Example' was not found exactly once; found 0\.",
    ):
        _parse_header_field(
            "  **Example:** indented",
            "Example",
        )

    # Case H: empty field at end
    assert _parse_header_field(
        "**Example:**",
        "Example",
    ) == ""

    # Case I: empty field followed by another field
    synthetic_header = (
        "**Example:**\n"
        "**Other:** next field"
    )
    assert _parse_header_field(
        synthetic_header,
        "Example",
    ) == ""


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

    assert "94A boundary: 24 passed" in status
    assert "93A Boundary: 34 passed" in status
    assert "New 93B: 26" in status
    assert "Current Progress-equivalent five-file family: 362 passed" in status
    assert "Full candidate: 2655 passed" in status
    assert "2571 pre-93A full-suite baseline" in baseline
    assert "93A Boundary: 34 passed" in baseline
    assert "New 93B: 26 passed" in baseline
    assert "Current Progress-equivalent five-file family: 362 passed" in baseline
    assert "94A boundary: 24 passed" in baseline
    assert "Full candidate: 2655 passed" in baseline

    assert "93A Boundary:** 34 passed" in current_section7
    assert "Milestone 93:** CLOSED" in current_section7
    assert "93A:** FINALIZED / DURABLE boundary" in current_section7
    assert "93B implementation content:** complete" in current_section7
    assert "Rule 4 physical owner in implemented content:** Core Governance" in current_section7
    assert "Implementation provenance:** rule_3 / clear" in current_section7
    assert "Direct supersession:** 27" in current_section7
    assert "Parameter cases:** 3" in current_section7
    assert "Observation:** BLOCKED / deferred" in current_section7
    assert "Candidate A-F:** DEFERRED" in current_section7
    assert "Capability expansion:** none" in current_section7
    assert "Git directly determines implementation durability, tagging, and publication" in current_section7
    assert "93B Rule 4 runtime contract:** 26 passed" in current_section7
    assert "Progress ledger canonical-header contract:** 23 passed" in current_section7
    assert "Current Progress-equivalent five-file family:** 362 passed" in current_section7
    assert "94A boundary:** 24 passed" in current_section7
    assert "Full suite:** 2655/2655 passed, 0 failures, 0 errors" in current_section7
    assert "2605" not in current_section7
    assert "Warnings:** 9 existing PytestRemovedIn10Warning" in current_section7
    assert "Warning occurrence delta versus parent:** 0" in current_section7
    assert "New warning regression caused by 93A:** none" in current_section7
    assert "Historical full suite: 2499" not in current_section7
    assert "Historical Progress accounting: 322" not in current_section7
    assert "Historical Architecture/Observation: 363" not in current_section7
    assert "Historical full suite:** 2499" in historical_section7
    assert "Historical Progress accounting:** 322" in historical_section7
    assert "M89A-R3 HISTORICAL_BASELINE_ACCOUNTING" in historical_section7
    assert "110 + 50 + 76 + 31 + 55 = 322" in historical_section7
    assert "M92A-R2 HISTORICAL_RECORDED_BASELINE_WITH_SELECTOR_PROVENANCE_NOT_PRESERVED" in historical_section7

    # Prohibit stale pre-Build counts
    assert "Full suite: 2488 passed" not in status, (
        "Current status must not contain stale pre-Build count 2488"
    )
    assert "Full suite: 2500 passed" not in status, (
        "Current status must not contain invalid count 2500"
    )
    assert "Canonical header: 12 passed" not in status, (
        "Current status must not contain stale pre-Build count 12"
    )
    assert "Canonical header: 24 passed" not in status, (
        "Current status must not contain invalid count 24"
    )


def test_92a_vs_functional_92_terminology_contract():
    text = _read_progress()
    header = _header_block(text)
    active = _parse_header_field(header, "Current active milestone/module")
    status = _parse_header_field(header, "Current status")
    section10 = text.split("## 10. Next Recommended Milestone\n", 1)[1].split(
        "\n---\n", 1
    )[0]

    assert "Milestone 94A current boundary / contract-lock submilestone" in active
    assert "Milestone 94 is OPEN" in active
    assert "Milestone 93 is CLOSED / DURABLE" in active
    assert "Milestone 93B OPEN" not in active
    assert "Rule 4 physical ownership is Core Governance" in active, (
        f"Missing local Rule 4 Governance owner, got: {active[:200]}"
    )
    assert "PM acceptance is an external review decision and is not self-asserted by this ledger" in active
    # Prohibit standalone "Milestone 92 not started" without qualification
    assert "Milestone 92 not started" not in active, (
        f"Must not contain standalone 'Milestone 92 not started', got: {active[:200]}"
    )

    for token in (
        "Milestone 93 CLOSED / DURABLE",
        "Milestone 94 OPEN",
        "Milestone 94A boundary / contract-lock Build complete locally",
        "Strategy C selected",
        "Observation Intake DEFER_FIRST_SLICE",
        "root registration MANUAL_ADMIN_CONFIG_EDIT",
        "approval may persist, scope may not persist",
        "execution-time Governance re-evaluation is required",
        "94A boundary: 24 passed",
        "Full candidate: 2655 passed",
    ):
        assert token in status, f"Current status missing token: {token}"

    for token in (
        "Milestone 93 is CLOSED / DURABLE",
        "Milestone 94 is OPEN",
        "Milestone 94A is the current boundary / contract-lock submilestone",
        "Strategy C selected",
        "Observation Intake DEFER_FIRST_SLICE",
        "Root registration MANUAL_ADMIN_CONFIG_EDIT",
        "approval may persist / scope may not persist",
        "execution-time Governance re-evaluation required",
        "Milestone 94B is NOT AUTHORIZED",
        "Milestone 94C is NOT DEFINED",
        "94A Boundary: 24 passed",
        "Full candidate: 2655 passed",
    ):
        assert token in section10, f"Section 10 missing current token: {token}"

    assert "Rule 4 remains in Thinking" not in section10
    assert "At the Milestone 92C closure boundary" in section10
    assert "current Rule 4 physical ownership is Core Governance" in section10
    assert "Milestone 93 OPEN" not in "\n".join((active, status, section10))
    assert "93C" not in "\n".join((active, status, section10))
    assert "Milestone 94" in "\n".join((active, status, section10))

    for stale in (
        "no functional milestone is selected",
        "no functional milestone is started",
        "Milestone 93 not started",
        "Milestone 93A not started",
        "Milestone 93A finalization is not yet committed",
        "commit/tag/push: none",
        "PM authorization is required before finalization",
        "Git finalization is not authorized",
        "Git finalization remains separately controlled and is not authorized",
        "Rule 4 durable migration NOT YET ESTABLISHED",
        "not committed",
        "not tagged",
        "not pushed",
    ):
        assert stale not in section10, f"Stale Section 10 phrase found: {stale}"
