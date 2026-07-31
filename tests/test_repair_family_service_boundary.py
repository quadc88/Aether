"""Boundary tests for 43 Repair Family endpoints before service extraction.

Covers 7 families: repair_planner (5), repair_bridge_selector (5),
repair_workflow_tracker (5), repair_workflow_exporter (4),
repair_cycle_completion (8), repair_learning (8), repair_guidance (8).
"""

from __future__ import annotations

import ast
import hashlib
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest
from fastapi.testclient import TestClient

from aether.interface.api_server import app


PROJECT_ROOT = Path(__file__).resolve().parents[1]

# (route_func, action_func, operation_id, wrapper_key, family)
REPAIR_ENDPOINTS: dict[tuple[str, str], tuple[str, str, str, str | None, str]] = {
    # repair_planner (5)
    ("POST", "/action/repair-plan/create"): (
        "create_repair_plan_action",
        "create_repair_plan",
        "create_repair_plan_action_action_repair_plan_create_post",
        "plan",
        "repair_planner",
    ),
    ("GET", "/action/repair-plan/status"): (
        "get_repair_plan_status_action",
        "repair_plan_status",
        "get_repair_plan_status_action_action_repair_plan_status_get",
        "repair_plan",
        "repair_planner",
    ),
    ("GET", "/action/repair-plan/list"): (
        "list_repair_plan_action",
        "list_repair_plans",
        "list_repair_plan_action_action_repair_plan_list_get",
        "plans",
        "repair_planner",
    ),
    ("GET", "/action/repair-plan/{plan_id}/summary"): (
        "summarize_repair_plan_action",
        "summarize_repair_plan",
        "summarize_repair_plan_action_action_repair_plan__plan_id__summary_get",
        "summary",
        "repair_planner",
    ),
    ("GET", "/action/repair-plan/{plan_id}"): (
        "get_repair_plan_action",
        "get_repair_plan",
        "get_repair_plan_action_action_repair_plan__plan_id__get",
        "plan",
        "repair_planner",
    ),
    # repair_bridge_selector (5)
    ("POST", "/action/repair-bridge-selection/create"): (
        "create_repair_bridge_selection_action",
        "create_bridge_from_repair_plan",
        "create_repair_bridge_selection_action_action_repair_bridge_selection_create_post",
        "record",
        "repair_bridge_selector",
    ),
    ("GET", "/action/repair-bridge-selection/status"): (
        "get_repair_bridge_selection_status_action",
        "repair_bridge_selection_status",
        "get_repair_bridge_selection_status_action_action_repair_bridge_selection_status_get",
        "repair_bridge_selection",
        "repair_bridge_selector",
    ),
    ("GET", "/action/repair-bridge-selection/list"): (
        "list_repair_bridge_selection_action",
        "list_repair_bridge_selections",
        "list_repair_bridge_selection_action_action_repair_bridge_selection_list_get",
        "records",
        "repair_bridge_selector",
    ),
    ("GET", "/action/repair-bridge-selection/{record_id}/summary"): (
        "summarize_repair_bridge_selection_action",
        "summarize_repair_bridge_selection",
        "summarize_repair_bridge_selection_action_action_repair_bridge_selection__record_id__summary_get",
        "summary",
        "repair_bridge_selector",
    ),
    ("GET", "/action/repair-bridge-selection/{record_id}"): (
        "get_repair_bridge_selection_action",
        "get_repair_bridge_selection",
        "get_repair_bridge_selection_action_action_repair_bridge_selection__record_id__get",
        "record",
        "repair_bridge_selector",
    ),
    # repair_workflow_tracker (5)
    ("POST", "/action/repair-workflow/trace"): (
        "trace_repair_workflow_action",
        "trace_repair_workflow",
        "trace_repair_workflow_action_action_repair_workflow_trace_post",
        "report",
        "repair_workflow_tracker",
    ),
    ("GET", "/action/repair-workflow/status"): (
        "get_repair_workflow_status_action",
        "repair_workflow_status",
        "get_repair_workflow_status_action_action_repair_workflow_status_get",
        "repair_workflow",
        "repair_workflow_tracker",
    ),
    ("GET", "/action/repair-workflow/list"): (
        "list_repair_workflow_action",
        "list_repair_workflow_reports",
        "list_repair_workflow_action_action_repair_workflow_list_get",
        "reports",
        "repair_workflow_tracker",
    ),
    ("GET", "/action/repair-workflow/{report_id}/summary"): (
        "summarize_repair_workflow_action",
        "summarize_repair_workflow",
        "summarize_repair_workflow_action_action_repair_workflow__report_id__summary_get",
        "summary",
        "repair_workflow_tracker",
    ),
    ("GET", "/action/repair-workflow/{report_id}"): (
        "get_repair_workflow_action",
        "get_repair_workflow_report",
        "get_repair_workflow_action_action_repair_workflow__report_id__get",
        "report",
        "repair_workflow_tracker",
    ),
    # repair_workflow_exporter (4) — all direct-return (no wrapper)
    ("POST", "/action/repair-workflow-export/export-report"): (
        "export_repair_workflow_report_action",
        "export_workflow_report",
        "export_repair_workflow_report_action_action_repair_workflow_export_export_report_post",
        None,
        "repair_workflow_exporter",
    ),
    ("POST", "/action/repair-workflow-export/export-index"): (
        "export_repair_workflow_index_action",
        "export_workflow_index",
        "export_repair_workflow_index_action_action_repair_workflow_export_export_index_post",
        None,
        "repair_workflow_exporter",
    ),
    ("POST", "/action/repair-workflow-export/export-private"): (
        "export_private_repair_workflow_report_action",
        "export_private_workflow_report",
        "export_private_repair_workflow_report_action_action_repair_workflow_export_export_private_post",
        None,
        "repair_workflow_exporter",
    ),
    ("GET", "/action/repair-workflow-export/status"): (
        "get_repair_workflow_export_status_action",
        "repair_workflow_export_status",
        "get_repair_workflow_export_status_action_action_repair_workflow_export_status_get",
        None,
        "repair_workflow_exporter",
    ),
    # repair_cycle_completion (8)
    ("POST", "/action/repair-cycle-completion/create"): (
        "create_repair_cycle_completion_action",
        "create_repair_cycle_completion_report",
        "create_repair_cycle_completion_action_action_repair_cycle_completion_create_post",
        "record",
        "repair_cycle_completion",
    ),
    ("POST", "/action/repair-cycle-completion/export-report"): (
        "export_repair_cycle_report_action",
        "export_repair_cycle_report",
        "export_repair_cycle_report_action_action_repair_cycle_completion_export_report_post",
        None,
        "repair_cycle_completion",
    ),
    ("POST", "/action/repair-cycle-completion/export-index"): (
        "export_repair_cycle_index_action",
        "export_repair_cycle_index",
        "export_repair_cycle_index_action_action_repair_cycle_completion_export_index_post",
        None,
        "repair_cycle_completion",
    ),
    ("POST", "/action/repair-cycle-completion/export-private"): (
        "export_private_repair_cycle_action",
        "export_private_repair_cycle_record",
        "export_private_repair_cycle_action_action_repair_cycle_completion_export_private_post",
        None,
        "repair_cycle_completion",
    ),
    ("GET", "/action/repair-cycle-completion/status"): (
        "get_repair_cycle_completion_status_action",
        "repair_cycle_completion_status",
        "get_repair_cycle_completion_status_action_action_repair_cycle_completion_status_get",
        "repair_cycle_completion",
        "repair_cycle_completion",
    ),
    ("GET", "/action/repair-cycle-completion/list"): (
        "list_repair_cycle_completion_action",
        "list_repair_cycle_completion_records",
        "list_repair_cycle_completion_action_action_repair_cycle_completion_list_get",
        "records",
        "repair_cycle_completion",
    ),
    ("GET", "/action/repair-cycle-completion/{record_id}/summary"): (
        "summarize_repair_cycle_completion_action",
        "summarize_repair_cycle_completion",
        "summarize_repair_cycle_completion_action_action_repair_cycle_completion__record_id__summary_get",
        "summary",
        "repair_cycle_completion",
    ),
    ("GET", "/action/repair-cycle-completion/{record_id}"): (
        "get_repair_cycle_completion_action",
        "get_repair_cycle_completion_record",
        "get_repair_cycle_completion_action_action_repair_cycle_completion__record_id__get",
        "record",
        "repair_cycle_completion",
    ),
    # repair_learning (8)
    ("POST", "/action/repair-learning/create"): (
        "create_repair_learning_action",
        "create_repair_learning_record",
        "create_repair_learning_action_action_repair_learning_create_post",
        "record",
        "repair_learning",
    ),
    ("POST", "/action/repair-learning/export-report"): (
        "export_repair_learning_report_action",
        "export_repair_learning_report",
        "export_repair_learning_report_action_action_repair_learning_export_report_post",
        None,
        "repair_learning",
    ),
    ("POST", "/action/repair-learning/export-index"): (
        "export_repair_learning_index_action",
        "export_repair_learning_index",
        "export_repair_learning_index_action_action_repair_learning_export_index_post",
        None,
        "repair_learning",
    ),
    ("POST", "/action/repair-learning/export-private"): (
        "export_private_repair_learning_action",
        "export_private_repair_learning_record",
        "export_private_repair_learning_action_action_repair_learning_export_private_post",
        None,
        "repair_learning",
    ),
    ("GET", "/action/repair-learning/status"): (
        "get_repair_learning_status_action",
        "repair_learning_index_status",
        "get_repair_learning_status_action_action_repair_learning_status_get",
        "repair_learning",
        "repair_learning",
    ),
    ("GET", "/action/repair-learning/list"): (
        "list_repair_learning_action",
        "list_repair_learning_records",
        "list_repair_learning_action_action_repair_learning_list_get",
        "records",
        "repair_learning",
    ),
    ("GET", "/action/repair-learning/{record_id}/summary"): (
        "summarize_repair_learning_action",
        "summarize_repair_learning_record",
        "summarize_repair_learning_action_action_repair_learning__record_id__summary_get",
        "summary",
        "repair_learning",
    ),
    ("GET", "/action/repair-learning/{record_id}"): (
        "get_repair_learning_action",
        "get_repair_learning_record",
        "get_repair_learning_action_action_repair_learning__record_id__get",
        "record",
        "repair_learning",
    ),
    # repair_guidance (8)
    ("POST", "/action/repair-guidance/create"): (
        "create_repair_guidance_action",
        "create_repair_guidance",
        "create_repair_guidance_action_action_repair_guidance_create_post",
        "record",
        "repair_guidance",
    ),
    ("POST", "/action/repair-guidance/export-report"): (
        "export_repair_guidance_report_action",
        "export_repair_guidance_report",
        "export_repair_guidance_report_action_action_repair_guidance_export_report_post",
        None,
        "repair_guidance",
    ),
    ("POST", "/action/repair-guidance/export-index"): (
        "export_repair_guidance_index_action",
        "export_repair_guidance_index",
        "export_repair_guidance_index_action_action_repair_guidance_export_index_post",
        None,
        "repair_guidance",
    ),
    ("POST", "/action/repair-guidance/export-private"): (
        "export_private_repair_guidance_action",
        "export_private_repair_guidance_record",
        "export_private_repair_guidance_action_action_repair_guidance_export_private_post",
        None,
        "repair_guidance",
    ),
    ("GET", "/action/repair-guidance/status"): (
        "get_repair_guidance_status_action",
        "repair_guidance_engine_status",
        "get_repair_guidance_status_action_action_repair_guidance_status_get",
        "repair_guidance",
        "repair_guidance",
    ),
    ("GET", "/action/repair-guidance/list"): (
        "list_repair_guidance_action",
        "list_repair_guidance_records",
        "list_repair_guidance_action_action_repair_guidance_list_get",
        "records",
        "repair_guidance",
    ),
    ("GET", "/action/repair-guidance/{record_id}/summary"): (
        "summarize_repair_guidance_action",
        "summarize_repair_guidance",
        "summarize_repair_guidance_action_action_repair_guidance__record_id__summary_get",
        "summary",
        "repair_guidance",
    ),
    ("GET", "/action/repair-guidance/{record_id}"): (
        "get_repair_guidance_action",
        "get_repair_guidance_record",
        "get_repair_guidance_action_action_repair_guidance__record_id__get",
        "record",
        "repair_guidance",
    ),
}

