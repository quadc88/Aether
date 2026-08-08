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
    assert header.count("**Current closure ledger:**") == 1


def test_header_has_one_current_closure_tag_field():
    text = _read_progress()
    header = _header_block(text)
    assert header.count("**Current closure tag:**") == 1


def test_header_has_one_previous_accepted_closure_tag_field():
    text = _read_progress()
    header = _header_block(text)
    assert header.count("**Previous accepted closure tag:**") == 1


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
        "Last updated": "Milestone 92A-R2",
        "Current completed local milestone": "Milestone 92A-R2",
        "Current active milestone/module": "R2 closure identity",
        "Current status": "R2 implementation commit",
        "Next milestone": "Milestone 92A-R2",
        "Test baseline": "R2 implementation commit",
    }
    assert all(
        token in fields[name] for name, token in identity_tokens.items()
    )

    assert "1c7dc6038a8ac0dd50f431d84983d3421fae5ff6" in _parse_header_field(header, "Current closure ledger")
    assert "1c7dc6038a8ac0dd50f431d84983d3421fae5ff6" in _parse_header_field(header, "Current closure tag")
    assert "milestone-92A-R2-baseline-lock-reconciliation" in _parse_header_field(header, "Current closure tag")
    assert "Stage-3 implementation/tag remote verification complete" in fields["Current active milestone/module"]
    assert "current closure is R2" in fields["Current status"]
    assert "previous accepted closure is original 92A" in fields["Current status"]
    assert "independent audit: PASS" in fields["Current status"]
    assert "Full suite: 2499 passed" in fields["Current status"]
    assert "Canonical header: 23 passed" in fields["Current status"]
    assert "Progress-referencing regression: 322 passed" in fields["Current status"]
    assert "Architecture/Observation: 363 passed" in fields["Current status"]
    assert "OpenAPI: 304 paths / 108 schemas" in fields["Current status"]
    assert "api_server: 8 direct @app routes / 23 include_router / 0 direct /action/*" in fields["Current status"]
    assert "no production/API/persistence/execution change" in fields["Current status"]
    assert "PM closure acceptance is external and not represented by this repository closure record" in fields["Current status"]
    assert "functional Milestone 92 not started" in fields["Current status"]
    assert "Milestone 92B not started" in fields["Current status"]
    assert "Rule 6 migration not started" in fields["Current status"]
    assert "milestone_92A_R2_finalization_summary.txt" in fields["Test baseline"]
    assert "Publish and verify the Milestone 92A-R2 repository closure record" in fields["Next milestone"]
    assert "human/project-manager closure acceptance" in fields["Next milestone"]
    assert "mandatory four-core-file read and Git verification before any functional Milestone 92 selection" in fields["Next milestone"]

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
    closure_ledger = _parse_header_field(header, "Current closure ledger")
    closure_tag = _parse_header_field(header, "Current closure tag")

    prev_tag = _parse_header_field(header, "Previous accepted closure tag")

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
    ledger_value = _parse_header_field(header, "Current closure ledger")

    # Extract SHA from field value
    match = re.search(r'[0-9a-f]{40}', ledger_value)
    assert match is not None, (
        f"No 40-char hex SHA found in Current closure ledger: {ledger_value}"
    )
    sha = match.group(0)

    # Verify exactly one match
    assert len(re.findall(r'[0-9a-f]{40}', ledger_value)) == 1, (
        "Expected exactly one 40-char hex SHA in Current closure ledger"
    )

    # Verify commit object exists
    result = _run_git(["git", "cat-file", "-e", f"{sha}^{{commit}}"])
    assert result.returncode == 0, (
        f"Commit object {sha} does not exist: {result.stderr}"
    )


def test_current_closure_ledger_is_ancestor_of_head():
    text = _read_progress()
    header = _header_block(text)
    ledger_value = _parse_header_field(header, "Current closure ledger")
    match = re.search(r'[0-9a-f]{40}', ledger_value)
    assert match is not None, "No SHA found in Current closure ledger"
    sha = match.group(0)

    result = _run_git(["git", "merge-base", "--is-ancestor", sha, "HEAD"])
    assert result.returncode == 0, (
        f"Closure ledger commit {sha} is not an ancestor of HEAD"
    )


def test_current_closure_tag_name_and_resolves():
    text = _read_progress()
    header = _header_block(text)
    tag_value = _parse_header_field(header, "Current closure tag")

    # Extract tag name from backticks
    match = re.search(r'`([^`]+)`', tag_value)
    assert match is not None, f"No tag name found in Current closure tag: {tag_value}"
    tag_name = match.group(1)
    assert tag_name == "milestone-92A-R2-baseline-lock-reconciliation", (
        f"Expected milestone-92A-R2-baseline-lock-reconciliation, got {tag_name}"
    )

    # Verify tag resolves locally
    result = _run_git(["git", "rev-list", "-n", "1", tag_name])
    assert result.returncode == 0, (
        f"Tag {tag_name} does not resolve locally: {result.stderr}"
    )


