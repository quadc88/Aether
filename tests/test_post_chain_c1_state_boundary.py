"""Tests-only safety boundary for the 24 post-chain C1 gate endpoints."""

from __future__ import annotations

import ast
import hashlib
import importlib
from pathlib import Path
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from aether.action import (
    approval_queue,
    approved_dry_run_gate,
    dry_run_review_gate,
    mutation_log,
    patch_apply,
    patch_proposal,
    patch_review,
    patch_rollback,
    post_apply_verification_gate,
    proposal_review_console,
    real_apply_approval_gate,
    revised_proposal_review_loop,
)
from aether.interface.api_server import app
from aether.memory.graph import store as graph_store
from aether.memory.timeline import recorder as timeline_recorder
from aether.memory.working.store import WorkingMemory


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REAL_DATA_ROOT = Path("/home/aether/data")

C1_ENDPOINTS = {
    ("POST", "/action/approved-dry-run-gate/open"): (
        "open_approved_dry_run_gate_action",
        "open_approved_dry_run_gate",
        "open_approved_dry_run_gate_action_action_approved_dry_run_gate_open_post",
        "record",
    ),
    ("POST", "/action/approved-dry-run-gate/execute"): (
        "execute_approved_dry_run_gate_action",
        "execute_approved_dry_run",
        "execute_approved_dry_run_gate_action_action_approved_dry_run_gate_execute_post",
        "record",
    ),
    ("GET", "/action/approved-dry-run-gate/status"): (
        "get_approved_dry_run_gate_status_action",
        "approved_dry_run_gate_status",
        "get_approved_dry_run_gate_status_action_action_approved_dry_run_gate_status_get",
        "approved_dry_run_gate",
    ),
    ("GET", "/action/approved-dry-run-gate/list"): (
        "list_approved_dry_run_gate_action",
        "list_approved_dry_run_gate_records",
        "list_approved_dry_run_gate_action_action_approved_dry_run_gate_list_get",
        "records",
    ),
    ("GET", "/action/approved-dry-run-gate/{record_id}/summary"): (
        "summarize_approved_dry_run_gate_action",
        "summarize_approved_dry_run_gate",
        "summarize_approved_dry_run_gate_action_action_approved_dry_run_gate__record_id__summary_get",
        "summary",
    ),
    ("GET", "/action/approved-dry-run-gate/{record_id}"): (
        "get_approved_dry_run_gate_action",
        "get_approved_dry_run_gate_record",
        "get_approved_dry_run_gate_action_action_approved_dry_run_gate__record_id__get",
        "record",
    ),
    ("POST", "/action/dry-run-review-gate/open"): (
        "open_dry_run_review_gate_action",
        "open_dry_run_review_gate",
        "open_dry_run_review_gate_action_action_dry_run_review_gate_open_post",
        "record",
    ),
    ("POST", "/action/dry-run-review-gate/submit"): (
        "submit_dry_run_review_action",
        "submit_dry_run_review",
        "submit_dry_run_review_action_action_dry_run_review_gate_submit_post",
        "record",
    ),
    ("GET", "/action/dry-run-review-gate/status"): (
        "get_dry_run_review_gate_status_action",
        "dry_run_review_gate_status",
        "get_dry_run_review_gate_status_action_action_dry_run_review_gate_status_get",
        "dry_run_review_gate",
    ),
    ("GET", "/action/dry-run-review-gate/list"): (
        "list_dry_run_review_gate_action",
        "list_dry_run_review_gate_records",
        "list_dry_run_review_gate_action_action_dry_run_review_gate_list_get",
        "records",
    ),
    ("GET", "/action/dry-run-review-gate/{record_id}/summary"): (
        "summarize_dry_run_review_gate_action",
        "summarize_dry_run_review_gate",
        "summarize_dry_run_review_gate_action_action_dry_run_review_gate__record_id__summary_get",
        "summary",
    ),
    ("GET", "/action/dry-run-review-gate/{record_id}"): (
        "get_dry_run_review_gate_action",
        "get_dry_run_review_gate_record",
        "get_dry_run_review_gate_action_action_dry_run_review_gate__record_id__get",
        "record",
    ),
    ("POST", "/action/real-apply-approval-gate/open"): (
        "open_real_apply_approval_gate_action",
        "open_real_apply_approval_gate",
        "open_real_apply_approval_gate_action_action_real_apply_approval_gate_open_post",
        "record",
    ),
    ("POST", "/action/real-apply-approval-gate/submit"): (
        "submit_real_apply_final_decision_action",
        "submit_real_apply_final_decision",
        "submit_real_apply_final_decision_action_action_real_apply_approval_gate_submit_post",
        "record",
    ),
    ("GET", "/action/real-apply-approval-gate/status"): (
        "get_real_apply_approval_gate_status_action",
        "real_apply_approval_gate_status",
        "get_real_apply_approval_gate_status_action_action_real_apply_approval_gate_status_get",
        "real_apply_approval_gate",
    ),
    ("GET", "/action/real-apply-approval-gate/list"): (
        "list_real_apply_approval_gate_action",
        "list_real_apply_approval_gate_records",
        "list_real_apply_approval_gate_action_action_real_apply_approval_gate_list_get",
        "records",
    ),
    ("GET", "/action/real-apply-approval-gate/{record_id}/summary"): (
        "summarize_real_apply_approval_gate_action",
        "summarize_real_apply_approval_gate",
        "summarize_real_apply_approval_gate_action_action_real_apply_approval_gate__record_id__summary_get",
        "summary",
    ),
    ("GET", "/action/real-apply-approval-gate/{record_id}"): (
        "get_real_apply_approval_gate_action",
        "get_real_apply_approval_gate_record",
        "get_real_apply_approval_gate_action_action_real_apply_approval_gate__record_id__get",
        "record",
    ),
    ("POST", "/action/post-apply-verification-gate/open"): (
        "open_post_apply_verification_gate_action",
        "open_post_apply_verification_gate",
        "open_post_apply_verification_gate_action_action_post_apply_verification_gate_open_post",
        "record",
    ),
    ("POST", "/action/post-apply-verification-gate/submit"): (
        "submit_post_apply_verification_action",
        "submit_post_apply_verification",
        "submit_post_apply_verification_action_action_post_apply_verification_gate_submit_post",
        "record",
    ),
    ("GET", "/action/post-apply-verification-gate/status"): (
        "get_post_apply_verification_gate_status_action",
        "post_apply_verification_gate_status",
        "get_post_apply_verification_gate_status_action_action_post_apply_verification_gate_status_get",
        "post_apply_verification_gate",
    ),
    ("GET", "/action/post-apply-verification-gate/list"): (
        "list_post_apply_verification_gate_action",
        "list_post_apply_verification_gate_records",
        "list_post_apply_verification_gate_action_action_post_apply_verification_gate_list_get",
        "records",
    ),
    ("GET", "/action/post-apply-verification-gate/{record_id}/summary"): (
        "summarize_post_apply_verification_gate_action",
        "summarize_post_apply_verification_gate",
        "summarize_post_apply_verification_gate_action_action_post_apply_verification_gate__record_id__summary_get",
        "summary",
    ),
    ("GET", "/action/post-apply-verification-gate/{record_id}"): (
        "get_post_apply_verification_gate_action",
        "get_post_apply_verification_gate_record",
        "get_post_apply_verification_gate_action_action_post_apply_verification_gate__record_id__get",
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

C1_MODULE_PATHS = (
    PROJECT_ROOT / "aether/action/approved_dry_run_gate.py",
    PROJECT_ROOT / "aether/action/dry_run_review_gate.py",
    PROJECT_ROOT / "aether/action/real_apply_approval_gate.py",
    PROJECT_ROOT / "aether/action/post_apply_verification_gate.py",
)

C1_ROUTE_TO_SERVICE_HANDLER = {
    "open_approved_dry_run_gate_action":
        "handle_open_approved_dry_run_gate",
    "execute_approved_dry_run_gate_action":
        "handle_execute_approved_dry_run",
    "get_approved_dry_run_gate_status_action":
        "handle_get_approved_dry_run_gate_status",
    "list_approved_dry_run_gate_action":
        "handle_list_approved_dry_run_gate_records",
    "summarize_approved_dry_run_gate_action":
        "handle_summarize_approved_dry_run_gate",
    "get_approved_dry_run_gate_action":
        "handle_get_approved_dry_run_gate_record",
    "open_dry_run_review_gate_action":
        "handle_open_dry_run_review_gate",
    "submit_dry_run_review_action":
        "handle_submit_dry_run_review",
    "get_dry_run_review_gate_status_action":
        "handle_get_dry_run_review_gate_status",
    "list_dry_run_review_gate_action":
        "handle_list_dry_run_review_gate_records",
    "summarize_dry_run_review_gate_action":
        "handle_summarize_dry_run_review_gate",
    "get_dry_run_review_gate_action":
        "handle_get_dry_run_review_gate_record",
    "open_real_apply_approval_gate_action":
        "handle_open_real_apply_approval_gate",
    "submit_real_apply_final_decision_action":
        "handle_submit_real_apply_final_decision",
    "get_real_apply_approval_gate_status_action":
        "handle_get_real_apply_approval_gate_status",
    "list_real_apply_approval_gate_action":
        "handle_list_real_apply_approval_gate_records",
    "summarize_real_apply_approval_gate_action":
        "handle_summarize_real_apply_approval_gate",
    "get_real_apply_approval_gate_action":
        "handle_get_real_apply_approval_gate_record",
    "open_post_apply_verification_gate_action":
        "handle_open_post_apply_verification_gate",
    "submit_post_apply_verification_action":
        "handle_submit_post_apply_verification",
    "get_post_apply_verification_gate_status_action":
        "handle_get_post_apply_verification_gate_status",
    "list_post_apply_verification_gate_action":
        "handle_list_post_apply_verification_gate_records",
    "summarize_post_apply_verification_gate_action":
        "handle_summarize_post_apply_verification_gate",
    "get_post_apply_verification_gate_action":
        "handle_get_post_apply_verification_gate_record",
}

C1_SERVICE_HANDLER_TO_ACTION = {
    "approved_dry_run_gate_service.py": {
        "handle_open_approved_dry_run_gate": "open_approved_dry_run_gate",
        "handle_execute_approved_dry_run": "execute_approved_dry_run",
        "handle_get_approved_dry_run_gate_status":
            "approved_dry_run_gate_status",
        "handle_list_approved_dry_run_gate_records":
            "list_approved_dry_run_gate_records",
        "handle_summarize_approved_dry_run_gate":
            "summarize_approved_dry_run_gate",
        "handle_get_approved_dry_run_gate_record":
            "get_approved_dry_run_gate_record",
    },
    "dry_run_review_gate_service.py": {
        "handle_open_dry_run_review_gate": "open_dry_run_review_gate",
        "handle_submit_dry_run_review": "submit_dry_run_review",
        "handle_get_dry_run_review_gate_status": "dry_run_review_gate_status",
        "handle_list_dry_run_review_gate_records":
            "list_dry_run_review_gate_records",
        "handle_summarize_dry_run_review_gate":
            "summarize_dry_run_review_gate",
        "handle_get_dry_run_review_gate_record":
            "get_dry_run_review_gate_record",
    },
    "real_apply_approval_gate_service.py": {
        "handle_open_real_apply_approval_gate":
            "open_real_apply_approval_gate",
        "handle_submit_real_apply_final_decision":
            "submit_real_apply_final_decision",
        "handle_get_real_apply_approval_gate_status":
            "real_apply_approval_gate_status",
        "handle_list_real_apply_approval_gate_records":
            "list_real_apply_approval_gate_records",
        "handle_summarize_real_apply_approval_gate":
            "summarize_real_apply_approval_gate",
        "handle_get_real_apply_approval_gate_record":
            "get_real_apply_approval_gate_record",
    },
    "post_apply_verification_gate_service.py": {
        "handle_open_post_apply_verification_gate":
            "open_post_apply_verification_gate",
        "handle_submit_post_apply_verification":
            "submit_post_apply_verification",
        "handle_get_post_apply_verification_gate_status":
            "post_apply_verification_gate_status",
        "handle_list_post_apply_verification_gate_records":
            "list_post_apply_verification_gate_records",
        "handle_summarize_post_apply_verification_gate":
            "summarize_post_apply_verification_gate",
        "handle_get_post_apply_verification_gate_record":
            "get_post_apply_verification_gate_record",
    },
}

WATCHED_REAL_ROOTS = (
    PROJECT_ROOT / "aether",
    PROJECT_ROOT / "tests",
    PROJECT_ROOT / "docs/history",
    REAL_DATA_ROOT / "private",
    REAL_DATA_ROOT / "timeline",
    REAL_DATA_ROOT / "graph_db",
)

API_CASES = (
    ("POST", "/action/approved-dry-run-gate/open",
     {"source_type": "invalid", "source_id": "missing", "metadata": {}}, "record"),
    ("POST", "/action/approved-dry-run-gate/execute",
     {"gate_record_id": "missing", "create_approval_if_required": False, "metadata": {}},
     "record"),
    ("GET", "/action/approved-dry-run-gate/status", None, "approved_dry_run_gate"),
    ("GET", "/action/approved-dry-run-gate/list", None, "records"),
    ("GET", "/action/approved-dry-run-gate/missing/summary", None, "summary"),
    ("GET", "/action/approved-dry-run-gate/missing", None, "record"),
    ("POST", "/action/dry-run-review-gate/open",
     {"source_type": "invalid", "source_id": "missing", "metadata": {}}, "record"),
    ("POST", "/action/dry-run-review-gate/submit",
     {"review_gate_record_id": "missing", "decision": "accept", "metadata": {}}, "record"),
    ("GET", "/action/dry-run-review-gate/status", None, "dry_run_review_gate"),
    ("GET", "/action/dry-run-review-gate/list", None, "records"),
    ("GET", "/action/dry-run-review-gate/missing/summary", None, "summary"),
    ("GET", "/action/dry-run-review-gate/missing", None, "record"),
    ("POST", "/action/real-apply-approval-gate/open",
     {"source_type": "invalid", "source_id": "missing",
      "create_approval_item": False, "metadata": {}}, "record"),
    ("POST", "/action/real-apply-approval-gate/submit",
     {"gate_record_id": "missing", "decision": "reject_real_apply", "metadata": {}},
     "record"),
    ("GET", "/action/real-apply-approval-gate/status", None,
     "real_apply_approval_gate"),
    ("GET", "/action/real-apply-approval-gate/list", None, "records"),
    ("GET", "/action/real-apply-approval-gate/missing/summary", None, "summary"),
    ("GET", "/action/real-apply-approval-gate/missing", None, "record"),
    ("POST", "/action/post-apply-verification-gate/open",
     {"source_type": "invalid", "source_id": "missing", "metadata": {}}, "record"),
    ("POST", "/action/post-apply-verification-gate/submit",
     {"verification_record_id": "missing", "decision": "needs_investigation",
      "metadata": {}}, "record"),
    ("GET", "/action/post-apply-verification-gate/status", None,
     "post_apply_verification_gate"),
    ("GET", "/action/post-apply-verification-gate/list", None, "records"),
    ("GET", "/action/post-apply-verification-gate/missing/summary", None, "summary"),
    ("GET", "/action/post-apply-verification-gate/missing", None, "record"),
)


def _fingerprint(root: Path) -> list[tuple]:
    if not root.exists():
        return []
    result = []
    for path in sorted(root.rglob("*")):
        try:
            relative = str(path.relative_to(root))
            if path.is_file():
                result.append(
                    ("file", relative, path.stat().st_size,
                     hashlib.sha256(path.read_bytes()).hexdigest())
                )
            elif path.is_dir():
                result.append(("dir", relative))
        except FileNotFoundError:
            continue
    return result


def _real_fingerprints() -> dict[str, list[tuple]]:
    return {str(root): _fingerprint(root) for root in WATCHED_REAL_ROOTS}


@pytest.fixture(scope="module", autouse=True)
def real_source_runtime_and_docs_roots_unchanged():
    """Prove this focused C1 module cannot drift real source or state roots."""

    before = _real_fingerprints()
    yield
    assert _real_fingerprints() == before


@pytest.fixture
def isolated_c1_env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    data_root = tmp_path / "AetherData"
    roots = {
        "data_root": data_root,
        "private_dir": data_root / "private",
        "vault_dir": data_root / "vault",
        "vector_db_dir": data_root / "vector_db",
        "timeline_dir": data_root / "timeline",
        "graph_db_dir": data_root / "graph_db",
        "logs_dir": data_root / "logs",
        "backups_dir": data_root / "backups",
        "patch_target_dir": data_root / "patch_targets",
        "docs_history_dir": data_root / "docs_history",
    }
    for root in roots.values():
        root.mkdir(parents=True, exist_ok=True)
        resolved = root.resolve()
        assert resolved.is_relative_to(tmp_path.resolve())
        assert not resolved.is_relative_to(PROJECT_ROOT.resolve())
        assert not resolved.is_relative_to(REAL_DATA_ROOT.resolve())

    config = {"paths": {name: str(path) for name, path in roots.items()}}

    def isolated_config(*_args, **_kwargs):
        return config

    config_modules = (
        approved_dry_run_gate,
        dry_run_review_gate,
        real_apply_approval_gate,
        post_apply_verification_gate,
        approval_queue,
        proposal_review_console,
        revised_proposal_review_loop,
        patch_proposal,
        patch_review,
        patch_apply,
        patch_rollback,
        mutation_log,
        timeline_recorder,
        graph_store,
    )
    for module in config_modules:
        monkeypatch.setattr(module, "load_aether_config", isolated_config)

    core_runtime = importlib.import_module("aether.core.runtime")
    isolated_runtime = SimpleNamespace(
        working_memory=WorkingMemory(max_events=100),
        status=lambda: "awake",
    )
    monkeypatch.setattr(core_runtime, "runtime", isolated_runtime)

    patch_calls = []

    def guarded_patch_apply(proposal_id, dry_run=True, metadata=None):
        patch_calls.append((proposal_id, dry_run, metadata))
        assert dry_run is True, "C1 attempted forbidden real apply"
        for value in (metadata or {}).values():
            if isinstance(value, str):
                resolved_text = value.replace("\\", "/").lower()
                assert "/home/aether/data" not in resolved_text
                assert str(PROJECT_ROOT).lower() not in resolved_text
        return {
            "id": "isolated_dry_run",
            "status": "dry_run",
            "proposal_id": proposal_id,
            "dry_run": True,
            "applied": False,
            "backup_path": None,
            "warnings": [],
        }

    monkeypatch.setattr(
        approved_dry_run_gate, "apply_patch_proposal", guarded_patch_apply
    )

    c2_read_calls = []

    def forbid_c2_record_read(*args, **kwargs):
        c2_read_calls.append((args, kwargs))
        pytest.fail("C1 invalid-source tests reached the C2 executor boundary")

    monkeypatch.setattr(
        post_apply_verification_gate,
        "get_final_real_apply_executor_record",
        forbid_c2_record_read,
    )

    yield SimpleNamespace(
        client=TestClient(app),
        roots=roots,
        patch_calls=patch_calls,
        c2_read_calls=c2_read_calls,
        runtime=isolated_runtime,
    )

    assert patch_calls == []
    assert c2_read_calls == []
    for path in roots["private_dir"].rglob("*"):
        assert path.resolve().is_relative_to(tmp_path.resolve())


def test_c1_openapi_contract_and_operation_ids_are_locked():
    schema = app.openapi()
    assert len(schema.get("paths", {})) == 300
    assert len(schema.get("components", {}).get("schemas", {})) == 103
    assert len(C1_ENDPOINTS) == 24

    for (method, path), (_, _, operation_id, _) in C1_ENDPOINTS.items():
        assert schema["paths"][path][method.lower()]["operationId"] == operation_id


def test_c1_routes_are_exact_single_service_pass_throughs():
    source_path = PROJECT_ROOT / "aether/interface/api_server.py"
    tree = ast.parse(source_path.read_text(encoding="utf-8"))
    expected = C1_ROUTE_TO_SERVICE_HANDLER
    found = {}

    for node in tree.body:
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if node.name not in expected:
            continue
        assert len(node.body) == 1
        assert isinstance(node.body[0], ast.Return)
        calls = [child for child in ast.walk(node.body[0]) if isinstance(child, ast.Call)]
        assert len(calls) == 1
        assert isinstance(calls[0].func, ast.Name)
        assert calls[0].func.id == expected[node.name]
        text = ast.unparse(node.body[0]).lower()
        for forbidden in (
            "execute_final_real_apply",
            "apply_patch_proposal",
            "rollback_patch",
            "collect_evidence",
            "execute_tool",
            "subprocess",
            "write_text",
            "write_bytes",
            "open(",
        ):
            assert forbidden not in text
        found[node.name] = calls[0].func.id

    assert found == expected


def test_c1_action_modules_have_no_real_apply_or_execution_capability():
    approved_apply_calls = []

    for path in C1_MODULE_PATHS:
        tree = ast.parse(path.read_text(encoding="utf-8"))
        imported = []
        calls = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                imported.extend(
                    (node.module, alias.name) for alias in node.names
                )
            elif isinstance(node, ast.Call):
                calls.append(node)

        imported_names = {name for _, name in imported}
        assert "execute_final_real_apply" not in imported_names
        assert "rollback_patch_proposal" not in imported_names
        assert "collect_evidence" not in imported_names
        assert "execute_tool" not in imported_names

        final_executor_imports = {
            name for module, name in imported
            if module == "aether.action.final_real_apply_executor"
        }
        if path.name == "post_apply_verification_gate.py":
            assert final_executor_imports == {"get_final_real_apply_executor_record"}
        else:
            assert final_executor_imports == set()

        for call in calls:
            call_name = ast.unparse(call.func)
            assert call_name != "execute_final_real_apply"
            assert call_name not in {
                "rollback_patch_proposal",
                "execute_patch_rollback",
                "collect_evidence",
                "execute_tool",
            }
            if call_name == "apply_patch_proposal":
                approved_apply_calls.append((path.name, call))
                assert path.name == "approved_dry_run_gate.py"
                assert len(call.args) >= 2
                assert isinstance(call.args[1], ast.Constant)
                assert call.args[1].value is True

    assert len(approved_apply_calls) == 1
    post_source = (
        PROJECT_ROOT / "aether/action/post_apply_verification_gate.py"
    ).read_text(encoding="utf-8")
    assert '"rollback_recommended"' in post_source
    assert "this gate does not rollback" in post_source


@pytest.mark.parametrize(
    ("method", "path", "payload", "wrapper_key"),
    API_CASES,
    ids=[f"{method}-{path}" for method, path, _, _ in API_CASES],
)
def test_all_c1_endpoints_have_safe_isolated_api_behavior(
    isolated_c1_env, method, path, payload, wrapper_key
):
    if method == "POST":
        response = isolated_c1_env.client.post(path, json=payload)
    else:
        response = isolated_c1_env.client.get(path)

    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "Aether"
    assert wrapper_key in body

    if method == "POST":
        assert body["record"]["status"] == "blocked"
    elif path.endswith("/missing") or path.endswith("/missing/summary"):
        assert body[wrapper_key] is None
    elif path.endswith("/list"):
        assert isinstance(body[wrapper_key], list)
    elif path.endswith("/status"):
        assert isinstance(body[wrapper_key], dict)

    assert isolated_c1_env.patch_calls == []
    assert isolated_c1_env.c2_read_calls == []


def test_isolated_c1_fixture_covers_all_required_roots(isolated_c1_env):
    expected = {
        "private_dir",
        "vault_dir",
        "vector_db_dir",
        "timeline_dir",
        "graph_db_dir",
        "logs_dir",
        "backups_dir",
        "patch_target_dir",
        "docs_history_dir",
    }
    assert expected.issubset(isolated_c1_env.roots)
    for name in expected:
        root = isolated_c1_env.roots[name].resolve()
        assert root.exists()
        assert not root.is_relative_to(PROJECT_ROOT.resolve())
        assert not root.is_relative_to(REAL_DATA_ROOT.resolve())


def test_protected_endpoint_contracts_remain_outside_c1():
    schema = app.openapi()
    c1_paths = {path for _, path in C1_ENDPOINTS}
    for (method, path), operation_id in PROTECTED_ENDPOINTS.items():
        assert path not in c1_paths
        assert schema["paths"][path][method.lower()]["operationId"] == operation_id

    test_tree = ast.parse(Path(__file__).read_text(encoding="utf-8"))
    invoked_paths = set()
    for node in ast.walk(test_tree):
        if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Attribute):
            continue
        if node.func.attr not in {"get", "post"} or not node.args:
            continue
        if isinstance(node.args[0], ast.Name) and node.args[0].id == "path":
            continue
        if isinstance(node.args[0], ast.Constant):
            invoked_paths.add(node.args[0].value)
    assert not invoked_paths.intersection(path for _, path in PROTECTED_ENDPOINTS)
    assert not any(str(path).startswith("/action/final-real-apply-executor")
                   for path in invoked_paths)


def test_c1_service_extraction_is_exact_and_router_extraction_has_not_started():
    router_paths = (
        "approved_dry_run_gate_routes.py",
        "dry_run_review_gate_routes.py",
        "real_apply_approval_gate_routes.py",
        "post_apply_verification_gate_routes.py",
        "final_real_apply_executor_routes.py",
    )
    services_root = PROJECT_ROOT / "aether/action/services"
    assert (services_root / "final_real_apply_executor_service.py").exists()  # C2 service extraction (82AK)
    assert not (services_root / "final_real_apply_executor_routes.py").exists()  # no C2 router extraction
    assert {
        handler
        for handlers in C1_SERVICE_HANDLER_TO_ACTION.values()
        for handler in handlers
    } == set(C1_ROUTE_TO_SERVICE_HANDLER.values())

    for filename, expected_handlers in C1_SERVICE_HANDLER_TO_ACTION.items():
        service_path = services_root / filename
        assert service_path.exists()
        tree = ast.parse(service_path.read_text(encoding="utf-8"))
        functions = {
            node.name: node
            for node in tree.body
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        }
        assert set(functions) == set(expected_handlers)

        imported_modules = {
            node.module for node in tree.body
            if isinstance(node, ast.ImportFrom)
        }
        assert "aether.action.final_real_apply_executor" not in imported_modules

        for handler, action in expected_handlers.items():
            node = functions[handler]
            assert len(node.body) == 1
            assert isinstance(node.body[0], ast.Return)
            calls = [
                child for child in ast.walk(node.body[0])
                if isinstance(child, ast.Call)
            ]
            assert len(calls) == 1
            assert isinstance(calls[0].func, ast.Name)
            assert calls[0].func.id == action
            return_text = ast.unparse(node.body[0])
            assert "'name': 'Aether'" in return_text
            for forbidden in (
                "final_real_apply_executor",
                "execute_final_real_apply",
                "apply_patch_proposal",
            ):
                assert forbidden not in return_text

    assert not any(
        (PROJECT_ROOT / "aether/interface/routers" / name).exists()
        for name in router_paths
    )

    tree = ast.parse(
        (PROJECT_ROOT / "aether/interface/api_server.py").read_text(encoding="utf-8")
    )
    direct_modules = {
        "aether.action.approved_dry_run_gate",
        "aether.action.dry_run_review_gate",
        "aether.action.real_apply_approval_gate",
        "aether.action.post_apply_verification_gate",
    }
    service_modules = {
        "aether.action.services.approved_dry_run_gate_service",
        "aether.action.services.dry_run_review_gate_service",
        "aether.action.services.real_apply_approval_gate_service",
        "aether.action.services.post_apply_verification_gate_service",
    }
    imported_modules = {
        node.module for node in tree.body
        if isinstance(node, ast.ImportFrom)
    }
    assert direct_modules.isdisjoint(imported_modules)
    assert service_modules.issubset(imported_modules)

    include_router_calls = [
        node for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "include_router"
    ]
    assert len(include_router_calls) == 16
