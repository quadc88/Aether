"""Tests for Apply Executor Evidence Collector Contract (Milestone 79A)."""

from aether.action.apply_executor_evidence_collector_contract import (
    build_apply_executor_evidence_collector_contract as _build_cc,
)


def _valid_record():
    """Return a fully valid approved_collection_plan_intent record."""
    return {
        "apply_executor_evidence_collection_plan_id": "p1",
        "apply_executor_evidence_contract_id": "ec1",
        "apply_executor_plan_id": "ap1", "apply_executor_contract_id": "ac1",
        "apply_execution_gate_id": "aeg1", "human_authorization_id": "ha1",
        "apply_gate_id": "ag1", "verification_verdict_id": "vv1",
        "simulation_result_id": "sr1", "simulation_plan_id": "sp1", "dry_run_id": "dr1",
        "status": "approved_collection_plan_intent",
        "decision": "approved_collection_plan_intent",
        "evidence_collection_plan_decision": "evidence_collection_plan_ready",
        "evidence_collection_plan_intent_recorded": True,
        "evidence_collection_plan_review_completed": True,
        "apply_executor_evidence_collection_plan_persisted": True,
        "confirmations_required": ["c1"],
        "confirmations_received": ["c1"],
        "evidence_collected": False, "rollback_plan_attached": False, "apply_authorized": False,
        "apply_allowed": False, "execution_allowed": False, "tool_execution_allowed": False,
        "apply_executed": False, "rollback_executed": False,
        "apply_executor_evidence_collection_plan": {
            "decision": "evidence_collection_plan_ready",
            "planned_collection_steps": [{"name": f"s{i}"} for i in range(6)],
            "planned_evidence_items": [{"name": f"i{i}"} for i in range(5)],
            "pre_execution_collection_plan": [{"name": f"pre{i}"} for i in range(4)],
            "during_execution_collection_plan": [{"name": f"dur{i}"} for i in range(3)],
            "post_execution_collection_plan": [{"name": f"post{i}"} for i in range(3)],
            "rollback_collection_plan": [{"name": f"rb{i}"} for i in range(4)],
            "audit_collection_plan": [{"name": f"au{i}"} for i in range(5)],
            "collection_execution_constraints": {"contract_scope": "contract_only_no_collection", "collection_allowed_now": False},
            "collector_boundary": {"collector_exists": False},
            "collection_acceptance_plan": [{"criterion": f"c{i}", "required": True, "satisfied_now": False} for i in range(5)],
            "requested_action": {"tool_id": "test.tool", "action_type": "status_check", "target": "test"},
            "blocking_reasons": [],
            "apply_authorized": False, "apply_allowed": False, "rollback_allowed": False,
            "execution_allowed": False, "tool_execution_allowed": False,
            "dry_run_execution_allowed": False, "simulation_execution_allowed": False,
            "apply_gate_execution_allowed": False, "human_authorization_execution_allowed": False,
            "apply_execution_gate_execution_allowed": False, "apply_executor_contract_execution_allowed": False,
            "apply_executor_plan_execution_allowed": False, "apply_executor_evidence_contract_execution_allowed": False,
            "apply_executor_evidence_collection_plan_execution_allowed": False,
            "apply_executor_evidence_collection_plan_record_execution_allowed": False,
            "apply_executor_evidence_collector_contract_execution_allowed": False,
        },
    }


def test_01_missing_record_returns_blocked():
    cc = _build_cc(None)
    assert cc["decision"] == "blocked"
    assert cc["collector_contract_required"] is False


def test_02_pending_record_is_blocked():
    rec = {"status": "pending", "decision": "not_ready", "evidence_collection_plan_intent_recorded": False}
    cc = _build_cc(rec)
    assert cc["decision"] == "blocked"


def test_03_rejected_record_is_blocked():
    rec = {"status": "rejected", "decision": "rejected", "evidence_collection_plan_intent_recorded": True}
    cc = _build_cc(rec)
    assert cc["decision"] == "blocked"


def test_04_cancelled_record_is_blocked():
    rec = {"status": "cancelled", "decision": "cancelled", "evidence_collection_plan_intent_recorded": True}
    cc = _build_cc(rec)
    assert cc["decision"] == "blocked"


def test_05_not_ready_source_is_blocked():
    rec = {"status": "approved_collection_plan_intent", "decision": "approved_collection_plan_intent",
           "evidence_collection_plan_decision": "not_ready",
           "evidence_collection_plan_intent_recorded": True, "evidence_collection_plan_review_completed": True,
           "apply_executor_evidence_collection_plan_persisted": True,
           "apply_executor_evidence_collection_plan": {"decision": "not_ready"}}
    cc = _build_cc(rec)
    assert cc["decision"] == "blocked"


def test_06_blocked_source_is_blocked():
    rec = {"status": "approved_collection_plan_intent", "decision": "approved_collection_plan_intent",
           "evidence_collection_plan_decision": "blocked",
           "evidence_collection_plan_intent_recorded": True, "evidence_collection_plan_review_completed": True,
           "apply_executor_evidence_collection_plan_persisted": True,
           "apply_executor_evidence_collection_plan": {"decision": "blocked"}}
    cc = _build_cc(rec)
    assert cc["decision"] == "blocked"


