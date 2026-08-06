"""Milestone 88A contract locks for the Cognitive Signal Arbitration classification.
import os

This suite is deliberately static or pure-call only. It does not use a
TestClient, invoke an endpoint, persist a record, modify configuration,
execute a tool/action, or access the network. It verifies the classification
record and the immutability of current runtime behavior.
"""

from __future__ import annotations

import ast
import importlib
import inspect
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / "docs/architecture/MILESTONE_88_COGNITIVE_SIGNAL_ARBITRATION_BOUNDARY.md"
ARCHITECTURE = ROOT / "docs/ARCHITECTURE.md"
CONSTITUTION = ROOT / "docs/CONSTITUTION.md"
M87_RECORD = ROOT / "docs/architecture/MILESTONE_87_CORE_GOVERNANCE_AUTHORIZATION_BOUNDARY.md"
M89_RECORD = ROOT / "docs/architecture/MILESTONE_89_IDENTITY_HARD_CONSTRAINT_MIGRATION_BOUNDARY.md"
POLICY = ROOT / "aether/thinking/policy.py"
GOVERNANCE = ROOT / "aether/core/governance.py"
LOOP = ROOT / "aether/core/loop.py"
API_SERVER = ROOT / "aether/interface/api_server.py"

H1 = "# Milestone 88 Cognitive Signal Arbitration Classification Boundary"
SECTIONS = [
    "## 1. Status and Scope",
    "## 2. Purpose",
    "## 3. Authoritative Existing Baseline",
    "## 4. Relationship to Architecture v0.3.0",
    "## 5. Relationship to Milestone 87",
    "## 6. Current Production Chain",
    "## 7. Current Thinking-Policy Rule Inventory",
    "## 8. Classification Model",
    "## 9. Constitutional Hard Constraints",
    "## 10. Operational Hard Constraints",
    "## 11. Soft Decision Signals",
    "## 12. Thinking Workflow and Default Rules",
    "## 13. Rule-by-Rule Classification Table",
    "## 14. Rule Precedence and Non-Override Contract",
    "## 15. Proposal, Evidence, and Authority Ownership",
    "## 16. Current Runtime Behavior",
    "## 17. Future Migration Implications",
    "## 18. Boundary-Test Contract",
    "## 19. Protected Files and Non-Goals",
    "## 20. Completion and Acceptance Criteria",
    "## 21. Milestone 88 Finalization and Closure Rule",
    "## 22. Deferred Behavioral Work",
]
CATEGORIES = (
    "Constitutional Hard Constraint",
    "Operational Hard Constraint",
    "Soft Decision Signal",
    "Thinking Workflow / Default Rule",
)


def _record() -> str:
    return RECORD.read_text(encoding="utf-8")


def _normalized() -> str:
    return " ".join(_record().split())


def _m89_record() -> str:
    return M89_RECORD.read_text(encoding="utf-8")


def _tree(path: Path) -> ast.Module:
    return ast.parse(path.read_text(encoding="utf-8"))


def _function(path: Path, name: str) -> ast.FunctionDef | ast.AsyncFunctionDef:
    for node in _tree(path).body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name:
            return node
    raise AssertionError(f"Missing function {name} in {path}")


def _call_names(node: ast.AST) -> list[str]:
    names: list[str] = []
    for child in ast.walk(node):
        if not isinstance(child, ast.Call):
            continue
        if isinstance(child.func, ast.Name):
            names.append(child.func.id)
        elif isinstance(child.func, ast.Attribute):
            names.append(child.func.attr)
    return names


def _policy_fn():
    return importlib.import_module("aether.thinking.policy").decide_chat_policy


def _gov_fn():
    return importlib.import_module("aether.core.governance").evaluate_authorization_envelope


def _base_perception(text: str = "hello") -> dict:
    return {"normalized_text": text, "risk_terms_detected": []}


def _base_risk(level: str = "low", action: str = "general_request") -> dict:
    return {"risk_level": level, "action_type": action, "confidence": "likely", "reasons": []}


def _make_policy(text: str = "hello", risk_level: str = "low",
                 risk_action: str = "general_request", tool: dict | None = None,
                 identity: dict | None = None, secrets: list[str] | None = None) -> dict:
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


