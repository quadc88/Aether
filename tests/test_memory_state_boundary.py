"""Isolated state and contract coverage for Aether's 21 memory endpoints."""

from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from aether.action.services import memory_service
from aether.interface.api_server import app
from aether.memory.episodic import writer as episodic_writer
from aether.memory.graph import store as graph_store
from aether.memory.semantic import indexer as semantic_indexer
from aether.memory.timeline import recorder as timeline_recorder
from aether.memory.working.store import WorkingMemory


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REAL_MEMORY_ROOTS = (
    Path("/home/aether/data/vault"),
    Path("/home/aether/data/vector_db"),
    Path("/home/aether/data/timeline"),
    Path("/home/aether/data/graph_db"),
)
REPO_FALLBACK_ROOTS = tuple(
    PROJECT_ROOT / name for name in ("vault", "vector_db", "timeline", "graph_db")
)
WATCHED_NON_TEST_ROOTS = REAL_MEMORY_ROOTS + REPO_FALLBACK_ROOTS

EXPECTED_MEMORY_OPERATION_IDS = {
    "GET /memory/episodic/latest": "get_latest_episodic_memory_memory_episodic_latest_get",
    "GET /memory/episodic/list": "list_episodic_memory_memory_episodic_list_get",
    "GET /memory/graph/edges": "get_graph_edges_memory_graph_edges_get",
    "GET /memory/graph/nodes": "get_graph_nodes_memory_graph_nodes_get",
    "GET /memory/graph/status": "get_graph_memory_status_memory_graph_status_get",
    "GET /memory/semantic/status": "get_semantic_memory_status_memory_semantic_status_get",
    "GET /memory/timeline/latest": "get_latest_timeline_event_memory_timeline_latest_get",
    "GET /memory/timeline/list": "list_timeline_events_memory_timeline_list_get",
    "GET /memory/timeline/status": "get_timeline_status_memory_timeline_status_get",
    "GET /memory/working": "get_working_memory_memory_working_get",
    "POST /memory/episodic/write": "write_episodic_memory_memory_episodic_write_post",
    "POST /memory/graph/edge": "create_graph_edge_memory_graph_edge_post",
    "POST /memory/graph/node": "create_graph_node_memory_graph_node_post",
    "POST /memory/graph/search": "search_graph_memory_memory_graph_search_post",
    "POST /memory/graph/seed": "seed_graph_memory_memory_graph_seed_post",
    "POST /memory/semantic/index": "index_semantic_memory_memory_semantic_index_post",
    "POST /memory/semantic/search": "search_memory_memory_semantic_search_post",
    "POST /memory/timeline/search": "search_timeline_memory_memory_timeline_search_post",
    "POST /memory/working/clear": "clear_working_memory_memory_working_clear_post",
    "POST /memory/working/goal": "set_working_goal_memory_working_goal_post",
    "POST /memory/working/milestone": "set_working_milestone_memory_working_milestone_post",
}

PROTECTED_FUNCTION_AST_HASHES = {
    "get_identity_integrity_status": "1c2d9f007fd4f6c2c540c78eb855ef764bec8ad3172fb7793831cb5e4e8e7d39",
    "post_initialize_identity_guard": "0a92465d1c989ab215c23a5b2ebd9a0073ece070fb20b5936d1a292a3c1660cb",
    "post_verify_identity_integrity": "a4322c76ec0e9ddb0d4a718f81395bac1794b1a67979728c2c2e72bcfbf48216",
    "root": "81dcfdbd910a059038434512c6d0ac5bed7fd76eddfa2e7e3b511e151172ccd9",
    "identity": "f62af538cda4903a1344faf2d81807c3752ad30ccd2b580dba5046a2a179eda6",
    "awaken": "63e5fc8835c9de844605461e424cd0b0a1322085f6009e79dd6af35b3e1f44a1",
    "chat": "e081ef96b52d98d803c86c5b3f48b19f6e6807f74a76e59a0af6faa5f6d00655",
    "classify_verification_risk": "ab41471ff78628c01e906ba92820ff14d7ea0f4d822f4b0760e628ac22548a2d",
}

TOOL_EXECUTOR_ROUTER_FUNCTION_AST_HASHES = {
    "execute_action_tool": "f30a174f29b4bc62285fead2cba4cb13e3413ca10603bcca3a5d30cfa6b2602c",
    "get_action_tool_execution": "c030d7634357a70562309cf74454313ac8b950015ed95b7249cf785db994efd7",
    "get_action_tool_executor_status": "bf5bc8544b74592a05f65fd64969eac8e701c08cdca246c881785afcf5d18534",
    "list_action_tool_executions": "1f8bf57b6a95d80bd796115cc3dee2128550e3bcc30d520f65c1d1576de78e9d",
    "seed_action_sandbox_tools": "785059afffefadf54cb1d7854fb00fe4ede4523266fe0aac4f182bee21439207",
}


