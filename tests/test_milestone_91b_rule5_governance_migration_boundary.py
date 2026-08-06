"""Milestone 91B Rule 5 ownership and compatibility boundary."""

import ast
import copy
import hashlib
from pathlib import Path

import pytest

from aether.core.governance import (
    _format_rule_5_compatibility_policy,
    evaluate_authorization_envelope,
)
from aether.thinking.policy import (
    _evaluate_chat_policy_with_precedence,
    decide_chat_policy,
)


POLICY = Path("aether/thinking/policy.py")
LOOP = Path("aether/core/loop.py")
GOVERNANCE = Path("aether/core/governance.py")


def _perception(text="ordinary request", terms=None):
    return {"text": text, "normalized_text": text, "risk_terms_detected": terms or []}


def _risk(level="high", action="file_delete", **extra):
    value = {"risk_level": level, "action_type": action}
    value.update(extra)
    return value


def _expected_projection(action="file_delete"):
    return {
        "decision_type": "require_approval", "confidence": "high",
        "reasons": [f"High-risk request ({action}). Human approval required before any action."],
        "required_user_confirmation": True, "tool_suggestion_allowed": False,
        "tool_execution_allowed": False, "blocked_reason": None,
        "clarification_question": None, "next_step": "Human approval is required before any action.",
        "warnings": [f"High-risk classification: {action}."],
    }


SCENARIOS = [
    pytest.param({"perception": _perception(""), "risk": _risk(), "tool": None, "identity": None, "signal": "rule_3", "raw": "ask_clarification", "effective": "ask_clarification", "envelope": "deny"}, id="s01_empty_high"),
    pytest.param({"perception": _perception("   "), "risk": _risk(), "tool": None, "identity": None, "signal": "rule_3", "raw": "ask_clarification", "effective": "ask_clarification", "envelope": "deny"}, id="s02_whitespace_high"),
    pytest.param({"perception": _perception("send secret", ["secret"]), "risk": _risk(), "tool": None, "identity": None, "signal": "rule_4", "raw": "require_approval", "effective": "require_approval", "envelope": "require_approval"}, id="s03_secret_high"),
    pytest.param({"perception": _perception("send secret", ["secret"]), "risk": _risk(), "tool": {"tool_id": "mailer"}, "identity": None, "signal": "rule_4", "raw": "require_approval", "effective": "require_approval", "envelope": "require_approval"}, id="s04_secret_high_tool"),
    pytest.param({"perception": _perception("delete the archive"), "risk": _risk(), "tool": None, "identity": None, "signal": "clear", "raw": "respond_only", "effective": "require_approval", "envelope": "require_approval"}, id="s05_ordinary_high"),
    pytest.param({"perception": _perception("delete the archive"), "risk": _risk(), "tool": {"tool_id": "filesystem"}, "identity": None, "signal": "clear", "raw": "respond_only", "effective": "require_approval", "envelope": "require_approval"}, id="s06_ordinary_high_tool"),
    pytest.param({"perception": _perception("delete"), "risk": _risk(), "tool": None, "identity": None, "signal": "clear", "raw": "ask_clarification", "effective": "require_approval", "envelope": "require_approval"}, id="s07_short_high"),
    pytest.param({"perception": _perception("review this document"), "risk": _risk("medium"), "tool": {"tool_id": "reviewer"}, "identity": None, "signal": "clear", "raw": "require_approval", "effective": "require_approval", "envelope": "require_approval"}, id="s08_medium_tool"),
    pytest.param({"perception": _perception("list files"), "risk": _risk("low"), "tool": {"tool_id": "filesystem"}, "identity": None, "signal": "clear", "raw": "suggest_tool", "effective": "suggest_tool", "envelope": "deny"}, id="s09_low_tool"),
    pytest.param({"perception": _perception("help me"), "risk": _risk("low"), "tool": None, "identity": None, "signal": "clear", "raw": "ask_clarification", "effective": "ask_clarification", "envelope": "deny"}, id="s10_short_low"),
    pytest.param({"perception": _perception("provide a general explanation"), "risk": _risk("low"), "tool": None, "identity": None, "signal": "clear", "raw": "respond_only", "effective": "respond_only", "envelope": "deny"}, id="s11_default_low"),
    pytest.param({"perception": _perception("delete archive"), "risk": _risk(), "tool": None, "identity": {"status": "changed"}, "signal": "clear", "raw": "respond_only", "effective": "block", "envelope": "block"}, id="s12_identity_changed"),
    pytest.param({"perception": _perception("delete archive"), "risk": _risk(), "tool": None, "identity": {"status": "missing"}, "signal": "clear", "raw": "respond_only", "effective": "require_approval", "envelope": "require_approval"}, id="s13_identity_missing"),
    pytest.param({"perception": _perception("send secret", ["secret"]), "risk": _risk(), "tool": None, "identity": {"status": "failed"}, "signal": "rule_4", "raw": "require_approval", "effective": "require_approval", "envelope": "require_approval"}, id="s14_identity_failed_secret"),
    pytest.param({"perception": _perception("delete archive"), "risk": _risk("low"), "evidence": None, "tool": None, "identity": None, "signal": "clear", "raw": "respond_only", "effective": "respond_only", "envelope": "deny"}, id="s15_risk_none"),
    pytest.param({"perception": _perception("delete archive"), "risk": _risk("low"), "evidence": "high", "tool": None, "identity": None, "signal": "clear", "raw": "respond_only", "effective": "respond_only", "envelope": "deny"}, id="s16_risk_non_dict"),
    pytest.param({"perception": _perception("delete archive"), "risk": {}, "tool": None, "identity": None, "signal": "clear", "raw": "respond_only", "effective": "respond_only", "envelope": "deny"}, id="s17_empty_risk"),
    pytest.param({"perception": _perception("delete archive"), "risk": {"action_type": "file_delete"}, "tool": None, "identity": None, "signal": "clear", "raw": "respond_only", "effective": "respond_only", "envelope": "deny"}, id="s18_missing_level"),
    pytest.param({"perception": _perception("delete archive"), "risk": {"risk_level": "HIGH", "action_type": "file_delete"}, "tool": None, "identity": None, "signal": "clear", "raw": "respond_only", "effective": "respond_only", "envelope": "deny"}, id="s19_unknown_level"),
    pytest.param({"perception": _perception("delete archive"), "risk": {"risk_level": "high"}, "tool": None, "identity": None, "signal": "clear", "raw": "respond_only", "effective": "require_approval", "envelope": "require_approval"}, id="s20_missing_action"),
    pytest.param({"perception": _perception("delete archive"), "risk": {"risk_level": "high", "action_type": 3}, "tool": None, "identity": None, "signal": "clear", "raw": "respond_only", "effective": "require_approval", "envelope": "require_approval"}, id="s21_non_string_action"),
    pytest.param({"perception": _perception("delete archive"), "risk": {"risk_level": "high", "action_type": "file_delete"}, "tool": None, "identity": None, "signal": "clear", "raw": "respond_only", "effective": "require_approval", "envelope": "require_approval"}, id="s22_missing_confidence"),
    pytest.param({"perception": _perception("delete archive"), "risk": {"risk_level": "high", "action_type": "file_delete", "confidence": "high", "reasons": "bad"}, "tool": None, "identity": None, "signal": "clear", "raw": "respond_only", "effective": "require_approval", "envelope": "require_approval"}, id="s23_non_list_reasons"),
    pytest.param({"perception": _perception("delete archive"), "risk": _risk(), "tool": None, "identity": None, "signal": "clear", "raw": "respond_only", "effective": "block", "envelope": "block", "synthetic": {"decision_type": "block", "blocked_reason": "pre-existing block", "tool_execution_allowed": False}}, id="s24_synthetic_block"),
    pytest.param({"perception": _perception("delete archive"), "risk": _risk(), "tool": None, "identity": None, "signal": "clear", "raw": "respond_only", "effective": "require_approval", "envelope": "require_approval", "synthetic": {"decision_type": "respond_only", "tool_execution_allowed": False}}, id="s25_synthetic_allow"),
]


