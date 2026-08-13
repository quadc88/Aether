"""Thin service boundary for explicit governed restricted-read attempts."""


def handle_restricted_file_read_execution(request):
    from aether.core.coordination import execute_approved_restricted_read
    return execute_approved_restricted_read(request)


def _resume_response(
    *, approval_id: str | None, approval_state: str, status: str = "denied",
    attempt_status: str = "REJECTED", reason: str | None = None,
    warnings: list[str] | None = None,
) -> dict:
    return {
        "name": "Aether",
        "status": status,
        "approval_id": approval_id,
        "approval_state": approval_state,
        "execution_attempt_status": attempt_status,
        "verification_status": None,
        "action_dispatched": False,
        "content": None,
        "truncated": False,
        "reason": reason,
        "warnings": warnings or [],
        "tool_execution_allowed": False,
    }


def _approval_state(record: dict | None) -> str:
    if record is None:
        return "missing"
    if not isinstance(record, dict):
        return "invalid"
    status = record.get("status")
    if status not in {"pending", "approved", "rejected", "cancelled"}:
        return "invalid"
    if status == "approved" and (
        record.get("execution_consumed") is True
        or record.get("consumed_by_execution_attempt") is not None
    ):
        return "consumed"
    return status


def _is_usable_restricted_read_record(record: dict) -> bool:
    from aether.action.approval_queue import restricted_read_fingerprint

    approval_request = record.get("approval_request")
    metadata = record.get("metadata")
    if not isinstance(approval_request, dict) or not isinstance(metadata, dict):
        return False
    action = approval_request.get("requested_action")
    fingerprint = restricted_read_fingerprint(action)
    return bool(fingerprint and record.get("requested_action_fingerprint") == fingerprint)


def _map_producer_result(result: dict, approval_id: str, approval_state: str) -> dict:
    # A coordinator preflight denial is not capability Verification. The
    # producer marks a real Action attempt with action_dispatched.
    verification = result.get("verification_status") if result.get("action_dispatched") else None
    successful = verification in {"VERIFIED_SUCCESS", "VERIFIED_PARTIAL"}
    return {
        "name": "Aether",
        "status": "completed" if successful else ("error" if verification == "INTERNAL_ERROR" else "denied"),
        "approval_id": approval_id,
        "approval_state": approval_state,
        "execution_attempt_status": result.get("execution_attempt_status"),
        "verification_status": verification,
        "action_dispatched": bool(result.get("action_dispatched", False)),
        "content": result.get("content") if successful else None,
        "truncated": bool(result.get("truncated", False)) if successful else False,
        "reason": result.get("reason"),
        "warnings": list(result.get("warnings") or []),
        "tool_execution_allowed": False,
    }


def handle_restricted_read_chat_resume(request):
    """Preflight a chat resume, then delegate the real attempt to M94B."""
    from aether.action.approval_queue import get_approval_record, restricted_read_fingerprint
    from aether.action.tool_planner import parse_restricted_read_command
    from aether.interface.api_models import ApprovedReadExecutionAttemptRequest

    try:
        record = get_approval_record(request.approval_id)
    except Exception:
        return _resume_response(
            approval_id=request.approval_id, approval_state="invalid",
            reason="Approval record is malformed.",
        )

    state = _approval_state(record)
    if state == "missing":
        return _resume_response(
            approval_id=request.approval_id, approval_state=state,
            reason="Approval record was not found.",
        )
    if state == "invalid" or not _is_usable_restricted_read_record(record):
        return _resume_response(
            approval_id=request.approval_id, approval_state="invalid",
            reason="Approval record is malformed or unusable.",
        )
    if state != "approved":
        return _resume_response(
            approval_id=request.approval_id, approval_state=state,
            status="pending" if state == "pending" else "denied",
            attempt_status="NOT_ATTEMPTED" if state == "pending" else "REJECTED",
            reason=("Approval is still pending." if state == "pending"
                    else "Approval is not executable."),
        )

    action = parse_restricted_read_command(request.request_text)
    if action is None:
        return _resume_response(
            approval_id=request.approval_id, approval_state=state,
            reason="Request text is not an exact read command.",
        )

    stored_action = record["approval_request"]["requested_action"]
    if action != stored_action or restricted_read_fingerprint(action) != record.get(
        "requested_action_fingerprint"
    ):
        return _resume_response(
            approval_id=request.approval_id, approval_state=state,
            reason="Execution request does not match the exact read binding.",
        )
    stored_session = record["metadata"].get("session_id")
    if stored_session is not None and stored_session != request.session_id:
        return _resume_response(
            approval_id=request.approval_id, approval_state=state,
            reason="Session binding does not match the approval.",
        )

    execution_request = ApprovedReadExecutionAttemptRequest(
        approval_id=request.approval_id,
        request_text=request.request_text,
        capability_id="file.restricted_read",
        target=action["target"],
        permission_class="read_only",
        max_chars=action["parameters"]["max_chars"],
        session_id=request.session_id,
    )
    result = handle_restricted_file_read_execution(execution_request)
    post_record = get_approval_record(request.approval_id)
    return _map_producer_result(
        result, request.approval_id, _approval_state(post_record) or state
    )
