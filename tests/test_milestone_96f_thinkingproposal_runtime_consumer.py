"""Focused runtime locks for the M96F ThinkingProposal consumer."""

from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

from aether.core.task_context import CoreCoordination, Plan, PlanStep
from aether.thinking.proposal import (
    PROPOSAL_NOT_READY,
    PROPOSAL_READY,
    PROVENANCE_CATEGORIES,
    ThinkingProposal,
)


ROOT = Path(__file__).resolve().parents[1]
TASK_CONTEXT_SOURCE = ROOT / "aether/core/task_context.py"
PROPOSAL_SOURCE = ROOT / "aether/thinking/proposal.py"


def _provenance() -> dict[str, dict[str, str]]:
    return {category: {"source": category} for category in PROVENANCE_CATEGORIES}


def _foundation() -> tuple[CoreCoordination, object, object, object]:
    coordinator = CoreCoordination(time_provider=lambda: "2026-08-17T00:00:00+00:00")
    goal = coordinator.accept_goal(
        coordinator.create_goal("Build a bounded canonical plan"), "human:m96f"
    )
    task = coordinator.create_task(goal, task_scope="M96F runtime consumer")
    context = coordinator.select_context(coordinator.context_for_task(task))
    return coordinator, goal, task, context


def _proposal(
    _coordinator,
    goal,
    task,
    context,
    *,
    proposal_state=PROPOSAL_READY,
    proposal_id="proposal_m96f_1",
    completion=None,
    failure=None,
    blocked=None,
    provenance=None,
    **overrides,
) -> ThinkingProposal:
    return ThinkingProposal(
        proposal_id=proposal_id,
        proposal_revision=1,
        created_at="2026-08-17T00:00:00+00:00",
        goal_id=overrides.pop("goal_id", goal.goal_id),
        task_id=overrides.pop("task_id", task.task_id),
        task_context_id=overrides.pop("task_context_id", context.task_context_id),
        task_context_revision=overrides.pop(
            "task_context_revision", context.context_revision
        ),
        proposal_state=proposal_state,
        proposed_objective=overrides.pop("proposed_objective", "Create the bounded plan"),
        proposed_completion_criteria=completion
        if completion is not None
        else {"description": "completion is observed"},
        proposed_failure_criteria=failure
        if failure is not None
        else {"description": "failure is recorded"},
        proposed_blocked_criteria=blocked
        if blocked is not None
        else {"description": "blocked state is explicit"},
        rationale=overrides.pop("rationale", "Explicit planning evidence"),
        constraints_references=overrides.pop("constraints_references", []),
        assumptions=overrides.pop("assumptions", []),
        dependency_proposals=overrides.pop("dependency_proposals", []),
        verification_requirement_proposals=overrides.pop(
            "verification_requirement_proposals", []
        ),
        risk_evidence_references=overrides.pop("risk_evidence_references", []),
        requested_action_relation=overrides.pop("requested_action_relation", None),
        tool_suggestion_relation=overrides.pop("tool_suggestion_relation", None),
        provenance=provenance or _provenance(),
        not_ready_reason=overrides.pop(
            "not_ready_reason",
            {"category": "missing_proposed_completion_criteria"}
            if proposal_state == PROPOSAL_NOT_READY
            else None,
        ),
        **overrides,
    )


def test_proposal_has_distinct_identity_and_explicit_ready_state():
    coordinator, goal, task, context = _foundation()
    proposal = _proposal(coordinator, goal, task, context)
    assert proposal.proposal_state == PROPOSAL_READY
    assert proposal.proposal_id not in {
        goal.goal_id,
        task.task_id,
        context.task_context_id,
    }
    assert proposal.proposal_revision == 1


def test_proposal_snapshot_is_frozen_and_does_not_alias_inputs():
    coordinator, goal, task, context = _foundation()
    criteria = {"items": ["complete"]}
    provenance = _provenance()
    proposal = _proposal(
        coordinator,
        goal,
        task,
        context,
        completion=criteria,
        provenance=provenance,
    )
    criteria["items"].append("mutated")
    provenance["goal_source"]["source"] = "mutated"
    payload = proposal.to_dict()
    payload["proposed_completion_criteria"]["items"].append("response prose")
    assert proposal.proposed_completion_criteria["items"] == ("complete",)
    assert proposal.provenance["goal_source"]["source"] == "goal_source"
    with pytest.raises(FrozenInstanceError):
        proposal.proposal_id = "changed"


