"""Focused runtime locks for the M96G Plan Governance evaluation seam."""

from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

from aether.core.governance import (
    CanonicalPlanGovernanceEvaluation,
    CanonicalPlanGovernanceEvaluationRequest,
    evaluate_canonical_plan_governance,
)
from aether.core.task_context import CoreCoordination


ROOT = Path(__file__).resolve().parents[1]
TASK_CONTEXT_SOURCE = ROOT / "aether/core/task_context.py"
GOVERNANCE_SOURCE = ROOT / "aether/core/governance.py"


def _criteria(label: str) -> dict[str, str]:
    return {"description": label}


def _foundation():
    coordinator = CoreCoordination(time_provider=lambda: "2026-08-17T00:00:00+00:00")
    goal = coordinator.accept_goal(
        coordinator.create_goal("Evaluate a bounded canonical plan"), "human:m96g"
    )
    task = coordinator.create_task(goal, task_constraints={"scope": "bounded"})
    context = coordinator.select_context(coordinator.context_for_task(task))
    plan = coordinator.create_plan(
        goal,
        task,
        context,
        completion_criteria=_criteria("plan complete"),
        failure_criteria=_criteria("plan failed"),
        blocked_criteria=_criteria("plan blocked"),
        proposal_provenance={"source": "M96G test proposal"},
    )
    step = coordinator.create_plan_step(
        plan,
        sequence_index=1,
        completion_criteria=_criteria("step complete"),
        failure_criteria=_criteria("step failed"),
        blocked_criteria=_criteria("step blocked"),
    )
    return (
        coordinator,
        goal,
        task,
        coordinator.context_for_task(task),
        coordinator.get_plan(plan.plan_id),
        coordinator.get_plan_step(step.plan_step_id),
    )


def _request(coordinator, goal, task, context, plan, step, **overrides):
    values = {
        "goal_id": goal.goal_id,
        "task_id": task.task_id,
        "task_context_id": context.task_context_id,
        "task_context_revision": plan.task_context_revision,
        "selected_context_id": context.task_context_id,
        "plan_id": plan.plan_id,
        "plan_revision": plan.plan_revision,
        "plan_step_id": step.plan_step_id if step else None,
        "plan_step_revision": step.step_revision if step else None,
        "plan_snapshot": plan.to_dict(),
        "current_plan_snapshot": plan.to_dict(),
        "plan_step_snapshot": step.to_dict() if step else None,
        "current_plan_step_snapshot": step.to_dict() if step else None,
        "task_context_snapshot": context.to_dict(),
        "proposal_provenance": plan.proposal_provenance,
        "hard_constraints": {},
        "soft_signals": {},
    }
    values.update(overrides)
    return CanonicalPlanGovernanceEvaluationRequest(**values)


def test_request_is_immutable_and_does_not_alias_inputs():
    coordinator, goal, task, context, plan, step = _foundation()
    provenance = {"source": {"kind": "proposal"}}
    request = _request(
        coordinator,
        goal,
        task,
        context,
        plan,
        step,
        proposal_provenance=provenance,
        plan_snapshot={**plan.to_dict(), "nested": {"items": ["one"]}},
    )
    provenance["source"]["kind"] = "mutated"
    assert request.proposal_provenance["source"]["kind"] == "proposal"
    assert request.plan_snapshot["nested"]["items"] == ("one",)
    with pytest.raises(FrozenInstanceError):
        request.plan_id = "changed"


def test_result_is_immutable_and_explicitly_non_authorizing():
    result = CanonicalPlanGovernanceEvaluation(
        evaluation_status="EVALUATED", reason="checked", proposal_provenance={"source": "test"}
    )
    assert result.consumer_boundary == "before_generic_act"
    assert result.authorization_granted is False
    assert result.execution_allowed is False
    assert result.action_dispatch_allowed is False
    assert result.to_dict()["consumer_boundary"] == "before_generic_act"
    with pytest.raises(FrozenInstanceError):
        result.reason = "changed"


def test_coordination_calls_governance_for_current_plan_and_selected_step():
    coordinator, goal, task, context, plan, step = _foundation()
    result = coordinator.evaluate_canonical_plan_governance(plan, step)
    assert result.evaluation_status == "EVALUATED"
    assert result.governance_decision == "evaluate"
    assert (result.goal_id, result.task_id, result.task_context_id) == (
        goal.goal_id,
        task.task_id,
        context.task_context_id,
    )
    assert (result.plan_id, result.plan_step_id) == (plan.plan_id, step.plan_step_id)
    assert result.proposal_provenance["source"] == "M96G test proposal"


