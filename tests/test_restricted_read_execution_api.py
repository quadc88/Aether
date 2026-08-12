from aether.interface.api_models import ApprovedReadExecutionAttemptRequest, RestrictedFileReadExecutionAttemptResponse


def _request(**changes):
    values = {"approval_id": "a", "request_text": 'read file "x.py"', "capability_id": "file.restricted_read", "target": "x.py", "permission_class": "read_only"}
    values.update(changes)
    return ApprovedReadExecutionAttemptRequest(**values)


def _response(**changes):
    values = {"status": "denied", "execution_attempt_status": "REJECTED", "verification_status": "DENIED"}
    values.update(changes)
    return RestrictedFileReadExecutionAttemptResponse(**values)


def test_request_defaults(): assert _request().max_chars == 12000
def test_request_approval_id(): assert _request().approval_id == "a"
def test_request_capability(): assert _request().capability_id == "file.restricted_read"
def test_request_permission(): assert _request().permission_class == "read_only"
def test_request_target(): assert _request().target == "x.py"
def test_request_text(): assert _request().request_text.startswith("read file")
def test_request_session_default(): assert _request().session_id is None
def test_request_zero_bound(): assert _request(max_chars=0).max_chars == 0
def test_request_upper_bound(): assert _request(max_chars=12000).max_chars == 12000
def test_response_default_name(): assert _response().name == "Aether"
def test_response_denied_status(): assert _response().status == "denied"
def test_response_attempt_status(): assert _response().execution_attempt_status == "REJECTED"
def test_response_verification_status(): assert _response().verification_status == "DENIED"
def test_response_tool_false(): assert _response().tool_execution_allowed is False
def test_response_content_optional(): assert _response().content is None
def test_response_warning_default(): assert _response().warnings == []
def test_response_success(): assert _response(status="completed", execution_attempt_status="COMPLETED", verification_status="VERIFIED_SUCCESS").status == "completed"
def test_response_partial(): assert _response(status="completed", execution_attempt_status="COMPLETED", verification_status="VERIFIED_PARTIAL").verification_status == "VERIFIED_PARTIAL"
def test_response_not_found(): assert _response(verification_status="NOT_FOUND").verification_status == "NOT_FOUND"
def test_response_changed(): assert _response(verification_status="CHANGED_DURING_READ").verification_status == "CHANGED_DURING_READ"
def test_response_internal(): assert _response(status="error", execution_attempt_status="FAILED", verification_status="INTERNAL_ERROR").status == "error"
def test_response_content(): assert _response(status="completed", execution_attempt_status="COMPLETED", verification_status="VERIFIED_SUCCESS", content="safe").content == "safe"
def test_response_truncated(): assert _response(truncated=True).truncated is True
def test_response_reason(): assert _response(reason="safe").reason == "safe"
def test_response_approval(): assert _response(approval_id="a").approval_id == "a"
def test_request_extra_is_ignored_by_default_model(): assert _request().model_dump()["approval_id"] == "a"
def test_request_model_name(): assert ApprovedReadExecutionAttemptRequest.__name__ == "ApprovedReadExecutionAttemptRequest"
def test_response_model_name(): assert RestrictedFileReadExecutionAttemptResponse.__name__ == "RestrictedFileReadExecutionAttemptResponse"
def test_request_json_has_bound(): assert '"max_chars":12000' in _request().model_dump_json()
def test_response_json_has_safe_flag(): assert '"tool_execution_allowed":false' in _response().model_dump_json()
def test_request_session_value(): assert _request(session_id="s").session_id == "s"
