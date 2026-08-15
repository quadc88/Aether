"""In-memory Goal Intake foundation for the Goal-first coordination slice."""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from types import MappingProxyType
from typing import Any, Mapping
import copy
import uuid

from aether.time import clock


GOAL_STATUSES = frozenset(
    {
        "proposed",
        "accepted",
        "active",
        "paused",
        "completed",
        "cancelled",
        "expired",
        "rejected",
    }
)


def _immutable(value: Any) -> Any:
    if isinstance(value, Mapping):
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


def _timestamp() -> str:
    return clock.now_iso()


def _require_text(value: str, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} must be a non-empty string")
    return value


@dataclass(frozen=True)
class Goal:
    """A human objective with an explicitly separate authority reference."""

    goal_id: str
    goal_text: str
    authority_reference: str | None = None
    goal_status: str = "proposed"
    created_at: str = field(default_factory=_timestamp)
    accepted_at: str | None = None
    temporal_scope_reference: str | None = None
    revision: int = 1
    requested_outcome: str | None = None
    goal_constraints: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _require_text(self.goal_id, "goal_id")
        _require_text(self.goal_text, "goal_text")
        if self.goal_status not in GOAL_STATUSES:
            raise ValueError(f"unsupported goal_status: {self.goal_status}")
        if self.revision < 1:
            raise ValueError("revision must be positive")
        if self.goal_status == "accepted" and not self.accepted_at:
            raise ValueError("accepted goals require accepted_at")
        if self.goal_status == "accepted" and not self.authority_reference:
            raise ValueError("accepted goals require authority_reference")
        object.__setattr__(self, "goal_constraints", _immutable(self.goal_constraints or {}))

    @classmethod
    def propose(
        cls,
        goal_text: str,
        *,
        authority_reference: str | None = None,
        temporal_scope_reference: str | None = None,
        requested_outcome: str | None = None,
        goal_constraints: Mapping[str, Any] | None = None,
        created_at: str | None = None,
    ) -> "Goal":
        _require_text(goal_text, "goal_text")
        return cls(
            goal_id=f"goal_{uuid.uuid4().hex}",
            goal_text=goal_text,
            authority_reference=authority_reference,
            temporal_scope_reference=temporal_scope_reference,
            requested_outcome=requested_outcome,
            goal_constraints=goal_constraints or {},
            created_at=created_at or _timestamp(),
        )

    create = propose

    def accept(
        self,
        authority_reference: str | None = None,
        *,
        accepted_at: str | None = None,
    ) -> "Goal":
        """Return an accepted revision only when human authority is explicit."""
        reference = authority_reference or self.authority_reference
        _require_text(reference, "authority_reference")
        if reference.startswith("approval_"):
            raise ValueError("approval_id cannot serve as authority_reference")
        if self.goal_status not in {"proposed", "accepted"}:
            raise ValueError(f"goal cannot be accepted from status {self.goal_status}")
        if self.goal_status == "accepted" and authority_reference is None:
            return self
        return replace(
            self,
            authority_reference=reference,
            goal_status="accepted",
            accepted_at=accepted_at or _timestamp(),
            revision=self.revision + (0 if self.goal_status == "accepted" else 1),
        )

    def reject(self, *, rejected_at: str | None = None) -> "Goal":
        if self.goal_status not in {"proposed", "accepted"}:
            raise ValueError(f"goal cannot be rejected from status {self.goal_status}")
        return replace(self, goal_status="rejected", revision=self.revision + 1)

    def to_dict(self) -> dict[str, Any]:
        return {
            "goal_id": self.goal_id,
            "goal_text": self.goal_text,
            "authority_reference": self.authority_reference,
            "goal_status": self.goal_status,
            "created_at": self.created_at,
            "accepted_at": self.accepted_at,
            "temporal_scope_reference": self.temporal_scope_reference,
            "revision": self.revision,
            "requested_outcome": self.requested_outcome,
            "goal_constraints": _mutable(self.goal_constraints),
        }


class GoalIntake:
    """Small process-local registry for Goal proposals and acceptance."""

    def __init__(self) -> None:
        self._goals: dict[str, Goal] = {}

    def propose(self, **kwargs: Any) -> Goal:
        goal = Goal.propose(**kwargs)
        self._goals[goal.goal_id] = goal
        return goal

    def register(self, goal: Goal) -> Goal:
        if goal.goal_id in self._goals:
            raise ValueError(f"goal already registered: {goal.goal_id}")
        self._goals[goal.goal_id] = goal
        return goal

    def accept(self, goal: Goal | str, authority_reference: str | None = None) -> Goal:
        current = self.get(goal)
        accepted = current.accept(authority_reference)
        self._goals[accepted.goal_id] = accepted
        return accepted

    def get(self, goal: Goal | str) -> Goal:
        goal_id = goal.goal_id if isinstance(goal, Goal) else goal
        try:
            return self._goals[goal_id]
        except KeyError as exc:
            raise KeyError(f"unknown goal: {goal_id}") from exc

    def list(self) -> tuple[Goal, ...]:
        return tuple(self._goals.values())