def test_missing_selected_plan_step_is_not_evaluable():
    coordinator, _goal, _task, _context, plan, _step = _foundation()
    result = coordinator.evaluate_canonical_plan_governance(plan)
    assert result.evaluation_status == "NOT_EVALUABLE"
    assert "missing_selected_plan_step" in result.reason


def test_switching_context_fails_closed_as_invalid_context():
    coordinator, goal, task, context, plan, step = _foundation()
    other_task = coordinator.create_task(goal)
    coordinator.select_context(coordinator.context_for_task(other_task))
    result = coordinator.evaluate_canonical_plan_governance(plan, step)
    assert result.evaluation_status == "INVALID_CONTEXT"
    assert "selected_context_is_not_current" in result.reason


def test_changed_context_snapshot_fails_closed_as_stale_context():
    coordinator, _goal, _task, context, plan, step = _foundation()
    coordinator.update_context(context, execution_phase="understand")
    result = coordinator.evaluate_canonical_plan_governance(plan, step)
    assert result.evaluation_status == "STALE_CONTEXT"
    assert "stale_task_context_snapshot" in result.reason


def test_stale_plan_snapshot_fails_closed_as_invalid_plan():
    coordinator, _goal, _task, _context, plan, step = _foundation()
    coordinator.transition_plan(plan, "ready")
    result = coordinator.evaluate_canonical_plan_governance(plan, step)
    assert result.evaluation_status == "INVALID_PLAN"
    assert "stale_plan_snapshot" in result.reason


def test_stale_plan_step_snapshot_fails_closed_as_invalid_plan():
    coordinator, _goal, _task, _context, plan, step = _foundation()
    coordinator.transition_plan_step(step, "ready")
    result = coordinator.evaluate_canonical_plan_governance(plan, step)
    assert result.evaluation_status == "INVALID_PLAN"
    assert "stale_plan_step_snapshot" in result.reason


def test_planstep_from_another_plan_cannot_be_selected():
    coordinator, goal, _task, context, plan, step = _foundation()
    other_task = coordinator.create_task(goal)
    other_context = coordinator.select_context(coordinator.context_for_task(other_task))
    other_plan = coordinator.create_plan(
        goal,
        other_task,
        other_context,
        completion_criteria=_criteria("other complete"),
        failure_criteria=_criteria("other failed"),
        blocked_criteria=_criteria("other blocked"),
    )
    other_step = coordinator.create_plan_step(
        other_plan,
        sequence_index=1,
        completion_criteria=_criteria("other step complete"),
        failure_criteria=_criteria("other step failed"),
        blocked_criteria=_criteria("other step blocked"),
    )
    coordinator.select_context(context)
    result = coordinator.evaluate_canonical_plan_governance(plan, other_step)
    assert result.evaluation_status == "INVALID_PLAN"
    assert "wrong_plan_parent" in result.reason
    assert step.plan_id != other_step.plan_id


def test_plan_parent_identity_is_checked_by_governance():
    coordinator, goal, task, context, plan, step = _foundation()
    request = _request(
        coordinator,
        goal,
        task,
        context,
        plan,
        step,
        plan_snapshot={**plan.to_dict(), "task_id": "task_wrong_parent"},
    )
    result = evaluate_canonical_plan_governance(request)
    assert result.evaluation_status == "INVALID_PLAN"
    assert "parent binding" in result.reason


def test_task_context_identity_is_checked_by_governance():
    coordinator, goal, task, context, plan, step = _foundation()
    request = _request(
        coordinator,
        goal,
        task,
        context,
        plan,
        step,
        task_context_snapshot={**context.to_dict(), "task_id": "task_wrong_parent"},
    )
    result = evaluate_canonical_plan_governance(request)
    assert result.evaluation_status == "INVALID_CONTEXT"
    assert "TaskContext identity" in result.reason


def test_plan_and_step_revision_freshness_is_checked():
    coordinator, goal, task, context, plan, step = _foundation()
    request = _request(
        coordinator,
        goal,
        task,
        context,
        plan,
        step,
        plan_revision=plan.plan_revision - 1,
    )
    result = evaluate_canonical_plan_governance(request)
    assert result.evaluation_status == "INVALID_PLAN"
    assert "revision is stale" in result.reason


def test_terminal_plan_is_not_evaluable():
    coordinator, _goal, _task, _context, plan, step = _foundation()
    ready = coordinator.transition_plan(plan, "ready")
    completed = coordinator.transition_plan(ready, "completed")
    result = coordinator.evaluate_canonical_plan_governance(completed, step)
    assert result.evaluation_status == "INVALID_PLAN"
    assert "terminal" in result.reason


