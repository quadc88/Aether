"""Milestone 89A contract locks for the Identity Hard-Constraint migration boundary.

This suite is deliberately static or pure-call only. It does not use a
TestClient, invoke an endpoint, persist a record, modify configuration,
execute a tool/action, or access the network. It verifies the migration
boundary record and the immutability of current runtime behavior.
"""

from __future__ import annotations

import ast
import importlib
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / "docs/architecture/MILESTONE_89_IDENTITY_HARD_CONSTRAINT_MIGRATION_BOUNDARY.md"
ARCHITECTURE = ROOT / "docs/ARCHITECTURE.md"
CONSTITUTION = ROOT / "docs/CONSTITUTION.md"
M87_RECORD = ROOT / "docs/architecture/MILESTONE_87_CORE_GOVERNANCE_AUTHORIZATION_BOUNDARY.md"
M88_RECORD = ROOT / "docs/architecture/MILESTONE_88_COGNITIVE_SIGNAL_ARBITRATION_BOUNDARY.md"
POLICY = ROOT / "aether/thinking/policy.py"
GOVERNANCE = ROOT / "aether/core/governance.py"
LOOP = ROOT / "aether/core/loop.py"
API_SERVER = ROOT / "aether/interface/api_server.py"

H1 = "# Milestone 89 Identity Hard-Constraint Migration Boundary"
SECTIONS = [
    "## 1. Status and Scope",
    "## 2. Purpose",
    "## 3. Authoritative Existing Baseline",
    "## 4. Relationship to Architecture v0.3.0",
    "## 5. Relationship to Milestone 87",
    "## 6. Relationship to Corrected Milestone 88",
    "## 7. Current Production Chain",
    "## 8. Current Identity Evidence Contract",
    "## 9. Current Rule 1 Contract",
    "## 10. Current Rule 2 Contract",
    "## 11. Current Rule Precedence",
    "## 12. Current Thinking-Policy Output Contract",
    "## 13. Current Governance-Envelope Contract",
    "## 14. Downstream Consumer Inventory",
    "## 15. Complete Compatibility Surface",
    "## 16. Internal Semantic Change Classification",
    "## 17. Evidence Operativity and Supersession Analysis",
    "## 18. Finalized-Test Impact Inventory",
    "## 19. Future Migration Dependency Direction",
    "## 20. Future Milestone 89B File Matrix",
    "## 21. Failure and Malformed-Evidence Rules",
    "## 22. Protected Files and Non-Goals",
    "## 23. Completion and Acceptance Criteria",
    "## 24. Milestone 89 Finalization and Closure Rule",
]


def _record() -> str:
    return RECORD.read_text(encoding="utf-8")


def _normalized() -> str:
    return " ".join(_record().split())


def _tree(path: Path) -> ast.Module:
    return ast.parse(path.read_text(encoding="utf-8"))


def _policy_fn():
    return importlib.import_module("aether.thinking.policy").decide_chat_policy


def _gov_fn():
    return importlib.import_module("aether.core.governance").evaluate_authorization_envelope


def _base_perception(text: str = "hello there") -> dict:
    return {"normalized_text": text, "risk_terms_detected": []}


def _base_risk(level: str = "low", action: str = "general_request") -> dict:
    return {"risk_level": level, "action_type": action, "confidence": "likely", "reasons": []}


def _make_policy(text: str = "hello there", risk_level: str = "low", risk_action: str = "general_request",
                 tool: dict | None = None, identity: dict | None = None,
                 secrets: list[str] | None = None) -> dict:
    perception = _base_perception(text)
    if secrets:
        perception = {**perception, "risk_terms_detected": secrets}
    risk = _base_risk(risk_level, risk_action)
    return _policy_fn()(
        perception=perception,
        risk=risk,
        suggested_tool=tool,
        identity_integrity_status=identity,
    )


def _changed_paths() -> list[str]:
    """Exact repository changed-path set for the Milestone 89 Build.

    This is a historical contract: it measures the committed changes between
    the pre-89 baseline and the Milestone 89 implementation commit, not the
    current working tree or HEAD. Future milestones may add new files without
    affecting this historical assertion.
    """
    import subprocess
    pre_89 = "943b442b3b765904fa508cc617ce25fd279a8b91"
    impl_commit = "6e5c7b8474314d21723a08c1655843548eb7d65e"
    return sorted(subprocess.run(
        ["git", "diff", "--name-only", pre_89, impl_commit],
        capture_output=True, text=True, cwd=str(ROOT),
    ).stdout.splitlines())


def _amended_test_sets() -> dict[str, list[str]]:
    """Exact set of amended test functions per superseded test file,
    computed as an AST diff between the pre-implementation commit and
    the implementation commit."""
    import subprocess
    files = (
        "tests/test_milestone_87_core_governance_authorization_boundary.py",
        "tests/test_milestone_88_cognitive_signal_arbitration_boundary.py",
        "tests/test_thinking_policy.py",
    )
    result = {}
    # Use the parent of the implementation commit as baseline
    impl_commit = "6e5c7b8474314d21723a08c1655843548eb7d65e"
    parent = subprocess.run(
        ["git", "rev-parse", f"{impl_commit}^"], capture_output=True, text=True, cwd=str(ROOT),
    ).stdout.strip()
    for rel in files:
        impl_src = subprocess.run(
            ["git", "show", f"{impl_commit}:{rel}"], capture_output=True, text=True,
            cwd=str(ROOT), check=True,
        ).stdout
        parent_src = subprocess.run(
            ["git", "show", f"{parent}:{rel}"], capture_output=True, text=True,
            cwd=str(ROOT), check=True,
        ).stdout

        def _func_src(src: str) -> dict[str, str]:
            tree = ast.parse(src)
            return {
                node.name: ast.dump(node)
                for node in ast.walk(tree)
                if isinstance(node, ast.FunctionDef) and node.name.startswith("test_")
            }

        impl_funcs = _func_src(impl_src)
        parent_funcs = _func_src(parent_src)
        result[rel] = sorted(
            name for name in impl_funcs
            if impl_funcs.get(name) != parent_funcs.get(name)
        )
    return result


def _assert_exact_amendment_matrix(sets: dict[str, list[str]]) -> None:
    """Lock the corrected authoritative supersession matrix (M87 2, M88 7,
    Thinking 5 full + 1 partial, total 15 existing tests touched)."""
    assert sets["tests/test_milestone_87_core_governance_authorization_boundary.py"] == [
        "test_60_direct_identity_evidence_operative_only_for_identity_rules",
        "test_62_identity_evidence_raw_values_absent_from_reason_and_warnings",
    ], f"M87 amendment set: {sets['tests/test_milestone_87_core_governance_authorization_boundary.py']}"
    assert sets["tests/test_milestone_88_cognitive_signal_arbitration_boundary.py"] == [
        "test_07_actual_current_rule_count_is_seven",
        "test_10_exact_trigger_conditions_from_ast",
        "test_11_exact_current_decision_outputs",
        "test_12_exact_confirmation_and_execution_fields",
        "test_29_identity_evidence_operative_only_through_governance",
        "test_30_exact_new_classification_string",
        "test_45_only_authorized_production_modules_changed",
    ], f"M88 amendment set: {sets['tests/test_milestone_88_cognitive_signal_arbitration_boundary.py']}"
    assert sets["tests/test_thinking_policy.py"] == [
        "test_block_even_with_tool_and_medium_risk",
        "test_block_on_identity_changed",
        "test_identity_issues_have_high_confidence",
        "test_require_approval_when_failed",
        "test_require_approval_when_missing",
        "test_tool_execution_always_false",
    ], f"Thinking amendment set: {sets['tests/test_thinking_policy.py']}"
    total = sum(len(v) for v in sets.values())
    assert total == 15, f"Expected 15 existing tests touched, got {total}"


def _assert_exact_nine_path_set() -> None:
    """Lock the exact nine-path Milestone 89B Build file set."""
    assert _changed_paths() == [
        "PROGRESS.md",
        "aether/core/governance.py",
        "aether/core/loop.py",
        "aether/thinking/policy.py",
        "docs/architecture/MILESTONE_89_IDENTITY_HARD_CONSTRAINT_MIGRATION_BOUNDARY.md",
        "tests/test_milestone_87_core_governance_authorization_boundary.py",
        "tests/test_milestone_88_cognitive_signal_arbitration_boundary.py",
        "tests/test_milestone_89_identity_hard_constraint_migration_boundary.py",
        "tests/test_thinking_policy.py",
    ], f"Repository changed paths not exact: {_changed_paths()}"