def test_proposal_rejects_missing_criteria_and_invalid_provenance():
    coordinator, goal, task, context = _foundation()
    with pytest.raises(ValueError, match="proposed_completion_criteria"):
        _proposal(coordinator, goal, task, context, completion={})
    invalid_provenance = _provenance()
    invalid_provenance.pop("task_source")
    with pytest.raises(ValueError, match="provenance"):
        _proposal(
            coordinator,
            goal,
            task,
            context,
            provenance=invalid_provenance,
        )


def test_not_ready_requires_structured_reason():
    coordinator, goal, task, context = _foundation()
    with pytest.raises(ValueError, match="not_ready_reason"):
        _proposal(
            coordinator,
            goal,
            task,
            context,
            proposal_state=PROPOSAL_NOT_READY,
            not_ready_reason=None,
        )


def test_not_ready_creates_no_plan_or_context_change():
    coordinator, goal, task, context = _foundation()
    proposal = _proposal(
        coordinator,
        goal,
        task,
        context,
        proposal_state=PROPOSAL_NOT_READY,
    )
    before = coordinator.selected_context()
    with pytest.raises(ValueError, match="PROPOSAL_NOT_READY"):
        coordinator.materialize_thinking_proposal(proposal)
    assert coordinator.list_plans() == ()
    assert coordinator.list_plan_steps() == ()
    assert coordinator.selected_context() == before


def test_ready_materializes_existing_canonical_plan_and_preserves_provenance():
    coordinator, goal, task, context = _foundation()
    proposal = _proposal(coordinator, goal, task, context)
    plan = coordinator.materialize_thinking_proposal(proposal)
    assert isinstance(plan, Plan)
    assert (plan.goal_id, plan.task_id, plan.task_context_id) == (
        goal.goal_id,
        task.task_id,
        context.task_context_id,
    )
    assert plan.task_context_revision == context.context_revision
    assert plan.proposal_provenance == proposal.provenance
    assert coordinator.get_task(task).current_plan_id == plan.plan_id


def test_consumer_requires_explicitly_selected_context():
    coordinator = CoreCoordination()
    goal = coordinator.accept_goal(coordinator.create_goal("Select before planning"), "human:m96f")
    task = coordinator.create_task(goal)
    context = coordinator.context_for_task(task)
    proposal = _proposal(coordinator, goal, task, context)
    with pytest.raises(ValueError, match="selected"):
        coordinator.materialize_thinking_proposal(proposal)
    assert coordinator.list_plans() == ()


def test_consumer_rejects_stale_context_revision():
    coordinator, goal, task, context = _foundation()
    proposal = _proposal(coordinator, goal, task, context)
    coordinator.update_context(context, execution_phase="understand")
    with pytest.raises(ValueError, match="revision is stale"):
        coordinator.materialize_thinking_proposal(proposal)
    assert coordinator.list_plans() == ()


def test_consumer_rejects_wrong_selected_context():
    coordinator, goal, task, context = _foundation()
    other_task = coordinator.create_task(goal)
    other_context = coordinator.select_context(coordinator.context_for_task(other_task))
    proposal = _proposal(coordinator, goal, task, context)
    with pytest.raises(ValueError, match="selected"):
        coordinator.materialize_thinking_proposal(proposal)
    assert coordinator.selected_context_id == other_context.task_context_id
    assert coordinator.list_plans() == ()


def test_consumer_rejects_task_context_that_is_not_selected():
    coordinator, goal, task, context = _foundation()
    other_task = coordinator.create_task(goal)
    other_context = coordinator.context_for_task(other_task)
    proposal = _proposal(coordinator, goal, other_task, other_context)
    with pytest.raises(ValueError, match="selected"):
        coordinator.materialize_thinking_proposal(proposal)
    assert coordinator.selected_context_id == context.task_context_id
    assert coordinator.list_plans() == ()


def test_consumer_rejects_goal_mismatch():
    coordinator, goal, task, context = _foundation()
    other_goal = coordinator.accept_goal(coordinator.create_goal("Other goal"), "human:other")
    proposal = _proposal(coordinator, goal, task, context, goal_id=other_goal.goal_id)
    with pytest.raises(ValueError, match="not owned by its Goal"):
        coordinator.materialize_thinking_proposal(proposal)
    assert coordinator.list_plans() == ()


def test_consumer_rejects_task_mismatch():
    coordinator, goal, task, context = _foundation()
    other_task = coordinator.create_task(goal)
    proposal = _proposal(coordinator, goal, other_task, context)
    with pytest.raises(ValueError, match="not owned by its Task"):
        coordinator.materialize_thinking_proposal(proposal)
    assert coordinator.list_plans() == ()


def test_consumer_rejects_task_context_ownership_mismatch():
    coordinator, goal, task, context = _foundation()
    other_task = coordinator.create_task(goal)
    other_context = coordinator.select_context(coordinator.context_for_task(other_task))
    proposal = _proposal(coordinator, goal, task, other_context)
    with pytest.raises(ValueError, match="not owned by its Task"):
        coordinator.materialize_thinking_proposal(proposal)
    assert coordinator.list_plans() == ()