def _fingerprint(root: Path) -> list[dict]:
    result: list[dict] = []
    if not root.exists():
        return result
    for path in sorted(root.rglob("*")):
        try:
            relative_path = str(path.relative_to(root))
            if path.is_file():
                result.append(
                    {
                        "type": "file",
                        "path": relative_path,
                        "size": path.stat().st_size,
                        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                    }
                )
            elif path.is_dir():
                result.append({"type": "dir", "path": relative_path})
        except FileNotFoundError:
            continue
    return result


def _watched_fingerprints() -> dict[str, list[dict]]:
    return {str(root): _fingerprint(root) for root in WATCHED_NON_TEST_ROOTS}


@pytest.fixture(autouse=True)
def real_and_fallback_memory_stores_unchanged():
    """Prove each test leaves real and repo-fallback memory stores untouched."""

    before = _watched_fingerprints()
    yield
    assert _watched_fingerprints() == before


@pytest.fixture
def isolated_memory_roots(tmp_path: Path) -> dict[str, str]:
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
    }
    for path in roots.values():
        path.mkdir(parents=True, exist_ok=True)
        assert path.resolve().is_relative_to(tmp_path.resolve())
        assert not path.resolve().is_relative_to(Path("/home/aether/data"))
    return {name: str(path) for name, path in roots.items()}


@pytest.fixture
def isolated_memory_env(monkeypatch: pytest.MonkeyPatch, isolated_memory_roots: dict[str, str]):
    config = {"paths": dict(isolated_memory_roots)}
    for module in (episodic_writer, semantic_indexer, timeline_recorder, graph_store):
        monkeypatch.setattr(module, "load_aether_config", lambda config=config: config)

    isolated_runtime = SimpleNamespace(
        working_memory=WorkingMemory(max_events=100),
        status=lambda: "awake",
    )
    monkeypatch.setattr(memory_service, "runtime", isolated_runtime)

    roots = {name: Path(path) for name, path in isolated_memory_roots.items()}
    client = TestClient(app)
    yield SimpleNamespace(client=client, roots=roots, runtime=isolated_runtime)


def _event_types(env) -> list[str]:
    return [event["type"] for event in env.runtime.working_memory.summary()["recent_events"]]


def _json_files(path: Path) -> list[Path]:
    return sorted(path.glob("*.json"))


def test_working_memory_endpoints_use_only_isolated_in_process_state(isolated_memory_env):
    env = isolated_memory_env

    initial = env.client.get("/memory/working")
    assert initial.status_code == 200
    assert initial.json()["working_memory"]["event_count"] == 0

    goal = env.client.post("/memory/working/goal", json={"goal": "Isolated memory goal"})
    assert goal.status_code == 200
    assert goal.json()["message"] == "Working Memory goal updated."
    assert goal.json()["working_memory"]["current_goal"] == "Isolated memory goal"

    milestone = env.client.post(
        "/memory/working/milestone", json={"milestone": "Boundary fixture milestone"}
    )
    assert milestone.status_code == 200
    assert milestone.json()["working_memory"]["current_milestone"] == "Boundary fixture milestone"
    assert _event_types(env) == ["goal_update", "milestone_update"]

    env.runtime.working_memory.add_note("temporary isolated session note")
    cleared = env.client.post("/memory/working/clear")
    assert cleared.status_code == 200
    assert cleared.json()["message"] == "Working Memory cleared."
    assert cleared.json()["working_memory"] == {
        "current_goal": None,
        "current_milestone": None,
        "session_notes": [],
        "recent_events": [],
        "event_count": 0,
        "max_events": 100,
    }
    for root_name in ("vault_dir", "vector_db_dir", "timeline_dir", "graph_db_dir"):
        assert not any(path.is_file() for path in env.roots[root_name].rglob("*"))


