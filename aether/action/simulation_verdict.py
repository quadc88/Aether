"""Simulation Verification Verdict Builder for Aether (Milestone 63A).

Creates a structured verification_verdict object from a simulation_result_record.
This is synthetic verification — it does NOT execute any simulation, call executors,
or modify target state. It only evaluates the record data against verification rules.
"""

from __future__ import annotations


# ── required check names and their severities ────────────────────────────────

_REQUIRED_CHECKS = [
    ("record_pending", "low"),
    ("result_persisted", "low"),
    ("simulation_not_executed", "medium"),
    ("tool_execution_blocked", "high"),
    ("apply_blocked", "critical"),
    ("rollback_blocked", "critical"),
    ("observations_are_synthetic", "high"),
    ("no_mutation_proof_clean", "high"),
    ("verification_evidence_present", "medium"),
    ("risk_findings_present", "medium"),
]


def _check_record_pending(record: dict, sim_result: dict | None = None) -> dict:
    return {
        "name": "record_pending",
        "passed": record.get("status") == "pending",
        "severity": "low",
        "detail": "Record status must be pending.",
    }


def _check_result_persisted(record: dict, sim_result: dict | None = None) -> dict:
    return {
        "name": "result_persisted",
        "passed": record.get("result_persisted") is True,
        "severity": "low",
        "detail": "Result must be persisted.",
    }


def _check_simulation_not_executed(record: dict, sim_result: dict) -> dict:
    return {
        "name": "simulation_not_executed",
        "passed": (
            record.get("simulation_executed") is False
            and sim_result.get("simulation_execution_allowed") is False
        ),
        "severity": "medium",
        "detail": "Both record.simulation_executed and result.simulation_execution_allowed must be false.",
    }


def _check_tool_execution_blocked(record: dict, sim_result: dict) -> dict:
    return {
        "name": "tool_execution_blocked",
        "passed": (
            sim_result.get("tool_execution_allowed") is False
            and record.get("tool_execution_allowed") is False
        ),
        "severity": "high",
        "detail": "Tool execution must be blocked in both record and result.",
    }


def _check_apply_blocked(record: dict, sim_result: dict) -> dict:
    return {
        "name": "apply_blocked",
        "passed": (
            sim_result.get("apply_allowed") is False
            and record.get("apply_allowed") is False
        ),
        "severity": "critical",
        "detail": "Apply must be blocked in both record and result.",
    }


def _check_rollback_blocked(record: dict, sim_result: dict) -> dict:
    return {
        "name": "rollback_blocked",
        "passed": (
            sim_result.get("rollback_allowed") is False
            and record.get("rollback_allowed") is False
        ),
        "severity": "critical",
        "detail": "Rollback must be blocked in both record and result.",
    }


def _check_observations_are_synthetic(record: dict | None = None, sim_result: dict = None) -> dict:
    if sim_result is None:
        sim_result = record or {}
    observations = sim_result.get("simulated_observations", [])
    if not observations:
        return {
            "name": "observations_are_synthetic",
            "passed": False,
            "severity": "high",
            "detail": "No simulated_observations found.",
        }
    all_false = all(o.get("real_world_observation") is False for o in observations)
    return {
        "name": "observations_are_synthetic",
        "passed": all_false,
        "severity": "high",
        "detail": "All simulated_observations must have real_world_observation=false." if all_false else "Some observations claim real-world observation.",
    }


def _check_no_mutation_proof_clean(record: dict | None = None, sim_result: dict = None) -> dict:
    if sim_result is None:
        sim_result = record or {}
    proof = sim_result.get("no_mutation_proof")
    if proof is None:
        return {
            "name": "no_mutation_proof_clean",
            "passed": False,
            "severity": "high",
            "detail": "no_mutation_proof is missing from simulation result.",
        }
    mutation_keys = [
        "filesystem_mutated", "network_called", "database_written",
        "identity_modified", "private_memory_modified", "target_state_modified",
        "apply_performed", "rollback_performed",
    ]
    clean = all(proof.get(k) is False for k in mutation_keys)
    return {
        "name": "no_mutation_proof_clean",
        "passed": clean,
        "severity": "high",
        "detail": "All no_mutation_proof mutation fields must be false." if clean else "Some mutation flags are non-false.",
    }


