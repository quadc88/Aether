"""Tests-only safety boundary for the guided launcher families (82AQ Build,
router placement locked after 82AR Build).

AST/OpenAPI-based only. No guided endpoint is ever invoked and no guided
action function is ever called, so no guided record-store JSON, export/report
files, or runtime state can be written by this module.
"""

from __future__ import annotations

import ast
import json
import subprocess
from pathlib import Path

from aether.interface.api_server import app


PROJECT_ROOT = Path(__file__).resolve().parents[1]
API_SERVER_PATH = PROJECT_ROOT / "aether/interface/api_server.py"
GUIDED_LAUNCHER_ROUTER_PATH = (
    PROJECT_ROOT / "aether/interface/routers/guided_launcher_routes.py"
)
GUIDED_ACTION_PATHS = (
    PROJECT_ROOT / "aether/action/guided_repair_intake.py",
    PROJECT_ROOT / "aether/action/guided_repair_plan_launcher.py",
    PROJECT_ROOT / "aether/action/guided_bridge_selection_launcher.py",
    PROJECT_ROOT / "aether/action/guided_proposal_review_launcher.py",
    PROJECT_ROOT / "aether/action/guided_proposal_decision_launcher.py",
)

# (method, path) -> (route_fn, action_fn, operation_id, wrap_key|None,
#                    request_model|None, expected call args)
GUIDED_ENDPOINTS: dict[tuple[str, str], tuple] = {
    # guided_repair_intake (9)
    ("POST", "/action/guided-repair-intake/open"): (
        "open_guided_repair_intake_action",
        "open_guided_repair_intake",
        "open_guided_repair_intake_action_action_guided_repair_intake_open_post",
        "record",
        "GuidedRepairIntakeOpenRequest",
        (
            "request.request_type",
            "request.requested_scope",
            "request.target_path",
            "request.requester",
            "request.guidance_record_id",
            "request.create_guidance_if_missing",
            "request.export_public",
            "request.export_index",
            "request.export_private",
            "request.metadata",
        ),
    ),
    ("POST", "/action/guided-repair-intake/submit-decision"): (
        "submit_guided_repair_intake_action",
        "submit_guided_repair_intake_decision",
        "submit_guided_repair_intake_action_action_guided_repair_intake_submit_decision_post",
        "record",
        "GuidedRepairIntakeDecisionRequest",
        (
            "request.intake_record_id",
            "request.decision",
            "request.comment",
            "request.reviewer",
            "request.metadata",
        ),
    ),
    ("POST", "/action/guided-repair-intake/export-report"): (
        "export_guided_repair_intake_report_action",
        "export_guided_repair_intake_report",
        "export_guided_repair_intake_report_action_action_guided_repair_intake_export_report_post",
        None,
        "GuidedRepairIntakeReportExportRequest",
        (
            "request.intake_record_id",
            "request.output_dir",
            "request.metadata",
        ),
    ),
    ("POST", "/action/guided-repair-intake/export-index"): (
        "export_guided_repair_intake_index_action",
        "export_guided_repair_intake_index",
        "export_guided_repair_intake_index_action_action_guided_repair_intake_export_index_post",
        None,
        "GuidedRepairIntakeIndexExportRequest",
        (
            "request.output_path",
            "request.limit",
            "request.metadata",
        ),
    ),
    ("POST", "/action/guided-repair-intake/export-private"): (
        "export_private_guided_repair_intake_action",
        "export_private_guided_repair_intake_record",
        "export_private_guided_repair_intake_action_action_guided_repair_intake_export_private_post",
        None,
        "PrivateGuidedRepairIntakeExportRequest",
        (
            "request.intake_record_id",
            "request.metadata",
        ),
    ),
    ("GET", "/action/guided-repair-intake/status"): (
        "guided_repair_intake_status_action",
        "guided_repair_intake_status",
        "guided_repair_intake_status_action_action_guided_repair_intake_status_get",
        "guided_repair_intake",
        None,
        (),
    ),
    ("GET", "/action/guided-repair-intake/list"): (
        "list_guided_repair_intake_action",
        "list_guided_repair_intake_records",
        "list_guided_repair_intake_action_action_guided_repair_intake_list_get",
        "records",
        None,
        ("status", "planning_allowed", "target_path", "limit"),
    ),
    ("GET", "/action/guided-repair-intake/{record_id}/summary"): (
        "summarize_guided_repair_intake_action",
        "summarize_guided_repair_intake",
        "summarize_guided_repair_intake_action_action_guided_repair_intake__record_id__summary_get",
        "summary",
        None,
        ("record_id",),
    ),
    ("GET", "/action/guided-repair-intake/{record_id}"): (
        "get_guided_repair_intake_action",
        "get_guided_repair_intake_record",
        "get_guided_repair_intake_action_action_guided_repair_intake__record_id__get",
        "record",
        None,
        ("record_id",),
    ),
    # guided_repair_plan_launcher (5)
    ("POST", "/action/guided-repair-plan-launcher/launch"): (
        "launch_guided_repair_plan_action",
        "launch_guided_repair_plan",
        "launch_guided_repair_plan_action_action_guided_repair_plan_launcher_launch_post",
        "record",
        "GuidedRepairPlanLaunchRequest",
        (
            "request.intake_record_id",
            "request.review_report_id",
            "request.create_repair_plan",
            "request.metadata",
        ),
    ),
    ("GET", "/action/guided-repair-plan-launcher/status"): (
        "guided_repair_plan_launcher_status_action",
        "guided_repair_plan_launcher_status",
        "guided_repair_plan_launcher_status_action_action_guided_repair_plan_launcher_status_get",
        "guided_repair_plan_launcher",
        None,
        (),
    ),
    ("GET", "/action/guided-repair-plan-launcher/list"): (
        "list_guided_repair_plan_launcher_action",
        "list_guided_repair_plan_launcher_records",
        "list_guided_repair_plan_launcher_action_action_guided_repair_plan_launcher_list_get",
        "records",
        None,
        ("status", "intake_record_id", "target_path", "limit"),
    ),
    ("GET", "/action/guided-repair-plan-launcher/{record_id}/summary"): (
        "summarize_guided_repair_plan_launcher_action",
        "summarize_guided_repair_plan_launcher",
        "summarize_guided_repair_plan_launcher_action_action_guided_repair_plan_launcher__record_id__summary_get",
        "summary",
        None,
        ("record_id",),
    ),
    ("GET", "/action/guided-repair-plan-launcher/{record_id}"): (
        "get_guided_repair_plan_launcher_action",
        "get_guided_repair_plan_launcher_record",
        "get_guided_repair_plan_launcher_action_action_guided_repair_plan_launcher__record_id__get",
        "record",
        None,
        ("record_id",),
    ),
    # guided_bridge_selection_launcher (5)
    ("POST", "/action/guided-bridge-selection-launcher/launch"): (
        "launch_guided_bridge_selection_action",
        "launch_guided_bridge_selection",
        "launch_guided_bridge_selection_action_action_guided_bridge_selection_launcher_launch_post",
        "record",
        "GuidedBridgeSelectionLaunchRequest",
        (
            "request.plan_launcher_record_id",
            "request.finding_id",
            "request.proposed_excerpt",
            "request.metadata",
        ),
    ),
    ("GET", "/action/guided-bridge-selection-launcher/status"): (
        "guided_bridge_selection_launcher_status_action",
        "guided_bridge_selection_launcher_status",
        "guided_bridge_selection_launcher_status_action_action_guided_bridge_selection_launcher_status_get",
        "guided_bridge_selection_launcher",
        None,
        (),
    ),
    ("GET", "/action/guided-bridge-selection-launcher/list"): (
        "list_guided_bridge_selection_launcher_action",
        "list_guided_bridge_selection_launcher_records",
        "list_guided_bridge_selection_launcher_action_action_guided_bridge_selection_launcher_list_get",
        "records",
        None,
        ("status", "plan_launcher_record_id", "repair_plan_id", "target_path", "limit"),
    ),
    ("GET", "/action/guided-bridge-selection-launcher/{record_id}/summary"): (
        "summarize_guided_bridge_selection_launcher_action",
        "summarize_guided_bridge_selection_launcher",
        "summarize_guided_bridge_selection_launcher_action_action_guided_bridge_selection_launcher__record_id__summary_get",
        "summary",
        None,
        ("record_id",),
    ),
    ("GET", "/action/guided-bridge-selection-launcher/{record_id}"): (
        "get_guided_bridge_selection_launcher_action",
        "get_guided_bridge_selection_launcher_record",
        "get_guided_bridge_selection_launcher_action_action_guided_bridge_selection_launcher__record_id__get",
        "record",
        None,
        ("record_id",),
    ),
    # guided_proposal_review_launcher (5)
    ("POST", "/action/guided-proposal-review-launcher/open"): (
        "open_guided_proposal_review_action",
        "open_guided_proposal_review",
        "open_guided_proposal_review_action_action_guided_proposal_review_launcher_open_post",
        "record",
        "GuidedProposalReviewOpenRequest",
        (
            "request.bridge_launcher_record_id",
            "request.metadata",
        ),
    ),
    ("GET", "/action/guided-proposal-review-launcher/status"): (
        "guided_proposal_review_launcher_status_action",
        "guided_proposal_review_launcher_status",
        "guided_proposal_review_launcher_status_action_action_guided_proposal_review_launcher_status_get",
        "guided_proposal_review_launcher",
        None,
        (),
    ),
    ("GET", "/action/guided-proposal-review-launcher/list"): (
        "list_guided_proposal_review_launcher_action",
        "list_guided_proposal_review_launcher_records",
        "list_guided_proposal_review_launcher_action_action_guided_proposal_review_launcher_list_get",
        "records",
        None,
        ("status", "bridge_launcher_record_id", "proposal_id", "target_path", "limit"),
    ),
    ("GET", "/action/guided-proposal-review-launcher/{record_id}/summary"): (
        "summarize_guided_proposal_review_launcher_action",
        "summarize_guided_proposal_review_launcher",
        "summarize_guided_proposal_review_launcher_action_action_guided_proposal_review_launcher__record_id__summary_get",
        "summary",
        None,
        ("record_id",),
    ),
    ("GET", "/action/guided-proposal-review-launcher/{record_id}"): (
        "get_guided_proposal_review_launcher_action",
        "get_guided_proposal_review_launcher_record",
        "get_guided_proposal_review_launcher_action_action_guided_proposal_review_launcher__record_id__get",
        "record",
        None,
        ("record_id",),
    ),
    # guided_proposal_decision_launcher (5)
    ("POST", "/action/guided-proposal-decision-launcher/submit"): (
        "submit_guided_proposal_decision_action",
        "submit_guided_proposal_decision",
        "submit_guided_proposal_decision_action_action_guided_proposal_decision_launcher_submit_post",
        "record",
        "GuidedProposalDecisionSubmitRequest",
        (
            "request.proposal_review_launcher_record_id",
            "request.decision",
            "request.reviewer",
            "request.comment",
            "request.metadata",
        ),
    ),
    ("GET", "/action/guided-proposal-decision-launcher/status"): (
        "guided_proposal_decision_launcher_status_action",
        "guided_proposal_decision_launcher_status",
        "guided_proposal_decision_launcher_status_action_action_guided_proposal_decision_launcher_status_get",
        "guided_proposal_decision_launcher",
        None,
        (),
    ),
    ("GET", "/action/guided-proposal-decision-launcher/list"): (
        "list_guided_proposal_decision_launcher_action",
        "list_guided_proposal_decision_launcher_records",
        "list_guided_proposal_decision_launcher_action_action_guided_proposal_decision_launcher_list_get",
        "records",
        None,
        (
            "status",
            "proposal_review_launcher_record_id",
            "proposal_id",
            "decision",
            "target_path",
            "limit",
        ),
    ),
    ("GET", "/action/guided-proposal-decision-launcher/{record_id}/summary"): (
        "summarize_guided_proposal_decision_launcher_action",
        "summarize_guided_proposal_decision_launcher",
        "summarize_guided_proposal_decision_launcher_action_action_guided_proposal_decision_launcher__record_id__summary_get",
        "summary",
        None,
        ("record_id",),
    ),
    ("GET", "/action/guided-proposal-decision-launcher/{record_id}"): (
        "get_guided_proposal_decision_launcher_action",
        "get_guided_proposal_decision_launcher_record",
        "get_guided_proposal_decision_launcher_action_action_guided_proposal_decision_launcher__record_id__get",
        "record",
        None,
        ("record_id",),
    ),
}

