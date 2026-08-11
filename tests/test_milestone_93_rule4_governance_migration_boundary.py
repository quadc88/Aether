"""Milestone 93A Rule 4 boundary and equivalence-proof locks.

Static inspection and pure current-state calls only. No endpoints, persistence,
environment mutation, real tools, or runtime migration are exercised.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from aether.core.governance import evaluate_authorization_envelope
from aether.thinking.policy import _evaluate_chat_policy_with_precedence


ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / "docs/architecture/MILESTONE_93_RULE4_GOVERNANCE_MIGRATION_BOUNDARY.md"
POLICY = ROOT / "aether/thinking/policy.py"
GOVERNANCE = ROOT / "aether/core/governance.py"
LOOP = ROOT / "aether/core/loop.py"
PROGRESS = ROOT / "PROGRESS.md"
CANONICAL = ROOT / "tests/test_progress_ledger_canonical_header.py"

H1 = "# Milestone 93 Rule 4 Governance Migration Boundary"
H2 = [
    "## 1. Status and Scope", "## 2. PM Authorization and Non-Authorization",
    "## 3. Authoritative Baseline", "## 4. Rule 4 Classification",
    "## 5. Current Rule Inventory", "## 6. Current Rule 4 Physical Ownership",
    "## 7. Exact Current Rule 4 Trigger", "## 8. Exact Current Rule 4 Ten-Key Projection",
    "## 9. Current Governance Envelope Behavior", "## 10. Current Cross-Layer Precedence",
    "## 11. Current Rule 3/4 Provenance Domain", "## 12. Future Provenance Domain",
    "## 13. Future Meaning of Clear", "## 14. Rule 4 Evidence Producer",
    "## 15. Rule 4 Evidence Transport", "## 16. Future _SECRET_RISK_TERMS Ownership",
    "## 17. Single-Authority and Single-Trigger Invariant", "## 18. Future Governance Precedence",
    "## 19. Rule 3 Protection Boundary", "## 20. Rule 5 Protection Boundary",
    "## 21. Rule 6 Protection Boundary", "## 22. Raw Thinking Fall-Through Contract",
    "## 23. Effective Compatibility Projection", "## 24. Rule 7 Collision Contract",
    "## 25. T3 Trace Truth Contract", "## 26. Downstream Consumer Map",
    "## 27. Malformed and Edge-Case Boundary", "## 28. Direct Thinking Semantic Supersession",
    "## 29. Finalized Artifact Supersession Matrix", "## 30. Future Runtime Production Matrix",
    "## 31. API Persistence and Capability Non-Expansion", "## 32. Observation and Candidate A-F Deferral",
    "## 33. Protected Artifact Policy", "## 34. Regression Gates and Accounting",
    "## 35. Failure and Rollback Boundary", "## 36. Future Runtime Migration Decision Gate",
]
TEN_KEYS = [
    "decision_type", "confidence", "reasons", "required_user_confirmation",
    "tool_suggestion_allowed", "tool_execution_allowed", "blocked_reason",
    "clarification_question", "next_step", "warnings",
]
TERMS = {"password", "secret", "api key", "token", "private_key", "credential", "secret_key", "access_key"}


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _normalized_record() -> str:
    return " ".join(_text(RECORD).split())


def _tree(path: Path) -> ast.Module:
    return ast.parse(_text(path))


def _calls(tree: ast.AST) -> list[str]:
    result = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            result.append(node.func.id if isinstance(node.func, ast.Name) else getattr(node.func, "attr", ""))
    return result


class TestCURRENT_STATE_LOCK:
    def test_record_identity_and_exact_sections(self):
        assert _text(RECORD).splitlines()[0] == H1
        assert [line for line in _text(RECORD).splitlines() if line.startswith("## ")] == H2
        assert len(H2) == 36
        assert "## 37." not in _text(RECORD)

    def test_current_source_trigger_and_owner(self):
        source = _text(POLICY)
        assert "risk_terms = perception.get(\"risk_terms_detected\", [])" in source
        assert "secret_found = any(t in _SECRET_RISK_TERMS for t in risk_terms)" in source
        assert "aether/thinking/policy.py::_evaluate_chat_policy_with_precedence" in _text(RECORD)
        assert "NO operative Rule 4-specific evaluator" in _text(RECORD)

    def test_current_term_set_is_exact(self):
        tree = _tree(POLICY)
        assignment = next(node for node in tree.body if isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id == "_SECRET_RISK_TERMS" for target in node.targets
        ))
        assert set(ast.literal_eval(assignment.value)) == TERMS


class TestTEN_KEY_COMPATIBILITY_LOCK:
    def test_current_rule4_projection_has_exact_ten_keys(self):
        policy, signal = _evaluate_chat_policy_with_precedence(
            {"normalized_text": "hello", "risk_terms_detected": ["password", "ordinary"]},
            {"risk_level": "low", "action_type": "general_request"},
        )
        assert signal == "rule_4"
        assert list(policy) == TEN_KEYS
        section = _text(RECORD).split("## 8. Exact Current Rule 4 Ten-Key Projection", 1)[1]
        key_block = section.split("```text", 1)[1].split("```", 1)[0]
        assert [line.strip() for line in key_block.splitlines() if line.strip()] == TEN_KEYS
        assert policy["tool_suggestion_allowed"] is False
        assert policy["tool_execution_allowed"] is False

    def test_complete_detected_terms_are_joined(self):
        policy, _ = _evaluate_chat_policy_with_precedence(
            {"normalized_text": "hello", "risk_terms_detected": ["ordinary", "password"]},
            {"risk_level": "low", "action_type": "general_request"},
        )
        assert "ordinary, password" in policy["reasons"][0]
        assert policy["warnings"] == ["Potentially sensitive terms detected: ordinary, password"]
        assert "complete detected-term list" in _normalized_record()


class TestCURRENT_PROVENANCE_LOCK:
    def test_current_domain_and_meanings_are_exact(self):
        text = _normalized_record()
        for value in ("rule_3", "rule_4", "clear", "Thinking evaluated the Rule 4 predicate"):
            assert value in text
        assert "Current Rule 3/4 Provenance Domain" in _text(RECORD)

    def test_current_envelope_is_generic_and_nonexecuting(self):
        raw, signal = _evaluate_chat_policy_with_precedence(
            {"normalized_text": "secret", "risk_terms_detected": ["secret"]},
            {"risk_level": "low", "action_type": "general_request"},
        )
        result = evaluate_authorization_envelope(
            thinking_policy=raw, rule_3_4_precedence=signal,
        )
        assert result["decision"] == "require_approval"
        assert result["reason"] == "Human approval is required before execution."
        assert result["tool_execution_allowed"] is False
        assert result["action_execution_allowed"] is False
        assert result["policy_snapshot"] == raw


class TestFUTURE_PROVENANCE_CONTRACT:
    def test_future_domain_removes_rule4(self):
        text = _normalized_record()
        assert "future produced domain" in text.lower()
        assert "rule_3 / clear" in text
        assert "Future `rule_4` provenance is REMOVED" in _text(RECORD)

    def test_future_clear_is_not_preclearance(self):
        text = _normalized_record()
        assert "Future `clear` means only: Rule 3 did not win" in _text(RECORD)
        assert "does not mean Rule 4 was evaluated, passed, or pre-cleared" in _text(RECORD)

    def test_perception_and_transport_are_separated(self):
        text = _normalized_record()
        for phrase in ("Perception is the factual evidence producer", "Core Coordination transports", "Evidence production is not authorization"):
            assert phrase in text


class TestSINGLE_AUTHORITY_LOCK:
    def test_single_future_evaluator_is_locked(self):
        text = _normalized_record()
        assert "exactly once" in text
        assert "one operative Governance evaluator" in text
        assert "one operative `_SECRET_RISK_TERMS` set in Core Governance" in text

    def test_current_governance_has_no_rule4_specific_branch(self):
        source = _text(GOVERNANCE)
        assert "_SECRET_RISK_TERMS" not in source
        assert "risk_terms_detected" not in source
        assert "generic `decision_type == \"require_approval\"`" in _text(RECORD)

    def test_future_duplicate_locations_are_prohibited(self):
        text = _normalized_record()
        for phrase in ("Thinking Rule 4 branch", "Core Coordination Rule 4 predicate", "Action-layer Rule 4 predicate", "duplicate Governance evaluators"):
            assert phrase in text


class TestPRECEDENCE_LOCK:
    def test_future_order_is_exact(self):
        text = _text(RECORD)
        section = text.split("## 18. Future Governance Precedence", 1)[1].split("## 19.", 1)[0]
        order = ["invalid policy", "Identity Rule 1", "Identity Rule 2", "Rule 3", "Rule 4", "Rule 5", "Rule 6"]
        positions = [section.index(item) for item in order]
        assert positions == sorted(positions)

    def test_rule4_blocks_rule5_and_rule6(self):
        text = _normalized_record()
        assert "Rule 5/6 are evaluated only when Rule 4 did not win" in text
        assert "Rule 4 precedes Rule 6" in text


class TestRULE_3_PROTECTION:
    def test_rule3_remains_thinking_and_blocks_governance(self):
        text = _normalized_record()
        for phrase in ("Rule 3 remains Thinking-owned", "Rule 3 prevents Governance evaluation of Rule 4, Rule 5, and Rule 6"):
            assert phrase in text
        policy, signal = _evaluate_chat_policy_with_precedence(
            {"normalized_text": "   ", "risk_terms_detected": ["secret"]},
            {"risk_level": "low", "action_type": "general_request"},
        )
        assert signal == "rule_3"
        assert policy["decision_type"] == "ask_clarification"


class TestRULE_5_6_PROTECTION:
    def test_rule5_contract_is_protected(self):
        text = _normalized_record()
        assert "Rule 5 remains Core Governance-owned" in text
        assert "exact durable high-risk evidence trigger" in text

    def test_rule6_contract_is_protected(self):
        text = _normalized_record()
        for phrase in ("Rule 6 remains Core Governance-owned", "non-None `requested_action`", "existing malformed-action behavior"):
            assert phrase in text


class TestRAW_FALLTHROUGH_LOCK:
    def test_all_remaining_raw_branches_are_named(self):
        text = _normalized_record()
        for phrase in ("Rule 3: ask_clarification + rule_3", "Rule 7: suggest_tool + clear", "Rule 8: ask_clarification + clear", "Rule 9: respond_only + clear"):
            assert phrase in text

    def test_raw_never_becomes_authoritative_rule4(self):
        assert "It never returns an authoritative Rule 4 approval" in _text(RECORD)


class TestRULE7_COLLISION_LOCK:
    def test_raw_true_cannot_leak_into_future_effective_policy(self):
        text = _normalized_record()
        for phrase in ("non-empty low-risk input", "tool_suggestion_allowed = True", "No raw `True` may leak"):
            assert phrase in text
        assert "tool_suggestion_allowed = False" in text
        assert "tool_execution_allowed = False" in text


class TestT3_TRACE_LOCK:
    def test_t3_sources_are_distinct(self):
        text = _normalized_record()
        for phrase in ("Thinking stage records the actual raw Thinking result", "Policy-Gate / Governance stage records the authoritative Governance result", "authorization_envelope[\"policy_snapshot\"]"):
            assert phrase in text

    def test_loop_has_truthful_raw_and_effective_names_currently(self):
        source = _text(LOOP)
        assert "raw_thinking_policy" in source
        assert "effective_thinking_policy = authorization_envelope[\"policy_snapshot\"]" in source
        assert "Do not merge" in _text(RECORD)


class TestMALFORMED_BOUNDARY_LOCK:
    def test_current_malformed_contract_is_exactly_recorded(self):
        text = _normalized_record()
        for phrase in ("missing `risk_terms_detected` defaults to `[]`", "explicit `None` raises native `TypeError`", "unhashable member raises native membership `TypeError`", "direct membership is case-sensitive"):
            assert phrase in text

    def test_future_sidecar_contract_is_exactly_resolved(self):
        text = _normalized_record()
        for phrase in ("The exact future private-sidecar contract is Contract B", "Any iterable is accepted", "A missing sidecar means `[]`", "explicit `None` is not iterable", "Core Governance, the sole future owner"):
            assert phrase in text
        assert "implementation will decide later" not in text.lower()

    def test_future_malformed_exception_class_and_direct_equivalence(self):
        text = _normalized_record()
        assert "native `TypeError`" in text
        assert "same predicate semantics as target `/chat` calls" in text
        assert "same malformed direct Governance calls match the target pipeline's native exception class" in text

    def test_current_none_really_raises_typeerror(self):
        with pytest.raises(TypeError):
            _evaluate_chat_policy_with_precedence(
                {"normalized_text": "secret", "risk_terms_detected": None},
                {"risk_level": "low", "action_type": "general_request"},
            )


class TestSUPERSESSION_LOCK:
    def test_seventeen_direct_surfaces_and_three_cases_are_recorded(self):
        text = _normalized_record()
        assert "17 direct surfaces" in text
        assert "3 Rule 4 cases inside one parameterized matrix" in text

    def test_named_planr2_files_are_present_in_matrix(self):
        text = _text(RECORD)
        for path in ("tests/test_thinking_policy.py", "tests/test_milestone_88_cognitive_signal_arbitration_boundary.py", "tests/test_milestone_89_identity_hard_constraint_migration_boundary.py", "tests/test_milestone_91b_rule5_governance_migration_boundary.py", "tests/test_milestone_92c_rule6_governance_runtime_migration.py"):
            assert path in text

    def test_historical_records_are_protected(self):
        text = _normalized_record()
        assert "Historical architecture records remain byte-identical" in text
        assert "not rewritten to claim Rule 4 was always Governance-owned" in text


class TestNON_CAPABILITY_LOCK:
    def test_production_and_runtime_mutation_are_forbidden(self):
        text = _normalized_record()
        for phrase in ("not a runtime migration", "No API field", "No tool or action execution", "No runtime/private files are touched"):
            assert phrase in text
        assert "Commit: none" not in _text(RECORD)
        assert "Tag: none" not in _text(RECORD)
        assert "Push: none" not in _text(RECORD)
        assert "Lifecycle durability:" in _text(RECORD)
        assert "determined from Git" in _normalized_record()
        assert "does not self-assert its own commit" in _normalized_record()

    def test_observation_and_candidates_are_deferred(self):
        text = _normalized_record()
        for phrase in ("Verification Aggregation remains undefined", "producer-proof", "aggregator-proof", "Candidate A-F remain deferred"):
            assert phrase in text

    def test_boundary_test_is_static_and_pure_call_only(self):
        source = _text(Path(__file__))
        tree = ast.parse(source)
        imported = {alias.name for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom)) for alias in node.names}
        assert not {"TestClient", "requests", "httpx"}.intersection(imported)
        assert not {"write_text", "open", "record_event", "create_approval_record"}.intersection(_calls(tree))

    def test_canonical_and_progress_are_the_only_existing_allowed_paths(self):
        assert CANONICAL.is_file() and PROGRESS.is_file()
        assert "Milestone 93A" in _text(PROGRESS)
        assert "Milestone 93A" in _text(RECORD)
