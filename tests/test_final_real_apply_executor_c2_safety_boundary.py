"""Tests-only safety boundary for the C2 final real-apply executor."""

from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from aether.action import final_real_apply_executor
from aether.interface.api_server import app


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REAL_DATA_ROOT = Path("/home/aether/data")
OPENAPI_BASELINE_PATH = Path("/tmp/aether_82AJ_openapi_before.json")
EXPECTED_OPENAPI_SHA256 = (
    "9ac4163f007a9b8a6a9ad14f2c21836b3f17c460505301d0c33c57c102a3b9bc"
)

C2_ENDPOINTS = {
    ("POST", "/action/final-real-apply-executor/open"): (
        "open_final_real_apply_executor_action",
        "handle_open_final_real_apply_executor",
        "open_final_real_apply_executor",
        "open_final_real_apply_executor_action_action_final_real_apply_executor_open_post",
        "record",
    ),
    ("POST", "/action/final-real-apply-executor/execute"): (
        "execute_final_real_apply_action",
        "handle_execute_final_real_apply",
        "execute_final_real_apply",
        "execute_final_real_apply_action_action_final_real_apply_executor_execute_post",
        "record",
    ),
    ("GET", "/action/final-real-apply-executor/status"): (
        "get_final_real_apply_executor_status_action",
        "handle_get_final_real_apply_executor_status",
        "final_real_apply_executor_status",
        "get_final_real_apply_executor_status_action_action_final_real_apply_executor_status_get",
        "final_real_apply_executor",
    ),
    ("GET", "/action/final-real-apply-executor/list"): (
        "list_final_real_apply_executor_action",
        "handle_list_final_real_apply_executor_records",
        "list_final_real_apply_executor_records",
        "list_final_real_apply_executor_action_action_final_real_apply_executor_list_get",
        "records",
    ),
    ("GET", "/action/final-real-apply-executor/{record_id}/summary"): (
        "summarize_final_real_apply_executor_action",
        "handle_summarize_final_real_apply_executor",
        "summarize_final_real_apply_executor",
        "summarize_final_real_apply_executor_action_action_final_real_apply_executor__record_id__summary_get",
        "summary",
    ),
    ("GET", "/action/final-real-apply-executor/{record_id}"): (
        "get_final_real_apply_executor_action",
        "handle_get_final_real_apply_executor_record",
        "get_final_real_apply_executor_record",
        "get_final_real_apply_executor_action_action_final_real_apply_executor__record_id__get",
        "record",
    ),
}

PROTECTED_ENDPOINTS = {
    ("GET", "/"): "root__get",
    ("GET", "/identity"): "identity_identity_get",
    ("GET", "/identity/integrity/status"):
        "get_identity_integrity_status_identity_integrity_status_get",
    ("POST", "/identity/integrity/initialize"):
        "post_initialize_identity_guard_identity_integrity_initialize_post",
    ("POST", "/identity/integrity/verify"):
        "post_verify_identity_integrity_identity_integrity_verify_post",
    ("POST", "/chat"): "chat_chat_post",
    ("POST", "/awaken"): "awaken_awaken_post",
    ("POST", "/verification/classify"):
        "classify_verification_risk_verification_classify_post",
}

API_CASES = (
    (
        "POST",
        "/action/final-real-apply-executor/open",
        {
            "source_type": "invalid_82AJ_source",
            "source_id": "missing_82AJ_gate",
            "metadata": {"milestone": "82AJ"},
        },
        "record",
    ),
    (
        "POST",
        "/action/final-real-apply-executor/execute",
        {
            "executor_record_id": "missing_82AJ_executor",
            "metadata": {"milestone": "82AJ"},
        },
        "record",
    ),
    (
        "GET",
        "/action/final-real-apply-executor/status",
        None,
        "final_real_apply_executor",
    ),
    ("GET", "/action/final-real-apply-executor/list", None, "records"),
    (
        "GET",
        "/action/final-real-apply-executor/missing_82AJ/summary",
        None,
        "summary",
    ),
    (
        "GET",
        "/action/final-real-apply-executor/missing_82AJ",
        None,
        "record",
    ),
)

WATCHED_REAL_ROOTS = (
    REAL_DATA_ROOT / "private",
    REAL_DATA_ROOT / "timeline",
    REAL_DATA_ROOT / "graph_db",
    REAL_DATA_ROOT / "vector_db",
    REAL_DATA_ROOT / "vault",
    REAL_DATA_ROOT / "logs",
)

