"""Approval Request Builder for Aether.

Builds structured approval_request objects when policy_gate returns
require_approval or block, or when thinking_policy requires confirmation.

This object is only a structured request — it does NOT approve anything,
execute anything, or create persistent approval records.
"""

from __future__ import annotations


def _needs_approval(policy_gate: dict | None, thinking_policy: dict | None) -> bool:
    """Determine if an approval request object should be built."""
    if policy_gate is None:
        return False
    decision = policy_gate.get("decision", "")
    tp_decision_type = ""
    tp_confirm = False
    if thinking_policy:
        tp_decision_type = thinking_policy.get("decision_type", "")
        tp_confirm = thinking_policy.get("required_user_confirmation", False)
    if decision in ("require_approval", "block", "invalid_policy"):
        return True
    if tp_decision_type == "block":
        return True
    if tp_confirm and tp_decision_type == "require_approval":
        return True
    return False


def build_approval_request(
    policy_gate: dict | None = None,
    thinking_policy: dict | None = None,
    risk: dict | None = None,
    requested_action: dict | None = None,
    perception: dict | None = None,
    context: dict | None = None,
) -> dict | None:
    """Build a structured approval request object.

    Returns None when no approval is needed.

    Args:
        policy_gate: Output of enforce_policy_gate().
        thinking_policy: Output of decide_chat_policy().
        risk: Output of classify_risk().
        requested_action: The action/tool being requested.
        perception: Output of perceive_text_input().
        context: Additional context (session_id etc).

    Returns:
        Approval request dict or None.
    """
    if not _needs_approval(policy_gate, thinking_policy):
        return None

    risk_level = None
    risk_action_type = None
    decision_type = None
    execution_decision = None
    blocked_reason = None

    if risk:
        risk_level = risk.get("risk_level")
        risk_action_type = risk.get("action_type")
    if thinking_policy:
        decision_type = thinking_policy.get("decision_type")
    if policy_gate:
        execution_decision = policy_gate.get("decision")
        blocked_reason = thinking_policy.get("blocked_reason") if thinking_policy else None

    # --- Determine approval_type and reason ---
    gate_decision = policy_gate.get("decision", "") if policy_gate else ""
    tp_decision_type = thinking_policy.get("decision_type", "") if thinking_policy else ""

    if gate_decision == "block" or tp_decision_type == "block":
        approval_type = "blocked_identity_review"
        reason = blocked_reason
        if not reason and policy_gate:
            reason = policy_gate.get("reason", "Policy blocked this request.")
        if not reason:
            reason = "Policy blocked this request."
    elif gate_decision == "invalid_policy":
        approval_type = "invalid_policy_review"
        reason = policy_gate.get("reason", "Missing or invalid policy.") if policy_gate else "Missing or invalid policy."
    else:
        approval_type = "human_review"
        reason = policy_gate.get("reason", "") if policy_gate else ""
        if not reason and thinking_policy:
            reason = thinking_policy.get("next_step", "Human approval is required.")
        if not reason:
            reason = "Human approval is required."

    # --- Build required_confirmations ---
    required_confirmations = [
        "Confirm the user's intent.",
        "Confirm no irreversible action will occur without explicit approval.",
    ]
    if risk_level == "high":
        required_confirmations.append("Confirm high-risk operation details.")
        required_confirmations.append("Confirm backup or rollback strategy if applicable.")
    if risk_action_type and "identity" in risk_action_type:
        required_confirmations.append("Confirm identity seed is not modified without explicit approval.")
    if risk_action_type and ("memory" in risk_action_type or "private" in risk_action_type):
        required_confirmations.append("Confirm memory/private data target and scope.")

    # --- Build safety_checks ---
    safety_checks = [
        "Verify requested action.",
        "Verify policy gate decision.",
        "Verify tool execution remains disabled.",
        "Verify no private data is exposed.",
    ]
    if requested_action:
        safety_checks.append("Verify requested tool/action identifier.")

    # --- Build summary ---
    summary_parts = ["Approval required"]
    if risk_level == "high":
        action_label = risk_action_type.replace("_", " ") if risk_action_type else "high-risk operation"
        summary_parts.append(f"for {action_label} request.")
    elif tp_decision_type == "block":
        summary_parts.append("before blocked action may proceed.")
    elif gate_decision == "invalid_policy":
        summary_parts.append("due to missing or invalid policy.")
    else:
        summary_parts.append("before executing suggested tool.")
    summary = "".join(summary_parts)

    # --- Build metadata ---
    metadata = {
        "source": "approval_request_builder",
        "schema_version": "1.0",
    }
    if context and isinstance(context, dict):
        sid = context.get("session_id")
        if sid:
            metadata["session_id"] = sid
    if perception and isinstance(perception, dict):
        lh = perception.get("language_hint")
        if lh:
            metadata["language_hint"] = lh

    return {
        "approval_required": True,
        "approval_type": approval_type,
        "approval_status": "pending",
        "reason": reason,
        "risk_level": risk_level,
        "risk_action_type": risk_action_type,
        "decision_type": decision_type,
        "execution_decision": execution_decision,
        "requested_action": requested_action,
        "summary": summary,
        "required_confirmations": required_confirmations,
        "safety_checks": safety_checks,
        "expires": None,
        "metadata": metadata,
    }