# api_server.py imports exactly these names from exactly these 5 modules.
EXPECTED_GUIDED_IMPORTS = {
    "aether.action.guided_repair_intake": (
        "open_guided_repair_intake",
        "submit_guided_repair_intake_decision",
        "export_guided_repair_intake_report",
        "export_guided_repair_intake_index",
        "export_private_guided_repair_intake_record",
        "get_guided_repair_intake_record",
        "list_guided_repair_intake_records",
        "guided_repair_intake_status",
        "summarize_guided_repair_intake",
    ),
    "aether.action.guided_repair_plan_launcher": (
        "launch_guided_repair_plan",
        "get_guided_repair_plan_launcher_record",
        "list_guided_repair_plan_launcher_records",
        "guided_repair_plan_launcher_status",
        "summarize_guided_repair_plan_launcher",
    ),
    "aether.action.guided_bridge_selection_launcher": (
        "launch_guided_bridge_selection",
        "get_guided_bridge_selection_launcher_record",
        "list_guided_bridge_selection_launcher_records",
        "guided_bridge_selection_launcher_status",
        "summarize_guided_bridge_selection_launcher",
    ),
    "aether.action.guided_proposal_review_launcher": (
        "open_guided_proposal_review",
        "get_guided_proposal_review_launcher_record",
        "list_guided_proposal_review_launcher_records",
        "guided_proposal_review_launcher_status",
        "summarize_guided_proposal_review_launcher",
    ),
    "aether.action.guided_proposal_decision_launcher": (
        "submit_guided_proposal_decision",
        "get_guided_proposal_decision_launcher_record",
        "list_guided_proposal_decision_launcher_records",
        "guided_proposal_decision_launcher_status",
        "summarize_guided_proposal_decision_launcher",
    ),
}

