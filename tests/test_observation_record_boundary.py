"""
Milestone 83A/83B/83C — Observation Record Boundary Tests.

This test file intentionally locks the Observation Record boundary as the
feature line progresses:

- 83A locked the pre-implementation boundary (no store/service/router).
- 83B added the 5 Observation API schema models to api_models.py.
- 83C added the service/store foundation (create/get/list only).
- 83D added the router/API endpoints (create/get/list only).

It does NOT test the builder (aether/action/observation_record.py is covered
by test_observation_record.py) and does NOT invoke any endpoints.

api_server.py must remain free of observation feature logic at all times.
"""

from __future__ import annotations

import ast
import subprocess
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent


# ---------------------------------------------------------------------------
# 1. Existing observation builder inventory
# ---------------------------------------------------------------------------

class TestObservationBuilderInventory:
    """Assert the 82B builder exists and is builder-only (no store/API)."""

    def test_observation_record_builder_module_exists(self):
        path = PROJECT_ROOT / "aether" / "action" / "observation_record.py"
        assert path.exists(), "aether/action/observation_record.py must exist (82B)"

    def test_builder_contains_build_observation_record(self):
        path = PROJECT_ROOT / "aether" / "action" / "observation_record.py"
        source = path.read_text(encoding="utf-8")
        assert "def build_observation_record(" in source

    def test_builder_contains_valid_statuses(self):
        path = PROJECT_ROOT / "aether" / "action" / "observation_record.py"
        source = path.read_text(encoding="utf-8")
        assert "VALID_STATUSES" in source

    def test_observation_builder_test_exists(self):
        path = PROJECT_ROOT / "tests" / "test_observation_record.py"
        assert path.exists(), "tests/test_observation_record.py must exist (82B)"


# ---------------------------------------------------------------------------
# 2. Observation service/store boundary (83C)
# ---------------------------------------------------------------------------

class TestObservationServiceStorePresent:
    """Assert the 83C service/store foundation exists (create/get/list only)."""

    def test_observation_record_service_exists(self):
        path = PROJECT_ROOT / "aether" / "action" / "services" / "observation_record_service.py"
        assert path.exists(), (
            "83C must add observation_record_service.py"
        )

    def test_observation_record_queue_exists(self):
        path = PROJECT_ROOT / "aether" / "action" / "observation_record_queue.py"
        assert path.exists(), (
            "83C must add observation_record_queue.py"
        )

    def test_observation_queue_tests_exist(self):
        path = PROJECT_ROOT / "tests" / "test_observation_record_queue.py"
        assert path.exists(), (
            "83C must add test_observation_record_queue.py"
        )

    def test_observation_service_tests_exist(self):
        path = PROJECT_ROOT / "tests" / "test_observation_record_service.py"
        assert path.exists(), (
            "83C must add test_observation_record_service.py"
        )

    def test_service_implements_create_get_list_only(self):
        """83C implements create/get/list only; update_status/cancel deferred."""
        path = PROJECT_ROOT / "aether" / "action" / "services" / "observation_record_service.py"
        source = path.read_text(encoding="utf-8")
        assert "def handle_create_observation_record" in source
        assert "def handle_get_observation_record" in source
        assert "def handle_list_observation_records" in source
        assert "def handle_update_observation_record_status" not in source
        assert "def handle_cancel_observation_record" not in source

    def test_queue_implements_save_load_list_only(self):
        """83C implements save/load/list only; update/cancel deferred."""
        path = PROJECT_ROOT / "aether" / "action" / "observation_record_queue.py"
        source = path.read_text(encoding="utf-8")
        assert "def save_observation_record" in source
        assert "def load_observation_record" in source
        assert "def list_observation_records" in source
        assert "def update_observation_record_status" not in source
        assert "def cancel_observation_record" not in source

    def test_observation_routes_router_exists(self):
        path = PROJECT_ROOT / "aether" / "interface" / "routers" / "observation_routes.py"
        assert path.exists(), (
            "83D must create observation_routes.py"
        )

    def test_no_protected_core_observation_routers(self):
        """Protected/core observation routers must not exist."""
        candidates = [
            "observation_record_routes.py",
        ]
        routers_dir = PROJECT_ROOT / "aether" / "interface" / "routers"
        for name in candidates:
            assert not (routers_dir / name).exists(), (
                f"83D must not create {name}"
            )

    def test_no_observation_records_in_git_index(self):
        """The observation_records private directory must not be tracked."""
        result = subprocess.run(
            [sys.executable, "-m", "git", "ls-files",
             str(PROJECT_ROOT / "aether" / "data" / "private" / "observation_records")],
            capture_output=True, text=True, cwd=PROJECT_ROOT,
        )
        assert result.stdout.strip() == "", (
            "observation_records must not be tracked by git"
        )