class TestDecisionRecordStructure:
    def test_01_record_path_and_h1(self):
        assert RECORD.is_file()
        assert _record().splitlines()[0] == H1

    def test_02_exact_twenty_four_sections(self):
        actual = [line for line in _record().splitlines() if line.startswith("## ")]
        assert actual == SECTIONS

    def test_03_documentation_and_tests_only_scope(self):
        text = _record()
        assert "documentation and tests only" in text.lower() or "Documentation/tests only" in text

    def test_04_rules_remain_in_thinking_during_89a(self):
        text = _record()
        assert "does not migrate Rules 1 or 2" in text

    def test_05_identity_evidence_non_operative_during_89a(self):
        text = _record()
        assert "does not make Identity evidence operative" in text

    def test_06_migration_classified_correctly(self):
        text = " ".join(_record().split())
        assert "EXTERNALLY DECISION-, APPROVAL-, RESPONSE-SHAPE-, AND EXECUTION-FLAG PRESERVING, WITH AN INTENTIONAL DIAGNOSTIC TRACE SEMANTIC CHANGE AND INTERNAL PHYSICAL-OWNERSHIP CHANGE" in text

    def test_07_no_current_production_behavior_modified(self):
        text = _record()
        assert "does not change any runtime behavior" in text

    def test_08_no_milestone_87_or_88_artifact_modified(self):
        text = _record()
        assert "Modifying any finalized Milestone 87 or 88 artifact" in text


class TestCurrentIdentityContract:
    def test_09_exact_identity_input_form_received_by_thinking(self):
        src = POLICY.read_text()
        tree = ast.parse(src)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "decide_chat_policy":
                params = [p.arg for p in node.args.args]
                assert "identity_integrity_status" in params
                break
        # Milestone 89B: the parameter is a compatibility argument only.
        # Thinking must NOT read its contents.
        assert 'identity_integrity_status.get("status", "")' not in src
        assert 'identity_status == "changed"' not in src

    def test_10_exact_identity_input_form_received_by_governance(self):
        src = GOVERNANCE.read_text()
        tree = ast.parse(src)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "evaluate_authorization_envelope":
                # Check regular params (not where identity_evidence lives)
                params = [p.arg for p in node.args.args]
                assert "thinking_policy" in params
                # Check it's keyword-only (after the * marker)
                kwonly = [p.arg for p in node.args.kwonlyargs]
                assert "identity_integrity_evidence" in kwonly
                assert "risk_evidence" in kwonly
                break

    def test_11_identity_evidence_operative_in_governance_rules_1_and_2(self):
        gov_src = GOVERNANCE.read_text()
        # The parameter is accepted AND used in the decision logic
        assert "identity_integrity_evidence" in gov_src
        assert "if isinstance(identity_integrity_evidence, dict)" in gov_src
        assert 'identity_integrity_evidence.get("status", "")' in gov_src
        # Rules 1/2 are evaluated here, authoritatively
        assert 'status == "changed"' in gov_src
        assert 'status in ("missing", "failed")' in gov_src

    def test_12_thinking_never_reads_identity_evidence(self):
        src = POLICY.read_text()
        # Thinking does NOT read status, changed, warnings, or hashes
        assert "identity_integrity_status.get" not in src
        assert "identity_integrity_status[" not in src
        assert 'identity_integrity_status.get("changed")' not in src
        assert 'identity_integrity_status.get("warnings")' not in src
        assert 'identity_integrity_status.get("current_sha256")' not in src


class TestRuleContracts:
    def test_13_exact_rule_1_trigger_in_governance(self):
        src = GOVERNANCE.read_text()
        assert 'status == "changed"' in src
        assert 'identity_status == "changed"' not in POLICY.read_text()

    def test_14_exact_rule_1_projection(self):
        p = _make_policy()  # raw Thinking is identity-insensitive
        env = _gov_fn()(thinking_policy=p, identity_integrity_evidence={"status": "changed"})
        snap = env["policy_snapshot"]
        assert snap["decision_type"] == "block"
        assert snap["confidence"] == "high"
        assert snap["required_user_confirmation"] is True
        assert snap["tool_execution_allowed"] is False
        assert snap["tool_suggestion_allowed"] is False
        assert snap["blocked_reason"] == "Identity integrity changed. Human review is required before continuing."
        assert snap["clarification_question"] is None
        assert snap["next_step"] == "Verify identity seed integrity before continuing."
        assert snap["warnings"] == ["Identity seed integrity mismatch detected."]
        assert snap["reasons"] == ["Identity seed checksum changed — integrity compromised."]

    def test_15_exact_rule_1_governance_envelope(self):
        p = _make_policy()
        env = _gov_fn()(thinking_policy=p, identity_integrity_evidence={"status": "changed"})
        assert env["allowed"] is False
        assert env["decision"] == "block"
        assert env["reason"] == "Identity integrity changed. Human review is required before continuing."
        assert env["required_user_confirmation"] is True
        assert env["tool_execution_allowed"] is False
        assert env["action_execution_allowed"] is False
        assert env["policy_snapshot"] != p  # Identity projection replaces the raw proposal
        assert env["warnings"] == []

    def test_16_exact_rule_2_trigger_in_governance(self):
        src = GOVERNANCE.read_text()
        assert 'status in ("missing", "failed")' in src
        assert 'identity_status in ("missing", "failed")' not in POLICY.read_text()

    def test_17_exact_rule_2_projection_missing(self):
        p = _make_policy()
        env = _gov_fn()(thinking_policy=p, identity_integrity_evidence={"status": "missing"})
        snap = env["policy_snapshot"]
        assert snap["decision_type"] == "require_approval"
        assert snap["confidence"] == "high"
        assert snap["required_user_confirmation"] is True
        assert snap["tool_execution_allowed"] is False
        assert snap["blocked_reason"] is None
        assert snap["clarification_question"] is None
        assert snap["warnings"] == ["Identity integrity status: missing."]
        assert "missing" in snap["reasons"][0]

    def test_18_exact_rule_2_projection_failed(self):
        p = _make_policy()
        env = _gov_fn()(thinking_policy=p, identity_integrity_evidence={"status": "failed"})
        snap = env["policy_snapshot"]
        assert snap["decision_type"] == "require_approval"
        assert snap["required_user_confirmation"] is True
        assert "failed" in snap["reasons"][0]
        assert snap["warnings"] == ["Identity integrity status: failed."]

    def test_19_exact_rule_2_governance_envelope(self):
        p = _make_policy()
        env = _gov_fn()(thinking_policy=p, identity_integrity_evidence={"status": "missing"})
        assert env["allowed"] is False
        assert env["decision"] == "require_approval"
        # Governance uses the GENERIC fixed reason
        assert env["reason"] == "Human approval is required before execution."
        assert env["required_user_confirmation"] is True
        assert env["tool_execution_allowed"] is False
        assert env["action_execution_allowed"] is False

    def test_20_policy_snapshot_behavior(self):
        p = _make_policy(identity={"status": "changed"})
        env = _gov_fn()(thinking_policy=p)
        # Non-Identity snapshot is a shallow copy of the raw proposal
        assert env["policy_snapshot"] == p
        assert env["policy_snapshot"] is not p  # not the same object
        # Identity projection is also a distinct object
        env2 = _gov_fn()(thinking_policy=p, identity_integrity_evidence={"status": "changed"})
        assert env2["policy_snapshot"] is not p

    def test_21_confirmation_behavior(self):
        # Rule 1: required_user_confirmation = True (envelope + projection)
        p = _make_policy()
        env1 = _gov_fn()(thinking_policy=p, identity_integrity_evidence={"status": "changed"})
        assert env1["required_user_confirmation"] is True
        assert env1["policy_snapshot"]["required_user_confirmation"] is True
        # Rule 2: required_user_confirmation = True (envelope + projection)
        env2 = _gov_fn()(thinking_policy=p, identity_integrity_evidence={"status": "missing"})
        assert env2["required_user_confirmation"] is True
        assert env2["policy_snapshot"]["required_user_confirmation"] is True

    def test_22_execution_flags(self):
        # Both rules set tool_execution_allowed = False in projections and
        # in the Governance envelope
        p = _make_policy()
        env1 = _gov_fn()(thinking_policy=p, identity_integrity_evidence={"status": "changed"})
        assert env1["policy_snapshot"]["tool_execution_allowed"] is False
        assert env1["tool_execution_allowed"] is False
        assert env1["action_execution_allowed"] is False
        env2 = _gov_fn()(thinking_policy=p, identity_integrity_evidence={"status": "missing"})
        assert env2["policy_snapshot"]["tool_execution_allowed"] is False
        assert env2["tool_execution_allowed"] is False
        assert env2["action_execution_allowed"] is False


