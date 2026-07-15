"""JSON-backed relationship memory for Aether's first Graph Memory foundation."""

from pathlib import Path
import json
import re

import yaml

from aether.time.clock import get_timezone, now_iso


def load_aether_config(path: str = "config/aether.yaml") -> dict:
    config_path = Path(path)
    if not config_path.exists():
        return {}

    with config_path.open("r", encoding="utf-8") as file:
        return yaml.safe_load(file) or {}


def get_graph_db_dir() -> Path:
    config = load_aether_config()
    graph_db_dir = config.get("paths", {}).get("graph_db_dir", "graph_db")
    return Path(graph_db_dir)


def get_graph_path() -> Path:
    return get_graph_db_dir() / "graph.json"


def _new_graph() -> dict:
    timestamp = now_iso()
    return {
        "type": "graph_memory",
        "version": "0.1.0",
        "created": timestamp,
        "updated": timestamp,
        "timezone": get_timezone(),
        "nodes": {},
        "edges": [],
    }


def load_graph() -> dict:
    graph_path = get_graph_path()
    if not graph_path.exists():
        return _new_graph()

    try:
        graph = json.loads(graph_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return _new_graph()

    graph.setdefault("type", "graph_memory")
    graph.setdefault("version", "0.1.0")
    graph.setdefault("created", now_iso())
    graph.setdefault("updated", graph["created"])
    graph.setdefault("timezone", get_timezone())
    graph.setdefault("nodes", {})
    graph.setdefault("edges", [])
    return graph


def save_graph(graph: dict) -> None:
    graph_path = get_graph_path()
    graph_path.parent.mkdir(parents=True, exist_ok=True)
    graph["updated"] = now_iso()
    graph["timezone"] = get_timezone()
    graph_path.write_text(json.dumps(graph, indent=2, ensure_ascii=False), encoding="utf-8")


def slugify_id(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", text.strip().lower())
    slug = re.sub(r"_+", "_", slug).strip("_")
    return f"node_{slug or 'unnamed'}"


def upsert_node(label: str, node_type: str = "entity", properties: dict | None = None) -> dict:
    node_id = slugify_id(label)
    graph = load_graph()
    timestamp = now_iso()
    existing = graph["nodes"].get(node_id)

    if existing:
        existing["label"] = label
        existing["type"] = node_type
        existing["properties"] = properties or {}
        existing["updated"] = timestamp
        node = existing
    else:
        node = {
            "id": node_id,
            "label": label,
            "type": node_type,
            "properties": properties or {},
            "created": timestamp,
            "updated": timestamp,
            "timezone": get_timezone(),
        }
        graph["nodes"][node_id] = node

    save_graph(graph)
    return node


def add_edge(source: str, relation: str, target: str, properties: dict | None = None) -> dict:
    source_node = upsert_node(source)
    target_node = upsert_node(target)
    graph = load_graph()
    source_id = source_node["id"]
    target_id = target_node["id"]

    for edge in graph["edges"]:
        if (
            edge.get("source") == source_id
            and edge.get("relation") == relation
            and edge.get("target") == target_id
        ):
            result = dict(edge)
            result["created_new"] = False
            return result

    timestamp = now_iso()
    edge = {
        "id": f"edge_{slugify_id(source)[5:]}_{slugify_id(relation)[5:]}_{slugify_id(target)[5:]}",
        "source": source_id,
        "relation": relation,
        "target": target_id,
        "properties": properties or {},
        "created": timestamp,
        "updated": timestamp,
        "timezone": get_timezone(),
    }
    graph["edges"].append(edge)
    save_graph(graph)

    result = dict(edge)
    result["created_new"] = True
    return result


def list_nodes(limit: int = 50) -> list[dict]:
    graph = load_graph()
    nodes = list(graph["nodes"].values())
    nodes.sort(key=lambda node: node.get("updated", ""), reverse=True)
    return nodes[: max(0, limit)]


def list_edges(limit: int = 50) -> list[dict]:
    graph = load_graph()
    edges = sorted(graph["edges"], key=lambda edge: edge.get("updated", ""), reverse=True)
    return edges[: max(0, limit)]


def search_graph(query: str, limit: int = 20) -> dict:
    query_lower = _search_text(query)
    if not query_lower:
        return {"nodes": [], "edges": []}

    graph = load_graph()
    nodes = []
    edges = []

    for node in graph["nodes"].values():
        searchable = _search_text(" ".join(
            [node.get("id", ""), node.get("label", ""), node.get("type", ""), json.dumps(node.get("properties", {}), ensure_ascii=False)]
        ))
        if query_lower in searchable:
            nodes.append(node)

    for edge in graph["edges"]:
        searchable = _search_text(" ".join(
            [edge.get("source", ""), edge.get("relation", ""), edge.get("target", ""), json.dumps(edge.get("properties", {}), ensure_ascii=False)]
        ))
        if query_lower in searchable:
            edges.append(edge)

    return {"nodes": nodes[: max(0, limit)], "edges": edges[: max(0, limit)]}


def _search_text(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()


def graph_status() -> dict:
    graph = load_graph()
    return {
        "graph_path": str(get_graph_path()),
        "node_count": len(graph["nodes"]),
        "edge_count": len(graph["edges"]),
        "created": graph.get("created"),
        "updated": graph.get("updated"),
        "timezone": graph.get("timezone"),
    }
