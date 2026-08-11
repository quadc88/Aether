"""Milestone 92C Rule 6 Governance runtime migration contract tests."""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from aether.core.governance import evaluate_authorization_envelope
from aether.thinking.policy import _evaluate_chat_policy_with_precedence


ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "aether/thinking/policy.py"
GOVERNANCE = ROOT / "aether/core/governance.py"
LOOP = ROOT / "aether/core/loop.py"
RECORD = ROOT / "docs/architecture/MILESTONE_92C_RULE6_GOVERNANCE_RUNTIME_MIGRATION.md"

EXPECTED_BUILD_PATHS = {
    "aether/thinking/policy.py",
    "aether/core/governance.py",
    "docs/architecture/MILESTONE_92C_RULE6_GOVERNANCE_RUNTIME_MIGRATION.md",
    "tests/test_milestone_92c_rule6_governance_runtime_migration.py",
    "tests/test_thinking_policy.py",
    "tests/test_milestone_88_cognitive_signal_arbitration_boundary.py",
    "tests/test_milestone_89_identity_hard_constraint_migration_boundary.py",
    "tests/test_milestone_91b_rule5_governance_migration_boundary.py",
    "tests/test_milestone_92_rule6_governance_migration_boundary.py",
    "PROGRESS.md",
    "tests/test_progress_ledger_canonical_header.py",
}


def _perception(text="ordinary request", terms=None):
    return {"normalized_text": text, "risk_terms_detected": terms or []}


def _risk(level="medium"):
    return {"risk_level": level, "action_type": "file_edit"}


def _raw(tool, risk="medium", text="edit the README", terms=None):
    return _evaluate_chat_policy_with_precedence(
        _perception(text, terms), _risk(risk), tool
    )


def _envelope(raw, tool, risk="medium", signal="clear"):
    return evaluate_authorization_envelope(
        thinking_policy=raw,
        requested_action=tool,
        risk_evidence=_risk(risk),
        rule_3_4_precedence=signal,
    )


def _rule6_projection(tool):
    return _envelope(
        {"decision_type": "respond_only", "tool_execution_allowed": False},
        tool,
    )["policy_snapshot"]


def test_current_rule6_trigger_exact():
    source = POLICY.read_text()
    assert 'risk_level == "medium"' not in source
    gov = GOVERNANCE.read_text()
    assert 'risk_level == "medium" and requested_action is not None' in gov
    assert 'rule_3_4_precedence in {"rule_3", "clear"}' in gov
    assert "rule4_risk_terms_detected" in gov
    assert "isinstance(risk_evidence, dict)" in gov