assert len(REPAIR_ENDPOINTS) == 43, f"Expected 43 repair endpoints, got {len(REPAIR_ENDPOINTS)}"

# Known pre-existing bugs: repair_guidance export functions crash on None
# from get_repair_guidance_record("missing"). Deferred to Part 3 or a
# dedicated bugfix milestone before guidance extraction.
KNOWN_BUGGY_EXPORT_ENDPOINTS = {
    "/action/repair-guidance/export-report",
    "/action/repair-guidance/export-private",
}

POST_PAYLOADS: dict[str, dict[str, Any]] = {
    "/action/repair-plan/create": {
        "review_report_id": "missing",
        "scope": "full",
        "include_deferred": False,
        "max_findings": 10,
        "metadata": {},
    },
    "/action/repair-bridge-selection/create": {
        "repair_plan_id": "missing",
        "finding_id": "f-missing",
        "proposed_excerpt": "test",
        "original_excerpt": "test",
        "proposed_change_summary": "test",
        "reason": "test",
        "metadata": {},
    },
    "/action/repair-workflow/trace": {
        "root_type": "missing",
        "root_id": "r-missing",
        "metadata": {},
    },
    "/action/repair-workflow-export/export-report": {
        "report_id": "missing",
        "output_dir": "/tmp/isolated",
        "metadata": {},
    },
    "/action/repair-workflow-export/export-index": {
        "output_path": "/tmp/isolated/index.json",
        "limit": 50,
        "metadata": {},
    },
    "/action/repair-workflow-export/export-private": {
        "report_id": "missing",
        "metadata": {},
    },
    "/action/repair-cycle-completion/create": {
        "source_type": "missing",
        "source_id": "s-missing",
        "export_public": False,
        "export_index": False,
        "export_private": False,
        "metadata": {},
    },
    "/action/repair-cycle-completion/export-report": {
        "completion_record_id": "missing",
        "output_dir": "/tmp/isolated",
        "metadata": {},
    },
    "/action/repair-cycle-completion/export-index": {
        "output_path": "/tmp/isolated/index.json",
        "limit": 50,
        "metadata": {},
    },
    "/action/repair-cycle-completion/export-private": {
        "completion_record_id": "missing",
        "metadata": {},
    },
    "/action/repair-learning/create": {
        "source_type": "missing",
        "source_id": "s-missing",
        "export_public": False,
        "export_index": False,
        "export_private": False,
        "metadata": {},
    },
    "/action/repair-learning/export-report": {
        "learning_record_id": "missing",
        "output_dir": "/tmp/isolated",
        "metadata": {},
    },
    "/action/repair-learning/export-index": {
        "output_path": "/tmp/isolated/index.json",
        "limit": 50,
        "metadata": {},
    },
    "/action/repair-learning/export-private": {
        "learning_record_id": "missing",
        "metadata": {},
    },
    "/action/repair-guidance/create": {
        "request_type": "missing",
        "requested_scope": "full",
        "target_path": "/tmp/test",
        "source_type": "test",
        "source_id": "s-missing",
        "export_public": False,
        "export_index": False,
        "export_private": False,
        "metadata": {},
    },
    "/action/repair-guidance/export-report": {
        "guidance_record_id": "missing",
        "output_dir": "/tmp/isolated",
        "metadata": {},
    },
    "/action/repair-guidance/export-index": {
        "output_path": "/tmp/isolated/index.json",
        "limit": 50,
        "metadata": {},
    },
    "/action/repair-guidance/export-private": {
        "guidance_record_id": "missing",
        "metadata": {},
    },
}

