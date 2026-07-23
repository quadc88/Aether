"""Policy Enforcement Gate for Aether.

Central execution gate that blocks any tool/action execution unless
thinking_policy explicitly allows it.

For Milestone 51A, thinking_policy always sets tool_execution_allowed=False,
so normal result should always be deny / require_approval / block.
"""

from __future__ import annotations


def enforce_policy_gate(
    thinking_policy: dict | None = None,
    requested_action: dict | None = None,
    context: dict | None = None,
) -> dict:
    """Enforce the policy gate on a requested action.

    Blocks execution unless thinking_policy explicitly allows it.

    Args:
        thinking_policy: Output of decide_chat_policy().
        requested_action: The action/tool being requested (optional).
        context: Additional context dict (optional, not used in decision).

    Returns:
        Dict with keys: allowed, decision, reason, required_user_confirmation,
        tool_execution_allowed, action_execution_allowed, requested_action,
        policy_snapshot, warnings.
    """
    warnings: list[str] = []

    # Rule 1: Missing thinking_policy
    if thinking_policy is None:
        return {
            "allowed": False,
            "decision": "invalid_policy",
            "reason": "Missing thinking policy.",
            "required_user_confirmation": True,
            "tool_execution_allowed": False,
            "action_execution_allowed": False,
            "requested_action": requested_action,
            "policy_snapshot": None,
            "warnings": ["No thinking policy available to evaluate."],
        }

    decision_type = thinking_policy.get("decision_type", "")
    policy_snapshot = dict(thinking_policy)
    required_user_confirmation = thinking_policy.get("required_user_confirmation", False)

    # Rule 2: decision_type == "block"
    if decision_type == "block":
        blocked_reason = thinking_policy.get("blocked_reason")
        return {
            "allowed": False,
            "decision": "block",
            "reason": blocked_reason or "Policy blocked this action.",
            "required_user_confirmation": True,
            "tool_execution_allowed": False,
            "action_execution_allowed": False,
            "requested_action": requested_action,
            "policy_snapshot": policy_snapshot,
            "warnings": warnings,
        }

    # Rule 3: decision_type == "require_approval"
    if decision_type == "require_approval":
        return {
            "allowed": False,
            "decision": "require_approval",
            "reason": "Human approval is required before execution.",
            "required_user_confirmation": True,
            "tool_execution_allowed": False,
            "action_execution_allowed": False,
            "requested_action": requested_action,
            "policy_snapshot": policy_snapshot,
            "warnings": warnings,
        }

    # Rule 4: tool_execution_allowed is not True
    if not thinking_policy.get("tool_execution_allowed"):
        return {
            "allowed": False,
            "decision": "deny",
            "reason": "Tool execution is not allowed by policy.",
            "required_user_confirmation": required_user_confirmation,
            "tool_execution_allowed": False,
            "action_execution_allowed": False,
            "requested_action": requested_action,
            "policy_snapshot": policy_snapshot,
            "warnings": warnings,
        }

    # Rule 5: tool_execution_allowed is True — allow
    return {
        "allowed": True,
        "decision": "allow",
        "reason": "Policy allows execution.",
        "required_user_confirmation": False,
        "tool_execution_allowed": True,
        "action_execution_allowed": True,
        "requested_action": requested_action,
        "policy_snapshot": policy_snapshot,
        "warnings": warnings,
    }
