"""Focused runtime locks for the M96B Goal-first foundation."""

from dataclasses import FrozenInstanceError

import pytest

from aether.core.goal import Goal, GoalIntake
from aether.core.task_context import CoreCoordination


def _accepted_goal(coordinator: CoreCoordination | None = None) -> Goal:
    owner = coordinator or CoreCoordination()
    return owner.accept_goal(owner.create_goal("Ship the bounded foundation"), "human:event-1")


def test_goal_proposal_has_distinct_semantic_identity():
    goal = Goal.propose("Improve context continuity")
    assert goal.goal_id.startswith("goal_")
    assert goal.goal_id != goal.goal_text
    assert goal.goal_id != "session-1"
    assert "session_id" not in goal.to_dict()
    assert goal.goal_status == "proposed"


def test_goal_acceptance_requires_human_authority_reference():
    with pytest.raises(ValueError, match="authority_reference"):
        Goal.propose("Require explicit authority").accept()


def test_approval_identifier_cannot_be_goal_authority():
    with pytest.raises(ValueError, match="approval_id"):
        Goal.propose("Keep approval separate").accept("approval_123")


def test_acceptance_creates_new_accepted_revision():
    proposed = Goal.propose("Accept a human objective")
    accepted = proposed.accept("human:event-2", accepted_at="2026-08-15T00:00:00+00:00")
    assert accepted.goal_id == proposed.goal_id
    assert accepted.goal_status == "accepted"
    assert accepted.accepted_at == "2026-08-15T00:00:00+00:00"
    assert accepted.revision == proposed.revision + 1
    assert proposed.goal_status == "proposed"


def test_requested_outcome_is_not_completion_criteria():
    goal = Goal.propose("Reach an outcome", requested_outcome="A human outcome")
    assert goal.requested_outcome == "A human outcome"
    assert "completion_criteria" not in goal.to_dict()


def test_goal_constraints_are_copied_and_immutable():
    constraints = {"scope": ["one"]}
    goal = Goal.propose("Preserve constraints", goal_constraints=constraints)
    constraints["scope"].append("two")
    assert goal.goal_constraints["scope"] == ("one",)
    with pytest.raises(TypeError):
        goal.goal_constraints["new"] = "value"


def test_rejected_goal_cannot_be_accepted_again():
    rejected = Goal.propose("Reject this objective").reject()
    with pytest.raises(ValueError, match="cannot be accepted"):
        rejected.accept("human:event-3")


def test_goal_intake_registers_and_returns_goal_snapshots():
    intake = GoalIntake()
    goal = intake.propose(goal_text="Register this objective")
    assert intake.get(goal.goal_id) == goal
    assert intake.list() == (goal,)


def test_task_creation_requires_an_accepted_goal():
    coordinator = CoreCoordination()
    proposed = coordinator.create_goal("Do not start without authority")
    with pytest.raises(ValueError, match="accepted goal"):
        coordinator.create_task(proposed)


def test_task_creation_creates_first_authoritative_context():
    coordinator = CoreCoordination()
    goal = _accepted_goal(coordinator)
    task = coordinator.create_task(goal)
    context = coordinator.context_for_task(task)
    assert context.task_context_id == task.task_context_id
    assert context.task_id == task.task_id
    assert context.goal_id == goal.goal_id
    assert context.context_revision == 1


def test_task_and_context_ids_are_fresh_and_distinct():
    coordinator = CoreCoordination()
    goal = _accepted_goal(coordinator)
    first = coordinator.create_task(goal)
    second = coordinator.create_task(goal)
    ids = {first.task_id, first.task_context_id, second.task_id, second.task_context_id}
    assert len(ids) == 4
    assert first.task_id.startswith("task_")
    assert first.task_context_id.startswith("task_context_")


def test_task_keeps_explicit_goal_parent_reference():
    coordinator = CoreCoordination()
    goal = _accepted_goal(coordinator)
    task = coordinator.create_task(goal, task_scope="bounded work")
    assert task.goal_id == goal.goal_id
    assert task.task_scope == "bounded work"
    assert task.task_id != task.goal_id


def test_context_snapshot_is_frozen():
    coordinator = CoreCoordination()
    task = coordinator.create_task(_accepted_goal(coordinator))
    context = coordinator.context_for_task(task)
    with pytest.raises(FrozenInstanceError):
        context.task_status = "completed"