@pytest.mark.parametrize("case", SCENARIOS)
def test_25_scenario_field_exact_matrix(case):
    raw, signal = _evaluate_chat_policy_with_precedence(case["perception"], case["risk"], case["tool"], case["identity"])
    assert signal == case["signal"]
    assert raw["decision_type"] == case["raw"]
    policy = case.get("synthetic", raw)
    envelope = evaluate_authorization_envelope(policy, requested_action=None, risk_evidence=case.get("evidence", case["risk"]), rule_3_4_precedence=signal, identity_integrity_evidence=case["identity"])
    assert envelope["decision"] == case["envelope"]
    if envelope["policy_snapshot"]:
        assert envelope["policy_snapshot"]["decision_type"] == case["effective"]
    assert envelope["tool_execution_allowed"] is False
    assert envelope["action_execution_allowed"] is False


def test_sidecar_shape_and_wrapper_compatibility():
    p = _perception("ordinary request"); r = _risk("low")
    sidecar = _evaluate_chat_policy_with_precedence(p, r)
    assert isinstance(sidecar, tuple) and len(sidecar) == 2 and isinstance(sidecar[0], dict)
    assert decide_chat_policy(p, r) == sidecar[0]


def test_rule3_signal_from_single_ordered_evaluation():
    assert _evaluate_chat_policy_with_precedence(_perception(""), _risk("high"))[1] == "rule_3"


def test_rule4_signal_from_single_ordered_evaluation():
    assert _evaluate_chat_policy_with_precedence(_perception("secret", ["secret"]), _risk("high"))[1] == "rule_4"


def test_clear_signal_for_rules6_to9():
    assert _evaluate_chat_policy_with_precedence(_perception("ordinary request"), _risk("high"))[1] == "clear"