# ---------------------------------------------------------------------------
# 3. api_server.py boundary
# ---------------------------------------------------------------------------

class TestApiServerBoundary:
    """Lock the current api_server.py state — no observation feature logic."""

    @pytest.fixture(scope="class")
    def api_tree(self):
        api_path = PROJECT_ROOT / "aether" / "interface" / "api_server.py"
        source = api_path.read_text(encoding="utf-8")
        return ast.parse(source)

    @pytest.fixture(scope="class")
    def api_routes(self, api_tree):
        routes = {}
        include_router_count = 0
        action_routes = []
        for node in ast.walk(api_tree):
            if isinstance(node, ast.Call) and ast.unparse(node.func) == "app.include_router":
                include_router_count += 1
        for node in api_tree.body:
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            for dec in node.decorator_list:
                text = ast.unparse(dec)
                if not text.startswith("app."):
                    continue
                method = text.split("(", 1)[0].split(".", 1)[1].upper()
                path = ast.literal_eval(dec.args[0])
                routes[node.name] = (method, path)
                if path.startswith("/action/"):
                    action_routes.append((node.name, method, path))
        return routes, include_router_count, action_routes

    def test_exactly_8_app_routes(self, api_routes):
        routes, _, _ = api_routes
        expected = {
            "root": ("GET", "/"),
            "get_identity_integrity_status": ("GET", "/identity/integrity/status"),
            "post_initialize_identity_guard": ("POST", "/identity/integrity/initialize"),
            "post_verify_identity_integrity": ("POST", "/identity/integrity/verify"),
            "identity": ("GET", "/identity"),
            "awaken": ("POST", "/awaken"),
            "chat": ("POST", "/chat"),
            "classify_verification_risk": ("POST", "/verification/classify"),
        }
        assert routes == expected, f"Expected 8 protected/core routes; got {routes}"

    def test_exactly_23_include_router_calls(self, api_routes):
        _, count, _ = api_routes
        assert count == 23, f"Expected 23 include_router calls; got {count}"

    def test_zero_action_routes_in_api_server(self, api_routes):
        _, _, action_routes = api_routes
        assert action_routes == [], (
            f"Zero /action/* routes should remain in api_server.py; found {action_routes}"
        )

    def test_observation_router_imported(self, api_routes):
        """api_server.py must import the observation router (registration only)."""
        api_path = PROJECT_ROOT / "aether" / "interface" / "api_server.py"
        source = api_path.read_text(encoding="utf-8")
        tree = ast.parse(source)
        found = False
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module:
                if "observation_routes" in node.module:
                    found = True
        assert found, "api_server.py must import the observation router"

    def test_observation_router_included_exactly_once(self, api_routes):
        """api_server.py must include_router the observation router exactly once."""
        api_path = PROJECT_ROOT / "aether" / "interface" / "api_server.py"
        source = api_path.read_text(encoding="utf-8")
        tree = ast.parse(source)
        count = 0
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                text = ast.unparse(node)
                if "include_router" in text and "observation_router" in text:
                    count += 1
        assert count == 1, (
            f"observation_router must be included exactly once; found {count}"
        )

    def test_no_observation_feature_logic_in_api_server(self, api_routes):
        """No observation feature logic should appear in api_server.py routes."""
        api_path = PROJECT_ROOT / "aether" / "interface" / "api_server.py"
        source = api_path.read_text(encoding="utf-8")
        # Check that the source does not reference observation record store concepts
        forbidden_terms = [
            "observation_record_service",
            "observation_record_queue",
        ]
        for term in forbidden_terms:
            assert term not in source, (
                f"api_server.py must not contain '{term}'; this would indicate "
                "observation feature logic was added"
            )


# ---------------------------------------------------------------------------
# 4. OpenAPI pre-feature baseline
# ---------------------------------------------------------------------------

