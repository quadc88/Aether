"""Process-local Core Coordination Task and authoritative TaskContext objects."""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from importlib import import_module
from threading import RLock
from typing import Any, Callable, Mapping
import copy
import uuid

from aether.core.goal import GOAL_STATUSES, Goal, GoalIntake
from aether.time import clock


TASK_STATUSES = frozenset({"active", "waiting", "paused", "completed", "cancelled", "blocked"})

PLAN_STATUSES = frozenset({"draft", "ready", "blocked", "completed", "failed", "cancelled"})
PLAN_STEP_STATUSES = frozenset(
    {"pending", "ready", "blocked", "completed", "failed", "cancelled"}
)

PLAN_TRANSITIONS = {
    "draft": frozenset({"ready", "blocked", "failed", "cancelled"}),
    "ready": frozenset({"blocked", "completed", "failed", "cancelled"}),
    "blocked": frozenset({"ready", "failed", "cancelled"}),
    "completed": frozenset(),
    "failed": frozenset(),
    "cancelled": frozenset(),
}
PLAN_STEP_TRANSITIONS = {
    "pending": frozenset({"ready", "blocked", "failed", "cancelled"}),
    "ready": frozenset({"blocked", "completed", "failed", "cancelled"}),
    "blocked": frozenset({"ready", "failed", "cancelled"}),
    "completed": frozenset(),
    "failed": frozenset(),
    "cancelled": frozenset(),
}


def _immutable(value: Any) -> Any:
    if isinstance(value, Mapping):
        from types import MappingProxyType

        return MappingProxyType({key: _immutable(item) for key, item in value.items()})
    if isinstance(value, list):
        return tuple(_immutable(item) for item in value)
    if isinstance(value, tuple):
        return tuple(_immutable(item) for item in value)
    if isinstance(value, set):
        return frozenset(_immutable(item) for item in value)
    return copy.deepcopy(value)


