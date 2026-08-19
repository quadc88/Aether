"""Static/document locks for the M99A ThinkingProposal producer proof."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / (
    "docs/architecture/"
    "MILESTONE_99A_THINKINGPROPOSAL_PRODUCTION_COMPATIBILITY_PRODUCER_PROOF_BOUNDARY.md"
)
POLICY = ROOT / "aether/thinking/policy.py"
LOOP = ROOT / "aether/core/loop.py"


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_m99a_record_has_read_only_status_and_selected_negative_decision():
    text = _text(RECORD)
    required = (
        "# Milestone 99A ThinkingProposal Production Compatibility Producer Proof Boundary",
        "STRICT READ-ONLY DESIGN / DISCOVERY / PRODUCER-PROOF",
        "COMPLETE LOCALLY / GIT DURABILITY NOT CLAIMED / PM ACCEPTANCE EXTERNAL",
        "a1b716748dcf7e45a263fed93da427c54cfcda75",
        "306 paths / 112 schemas",
        "8 direct @app routes / 23 include_router / 0 direct /action/*",
        "D_NO_TRUTHFUL_PRODUCTION_THINKINGPROPOSAL_PRODUCER_CURRENTLY_JUSTIFIED",
        "MODEL_D_NO_PRODUCTION_THINKINGPROPOSAL_PRODUCER_YET",
        "Current production ThinkingProposal producer: ABSENT",
        "Runtime producer implementation: NOT AUTHORIZED",
    )
    for marker in required:
        assert marker in text, marker


def test_required_contract_semantics_and_non_fabrication_are_locked():
    text = _text(RECORD)
    required = (
        "distinct `proposal_id`, positive `proposal_revision`, proposal `created_at`",
        "`goal_id`, `task_id`, `task_context_id`, current `task_context_revision`",
        "`PROPOSAL_READY` or `PROPOSAL_NOT_READY`",
        "explicit non-empty `proposed_objective`",
        "explicit non-empty completion, failure, and blocked criteria",
        "complete structured provenance envelope",
        "structured `not_ready_reason`",
        "`decision_type` cannot be substituted for `proposal_state`",
        "normalized user text is not an authorized objective mapping",
        "session, trace, approval, request, timestamp, tool, or text identifiers",
        "No policy dictionary is a `ThinkingProposal` by name similarity.",
        "Clarification remains a policy/workflow result",
        "GOVERNANCE_EVALUATION !=\n   EXECUTION_AUTHORIZATION",
    )
    for marker in required:
        assert marker in text, marker


def test_candidate_models_and_scope_freeze_are_locked():
    text = _text(RECORD)
    required = (
        "MODEL_A_LEGACY_POLICY_TO_PROPOSAL_ADAPTER",
        "MODEL_B_CORE_LOOP_THINKINGPROPOSAL_PRODUCER",
        "MODEL_C_COORDINATION_BOUND_PROPOSAL_PROVIDER",
        "MODEL_D_NO_PRODUCTION_THINKINGPROPOSAL_PRODUCER_YET",
        "Legacy policy adapter: REJECTED",
        "Core-loop producer: REJECTED",
        "Coordination-bound provider: NOT JUSTIFIED",
        "a ThinkingProposal producer, adapter, provider, or factory",
        "`PROGRESS.md`, README, Constitution, Architecture, production code",
        "MILESTONE_99A_THINKINGPROPOSAL_PRODUCTION_COMPATIBILITY_PRODUCER_PROOF_BOUNDARY.md",
        "test_milestone_99a_thinkingproposal_production_compatibility_producer_proof_boundary.py",
        "/home/aether/summaries/milestone_99A_producer_proof_summary.txt",
    )
    for marker in required:
        assert marker in text, marker


def test_current_policy_is_a_dictionary_producer_not_a_thinkingproposal_producer():
    source = _text(POLICY)
    assert "def _evaluate_chat_policy_with_precedence(" in source
    assert '"decision_type": "ask_clarification"' in source
    assert '"decision_type": "suggest_tool"' in source
    assert '"decision_type": "respond_only"' in source
    assert "ThinkingProposal" not in source
    assert "proposed_completion_criteria" not in source
    assert "proposed_failure_criteria" not in source
    assert "proposed_blocked_criteria" not in source


def test_current_loop_has_no_production_proposal_wiring():
    source = _text(LOOP)
    assert "raw_thinking_policy, rule_3_4_precedence = _evaluate_chat_policy_with_precedence" in source
    assert "ThinkingProposal" not in source
    assert "materialize_thinking_proposal" not in source
    assert "create_task" not in source
    assert "select_context" not in source
    assert "proposed_objective" not in source
    assert "proposed_completion_criteria" not in source


def test_record_preserves_existing_consumer_and_act_boundaries():
    text = _text(RECORD)
    required = (
        "Core Coordination process-local consumer: SATISFIED",
        "External canonical runtime consumer: NOT YET SATISFIED",
        "Core Coordination must fail closed",
        "A proposal, even if later produced, remains non-authoritative",
        "Generic Act: NOT_IMPLEMENTED",
        "Generic Act integration: NOT_AUTHORIZED",
        "Generic Act authority: NOT_GRANTED",
    )
    for marker in required:
        assert marker in text, marker