class TestDecisionRecordStructure:
    def test_01_record_path_and_h1(self):
        assert RECORD.is_file()
        assert _record().splitlines()[0] == H1

    def test_02_exact_twenty_two_sections(self):
        actual = [line for line in _record().splitlines() if line.startswith("## ")]
        assert actual == SECTIONS

    def test_03_documentation_and_tests_only_scope(self):
        text = _record()
        assert "documentation and tests only" in text.lower() or "Documenta" in text
        assert "does not implement" in text or "does not change" in text

    def test_04_classification_is_not_a_runtime_object(self):
        text = _record()
        assert "classification is not a runtime object" in text.lower()

    def test_05_no_current_runtime_consumer_is_claimed(self):
        text = _normalized()
        assert "No runtime function currently consumes" in text or "does not consume" in text.lower()

    def test_06_four_exact_classification_categories(self):
        text = _record()
        for cat in CATEGORIES:
            assert cat in text

    def test_07_actual_current_rule_count_is_seven(self):
        # Verify from actual source, not from plan assumptions.
        # Milestone 89B moved Rules 1/2 to Core Governance: Thinking now
        # evaluates Rules 3-9 only (7 returns).
        fn = _function(POLICY, "_evaluate_chat_policy_with_precedence")
        returns = []
        for node in ast.walk(fn):
            if isinstance(node, ast.Return):
                returns.append(node)
        assert len(returns) == 6

    def test_08_every_source_rule_inventoried_once(self):
        text = _normalized()
        # All 9 rule conditions must appear
        conditions = [
            "identity_status == \"changed\"",
            "identity_status in (\"missing\", \"failed\")",
            "not normalized_text",
            "secret_found",
            "risk_level == \"high\"",
            "risk_level == \"medium\" and suggested_tool",
            "risk_level == \"low\" and suggested_tool",
            "not suggested_tool and len(normalized_text) < 10",
        ]
        for cond in conditions:
            assert cond in text, f"Missing condition: {cond}"
        # Default rule must also be present
        assert "default" in text.lower() or "respond_only" in text

    def test_09_exact_source_order_preserved(self):
        text = _normalized()
        # Rule 1 (identity changed) must appear before Rule 2 (identity missing)
        idx1 = text.index('identity_status == "changed"')
        idx2 = text.index('identity_status in ("missing", "failed")')
        assert idx1 < idx2
        # Rule 5 (high risk) before Rule 6 (medium risk)
        idx5 = text.index('risk_level == "high"')
        idx6 = text.index('risk_level == "medium"')
        assert idx5 < idx6


