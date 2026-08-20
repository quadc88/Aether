"""Static/document lock for the M110A producer re-entry proof boundary."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / (
    "docs/architecture/"
    "MILESTONE_110A_THINKINGPROPOSAL_PRODUCTION_PRODUCER_REENTRY_PROOF_BOUNDARY.md"
)


def _text() -> str:
    return RECORD.read_text(encoding="utf-8")


def test_m110a_selected_negative_producer_boundary_is_locked():
    text = " ".join(_text().split())
    required = (
        "# Milestone 110A ThinkingProposal Production Producer Re-entry Proof Boundary",
        "STRICT READ-ONLY CORE-ARCHITECTURE / PRODUCTION-PRODUCER-PROOF",
        "c3e70887969afb19892e0b31c0a5cff4a4d3b336",
        "MODEL_D_NO_MEANINGFUL_PRODUCER_CHANGE_SINCE_M99A",
        "P2_LEGACY_OR_NONCANONICAL_PRODUCTION_OUTPUT",
        "A1_ADAPTER_WOULD_FABRICATE_SEMANTICS",
        "D_NO_TRUTHFUL_PRODUCTION_PRODUCER_CURRENTLY_JUSTIFIED",
        "CONCRETE_PRODUCER_USE_CASE_AND_AUTHORITATIVE_CONTEXT_HANDOFF_PROOF",
        "Future Build: NOT JUSTIFIED",
        "M99A substantive result:",
        "UNCHANGED",
        "MATERIALIZATION_SEAM: PRESENT",
        "PRODUCTION_PRODUCER: ABSENT",
        "External canonical runtime consumer: ABSENT",
        "Durable/async canonical consumer: ABSENT",
        "Selected PlanStep external runtime consumer: ABSENT",
    )
    for marker in required:
        assert marker in text, marker


def test_m110a_preserves_non_authorization_and_patch_pause_boundaries():
    text = _text()
    required = (
        "THINKING_PROPOSAL != EXECUTION_AUTHORIZATION",
        "GOVERNANCE_EVALUATION != EXECUTION_AUTHORIZATION",
        "Generic Act: NOT_IMPLEMENTED",
        "Generic Act integration: NOT_AUTHORIZED",
        "Generic Act authority: NOT_GRANTED",
        "Patch security: PAUSED",
        "M105B F03: RESOLVED",
        "M107B F02 final-workflow: ADDRESSED",
        "a ThinkingProposal production producer",
        "a policy-to-proposal adapter",
        "Goal-to-Plan runtime consumption",
        "commit, tag, or push",
    )
    for marker in required:
        assert marker in text, marker


def test_m110a_candidate_models_do_not_select_a_positive_build():
    text = _text()
    required = (
        "MODEL_A_TRUTHFUL_PRODUCTION_PRODUCER_NOW_EXISTS",
        "MODEL_B_BOUNDED_TRUTHFUL_ADAPTER_BUILD_JUSTIFIED",
        "MODEL_C_PRODUCTION_SEAM_EXISTS_BUT_SEMANTICS_INCOMPLETE",
        "MODEL_D_NO_MEANINGFUL_PRODUCER_CHANGE_SINCE_M99A",
        "MODEL_E_PRODUCER_EVIDENCE_INSUFFICIENT",
        "Adapter Build: NOT JUSTIFIED",
        "No adapter scope is selected.",
        "Next authorized action: HUMAN/PROJECT-MANAGER M110A PRODUCER-PROOF REVIEW",
    )
    for marker in required:
        assert marker in text, marker

    forbidden = (
        "MODEL_A_TRUTHFUL_PRODUCTION_PRODUCER_NOW_EXISTS` | SELECTED",
        "MODEL_B_BOUNDED_TRUTHFUL_ADAPTER_BUILD_JUSTIFIED` | SELECTED",
        "Future Build: JUSTIFIED FOR PM REVIEW",
        "PRODUCTION_PRODUCER: PROVEN",
        "Generic Act: IMPLEMENTED",
        "PROGRESS.md updated",
    )
    for marker in forbidden:
        assert marker not in text, marker
