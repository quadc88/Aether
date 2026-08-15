"""Process-local Core Coordination Task and authoritative TaskContext objects."""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from threading import RLock
from typing import Any, Callable, Mapping
import copy
import uuid

from aether.core.goal import GOAL_STATUSES, Goal, GoalIntake
from aether.time import clock


TASK_STATUSES = frozenset({"active", "waiting", "paused", "completed", "cancelled", "blocked"})


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


class CoreCoordination:
    """Owns process-local Task continuity and explicit current-context selection."""

    def __init__(self, *, time_provider: Callable[[], str] | None = None) -> None:
        self._lock = RLock()
        self._time_provider = time_provider or clock.now_iso
        self._goals = GoalIntake()
        self._tasks: dict[str, Task] = {}
        self._contexts: dict[str, TaskContext] = {}
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