EXPECTED_ACTION_FUNCTIONS = {
    "aether/action/guided_repair_intake.py": {
        "load_aether_config",
        "get_guided_repair_intake_dir",
        "get_guided_repair_intake_path",
        "get_public_repair_intake_dir",
        "get_public_repair_intake_index_path",
        "load_guided_repair_intake_records",
        "save_guided_repair_intake_records",
        "sanitize_target_path",
        "shorten_id",
        "_sanitize_public_value",
        "sanitize_intake_record_for_public",
        "_save",
        "get_guided_repair_intake_record",
        "list_guided_repair_intake_records",
        "guided_repair_intake_status",
        "summarize_guided_repair_intake",
        "open_guided_repair_intake",
        "submit_guided_repair_intake_decision",
        "_bool_text",
        "export_guided_repair_intake_report",
        "export_guided_repair_intake_index",
        "export_private_guided_repair_intake_record",
    },
    "aether/action/guided_repair_plan_launcher.py": {
        "load_aether_config",
        "get_guided_repair_plan_launcher_dir",
        "get_guided_repair_plan_launcher_path",
        "load_guided_repair_plan_launcher_records",
        "save_guided_repair_plan_launcher_records",
        "sanitize_target_path",
        "shorten_id",
        "_save",
        "launch_guided_repair_plan",
        "get_guided_repair_plan_launcher_record",
        "list_guided_repair_plan_launcher_records",
        "guided_repair_plan_launcher_status",
        "summarize_guided_repair_plan_launcher",
    },
    "aether/action/guided_bridge_selection_launcher.py": {
        "load_aether_config",
        "get_guided_bridge_selection_launcher_dir",
        "get_guided_bridge_selection_launcher_path",
        "load_guided_bridge_selection_launcher_records",
        "save_guided_bridge_selection_launcher_records",
        "sanitize_target_path",
        "shorten_id",
        "_save",
        "launch_guided_bridge_selection",
        "get_guided_bridge_selection_launcher_record",
        "list_guided_bridge_selection_launcher_records",
        "guided_bridge_selection_launcher_status",
        "summarize_guided_bridge_selection_launcher",
    },
    "aether/action/guided_proposal_review_launcher.py": {
        "load_aether_config",
        "get_guided_proposal_review_launcher_dir",
        "get_guided_proposal_review_launcher_path",
        "load_guided_proposal_review_launcher_records",
        "save_guided_proposal_review_launcher_records",
        "sanitize_target_path",
        "shorten_id",
        "_save",
        "open_guided_proposal_review",
        "get_guided_proposal_review_launcher_record",
        "list_guided_proposal_review_launcher_records",
        "guided_proposal_review_launcher_status",
        "summarize_guided_proposal_review_launcher",
    },
    "aether/action/guided_proposal_decision_launcher.py": {
        "load_aether_config",
        "get_guided_proposal_decision_launcher_dir",
        "get_guided_proposal_decision_launcher_path",
        "load_guided_proposal_decision_launcher_records",
        "save_guided_proposal_decision_launcher_records",
        "sanitize_target_path",
        "shorten_id",
        "_save",
        "submit_guided_proposal_decision",
        "get_guided_proposal_decision_launcher_record",
        "list_guided_proposal_decision_launcher_records",
        "guided_proposal_decision_launcher_status",
        "summarize_guided_proposal_decision_launcher",
    },
}