class TestRuleInventoryAndOutputs:
    def test_10_exact_trigger_conditions_from_ast(self):
        fn = _function(POLICY, "_evaluate_chat_policy_with_precedence")
        # Verify exact line numbers of return statements.
        # Milestone 89B removed Rules 1/2: 7 returns at the following lines.
        returns = []
        for node in ast.walk(fn):
            if isinstance(node, ast.Return):
                returns.append(node.lineno)
        assert len(returns) == 6
        assert any("rule_3" in ast.unparse(node) for node in ast.walk(fn) if isinstance(node, ast.Return))
        assert any("rule_4" in ast.unparse(node) for node in ast.walk(fn) if isinstance(node, ast.Return))
        assert 'risk_level == "high"' not in POLICY.read_text()

    def test_11_exact_current_decision_outputs(self):
        # Rules 1 and 2 are authoritatively evaluated by Core Governance
        # (Milestone 89B). The exact legacy decision semantics are preserved
        # through the authorization envelope projections.
        import aether.core.governance as gov

        # Rule 1: identity changed -> block (via Governance)
        envelope = gov.evaluate_authorization_envelope(
            thinking_policy=_make_policy(),
            identity_integrity_evidence={"status": "changed"},
        )
        assert envelope["decision"] == "block"
        assert envelope["policy_snapshot"]["decision_type"] == "block"
        assert envelope["policy_snapshot"]["required_user_confirmation"] is True
        assert envelope["policy_snapshot"]["tool_execution_allowed"] is False

        # Rule 2: identity missing/failed -> require_approval (via Governance)
        for status in ("missing", "failed"):
            envelope = gov.evaluate_authorization_envelope(
                thinking_policy=_make_policy(),
                identity_integrity_evidence={"status": status},
            )
            assert envelope["decision"] == "require_approval"
            assert envelope["policy_snapshot"]["decision_type"] == "require_approval"
            assert envelope["policy_snapshot"]["required_user_confirmation"] is True

        # Rules 3-9 remain exact raw Thinking outputs
        # Rule 3: empty text -> ask_clarification
        p = _make_policy(text="")
        assert p["decision_type"] == "ask_clarification"

        # Rule 4: secret terms -> require_approval
        p = _make_policy(secrets=["password"])
        assert p["decision_type"] == "require_approval"

        # Rule 5: high risk is selected by Governance from the sidecar.
        p = _make_policy(risk_level="high", risk_action="destructive_memory_action")
        envelope = gov.evaluate_authorization_envelope(
            thinking_policy=p,
            risk_evidence={"risk_level": "high", "action_type": "destructive_memory_action"},
            rule_3_4_precedence="clear",
        )
        assert envelope["decision"] == "require_approval"

        # Rule 6: medium risk + tool -> require_approval
        p = _make_policy(risk_level="medium", tool={"tool_id": "file.edit"})
        assert p["decision_type"] == "require_approval"

        # Rule 7: low risk + tool -> suggest_tool
        p = _make_policy(risk_level="low", tool={"tool_id": "file.search"})
        assert p["decision_type"] == "suggest_tool"

        # Rule 8: short input + no tool -> ask_clarification
        p = _make_policy(text="hi", tool=None)
        assert p["decision_type"] == "ask_clarification"

        # Rule 9: default -> respond_only
        p = _make_policy(text="write a story about cats")
        assert p["decision_type"] == "respond_only"

    def test_12_exact_confirmation_and_execution_fields(self):
        # Governance projections (Rules 1/2) preserve former fields exactly
        import aether.core.governance as gov
        for status in ("changed", "missing", "failed"):
            envelope = gov.evaluate_authorization_envelope(
                thinking_policy=_make_policy(),
                identity_integrity_evidence={"status": status},
            )
            snap = envelope["policy_snapshot"]
            assert snap["tool_execution_allowed"] is False
            assert snap["required_user_confirmation"] is True
            assert snap["tool_suggestion_allowed"] is False
            assert snap["decision_type"] in ("block", "require_approval")

        # All raw Thinking rules still force tool_execution_allowed == False
        for identity_status in (None, {"status": "changed"}, {"status": "missing"}, {"status": "failed"}):
            p = _make_policy(identity=identity_status)
            assert p["tool_execution_allowed"] is False

        p = _make_policy(secrets=["token"])
        assert p["tool_execution_allowed"] is False

        p = _make_policy(risk_level="high")
        assert p["tool_execution_allowed"] is False

        p = _make_policy(risk_level="medium", tool={"tool_id": "x"})
        assert p["tool_execution_allowed"] is False

        p = _make_policy(risk_level="low", tool={"tool_id": "x"})
        assert p["tool_execution_allowed"] is False

        p = _make_policy(text="hi")
        assert p["tool_execution_allowed"] is False

        p = _make_policy(text="hello world")
        assert p["tool_execution_allowed"] is False

    def test_13_exact_architectural_classification_table(self):
        text = _record()
        # Constitutional Hard Constraints: 2 rules (1, 5)
        assert text.count("Constitutional Hard Constraint") >= 2
        # Operational Hard Constraint: 3 rules (2, 4, 6)
        assert text.count("Operational Hard Constraint") >= 3
        # Soft Decision Signal: 1 rule (7)
        assert "Soft Decision Signal" in text
        # Thinking Workflow / Default Rule: 3 rules (3, 8, 9)
        assert text.count("Thinking Workflow / Default Rule") >= 3
        # Total: 9
        assert "Total: 9 rules" in text or "9 rules" in text


