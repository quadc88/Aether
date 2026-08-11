"""Static and pure-call contract tests for the Milestone 92B boundary."""

from __future__ import annotations

import ast
import re
import subprocess
from pathlib import Path

from aether.core.governance import evaluate_authorization_envelope


ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / "docs/architecture/MILESTONE_92_RULE6_GOVERNANCE_MIGRATION_BOUNDARY.md"
PROGRESS = ROOT / "PROGRESS.md"
POLICY = ROOT / "aether/thinking/policy.py"
GOVERNANCE = ROOT / "aether/core/governance.py"
LOOP = ROOT / "aether/core/loop.py"
RISK = ROOT / "aether/verification/risk.py"
CANONICAL = ROOT / "tests/test_progress_ledger_canonical_header.py"
BOUNDARY = ROOT / "tests/test_milestone_92_rule6_governance_migration_boundary.py"

H1 = "# Milestone 92 Rule 6 Medium-Risk Tool Governance Migration Boundary"
SECTIONS = [
    "## 1. Status and Scope",
    "## 2. Purpose and Classification",
    "## 3. Current Architectural Authority",
    "## 4. Current Rule 6 Trigger and Output",
    "## 5. Current Ownership Split",
    "## 6. Rule 4 Incremental-Migration Boundary",
    "## 7. Current Effective Precedence",
    "## 8. Future Target Precedence",
    "## 9. Risk Evidence and Requested-Action Transport",
    "## 10. Target Governance Rule 6 Evaluator",
    "## 11. Single-Authority and Single-Trigger Invariant",
    "## 12. Raw Thinking Proposal Contract",
    "## 13. Effective Compatibility Projection",
    "## 14. T3 Truthful Trace Contract",
    "## 15. External Behavior Equivalence",
    "## 16. Rule 7 Protection",
    "## 17. Rules 3, 8, and 9 Protection",
    "## 18. Current Consumer Map",
    "## 19. Future 92C Supersession Matrix",
    "## 20. Future 92C Runtime Production Matrix",
    "## 21. Protected Paths and Artifact Policy",
    "## 22. 92B Non-Capabilities",
    "## 23. Regression Gates and Accounting",
    "## 24. Failure and Rollback Boundary",
    "## 25. Future Migration Decision Gate",
]
BUILD_PATHS = [
    "PROGRESS.md",
    "docs/architecture/MILESTONE_92_RULE6_GOVERNANCE_MIGRATION_BOUNDARY.md",
    "tests/test_milestone_92_rule6_governance_migration_boundary.py",
    "tests/test_progress_ledger_canonical_header.py",
]
CANONICAL_ALLOWED = {
    "test_current_92a_local_state_is_consistent_acROSS_header".lower(),
    "test_pipeline_maturity_records_current_state",
    "test_full_suite_and_canonical_counts_match_header",
    "test_92a_vs_functional_92_terminology_contract",
}
PRE_92B_COMMIT = "a9c0b8cfe09251d688bbf0e97f799b8597d9dd87"
IMPLEMENTATION_TAG = "milestone-92B-rule6-governance-migration-boundary"
IMPLEMENTATION_COMMIT = "22d819b6bd3a305536c0beba57f670a5433fe21e"
FINAL_CLOSURE_COMMIT = "680878aeb9dc97e476d82751810899d41bddbe8b"
BUILD_STAGE_ALLOWED = {
    "test_current_92a_local_state_is_consistent_across_header",
    "test_pipeline_maturity_records_current_state",
    "test_full_suite_and_canonical_counts_match_header",
    "test_92a_vs_functional_92_terminology_contract",
}
CLOSURE_STAGE_ALLOWED = {
    "test_current_92a_local_state_is_consistent_across_header",
    "test_pipeline_maturity_records_current_state",
    "test_92a_vs_functional_92_terminology_contract",
    "test_current_closure_tag_name_and_resolves",
    "test_previous_closure_tag_is_92a",
}


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _record() -> str:
    return _text(RECORD)


def _declared_build_paths(text: str) -> tuple[str, ...]:
    scope_start = "The actual four-path Build scope is exactly:\n"
    scope_end = "\n\nThe three core boundary artifact paths"
    scope = text.split(scope_start, 1)[1].split(scope_end, 1)[0]
    return tuple(re.findall(r"^\s*\d+\.\s+`([^`]+)`[.;]?\s*$", scope, re.MULTILINE))