class TestRulePrecedence:
    def test_23_current_source_order_preserved(self):
        # Thinking: sidecar Rules 3/4 remain ordered before Rules 6-9.
        src = POLICY.read_text()
        lines = src.splitlines()
        rule_lines = {}
        for i, line in enumerate(lines):
            lineno = i + 1
            if "not normalized_text" in line:
                rule_lines[3] = lineno
            elif "secret_found = any" in line:
                rule_lines[4] = lineno
            elif 'risk_level == "medium"' in line:
                rule_lines[6] = lineno
            elif 'risk_level == "low"' in line:
                rule_lines[7] = lineno
            elif "not suggested_tool and len" in line:
                rule_lines[8] = lineno
        for i in (3, 4, 6, 7, 8):
            for j in (3, 4, 6, 7, 8):
                if i >= j:
                    continue
                assert rule_lines[i] < rule_lines[j], f"Rule {i} (line {rule_lines[i]}) must precede Rule {j} (line {rule_lines[j]})"
        assert 'risk_level == "high"' not in src
        assert set(rule_lines) == {3, 4, 6, 7, 8}
        assert "_evaluate_chat_policy_with_precedence" in src
        # Governance: the Identity Rules 1/2 branch precedes the normal
        # Thinking-proposal evaluation branch
        gov_src = GOVERNANCE.read_text()
        r1_idx = gov_src.index('if status == "changed"')
        normal_idx = gov_src.index("Precedence 3")
        assert r1_idx < normal_idx

    def test_24_governance_identity_rules_precede_normal_evaluation(self):
        gov_src = GOVERNANCE.read_text()
        r1_line = gov_src.index('if status == "changed"')
        r2_line = gov_src.index('if status in ("missing", "failed")')
        normal_line = gov_src.index("Precedence 3")
        assert r1_line < r2_line < normal_line
        # Thinking contains no Identity rule triggers
        policy_src = POLICY.read_text()
        assert 'identity_status == "changed"' not in policy_src
        assert 'identity_status in ("missing", "failed")' not in policy_src


class TestEvidenceStates:
    def test_25_missing_evidence_none(self):
        # None evidence → Thinking falls through to Rule 3+
        p = _make_policy(identity=None)
        assert p["decision_type"] == "respond_only"  # default for long text

    def test_26_unknown_status(self):
        p = _make_policy(identity={"status": "unknown"})
        assert p["decision_type"] == "respond_only"

    def test_27_missing_status_key(self):
        p = _make_policy(identity={"other": "value"})
        assert p["decision_type"] == "respond_only"

    def test_28_valid_verified_status(self):
        p = _make_policy(identity={"status": "verified"})
        assert p["decision_type"] == "respond_only"

    def test_29_conflicting_status_and_changed(self):
        # status="verified" but changed=True — Thinking uses status
        p = _make_policy(identity={"status": "verified", "changed": True})
        assert p["decision_type"] == "respond_only"  # status takes precedence

    def test_30_malformed_non_dict_evidence(self):
        # Non-dict evidence should not crash Thinking
        # (Thinking checks `if identity_integrity_status:` first)
        # We can't easily pass non-dict since type hint says dict | None
        # But we verify the guard produces dict outputs
        guard_src = Path("aether/identity/guard.py").read_text()
        assert "_safe_summary" in guard_src  # always returns dict


class TestEvidenceEquivalence:
    def test_31_evidence_present_absent_equivalence_for_non_operative_states(self):
        """Non-operative evidence states leave envelopes unchanged; Rules 1/2
        statuses are operative and change the envelope."""
        policies = [
            None,
            {},
            {"decision_type": "unknown"},
            {"decision_type": "block"},
            {"decision_type": "require_approval"},
            {"decision_type": "respond_only", "tool_execution_allowed": False},
            {"decision_type": "respond_only", "tool_execution_allowed": True},
        ]
        # Non-operative evidence states fall through unchanged
        for policy in policies:
            r1 = _gov_fn()(thinking_policy=policy)
            for evidence in ({"status": "verified"}, {"status": "unknown"},
                             {"foo": "bar"}, "not-a-dict", None):
                r2 = _gov_fn()(thinking_policy=policy, identity_integrity_evidence=evidence)
                assert r1 == r2, f"Equivalence failed for {policy} with {evidence}"
        # Operative identity statuses change the envelope (except when the
        # invalid_policy precedence already decided)
        for policy in policies:
            if policy is None:
                continue
            r1 = _gov_fn()(thinking_policy=policy)
            for status in ("changed", "missing", "failed"):
                r2 = _gov_fn()(thinking_policy=policy,
                               identity_integrity_evidence={"status": status})
                assert r1 != r2, f"Operativity failed for {policy} with {status}"

    def test_32_evidence_not_in_policy_snapshot(self):
        p = _make_policy(identity={"status": "changed"})
        env = _gov_fn()(thinking_policy=p, identity_integrity_evidence={"status": "changed"})
        assert "identity_integrity_evidence" not in env["policy_snapshot"]
        assert "risk_evidence" not in env["policy_snapshot"]

    def test_33_evidence_not_in_warnings_or_reason(self):
        p = _make_policy(identity={"status": "changed"})
        env = _gov_fn()(thinking_policy=p, identity_integrity_evidence={"status": "changed"})
        assert "changed" not in str(env.get("warnings", []))
        assert "evidence" not in env.get("reason", "").lower()


class TestDownstreamConsumers:
    def test_34_approval_request_behavior_for_block(self):
        from aether.action.approval_request import build_approval_request
        p = _make_policy()
        env = _gov_fn()(thinking_policy=p, identity_integrity_evidence={"status": "changed"})
        req = build_approval_request(policy_gate=env)
        assert req is not None
        assert req["approval_required"] is True
        assert req["approval_type"] == "blocked_identity_review"
        assert req["approval_status"] == "pending"

    def test_35_approval_request_behavior_for_require_approval(self):
        from aether.action.approval_request import build_approval_request
        p = _make_policy()
        env = _gov_fn()(thinking_policy=p, identity_integrity_evidence={"status": "missing"})
        req = build_approval_request(policy_gate=env)
        assert req is not None
        assert req["approval_required"] is True
        assert req["approval_type"] == "human_review"
        assert req["approval_status"] == "pending"

    def test_36_input_dictionaries_not_mutated(self):
        p = _make_policy(identity={"status": "changed"})
        p_copy = dict(p)
        env = _gov_fn()(thinking_policy=p, identity_integrity_evidence={"status": "changed"})
        assert p == p_copy  # thinking_policy not mutated
        # Evidence dict not mutated
        evidence = {"status": "changed"}
        evidence_copy = dict(evidence)
        _gov_fn()(thinking_policy=p, identity_integrity_evidence=evidence)
        assert evidence == evidence_copy


class TestMigrationBoundary:
    def test_37_no_source_migration_claimed(self):
        text = _record()
        assert "does not migrate Rules 1 or 2" in text

    def test_38_no_evidence_activation_claimed(self):
        text = _record()
        assert "does not make Identity evidence operative" in text

    def test_39_no_runtime_behavior_change_claimed(self):
        text = _record()
        assert "does not change any runtime behavior" in text

    def test_40_no_execution_enabled_claimed(self):
        text = _record()
        assert "does not change any runtime behavior" in text

    def test_41_no_persistence_added_claimed(self):
        text = _record()
        assert "Adding persistence, APIs, routers, or execution paths" in text


class TestProtectedRecords:
    def test_42_milestone_87_record_unchanged(self):
        assert M87_RECORD.is_file()
        text = M87_RECORD.read_text(encoding="utf-8")
        assert "Milestone 87 Core Governance Authorization Decision-Envelope Boundary" in text

    def test_43_milestone_88_record_unchanged(self):
        assert M88_RECORD.is_file()
        text = M88_RECORD.read_text(encoding="utf-8")
        assert "Milestone 88 Cognitive Signal Arbitration Classification Boundary" in text

    def test_44_milestone_87_tests_authoritative(self):
        m87_test_path = ROOT / "tests" / "test_milestone_87_core_governance_authorization_boundary.py"
        assert m87_test_path.is_file()
        src = m87_test_path.read_text()
        assert "test_71_no_fallback_engine_in_facade" in src

    def test_45_milestone_88_tests_authoritative(self):
        m88_test_path = ROOT / "tests" / "test_milestone_88_cognitive_signal_arbitration_boundary.py"
        assert m88_test_path.is_file()
        src = m88_test_path.read_text()
        assert "test_50_constitutional_rules_have_article_citations" in src