def test_episodic_endpoints_capture_vault_timeline_and_working_side_effects(
    isolated_memory_env,
):
    env = isolated_memory_env
    payload = {
        "title": "Isolated Aurora Episode",
        "summary": "Aurora boundary fixture summary",
        "details": "Created only inside tmp_path.",
        "importance": "high",
        "tags": ["boundary", "isolated"],
        "related_files": ["notes/example.md"],
    }
    written = env.client.post("/memory/episodic/write", json=payload)
    assert written.status_code == 200
    body = written.json()
    assert body["message"] == "Episodic Memory written."
    assert body["episode"]["title"] == payload["title"]
    episode_path = Path(body["episode"]["file_path"])
    assert episode_path.is_relative_to(env.roots["vault_dir"])
    assert episode_path.exists()
    assert len(list((env.roots["vault_dir"] / "episodic").glob("*.md"))) == 1
    assert len(_json_files(env.roots["timeline_dir"])) == 1
    assert _event_types(env) == ["episodic_memory_written"]

    listed = env.client.get("/memory/episodic/list", params={"limit": 10})
    assert listed.status_code == 200
    assert len(listed.json()["episodes"]) == 1
    assert listed.json()["episodes"][0]["file_path"] == str(episode_path)

    latest = env.client.get("/memory/episodic/latest")
    assert latest.status_code == 200
    assert latest.json()["episode"]["file_path"] == str(episode_path)
    assert "# Isolated Aurora Episode" in latest.json()["episode"]["content"]

    timeline_search = env.client.post(
        "/memory/timeline/search", json={"query": "Aurora boundary", "limit": 10}
    )
    assert timeline_search.status_code == 200
    assert len(timeline_search.json()["results"]) == 1
    assert _event_types(env) == ["episodic_memory_written", "timeline_memory_search"]


def test_episodic_list_and_latest_safely_create_missing_isolated_directory(
    isolated_memory_env,
):
    env = isolated_memory_env
    episodic_dir = env.roots["vault_dir"] / "episodic"
    assert not episodic_dir.exists()
    assert env.client.get("/memory/episodic/list").json()["episodes"] == []
    assert episodic_dir.is_dir()
    assert env.client.get("/memory/episodic/latest").json()["episode"] is None


def test_semantic_endpoints_use_only_isolated_vault_and_vector_index(isolated_memory_env):
    env = isolated_memory_env
    vector_dir = env.roots["vector_db_dir"]
    vector_dir.rmdir()

    before = env.client.get("/memory/semantic/status")
    assert before.status_code == 200
    assert before.json()["semantic_memory"]["document_count"] == 0
    assert vector_dir.is_dir()

    (env.roots["vault_dir"] / "aurora.md").write_text(
        "# Aurora Memory\n\nA unique aurora boundary token.", encoding="utf-8"
    )
    nested = env.roots["vault_dir"] / "notes"
    nested.mkdir()
    (nested / "harbor.md").write_text(
        "# Harbor Memory\n\nAn isolated harbor token.", encoding="utf-8"
    )

    indexed = env.client.post("/memory/semantic/index")
    assert indexed.status_code == 200
    assert indexed.json()["result"]["document_count"] == 2
    index_path = vector_dir / "semantic_index.json"
    assert index_path.exists()
    index = json.loads(index_path.read_text(encoding="utf-8"))
    assert index["document_count"] == 2
    assert all(
        Path(document["file_path"]).is_relative_to(env.roots["vault_dir"])
        for document in index["documents"]
    )
    assert _event_types(env) == ["semantic_memory_indexed"]

    status = env.client.get("/memory/semantic/status")
    assert status.status_code == 200
    assert status.json()["semantic_memory"]["document_count"] == 2

    searched = env.client.post(
        "/memory/semantic/search", json={"query": "aurora boundary", "limit": 5}
    )
    assert searched.status_code == 200
    assert searched.json()["query"] == "aurora boundary"
    assert searched.json()["results"][0]["title"] == "Aurora Memory"
    assert Path(searched.json()["results"][0]["file_path"]).is_relative_to(
        env.roots["vault_dir"]
    )
    assert _event_types(env) == ["semantic_memory_indexed", "semantic_memory_search"]


def test_timeline_status_list_latest_and_empty_search_are_isolated(isolated_memory_env):
    env = isolated_memory_env
    timeline_dir = env.roots["timeline_dir"]
    timeline_dir.rmdir()

    status = env.client.get("/memory/timeline/status")
    assert status.status_code == 200
    assert status.json()["timeline"]["timeline_dir"] == str(timeline_dir)
    assert status.json()["timeline"]["event_count"] == 0
    assert status.json()["timeline"]["latest_event"] is None
    assert timeline_dir.is_dir()

    listed = env.client.get("/memory/timeline/list")
    assert listed.status_code == 200
    assert listed.json()["events"] == []
    latest = env.client.get("/memory/timeline/latest")
    assert latest.status_code == 200
    assert latest.json()["event"] is None

    empty = env.client.post("/memory/timeline/search", json={"query": "", "limit": 20})
    assert empty.status_code == 200
    assert empty.json()["results"] == []
    assert _event_types(env) == ["timeline_memory_search"]


