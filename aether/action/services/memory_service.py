"""Memory Service — Thin Interface Refactor Phase 8 (Milestone 80K).

Moves memory endpoint orchestration from api_server.py into this service module.

Behavior-preserving refactor: no endpoint path, response shape, or side-effect changes.
"""

from aether.core.runtime import runtime
from aether.time.clock import time_state

from aether.memory.timeline.recorder import (
    record_event,
    list_events,
    latest_event,
    search_events,
    timeline_status,
)
from aether.memory.episodic.writer import write_episode, list_episodes, latest_episode
from aether.memory.semantic.indexer import (
    build_semantic_index,
    search_semantic_memory,
    semantic_memory_status,
)
from aether.memory.graph.store import (
    add_edge,
    graph_status,
    list_edges,
    list_nodes,
    search_graph,
    upsert_node,
)


# --------------------------------------------------------------------------- #
# Working Memory
# --------------------------------------------------------------------------- #


def handle_get_working_memory() -> dict:
    return {
        "name": "Aether",
        "status": runtime.status(),
        "time": time_state(),
        "working_memory": runtime.working_memory.summary(),
    }


def handle_set_working_goal(goal: str) -> dict:
    runtime.working_memory.set_goal(goal)
    return {
        "name": "Aether",
        "status": runtime.status(),
        "message": "Working Memory goal updated.",
        "working_memory": runtime.working_memory.summary(),
    }


def handle_set_working_milestone(milestone: str) -> dict:
    runtime.working_memory.set_milestone(milestone)
    return {
        "name": "Aether",
        "status": runtime.status(),
        "message": "Working Memory milestone updated.",
        "working_memory": runtime.working_memory.summary(),
    }


def handle_clear_working_memory() -> dict:
    runtime.working_memory.clear()
    return {
        "name": "Aether",
        "status": runtime.status(),
        "message": "Working Memory cleared.",
        "working_memory": runtime.working_memory.summary(),
    }


# --------------------------------------------------------------------------- #
# Episodic Memory
# --------------------------------------------------------------------------- #


def handle_write_episodic_memory(
    title: str,
    summary: str,
    details: str = "",
    importance: str = "normal",
    tags: list[str] | None = None,
    related_files: list[str] | None = None,
) -> dict:
    episode = write_episode(
        title=title,
        summary=summary,
        details=details,
        importance=importance,
        tags=tags or [],
        related_files=related_files or [],
    )
    runtime.working_memory.add_event(
        role="aether",
        content=f"Episodic Memory written: {title}",
        event_type="episodic_memory_written",
        metadata={"file_path": episode["file_path"]},
    )
    return {
        "name": "Aether",
        "status": runtime.status(),
        "message": "Episodic Memory written.",
        "episode": episode,
    }


def handle_list_episodic_memory(limit: int = 20) -> dict:
    return {
        "name": "Aether",
        "status": runtime.status(),
        "episodes": list_episodes(limit=limit),
    }


def handle_latest_episodic_memory() -> dict:
    episode = latest_episode()
    return {
        "name": "Aether",
        "status": runtime.status(),
        "episode": episode,
    }


# --------------------------------------------------------------------------- #
# Semantic Memory
# --------------------------------------------------------------------------- #


def handle_index_semantic_memory() -> dict:
    result = build_semantic_index()
    runtime.working_memory.add_event(
        role="aether",
        content=f"Semantic Memory index built with {result['document_count']} documents.",
        event_type="semantic_memory_indexed",
        metadata={"index_path": result["index_path"]},
    )
    return {
        "name": "Aether",
        "status": runtime.status(),
        "message": "Semantic Memory index built.",
        "result": result,
    }


def handle_semantic_memory_status() -> dict:
    return {
        "name": "Aether",
        "status": runtime.status(),
        "semantic_memory": semantic_memory_status(),
    }


def handle_search_semantic_memory(query: str, limit: int = 5) -> dict:
    results = search_semantic_memory(query=query, limit=limit)
    runtime.working_memory.add_event(
        role="user",
        content=f"Semantic memory search: {query}",
        event_type="semantic_memory_search",
        metadata={"result_count": len(results)},
    )
    return {
        "name": "Aether",
        "status": runtime.status(),
        "query": query,
        "results": results,
    }


# --------------------------------------------------------------------------- #
# Timeline Memory
# --------------------------------------------------------------------------- #


def handle_timeline_status() -> dict:
    return {
        "name": "Aether",
        "status": runtime.status(),
        "timeline": timeline_status(),
    }


def handle_list_timeline_events(limit: int = 20) -> dict:
    return {
        "name": "Aether",
        "status": runtime.status(),
        "events": list_events(limit=limit),
    }


