"""Dry-Run Sandbox Contract Builder for Aether (Milestone 58A).

Produces a contract object that determines whether a dry-run record is
eligible for a future safe simulation.  This module does NOT execute any
dry-run, call executors, apply changes, or modify persistent state.
"""

from __future__ import annotations

# Action types allowed for sandbox simulation planning.
_ALLOWED_ACTION_TYPES = frozenset({
    "status_check",
    "read_only_check",
    "inspection",
    "validation",
    "report_generation",
    "plan_review",
})

_REQUIRED_SANDBOX_REQUIREMENTS = [
    "Use isolated sandbox context.",
    "Do not call real external tools.",
    "Do not modify persistent state.",
    "Do not write to target systems.",
    "Do not apply changes.",
    "Do not rollback changes.",
    "Capture simulated observations only.",
]

_REQUIRED_EXPECTED_OBSERVATIONS = [
    "simulation_plan",
    "expected_inputs",
    "expected_outputs",
    "risk_notes",
    "verification_points",
]

_REQUIRED_FORBIDDEN_OPERATIONS = [
    "real_tool_execution",
    "filesystem_mutation",
    "network_call",
    "database_write",
    "identity_seed_modification",
    "private_memory_modification",
    "apply",
    "rollback",
]

_REQUIRED_PRECONDITIONS = [
    "Dry-run record exists.",
    "Dry-run record status is pending.",
    "Dry-run request exists.",
    "Requested action is present.",
    "Approval validation snapshot exists.",
]

_REQUIRED_POSTCONDITIONS = [
    "No real tools were executed.",
    "No target state was modified.",
    "No apply or rollback occurred.",
    "Dry-run execution flag remains false.",
    "A later milestone may create a simulation result record.",
]


def build_dry_run_sandbox_contract(
    dry_run_record: dict | None,
    context: dict | None = None,
) -> dict:
    """Build a sandbox-contract decision for a dry-run record.

    Returns a contract dict describing eligibility for sandbox simulation
    planning.  All execution flags remain False in Milestone 58A.

    Args:
        dry_run_record: The saved dry-run record dict (may be None).
        context: Optional metadata context (e.g. session_id).

    Returns:
        Contract dict with ``contract_valid``, ``decision``, and related fields.
    """
    # Shared empty-result baseline
    _empty = {
        "contract_valid": False,
        "decision": "",
        "reason": "",
        "dry_run_id": None,
        "dry_run_status": None,
        "requested_action": None,
        "allowed_simulation_mode": None,
        "sandbox_requirements": list(_REQUIRED_SANDBOX_REQUIREMENTS),
        "expected_observations": list(_REQUIRED_EXPECTED_OBSERVATIONS),
        "forbidden_operations": list(_REQUIRED_FORBIDDEN_OPERATIONS),
        "preconditions": list(_REQUIRED_PRECONDITIONS),
        "postconditions": list(_REQUIRED_POSTCONDITIONS),
        "execution_allowed": False,
        "tool_execution_allowed": False,
        "apply_allowed": False,
        "rollback_allowed": False,
        "dry_run_execution_allowed": False,
        "warnings": [],
        "metadata": {"source": "dry_run_sandbox_contract_builder", "schema_version": "1.0"},
    }
    if context and isinstance(context, dict):
        sid = context.get("session_id")
        if sid:
            _empty["metadata"]["session_id"] = sid

    # Rule 1: missing dry_run_record
    if dry_run_record is None:
        result = dict(_empty)
        result["decision"] = "not_found"
        result["reason"] = "Dry-run record was not found."
        return result

    dry_run_id = dry_run_record.get("dry_run_id")
    result = dict(_empty)
    result["dry_run_id"] = dry_run_id
    result["dry_run_status"] = dry_run_record.get("status")

    # Rule 2: missing dry_run_request
    dr_req = dry_run_record.get("dry_run_request")
    if not dr_req:
        result["decision"] = "invalid_record"
        result["reason"] = "Dry-run record is missing a valid dry-run request."
        return result

    # Rule 3: status != pending
    status = dry_run_record.get("status")
    if status != "pending":
        result["decision"] = "not_pending"
        result["reason"] = f"Dry-run record is not pending (status={status})."
        return result

    # Rule 4: dry_run_executed already true
    if dry_run_record.get("dry_run_executed") is True:
        result["decision"] = "invalid_record"
        result["reason"] = "Dry-run record is already marked executed."
        return result

    # Rule 5: requested_action missing
    ra = dr_req.get("requested_action")
    if not ra:
        result["decision"] = "invalid_record"
        result["reason"] = "Requested action is missing from dry-run request."
        return result

    result["requested_action"] = ra

    # Rule 6: check action_type against allowed list
    action_type = ra.get("action_type")
    if action_type not in _ALLOWED_ACTION_TYPES:
        result["decision"] = "unsafe_action_type"
        result["reason"] = "Requested action type is not allowed for sandbox simulation planning."
        return result

    # Rule 7: valid — allow simulation_planning
    result["contract_valid"] = True
    result["decision"] = "allow_simulation_planning"
    result["reason"] = "Dry-run record is eligible for sandbox simulation planning."
    result["allowed_simulation_mode"] = "contract_only"

    # Safety: ALL execution flags stay false in Milestone 58A
    result["execution_allowed"] = False
    result["tool_execution_allowed"] = False
    result["apply_allowed"] = False
    result["rollback_allowed"] = False
    result["dry_run_execution_allowed"] = False

    # Warnings
    warnings: list[str] = []
    if "parameters" in ra:
        warnings.append("Parameters must be treated as simulation inputs only.")
    if "target" in ra:
        warnings.append("Target must not be modified during sandbox planning.")
    result["warnings"] = warnings

    return result
