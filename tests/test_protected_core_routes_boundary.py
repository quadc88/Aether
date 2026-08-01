"""AST/OpenAPI-only boundary coverage for Protected/Core routes in api_server.py.

This test locks the current protected/core route behavior WITHOUT invoking
any endpoint or calling any route/action/service function.
"""
import ast
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
API_SERVER_PATH = PROJECT_ROOT / "aether" / "interface" / "api_server.py"
ROUTER_DIR = PROJECT_ROOT / "aether" / "interface" / "routers"

# Protected/core routes expected contract
PROTECTED_CORE_ROUTES = {
    "root": {
        "method": "GET",
        "path": "/",
        "operation_id": "root__get",
        "request_model": None,
        "expected_signature": "",
        "expected_return_count": 1,
        "expected_flows": [],
        "expected_call_substrings": ["runtime.status", "time_state", "runtime.working_memory.summary"],
    },
    "get_identity_integrity_status": {
        "method": "GET",
        "path": "/identity/integrity/status",
        "operation_id": "get_identity_integrity_status_identity_integrity_status_get",
        "request_model": None,
        "expected_signature": "",
        "expected_return_count": 1,
        "expected_flows": [],
        "expected_call_substrings": ["identity_guard_status"],
    },
    "post_initialize_identity_guard": {
        "method": "POST",
        "path": "/identity/integrity/initialize",
        "operation_id": "post_initialize_identity_guard_identity_integrity_initialize_post",
        "request_model": None,
        "expected_signature": "",
        "expected_return_count": 1,
        "expected_flows": [],
        "expected_call_substrings": ["initialize_identity_guard", "state.get"],
    },
    "post_verify_identity_integrity": {
        "method": "POST",
        "path": "/identity/integrity/verify",
        "operation_id": "post_verify_identity_integrity_identity_integrity_verify_post",
        "request_model": None,
        "expected_signature": "",
        "expected_return_count": 1,
        "expected_flows": [],
        "expected_call_substrings": ["verify_identity_integrity"],
    },
    "identity": {
        "method": "GET",
        "path": "/identity",
        "operation_id": "identity_identity_get",
        "request_model": None,
        "expected_signature": "",
        "expected_return_count": 1,
        "expected_flows": [],
        "expected_call_substrings": ["identity_preview"],
    },
    "awaken": {
        "method": "POST",
        "path": "/awaken",
        "operation_id": "awaken_awaken_post",
        "request_model": None,
        "expected_signature": "",
        "expected_return_count": 1,
        "expected_flows": [],
        "expected_call_substrings": ["handle_awaken"],
    },
    "chat": {
        "method": "POST",
        "path": "/chat",
        "operation_id": "chat_chat_post",
        "request_model": "ChatRequest",
        "expected_signature": "request: ChatRequest",
        "expected_return_count": 2,
        "expected_flows": ["If"],
        "expected_call_substrings": [
            "runtime.process_chat",
            "runtime.working_memory.summary",
            "ChatResponse",
            "build_loop_trace",
            "generate_trace_id",
            "now_iso",
            "build_stage",
        ],
    },
    "classify_verification_risk": {
        "method": "POST",
        "path": "/verification/classify",
        "operation_id": "classify_verification_risk_verification_classify_post",
        "request_model": "VerificationRequest",
        "expected_signature": "request: VerificationRequest",
        "expected_return_count": 1,
        "expected_flows": [],
        "expected_call_substrings": ["runtime.status", "classify_risk"],
    },
}

FORBIDDEN_RISK_TERMS = {
    "apply_patch_proposal",
    "rollback_patch_apply",
    "collect_evidence",
    "execute_tool",
    "subprocess",
    "os.system",
    "requests.",
    "httpx.",
    "shutil",
    "git ",
}