PROTECTED_ENDPOINTS: dict[tuple[str, str], str] = {
    ("GET", "/"): "root__get",
    ("GET", "/identity"): "identity_identity_get",
    ("GET", "/identity/integrity/status"): "get_identity_integrity_status_identity_integrity_status_get",
    ("POST", "/identity/integrity/initialize"): "post_initialize_identity_guard_identity_integrity_initialize_post",
    ("POST", "/identity/integrity/verify"): "post_verify_identity_integrity_identity_integrity_verify_post",
    ("POST", "/chat"): "chat_chat_post",
    ("POST", "/awaken"): "awaken_awaken_post",
    ("POST", "/verification/classify"): "classify_verification_risk_verification_classify_post",
}

# Build safe-endpoint API cases (excluding known buggy endpoints)
API_CASES: list[tuple[str, str, dict[str, Any] | None, str | None]] = []

for (method, path), (_, _, _, wrapper_key, _) in sorted(REPAIR_ENDPOINTS.items()):
    if path in KNOWN_BUGGY_EXPORT_ENDPOINTS:
        continue
    payload = None
    if method == "POST":
        payload = POST_PAYLOADS.get(path, {})
    API_CASES.append((method, path, payload, wrapper_key))

# ----- fingerprint helpers -----

def _fingerprint(root: Path) -> list[tuple]:
    if not root.exists():
        return []
    result = []
    for p in sorted(root.rglob("*")):
        try:
            relative = str(p.relative_to(root))
            if p.is_file():
                result.append(
                    ("file", relative, p.stat().st_size,
                     hashlib.sha256(p.read_bytes()).hexdigest())
                )
            elif p.is_dir():
                result.append(("dir", relative))
        except FileNotFoundError:
            continue
    return result


