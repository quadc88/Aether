"""Static design locks for the M96A Goal/Task/Plan boundary."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / "docs/architecture/MILESTONE_96A_AUTHORITATIVE_GOAL_TASK_PLAN_BOUNDARY.md"


def _text() -> str:
    return RECORD.read_text(encoding="utf-8")


def _normalized() -> str:
    return " ".join(_text().split())


def test_title_classification_and_think_plan_seam():
    text = _text()
    assert text.startswith("# Milestone 96A Authoritative Goal / TaskContext / Canonical Plan Boundary")
    assert "Classification: DESIGN / OWNERSHIP BOUNDARY ONLY" in text
    assert "Think -> Plan" in text
    assert "STOP BEFORE GENERIC ACT" in text


def test_goal_ownership_and_accepted_before_criteria_rule():
    text = _normalized()
    for marker in (
        "Semantic owner: **Goal Intake under Human Authority**",
        "goal_id",
        "goal_text",
        "authority_reference",
        "requested_outcome",
        "goal_constraints",
        "Goal requested_outcome != authoritative Plan completion criteria",
        "A Goal may be accepted before authoritative execution completion criteria are known",
        "Goal does not own",
    ):
        assert marker in text


def test_task_core_coordination_ownership_and_reference_only_criteria():
    text = _normalized()
    for marker in (
        "Semantic owner: **Core Coordination**",
        "Task is a bounded work or execution unit formed under a Goal",
        "task_id",
        "goal_id",
        "completion_criteria_reference",
        "must resolve only to canonical Plan criteria or canonical PlanStep criteria",
        "Task must not define a competing local authoritative criteria payload",
    ):
        assert marker in text


def test_task_context_ownership_cardinality_and_reference_only_criteria():
    text = _normalized()
    for marker in (
        "TaskContext is the single authoritative current-state envelope",
        "task_context_id",
        "completion_criteria_reference",
        "TaskContext carries state and references only",
        "TaskContext criteria are **REFERENCE ONLY**",
        "Every active Task has exactly one authoritative TaskContext",
    ):
        assert marker in text


def test_canonical_plan_owns_criteria_and_not_ready_behavior():
    text = _normalized()
    for marker in (
        "Semantic owner: **canonical Plan stage / planning contract**",
        "authoritative Plan completion criteria",
        "authoritative Plan failure criteria",
        "authoritative Plan blocked criteria",
        "plan_not_ready_reason",
        "If authoritative criteria cannot be derived, Plan status is `not_ready`",
        "Generic Act is then **NO**",
        "Plan readiness and Plan selection are not execution authorization",
    ):
        assert marker in text


def test_canonical_plan_step_owns_step_criteria_or_no_expectation():
    text = _normalized()
    for marker in (
        "Semantic owner: **canonical Plan / PlanStep contract**",
        "plan_step_id",
        "authoritative `step_completion_criteria`",
        "no_applicable_expectation",
        "PlanStep owns authoritative step criteria",
        "A caller-supplied `plan_step_id` is not proof of canonical PlanStep identity",
        "PlanStep identity is not ordinal position",
    ):
        assert marker in text


def test_exact_ownership_matrix_has_one_owner_per_category():
    text = _normalized()
    for marker in (
        "## 8. Exact Ownership Matrix",
        "Human objective/intention | Goal Intake",
        "Task identity/lifecycle | Core Coordination",
        "TaskContext identity/lifecycle | Core Coordination",
        "Canonical Plan semantics | canonical Plan stage / planning contract",
        "Canonical Plan completion/failure/blocked criteria | canonical Plan stage / planning contract",
        "Canonical PlanStep identity/criteria | canonical Plan / PlanStep contract",
        "Permission / authorization policy | Core Governance",
        "Temporal facts/scope | Time",
        "Working-memory content | Memory",
        "Action-attempt identity | Action occurrence contract",
        "Observation facts/identity | Observation producer boundary",
        "Verification evidence/status/identity | Verification contract",
        "Consumer identity/use | concrete downstream consumer contract",
        "Each category has exactly one authoritative owner",
    ):
        assert marker in text


def test_asc_framework_cardinality_explicit_switching_and_no_silent_merge():
    text = _normalized()
    for marker in (
        "One ASC architecture framework exists",
        "Every active Task has exactly one authoritative TaskContext",
        "Every reasoning turn has exactly one selected current TaskContext",
        "Waiting and paused Tasks may retain separate TaskContexts",
        "Context selection and switching are explicit Core Coordination operations",
        "No silent merge, overwrite, fallback adoption, or cross-task context transfer",
        "Governance constrains authority-sensitive selection and switching",
        "The ASC is not",
    ):
        assert marker in text


def test_governance_time_separation_and_authority_rules():
    text = _normalized()
    for marker in (
        "Thinking proposes. Governance authorizes. Verification supplies evidence. Action executes only within authorization.",
        "Core Governance owns Constitution enforcement",
        "Core Governance does not own Goal identity, Task continuity, canonical Plan semantics",
        "Time owns clock facts",
        "Time provides context, not authority",
        "Time does not select a Goal, create a Task, own a Plan",
        "AetherOS supplies timing mechanisms and raw clock facts",
    ):
        assert marker in text


def test_identity_non_aliasing_is_explicit_and_fabrication_is_forbidden():
    text = _normalized()
    assert (
        "goal_id != task_id != task_context_id != plan_id != plan_step_id != approval_id != "
        "action_attempt_id != observation_id != verification_id != session_id"
    ) in text
    for marker in (
        "Absence is allowed when the semantic object does not yet exist",
        "Fabrication is not allowed",
        "session_id",
        "approval_id",
        "file-access ID",
        "request ID",
        "generic record ID",
        "timestamp",
        "hash",
    ):
        assert marker in text


def test_frozen_m94_m95_boundary_and_no_restricted_read_retrofit():
    text = _normalized()
    for marker in (
        "Capability: `file.restricted_read`",
        "Governed capability count: `1`",
        "Generic `/chat` execution authority: **NO**",
        "Restricted-read Observation: **CALL_LOCAL / AUTHORITATIVE**",
        "Persistent restricted-read Observation: **NONE / NOT JUSTIFIED**",
        "Restricted-read persistence eligibility: **BLOCKED**",
        "Observation Intake caller: **NONE / NOT PROVEN**",
        "Verification Aggregation: **NOT WIRED**",
        "Critic: **NOT WIRED**",
        "Repair: **NOT WIRED**",
        "Learning: **NOT WIRED**",
        "Retry: **NO**",
        "Background execution: **NO**",
        "No Goal, Task, TaskContext, Plan, or PlanStep identity is retrofitted",
    ):
        assert marker in text


def test_stop_before_generic_act_and_explicit_non_authorizations():
    text = _normalized()
    for marker in (
        "## 10. Lifecycle and Stop Boundary",
        "STOP BEFORE GENERIC ACT",
        "## 13. Future Slices and Build Boundary",
        "Slice A",
        "Slice B",
        "Slice C",
        "Slice D",
        "## 14. Verification and Non-Authorization",
        "M96A runtime implementation: **NOT AUTHORIZED**",
        "NO RUNTIME IMPLEMENTATION",
        "NO API",
        "NO PERSISTENCE",
        "NO GENERIC ACT",
        "NO RESTRICTED-READ RETROFIT",
        "NO COMMIT, TAG, OR PUSH",
    ):
        assert marker in text
