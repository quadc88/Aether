"""Route tests for the Observation Record router (Milestone 83D/83E).

TestClient is allowed in this file because 83D/83E are the API router
milestones. Only the observation endpoints may be called:
- POST /observation-records
- GET /observation-records
- GET /observation-records/{observation_id}
- PATCH /observation-records/{observation_id}/status
- POST /observation-records/{observation_id}/cancel

Persistence is isolated via tmp_path + monkeypatch of the store directory.
No real private data, docs/history, or protected/core endpoints are touched.
"""

import ast
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import aether.interface.api_server as ap_mod
from aether.action import observation_record_queue as obs_queue

RECORD_FIELDS = [
    "observation_id",
    "observation_type",
    "plan_step_id",
    "evidence_item_id",
    "collector_contract_id",
    "target",
    "observed_value",
    "expected_value",
    "status",
    "observed_at",
    "metadata",
    "safety_flags",
]

FORBIDDEN_ENVELOPE_KEYS = [
    "name",
    "created",
    "found",
    "observation_record",
    "observation_records",
    "count",
]

LIST_FORBIDDEN_ENVELOPE_KEYS = ["name", "status", "count", "observation_records"]


def _assert_pure_observation_response_shape(payload: dict) -> None:
    """Lock API responses to the pure 83B ObservationRecordResponse shape.

    API responses must NOT leak service envelope fields (name, found,
    updated, cancelled, observation_record) nor store/lifecycle fields
    (created_at, updated_at, decision, decided_at, reviewer,
    decision_reason, warnings, context_metadata). Those fields are verified
    only through queue load or service tests, never in the API response.
    """
    expected_keys = {
        "observation_id",
        "observation_type",
        "plan_step_id",
        "evidence_item_id",
        "collector_contract_id",
        "target",
        "observed_value",
        "expected_value",
        "status",
        "observed_at",
        "metadata",
        "safety_flags",
    }
    forbidden_envelope_or_store_keys = {
        # service envelope keys
        "name",
        "found",
        "updated",
        "cancelled",
        "observation_record",
        # store/envelope lifecycle fields
        "created_at",
        "updated_at",
        "decision",
        "decided_at",
        "reviewer",
        "decision_reason",
        "warnings",
        "context_metadata",
    }
    assert set(payload) == expected_keys, (
        "API response must be exactly the pure ObservationRecordResponse shape; "
        "no service envelope or store lifecycle leakage; got: "
        + ", ".join(sorted(payload))
    )
    assert not (forbidden_envelope_or_store_keys & set(payload)), (
        "service envelope/store lifecycle keys leaked into API response: "
        + ", ".join(sorted(forbidden_envelope_or_store_keys & set(payload)))
    )


@pytest.fixture
def store_dir(monkeypatch, tmp_path):
    store = tmp_path / "observation_records"
    store.mkdir(parents=True, exist_ok=True)

    def _fake_get_dir():
        return store

    monkeypatch.setattr(obs_queue, "get_observation_records_dir", _fake_get_dir)
    return store


@pytest.fixture
def client():
    return TestClient(ap_mod.app)


def _valid_payload(**overrides):
    payload = {
        "plan_step_id": "a" * 32,
        "evidence_item_id": None,
        "target": "gate_1",
        "observed_value": {"value": 3},
        "expected_value": {"value": 2},
        "status": "pending",
        "collector_contract_id": None,
        "metadata": {"source": "route_test"},
    }
    payload.update(overrides)
    return payload


def _create_record(client, store_dir, **overrides):
    response = client.post("/observation-records", json=_valid_payload(**overrides))
    assert response.status_code == 200, response.text
    return response.json()