FORBIDDEN_ACTION_TERMS = (
    "apply_patch_proposal",
    "rollback_patch",
    "collect_evidence",
    "execute_tool",
    "subprocess",
    "os.system",
    "requests.",
    "httpx.",
)

GUIDED_ACTION_NAMES = {
    name for names in EXPECTED_GUIDED_IMPORTS.values() for name in names
}
GUIDED_ROUTE_FUNCTION_NAMES = {
    route_fn for _, (route_fn, _, _, _, _, _) in GUIDED_ENDPOINTS.items()
}
WRAPPED_ENDPOINT_COUNT = sum(
    1 for _, (_, _, _, wrap_key, _, _) in GUIDED_ENDPOINTS.items() if wrap_key
)
DIRECT_RETURN_ENDPOINT_COUNT = len(GUIDED_ENDPOINTS) - WRAPPED_ENDPOINT_COUNT


def _canonical_openapi(schema: dict) -> bytes:
    return json.dumps(schema, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _call_name(call: ast.Call) -> str:
    return ast.unparse(call.func)


def _route_functions(tree: ast.Module) -> dict[str, ast.FunctionDef]:
    return {
        node.name: node
        for node in tree.body
        if isinstance(node, ast.FunctionDef)
        and any(
            isinstance(dec, ast.Call)
            and isinstance(dec.func, ast.Attribute)
            and dec.func.attr in ("get", "post", "put", "delete", "patch")
            for dec in node.decorator_list
        )
    }


def _single_return_call(fn: ast.FunctionDef) -> ast.Return:
    returns = [n for n in ast.walk(fn) if isinstance(n, ast.Return)]
    assert len(returns) == 1
    assert returns[0].value is not None
    return returns[0]


def _import_froms(tree: ast.Module) -> list[ast.ImportFrom]:
    return [n for n in tree.body if isinstance(n, ast.ImportFrom)]


def test_guided_openapi_contract_and_operation_ids_are_locked():
    spec = app.openapi()
    paths = spec["paths"]
    assert len(paths) == 304
    assert len(spec["components"]["schemas"]) == 108
    guided_paths = {p for p in paths if p.startswith("/action/guided-")}
    assert guided_paths == {p for _, p in GUIDED_ENDPOINTS}
    for (method, path), (_, _, operation_id, _, request_model, _) in (
        GUIDED_ENDPOINTS.items()
    ):
        assert method.lower() in paths[path]
        assert paths[path][method.lower()]["operationId"] == operation_id
        if request_model is not None:
            body_ref = paths[path][method.lower()]["requestBody"]["content"][
                "application/json"
            ]["schema"]["$ref"]
            assert body_ref == f"#/components/schemas/{request_model}"
        else:
            assert "requestBody" not in paths[path][method.lower()]
    # All other families unchanged.
    assert len({p for p in paths if "/changelog" in p}) == 4
    assert len({p for p in paths if "/final-real-apply-executor" in p}) == 6
    assert len(
        {
            p
            for p in paths
            if any(
                family in p
                for family in (
                    "approved-dry-run-gate",
                    "dry-run-review-gate",
                    "post-apply-verification-gate",
                    "real-apply-approval-gate",
                )
            )
        }
    ) == 24
    assert len({p for p in paths if "/action/repair-" in p}) == 43
    assert len(GUIDED_ENDPOINTS) == 29
    assert WRAPPED_ENDPOINT_COUNT == 26
    assert DIRECT_RETURN_ENDPOINT_COUNT == 3


def test_guided_routes_are_exact_direct_action_pass_throughs():
    tree = ast.parse(GUIDED_LAUNCHER_ROUTER_PATH.read_text(encoding="utf-8"))
    functions = _route_functions(tree)
    guided_functions = {
        name: fn for name, fn in functions.items() if name in GUIDED_ROUTE_FUNCTION_NAMES
    }
    assert set(guided_functions) == GUIDED_ROUTE_FUNCTION_NAMES
    for (method, path), (
        route_fn,
        action_fn,
        _,
        wrap_key,
        request_model,
        call_args,
    ) in GUIDED_ENDPOINTS.items():
        fn = guided_functions[route_fn]
        decorator_paths = [
            dec.args[0].value
            for dec in fn.decorator_list
            if isinstance(dec, ast.Call)
            and isinstance(dec.func, ast.Attribute)
            and dec.func.attr == method.lower()
            and dec.args
        ]
        assert decorator_paths == [path]
        assert all(
            isinstance(dec.func, ast.Attribute)
            and dec.func.value.id == "guided_launcher_router"
            for dec in fn.decorator_list
            if isinstance(dec, ast.Call)
            and isinstance(dec.func, ast.Attribute)
            and dec.func.attr == method.lower()
        )
        if request_model is not None:
            assert len(fn.args.args) == 1
            assert fn.args.args[0].arg == "request"
            assert fn.args.args[0].annotation is not None
            assert ast.unparse(fn.args.args[0].annotation) == request_model
            assert not fn.args.defaults
        else:
            param_spec = _param_specs(fn)
            assert param_spec == _expected_param_specs(call_args)
        return_node = _single_return_call(fn)
        if wrap_key is not None:
            assert isinstance(return_node.value, ast.Dict)
            keys = [
                k.value
                for k in return_node.value.keys
                if isinstance(k, ast.Constant)
            ]
            assert keys == ["name", wrap_key]
            values = return_node.value.values
            assert isinstance(values[0], ast.Constant)
            assert values[0].value == "Aether"
            call = values[1]
        else:
            call = return_node.value
        assert isinstance(call, ast.Call)
        assert isinstance(call.func, ast.Name)
        assert call.func.id == action_fn
        assert [ast.unparse(arg) for arg in call.args] == list(call_args)
        assert not call.keywords
        assert not any(
            isinstance(n, (ast.If, ast.For, ast.While, ast.Try))
            for n in ast.walk(fn)
        )
        called = {
            _call_name(n)
            for n in ast.walk(fn)
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
        }
        assert called == {action_fn}
    # No guided route calls a service module, another family, or a tool.
    all_call_names = {
        ast.unparse(arg)
        for fn in guided_functions.values()
        for n in ast.walk(fn)
        if isinstance(n, ast.Call)
        for arg in [n.func]
        if isinstance(arg, ast.Name)
    }
    assert all_call_names == GUIDED_ACTION_NAMES
    router_source = GUIDED_LAUNCHER_ROUTER_PATH.read_text(encoding="utf-8")
    assert not any(term in router_source for term in FORBIDDEN_ACTION_TERMS)


def _param_specs(fn: ast.FunctionDef) -> dict[str, tuple[str, str | None]]:
    specs = {}
    args = fn.args
    for arg in args.args:
        if arg.arg in ("self", "cls"):
            continue
        default = None
        defaults = args.defaults
        offset = len(args.args) - len(defaults)
        idx = args.args.index(arg)
        if idx >= offset:
            default = ast.unparse(defaults[idx - offset])
        annotation = ast.unparse(arg.annotation) if arg.annotation else None
        if annotation is not None:
            annotation = annotation.replace(" ", "")
        specs[arg.arg] = (annotation, default)
    return specs


def _expected_param_specs(call_args: tuple) -> dict[str, tuple[str, str | None]]:
    specs = {}
    for arg in call_args:
        if arg == "limit":
            specs[arg] = ("int", "50")
        elif arg == "planning_allowed":
            specs[arg] = ("bool|None", "None")
        elif arg == "record_id":
            specs[arg] = ("str", None)
        else:
            specs[arg] = ("str|None", "None")
    return specs


def test_guided_import_boundary_and_router_placement():
    api_tree = ast.parse(API_SERVER_PATH.read_text(encoding="utf-8"))
    router_tree = ast.parse(GUIDED_LAUNCHER_ROUTER_PATH.read_text(encoding="utf-8"))

    # api_server.py no longer imports the 5 guided action modules directly.
    api_guided_action_imports = {
        n.module: tuple(a.name for a in n.names)
        for n in _import_froms(api_tree)
        if n.module in EXPECTED_GUIDED_IMPORTS
    }
    assert api_guided_action_imports == {}
    api_all_modules = {n.module for n in _import_froms(api_tree)}
    assert not any(
        m and "guided" in m and ("service" in m or "services" in m)
        for m in api_all_modules
    )

    # api_server.py no longer defines the 29 guided route functions.
    api_function_names = {
        node.name
        for node in api_tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }
    assert not GUIDED_ROUTE_FUNCTION_NAMES & api_function_names

    # api_server.py imports guided_launcher_router exactly once.
    api_router_imports = [
        (n.module, tuple(a.name for a in n.names))
        for n in _import_froms(api_tree)
        if n.module == "aether.interface.routers.guided_launcher_routes"
    ]
    assert api_router_imports == [
        ("aether.interface.routers.guided_launcher_routes", ("guided_launcher_router",))
    ]

    # api_server.py includes guided_launcher_router exactly once with prefix="".
    include_calls = [
        n
        for n in ast.walk(api_tree)
        if isinstance(n, ast.Call)
        and isinstance(n.func, ast.Attribute)
        and n.func.attr == "include_router"
    ]
    guided_includes = [
        n
        for n in include_calls
        if n.args
        and isinstance(n.args[0], ast.Name)
        and n.args[0].id == "guided_launcher_router"
    ]
    assert len(guided_includes) == 1
    assert any(
        kw.arg == "prefix" and ast.unparse(kw.value) == "''"
        for kw in guided_includes[0].keywords
    )

    # guided_launcher_routes.py exists and defines guided_launcher_router = APIRouter().
    assert GUIDED_LAUNCHER_ROUTER_PATH.is_file()
    router_assigns = [
        n
        for n in router_tree.body
        if isinstance(n, ast.Assign)
        and any(isinstance(t, ast.Name) and t.id == "guided_launcher_router" for t in n.targets)
    ]
    assert len(router_assigns) == 1
    assert ast.unparse(router_assigns[0].value) == "APIRouter()"

    # guided_launcher_routes.py imports exactly the 5 guided action modules
    # with exactly the 29 expected names.
    router_guided_imports = {
        n.module: tuple(a.name for a in n.names)
        for n in _import_froms(router_tree)
        if n.module in EXPECTED_GUIDED_IMPORTS
    }
    assert router_guided_imports == EXPECTED_GUIDED_IMPORTS
    assert sum(len(names) for names in router_guided_imports.values()) == 29

    # guided_launcher_routes.py imports exactly fastapi + api_models + the 5
    # guided action modules; no service modules and no C1/C2/Repair/Changelog/
    # Self-modification/tool/patch/evidence modules.
    allowed_modules = set(EXPECTED_GUIDED_IMPORTS) | {"fastapi", "aether.interface.api_models"}
    router_modules = {n.module for n in _import_froms(router_tree)}
    assert router_modules == allowed_modules

    # No other guided router file exists, especially guided_routes.py.
    router_dir = PROJECT_ROOT / "aether/interface/routers"
    guided_router_files = sorted(p.name for p in router_dir.glob("guided_*_routes.py"))
    assert guided_router_files == ["guided_launcher_routes.py"]
    assert not (router_dir / "guided_routes.py").exists()


def test_guided_test_module_never_invokes_endpoints():
    source = Path(__file__).resolve().read_text(encoding="utf-8")
    tree = ast.parse(source)
    imported_modules = {n.module for n in _import_froms(tree)}
    assert not any(
        m and "testclient" in m for m in imported_modules
    )
    assert not any(
        n.module and "guided" in n.module and "action" in n.module
        for n in _import_froms(tree)
    )
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                assert node.func.id not in GUIDED_ACTION_NAMES
                assert node.func.id not in GUIDED_ROUTE_FUNCTION_NAMES
            if isinstance(node.func, ast.Attribute):
                assert "TestClient" not in ast.unparse(node.func)


def test_guided_action_static_risk_unchanged():
    diff = subprocess.run(
        [
            "git",
            "diff",
            "--quiet",
            "HEAD",
            "--",
        ]
        + [str(p.relative_to(PROJECT_ROOT)) for p in GUIDED_ACTION_PATHS],
        cwd=PROJECT_ROOT,
        capture_output=True,
    )
    assert diff.returncode == 0, "guided action modules must be unchanged in 82AQ"
    for path in GUIDED_ACTION_PATHS:
        rel = str(path.relative_to(PROJECT_ROOT))
        tree = ast.parse(path.read_text(encoding="utf-8"))
        functions = {
            node.name
            for node in tree.body
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        }
        assert functions == EXPECTED_ACTION_FUNCTIONS[rel]
        source = path.read_text(encoding="utf-8")
        assert not any(term in source for term in FORBIDDEN_ACTION_TERMS)
        call_targets = {
            _call_name(node)
            for node in ast.walk(tree)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
        }
        assert not any(
            term in target for target in call_targets for term in FORBIDDEN_ACTION_TERMS
        )
        imported_modules = {n.module for n in _import_froms(tree)}
        assert not any(
            term in (m or "") for m in imported_modules for term in FORBIDDEN_ACTION_TERMS
        )
    # guided_repair_intake export behavior is pre-existing declarative file
    # writes, never invoked by this module.
    intake_source = (
        PROJECT_ROOT / "aether/action/guided_repair_intake.py"
    ).read_text(encoding="utf-8")
    assert intake_source.count("write_text") >= 3
