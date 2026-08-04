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
        assert calls.count("evaluate_authorization_envelope") == 1
        assert calls.count("build_approval_request") == 1
        assert calls.index("decide_chat_policy") < calls.index("evaluate_authorization_envelope")

    def test_12_production_policy_gate_importers_are_exact(self):
        # enforce_policy_gate is now only in the Action compatibility facade
        # Production importers of enforce_policy_gate should be empty
        # (loop no longer imports it; only tests import it directly)
        facade_importers = _production_importers(
            "aether.action.policy_gate", "enforce_policy_gate"
        )
        assert facade_importers == set()
        # loop imports evaluate_authorization_envelope from governance
        governance_importers = _production_importers(
            "aether.core.governance", "evaluate_authorization_envelope"
        )
        assert "aether/core/loop.py" in governance_importers

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
        assert "evaluate_authorization_envelope" in _call_names(fn)

    def test_30_gate_is_followed_by_builder_not_executor(self):
        fn = _function(LOOP, "run_core_chat_loop")
        calls = _call_names(fn)
        gate_index = calls.index("evaluate_authorization_envelope")
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
        assert (ROOT / "aether/core/governance.py").exists()

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
        # enforce_policy_gate now exists only in the Action compatibility facade
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
        assert (ROOT / "aether/core/governance.py").exists()
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