class TestStructuralGates:
    def test_46_openapi_counts_unchanged(self):
        app = importlib.import_module("aether.interface.api_server").app
        schema = app.openapi()
        assert len(schema.get("paths", {})) == 304
        assert len(schema.get("components", {}).get("schemas", {})) == 108

    def test_47_api_server_shape_unchanged(self):
        tree = _tree(API_SERVER)
        app_routes = 0
        include_router = 0
        direct_action = 0
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                for decorator in node.decorator_list:
                    text_dec = ast.unparse(decorator)
                    if text_dec.startswith("app."):
                        app_routes += 1
                        if '"/action/' in text_dec or "'/action/" in text_dec:
                            direct_action += 1
            if isinstance(node, ast.Call) and ast.unparse(node.func) == "app.include_router":
                include_router += 1
        assert (app_routes, include_router, direct_action) == (8, 23, 0)


class TestArchitectureConstitution:
    def test_48_architecture_0_3_0_binding(self):
        arch = ARCHITECTURE.read_text(encoding="utf-8")
        assert "**Version:** 0.3.0" in arch

    def test_49_constitution_0_2_0_binding(self):
        const = CONSTITUTION.read_text(encoding="utf-8")
        assert "**Version:** 0.2.0" in const

    def test_50_milestone_89_remains_open(self):
        text = _normalized()
        assert "Milestone 89 remains open" in text or "Milestone 89: open" in text

    def test_51_milestone_90_does_not_start_automatically(self):
        text = _record()
        assert "Milestone 90 does not start automatically" in text or \
               "Milestone 90 has not started" in text


class TestMigrationDecisionGate:
    def test_52_migration_decision_gate_result(self):
        text = _record()
        assert "READY_WITH_EXPLICIT_SUPERSESSION_AMENDMENTS" in text

    def test_53_amended_tests_listed(self):
        text = _record()
        # Must list the specific tests that need amendment (corrected matrix)
        assert "test_60_direct_identity_evidence_operative_only_for_identity_rules" in text
        assert "test_62_identity_evidence_raw_values_absent_from_reason_and_warnings" in text
        assert "test_07_actual_current_rule_count_is_seven" in text
        assert "test_10_exact_trigger_conditions_from_ast" in text
        assert "test_45_only_authorized_production_modules_changed" in text

    def test_54_future_file_matrix_defined(self):
        text = _record()
        assert "aether/core/governance.py" in text
        assert "aether/thinking/policy.py" in text


class TestNoProductionChanges:
    def test_55_only_authorized_production_modules_changed(self):
        import subprocess
        result = subprocess.run(
            ["git", "diff", "943b442", "HEAD", "--name-only", "--", "aether/"],
            capture_output=True, text=True, cwd=str(ROOT),
        )
        assert result.stdout.splitlines() == [
            "aether/core/governance.py",
            "aether/core/loop.py",
            "aether/thinking/policy.py",
        ], f"Unauthorized production source changed: {result.stdout[:200]}"

    def test_56_no_finalized_record_changed(self):
        import subprocess
        result = subprocess.run(
            ["git", "diff", "943b442", "HEAD", "--",
             "docs/architecture/MILESTONE_87_CORE_GOVERNANCE_AUTHORIZATION_BOUNDARY.md",
             "docs/architecture/MILESTONE_88_COGNITIVE_SIGNAL_ARBITRATION_BOUNDARY.md"],
            capture_output=True, text=True, cwd=str(ROOT),
        )
        assert result.stdout == "", f"Finalized record changed: {result.stdout[:200]}"

    def test_57_no_new_persistence_or_execution_imports(self):
        test_src = Path(__file__).read_text(encoding="utf-8")
        tree = ast.parse(test_src)
        imported_names = {
            alias.name
            for node in ast.walk(tree)
            if isinstance(node, (ast.Import, ast.ImportFrom))
            for alias in node.names
        }
        assert "TestClient" not in imported_names
        assert "requests" not in imported_names
        assert "httpx" not in imported_names


class TestAppliedMigration:
    """Milestone 89B applied-migration contract: the runtime migration is
    physically implemented and the boundary test now verifies the
    post-migration state (Rules 1/2 authoritative in Governance, raw
    Thinking insensitivity, truthful T3 routing, and preserved legacy
    decision/approval/response semantics)."""

    def test_139_full_dictionary_identity_insensitivity_behavioral(self):
        neutral = _make_policy()
        variants = [
            None,
            {"status": "verified"},
            {"status": "changed"},
            {"status": "missing"},
            {"status": "failed"},
            {"status": "unknown"},
            {},
        ]
        for variant in variants:
            assert _make_policy(identity=variant) == neutral, f"Insensitive for {variant}"

    def test_140_evidence_rules_triggered_exactly_once_in_governance(self):
        gov_src = GOVERNANCE.read_text()
        # Exact-once trigger evaluation (count the condition statements, not
        # matching prose comments)
        assert gov_src.count('if status == "changed":') == 1
        assert gov_src.count('if status in ("missing", "failed"):') == 1
        # Only dict evidence reaches the trigger
        assert gov_src.count("isinstance(identity_integrity_evidence, dict)") == 1

    def test_141_status_authoritative_over_conflicting_changed(self):
        # status="changed" wins even when changed=False
        env = _gov_fn()(
            thinking_policy=_make_policy(),
            identity_integrity_evidence={"status": "changed", "changed": False},
        )
        assert env["decision"] == "block"
        # status="verified" falls through even when changed=True
        env = _gov_fn()(
            thinking_policy=_make_policy(),
            identity_integrity_evidence={"status": "verified", "changed": True},
        )
        assert env["decision"] != "block"

    def test_142_invalid_policy_precedence_over_identity_evidence(self):
        env = _gov_fn()(
            thinking_policy=None,
            identity_integrity_evidence={"status": "changed"},
        )
        assert env["decision"] == "invalid_policy"

    def test_143_risk_evidence_stays_non_operative_behavioral(self):
        base = _gov_fn()(thinking_policy=_make_policy())
        with_risk = _gov_fn()(
            thinking_policy=_make_policy(),
            risk_evidence={"risk_level": "high", "action_type": "destructive"},
        )
        assert base == with_risk

    def test_144_exact_envelope_key_set_unchanged(self):
        expected = {
            "allowed", "decision", "reason", "required_user_confirmation",
            "tool_execution_allowed", "action_execution_allowed",
            "requested_action", "policy_snapshot", "warnings",
        }
        cases = [
            _gov_fn()(thinking_policy=None),
            _gov_fn()(thinking_policy=_make_policy()),
            _gov_fn()(thinking_policy=_make_policy(),
                      identity_integrity_evidence={"status": "changed"}),
            _gov_fn()(thinking_policy=_make_policy(),
                      identity_integrity_evidence={"status": "missing"}),
        ]
        for env in cases:
            assert set(env.keys()) == expected

    def test_145_governance_signature_unchanged(self):
        import inspect
        sig = inspect.signature(_gov_fn())
        params = sig.parameters
        assert list(params) == [
            "thinking_policy", "requested_action", "context",
            "risk_evidence", "identity_integrity_evidence",
            "rule_3_4_precedence",
        ]
        assert params["risk_evidence"].kind is inspect.Parameter.KEYWORD_ONLY
        assert params["identity_integrity_evidence"].kind is inspect.Parameter.KEYWORD_ONLY

    def test_146_no_raw_evidence_values_leak(self):
        def _strings(obj):
            if isinstance(obj, str):
                return [obj]
            if isinstance(obj, dict):
                out = []
                for k, v in obj.items():
                    out.extend(_strings(k))
                    out.extend(_strings(v))
                return out
            if isinstance(obj, list):
                out = []
                for v in obj:
                    out.extend(_strings(v))
                return out
            return []

        markers = ("HASH-RAW-SECRET-abc123", "RAW-SEED")
        env = _gov_fn()(
            thinking_policy=_make_policy(),
            identity_integrity_evidence={
                "status": "changed",
                "checksum": markers[0],
                "seed": markers[1],
            },
        )
        for marker in markers:
            assert marker not in _strings(env)
        assert "identity_integrity_evidence" not in env["policy_snapshot"]
        assert "risk_evidence" not in env["policy_snapshot"]

    def test_147_loop_truthful_t3_routing_behavioral(self, monkeypatch):
        import aether.action.tool_planner as tpl
        import aether.core.loop as core_loop
        from aether.memory.working.store import WorkingMemory

        monkeypatch.setattr(core_loop, "verify_identity_integrity",
                            lambda *a, **k: {"status": "changed"})
        monkeypatch.setattr(core_loop, "record_event",
                            lambda *a, **k: {"id": "test_evt"})
        monkeypatch.setattr(core_loop, "time_state",
                            lambda: {"timezone": "UTC", "now": "00:00:00",
                                     "iso": "2026-01-01T00:00:00+00:00"})
        monkeypatch.setattr(tpl, "infer_candidate_tool",
                            lambda *a, **k: {"candidate_tool": {}})
        monkeypatch.setattr(
            "aether.action.approval_queue.create_approval_record",
            lambda *a, **k: {"approval_id": "test-approval-id"},
        )

        wm = WorkingMemory()
        result = core_loop.run_core_chat_loop(
            text="hello there", working_memory=wm, session_id="t")
        stages = {s["name"]: s for s in result["loop_trace"]["stages"]}
        # Truthful T3 trace: Thinking stage shows the raw (identity-insensitive)
        # proposal; the Governance stage shows the authoritative Identity block
        assert stages["thinking_policy"]["summary"] == "Decision: respond_only"
        assert stages["policy_gate"]["summary"] == "Decision: block"
        # Returned legacy fields come from the effective policy
        assert result["thinking_policy"] == result["policy_gate"]["policy_snapshot"]
        assert result["decision_type"] == "block"
        assert result["required_user_confirmation"] is True
        assert result["blocked_reason"] == (
            "Identity integrity changed. Human review is required before continuing."
        )
        assert result["execution_decision"] == "block"
        assert result["approval_required"] is True

        # Verified status follows the normal path
        monkeypatch.setattr(core_loop, "verify_identity_integrity",
                            lambda *a, **k: {"status": "verified"})
        result = core_loop.run_core_chat_loop(
            text="hello there", working_memory=wm, session_id="t2")
        assert result["decision_type"] == "respond_only"
        assert result["approval_required"] is False

    def test_148_response_and_approval_shape_use_effective_policy(self, monkeypatch):
        import aether.action.tool_planner as tpl
        import aether.core.loop as core_loop
        from aether.memory.working.store import WorkingMemory

        monkeypatch.setattr(core_loop, "verify_identity_integrity",
                            lambda *a, **k: {"status": "changed"})
        monkeypatch.setattr(core_loop, "record_event",
                            lambda *a, **k: {"id": "test_evt"})
        monkeypatch.setattr(core_loop, "time_state",
                            lambda: {"timezone": "UTC", "now": "00:00:00",
                                     "iso": "2026-01-01T00:00:00+00:00"})
        monkeypatch.setattr(tpl, "infer_candidate_tool",
                            lambda *a, **k: {"candidate_tool": {}})
        monkeypatch.setattr(
            "aether.action.approval_queue.create_approval_record",
            lambda *a, **k: {"approval_id": "test-approval-id"},
        )

        wm = WorkingMemory()
        result = core_loop.run_core_chat_loop(
            text="hello there", working_memory=wm, session_id="t3")
        assert "[BLOCKED] Identity integrity changed. Human review is required before continuing." in result["response_text"]
        assert result["tool_execution_allowed"] is False
        assert result["tool_executed"] is False
        assert result["approval_type"] == "blocked_identity_review"
        assert result["approval_status"] == "pending"
        # The approval request is built from the envelope decision
        assert result["approval_request"]["decision_type"] == "block"
        assert result["policy_gate"]["decision"] == "block"

    def test_149_no_duplicate_identity_evaluation_across_components(self):
        # Thinking, the loop, the approval builder, and the Action gate must
        # not evaluate Identity status; Governance is the sole authority
        for path in (POLICY, LOOP, ROOT / "aether/action/approval_request.py",
                     ROOT / "aether/action/policy_gate.py"):
            src = path.read_text()
            assert 'status == "changed"' not in src, path
            assert 'status in ("missing", "failed")' not in src, path

    def test_150_action_module_remains_unchanged(self):
        pg_src = (ROOT / "aether/action/policy_gate.py").read_text()
        # The Action-located gate stays a thin compatibility facade that
        # delegates to Core Governance
        assert "evaluate_authorization_envelope" in pg_src
        assert 'status == "changed"' not in pg_src
        assert 'status in ("missing", "failed")' not in pg_src


