"""Static/document lock for the M102A consumer-proof decision."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / (
    "docs/architecture/"
    "MILESTONE_102A_NEXT_ACTION_CAPABILITY_AUTHORITY_CONSUMER_PROOF_BOUNDARY.md"
)


def _text() -> str:
    return RECORD.read_text(encoding="utf-8")


def test_m102a_no_second_capability_decision_is_locked():
    text = _text()
    required = (
        "# Milestone 102A Next Action Capability Authority Consumer-Proof Boundary",
        "STRICT READ-ONLY DISCOVERY / CONSUMER-PROOF BOUNDARY",
        "M101B Durable Baseline",
        "file.restricted_read",
        "RestrictedReadAuthorityBinding",
        "Number of qualifying real second-capability candidates: `0`.",
        "Selected capability:\n\n```text\nNONE",
        "D_NO_SECOND_CAPABILITY_CURRENTLY_JUSTIFIED",
        "MODEL_E_NO_SECOND_BUILD_YET",
    )
    for marker in required:
        assert marker in text, marker


def test_m102a_generic_act_and_shared_abstraction_remain_locked_out():
    text = _text()
    required = (
        "Generic Act: `NOT_IMPLEMENTED`",
        "Generic Act integration: `NOT_AUTHORIZED`",
        "Generic Act authority: `NOT_GRANTED`",
        "Generic abstraction pressure: `NOT PROVEN`.",
        "No generic authority registry,",
        "Generic Act, or shared Action abstraction is authorized or implemented.",
        "create a shared Action authority registry or Generic Act",
    )
    for marker in required:
        assert marker in text, marker


def test_m102a_candidate_classifications_and_non_goals_are_locked():
    text = _text()
    required = (
        "KEEP_SEPARATE",
        "LEGACY_QUARANTINE_JUSTIFIED",
        "KEEP_CURRENT_ACTION_SPECIFIC_MODEL",
        "CAND-01",
        "CAND-06",
        "Decision: no durable Observation reopening",
        "M102A authorizes only these two untracked candidates",
        "does not:\n\n- implement a second capability binding",
        "commit, tag, push, or claim PM acceptance",
        "M102, M103, or a successor Build",
    )
    for marker in required:
        assert marker in text, marker


def test_m102a_next_gate_is_human_review_only():
    text = _text()
    required = (
        "M102A discovery: COMPLETE LOCALLY",
        "Second capability Build authorization: NOT GRANTED",
        "Next authorized action: HUMAN/PROJECT-MANAGER M102A CONSUMER-PROOF REVIEW",
        "No second capability binding is authorized.",
        "No shared Action authority is authorized.",
    )
    for marker in required:
        assert marker in text, marker
