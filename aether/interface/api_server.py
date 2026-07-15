from fastapi import FastAPI
from pydantic import BaseModel

from aether.identity.loader import load_identity_seed, identity_preview
from aether.time.clock import time_state
from aether.memory.timeline.recorder import (
    record_event,
    list_events,
    latest_event,
    search_events,
    timeline_status,
)
from aether.core.runtime import runtime
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
from aether.verification.risk import classify_risk, verification_plan

app = FastAPI(
    title="Aether API",
    description="First Awakening API with Working Memory for Aether",
    version="0.2.0",
)


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    name: str
    status: str
    response: str
    time: dict
    working_memory_event_count: int


class GoalRequest(BaseModel):
    goal: str


class MilestoneRequest(BaseModel):
    milestone: str

class EpisodeWriteRequest(BaseModel):
    title: str
    summary: str
    details: str = ""
    importance: str = "normal"
    tags: list[str] = []
    related_files: list[str] = []

class SemanticSearchRequest(BaseModel):
    query: str
    limit: int = 5

class TimelineSearchRequest(BaseModel):
    query: str
    limit: int = 20


class GraphNodeRequest(BaseModel):
    label: str
    node_type: str = "entity"
    properties: dict = {}


class GraphEdgeRequest(BaseModel):
    source: str
    relation: str
    target: str
    properties: dict = {}


class GraphSearchRequest(BaseModel):
    query: str
    limit: int = 20


class VerificationRequest(BaseModel):
    text: str

@app.get("/")
def root():
    return {
        "name": "Aether",
        "status": runtime.status(),
        "message": "Aether API is running.",
        "time": time_state(),
        "working_memory": {
            "event_count": runtime.working_memory.summary()["event_count"],
            "current_goal": runtime.working_memory.current_goal,
            "current_milestone": runtime.working_memory.current_milestone,
        },
    }


@app.get("/identity")
def identity():
    preview = identity_preview()

    return {
        "name": "Aether",
        "identity_seed_loaded": True,
        "preview": preview,
    }


@app.post("/awaken")
def awaken():
    identity_seed = load_identity_seed()
    current_time = time_state()

    event = None
    event_recorded = False

    if not runtime.awake:
        runtime.awaken()

        existing_first_awakening = search_events("First Awakening", limit=1)

        if existing_first_awakening:
            event = existing_first_awakening[0]
            event_recorded = False
        else:
            event = record_event(
                event_type="milestone",
                title="First Awakening",
                description="Aether was awakened through the First Awakening API.",
                importance="high",
                related_files=[
                    "identity/identity_seed.md",
                    "config/time.yaml",
                    "docs/CONSTITUTION.md",
                    "docs/ARCHITECTURE.md",
                ],
            )
            event_recorded = True

        runtime.working_memory.add_event(
            role="aether",
            content="I am Aether. My Identity Seed is loaded. My local time is loaded. I am awake.",
            event_type="awakening",
            metadata={
                "timeline_event_id": event["id"] if event else None,
                "event_recorded": event_recorded,
            },
        )

    return {
        "name": "Aether",
        "status": runtime.status(),
        "identity_seed_loaded": True,
        "identity_seed_length": len(identity_seed),
        "time": current_time,
        "event_recorded": event_recorded,
        "event": event,
        "working_memory": runtime.working_memory.summary(),
        "message": "I am Aether. My Identity Seed is loaded. My local time is loaded. I am awake.",
    }

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    current_time = time_state()

    runtime.working_memory.add_event(
        role="user",
        content=request.message,
        event_type="message",
    )

    response_text = (
        "I am Aether. "
        "I can now keep short-term Working Memory during this runtime. "
        f"You said: {request.message}"
    )

    runtime.working_memory.add_event(
        role="aether",
        content=response_text,
        event_type="message",
    )

    summary = runtime.working_memory.summary()

    return ChatResponse(
        name="Aether",
        status=runtime.status(),
        time=current_time,
        response=response_text,
        working_memory_event_count=summary["event_count"],
    )


