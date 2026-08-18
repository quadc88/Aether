"""Static locks for the M96 parent closure record."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / "docs/architecture/MILESTONE_96_AUTHORITATIVE_GOAL_TO_PLAN_COGNITIVE_FOUNDATION_CLOSURE_RECORD.md"


def _text() -> str:
    return RECORD.read_text(encoding="utf-8")


def _normalized() -> str:
    return " ".join(_text().split())


def test_title_parent_objective_and_canonical_path_are_locked():
    text = _normalized()
    assert text.startswith("# Milestone 96 Authoritative Goal-to-Plan Cognitive Foundation Closure Record")
    assert "PARENT MILESTONE CLOSURE RECORD" in text
    assert "Milestone 96 - Authoritative Goal-to-Plan Cognitive Foundation" in text
    assert "minimum authoritative, process-local cognitive execution foundation" in text
    assert "while stopping before any generic Act" in text
    assert "Human Authority -> Goal acceptance -> Goal -> Task" in text
    assert "Core Governance evaluation -> STOP BEFORE GENERIC ACT" in text


def test_m96a_design_ownership_contribution_is_locked():
    text = _normalized()
    for marker in (
        "M96A - Design / Ownership Boundary",
        "c86fcf05c12ae19bdf957b100ea2969905509e3a",
        "milestone-96A-authoritative-goal-task-plan-boundary",
        "Goal Intake/Human Authority ownership of Goal",
        "Core Coordination ownership of Task and TaskContext",
        "ASC cardinality and selection",
        "M96A established",
        "It did not implement Plan or PlanStep runtime",
    ):
        assert marker in text


def test_m96b_goal_task_context_contribution_is_locked():
    text = _normalized()
    for marker in (
        "M96B - Goal-First Process-Local Runtime Foundation",
        "32f9a36b7d847afb3960a6efd87c60978a656163",
        "milestone-96B-goal-first-in-memory-foundation",
        "explicit Human-Authority Goal acceptance",
        "accepted Goal -> atomic Task -> initial authoritative TaskContext",
        "process-local Core Coordination registry",
        "immutable snapshots/revisions",
        "one authoritative TaskContext per active Task",
        "no silent merge",
    ):
        assert marker in text


def test_m96c_plan_and_planstep_contribution_is_locked():
    text = _normalized()
    for marker in (
        "M96C - Canonical Plan / PlanStep Process-Local Foundation",
        "1ce9b056ef9172b12cf7b33c949ba9175e76768a",
        "milestone-96C-canonical-plan-planstep-process-local-foundation",
        "canonical Plan identity",
        "Plan lifecycle",
        "canonical PlanStep identity",
        "one Plan parent",
        "explicit sequence identity",
        "rejection of hidden PlanStep merging",
    ):
        assert marker in text


def test_m96d_discovery_provenance_is_not_a_parent_blocker():
    text = _normalized()
    for marker in (
        "M96D - Prerequisite Discovery Provenance",
        "B_THINK_OUTPUT_NOT_YET_PLAN_COMPATIBLE",
        "MODEL_E_NO_RUNTIME_INTEGRATION_YET",
        "No standalone authoritative M96D file or tag is asserted",
        "not an original parent obligation",
        "not a closure blocker",
    ):
        assert marker in text


def test_m96e_prerequisite_and_m96f_consumer_are_locked():
    text = _normalized()
    for marker in (
        "M96E - Structured Thinking Proposal Contract Boundary",
        "2d1ed67bb7e5f981a287709c1bc01efa8b9d3dc2",
        "milestone-96E-structured-thinking-proposal-contract-boundary",
        "immutable proposal semantics",
        "PROPOSAL_NOT_READY",
        "M96F - ThinkingProposal Runtime Consumer",
        "7b04146a62efff58ec01db7a4df7e680547e51c3",
        "milestone-96F-thinkingproposal-runtime-consumer",
        "materialize_thinking_proposal",
        "materializes the canonical Plan",
        "required process-local Think -> Plan seam is SATISFIED",
        "outside-process-local consumer is NOT YET SATISFIED and is outside M96 parent scope",
    ):
        assert marker in text


def test_m96g_governance_identity_and_non_authority_are_locked():
    text = _normalized()
    for marker in (
        "M96G - Governance Before Generic Act",
        "9d288215f2483913ccc702916bbd39e8c487a4e0",
        "milestone-96G-canonical-plan-governance-evaluation",
        "8190fed2fff8ad818272a10391666956471c754e",
        "POST-FINALIZATION HISTORICAL LEDGER CORRECTION",
        "CanonicalPlanGovernanceEvaluationRequest",
        "CanonicalPlanGovernanceEvaluation",
        "evaluate_canonical_plan_governance",
        "PLAN_PLUS_SELECTED_CURRENT_PLANSTEP",
        "EVIDENCE_ONLY",
        "authorization_granted",
        "execution_allowed",
        "action_dispatch_allowed",
        "does not grant execution authority or perform Generic Act",
    ):
        assert marker in text


def test_eight_parent_obligations_and_final_conclusion_are_locked():
    text = _normalized()
    for number in range(1, 9):
        assert f"| {number} |" in text
    for marker in (
        "Human-authority Goal admission",
        "Authoritative Task ownership",
        "Authoritative TaskContext",
        "Canonical Plan runtime",
        "Canonical PlanStep runtime",
        "Think -> Plan authoritative consumer seam",
        "Governance before generic Act",
        "Architecture integrity",
        "ALL_PARENT_OBLIGATIONS_SATISFIED",
    ):
        assert marker in text


def test_generic_act_non_goals_and_closure_boundary_are_locked():
    text = _normalized()
    for marker in (
        "GENERIC_ACT_NOT_REQUIRED_FOR_M96_PARENT_CLOSURE",
        "Explicit Parent Non-Goals",
        "persistent Goal, Task, TaskContext, or Plan storage",
        "generic POST /chat integration or full /chat replacement",
        "Generic Act or a second governed capability",
        "Observation Intake or Verification Aggregation",
        "Critic, Repair, Learning, or automatic retry",
        "scheduler, background execution, or wake behavior",
        "They may be separately authorized future milestones",
        "Generic Act: NOT_IMPLEMENTED",
        "Generic Act integration: NOT_AUTHORIZED",
    ):
        assert marker in text


def test_architecture_and_lifecycle_lock_are_locked():
    text = _normalized()
    for marker in (
        "Aether remains one persistent digital intelligence",
        "AetherOS remains runtime/world/body",
        "Nine cognitive organs remain unchanged",
        "Core Governance owns authorization",
        "Core Coordination owns Task/TaskContext continuity and coordination",
        "ASC remains one Authoritative Shared Cognitive Context framework",
        "Time provides context, not authority",
        "Resource Observation reports facts; Resource Governance decides",
        "Thinking proposes; Governance authorizes; Verification supplies evidence",
        "canonical global Execution Loop remains unchanged",
        "M96 substantive parent work is COMPLETE",
        "M96 closure record is COMPLETE LOCALLY",
        "M96 durable closure is PENDING GIT FINALIZATION AND PM ACCEPTANCE",
        "M96 remains OPEN / NOT DURABLY CLOSED YET",
        "No M96H, M97, Generic Act implementation, or successor milestone",
    ):
        assert marker in text
