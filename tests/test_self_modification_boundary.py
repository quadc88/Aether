"""AST/OpenAPI-only boundary coverage for Self-Modification routes in api_server.py.

This test locks the current direct-action pass-through behavior of all 9
Self-Modification routes WITHOUT invoking any endpoint or action function.
"""
import ast
import json
import subprocess
import sys
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
API_SERVER_PATH = PROJECT_ROOT / "aether" / "interface" / "api_server.py"
ROUTER_PATH = PROJECT_ROOT / "aether" / "interface" / "routers" / "self_modification_routes.py"
SELF_MODIFICATION_MODULE_PATH = PROJECT_ROOT / "aether" / "action" / "self_modification_cycle.py"
API_MODELS_PATH = PROJECT_ROOT / "aether" / "interface" / "api_models.py"

SELF_MODIFICATION_ENDPOINTS = {
    ("POST", "/action/self-modification/create"): {
        "route_function": "create_self_modification",
        "action_function": "create_self_modification_session",
        "operation_id": "create_self_modification_action_self_modification_create_post",
        "wrapper_key": "session",
        "request_model": "SelfModificationCreateRequest",
        "expected_args": [
            "request.goal",
            "request.target_path",
            "request.proposed_change_summary",
            "request.proposed_excerpt",
            "request.reason",
            "request.original_excerpt",
            "request.create_approval_if_required",
            "request.metadata",
        ],
    },
    ("POST", "/action/self-modification/review"): {
        "route_function": "review_self_modification",
        "action_function": "review_self_modification_session",
        "operation_id": "review_self_modification_action_self_modification_review_post",
        "wrapper_key": "session",
        "request_model": "SelfModificationReviewRequest",
        "expected_args": [
            "request.session_id",
            "request.decision",
            "request.review_reason",
            "request.reviewer",
            "request.metadata",
        ],
    },
    ("POST", "/action/self-modification/dry-run"): {
        "route_function": "dry_run_self_modification",
        "action_function": "dry_run_self_modification_session",
        "operation_id": "dry_run_self_modification_action_self_modification_dry_run_post",
        "wrapper_key": "session",
        "request_model": "SelfModificationActionRequest",
        "expected_args": [
            "request.session_id",
            "request.metadata",
        ],
    },
    ("POST", "/action/self-modification/apply"): {
        "route_function": "apply_self_modification",
        "action_function": "apply_self_modification_session",
        "operation_id": "apply_self_modification_action_self_modification_apply_post",
        "wrapper_key": "session",
        "request_model": "SelfModificationActionRequest",
        "expected_args": [
            "request.session_id",
            "request.metadata",
        ],
    },
    ("POST", "/action/self-modification/rollback"): {
        "route_function": "rollback_self_modification",
        "action_function": "rollback_self_modification_session",
        "operation_id": "rollback_self_modification_action_self_modification_rollback_post",
        "wrapper_key": "session",
        "request_model": "SelfModificationActionRequest",
        "expected_args": [
            "request.session_id",
            "request.metadata",
        ],
    },
    ("GET", "/action/self-modification/status"): {
        "route_function": "get_self_modification_status",
        "action_function": "self_modification_status",
        "operation_id": "get_self_modification_status_action_self_modification_status_get",
        "wrapper_key": "self_modification",
        "request_model": None,
        "expected_args": [],
    },
    ("GET", "/action/self-modification/list"): {
        "route_function": "list_self_modification",
        "action_function": "list_self_modification_sessions",
        "operation_id": "list_self_modification_action_self_modification_list_get",
        "wrapper_key": "sessions",
        "request_model": None,
        "expected_args": [
            "status",
            "target_path",
            "limit",
        ],
    },
    ("GET", "/action/self-modification/{session_id}/summary"): {
        "route_function": "summarize_self_modification",
        "action_function": "summarize_self_modification_session",
        "operation_id": "summarize_self_modification_action_self_modification__session_id__summary_get",
        "wrapper_key": "summary",
        "request_model": None,
        "expected_args": [
            "session_id",
        ],
    },
    ("GET", "/action/self-modification/{session_id}"): {
        "route_function": "get_self_modification",
        "action_function": "get_self_modification_session",
        "operation_id": "get_self_modification_action_self_modification__session_id__get",
        "wrapper_key": "session",
        "request_model": None,
        "expected_args": [
            "session_id",
        ],
    },
}

FORBIDDEN_RISK_TERMS = {
    "collect_evidence",
    "execute_tool",
    "subprocess",
    "os.system",
    "requests.",
    "httpx.",
    "shutil",
    "git ",
    "git.",
}