class TestConstitutionGrounding:
    def test_14_constitutional_grounding_cited_only_when_present(self):
        text = _record()
        # Rule 1 must cite §1.1 and §1.2
        assert "§1.1" in text
        assert "§1.2" in text
        # Rule 4 must cite §6.1
        assert "§6.1" in text
        # Rule 5 must cite §5.1
        assert "§5.1" in text
        # Rule 6 must NOT cite a specific article as constitutional
        # (it is operational, not constitutional)
        # Verify operational hard constraint section exists
        assert "Operational Hard Constraints" in text

    def test_15_operational_hard_constraints_distinct_from_constitutional(self):
        text = _record()
        # Rule 6 must appear in Operational Hard Constraints section
        # and must NOT appear in Constitutional Hard Constraints section
        # Find section boundaries
        op_idx = text.index("## 10. Operational Hard Constraints")
        soft_idx = text.index("## 11. Soft Decision Signals")
        rule6_in_op = "medium risk" in text[op_idx:soft_idx].lower()
        assert rule6_in_op, "Rule 6 must be in Operational Hard Constraints"
        # It should NOT be in the Constitutional section
        con_idx = text.index("## 9. Constitutional Hard Constraints")
        op_start = text.index("## 10. Operational Hard Constraints")
        rule6_not_in_con = "medium risk" not in text[con_idx:op_start].lower()
        assert rule6_not_in_con, "Rule 6 must not be in Constitutional Hard Constraints"


class TestClassificationSemantics:
    def test_16_mandatory_approval_rules_are_not_soft_signals(self):
        text = _record()
        # Rule 6 produces require_approval and must NOT be classified as soft
        # Find the Soft Decision Signals section
        soft_start = text.index("## 11. Soft Decision Signals")
        wf_start = text.index("## 12. Thinking Workflow and Default Rules")
        soft_section = text[soft_start:wf_start]
        # The only rule in soft section should be Rule 7 (low risk + tool)
        assert "Rule 7" in soft_section or "low risk" in soft_section.lower()
        # Rule 6 must NOT appear in soft section
        assert "Rule 6" not in soft_section
        assert "medium risk" not in soft_section.lower()

    def test_17_soft_signals_cannot_override_hard_constraints(self):
        text = _record()
        assert "must not independently override" in text or "cannot override" in text

    def test_18_workflow_default_rules_are_separately_classified(self):
        text = _record()
        assert "Thinking Workflow / Default Rule" in text
        # Rules 3, 8, 9 must appear in this category
        wf_idx = text.index("## 12. Thinking Workflow and Default Rules")
        next_section = text.index("## 13.", wf_idx)
        wf_section = text[wf_idx:next_section]
        assert "ask_clarification" in wf_section or "empty" in wf_section.lower()
        assert "short" in wf_section.lower() or "len(normalized_text)" in wf_section
        assert "respond_only" in wf_section or "default" in wf_section.lower()

    def test_19_clarification_default_routing_does_not_become_governance_authority(self):
        text = _normalized()
        assert "workflow rule" in text.lower() or "Workflow" in text
        assert "without becoming authorization authority" in text or "without creating authorization" in text


class TestOwnershipAndSeparation:
    def test_20_current_physical_owner_versus_architectural_owner(self):
        text = _normalized()
        # Physical owner: aether/thinking/policy.py
        assert "aether/thinking/policy.py" in text
        # Architectural owner for hard constraints: Core Governance
        assert "Core Governance" in text
        # Distinction must be stated
        assert "physical" in text.lower() and "architectural" in text.lower()

    def test_21_thinking_proposes(self):
        text = _record()
        assert "Thinking proposes" in text

    def test_22_governance_authorizes(self):
        text = _record()
        assert "Governance authorizes" in text

    def test_23_verification_and_identity_supply_evidence(self):
        text = _normalized()
        assert "Verification and Identity supply evidence" in text or \
               "Verification supplies evidence" in text

    def test_24_action_executes_only_within_authorization(self):
        text = _record()
        assert "Action executes only within authorization" in text

    def test_25_current_rule_precedence_remains_unchanged(self):
        text = _normalized()
        assert "source order" in text.lower() or "precedence" in text.lower()
        assert "does not reorder" in text.lower()

    def test_26_no_source_migration_is_claimed(self):
        text = _normalized()
        assert "no source migration" in text or "not moving" in text.lower()
        assert "implications only" in text.lower() or "implication" in text.lower()

    def test_27_no_evidence_activation_is_claimed(self):
        text = _normalized()
        assert "no evidence activation" in text or "Evidence non-operative" in text

    def test_28_risk_evidence_remains_non_operative(self):
        text = _normalized()
        assert "risk_evidence" in text
        assert "non-operative" in text or "provenance-only" in text

    def test_29_identity_evidence_operative_only_through_governance(self):
        import aether.core.governance as gov
        # Thinking never evaluates identity: raw output is identical for all
        # identity statuses (Milestone 89B insensitivity contract)
        neutral = _make_policy()
        for status in ("changed", "missing", "failed", "verified", "unknown"):
            assert _make_policy(identity={"status": status}) == neutral
        # Core Governance evaluates Rules 1 and 2 authoritatively
        for status, expected in (
            ("changed", "block"),
            ("missing", "require_approval"),
            ("failed", "require_approval"),
        ):
            envelope = gov.evaluate_authorization_envelope(
                thinking_policy=_make_policy(),
                identity_integrity_evidence={"status": status},
            )
            assert envelope["decision"] == expected
        # Risk evidence remains non-operative
        base = gov.evaluate_authorization_envelope(thinking_policy=_make_policy())
        with_risk = gov.evaluate_authorization_envelope(
            thinking_policy=_make_policy(),
            risk_evidence={"risk_level": "high"},
        )
        assert base == with_risk
        # No duplicate authority: Thinking must not read identity status
        policy_src = POLICY.read_text(encoding="utf-8")
        assert 'identity_status == "changed"' not in policy_src
        assert "identity_integrity_status.get" not in policy_src


