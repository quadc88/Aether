"""Focused locks for the M96C process-local Plan/PlanStep foundation."""

from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

from aether.core.task_context import CoreCoordination, Plan, PlanStep


ROOT = Path(__file__).resolve().parents[1]
TASK_CONTEXT_SOURCE = ROOT / "aether/core/task_context.py"


def _criteria(label: str) -> dict[str, str]:
    return {"description": label}


def _foundation(time_provider=None):
    coordinator = CoreCoordination(time_provider=time_provider)
    goal = coordinator.accept_goal(
        coordinator.create_goal("Build the canonical process-local foundation"),
        "human:m96c",
    )
    task = coordinator.create_task(goal, task_scope="canonical planning")
    context = coordinator.select_context(coordinator.context_for_task(task))
    return coordinator, goal, task, context


def _plan(coordinator, goal, task, context):
    return coordinator.create_plan(
        goal,
        task,
        context,
        completion_criteria=_criteria("completion"),
        failure_criteria=_criteria("failure"),
        blocked_criteria=_criteria("blocked"),
    )


def _step(coordinator, plan, sequence_index=1):
    return coordinator.create_plan_step(
        plan,
        sequence_index=sequence_index,
        completion_criteria=_criteria(f"step {sequence_index} complete"),
        failure_criteria=_criteria(f"step {sequence_index} failed"),
        blocked_criteria=_criteria(f"step {sequence_index} blocked"),
    )


def test_plan_is_a_real_object_with_distinct_semantic_identity():
    coordinator, goal, task, context = _foundation()
    plan = _plan(coordinator, goal, task, context)
    assert isinstance(plan, Plan)
    assert plan.plan_id.startswith("plan_")
    assert plan.plan_id not in {goal.goal_id, task.task_id, context.task_context_id}
    assert plan.plan_id != plan.plan_step_ids


def test_plan_binds_exact_goal_task_and_context_revision_snapshot():
    coordinator, goal, task, context = _foundation()
    plan = _plan(coordinator, goal, task, context)
    assert (plan.goal_id, plan.task_id, plan.task_context_id) == (
        goal.goal_id,
        task.task_id,
        context.task_context_id,
    )
    assert plan.task_context_revision == context.context_revision
    assert plan.task_context_snapshot["context_revision"] == context.context_revision
    assert coordinator.get_task(task).current_plan_id == plan.plan_id
    assert coordinator.context_for_task(task).current_plan_id == plan.plan_id


def test_plan_requires_explicitly_selected_context():
    coordinator = CoreCoordination()
    goal = coordinator.accept_goal(coordinator.create_goal("Select context first"), "human:m96c")
    task = coordinator.create_task(goal)
    context = coordinator.context_for_task(task)
    with pytest.raises(ValueError, match="explicitly selected"):
        _plan(coordinator, goal, task, context)


def test_plan_rejects_unknown_goal():
    coordinator, goal, task, context = _foundation()
    with pytest.raises(KeyError, match="unknown goal"):
        _plan(coordinator, "goal_unknown", task, context)


def test_plan_rejects_unaccepted_goal():
    coordinator, goal, task, context = _foundation()
    proposed = coordinator.create_goal("Still needs authority")
    with pytest.raises(ValueError, match="accepted goal"):
        _plan(coordinator, proposed, task, context)


def test_plan_rejects_task_goal_mismatch():
    coordinator, goal, task, context = _foundation()
    other_goal = coordinator.accept_goal(
        coordinator.create_goal("Different parent"), "human:other"
    )
    with pytest.raises(ValueError, match="not owned by the goal"):
        _plan(coordinator, other_goal, task, context)


def test_plan_rejects_unknown_or_mismatched_context():
    coordinator, goal, task, context = _foundation()
    with pytest.raises(KeyError, match="unknown task"):
        _plan(coordinator, goal, "task_unknown", context)
    with pytest.raises(KeyError, match="unknown task context"):
        _plan(coordinator, goal, task, "task_context_unknown")
    other_task = coordinator.create_task(goal)
    other_context = coordinator.select_context(coordinator.context_for_task(other_task))
    coordinator.select_context(context)
    with pytest.raises(ValueError, match="not owned by the task"):
        _plan(coordinator, goal, task, other_context)