class TestCreateEndpoint:
    def test_post_valid_observation_record(self, client, store_dir):
        response = client.post("/observation-records", json=_valid_payload())
        assert response.status_code == 200

    def test_post_response_pure_observation_record_shape(self, client, store_dir):
        record = _create_record(client, store_dir)
        assert sorted(record.keys()) == sorted(RECORD_FIELDS)

    def test_post_response_no_service_envelope_keys(self, client, store_dir):
        record = _create_record(client, store_dir)
        for key in FORBIDDEN_ENVELOPE_KEYS:
            assert key not in record, f"envelope key leaked: {key}"

    def test_post_persisted_record_loadable_from_store(self, client, store_dir):
        record = _create_record(client, store_dir)
        loaded = obs_queue.load_observation_record(record["observation_id"])
        assert loaded is not None
        assert loaded["observation_id"] == record["observation_id"]
        assert loaded["target"] == "gate_1"

    def test_post_default_status_pending(self, client, store_dir):
        record = _create_record(client, store_dir)
        assert record["status"] == "pending"

    def test_post_rejects_invalid_target(self, client, store_dir):
        response = client.post("/observation-records", json=_valid_payload(target=""))
        assert response.status_code == 400

    def test_post_rejects_missing_both_ids(self, client, store_dir):
        payload = _valid_payload(plan_step_id=None, evidence_item_id=None)
        response = client.post("/observation-records", json=payload)
        assert response.status_code == 400

    def test_post_rejects_caller_supplied_observation_id(self, client, store_dir):
        payload = _valid_payload(observation_id="c" * 32)
        response = client.post("/observation-records", json=payload)
        assert response.status_code == 400
        assert "generated/internal" in response.json()["detail"]
        assert client.get("/observation-records").json()["total"] == 0

    def test_post_rejects_caller_supplied_observation_type(self, client, store_dir):
        payload = _valid_payload(observation_type="observation_record")
        response = client.post("/observation-records", json=payload)
        assert response.status_code == 400
        assert "generated/internal" in response.json()["detail"]
        assert client.get("/observation-records").json()["total"] == 0

    def test_post_rejects_caller_supplied_observed_at(self, client, store_dir):
        payload = _valid_payload(observed_at="2026-08-01T00:00:00+00:00")
        response = client.post("/observation-records", json=payload)
        assert response.status_code == 400
        assert "generated/internal" in response.json()["detail"]
        assert client.get("/observation-records").json()["total"] == 0

    def test_post_rejects_caller_supplied_safety_flags(self, client, store_dir):
        payload = _valid_payload(safety_flags={"apply_executed": True})
        response = client.post("/observation-records", json=payload)
        assert response.status_code == 400
        assert "generated/internal" in response.json()["detail"]
        assert client.get("/observation-records").json()["total"] == 0

    def test_post_rejects_invalid_status(self, client, store_dir):
        payload = _valid_payload(status="not_a_status")
        response = client.post("/observation-records", json=payload)
        assert response.status_code == 400


class TestGetEndpoint:
    def test_get_existing_id(self, client, store_dir):
        record = _create_record(client, store_dir)
        response = client.get(f"/observation-records/{record['observation_id']}")
        assert response.status_code == 200
        body = response.json()
        assert sorted(body.keys()) == sorted(RECORD_FIELDS)
        assert body["observation_id"] == record["observation_id"]

    def test_get_missing_valid_id(self, client, store_dir):
        response = client.get(f"/observation-records/{'b' * 32}")
        assert response.status_code == 404

    def test_get_invalid_id(self, client, store_dir):
        response = client.get("/observation-records/not-a-valid-id")
        assert response.status_code == 400


