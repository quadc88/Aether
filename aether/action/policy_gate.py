"""Policy Enforcement Gate — Action compatibility facade.

This module is a thin compatibility facade. The authoritative decision logic
has been migrated to aether.core.governance.evaluate_authorization_envelope.
This facade preserves the existing public function signature and exact
results for direct importers and tests.
"""

from __future__ import annotations

from aether.core.governance import evaluate_authorization_envelope


def enforce_policy_gate(
    thinking_policy: dict | None = None,
    requested_action: dict | None = None,
    context: dict | None = None,
) -> dict:
    """Enforce the policy gate on a requested action.

    Compatibility facade that delegates to the Core Governance evaluation
    function. See aether.core.governance.evaluate_authorization_envelope
    for the authoritative decision logic.

    Args:
        thinking_policy: Output of decide_chat_policy().
        requested_action: The action/tool being requested (optional).
        context: Additional context dict (optional, not used in decision).

    Returns:
        Dict with keys: allowed, decision, reason, required_user_confirmation,
        tool_execution_allowed, action_execution_allowed, requested_action,
        policy_snapshot, warnings.
    """
    return evaluate_authorization_envelope(
        thinking_policy=thinking_policy,
        requested_action=requested_action,
        context=context,
    )