def handle_latest_timeline_event() -> dict:
    return {
        "name": "Aether",
        "status": runtime.status(),
        "event": latest_event(),
    }


def handle_search_timeline(query: str, limit: int = 20) -> dict:
    results = search_events(query=query, limit=limit)
    runtime.working_memory.add_event(
        role="user",
        content=f"Timeline memory search: {query}",
        event_type="timeline_memory_search",
        metadata={"result_count": len(results)},
    )
    return {
        "name": "Aether",
        "status": runtime.status(),
        "query": query,
        "results": results,
    }


# --------------------------------------------------------------------------- #
# Graph Memory
# --------------------------------------------------------------------------- #


def handle_graph_status() -> dict:
    return {"name": "Aether", "status": runtime.status(), "graph_memory": graph_status()}


def handle_create_graph_node(label: str, node_type: str = "entity", properties: dict | None = None) -> dict:
    node = upsert_node(label, node_type, properties or {})
    runtime.working_memory.add_event(
        role="aether",
        content=f"Graph node upserted: {label}",
        event_type="graph_node_upserted",
        metadata={"node_id": node["id"]},
    )
    return {"name": "Aether", "status": runtime.status(), "node": node}


def handle_create_graph_edge(source: str, relation: str, target: str, properties: dict | None = None) -> dict:
    edge = add_edge(source, relation, target, properties or {})
    created_new = edge.pop("created_new")
    timeline_event = None
    if created_new:
        timeline_event = record_event(
            event_type="graph_memory",
            title=f"Graph relationship added: {source} --{relation}--> {target}",
            description=f"Aether recorded a graph relationship from {source} to {target} using relation {relation}.",
            importance="normal",
        )
    runtime.working_memory.add_event(
        role="aether",
        content=f"Graph relationship {'added' if created_new else 'already exists'}: {source} --{relation}--> {target}",
        event_type="graph_edge_added",
        metadata={"edge_id": edge["id"], "created_new": created_new},
    )
    return {"name": "Aether", "status": runtime.status(), "edge": edge, "created_new": created_new, "timeline_event": timeline_event}


def handle_list_graph_nodes(limit: int = 50) -> dict:
    return {"name": "Aether", "status": runtime.status(), "nodes": list_nodes(limit)}


def handle_list_graph_edges(limit: int = 50) -> dict:
    return {"name": "Aether", "status": runtime.status(), "edges": list_edges(limit)}


def handle_search_graph(query: str, limit: int = 20) -> dict:
    results = search_graph(query, limit)
    runtime.working_memory.add_event(
        role="user",
        content=f"Graph memory search: {query}",
        event_type="graph_memory_search",
        metadata={"node_count": len(results["nodes"]), "edge_count": len(results["edges"])},
    )
    return {"name": "Aether", "status": runtime.status(), "query": query, "results": results}


def handle_seed_graph_memory() -> dict:
    relationships = [
        ("Aether", "has_identity_seed", "identity/identity_seed.md"),
        ("Aether", "follows", "docs/CONSTITUTION.md"),
        ("Aether", "has_architecture", "docs/ARCHITECTURE.md"),
        ("Time Layer", "supports", "Memory"),
        ("Timeline Memory", "belongs_to", "Memory"),
        ("Semantic Memory", "belongs_to", "Memory"),
        ("Episodic Memory", "belongs_to", "Memory"),
        ("Graph Memory", "belongs_to", "Memory"),
        ("Workflow Policy", "belongs_to", "Thinking"),
        ("External LLM", "is_consultant_not_identity", "Aether"),
    ]
    edges = []
    new_edge_count = 0
    for source, relation, target in relationships:
        edge = add_edge(source, relation, target)
        created_new = edge.pop("created_new")
        if created_new:
            new_edge_count += 1
            record_event(
                event_type="graph_memory",
                title=f"Graph relationship added: {source} --{relation}--> {target}",
                description=f"Aether recorded a graph relationship from {source} to {target} using relation {relation}.",
                importance="normal",
            )
        runtime.working_memory.add_event(
            role="aether",
            content=f"Graph relationship {'added' if created_new else 'already exists'}: {source} --{relation}--> {target}",
            event_type="graph_edge_added",
            metadata={"edge_id": edge["id"], "created_new": created_new},
        )
        edges.append(edge)
    runtime.working_memory.add_event(
        role="aether",
        content=f"Graph Memory seed completed with {new_edge_count} new relationships.",
        event_type="graph_edge_added",
        metadata={"new_edge_count": new_edge_count},
    )
    return {"name": "Aether", "status": runtime.status(), "new_edge_count": new_edge_count, "edges": edges, "graph_memory": graph_status()}