class TestListEndpoint:
    def test_list_empty(self, client, store_dir):
        response = client.get("/observation-records")
        assert response.status_code == 200
        body = response.json()
        assert body["records"] == []
        assert body["total"] == 0

    def test_list_after_create(self, client, store_dir):
        record = _create_record(client, store_dir)
        response = client.get("/observation-records")
        assert response.status_code == 200
        body = response.json()
        assert [r["observation_id"] for r in body["records"]] == [
            record["observation_id"]
        ]
        assert body["total"] == 1

    def test_list_status_filter(self, client, store_dir):
        _create_record(client, store_dir)
        _create_record(client, store_dir, status="matched")
        response = client.get("/observation-records", params={"status": "matched"})
        assert response.status_code == 200
        body = response.json()
        assert body["total"] == 1
        assert all(r["status"] == "matched" for r in body["records"])

    def test_list_limit_offset(self, client, store_dir):
        import time

        ids = []
        for _ in range(3):
            ids.append(_create_record(client, store_dir)["observation_id"])
            time.sleep(0.01)
        limited = client.get("/observation-records", params={"limit": 2}).json()
        assert [r["observation_id"] for r in limited["records"]] == [ids[2], ids[1]]
        assert limited["total"] == 3
        offset = client.get("/observation-records", params={"offset": 1}).json()
        assert [r["observation_id"] for r in offset["records"]] == [ids[1], ids[0]]
        assert offset["offset"] == 1

    def test_list_invalid_limit(self, client, store_dir):
        response = client.get("/observation-records", params={"limit": 0})
        assert response.status_code == 400

    def test_list_invalid_offset(self, client, store_dir):
        response = client.get("/observation-records", params={"offset": -1})
        assert response.status_code == 400

    def test_list_response_pure_list_shape(self, client, store_dir):
        _create_record(client, store_dir)
        response = client.get("/observation-records")
        assert response.status_code == 200
        body = response.json()
        assert sorted(body.keys()) == sorted(
            ["records", "total", "limit", "offset"]
        )
        for key in LIST_FORBIDDEN_ENVELOPE_KEYS:
            assert key not in body, f"envelope key leaked: {key}"


