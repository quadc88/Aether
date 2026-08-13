"""Tests-only safety boundary for the changelog router extraction (82AP Build).

AST/OpenAPI-based only. No changelog endpoint is ever invoked, so no
public/private changelog files, milestone reports, or runtime state can be
written by this module.
"""

from __future__ import annotations

import ast
import json
import subprocess
from pathlib import Path

import pytest

from aether.interface.api_server import app


PROJECT_ROOT = Path(__file__).resolve().parents[1]
API_SERVER_PATH = PROJECT_ROOT / "aether/interface/api_server.py"
CHANGELOG_ROUTER_PATH = (
    PROJECT_ROOT / "aether/interface/routers/changelog_routes.py"
)
CHANGELOG_ACTION_PATH = PROJECT_ROOT / "aether/action/changelog_exporter.py"

CHANGELOG_ENDPOINTS = {
    ("POST", "/action/changelog/export-public"): (
        "export_public_changelog_action",
        "export_public_changelog",
        "export_public_changelog_action_action_changelog_export_public_post",
    ),
    ("POST", "/action/changelog/export-milestone"): (
        "export_milestone_changelog_action",
        "export_milestone_report",
        "export_milestone_changelog_action_action_changelog_export_milestone_post",
    ),
    ("POST", "/action/changelog/export-private"): (
        "export_private_changelog_action",
        "export_private_changelog_report",
        "export_private_changelog_action_action_changelog_export_private_post",
    ),
    ("GET", "/action/changelog/status"): (
        "get_changelog_status",
        "changelog_export_status",
        "get_changelog_status_action_changelog_status_get",
    ),
}

EXPECTED_ACTION_FUNCTIONS = {
    "_audit_changelog_export",
    "load_aether_config",
    "get_private_export_dir",
    "get_public_history_dir",
    "get_public_milestone_dir",
    "sanitize_target_path",
    "shorten_id",
    "sanitize_mutation_for_public",
    "build_changelog_markdown",
    "export_public_changelog",
    "export_milestone_report",
    "export_private_changelog_report",
    "changelog_export_status",
}

ALLOWED_ROUTER_IMPORT_MODULES = {
    "fastapi",
    "aether.interface.api_models",
    "aether.action.changelog_exporter",
}

FORBIDDEN_ROUTER_TERMS = (
    "service",
    "repair",
    "guided",
    "self_modification",
    "tool_executor",
    "apply",
    "rollback",
    "evidence",
    "patch",
    "dry_run",
    "simulation",
    "executor",
)

FORBIDDEN_ACTION_TERMS = (
    "real_apply",
    "rollback",
    "evidence",
    "apply_patch",
)


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


def _single_return_call(fn: ast.FunctionDef) -> ast.Call:
    returns = [n for n in ast.walk(fn) if isinstance(n, ast.Return) and n.value]
    assert len(returns) == 1
    assert isinstance(returns[0].value, ast.Call)
    return returns[0].value


def _import_froms(tree: ast.Module) -> list[ast.ImportFrom]:
    return [n for n in tree.body if isinstance(n, ast.ImportFrom)]


def test_changelog_openapi_contract_and_operation_ids_are_locked():
    spec = app.openapi()
    paths = spec["paths"]
    changelog_paths = {p for p in paths if "/changelog" in p}
    assert changelog_paths == {p for _, p in CHANGELOG_ENDPOINTS}
    for (method, path), (_, _, operation_id) in CHANGELOG_ENDPOINTS.items():
        assert method.lower() in paths[path]
        assert paths[path][method.lower()]["operationId"] == operation_id
    assert len(paths) == 306


def test_changelog_routes_are_exact_direct_action_pass_throughs():
    tree = ast.parse(CHANGELOG_ROUTER_PATH.read_text(encoding="utf-8"))
    functions = _route_functions(tree)
    assert set(functions) == {name for _, (name, _, _) in CHANGELOG_ENDPOINTS.items()}
    for (method, path), (route_fn, action_fn, _) in CHANGELOG_ENDPOINTS.items():
        fn = functions[route_fn]
        route_paths = [
            dec.args[0].value
            for dec in fn.decorator_list
            if isinstance(dec, ast.Call)
            and isinstance(dec.func, ast.Attribute)
            and dec.func.attr == method.lower()
            and dec.args
        ]
        assert route_paths == [path]
        call = _single_return_call(fn)
        assert _call_name(call) == action_fn
        assert not any(
            isinstance(n, (ast.If, ast.For, ast.While, ast.Try))
            for n in ast.walk(fn)
        )


def test_changelog_import_boundary_and_api_server_removal():
    router_tree = ast.parse(CHANGELOG_ROUTER_PATH.read_text(encoding="utf-8"))
    imports = _import_froms(router_tree)
    assert {n.module for n in imports} == ALLOWED_ROUTER_IMPORT_MODULES
    imported_names = [alias.name for n in imports for alias in n.names]
    assert "APIRouter" in imported_names
    assert {
        "ChangelogExportRequest",
        "MilestoneReportExportRequest",
        "export_public_changelog",
        "export_milestone_report",
        "export_private_changelog_report",
        "changelog_export_status",
    } <= set(imported_names)
    router_assignments = [
        n for n in router_tree.body
        if isinstance(n, ast.Assign)
        and any(
            isinstance(t, ast.Name) and t.id == "changelog_router"
            for t in n.targets
        )
        and isinstance(n.value, ast.Call)
        and _call_name(n.value) == "APIRouter"
    ]
    assert len(router_assignments) == 1

    api_tree = ast.parse(API_SERVER_PATH.read_text(encoding="utf-8"))
    api_route_functions = _route_functions(api_tree)
    assert not any(
        any("/changelog" in str(dec.args[0].value)
            for dec in fn.decorator_list
            if isinstance(dec, ast.Call) and dec.args)
        for fn in api_route_functions.values()
    )
    assert not any(
        n.module == "aether.action.changelog_exporter" for n in _import_froms(api_tree)
    )
    changelog_imports = [
        n for n in _import_froms(api_tree)
        if n.module == "aether.interface.routers.changelog_routes"
    ]
    assert len(changelog_imports) == 1
    assert [a.name for a in changelog_imports[0].names] == ["changelog_router"]
    include_calls = [
        n for n in ast.walk(api_tree)
        if isinstance(n, ast.Call)
        and isinstance(n.func, ast.Attribute)
        and n.func.attr == "include_router"
        and n.args
        and isinstance(n.args[0], ast.Name)
        and n.args[0].id == "changelog_router"
    ]
    assert len(include_calls) == 1


def test_changelog_action_static_risk_unchanged():
    diff = subprocess.run(
        [
            "git",
            "diff",
            "--quiet",
            "HEAD",
            "--",
            str(CHANGELOG_ACTION_PATH.relative_to(PROJECT_ROOT)),
        ],
        cwd=PROJECT_ROOT,
        capture_output=True,
    )
    assert diff.returncode == 0, "changelog_exporter.py must be unchanged in 82AP"
    tree = ast.parse(CHANGELOG_ACTION_PATH.read_text(encoding="utf-8"))
    functions = {
        node.name for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }
    assert functions == EXPECTED_ACTION_FUNCTIONS
    call_targets = {
        _call_name(node)
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    }
    assert not any(
        term in target for target in call_targets for term in FORBIDDEN_ACTION_TERMS
    )
    imported_modules = {
        n.module for n in _import_froms(tree)
    }
    assert not any(
        term in (m or "") for m in imported_modules for term in FORBIDDEN_ACTION_TERMS
    )
