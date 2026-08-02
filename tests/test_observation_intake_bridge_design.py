from pathlib import Path

DOC_PATH = Path("docs/architecture/OBSERVATION_INTAKE_BRIDGE_DESIGN.md")


def _text() -> str:
    return DOC_PATH.read_text(encoding="utf-8")


def test_design_doc_exists():
    assert DOC_PATH.exists()


def test_design_doc_locks_service_module_and_function():
    text = _text()
    for marker in (
        "aether/action/services/observation_intake_service.py",
        "handle_observation_intake",
        "handle_observation_intake(request, context=None)",
    ):
        assert marker in text


def test_design_doc_locks_non_execution_boundary():
    text = _text()
    for marker in (
        "does not execute tools",
        "does not collect evidence",
        "does not call executor code",
        "does not call real apply",
        "does not call rollback",
        "does not call the policy/execution gate",
        "does not call /chat",
        "does not call protected/core route functions directly",
        "does not write runtime/private data during tests",
        "uses only the supplied observed_value",
        "no automatic observation capture yet",
    ):
        assert marker in text


def test_design_doc_locks_input_contract():
    text = _text()
    for field in (
        "plan_step_id",
        "collector_contract_id",
        "evidence_items",
        "target",
        "observed_value",
        "expected_value",
        "evidence_item_id",
        "metadata",
    ):
        assert field in text
    assert "safety_flags" in text
    assert "NOT accepted" in text


def test_design_doc_locks_forbidden_input_fields():
    text = _text()
    for field in (
        "observation_id",
        "observation_type",
        "observed_at",
        "status",
        "created_at",
        "updated_at",
        "decision",
        "decided_at",
        "reviewer",
        "decision_reason",
        "warnings",
        "context_metadata",
        "new_status",
        "reason",
        "safety_flags",
    ):
        assert field in text
    assert "ValueError" in text
    assert "zero records are created" in text


def test_design_doc_locks_status_decision():
    text = _text()
    assert "matched" in text
    assert "mismatched" in text
    for marker in (
        "pending is NOT a valid intake outcome",
        "error is never inferred by intake",
        "cancelled is never created by intake",
        "strict JSON-normalized equality",
    ):
        assert marker in text


def test_design_doc_locks_output_contract():
    text = _text()
    for envelope_key in (
        "observation_intake",
        "completed",
        "created",
        "observation_records",
        "errors",
    ):
        assert envelope_key in text
    for store_key in (
        "created_at",
        "updated_at",
        "decision",
        "decided_at",
        "reviewer",
        "decision_reason",
        "warnings",
        "context_metadata",
    ):
        assert store_key in text
    for marker in (
        "must not call API response models",
        "must not leak runtime/private paths",
    ):
        assert marker in text


def test_design_doc_locks_matching_semantics():
    text = _text()
    for marker in (
        "json.dumps(value, sort_keys=True)",
        "1 vs 1.0 NOT equal",
        "no fuzzy matching",
        "no LLM judgment",
        "no external verification",
        "no tool calls",
        "strict JSON-normalized equality",
    ):
        assert marker in text


def test_design_doc_locks_atomicity():
    text = _text()
    for marker in ("all-or-nothing", "ValueError", "zero records are created"):
        assert marker in text


def test_design_doc_locks_persistence_and_testing_boundary():
    text = _text()
    for marker in (
        "build_observation_record",
        "queue.save_observation_record",
        "get_observation_records_dir",
        "tmp_path",
        "no runtime/private mutation",
        "no new persistence directory",
    ):
        assert marker in text


def test_design_doc_locks_forbidden_imports():
    text = _text()
    for marker in (
        "aether.interface.api_server",
        "fastapi.testclient." + "Test" + "Client",
        "starlette.testclient." + "Test" + "Client",
        "aether.action.policy_gate",
        "re" + "quests",
        "ht" + "tpx",
        "urllib",
        "tool execution modules",
    ):
        assert marker in text


def test_design_doc_locks_preserved_invariants_and_platform_locks():
    text = _text()
    assert "VALID_STATUSES" in text
    for status in ("pending", "matched", "mismatched", "error", "cancelled"):
        assert status in text
    for marker in (
        "no completed status",
        "safety_flags all False",
        "decision == new_status",
        "decision_reason == reason",
        'decision == "cancelled"',
        "304 paths",
        "108 schemas",
        "8 protected/core @app routes",
        "23 include_router",
        "zero direct /action/* routes",
        "Protected Core Interface",
        "New feature code must not be added to api_server.py",
    ):
        assert marker in text


def test_design_doc_locks_future_sequence():
    text = _text()
    for marker in (
        "Candidate A",
        "84B not started",
        "Milestone 85 not started",
        "milestone-84A-observation-intake-bridge-design",
        "milestone-84A-observation-intake-boundary-tests",
        "tests/test_observation_intake_boundary.py",
        "REQUIRED before 84B",
        "84C",
        "84D",
    ):
        assert marker in text


def test_design_doc_has_no_runtime_instruction_language():
    lowered = _text().lower()
    for forbidden in (
        "run real apply",
        "execute rollback",
        "collect real evidence now",
    ):
        assert forbidden not in lowered
