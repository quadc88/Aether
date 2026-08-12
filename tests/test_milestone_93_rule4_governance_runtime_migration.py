"""Milestone 93B Rule 4 Governance runtime migration contract tests."""

from __future__ import annotations

import ast
import inspect
import subprocess
from pathlib import Path

import pytest

from aether.core.governance import evaluate_authorization_envelope
from aether.thinking.policy import (
    _evaluate_chat_policy_with_precedence,
    decide_chat_policy,
)


ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "aether/thinking/policy.py"
GOVERNANCE = ROOT / "aether/core/governance.py"
LOOP = ROOT / "aether/core/loop.py"
APPROVAL_REQUEST = ROOT / "aether/action/approval_request.py"
APPROVAL_QUEUE = ROOT / "aether/action/approval_queue.py"
LOOP_TRACE = ROOT / "aether/core/loop_trace.py"
API_SERVER = ROOT / "aether/interface/api_server.py"

TEN_KEYS = [
    "decision_type",
    "confidence",
    "reasons",
    "required_user_confirmation",
    "tool_suggestion_allowed",
    "tool_execution_allowed",
    "blocked_reason",
    "clarification_question",
    "next_step",
    "warnings",
]


def _raw(
    text: str = "ordinary request",
    terms=None,
    risk_level: str = "low",
    tool: dict | None = None,
):
    return _evaluate_chat_policy_with_precedence(
        perception={"normalized_text": text, "risk_terms_detected": terms or []},
        risk={"risk_level": risk_level, "action_type": "general_request"},
        suggested_tool=tool,
    )


def _envelope(
    raw: dict,
    *,
    terms=None,
    risk_level: str = "low",
    requested_action: dict | None = None,
    signal: str = "clear",
):
    return evaluate_authorization_envelope(
        thinking_policy=raw,
        requested_action=requested_action,
        risk_evidence={"risk_level": risk_level, "action_type": "general_request"},
        rule_3_4_precedence=signal,
        **({"rule4_risk_terms_detected": terms} if terms is not None else {}),
    )


def _tree(path: Path) -> ast.Module:
    return ast.parse(path.read_text(encoding="utf-8"))


def _loop_result(monkeypatch, text: str) -> dict:
    import aether.action.tool_planner as tool_planner
    import aether.core.loop as core_loop

    monkeypatch.setattr(
        core_loop,
        "verify_identity_integrity",
        lambda *args, **kwargs: {"status": "verified"},
    )
    monkeypatch.setattr(
        core_loop,
        "record_event",
        lambda *args, **kwargs: {"id": "test-event"},
    )
    monkeypatch.setattr(
        core_loop,
        "time_state",
        lambda: {"timezone": "UTC", "now": "00:00:00", "iso": "2026-01-01T00:00:00+00:00"},
    )
    monkeypatch.setattr(
        tool_planner,
        "infer_candidate_tool",
        lambda *args, **kwargs: {"candidate_tool": {}},
    )
    monkeypatch.setattr(
        "aether.action.approval_queue.create_approval_record",
        lambda *args, **kwargs: {"approval_id": "test-approval"},
    )
    return core_loop.run_core_chat_loop(text=text, session_id="test-session")


def _contains_key(value, key: str) -> bool:
    if isinstance(value, dict):
        return any(k == key or _contains_key(v, key) for k, v in value.items())
    if isinstance(value, (list, tuple)):
        return any(_contains_key(item, key) for item in value)
    return False


def test_single_rule4_evaluator():
    tree = _tree(GOVERNANCE)
    predicates = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "any"
        and "_SECRET_RISK_TERMS" in ast.unparse(node)
    ]
    assert len(predicates) == 1
    assert "rule4_risk_terms_detected" in inspect.signature(
        evaluate_authorization_envelope
    ).parameters


