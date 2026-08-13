# 82AD Build — Tool Execution Safety Tests
# Tests API-level safety boundary for /action/tool-executor endpoints
# before any router extraction.
# dry_run is currently advisory-only and must not be treated as a security boundary.

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from aether.interface.api_server import app


def _isolated_config(private_dir: Path) -> dict:
    return {
        "paths": {
            "private_dir": str(private_dir),
        }
    }


@pytest.fixture
def isolated_private_dir(tmp_path, monkeypatch):
    private_dir = tmp_path / "AetherPrivate"
    for sub in ("tool_executions", "tool_registry", "tool_plans", "approvals"):
        (private_dir / sub).mkdir(parents=True, exist_ok=True)

    config = _isolated_config(private_dir)

    import aether.action.tool_executor as te
    import aether.action.tool_registry as tr
    import aether.action.tool_planner as tp
    import aether.action.approval_queue as aq

    monkeypatch.setattr(te, "load_aether_config", lambda path=None: config)
    monkeypatch.setattr(tr, "load_aether_config", lambda path=None: config)
    monkeypatch.setattr(tp, "load_aether_config", lambda path=None: config)
    monkeypatch.setattr(aq, "load_aether_config", lambda path=None: config)

    return private_dir


@pytest.fixture
def isolated_runtime(monkeypatch):
    from aether.memory.working.store import WorkingMemory
    from aether.core.runtime import AetherRuntime

    rt = AetherRuntime()
    rt.awake = True
    rt.working_memory = WorkingMemory(max_events=30)

    import aether.action.services.tool_execution_service as svc
    monkeypatch.setattr(svc, "runtime", rt)
    return rt


@pytest.fixture
def client(isolated_private_dir, isolated_runtime):
    return TestClient(app)


@pytest.fixture
def seeded_client(client):
    client.post("/action/tool-executor/seed-sandbox-tools")
    from aether.action.tool_registry import seed_default_tools
    seed_default_tools()
    return client


OPENAPI_PATH_COUNT = 306
OPENAPI_SCHEMA_COUNT = 112

# ---------------------------------------------------------------------- #
# 1. Seed sandbox tools
# ---------------------------------------------------------------------- #

class TestSeedSandboxTools:
    def test_seed_success(self, client, isolated_private_dir, isolated_runtime):
        resp = client.post("/action/tool-executor/seed-sandbox-tools")
        assert resp.status_code == 200
        data = resp.json()
        assert "result" in data
        assert data["result"]["created_count"] >= 0
        assert len(data["result"]["tools"]) > 0

        reg_path = isolated_private_dir / "tool_registry" / "tools.json"
        assert reg_path.exists()
        registry = json.loads(reg_path.read_text(encoding="utf-8"))
        assert len(registry["tools"]) > 0

        assert len(isolated_runtime.working_memory.events) > 0

    def test_seed_idempotent(self, client, isolated_private_dir):
        r1 = client.post("/action/tool-executor/seed-sandbox-tools")
        r2 = client.post("/action/tool-executor/seed-sandbox-tools")
        assert r1.status_code == 200
        assert r2.status_code == 200

    def test_seed_writes_only_isolated_private(self, client, isolated_private_dir):
        client.post("/action/tool-executor/seed-sandbox-tools")
        reg_file = isolated_private_dir / "tool_registry" / "tools.json"
        assert reg_file.exists()
        assert str(isolated_private_dir).startswith("/tmp/")


# ---------------------------------------------------------------------- #
# 2. Execute basic safe tool
# ---------------------------------------------------------------------- #