WATCHED_REAL_ROOTS = (
    PROJECT_ROOT / "aether",
    PROJECT_ROOT / "tests",
    PROJECT_ROOT / "PROGRESS.md",
    Path("/home/aether/data/private"),
    Path("/home/aether/data/timeline"),
    Path("/home/aether/data/graph_db"),
    Path("/home/aether/data/vector_db"),
    Path("/home/aether/data/vault"),
    Path("/home/aether/data/logs"),
    PROJECT_ROOT / "docs/history",
)


@pytest.fixture(scope="module", autouse=True)
def real_source_runtime_and_data_roots_unchanged():
    before = {
        str(root): _fingerprint(root) if root.exists() else []
        for root in WATCHED_REAL_ROOTS
    }
    yield
    after = {
        str(root): _fingerprint(root) if root.exists() else []
        for root in WATCHED_REAL_ROOTS
    }
    assert before == after


@pytest.fixture
def isolated_repair_env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    data_root = tmp_path / "AetherData"
    private_dir = data_root / "private"
    private_dir.mkdir(parents=True, exist_ok=True)

    config = {"paths": {"private_dir": str(private_dir)}}

    import aether.action.repair_planner as rp
    import aether.action.repair_bridge_selector as rbs
    import aether.action.repair_workflow_tracker as rwt
    import aether.action.repair_workflow_exporter as rwe
    import aether.action.repair_cycle_completion_report as rcc
    import aether.action.repair_learning_index as rli
    import aether.action.repair_guidance_engine as rge

    for module in (rp, rbs, rwt, rwe, rcc, rli, rge):
        monkeypatch.setattr(module, "load_aether_config", lambda path=None, _config=config: _config)

    client = TestClient(app)
    yield SimpleNamespace(client=client, private_dir=private_dir)