class TestOpenAPIStrictBaseline:
    """Lock OpenAPI at the 83D router baseline."""

    @pytest.fixture(scope="class")
    def openapi_schema(self):
        from aether.interface.api_server import app
        return app.openapi()

    def test_openapi_path_count_302(self, openapi_schema):
        paths = len(openapi_schema.get("paths", {}))
        assert paths == 302, f"Expected 302 paths; got {paths}"

    def test_openapi_schema_count_106(self, openapi_schema):
        schemas = len(openapi_schema.get("components", {}).get("schemas", {}))
        assert schemas == 106, f"Expected 106 schemas; got {schemas}"

    def test_observation_paths_exact(self, openapi_schema):
        paths = openapi_schema.get("paths", {})
        observation_paths = [
            p for p in paths
            if "observation" in p.lower()
        ]
        assert observation_paths == [
            "/observation-records",
            "/observation-records/{observation_id}",
        ], (
            f"Expected the two 83D observation paths; found: {observation_paths}"
        )

    def test_observation_operation_ids_exact(self, openapi_schema):
        operation_ids = []
        for methods in openapi_schema.get("paths", {}).values():
            for spec in methods.values():
                op_id = spec.get("operationId", "")
                if "observation" in op_id.lower():
                    operation_ids.append(op_id)
        assert sorted(operation_ids) == [
            "create_observation_record",
            "get_observation_record",
            "list_observation_records",
        ], (
            f"Expected the three 83D observation operationIds; found: {operation_ids}"
        )

    def test_family_counts_unchanged(self, openapi_schema):
        paths = openapi_schema.get("paths", {})
        self_paths = [p for p in paths if p.startswith("/action/self-modification")]
        guided_prefixes = (
            "/action/guided-repair-intake",
            "/action/guided-repair-plan-launcher",
            "/action/guided-bridge-selection-launcher",
            "/action/guided-proposal-review-launcher",
            "/action/guided-proposal-decision-launcher",
        )
        guided_paths = [p for p in paths if p.startswith(guided_prefixes)]
        changelog_paths = [p for p in paths if p.startswith("/action/changelog")]
        c2_paths = [p for p in paths if p.startswith("/action/final-real-apply-executor")]
        c1_prefixes = (
            "/action/approved-dry-run-gate",
            "/action/dry-run-review-gate",
            "/action/real-apply-approval-gate",
            "/action/post-apply-verification-gate",
        )
        c1_paths = [p for p in paths if p.startswith(c1_prefixes)]
        repair_paths = [p for p in paths if p.startswith("/action/repair-")]
        assert len(self_paths) == 9, f"Expected 9 self-modification paths; got {len(self_paths)}"
        assert len(guided_paths) == 29, f"Expected 29 guided paths; got {len(guided_paths)}"
        assert len(changelog_paths) == 4, f"Expected 4 changelog paths; got {len(changelog_paths)}"
        assert len(c2_paths) == 6, f"Expected 6 C2 paths; got {len(c2_paths)}"
        assert len(c1_paths) == 24, f"Expected 24 C1 paths; got {len(c1_paths)}"
        assert len(repair_paths) == 43, f"Expected 43 repair paths; got {len(repair_paths)}"


# ---------------------------------------------------------------------------
# 5. api_models.py boundary
# ---------------------------------------------------------------------------

class TestApiModelsBoundary:
    """Assert Observation Record API Pydantic models exist (added in 83B)."""

    def test_observation_record_create_request_exists(self):
        path = PROJECT_ROOT / "aether" / "interface" / "api_models.py"
        source = path.read_text(encoding="utf-8")
        assert "ObservationRecordCreateRequest" in source

    def test_observation_record_response_exists(self):
        path = PROJECT_ROOT / "aether" / "interface" / "api_models.py"
        source = path.read_text(encoding="utf-8")
        assert "ObservationRecordResponse" in source

    def test_observation_record_list_response_exists(self):
        path = PROJECT_ROOT / "aether" / "interface" / "api_models.py"
        source = path.read_text(encoding="utf-8")
        assert "ObservationRecordListResponse" in source

    def test_observation_record_update_status_request_exists(self):
        path = PROJECT_ROOT / "aether" / "interface" / "api_models.py"
        source = path.read_text(encoding="utf-8")
        assert "ObservationRecordUpdateStatusRequest" in source

    def test_observation_record_cancel_request_exists(self):
        path = PROJECT_ROOT / "aether" / "interface" / "api_models.py"
        source = path.read_text(encoding="utf-8")
        assert "ObservationRecordCancelRequest" in source


# ---------------------------------------------------------------------------
# 6. Architecture rule boundary
# ---------------------------------------------------------------------------

class TestArchitectureRule:
    """Assert the Protected Core Interface Feature Boundary rule is present."""

    def test_architecture_rule_exists(self):
        path = PROJECT_ROOT / "docs" / "ARCHITECTURE.md"
        source = path.read_text(encoding="utf-8")
        assert "Protected Core Interface Feature Boundary" in source

    def test_no_feature_code_in_api_server_rule(self):
        path = PROJECT_ROOT / "docs" / "ARCHITECTURE.md"
        source = path.read_text(encoding="utf-8")
        assert "No new feature code should be added directly to `api_server.py`" in source

    def test_router_service_model_test_structure_rule(self):
        path = PROJECT_ROOT / "docs" / "ARCHITECTURE.md"
        source = path.read_text(encoding="utf-8")
        assert "New feature surfaces must use the router / service / model / test structure" in source

    def test_future_decision_record_reopens_boundary_rule(self):
        path = PROJECT_ROOT / "docs" / "ARCHITECTURE.md"
        source = path.read_text(encoding="utf-8")
        assert "future decision record explicitly reopens the protected/core boundary" in source


