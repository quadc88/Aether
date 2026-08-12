"""Phase-2 coordination for the explicit governed restricted-read endpoint."""

from __future__ import annotations

import uuid
from pathlib import Path

from aether.action.approval_decision_gate import validate_restricted_read_approval
from aether.action.approval_queue import claim_approval_for_execution
from aether.action.services.restricted_file_read_bridge import dispatch_restricted_read
from aether.action.tool_planner import parse_restricted_read_command, normalize_restricted_read_target
from aether.perception.text import perceive_text_input
from aether.verification.risk import classify_risk
from aether.verification.restricted_file_read import verify_restricted_file_read


def _response(
    *, approval_id: str | None, status: str, attempt_status: str,
    verification_status: str, action_dispatched: bool = False,
    content: str | None = None, truncated: bool = False,
    reason: str | None = None, warnings: list[str] | None = None,
) -> dict:
    return {
        "name": "Aether", "status": status, "approval_id": approval_id,
        "execution_attempt_status": attempt_status,
        "verification_status": verification_status,
        "action_dispatched": action_dispatched, "content": content,
        "truncated": truncated, "reason": reason, "warnings": warnings or [],
        "tool_execution_allowed": False,
    }


def execute_approved_restricted_read(request) -> dict:
    attempt_id = f"read_attempt_{uuid.uuid4().hex}"
    requested_action = parse_restricted_read_command(request.request_text)
    if requested_action is None:
        return _response(
            approval_id=request.approval_id, status="denied", attempt_status="REJECTED",
            verification_status="DENIED", reason="Request text is not an exact read command.",
        )
    request_target = normalize_restricted_read_target(request.target)
    if (
        request.capability_id != "file.restricted_read"
        or request.permission_class != "read_only"
        or requested_action.get("target") != request_target
        or requested_action["parameters"]["max_chars"] != request.max_chars
    ):
        return _response(
            approval_id=request.approval_id, status="denied", attempt_status="REJECTED",
            verification_status="DENIED", reason="Execution request does not match the exact read binding.",
        )

    binding = validate_restricted_read_approval(
        request.approval_id, requested_action, request.session_id,
    )
    if not binding.get("approval_valid"):
        return _response(
            approval_id=request.approval_id, status="denied", attempt_status="REJECTED",
            verification_status="DENIED", reason=binding.get("reason"),
        )

    perception = perceive_text_input(request.request_text, metadata={"session_id": request.session_id})
    risk = classify_risk(request.request_text)
    if risk.get("risk_level") == "low":
        risk = {**risk, "risk_level": "medium", "action_type": "restricted_file_read"}
    identity = None
    try:
        from aether.identity.guard import verify_identity_integrity
        identity = verify_identity_integrity()
    except Exception:
        identity = {"status": "failed", "changed": False}
    from aether.thinking.policy import _evaluate_chat_policy_with_precedence
    thinking, precedence = _evaluate_chat_policy_with_precedence(
        perception=perception, risk=risk, suggested_tool=requested_action,
        identity_integrity_status=identity,
        metadata={"session_id": request.session_id},
    )
    from aether.core.governance import authorize_restricted_read_execution
    decision = authorize_restricted_read_execution(
        thinking_policy=thinking, requested_action=requested_action,
        context={"session_id": request.session_id}, risk_evidence=risk,
        identity_integrity_evidence=identity, rule_3_4_precedence=precedence,
        rule4_risk_terms_detected=perception.get("risk_terms_detected", []),
        approval_evidence=binding, execution_attempt_id=attempt_id,
        session_id=request.session_id,
    )
    if not decision.authorization_granted or decision.scope is None:
        return _response(
            approval_id=request.approval_id, status="denied", attempt_status="REJECTED",
            verification_status="DENIED", reason=decision.safe_reason,
            warnings=list(decision.warnings),
        )
    claim = claim_approval_for_execution(request.approval_id, attempt_id)
    if not claim.get("claimed"):
        return _response(
            approval_id=request.approval_id, status="denied", attempt_status="REJECTED",
            verification_status="DENIED", reason="Approval could not be claimed.",
        )
    try:
        result = dispatch_restricted_read(decision.scope, execution_attempt_id=attempt_id)
        observation = result.pop("observation", None)
        verification = verify_restricted_file_read(
            authorized=True, reader_result=result, observation=observation,
        )
        if verification in {"VERIFIED_SUCCESS", "VERIFIED_PARTIAL"}:
            return _response(
                approval_id=request.approval_id, status="completed", attempt_status="COMPLETED",
                verification_status=verification, action_dispatched=True,
                content=result.get("content"), truncated=bool(result.get("truncated")),
            )
        status = "error" if verification == "INTERNAL_ERROR" else "denied"
        return _response(
            approval_id=request.approval_id, status=status, attempt_status="FAILED",
            verification_status=verification, action_dispatched=True,
            truncated=bool(result.get("truncated")), reason=result.get("reason"),
        )
    except Exception:
        return _response(
            approval_id=request.approval_id, status="error", attempt_status="FAILED",
            verification_status="INTERNAL_ERROR", action_dispatched=True,
            reason="Restricted read execution failed safely.",
        )