class TestGovernanceModuleExtraction:
    """Tests for the Milestone 87B extraction state."""

    def test_46_governance_module_exists(self):
        assert (ROOT / "aether/core/governance.py").exists()

    def test_47_governance_module_path_is_exact(self):
        import aether.core.governance as gov
        assert gov.__file__ == str(ROOT / "aether/core/governance.py")

    def test_48_governance_has_exact_public_function_name(self):
        import aether.core.governance as gov
        assert hasattr(gov, "evaluate_authorization_envelope")
        assert callable(gov.evaluate_authorization_envelope)

    def test_49_governance_function_signature_exact(self):
        import aether.core.governance as gov
        sig = inspect.signature(gov.evaluate_authorization_envelope)
        params = list(sig.parameters.keys())
        assert params == [
            "thinking_policy", "requested_action", "context",
            "risk_evidence", "identity_integrity_evidence",
        ]
        defaults = [
            sig.parameters["thinking_policy"].default,
            sig.parameters["requested_action"].default,
            sig.parameters["context"].default,
        ]
        assert all(d is None for d in defaults)
        kwonly = [
            p for p, v in sig.parameters.items()
            if v.kind == inspect.Parameter.KEYWORD_ONLY
        ]
        assert set(kwonly) == {"risk_evidence", "identity_integrity_evidence"}
        assert sig.return_annotation in (dict, "dict")

    def test_50_governance_narrow_scope_docstring(self):
        import aether.core.governance as gov
        doc = gov.__doc__ or ""
        assert "Milestone 87" in doc
        assert "narrow" in doc.lower() or "decision envelope" in doc.lower()
        assert "not the complete Governance plane" in doc
        assert "not a universal Governance runtime" in doc

    def test_51_governance_does_not_import_loop_or_interface(self):
        import aether.core.governance as gov
        src = gov.__file__
        tree = ast.parse(Path(src).read_text(encoding="utf-8"))
        imported_modules = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module:
                imported_modules.add(node.module)
        assert "aether.core.loop" not in imported_modules
        assert "aether.interface" not in imported_modules
        assert "aether.action.approval_queue" not in imported_modules
        assert "aether.memory.timeline" not in imported_modules

    def test_52_authoritative_logic_only_in_governance(self):
        # enforce_policy_gate logic exists only in governance module
        gov_src = (ROOT / "aether/core/governance.py").read_text(encoding="utf-8")
        facade_src = (ROOT / "aether/action/policy_gate.py").read_text(encoding="utf-8")
        # Governance has the full decision logic (decision_type checks)
        assert "decision_type" in gov_src
        # Facade has only a delegation, no decision branches
        assert "evaluate_authorization_envelope" in facade_src
        # Facade does NOT contain decision branching logic
        assert 'if decision_type == "block"' not in facade_src
        assert 'if decision_type == "require_approval"' not in facade_src

    def test_53_facade_has_exact_legacy_signature(self):
        facade_sig = inspect.signature(_gate())
        assert list(facade_sig.parameters) == [
            "thinking_policy", "requested_action", "context"
        ]
        assert all(
            p.default is None for p in facade_sig.parameters.values()
        )

    def test_54_facade_directly_delegates(self):
        import aether.action.policy_gate as pg
        import aether.core.governance as gov
        # Facade returns exactly what Governance returns
        policy = {"decision_type": "block", "blocked_reason": "test"}
        g_result = gov.evaluate_authorization_envelope(thinking_policy=policy)
        f_result = pg.enforce_policy_gate(thinking_policy=policy)
        assert g_result == f_result
        # Check source code contains delegation
        facade_src = Path(pg.__file__).read_text(encoding="utf-8")
        assert "evaluate_authorization_envelope" in facade_src

    def test_55_facade_contains_no_decision_branches(self):
        facade_src = (ROOT / "aether/action/policy_gate.py").read_text(encoding="utf-8")
        # The facade should not have any if/elif decision logic
        assert 'if decision_type' not in facade_src
        assert 'if not thinking_policy' not in facade_src

    def test_56_core_loop_imports_governance_directly(self):
        loop_src = LOOP.read_text(encoding="utf-8")
        assert "from aether.core.governance import evaluate_authorization_envelope" in loop_src
        assert "from aether.action.policy_gate import" not in loop_src

    def test_57_core_loop_passes_risk_evidence_directly(self):
        loop_src = LOOP.read_text(encoding="utf-8")
        assert "risk_evidence=risk" in loop_src

    def test_58_core_loop_passes_identity_evidence_directly(self):
        loop_src = LOOP.read_text(encoding="utf-8")
        assert "identity_integrity_evidence=identity_status" in loop_src

    def test_59_core_loop_does_not_recompute_risk(self):
        loop_src = LOOP.read_text(encoding="utf-8")
        # classify_risk is called once (in Step 6) and its result passed through
        # The loop should not call classify_risk inside the governance call
        fn = _function(LOOP, "run_core_chat_loop")
        calls = _call_names(fn)
        # classify_risk should appear only in Step 6, not in Step 7c
        classify_idx = calls.index("classify_risk")
        gov_idx = calls.index("evaluate_authorization_envelope")
        assert classify_idx < gov_idx

    def test_60_direct_identity_evidence_operative_only_for_identity_rules(self):
        import aether.core.governance as gov
        policy = {"decision_type": "block", "blocked_reason": "test"}
        risk = {"risk_level": "high", "action_type": "destructive"}
        base = gov.evaluate_authorization_envelope(thinking_policy=policy)
        # Operative only for Rules 1/2 statuses (changed/missing/failed)
        for status in ("changed", "missing", "failed"):
            with_evidence = gov.evaluate_authorization_envelope(
                thinking_policy=policy,
                risk_evidence=risk,
                identity_integrity_evidence={"status": status},
            )
            assert with_evidence != base, f"evidence must be operative for {status}"
        # Neutral, unknown, missing-key, and malformed evidence falls through
        for identity in ({"status": "verified"}, {"status": "intact"}, {"status": "unknown"},
                         {"foo": "bar"}, "not-a-dict"):
            with_evidence = gov.evaluate_authorization_envelope(
                thinking_policy=policy,
                risk_evidence=risk,
                identity_integrity_evidence=identity,
            )
            assert with_evidence == base, f"evidence must fall through for {identity}"

    def test_61_direct_evidence_absent_from_policy_snapshot(self):
        import aether.core.governance as gov
        policy = {"decision_type": "block"}
        risk = {"risk_level": "high"}
        result = gov.evaluate_authorization_envelope(
            thinking_policy=policy,
            risk_evidence=risk,
        )
        assert "risk" not in result["policy_snapshot"]
        assert "risk_evidence" not in result

    def test_62_identity_evidence_raw_values_absent_from_reason_and_warnings(self):
        import aether.core.governance as gov
        policy = {"decision_type": "respond_only", "tool_execution_allowed": False}
        raw_markers = ("HASH-RAW-SECRET-abc123", "RAW-SEED")

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

        # Rule 1: only the fixed approved reason; raw values never leak
        result = gov.evaluate_authorization_envelope(
            thinking_policy=policy,
            risk_evidence={"risk_level": "high"},
            identity_integrity_evidence={
                "status": "changed",
                "checksum": "HASH-RAW-SECRET-abc123",
                "seed": "RAW-SEED",
            },
        )
        assert result["reason"] == (
            "Identity integrity changed. Human review is required before continuing."
        )
        for marker in raw_markers:
            assert marker not in _strings(result)

        # Rule 2: only the fixed generic reason; raw values never leak
        result = gov.evaluate_authorization_envelope(
            thinking_policy=policy,
            identity_integrity_evidence={
                "status": "missing",
                "detail": "HASH-RAW-SECRET-abc123",
            },
        )
        assert result["reason"] == "Human approval is required before execution."
        for marker in raw_markers:
            assert marker not in _strings(result)

    def test_63_facade_governance_exact_equivalence_matrix(self):
        import aether.core.governance as gov
        import aether.action.policy_gate as pg
        cases = [
            None,
            {},
            {"decision_type": "unknown"},
            {"decision_type": "respond_only", "tool_execution_allowed": False},
            {"decision_type": "block"},
            {"decision_type": "block", "blocked_reason": "custom reason"},
            {"decision_type": "require_approval"},
            {"decision_type": "respond_only", "tool_execution_allowed": True},
            {"decision_type": "suggest_tool", "tool_execution_allowed": False},
        ]
        for policy in cases:
            g = gov.evaluate_authorization_envelope(thinking_policy=policy)
            f = pg.enforce_policy_gate(thinking_policy=policy)
            assert g == f, f"mismatch for {policy}: {g} != {f}"

    def test_64_input_dictionaries_not_mutated(self):
        import aether.core.governance as gov
        policy = {"decision_type": "block", "extra": "kept"}
        risk = {"risk_level": "high", "extra": "kept"}
        identity = {"status": "intact", "extra": "kept"}
        policy_copy = dict(policy)
        risk_copy = dict(risk)
        identity_copy = dict(identity)
        gov.evaluate_authorization_envelope(
            thinking_policy=policy,
            risk_evidence=risk,
            identity_integrity_evidence=identity,
        )
        assert policy == policy_copy
        assert risk == risk_copy
        assert identity == identity_copy

    def test_65_legacy_synthetic_allow_still_compatible(self):
        import aether.core.governance as gov
        result = gov.evaluate_authorization_envelope({
            "decision_type": "respond_only",
            "tool_execution_allowed": True,
        })
        assert result["decision"] == "allow"
        assert result["allowed"] is True
        assert result["tool_execution_allowed"] is True
        assert result["action_execution_allowed"] is True

    def test_66_fail_closed_cases_unchanged(self):
        import aether.core.governance as gov
        missing = gov.evaluate_authorization_envelope(None)
        malformed = gov.evaluate_authorization_envelope({})
        assert (missing["decision"], missing["allowed"]) == ("invalid_policy", False)
        assert (malformed["decision"], malformed["allowed"]) == ("deny", False)

    def test_67_allowed_not_execution_authority(self):
        import aether.core.governance as gov
        # Even when allowed=True, tool/action execution is separate
        result = gov.evaluate_authorization_envelope({
            "decision_type": "respond_only",
            "tool_execution_allowed": True,
        })
        assert result["allowed"] is True
        assert result["tool_execution_allowed"] is True
        assert result["action_execution_allowed"] is True
        # In production /chat these are always False
        prod_result = gov.evaluate_authorization_envelope({
            "decision_type": "respond_only",
            "tool_execution_allowed": False,
        })
        assert prod_result["allowed"] is False
        assert prod_result["tool_execution_allowed"] is False
        assert prod_result["action_execution_allowed"] is False

    def test_68_no_executor_calls_added_after_governance(self):
        fn = _function(LOOP, "run_core_chat_loop")
        calls = _call_names(fn)
        gov_idx = calls.index("evaluate_authorization_envelope")
        after = calls[gov_idx + 1:]
        for bad in ("execute_tool", "execute_action", "apply_patch_proposal",
                     "rollback_patch_apply", "collect_evidence"):
            assert bad not in after

    def test_69_governance_has_no_persistence_or_timeline_calls(self):
        import aether.core.governance as gov
        src = Path(gov.__file__).read_text(encoding="utf-8")
        tree = ast.parse(src)
        calls = _call_names(tree)
        for forbidden in ("record_event", "create_approval_record", "write_text",
                          "add_event", "persist"):
            assert forbidden not in calls

    def test_70_no_second_decision_implementation(self):
        definitions = []
        for path in (ROOT / "aether").rglob("*.py"):
            for node in ast.walk(_tree(path)):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    if node.name == "evaluate_authorization_envelope":
                        definitions.append(path.relative_to(ROOT).as_posix())
        assert definitions == ["aether/core/governance.py"]

    def test_71_no_fallback_engine_in_facade(self):
        facade_src = (ROOT / "aether/action/policy_gate.py").read_text(encoding="utf-8")
        # No if/else branches that implement decision logic
        assert 'if decision_type' not in facade_src
        assert 'if not thinking_policy' not in facade_src
        assert 'if not thinking_policy.get' not in facade_src
        # Only delegation
        assert facade_src.count("return") == 1