def _check_verification_evidence_present(record: dict | None = None, sim_result: dict = None) -> dict:
    if sim_result is None:
        sim_result = record or {}
    evidence_names = [e.get("name") for e in sim_result.get("verification_evidence", [])]
    required = ["no_real_tool_execution", "no_state_mutation", "no_rollback", "simulation_plan_not_execution"]
    present = all(n in evidence_names for n in required)
    return {
        "name": "verification_evidence_present",
        "passed": present,
        "severity": "medium",
        "detail": "verification_evidence must include required items." if present else "Missing required verification evidence names.",
    }


def _check_risk_findings_present(record: dict | None = None, sim_result: dict = None) -> dict:
    if sim_result is None:
        sim_result = record or {}
    finding_names = [f.get("name") for f in sim_result.get("risk_findings", [])]
    required = ["synthetic_result_only", "future_execution_requires_new_milestone"]
    present = all(n in finding_names for n in required)
    return {
        "name": "risk_findings_present",
        "passed": present,
        "severity": "medium",
        "detail": "risk_findings must include required items." if present else "Missing required risk findings.",
    }


CHECK_HARDCODED = {
    "record_pending": _check_record_pending,
    "result_persisted": _check_result_persisted,
    "simulation_not_executed": _check_simulation_not_executed,
    "tool_execution_blocked": _check_tool_execution_blocked,
    "apply_blocked": _check_apply_blocked,
    "rollback_blocked": _check_rollback_blocked,
    "observations_are_synthetic": _check_observations_are_synthetic,
    "no_mutation_proof_clean": _check_no_mutation_proof_clean,
    "verification_evidence_present": _check_verification_evidence_present,
    "risk_findings_present": _check_risk_findings_present,
}


# ── main builder ─────────────────────────────────────────────────────────────