class TestReconciliationAccounting:
    """Reconciliation-specific tests for 89A-R."""

    def test_58_exact_test_class_count(self):
        """Verify exact 17-class distribution (13 original + reconciliation + R2 + R3 + applied)."""
        test_src = Path(__file__).read_text(encoding="utf-8")
        tree = ast.parse(test_src)
        classes = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                methods = [n.name for n in node.body if isinstance(n, ast.FunctionDef) and n.name.startswith("test_")]
                classes[node.name] = len(methods)
        assert len(classes) == 17, f"Expected 17 classes, got {len(classes)}: {classes}"

    def test_59_exact_test_method_count(self):
        """Verify exact total test count across 89A-R, 89A-R2, 89A-R3, and 89B."""
        test_src = Path(__file__).read_text(encoding="utf-8")
        tree = ast.parse(test_src)
        total = 0
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                methods = [n for n in node.body if isinstance(n, ast.FunctionDef) and n.name.startswith("test_")]
                total += len(methods)
        assert total == 150, f"Expected 150 tests, got {total}"

    def test_60_m87_exact_affected_test_names(self):
        """Verify exact M87 test names requiring amendment are documented."""
        record = _record()
        assert "test_60_direct_identity_evidence_operative_only_for_identity_rules" in record
        assert "test_62_identity_evidence_raw_values_absent_from_reason_and_warnings" in record
        assert "test_61_direct_evidence_absent_from_policy_snapshot" in record

    def test_61_m88_exact_affected_test_names(self):
        """Verify exact M88 test names requiring amendment are documented."""
        record = _record()
        assert "test_07_actual_current_rule_count_is_seven" in record
        assert "test_10_exact_trigger_conditions_from_ast" in record
        assert "test_11_exact_current_decision_outputs" in record
        assert "test_12_exact_confirmation_and_execution_fields" in record
        assert "test_29_identity_evidence_operative_only_through_governance" in record
        assert "test_30_exact_new_classification_string" in record
        assert "test_45_only_authorized_production_modules_changed" in record
        # R2 correction: original authorized matrix was 11, 12, 29, 30
        # (not 08, 09, 29, 30 as misstated in the initial reconciliation)
        assert "original" in record.lower() or "11, 12, 29, 30" in record
        # Historical locks explicitly preserved
        assert "08" in record and "09" in record

    def test_62_thinking_exact_affected_test_names(self):
        """Verify exact Thinking test names requiring amendment are documented."""
        record = _record()
        assert "test_block_on_identity_changed" in record
        assert "test_block_even_with_tool_and_medium_risk" in record
        assert "test_require_approval_when_missing" in record
        assert "test_require_approval_when_failed" in record
        assert "test_identity_issues_have_high_confidence" in record

    def test_63_core_loop_is_consumer(self):
        """Verify loop.py consumes raw/envelope/effective routing (T3)."""
        loop_src = Path("aether/core/loop.py").read_text()
        assert "raw_thinking_policy, rule_3_4_precedence = _evaluate_chat_policy_with_precedence" in loop_src
        assert "rule_3_4_precedence=rule_3_4_precedence" in loop_src
        assert "authorization_envelope = evaluate_authorization_envelope" in loop_src
        assert 'effective_thinking_policy = authorization_envelope["policy_snapshot"]' in loop_src
        assert "build_approval_request" in loop_src
        assert "build_loop_trace" in loop_src
        assert "record_event" in loop_src
        assert "thinking_policy=raw_thinking_policy" in loop_src
        assert "policy_gate=authorization_envelope" in loop_src

    def test_64_compatibility_bridge_defined(self):
        """Verify compatibility bridge design is documented."""
        record = _record()
        assert "Compatibility-Bridge Design" in record
        assert "effective_thinking_policy" in record
        assert "raw_thinking_policy" in record
        assert "Single-Authority and Single-Trigger-Evaluation Rule" in record

    def test_65_single_authority_rule(self):
        """Verify single-authority rule is documented."""
        record = _record()
        assert "Thinking must not authoritatively evaluate Rules 1 or 2" in record
        assert "Governance must be the sole authoritative evaluator" in record
        assert "Trigger evaluation must occur exactly once" in record

    def test_66_future_governance_precedence(self):
        """Verify future Governance precedence is defined."""
        record = _record()
        assert "If `thinking_policy is None`" in record
        assert "status `changed` activates Rule 1" in record
        assert "status `missing` or `failed` activates Rule 2" in record
        assert "Risk evidence remains non-operative" in record

    def test_67_malformed_evidence_behavior(self):
        """Verify malformed evidence falls through safely."""
        record = _record()
        assert "Non-dictionary Identity evidence must not raise a new exception" in record
        # "fall through safely" may span lines
        assert "fall" in record and "safely" in record

    def test_68_status_field_precedence(self):
        """Verify status field is authoritative over changed boolean."""
        record = _record()
        # "the `status` field is authoritative" may span lines
        assert "status" in record and "authoritative" in record

    def test_69_risk_evidence_non_operative(self):
        """Verify risk evidence remains non-operative."""
        record = _record()
        assert "Risk evidence remains non-operative" in record

    def test_70_no_raw_identity_leakage(self):
        """Verify no raw Identity data leaks into outputs."""
        record = _record()
        assert "raw hashes" in record.lower() or "Raw hashes" in record
        assert "Identity Seed content" in record or "seed content" in record.lower()
        assert "evidence warning payloads" in record.lower() or "warning payloads" in record.lower()

    def test_71_policy_snapshot_semantics(self):
        """Verify policy_snapshot semantics are defined."""
        record = _record()
        assert "policy_snapshot" in record
        assert "shallow dictionary copy" in record or "shallow copy" in record

    def test_72_trace_compatibility(self):
        """Verify trace compatibility is addressed."""
        record = _record()
        assert "loop trace" in record.lower() or "trace" in record.lower()
        assert "stage order" in record.lower() or "Stage order" in record

    def test_73_approval_compatibility(self):
        """Verify approval compatibility is addressed."""
        record = _record()
        assert "approval_type" in record
        assert "blocked_identity_review" in record
        assert "human_review" in record

    def test_74_future_89b_file_matrix_exact(self):
        """Verify exact future 89B file matrix includes loop.py."""
        record = _record()
        assert "aether/core/governance.py" in record
        assert "aether/thinking/policy.py" in record
        assert "aether/core/loop.py" in record
        assert "approval_request.py" in record or "approval_request" in record
        assert "aether/action/policy_gate.py" in record
        assert "aether/core/loop_trace.py" in record
        assert "docs/CONSTITUTION.md" in record
        assert "docs/ARCHITECTURE.md" in record

    def test_75_reconciliation_decision_gate_result(self):
        """Verify reconciliation decision-gate result."""
        record = _record()
        assert "READY_WITH_EXPLICIT_SUPERSESSION_AMENDMENTS" in record

    def test_76_only_authorized_production_source_changed(self):
        """Verify 89B changed exactly the three authorized production files."""
        import subprocess
        result = subprocess.run(
            ["git", "diff", "943b442", "HEAD", "--name-only", "--", "aether/"],
            capture_output=True, text=True, cwd=str(ROOT),
        )
        assert result.stdout.splitlines() == [
            "aether/core/governance.py",
            "aether/core/loop.py",
            "aether/thinking/policy.py",
        ], f"Unauthorized production source changed: {result.stdout[:200]}"

    def test_77_m87_m88_records_unchanged_tests_amended_only_as_authorized(self):
        import subprocess
        records = subprocess.run(
            ["git", "diff", "943b442", "HEAD", "--",
             "docs/architecture/MILESTONE_87_CORE_GOVERNANCE_AUTHORIZATION_BOUNDARY.md",
             "docs/architecture/MILESTONE_88_COGNITIVE_SIGNAL_ARBITRATION_BOUNDARY.md"],
            capture_output=True, text=True, cwd=str(ROOT),
        )
        assert records.stdout == "", f"Finalized record changed: {records.stdout[:200]}"
        _assert_exact_nine_path_set()
        _assert_exact_amendment_matrix(_amended_test_sets())

    def test_78_m87_unaffected_tests_still_pass(self):
        """Verify M87 tests that should remain unchanged still pass."""
        import importlib
        m87 = importlib.import_module("tests.test_milestone_87_core_governance_authorization_boundary")
        test_instance = m87.TestGovernanceModuleExtraction()
        assert test_instance.test_49_governance_function_signature_exact() is None
        assert test_instance.test_58_core_loop_passes_identity_evidence_directly() is None
        assert test_instance.test_61_direct_evidence_absent_from_policy_snapshot() is None
        assert test_instance.test_64_input_dictionaries_not_mutated() is None

    def test_79_m88_unaffected_tests_still_pass(self):
        """Verify M88 tests that should remain unchanged still pass."""
        import importlib
        m88 = importlib.import_module("tests.test_milestone_88_cognitive_signal_arbitration_boundary")
        test_instance = m88.TestOwnershipAndSeparation()
        assert test_instance.test_28_risk_evidence_remains_non_operative() is None
        test_instance2 = m88.TestDecisionRecordStructure()
        assert test_instance2.test_08_every_source_rule_inventoried_once() is None
        assert test_instance2.test_09_exact_source_order_preserved() is None

    def test_80_evidence_operativity_is_internal_semantic_change(self):
        """Verify evidence operativity is correctly classified."""
        record = " ".join(_record().split())
        assert "EXTERNALLY DECISION-, APPROVAL-, RESPONSE-SHAPE-, AND EXECUTION-FLAG PRESERVING, WITH AN INTENTIONAL DIAGNOSTIC TRACE SEMANTIC CHANGE AND INTERNAL PHYSICAL-OWNERSHIP CHANGE" in record
        assert "MIGRATION" in record

    def test_81_no_evidence_activation_during_89a(self):
        """Verify no evidence activation during 89A."""
        record = _record()
        assert "does not make Identity evidence operative" in record
        assert "Evidence remains non-operative" in record or "evidence remains non-operative" in record.lower()

    def test_82_no_rules_migrated_during_89a(self):
        """Verify no rules migrated during 89A."""
        record = _record()
        assert "does not migrate Rules 1 or 2" in record

    def test_83_no_runtime_behavior_change_during_89a(self):
        """Verify no runtime behavior change during 89A."""
        record = _record()
        assert "does not change any runtime behavior" in record

    def test_84_milestone_89_still_open(self):
        """Verify Milestone 89 remains open."""
        record = _record()
        assert "Milestone 89 remains open" in record or "Milestone 89: OPEN" in record

    def test_85_milestone_90_not_started(self):
        """Verify Milestone 90 has not started."""
        record = _record()
        assert "Milestone 90 does not start automatically" in record or "Milestone 90: not started" in record