def test_plan_rejects_terminal_task():
    coordinator, goal, task, context = _foundation()
    terminal_context = coordinator.update_context(context, task_status="completed")
    with pytest.raises(ValueError, match="non-terminal task"):
        _plan(coordinator, goal, task.task_id, terminal_context)


def test_plan_criteria_are_explicit_and_malformed_criteria_fail_closed():
    coordinator, goal, task, context = _foundation()
    with pytest.raises(ValueError, match="failure_criteria"):
        coordinator.create_plan(
            goal,
            task,
            context,
            completion_criteria=_criteria("completion"),
            failure_criteria={},
            blocked_criteria=_criteria("blocked"),
        )


def test_plan_lifecycle_is_explicit_and_terminal_states_do_not_reopen():
    coordinator, goal, task, context = _foundation()
    plan = _plan(coordinator, goal, task, context)
    ready = coordinator.transition_plan(plan, "ready")
    completed = coordinator.transition_plan(ready, "completed")
    assert completed.plan_status == "completed"
    with pytest.raises(ValueError, match="invalid plan transition"):
        coordinator.transition_plan(completed, "ready")


def test_plan_stale_snapshot_cannot_update_registry():
    coordinator, goal, task, context = _foundation()
    plan = _plan(coordinator, goal, task, context)
    updated = coordinator.transition_plan(plan, "ready")
    with pytest.raises(ValueError, match="stale"):
        coordinator.transition_plan(plan, "blocked")
    assert coordinator.get_plan(updated).plan_status == "ready"


def test_plan_step_has_distinct_identity_and_exactly_one_plan_parent():
    coordinator, goal, task, context = _foundation()
    plan = _plan(coordinator, goal, task, context)
    step = _step(coordinator, plan)
    assert isinstance(step, PlanStep)
    assert step.plan_step_id.startswith("plan_step_")
    assert step.plan_step_id not in {
        plan.plan_id,
        goal.goal_id,
        task.task_id,
        context.task_context_id,
    }
    assert step.plan_id == plan.plan_id
    assert step.plan_step_id in coordinator.get_plan(plan.plan_id).plan_step_ids


def test_plan_step_binds_plan_context_snapshot_and_criteria():
    coordinator, goal, task, context = _foundation()
    plan = _plan(coordinator, goal, task, context)
    step = _step(coordinator, plan)
    assert step.task_context_revision == plan.task_context_revision
    assert step.task_context_snapshot == plan.task_context_snapshot
    assert step.completion_criteria["description"] == "step 1 complete"
    assert step.failure_criteria["description"] == "step 1 failed"
    assert step.blocked_criteria["description"] == "step 1 blocked"


def test_plan_steps_have_deterministic_explicit_ordering():
    coordinator, goal, task, context = _foundation()
    plan = _plan(coordinator, goal, task, context)
    second = _step(coordinator, plan, 2)
    current_plan = coordinator.get_plan(plan.plan_id)
    first = _step(coordinator, current_plan, 1)
    ordered = coordinator.get_plan(current_plan.plan_id).plan_step_ids
    assert ordered == (first.plan_step_id, second.plan_step_id)
    assert [item.sequence_index for item in coordinator.list_plan_steps(current_plan.plan_id)] == [1, 2]


def test_duplicate_sequence_position_and_hidden_merge_are_rejected():
    coordinator, goal, task, context = _foundation()
    plan = _plan(coordinator, goal, task, context)
    with pytest.raises(ValueError, match="sequence_index"):
        _step(coordinator, plan, 0)
    with pytest.raises(ValueError, match="sequence_index"):
        coordinator.create_plan_step(
            plan,
            sequence_index="1",
            completion_criteria=_criteria("invalid"),
            failure_criteria=_criteria("invalid"),
            blocked_criteria=_criteria("invalid"),
        )
    first = _step(coordinator, plan)
    with pytest.raises(ValueError, match="duplicate sequence_index"):
        _step(coordinator, coordinator.get_plan(plan.plan_id))
    second = coordinator.create_plan_step(
        coordinator.get_plan(plan.plan_id),
        sequence_index=2,
        completion_criteria=_criteria("step 1 complete"),
        failure_criteria=_criteria("step 1 failed"),
        blocked_criteria=_criteria("step 1 blocked"),
    )
    assert first.plan_step_id != second.plan_step_id
    assert first.completion_criteria == second.completion_criteria


