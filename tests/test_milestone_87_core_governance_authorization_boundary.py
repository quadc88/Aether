"""Milestone 87A contract locks for the future Core Governance boundary.

This suite is deliberately static or pure-call only.  It does not use a
TestClient, invoke an endpoint, persist an approval or Timeline record, modify
configuration, execute a tool/action, or access the network.
"""

from __future__ import annotations

import ast
import importlib
import inspect
import re
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / "docs/architecture/MILESTONE_87_CORE_GOVERNANCE_AUTHORIZATION_BOUNDARY.md"
ARCHITECTURE = ROOT / "docs/ARCHITECTURE.md"
MILESTONE_85 = ROOT / "docs/architecture/MILESTONE_85_OBSERVE_VERIFY_LIFECYCLE_BOUNDARY_RECORD.md"
LOOP = ROOT / "aether/core/loop.py"
API_SERVER = ROOT / "aether/interface/api_server.py"
POLICY = ROOT / "aether/thinking/policy.py"
GATE = ROOT / "aether/action/policy_gate.py"
APPROVAL_REQUEST = ROOT / "aether/action/approval_request.py"

H1 = "# Milestone 87 Core Governance Authorization Decision-Envelope Boundary"
SECTIONS = [
    "## 1. Status and Scope",
    "## 2. Purpose",
    "## 3. Authoritative Existing Baseline",
    "## 4. Architecture Ownership",
    "## 5. Current Production Chain",
    "## 6. Current Responsibility Mixing",
    "## 7. Selected Boundary",
    "## 8. Exact Caller and Invocation Point",
    "## 9. Input Provenance and Authority",
    "## 10. Thinking Proposal Contract",
    "## 11. Verification and Identity Evidence Contract",
    "## 12. Governance Decision-Envelope Contract",
    "## 13. Decision-Envelope Field Semantics",
    "## 14. Approval and Confirmation Boundary",
    "## 15. No-Execution Boundary",
    "## 16. Consumers and Compatibility Obligations",
    "## 17. Failure and Fail-Closed Behavior",
    "## 18. Persistence, Privacy, and Side Effects",
    "## 19. Physical Runtime Home Decision",
    "## 20. Import and Dependency Direction",
    "## 21. Milestone 87B Migration Rule",
    "## 22. Boundary-Test Contract",
    "## 23. Protected-Core and Non-Goals",
    "## 24. Milestone 87 Completion and Closure Rule",
]
ENVELOPE_KEYS = {
    "allowed",
    "decision",
    "reason",
    "required_user_confirmation",
    "tool_execution_allowed",
    "action_execution_allowed",
    "requested_action",
    "policy_snapshot",
    "warnings",
}


def _record() -> str:
    return RECORD.read_text(encoding="utf-8")


def _normalized_record() -> str:
    return " ".join(_record().split())


def _tree(path: Path) -> ast.Module:
    return ast.parse(path.read_text(encoding="utf-8"))


def _function(path: Path, name: str) -> ast.FunctionDef | ast.AsyncFunctionDef:
    for node in _tree(path).body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name:
            return node
    raise AssertionError(f"Missing function {name} in {path}")


def _gate():
    return importlib.import_module("aether.action.policy_gate").enforce_policy_gate


def _builder():
    return importlib.import_module("aether.action.approval_request").build_approval_request


def _production_importers(module: str, symbol: str) -> set[str]:
    importers: set[str] = set()
    for path in (ROOT / "aether").rglob("*.py"):
        for node in ast.walk(_tree(path)):
            if isinstance(node, ast.ImportFrom) and node.module == module:
                if any(alias.name == symbol for alias in node.names):
                    importers.add(path.relative_to(ROOT).as_posix())
    return importers


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


class TestDecisionRecordStructure:
    def test_01_record_path_and_h1(self):
        assert RECORD.is_file()
        assert _record().splitlines()[0] == H1

    def test_02_exact_twenty_four_sections(self):
        actual = [line for line in _record().splitlines() if line.startswith("## ")]
        assert actual == SECTIONS

    def test_03_record_does_not_claim_runtime_implementation(self):
        text = _record()
        assert "does not implement, extract, redirect" in text
        assert "Runtime extraction performed: yes" not in text

    def test_04_architecture_v030_remains_in_force(self):
        architecture = ARCHITECTURE.read_text(encoding="utf-8")
        assert re.search(r"\*\*Version:\*\* 0\.3\.0", architecture)
        assert "Architecture v0.3.0" in _record()

    def test_05_milestone_85_boundary_remains_in_force(self):
        assert MILESTONE_85.is_file()
        text = _normalized_record()
        assert "Milestone 85" in text
        assert "No Observation classification or record becomes an execution trigger" in text


