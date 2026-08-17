"""Static/document-content locks for the M96E proposal contract boundary."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / "docs/architecture/MILESTONE_96E_STRUCTURED_THINKING_PROPOSAL_CONTRACT_BOUNDARY.md"


def _text() -> str:
    return RECORD.read_text(encoding="utf-8")


def test_title_classification_and_no_runtime_status_are_exact():
    text = _text()
    assert text.startswith("# Milestone 96E Structured Thinking Proposal Contract Boundary")
    assert "Classification: DESIGN / SEMANTIC CONTRACT BOUNDARY" in text
    assert "NO RUNTIME IMPLEMENTATION" in text
    assert "CONTRACT CONTENT ESTABLISHED LOCALLY / GIT LIFECYCLE EXTERNAL / PM ACCEPTANCE EXTERNAL" in text
    for marker in (
        "M96E CONTRACT CONTENT ESTABLISHED LOCALLY",
        "NO RUNTIME THINKINGPROPOSAL IMPLEMENTATION",
        "THINK -> PLAN CONSUMER NOT YET SATISFIED",
        "GOVERNANCE-BEFORE-GENERIC-ACT NOT YET SATISFIED",
        "M96 OPEN",
        "GIT LIFECYCLE EXTERNAL",
        "PM ACCEPTANCE EXTERNAL",
    ):
        assert marker in text
    for stale in (
        "PENDING PM REVIEW / GIT FINALIZATION",
        "PENDING HUMAN/PROJECT-MANAGER REVIEW",
        "NO COMMIT",
        "NO TAG",
        "NO PUSH",
    ):
        assert stale not in text


def test_selected_model_and_thinking_ownership_are_locked():
    text = _text()
    assert "MODEL B-S — STRUCTURED IMMUTABLE THINKING PROPOSAL WITH AUTHORITATIVE CONTEXT BINDING" in text
    assert "The conceptual object is `ThinkingProposal`." in text
    assert "Thinking owns proposal semantics and proposal content." in text
    assert "Thinking does not own" in text


def test_proposal_identity_revision_and_non_aliasing_are_locked():
    text = _text()
    for marker in (
        "proposal_id",
        "proposal_revision",
        "created_at",
        "proposal_id != goal_id != task_id != task_context_id != plan_id != plan_step_id",
        "proposal_id != session_id != trace_id != approval_id",
        "`proposal_revision` is not a TaskContext revision",
        "`created_at` is proposal creation time, not",
    ):
        assert marker in text


def test_authoritative_goal_task_context_binding_is_locked():
    text = _text()
    for marker in (
        "goal_id",
        "task_id",
        "task_context_id",
        "task_context_revision",
        "TaskContext was explicitly selected for the reasoning turn",
        "the supplied TaskContext revision is current for the handoff",
        "must not be derived from",
        "session_id",
        "`trace_id` or `loop_trace`",
        "approval_id",
    ):
        assert marker in text


def test_proposed_criteria_remain_distinct_from_canonical_criteria():
    text = _text()
    for marker in (
        "proposed_completion_criteria",
        "proposed_failure_criteria",
        "proposed_blocked_criteria",
        "Thinking may propose criteria. Thinking does not make criteria authoritative.",
        "canonical Plan stage remains the sole authority",
        "ThinkingProposal is not",
    ):
        assert marker in text


def test_criteria_non_fabrication_sources_are_explicitly_excluded():
    text = _text()
    for marker in (
        "Goal.requested_outcome",
        "Goal.goal_constraints",
        "Task.task_scope",
        "Task.task_constraints",
        "TaskContext.completion_criteria_reference",
        "Thinking `reasons`",
        "Thinking `next_step`",
        "Thinking `warnings`",
        "Thinking `blocked_reason`",
        "Governance `reason`",
        "response_text",
        "normalized user text",
        "prose fallback",
        "fabricated",
    ):
        assert marker in text


def test_structured_provenance_categories_and_non_authority_are_locked():
    text = _text()
    for marker in (
        "Structured Provenance",
        "Human / Goal authority",
        "Goal source",
        "Task source",
        "TaskContext source",
        "Thinking reasoning/proposal source",
        "Verification / risk evidence",
        "tool-suggestion evidence",
        "Time context",
        "Provenance may",
        "structured evidence, not authorization",
        "`loop_trace` is not proposal provenance identity",
    ):
        assert marker in text


def test_constraint_ownership_and_conflict_behavior_are_locked():
    text = _text()
    for marker in (
        "Goal constraints remain owned by Goal Intake under Human Authority",
        "constraints remain owned by Core Coordination",
        "rewrite them silently",
        "discard them silently",
        "change their precedence silently",
        "merge metadata into them as equal authority",
        "Conflicting constraints require a non-fabricating proposal failure state",
    ):
        assert marker in text


def test_ready_and_not_ready_outcomes_and_structured_reasons_are_locked():
    text = _text()
    for marker in (
        "PROPOSAL_READY",
        "PROPOSAL_NOT_READY",
        "structured `not_ready_reason`",
        "missing_selected_task_context",
        "stale_task_context_revision",
        "missing_proposed_completion_criteria",
        "missing_proposed_failure_criteria",
        "missing_proposed_blocked_criteria",
        "clarification_required",
        "insufficient_user_intent",
        "conflicting_constraints",
        "unsupported_provenance",
        "invalid_authoritative_binding",
        "No canonical Plan may be created when proposal state is `PROPOSAL_NOT_READY`",
    ):
        assert marker in text


def test_clarification_and_cannot_plan_are_not_plan_semantics():
    text = _text()
    for marker in (
        "ask_clarification",
        "clarification_question",
        "next_step",
        "distinct from all of the following",
        "canonical Plan ready",
        "Plan blocked",
        "Governance denied",
        "execution blocked",
        "Clarification does not materialize",
        "must not be only arbitrary response prose",
    ):
        assert marker in text


def test_action_and_tool_relations_do_not_authorize_execution():
    text = _text()
    for marker in (
        "requested_action_relation",
        "tool_suggestion_relation",
        "Action-attempt identity",
        "PlanStep identity",
        "Plan readiness",
        "or execution",
        "Thinking proposes. Core Coordination materializes canonical planning state.",
        "Action executes",
    ):
        assert marker in text


def test_core_coordination_materialization_boundary_is_locked():
    text = _text()
    for marker in (
        "Core Coordination validates binding, freshness, and explicit supported fields",
        "materializes canonical Plan and PlanStep state",
        "fails closed",
        "does not become a semantic reasoner",
        "may not invent missing",
        "Canonical Plan identity and lifecycle",
        "Canonical Plan criteria",
    ):
        assert marker in text


def test_governance_before_act_separation_is_locked():
    text = _text()
    for marker in (
        "Milestone 96E does not modify Core Governance runtime",
        "Plan/PlanStep consumer requires separate authorization",
        "ThinkingProposal ready       != Plan authorized",
        "canonical Plan ready         != execution authorized",
        "Governance evaluation        != Action execution",
        "STOP BEFORE GENERIC ACT",
        "M96 remains STOP BEFORE GENERIC ACT",
    ):
        assert marker in text


def test_runtime_api_persistence_freeze_and_parent_accounting_are_locked():
    text = _text()
    for marker in (
        "runtime ThinkingProposal class",
        "Think -> Plan consumer",
        "API, router, request model",
        "JSON store",
        "generic Act",
        "aether/core/loop.py",
        "aether/core/governance.py",
        "aether/thinking/policy.py",
        "Structured Thinking Proposal prerequisite contract: **ESTABLISHED LOCALLY**",
        "Think -> Plan consumer: **NOT YET SATISFIED**",
        "M96: **OPEN**",
        "M95 reopened: **NO**",
    ):
        assert marker in text
