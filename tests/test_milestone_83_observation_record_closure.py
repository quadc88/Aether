from pathlib import Path

DOC = Path("docs/architecture/MILESTONE_83_OBSERVATION_RECORD_CLOSURE.md")


def _text() -> str:
    return DOC.read_text(encoding="utf-8")


def test_closure_doc_exists():
    assert DOC.exists()


def test_closure_doc_mentions_83a_through_83e():
    text = _text()
    for marker in (
        "83A",
        "83B",
        "83C",
        "83D",
        "83E",
        "milestone-83A-observation-record-boundary-tests",
        "milestone-83B-observation-record-schema-foundation",
        "milestone-83C-observation-record-service-and-store-foundation",
        "milestone-83D-observation-record-router-and-api-endpoints",
        "milestone-83E-observation-record-update-cancel-lifecycle",
    ):
        assert marker in text


def test_closure_doc_locks_final_public_api():
    text = _text()
    for endpoint in (
        "POST /observation-records",
        "GET /observation-records",
        "GET /observation-records/{observation_id}",
        "PATCH /observation-records/{observation_id}/status",
        "POST /observation-records/{observation_id}/cancel",
    ):
        assert endpoint in text
    for operation_id in (
        "create_observation_record",
        "get_observation_record",
        "list_observation_records",
        "update_observation_record_status",
        "cancel_observation_record",
    ):
        assert operation_id in text
    assert "304 paths" in text
    assert "108 schemas" in text
    assert "Observation paths exact 4" in text
    assert "Observation operation IDs exact 5" in text


def test_closure_doc_locks_protected_core_interface():
    text = _text()
    for marker in (
        "Protected Core Interface",
        "8 protected/core @app routes",
        "23 include_router",
        "zero direct /action/* routes",
        "New feature code must not be added to api_server.py",
    ):
        assert marker in text


def test_closure_doc_locks_status_and_decision_semantics():
    text = _text()
    for status in ("pending", "matched", "mismatched", "error", "cancelled"):
        assert status in text
    for marker in (
        "decision == new_status",
        "decision_reason == reason",
        'decision == "cancelled"',
        "queue update/cancel return None",
        "found=False",
        "observation_record=None",
    ):
        assert marker in text


def test_closure_doc_locks_response_shape_and_forbidden_fields():
    text = _text()
    for marker in (
        "pure ObservationRecordResponse",
        "No service envelope leakage",
        "No store lifecycle leakage",
    ):
        assert marker in text
    for forbidden_field in (
        "observation_id",
        "observation_type",
        "observed_at",
        "safety_flags",
        "created_at",
        "updated_at",
        "decision",
        "decided_at",
        "decision_reason",
        "warnings",
        "context_metadata",
        "status",
    ):
        assert forbidden_field in text
    assert "new_status" in text
    assert "Cancel only accepts reviewer and reason" in text
    assert "Update-status only accepts new_status, reviewer, reason" in text


def test_closure_doc_rejects_completed_status_now():
    text = _text()
    for marker in (
        "no completed status is added",
        "does not recommend adding a completed status",
        "future milestone only if a later architecture decision proves it necessary",
    ):
        assert marker in text


def test_closure_doc_locks_next_milestone_rule():
    text = _text()
    for marker in (
        "Milestone 84 Plan may start only after 83F Finalization is accepted",
        "Milestone 84 is not started by 83F Build",
        "Milestone 83 be declared closed",
    ):
        assert marker in text


def test_closure_doc_no_runtime_invocation_language():
    lowered = _text().lower()
    for forbidden in (
        "run real apply",
        "execute rollback",
        "collect real evidence now",
    ):
        assert forbidden not in lowered