class TestArchitectureOwnership:
    def test_06_core_governance_owns_authoritative_decision(self):
        assert "Core Governance owns the authoritative authorization decision" in _record()

    def test_07_coordination_remains_caller(self):
        text = _normalized_record()
        assert "Core Coordination owns call sequencing and invokes Governance" in text
        assert "aether.core.loop.run_core_chat_loop" in text

    def test_08_thinking_proposal_is_non_authoritative(self):
        text = _normalized_record()
        assert "Thinking proposes. It does not grant execution permission" in text
        assert "legacy compatibility/proposal data" in text

    def test_09_verification_and_identity_supply_evidence(self):
        text = _normalized_record()
        assert "Verification supplies the existing risk evidence dictionary" in text
        assert "Identity supplies the existing integrity-state dictionary" in text
        assert "Evidence describes the current condition" in text

    def test_10_action_remains_downstream(self):
        text = _normalized_record()
        assert "Action owns execution and downstream approval mechanics" in text
        assert "Approval records represent human review state but do not own authorization policy" in text


class TestProductionChainAndImporters:
    def test_11_current_production_call_site_exists(self):
        loop = _function(LOOP, "run_core_chat_loop")
        calls = _call_names(loop)
        assert calls.count("decide_chat_policy") == 1
        assert calls.count("enforce_policy_gate") == 1
        assert calls.count("build_approval_request") == 1
        assert calls.index("decide_chat_policy") < calls.index("enforce_policy_gate")

    def test_12_production_policy_gate_importers_are_exact(self):
        assert _production_importers(
            "aether.action.policy_gate", "enforce_policy_gate"
        ) == {"aether/core/loop.py"}

    def test_13_record_inventories_direct_importers(self):
        text = _normalized_record()
        assert "Production importer inventory for `enforce_policy_gate`: exactly" in text
        assert "The direct test importer is `tests/test_policy_gate.py`" in text

    def test_14_current_gate_signature_exact(self):
        signature = inspect.signature(_gate())
        assert list(signature.parameters) == [
            "thinking_policy", "requested_action", "context"
        ]
        assert all(param.default is None for param in signature.parameters.values())
        assert signature.return_annotation in (dict, "dict")


class TestCurrentEnvelopeContract:
    @pytest.mark.parametrize(
        "policy,expected_decision",
        [
            (None, "invalid_policy"),
            ({}, "deny"),
            ({"decision_type": "unknown"}, "deny"),
            ({"decision_type": "respond_only", "tool_execution_allowed": False}, "deny"),
            ({"decision_type": "block", "tool_execution_allowed": False}, "block"),
            ({"decision_type": "require_approval", "tool_execution_allowed": False}, "require_approval"),
        ],
    )
    def test_15_exact_envelope_shape_for_fail_closed_cases(self, policy, expected_decision):
        result = _gate()(thinking_policy=policy)
        assert set(result) == ENVELOPE_KEYS
        assert result["decision"] == expected_decision

    def test_16_field_types_and_defaults(self):
        result = _gate()()
        assert result == {
            "allowed": False,
            "decision": "invalid_policy",
            "reason": "Missing thinking policy.",
            "required_user_confirmation": True,
            "tool_execution_allowed": False,
            "action_execution_allowed": False,
            "requested_action": None,
            "policy_snapshot": None,
            "warnings": ["No thinking policy available to evaluate."],
        }
        assert isinstance(result["allowed"], bool)
        assert isinstance(result["decision"], str)
        assert isinstance(result["reason"], str)
        assert isinstance(result["warnings"], list)

    def test_17_requested_action_and_snapshot_are_provenance(self):
        action = {"tool_id": "example.read"}
        proposal = {"decision_type": "respond_only", "tool_execution_allowed": False}
        result = _gate()(proposal, action)
        assert result["requested_action"] is action
        assert result["policy_snapshot"] == proposal
        assert result["policy_snapshot"] is not proposal
        text = _normalized_record()
        assert "request/proposal provenance" in text
        assert "not an authoritative Governance policy object" in text

    def test_18_existing_warning_behavior(self):
        assert _gate()()["warnings"] == ["No thinking policy available to evaluate."]
        denied = _gate()({"decision_type": "unknown"})
        assert denied["warnings"] == []