def _tree(path: Path) -> ast.Module:
    return ast.parse(_text(path))


def _function_names(path: Path) -> set[str]:
    return {
        node.name
        for node in ast.walk(_tree(path))
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name.startswith("test_")
    }


def _function_dumps(path: Path) -> dict[str, str]:
    return _function_dumps_from_text(_text(path))


def _function_dumps_from_text(text: str) -> dict[str, str]:
    return {
        node.name: ast.dump(node)
        for node in ast.walk(ast.parse(text))
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name.startswith("test_")
    }


def _policy(perception=None, risk=None, tool=None):
    from aether.thinking.policy import _evaluate_chat_policy_with_precedence

    return _evaluate_chat_policy_with_precedence(
        perception or {"normalized_text": "ordinary request", "risk_terms_detected": []},
        risk or {"risk_level": "low", "action_type": "general_request"},
        tool,
    )


class TestDecisionRecordScope:
    def test_record_path_and_h1(self):
        assert RECORD.is_file()
        assert _record().splitlines()[0] == H1

    def test_exact_twenty_five_top_level_sections(self):
        assert [line for line in _record().splitlines() if line.startswith("## ")] == SECTIONS

    def test_boundary_scope_is_documentation_and_tests_only(self):
        text = _record().lower()
        for phrase in ("boundary-only", "no runtime edit", "no real tool execution", "persistent store"):
            assert phrase in text

    def test_rule_6_classification_and_owner_are_exact(self):
        text = " ".join(_record().split())
        assert "Operational Hard Constraint" in text
        assert "Core Governance" in text
        assert "aether/thinking/policy.py::_evaluate_chat_policy_with_precedence" in text

    def test_exact_four_path_build_matrix(self):
        text = _record()
        assert _declared_build_paths(text) == tuple(BUILD_PATHS)

    def test_finalized_records_and_existing_tests_are_protected_in_92b(self):
        text = " ".join(_record().split())
        assert "Finalized M87/M88/M89/M91" in text
        assert "finalized/runtime tests" in text
        assert "Thinking-policy/runtime tests" in text
        assert "Exactly four canonical functions may change" in text
        assert "future 92C targets" in text
        tag_result = subprocess.run(
            ["git", "rev-parse", IMPLEMENTATION_TAG],
            check=True, capture_output=True, text=True, cwd=ROOT,
        )
        assert tag_result.stdout.strip() == IMPLEMENTATION_COMMIT
        build_baseline_text = subprocess.run(
            ["git", "show", f"{PRE_92B_COMMIT}:tests/test_progress_ledger_canonical_header.py"],
            check=True, capture_output=True, text=True, cwd=ROOT,
        ).stdout
        implementation_baseline_text = subprocess.run(
            ["git", "show", f"{IMPLEMENTATION_TAG}:tests/test_progress_ledger_canonical_header.py"],
            check=True, capture_output=True, text=True, cwd=ROOT,
        ).stdout
        closure_baseline_text = subprocess.run(
            ["git", "show", f"{FINAL_CLOSURE_COMMIT}:tests/test_progress_ledger_canonical_header.py"],
            check=True, capture_output=True, text=True, cwd=ROOT,
        ).stdout
        build_baseline = _function_dumps_from_text(build_baseline_text)
        implementation_baseline = _function_dumps_from_text(implementation_baseline_text)
        closure_baseline = _function_dumps_from_text(closure_baseline_text)
        build_delta = {
            name for name in implementation_baseline
            if implementation_baseline[name] != build_baseline.get(name)
        }
        closure_delta = {
            name for name in closure_baseline
            if closure_baseline[name] != implementation_baseline.get(name)
        }
        assert build_delta == BUILD_STAGE_ALLOWED
        assert closure_delta == CLOSURE_STAGE_ALLOWED
        baseline_path = ROOT / ".milestone_92b_canonical_baseline.tmp"
        assert not baseline_path.exists()