def _mutable(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {key: _mutable(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_mutable(item) for item in value]
    if isinstance(value, frozenset):
        return {_mutable(item) for item in value}
    return copy.deepcopy(value)


def _require_text(value: str, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} must be a non-empty string")
    return value


def _criteria(value: Mapping[str, Any], field_name: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping) or not value:
        raise ValueError(f"{field_name} must be a non-empty mapping")

    def valid(item: Any) -> bool:
        if isinstance(item, Mapping):
            return bool(item) and all(
                isinstance(key, str) and key.strip() and valid(child)
                for key, child in item.items()
            )
        if isinstance(item, (list, tuple)):
            return all(valid(child) for child in item)
        return item is None or isinstance(item, (str, int, float, bool))

    if not valid(value):
        raise ValueError(f"{field_name} must be immutable JSON-like data")
    try:
        return _immutable(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field_name} must be immutable JSON-like data") from exc


@dataclass(frozen=True)
class Task:
    task_id: str
    goal_id: str
    task_status: str = "active"
    created_at: str = ""
    activated_at: str | None = None
    task_scope: Any = None
    task_constraints: Mapping[str, Any] = field(default_factory=dict)
    task_context_id: str = ""
    current_plan_id: str | None = None
    current_plan_step_id: str | None = None
    completion_criteria_reference: str | None = None
    governance_context_reference: str | None = None
    time_context_reference: str | None = None
    revision: int = 1

    def __post_init__(self) -> None:
        _require_text(self.task_id, "task_id")
        _require_text(self.goal_id, "goal_id")
        _require_text(self.task_context_id, "task_context_id")
        if self.task_status not in TASK_STATUSES:
            raise ValueError(f"unsupported task_status: {self.task_status}")
        if self.revision < 1:
            raise ValueError("revision must be positive")
        object.__setattr__(self, "task_scope", _immutable(self.task_scope))
        object.__setattr__(self, "task_constraints", _immutable(self.task_constraints or {}))

    def to_dict(self) -> dict[str, Any]:
        return {
            "task_id": self.task_id,
            "goal_id": self.goal_id,
            "task_status": self.task_status,
            "created_at": self.created_at,
            "activated_at": self.activated_at,
            "task_scope": _mutable(self.task_scope),
            "task_constraints": _mutable(self.task_constraints),
            "task_context_id": self.task_context_id,
            "current_plan_id": self.current_plan_id,
            "current_plan_step_id": self.current_plan_step_id,
            "completion_criteria_reference": self.completion_criteria_reference,
            "governance_context_reference": self.governance_context_reference,
            "time_context_reference": self.time_context_reference,
            "revision": self.revision,
        }


@dataclass(frozen=True)
class TaskContext:
    task_context_id: str
    task_id: str
    goal_id: str
    context_revision: int = 1
    created_at: str = ""
    updated_at: str = ""
    task_status: str = "active"
    execution_phase: str = "initial"
    current_plan_id: str | None = None
    current_plan_step_id: str | None = None
    completion_criteria_reference: str | None = None
    governance_context_reference: str | None = None
    approval_references: tuple[str, ...] = ()
    permission_references: tuple[str, ...] = ()
    time_context_reference: str | None = None
    working_memory_references: tuple[str, ...] = ()
    observation_references: tuple[str, ...] = ()
    verification_references: tuple[str, ...] = ()
    selection_metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in ("task_context_id", "task_id", "goal_id", "execution_phase"):
            _require_text(getattr(self, name), name)
        if self.context_revision < 1:
            raise ValueError("context_revision must be positive")
        if self.task_status not in TASK_STATUSES:
            raise ValueError(f"unsupported task_status: {self.task_status}")
        object.__setattr__(self, "selection_metadata", _immutable(self.selection_metadata or {}))
        for name in (
            "approval_references",
            "permission_references",
            "working_memory_references",
            "observation_references",
            "verification_references",
        ):
            object.__setattr__(self, name, tuple(getattr(self, name)))

    def evolve(self, *, updated_at: str, **changes: Any) -> "TaskContext":
        """Create a new immutable context snapshot with an incremented revision."""
        return replace(
            self,
            **changes,
            context_revision=self.context_revision + 1,
            updated_at=updated_at,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "task_context_id": self.task_context_id,
            "task_id": self.task_id,
            "goal_id": self.goal_id,
            "context_revision": self.context_revision,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "task_status": self.task_status,
            "execution_phase": self.execution_phase,
            "current_plan_id": self.current_plan_id,
            "current_plan_step_id": self.current_plan_step_id,
            "completion_criteria_reference": self.completion_criteria_reference,
            "governance_context_reference": self.governance_context_reference,
            "approval_references": list(self.approval_references),
            "permission_references": list(self.permission_references),
            "time_context_reference": self.time_context_reference,
            "working_memory_references": list(self.working_memory_references),
            "observation_references": list(self.observation_references),
            "verification_references": list(self.verification_references),
            "selection_metadata": _mutable(self.selection_metadata),
        }


@dataclass(frozen=True)
class ContextSelection:
    task_context_id: str
    selected_at: str
    previous_task_context_id: str | None = None


@dataclass(frozen=True)
class Plan:
    """Canonical process-local Plan owned by Core Coordination."""

    plan_id: str
    goal_id: str
    task_id: str
    task_context_id: str
    task_context_revision: int
    task_context_snapshot: Mapping[str, Any]
    completion_criteria: Mapping[str, Any]
    failure_criteria: Mapping[str, Any]
    blocked_criteria: Mapping[str, Any]
    plan_status: str = "draft"
    plan_step_ids: tuple[str, ...] = ()
    created_at: str = ""
    updated_at: str = ""
    plan_revision: int = 1
    proposal_provenance: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in ("plan_id", "goal_id", "task_id", "task_context_id"):
            _require_text(getattr(self, name), name)
        if self.plan_status not in PLAN_STATUSES:
            raise ValueError(f"unsupported plan_status: {self.plan_status}")
        if self.task_context_revision < 1 or self.plan_revision < 1:
            raise ValueError("plan revisions must be positive")
        if not isinstance(self.task_context_snapshot, Mapping):
            raise ValueError("task_context_snapshot must be a mapping")
        object.__setattr__(self, "task_context_snapshot", _immutable(self.task_context_snapshot))
        for name in ("completion_criteria", "failure_criteria", "blocked_criteria"):
            object.__setattr__(self, name, _criteria(getattr(self, name), name))
        if not isinstance(self.proposal_provenance, Mapping):
            raise ValueError("proposal_provenance must be a mapping")
        object.__setattr__(self, "proposal_provenance", _immutable(self.proposal_provenance))
        object.__setattr__(self, "plan_step_ids", tuple(self.plan_step_ids))

    def to_dict(self) -> dict[str, Any]:
        return {
            "plan_id": self.plan_id,
            "goal_id": self.goal_id,
            "task_id": self.task_id,
            "task_context_id": self.task_context_id,
            "task_context_revision": self.task_context_revision,
            "task_context_snapshot": _mutable(self.task_context_snapshot),
            "completion_criteria": _mutable(self.completion_criteria),
            "failure_criteria": _mutable(self.failure_criteria),
            "blocked_criteria": _mutable(self.blocked_criteria),
            "plan_status": self.plan_status,
            "plan_step_ids": list(self.plan_step_ids),
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "plan_revision": self.plan_revision,
            "proposal_provenance": _mutable(self.proposal_provenance),
        }


@dataclass(frozen=True)
class PlanStep:
    """Canonical process-local PlanStep owned by exactly one Plan."""

    plan_step_id: str
    plan_id: str
    goal_id: str
    task_id: str
    task_context_id: str
    task_context_revision: int
    task_context_snapshot: Mapping[str, Any]
    sequence_index: int
    completion_criteria: Mapping[str, Any]
    failure_criteria: Mapping[str, Any]
    blocked_criteria: Mapping[str, Any]
    step_status: str = "pending"
    created_at: str = ""
    updated_at: str = ""
    step_revision: int = 1

    def __post_init__(self) -> None:
        for name in (
            "plan_step_id",
            "plan_id",
            "goal_id",
            "task_id",
            "task_context_id",
        ):
            _require_text(getattr(self, name), name)
        if not isinstance(self.sequence_index, int) or isinstance(self.sequence_index, bool):
            raise ValueError("sequence_index must be an integer")
        if self.sequence_index < 1:
            raise ValueError("sequence_index must be positive")
        if self.step_status not in PLAN_STEP_STATUSES:
            raise ValueError(f"unsupported step_status: {self.step_status}")
        if self.task_context_revision < 1 or self.step_revision < 1:
            raise ValueError("step revisions must be positive")
        if not isinstance(self.task_context_snapshot, Mapping):
            raise ValueError("task_context_snapshot must be a mapping")
        object.__setattr__(self, "task_context_snapshot", _immutable(self.task_context_snapshot))
        for name in ("completion_criteria", "failure_criteria", "blocked_criteria"):
            object.__setattr__(self, name, _criteria(getattr(self, name), name))

    def to_dict(self) -> dict[str, Any]:
        return {
            "plan_step_id": self.plan_step_id,
            "plan_id": self.plan_id,
            "goal_id": self.goal_id,
            "task_id": self.task_id,
            "task_context_id": self.task_context_id,
            "task_context_revision": self.task_context_revision,
            "task_context_snapshot": _mutable(self.task_context_snapshot),
            "sequence_index": self.sequence_index,
            "completion_criteria": _mutable(self.completion_criteria),
            "failure_criteria": _mutable(self.failure_criteria),
            "blocked_criteria": _mutable(self.blocked_criteria),
            "step_status": self.step_status,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "step_revision": self.step_revision,
        }


class CoreCoordination:
    """Owns process-local Task continuity and explicit current-context selection."""

    def __init__(self, *, time_provider: Callable[[], str] | None = None) -> None:
        self._lock = RLock()
        self._time_provider = time_provider or clock.now_iso
        self._goals = GoalIntake()
        self._tasks: dict[str, Task] = {}
        self._contexts: dict[str, TaskContext] = {}
        self._plans: dict[str, Plan] = {}
        self._plan_steps: dict[str, PlanStep] = {}
        self._selected_context_id: str | None = None
        self._selection_history: list[ContextSelection] = []

    def _now(self) -> str:
        return self._time_provider()

    def create_goal(self, goal_text: str, **kwargs: Any) -> Goal:
        with self._lock:
            return self._goals.propose(goal_text=goal_text, **kwargs)

    def register_goal(self, goal: Goal) -> Goal:
        with self._lock:
            return self._goals.register(goal)

    def accept_goal(self, goal: Goal | str, authority_reference: str | None = None) -> Goal:
        with self._lock:
            return self._goals.accept(goal, authority_reference)

    def get_goal(self, goal: Goal | str) -> Goal:
        with self._lock:
            return self._goals.get(goal)

    def create_task(
        self,
        goal: Goal | str,
        *,
        task_scope: Any = None,
        task_constraints: Mapping[str, Any] | None = None,
        governance_context_reference: str | None = None,
        time_context_reference: str | None = None,
    ) -> Task:
        """Atomically create one Task and its first authoritative TaskContext."""
        with self._lock:
            accepted_goal = self._goals.get(goal)
            if accepted_goal.goal_status not in {"accepted", "active"}:
                raise ValueError(
                    f"task requires an accepted goal, got {accepted_goal.goal_status}"
                )

            timestamp = self._now()
            task_id = f"task_{uuid.uuid4().hex}"
            context_id = f"task_context_{uuid.uuid4().hex}"
            task = Task(
                task_id=task_id,
                goal_id=accepted_goal.goal_id,
                created_at=timestamp,
                activated_at=timestamp,
                task_scope=task_scope,
                task_constraints=task_constraints or {},
                task_context_id=context_id,
                governance_context_reference=governance_context_reference,
                time_context_reference=time_context_reference,
            )
            context = TaskContext(
                task_context_id=context_id,
                task_id=task_id,
                goal_id=accepted_goal.goal_id,
                created_at=timestamp,
                updated_at=timestamp,
                governance_context_reference=governance_context_reference,
                time_context_reference=time_context_reference,
            )
            self._tasks[task_id] = task
            self._contexts[context_id] = context
            return task

    create_task_from_goal = create_task

    def get_task(self, task: Task | str) -> Task:
        task_id = task.task_id if isinstance(task, Task) else task
        with self._lock:
            try:
                return self._tasks[task_id]
            except KeyError as exc:
                raise KeyError(f"unknown task: {task_id}") from exc

    def get_context(self, context: TaskContext | str) -> TaskContext:
        context_id = context.task_context_id if isinstance(context, TaskContext) else context
        with self._lock:
            try:
                return self._contexts[context_id]
            except KeyError as exc:
                raise KeyError(f"unknown task context: {context_id}") from exc

    def context_for_task(self, task: Task | str) -> TaskContext:
        return self.get_context(self.get_task(task).task_context_id)

    def update_context(self, context: TaskContext | str, **changes: Any) -> TaskContext:
        with self._lock:
            current = self.get_context(context)
            updated = current.evolve(updated_at=self._now(), **changes)
            self._contexts[current.task_context_id] = updated
            task = self._tasks[current.task_id]
            self._tasks[current.task_id] = replace(
                task,
                task_status=updated.task_status,
                current_plan_id=updated.current_plan_id,
                current_plan_step_id=updated.current_plan_step_id,
                completion_criteria_reference=updated.completion_criteria_reference,
                revision=task.revision + 1,
            )
            return updated

    def select_context(self, context: TaskContext | str) -> TaskContext:
        with self._lock:
            selected = self.get_context(context)
            if selected.task_status not in {"active", "waiting", "paused"}:
                raise ValueError(
                    f"cannot select context for task status {selected.task_status}"
                )
            previous = self._selected_context_id
            self._selected_context_id = selected.task_context_id
            self._selection_history.append(
                ContextSelection(
                    task_context_id=selected.task_context_id,
                    selected_at=self._now(),
                    previous_task_context_id=previous,
                )
            )
            return selected

    def switch_context(self, context: TaskContext | str) -> TaskContext:
        return self.select_context(context)

    @property
    def selected_context_id(self) -> str | None:
        with self._lock:
            return self._selected_context_id

    def selected_context(self) -> TaskContext | None:
        with self._lock:
            if self._selected_context_id is None:
                return None
            return self._contexts[self._selected_context_id]

    def _resolve_current_plan(self, plan: Plan | str) -> Plan:
        plan_id = plan.plan_id if isinstance(plan, Plan) else plan
        try:
            current = self._plans[plan_id]
        except KeyError as exc:
            raise KeyError(f"unknown plan: {plan_id}") from exc
        if isinstance(plan, Plan) and current != plan:
            raise ValueError("plan snapshot is stale or not authoritative")
        return current

    def _resolve_current_plan_step(self, plan_step: PlanStep | str) -> PlanStep:
        plan_step_id = plan_step.plan_step_id if isinstance(plan_step, PlanStep) else plan_step
        try:
            current = self._plan_steps[plan_step_id]
        except KeyError as exc:
            raise KeyError(f"unknown plan step: {plan_step_id}") from exc
        if isinstance(plan_step, PlanStep) and current != plan_step:
            raise ValueError("plan step snapshot is stale or not authoritative")
        return current

    def _validate_plan_binding(
        self,
        goal: Goal | str,
        task: Task | str,
        task_context: TaskContext | str,
    ) -> tuple[Goal, Task, TaskContext]:
        current_goal = self._goals.get(goal)
        if isinstance(goal, Goal) and current_goal != goal:
            raise ValueError("goal snapshot is stale or not authoritative")
        current_task = self.get_task(task)
        if isinstance(task, Task) and current_task != task:
            raise ValueError("task snapshot is stale or not authoritative")
        current_context = self.get_context(task_context)
        if isinstance(task_context, TaskContext) and current_context != task_context:
            raise ValueError("task context snapshot is stale or not authoritative")
        if current_goal.goal_status not in {"accepted", "active"}:
            raise ValueError("plan requires an accepted goal")
        if current_task.task_status not in {"active", "waiting", "paused"}:
            raise ValueError("plan requires a non-terminal task")
        if current_task.goal_id != current_goal.goal_id:
            raise ValueError("task is not owned by the goal")
        if current_context.task_context_id != current_task.task_context_id:
            raise ValueError("task context is not owned by the task")
        if current_context.task_id != current_task.task_id:
            raise ValueError("task context/task relationship is invalid")
        if current_context.goal_id != current_goal.goal_id:
            raise ValueError("task context/goal relationship is invalid")
        if self._selected_context_id != current_context.task_context_id:
            raise ValueError("plan requires an explicitly selected task context")
        return current_goal, current_task, current_context

    def _bind_plan_reference(self, plan_id: str, task: Task, context: TaskContext, timestamp: str) -> None:
        updated_context = context.evolve(updated_at=timestamp, current_plan_id=plan_id)
        self._contexts[context.task_context_id] = updated_context
        self._tasks[task.task_id] = replace(
            task,
            current_plan_id=plan_id,
            revision=task.revision + 1,
        )

    def _bind_plan_step_reference(self, plan_step_id: str, plan: Plan, timestamp: str) -> None:
        current_context = self._contexts[plan.task_context_id]
        updated_context = current_context.evolve(
            updated_at=timestamp,
            current_plan_id=plan.plan_id,
            current_plan_step_id=plan_step_id,
        )
        self._contexts[plan.task_context_id] = updated_context
        task = self._tasks[plan.task_id]
        self._tasks[plan.task_id] = replace(
            task,
            current_plan_id=plan.plan_id,
            current_plan_step_id=plan_step_id,
            revision=task.revision + 1,
        )

    def create_plan(
        self,
        goal: Goal | str,
        task: Task | str,
        task_context: TaskContext | str,
        *,
        completion_criteria: Mapping[str, Any],
        failure_criteria: Mapping[str, Any],
        blocked_criteria: Mapping[str, Any],
        proposal_provenance: Mapping[str, Any] | None = None,
    ) -> Plan:
        """Create a canonical Plan from an explicitly selected context snapshot."""
        with self._lock:
            current_goal, current_task, current_context = self._validate_plan_binding(
                goal, task, task_context
            )
            timestamp = self._now()
            plan = Plan(
                plan_id=f"plan_{uuid.uuid4().hex}",
                goal_id=current_goal.goal_id,
                task_id=current_task.task_id,
                task_context_id=current_context.task_context_id,
                task_context_revision=current_context.context_revision,
                task_context_snapshot=current_context.to_dict(),
                completion_criteria=completion_criteria,
                failure_criteria=failure_criteria,
                blocked_criteria=blocked_criteria,
                created_at=timestamp,
                updated_at=timestamp,
                proposal_provenance=proposal_provenance or {},
            )
            self._plans[plan.plan_id] = plan
            self._bind_plan_reference(plan.plan_id, current_task, current_context, timestamp)
            return plan

    create_canonical_plan = create_plan

    def materialize_thinking_proposal(self, proposal: Any) -> Plan:
        """Materialize one ready proposal under the authoritative context."""
        proposal_type = import_module("aether." + "thinking.proposal").ThinkingProposal
        if not isinstance(proposal, proposal_type):
            raise TypeError("proposal must be a ThinkingProposal")
        if proposal.proposal_state == "PROPOSAL_NOT_READY":
            raise ValueError(
                "cannot materialize PROPOSAL_NOT_READY: "
                f"{dict(proposal.not_ready_reason)}"
            )

        with self._lock:
            current_goal = self._goals.get(proposal.goal_id)
            current_task = self.get_task(proposal.task_id)
            current_context = self.get_context(proposal.task_context_id)
            if current_task.goal_id != proposal.goal_id:
                raise ValueError("thinking proposal Task is not owned by its Goal")
            if current_context.task_id != proposal.task_id:
                raise ValueError("thinking proposal TaskContext is not owned by its Task")
            if current_context.goal_id != proposal.goal_id:
                raise ValueError("thinking proposal TaskContext is not owned by its Goal")
            if current_context.context_revision != proposal.task_context_revision:
                raise ValueError("thinking proposal TaskContext revision is stale")
            if self._selected_context_id != proposal.task_context_id:
                raise ValueError("thinking proposal requires its TaskContext to be selected")
            self._validate_plan_binding(current_goal, current_task, current_context)
            return self.create_plan(
                current_goal,
                current_task,
                current_context,
                completion_criteria=proposal.proposed_completion_criteria,
                failure_criteria=proposal.proposed_failure_criteria,
                blocked_criteria=proposal.proposed_blocked_criteria,
                proposal_provenance=proposal.provenance,
            )

    def get_plan(self, plan: Plan | str) -> Plan:
        with self._lock:
            return self._resolve_current_plan(plan)

    def evaluate_canonical_plan_governance(
        self,
        plan: Plan | str,
        selected_plan_step: PlanStep | str | None = None,
    ):
        """Pass one current Plan/PlanStep binding to Core Governance."""
        from aether.core.governance import (
            CanonicalPlanGovernanceEvaluationRequest,
            evaluate_canonical_plan_governance,
        )

        with self._lock:
            binding_errors: list[str] = []
            try:
                current_plan = self._resolve_current_plan(plan)
            except ValueError:
                if not isinstance(plan, Plan) or plan.plan_id not in self._plans:
                    raise
                current_plan = self._plans[plan.plan_id]
                binding_errors.append("stale_plan_snapshot")
            current_goal = self._goals.get(current_plan.goal_id)
            current_task = self._tasks[current_plan.task_id]
            current_context = self._contexts[current_plan.task_context_id]

            if isinstance(plan, Plan) and plan != current_plan and "stale_plan_snapshot" not in binding_errors:
                binding_errors.append("stale_plan_snapshot")
            if current_goal.goal_id != current_plan.goal_id:
                binding_errors.append("invalid_plan_goal_binding")
            if current_task.goal_id != current_goal.goal_id:
                binding_errors.append("invalid_plan_task_goal_binding")
            if current_context.task_id != current_task.task_id or current_context.goal_id != current_goal.goal_id:
                binding_errors.append("invalid_task_context_parent_binding")
            if self._selected_context_id != current_context.task_context_id:
                binding_errors.append("selected_context_is_not_current")
            if current_task.current_plan_id != current_plan.plan_id or current_context.current_plan_id != current_plan.plan_id:
                binding_errors.append("invalid_current_plan_binding")

            context_snapshot = current_plan.task_context_snapshot
            ignored_context_fields = {
                "context_revision",
                "updated_at",
                "current_plan_id",
                "current_plan_step_id",
            }
            current_context_payload = current_context.to_dict()
            def normalized(value: Any) -> Any:
                if isinstance(value, Mapping):
                    return {key: normalized(item) for key, item in value.items()}
                if isinstance(value, (list, tuple)):
                    return tuple(normalized(item) for item in value)
                return value

            if any(
                normalized(context_snapshot.get(key)) != normalized(value)
                for key, value in current_context_payload.items()
                if key not in ignored_context_fields
            ):
                binding_errors.append("stale_task_context_snapshot")

            current_step = None
            selected_step_snapshot = None
            if selected_plan_step is None:
                binding_errors.append("missing_selected_plan_step")
            else:
                try:
                    current_step = self._resolve_current_plan_step(selected_plan_step)
                except ValueError:
                    if not isinstance(selected_plan_step, PlanStep) or selected_plan_step.plan_step_id not in self._plan_steps:
                        raise
                    current_step = self._plan_steps[selected_plan_step.plan_step_id]
                    binding_errors.append("stale_plan_step_snapshot")
                selected_step_snapshot = current_step.to_dict()
                if isinstance(selected_plan_step, PlanStep) and selected_plan_step != current_step and "stale_plan_step_snapshot" not in binding_errors:
                    binding_errors.append("stale_plan_step_snapshot")
                if current_step.plan_id != current_plan.plan_id:
                    binding_errors.append("selected_plan_step_has_wrong_plan_parent")
                if current_step.plan_step_id not in current_plan.plan_step_ids:
                    binding_errors.append("selected_plan_step_is_not_in_plan")
                if current_context.current_plan_step_id != current_step.plan_step_id:
                    binding_errors.append("selected_plan_step_is_not_current")

            request = CanonicalPlanGovernanceEvaluationRequest(
                goal_id=current_goal.goal_id,
                task_id=current_task.task_id,
                task_context_id=current_context.task_context_id,
                task_context_revision=current_plan.task_context_revision,
                selected_context_id=self._selected_context_id,
                plan_id=current_plan.plan_id,
                plan_revision=current_plan.plan_revision,
                plan_step_id=current_step.plan_step_id if current_step else None,
                plan_step_revision=current_step.step_revision if current_step else None,
                plan_snapshot=current_plan.to_dict(),
                current_plan_snapshot=current_plan.to_dict(),
                plan_step_snapshot=selected_step_snapshot,
                current_plan_step_snapshot=selected_step_snapshot,
                task_context_snapshot=current_context_payload,
                proposal_provenance=current_plan.proposal_provenance,
                binding_errors=tuple(binding_errors),
                hard_constraints={
                    "goal_constraints": current_goal.to_dict()["goal_constraints"],
                    "task_constraints": current_task.to_dict()["task_constraints"],
                },
                soft_signals={},
            )
            return evaluate_canonical_plan_governance(request)

    def transition_plan(self, plan: Plan | str, new_status: str) -> Plan:
        with self._lock:
            current = self._resolve_current_plan(plan)
            if new_status not in PLAN_STATUSES:
                raise ValueError(f"unsupported plan_status: {new_status}")
            if new_status not in PLAN_TRANSITIONS[current.plan_status]:
                raise ValueError(
                    f"invalid plan transition: {current.plan_status} -> {new_status}"
                )
            updated = replace(
                current,
                plan_status=new_status,
                plan_revision=current.plan_revision + 1,
                updated_at=self._now(),
            )
            self._plans[current.plan_id] = updated
            return updated

    update_plan_status = transition_plan

    def create_plan_step(
        self,
        plan: Plan | str,
        *,
        sequence_index: int,
        completion_criteria: Mapping[str, Any],
        failure_criteria: Mapping[str, Any],
        blocked_criteria: Mapping[str, Any],
    ) -> PlanStep:
        """Create one fresh, explicitly ordered PlanStep under one Plan."""
        with self._lock:
            current_plan = self._resolve_current_plan(plan)
            if current_plan.plan_status not in {"draft", "ready"}:
                raise ValueError("cannot add a step to the current plan status")
            if not isinstance(sequence_index, int) or isinstance(sequence_index, bool):
                raise ValueError("sequence_index must be an integer")
            if sequence_index < 1:
                raise ValueError("sequence_index must be positive")
            if any(
                self._plan_steps[step_id].sequence_index == sequence_index
                for step_id in current_plan.plan_step_ids
            ):
                raise ValueError("duplicate sequence_index in plan")
            timestamp = self._now()
            plan_step = PlanStep(
                plan_step_id=f"plan_step_{uuid.uuid4().hex}",
                plan_id=current_plan.plan_id,
                goal_id=current_plan.goal_id,
                task_id=current_plan.task_id,
                task_context_id=current_plan.task_context_id,
                task_context_revision=current_plan.task_context_revision,
                task_context_snapshot=current_plan.task_context_snapshot,
                sequence_index=sequence_index,
                completion_criteria=completion_criteria,
                failure_criteria=failure_criteria,
                blocked_criteria=blocked_criteria,
                created_at=timestamp,
                updated_at=timestamp,
            )
            self._plan_steps[plan_step.plan_step_id] = plan_step
            ordered_step_ids = tuple(
                sorted(
                    (*current_plan.plan_step_ids, plan_step.plan_step_id),
                    key=lambda step_id: self._plan_steps[step_id].sequence_index,
                )
            )
            updated_plan = replace(
                current_plan,
                plan_step_ids=ordered_step_ids,
                plan_revision=current_plan.plan_revision + 1,
                updated_at=timestamp,
            )
            self._plans[current_plan.plan_id] = updated_plan
            self._bind_plan_step_reference(plan_step.plan_step_id, current_plan, timestamp)
            return plan_step

    create_canonical_plan_step = create_plan_step

    def get_plan_step(self, plan_step: PlanStep | str) -> PlanStep:
        with self._lock:
            return self._resolve_current_plan_step(plan_step)

    def transition_plan_step(self, plan_step: PlanStep | str, new_status: str) -> PlanStep:
        with self._lock:
            current = self._resolve_current_plan_step(plan_step)
            if new_status not in PLAN_STEP_STATUSES:
                raise ValueError(f"unsupported step_status: {new_status}")
            if new_status not in PLAN_STEP_TRANSITIONS[current.step_status]:
                raise ValueError(
                    f"invalid plan step transition: {current.step_status} -> {new_status}"
                )
            updated = replace(
                current,
                step_status=new_status,
                step_revision=current.step_revision + 1,
                updated_at=self._now(),
            )
            self._plan_steps[current.plan_step_id] = updated
            return updated

    update_plan_step_status = transition_plan_step

    def list_plans(self) -> tuple[Plan, ...]:
        with self._lock:
            return tuple(self._plans.values())

    def list_plan_steps(self, plan: Plan | str | None = None) -> tuple[PlanStep, ...]:
        with self._lock:
            if plan is None:
                return tuple(self._plan_steps.values())
            current_plan = self._resolve_current_plan(plan)
            return tuple(self._plan_steps[step_id] for step_id in current_plan.plan_step_ids)

    @property
    def selection_history(self) -> tuple[ContextSelection, ...]:
        with self._lock:
            return tuple(self._selection_history)

    def list_tasks(self) -> tuple[Task, ...]:
        with self._lock:
            return tuple(self._tasks.values())

    def list_contexts(self) -> tuple[TaskContext, ...]:
        with self._lock:
            return tuple(self._contexts.values())


TaskContextCoordinator = CoreCoordination