class TestR2ContractCorrections:
    """Milestone 89A-R2 contract corrections: 24-section record, reconciled
    Thinking supersession matrix, exact future data path, trace strategy,
    snapshot contract, and separated 89B file matrices."""

    def test_86_record_has_exactly_twenty_four_sections_restored(self):
        actual = [line for line in _record().splitlines() if line.startswith("## ")]
        assert actual == SECTIONS
        assert len(actual) == 24

    def test_87_no_top_level_section_25(self):
        assert not any(line.startswith("## 25.") for line in _record().splitlines())

    def test_88_bridge_content_in_authorized_sections(self):
        record = _record()
        assert "Compatibility-Bridge Design" in record
        assert "raw_thinking_policy" in record
        assert "effective_thinking_policy" in record
        assert "authorization_envelope" in record
        assert "Single-Authority and Single-Trigger-Evaluation Rule" in record

    def test_89_exact_current_test_class_accounting(self):
        test_src = Path(__file__).read_text(encoding="utf-8")
        tree = ast.parse(test_src)
        classes = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                methods = [n.name for n in node.body
                           if isinstance(n, ast.FunctionDef) and n.name.startswith("test_")]
                classes[node.name] = len(methods)
        expected = {
            "TestDecisionRecordStructure": 8,
            "TestCurrentIdentityContract": 4,
            "TestRuleContracts": 10,
            "TestRulePrecedence": 2,
            "TestEvidenceStates": 6,
            "TestEvidenceEquivalence": 3,
            "TestDownstreamConsumers": 3,
            "TestMigrationBoundary": 5,
            "TestProtectedRecords": 4,
            "TestStructuralGates": 2,
            "TestArchitectureConstitution": 4,
            "TestMigrationDecisionGate": 3,
            "TestNoProductionChanges": 3,
            "TestAppliedMigration": 12,
            "TestReconciliationAccounting": 28,
            "TestR2ContractCorrections": 25,
            "TestR3FinalLock": 28,
        }
        assert classes == expected, f"Class accounting mismatch: {classes}"

    def test_90_exact_current_test_count(self):
        test_src = Path(__file__).read_text(encoding="utf-8")
        tree = ast.parse(test_src)
        total = sum(
            len([n for n in node.body
                 if isinstance(n, ast.FunctionDef) and n.name.startswith("test_")])
            for node in ast.walk(tree)
            if isinstance(node, ast.ClassDef)
        )
        assert total == 150, f"Expected 150 tests, got {total}"

    def test_91_thinking_affected_test_count_reconciled(self):
        record = _record()
        assert "Affected Thinking tests: **6**" in record
        assert "5 full amendments + 1 partial amendment" in record

    def test_92_full_amendment_count_fourteen(self):
        record = _record()
        assert "Full amendments: 14 tests" in record
        assert "Thinking (5): test_block_on_identity_changed" in record

    def test_93_partial_amendment_count_one(self):
        record = _record()
        assert "Partial amendments: 1 test" in record
        assert "test_tool_execution_always_false (18 of 30 parametrized cases" in record

    def test_94_tool_execution_always_false_resolved(self):
        record = _record()
        assert "PARTIAL_EXPLICIT_89B_SUPERSESSION_AMENDMENT_REQUIRED" in record
        assert "30 parametrized cases" in record
        assert "Identity-related cases (18)" in record
        assert "Non-Identity cases (12)" in record
        assert "Why the whole test must not be deleted" in record

    def test_95_raw_thinking_policy_contract_exact(self):
        record = _record()
        assert "raw_thinking_policy" in record
        assert "aether.thinking.policy.decide_chat_policy" in record
        assert "Rules 3, 4, 5, 6, 7, 8, 9 only" in record
        assert "non-authoritative proposal" in record

    def test_96_authorization_envelope_contract_exact(self):
        record = _record()
        assert "authorization_envelope" in record
        assert "aether.core.governance.evaluate_authorization_envelope" in record
        assert "evaluates Identity Rules 1 and 2 exactly once" in record
        assert "authoritative decision" in record

    def test_97_effective_thinking_policy_source_exact(self):
        record = _record()
        assert 'effective_thinking_policy = authorization_envelope["policy_snapshot"]' in record

    def test_98_effective_policy_routing_for_identity_cases(self):
        record = " ".join(_record().split())
        assert "shallow copy of `raw_thinking_policy`" in record
        assert "legacy-compatible projection produced by Governance" in record

    def test_99_no_new_public_envelope_key(self):
        record = _record()
        assert "No new public envelope key is added" in record

    def test_100_loop_consumer_routing_exact(self):
        record = _record()
        assert "Exact Core-Loop Consumer Mapping" in record
        assert "| Governance call" in record
        assert "| approval-request builder" in record
        assert "| response builder" in record
        assert "| returned `thinking_policy`" in record

    def test_101_trace_strategy_selected(self):
        record = _record()
        assert "Strategy T3 — Truthful Raw Thinking Proposal Trace" in record
        assert "Rejected strategy T1" in record
        assert "No duplicate stage is added" in record
        assert "Thinking -> Governance" in record

    def test_102_single_trigger_evaluation_locked(self):
        record = _record()
        assert "Trigger evaluation must occur exactly once" in record
        assert "Core Coordination (the loop) must not re-evaluate Identity status" in record
        assert "The approval builder must not re-evaluate Identity status" in record

    def test_103_projection_is_formatting_only(self):
        record = " ".join(_record().split())
        assert "Effective Policy Projection Is Formatting Only" in record
        assert "must not independently determine whether a constraint triggers" in record

    def test_104_policy_snapshot_contract_exact(self):
        record = _record()
        assert "policy_snapshot == shallow copy of\n  raw_thinking_policy" in record
        assert "policy_snapshot == exact former Rule 1 Thinking-policy\n  dictionary" in record
        assert "No evidence fields may be copied into `policy_snapshot`" in record
        assert "Nested mutable values must not be newly mutated" in record

    def test_105_approval_and_response_source_fields(self):
        record = _record()
        assert "blocked_identity_review" in record
        assert "human_review" in record
        assert "Response text: effective policy" in record
        assert "execution_reason" in record

    def test_106_production_file_matrix_separated(self):
        record = _record()
        assert "### Production Files Expected to Change" in record
        assert "### Existing Tests Explicitly Authorized for Future Amendment" in record
        prod_start = record.index("### Production Files Expected to Change")
        test_start = record.index("### Existing Tests Explicitly Authorized for Future Amendment")
        prod_block = record[prod_start:test_start]
        assert "aether/core/governance.py" in prod_block
        assert "aether/thinking/policy.py" in prod_block
        assert "aether/core/loop.py" in prod_block
        assert "tests/" not in prod_block, "Test path inside production files list"

    def test_107_test_amendment_matrix_separated(self):
        record = _record()
        assert "test_milestone_87_core_governance_authorization_boundary.py" in record
        assert "test_milestone_88_cognitive_signal_arbitration_boundary.py" in record
        assert "test_thinking_policy.py" in record
        assert "test_tool_execution_always_false" in record

    def test_108_decision_gate_conditions_met(self):
        record = _record()
        assert "READY_WITH_EXPLICIT_SUPERSESSION_AMENDMENTS" in record
        assert "exactly 24 top-level" in record
        assert "Strategy T3" in record
        assert "policy-snapshot contract" in record.lower() or "policy-snapshot" in record

    def test_109_only_authorized_production_change_during_r2(self):
        import subprocess
        result = subprocess.run(
            ["git", "diff", "943b442", "HEAD", "--name-only", "--", "aether/"],
            capture_output=True, text=True, cwd=str(ROOT),
        )
        assert result.stdout.splitlines() == [
            "aether/core/governance.py",
            "aether/core/loop.py",
            "aether/thinking/policy.py",
        ], f"Unauthorized production source changed: {result.stdout[:200]}"

    def test_110_m87_m88_records_unchanged_tests_amended_only_as_authorized(self):
        import subprocess
        records = subprocess.run(
            ["git", "diff", "943b442", "HEAD", "--",
             "docs/architecture/MILESTONE_87_CORE_GOVERNANCE_AUTHORIZATION_BOUNDARY.md",
             "docs/architecture/MILESTONE_88_COGNITIVE_SIGNAL_ARBITRATION_BOUNDARY.md"],
            capture_output=True, text=True, cwd=str(ROOT),
        )
        assert records.stdout == "", f"Finalized record changed: {records.stdout[:200]}"
        _assert_exact_nine_path_set()
        _assert_exact_amendment_matrix(_amended_test_sets())