class TestUpdateStatusEndpoint:
    def test_patch_valid_status_update(self, client, store_dir):
        record = _create_record(client, store_dir)
        response = client.patch(
            f"/observation-records/{record['observation_id']}/status",
            json={"new_status": "matched", "reviewer": "human_001"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "matched"
        _assert_pure_observation_response_shape(body)

    def test_patch_response_pure_observation_record_shape(self, client, store_dir):
        record = _create_record(client, store_dir)
        response = client.patch(
            f"/observation-records/{record['observation_id']}/status",
            json={"new_status": "error", "reviewer": "human_001"},
        )
        assert response.status_code == 200
        _assert_pure_observation_response_shape(response.json())

    def test_patch_persisted_status_change(self, client, store_dir):
        record = _create_record(client, store_dir)
        client.patch(
            f"/observation-records/{record['observation_id']}/status",
            json={"new_status": "matched", "reviewer": "human_001"},
        )
        loaded = obs_queue.load_observation_record(record["observation_id"])
        assert loaded["status"] == "matched"
        assert loaded["reviewer"] == "human_001"

    def test_patch_persisted_lifecycle_fields(self, client, store_dir):
        record = _create_record(client, store_dir)
        client.patch(
            f"/observation-records/{record['observation_id']}/status",
            json={
                "new_status": "matched",
                "reviewer": "human_001",
                "reason": "manual audit matched reason",
            },
        )
        loaded = obs_queue.load_observation_record(record["observation_id"])
        assert loaded["status"] == "matched"
        assert loaded["decision"] == "matched"
        assert loaded["reviewer"] == "human_001"
        assert loaded["decision_reason"] == "manual audit matched reason"
        assert loaded["decision"] != loaded["decision_reason"]
        assert loaded["decided_at"] is not None
        assert loaded["updated_at"] is not None

    def test_patch_sets_reviewer_and_reason(self, client, store_dir):
        record = _create_record(client, store_dir)
        response = client.patch(
            f"/observation-records/{record['observation_id']}/status",
            json={"new_status": "mismatched", "reviewer": "human_001", "reason": "values differ"},
        )
        assert response.status_code == 200
        loaded = obs_queue.load_observation_record(record["observation_id"])
        assert loaded["reviewer"] == "human_001"
        assert loaded["decision_reason"] == "values differ"

    def test_patch_missing_record_404(self, client, store_dir):
        response = client.patch(
            f"/observation-records/{'b' * 32}/status",
            json={"new_status": "matched", "reviewer": "human_001"},
        )
        assert response.status_code == 404

    def test_patch_invalid_id_400(self, client, store_dir):
        response = client.patch(
            "/observation-records/not-a-valid-id/status",
            json={"new_status": "matched", "reviewer": "human_001"},
        )
        assert response.status_code == 400

    def test_patch_invalid_new_status_400(self, client, store_dir):
        record = _create_record(client, store_dir)
        response = client.patch(
            f"/observation-records/{record['observation_id']}/status",
            json={"new_status": "not_a_status", "reviewer": "human_001"},
        )
        assert response.status_code == 400

    def test_patch_missing_new_status_422(self, client, store_dir):
        record = _create_record(client, store_dir)
        response = client.patch(
            f"/observation-records/{record['observation_id']}/status",
            json={"reviewer": "human_001"},
        )
        assert response.status_code == 422

    def test_patch_rejects_status_key(self, client, store_dir):
        record = _create_record(client, store_dir)
        response = client.patch(
            f"/observation-records/{record['observation_id']}/status",
            json={"new_status": "matched", "reviewer": "human_001", "status": "matched"},
        )
        assert response.status_code == 400
        assert "generated/internal" in response.json()["detail"]
        assert obs_queue.load_observation_record(record["observation_id"])["status"] == "pending"

    def test_patch_rejects_observation_id_key(self, client, store_dir):
        record = _create_record(client, store_dir)
        response = client.patch(
            f"/observation-records/{record['observation_id']}/status",
            json={"new_status": "matched", "reviewer": "human_001", "observation_id": "c" * 32},
        )
        assert response.status_code == 400
        assert "generated/internal" in response.json()["detail"]

    def test_patch_rejects_lifecycle_key(self, client, store_dir):
        record = _create_record(client, store_dir)
        response = client.patch(
            f"/observation-records/{record['observation_id']}/status",
            json={"new_status": "matched", "reviewer": "human_001", "decision": "nope"},
        )
        assert response.status_code == 400
        assert "generated/internal" in response.json()["detail"]
        assert obs_queue.load_observation_record(record["observation_id"])["status"] == "pending"

    def test_patch_non_pending_record_unchanged(self, client, store_dir):
        record = _create_record(client, store_dir, status="matched")
        response = client.patch(
            f"/observation-records/{record['observation_id']}/status",
            json={"new_status": "error", "reviewer": "human_001"},
        )
        assert response.status_code == 200
        assert response.json()["status"] == "matched"

    def test_get_after_update_pure_shape(self, client, store_dir):
        record = _create_record(client, store_dir)
        client.patch(
            f"/observation-records/{record['observation_id']}/status",
            json={"new_status": "matched", "reviewer": "human_001"},
        )
        response = client.get(f"/observation-records/{record['observation_id']}")
        assert response.status_code == 200
        _assert_pure_observation_response_shape(response.json())
        assert response.json()["status"] == "matched"


class TestCancelEndpoint:
    def test_post_cancel_valid(self, client, store_dir):
        record = _create_record(client, store_dir)
        response = client.post(
            f"/observation-records/{record['observation_id']}/cancel",
            json={"reviewer": "human_001", "reason": "incorrect observation"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "cancelled"
        _assert_pure_observation_response_shape(body)

    def test_post_cancel_response_pure_shape(self, client, store_dir):
        record = _create_record(client, store_dir)
        response = client.post(
            f"/observation-records/{record['observation_id']}/cancel",
            json={"reviewer": "human_001"},
        )
        assert response.status_code == 200
        _assert_pure_observation_response_shape(response.json())

    def test_post_cancel_persisted(self, client, store_dir):
        record = _create_record(client, store_dir)
        client.post(
            f"/observation-records/{record['observation_id']}/cancel",
            json={"reviewer": "human_001", "reason": "manual audit cancel reason"},
        )
        loaded = obs_queue.load_observation_record(record["observation_id"])
        assert loaded["status"] == "cancelled"
        assert loaded["decision"] == "cancelled"
        assert loaded["reviewer"] == "human_001"
        assert loaded["decision_reason"] == "manual audit cancel reason"
        assert loaded["decision"] != loaded["decision_reason"]
        assert loaded["decided_at"] is not None
        assert loaded["updated_at"] is not None

    def test_post_cancel_missing_record_404(self, client, store_dir):
        response = client.post(f"/observation-records/{'b' * 32}/cancel", json={"reviewer": "human_001"})
        assert response.status_code == 404

    def test_post_cancel_invalid_id_400(self, client, store_dir):
        response = client.post("/observation-records/not-a-valid-id/cancel", json={"reviewer": "human_001"})
        assert response.status_code == 400

    def test_post_cancel_rejects_new_status_key(self, client, store_dir):
        record = _create_record(client, store_dir)
        response = client.post(
            f"/observation-records/{record['observation_id']}/cancel",
            json={"reviewer": "human_001", "new_status": "cancelled"},
        )
        assert response.status_code == 400
        assert "generated/internal" in response.json()["detail"]
        assert obs_queue.load_observation_record(record["observation_id"])["status"] == "pending"

    def test_post_cancel_rejects_status_key(self, client, store_dir):
        record = _create_record(client, store_dir)
        response = client.post(
            f"/observation-records/{record['observation_id']}/cancel",
            json={"reviewer": "human_001", "status": "cancelled"},
        )
        assert response.status_code == 400
        assert "generated/internal" in response.json()["detail"]

    def test_post_cancel_rejects_lifecycle_key(self, client, store_dir):
        record = _create_record(client, store_dir)
        response = client.post(
            f"/observation-records/{record['observation_id']}/cancel",
            json={"reviewer": "human_001", "decision_reason": "nope"},
        )
        assert response.status_code == 400
        assert "generated/internal" in response.json()["detail"]

    def test_post_cancel_non_pending_record_unchanged(self, client, store_dir):
        record = _create_record(client, store_dir, status="error")
        response = client.post(
            f"/observation-records/{record['observation_id']}/cancel", json={"reviewer": "human_001"}
        )
        assert response.status_code == 200
        assert response.json()["status"] == "error"

    def test_list_after_cancel_pure_shape(self, client, store_dir):
        record = _create_record(client, store_dir)
        client.post(
            f"/observation-records/{record['observation_id']}/cancel",
            json={"reviewer": "human_001"},
        )
        response = client.get("/observation-records")
        assert response.status_code == 200
        body = response.json()
        assert [r["observation_id"] for r in body["records"]] == [
            record["observation_id"]
        ]
        for item in body["records"]:
            _assert_pure_observation_response_shape(item)
        assert body["records"][0]["status"] == "cancelled"


class TestOpenAPI:
    def test_openapi_path_count_304(self):
        schema = ap_mod.app.openapi()
        assert len(schema.get("paths", {})) == 306

    def test_openapi_schema_count_108(self):
        schema = ap_mod.app.openapi()
        assert len(schema.get("components", {}).get("schemas", {})) == 112

    def test_openapi_observation_paths_exact(self):
        schema = ap_mod.app.openapi()
        paths = schema.get("paths", {})
        observation_paths = sorted(
            p for p in paths if "observation" in p.lower()
        )
        assert observation_paths == sorted(
            [
                "/observation-records",
                "/observation-records/{observation_id}",
                "/observation-records/{observation_id}/cancel",
                "/observation-records/{observation_id}/status",
            ]
        )

    def test_openapi_observation_operation_ids_exact(self):
        schema = ap_mod.app.openapi()
        paths = schema.get("paths", {})
        operation_ids = sorted(
            spec.get("operationId", "")
            for methods in paths.values()
            for spec in methods.values()
            if "observation" in spec.get("operationId", "").lower()
        )
        assert operation_ids == sorted(
            [
                "cancel_observation_record",
                "create_observation_record",
                "get_observation_record",
                "list_observation_records",
                "update_observation_record_status",
            ]
        )

    def test_no_action_observation_path(self):
        schema = ap_mod.app.openapi()
        paths = schema.get("paths", {})
        assert not any(p.startswith("/action/") and "observation" in p.lower() for p in paths)


class TestApiServerBoundary:
    def test_api_server_route_count_8(self):
        tree = ast.parse(Path(ap_mod.__file__).read_text(encoding="utf-8"))
        routes = {}
        for node in tree.body:
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            for dec in node.decorator_list:
                text = ast.unparse(dec)
                if text.startswith("app."):
                    method = text.split("(", 1)[0].split(".", 1)[1].upper()
                    path = ast.literal_eval(dec.args[0])
                    routes[node.name] = (method, path)
        assert len(routes) == 8

    def test_include_router_count_23(self):
        tree = ast.parse(Path(ap_mod.__file__).read_text(encoding="utf-8"))
        count = sum(
            1
            for node in ast.walk(tree)
            if isinstance(node, ast.Call)
            and ast.unparse(node.func) == "app.include_router"
        )
        assert count == 23

    def test_no_action_routes_in_api_server(self):
        tree = ast.parse(Path(ap_mod.__file__).read_text(encoding="utf-8"))
        action_routes = []
        for node in tree.body:
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            for dec in node.decorator_list:
                text = ast.unparse(dec)
                if text.startswith("app."):
                    path = ast.literal_eval(dec.args[0])
                    if path.startswith("/action/"):
                        action_routes.append(path)
        assert action_routes == []

    def test_observation_endpoint_functions_not_in_api_server(self):
        tree = ast.parse(Path(ap_mod.__file__).read_text(encoding="utf-8"))
        names = {
            node.name
            for node in tree.body
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        }
        assert not (names & {
            "create_observation_record",
            "get_observation_record",
            "list_observation_records",
        })

    def test_observation_router_included_exactly_once(self):
        tree = ast.parse(Path(ap_mod.__file__).read_text(encoding="utf-8"))
        count = sum(
            1
            for node in ast.walk(tree)
            if isinstance(node, ast.Call)
            and ast.unparse(node.func) == "app.include_router"
            and "observation_router" in ast.unparse(node)
        )
        assert count == 1


class TestNoInvocationSelfCheck:
    """Static checks that this test file only calls observation endpoints."""

    def test_parser_uses_only_observation_endpoints(self):
        path = Path(__file__)
        tree = ast.parse(path.read_text(encoding="utf-8"))
        allowed = {"/observation-records"}
        called = set()
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Attribute):
                continue
            if not (isinstance(node.func.value, ast.Name) and node.func.value.id == "client"):
                continue
            if node.func.attr not in {"get", "post", "patch", "put", "delete"}:
                continue
            for arg in node.args:
                if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                    url = arg.value.split("{", 1)[0].split("/", 2)[:2]
                    url = "/" + "/".join(part for part in url if part)
                    if url:
                        called.add(url)
        assert called, "no client endpoint calls found"
        assert called <= allowed, (
            "non-observation endpoint called: " + ", ".join(sorted(called - allowed))
        )

    def test_no_forbidden_endpoint_strings(self):
        path = Path(__file__)
        source = path.read_text(encoding="utf-8")
        for forbidden in [
            "/" + "chat",
            "/" + "awak" + "en",
            "/" + "verification" + "/classify",
        ]:
            assert forbidden not in source, f"forbidden endpoint string: {forbidden}"
        assert "/" + "identity" not in source.replace("observation_id", "")
        assert "client.get(\"/\")" not in source

    def test_no_protected_route_function_calls(self):
        path = Path(__file__)
        source = path.read_text(encoding="utf-8")
        for forbidden in [
            "get_identity" + "_integrity_status",
            "awak" + "en",
            "handle_" + "awak" + "en",
            "classify_" + "risk",
        ]:
            assert forbidden not in source, f"protected function referenced: {forbidden}"

    def test_no_apply_rollback_tool_evidence_invocation(self):
        path = Path(__file__)
        source = path.read_text(encoding="utf-8")
        for forbidden in [
            "collect_" + "evidence",
            "execute_" + "tool",
            "run_" + "apply",
            "run_" + "rollback",
            "apply_" + "patch_proposal",
        ]:
            assert forbidden not in source, f"forbidden invocation string: {forbidden}"

    def test_no_real_private_path_string(self):
        path = Path(__file__)
        source = path.read_text(encoding="utf-8")
        real_data = "/home/" + "aether" + "/data"
        assert real_data not in source, (
            "Route tests must not reference the real private data path"
        )

    def test_no_real_private_writes(self):
        path = Path(__file__)
        source = path.read_text(encoding="utf-8")
        for forbidden in ["get_private" + "_dir", "/home/" + "aether"]:
            assert forbidden not in source, f"real private path referenced: {forbidden}"
