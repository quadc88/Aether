"""Static/document lock for the M111A authoritative handoff proof."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / (
    "docs/architecture/"
    "MILESTONE_111A_CONCRETE_PRODUCER_USE_CASE_AUTHORITATIVE_CONTEXT_HANDOFF_PROOF.md"
)


def _text() -> str:
    return RECORD.read_text(encoding="utf-8")


def test_m111a_selected_handoff_model_is_locked():
    text = " ".join(_text().split())
    required = (
        "# Milestone 111A Concrete Producer Use Case and Authoritative Context Handoff Proof",
        "MODEL_B_PROCESS_LOCAL_HANDOFF_PROVEN_BUT_RUNTIME_CALLER_MISSING",
        "B_RUNTIME_ENTRY_TO_AUTHORITATIVE_CONTEXT_PROOF_REQUIRED_NEXT",
        "CORE_COORDINATION_PROCESS_LOCAL_AUTHORITATIVE_CONTEXT_HANDOFF_SEAM",
        "H3_AUTHORITATIVE_PROCESS_LOCAL_HANDOFF_PROVEN",
        "R2_PARTIAL_TRUTHFUL_CONTEXT_AVAILABLE",
        "External canonical runtime consumer: ABSENT",
        "Durable/async consumer: ABSENT",
        "Selected PlanStep external consumer: ABSENT",
    )
    for marker in required:
        assert marker in text, marker


def test_m111a_preserves_non_authorization_and_security_boundaries():
    text = _text()
    required = (
        "THINKING_PROPOSAL != EXECUTION_AUTHORIZATION",
        "GOVERNANCE_EVALUATION != EXECUTION_AUTHORIZATION",
        "Generic Act: NOT_IMPLEMENTED",
        "Generic Act integration: NOT_AUTHORIZED",
        "Generic Act authority: NOT_GRANTED",
        "Patch security: PAUSED",
        "No producer Build or adapter is recommended.",
        "No implementation contract is authorized.",
        "commit, tag, push, or PM acceptance claims",
        "Next authorized action: HUMAN/PROJECT-MANAGER M111A HANDOFF-PROOF REVIEW",
    )
    for marker in required:
        assert marker in text, marker


def test_m111a_locks_negative_runtime_and_implementation_status():
    text = _text()
    required = (
        "Concrete production use case: NOT PROVEN",
        "Real production caller: NOT PROVEN",
        "Authoritative context handoff: PROVEN process-locally only",
        "ThinkingProposal input semantics sufficient: NO",
        "Fabrication required: YES for any current producer attempt",
        "Future Build: NOT JUSTIFIED",
        "a ThinkingProposal producer, adapter, provider, factory, model, or inference runtime",
        "Goal-to-Plan runtime consumption or an external consumer",
        "persistence, restart restoration, worker, scheduler, queue, event, or async integration",
    )
    for marker in required:
        assert marker in text, marker

    forbidden = (
        "MODEL_A_CONCRETE_AUTHORITATIVE_HANDOFF_NOW_PROVEN` | SELECTED",
        "H4_AUTHORITATIVE_RUNTIME_HANDOFF_PROVEN",
        "R3_TRUTHFUL_AUTHORITATIVE_CONTEXT_HANDOFF_PROVEN",
        "Concrete production use case: PROVEN",
        "Real production caller: PROVEN",
        "Future Build: JUSTIFIED FOR PM REVIEW",
        "Generic Act: IMPLEMENTED",
    )
    for marker in forbidden:
        assert marker not in text, marker