# ----- Test 1: OpenAPI operation ID lock -----

def test_openapi_contract_and_operation_ids_locked():
    schema = app.openapi()
    assert len(schema.get("paths", {})) == 300
    assert len(schema.get("components", {}).get("schemas", {})) == 103
    assert len(REPAIR_ENDPOINTS) == 43

    for (method, path), (_, _, operation_id, _, _) in REPAIR_ENDPOINTS.items():
        actual = schema["paths"][path][method.lower()]["operationId"]
        assert actual == operation_id, (
            f"{method} {path}: expected {operation_id}, got {actual}"
        )


# ----- Test 2: Protected endpoints remain outside repair scope -----

def test_protected_endpoints_remain_outside_repair_families():
    schema = app.openapi()
    repair_paths = {path for _, path in REPAIR_ENDPOINTS}
    for (method, path), operation_id in PROTECTED_ENDPOINTS.items():
        assert path not in repair_paths
        assert schema["paths"][path][method.lower()]["operationId"] == operation_id

    this_file = Path(__file__).read_text(encoding="utf-8")
    invoked_paths = set()
    for node in ast.walk(ast.parse(this_file)):
        if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Attribute):
            continue
        if node.func.attr not in {"get", "post"} or not node.args:
            continue
        if isinstance(node.args[0], ast.Constant):
            invoked_paths.add(node.args[0].value)
    assert not invoked_paths.intersection(path for _, path in PROTECTED_ENDPOINTS)