def test_current_closure_tag_target_matches_header():
    text = _read_progress()
    header = _header_block(text)
    tag_value = _parse_header_field(header, "Current closure tag")

    # Extract tag name and target SHA
    tag_match = re.search(r'`([^`]+)`', tag_value)
    assert tag_match is not None, "No tag name in Current closure tag"
    tag_name = tag_match.group(1)

    target_match = re.search(r'[0-9a-f]{40}', tag_value)
    assert target_match is not None, "No target SHA in Current closure tag"
    header_target = target_match.group(0)

    # Resolve tag target via git
    result = _run_git(["git", "rev-list", "-n", "1", tag_name])
    assert result.returncode == 0, f"Tag {tag_name} does not resolve"
    resolved_target = result.stdout.strip()

    assert resolved_target == header_target, (
        f"Tag target mismatch: resolved={resolved_target}, header={header_target}"
    )


def test_implementation_commit_is_ancestor_of_closure_commit():
    text = _read_progress()
    header = _header_block(text)

    # Parse implementation tag target from Current closure tag
    tag_value = _parse_header_field(header, "Current closure tag")
    target_match = re.search(r'[0-9a-f]{40}', tag_value)
    assert target_match is not None, "No target SHA in Current closure tag"
    impl_commit = target_match.group(0)

    # Parse closure ledger SHA from Current closure ledger
    ledger_value = _parse_header_field(header, "Current closure ledger")
    ledger_match = re.search(r'[0-9a-f]{40}', ledger_value)
    assert ledger_match is not None, "No SHA in Current closure ledger"
    closure_sha = ledger_match.group(0)

    # Verify implementation commit is ancestor of closure commit
    result = _run_git(["git", "merge-base", "--is-ancestor", impl_commit, closure_sha])
    assert result.returncode == 0, (
        f"Implementation commit {impl_commit} is not an ancestor of closure commit {closure_sha}"
    )


def test_previous_closure_tag_is_92a():
    text = _read_progress()
    header = _header_block(text)
    prev_value = _parse_header_field(header, "Previous accepted closure tag")

    assert "milestone-92A-canonical-ledger-reconciliation" in prev_value, (
        f"Expected milestone-92A tag, got: {prev_value}"
    )
    assert "19fc589ae07c2d3bedc659556621bf83274026b7" in prev_value, (
        f"Expected 92A SHA, got: {prev_value}"
    )
    assert "milestone-91B-rule5-governance-migration" not in prev_value, (
        f"Should not contain older 91B tag, got: {prev_value}"
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
        "Milestone 92A",
        "Milestone 92 functional capability not started",
        "Milestone 92B not started",
    ]
    for token in required_tokens:
        assert token in maturity, f"Pipeline maturity missing required token: {token}"


def test_full_suite_and_canonical_counts_match_header():
    text = _read_progress()
    header = _header_block(text)

    status = _parse_header_field(header, "Current status")
    baseline = _parse_header_field(header, "Test baseline")

    # Current status must contain post-Build counts
    assert "Full suite: 2499 passed" in status, (
        f"Current status missing 'Full suite: 2499 passed': {status[:200]}"
    )
    assert "Canonical header: 23 passed" in status, (
        f"Current status missing 'Canonical header: 23 passed': {status[:200]}"
    )

    # Test baseline must contain post-Build counts
    assert "Full suite: 2499 passed" in baseline, (
        f"Test baseline missing 'Full suite: 2499 passed': {baseline[:200]}"
    )
    assert "Canonical header: 23 passed" in baseline, (
        f"Test baseline missing 'Canonical header: 23 passed': {baseline[:200]}"
    )

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

    assert "R2 closure identity is the current accepted implementation/tag" in active, (
        f"Missing R2 closure identity, got: {active[:200]}"
    )
    assert "Milestone 92 functional capability not started" in active, (
        f"Missing functional 92 not started, got: {active[:200]}"
    )
    assert "Milestone 92B not started" in active, (
        f"Missing 92B not started, got: {active[:200]}"
    )
    assert "Rule 6 migration not started" in active, (
        f"Missing Rule 6 migration not started, got: {active[:200]}"
    )
    # Prohibit standalone "Milestone 92 not started" without qualification
    assert "Milestone 92 not started" not in active, (
        f"Must not contain standalone 'Milestone 92 not started', got: {active[:200]}"
    )