def test_blocked_plan_returns_blocked_without_authority():
    coordinator, _goal, _task, _context, plan, step = _foundation()
    blocked = coordinator.transition_plan(plan, "blocked")
    result = coordinator.evaluate_canonical_plan_governance(blocked, step)
    assert result.evaluation_status == "BLOCKED"
    assert result.governance_decision == "block"
    assert result.execution_allowed is False


def test_blocked_planstep_returns_blocked_without_authority():
    coordinator, _goal, _task, _context, plan, step = _foundation()
    blocked = coordinator.transition_plan_step(step, "blocked")
    result = coordinator.evaluate_canonical_plan_governance(plan, blocked)
    assert result.evaluation_status == "BLOCKED"
    assert result.governance_decision == "block"


def test_hard_constraints_block_before_any_positive_evaluation():
    coordinator, goal, task, context, plan, step = _foundation()
    request = _request(
        coordinator,
        goal,
        task,
        context,
        plan,
        step,
        hard_constraints={"blocked": True},
    )
    result = evaluate_canonical_plan_governance(request)
    assert result.evaluation_status == "BLOCKED"
    assert result.governance_decision == "block"


def test_soft_signals_never_override_hard_constraints():
    coordinator, goal, task, context, plan, step = _foundation()
    request = _request(
        coordinator,
        goal,
        task,
        context,
        plan,
        step,
        hard_constraints={"blocked": True},
        soft_signals={"preferred": True},
    )
    result = evaluate_canonical_plan_governance(request)
    assert result.evaluation_status == "BLOCKED"
    assert result.execution_allowed is False


def test_provenance_is_preserved_as_evidence_only():
    coordinator, goal, task, context, plan, step = _foundation()
    provenance = {"thinking": {"proposal_id": "proposal_1"}}
    request = _request(
        coordinator,
        goal,
        task,
        context,
        plan,
        step,
        proposal_provenance=provenance,
    )
    result = evaluate_canonical_plan_governance(request)
    provenance["thinking"]["proposal_id"] = "mutated"
    assert result.proposal_provenance["thinking"]["proposal_id"] == "proposal_1"
    assert result.authorization_granted is False


def test_evaluation_result_has_no_action_scope_or_approval_authority():
    coordinator, goal, task, context, plan, step = _foundation()
    result = coordinator.evaluate_canonical_plan_governance(plan, step)
    payload = result.to_dict()
    assert payload["authorization_granted"] is False
    assert payload["execution_allowed"] is False
    assert payload["action_dispatch_allowed"] is False
    assert "scope" not in payload
    assert "approval_satisfied" not in payload


def test_non_request_input_fails_closed():
    result = evaluate_canonical_plan_governance(object())
    assert result.evaluation_status == "NOT_EVALUABLE"
    assert result.authorization_granted is False


def test_request_rejects_mutable_set_data():
    coordinator, goal, task, context, plan, step = _foundation()
    with pytest.raises(ValueError, match="immutable JSON-like"):
        _request(
            coordinator,
            goal,
            task,
            context,
            plan,
            step,
            soft_signals={"unsupported": {"set-value"}},
        )


def test_governance_contract_is_process_local_and_has_no_execution_wiring():
    task_context_source = TASK_CONTEXT_SOURCE.read_text(encoding="utf-8")
    governance_source = GOVERNANCE_SOURCE.read_text(encoding="utf-8")
    for forbidden in (
        "from fastapi",
        "api_server",
        "json.dump",
        "dispatch_restricted_read",
        "execute_tool",
        "apply_patch",
        "rollback",
    ):
        assert forbidden not in task_context_source
        assert forbidden not in governance_source


def test_coordination_is_the_caller_and_governance_is_the_decision_owner():
    task_context_source = TASK_CONTEXT_SOURCE.read_text(encoding="utf-8")
    governance_source = GOVERNANCE_SOURCE.read_text(encoding="utf-8")
    assert "evaluate_canonical_plan_governance(request)" in task_context_source
    assert "def evaluate_canonical_plan_governance(" in governance_source
    assert "from aether.core.task_context" not in governance_source


def test_evaluator_does_not_treat_readiness_as_execution_authorization():
    coordinator, _goal, _task, _context, plan, step = _foundation()
    ready_plan = coordinator.transition_plan(plan, "ready")
    ready_step = coordinator.transition_plan_step(step, "ready")
    result = coordinator.evaluate_canonical_plan_governance(ready_plan, ready_step)
    assert result.evaluation_status == "EVALUATED"
    assert result.authorization_granted is False
    assert result.execution_allowed is False
    assert result.action_dispatch_allowed is False