# ----- Test 3: Dynamic API smoke tests -----

@pytest.mark.parametrize(
    ("method", "path", "payload", "wrapper_key"),
    API_CASES,
    ids=[f"{method}-{path}" for method, path, _, _ in API_CASES],
)
def test_repair_wrapped_endpoints_respond(
    isolated_repair_env, method, path, payload, wrapper_key
):
    if method == "POST":
        response = isolated_repair_env.client.post(path, json=payload)
    else:
        response = isolated_repair_env.client.get(path)

    assert response.status_code == 200, (
        f"{method} {path}: expected 200, got {response.status_code}: {response.text[:200]}"
    )

    body = response.json()
    if wrapper_key is not None:
        # wrapped route: must have {"name":"Aether","<wrapper_key>": ...}
        assert body["name"] == "Aether", (
            f"{method} {path}: expected name=Aether, got {body}"
        )
        assert wrapper_key in body, (
            f"{method} {path}: expected wrapper_key={wrapper_key!r} in body, got keys {list(body)}"
        )
    else:
        # direct-return route: no wrapper; accept any valid JSON response
        assert isinstance(body, (dict, list)), (
            f"{method} {path}: expected dict/list, got {type(body).__name__}"
        )


# ----- Test 4: Known buggy endpoints documentation -----

def test_known_buggy_export_endpoints_documented():
    """Repair-guidance export endpoints crash on missing records (pre-existing bug).
    These are pre-existing missing-record crash bugs in repair_guidance_engine.py,
    deferred to 82AL Part 3 / guidance extraction or a dedicated bugfix milestone
    before guidance extraction.
    """
    assert KNOWN_BUGGY_EXPORT_ENDPOINTS == {
        "/action/repair-guidance/export-report",
        "/action/repair-guidance/export-private",
    }, "Bug endpoints list changed — verify and update this test"


# ----- Test 5: Route -> action function direct pass-through (pre-extraction snapshot) -----

def test_repair_routes_are_direct_pass_throughs():
    """Verify each repair route calls exactly one action function directly
    (no service handler, no handle_* wrapper)."""
    source_path = PROJECT_ROOT / "aether/interface/api_server.py"
    tree = ast.parse(source_path.read_text(encoding="utf-8"))

    route_map = {(route_func, action_func): path
                 for (method, path), (route_func, action_func, _, _, _) in REPAIR_ENDPOINTS.items()}
    func_names = {route_func for route_func, _ in route_map}

    found = {}
    for node in tree.body:
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if node.name not in func_names:
            continue
        assert len(node.body) == 1, f"{node.name}: expected single-statement body"
        assert isinstance(node.body[0], ast.Return), f"{node.name}: expected return"
        calls = [child for child in ast.walk(node.body[0]) if isinstance(child, ast.Call)]
        assert len(calls) == 1, f"{node.name}: expected exactly 1 call, got {len(calls)}"
        called_name = ast.unparse(calls[0].func)

        assert not called_name.startswith("handle_"), (
            f"{node.name}: calls handle_* service function {called_name!r}; "
            f"service extraction has not started"
        )

        found[node.name] = called_name

    assert len(found) == 43, f"Expected 43 route functions, found {len(found)}"

    for (route_func, action_func), path in route_map.items():
        assert found[route_func] == action_func, (
            f"Route {route_func} ({path}): expected action {action_func!r}, "
            f"got {found[route_func]!r}"
        )

    # Verify wrapper contract for each route
    for (method, path), (route_func, action_func, _, wrapper_key, _) in REPAIR_ENDPOINTS.items():
        for node in tree.body:
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            if node.name != route_func:
                continue
            ret = node.body[0]
            if wrapper_key is not None:
                # wrapped: return {"name":"Aether","<key>": action_func(...)}
                assert isinstance(ret.value, ast.Dict), (
                    f"{route_func}: expected dict return for wrapped route"
                )
                keys = [ast.unparse(k) for k in ret.value.keys]
                assert "'name'" in keys, f"{route_func}: missing 'name' key"
                assert f"'{wrapper_key}'" in keys, (
                    f"{route_func}: missing {wrapper_key!r} key"
                )
            else:
                # direct-return: return action_func(...)
                assert isinstance(ret.value, ast.Call), (
                    f"{route_func}: expected direct call return for direct-return route"
                )
            break


