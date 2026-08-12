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

from dataclasses import dataclass
from pathlib import Path
import threading
from typing import Callable, Literal, Mapping

from aether.core.config import get_restricted_file_read_approved_roots


_SECRET_RISK_TERMS = {
    "password", "secret", "api key", "token", "private_key",
    "credential", "secret_key", "access_key",
}
_MISSING_RULE4_RISK_TERMS = object()


class _ScopeDispatchState:
    def __init__(self) -> None:
        self.lock = threading.Lock()
        self.consumed = False


@dataclass(frozen=True)
class RestrictedReadScope:
    capability_id: Literal["file.restricted_read"]
    bound_function: Callable[..., dict]
    normalized_target: str
    approved_root: Path
    permission_class: Literal["read_only"]
    max_chars: int
    execution_attempt_id: str
    session_id: str | None
    task_binding: str | None
    _dispatch_state: _ScopeDispatchState


@dataclass(frozen=True)
class RestrictedReadAuthorizationDecision:
    generic_envelope: Mapping[str, object]
    approval_requirement_state: Literal[
        "not_required", "required_unsatisfied", "required_satisfied", "invalid_or_stale"
    ]
    approval_requirement_satisfied: bool
    authorization_granted: bool
    scope: RestrictedReadScope | None
    safe_reason: str
    warnings: tuple[str, ...]


def authorize_restricted_read_execution(
    *,
    thinking_policy: dict | None,
    requested_action: dict | None,
    context: dict | None = None,
    risk_evidence: dict | None = None,
    identity_integrity_evidence: dict | None = None,
    rule_3_4_precedence: str | None = None,
    rule4_risk_terms_detected=None,
    approval_evidence: dict | None = None,
    execution_attempt_id: str = "",
    session_id: str | None = None,
) -> RestrictedReadAuthorizationDecision:
    """Authorize only one exact restricted-read attempt and mint its scope."""
    generic = evaluate_authorization_envelope(
        thinking_policy=thinking_policy,
        requested_action=requested_action,
        context=context,
        risk_evidence=risk_evidence,
        identity_integrity_evidence=identity_integrity_evidence,
        rule_3_4_precedence=rule_3_4_precedence,
        rule4_risk_terms_detected=rule4_risk_terms_detected,
    )
    denied = lambda state, reason, warnings=(): RestrictedReadAuthorizationDecision(
        generic, state, False, False, None, reason, tuple(warnings)
    )
    if not isinstance(requested_action, dict) or requested_action.get("tool_id") != "file.restricted_read":
        return denied("invalid_or_stale", "Restricted-read action binding is invalid.")
    if rule_3_4_precedence == "rule_3":
        return denied("required_unsatisfied", "Current Thinking precedence blocks the read.")
    identity_status = identity_integrity_evidence.get("status") if isinstance(identity_integrity_evidence, Mapping) else None
    if identity_status == "changed":
        return denied("required_unsatisfied", "Identity integrity changed.")
    if identity_status in {"missing", "failed", "not_initialized"}:
        return denied("required_unsatisfied", "Identity integrity is not verified.")
    if not isinstance(thinking_policy, dict) or thinking_policy.get("decision_type") == "block":
        return denied("required_unsatisfied", "Current Thinking policy blocks the read.")
    risk_terms = rule4_risk_terms_detected or []
    if isinstance(risk_terms, (list, tuple)):
        for term in risk_terms:
            if term in _SECRET_RISK_TERMS:
                return denied("required_unsatisfied", "Current sensitive evidence blocks the read.")
    if not isinstance(risk_evidence, dict) or risk_evidence.get("risk_level") != "medium":
        return denied("required_unsatisfied", "Current risk evidence is not eligible for this read.")
    if rule_3_4_precedence != "clear":
        return denied("required_unsatisfied", "Current Thinking precedence is unavailable.")
    if approval_evidence is None:
        approval_state = "required_unsatisfied"
    elif approval_evidence.get("approval_valid") is True:
        approval_state = "required_satisfied"
    else:
        return denied("invalid_or_stale", "Approval evidence is invalid or stale.")
    roots = get_restricted_file_read_approved_roots()
    if not roots:
        return denied(approval_state, "No approved restricted-read root is configured.")
    target = requested_action.get("target")
    params = requested_action.get("parameters")
    if (
        not isinstance(target, str) or requested_action.get("permission_class") != "read_only"
        or not isinstance(params, dict) or set(params) != {"max_chars"}
        or not isinstance(params["max_chars"], int) or not 0 <= params["max_chars"] <= 12000
    ):
        return denied("invalid_or_stale", "Restricted-read parameters are invalid.")
    normalized = Path(target).expanduser().resolve(strict=False)
    root = next((root for root in roots if normalized == root or root in normalized.parents), None)
    if root is None:
        return denied("required_satisfied", "Target is outside approved restricted-read roots.")
    from aether.action.restricted_file_reader import read_restricted_file
    scope = RestrictedReadScope(
        "file.restricted_read", read_restricted_file, str(normalized), root,
        "read_only", params["max_chars"], execution_attempt_id, session_id,
        (context or {}).get("task_binding"), _ScopeDispatchState(),
    )
    return RestrictedReadAuthorizationDecision(
        generic, approval_state, True, True, scope, "Restricted read authorized.", ()
    )


