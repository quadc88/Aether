"""Observation Record Builder for Aether (Milestone 82B).

Defines the declarative ObservationRecord — the schema for the missing
Observe stage of the cognitive loop. An ObservationRecord represents what
an observed outcome looks like: what was observed, what was expected,
whether they matched, and which plan step or evidence item it relates to.

This is a pure declarative builder. It does NOT:
- observe anything
- collect evidence
- execute tools
- persist records
- perform apply/rollback
- perform any filesystem, network, or subprocess operation

It prepares a safe, JSON-serializable shape for future evidence-based
verification, critic analysis, and repair planning.
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone


VALID_STATUSES = frozenset({"pending", "matched", "mismatched", "error"})


def _ensure_json_serializable(value: object, path: str = "") -> None:
    """Raise ValueError if value cannot be JSON-serialized."""
    try:
        json.dumps(value)
    except (TypeError, OverflowError, ValueError) as exc:
        raise ValueError(
            f"Value at {path} is not JSON-serializable: {exc}"
        ) from exc


def _generate_observation_id() -> str:
    """Generate a unique observation identifier."""
    return uuid.uuid4().hex


def _iso_now() -> str:
    """Return current UTC ISO timestamp."""
    return datetime.now(timezone.utc).isoformat()


def build_observation_record(
    *,
    plan_step_id: str | None = None,
    evidence_item_id: str | None = None,
    target: str,
    observed_value: object | None = None,
    expected_value: object | None = None,
    status: str = "pending",
    collector_contract_id: str | None = None,
    metadata: dict | None = None,
) -> dict:
    """Build a declarative ObservationRecord dict.

    Args:
        plan_step_id: ID of the executor plan step that produced this observation.
        evidence_item_id: ID of the evidence contract item this observation relates to.
        target: What was observed (e.g. file path, API response, system metric).
        observed_value: The actual observed value. Must be JSON-serializable.
        expected_value: The expected value (from plan or contract). Must be JSON-serializable.
        status: One of "pending", "matched", "mismatched", "error".
        collector_contract_id: Optional ID of the collector contract that produced this observation.
        metadata: Optional dict of additional metadata. Must be JSON-serializable.

    Returns:
        A dict with all observation fields and safety flags set to False.

    Raises:
        ValueError: If validation fails.
    """
    if not plan_step_id and not evidence_item_id:
        raise ValueError(
            "At least one of plan_step_id or evidence_item_id must be provided."
        )

    if not target or not isinstance(target, str):
        raise ValueError("target must be a non-empty string.")

    if status not in VALID_STATUSES:
        raise ValueError(
            f"Invalid status '{status}'. Must be one of: {', '.join(sorted(VALID_STATUSES))}."
        )

    resolved_metadata = metadata if metadata is not None else {}
    if not isinstance(resolved_metadata, dict):
        raise ValueError("metadata must be a dict or None.")

    _ensure_json_serializable(resolved_metadata, "metadata")
    _ensure_json_serializable(observed_value, "observed_value")
    _ensure_json_serializable(expected_value, "expected_value")

    return {
        "observation_id": _generate_observation_id(),
        "observation_type": "observation_record",
        "plan_step_id": plan_step_id,
        "evidence_item_id": evidence_item_id,
        "collector_contract_id": collector_contract_id,
        "target": target,
        "observed_value": observed_value,
        "expected_value": expected_value,
        "status": status,
        "observed_at": _iso_now(),
        "metadata": resolved_metadata,
        "safety_flags": {
            "tool_execution_allowed": False,
            "tool_executed": False,
            "evidence_collection_performed": False,
            "system_state_modified": False,
            "apply_performed": False,
            "rollback_performed": False,
            "persistent_write_performed": False,
            "external_side_effect_performed": False,
        },
    }