# ----- Test 6: Import boundary — api_server.py imports repair action modules directly -----

def test_api_server_imports_repair_action_modules_directly():
    source = (PROJECT_ROOT / "aether/interface/api_server.py").read_text(encoding="utf-8")
    tree = ast.parse(source)

    repair_imports = set()
    future_service_imports = set()
    for node in tree.body:
        if isinstance(node, ast.ImportFrom):
            module = node.module or ""
            for alias in node.names:
                if module.startswith("aether.action.") and "repair" in module:
                    repair_imports.add(module)
                if module.startswith("aether.action.services.") and "repair" in module:
                    future_service_imports.add(module)

    expected_repair_modules = {
        "aether.action.repair_planner",
        "aether.action.repair_bridge_selector",
        "aether.action.repair_workflow_tracker",
        "aether.action.repair_workflow_exporter",
        "aether.action.repair_cycle_completion_report",
        "aether.action.repair_learning_index",
        "aether.action.repair_guidance_engine",
    }
    for mod in expected_repair_modules:
        assert mod in repair_imports, (
            f"Missing direct import of repair action module: {mod}"
        )

    forbidden_future = {
        "aether.action.services.repair_planner_service",
        "aether.action.services.repair_bridge_selector_service",
        "aether.action.services.repair_workflow_tracker_service",
        "aether.action.services.repair_workflow_exporter_service",
        "aether.action.services.repair_cycle_completion_service",
        "aether.action.services.repair_learning_service",
        "aether.action.services.repair_guidance_service",
    }
    overlap = future_service_imports & forbidden_future
    assert not overlap, (
        f"Future service module(s) already imported in api_server.py: {overlap}"
    )


# ----- Test 7: Service absence proof -----

def test_repair_service_modules_do_not_exist_yet():
    service_paths = [
        PROJECT_ROOT / "aether/action/services/repair_planner_service.py",
        PROJECT_ROOT / "aether/action/services/repair_bridge_selector_service.py",
        PROJECT_ROOT / "aether/action/services/repair_workflow_tracker_service.py",
        PROJECT_ROOT / "aether/action/services/repair_workflow_exporter_service.py",
        PROJECT_ROOT / "aether/action/services/repair_cycle_completion_service.py",
        PROJECT_ROOT / "aether/action/services/repair_learning_service.py",
        PROJECT_ROOT / "aether/action/services/repair_guidance_service.py",
    ]
    for path in service_paths:
        assert not path.exists(), (
            f"Service module already exists (should not before Part 2): {path}"
        )


# ----- Test 8: Action risk static proof (strengthened) -----

REPAIR_ACTION_MODULE_PATHS = [
    PROJECT_ROOT / "aether/action/repair_planner.py",
    PROJECT_ROOT / "aether/action/repair_bridge_selector.py",
    PROJECT_ROOT / "aether/action/repair_workflow_tracker.py",
    PROJECT_ROOT / "aether/action/repair_workflow_exporter.py",
    PROJECT_ROOT / "aether/action/repair_cycle_completion_report.py",
    PROJECT_ROOT / "aether/action/repair_learning_index.py",
    PROJECT_ROOT / "aether/action/repair_guidance_engine.py",
]

