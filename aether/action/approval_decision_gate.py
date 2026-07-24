"""Approval Decision Gate for Aether (Milestone 55A).

Validates whether a requested action may proceed beyond approval stage by
checking an approval record's status and matching the requested action against
the originally approved action.

This module does NOT execute tools, perform dry-runs, apply changes, or
modify any approval record state.  It only reads records and returns
validation results.
"""

from __future__ import annotations


# Fields considered required to match between approved and requested actions.
_REQUIRED_MATCH_FIELDS = {"tool_id", "action_type", "name", "target"}


def validate_approval_for_action(
    approval_id: str | None,
    requested_action: dict | None,
    context: dict | None = None,
) -> dict:
    """Validate that a requested action is covered by an approved record.

    Returns a validation result dict.  See the docstring below for the full
    schema.

    Args:
        approval_id: Id of an existing approval record.
        requested_action: The action dict being validated against the record.
        context: Optional context (not used in current version).

    Returns:
        Validation result dict with ``approval_valid``, ``decision``,
        ``execution_allowed``, ``dry_run_allowed``, ``tool_execution_allowed``, etc.
    """
    # ----- shared baseline for all errors -----
    _null_result = {
        "approval_valid": False,
        "decision": "",
        "reason": "",
        "approval_id": approval_id,
        "approval_status": None,
        "requested_action": requested_action,
        "approval_record": None,
        "matched_fields": [],
        "mismatched_fields": [],
        "execution_allowed": False,
        "dry_run_allowed": False,
        "tool_execution_allowed": False,
        "warnings": [],
    }

    # --- Rule 1: missing approval_id ---
    if not approval_id:
        result = dict(_null_result)
        result["decision"] = "missing_approval"
        result["reason"] = "Approval id is required."
        return result

    # --- Rule 2: missing requested_action ---
    if not requested_action:
        result = dict(_null_result)
        result["decision"] = "invalid_request"
        result["reason"] = "Requested action is required."
        return result

    # --- Rule 3: load record ---
    from aether.action.approval_queue import get_approval_record as _get_rec
    record = _get_rec(approval_id)
    if record is None:
        result = dict(_null_result)
        result["approval_id"] = approval_id
        result["decision"] = "not_found"
        result["reason"] = "Approval record was not found."
        return result

    # --- Rule 4: check status ---
    status = record.get("status")
    result = dict(_null_result)
    result["approval_id"] = approval_id
    result["approval_status"] = status
    result["approval_record"] = record

    if status != "approved":
        result["decision"] = "not_approved"
        result["reason"] = "Approval record is not approved."
        return result

    # --- Rule 5: action matching ---
    approved_action = record.get("approval_request", {}).get("requested_action")
    matched: list[str] = []
    mismatched: list[str] = []
    warnings: list[str] = []

    if approved_action is None:
        # No approved action defined — cannot match anything concrete
        result["decision"] = "action_mismatch"
        result["reason"] = "Requested action does not match the approved action."
        result["mismatched_fields"] = ["requested_action is None in approval_record"]
        return result

    # Compare fields
    for field in _REQUIRED_MATCH_FIELDS:
        approved_val = approved_action.get(field)
        requested_val = requested_action.get(field)
        if approved_val is not None:
            if approved_val == requested_val:
                matched.append(field)
            else:
                mismatched.append(field)
        elif field in requested_action:
            # Approved action doesn't specify this field but requested does
            matched.append(field)

    # Check parameters if present
    approved_params = approved_action.get("parameters")
    requested_params = requested_action.get("parameters")
    if approved_params is not None:
        if approved_params == requested_params:
            matched.append("parameters")
        else:
            mismatched.append("parameters")

    # Check extra fields in requested_action
    all_approved_keys = set(approved_action.keys())
    for key in requested_action:
        if key not in all_approved_keys and key not in matched:
            warnings.append(f"Extra field '{key}' in requested_action not present in approved action.")

    # Determine match success
    has_core_match = bool(set(matched) & _REQUIRED_MATCH_FIELDS)
    if not has_core_match or mismatched:
        result["decision"] = "action_mismatch"
        result["reason"] = "Requested action does not match the approved action."
        result["matched_fields"] = matched
        result["mismatched_fields"] = mismatched
        result["warnings"] = warnings
        return result

    # --- Rule 6: valid match ---
    result["approval_valid"] = True
    result["decision"] = "allow_dry_run"
    result["reason"] = (
        "Approval is valid for this requested action. "
        "Dry-run may be considered by a future stage."
    )
    result["matched_fields"] = matched
    result["mismatched_fields"] = mismatched
    result["warnings"] = warnings
    result["dry_run_allowed"] = True

    # Safety: always deny execution
    result["execution_allowed"] = False
    result["tool_execution_allowed"] = False

    return result