FORBIDDEN_ROUTER_NAMES = {
    "protected_core_routes.py",
    "core_routes.py",
    "chat_routes.py",
    "identity_routes.py",
    "awaken_routes.py",
    "verification_routes.py",
    "root_routes.py",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _parse_api_server():
    """Parse api_server.py and return AST tree + source."""
    source = API_SERVER_PATH.read_text(encoding="utf-8")
    tree = ast.parse(source)
    return tree, source


def _find_protected_core_routes(tree):
    """Find all protected/core route functions in the AST."""
    routes = {}
    for node in tree.body:
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue

        for dec in node.decorator_list:
            text = ast.unparse(dec)
            if not text.startswith("app."):
                continue

            method = text.split("(", 1)[0].split(".", 1)[1].upper()
            path = None
            if isinstance(dec, ast.Call) and dec.args:
                try:
                    path = ast.literal_eval(dec.args[0])
                except Exception:
                    pass

            if path and path in ["/", "/identity", "/awaken", "/chat", "/verification/classify"] or \
               (path and path.startswith("/identity/integrity")):
                routes[node.name] = {
                    "method": method,
                    "path": path,
                    "node": node,
                }
    return routes


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
class TestProtectedCoreOpenAPIContract:
    """Lock OpenAPI contract unchanged."""

    def test_openapi_path_and_schema_count(self):
        from aether.interface.api_server import app
        schema = app.openapi()
        paths = len(schema.get("paths", {}))
        schemas = len(schema.get("components", {}).get("schemas", {}))
        assert paths == 302, f"Expected 302 paths, got {paths}"
        assert schemas == 106, f"Expected 106 schemas, got {schemas}"

    def test_protected_core_paths_present(self):
        from aether.interface.api_server import app
        schema = app.openapi()
        protected_paths = [
            "/",
            "/identity/integrity/status",
            "/identity/integrity/initialize",
            "/identity/integrity/verify",
            "/identity",
            "/awaken",
            "/chat",
            "/verification/classify",
        ]
        actual_paths = set(schema.get("paths", {}).keys())
        for path in protected_paths:
            assert path in actual_paths, f"Protected/core path missing: {path}"

    def test_operation_ids_exact(self):
        from aether.interface.api_server import app
        schema = app.openapi()
        for func_name, expected in PROTECTED_CORE_ROUTES.items():
            path = expected["path"]
            method = expected["method"].lower()
            spec = schema["paths"][path]
            op = spec[method]
            assert op.get("operationId") == expected["operation_id"], \
                f"Wrong operationId for {func_name}: {op.get('operationId')}"

    def test_request_body_refs_exact(self):
        from aether.interface.api_server import app
        schema = app.openapi()
        expected_refs = {
            "/chat": "ChatRequest",
            "/verification/classify": "VerificationRequest",
        }
        for path, model_name in expected_refs.items():
            spec = schema["paths"][path]
            op = spec["post"]
            request_body = op.get("requestBody", {})
            content = request_body.get("content", {})
            json_content = content.get("application/json", {})
            schema_ref = json_content.get("schema", {}).get("$ref", "")
            assert f"#/components/schemas/{model_name}" in schema_ref, \
                f"Wrong ref for {path}: {schema_ref}"

    def test_family_counts_unchanged(self):
        from aether.interface.api_server import app
        schema = app.openapi()
        paths = schema.get("paths", {})

        self_count = sum(1 for p in paths if p.startswith("/action/self-modification"))
        guided_count = sum(
            1 for p in paths
            if p.startswith((
                "/action/guided-repair-intake",
                "/action/guided-repair-plan-launcher",
                "/action/guided-bridge-selection-launcher",
                "/action/guided-proposal-review-launcher",
                "/action/guided-proposal-decision-launcher",
            ))
        )
        changelog_count = sum(1 for p in paths if p.startswith("/action/changelog"))
        c2_count = sum(1 for p in paths if p.startswith("/action/final-real-apply-executor"))
        c1_count = sum(
            1 for p in paths
            if p.startswith((
                "/action/approved-dry-run-gate",
                "/action/dry-run-review-gate",
                "/action/real-apply-approval-gate",
                "/action/post-apply-verification-gate",
            ))
        )
        repair_count = sum(1 for p in paths if p.startswith("/action/repair-"))

        assert self_count == 9, f"Expected 9 self-modification paths, got {self_count}"
        assert guided_count == 29, f"Expected 29 guided paths, got {guided_count}"
        assert changelog_count == 4, f"Expected 4 changelog paths, got {changelog_count}"
        assert c2_count == 6, f"Expected 6 C2 paths, got {c2_count}"
        assert c1_count == 24, f"Expected 24 C1 paths, got {c1_count}"
        assert repair_count == 43, f"Expected 43 repair paths, got {repair_count}"


class TestProtectedCoreRoutePlacement:
    """Lock protected/core routes remain in api_server.py."""

    def test_api_server_has_exactly_8_app_routes(self):
        tree, _ = _parse_api_server()
        routes = []
        for node in tree.body:
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            for dec in node.decorator_list:
                text = ast.unparse(dec)
                if text.startswith("app."):
                    routes.append(node.name)
        assert len(routes) == 8, f"Expected 8 @app routes, got {len(routes)}"

    def test_api_server_has_exactly_23_include_router_calls(self):
        tree, _ = _parse_api_server()
        calls = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and ast.unparse(node.func) == "app.include_router":
                calls.append(ast.unparse(node))
        assert len(calls) == 23, f"Expected 23 include_router calls, got {len(calls)}"

    def test_no_action_routes_remain_in_api_server(self):
        tree, _ = _parse_api_server()
        action_routes = []
        for node in tree.body:
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            for dec in node.decorator_list:
                text = ast.unparse(dec)
                if text.startswith("app.") and "/action/" in text:
                    action_routes.append(node.name)
        assert not action_routes, f"Action routes should not remain in api_server.py: {action_routes}"

    def test_all_protected_core_routes_remain(self):
        tree, _ = _parse_api_server()
        routes = _find_protected_core_routes(tree)
        expected_funcs = set(PROTECTED_CORE_ROUTES.keys())
        actual_funcs = set(routes.keys())
        assert actual_funcs == expected_funcs, \
            f"Missing: {expected_funcs - actual_funcs}, Extra: {actual_funcs - expected_funcs}"

    def test_no_protected_core_router_files_exist(self):
        for name in FORBIDDEN_ROUTER_NAMES:
            path = ROUTER_DIR / name
            assert not path.exists(), f"Protected/core router should not exist: {name}"

    def test_self_modification_router_exists(self):
        path = ROUTER_DIR / "self_modification_routes.py"
        assert path.exists(), "self_modification_routes.py should exist"

    def test_guided_launcher_router_exists(self):
        path = ROUTER_DIR / "guided_launcher_routes.py"
        assert path.exists(), "guided_launcher_routes.py should exist"


class TestProtectedCoreRouteBehavior:
    """Lock exact protected/core route behavior."""

    def test_exact_function_names_and_paths(self):
        tree, _ = _parse_api_server()
        routes = _find_protected_core_routes(tree)
        for func_name, expected in PROTECTED_CORE_ROUTES.items():
            assert func_name in routes, f"Route {func_name} not found"
            actual = routes[func_name]
            assert actual["method"] == expected["method"], \
                f"{func_name}: Expected {expected['method']}, got {actual['method']}"
            assert actual["path"] == expected["path"], \
                f"{func_name}: Expected path {expected['path']}, got {actual['path']}"

    def test_signatures_match_expected(self):
        tree, source = _parse_api_server()
        routes = _find_protected_core_routes(tree)
        for func_name, expected in PROTECTED_CORE_ROUTES.items():
            if func_name not in routes:
                continue
            node = routes[func_name]["node"]
            args = ast.unparse(node.args)
            if expected["expected_signature"]:
                assert args == expected["expected_signature"], \
                    f"{func_name}: Expected '{expected['expected_signature']}', got '{args}'"

    def test_return_count_profile(self):
        tree, _ = _parse_api_server()
        routes = _find_protected_core_routes(tree)
        for func_name, expected in PROTECTED_CORE_ROUTES.items():
            if func_name not in routes:
                continue
            node = routes[func_name]["node"]
            returns = [n for n in ast.walk(node) if isinstance(n, ast.Return) and n.value is not None]
            assert len(returns) == expected["expected_return_count"], \
                f"{func_name}: Expected {expected['expected_return_count']} returns, got {len(returns)}"

    def test_control_flow_profile(self):
        tree, _ = _parse_api_server()
        routes = _find_protected_core_routes(tree)
        for func_name, expected in PROTECTED_CORE_ROUTES.items():
            if func_name not in routes:
                continue
            node = routes[func_name]["node"]
            flows = [
                type(n).__name__
                for n in ast.walk(node)
                if isinstance(n, (ast.If, ast.For, ast.While, ast.Try, ast.With, ast.Match, ast.Raise))
            ]
            for expected_flow in expected["expected_flows"]:
                assert expected_flow in flows, \
                    f"{func_name}: Expected control flow {expected_flow} not found. Flows: {flows}"
            for flow in flows:
                if flow not in expected["expected_flows"]:
                    pytest.fail(f"{func_name}: Unexpected control flow {flow}")

    def test_call_profiles_preserved(self):
        tree, source = _parse_api_server()
        routes = _find_protected_core_routes(tree)
        for func_name, expected in PROTECTED_CORE_ROUTES.items():
            if func_name not in routes:
                continue
            node = routes[func_name]["node"]
            calls = [
                ast.unparse(c.func)
                for c in ast.walk(node)
                if isinstance(c, ast.Call)
                and not ast.unparse(c.func).startswith("app.")
            ]
            for substr in expected["expected_call_substrings"]:
                found = any(substr in call for call in calls)
                assert found, f"{func_name}: Expected call containing '{substr}' not found in {calls}"


class TestProtectedCoreImportBoundary:
    """Lock import boundary unchanged."""

    def test_no_direct_action_imports(self):
        tree, _ = _parse_api_server()
        action_imports = []
        for node in tree.body:
            if isinstance(node, ast.ImportFrom):
                if node.module and node.module.startswith("aether.action.") and not node.module.startswith("aether.action.services."):
                    action_imports.append(node.module)
        assert not action_imports, f"No direct action imports should remain: {action_imports}"

    def test_service_import_includes_handle_awaken(self):
        tree, _ = _parse_api_server()
        service_imports = []
        for node in tree.body:
            if isinstance(node, ast.ImportFrom):
                if node.module and node.module.startswith("aether.action.services."):
                    service_imports.append((node.module, [a.name for a in node.names]))
        found = any(
            "runtime_lifecycle_service" in mod and "handle_awaken" in names
            for mod, names in service_imports
        )
        assert found, "Expected handle_awaken service import"

    def test_core_runtime_imports_present(self):
        tree, _ = _parse_api_server()
        imports = []
        for node in tree.body:
            if isinstance(node, ast.ImportFrom):
                imports.append((node.module or "", [a.name for a in node.names]))

        # Check key imports exist
        core_imports = {
            "aether.identity.loader": ["identity_preview"],
            "aether.identity.guard": ["initialize_identity_guard", "verify_identity_integrity", "identity_guard_status"],
            "aether.time.clock": ["time_state"],
            "aether.memory.timeline.recorder": ["record_event", "search_events"],
            "aether.core.runtime": ["runtime"],
            "aether.memory.graph.store": ["add_edge"],
            "aether.verification.risk": ["classify_risk"],
        }
        for mod, expected_names in core_imports.items():
            found = any(
                item[0] == mod and all(n in item[1] for n in expected_names)
                for item in imports
            )
            assert found, f"Missing import: {mod} with {expected_names}"

    def test_api_models_imports_include_protected_core_models(self):
        tree, _ = _parse_api_server()
        api_models_import = None
        for node in tree.body:
            if isinstance(node, ast.ImportFrom) and node.module == "aether.interface.api_models":
                api_models_import = [a.name for a in node.names]
                break
        assert api_models_import is not None, "api_models import missing"
        expected_models = [
            "ChatRequest",
            "ChatResponse",
            "VerificationRequest",
            "IdentityIntegrityStatusResponse",
            "InitializeIdentityGuardResponse",
            "VerifyIdentityIntegrityResponse",
        ]
        for model in expected_models:
            assert model in api_models_import, f"Missing api_models import: {model}"


class TestProtectedCoreNoInvocation:
    """Self-check: verify this test module never invokes endpoints or functions."""

    def test_no_testclient_or_endpoint_invocation(self):
        source = Path(__file__).read_text(encoding="utf-8")
        tree = ast.parse(source)

        forbidden_modules = {"fastapi.testclient", "requests", "httpx", "subprocess"}
        forbidden_names = {
            "TestClient",
            "root",
            "get_identity_integrity_status",
            "post_initialize_identity_guard",
            "post_verify_identity_integrity",
            "identity",
            "awaken",
            "chat",
            "classify_verification_risk",
            "runtime.process_chat",
            "handle_awaken",
            "identity_preview",
            "identity_guard_status",
            "initialize_identity_guard",
            "verify_identity_integrity",
            "classify_risk",
            "record_event",
            "add_edge",
        }

        bad_imports = []
        bad_calls = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                if node.module in forbidden_modules:
                    bad_imports.append((node.module, [a.name for a in node.names]))
                for alias in node.names:
                    if alias.name == "TestClient":
                        bad_imports.append((node.module, [alias.name]))

            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name in forbidden_modules or alias.name.endswith(".testclient"):
                        bad_imports.append(("import", alias.name))

            if isinstance(node, ast.Call):
                func = ast.unparse(node.func)
                if func in forbidden_names or func.endswith(".TestClient"):
                    bad_calls.append(func)
                if isinstance(node.func, ast.Attribute) and node.func.attr in {"get", "post", "put", "delete", "patch"}:
                    receiver = ast.unparse(node.func.value)
                    if receiver in {"client", "test_client", "api_client", "self_client"}:
                        bad_calls.append(func)

        assert not bad_imports, f"Forbidden imports found: {bad_imports}"
        assert not bad_calls, f"Forbidden calls found: {bad_calls}"


class TestProtectedCoreStaticRisk:
    """Lock static risk: no high-risk terms in protected/core route bodies."""

    def test_no_high_risk_terms_in_protected_core_routes(self):
        tree, source = _parse_api_server()
        routes = _find_protected_core_routes(tree)

        for func_name, node in routes.items():
            route_source = ast.get_source_segment(source, node) or ""
            for term in FORBIDDEN_RISK_TERMS:
                assert term not in route_source, \
                    f"{func_name}: Forbidden term '{term}' found in route body"
