"""
Milestone 90B-R1-R — Canonical Header Singleton-Field Contract Tests

This test module enforces the canonical current-state header contract for
PROGRESS.md. It validates that each authorized header field occurs exactly
once and that obsolete fields are absent from the canonical header.

The canonical header is defined as the beginning of PROGRESS.md through the
first horizontal section separator before Section 1.

Historical archive content is outside this singleton-field contract.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROGRESS = ROOT / "PROGRESS.md"


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