def test_07_intent_recorded_false_blocks():
    rec = {"status": "approved_collection_plan_intent", "decision": "approved_collection_plan_intent",
           "evidence_collection_plan_decision": "evidence_collection_plan_ready",
           "evidence_collection_plan_intent_recorded": False, "evidence_collection_plan_review_completed": True,
           "apply_executor_evidence_collection_plan_persisted": True,
           "apply_executor_evidence_collection_plan": {"decision": "evidence_collection_plan_ready"}}
    cc = _build_cc(rec)
    assert cc["decision"] == "blocked"


def test_08_review_completed_false_blocks():
    rec = {"status": "approved_collection_plan_intent", "decision": "approved_collection_plan_intent",
           "evidence_collection_plan_decision": "evidence_collection_plan_ready",
           "evidence_collection_plan_intent_recorded": True, "evidence_collection_plan_review_completed": False,
           "apply_executor_evidence_collection_plan_persisted": True,
           "apply_executor_evidence_collection_plan": {"decision": "evidence_collection_plan_ready"}}
    cc = _build_cc(rec)
    assert cc["decision"] == "blocked"


def test_09_evidence_collected_true_blocks():
    rec = {"status": "approved_collection_plan_intent", "decision": "approved_collection_plan_intent",
           "evidence_collection_plan_decision": "evidence_collection_plan_ready",
           "evidence_collection_plan_intent_recorded": True, "evidence_collection_plan_review_completed": True,
           "apply_executor_evidence_collection_plan_persisted": True, "evidence_collected": True,
           "apply_executor_evidence_collection_plan": {"decision": "evidence_collection_plan_ready"}}
    cc = _build_cc(rec)
    assert cc["decision"] == "blocked"


def test_10_rollback_plan_attached_true_blocks():
    rec = {"status": "approved_collection_plan_intent", "decision": "approved_collection_plan_intent",
           "evidence_collection_plan_decision": "evidence_collection_plan_ready",
           "evidence_collection_plan_intent_recorded": True, "evidence_collection_plan_review_completed": True,
           "apply_executor_evidence_collection_plan_persisted": True, "rollback_plan_attached": True,
           "apply_executor_evidence_collection_plan": {"decision": "evidence_collection_plan_ready"}}
    cc = _build_cc(rec)
    assert cc["decision"] == "blocked"


def test_11_apply_authorized_true_blocks():
    rec = {"status": "approved_collection_plan_intent", "decision": "approved_collection_plan_intent",
           "evidence_collection_plan_decision": "evidence_collection_plan_ready",
           "evidence_collection_plan_intent_recorded": True, "evidence_collection_plan_review_completed": True,
           "apply_executor_evidence_collection_plan_persisted": True, "apply_authorized": True,
           "apply_executor_evidence_collection_plan": {"decision": "evidence_collection_plan_ready"}}
    cc = _build_cc(rec)
    assert cc["decision"] == "blocked"


def test_12_apply_executed_true_blocks():
    rec = {"status": "approved_collection_plan_intent", "decision": "approved_collection_plan_intent",
           "evidence_collection_plan_decision": "evidence_collection_plan_ready",
           "evidence_collection_plan_intent_recorded": True, "evidence_collection_plan_review_completed": True,
           "apply_executor_evidence_collection_plan_persisted": True, "apply_executed": True,
           "apply_executor_evidence_collection_plan": {"decision": "evidence_collection_plan_ready"}}
    cc = _build_cc(rec)
    assert cc["decision"] == "blocked"


def test_13_missing_nested_plan_returns_not_ready():
    rec = {"status": "approved_collection_plan_intent", "decision": "approved_collection_plan_intent",
           "evidence_collection_plan_decision": "evidence_collection_plan_ready",
           "evidence_collection_plan_intent_recorded": True, "evidence_collection_plan_review_completed": True,
           "apply_executor_evidence_collection_plan_persisted": True,
           "apply_executor_evidence_collection_plan": None}
    cc = _build_cc(rec)
    assert cc["decision"] == "not_ready"


def test_14_ready_approved_plan_returns_collector_contract_ready():
    rec = _valid_record()
    cc = _build_cc(rec)
    assert cc["decision"] == "collector_contract_ready"
    assert cc["collector_contract_required"] is True


def test_15_collector_contract_ready_keeps_safety_flags_false():
    rec = _valid_record()
    cc = _build_cc(rec)
    assert cc["evidence_collected"] is False
    assert cc["apply_authorized"] is False
    assert cc["execution_allowed"] is False
    assert cc["rollback_plan_attached"] is False