def test_consumer_rejects_terminal_task():
    coordinator, goal, task, context = _foundation()
    terminal = coordinator.update_context(context, task_status="completed")
    proposal = _proposal(
        coordinator,
        goal,
        task,
        terminal,
        task_context_revision=terminal.context_revision,
    )
    with pytest.raises(ValueError, match="non-terminal task"):
        coordinator.materialize_thinking_proposal(proposal)
    assert coordinator.list_plans() == ()


def test_proposal_rejects_invalid_required_binding():
    coordinator, goal, task, context = _foundation()
    with pytest.raises(ValueError, match="goal_id"):
        _proposal(coordinator, goal, task, context, goal_id="")
    with pytest.raises(ValueError, match="task_context_revision"):
        _proposal(coordinator, goal, task, context, task_context_revision=0)


def test_only_explicit_proposal_criteria_reach_plan():
    coordinator, goal, task, context = _foundation()
    proposal = _proposal(
        coordinator,
        goal,
        task,
        context,
        completion={"explicit": "completion"},
        failure={"explicit": "failure"},
        blocked={"explicit": "blocked"},
        rationale="policy reasons must not be used",
        risk_evidence_references={"risk_level": "high"},
        tool_suggestion_relation={"tool_id": "file.restricted_read"},
        requested_action_relation={"response_text": "write a file"},
    )
    plan = coordinator.materialize_thinking_proposal(proposal)
    assert plan.completion_criteria == {"explicit": "completion"}
    assert plan.failure_criteria == {"explicit": "failure"}
    assert plan.blocked_criteria == {"explicit": "blocked"}
    assert "reasons" not in plan.completion_criteria
    assert "risk_level" not in plan.completion_criteria
    assert "tool_id" not in plan.completion_criteria
    assert "response_text" not in plan.completion_criteria


def test_unsupported_step_content_does_not_invent_plan_steps():
    coordinator, goal, task, context = _foundation()
    proposal = _proposal(
        coordinator,
        goal,
        task,
        context,
        dependency_proposals=[{"sequence_index": 1, "description": "suggested step"}],
        verification_requirement_proposals=[{"sequence_index": 2}],
    )
    plan = coordinator.materialize_thinking_proposal(proposal)
    assert plan.plan_step_ids == ()
    assert coordinator.list_plan_steps(plan) == ()


def test_explicit_plan_step_keeps_distinct_identity_and_parent():
    coordinator, goal, task, context = _foundation()
    plan = coordinator.materialize_thinking_proposal(_proposal(coordinator, goal, task, context))
    step = coordinator.create_plan_step(
        plan,
        sequence_index=1,
        completion_criteria={"description": "step complete"},
        failure_criteria={"description": "step failed"},
        blocked_criteria={"description": "step blocked"},
    )
    assert isinstance(step, PlanStep)
    assert step.plan_id == plan.plan_id
    assert step.plan_step_id not in {
        plan.plan_id,
        goal.goal_id,
        task.task_id,
        context.task_context_id,
    }


def test_readiness_does_not_grant_execution_authority():
    coordinator, goal, task, context = _foundation()
    plan = coordinator.materialize_thinking_proposal(_proposal(coordinator, goal, task, context))
    payload = plan.to_dict()
    assert "execution_allowed" not in payload
    assert "plan_authorized" not in payload
    assert "generic_action_allowed" not in payload
    assert not hasattr(plan, "execution_allowed")


def test_consumer_has_no_live_policy_api_persistence_or_execution_wiring():
    task_context_source = TASK_CONTEXT_SOURCE.read_text(encoding="utf-8")
    proposal_source = PROPOSAL_SOURCE.read_text(encoding="utf-8")
    for source in (task_context_source, proposal_source):
        for forbidden in (
            "aether.thinking",
            "policy.py",
            "api_server",
            "from fastapi",
            "json.dump",
            "write_text",
            "restricted_read",
            "evaluate_authorization",
            "execute_tool",
            "tool_service",
            "generic Act",
            "Observation Intake",
            "scheduler",
            "/chat",
        ):
            assert forbidden not in source


def test_consumer_method_uses_existing_canonical_plan_owner():
    source = TASK_CONTEXT_SOURCE.read_text(encoding="utf-8")
    assert "def materialize_thinking_proposal" in source
    assert "return self.create_plan(" in source
    assert "proposal_provenance=proposal.provenance" in source
    assert "def create_plan(" in source
    assert "def create_plan_step(" in source
