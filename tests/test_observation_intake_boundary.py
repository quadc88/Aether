from pathlib import Path

import ast

from aether.interface.api_server import app

DOC_PATH = Path("docs/architecture/OBSERVATION_INTAKE_BRIDGE_DESIGN.md")
BOUNDARY_TEST_PATH = Path("tests/test_observation_intake_boundary.py")
API_SERVER_PATH = Path("aether/interface/api_server.py")
API_MODELS_PATH = Path("aether/interface/api_models.py")
FUTURE_SERVICE_PATH = Path("aether/action/services/observation_intake_service.py")
FUTURE_ROUTER_PATH = Path("aether/interface/routers/observation_intake_bridge.py")
FUTURE_BRIDGE_PATH = Path("aether/action/observation_intake_bridge.py")


def _doc_text() -> str:
    return DOC_PATH.read_text(encoding="utf-8")


def _assert_contains_all(text: str, markers):
    for marker in markers:
        assert marker in text, marker


def test_design_doc_exists():
    assert DOC_PATH.exists()


def test_future_service_module_does_not_exist():
    assert not FUTURE_SERVICE_PATH.exists()


def test_design_doc_locks_non_execution_boundary():
    _assert_contains_all(
        _doc_text(),
        (
            "does not execute tools",
            "does not collect evidence",
            "does not call executor code",
            "does not call real apply",
            "does not call rollback",
            "does not call the policy/execution gate",
            "does not call /cha" + "t",
            "does not call /awak" + "en",
            "does not call /identit" + "y*",
            "does not call /verification/class" + "ify",
            "does not call / (root path)",
            "performs no network calls",
            "does not call protected/core route functions directly",
            "does not write runtime/private data during tests",
            "uses only the supplied observed_value",
            "no automatic observation capture yet",
        ),
    )


def test_design_doc_locks_service_module_and_function():
    _assert_contains_all(
        _doc_text(),
        (
            "aether/action/services/observation_intake_service.py",
            "handle_observation_intake",
            "handle_observation_intake(request, context=None)",
            "handle_*",
            "The module does NOT exist yet",
            "implemented in Milestone 84B",
        ),
    )


def test_design_doc_locks_input_contract():
    _assert_contains_all(
        _doc_text(),
        (
            "plan_step_id",
            "collector_contract_id",
            "evidence_items",
            "evidence_item_id",
            "target",
            "observed_value",
            "expected_value",
            "metadata",
            "safety_flags",
            "NOT accepted",
            "required, non-empty string",
        ),
    )


def test_design_doc_locks_forbidden_input_fields():
    _assert_contains_all(
        _doc_text(),
        (
            "observation_id",
            "observation_type",
            "observed_at",
            "status",
            "created_at",
            "updated_at",
            "decision",
            "decided_at",
            "reviewer",
            "decision_reason",
            "warnings",
            "context_metadata",
            "new_status",
            "reason",
            "safety_flags",
            "ValueError",
            "zero records are created",
            "never partially created",
        ),
    )


def test_design_doc_locks_status_decision():
    _assert_contains_all(
        _doc_text(),
        (
            "matched",
            "mismatched",
            "pending is NOT a valid intake outcome",
            "pending is not produced",
            "error is never inferred by intake",
            "error is not inferred",
            "cancelled is never created by intake",
            "strict JSON-normalized equality",
            "1 and 1.0 are treated as not equal",
            "completed is not introduced",
        ),
    )


def test_design_doc_locks_output_contract():
    _assert_contains_all(
        _doc_text(),
        (
            "observation_intake",
            "completed",
            "created",
            "observation_records",
            "errors",
            "created_at",
            "updated_at",
            "decision",
            "decided_at",
            "reviewer",
            "decision_reason",
            "warnings",
            "context_metadata",
            "must not call API response models",
            "must not leak runtime/private paths",
            "not the route pure response shape",
            "84C",
        ),
    )


def test_design_doc_locks_matching_semantics():
    _assert_contains_all(
        _doc_text(),
        (
            "json.dumps(value, sort_keys=True)",
            "no type coercion",
            "no fuzzy matching",
            "no LLM judgment",
            "no external verification",
            "no tool calls",
            "deterministic strict equality",
            "1 vs 1.0 NOT equal",
        ),
    )


def test_design_doc_locks_atomicity():
    _assert_contains_all(
        _doc_text(),
        (
            "all-or-nothing",
            "zero records are created",
            "ValueError",
            "no partial creation",
            "no orphan observation records",
            "no duplicates",
        ),
    )


def test_design_doc_locks_persistence_and_testing_boundary():
    _assert_contains_all(
        _doc_text(),
        (
            "build_observation_record",
            "queue.save_observation_record",
            "get_observation_records_dir",
            "tmp_path",
            "no runtime/private mutation",
            "no new persistence directory",
            "no direct filesystem writes",
        ),
    )


