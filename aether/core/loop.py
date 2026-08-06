"""Core chat loop skeleton for Aether.

Orchestrates the basic flow: validate → perceive → verify identity →
time → record input → risk classify → tool suggest → respond → record
timeline. Does NOT execute tools or call external models.
"""

from __future__ import annotations

import time as _time

from aether.core.config import get_project_root
from aether.core.loop_trace import (
    build_loop_trace,
    build_stage,
    generate_trace_id,
)
from aether.identity.guard import verify_identity_integrity
from aether.memory.timeline.recorder import record_event
from aether.memory.working.store import WorkingMemory
from aether.perception.text import perceive_text_input
from aether.time.clock import now_iso, time_state


LOOP_VERSION = "0.1.0"


def run_core_chat_loop(
    text: str,
    working_memory: WorkingMemory | None = None,
    session_id: str | None = None,
    metadata: dict | None = None,
    allow_tool_execution: bool = False,
) -> dict:
    """Execute one iteration of the core chat loop.

    Args:
        text: User input text.
        working_memory: Existing WorkingMemory instance (optional).
        session_id: Optional session identifier.
        metadata: Arbitrary metadata to attach.
        allow_tool_execution: Ignored — tool execution is always disabled.

    Returns:
        Response dict with all loop stage results.
    """
    trace_id = generate_trace_id("chat")
    trace_start_wall = _time.time()
    trace_start_iso = now_iso()
    stages: list[dict] = []
    warnings: list[str] = []

    # --- Step 1: Validate ---
    if not text or not text.strip():
        return _error_response("Input text is empty.", warnings, trace_id, trace_start_wall, trace_start_iso)

    # --- Step 2: Perceive ---
    perception = perceive_text_input(text, metadata=metadata)
    perception_warnings = len(perception.get("warnings", []))
    if perception.get("warnings"):
        warnings.extend(perception["warnings"])
    stages.append(build_stage(
        "perception",
        summary=f"Input classified as {perception['type']}, {perception['language_hint']}, {perception['original_length']} chars",
        warnings_count=perception_warnings,
    ))

    # --- Step 3: Verify identity integrity ---
    identity_status: dict | None = None
    identity_stage_warnings = 0
    identity_stage_status = "completed"
    identity_stage_summary = ""
    try:
        identity_status = verify_identity_integrity()
        if identity_status and identity_status.get("changed"):
            identity_stage_summary = "Identity checksum changed"
        elif identity_status and identity_status.get("status") == "failed":
            identity_stage_summary = "Identity verification failed"
            identity_stage_status = "warning"
        else:
            identity_stage_summary = "Identity verified"
    except FileNotFoundError:
        warnings.append(
            "Identity guard not initialized. Call POST /identity/integrity/initialize first."
        )
        identity_stage_status = "warning"
        identity_stage_summary = "Identity guard not initialized"
        identity_stage_warnings = 1
    except Exception as exc:
        warnings.append(f"Identity verification error: {exc}")
        identity_stage_status = "error"
        identity_stage_summary = f"Identity verification error"
        identity_stage_warnings = 1
    stages.append(build_stage(
        "identity_integrity",
        status=identity_stage_status,
        summary=identity_stage_summary,
        warnings_count=identity_stage_warnings,
    ))

    # --- Step 4: Get current time ---
    ts = now_iso()
    current_time = time_state()
    stages.append(build_stage(
        "time_state",
        summary=f"Time state captured ({current_time.get('timezone', 'unknown')})",
    ))

    # --- Step 5: Record input to working memory ---
    memory_recorded = False
    wm_event_count = 0
    if working_memory is not None:
        working_memory.add_event(
            role="user",
            content=text[:500],  # truncate long inputs for WM
            event_type="chat_input",
            metadata={
                "session_id": session_id,
                "perceived_language": perception["language_hint"],
            },
        )
        working_memory.add_event(
            role="aether",
            content=f"[Loop v{LOOP_VERSION}] Received input ({perception['language_hint']}, {perception['original_length']} chars).",
            event_type="chat_response",
            metadata={"session_id": session_id},
        )
        memory_recorded = True
        wm_event_count = 2
    stages.append(build_stage(
        "working_memory",
        summary=f"Recorded {wm_event_count} events" if memory_recorded else "Working memory unavailable",
    ))

    # --- Step 6: Classify risk ---
    from aether.verification.risk import classify_risk
    risk = classify_risk(text)
    stages.append(build_stage(
        "risk_classification",
        summary=f"Classified as {risk['risk_level']} ({risk['action_type']})",
    ))

    # --- Step 7: Suggest tool (read-only suggestion, no execution) ---
    suggested_tool = _suggest_tool(text, risk)
    stages.append(build_stage(
        "tool_suggestion",
        summary=f"Tool suggested: {suggested_tool['tool_id']} ({suggested_tool.get('match_confidence', 'unknown')})" if suggested_tool else "No tool matched",
    ))

    # --- Step 7b: Thinking policy decision (Rules 3-9 only; Identity Rules 1/2
    # evaluated authoritatively in Governance — Strategy T3) ---
    from aether.thinking.policy import _evaluate_chat_policy_with_precedence

    raw_thinking_policy, rule_3_4_precedence = _evaluate_chat_policy_with_precedence(
        perception=perception,
        risk=risk,
        suggested_tool=suggested_tool,
        identity_integrity_status=identity_status,
        metadata=metadata,
    )
    stages.append(build_stage(
        "thinking_policy",
        summary=f"Decision: {raw_thinking_policy.get('decision_type', 'unknown')}",
        warnings_count=len(raw_thinking_policy.get("warnings", [])),
    ))

    # --- Step 7c: Policy Enforcement Gate (Core Governance) ---
    from aether.core.governance import evaluate_authorization_envelope
    authorization_envelope = evaluate_authorization_envelope(
        thinking_policy=raw_thinking_policy,
        requested_action=suggested_tool,
        context={"session_id": session_id},
        risk_evidence=risk,
        identity_integrity_evidence=identity_status,
        rule_3_4_precedence=rule_3_4_precedence,
    )
    effective_thinking_policy = authorization_envelope["policy_snapshot"]
    execution_allowed = authorization_envelope.get("allowed", False)
    execution_decision = authorization_envelope.get("decision", "invalid_policy")
    execution_reason = authorization_envelope.get("reason", "")
    stages.append(build_stage(
        "policy_gate",
        summary=f"Decision: {execution_decision}",
        warnings_count=len(authorization_envelope.get("warnings", [])),
    ))

    # --- Step 7d: Approval Request Builder (Milestone 52A) ---
    from aether.action.approval_request import build_approval_request
    approval_request = build_approval_request(
        policy_gate=authorization_envelope,
        thinking_policy=effective_thinking_policy,
        risk=risk,
        requested_action=suggested_tool,
        perception=perception,
        context={"session_id": session_id},
    )

    stages.append(build_stage(
        "approval_request",
        summary=f"Approval {'required' if (approval_request and approval_request.get('approval_required')) else 'not required'}",
    ))

    # --- Step 7e: Persist to approval queue (Milestone 54A) ---
    approval_record = None
    approval_id = None
    if approval_request is not None and approval_request.get("approval_required", False):
        from aether.action.approval_queue import create_approval_record
        approval_record = create_approval_record(
            approval_request=approval_request,
            context={"session_id": session_id},
        )
        approval_id = approval_record["approval_id"]
        stages.append(build_stage(
            "approval_queue",
            summary=f"Approval record created (id: {approval_id[:16]}...)",
        ))
    else:
        stages.append(build_stage(
            "approval_queue",
            status="skipped",
            summary="No approval record needed",
        ))

    # --- Step 8: Tool execution is NEVER performed in this milestone ---
    tool_executed = False
    tool_execution_allowed = False

    # --- Step 9: Record timeline event ---
    timeline_recorded = False
    timeline_event_id = None
    try:
        timeline_event = record_event(
            event_type="chat_input",
            title=f"Chat input ({risk['risk_level']})",
            description=text[:200],
            importance="high" if risk["risk_level"] == "high" else "normal",
            related_files=["aether/interface/api_server.py"],
        )
        timeline_recorded = True
        if timeline_event and isinstance(timeline_event, dict):
            timeline_event_id = timeline_event.get("id")
    except Exception as exc:
        warnings.append(f"Timeline recording failed: {exc}")
    stages.append(build_stage(
        "timeline_recording",
        summary=f"Timeline event recorded" if timeline_recorded else "Timeline recording failed",
    ))

    # --- Step 10: Build response ---
    response_text = _build_response(text, risk, perception, suggested_tool, effective_thinking_policy)
    stages.append(build_stage("response_generation", summary="Response generated"))

    # --- Build loop trace ---
    trace_end_wall = _time.time()
    trace_end_iso = now_iso()
    duration_ms = int((trace_end_wall - trace_start_wall) * 1000)

    loop_trace = build_loop_trace(
        trace_id=trace_id,
        loop_version=LOOP_VERSION,
        started_at=trace_start_iso,
        completed_at=trace_end_iso,
        duration_ms=duration_ms,
        status="completed",
        stages=stages,
        safety={
            "tool_execution_allowed": False,
            "tool_executed": False,
            "execution_allowed": execution_allowed,
            "approval_required": approval_request.get("approval_required", False) if approval_request else False,
        },
        records={
            "working_memory_event_ids": [],
            "timeline_event_id": timeline_event_id,
            "approval_id": approval_id,
        },
        warnings=warnings,
    )

    return {
        "status": "completed",
        "loop_trace": loop_trace,
        "session_id": session_id,
        "loop_version": LOOP_VERSION,
        "time": current_time,
        "identity_integrity_status": identity_status,
        "perception": {
            "type": perception["type"],
            "normalized_text": perception["normalized_text"],
            "original_length": perception["original_length"],
            "language_hint": perception["language_hint"],
            "contains_question": perception["contains_question"],
            "contains_command_hint": perception["contains_command_hint"],
            "risk_terms_detected": perception["risk_terms_detected"],
        },
        "risk": risk,
        "suggested_tool": suggested_tool,
        "tool_execution_allowed": False,
        "tool_executed": False,
        "response_text": response_text,
        "memory_recorded": memory_recorded,
        "timeline_recorded": timeline_recorded,
        "warnings": warnings,
        # --- Thinking Policy Layer ---
        "thinking_policy": effective_thinking_policy,
        "decision_type": effective_thinking_policy.get("decision_type"),
        "required_user_confirmation": effective_thinking_policy.get("required_user_confirmation", False),
        "clarification_question": effective_thinking_policy.get("clarification_question"),
        "blocked_reason": effective_thinking_policy.get("blocked_reason"),
        # --- Policy Enforcement Gate (Milestone 51A) ---
        "policy_gate": authorization_envelope,
        "execution_allowed": execution_allowed,
        "execution_decision": execution_decision,
        "execution_reason": execution_reason,
        # --- Approval Request Builder (Milestone 52A) ---
        "approval_request": approval_request,
        "approval_required": approval_request.get("approval_required", False) if approval_request else False,
        "approval_status": approval_request.get("approval_status") if approval_request else None,
        "approval_type": approval_request.get("approval_type") if approval_request else None,
        # --- Approval Queue (Milestone 54A) ---
        "approval_record": approval_record,
        "approval_id": approval_id,
    }