def test_plan_step_lifecycle_is_explicit_and_terminal_states_do_not_reopen():
    coordinator, goal, task, context = _foundation()
    plan = _plan(coordinator, goal, task, context)
    step = _step(coordinator, plan)
    ready = coordinator.transition_plan_step(step, "ready")
    completed = coordinator.transition_plan_step(ready, "completed")
    assert completed.step_status == "completed"
    with pytest.raises(ValueError, match="invalid plan step transition"):
        coordinator.transition_plan_step(completed, "pending")


def test_snapshots_are_frozen_and_to_dict_does_not_alias_registry_state():
    coordinator, goal, task, context = _foundation()
    constraints = {"items": ["one"]}
    plan = coordinator.create_plan(
        goal,
        task,
        context,
        completion_criteria={"items": constraints["items"]},
        failure_criteria=_criteria("failure"),
        blocked_criteria=_criteria("blocked"),
    )
    constraints["items"].append("two")
    payload = plan.to_dict()
    payload["completion_criteria"]["items"].append("three")
    assert plan.completion_criteria["items"] == ("one",)
    with pytest.raises(FrozenInstanceError):
        plan.plan_status = "ready"


def test_injected_time_is_used_for_plan_and_step_creation():
    values = iter(("t1", "t2", "t3", "t4"))
    coordinator, goal, task, context = _foundation(time_provider=lambda: next(values))
    plan = _plan(coordinator, goal, task, context)
    step = _step(coordinator, plan)
    assert plan.created_at == "t3"
    assert step.created_at == "t4"


def test_plan_and_plan_step_ids_are_fresh_for_each_object():
    coordinator, goal, task, context = _foundation()
    first_plan = _plan(coordinator, goal, task, context)
    second_task = coordinator.create_task(goal)
    second_context = coordinator.select_context(coordinator.context_for_task(second_task))
    second_plan = _plan(coordinator, goal, second_task, second_context)
    first_step = _step(coordinator, first_plan)
    second_step = _step(coordinator, second_plan)
    assert len({first_plan.plan_id, second_plan.plan_id, first_step.plan_step_id, second_step.plan_step_id}) == 4


def test_readiness_is_not_authorization():
    coordinator, goal, task, context = _foundation()
    plan = coordinator.transition_plan(_plan(coordinator, goal, task, context), "ready")
    step = coordinator.transition_plan_step(_step(coordinator, plan), "ready")
    for payload in (plan.to_dict(), step.to_dict()):
        assert "plan_authorized" not in payload
        assert "plan_execution_allowed" not in payload
        assert "step_authorized" not in payload
        assert "generic_action_allowed" not in payload


def test_no_thinking_consumer_governance_evaluation_or_execution_path_exists():
    source = TASK_CONTEXT_SOURCE.read_text(encoding="utf-8")
    for forbidden in (
        "aether.thinking",
        "evaluate_authorization",
        "plan_authorized",
        "execute_tool",
        "tool_service",
        "restricted_read",
        "apply_patch",
        "rollback",
    ):
        assert forbidden not in source


def test_no_api_persistence_chat_loop_or_second_capability_integration_exists():
    source = TASK_CONTEXT_SOURCE.read_text(encoding="utf-8")
    for forbidden in (
        "from fastapi",
        "TestClient",
        "api_server",
        "router",
        "private/",
        "write_text",
        "json.dump",
        "/chat",
        "Observation Intake",
        "scheduler",
    ):
        assert forbidden not in source
