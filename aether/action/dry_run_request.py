"""Dry-Run Request Builder for Aether (Milestone 56A).

Creates structured dry_run_request objects when approval validation
returns allow_dry_run and dry_run_allowed is True.

This object is only a structured request — it does NOT execute any
dry-run, call any executor, apply changes, or modify persistent state.
"""

from __future__ import annotations


def build_dry_run_request(
    approval_validation: dict | None,
    requested_action: dict | None,
    context: dict | None = None,
) -> dict | None:
    """Build a structured dry-run request when validation permits it.

    Returns None when dry-run is not allowed.

    Args:
        approval_validation: Result from validate_approval_for_action().
        requested_action: The action being proposed for dry-run.
        context: Optional metadata context (e.g. session_id).

    Returns:
        Dry-run request dict or None.
    """
    # Rule 1: no validation result
    if approval_validation is None:
        return None

    # Rule 2: approval not valid
    if approval_validation.get("approval_valid") is not True:
        return None

    # Rule 3: decision is not allow_dry_run
    if approval_validation.get("decision") != "allow_dry_run":
        return None

    # Rule 4: dry_run_allowed is not True
    if approval_validation.get("dry_run_allowed") is not True:
        return None

    # Rule 5: requested_action missing
    if not requested_action:
        return None

    # --- Build warnings for safety anomalies ---
    warnings: list[str] = []
    if approval_validation.get("execution_allowed") is True:
        warnings.append(
            "WARNING: approval_validation unexpectedly has execution_allowed=true."
        )
    if approval_validation.get("tool_execution_allowed") is True:
        warnings.append(
            "WARNING: approval_validation unexpectedly has tool_execution_allowed=true."
        )

    # --- Build metadata ---
    metadata = {
        "source": "dry_run_request_builder",
        "schema_version": "1.0",
    }
    if context and isinstance(context, dict):
        sid = context.get("session_id")
        if sid:
            metadata["session_id"] = sid

    return {
        "dry_run_required": True,
        "dry_run_status": "pending",
        "dry_run_type": "action_simulation",
        "reason": "Approval validated; dry-run may be considered by a future stage.",
        "approval_id": approval_validation.get("approval_id"),
        "approval_status": approval_validation.get("approval_status"),
        "requested_action": dict(requested_action),
        "approval_validation_snapshot": dict(approval_validation),
        "execution_allowed": False,
        "tool_execution_allowed": False,
        "apply_allowed": False,
        "rollback_allowed": False,
        "summary": "Dry-run request pending for approved action.",
        "safety_checks": [
            "Verify approval validation before dry-run.",
            "Verify requested action matches approved action.",
            "Verify dry-run does not execute real tools.",
            "Verify no persistent state is modified during dry-run.",
            "Verify apply remains disabled.",
        ],
        "metadata": metadata,
        "warnings": warnings,
    }
