"""Simulation Plan Builder for Aether (Milestone 59A).

Creates a structured simulation_plan object when an approved sandbox contract
permits simulation planning.  This object is only a plan — it does NOT execute
any simulation, call any executor, apply changes, or modify persistent state.
"""

from __future__ import annotations

_SIMULATION_STEPS = [
    {
        "step": 1,
        "name": "Review requested action",
        "description": "Inspect the requested action without executing it.",
        "executes_tool": False,
        "mutates_state": False,
    },
    {
        "step": 2,
        "name": "Prepare simulated inputs",
        "description": "Identify inputs that would be needed for a future simulation.",
        "executes_tool": False,
        "mutates_state": False,
    },
    {
        "step": 3,
        "name": "Define expected observations",
        "description": "Describe what a safe simulation should observe.",
        "executes_tool": False,
        "mutates_state": False,
    },
    {
        "step": 4,
        "name": "Define verification points",
        "description": "List evidence needed to verify a future dry-run result.",
        "executes_tool": False,
        "mutates_state": False,
    },
    {
        "step": 5,
        "name": "Confirm no execution",
        "description": "Confirm that this plan does not execute tools or modify state.",
        "executes_tool": False,
        "mutates_state": False,
    },
]


def _build_expected_inputs(ra: dict) -> list[str]:
    inputs: list[str] = []
    if ra.get("tool_id"):
        inputs.append("requested_action.tool_id")
    if ra.get("action_type"):
        inputs.append("requested_action.action_type")
    if ra.get("parameters"):
        inputs.append("requested_action.parameters")
    if ra.get("target"):
        inputs.append("requested_action.target")
    inputs.extend(["sandbox_contract", "dry_run_record_reference"])
    return inputs


def build_simulation_plan(
    sandbox_contract: dict | None,
    context: dict | None = None,
) -> dict | None:
    """Build a structured simulation plan when the sandbox contract permits it.

    Returns None when simulation planning is not allowed.

    Args:
        sandbox_contract: Result from build_dry_run_sandbox_contract().
        context: Optional metadata context (e.g. session_id).

    Returns:
        Simulation plan dict or None.
    """
    # Rule 1: no contract
    if sandbox_contract is None:
        return None

    # Rule 2: contract not valid
    if sandbox_contract.get("contract_valid") is not True:
        return None

    # Rule 3: decision not allow_simulation_planning
    if sandbox_contract.get("decision") != "allow_simulation_planning":
        return None

    # Rule 4: not contract_only mode
    if sandbox_contract.get("allowed_simulation_mode") != "contract_only":
        return None

    # Rule 5: no requested_action
    ra = sandbox_contract.get("requested_action")
    if not ra:
        return None

    # --- Build warnings ---
    warnings: list[str] = []
    # Copy sandbox warnings
    for w in sandbox_contract.get("warnings", []):
        warnings.append(f"sandbox_warning: {w}")
    # Parameter warning
    if ra.get("parameters"):
        warnings.append("Parameters are plan inputs only.")
    # Target warning
    if ra.get("target"):
        warnings.append("Target must not be modified.")

    # --- Build expected_inputs ---
    expected_inputs = _build_expected_inputs(ra)

    # --- Build risk_notes ---
    risk_notes: list[str] = [
        "Simulation plan is not execution.",
        "Future dry-run execution must remain sandboxed.",
        "Any tool call requires a later explicit execution milestone.",
    ]
    forb = sandbox_contract.get("forbidden_operations", [])
    if forb:
        risk_notes.append(f"Forbidden operations: {', '.join(forb)}.")

    # --- Build metadata ---
    metadata: dict = {
        "source": "simulation_plan_builder",
        "schema_version": "1.0",
    }
    if context and isinstance(context, dict):
        sid = context.get("session_id")
        if sid:
            metadata["session_id"] = sid

    return {
        "simulation_plan_required": True,
        "simulation_plan_status": "pending",
        "simulation_plan_type": "contract_only_plan",
        "reason": "Sandbox contract is valid; simulation plan may be prepared.",
        "dry_run_id": sandbox_contract.get("dry_run_id"),
        "dry_run_status": sandbox_contract.get("dry_run_status"),
        "requested_action": dict(ra),
        "sandbox_contract_snapshot": dict(sandbox_contract),
        "simulation_steps": list(_SIMULATION_STEPS),
        "expected_inputs": list(expected_inputs),
        "expected_outputs": [
            "simulation_result_status",
            "simulated_observations",
            "verification_evidence",
            "risk_findings",
            "no_mutation_confirmation",
        ],
        "verification_points": [
            "Requested action matches approved action.",
            "Sandbox contract is valid.",
            "No real tools are executed.",
            "No persistent state is modified.",
            "No apply or rollback occurs.",
            "All simulation steps are non-mutating.",
        ],
        "risk_notes": risk_notes,
        "observation_requirements": [
            "Capture planned inputs.",
            "Capture simulated outputs only.",
            "Capture verification evidence.",
            "Capture no-mutation proof.",
            "Capture any safety warning.",
        ],
        "execution_allowed": False,
        "tool_execution_allowed": False,
        "dry_run_execution_allowed": False,
        "apply_allowed": False,
        "rollback_allowed": False,
        "summary": "Simulation plan pending for sandbox-approved dry-run.",
        "metadata": metadata,
        "warnings": warnings,
    }