class TestAllowedAndApprovalSeparation:
    def test_19_allowed_is_not_documented_as_execution_authority(self):
        text = _normalized_record()
        assert "must not be consumed alone as tool/action execution authority" in text
        assert "`allowed=True` does not prove completed Human Authority approval" in text

    def test_20_current_production_thinking_never_allows_tool_execution(self):
        fn = _function(POLICY, "decide_chat_policy")
        values = []
        for node in ast.walk(fn):
            if isinstance(node, ast.Dict):
                for key, value in zip(node.keys, node.values):
                    if isinstance(key, ast.Constant) and key.value == "tool_execution_allowed":
                        values.append(ast.literal_eval(value))
        assert values
        assert set(values) == {False}

    def test_21_approval_required_is_not_approval_granted(self):
        envelope = _gate()({
            "decision_type": "require_approval",
            "required_user_confirmation": True,
            "tool_execution_allowed": False,
        })
        request = _builder()(policy_gate=envelope)
        assert envelope["allowed"] is False
        assert request["approval_required"] is True
        assert request["approval_status"] == "pending"
        assert "approved" not in request.values()

    def test_22_pending_approval_has_no_execution_fields(self):
        request = _builder()(policy_gate={
            "allowed": False,
            "decision": "require_approval",
            "reason": "Human approval is required before execution.",
        })
        assert request["approval_status"] == "pending"
        assert "tool_execution_allowed" not in request
        assert "action_execution_allowed" not in request
        assert "execution_allowed" not in request


class TestFailClosedBehavior:
    def test_23_malformed_input_is_invalid_or_denied(self):
        missing = _gate()(None)
        malformed = _gate()({})
        assert (missing["decision"], missing["allowed"]) == ("invalid_policy", False)
        assert (malformed["decision"], malformed["allowed"]) == ("deny", False)
        assert malformed["tool_execution_allowed"] is False
        assert malformed["action_execution_allowed"] is False

    def test_24_unknown_decision_fails_closed(self):
        result = _gate()({"decision_type": "not_a_decision"})
        assert result["decision"] == "deny"
        assert result["allowed"] is False

    def test_25_explicit_block_fails_closed(self):
        result = _gate()({"decision_type": "block", "blocked_reason": "blocked"})
        assert result["decision"] == "block"
        assert result["reason"] == "blocked"
        assert result["required_user_confirmation"] is True
        assert result["tool_execution_allowed"] is False
        assert result["action_execution_allowed"] is False

    def test_26_approval_required_fails_closed(self):
        result = _gate()({"decision_type": "require_approval"})
        assert result["decision"] == "require_approval"
        assert result["allowed"] is False
        assert result["required_user_confirmation"] is True
        assert result["tool_execution_allowed"] is False
        assert result["action_execution_allowed"] is False

    def test_27_response_only_current_gate_behavior(self):
        result = _gate()({
            "decision_type": "respond_only",
            "required_user_confirmation": False,
            "tool_execution_allowed": False,
        })
        assert result["decision"] == "deny"
        assert result["allowed"] is False
        assert result["reason"] == "Tool execution is not allowed by policy."

    def test_28_legacy_synthetic_allow_is_recorded_not_normalized_away(self):
        result = _gate()({
            "decision_type": "respond_only",
            "tool_execution_allowed": True,
        })
        assert result["decision"] == "allow"
        assert result["allowed"] is True
        assert result["tool_execution_allowed"] is True
        assert result["action_execution_allowed"] is True
        assert "legacy synthetic truthy execution flag" in _record()


class TestNoExecutionAndConsumers:
    def test_29_core_loop_forces_tool_execution_false(self):
        source = LOOP.read_text(encoding="utf-8")
        assert "tool_executed = False" in source
        assert "tool_execution_allowed = False" in source
        fn = _function(LOOP, "run_core_chat_loop")
        assert "execute_tool" not in _call_names(fn)
        assert "apply_patch_proposal" not in _call_names(fn)
        assert "rollback_patch_apply" not in _call_names(fn)

    def test_30_gate_is_followed_by_builder_not_executor(self):
        fn = _function(LOOP, "run_core_chat_loop")
        calls = _call_names(fn)
        gate_index = calls.index("enforce_policy_gate")
        after = calls[gate_index + 1 :]
        assert "build_approval_request" in after
        assert not {"execute_tool", "execute_action", "apply_patch_proposal"}.intersection(after)

    def test_31_exact_consumers_are_recorded(self):
        text = _normalized_record()
        for symbol in (
            "aether.action.approval_request.build_approval_request",
            "aether.core.loop.run_core_chat_loop",
            "aether.core.loop_trace.build_loop_trace",
            "aether.memory.timeline.recorder.record_event",
        ):
            assert symbol in text
        assert "currently consumes no decision-envelope field" in text

    def test_32_approval_builder_does_not_mutate_envelope(self):
        envelope = _gate()({"decision_type": "require_approval"})
        before = dict(envelope)
        _builder()(policy_gate=envelope)
        assert envelope == before