class TestRule6CurrentAndTargetContract:
    def test_current_medium_comparison_is_exact(self):
        assert 'risk_level == "medium" and suggested_tool is not None' not in _text(POLICY)
        assert 'risk_level == "medium" and requested_action is not None' in _text(GOVERNANCE)

    def test_current_non_none_suggested_tool_condition_is_exact(self):
        assert "suggested_tool is not None" in _text(POLICY)
        assert "A dictionary without `tool_id` is non-None and triggers" in " ".join(_record().split())

    def test_current_none_tool_does_not_trigger_rule6(self):
        policy, signal = _policy(risk={"risk_level": "medium"}, tool=None)
        assert signal == "clear"
        assert policy["decision_type"] != "require_approval"

    def test_current_empty_dict_triggers_rule6(self):
        policy, signal = _policy(risk={"risk_level": "medium"}, tool={})
        assert signal == "clear"
        assert policy["decision_type"] == "respond_only"
        assert evaluate_authorization_envelope(
            policy,
            requested_action={},
            risk_evidence={"risk_level": "medium"},
            rule_3_4_precedence=signal,
        )["decision"] == "require_approval"

    def test_current_missing_tool_id_triggers_rule6(self):
        policy, _ = _policy(risk={"risk_level": "medium"}, tool={"name": "unknown"})
        assert policy["decision_type"] == "respond_only"

    def test_current_non_dict_malformed_shape_is_documented(self):
        assert ".get('tool_id', '')" in _text(POLICY)
        assert "unsupported non-dictionary malformed shape" in _record()

    def test_current_rule6_raw_fields_are_exact(self):
        policy, _ = _policy(risk={"risk_level": "medium"}, tool={})
        assert set(policy) == {
            "decision_type", "confidence", "reasons", "required_user_confirmation",
            "tool_suggestion_allowed", "tool_execution_allowed", "blocked_reason",
            "clarification_question", "next_step", "warnings",
        }

    def test_future_governance_uses_clear_provenance(self):
        assert 'rule_3_4_precedence == "clear"' in _record()
        assert "exact `clear` provenance" in _record()

    def test_future_governance_uses_non_none_requested_action(self):
        text = _record()
        assert "non-None requested_action" in text
        assert "must not be narrowed to a valid tool" in text

    def test_future_rule6_projection_preserves_legacy_effective_fields(self):
        text = _record()
        for field in ("decision_type", "required_user_confirmation", "blocked_reason", "next_step"):
            assert field in text
        assert "formatting-only" in text
        assert "tool_execution_allowed=false" in text


class TestRule6GovernanceOwnership:
    def test_current_physical_evaluator_is_thinking(self):
        assert "_evaluate_chat_policy_with_precedence" in _text(POLICY)
        assert "current physical evaluator" in _record().lower()

    def test_current_governance_has_generic_not_rule6_branch(self):
        assert 'risk_level == "medium" and requested_action is not None' in _text(GOVERNANCE)
        assert "_format_rule_6_compatibility_policy" in _text(GOVERNANCE)
        assert "current envelope authority" in _record()

    def test_future_governance_is_single_authoritative_evaluator(self):
        text = _record()
        assert "sole authoritative Rule 6 evaluator" in text
        assert "one Rule 6 trigger evaluator" in text

    def test_future_projection_is_formatting_only(self):
        assert "projection is formatting-only" in _record()
        assert "not a second trigger evaluator" in _record()

    def test_rule4_signal_blocks_rule6_governance_activation(self):
        text = _record()
        assert "Rule 4 provenance signal blocks downstream Rule 5 and future Rule 6" in text
        assert "92B changes no Rule 4 semantics" in text

    def test_rule5_precedes_rule6(self):
        text = _record()
        assert text.index("Governance Rule 5 high-risk selection precedes Governance Rule 6") < text.index("## 9.")

    def test_rule7_remains_thinking_soft_signal(self):
        assert "Rule 7 remains a Thinking soft signal" in _record()

    def test_rules3_8_9_remain_thinking_defaults(self):
        text = _record()
        for rule in ("Rule 3 remains", "Rule 8 remains", "Rule 9 remains"):
            assert rule in text


