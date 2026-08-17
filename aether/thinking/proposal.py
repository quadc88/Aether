"""Immutable structured Thinking proposals for the process-local Plan seam."""

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Literal, Mapping
import copy


PROPOSAL_READY = "PROPOSAL_READY"
PROPOSAL_NOT_READY = "PROPOSAL_NOT_READY"

PROPOSAL_STATES = frozenset({PROPOSAL_READY, PROPOSAL_NOT_READY})
NOT_READY_CATEGORIES = frozenset(
    {
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
    }
)
PROVENANCE_CATEGORIES = (
    "human_goal_authority",
    "goal_source",
    "task_source",
    "task_context_source",
    "thinking_proposal_source",
    "verification_risk_evidence",
    "tool_suggestion_evidence",
    "time_context",
)


def _require_text(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} must be a non-empty string")
    return value


def _freeze(value: Any, field_name: str) -> Any:
    if isinstance(value, Mapping):
        if any(not isinstance(key, str) or not key.strip() for key in value):
            raise ValueError(f"{field_name} must use non-empty string keys")
        return MappingProxyType(
            {key: _freeze(item, f"{field_name}.{key}") for key, item in value.items()}
        )
    if isinstance(value, (list, tuple)):
        return tuple(_freeze(item, field_name) for item in value)
    if isinstance(value, (set, frozenset)):
        raise ValueError(f"{field_name} must be immutable JSON-like data")
    if value is None or isinstance(value, (str, int, float, bool)):
        return copy.deepcopy(value)
    raise ValueError(f"{field_name} must be immutable JSON-like data")


def _thaw(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {key: _thaw(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_thaw(item) for item in value]
    return copy.deepcopy(value)


def _criteria(value: Mapping[str, Any] | None, field_name: str) -> Mapping[str, Any] | None:
    if value is None:
        return None
    if not isinstance(value, Mapping) or not value:
        raise ValueError(f"{field_name} must be a non-empty mapping")
    frozen = _freeze(value, field_name)
    if not isinstance(frozen, Mapping):
        raise ValueError(f"{field_name} must be a mapping")
    return frozen


def _provenance(value: Mapping[str, Any]) -> Mapping[str, Any]:
    if not isinstance(value, Mapping) or not value:
        raise ValueError("provenance must be a non-empty mapping")
    missing = [category for category in PROVENANCE_CATEGORIES if category not in value]
    if missing:
        raise ValueError("provenance is missing categories: " + ", ".join(missing))
    if any(value[category] is None for category in PROVENANCE_CATEGORIES):
        raise ValueError("provenance categories must preserve source references")
    frozen = _freeze(value, "provenance")
    if not isinstance(frozen, Mapping):
        raise ValueError("provenance must be a mapping")
    return frozen


@dataclass(frozen=True)
class ThinkingProposal:
    """Non-authoritative immutable Thinking output for Core Coordination."""

    proposal_id: str
    proposal_revision: int
    created_at: str
    goal_id: str
    task_id: str
    task_context_id: str
    task_context_revision: int
    proposal_state: Literal["PROPOSAL_READY", "PROPOSAL_NOT_READY"]
    proposed_objective: Any = None
    proposed_completion_criteria: Mapping[str, Any] | None = None
    proposed_failure_criteria: Mapping[str, Any] | None = None
    proposed_blocked_criteria: Mapping[str, Any] | None = None
    rationale: Any = None
    constraints_references: Any = None
    assumptions: Any = None
    dependency_proposals: Any = None
    verification_requirement_proposals: Any = None
    risk_evidence_references: Any = None
    requested_action_relation: Any = None
    tool_suggestion_relation: Any = None
    provenance: Mapping[str, Any] = None  # type: ignore[assignment]
    not_ready_reason: Mapping[str, Any] | None = None

    def __post_init__(self) -> None:
        for name in (
            "proposal_id",
            "created_at",
            "goal_id",
            "task_id",
            "task_context_id",
        ):
            _require_text(getattr(self, name), name)
        for name in ("proposal_revision", "task_context_revision"):
            value = getattr(self, name)
            if not isinstance(value, int) or isinstance(value, bool) or value < 1:
                raise ValueError(f"{name} must be a positive integer")
        if self.proposal_state not in PROPOSAL_STATES:
            raise ValueError(f"unsupported proposal_state: {self.proposal_state}")

        object.__setattr__(self, "proposed_objective", _freeze(self.proposed_objective, "proposed_objective"))
        for name in (
            "rationale",
            "constraints_references",
            "assumptions",
            "dependency_proposals",
            "verification_requirement_proposals",
            "risk_evidence_references",
            "requested_action_relation",
            "tool_suggestion_relation",
        ):
            object.__setattr__(self, name, _freeze(getattr(self, name), name))
        for name in (
            "proposed_completion_criteria",
            "proposed_failure_criteria",
            "proposed_blocked_criteria",
        ):
            object.__setattr__(self, name, _criteria(getattr(self, name), name))
        object.__setattr__(self, "provenance", _provenance(self.provenance))

        if self.proposal_state == PROPOSAL_READY:
            if not isinstance(self.proposed_objective, str) or not self.proposed_objective.strip():
                raise ValueError("PROPOSAL_READY requires proposed_objective")
            for name in (
                "proposed_completion_criteria",
                "proposed_failure_criteria",
                "proposed_blocked_criteria",
            ):
                if getattr(self, name) is None:
                    raise ValueError(f"PROPOSAL_READY requires {name}")
            if self.not_ready_reason is not None:
                raise ValueError("PROPOSAL_READY cannot carry not_ready_reason")
        else:
            if not isinstance(self.not_ready_reason, Mapping) or not self.not_ready_reason:
                raise ValueError("PROPOSAL_NOT_READY requires structured not_ready_reason")
            reason = _freeze(self.not_ready_reason, "not_ready_reason")
            if not isinstance(reason, Mapping) or reason.get("category") not in NOT_READY_CATEGORIES:
                raise ValueError("not_ready_reason.category is unsupported")
            object.__setattr__(self, "not_ready_reason", reason)

    def to_dict(self) -> dict[str, Any]:
        return {
            "proposal_id": self.proposal_id,
            "proposal_revision": self.proposal_revision,
            "created_at": self.created_at,
            "goal_id": self.goal_id,
            "task_id": self.task_id,
            "task_context_id": self.task_context_id,
            "task_context_revision": self.task_context_revision,
            "proposal_state": self.proposal_state,
            "proposed_objective": _thaw(self.proposed_objective),
            "proposed_completion_criteria": _thaw(self.proposed_completion_criteria),
            "proposed_failure_criteria": _thaw(self.proposed_failure_criteria),
            "proposed_blocked_criteria": _thaw(self.proposed_blocked_criteria),
            "rationale": _thaw(self.rationale),
            "constraints_references": _thaw(self.constraints_references),
            "assumptions": _thaw(self.assumptions),
            "dependency_proposals": _thaw(self.dependency_proposals),
            "verification_requirement_proposals": _thaw(self.verification_requirement_proposals),
            "risk_evidence_references": _thaw(self.risk_evidence_references),
            "requested_action_relation": _thaw(self.requested_action_relation),
            "tool_suggestion_relation": _thaw(self.tool_suggestion_relation),
            "provenance": _thaw(self.provenance),
            "not_ready_reason": _thaw(self.not_ready_reason),
        }
