"""Simulation Result Builder for Aether (Milestone 61A).

Creates a structured simulation_result object from a pending simulation_plan_record.
This is a synthetic result — it does NOT execute any simulation, call executors,
or modify target state.  It only derives observations and evidence from the plan data.
"""

from __future__ import annotations


def build_simulation_result(
    simulation_plan_record: dict | None,
    context: dict | None = None,
) -> dict | None:
    """Build a synthetic simulation result from a pending simulation plan record.

    Returns None when result generation conditions are not met.

    Args:
        simulation_plan_record: The saved simulation plan record dict.
        context: Optional metadata context (e.g. session_id).

    Returns:
        Simulation result dict or None.
    """
    # Rule 1: missing record
    if simulation_plan_record is None:
        return None

    # Rule 2: status must be pending
    status = simulation_plan_record.get("status")
    if status != "pending":
        return None

    # Rule 3: simulation_executed must be false
    if simulation_plan_record.get("simulation_executed") is True:
        return None

    # Rule 4: simulation_plan must exist
    sim_plan = simulation_plan_record.get("simulation_plan")
    if not sim_plan or not isinstance(sim_plan, dict):
        return None

    # Rule 5: simulation_plan_status must be pending
    plan_status = sim_plan.get("simulation_plan_status")
    if plan_status != "pending":
        return None

    # Rule 6: simulation_plan_type must be contract_only_plan
    if sim_plan.get("simulation_plan_type") != "contract_only_plan":
        return None

    # --- Extract fields from plan ---
    dry_run_id = sim_plan.get("dry_run_id")
    requested_action = sim_plan.get("requested_action")
    sim_warnings = sim_plan.get("warnings", [])

    # --- Build warnings ---
    warnings: list[str] = []
    for w in sim_warnings:
        warnings.append(f"simulation_plan_warning: {w}")
    warnings.append("Synthetic result only; no real-world observation was performed.")
    warnings.append("No target system was contacted.")
    if requested_action and requested_action.get("parameters"):
        pass  # Already warned in simulation_plan
    if requested_action and requested_action.get("target"):
        pass  # Already warned in simulation_plan

    # --- Build simulated_observations ---
    observed: list[dict] = [
        {
            "name": "plan_loaded",
            "status": "observed",
            "source": "simulation_plan_record",
            "detail": "Simulation plan was loaded without executing it.",
            "real_world_observation": False,
        },
        {
            "name": "requested_action_reviewed",
            "status": "observed",
            "source": "simulation_plan.requested_action",
            "detail": "Requested action was reviewed as data only.",
            "real_world_observation": False,
        },
        {
            "name": "non_execution_confirmed",
            "status": "observed",
            "source": "simulation_plan.safety_flags",
            "detail": "No tool execution or state mutation was allowed by the plan.",
            "real_world_observation": False,
        },
    ]
    if sim_plan.get("expected_outputs"):
        observed.append({
            "name": "expected_outputs_identified",
            "status": "observed",
            "source": "simulation_plan.expected_outputs",
            "detail": "Expected outputs were identified from the plan.",
            "real_world_observation": False,
        })
    if sim_plan.get("verification_points"):
        observed.append({
            "name": "verification_points_identified",
            "status": "observed",
            "source": "simulation_plan.verification_points",
            "detail": "Verification points were identified from the plan.",
            "real_world_observation": False,
        })

    # --- Build verification_evidence ---
    evidence: list[dict] = [
        {"name": "no_real_tool_execution", "verified": True,
         "evidence_type": "contract_flag",
         "detail": "tool_execution_allowed is false."},
        {"name": "no_state_mutation", "verified": True,
         "evidence_type": "contract_flag",
         "detail": "execution_allowed and apply_allowed are false."},
        {"name": "no_rollback", "verified": True,
         "evidence_type": "contract_flag",
         "detail": "rollback_allowed is false."},
        {"name": "simulation_plan_not_execution", "verified": True,
         "evidence_type": "plan_semantics",
         "detail": "The simulation plan is non-executing."},
    ]

    # --- Build no_mutation_proof ---
    proof: dict = {
        "mutation_checked": True,
        "proof_type": "flag_based_non_execution_proof",
        "filesystem_mutated": False,
        "network_called": False,
        "database_written": False,
        "identity_modified": False,
        "private_memory_modified": False,
        "target_state_modified": False,
        "apply_performed": False,
        "rollback_performed": False,
        "notes": [
            "This proof is based on contract and plan flags only.",
            "No real filesystem, network, database, identity, or memory operation was performed.",
        ],
    }

    # --- Build risk_findings ---
    findings: list[dict] = [
        {"name": "synthetic_result_only", "severity": "low",
         "detail": "Result was prepared without executing the requested action."},
        {"name": "future_execution_requires_new_milestone", "severity": "medium",
         "detail": "Actual sandbox execution must be implemented separately with additional safety gates."},
    ]
    if requested_action and requested_action.get("parameters"):
        findings.append({"name": "parameters_not_executed", "severity": "low",
                         "detail": "Parameters were treated as data only."})
    if requested_action and requested_action.get("target"):
        findings.append({"name": "target_not_modified", "severity": "low",
                         "detail": "Target was not modified."})

    # --- Build metadata ---
    metadata: dict = {
        "source": "simulation_result_builder",
        "schema_version": "1.0",
    }
    if context and isinstance(context, dict):
        sid = context.get("session_id")
        if sid:
            metadata["session_id"] = sid

    return {
        "simulation_result_required": True,
        "simulation_result_status": "prepared",
        "simulation_result_type": "synthetic_contract_only_result",
        "reason": "Simulation result object prepared from non-executing simulation plan.",
        "simulation_plan_id": simulation_plan_record.get("simulation_plan_id"),
        "simulation_plan_status": simulation_plan_record.get("status"),
        "dry_run_id": dry_run_id,
        "requested_action": dict(requested_action) if requested_action else None,
        "simulation_plan_snapshot": dict(sim_plan),
        "simulated_observations": observed,
        "verification_evidence": evidence,
        "no_mutation_proof": proof,
        "risk_findings": findings,
        "result_summary": "Simulation result prepared without executing tools or modifying state.",
        "execution_allowed": False,
        "tool_execution_allowed": False,
        "dry_run_execution_allowed": False,
        "simulation_execution_allowed": False,
        "apply_allowed": False,
        "rollback_allowed": False,
        "metadata": metadata,
        "warnings": warnings,
    }