def test_current_rule6_projection_fields_exact():
    projection = _rule6_projection({"tool_id": "file.edit"})
    assert projection == {
        "decision_type": "require_approval",
        "confidence": "medium",
        "reasons": [
            "Medium-risk request with suggested tool 'file.edit'. "
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


def test_current_rule6_empty_and_missing_tool_id_inputs():
    for tool in ({}, {"foo": "bar"}, {"tool_id": ""}):
        assert _rule6_projection(tool)["decision_type"] == "require_approval"
        assert _envelope({"decision_type": "respond_only", "tool_execution_allowed": False}, tool)["decision"] == "require_approval"


def test_current_rule6_malformed_tool_behavior():
    for tool in ("", "tool", [], 123, object()):
        with pytest.raises(AttributeError):
            _rule6_projection(tool)


def test_governance_rule6_single_authority():
    assert 'risk_level == "medium"' not in POLICY.read_text()
    assert "_format_rule_6_compatibility_policy" in GOVERNANCE.read_text()
    assert GOVERNANCE.read_text().count("_format_rule_6_compatibility_policy") == 2


def test_governance_rule6_exact_trigger_gate():
    raw = {"decision_type": "respond_only", "tool_execution_allowed": False}
    assert _envelope(raw, {"tool_id": "x"})["decision"] == "require_approval"
    assert evaluate_authorization_envelope(raw, requested_action={"tool_id": "x"}, risk_evidence={"risk_level": "HIGH"}, rule_3_4_precedence="clear")["decision"] == "deny"
    assert evaluate_authorization_envelope(raw, requested_action={"tool_id": "x"}, risk_evidence={"risk_level": "medium"}, rule_3_4_precedence="rule_4")["decision"] == "deny"
    assert evaluate_authorization_envelope(raw, requested_action=None, risk_evidence={"risk_level": "medium"}, rule_3_4_precedence="clear")["decision"] == "deny"


def test_governance_rule6_projection_matches_legacy():
    result = _envelope({"decision_type": "respond_only", "tool_execution_allowed": False}, {"tool_id": "x"})
    assert result["allowed"] is False
    assert result["decision"] == "require_approval"
    assert result["reason"] == "Human approval is required before execution."
    assert result["requested_action"] == {"tool_id": "x"}
    assert result["policy_snapshot"]["decision_type"] == "require_approval"


def test_governance_rule6_malformed_action_raises_exactly():
    raw = {"decision_type": "respond_only", "tool_execution_allowed": False}
    for tool in ("", "tool", [], 123, object()):
        with pytest.raises(AttributeError):
            evaluate_authorization_envelope(raw, requested_action=tool, risk_evidence=_risk(), rule_3_4_precedence="clear")


def test_governance_rule5_precedes_rule6():
    raw = {"decision_type": "respond_only", "tool_execution_allowed": False}
    result = evaluate_authorization_envelope(raw, requested_action={"tool_id": "x"}, risk_evidence=_risk("high"), rule_3_4_precedence="clear")
    assert result["decision"] == "require_approval"
    assert result["policy_snapshot"]["confidence"] == "high"


def test_thinking_no_operative_rule6_branch():
    tree = ast.parse(POLICY.read_text())
    fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "_evaluate_chat_policy_with_precedence")
    assert not any(isinstance(n, ast.Compare) and "medium" in ast.unparse(n) for n in ast.walk(fn))


def test_thinking_medium_tool_returns_neutral_proposal():
    raw, signal = _raw({"tool_id": "file.edit"})
    assert raw["decision_type"] == "respond_only"
    assert signal == "clear"
    assert _envelope(raw, {"tool_id": "file.edit"})["decision"] == "require_approval"


def test_thinking_rule3_rule4_provenance_retained():
    assert _raw(None, text="")[1] == "rule_3"
    raw, signal = _raw({"tool_id": "x"}, text="secret", terms=["secret"])
    assert signal == "clear"
    effective = evaluate_authorization_envelope(
        raw,
        requested_action={"tool_id": "x"},
        risk_evidence=_risk(),
        rule_3_4_precedence=signal,
        rule4_risk_terms_detected=["secret"],
    )
    assert effective["decision"] == "require_approval"


def test_thinking_rules7_8_9_unchanged():
    assert _raw({"tool_id": "x"}, risk="low", text="list files")[0]["decision_type"] == "suggest_tool"
    assert _raw(None, risk="low", text="hi")[0]["decision_type"] == "ask_clarification"
    assert _raw(None, risk="low", text="write a story")[0]["decision_type"] == "respond_only"


def test_identity_rules_precede_rule6():
    raw, signal = _raw({"tool_id": "x"})
    result = evaluate_authorization_envelope(raw, requested_action={"tool_id": "x"}, risk_evidence=_risk(), rule_3_4_precedence=signal, identity_integrity_evidence={"status": "changed"})
    assert result["decision"] == "block"


def test_rule3_provenance_blocks_rule6():
    raw, signal = _raw({"tool_id": "x"}, text="")
    assert signal == "rule_3"
    assert _envelope(raw, {"tool_id": "x"}, signal=signal)["decision"] == "deny"


def test_rule4_provenance_blocks_rule6():
    raw, signal = _raw({"tool_id": "x"}, text="secret", terms=["secret"])
    assert signal == "clear"
    result = evaluate_authorization_envelope(
        raw,
        requested_action={"tool_id": "x"},
        risk_evidence=_risk(),
        rule_3_4_precedence=signal,
        rule4_risk_terms_detected=["secret"],
    )
    assert result["decision"] == "require_approval"
    assert result["policy_snapshot"]["confidence"] == "high"


def test_rule6_precedes_rule7():
    raw, signal = _raw({"tool_id": "x"}, risk="medium")
    assert signal == "clear"
    assert _envelope(raw, {"tool_id": "x"})["policy_snapshot"]["decision_type"] == "require_approval"


def test_rule6_unknown_and_missing_risk_do_not_trigger():
    raw = {"decision_type": "respond_only", "tool_execution_allowed": False}
    for evidence in ({}, {"action_type": "file_edit"}, {"risk_level": "HIGH"}, "bad", None):
        result = evaluate_authorization_envelope(raw, requested_action={"tool_id": "x"}, risk_evidence=evidence, rule_3_4_precedence="clear")
        assert result["decision"] == "deny"


def test_rule6_envelope_flags_are_non_executing():
    result = _envelope({"decision_type": "respond_only", "tool_execution_allowed": False}, {"tool_id": "x"})
    assert result["allowed"] is False
    assert result["tool_execution_allowed"] is False
    assert result["action_execution_allowed"] is False


def test_rule6_approval_request_consumes_projection():
    result = _envelope({"decision_type": "respond_only", "tool_execution_allowed": False}, {"tool_id": "x"})
    assert result["policy_snapshot"]["required_user_confirmation"] is True
    assert result["policy_snapshot"]["tool_suggestion_allowed"] is True


def test_rule6_trace_separates_raw_and_authoritative_policy():
    raw, signal = _raw({"tool_id": "x"})
    effective = _envelope(raw, {"tool_id": "x"}, signal=signal)["policy_snapshot"]
    assert raw["decision_type"] == "respond_only"
    assert effective["decision_type"] == "require_approval"
    assert "rule_3_4_precedence" not in effective


def test_rule6_response_shape_and_openapi_unchanged():
    from aether.interface.api_server import app

    assert (len(app.openapi()["paths"]), len(app.openapi()["components"]["schemas"])) == (304, 108)
    result = _envelope({"decision_type": "respond_only", "tool_execution_allowed": False}, {"tool_id": "x"})
    assert set(result) == {"allowed", "decision", "reason", "warnings", "required_user_confirmation", "tool_execution_allowed", "action_execution_allowed", "requested_action", "policy_snapshot"}


def test_no_rule4_migration_or_duplicate_evaluator():
    assert "secret_found = any" not in POLICY.read_text()
    assert "_SECRET_RISK_TERMS" not in POLICY.read_text()
    assert 'risk_level == "medium"' not in POLICY.read_text()
    assert GOVERNANCE.read_text().count('if risk_level == "medium" and requested_action is not None') == 1
    assert "_format_rule_6_compatibility_policy" in GOVERNANCE.read_text()
    assert "rule4_risk_terms_detected" in GOVERNANCE.read_text()


def test_no_capability_expansion_or_loop_mutation():
    loop_source = LOOP.read_text()
    loop_tree = ast.parse(loop_source)
    governance_calls = [
        node
        for node in ast.walk(loop_tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "evaluate_authorization_envelope"
    ]
    assert len(governance_calls) == 1
    governance_call = governance_calls[0]
    assert [keyword.arg for keyword in governance_call.keywords] == [
        "thinking_policy",
        "requested_action",
        "context",
        "risk_evidence",
        "identity_integrity_evidence",
        "rule_3_4_precedence",
        "rule4_risk_terms_detected",
    ]
    sidecar_keyword = governance_call.keywords[-1]
    assert isinstance(sidecar_keyword.value, ast.Subscript)
    assert isinstance(sidecar_keyword.value.value, ast.Name)
    assert sidecar_keyword.value.value.id == "perception"
    assert isinstance(sidecar_keyword.value.slice, ast.Constant)
    assert sidecar_keyword.value.slice.value == "risk_terms_detected"

    # The loop transports the factual iterable and leaves Rule 4 semantics to
    # Governance. Existing public perception projection is unrelated to the
    # private sidecar name and remains part of the historical response shape.
    assert "_SECRET_RISK_TERMS" not in loop_source
    assert "secret_found" not in loop_source
    assert loop_source.count("rule4_risk_terms_detected") == 1
    assert not any(
        isinstance(node, ast.Constant)
        and node.value == "rule4_risk_terms_detected"
        for node in ast.walk(loop_tree)
    )
    term_calls = [
        node
        for node in ast.walk(loop_tree)
        if isinstance(node, ast.Call)
        and "risk_terms_detected" in ast.unparse(node)
    ]
    assert term_calls == [governance_call]
    assert not any(
        isinstance(node, (ast.For, ast.AsyncFor, ast.comprehension))
        and "risk_terms_detected" in ast.unparse(node)
        for node in ast.walk(loop_tree)
    )
    assert not any(
        isinstance(node, ast.Compare)
        and "risk_terms_detected" in ast.unparse(node)
        and any(isinstance(op, ast.In) for op in node.ops)
        for node in ast.walk(loop_tree)
    )

    record = RECORD.read_text()
    scope = record.split("## 19. Exact Eleven-Path Build Scope\n", 1)[1].split(
        "\n## 20. Build Completion Gates", 1
    )[0]
    assert {
        line.split("`", 2)[1]
        for line in scope.splitlines()
        if line.lstrip().startswith(tuple(f"{n}." for n in range(1, 12)))
        and "`" in line
    } == EXPECTED_BUILD_PATHS
    assert "Total unique Build paths: 11." in scope
    assert "tests/test_milestone_92_rule6_governance_migration_boundary.py" in scope
    assert "Exact Ten-Path Build Scope" not in record
    assert "Total unique Build paths: 10" not in record
    assert "No eleventh path" not in record
    assert "The 92B decision record is frozen and remains byte-identical." in record
    assert "one-time historical harness correction" in record
    assert "frozen after the 92C implementation tag" in record
    assert "Stage 2 closure remains limited to `PROGRESS.md` and" in record
    assert "tests/test_progress_ledger_canonical_header.py` only" in record
    for phrase in ("real execution/apply", "rollback", "evidence collection"):
        assert phrase in record
