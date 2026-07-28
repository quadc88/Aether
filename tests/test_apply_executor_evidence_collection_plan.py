"""Tests for Apply Executor Evidence Collection Plan (Milestone 77A)."""

from aether.action.apply_executor_evidence_collection_plan import build_apply_executor_evidence_collection_plan


def test_missing_record_returns_blocked():
    plan = build_apply_executor_evidence_collection_plan(None)
    assert plan["decision"] == "blocked"
    assert plan["evidence_collection_plan_required"] is False


def test_basic_builder_structure():
    plan = build_apply_executor_evidence_collection_plan(None)
    assert isinstance(plan, dict)
    assert "decision" in plan
    assert "evidence_collection_plan_required" in plan
    assert "planned_collection_steps" in plan
    assert "planned_evidence_items" in plan
    assert len(plan["planned_collection_steps"]) == 6
    assert len(plan["planned_evidence_items"]) == 5


def test_planned_collection_steps_structure():
    plan = build_apply_executor_evidence_collection_plan(None)
    for step in plan["planned_collection_steps"]:
        assert step["allowed_to_collect_now"] is False
        assert step["allowed_to_execute_now"] is False
        assert step["requires_future_evidence_collector"] is True


def test_planned_evidence_items_structure():
    plan = build_apply_executor_evidence_collection_plan(None)
    for item in plan["planned_evidence_items"]:
        assert item["collected_now"] is False
        assert item["collection_allowed_now"] is False


def test_pre_execution_collection_plan_structure():
    plan = build_apply_executor_evidence_collection_plan(None)
    assert len(plan["pre_execution_collection_plan"]) >= 4
    for item in plan["pre_execution_collection_plan"]:
        assert item["collected_now"] is False
        assert item["collection_allowed_now"] is False


def test_during_execution_collection_plan_structure():
    plan = build_apply_executor_evidence_collection_plan(None)
    assert len(plan["during_execution_collection_plan"]) >= 3
    for item in plan["during_execution_collection_plan"]:
        assert item["collected_now"] is False
        assert item["collection_allowed_now"] is False


def test_post_execution_collection_plan_structure():
    plan = build_apply_executor_evidence_collection_plan(None)
    assert len(plan["post_execution_collection_plan"]) >= 3
    for item in plan["post_execution_collection_plan"]:
        assert item["collected_now"] is False
        assert item["collection_allowed_now"] is False


def test_rollback_collection_plan_structure():
    plan = build_apply_executor_evidence_collection_plan(None)
    assert len(plan["rollback_collection_plan"]) >= 4
    for item in plan["rollback_collection_plan"]:
        assert item["collected_now"] is False
        assert item["collection_allowed_now"] is False


def test_audit_collection_plan_structure():
    plan = build_apply_executor_evidence_collection_plan(None)
    assert len(plan["audit_collection_plan"]) >= 5
    for item in plan["audit_collection_plan"]:
        assert item["collected_now"] is False
        assert item["collection_allowed_now"] is False


def test_collection_execution_constraints_has_forbidden_methods():
    plan = build_apply_executor_evidence_collection_plan(None)
    forbidden = plan["collection_execution_constraints"]["forbidden_collection_methods"]
    assert "shell" in forbidden
    assert "subprocess" in forbidden


def test_collection_acceptance_plan_has_criteria():
    plan = build_apply_executor_evidence_collection_plan(None)
    assert len(plan["collection_acceptance_plan"]) >= 5
    for item in plan["collection_acceptance_plan"]:
        assert item["satisfied_now"] is False


def test_collector_boundary_structure():
    plan = build_apply_executor_evidence_collection_plan(None)
    b = plan["collector_boundary"]
    assert b["collector_exists"] is False
    assert b["collector_authorized"] is False
    assert b["collector_execution_allowed"] is False
    assert b["collection_allowed_now"] is False
    assert b["requires_future_evidence_collector"] is True


def test_metadata_present():
    plan = build_apply_executor_evidence_collection_plan(None)
    assert plan["metadata"]["source"] == "apply_executor_evidence_collection_plan_builder"
    assert plan["metadata"]["schema_version"] == "1.0"


def test_warnings_present():
    plan = build_apply_executor_evidence_collection_plan(None)
    warnings = plan["warnings"]
    assert any("does not authorize execution" in w for w in warnings)
    assert any("does not authorize apply" in w for w in warnings)


def test_empty_confirmations_for_blocked():
    plan = build_apply_executor_evidence_collection_plan(None)
    assert plan["required_collection_plan_confirmations"] == []


def test_no_statement_for_blocked():
    plan = build_apply_executor_evidence_collection_plan(None)
    assert plan["evidence_collection_plan_statement"] is None