C1_SERVICE_FILES = (
    "approved_dry_run_gate_service.py",
    "dry_run_review_gate_service.py",
    "real_apply_approval_gate_service.py",
    "post_apply_verification_gate_service.py",
)


def _canonical_openapi(schema: dict) -> bytes:
    return json.dumps(
        schema, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def _fingerprint(root: Path) -> tuple:
    if not root.exists():
        return ("missing",)
    entries = []
    for path in sorted(root.rglob("*")):
        try:
            relative = str(path.relative_to(root))
            if path.is_file():
                data = path.read_bytes()
                entries.append(
                    ("file", relative, len(data), hashlib.sha256(data).hexdigest())
                )
            elif path.is_dir():
                entries.append(("dir", relative))
        except FileNotFoundError:
            continue
    return tuple(entries)


def _real_fingerprints() -> dict[str, tuple]:
    return {str(root): _fingerprint(root) for root in WATCHED_REAL_ROOTS}


def _call_name(call: ast.Call) -> str:
    return ast.unparse(call.func)


@pytest.fixture(scope="module", autouse=True)
def real_runtime_roots_unchanged():
    """Prove the focused C2 module cannot drift real Aether persistence."""

    before = _real_fingerprints()
    yield
    assert _real_fingerprints() == before


@pytest.fixture
def denied_c2_api(
    monkeypatch: pytest.MonkeyPatch,
    isolated_test_config: dict,
    isolated_test_paths: dict[str, Path],
):
    """Expose C2 only under isolated persistence and a fail-closed apply guard."""

    apply_calls = []

    def deny_real_apply(*args, **kwargs):
        apply_calls.append((args, kwargs))
        raise AssertionError("REAL_APPLY_DENIED_IN_82AJ_TEST")

    monkeypatch.setattr(
        final_real_apply_executor, "apply_patch_proposal", deny_real_apply
    )
    monkeypatch.setattr(
        final_real_apply_executor,
        "load_aether_config",
        lambda *_args, **_kwargs: isolated_test_config,
    )

    executor_dir = final_real_apply_executor.get_final_real_apply_executor_dir()
    assert executor_dir.is_relative_to(isolated_test_paths["private_dir"])
    assert not executor_dir.resolve().is_relative_to(REAL_DATA_ROOT.resolve())
    assert not executor_dir.resolve().is_relative_to(PROJECT_ROOT.resolve())

    yield SimpleNamespace(client=TestClient(app), apply_calls=apply_calls)

    assert apply_calls == []


def test_c2_openapi_inventory_operation_ids_and_exact_schema_are_locked():
    schema = app.openapi()
    assert len(schema.get("paths", {})) == 304
    assert len(schema.get("components", {}).get("schemas", {})) == 108
    assert len(C2_ENDPOINTS) == 6

    for (method, path), (_, _, _, operation_id, _) in C2_ENDPOINTS.items():
        assert schema["paths"][path][method.lower()]["operationId"] == operation_id

    canonical = _canonical_openapi(schema)
    assert hashlib.sha256(canonical).hexdigest() == EXPECTED_OPENAPI_SHA256
    if OPENAPI_BASELINE_PATH.exists():
        baseline = json.loads(OPENAPI_BASELINE_PATH.read_text(encoding="utf-8"))
        assert baseline == schema


def test_c2_routes_remain_exact_service_pass_throughs():
    router_path = PROJECT_ROOT / "aether/interface/routers/final_real_apply_executor_routes.py"
    api_path = PROJECT_ROOT / "aether/interface/api_server.py"
    assert router_path.exists()
    router_tree = ast.parse(router_path.read_text(encoding="utf-8"))
    api_tree = ast.parse(api_path.read_text(encoding="utf-8"))

    expected = {
        details[0]: (details[1], details[4])
        for details in C2_ENDPOINTS.values()
    }

    router_assigns = [
        node for node in router_tree.body
        if isinstance(node, ast.Assign)
        and any(
            isinstance(t, ast.Name)
            and t.id == "final_real_apply_executor_router"
            for t in node.targets
        )
    ]
    assert len(router_assigns) == 1
    assert ast.unparse(router_assigns[0].value) == "APIRouter()"

    found = {}
    for node in router_tree.body:
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if node.name not in expected:
            continue

        assert node.decorator_list, f"{node.name}: missing decorator"
        for dec in node.decorator_list:
            text = ast.unparse(dec)
            assert text.startswith("final_real_apply_executor_router."), (
                f"{node.name}: wrong decorator {text}"
            )
            assert not text.startswith("app."), (
                f"{node.name}: app decorator must not appear in router"
            )

        service_handler_name, wrapper_key = expected[node.name]
        assert len(node.body) == 1
        assert isinstance(node.body[0], ast.Return)
        assert isinstance(node.body[0].value, ast.Call)
        call = node.body[0].value
        assert isinstance(call.func, ast.Name)
        assert call.func.id == service_handler_name
        found[node.name] = service_handler_name

    assert found == {
        route_name: service_handler_name
        for route_name, (service_handler_name, _) in expected.items()
    }

    api_route_names = set()
    for node in api_tree.body:
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if node.name in expected:
            api_route_names.add(node.name)
    assert api_route_names == set(), f"api_server still defines C2 routes: {api_route_names}"

    api_router_imports = []
    api_c2_service_imports = []
    router_module_imports = []
    for node in api_tree.body:
        if isinstance(node, ast.ImportFrom):
            mod = node.module or ""
            names = {alias.name for alias in node.names}
            if mod == "aether.interface.routers.final_real_apply_executor_routes":
                api_router_imports.append(names)
            if "final_real_apply_executor_service" in mod:
                api_c2_service_imports.append((mod, names))
    assert api_router_imports == [{"final_real_apply_executor_router"}]
    assert api_c2_service_imports == []

    include_calls = [
        n for n in ast.walk(api_tree)
        if isinstance(n, ast.Call)
        and ast.unparse(n.func) == "app.include_router"
        and n.args
        and ast.unparse(n.args[0]) == "final_real_apply_executor_router"
    ]
    assert len(include_calls) == 1
    assert ast.unparse(include_calls[0]) == (
        "app.include_router(final_real_apply_executor_router, prefix='')"
    )

    router_service_imports = []
    router_action_imports = []
    for node in router_tree.body:
        if isinstance(node, ast.ImportFrom):
            mod = node.module or ""
            names = {alias.name for alias in node.names}
            if "final_real_apply_executor_service" in mod:
                router_service_imports.append(names)
            elif mod.startswith("aether.action."):
                router_action_imports.append((mod, names))
    assert router_service_imports == [
        {details[1] for details in C2_ENDPOINTS.values()}
    ]
    assert router_action_imports == []

    router_forbidden_modules = []
    for node in router_tree.body:
        if isinstance(node, ast.ImportFrom):
            mod = node.module or ""
            if any(x in mod for x in [
                "approved_dry_run", "dry_run_review", "real_apply_approval",
                "post_apply_verification", "repair", "guided", "self_modification",
                "changelog", "tool", "patch", "evidence",
            ]) and "final_real_apply_executor_service" not in mod:
                router_forbidden_modules.append(mod)
    assert router_forbidden_modules == []


def test_c2_action_static_risk_is_single_explicit_real_apply_boundary():
    action_path = PROJECT_ROOT / "aether/action/final_real_apply_executor.py"
    tree = ast.parse(action_path.read_text(encoding="utf-8"))
    functions = {
        node.name: node
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }
    assert "execute_final_real_apply" in functions

    apply_calls = []
    forbidden_calls = []
    for function_name, function in functions.items():
        for call in (
            node for node in ast.walk(function) if isinstance(node, ast.Call)
        ):
            name = _call_name(call)
            if name == "apply_patch_proposal":
                apply_calls.append((function_name, call))
            lowered = name.lower()
            if (
                "rollback" in lowered
                or "collect_evidence" in lowered
                or "evidence_collection" in lowered
                or "execute_tool" in lowered
                or lowered in {"subprocess.run", "subprocess.call", "os.system"}
            ):
                forbidden_calls.append(name)

    assert len(apply_calls) == 1
    function_name, apply_call = apply_calls[0]
    assert function_name == "execute_final_real_apply"
    assert len(apply_call.args) >= 2
    assert isinstance(apply_call.args[1], ast.Constant)
    assert apply_call.args[1].value is False
    assert forbidden_calls == []

    imported_modules = set()
    imported_names = set()
    for node in tree.body:
        if isinstance(node, ast.Import):
            imported_modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imported_modules.add(node.module or "")
            imported_names.update(alias.name for alias in node.names)

    assert "apply_patch_proposal" in imported_names
    assert imported_modules.isdisjoint(
        {"subprocess", "requests", "httpx", "socket", "urllib", "urllib.request"}
    )
    assert imported_names.isdisjoint(
        {
            "rollback_patch_apply",
            "execute_patch_rollback",
            "collect_evidence",
            "execute_tool",
        }
    )


def test_c2_service_module_exists_and_is_boundary_correct():
    services_root = PROJECT_ROOT / "aether/action/services"
    service_path = services_root / "final_real_apply_executor_service.py"
    assert service_path.exists()

    tree = ast.parse(service_path.read_text(encoding="utf-8"))

    functions = {
        node.name: node
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }
    expected_handlers = {
        details[1] for details in C2_ENDPOINTS.values()
    }
    for handler in expected_handlers:
        assert handler in functions, f"Missing service handler: {handler}"

    called_action_functions = {}
    for handler_name, func in functions.items():
        calls = [
            node for node in ast.walk(func) if isinstance(node, ast.Call)
        ]
        assert len(calls) == 1, f"{handler_name}: expected 1 call, got {len(calls)}"
        call_name = ast.unparse(calls[0].func)
        called_action_functions[handler_name] = call_name

    expected_routes = {
        details[1]: details[2]
        for details in C2_ENDPOINTS.values()
    }
    assert called_action_functions == expected_routes

    for func in tree.body:
        if isinstance(func, ast.ImportFrom):
            assert func.module == "aether.action.final_real_apply_executor"

    imported_names = set()
    for func in tree.body:
        if isinstance(func, (ast.Import, ast.ImportFrom)):
            if isinstance(func, ast.ImportFrom):
                imported_names.update(alias.name for alias in func.names)
            else:
                imported_names.update(alias.name for alias in func.names)

    forbidden_imports = {"apply_patch_proposal", "rollback", "collect_evidence", "execute_tool"}
    assert imported_names.isdisjoint(forbidden_imports)


def test_c1_services_cannot_reach_real_apply():
    services_root = PROJECT_ROOT / "aether/action/services"
    for path in services_root.glob("*.py"):
        if path.name == "final_real_apply_executor_service.py":
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                assert node.module != "aether.action.final_real_apply_executor"

    for filename in C1_SERVICE_FILES:
        source = (services_root / filename).read_text(encoding="utf-8")
        assert "execute_final_real_apply" not in source
        assert "apply_patch_proposal" not in source
        assert "final_real_apply_executor" not in source


def test_protected_endpoints_are_outside_c2_and_never_invoked_here():
    schema = app.openapi()
    assert set(PROTECTED_ENDPOINTS).isdisjoint(C2_ENDPOINTS)
    for (method, path), operation_id in PROTECTED_ENDPOINTS.items():
        assert schema["paths"][path][method.lower()]["operationId"] == operation_id

    invoked_paths = {path for _, path, _, _ in API_CASES}
    protected_paths = {path for _, path in PROTECTED_ENDPOINTS}
    assert all(
        not any(
            invoked == protected
            or (
                protected != "/"
                and invoked.startswith(protected.rstrip("/") + "/")
            )
            for protected in protected_paths
        )
        for invoked in invoked_paths
    )


@pytest.mark.parametrize(
    ("method", "path", "payload", "wrapper_key"),
    API_CASES,
    ids=[f"{method}-{path}" for method, path, _, _ in API_CASES],
)
def test_c2_api_is_safe_under_hard_deny_real_apply_guard(
    denied_c2_api, method, path, payload, wrapper_key
):
    if method == "POST":
        response = denied_c2_api.client.post(path, json=payload)
    else:
        response = denied_c2_api.client.get(path)

    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "Aether"
    assert wrapper_key in body

    if path.endswith("/open"):
        assert body["record"]["status"] == "blocked"
    elif path.endswith("/execute"):
        assert body["record"]["status"] == "blocked"
        assert body["record"]["id"] == "missing_82AJ_executor"
    elif path.endswith("/status"):
        assert isinstance(body[wrapper_key], dict)
    elif path.endswith("/list"):
        assert isinstance(body[wrapper_key], list)
    else:
        assert body[wrapper_key] is None

    assert denied_c2_api.apply_calls == []