def test_one_evaluation_no_duplicate_predicates():
    tree = ast.parse(POLICY.read_text())
    fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "_evaluate_chat_policy_with_precedence")
    assert sum(isinstance(n, ast.Call) and getattr(n.func, "id", "") == "any" for n in ast.walk(fn)) == 1
    assert POLICY.read_text().count("_SECRET_RISK_TERMS") == 2


def test_loop_transports_sidecar_unchanged():
    src = LOOP.read_text()
    assert "raw_thinking_policy, rule_3_4_precedence = _evaluate_chat_policy_with_precedence" in src
    assert "rule_3_4_precedence=rule_3_4_precedence" in src


def test_governance_signal_validation():
    policy = {"decision_type": "respond_only", "tool_execution_allowed": False}
    for value in (None, "RULE_3", "unknown", True, 1, [], {}, set()):
        assert evaluate_authorization_envelope(policy, risk_evidence=_risk(), rule_3_4_precedence=value)["decision"] == "deny"


def test_direct_call_fallback_without_signal():
    result = evaluate_authorization_envelope({"decision_type": "respond_only", "tool_execution_allowed": False}, risk_evidence=_risk())
    assert result["decision"] == "deny"


def test_risk_variants_and_unknown_action_fallback():
    result = evaluate_authorization_envelope({"decision_type": "respond_only", "tool_execution_allowed": False}, risk_evidence={"risk_level": "high", "action_type": 7}, rule_3_4_precedence="clear")
    assert result["policy_snapshot"] == _expected_projection("unknown")


def test_rule5_exact_trigger_and_precedence():
    p = {"decision_type": "respond_only", "tool_execution_allowed": False}
    assert evaluate_authorization_envelope(p, risk_evidence=_risk(), rule_3_4_precedence="rule_3")["decision"] == "deny"
    assert evaluate_authorization_envelope(p, risk_evidence=_risk(), rule_3_4_precedence="clear")["decision"] == "require_approval"


def test_projection_fresh_dict_and_exact_literals():
    a = _format_rule_5_compatibility_policy("file_delete"); b = _format_rule_5_compatibility_policy("file_delete")
    assert a == _expected_projection("file_delete") and a is not b and a["reasons"] is not b["reasons"]


def test_single_authoritative_rule5_static():
    assert GOVERNANCE.read_text().count('if risk_level == "high"') == 1
    assert 'if risk_level == "high"' not in POLICY.read_text()


def test_policy_snapshot_has_no_sidecar_or_evidence():
    result = evaluate_authorization_envelope({"decision_type": "respond_only", "tool_execution_allowed": False}, risk_evidence=_risk(), rule_3_4_precedence="clear")
    assert "rule_3_4_precedence" not in result and "risk_evidence" not in result["policy_snapshot"]


def test_input_dictionaries_remain_unmodified():
    p = _perception("delete archive"); r = _risk(); before = (copy.deepcopy(p), copy.deepcopy(r))
    _evaluate_chat_policy_with_precedence(p, r)
    evaluate_authorization_envelope({"decision_type": "respond_only", "tool_execution_allowed": False}, risk_evidence=r, rule_3_4_precedence="clear")
    assert (p, r) == before


def test_sidecar_never_reaches_api_approval_or_trace():
    assert "rule_3_4_precedence" not in LOOP.read_text().split('return {', 1)[-1]


def test_api_field_equivalence():
    result = evaluate_authorization_envelope({"decision_type": "respond_only", "tool_execution_allowed": False}, risk_evidence=_risk(), rule_3_4_precedence="clear")
    assert set(result) == {"allowed", "decision", "reason", "warnings", "required_user_confirmation", "tool_execution_allowed", "action_execution_allowed", "requested_action", "policy_snapshot"}


def test_approval_field_equivalence():
    result = evaluate_authorization_envelope({"decision_type": "respond_only", "tool_execution_allowed": False}, risk_evidence=_risk(), rule_3_4_precedence="clear")
    assert result["decision"] == "require_approval" and result["required_user_confirmation"] is True


def test_t3_raw_and_effective_trace_truth():
    raw, signal = _evaluate_chat_policy_with_precedence(_perception("delete archive"), _risk())
    effective = evaluate_authorization_envelope(raw, risk_evidence=_risk(), rule_3_4_precedence=signal)["policy_snapshot"]
    assert raw["decision_type"] == "respond_only" and effective["decision_type"] == "require_approval"


def test_platform_shape_and_no_persistence():
    assert Path("aether/core/loop_trace.py").exists()
    assert "rule_3_4_precedence" not in LOOP.read_text().split("return {", 1)[-1]


def test_all_execution_flags_false():
    result = evaluate_authorization_envelope({"decision_type": "respond_only", "tool_execution_allowed": False}, risk_evidence=_risk(), rule_3_4_precedence="clear")
    assert result["tool_execution_allowed"] is False and result["action_execution_allowed"] is False