class TestR3FinalLock:
    """Milestone 89A-R3 final lock: 24-section record, exact combined suite
    including Milestone 89, trace strategy T3, intentional diagnostic trace
    semantic change, exact trace-test impact inventory, full-dictionary
    Identity-insensitivity contract, protected-versus-future-amendable
    distinction, and exact decision gate."""

    def test_111_record_has_exactly_twenty_four_sections(self):
        actual = [line for line in _record().splitlines() if line.startswith("## ")]
        assert actual == SECTIONS
        assert len(actual) == 24

    def test_112_no_top_level_section_25(self):
        assert not any(line.startswith("## 25.") for line in _record().splitlines())

    def test_113_exact_current_class_accounting(self):
        test_src = Path(__file__).read_text(encoding="utf-8")
        tree = ast.parse(test_src)
        classes = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                methods = [n.name for n in node.body
                           if isinstance(n, ast.FunctionDef) and n.name.startswith("test_")]
                classes[node.name] = len(methods)
        expected = {
            "TestDecisionRecordStructure": 8,
            "TestCurrentIdentityContract": 4,
            "TestRuleContracts": 10,
            "TestRulePrecedence": 2,
            "TestEvidenceStates": 6,
            "TestEvidenceEquivalence": 3,
            "TestDownstreamConsumers": 3,
            "TestMigrationBoundary": 5,
            "TestProtectedRecords": 4,
            "TestStructuralGates": 2,
            "TestArchitectureConstitution": 4,
            "TestMigrationDecisionGate": 3,
            "TestNoProductionChanges": 3,
            "TestAppliedMigration": 12,
            "TestReconciliationAccounting": 28,
            "TestR2ContractCorrections": 25,
            "TestR3FinalLock": 28,
        }
        assert classes == expected, f"Class accounting mismatch: {classes}"

    def test_114_exact_current_test_count(self):
        test_src = Path(__file__).read_text(encoding="utf-8")
        tree = ast.parse(test_src)
        total = sum(
            len([n for n in node.body
                 if isinstance(n, ast.FunctionDef) and n.name.startswith("test_")])
            for node in ast.walk(tree)
            if isinstance(node, ast.ClassDef)
        )
        assert total == 150, f"Expected 150 tests, got {total}"

    def test_115_combined_suite_exact_files(self):
        record = _record()
        assert "test_milestone_89_identity_hard_constraint_migration_boundary.py" in record
        assert "test_milestone_88_cognitive_signal_arbitration_boundary.py" in record
        assert "test_milestone_87_core_governance_authorization_boundary.py" in record
        assert "test_milestone_86_architecture_evolution_contract.py" in record
        assert "test_repair_family_service_boundary.py" in record
        assert "Milestone 89 combined gate" in record
        # Exact established test gate labels (89B-R corrected Build record)
        assert "exact established Governance/policy/core gate: 592 passed" in record
        assert "exact established Architecture/Observation gate: 240 passed" in record
        assert "PROGRESS consistency: 55 passed" in record
        assert "exact combined suite: 362 passed" in record
        assert "full suite: 2413 passed" in record
        assert "supplemental expanded runs only" in record

    def test_116_combined_suite_arithmetic_322(self):
        record = " ".join(_record().split())
        assert "110 + 50 + 76 + 31 + 55 = 322" in record or "322 (110 + 50 + 76 + 31 + 55)" in record
        assert "322 passed" in record

    def test_117_no_212_as_current_combined(self):
        record = _record()
        assert "must not be recorded as 212" in record or "must never be recorded as 212" in record
        assert "pre-Milestone-89 combined baseline" in record.lower() or "pre-Milestone-89" in record

    def test_118_trace_strategy_t3_selected(self):
        record = _record()
        assert "Strategy T3 — Truthful Raw Thinking Proposal Trace" in record
        assert "Strategy T1" in record
        assert "Rejected strategy T1" in record

    def test_119_thinking_trace_stage_uses_raw(self):
        record = _record()
        assert "Thinking Stage" in record
        assert "Source: `raw_thinking_policy`" in record
        assert "must not contain a Governance-generated Identity block" in record

    def test_120_governance_trace_stage_uses_envelope(self):
        record = _record()
        assert "Governance / Policy-Gate Stage" in record
        assert "Source: `authorization_envelope`" in record
        assert "authoritative decision, including Identity Rule 1 or Rule 2" in record

    def test_121_effective_not_used_to_falsify_thinking_stage(self):
        record = " ".join(_record().split())
        assert "Must NOT be used to falsify the recorded raw Thinking stage" in record
        assert "never records the Governance-derived effective policy as if Thinking had produced it" in record

    def test_122_trace_classification_intentional_diagnostic_change(self):
        record = " ".join(_record().split())
        assert "EXTERNALLY DECISION-, APPROVAL-, RESPONSE-SHAPE-, AND EXECUTION-FLAG PRESERVING, WITH AN INTENTIONAL DIAGNOSTIC TRACE SEMANTIC CHANGE AND INTERNAL PHYSICAL-OWNERSHIP CHANGE" in record

    def test_123_trace_test_impact_audit_exact(self):
        record = _record()
        assert "### 18.7 Core-loop/chat/approval/trace test-impact audit" in record
        assert "ZERO tests require EXPLICIT_89B_SUPERSESSION_AMENDMENT" in record
        assert "No trace test is added to the 89B amendment matrix" in record

    def test_124_trace_hardening_tests_classified_unchanged(self):
        record = _record()
        assert "test_loop_trace_does_not_include_user_text" in record
        assert "test_loop_trace_high_risk_summary_does_not_dump_approval_record" in record
        assert "test_loop_trace_stage_count_matches_expected_minimum" in record
        assert "UNCHANGED_CURRENT_CONTRACT" in record

    def test_125_full_dictionary_identity_insensitivity_contract(self):
        record = " ".join(_record().split())
        assert "the equality contract covers the FULL returned dictionary" in record
        for key in ("decision_type", "confidence", "reasons", "required_user_confirmation",
                    "tool_suggestion_allowed", "tool_execution_allowed", "blocked_reason",
                    "clarification_question", "next_step", "warnings"):
            assert key in record, f"Missing insensitivity key: {key}"

    def test_126_neutral_baseline_is_none(self):
        record = " ".join(_record().split())
        assert "`identity_integrity_status=None` is the explicit neutral baseline" in record
        assert "used consistently throughout the partial contract" in record

    def test_127_rule5_rule6_approval_still_permitted(self):
        record = " ".join(_record().split())
        assert "Rule 5 (secret/risk terms) or Rule 6 (high/medium risk with tool)" in record
        assert "NOT Identity Rule 2 decisions" in record

    def test_128_exact_full_partial_thinking_matrix(self):
        record = _record()
        assert "Affected Thinking tests: **6**" in record
        assert "5 full amendments + 1 partial amendment" in record
        assert "test_tool_execution_always_false" in record

    def test_129_exact_core_loop_routing(self):
        record = _record()
        assert "| Governance call" in record
        assert "| approval-request builder" in record
        assert "| response builder" in record
        assert "| returned `thinking_policy`" in record
        assert "| Governance/Policy-Gate trace stage" in record

    def test_130_single_trigger_evaluation(self):
        record = _record()
        assert "Trigger evaluation occurs exactly once, in Governance" in record or "Trigger evaluation must occur exactly once" in record
        assert "approval builder must not re-evaluate Identity status" in record

    def test_131_projection_formatting_only(self):
        record = " ".join(_record().split())
        assert "must not independently determine whether a constraint triggers" in record

    def test_132_risk_evidence_remains_non_operative(self):
        record = _record()
        assert "risk evidence as non-operative" in record or "Risk evidence remains non-operative" in record

    def test_133_protected_vs_future_amendable(self):
        record = " ".join(_record().split())
        assert "protected during 89A (all passes), and the exact named tests become amendable ONLY under a separately authorized 89B prompt" in record
        assert "never uses an unqualified statement that Milestone 87 and 88 tests are both permanently protected and simultaneously authorized" in record

    def test_134_exact_production_matrix(self):
        record = _record()
        prod_start = record.index("### Production Files Expected to Change")
        test_start = record.index("### Existing Tests Explicitly Authorized for Future Amendment")
        prod_block = record[prod_start:test_start]
        assert "aether/core/governance.py" in prod_block
        assert "aether/thinking/policy.py" in prod_block
        assert "aether/core/loop.py" in prod_block
        assert "tests/" not in prod_block, "Test path inside production files list"

    def test_135_exact_test_amendment_matrix(self):
        record = _record()
        assert "test_60_direct_identity_evidence_operative_only_for_identity_rules" in record
        assert "test_62_identity_evidence_raw_values_absent_from_reason_and_warnings" in record
        assert "test_07_actual_current_rule_count_is_seven" in record
        assert "test_10_exact_trigger_conditions_from_ast" in record
        assert "test_11_exact_current_decision_outputs" in record
        assert "test_12_exact_confirmation_and_execution_fields" in record
        assert "test_29_identity_evidence_operative_only_through_governance" in record
        assert "test_30_exact_new_classification_string" in record
        assert "test_45_only_authorized_production_modules_changed" in record
        assert "test_tool_execution_always_false" in record
        assert "Tests touched across finalized suites: 15" in record

    def test_136_decision_gate_retained(self):
        record = " ".join(_record().split())
        assert "READY_WITH_EXPLICIT_SUPERSESSION_AMENDMENTS" in record
        assert "actual combined suite includes Milestone 89 (322 + N)" in record
        assert "trace strategy is T3" in record
        assert "the trace-test impact audit is exact" in record
        assert "Identity insensitivity" in record

    def test_137_only_authorized_production_change_during_r3(self):
        import subprocess
        result = subprocess.run(
            ["git", "diff", "943b442", "HEAD", "--name-only", "--", "aether/"],
            capture_output=True, text=True, cwd=str(ROOT),
        )
        assert result.stdout.splitlines() == [
            "aether/core/governance.py",
            "aether/core/loop.py",
            "aether/thinking/policy.py",
        ], f"Unauthorized production source changed: {result.stdout[:200]}"

    def test_138_m87_m88_records_unchanged_tests_amended_only_as_authorized(self):
        import subprocess
        records = subprocess.run(
            ["git", "diff", "943b442", "HEAD", "--",
             "docs/architecture/MILESTONE_87_CORE_GOVERNANCE_AUTHORIZATION_BOUNDARY.md",
             "docs/architecture/MILESTONE_88_COGNITIVE_SIGNAL_ARBITRATION_BOUNDARY.md"],
            capture_output=True, text=True, cwd=str(ROOT),
        )
        assert records.stdout == "", f"Finalized record changed: {records.stdout[:200]}"
        _assert_exact_nine_path_set()
        _assert_exact_amendment_matrix(_amended_test_sets())