def test_single_operative_term_set():
    gov_assignments = [
        node
        for node in _tree(GOVERNANCE).body
        if isinstance(node, ast.Assign)
        and any(
            isinstance(target, ast.Name) and target.id == "_SECRET_RISK_TERMS"
            for target in node.targets
        )
    ]
    policy_assignments = [
        node
        for node in _tree(POLICY).body
        if isinstance(node, ast.Assign)
        and any(
            isinstance(target, ast.Name) and target.id == "_SECRET_RISK_TERMS"
            for target in node.targets
        )
    ]
    assert len(gov_assignments) == 1
    assert len(policy_assignments) == 0
    assert set(ast.literal_eval(gov_assignments[0].value)) == {
        "password",
        "secret",
        "api key",
        "token",
        "private_key",
        "credential",
        "secret_key",
        "access_key",
    }


def test_thinking_has_no_rule4_predicate():
    tree = _tree(POLICY)
    assert not any(
        isinstance(node, ast.Name) and node.id == "_SECRET_RISK_TERMS"
        for node in ast.walk(tree)
    )
    assert not any(
        isinstance(node, ast.Constant) and node.value == "rule_4"
        for node in ast.walk(tree)
    )
    assert not any(
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "any"
        and "risk_terms" in ast.unparse(node)
        for node in ast.walk(tree)
    )


def test_future_provenance_domain():
    _, empty_signal = _raw(text="")
    raw, secret_signal = _raw(text="hello world", terms=["password"])
    assert empty_signal == "rule_3"
    assert secret_signal == "clear"
    assert raw["decision_type"] == "respond_only"


def test_future_clear_means_rule3_only():
    raw, signal = _raw(text="hello world", terms=["password"])
    assert signal == "clear"
    result = _envelope(raw)
    assert result["decision"] == "deny"
    assert result["policy_snapshot"] == raw