def _format_rule_4_compatibility_policy(risk_terms_detected) -> dict:
    """Format the complete effective Rule 4 policy projection."""
    return {
        "decision_type": "require_approval",
        "confidence": "high",
        "reasons": [
            "Text contains sensitive terms: "
            + ", ".join(risk_terms_detected)
            + ". User confirmation required before handling."
        ],
        "required_user_confirmation": True,
        "tool_suggestion_allowed": False,
        "tool_execution_allowed": False,
        "blocked_reason": None,
        "clarification_question": None,
        "next_step": "Confirm whether sensitive information should be handled.",
        "warnings": [
            "Potentially sensitive terms detected: "
            + ", ".join(risk_terms_detected)
        ],
    }


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
    rule4_risk_terms_detected=_MISSING_RULE4_RISK_TERMS,
) -> dict:
    """Evaluate the Core Governance authorization decision envelope.

    This is the single authoritative compatibility decision implementation.
    Thinking proposes (Rules 3-9 only). Verification and Identity supply
    evidence. Core Governance evaluates Identity Rules 1 and 2 and
    authorizes. Action executes only within authorization.

    The keyword-only arguments are direct call-local provenance inputs. The
    Rule 3 signal is recognized only for its exact private value, and the Rule
    4 evidence sidecar is never copied into an output.

    Args:
        thinking_policy: Output of decide_chat_policy(). Non-authoritative
            proposal data (Rules 3-9 only after Milestone 89B).
        requested_action: The action/tool being requested (optional).
        context: Additional context dict (optional, not used in decision).
        risk_evidence: Raw existing risk dictionary from classify_risk.
            Provenance-only; remains non-operative.
        identity_integrity_evidence: Safe summary from identity guard.
            Operative only for Identity Rules 1 and 2.
        rule_3_4_precedence: Private Thinking precedence signal. Only the
            exact values ``rule_3`` and ``clear`` are recognized.
        rule4_risk_terms_detected: Private factual iterable transported from
            Perception. Omitted input defaults to an empty list.

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
        and rule_3_4_precedence in {"rule_3", "clear"}
        else None
    )

    risk_terms_detected = (
        []
        if rule4_risk_terms_detected is _MISSING_RULE4_RISK_TERMS
        else rule4_risk_terms_detected
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

    # --- Governance Rule 4: exact sensitive-term evidence plus clear signal ---
    risk_level = risk_evidence.get("risk_level") if isinstance(risk_evidence, dict) else None
    if recognized_precedence == "clear":
        secret_found = any(
            t in _SECRET_RISK_TERMS
            for t in risk_terms_detected
        )
        if secret_found:
            policy_snapshot = _format_rule_4_compatibility_policy(risk_terms_detected)
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

        # --- Governance Rule 5: exact high evidence plus clear Thinking signal ---
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