def _error_response(
    error_msg: str,
    warnings: list[str],
    trace_id: str | None = None,
    trace_start_wall: float | None = None,
    trace_start_iso: str | None = None,
) -> dict:
    error_warnings = [*warnings, error_msg]
    loop_trace = None
    if trace_id and trace_start_wall is not None and trace_start_iso:
        trace_end_wall = _time.time()
        trace_end_iso = now_iso()
        duration_ms = int((trace_end_wall - trace_start_wall) * 1000)
        loop_trace = build_loop_trace(
            trace_id=trace_id,
            loop_version=LOOP_VERSION,
            started_at=trace_start_iso,
            completed_at=trace_end_iso,
            duration_ms=duration_ms,
            status="error",
            stages=[
                build_stage("input_validation", status="error", summary=error_msg),
                build_stage("response_generation", summary="Response generated"),
            ],
            safety={
                "tool_execution_allowed": False,
                "tool_executed": False,
                "execution_allowed": False,
                "approval_required": False,
            },
            records={
                "working_memory_event_ids": [],
                "timeline_event_id": None,
                "approval_id": None,
            },
            warnings=error_warnings,
        )
    return {
        "status": "error",
        "loop_trace": loop_trace,
        "session_id": None,
        "loop_version": LOOP_VERSION,
        "time": time_state(),
        "identity_integrity_status": None,
        "perception": None,
        "risk": {"risk_level": "low", "action_type": "invalid_input"},
        "suggested_tool": None,
        "tool_execution_allowed": False,
        "tool_executed": False,
        "response_text": f"Aether received nothing. {error_msg}",
        "memory_recorded": False,
        "timeline_recorded": False,
        "warnings": error_warnings,
        "thinking_policy": {
            "decision_type": "ask_clarification",
            "confidence": "high",
            "reasons": [error_msg],
            "required_user_confirmation": False,
            "tool_suggestion_allowed": False,
            "tool_execution_allowed": False,
            "blocked_reason": None,
            "clarification_question": None,
            "next_step": "Await valid input.",
            "warnings": [],
        },
        "decision_type": "ask_clarification",
        "required_user_confirmation": False,
        "clarification_question": None,
        "blocked_reason": None,
        # --- Policy Enforcement Gate (Milestone 51A) ---
        "policy_gate": {
            "allowed": False,
            "decision": "invalid_policy",
            "reason": "Missing thinking policy.",
            "required_user_confirmation": True,
            "tool_execution_allowed": False,
            "action_execution_allowed": False,
            "requested_action": None,
            "policy_snapshot": None,
            "warnings": [error_msg],
        },
        "execution_allowed": False,
        "execution_decision": "invalid_policy",
        "execution_reason": "Missing thinking policy.",
        # --- Approval Request Builder (Milestone 52A) ---
        "approval_request": None,
        "approval_required": False,
        "approval_status": None,
        "approval_type": None,
        # --- Approval Queue (Milestone 54A) ---
        "approval_record": None,
        "approval_id": None,
    }