def test_private_sidecar_transport():
    signature = inspect.signature(evaluate_authorization_envelope)
    parameter = signature.parameters["rule4_risk_terms_detected"]
    assert parameter.kind is inspect.Parameter.KEYWORD_ONLY

    loop_tree = _tree(LOOP)
    calls = [
        node
        for node in ast.walk(loop_tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "evaluate_authorization_envelope"
    ]
    assert len(calls) == 1
    sidecar = next(
        keyword
        for keyword in calls[0].keywords
        if keyword.arg == "rule4_risk_terms_detected"
    )
    assert isinstance(sidecar.value, ast.Subscript)
    assert isinstance(sidecar.value.value, ast.Name)
    assert sidecar.value.value.id == "perception"
    assert isinstance(sidecar.value.slice, ast.Constant)
    assert sidecar.value.slice.value == "risk_terms_detected"


def test_rule4_exact_trigger():
    raw = {"decision_type": "respond_only", "tool_execution_allowed": False}
    selected = _envelope(raw, terms=["ordinary", "password"])
    not_selected = _envelope(raw, terms=["ordinary"])
    assert selected["decision"] == "require_approval"
    assert not_selected["decision"] == "deny"


def test_rule4_exact_ten_key_projection():
    raw = {
        "decision_type": "suggest_tool",
        "tool_suggestion_allowed": True,
        "tool_execution_allowed": False,
    }
    snapshot = _envelope(raw, terms=["ordinary", "password"])["policy_snapshot"]
    assert list(snapshot) == TEN_KEYS
    assert snapshot == {
        "decision_type": "require_approval",
        "confidence": "high",
        "reasons": [
            "Text contains sensitive terms: ordinary, password. "
            "User confirmation required before handling."
        ],
        "required_user_confirmation": True,
        "tool_suggestion_allowed": False,
        "tool_execution_allowed": False,
        "blocked_reason": None,
        "clarification_question": None,
        "next_step": "Confirm whether sensitive information should be handled.",
        "warnings": ["Potentially sensitive terms detected: ordinary, password"],
    }


def test_rule3_precedence_protection():
    def forbidden_iteration():
        raise AssertionError("Rule 3 must prevent Rule 4 iteration")
        yield "password"

    raw, signal = _raw(text="", terms=["password"])
    result = evaluate_authorization_envelope(
        raw,
        rule_3_4_precedence=signal,
        rule4_risk_terms_detected=forbidden_iteration(),
        risk_evidence={"risk_level": "high", "action_type": "file_delete"},
        requested_action={"tool_id": "file.delete"},
    )
    assert result["decision"] == "deny"


def test_rule5_precedence_protection():
    raw = {"decision_type": "respond_only", "tool_execution_allowed": False}
    result = _envelope(raw, terms=["ordinary"], risk_level="high")
    assert result["decision"] == "require_approval"
    assert result["policy_snapshot"]["confidence"] == "high"
    assert result["policy_snapshot"]["tool_execution_allowed"] is False


def test_rule6_precedence_protection():
    raw = {"decision_type": "respond_only", "tool_execution_allowed": False}
    result = _envelope(
        raw,
        terms=["ordinary"],
        risk_level="medium",
        requested_action={"tool_id": "file.edit"},
    )
    assert result["decision"] == "require_approval"
    assert result["policy_snapshot"]["confidence"] == "medium"

    rule4_result = _envelope(
        raw,
        terms=["password"],
        risk_level="medium",
        requested_action={"tool_id": "file.edit"},
    )
    assert rule4_result["policy_snapshot"]["confidence"] == "high"


def test_rule7_collision():
    raw, signal = _raw(
        text="list the files in this directory",
        terms=["password"],
        tool={"tool_id": "filesystem"},
    )
    assert raw["decision_type"] == "suggest_tool"
    assert raw["tool_suggestion_allowed"] is True
    assert signal == "clear"
    effective = evaluate_authorization_envelope(
        raw,
        requested_action={"tool_id": "filesystem"},
        rule_3_4_precedence=signal,
        rule4_risk_terms_detected=["password"],
    )
    assert effective["decision"] == "require_approval"
    assert effective["policy_snapshot"]["tool_suggestion_allowed"] is False
    assert effective["policy_snapshot"]["tool_execution_allowed"] is False


def test_contract_b_explicit_none():
    raw = {"decision_type": "respond_only", "tool_execution_allowed": False}
    with pytest.raises(TypeError):
        evaluate_authorization_envelope(
            raw,
            rule_3_4_precedence="clear",
            rule4_risk_terms_detected=None,
        )


def test_contract_b_non_iterable():
    raw = {"decision_type": "respond_only", "tool_execution_allowed": False}
    with pytest.raises(TypeError):
        evaluate_authorization_envelope(
            raw,
            rule_3_4_precedence="clear",
            rule4_risk_terms_detected=123,
        )


def test_contract_b_unhashable_member():
    raw = {"decision_type": "respond_only", "tool_execution_allowed": False}
    with pytest.raises(TypeError):
        evaluate_authorization_envelope(
            raw,
            rule_3_4_precedence="clear",
            rule4_risk_terms_detected=[[]],
        )


def test_missing_sidecar_defaults_to_empty():
    raw = {"decision_type": "respond_only", "tool_execution_allowed": False}
    result = evaluate_authorization_envelope(
        raw,
        rule_3_4_precedence="clear",
    )
    assert result["decision"] == "deny"
    assert result["policy_snapshot"] == raw


def test_direct_thinking_semantic_supersession():
    raw, signal = _raw(text="hello world", terms=["password"])
    wrapped = decide_chat_policy(
        perception={"normalized_text": "hello world", "risk_terms_detected": ["password"]},
        risk={"risk_level": "low", "action_type": "general_request"},
    )
    assert signal == "clear"
    assert raw["decision_type"] == "respond_only"
    assert wrapped == raw
    assert "password" not in " ".join(raw["reasons"] + raw["warnings"])


def test_effective_chat_compatibility(monkeypatch):
    result = _loop_result(monkeypatch, "Please reset my password now")
    assert result["thinking_policy"]["decision_type"] == "require_approval"
    assert result["policy_gate"]["decision"] == "require_approval"
    assert result["approval_required"] is True
    assert result["tool_execution_allowed"] is False
    assert result["policy_gate"]["policy_snapshot"]["warnings"] == [
        "Potentially sensitive terms detected: password"
    ]


def test_t3_raw_and_effective_attribution(monkeypatch):
    result = _loop_result(monkeypatch, "Please reset my password now")
    stages = {stage["name"]: stage for stage in result["loop_trace"]["stages"]}
    assert stages["thinking_policy"]["summary"] == "Decision: respond_only"
    assert stages["policy_gate"]["summary"] == "Decision: require_approval"
    assert result["thinking_policy"] == result["policy_gate"]["policy_snapshot"]


def test_no_api_or_public_sidecar_expansion(monkeypatch):
    result = _loop_result(monkeypatch, "Please reset my password now")
    assert not _contains_key(result, "rule4_risk_terms_detected")
    assert "rule4_risk_terms_detected" not in API_SERVER.read_text(encoding="utf-8")
    assert "rule4_risk_terms_detected" not in (ROOT / "aether/interface/api_models.py").read_text(encoding="utf-8")


def test_no_persistence_expansion(monkeypatch):
    result = _loop_result(monkeypatch, "Please reset my password now")
    assert not _contains_key(result.get("approval_request"), "rule4_risk_terms_detected")
    assert not _contains_key(result.get("approval_record"), "rule4_risk_terms_detected")
    assert "rule4_risk_terms_detected" not in APPROVAL_REQUEST.read_text(encoding="utf-8")
    assert "rule4_risk_terms_detected" not in APPROVAL_QUEUE.read_text(encoding="utf-8")
    assert "rule4_risk_terms_detected" not in LOOP_TRACE.read_text(encoding="utf-8")


def test_no_duplicate_rule4_predicate():
    def _rule4_predicates(path: Path):
        return [
            node
            for node in ast.walk(_tree(path))
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "any"
            and "_SECRET_RISK_TERMS" in ast.unparse(node)
        ]

    assert len(_rule4_predicates(GOVERNANCE)) == 1
    assert len(_rule4_predicates(POLICY)) == 0
    assert len(_rule4_predicates(LOOP)) == 0


def test_no_duplicate_rule4_formatter():
    tree = _tree(GOVERNANCE)
    definitions = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef)
        and node.name == "_format_rule_4_compatibility_policy"
    ]
    calls = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "_format_rule_4_compatibility_policy"
    ]
    assert len(definitions) == 1
    assert len(calls) == 1
    assert "_format_rule_4_compatibility_policy" not in POLICY.read_text(encoding="utf-8")


