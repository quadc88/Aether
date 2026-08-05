"""Milestone 91A risk-evidence boundary tests.

These tests use current pure functions and stable static inspection only.
They do not invoke an interface, queue, persistence path, network, or tool.
"""

from __future__ import annotations

import ast
import importlib
import inspect
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / "docs/architecture/MILESTONE_91_RISK_EVIDENCE_CONTRACT_BOUNDARY.md"
PROGRESS = ROOT / "PROGRESS.md"
GOVERNANCE = ROOT / "aether/core/governance.py"
LOOP = ROOT / "aether/core/loop.py"
POLICY = ROOT / "aether/thinking/policy.py"
RISK = ROOT / "aether/verification/risk.py"


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _normalized_record() -> str:
    return " ".join(_text(RECORD).split())


def _tree(path: Path) -> ast.Module:
    return ast.parse(_text(path))


def _governance():
    return importlib.import_module("aether.core.governance").evaluate_authorization_envelope


def _policy() -> dict:
    return {
        "decision_type": "require_approval",
        "required_user_confirmation": True,
        "tool_execution_allowed": False,
        "blocked_reason": None,
    }


def _test_functions() -> list[ast.FunctionDef]:
    return [node for node in _tree(Path(__file__)).body
            if isinstance(node, ast.FunctionDef) and node.name.startswith("test_")]


def _has_executable_high_risk_branch(path: Path) -> bool:
    for node in ast.walk(_tree(path)):
        if not isinstance(node, ast.If):
            continue
        if not isinstance(node.test, ast.Compare) or len(node.test.ops) != 1:
            continue
        left = node.test.left
        right = node.test.comparators[0]
        if (isinstance(left, ast.Name) and left.id == "risk_level"
                and isinstance(right, ast.Constant) and right.value == "high"):
            return True
    return False


def _has_governance_risk_branch() -> bool:
    return _has_executable_high_risk_branch(GOVERNANCE)


def test_current_risk_evidence_shape():
    from aether.verification.risk import classify_risk

    result = classify_risk("delete private memory")
    assert set(result) == {"risk_level", "action_type", "confidence", "reasons"}
    assert isinstance(result["risk_level"], str)
    assert isinstance(result["action_type"], str)
    assert isinstance(result["confidence"], str)
    assert isinstance(result["reasons"], list)


def test_risk_evidence_input_boundary():
    signature = inspect.signature(_governance())
    parameter = signature.parameters["risk_evidence"]
    assert parameter.kind is inspect.Parameter.KEYWORD_ONLY


def test_loop_risk_transport():
    tree = _tree(LOOP)
    calls = [node for node in ast.walk(tree) if isinstance(node, ast.Call)]
    classifications = [node for node in calls
                       if isinstance(node.func, ast.Name) and node.func.id == "classify_risk"]
    governance_calls = [node for node in calls
                        if isinstance(node.func, ast.Name)
                        and node.func.id == "evaluate_authorization_envelope"]
    assert len(classifications) == 1
    assert len(governance_calls) == 1
    keyword = next((arg for arg in governance_calls[0].keywords
                    if arg.arg == "risk_evidence"), None)
    assert keyword is not None
    assert isinstance(keyword.value, ast.Name) and keyword.value.id == "risk"


def test_current_risk_non_operativity():
    policy = _policy()
    base = _governance()(thinking_policy=policy)
    with_risk = _governance()(
        thinking_policy=policy,
        risk_evidence={
            "risk_level": "high",
            "action_type": "destructive_memory_action",
            "confidence": "probable",
            "reasons": ["high risk"],
        },
    )
    assert with_risk == base


def test_safe_risk_evidence_variants():
    baseline = _governance()(thinking_policy=_policy())
    variants = (None, "not-a-dict", {}, {"risk_level": "unknown"})
    for evidence in variants:
        assert _governance()(thinking_policy=_policy(), risk_evidence=evidence) == baseline


def test_rule_5_remains_thinking_owned():
    assert _has_executable_high_risk_branch(POLICY)
    assert "Rule 5: High risk -> require_approval" in _text(POLICY)


def test_no_current_duplicate_rule_5_evaluator():
    assert not _has_governance_risk_branch()
    assert "risk_evidence" in _text(GOVERNANCE)