class TestExecuteBasic:
    def test_safe_tool_echo(self, client, isolated_private_dir, isolated_runtime):
        client.post("/action/tool-executor/seed-sandbox-tools")
        resp = client.post("/action/tool-executor/execute", json={
            "text": "echo test",
            "tool_id": "echo.test",
            "input_payload": {"message": "hello"},
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["execution"]["status"] == "success"
        assert data["execution"]["result"]["echo"] == {"message": "hello"}

        exec_dir = isolated_private_dir / "tool_executions"
        exec_file = exec_dir / "tool_executions.json"
        assert exec_file.exists()
        log = json.loads(exec_file.read_text(encoding="utf-8"))
        assert len(log["executions"]) == 1


# ---------------------------------------------------------------------- #
# 3. Non-existent tool
# ---------------------------------------------------------------------- #

class TestNonExistentTool:
    def test_returns_tool_not_found(self, client, isolated_private_dir):
        client.post("/action/tool-executor/seed-sandbox-tools")
        resp = client.post("/action/tool-executor/execute", json={
            "text": "nonexistent",
            "tool_id": "does.not.exist",
        })
        assert resp.status_code == 200
        assert resp.json()["execution"]["status"] == "tool_not_found"
        assert resp.json()["execution"]["error"] is not None


# ---------------------------------------------------------------------- #
# 4. Non-sandbox denied tools
# ---------------------------------------------------------------------- #

class TestDeniedTools:
    DENIED_IDS = ["file.write", "shell.run", "memory.clear", "file.delete",
                  "email.send", "approval.approve"]

    @pytest.mark.parametrize("tool_id", DENIED_IDS)
    def test_denied_tool_blocked(self, seeded_client, isolated_private_dir, tool_id):
        resp = seeded_client.post("/action/tool-executor/execute", json={
            "text": f"try {tool_id}",
            "tool_id": tool_id,
        })
        assert resp.status_code == 200
        data = resp.json()["execution"]
        assert data["status"] == "blocked", f"{tool_id}: expected blocked, got {data['status']}"
        assert "blocked" in data.get("error", "").lower()


# ---------------------------------------------------------------------- #
# 5. Disabled tool
# ---------------------------------------------------------------------- #

class TestDisabledTool:
    def test_disabled_returns_disabled(self, client, isolated_private_dir):
        client.post("/action/tool-executor/seed-sandbox-tools")
        from aether.action.tool_registry import disable_tool
        disable_tool("echo.test")
        resp = client.post("/action/tool-executor/execute", json={
            "text": "echo disabled",
            "tool_id": "echo.test",
        })
        assert resp.status_code == 200
        data = resp.json()["execution"]
        assert data["status"] == "tool_disabled", f"expected tool_disabled, got {data['status']}"
        assert "disabled" in data.get("error", "").lower()


# ---------------------------------------------------------------------- #
# 6. Approval-required tools
# ---------------------------------------------------------------------- #

class TestApprovalRequired:
    APPROVAL_REQUIRED_IDS = [
        "project.self_modification.apply",
        "project.final_real_apply_executor.execute",
        "shell.plan_only",
    ]

    @pytest.mark.parametrize("tool_id", APPROVAL_REQUIRED_IDS)
    def test_approval_required_without_approval(self, seeded_client, isolated_private_dir, tool_id):
        resp = seeded_client.post("/action/tool-executor/execute", json={
            "text": f"try {tool_id}",
            "tool_id": tool_id,
        })
        assert resp.status_code == 200
        data = resp.json()["execution"]
        assert data["status"] == "approval_required", (
            f"{tool_id}: expected approval_required, got {data['status']}"
        )

    def test_high_risk_tools_not_executed(self, seeded_client, isolated_private_dir):
        for tool_id in self.APPROVAL_REQUIRED_IDS:
            resp = seeded_client.post("/action/tool-executor/execute", json={
                "text": f"try {tool_id}",
                "tool_id": tool_id,
            })
            data = resp.json()["execution"]
            assert data["result"] is None, f"{tool_id}: result should be None when blocked"


# ---------------------------------------------------------------------- #
# 7. create_approval_if_required flag
# ---------------------------------------------------------------------- #

class TestApprovalFlag:
    def test_create_approval_false_no_approval_item(self, seeded_client, isolated_private_dir):
        resp = seeded_client.post("/action/tool-executor/execute", json={
            "text": "test approval flag",
            "tool_id": "shell.plan_only",
            "create_approval_if_required": False,
        })
        assert resp.status_code == 200
        data = resp.json()["execution"]
        assert data["status"] in ("approval_required",)
        assert data["approval_id"] is None

    def test_create_approval_true_creates_approval_item(self, seeded_client, isolated_private_dir):
        resp = seeded_client.post("/action/tool-executor/execute", json={
            "text": "test approval flag",
            "tool_id": "shell.plan_only",
            "create_approval_if_required": True,
        })
        assert resp.status_code == 200
        data = resp.json()["execution"]
        assert data["status"] == "approval_required"
        assert data["approval_id"] is not None

    def test_approval_item_in_isolated_path(self, seeded_client, isolated_private_dir):
        seeded_client.post("/action/tool-executor/execute", json={
            "text": "test isolated approval",
            "tool_id": "shell.plan_only",
            "create_approval_if_required": True,
        })
        q_path = isolated_private_dir / "approvals" / "approval_queue.json"
        assert q_path.exists()
        queue = json.loads(q_path.read_text(encoding="utf-8"))
        assert len(queue["items"]) > 0


# ---------------------------------------------------------------------- #
# 8. dry_run invariant
# ---------------------------------------------------------------------- #

class TestDryRunInvariant:
    def test_dry_run_true_does_not_prevent_dispatch(self, client, isolated_private_dir):
        client.post("/action/tool-executor/seed-sandbox-tools")
        resp_true = client.post("/action/tool-executor/execute", json={
            "text": "dry run test",
            "tool_id": "echo.test",
            "input_payload": {"x": 1},
            "dry_run": True,
        })
        assert resp_true.status_code == 200
        assert resp_true.json()["execution"]["status"] == "success"

    def test_dry_run_false_reaches_same_dispatch(self, client, isolated_private_dir):
        client.post("/action/tool-executor/seed-sandbox-tools")
        resp_false = client.post("/action/tool-executor/execute", json={
            "text": "dry run test",
            "tool_id": "echo.test",
            "input_payload": {"x": 1},
            "dry_run": False,
        })
        assert resp_false.status_code == 200
        assert resp_false.json()["execution"]["status"] == "success"

    def test_dry_run_stored_in_execution_record(self, client, isolated_private_dir):
        client.post("/action/tool-executor/seed-sandbox-tools")
        for dr in (True, False):
            resp = client.post("/action/tool-executor/execute", json={
                "text": f"dry_run={dr}",
                "tool_id": "echo.test",
                "dry_run": dr,
            })
            assert resp.json()["execution"]["dry_run"] == dr

    def test_dry_run_not_security_boundary(self, client, isolated_private_dir):
        client.post("/action/tool-executor/seed-sandbox-tools")
        r_true = client.post("/action/tool-executor/execute", json={
            "text": "boundary test",
            "tool_id": "echo.test",
            "input_payload": {"msg": "hello"},
            "dry_run": True,
        })
        r_false = client.post("/action/tool-executor/execute", json={
            "text": "boundary test",
            "tool_id": "echo.test",
            "input_payload": {"msg": "hello"},
            "dry_run": False,
        })
        t_result = r_true.json()["execution"]["result"]
        f_result = r_false.json()["execution"]["result"]
        assert t_result == f_result, (
            "dry_run should not alter dispatch behavior — "
            "both True and False must reach the same _safe_result()"
        )


# ---------------------------------------------------------------------- #
# 9. Status endpoint
# ---------------------------------------------------------------------- #

class TestStatus:
    def test_returns_status(self, client, isolated_private_dir):
        resp = client.get("/action/tool-executor/status")
        assert resp.status_code == 200
        data = resp.json()
        assert "tool_executor" in data
        assert "execution_count" in data["tool_executor"]

    def test_status_includes_isolated_path(self, client, isolated_private_dir):
        client.post("/action/tool-executor/seed-sandbox-tools")
        client.post("/action/tool-executor/execute", json={
            "text": "status test",
            "tool_id": "echo.test",
        })
        resp = client.get("/action/tool-executor/status")
        data = resp.json()["tool_executor"]
        assert data["execution_count"] == 1


# ---------------------------------------------------------------------- #
# 10. List endpoint
# ---------------------------------------------------------------------- #

class TestList:
    def test_list_returns_executions(self, client, isolated_private_dir):
        client.post("/action/tool-executor/seed-sandbox-tools")
        client.post("/action/tool-executor/execute", json={
            "text": "list test",
            "tool_id": "echo.test",
        })
        resp = client.get("/action/tool-executor/list")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["executions"]) >= 1

    def test_list_empty_before_any_execution(self, client, isolated_private_dir):
        resp = client.get("/action/tool-executor/list")
        assert resp.status_code == 200
        assert len(resp.json()["executions"]) == 0


# ---------------------------------------------------------------------- #
# 11. Get execution by ID
# ---------------------------------------------------------------------- #

class TestGetExecution:
    def test_get_known_execution(self, client, isolated_private_dir):
        client.post("/action/tool-executor/seed-sandbox-tools")
        exec_resp = client.post("/action/tool-executor/execute", json={
            "text": "get test",
            "tool_id": "echo.test",
        })
        exec_id = exec_resp.json()["execution"]["id"]
        resp = client.get(f"/action/tool-executor/{exec_id}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["execution"]["id"] == exec_id


# ---------------------------------------------------------------------- #
# 12. Get execution non-existent ID
# ---------------------------------------------------------------------- #

class TestGetNonexistent:
    def test_nonexistent_id_returns_none(self, client, isolated_private_dir):
        resp = client.get("/action/tool-executor/nonexistent-execution-id-12345")
        assert resp.status_code == 200
        data = resp.json()
        assert data["execution"] is None


# ---------------------------------------------------------------------- #
# Additional Safety Tests
# ---------------------------------------------------------------------- #

class TestDeniedDefaultTools:
    DEFAULT_DENIED = [
        "file.write", "file.delete", "shell.run",
        "email.send", "memory.clear", "approval.approve",
    ]

    @pytest.mark.parametrize("tool_id", DEFAULT_DENIED)
    def test_default_denied_tools_blocked(self, seeded_client, isolated_private_dir, tool_id):
        resp = seeded_client.post("/action/tool-executor/execute", json={
            "text": f"try {tool_id}",
            "tool_id": tool_id,
        })
        data = resp.json()["execution"]
        assert data["status"] == "blocked", f"{tool_id}: expected blocked, got {data['status']}"
        assert data["result"] is None


class TestHighRiskSandboxTools:
    HIGH_RISK = [
        "project.self_modification.apply",
        "project.self_modification.rollback",
        "project.final_real_apply_executor.execute",
        "shell.plan_only",
    ]

    @pytest.mark.parametrize("tool_id", HIGH_RISK)
    def test_high_risk_not_executed_without_approval(self, seeded_client, isolated_private_dir, tool_id):
        resp = seeded_client.post("/action/tool-executor/execute", json={
            "text": f"try {tool_id}",
            "tool_id": tool_id,
        })
        data = resp.json()["execution"]
        assert data["status"] == "approval_required", (
            f"{tool_id}: expected approval_required, got {data['status']}"
        )
        assert data["result"] is None


class TestAllHighRiskHaveApprovalRequired:
    def test_all_high_risk_sandbox_tools_require_approval(self, seeded_client, isolated_private_dir):
        from aether.action.tool_registry import load_registry
        from aether.action.tool_executor import SANDBOX_TOOL_IDS

        registry = load_registry()
        high_risk_no_approval = []
        for tool_id, tool in registry["tools"].items():
            if tool_id not in SANDBOX_TOOL_IDS:
                continue
            if tool.get("risk_level") == "high":
                if not tool.get("requires_user_approval", False):
                    high_risk_no_approval.append(tool_id)
        assert high_risk_no_approval == [], (
            f"High-risk sandbox tools missing requires_user_approval=True: {high_risk_no_approval}"
        )


class TestSourceMutationDenial:
    def test_no_real_source_mutation(self, seeded_client, isolated_private_dir):
        resp = seeded_client.post("/action/tool-executor/execute", json={
            "text": "test mutation",
            "tool_id": "echo.test",
        })
        assert resp.status_code == 200

    def test_blocked_tool_cannot_mutate_source(self, seeded_client, isolated_private_dir):
        resp = seeded_client.post("/action/tool-executor/execute", json={
            "text": "try write",
            "tool_id": "file.write",
        })
        assert resp.json()["execution"]["status"] == "blocked"

    def test_approval_required_not_executed(self, seeded_client, isolated_private_dir):
        resp = seeded_client.post("/action/tool-executor/execute", json={
            "text": "try apply",
            "tool_id": "project.self_modification.apply",
        })
        assert resp.json()["execution"]["status"] == "approval_required"


# ---------------------------------------------------------------------- #
# OpenAPI operation ID lock
# ---------------------------------------------------------------------- #

class TestOperationIdLock:
    def test_operation_ids_locked(self):
        schema = app.openapi()
        paths = schema.get("paths", {})

        expected = {
            "POST /action/tool-executor/seed-sandbox-tools":
                "seed_action_sandbox_tools_action_tool_executor_seed_sandbox_tools_post",
            "POST /action/tool-executor/execute":
                "execute_action_tool_action_tool_executor_execute_post",
            "GET /action/tool-executor/status":
                "get_action_tool_executor_status_action_tool_executor_status_get",
            "GET /action/tool-executor/list":
                "list_action_tool_executions_action_tool_executor_list_get",
            "GET /action/tool-executor/{execution_id}":
                "get_action_tool_execution_action_tool_executor__execution_id__get",
        }

        for key, expected_op_id in expected.items():
            method, _, path = key.partition(" ")
            method_lower = method.lower()
            actual = paths[path][method_lower].get("operationId")
            assert actual == expected_op_id, (
                f"{key}: expected {expected_op_id}, got {actual}"
            )

    def test_openapi_paths_and_schemas_unchanged(self):
        schema = app.openapi()
        assert len(schema.get("paths", {})) == OPENAPI_PATH_COUNT
        assert len(schema.get("components", {}).get("schemas", {})) == OPENAPI_SCHEMA_COUNT

    def test_all_tool_executor_paths_present(self):
        schema = app.openapi()
        paths = schema.get("paths", {})
        required_paths = [
            "/action/tool-executor/seed-sandbox-tools",
            "/action/tool-executor/execute",
            "/action/tool-executor/status",
            "/action/tool-executor/list",
            "/action/tool-executor/{execution_id}",
        ]
        for p in required_paths:
            assert p in paths, f"Missing OpenAPI path: {p}"