def test_graph_endpoints_capture_graph_timeline_and_working_side_effects(
    isolated_memory_env,
):
    env = isolated_memory_env
    graph_dir = env.roots["graph_db_dir"]
    graph_dir.rmdir()
    graph_path = graph_dir / "graph.json"

    initial = env.client.get("/memory/graph/status")
    assert initial.status_code == 200
    assert initial.json()["graph_memory"]["node_count"] == 0
    assert initial.json()["graph_memory"]["edge_count"] == 0
    assert not graph_path.exists()

    node = env.client.post(
        "/memory/graph/node",
        json={"label": "Aurora", "node_type": "concept", "properties": {"scope": "tmp"}},
    )
    assert node.status_code == 200
    assert node.json()["node"]["id"] == "node_aurora"
    assert graph_path.exists()
    assert _event_types(env) == ["graph_node_upserted"]

    edge_payload = {
        "source": "Aurora",
        "relation": "illuminates",
        "target": "Harbor",
        "properties": {"strength": 1},
    }
    edge = env.client.post("/memory/graph/edge", json=edge_payload)
    assert edge.status_code == 200
    assert edge.json()["created_new"] is True
    assert edge.json()["timeline_event"]["type"] == "graph_memory"
    assert len(_json_files(env.roots["timeline_dir"])) == 1

    duplicate = env.client.post("/memory/graph/edge", json=edge_payload)
    assert duplicate.status_code == 200
    assert duplicate.json()["created_new"] is False
    assert duplicate.json()["timeline_event"] is None
    assert len(_json_files(env.roots["timeline_dir"])) == 1

    nodes = env.client.get("/memory/graph/nodes", params={"limit": 50})
    edges = env.client.get("/memory/graph/edges", params={"limit": 50})
    assert nodes.status_code == edges.status_code == 200
    assert {item["id"] for item in nodes.json()["nodes"]} >= {
        "node_aurora",
        "node_harbor",
    }
    assert len(edges.json()["edges"]) == 1

    searched = env.client.post(
        "/memory/graph/search", json={"query": "illuminates", "limit": 20}
    )
    assert searched.status_code == 200
    assert len(searched.json()["results"]["edges"]) == 1
    assert _event_types(env)[-1] == "graph_memory_search"

    seeded = env.client.post("/memory/graph/seed")
    assert seeded.status_code == 200
    assert seeded.json()["new_edge_count"] == 10
    assert seeded.json()["graph_memory"]["edge_count"] == 11
    assert len(_json_files(env.roots["timeline_dir"])) == 11

    seeded_again = env.client.post("/memory/graph/seed")
    assert seeded_again.status_code == 200
    assert seeded_again.json()["new_edge_count"] == 0
    assert seeded_again.json()["graph_memory"]["edge_count"] == 11
    assert len(_json_files(env.roots["timeline_dir"])) == 11


def test_openapi_and_all_memory_operation_ids_are_locked():
    schema = app.openapi()
    assert len(schema.get("paths", {})) == 305
    assert len(schema.get("components", {}).get("schemas", {})) == 110

    actual = {}
    for method_and_path in EXPECTED_MEMORY_OPERATION_IDS:
        method, path = method_and_path.split(" ", 1)
        details = schema["paths"][path][method.lower()]
        actual[method_and_path] = details["operationId"]
    assert actual == EXPECTED_MEMORY_OPERATION_IDS


def test_protected_route_function_ast_is_locked():
    source = (PROJECT_ROOT / "aether/interface/api_server.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    actual = {}
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.name in PROTECTED_FUNCTION_AST_HASHES:
                normalized = ast.dump(node, include_attributes=False)
                actual[node.name] = hashlib.sha256(normalized.encode("utf-8")).hexdigest()
    assert actual == PROTECTED_FUNCTION_AST_HASHES

    source = (
        PROJECT_ROOT / "aether/interface/routers/tool_executor_routes.py"
    ).read_text(encoding="utf-8")
    tree = ast.parse(source)
    actual = {}
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.name in TOOL_EXECUTOR_ROUTER_FUNCTION_AST_HASHES:
                normalized = ast.dump(node, include_attributes=False)
                actual[node.name] = hashlib.sha256(normalized.encode("utf-8")).hexdigest()
    assert actual == TOOL_EXECUTOR_ROUTER_FUNCTION_AST_HASHES