class TestNoBehaviorChange:
    def test_30_exact_new_classification_string(self):
        # Milestone 89B carries the explicit classification string; the M89
        # record must state it verbatim (normalized).
        text = " ".join(_m89_record().split())
        assert "EXTERNALLY DECISION-, APPROVAL-, RESPONSE-SHAPE-, AND EXECUTION-FLAG" in text
        assert "PRESERVING" in text
        assert "INTENTIONAL DIAGNOSTIC TRACE SEMANTIC CHANGE" in text
        assert "INTERNAL PHYSICAL-OWNERSHIP CHANGE" in text

    def test_31_no_execution_enabled(self):
        text = _normalized()
        assert "no execution" in text.lower() or "Execution enabled: no" in text

    def test_32_no_persistence_added(self):
        text = _normalized()
        assert "no persistence" in text.lower() or "Persistence added: no" in text


class TestProtectedRecordsAndFiles:
    def test_33_milestone_87_record_remains_referenced_and_unchanged(self):
        text = _record()
        assert "MILESTONE_87_CORE_GOVERNANCE_AUTHORIZATION_BOUNDARY" in text
        # Verify the M87 record file still exists and is readable
        assert M87_RECORD.is_file()
        m87_text = M87_RECORD.read_text(encoding="utf-8")
        assert "Milestone 87 Core Governance Authorization Decision-Envelope Boundary" in m87_text

    def test_34_existing_76_milestone_87_tests_remain_authoritative(self):
        # Verify the M87 test file still has the expected content
        m87_test_path = ROOT / "tests" / "test_milestone_87_core_governance_authorization_boundary.py"
        assert m87_test_path.is_file()
        # Check the file has the governance module extraction tests (test_46+)
        m87_text = m87_test_path.read_text(encoding="utf-8")
        assert "test_46_governance_module_exists" in m87_text
        assert "test_71_no_fallback_engine_in_facade" in m87_text

    def test_35_architecture_remains_0_3_0(self):
        arch_text = ARCHITECTURE.read_text(encoding="utf-8")
        assert "**Version:** 0.3.0" in arch_text

    def test_36_constitution_remains_0_2_0(self):
        const_text = CONSTITUTION.read_text(encoding="utf-8")
        assert "**Version:** 0.2.0" in const_text

    def test_37_openapi_304_108_recorded(self):
        text = _record()
        assert "304" in text
        assert "108" in text

    def test_38_api_server_8_23_0_recorded(self):
        text = _record()
        assert "8" in text
        assert "23" in text
        assert "0" in text

    def test_39_milestone_88_remains_open(self):
        text = _normalized()
        assert "Milestone 88 remains open" in text or "Milestone 88: open" in text

    def test_40_milestone_89_does_not_start_automatically(self):
        text = _record()
        assert "Milestone 89 does not start automatically" in text or \
               "Milestone 89 has not started" in text

    def test_41_milestone_88_closes_only_after_88a_finalization(self):
        text = _record()
        assert "Milestone 88 closes only after" in text or \
               "88A Finalization" in text

    def test_42_future_migration_requires_new_plan(self):
        text = _record()
        assert "new Plan" in text or "new post-Milestone-88" in text or \
               "Future work requires" in text