def test_design_doc_locks_forbidden_imports():
    _assert_contains_all(
        _doc_text(),
        (
            "aether.interface.api_server",
            "fastapi.testclient" + "." + "Test" + "Client",
            "starlette.testclient" + "." + "Test" + "Client",
            "aether.action.policy_gate",
            "executor/apply/rollback execution modules",
            "tool execution modules",
            "re" + "quests",
            "ht" + "tpx",
            "ur" + "llib",
            "runtime route handlers",
            "private runtime paths directly",
        ),
    )


def test_openapi_surface_locked():
    schema = app.openapi()
    paths = schema.get("paths", {})
    assert len(paths) == 304, "OpenAPI path count must stay locked at 304"
    schemas = schema.get("components", {}).get("schemas", {})
    assert len(schemas) == 108, "OpenAPI schema count must stay locked at 108"
    observation_paths = sorted(p for p in paths if "/observation-records" in p)
    assert observation_paths == [
        "/observation-records",
        "/observation-records/{observation_id}",
        "/observation-records/{observation_id}/cancel",
        "/observation-records/{observation_id}/status",
    ]
    operation_ids = []
    for path, methods in paths.items():
        for method, detail in methods.items():
            if method in ("get", "post", "put", "patch", "delete"):
                operation_ids.append(detail.get("operationId", ""))
    observation_operation_ids = sorted(o for o in operation_ids if "observation" in o)
    assert observation_operation_ids == [
        "cancel_observation_record",
        "create_observation_record",
        "get_observation_record",
        "list_observation_records",
        "update_observation_record_status",
    ]


def test_api_server_ast_surface_locked():
    tree = ast.parse(API_SERVER_PATH.read_text(encoding="utf-8"))
    route_function_names = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            for decorator in node.decorator_list:
                decorator_source = ast.unparse(decorator)
                if any(
                    decorator_source.startswith(prefix)
                    for prefix in (
                        "app.get(",
                        "app.post(",
                        "app.put(",
                        "app.patch(",
                        "app.delete(",
                    )
                ):
                    route_function_names.append(node.name)
    assert len(route_function_names) == 8
    include_router_calls = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "include_router"
    ]
    assert len(include_router_calls) == 23
    source = API_SERVER_PATH.read_text(encoding="utf-8")
    assert "/action/" not in source, "zero direct /action/* routes in api_server"
    for forbidden_name in (
        "handle_observation_intake",
        "create_observation_intake",
        "observation_intake",
        "intake_observation",
    ):
        assert forbidden_name not in source


def test_future_artifacts_absent():
    for future_path in (
        FUTURE_SERVICE_PATH,
        FUTURE_ROUTER_PATH,
        FUTURE_BRIDGE_PATH,
    ):
        assert not future_path.exists(), future_path
    api_models_tree = ast.parse(API_MODELS_PATH.read_text(encoding="utf-8"))
    class_names = {
        node.name
        for node in ast.walk(api_models_tree)
        if isinstance(node, ast.ClassDef)
    }
    for forbidden_class in (
        "ObservationIntakeRequest",
        "ObservationIntakeResponse",
        "ObservationIntake",
    ):
        assert forbidden_class not in class_names
    api_server_source = API_SERVER_PATH.read_text(encoding="utf-8")
    for forbidden_name in (
        "observation-intake",
        "observation_intake",
        "handle_observation_intake",
    ):
        assert forbidden_name not in api_server_source


def test_boundary_test_source_stays_static():
    source = BOUNDARY_TEST_PATH.read_text(encoding="utf-8")
    for forbidden in (
        "Test" + "Client",
        "clie" + "nt.",
        "cha" + "t",
        "/awak" + "en",
        "/identit" + "y",
        "/verification/class" + "ify",
        "/home/aether/da" + "ta",
        "re" + "quests",
        "ht" + "tpx",
        "ur" + "llib",
        "sub" + "process",
        "pytest.sk" + "ip",
        "pytest.xfa" + "il",
    ):
        assert forbidden not in source, forbidden


def test_future_sequence_locked():
    text = _doc_text()
    _assert_contains_all(
        text,
        (
            "84A Build Boundary Tests",
            "tests/test_observation_intake_boundary.py",
            "REQUIRED before 84B",
            "84B Service Foundation",
            "84C Router/API",
            "84D Closure",
            "Milestone 85 not started",
            "milestone-84A-observation-intake-boundary-tests",
        ),
    )
    lowered = text.lower()
    for marker in (
        "84a build boundary tests",
        "tests/test_observation_intake_boundary.py",
        "required before 84b",
        "84b service foundation",
        "84c router/api",
        "only if a real consumer need is proven",
        "84d closure",
        "milestone 85 not started",
    ):
        assert marker in lowered, marker