def test_exact_production_path_lock():
    result = subprocess.run(
        ["git", "diff", "--name-only", "--", "aether/"],
        check=True,
        capture_output=True,
        text=True,
        cwd=ROOT,
    )
    assert set(result.stdout.splitlines()) <= {
        "aether/thinking/policy.py",
        "aether/core/governance.py",
        "aether/core/loop.py",
        "aether/action/approval_decision_gate.py",
        "aether/action/approval_queue.py",
        "aether/action/restricted_file_reader.py",
        "aether/action/tool_planner.py",
        "aether/core/config.py",
        "aether/interface/api_models.py",
        "aether/interface/routers/file_routes.py",
    }


def test_governance_generator_match_first_native_sequential_consumption():
    raw = {"decision_type": "respond_only", "tool_execution_allowed": False}
    terms = iter(["password", "other"])
    snapshot = _envelope(raw, terms=terms)["policy_snapshot"]
    assert snapshot["reasons"] == [
        "Text contains sensitive terms: other. User confirmation required before handling."
    ]
    assert snapshot["warnings"] == ["Potentially sensitive terms detected: "]
    assert next(terms, None) is None


def test_governance_generator_match_later_exhaustion():
    raw = {"decision_type": "respond_only", "tool_execution_allowed": False}
    terms = iter(["other", "password"])
    snapshot = _envelope(raw, terms=terms)["policy_snapshot"]
    assert snapshot["reasons"] == [
        "Text contains sensitive terms: . User confirmation required before handling."
    ]
    assert snapshot["warnings"] == ["Potentially sensitive terms detected: "]
    assert next(terms, None) is None
