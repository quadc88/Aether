"""Core chat loop skeleton for Aether.

Orchestrates the basic flow: validate → perceive → verify identity →
time → record input → risk classify → tool suggest → respond → record
timeline. Does NOT execute tools or call external models.
"""

from __future__ import annotations

from aether.core.config import get_project_root
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
    warnings: list[str] = []

    # --- Step 1: Validate ---
    if not text or not text.strip():
        return _error_response("Input text is empty.", warnings)

    # --- Step 2: Perceive ---
    perception = perceive_text_input(text, metadata=metadata)
    if perception.get("warnings"):
        warnings.extend(perception["warnings"])

    # --- Step 3: Verify identity integrity ---
    identity_status: dict | None = None
    try:
        identity_status = verify_identity_integrity()
    except FileNotFoundError:
        warnings.append(
            "Identity guard not initialized. Call POST /identity/integrity/initialize first."
        )
    except Exception as exc:
        warnings.append(f"Identity verification error: {exc}")

    # --- Step 4: Get current time ---
    ts = now_iso()
    current_time = time_state()

    # --- Step 5: Record input to working memory ---
    memory_recorded = False
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

    # --- Step 6: Classify risk ---
    from aether.verification.risk import classify_risk
    risk = classify_risk(text)

    # --- Step 7: Suggest tool (read-only suggestion, no execution) ---
    suggested_tool = _suggest_tool(text, risk)

    # --- Step 7b: Thinking policy decision ---
    from aether.thinking.policy import decide_chat_policy

    thinking_policy = decide_chat_policy(
        perception=perception,
        risk=risk,
        suggested_tool=suggested_tool,
        identity_integrity_status=identity_status,
        metadata=metadata,
    )

    # --- Step 7c: Policy Enforcement Gate ---
    from aether.action.policy_gate import enforce_policy_gate
    policy_gate_result = enforce_policy_gate(
        thinking_policy=thinking_policy,
        requested_action=suggested_tool,
        context={"session_id": session_id},
    )
    execution_allowed = policy_gate_result.get("allowed", False)
    execution_decision = policy_gate_result.get("decision", "invalid_policy")
    execution_reason = policy_gate_result.get("reason", "")

    # --- Step 8: Tool execution is NEVER performed in this milestone ---
    tool_executed = False
    tool_execution_allowed = False

    # --- Step 9: Record timeline event ---
    timeline_recorded = False
    try:
        record_event(
            event_type="chat_input",
            title=f"Chat input ({risk['risk_level']})",
            description=text[:200],
            importance="high" if risk["risk_level"] == "high" else "normal",
            related_files=["aether/interface/api_server.py"],
        )
        timeline_recorded = True
    except Exception as exc:
        warnings.append(f"Timeline recording failed: {exc}")

    # --- Step 10: Build response ---
    response_text = _build_response(text, risk, perception, suggested_tool, thinking_policy)

    return {
        "status": "completed",
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
        "thinking_policy": thinking_policy,
        "decision_type": thinking_policy.get("decision_type"),
        "required_user_confirmation": thinking_policy.get("required_user_confirmation", False),
        "clarification_question": thinking_policy.get("clarification_question"),
        "blocked_reason": thinking_policy.get("blocked_reason"),
        # --- Policy Enforcement Gate (Milestone 51A) ---
        "policy_gate": policy_gate_result,
        "execution_allowed": execution_allowed,
        "execution_decision": execution_decision,
        "execution_reason": execution_reason,
    }


def _error_response(error_msg: str, warnings: list[str]) -> dict:
    return {
        "status": "error",
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
        "warnings": [*warnings, error_msg],
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