def build_simulation_verification_verdict(
    simulation_result_record: dict | None,
    context: dict | None = None,
) -> dict:
    """Build a verification verdict from a simulation result record.

    Returns a verdict dict. Never returns None — even for missing records
    a blocked verdict is returned.

    Args:
        simulation_result_record: The saved simulation result record dict.
        context: Optional metadata context (e.g. session_id).

    Returns:
        Verification verdict dict.
    """
    # --- safe baseline ---
    _meta: dict = {
        "source": "simulation_verdict_builder",
        "schema_version": "1.0",
    }
    if context and isinstance(context, dict):
        sid = context.get("session_id")
        if sid:
            _meta["session_id"] = sid

    _warns: list[str] = []

    def _empty_verdict(
        decision: str,
        reason: str,
        sim_status: str | None = None,
        plan_id: str | None = None,
        dry_run_id: str | None = None,
        req_action=None,
        sim_snapshot=None,
        checks: list[dict] | None = None,
        blocking_reasons: list[str] | None = None,
        extra_wins: list[str] | None = None,
        next_step: str = "",
    ) -> dict:
        if extra_wins is None:
            extra_wins = []
        warnings = list(_warns) + list(extra_wins)
        warnings.append("Verification verdict does not authorize apply.")
        warnings.append("Synthetic verification only; no real-world system was contacted.")
        return {
            "verification_verdict_required": decision != "blocked" and simulation_result_record is not None,
            "verification_verdict_status": "prepared",
            "verification_verdict_type": "synthetic_result_verification",
            "decision": decision,
            "reason": reason,
            "simulation_result_id": None if simulation_result_record is None else simulation_result_record.get("simulation_result_id"),
            "simulation_result_record_status": sim_status,
            "simulation_plan_id": plan_id,
            "dry_run_id": dry_run_id,
            "requested_action": req_action,
            "simulation_result_snapshot": sim_snapshot,
            "checks": checks or [],
            "evidence_summary": [],
            "unresolved_risks": [],
            "blocking_reasons": blocking_reasons or [],
            "recommended_next_step": next_step,
            "apply_allowed": False,
            "rollback_allowed": False,
            "execution_allowed": False,
            "tool_execution_allowed": False,
            "dry_run_execution_allowed": False,
            "simulation_execution_allowed": False,
            "verdict_apply_allowed": False,
            "metadata": dict(_meta),
            "warnings": warnings,
        }

    # --- Rule 1: missing record → blocked ---
    if simulation_result_record is None:
        return _empty_verdict(
            decision="blocked",
            reason="Simulation result record was not found.",
            blocking_reasons=["Simulation result record was not found."],
            next_step="Create or provide a valid simulation result record.",
        )

    record = simulation_result_record
    sr_id = record.get("simulation_result_id")
    rec_status = record.get("status")
    plan_id = None
    dry_run_id = None
    req_action = None
    sim_snapshot = None

    # Extract link fields from nested simulation_result
    sim_obj = record.get("simulation_result")
    if sim_obj and isinstance(sim_obj, dict):
        plan_id = sim_obj.get("simulation_plan_id")
        dry_run_id = sim_obj.get("dry_run_id")
        req_action = sim_obj.get("requested_action")
        sim_snapshot = sim_obj

    # --- Rule 2: status != pending → blocked ---
    if rec_status != "pending":
        return _empty_verdict(
            decision="blocked",
            reason="Simulation result record is not pending.",
            sim_status=rec_status,
            plan_id=plan_id,
            dry_run_id=dry_run_id,
            req_action=req_action,
            sim_snapshot=sim_snapshot,
            blocking_reasons=["Record status is not pending."],
            next_step="Resolve blocking record state before verification.",
        )

    # --- Rule 3: simulation_executed is True → blocked ---
    if record.get("simulation_executed") is True:
        return _empty_verdict(
            decision="blocked",
            reason="Simulation result record is unexpectedly marked executed.",
            sim_status=rec_status,
            plan_id=plan_id,
            dry_run_id=dry_run_id,
            req_action=req_action,
            sim_snapshot=sim_snapshot,
            blocking_reasons=["simulation_executed is true."],
            next_step="Resolve the executed flag before verification.",
        )

    # --- Rule 4: missing/invalid simulation_result → fail ---
    if sim_obj is None or not isinstance(sim_obj, dict):
        return _empty_verdict(
            decision="fail",
            reason="Simulation result payload is missing or invalid.",
            sim_status=rec_status,
            plan_id=plan_id,
            dry_run_id=dry_run_id,
            req_action=req_action,
            sim_snapshot=sim_snapshot,
            blocking_reasons=["simulation_result is missing or not a dict."],
            next_step="Regenerate the simulation result object.",
        )

    # --- Rule 5: invalid simulation_result_status → fail ---
    result_status = sim_obj.get("simulation_result_status")
    if result_status != "prepared":
        return _empty_verdict(
            decision="fail",
            reason="Simulation result status is not prepared.",
            sim_status=rec_status,
            plan_id=plan_id,
            dry_run_id=dry_run_id,
            req_action=req_action,
            sim_snapshot=sim_snapshot,
            blocking_reasons=[f"simulation_result_status={result_status!r}, expected 'prepared'."],
            next_step="Regenerate the simulation result object with status 'prepared'.",
        )

    # --- Rule 6: invalid simulation_result_type → fail ---
    result_type = sim_obj.get("simulation_result_type")
    if result_type != "synthetic_contract_only_result":
        return _empty_verdict(
            decision="fail",
            reason="Unsupported simulation result type.",
            sim_status=rec_status,
            plan_id=plan_id,
            dry_run_id=dry_run_id,
            req_action=req_action,
            sim_snapshot=sim_snapshot,
            blocking_reasons=[f"simulation_result_type={result_type!r}."],
            next_step="Use a synthetic_contract_only_result type.",
        )

    # --- Rule 7: evaluate checks ---
    checks: list[dict] = []
    for check_name, _ in _REQUIRED_CHECKS:
        fn = CHECK_HARDCODED[check_name]
        check_result = fn(record, sim_obj)
        checks.append(check_result)

    # --- Copy warnings from simulation_result with prefix ---
    sim_warnings = sim_obj.get("warnings", [])
    for w in sim_warnings:
        _warns.append(f"simulation_result_warning: {w}")

    # --- Rule 8: decision logic ---
    has_critical_fail = any(c.get("passed") is False for c in checks if c.get("severity") == "critical")
    has_high_fail = any(c.get("passed") is False for c in checks if c.get("severity") == "high")
    has_medium_fail = any(c.get("passed") is False for c in checks if c.get("severity") == "medium")
    has_low_fail = any(c.get("passed") is False for c in checks if c.get("severity") == "low")

    if has_critical_fail or has_high_fail:
        verdict_decision = "fail"
    elif has_medium_fail or has_low_fail:
        verdict_decision = "warning"
    else:
        verdict_decision = "pass"

    # --- Build evidence_summary ---
    ev_sim_no_tool = False
    ev_sim_no_mutation = False
    ev_sim_no_rollback = False
    for e in sim_obj.get("verification_evidence", []):
        n = e.get("name", "")
        if n == "no_real_tool_execution":
            ev_sim_no_tool = True
        elif n == "no_state_mutation":
            ev_sim_no_mutation = True
        elif n == "no_rollback":
            ev_sim_no_rollback = True

    observations = sim_obj.get("simulated_observations", [])
    synth_obs = all(o.get("real_world_observation") is False for o in observations) if observations else False
    mproof = sim_obj.get("no_mutation_proof", {})
    mutation_clean = mproof.get("mutation_checked") is True

    evidence_summary: list[dict] = [
        {"name": "no_real_tool_execution", "status": "verified" if ev_sim_no_tool else "missing",
         "detail": "Verification evidence includes no_real_tool_execution."},
        {"name": "no_state_mutation", "status": "verified" if ev_sim_no_mutation else "missing",
         "detail": "Verification evidence includes no_state_mutation."},
        {"name": "no_rollback", "status": "verified" if ev_sim_no_rollback else "missing",
         "detail": "Verification evidence includes no_rollback."},
        {"name": "synthetic_observations_only", "status": "verified" if synth_obs else "missing",
         "detail": "All simulated_observations have real_world_observation=false."},
        {"name": "no_mutation_proof_clean", "status": "verified" if mutation_clean else "missing",
         "detail": "no_mutation_proof exists and is clean."},
    ]

    # --- Build unresolved_risks ---
    unresolved_risks: list[dict] = []
    if verdict_decision in ("pass", "warning"):
        unresolved_risks.append({
            "name": "real_apply_not_authorized",
            "severity": "medium",
            "detail": "Verification pass does not authorize real-world apply.",
        })
    else:
        for c in checks:
            if c.get("passed") is False and c.get("severity") in ("critical", "high"):
                unresolved_risks.append({
                    "name": c["name"],
                    "severity": c["severity"],
                    "detail": c["detail"],
                })

    # --- Build blocking_reasons ---
    blocking_reasons: list[str] = []
    if verdict_decision == "blocked":
        blocking_reasons = blocking_reasons or ["Unexpected state."]
    elif verdict_decision == "fail":
        for c in checks:
            if c.get("passed") is False and c.get("severity") in ("critical", "high"):
                blocking_reasons.append(c["name"])

    # --- recommended_next_step ---
    step_map = {
        "pass": "Proceed to a future apply-gate design milestone; do not apply changes yet.",
        "warning": "Review unresolved risks before any future apply-gate milestone.",
        "fail": "Repair or regenerate the simulation result before continuing.",
        "blocked": "Resolve blocking record state before verification.",
    }

    # Finalize warnings
    warnings = list(_warns)
    warnings.append("Verification verdict does not authorize apply.")
    warnings.append("Synthetic verification only; no real-world system was contacted.")

    return {
        "verification_verdict_required": True,
        "verification_verdict_status": "prepared",
        "verification_verdict_type": "synthetic_result_verification",
        "decision": verdict_decision,
        "reason": _build_pass_fallback_reason(checks),
        "simulation_result_id": sr_id,
        "simulation_result_record_status": rec_status,
        "simulation_plan_id": plan_id,
        "dry_run_id": dry_run_id,
        "requested_action": req_action,
        "simulation_result_snapshot": sim_snapshot,
        "checks": checks,
        "evidence_summary": evidence_summary,
        "unresolved_risks": unresolved_risks,
        "blocking_reasons": blocking_reasons,
        "recommended_next_step": step_map[verdict_decision],
        "apply_allowed": False,
        "rollback_allowed": False,
        "execution_allowed": False,
        "tool_execution_allowed": False,
        "dry_run_execution_allowed": False,
        "simulation_execution_allowed": False,
        "verdict_apply_allowed": False,
        "metadata": dict(_meta),
        "warnings": warnings,
    }


def _build_pass_fallback_reason(checks: list[dict]) -> str:
    """If every check passes, return pass reason; otherwise return first fail detail."""
    failed = [c for c in checks if c.get("passed") is False]
    if not failed:
        return "All verification checks passed. Synthetic result satisfies non-execution verification."
    return failed[0]["detail"]