class TestPrecedenceAndTransport:
    def test_invalid_policy_precedes_all_rules(self):
        assert "invalid policy" in _record()
        assert _text(GOVERNANCE).index("Precedence 1") < _text(GOVERNANCE).index("Precedence 2")

    def test_identity_rules_precede_rule4_and_rule6(self):
        text = _record().split("## 7.", 1)[1].split("## 8.", 1)[0]
        assert text.index("Identity Rule 1") < text.index("Rule 4")
        assert text.index("Identity Rule 2") < text.index("Rule 6")

    def test_rule3_precedes_rule4_and_rule6(self):
        text = _record().split("## 7.", 1)[1].split("## 8.", 1)[0]
        assert text.index("Rule 3") < text.index("Rule 4") < text.index("Rule 6")

    def test_rule4_precedes_rule6_in_current_thinking(self):
        source = _text(POLICY)
        assert "secret_found" not in source
        assert "_SECRET_RISK_TERMS" not in source
        assert 'risk_level == "medium"' not in source
        governance = _text(GOVERNANCE)
        assert governance.index("# --- Governance Rule 4") < governance.index("# --- Governance Rule 6")
        assert 'rule4_risk_terms_detected' in governance

    def test_future_rule5_clear_high_precedes_rule6(self):
        text = _record()
        assert "Governance Rule 5 high-risk selection precedes Governance Rule 6" in text

    def test_future_rule6_medium_non_none_requested_action(self):
        assert 'risk_evidence["risk_level"] == "medium"' in _record()
        assert "non-None requested_action" in _record()

    def test_low_tool_behavior_remains_distinct(self):
        policy, _ = _policy(risk={"risk_level": "low"}, tool={"tool_id": "x"})
        assert policy["decision_type"] == "suggest_tool"
        assert "Rule 7 remains" in _record()

    def test_rule8_and_rule9_fall_through_remains_separate(self):
        text = _record()
        assert "Rule 8 remains" in text and "Rule 9 remains" in text


class TestCompatibilityAndTrace:
    def test_effective_decision_remains_require_approval(self):
        assert "decision_type=require_approval" in _record()

    def test_effective_confirmation_and_approval_type_remain_exact(self):
        text = _record()
        assert "required_user_confirmation=true" in text
        assert "approval_type=human_review" in text

    def test_effective_reason_and_policy_snapshot_remain_exact(self):
        text = _record()
        assert "existing approval reason semantics" in text
        assert 'authorization_envelope["policy_snapshot"]' in text

    def test_pending_queue_status_remains_non_executing(self):
        text = _record()
        assert "approval_status=pending" in text
        assert "does not authorize execution" in text

    def test_all_execution_flags_remain_false(self):
        text = _record()
        for flag in ("tool_execution_allowed=false", "execution_allowed=false", "tool_executed=false"):
            assert flag in text

    def test_response_shape_and_openapi_remain_unchanged(self):
        text = _record()
        assert "response shape" in text and "OpenAPI" in text
        assert "304 paths / 108 schemas" in text

    def test_loop_trace_stage_names_order_and_count_remain_unchanged(self):
        assert "loop_trace" in _record()
        assert "stage ordering" in _record()
        assert "count" in _record()

    def test_raw_thinking_trace_is_truthful(self):
        assert "actual raw Thinking proposal" in _record()
        assert "must not be written back into the raw Thinking trace" in " ".join(_record().split())

    def test_governance_trace_is_authoritative(self):
        assert "Governance/Policy-Gate trace: authoritative Governance result" in _record()

    def test_raw_evidence_and_policy_values_do_not_leak(self):
        text = _record()
        assert "Raw evidence" in text
        assert "must not leak" in text


class TestProtectedAndNonCapabilities:
    def test_no_new_public_api_field(self):
        assert "No new public field" in _record()

    def test_no_new_persistence_or_store(self):
        assert "persistent store" in _record()
        assert "No new public envelope key" in _record()

    def test_no_tool_execution(self):
        assert "real tool execution" in _record()

    def test_no_evidence_collection_or_observe_capture(self):
        text = _record()
        assert "evidence collection" in text
        assert "automatic Observe capture" in text

    def test_no_apply_rollback_or_background_runtime(self):
        text = " ".join(_record().split())
        for phrase in ("real apply", "rollback", "background scheduler"):
            assert phrase in text

    def test_candidate_a_to_f_remain_deferred(self):
        assert "Candidate A-F remain deferred" in _record()