FORBIDDEN_ACTION_IMPORTS = {
    "apply_patch_proposal",
    "execute_final_real_apply",
    "execute_patch_rollback",
    "rollback_patch_apply",
    "perform_rollback",
    "apply_rollback",
    "run_rollback",
    "collect_evidence",
    "evidence_collection",
    "execute_tool",
}

FORBIDDEN_ACTION_CALLS = {
    "apply_patch_proposal",
    "execute_final_real_apply",
    "execute_patch_rollback",
    "rollback_patch_apply",
    "perform_rollback",
    "apply_rollback",
    "run_rollback",
    "collect_evidence",
    "evidence_collection",
    "execute_tool",
    "subprocess.run",
    "subprocess.call",
    "subprocess.Popen",
    "os.system",
    "requests",
    "httpx",
    "socket",
    "urllib",
}

# Exception: repair_cycle_completion_report.py may import/call
# get_final_real_apply_executor_record as read-only lookup only.
# It must NOT import/call execute_final_real_apply or apply_patch_proposal.
ALLOWED_READ_ONLY_FETCH = {"get_final_real_apply_executor_record"}


def test_no_forbidden_imports_in_repair_action_modules():
    for module_path in REPAIR_ACTION_MODULE_PATHS:
        assert module_path.exists(), f"Missing module: {module_path}"
        tree = ast.parse(module_path.read_text(encoding="utf-8"))
        imported_names = set()
        imported_from_final_exec = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    imported_names.add(alias.name)
                    if node.module == "aether.action.final_real_apply_executor":
                        imported_from_final_exec.add(alias.name)

        overlap = imported_names & FORBIDDEN_ACTION_IMPORTS
        assert not overlap, (
            f"{module_path.name}: forbidden import(s): {overlap}"
        )

        # Check read-only fetch exception
        exec_imports = imported_from_final_exec - ALLOWED_READ_ONLY_FETCH
        assert not exec_imports, (
            f"{module_path.name}: unexpected import(s) from final_real_apply_executor: {exec_imports}"
        )

        # Only repair_cycle_completion_report may have read-only fetch
        if imported_from_final_exec:
            assert module_path.name == "repair_cycle_completion_report.py", (
                f"{module_path.name}: only repair_cycle_completion_report may import "
                f"from final_real_apply_executor"
            )
            assert imported_from_final_exec == {"get_final_real_apply_executor_record"}, (
                f"{module_path.name}: only get_final_real_apply_executor_record allowed, "
                f"got {imported_from_final_exec}"
            )


def test_no_forbidden_calls_or_network_in_repair_action_modules():
    for module_path in REPAIR_ACTION_MODULE_PATHS:
        assert module_path.exists(), f"Missing module: {module_path}"
        tree = ast.parse(module_path.read_text(encoding="utf-8"))
        all_calls = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                call_str = ast.unparse(node.func)
                all_calls.add(call_str)

        overlap = all_calls & FORBIDDEN_ACTION_CALLS
        assert not overlap, (
            f"{module_path.name}: forbidden call(s): {overlap}"
        )


def test_repair_cycle_completion_read_only_fetch_exception_documented():
    """repair_cycle_completion_report.py may import get_final_real_apply_executor_record
    as a read-only lookup. Verify it does NOT import execute_final_real_apply
    or apply_patch_proposal."""
    cycle_path = PROJECT_ROOT / "aether/action/repair_cycle_completion_report.py"
    assert cycle_path.exists()
    tree = ast.parse(cycle_path.read_text(encoding="utf-8"))
    imported_names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            for alias in node.names:
                imported_names.add(alias.name)

    assert "execute_final_real_apply" not in imported_names, (
        "repair_cycle_completion_report must NOT import execute_final_real_apply"
    )
    assert "apply_patch_proposal" not in imported_names, (
        "repair_cycle_completion_report must NOT import apply_patch_proposal"
    )
    assert "get_final_real_apply_executor_record" in imported_names, (
        "repair_cycle_completion_report should import get_final_real_apply_executor_record "
        "for read-only lookup (expected read-only fetch exception)"
    )