@app.get("/memory/working")
def get_working_memory():
    return {
        "name": "Aether",
        "status": runtime.status(),
        "time": time_state(),
        "working_memory": runtime.working_memory.summary(),
    }


@app.post("/memory/working/goal")
def set_working_goal(request: GoalRequest):
    runtime.working_memory.set_goal(request.goal)

    return {
        "name": "Aether",
        "status": runtime.status(),
        "message": "Working Memory goal updated.",
        "working_memory": runtime.working_memory.summary(),
    }


@app.post("/memory/working/milestone")
def set_working_milestone(request: MilestoneRequest):
    runtime.working_memory.set_milestone(request.milestone)

    return {
        "name": "Aether",
        "status": runtime.status(),
        "message": "Working Memory milestone updated.",
        "working_memory": runtime.working_memory.summary(),
    }


@app.post("/memory/working/clear")
def clear_working_memory():
    runtime.working_memory.clear()

    return {
        "name": "Aether",
        "status": runtime.status(),
        "message": "Working Memory cleared.",
        "working_memory": runtime.working_memory.summary(),
    }

@app.post("/memory/episodic/write")
def write_episodic_memory(request: EpisodeWriteRequest):
    episode = write_episode(
        title=request.title,
        summary=request.summary,
        details=request.details,
        importance=request.importance,
        tags=request.tags,
        related_files=request.related_files,
    )

    runtime.working_memory.add_event(
        role="aether",
        content=f"Episodic Memory written: {request.title}",
        event_type="episodic_memory_written",
        metadata={"file_path": episode["file_path"]},
    )

    return {
        "name": "Aether",
        "status": runtime.status(),
        "message": "Episodic Memory written.",
        "episode": episode,
    }


@app.get("/memory/episodic/list")
def list_episodic_memory(limit: int = 20):
    return {
        "name": "Aether",
        "status": runtime.status(),
        "episodes": list_episodes(limit=limit),
    }


@app.get("/memory/episodic/latest")
def get_latest_episodic_memory():
    episode = latest_episode()

    return {
        "name": "Aether",
        "status": runtime.status(),
        "episode": episode,
    }

@app.post("/memory/semantic/index")
def index_semantic_memory():
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


@app.get("/memory/semantic/status")
def get_semantic_memory_status():
    return {
        "name": "Aether",
        "status": runtime.status(),
        "semantic_memory": semantic_memory_status(),
    }


@app.post("/memory/semantic/search")
def search_memory(request: SemanticSearchRequest):
    results = search_semantic_memory(
        query=request.query,
        limit=request.limit,
    )

    runtime.working_memory.add_event(
        role="user",
        content=f"Semantic memory search: {request.query}",
        event_type="semantic_memory_search",
        metadata={"result_count": len(results)},
    )

    return {
        "name": "Aether",
        "status": runtime.status(),
        "query": request.query,
        "results": results,
    }

@app.get("/memory/timeline/status")
def get_timeline_status():
    return {
        "name": "Aether",
        "status": runtime.status(),
        "timeline": timeline_status(),
    }


@app.get("/memory/timeline/list")
def list_timeline_events(limit: int = 20):
    return {
        "name": "Aether",
        "status": runtime.status(),
        "events": list_events(limit=limit),
    }


@app.get("/memory/timeline/latest")
def get_latest_timeline_event():
    return {
        "name": "Aether",
        "status": runtime.status(),
        "event": latest_event(),
    }


@app.post("/memory/timeline/search")
def search_timeline_memory(request: TimelineSearchRequest):
    results = search_events(
        query=request.query,
        limit=request.limit,
    )

    runtime.working_memory.add_event(
        role="user",
        content=f"Timeline memory search: {request.query}",
        event_type="timeline_memory_search",
        metadata={"result_count": len(results)},
    )

    return {
        "name": "Aether",
        "status": runtime.status(),
        "query": request.query,
        "results": results,
    }