def test_16_all_execution_flags_false():
    rec = _valid_record()
    cc = _build_cc(rec)
    flags = ["execution_allowed", "tool_execution_allowed", "dry_run_execution_allowed",
             "simulation_execution_allowed", "apply_gate_execution_allowed",
             "human_authorization_execution_allowed", "apply_execution_gate_execution_allowed",
             "apply_executor_contract_execution_allowed", "apply_executor_plan_execution_allowed",
             "apply_executor_evidence_contract_execution_allowed",
             "apply_executor_evidence_collection_plan_execution_allowed",
             "apply_executor_evidence_collection_plan_record_execution_allowed",
             "apply_executor_evidence_collector_contract_execution_allowed"]
    for f in flags:
        assert cc.get(f) is False


def test_17_collector_contract_checks_included():
    rec = _valid_record()
    cc = _build_cc(rec)
    names = [c["name"] for c in cc["collector_contract_checks"]]
    assert "collection_plan_record_approved_intent" in names
    assert "nested_collection_plan_ready" in names
    assert "collector_boundary_declares_no_collector" in names


def test_18_critical_failure_blocks():
    rec = _valid_record()
    rec["evidence_collected"] = True  # override one flag
    cc = _build_cc(rec)
    assert cc["decision"] == "blocked"


def test_19_high_failure_blocks():
    rec = _valid_record()
    rec["apply_executor_evidence_collection_plan"]["decision"] = "blocked"
    cc = _build_cc(rec)
    assert cc["decision"] == "blocked"


def test_20_permission_model_all_false():
    rec = _valid_record()
    cc = _build_cc(rec)
    pm = cc["collector_permission_model"]
    assert pm["can_collect_evidence_now"] is False
    assert pm["can_inspect_filesystem_now"] is False
    assert pm["future_permissions_require_separate_authorization"] is True


def test_21_forbidden_actions_present():
    rec = _valid_record()
    cc = _build_cc(rec)
    fa = cc["collector_forbidden_actions"]
    assert "shell" in fa
    assert "subprocess" in fa
    assert "evidence_collection_now" in fa


def test_22_allowed_future_actions_present():
    rec = _valid_record()
    cc = _build_cc(rec)
    af = cc["collector_allowed_future_actions"]
    assert "prepare_evidence_collection_request" in af


def test_23_input_requirements_present():
    rec = _valid_record()
    cc = _build_cc(rec)
    assert len(cc["collector_input_requirements"]) >= 5


def test_24_output_requirements_present():
    rec = _valid_record()
    cc = _build_cc(rec)
    assert len(cc["collector_output_requirements"]) >= 5


def test_25_execution_constraints_contract_only():
    rec = _valid_record()
    cc = _build_cc(rec)
    ec = cc["collector_execution_constraints"]
    assert ec["contract_scope"] == "contract_only_no_collection"
    assert ec["collection_allowed_now"] is False


def test_26_acceptance_criteria_ready():
    rec = _valid_record()
    cc = _build_cc(rec)
    ac = cc["collector_acceptance_criteria"]
    assert len(ac) >= 5
    for c in ac:
        assert c.get("satisfied_now") is False


def test_27_confirmations_ready():
    rec = _valid_record()
    cc = _build_cc(rec)
    confs = cc["required_collector_contract_confirmations"]
    assert len(confs) >= 6
    assert any("does not collect evidence" in c for c in confs)


def test_28_statement_present_ready():
    rec = _valid_record()
    cc = _build_cc(rec)
    assert cc.get("collector_contract_statement") is not None


def test_29_requested_action_copied():
    rec = _valid_record()
    cc = _build_cc(rec)
    assert cc["requested_action"]["tool_id"] == "test.tool"


def test_30_metadata_present():
    rec = _valid_record()
    cc = _build_cc(rec)
    m = cc["metadata"]
    assert m["source"] == "apply_executor_evidence_collector_contract_builder"
    assert m["schema_version"] == "1.0"


def test_31_warnings_present():
    rec = _valid_record()
    cc = _build_cc(rec)
    w = cc["warnings"]
    assert len(w) >= 5
    assert "does not authorize execution" in w[0]


def test_32_link_ids_copied():
    rec = _valid_record()
    cc = _build_cc(rec)
    assert cc["apply_executor_evidence_collection_plan_id"] == "p1"
    assert cc["apply_executor_evidence_contract_id"] == "ec1"
    assert cc["apply_executor_plan_id"] == "ap1"


def test_33_collector_boundary_no_collector():
    rec = _valid_record()
    cc = _build_cc(rec)
    b = cc["collector_boundary"]
    assert b["collector_exists"] is False
    assert b["requires_future_collector_implementation"] is True


def test_34_medium_failure_not_ready():
    # Valid record with only medium failure: empty planned_collection_steps
    rec = _valid_record()
    rec["apply_executor_evidence_collection_plan"]["planned_collection_steps"] = []
    cc = _build_cc(rec)
    assert cc["decision"] == "not_ready"


def test_35_low_failure_not_ready():
    # Valid record with only low failure: non-empty blocking_reasons
    rec = _valid_record()
    rec["apply_executor_evidence_collection_plan"]["blocking_reasons"] = ["low issue"]
    cc = _build_cc(rec)
    assert cc["decision"] == "not_ready"