EXPECTED_HIGH_RISK_TERMS = {
    "apply_patch_proposal",
    "rollback_patch_apply",
    "write_text",
    "Path(",
    "create_patch_proposal",
    "review_patch_proposal",
    "json.dumps",
    "Path(",
}

FORBIDDEN_ROUTER_NAMES = {
    "self_modification_router",
    "guided_launcher_router",
    "changelog_router",
    "final_real_apply_executor_router",
    "post_chain_c1_router",
    "repair_router",
    "code_review_router",
    "mutation_log_router",
    "proposal_console_router",
    "file_router",
    "patch_router",
    "approval_router",
    "dry_run_router",
    "simulation_router",
    "verification_apply_gate_router",
    "authorization_execution_gate_router",
    "executor_router",
    "evidence_router",
    "verification_plan_router",
    "tool_registry_plan_router",
    "memory_router",
    "tool_executor_router",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _parse_router():
    """Parse self_modification_routes.py and return AST tree + source."""
    source = ROUTER_PATH.read_text(encoding="utf-8")
    tree = ast.parse(source)
    return tree, source


def _parse_api_server_only():
    """Parse api_server.py and return AST tree + source."""
    source = API_SERVER_PATH.read_text(encoding="utf-8")
    tree = ast.parse(source)
    return tree, source


def _find_self_modification_routes(tree):
    """Find all Self-Modification route functions in the AST."""
    routes = {}
    for node in tree.body:
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        for dec in node.decorator_list:
            text = ast.unparse(dec)
            if text.startswith("self_modification_router.") and "/action/self-modification" in text:
                method = text.split("(", 1)[0].split(".", 1)[1].upper()
                path = None
                if isinstance(dec, ast.Call) and dec.args:
                    try:
                        path = ast.literal_eval(dec.args[0])
                    except Exception:
                        pass
                if path:
                    routes[(method, path)] = node
    return routes


def _get_route_info(route_node):
    """Extract route information from an AST function node."""
    returns = [n for n in ast.walk(route_node) if isinstance(n, ast.Return) and n.value is not None]
    value = returns[0].value if len(returns) == 1 else None
    calls = [
        ast.unparse(c.func)
        for c in ast.walk(route_node)
        if isinstance(c, ast.Call)
        and not ast.unparse(c.func).startswith("self_modification_router.")
        and not ast.unparse(c.func).startswith("app.")
    ]
    flow = [
        type(n).__name__
        for n in ast.walk(route_node)
        if isinstance(n, (ast.If, ast.For, ast.While, ast.Try, ast.With, ast.Match))
    ]
    is_wrapper = isinstance(value, ast.Dict) and any(
        isinstance(k, ast.Constant) and k.value == "name"
        and isinstance(v, ast.Constant) and v.value == "Aether"
        for k, v in zip(value.keys, value.values)
    )
    return {
        "calls": calls,
        "flow": flow,
        "wrapped": is_wrapper,
        "return_count": len(returns),
        "return_value": ast.unparse(value) if value is not None else None,
    }


def _check_no_invocation_in_test():
    """Verify this test module does not invoke endpoints or action functions."""
    source = Path(__file__).read_text(encoding="utf-8")
    tree = ast.parse(source)

    forbidden_names = {
        "create_self_modification_session",
        "review_self_modification_session",
        "dry_run_self_modification_session",
        "apply_self_modification_session",
        "rollback_self_modification_session",
        "self_modification_status",
        "list_self_modification_sessions",
        "get_self_modification_session",
        "summarize_self_modification_session",
        "apply_patch_proposal",
        "rollback_patch_apply",
        "TestClient",
    }

    bad_imports = []
    bad_calls = []

    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            if node.module == "fastapi.testclient":
                bad_imports.append((node.module, [a.name for a in node.names]))
            if node.module and "self_modification" in node.module.lower():
                bad_imports.append((node.module, [a.name for a in node.names]))
            for alias in node.names:
                if alias.name == "TestClient":
                    bad_imports.append((node.module or "", [alias.name]))

        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == "fastapi.testclient" or alias.name.endswith(".testclient"):
                    bad_imports.append(("import", alias.name))

        if isinstance(node, ast.Call):
            func = ast.unparse(node.func)
            if func in forbidden_names:
                bad_calls.append(func)
            if isinstance(node.func, ast.Attribute) and node.func.attr in {"get", "post", "put", "delete", "patch"}:
                receiver = ast.unparse(node.func.value)
                if receiver in {"client", "test_client", "api_client", "self_client"}:
                    bad_calls.append(func)

    assert not bad_imports, f"Forbidden imports found: {bad_imports}"
    assert not bad_calls, f"Forbidden calls found: {bad_calls}"


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
class TestOpenAPIContract:
    """Lock OpenAPI contract unchanged."""

    def test_openapi_path_and_schema_count(self):
        from aether.interface.api_server import app
        schema = app.openapi()
        paths = len(schema.get("paths", {}))
        schemas = len(schema.get("components", {}).get("schemas", {}))
        assert paths == 306, f"Expected 306 paths, got {paths}"
        assert schemas == 112, f"Expected 112 schemas, got {schemas}"

    def test_self_modification_paths_present(self):
        from aether.interface.api_server import app
        schema = app.openapi()
        self_paths = sorted(
            p for p in schema.get("paths", {})
            if p.startswith("/action/self-modification")
        )
        assert len(self_paths) == 9, f"Expected 9 self-modification paths, got {len(self_paths)}"
        expected_paths = {
            "/action/self-modification/create",
            "/action/self-modification/review",
            "/action/self-modification/dry-run",
            "/action/self-modification/apply",
            "/action/self-modification/rollback",
            "/action/self-modification/status",
            "/action/self-modification/list",
            "/action/self-modification/{session_id}/summary",
            "/action/self-modification/{session_id}",
        }
        actual_paths = set(self_paths)
        assert actual_paths == expected_paths, f"Missing or extra paths: {actual_paths ^ expected_paths}"

    def test_operation_ids_exact(self):
        from aether.interface.api_server import app
        schema = app.openapi()
        for (method, path), info in SELF_MODIFICATION_ENDPOINTS.items():
            spec = schema["paths"][path]
            op = spec[method.lower()]
            assert op.get("operationId") == info["operation_id"], \
                f"Wrong operationId for {method} {path}: {op.get('operationId')}"

    def test_request_body_refs_exact(self):
        from aether.interface.api_server import app
        schema = app.openapi()
        post_endpoints = {
            ("POST", "/action/self-modification/create"): "SelfModificationCreateRequest",
            ("POST", "/action/self-modification/review"): "SelfModificationReviewRequest",
            ("POST", "/action/self-modification/dry-run"): "SelfModificationActionRequest",
            ("POST", "/action/self-modification/apply"): "SelfModificationActionRequest",
            ("POST", "/action/self-modification/rollback"): "SelfModificationActionRequest",
        }
        for (method, path), model_name in post_endpoints.items():
            spec = schema["paths"][path]
            op = spec[method.lower()]
            request_body = op.get("requestBody", {})
            content = request_body.get("content", {})
            json_content = content.get("application/json", {})
            schema_ref = json_content.get("schema", {}).get("$ref", "")
            assert f"#/components/schemas/{model_name}" in schema_ref, \
                f"Wrong ref for {method} {path}: {schema_ref}"

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


class TestRoutePlacement:
    """Lock Self-Modification routes in self_modification_routes.py with router.* decorators."""

    def test_self_modification_router_exists(self):
        assert ROUTER_PATH.exists(), "self_modification_routes.py should exist"

    def test_self_modification_router_definition(self):
        source = ROUTER_PATH.read_text(encoding="utf-8")
        assert "self_modification_router = APIRouter()" in source, \
            "self_modification_routes.py should define self_modification_router = APIRouter()"

    def test_self_modification_router_import_in_api_server(self):
        source = API_SERVER_PATH.read_text(encoding="utf-8")
        assert "from aether.interface.routers.self_modification_routes import self_modification_router" in source, \
            "api_server.py should import self_modification_router"

    def test_self_modification_router_include_in_api_server(self):
        source = API_SERVER_PATH.read_text(encoding="utf-8")
        assert "app.include_router(self_modification_router, prefix=\"\")" in source, \
            "api_server.py should include self_modification_router with prefix=\"\""

    def test_no_self_modification_routes_in_api_server(self):
        tree, _ = _parse_api_server_only()
        routes = []
        for node in tree.body:
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            for dec in node.decorator_list:
                text = ast.unparse(dec)
                if text.startswith("app.") and "/action/self-modification" in text:
                    routes.append(node.name)
        assert not routes, f"Self-Modification routes should not remain in api_server.py: {routes}"

    def test_router_decorators_used(self):
        tree, _ = _parse_router()
        routes = _find_self_modification_routes(tree)
        assert len(routes) == 9, f"Expected 9 routes, got {len(routes)}"
        for (method, path), node in routes.items():
            has_router_decorator = False
            for dec in node.decorator_list:
                text = ast.unparse(dec)
                if "self_modification_router" in text and "/action/self-modification" in text:
                    has_router_decorator = True
                    break
            assert has_router_decorator, f"Route {node.name} missing self_modification_router.* decorator"


class TestRouteBehavior:
    """Lock exact route behavior: single-return wrapped pass-throughs."""

    def test_all_routes_are_wrapped_pass_throughs(self):
        tree, _ = _parse_router()
        routes = _find_self_modification_routes(tree)
        assert len(routes) == 9, f"Expected 9 routes, got {len(routes)}"

        for (method, path), node in routes.items():
            info = _get_route_info(node)
            assert info["return_count"] == 1, \
                f"{node.name}: Expected 1 return, got {info['return_count']}"
            assert info["wrapped"], \
                f"{node.name}: Expected wrapped Aether dict return"
            assert not info["flow"], \
                f"{node.name}: Unexpected control flow: {info['flow']}"

            # Verify call matches expected action function
            endpoint_info = SELF_MODIFICATION_ENDPOINTS[(method, path)]
            assert info["calls"] == [endpoint_info["action_function"]], \
                f"{node.name}: Wrong calls: {info['calls']}"

    def test_signatures_match_expected(self):
        tree, source = _parse_router()
        routes = _find_self_modification_routes(tree)

        expected_signatures = {
            "create_self_modification": "request: SelfModificationCreateRequest",
            "review_self_modification": "request: SelfModificationReviewRequest",
            "dry_run_self_modification": "request: SelfModificationActionRequest",
            "apply_self_modification": "request: SelfModificationActionRequest",
            "rollback_self_modification": "request: SelfModificationActionRequest",
            "get_self_modification_status": "",
            "list_self_modification": "status: str | None=None, target_path: str | None=None, limit: int=50",
            "summarize_self_modification": "session_id: str",
            "get_self_modification": "session_id: str",
        }

        for node in tree.body:
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            for dec in node.decorator_list:
                text = ast.unparse(dec)
                if text.startswith("app.") and "/action/self-modification" in text:
                    args = ast.unparse(node.args)
                    expected = expected_signatures.get(node.name, "")
                    assert args == expected, \
                        f"{node.name}: Expected '{expected}', got '{args}'"
                    break

    def test_call_argument_order(self):
        tree, _ = _parse_router()
        routes = _find_self_modification_routes(tree)

        for (method, path), node in routes.items():
            endpoint_info = SELF_MODIFICATION_ENDPOINTS[(method, path)]
            expected_args = endpoint_info["expected_args"]

            if not expected_args:
                # No args expected - function call should have no arguments
                for c in ast.walk(node):
                    if isinstance(c, ast.Call):
                        func = ast.unparse(c.func)
                        if func == endpoint_info["action_function"]:
                            assert len(c.args) == 0, \
                                f"{node.name}: Expected 0 args, got {len(c.args)}"
                            assert len(c.keywords) == 0, \
                                f"{node.name}: Expected 0 keyword args"
                            break
                continue

            # Verify argument order in the return statement
            source = API_SERVER_PATH.read_text(encoding="utf-8")
            # Find the return statement and extract the call
            for n in ast.walk(node):
                if isinstance(n, ast.Return) and n.value:
                    ret_str = ast.unparse(n.value)
                    # Check that each expected arg appears in order
                    last_pos = -1
                    for expected_arg in expected_args:
                        pos = ret_str.find(expected_arg)
                        assert pos > last_pos, \
                            f"{node.name}: Expected arg '{expected_arg}' not in correct order"
                        last_pos = pos
                    break


class TestImportBoundary:
    """Lock import boundary: router imports self_modification_cycle, api_server imports router."""

    def test_router_exactly_self_modification_cycle_import(self):
        tree, _ = _parse_router()
        self_mod_imports = []
        for node in tree.body:
            if isinstance(node, ast.ImportFrom):
                if node.module and "self_modification" in node.module.lower():
                    if not node.module.startswith("aether.action.self_modification_cycle"):
                        pytest.fail(f"Unexpected self_modification import in router: {node.module}")
                    names = [a.name for a in node.names]
                    self_mod_imports.extend(names)

        expected_names = {
            "create_self_modification_session",
            "review_self_modification_session",
            "dry_run_self_modification_session",
            "apply_self_modification_session",
            "rollback_self_modification_session",
            "self_modification_status",
            "list_self_modification_sessions",
            "get_self_modification_session",
            "summarize_self_modification_session",
        }
        actual_names = set(self_mod_imports)
        assert actual_names == expected_names, \
            f"Router import mismatch. Missing: {expected_names - actual_names}, Extra: {actual_names - expected_names}"

    def test_api_server_no_self_modification_cycle_import(self):
        tree, _ = _parse_api_server_only()
        for node in tree.body:
            if isinstance(node, ast.ImportFrom):
                if node.module and node.module.startswith("aether.action.self_modification_cycle"):
                    pytest.fail("api_server.py should no longer import aether.action.self_modification_cycle")

    def test_api_server_imports_self_modification_router(self):
        api_tree, _ = _parse_api_server_only()
        router_imports = []
        for node in api_tree.body:
            if isinstance(node, ast.ImportFrom):
                if node.module and "self_modification" in node.module.lower():
                    if "routers" in node.module:
                        router_imports.append(node.module)
        assert len(router_imports) == 1, f"Expected 1 self_modification router import, got {len(router_imports)}"
        assert "aether.interface.routers.self_modification_routes" in router_imports[0], \
            f"Expected import from aether.interface.routers.self_modification_routes, got {router_imports[0]}"

    def test_api_server_includes_self_modification_router(self):
        api_tree, _ = _parse_api_server_only()
        include_calls = []
        for node in ast.walk(api_tree):
            if isinstance(node, ast.Call) and ast.unparse(node.func) == "app.include_router":
                include_calls.append(ast.unparse(node))
        self_mod_includes = [c for c in include_calls if "self_modification_router" in c]
        assert len(self_mod_includes) == 1, f"Expected 1 self_modification_router include, got {len(self_mod_includes)}"
        assert "prefix=''" in self_mod_includes[0] or 'prefix=""' in self_mod_includes[0], \
            f"Expected prefix='' in include_router call, got {self_mod_includes[0]}"

    def test_routers_unchanged(self):
        """Verify existing router imports are still present."""
        api_tree, _ = _parse_api_server_only()
        router_modules = []
        for node in api_tree.body:
            if isinstance(node, ast.ImportFrom):
                if node.module and node.module.startswith("aether.interface.routers."):
                    router_modules.append(node.module.split(".")[-1])

        expected_routers = [
            "guided_launcher_routes",
            "changelog_routes",
            "final_real_apply_executor_routes",
            "post_chain_c1_routes",
            "repair_routes",
            "code_review_routes",
            "mutation_log_routes",
            "proposal_console_routes",
            "file_routes",
            "patch_routes",
            "approval_routes",
            "dry_run_routes",
            "simulation_routes",
            "verification_apply_gate_routes",
            "authorization_execution_gate_routes",
            "executor_routes",
            "evidence_routes",
            "verification_plan_routes",
            "tool_registry_plan_routes",
            "memory_routes",
            "tool_executor_routes",
        ]
        for expected in expected_routers:
            assert expected in " ".join(router_modules), f"Router module {expected} missing from imports"


class TestNoInvocation:
    """Self-check: verify this test module never invokes endpoints or actions."""

    def test_no_endpoint_invocation(self):
        _check_no_invocation_in_test()


class TestStaticRisk:
    """Lock static risk profile of self_modification_cycle module."""

    def test_module_unchanged_in_git(self):
        result = subprocess.run(
            ["git", "diff", "--quiet", "HEAD", "--", str(SELF_MODIFICATION_MODULE_PATH)],
            capture_output=True,
        )
        assert result.returncode == 0, \
            f"self_modification_cycle.py was modified in git diff"

    def test_function_inventory_locked(self):
        tree = ast.parse(SELF_MODIFICATION_MODULE_PATH.read_text(encoding="utf-8"))
        functions = [node.name for node in tree.body if isinstance(node, ast.FunctionDef)]
        expected = {
            "load_aether_config",
            "get_self_modification_dir",
            "get_self_modification_path",
            "load_self_modification_sessions",
            "save_self_modification_sessions",
            "_save",
            "create_self_modification_session",
            "get_self_modification_session",
            "list_self_modification_sessions",
            "self_modification_status",
            "review_self_modification_session",
            "dry_run_self_modification_session",
            "apply_self_modification_session",
            "rollback_self_modification_session",
            "summarize_self_modification_session",
        }
        assert set(functions) == expected, \
            f"Function inventory changed. Missing: {expected - set(functions)}, Extra: {set(functions) - expected}"

    def test_expected_high_risk_terms_present(self):
        source = SELF_MODIFICATION_MODULE_PATH.read_text(encoding="utf-8")
        for term in EXPECTED_HIGH_RISK_TERMS:
            assert term in source, f"Expected high-risk term '{term}' not found in module"

    def test_forbidden_terms_absent(self):
        source = SELF_MODIFICATION_MODULE_PATH.read_text(encoding="utf-8")
        for term in FORBIDDEN_RISK_TERMS:
            assert term not in source, f"Forbidden term '{term}' found in module"