def _suggest_tool(text: str, risk: dict) -> dict | None:
    """Return a suggested tool from tool_planner via infer_candidate_tool.

    Never executes any tool. Supports both top-level and nested candidate_tool
    shapes returned by different planner implementations. Returns None if no
    tool matches.
    """
    from aether.action.tool_planner import infer_candidate_tool

    try:
        suggestion = infer_candidate_tool(text)
        # Shape A: top-level tool_id (e.g. infer_candidate_tool direct output)
        candidate = suggestion.get("candidate_tool") or {}
        if not candidate or not candidate.get("tool_id"):
            # Shape B: tool_id at top level of suggestion
            if suggestion.get("tool_id"):
                candidate = {k: v for k, v in suggestion.items()
                             if k in ("tool_id", "name", "match_confidence", "reason")}
        if candidate and candidate.get("tool_id"):
            return candidate
        return None
    except Exception:
        return None


def _build_response(
    text: str,
    risk: dict,
    perception: dict,
    suggested_tool: dict | None,
    thinking_policy: dict | None = None,
) -> str:
    lang = perception["language_hint"]
    language_str = lang if lang != "unknown" else "mixed or unknown"
    decision_type = (thinking_policy or {}).get("decision_type", "respond_only")

    lines = [
        f"Aether received your input ({len(text)} characters).",
        f"Perception: detected language hint is '{language_str}'.",
        f"Risk level: {risk['risk_level']} ({risk['action_type']}).",
        "",
    ]

    if decision_type == "block":
        blocked = thinking_policy.get("blocked_reason", "") if thinking_policy else ""
        lines.append(f"[BLOCKED] {blocked}")
        lines.append(
            "Aether cannot proceed until a human reviews the identity integrity status."
        )
    elif decision_type == "require_approval":
        lines.append(
            "This request requires user confirmation. Tool execution is disabled in this milestone."
        )
    elif decision_type == "suggest_tool":
        if suggested_tool:
            tool_id = suggested_tool.get("tool_id", "unknown")
            lines.append(f"Suggested tool (not executed): {tool_id}")
        lines.append(
            "Tool execution is disabled in this milestone. This message is informational only."
        )
    elif decision_type == "ask_clarification":
        cq = thinking_policy.get("clarification_question", "") if thinking_policy else ""
        if cq:
            lines.append(cq)
    else:
        if risk["risk_level"] == "high":
            lines.append(
                "This request is classified as high-risk. "
                "Tool execution is disabled in this milestone. "
                "User confirmation would be required before any action."
            )
        elif risk["risk_level"] == "medium":
            lines.append(
                "This request is medium-risk. "
                "Verification is recommended before proceeding."
            )

        if suggested_tool:
            tool_id = suggested_tool.get("tool_id", "unknown")
            lines.append(f"Suggested tool (not executed): {tool_id}")

    lines.append("")
    lines.append(
        "Note: This milestone does not execute tools, call external models, "
        "or perform write actions. Input is recorded in Working Memory and Timeline."
    )

    return "\n".join(lines)