@app.get("/memory/graph/status")
def get_graph_memory_status():
    return {"name": "Aether", "status": runtime.status(), "graph_memory": graph_status()}


@app.post("/memory/graph/node")
def create_graph_node(request: GraphNodeRequest):
    node = upsert_node(request.label, request.node_type, request.properties)
    runtime.working_memory.add_event(
        role="aether",
        content=f"Graph node upserted: {request.label}",
        event_type="graph_node_upserted",
        metadata={"node_id": node["id"]},
    )
    return {"name": "Aether", "status": runtime.status(), "node": node}


@app.post("/memory/graph/edge")
def create_graph_edge(request: GraphEdgeRequest):
    edge = add_edge(request.source, request.relation, request.target, request.properties)
    created_new = edge.pop("created_new")
    timeline_event = None
    if created_new:
        timeline_event = record_event(
            event_type="graph_memory",
            title=f"Graph relationship added: {request.source} --{request.relation}--> {request.target}",
            description=f"Aether recorded a graph relationship from {request.source} to {request.target} using relation {request.relation}.",
            importance="normal",
        )
    runtime.working_memory.add_event(
        role="aether",
        content=f"Graph relationship {'added' if created_new else 'already exists'}: {request.source} --{request.relation}--> {request.target}",
        event_type="graph_edge_added",
        metadata={"edge_id": edge["id"], "created_new": created_new},
    )
    return {"name": "Aether", "status": runtime.status(), "edge": edge, "created_new": created_new, "timeline_event": timeline_event}


@app.get("/memory/graph/nodes")
def get_graph_nodes(limit: int = 50):
    return {"name": "Aether", "status": runtime.status(), "nodes": list_nodes(limit)}


@app.get("/memory/graph/edges")
def get_graph_edges(limit: int = 50):
    return {"name": "Aether", "status": runtime.status(), "edges": list_edges(limit)}


@app.post("/memory/graph/search")
def search_graph_memory(request: GraphSearchRequest):
    results = search_graph(request.query, request.limit)
    runtime.working_memory.add_event(
        role="user",
        content=f"Graph memory search: {request.query}",
        event_type="graph_memory_search",
        metadata={"node_count": len(results["nodes"]), "edge_count": len(results["edges"])},
    )
    return {"name": "Aether", "status": runtime.status(), "query": request.query, "results": results}


@app.post("/memory/graph/seed")
def seed_graph_memory():
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


@app.post("/verification/classify")
def classify_verification_risk(request: VerificationRequest):
    return {"name": "Aether", "status": runtime.status(), "classification": classify_risk(request.text)}


@app.post("/verification/plan")
def create_verification_plan(request: VerificationRequest):
    plan = verification_plan(request.text)
    runtime.working_memory.add_event(
        role="aether",
        content=f"Verification plan created for {plan['action_type']} request.",
        event_type="verification_plan_created",
        metadata={
            "risk_level": plan["risk_level"],
            "action_type": plan["action_type"],
            "requires_verification": plan["requires_verification"],
            "requires_user_approval": plan["requires_user_approval"],
        },
    )

    warnings = []
    timeline_event = None
    graph_relationship = None
    if plan["risk_level"] == "high":
        timeline_event = record_event(
            event_type="verification",
            title=f"High-risk verification plan: {plan['action_type']}",
            description="Aether created a verification plan for a high-risk request.",
            importance="high",
        )
        try:
            graph_relationship = add_edge(
                "Aether",
                "created_verification_plan_for",
                plan["action_type"],
            )
            graph_relationship.pop("created_new", None)
        except Exception as error:
            warnings.append(f"Graph Memory integration was unavailable: {error}")

    return {
        "name": "Aether",
        "status": runtime.status(),
        "plan": plan,
        "timeline_event": timeline_event,
        "graph_relationship": graph_relationship,
        "warnings": warnings,
    }
