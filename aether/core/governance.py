"""Core Governance Authorization Decision-Envelope Boundary.

This module is the narrow physical home for the Milestone 87 Core Governance
authorization decision envelope. It is not the complete Governance plane,
not a universal Governance runtime, and not a general location for unrelated
Governance capabilities. Future Governance capabilities require their own
authorized ownership and module decisions.

The authoritative decision logic exists here. The current Action-located
enforcement gate is converted to a thin compatibility facade that delegates
to this module.

Rules 1 and 2 (Identity constraints) are authoritatively evaluated here
after Milestone 89B. Thinking proposes only Rules 3 through 9.
"""

from __future__ import annotations


def _format_rule_5_compatibility_policy(action_type: str) -> dict:
    """Format the legacy Rule 5 policy after Governance selects Rule 5."""
    return {
        "decision_type": "require_approval",
        "confidence": "high",
        "reasons": [
            f"High-risk request ({action_type}). "
            "Human approval required before any action."
        ],
        "required_user_confirmation": True,
        "tool_suggestion_allowed": False,
        "tool_execution_allowed": False,
        "blocked_reason": None,
        "clarification_question": None,
        "next_step": "Human approval is required before any action.",
        "warnings": [f"High-risk classification: {action_type}."],
    }


def _format_rule_6_compatibility_policy(requested_action) -> dict:
    """Format the legacy Rule 6 policy after Governance selects Rule 6."""
    tool_id = requested_action.get("tool_id", "")
    return {
        "decision_type": "require_approval",
        "confidence": "medium",
        "reasons": [
            f"Medium-risk request with suggested tool '{tool_id}'. "
            "Requires human approval before tool use."
        ],
        "required_user_confirmation": True,
        "tool_suggestion_allowed": True,
        "tool_execution_allowed": False,
        "blocked_reason": None,
        "clarification_question": None,
        "next_step": "Review suggested tool and confirm before proceeding.",
        "warnings": ["Medium-risk tool usage requires human confirmation."],
    }


def evaluate_authorization_envelope(
    thinking_policy: dict | None = None,
    requested_action: dict | None = None,
    context: dict | None = None,
    *,
    risk_evidence: dict | None = None,
    identity_integrity_evidence: dict | None = None,
    rule_3_4_precedence: str | None = None,
) -> dict:
    """Evaluate the Core Governance authorization decision envelope.

    This is the single authoritative compatibility decision implementation.
    Thinking proposes (Rules 3-9 only). Verification and Identity supply
    evidence. Core Governance evaluates Identity Rules 1 and 2 and
    authorizes. Action executes only within authorization.

    The keyword-only arguments are direct call-local provenance inputs. The
    Rule 3/4 signal is recognized only for its three exact private values and
    is never copied into an output.

    Args:
        thinking_policy: Output of decide_chat_policy(). Non-authoritative
            proposal data (Rules 3-9 only after Milestone 89B).
        requested_action: The action/tool being requested (optional).
        context: Additional context dict (optional, not used in decision).
        risk_evidence: Raw existing risk dictionary from classify_risk.
            Provenance-only; remains non-operative.
        identity_integrity_evidence: Safe summary from identity guard.
            Operative only for Identity Rules 1 and 2.
        rule_3_4_precedence: Private Thinking provenance signal. Only the
            exact values ``rule_3``, ``rule_4`` and ``clear`` are recognized.

    Returns:
        Dict with keys: allowed, decision, reason,
        required_user_confirmation, tool_execution_allowed,
        action_execution_allowed, requested_action, policy_snapshot,
        warnings.
    """
    warnings: list[str] = []

    # --- Precedence 1: Missing thinking_policy ---
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

    # --- Precedence 2: Identity evidence — Rules 1 and 2 ---
    # Identity evidence is a dictionary: read its `status` field.
    # Malformed non-dictionary evidence falls through safely.
    # Status is authoritative over any conflicting `changed` boolean.
    if isinstance(identity_integrity_evidence, dict):
        status = identity_integrity_evidence.get("status", "")

        # --- Rule 1: Identity status == "changed" ---
        if status == "changed":
            return {
                "allowed": False,
                "decision": "block",
                "reason": "Identity integrity changed. Human review is required before continuing.",
                "required_user_confirmation": True,
                "tool_execution_allowed": False,
                "action_execution_allowed": False,
                "requested_action": requested_action,
                "policy_snapshot": {
                    "decision_type": "block",
                    "confidence": "high",
                    "reasons": ["Identity seed checksum changed — integrity compromised."],
                    "required_user_confirmation": True,
                    "tool_suggestion_allowed": False,
                    "tool_execution_allowed": False,
                    "blocked_reason": "Identity integrity changed. Human review is required before continuing.",
                    "clarification_question": None,
                    "next_step": "Verify identity seed integrity before continuing.",
                    "warnings": ["Identity seed integrity mismatch detected."],
                },
                "warnings": warnings,
            }

        # --- Rule 2: Identity status == "missing" or "failed" ---
        if status in ("missing", "failed"):
            return {
                "allowed": False,
                "decision": "require_approval",
                "reason": "Human approval is required before execution.",
                "required_user_confirmation": True,
                "tool_execution_allowed": False,
                "action_execution_allowed": False,
                "requested_action": requested_action,
                "policy_snapshot": {
                    "decision_type": "require_approval",
                    "confidence": "high",
                    "reasons": [
                        f"Identity integrity status is '{status}'. "
                        "Human inspection is needed before proceeding."
                    ],
                    "required_user_confirmation": True,
                    "tool_suggestion_allowed": False,
                    "tool_execution_allowed": False,
                    "blocked_reason": None,
                    "clarification_question": None,
                    "next_step": "Human should inspect identity integrity status.",
                    "warnings": [f"Identity integrity status: {status}."],
                },
                "warnings": warnings,
            }

        # --- Status is "verified", unknown, empty, or missing key ---
        # Fall through to normal Thinking-proposal evaluation.

    recognized_precedence = (
        rule_3_4_precedence
        if isinstance(rule_3_4_precedence, str)
        and rule_3_4_precedence in {"rule_3", "rule_4", "clear"}
        else None
    )

    # --- Precedence 3: Normal Thinking-proposal evaluation ---
    decision_type = thinking_policy.get("decision_type", "")
    policy_snapshot = dict(thinking_policy)
    required_user_confirmation = thinking_policy.get("required_user_confirmation", False)

    # An existing block is never weakened by a contradictory signal/evidence
    # combination.
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

    # --- Governance Rule 5: exact high evidence plus clear Thinking signal ---
    risk_level = risk_evidence.get("risk_level") if isinstance(risk_evidence, dict) else None
    if recognized_precedence == "clear":
        if risk_level == "high":
            action_type = risk_evidence.get("action_type", "unknown")
            if not isinstance(action_type, str):
                action_type = "unknown"
            policy_snapshot = _format_rule_5_compatibility_policy(action_type)
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

        # --- Governance Rule 6: exact medium evidence plus clear signal ---
        if risk_level == "medium" and requested_action is not None:
            policy_snapshot = _format_rule_6_compatibility_policy(requested_action)
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

    # --- Existing proposal approval behavior (including Rule 4) ---
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

    # --- Rule 5: tool_execution_allowed is not True ---
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

    # --- Rule 6: tool_execution_allowed is True — legacy synthetic allow branch ---
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