class TestPhysicalHomeAndMigration:
    def test_33_selected_physical_home_is_exact(self):
        text = _normalized_record()
        assert "Selected future physical home: `aether/core/governance.py`" in text
        assert not (ROOT / "aether/core/governance.py").exists()

    def test_34_dependency_direction_is_locked(self):
        text = _normalized_record()
        assert "`aether.core.loop` (Coordination) -> imports and invokes" in text
        assert "`aether.core.governance` must not import `aether.core.loop`" in text
        assert "The Action compatibility facade may import Core Governance" in text

    def test_35_selected_migration_is_compatibility_facade(self):
        text = _normalized_record()
        assert "convert `aether/action/policy_gate.py` into a thin compatibility" in text
        assert "There must be no second live decision engine" in text

    def test_36_future_87b_matrix_is_exactly_recorded(self):
        text = _normalized_record()
        for path in (
            "aether/core/governance.py",
            "aether/core/loop.py",
            "aether/action/policy_gate.py",
            "tests/test_milestone_87_core_governance_authorization_boundary.py",
            "PROGRESS.md",
        ):
            assert f"`{path}`" in text

    def test_37_no_parallel_authoritative_gate_exists_in_87a(self):
        definitions = []
        for path in (ROOT / "aether").rglob("*.py"):
            for node in ast.walk(_tree(path)):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    if node.name == "enforce_policy_gate":
                        definitions.append(path.relative_to(ROOT).as_posix())
        assert definitions == ["aether/action/policy_gate.py"]


class TestProtectedStructureAndNonGoals:
    def test_38_openapi_counts_unchanged(self):
        app = importlib.import_module("aether.interface.api_server").app
        schema = app.openapi()
        assert len(schema.get("paths", {})) == 304
        assert len(schema.get("components", {}).get("schemas", {})) == 108

    def test_39_api_server_shape_unchanged(self):
        tree = _tree(API_SERVER)
        app_routes = 0
        include_router = 0
        direct_action = 0
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                for decorator in node.decorator_list:
                    text = ast.unparse(decorator)
                    if text.startswith("app."):
                        app_routes += 1
                        if '"/action/' in text or "'/action/" in text:
                            direct_action += 1
            if isinstance(node, ast.Call) and ast.unparse(node.func) == "app.include_router":
                include_router += 1
        assert (app_routes, include_router, direct_action) == (8, 23, 0)

    def test_40_no_runtime_module_or_interface_artifact_added(self):
        assert not (ROOT / "aether/core/governance.py").exists()
        assert not (ROOT / "aether/interface/routers/governance_routes.py").exists()
        assert not (ROOT / "aether/interface/governance_api_models.py").exists()

    def test_41_boundary_files_contain_no_persistence_or_endpoint_invocation(self):
        test_source = Path(__file__).read_text(encoding="utf-8")
        tree = ast.parse(test_source)
        imported_names = {
            alias.name
            for node in ast.walk(tree)
            if isinstance(node, (ast.Import, ast.ImportFrom))
            for alias in node.names
        }
        assert "TestClient" not in imported_names
        assert "requests" not in imported_names
        assert "httpx" not in imported_names
        calls = _call_names(tree)
        assert not {"write_text", "open", "record_event", "create_approval_record"}.intersection(calls)

    def test_42_record_locks_no_new_persistence(self):
        text = _normalized_record()
        assert "no queue, store, schema, runtime/private" in text
        assert "non-persistent" in text

    def test_43_protected_core_and_non_goals_are_explicit(self):
        text = _normalized_record()
        for protected in (
            "Constitution",
            "Architecture",
            "README",
            "API models",
            "routers",
            "endpoints",
            "queues",
            "stores",
            "schemas",
            "docs/history",
        ):
            assert protected in text

    def test_44_milestone_87_remains_open(self):
        text = _normalized_record()
        assert "Milestone 87 remains open after 87A" in text
        assert "Milestone 87B has not started" in text

    def test_45_milestone_88_does_not_start_automatically(self):
        text = _normalized_record()
        assert "Milestone 88 does not start automatically" in text