def test_context_snapshot_does_not_alias_input_constraints():
    coordinator = CoreCoordination()
    constraints = {"limit": [1]}
    task = coordinator.create_task(_accepted_goal(coordinator), task_constraints=constraints)
    constraints["limit"].append(2)
    assert task.task_constraints["limit"] == (1,)


def test_context_to_dict_exposes_references_not_authoritative_criteria_payload():
    coordinator = CoreCoordination()
    task = coordinator.create_task(_accepted_goal(coordinator))
    payload = coordinator.context_for_task(task).to_dict()
    assert "completion_criteria_reference" in payload
    assert payload["completion_criteria_reference"] is None
    assert "completion_criteria" not in payload


def test_task_creation_does_not_silently_select_a_context():
    coordinator = CoreCoordination()
    task = coordinator.create_task(_accepted_goal(coordinator))
    assert coordinator.selected_context() is None
    assert coordinator.selected_context_id is None
    assert coordinator.context_for_task(task) not in coordinator.selection_history


def test_context_selection_is_explicit_and_returns_selected_snapshot():
    coordinator = CoreCoordination()
    task = coordinator.create_task(_accepted_goal(coordinator))
    context = coordinator.select_context(coordinator.context_for_task(task))
    assert coordinator.selected_context_id == context.task_context_id
    assert coordinator.selected_context() == context


def test_switch_context_records_previous_context_without_merging():
    coordinator = CoreCoordination()
    goal = _accepted_goal(coordinator)
    first = coordinator.create_task(goal)
    second = coordinator.create_task(goal)
    first_context = coordinator.select_context(coordinator.context_for_task(first))
    second_context = coordinator.switch_context(coordinator.context_for_task(second))
    assert first_context.task_context_id != second_context.task_context_id
    assert coordinator.selection_history[-1].previous_task_context_id == first_context.task_context_id


def test_terminal_context_cannot_be_selected_or_revived():
    coordinator = CoreCoordination()
    task = coordinator.create_task(_accepted_goal(coordinator))
    context = coordinator.update_context(coordinator.context_for_task(task), task_status="completed")
    with pytest.raises(ValueError, match="cannot select"):
        coordinator.select_context(context)


def test_context_update_creates_a_new_revision_and_preserves_old_snapshot():
    coordinator = CoreCoordination()
    task = coordinator.create_task(_accepted_goal(coordinator))
    original = coordinator.context_for_task(task)
    updated = coordinator.update_context(original, execution_phase="understand")
    assert original.context_revision == 1
    assert updated.context_revision == 2
    assert original.execution_phase == "initial"
    assert updated.execution_phase == "understand"


def test_context_update_keeps_task_context_identity_and_updates_task_reference_state():
    coordinator = CoreCoordination()
    task = coordinator.create_task(_accepted_goal(coordinator))
    updated = coordinator.update_context(
        coordinator.context_for_task(task),
        current_plan_id="plan_canonical_1",
    )
    assert updated.task_context_id == task.task_context_id
    assert coordinator.get_task(task).current_plan_id == "plan_canonical_1"


def test_waiting_and_paused_contexts_remain_explicitly_selectable():
    coordinator = CoreCoordination()
    goal = _accepted_goal(coordinator)
    waiting = coordinator.create_task(goal)
    paused = coordinator.create_task(goal)
    waiting_context = coordinator.update_context(
        coordinator.context_for_task(waiting), task_status="waiting"
    )
    paused_context = coordinator.update_context(
        coordinator.context_for_task(paused), task_status="paused"
    )
    assert coordinator.select_context(waiting_context).task_status == "waiting"
    assert coordinator.select_context(paused_context).task_status == "paused"


def test_injected_time_provider_supplies_runtime_timestamps():
    values = iter(("t1", "t2", "t3"))
    coordinator = CoreCoordination(time_provider=lambda: next(values))
    goal = coordinator.accept_goal(coordinator.create_goal("Use injected time"), "human:event-4")
    task = coordinator.create_task(goal)
    assert task.created_at == "t1"
    assert coordinator.context_for_task(task).created_at == "t1"
    coordinator.select_context(coordinator.context_for_task(task))
    assert coordinator.selection_history[0].selected_at == "t2"


def test_list_operations_return_snapshots_without_registry_aliasing():
    coordinator = CoreCoordination()
    goal = _accepted_goal(coordinator)
    task = coordinator.create_task(goal)
    assert coordinator.list_tasks() == (task,)
    assert coordinator.list_contexts() == (coordinator.context_for_task(task),)
    assert isinstance(coordinator.list_tasks(), tuple)