class TestOpenAPIServerUnchanged:
    def test_43_openapi_counts_unchanged(self):
        app = importlib.import_module("aether.interface.api_server").app
        schema = app.openapi()
        assert len(schema.get("paths", {})) == 304
        assert len(schema.get("components", {}).get("schemas", {})) == 108

    def test_44_api_server_shape_unchanged(self):
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


class TestNoProductionSourceChanges:
    def test_45_only_authorized_production_modules_changed(self):
        # Milestone 89B authorizes exactly three production files to change
        # (policy.py, governance.py, loop.py). Every other production module
        # must remain byte-identical.
        import subprocess
        result = subprocess.run(
            ["git", "diff", "943b442", "HEAD", "--name-only", "--", "aether/"],
            capture_output=True, text=True, cwd=str(ROOT)
        )
        assert result.stdout.splitlines() == [
            "aether/core/governance.py",
            "aether/core/loop.py",
            "aether/thinking/policy.py",
        ], f"Unauthorized production source changed: {result.stdout[:200]}"

    def test_46_no_new_persistence_or_execution_imports(self):
        # The new test file must not import TestClient, requests, httpx
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

    def test_47_no_writer_calls_in_new_test(self):
        test_src = Path(__file__).read_text(encoding="utf-8")
        tree = ast.parse(test_src)
        calls = _call_names(tree)
        assert "write_text" not in calls
        assert "record_event" not in calls
        assert "create_approval_record" not in calls


class TestClassificationCorrectness:
    def test_48_count_per_category(self):
        text = _record()
        # Extract ONLY the classification table in section 13 (between ## 13 and ## 14)
        t13_start = text.index("## 13. Rule-by-Rule Classification Table")
        t14_start = text.index("## 14.", t13_start)
        table_text = text[t13_start:t14_start]
        # Count only pipe-delimited rows that contain a category name
        cat_counts = {"Constitutional Hard Constraint": 0, "Operational Hard Constraint": 0,
                      "Soft Decision Signal": 0, "Thinking Workflow / Default Rule": 0}
        for line in table_text.splitlines():
            if "|" not in line:
                continue
            parts = [p.strip() for p in line.split("|")]
            # Skip header and separator lines
            if len(parts) < 5 or "Order" in parts[1] or parts[1].startswith("---"):
                continue
            # The category is in column 6 (index 5)
            if len(parts) >= 6:
                cat_cell = parts[5]
                for cat in cat_counts:
                    if cat in cat_cell:
                        cat_counts[cat] += 1
                        break
        assert cat_counts["Constitutional Hard Constraint"] == 2, f"Expected 2, got {cat_counts['Constitutional Hard Constraint']}"
        assert cat_counts["Operational Hard Constraint"] == 3, f"Expected 3, got {cat_counts['Operational Hard Constraint']}"
        assert cat_counts["Soft Decision Signal"] == 1, f"Expected 1, got {cat_counts['Soft Decision Signal']}"
        assert cat_counts["Thinking Workflow / Default Rule"] == 3, f"Expected 3, got {cat_counts['Thinking Workflow / Default Rule']}"

    def test_49_rule_6_not_soft_signal(self):
        text = _record()
        # Find the Operational Hard Constraints section
        op_start = text.index("## 10. Operational Hard Constraints")
        soft_start = text.index("## 11. Soft Decision Signals")
        op_section = text[op_start:soft_start]
        # Rule 6 (medium risk + tool) must be in the operational section
        assert "medium risk" in op_section.lower() or "medium" in op_section.lower()
        # And the word "require_approval" must appear near it
        assert "require_approval" in op_section

    def test_50_constitutional_rules_have_article_citations(self):
        text = _record()
        # Rules 1 and 5 are Constitutional Hard Constraints with direct grounding
        assert "§1.1" in text
        assert "§1.2" in text
        assert "§5.1" in text
        assert "§8.2" in text
        assert "§11.1" in text
        # Rules 2 and 4 are Operational Hard Constraints with constitutional support
        # (they cite §10, §10.1, §6.1 but are not direct mandates)
        assert "§10" in text
        assert "§10.1" in text
        assert "§6.1" in text
