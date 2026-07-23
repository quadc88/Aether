"""Thinking Policy Layer for Aether.

Determines a safe decision about how to handle chat input based on
perception + risk + suggested tool + identity integrity status.
Does NOT execute tools or call external APIs.
"""

from __future__ import annotations


_SECRET_RISK_TERMS = {
    "password", "secret", "api key", "token", "private_key",
    "credential", "secret_key", "access_key",
}


def decide_chat_policy(
    perception: dict,
    risk: dict,
    suggested_tool: dict | None = None,
    identity_integrity_status: dict | None = None,
    metadata: dict | None = None,
) -> dict:
    """Decide the safest handling policy for a chat input.

    Decision rules are applied in order. Higher-priority rules
    (identity integrity, secrets) override lower ones.

    Args:
        perception: Output of perceive_text_input().
        risk: Output of classify_risk() from verification/risk.py.
        suggested_tool: Optional tool suggestion dict (may be None).
        identity_integrity_status: Safe summary from identity guard.
        metadata: Arbitrary metadata passed through.

    Returns:
        Dict with keys: decision_type, confidence, reasons,
        required_user_confirmation, tool_suggestion_allowed,
        tool_execution_allowed, blocked_reason, clarification_question,
        next_step, warnings.
    """
    reasons: list[str] = []
    warnings: list[str] = []
    normalized_text = perception.get("normalized_text", "")
    risk_terms = perception.get("risk_terms_detected", [])
    risk_level = risk.get("risk_level", "low")
    identity_status: str | None = None

    if identity_integrity_status:
        identity_status = identity_integrity_status.get("status", "")

    # --- Rule 1: Identity changed -> block ---
    if identity_status == "changed":
        return {
            "decision_type": "block",
            "confidence": "high",
            "reasons": ["Identity seed checksum changed — integrity compromised."],
            "required_user_confirmation": True,
            "tool_suggestion_allowed": False,
            "tool_execution_allowed": False,
            "blocked_reason": (
                "Identity integrity changed. Human review is required before continuing."
            ),
            "clarification_question": None,
            "next_step": "Verify identity seed integrity before continuing.",
            "warnings": [
                "Identity seed integrity mismatch detected.",
            ],
        }

    # --- Rule 2: Identity missing/failed -> require_approval ---
    if identity_status in ("missing", "failed"):
        return {
            "decision_type": "require_approval",
            "confidence": "high",
            "reasons": [
                f"Identity integrity status is '{identity_status}'. "
                "Human inspection is needed before proceeding."
            ],
            "required_user_confirmation": True,
            "tool_suggestion_allowed": False,
            "tool_execution_allowed": False,
            "blocked_reason": None,
            "clarification_question": None,
            "next_step": "Human should inspect identity integrity status.",
            "warnings": [f"Identity integrity status: {identity_status}."],
        }

    # --- Rule 3: Empty normalized text -> ask_clarification ---
    if not normalized_text or not normalized_text.strip():
        return {
            "decision_type": "ask_clarification",
            "confidence": "high",
            "reasons": ["Input text is empty or whitespace-only."],
            "required_user_confirmation": False,
            "tool_suggestion_allowed": False,
            "tool_execution_allowed": False,
            "blocked_reason": None,
            "clarification_question": "What would you like Aether to help with?",
            "next_step": "Wait for user to provide a valid input.",
            "warnings": [],
        }

    # --- Rule 4: Secret-like risk terms -> require_approval ---
    secret_found = any(t in _SECRET_RISK_TERMS for t in risk_terms)
    if secret_found:
        return {
            "decision_type": "require_approval",
            "confidence": "high",
            "reasons": [
                f"Text contains sensitive terms: {', '.join(risk_terms)}. "
                "User confirmation required before handling."
            ],
            "required_user_confirmation": True,
            "tool_suggestion_allowed": False,
            "tool_execution_allowed": False,
            "blocked_reason": None,
            "clarification_question": None,
            "next_step": "Confirm whether sensitive information should be handled.",
            "warnings": [
                "Potentially sensitive terms detected: " + ", ".join(risk_terms),
            ],
        }

    # --- Rule 5: High risk -> require_approval ---
    if risk_level == "high":
        action_type = risk.get("action_type", "unknown")
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

    # --- Rule 6: Medium risk with suggested tool -> require_approval ---
    if risk_level == "medium" and suggested_tool is not None:
        return {
            "decision_type": "require_approval",
            "confidence": "medium",
            "reasons": [
                f"Medium-risk request with suggested tool '{suggested_tool.get('tool_id', '')}'. "
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

    # --- Rule 7: Low risk with suggested tool -> suggest_tool ---
    if risk_level == "low" and suggested_tool is not None:
        return {
            "decision_type": "suggest_tool",
            "confidence": "medium",
            "reasons": [
                f"Low-risk request matched tool '{suggested_tool.get('tool_id', '')}'. "
                "Tool suggested but execution is disabled."
            ],
            "required_user_confirmation": False,
            "tool_suggestion_allowed": True,
            "tool_execution_allowed": False,
            "blocked_reason": None,
            "clarification_question": None,
            "next_step": "Present tool suggestion to user without executing.",
            "warnings": [],
        }

    # --- Rule 8: No tool, vague/short input -> ask_clarification ---
    if not suggested_tool and len(normalized_text) < 10:
        return {
            "decision_type": "ask_clarification",
            "confidence": "low",
            "reasons": [
                "Input is very short without a matching tool suggestion. "
                "Consider asking for more details."
            ],
            "required_user_confirmation": False,
            "tool_suggestion_allowed": False,
            "tool_execution_allowed": False,
            "blocked_reason": None,
            "clarification_question": "Can you provide more details?",
            "next_step": "Await user clarification before deeper processing.",
            "warnings": [],
        }

    # --- Rule 9: Default -> respond_only ---
    return {
        "decision_type": "respond_only",
        "confidence": "medium",
        "reasons": [
            "No elevated risk or special conditions detected. "
            "Safe to proceed with a textual response."
        ],
        "required_user_confirmation": False,
        "tool_suggestion_allowed": False,
        "tool_execution_allowed": False,
        "blocked_reason": None,
        "clarification_question": None,
        "next_step": "Generate a textual response to the user's input.",
        "warnings": warnings,
    }