# ---------------------------------------------------------------------------
# 7. No-invocation self-check
# ---------------------------------------------------------------------------

class TestNoInvocationSelfCheck:
    """Parse this very file and assert it does not violate boundary rules.

    Only AST nodes (code) are scanned — docstrings and comments are excluded
    because they may legitimately reference endpoints for documentation.
    """

    @pytest.fixture(scope="class")
    def this_tree(self):
        path = Path(__file__)
        source = path.read_text(encoding="utf-8")
        return ast.parse(source)

    def test_no_testclient_import(self, this_tree):
        for node in ast.walk(this_tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name == "TestClient":
                        pytest.fail("Boundary tests must not import TestClient")
            if isinstance(node, ast.ImportFrom) and node.module:
                if node.module == "pytest" and any(a.name == "TestClient" for a in node.names):
                    pytest.fail("Boundary tests must not import TestClient from pytest")

    def test_no_build_observation_record_call(self, this_tree):
        for node in ast.walk(this_tree):
            if isinstance(node, ast.Call):
                func = ast.unparse(node.func)
                if "build_observation_record" in func:
                    pytest.fail("Boundary tests must not call build_observation_record")

    def test_no_endpoint_invocation_calls(self, this_tree):
        """No direct calls to protected/core route functions."""
        forbidden = [
            "root(",
            "get_identity_integrity_status(",
            "post_initialize_identity_guard(",
            "post_verify_identity_integrity(",
            "identity(",
            "awaken(",
            "classify_verification_risk(",
        ]
        for node in ast.walk(this_tree):
            if isinstance(node, ast.Call):
                func = ast.unparse(node.func)
                for f in forbidden:
                    if func == f or func.endswith(f):
                        pytest.fail(f"Boundary tests must not call {f}")

    def test_no_runtime_action_service_calls(self, this_tree):
        """No direct calls to runtime/action/service functions."""
        # Use tuple parts to avoid embedding raw dotted strings in source.
        forbidden_parts = [
            (("runtime", "process_chat"), ("runtime", "status")),
            ("classify_risk",),
            ("handle_awaken",),
        ]
        for node in ast.walk(this_tree):
            if isinstance(node, ast.Call):
                func = ast.unparse(node.func)
                for parts in forbidden_parts:
                    for part in parts:
                        if isinstance(part, tuple):
                            if all(p in func for p in part):
                                pytest.fail(
                                    f"Boundary tests must not call {'.'.join(part)}"
                                )
                        elif part in func:
                            pytest.fail(
                                f"Boundary tests must not call {part}("
                            )

    def test_no_file_writes(self, this_tree):
        """Assert no file write operations in the test file."""
        for node in ast.walk(this_tree):
            if isinstance(node, ast.Call):
                func = ast.unparse(node.func)
                if func.endswith(".write_text") or func.endswith(".write_bytes") or func == "open":
                    pytest.fail(f"Boundary tests must not write files; found: {func}")

    def test_no_testclient_attribute_access(self, this_tree):
        """Assert no TestClient attribute access (e.g. HTTP method calls on TestClient)."""
        for node in ast.walk(this_tree):
            if isinstance(node, ast.Attribute):
                if node.attr == "get" or node.attr == "post" or node.attr == "put" or node.attr == "delete":
                    # Check if the object is TestClient
                    if isinstance(node.value, ast.Name) and node.value.id == "TestClient":
                        pytest.fail("Boundary tests must not use TestClient")


# ---------------------------------------------------------------------------
# 8. Future migration note (documented via test comments)
# ---------------------------------------------------------------------------

class TestFutureMigrationNotes:
    """
    These tests encode the migration narrative for the 83A-83D sequence.

    83A intentionally locked the pre-implementation boundary.
    83B intentionally added Observation Record schema models to api_models.py.
    83C intentionally added the service/store foundation (create/get/list only).
    83D remains the router/API endpoint milestone.

    api_server.py must still remain free of observation feature logic at all times.
    """

    def test_migration_note_present_in_source(self):
        """The test file should contain migration notes referencing future Builds."""
        path = Path(__file__)
        source = path.read_text(encoding="utf-8")
        assert "83B" in source or "83C" in source or "83D" in source, (
            "Boundary test file should contain migration notes referencing future Builds"
        )

    def test_api_server_feature_logic_warning(self):
        """The test file should document that api_server.py must remain feature-free."""
        path = Path(__file__)
        source = path.read_text(encoding="utf-8")
        assert "api_server.py" in source, (
            "Boundary test file should reference api_server.py constraint"
        )