def test_current_identity_precedence_and_disabled_execution():
    changed = _governance()(
        thinking_policy=_policy(),
        identity_integrity_evidence={"status": "changed"},
    )
    missing = _governance()(
        thinking_policy=_policy(),
        identity_integrity_evidence={"status": "missing"},
    )
    assert changed["decision"] == "block"
    assert missing["decision"] == "require_approval"
    for result in (changed, missing):
        assert result["tool_execution_allowed"] is False
        assert result["action_execution_allowed"] is False


def test_boundary_declares_future_rule_5_governance_owner():
    text = _normalized_record()
    assert "Governance is the required future authoritative owner" in text
    assert "A future, separately authorized Milestone 91B may consume `risk_evidence` operatively" in text
    assert "current operative Rule 5 Governance consumer is none" in text


def test_boundary_declares_rule_5_supersession_and_no_duplicate_owner():
    text = _normalized_record()
    assert "remove or make non-authoritative the Thinking Rule 5 evaluator" in text
    assert "prevent two authoritative Rule 5 evaluators" in text
    assert "No duplicate authoritative evaluator may be introduced by 91A" in text


def test_boundary_declares_required_future_effective_precedence():
    text = _normalized_record()
    for rule in (
        "Identity Rule 1 / Rule 2", "Rule 3", "Rule 4", "Rule 5", "Rule 6",
        "Rule 7", "Rule 8", "Rule 9",
    ):
        assert rule in text
    assert "Future Rule 5 migration precedence is not yet implemented or proven" in text
    assert "Rule 5 to override Rule 3 or Rule 4" in text


def test_boundary_selects_exact_reason_preservation():
    text = _normalized_record()
    assert "OPTION A — EXACT REASON PRESERVATION" in text
    assert "High-risk request ({action_type}). Human approval required before any action." in text
    assert "High-risk classification: {action_type}." in text
    assert "Human approval is required before execution." in text
    assert "No Governance-generic replacement reason is authorized" in text


def test_boundary_declares_approval_request_equivalence():
    text = _normalized_record()
    for field in (
        "approval_required", "approval_type", "approval_status", "decision_type",
        "execution_decision", "reason", "risk_level", "risk_action_type",
        "requested_action", "required_confirmations", "safety_checks", "metadata shape",
    ):
        assert field in text
    assert "No new approval-request schema is authorized" in text


def test_boundary_declares_t3_raw_and_effective_trace_contract():
    text = _normalized_record()
    assert "raw Thinking trace must remain truthful" in text
    assert "effective Governance trace must remain truthful" in text
    assert "trace must not claim Rule 5 Governance ownership before future activation" in text
    assert "required strategy is T3-style separation" in text
    assert "Trace remains response-only and non-persistent" in text


def test_boundary_declares_activation_and_safe_evidence_handling():
    text = _normalized_record()
    for value in ("`None`", "non-dict evidence", "missing `risk_level`", "unknown `risk_level`",
                  "missing `action_type`", "missing `confidence`", "non-list `reasons`"):
        assert value in text
    assert "does not authorize or perform any of those changes" in text
    assert "Before Milestone 91B may begin" in text
    assert "91A these values remain safe" in text


def test_boundary_declares_api_persistence_execution_and_future_gate():
    text = _normalized_record()
    assert "304 paths and 108 schemas" in text
    assert "adds no record store, queue, risk-evidence persistence" in text
    assert "All current execution flags remain false" in text
    assert "separately authorized Milestone 91B" in text
    assert "does not authorize Rule 5 migration, risk activation" in text


def test_boundary_declares_exact_authorized_path_scope():
    text = _text(RECORD)
    section = text.split("## 18. Protected Scope", 1)[1].split("## 19.", 1)[0]
    paths = [
        "PROGRESS.md",
        "docs/architecture/MILESTONE_91_RISK_EVIDENCE_CONTRACT_BOUNDARY.md",
        "tests/test_milestone_91_risk_evidence_contract_boundary.py",
    ]
    assert section.count("```text") == 1
    block = section.split("```text", 1)[1].split("```", 1)[0].strip().splitlines()
    assert block == paths
    assert "All production files" in section


def test_milestone_91a_contains_no_runtime_migration():
    text = _normalized_record()
    assert "performs no runtime migration" in text
    assert "No Rule 5 Governance branch may exist during 91A" in text
    assert "does not authorize Rule 5 migration" in text
    assert not _has_governance_risk_branch()
    assert "aether/core/governance.py" in text
    assert "aether/thinking/policy.py" in text
