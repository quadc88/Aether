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
from aether.action.approval_queue import (
    approval_queue_status,
    approve_item,
    cancel_item,
    create_approval_item,
    get_approval_item,
    list_approval_items,
    reject_item,
)
from aether.action.tool_registry import (
    disable_tool,
    enable_tool,
    get_tool,
    list_tools,
    register_tool,
    search_tools,
    seed_default_tools,
    tool_registry_status,
    update_tool_policy,
)
from aether.action.tool_planner import (
    create_tool_invocation_plan,
    get_tool_plan,
    list_tool_plans,
    tool_planner_status,
)
from aether.action.tool_executor import (
    execute_tool,
    get_execution,
    list_executions,
    seed_sandbox_tools,
    tool_executor_status,
)
from aether.action.restricted_file_reader import (
    file_access_status,
    get_file_access,
    list_allowed_roots,
    list_file_accesses,
    read_restricted_file,
)
from aether.action.restricted_file_browser import (
    browse_restricted_path,
    file_browser_status,
    get_file_browse,
    list_browser_allowed_roots,
    list_file_browses,
    search_restricted_files,
)
from aether.action.self_inspector import (
    create_project_self_inspection,
    get_self_inspection_report,
    list_self_inspection_reports,
    self_inspection_status,
)
from aether.action.patch_proposal import create_patch_proposal, get_patch_proposal, list_patch_proposals, mark_patch_proposal_status, patch_proposal_status
from aether.action.patch_review import get_patch_review, list_patch_reviews, patch_review_status, review_patch_proposal
from aether.action.patch_apply import apply_patch_proposal, get_patch_apply, list_patch_applies, patch_apply_status
from aether.action.patch_rollback import rollback_patch_apply, get_patch_rollback, list_patch_rollbacks, patch_rollback_status
from aether.action.mutation_log import record_mutation, record_milestone_completed, mutation_log_status, list_mutations, summarize_mutations, get_mutation

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


class ApprovalCreateRequest(BaseModel):
    request_text: str
    proposed_action: str
    metadata: dict = {}


class ApprovalDecisionRequest(BaseModel):
    approval_id: str
    decision_reason: str = ""


class ApprovalListRequest(BaseModel):
    status: str | None = None
    limit: int = 50


class ToolRegisterRequest(BaseModel):
    tool_id: str
    name: str
    description: str
    category: str
    risk_level: str = "medium"
    enabled: bool = True
    requires_verification: bool = True
    requires_user_approval: bool = False
    allow_auto_execute: bool = False
    input_schema: dict = {}
    output_schema: dict = {}
    metadata: dict = {}


class ToolSearchRequest(BaseModel):
    query: str
    limit: int = 20


class ToolPolicyUpdateRequest(BaseModel):
    tool_id: str
    risk_level: str | None = None
    requires_verification: bool | None = None
    requires_user_approval: bool | None = None
    allow_auto_execute: bool | None = None


class ToolPlanRequest(BaseModel):
    text: str
    proposed_action: str | None = None
    create_approval_if_required: bool = False
    metadata: dict = {}


class ToolPlanListRequest(BaseModel):
    limit: int = 50


class ToolExecutionRequest(BaseModel):
    text: str
    tool_id: str | None = None
    input_payload: dict = {}
    proposed_action: str | None = None
    create_approval_if_required: bool = False
    dry_run: bool = True
    metadata: dict = {}


class ToolExecutionListRequest(BaseModel):
    limit: int = 50


class RestrictedFileReadRequest(BaseModel):
    path: str
    max_chars: int = 12000
    metadata: dict = {}


class RestrictedFileAccessListRequest(BaseModel):
    limit: int = 50


class RestrictedFileBrowseRequest(BaseModel):
    path: str = "C:/Aether"
    max_depth: int = 3
    max_entries: int = 200
    include_files: bool = True
    include_dirs: bool = True
    metadata: dict = {}


class RestrictedFileSearchRequest(BaseModel):
    query: str
    root: str = "C:/Aether"
    max_results: int = 50
    metadata: dict = {}


class RestrictedFileBrowseListRequest(BaseModel):
    limit: int = 50


class SelfInspectionRequest(BaseModel):
    root: str = "C:/Aether"
    max_files_to_read: int = 20
    max_chars_per_file: int = 6000
    metadata: dict = {}


class SelfInspectionListRequest(BaseModel):
    limit: int = 20

class PatchProposalRequest(BaseModel):
    target_path: str
    request_text: str
    proposed_change_summary: str
    proposed_excerpt: str
    reason: str = ""
    original_excerpt: str | None = None
    create_approval_if_required: bool = False
    metadata: dict = {}

class PatchProposalStatusUpdateRequest(BaseModel):
    proposal_id: str
    status: str
    reason: str = ""

class PatchReviewRequest(BaseModel):
    proposal_id: str
    decision: str
    review_reason: str = ""
    reviewer: str = "user"
    metadata: dict = {}
class PatchApplyRequest(BaseModel):
    proposal_id: str
    dry_run: bool = True
    metadata: dict = {}
class PatchRollbackRequest(BaseModel):
    apply_id: str
    dry_run: bool = True
    metadata: dict = {}
class MutationRecordRequest(BaseModel):
    mutation_type: str
    title: str
    summary: str
    milestone: str | None = None
    target_path: str | None = None
    metadata: dict = {}
class MilestoneCompletedRequest(BaseModel):
    milestone: str
    summary: str
    metadata: dict = {}

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


def _add_approval_working_memory_event(item: dict, event_type: str) -> None:
    runtime.working_memory.add_event(
        role="aether",
        content=f"Approval item {item['status']}: {item['id']}",
        event_type=event_type,
        metadata={
            "approval_id": item["id"],
            "action_type": item["action_type"],
            "risk_level": item["risk_level"],
            "status": item["status"],
        },
    )


@app.post("/action/approval/create")
def create_action_approval(request: ApprovalCreateRequest):
    plan = verification_plan(request.request_text)
    item = create_approval_item(
        request_text=request.request_text,
        proposed_action=request.proposed_action,
        verification_plan=plan,
        metadata=request.metadata,
    )
    _add_approval_working_memory_event(item, "approval_item_created")
    warnings = []
    timeline_event = None
    graph_relationship = None
    if item["risk_level"] == "high":
        timeline_event = record_event(
            event_type="action_approval",
            title=f"Approval item created: {item['action_type']}",
            description=f"Aether created an approval item for a {item['risk_level']}-risk action.",
            importance="high",
        )
    try:
        graph_relationship = add_edge("Aether", "created_approval_item_for", item["action_type"])
        graph_relationship.pop("created_new", None)
    except Exception as error:
        warnings.append(f"Graph Memory integration was unavailable: {error}")
    return {
        "name": "Aether",
        "status": runtime.status(),
        "item": item,
        "approval_optional": not item["requires_user_approval"],
        "queue_status": approval_queue_status(),
        "timeline_event": timeline_event,
        "graph_relationship": graph_relationship,
        "warnings": warnings,
    }


@app.get("/action/approval/status")
def get_action_approval_status():
    return {"name": "Aether", "status": runtime.status(), "approval_queue": approval_queue_status()}


@app.get("/action/approval/list")
def list_action_approvals(status: str | None = None, limit: int = 50):
    return {"name": "Aether", "status": runtime.status(), "items": list_approval_items(status, limit)}


@app.get("/action/approval/{approval_id}")
def get_action_approval(approval_id: str):
    return {"name": "Aether", "status": runtime.status(), "item": get_approval_item(approval_id)}


def _record_approval_decision(approval_id: str, decision_reason: str, decision: str) -> dict:
    decision_functions = {"approved": approve_item, "rejected": reject_item, "cancelled": cancel_item}
    item = decision_functions[decision](approval_id, decision_reason)
    if item is None:
        return {"name": "Aether", "status": runtime.status(), "item": None, "warnings": ["Approval item was not found."]}
    if item.get("warning"):
        return {"name": "Aether", "status": runtime.status(), "item": item, "warnings": [item["warning"]]}

    _add_approval_working_memory_event(item, f"approval_item_{decision}")
    timeline_event = record_event(
        event_type="action_approval_decision",
        title=f"Approval item {decision}: {approval_id}",
        description=f"User decision recorded for approval item {approval_id}.",
        importance="high",
    )
    warnings = []
    graph_relationship = None
    try:
        graph_relationship = add_edge(approval_id, "has_decision", decision)
        graph_relationship.pop("created_new", None)
    except Exception as error:
        warnings.append(f"Graph Memory integration was unavailable: {error}")
    return {
        "name": "Aether",
        "status": runtime.status(),
        "item": item,
        "timeline_event": timeline_event,
        "graph_relationship": graph_relationship,
        "warnings": warnings,
    }


@app.post("/action/approval/approve")
def approve_action_approval(request: ApprovalDecisionRequest):
    return _record_approval_decision(request.approval_id, request.decision_reason, "approved")


@app.post("/action/approval/reject")
def reject_action_approval(request: ApprovalDecisionRequest):
    return _record_approval_decision(request.approval_id, request.decision_reason, "rejected")


@app.post("/action/approval/cancel")
def cancel_action_approval(request: ApprovalDecisionRequest):
    return _record_approval_decision(request.approval_id, request.decision_reason, "cancelled")


def _add_tool_working_memory_event(tool: dict, event_type: str) -> None:
    runtime.working_memory.add_event(
        role="aether",
        content=f"Tool {event_type.replace('_', ' ')}: {tool['id']}",
        event_type=event_type,
        metadata={
            "tool_id": tool["id"],
            "risk_level": tool["risk_level"],
            "enabled": tool["enabled"],
            "requires_user_approval": tool["requires_user_approval"],
            "allow_auto_execute": tool["allow_auto_execute"],
        },
    )


def _add_tool_graph_relationships(tool: dict, policy_only: bool = False) -> tuple[list[dict], list[str]]:
    relationships = []
    warnings = []
    try:
        if not policy_only:
            relationships.extend(
                [
                    add_edge("Aether", "registered_tool", tool["id"]),
                    add_edge(tool["id"], "belongs_to_category", tool["category"]),
                    add_edge(tool["id"], "has_risk_level", tool["risk_level"]),
                ]
            )
        else:
            relationships.append(add_edge(tool["id"], "has_policy", tool["risk_level"]))
        for relationship in relationships:
            relationship.pop("created_new", None)
    except Exception as error:
        warnings.append(f"Graph Memory integration was unavailable: {error}")
    return relationships, warnings


def _record_tool_timeline(tool: dict, title: str, description: str) -> dict:
    return record_event(
        event_type="tool_registry",
        title=title,
        description=description,
        importance="high" if tool["risk_level"] == "high" else "normal",
    )


@app.get("/action/tools/status")
def get_tool_registry_status():
    return {"name": "Aether", "status": runtime.status(), "tool_registry": tool_registry_status()}


@app.post("/action/tools/register")
def register_action_tool(request: ToolRegisterRequest):
    tool = register_tool(
        tool_id=request.tool_id,
        name=request.name,
        description=request.description,
        category=request.category,
        risk_level=request.risk_level,
        enabled=request.enabled,
        requires_verification=request.requires_verification,
        requires_user_approval=request.requires_user_approval,
        allow_auto_execute=request.allow_auto_execute,
        input_schema=request.input_schema,
        output_schema=request.output_schema,
        metadata=request.metadata,
    )
    _add_tool_working_memory_event(tool, "tool_registered")
    timeline_event = None
    if tool["risk_level"] == "high":
        timeline_event = _record_tool_timeline(
            tool,
            f"Tool registered: {tool['id']}",
            f"Aether registered tool {tool['id']} with risk level {tool['risk_level']}.",
        )
    graph_relationships, warnings = _add_tool_graph_relationships(tool)
    return {"name": "Aether", "status": runtime.status(), "tool": tool, "timeline_event": timeline_event, "graph_relationships": graph_relationships, "warnings": warnings}


@app.post("/action/tools/seed")
def seed_action_tools():
    result = seed_default_tools()
    runtime.working_memory.add_event(
        role="aether",
        content=f"Tool Registry seeded with {result['created_count']} new tools.",
        event_type="tool_registry_seeded",
        metadata={"tool_count": len(result["tools"]), "created_count": result["created_count"]},
    )
    timeline_events = []
    warnings = []
    for tool in result["tools"]:
        if tool["risk_level"] == "high" and tool["id"] in result["created_tool_ids"]:
            timeline_events.append(_record_tool_timeline(tool, f"Tool registered: {tool['id']}", f"Aether registered tool {tool['id']} with risk level {tool['risk_level']}."))
        _, graph_warnings = _add_tool_graph_relationships(tool)
        warnings.extend(graph_warnings)
    return {"name": "Aether", "status": runtime.status(), "result": result, "tool_registry": tool_registry_status(), "timeline_events": timeline_events, "warnings": warnings}


@app.get("/action/tools/list")
def list_action_tools(category: str | None = None, enabled: bool | None = None, limit: int = 100):
    return {"name": "Aether", "status": runtime.status(), "tools": list_tools(category, enabled, limit)}


@app.get("/action/tools/{tool_id}")
def get_action_tool(tool_id: str):
    return {"name": "Aether", "status": runtime.status(), "tool": get_tool(tool_id)}


@app.post("/action/tools/search")
def search_action_tools(request: ToolSearchRequest):
    return {"name": "Aether", "status": runtime.status(), "query": request.query, "tools": search_tools(request.query, request.limit)}


def _change_tool_enabled(tool_id: str, enabled: bool) -> dict:
    tool = enable_tool(tool_id) if enabled else disable_tool(tool_id)
    if tool is None:
        return {"name": "Aether", "status": runtime.status(), "tool": None, "warnings": ["Tool was not found."]}
    event_type = "tool_enabled" if enabled else "tool_disabled"
    _add_tool_working_memory_event(tool, event_type)
    timeline_event = None
    if not enabled or tool["risk_level"] == "high":
        action = "enabled" if enabled else "disabled"
        timeline_event = _record_tool_timeline(tool, f"Tool {action}: {tool['id']}", f"Aether {action} tool {tool['id']}.")
    return {"name": "Aether", "status": runtime.status(), "tool": tool, "timeline_event": timeline_event, "warnings": []}


@app.post("/action/tools/enable/{tool_id}")
def enable_action_tool(tool_id: str):
    return _change_tool_enabled(tool_id, True)


@app.post("/action/tools/disable/{tool_id}")
def disable_action_tool(tool_id: str):
    return _change_tool_enabled(tool_id, False)


@app.post("/action/tools/policy")
def update_action_tool_policy(request: ToolPolicyUpdateRequest):
    tool = update_tool_policy(
        tool_id=request.tool_id,
        risk_level=request.risk_level,
        requires_verification=request.requires_verification,
        requires_user_approval=request.requires_user_approval,
        allow_auto_execute=request.allow_auto_execute,
    )
    if tool is None:
        return {"name": "Aether", "status": runtime.status(), "tool": None, "warnings": ["Tool was not found."]}
    _add_tool_working_memory_event(tool, "tool_policy_updated")
    timeline_event = None
    if tool["risk_level"] == "high":
        timeline_event = _record_tool_timeline(tool, f"Tool policy updated: {tool['id']}", f"Aether updated policy for high-risk tool {tool['id']}.")
    graph_relationships, warnings = _add_tool_graph_relationships(tool, policy_only=True)
    return {"name": "Aether", "status": runtime.status(), "tool": tool, "timeline_event": timeline_event, "graph_relationships": graph_relationships, "warnings": warnings}


@app.post("/action/tool-plan/create")
def create_action_tool_plan(request: ToolPlanRequest):
    plan = create_tool_invocation_plan(
        text=request.text,
        proposed_action=request.proposed_action,
        metadata=request.metadata,
        create_approval_if_required=request.create_approval_if_required,
    )
    decision = plan["decision"]
    tool_id = plan["candidate_tool"]["tool_id"]
    runtime.working_memory.add_event(
        role="aether",
        content=f"Tool invocation plan created: {tool_id or 'no tool'}.",
        event_type="tool_invocation_plan_created",
        metadata={
            "plan_id": plan["id"],
            "tool_id": tool_id,
            "plan_status": decision["plan_status"],
            "risk_level": decision["risk_level"],
            "requires_user_approval": decision["requires_user_approval"],
            "approval_item_created": decision["approval_item_created"],
        },
    )
    timeline_event = None
    if decision["plan_status"] in {"approval_required", "blocked", "tool_disabled"} or decision["approval_item_created"]:
        timeline_event = record_event(
            event_type="tool_planning",
            title=f"Tool invocation plan: {tool_id or 'no tool'}",
            description=f"Aether created a tool invocation plan with status {decision['plan_status']}.",
            importance="high" if decision["requires_user_approval"] or decision["plan_status"] in {"blocked", "tool_disabled"} else "normal",
        )
    warnings = []
    graph_relationships = []
    try:
        graph_relationships.append(add_edge("Aether", "created_tool_plan", plan["id"]))
        if tool_id:
            graph_relationships.append(add_edge(plan["id"], "planned_tool", tool_id))
        graph_relationships.append(add_edge(plan["id"], "has_status", decision["plan_status"]))
        if plan["approval_item"]:
            graph_relationships.append(add_edge(plan["id"], "created_approval_item", plan["approval_item"]["id"]))
        for relationship in graph_relationships:
            relationship.pop("created_new", None)
    except Exception as error:
        warnings.append(f"Graph Memory integration was unavailable: {error}")
    return {"name": "Aether", "status": runtime.status(), "plan": plan, "timeline_event": timeline_event, "graph_relationships": graph_relationships, "warnings": warnings}


@app.get("/action/tool-plan/status")
def get_action_tool_plan_status():
    return {"name": "Aether", "status": runtime.status(), "tool_planner": tool_planner_status()}


@app.get("/action/tool-plan/list")
def list_action_tool_plans(limit: int = 50):
    return {"name": "Aether", "status": runtime.status(), "plans": list_tool_plans(limit)}


@app.get("/action/tool-plan/{plan_id}")
def get_action_tool_plan(plan_id: str):
    return {"name": "Aether", "status": runtime.status(), "plan": get_tool_plan(plan_id)}


@app.post("/action/tool-executor/seed-sandbox-tools")
def seed_action_sandbox_tools():
    result = seed_sandbox_tools()
    runtime.working_memory.add_event(
        role="aether",
        content=f"Sandbox tools seeded: {result['created_count']} new tools.",
        event_type="sandbox_tools_seeded",
        metadata={"tool_count": len(result["tools"]), "created_count": result["created_count"]},
    )
    return {"name": "Aether", "status": runtime.status(), "result": result}


@app.post("/action/tool-executor/execute")
def execute_action_tool(request: ToolExecutionRequest):
    execution = execute_tool(
        text=request.text,
        tool_id=request.tool_id,
        input_payload=request.input_payload,
        proposed_action=request.proposed_action,
        create_approval_if_required=request.create_approval_if_required,
        dry_run=request.dry_run,
        metadata=request.metadata,
    )
    runtime.working_memory.add_event(
        role="aether",
        content=f"Tool execution attempted: {execution['tool_id'] or 'no tool'} ({execution['status']}).",
        event_type="tool_execution_attempted",
        metadata={
            "execution_id": execution["id"],
            "tool_id": execution["tool_id"],
            "status": execution["status"],
            "dry_run": execution["dry_run"],
            "requires_user_approval": execution["plan"]["decision"]["requires_user_approval"],
        },
    )
    file_access_audit = None
    if execution["tool_id"] == "file.restricted_read" and isinstance(execution["result"], dict) and "id" in execution["result"]:
        file_access_audit = _record_restricted_file_access(execution["result"])
    self_inspection_audit = None
    if execution["tool_id"] == "project.self_inspect" and isinstance(execution["result"], dict) and "id" in execution["result"]:
        self_inspection_audit = _record_self_inspection_report(execution["result"])
    timeline_event = None
    if (
        execution["status"] in {"blocked", "approval_required", "failed"}
        or not execution["dry_run"]
        or execution["tool_id"] not in {"echo.test", "file.preview_read", "web.search.mock", "shell.plan_only", "memory.write.dry_run", "approval.status"}
    ):
        timeline_event = record_event(
            event_type="tool_execution",
            title=f"Tool execution attempt: {execution['tool_id']}",
            description=f"Aether attempted tool execution with status {execution['status']}.",
            importance="high" if execution["status"] in {"blocked", "approval_required", "failed"} else "normal",
        )
    warnings = []
    graph_relationships = []
    try:
        graph_relationships.extend(
            [
                add_edge("Aether", "attempted_tool_execution", execution["id"]),
                add_edge(execution["id"], "used_tool", execution["tool_id"] or "no_tool"),
                add_edge(execution["id"], "has_status", execution["status"]),
            ]
        )
        for relationship in graph_relationships:
            relationship.pop("created_new", None)
    except Exception as error:
        warnings.append(f"Graph Memory integration was unavailable: {error}")
    return {"name": "Aether", "status": runtime.status(), "execution": execution, "timeline_event": timeline_event, "file_access_audit": file_access_audit, "self_inspection_audit": self_inspection_audit, "graph_relationships": graph_relationships, "warnings": warnings}


@app.get("/action/tool-executor/status")
def get_action_tool_executor_status():
    return {"name": "Aether", "status": runtime.status(), "tool_executor": tool_executor_status()}


@app.get("/action/tool-executor/list")
def list_action_tool_executions(limit: int = 50):
    return {"name": "Aether", "status": runtime.status(), "executions": list_executions(limit)}


@app.get("/action/tool-executor/{execution_id}")
def get_action_tool_execution(execution_id: str):
    return {"name": "Aether", "status": runtime.status(), "execution": get_execution(execution_id)}


def _record_restricted_file_access(access: dict) -> tuple[dict | None, list[dict], list[str]]:
    runtime.working_memory.add_event(
        role="aether",
        content=f"Restricted file read attempted: {access['path']} ({access['status']}).",
        event_type="restricted_file_read_attempted",
        metadata={
            "access_id": access["id"],
            "path": access["path"],
            "status": access["status"],
            "allowed": access["allowed"],
            "reason": access["reason"],
        },
    )
    timeline_event = record_event(
        event_type="file_access",
        title=f"Restricted file read: {access['status']}",
        description=f"Aether attempted restricted file read for {access['path']} with status {access['status']}.",
        importance="high" if access["status"] == "blocked" else "normal",
    )
    warnings = []
    graph_relationships = []
    try:
        graph_relationships.extend(
            [
                add_edge("Aether", "attempted_file_access", access["id"]),
                add_edge(access["id"], "has_status", access["status"]),
                add_edge(access["id"], "target_path", access["normalized_path"]),
            ]
        )
        for relationship in graph_relationships:
            relationship.pop("created_new", None)
    except Exception as error:
        warnings.append(f"Graph Memory integration was unavailable: {error}")
    return timeline_event, graph_relationships, warnings


@app.post("/action/file/read")
def read_action_file(request: RestrictedFileReadRequest):
    access = read_restricted_file(request.path, request.max_chars, request.metadata)
    timeline_event, graph_relationships, warnings = _record_restricted_file_access(access)
    return {"name": "Aether", "status": runtime.status(), "access": access, "timeline_event": timeline_event, "graph_relationships": graph_relationships, "warnings": warnings}


@app.get("/action/file/allowed-roots")
def get_action_file_allowed_roots():
    return {"name": "Aether", "status": runtime.status(), "allowed_roots": list_allowed_roots()}


@app.get("/action/file/access/status")
def get_action_file_access_status():
    return {"name": "Aether", "status": runtime.status(), "file_access": file_access_status()}


@app.get("/action/file/access/list")
def list_action_file_accesses(limit: int = 50):
    return {"name": "Aether", "status": runtime.status(), "accesses": list_file_accesses(limit)}


@app.get("/action/file/access/{access_id}")
def get_action_file_access(access_id: str):
    return {"name": "Aether", "status": runtime.status(), "access": get_file_access(access_id)}


def _record_restricted_file_browse(browse: dict) -> tuple[dict, list[dict], list[str]]:
    is_search = browse.get("operation") == "search"
    target = browse.get("root") if is_search else browse.get("path")
    normalized_target = browse.get("normalized_root") if is_search else browse.get("normalized_path")
    count = browse.get("result_count") if is_search else browse.get("entry_count")
    runtime.working_memory.add_event(
        role="aether",
        content=f"Restricted file {'search' if is_search else 'browse'} attempted: {target} ({browse['status']}).",
        event_type="restricted_file_search_attempted" if is_search else "restricted_file_browse_attempted",
        metadata={
            "browse_id": browse["id"], "path": target, "status": browse["status"],
            "allowed": browse["allowed"], "reason": browse["reason"], "count": count,
        },
    )
    timeline_event = record_event(
        event_type="file_browser",
        title=f"Restricted file {'search' if is_search else 'browse'}: {browse['status']}",
        description=f"Aether attempted restricted file {'search' if is_search else 'browse'} for {target} with status {browse['status']}.",
        importance="high" if browse["status"] == "blocked" else "normal",
    )
    warnings = []
    graph_relationships = []
    try:
        graph_relationships.append(add_edge("Aether", "attempted_file_search" if is_search else "attempted_file_browse", browse["id"]))
        if is_search:
            graph_relationships.append(add_edge(browse["id"], "has_query", browse["query"]))
        else:
            graph_relationships.append(add_edge(browse["id"], "target_path", normalized_target))
        graph_relationships.append(add_edge(browse["id"], "has_status", browse["status"]))
        for relationship in graph_relationships:
            relationship.pop("created_new", None)
    except Exception as error:
        warnings.append(f"Graph Memory integration was unavailable: {error}")
    return timeline_event, graph_relationships, warnings


@app.post("/action/file/browse")
def browse_action_file(request: RestrictedFileBrowseRequest):
    browse = browse_restricted_path(
        request.path, request.max_depth, request.max_entries, request.include_files, request.include_dirs, request.metadata
    )
    timeline_event, graph_relationships, warnings = _record_restricted_file_browse(browse)
    return {"name": "Aether", "status": runtime.status(), "browse": browse, "timeline_event": timeline_event, "graph_relationships": graph_relationships, "warnings": warnings}


@app.post("/action/file/search")
def search_action_file(request: RestrictedFileSearchRequest):
    browse = search_restricted_files(request.query, request.root, request.max_results, request.metadata)
    timeline_event, graph_relationships, warnings = _record_restricted_file_browse(browse)
    return {"name": "Aether", "status": runtime.status(), "search": browse, "timeline_event": timeline_event, "graph_relationships": graph_relationships, "warnings": warnings}


@app.get("/action/file/browser/allowed-roots")
def get_action_file_browser_allowed_roots():
    return {"name": "Aether", "status": runtime.status(), "allowed_roots": list_browser_allowed_roots()}


@app.get("/action/file/browser/status")
def get_action_file_browser_status():
    return {"name": "Aether", "status": runtime.status(), "file_browser": file_browser_status()}


@app.get("/action/file/browser/list")
def list_action_file_browses(limit: int = 50):
    return {"name": "Aether", "status": runtime.status(), "browses": list_file_browses(limit)}


@app.get("/action/file/browser/{browse_id}")
def get_action_file_browse(browse_id: str):
    return {"name": "Aether", "status": runtime.status(), "browse": get_file_browse(browse_id)}


def _record_self_inspection_report(report: dict) -> tuple[dict, list[dict], list[str]]:
    runtime.working_memory.add_event(
        role="aether",
        content=f"Project self-inspection report created: {report['id']} ({report['status']}).",
        event_type="self_inspection_report_created",
        metadata={
            "report_id": report["id"], "status": report["status"],
            "files_read": report["summary"]["files_read"], "endpoint_count": report["summary"]["endpoint_count"],
            "warning_count": len(report["warnings"]),
        },
    )
    timeline_event = record_event(
        event_type="self_inspection",
        title="Project self-inspection report created",
        description=f"Aether created project self-inspection report {report['id']} with status {report['status']}.",
        importance="high" if report["status"] in {"failed", "blocked"} else "normal",
    )
    warnings = []
    graph_relationships = []
    try:
        graph_relationships.extend(
            [
                add_edge("Aether", "created_self_inspection_report", report["id"]),
                add_edge(report["id"], "inspected_project", "Aether"),
                add_edge(report["id"], "has_status", report["status"]),
            ]
        )
        for relationship in graph_relationships:
            relationship.pop("created_new", None)
    except Exception as error:
        warnings.append(f"Graph Memory integration was unavailable: {error}")
    return timeline_event, graph_relationships, warnings


@app.post("/action/self-inspection/create")
def create_action_self_inspection(request: SelfInspectionRequest):
    report = create_project_self_inspection(request.root, request.max_files_to_read, request.max_chars_per_file, request.metadata)
    timeline_event, graph_relationships, warnings = _record_self_inspection_report(report)
    return {"name": "Aether", "status": runtime.status(), "report": report, "timeline_event": timeline_event, "graph_relationships": graph_relationships, "warnings": warnings}


@app.get("/action/self-inspection/status")
def get_action_self_inspection_status():
    return {"name": "Aether", "status": runtime.status(), "self_inspection": self_inspection_status()}


@app.get("/action/self-inspection/list")
def list_action_self_inspections(limit: int = 20):
    return {"name": "Aether", "status": runtime.status(), "reports": list_self_inspection_reports(limit)}


@app.get("/action/self-inspection/{report_id}")
def get_action_self_inspection(report_id: str):
    return {"name": "Aether", "status": runtime.status(), "report": get_self_inspection_report(report_id)}


@app.post("/action/patch-proposal/create")
def create_action_patch_proposal(request: PatchProposalRequest):
    proposal = create_patch_proposal(request.target_path, request.request_text, request.proposed_change_summary, request.proposed_excerpt, request.reason, request.original_excerpt, request.create_approval_if_required, request.metadata)
    runtime.working_memory.add_event(role="aether", content=f"Patch proposal created: {proposal['target_path']}", event_type="patch_proposal_created", metadata={key: proposal.get(key) for key in ("id", "target_path", "status", "risk_level", "requires_user_approval", "approval_id")})
    return {"name": "Aether", "status": runtime.status(), "proposal": proposal}

@app.get("/action/patch-proposal/status")
def get_action_patch_proposal_status():
    return {"name": "Aether", "status": runtime.status(), "patch_proposals": patch_proposal_status()}

@app.get("/action/patch-proposal/list")
def list_action_patch_proposals(status: str | None = None, limit: int = 50):
    return {"name": "Aether", "status": runtime.status(), "proposals": list_patch_proposals(status, limit)}

@app.get("/action/patch-proposal/{proposal_id}")
def get_action_patch_proposal(proposal_id: str):
    return {"name": "Aether", "status": runtime.status(), "proposal": get_patch_proposal(proposal_id)}

@app.post("/action/patch-proposal/mark-status")
def mark_action_patch_proposal_status(request: PatchProposalStatusUpdateRequest):
    return {"name": "Aether", "status": runtime.status(), "proposal": mark_patch_proposal_status(request.proposal_id, request.status, request.reason)}

@app.post("/action/patch-review/review")
def review_action_patch_proposal(request: PatchReviewRequest):
    review = review_patch_proposal(request.proposal_id, request.decision, request.review_reason, request.reviewer, request.metadata)
    runtime.working_memory.add_event(role="aether", content=f"Patch review created: {request.decision}", event_type="patch_review_created", metadata={"review_id": review.get("id"), "proposal_id": request.proposal_id, "decision": request.decision, "status": review.get("status"), "proposal_status_after": review.get("proposal_status_after"), "risk_level": review.get("risk_level"), "approval_status": review.get("approval_status")})
    return {"name":"Aether","status":runtime.status(),"review":review}

@app.get("/action/patch-review/status")
def get_action_patch_review_status(): return {"name":"Aether","status":runtime.status(),"patch_reviews":patch_review_status()}
@app.get("/action/patch-review/list")
def list_action_patch_reviews(proposal_id: str | None = None, limit: int = 50): return {"name":"Aether","status":runtime.status(),"reviews":list_patch_reviews(proposal_id,limit)}
@app.get("/action/patch-review/{review_id}")
def get_action_patch_review(review_id: str): return {"name":"Aether","status":runtime.status(),"review":get_patch_review(review_id)}

@app.post("/action/patch-apply/apply")
def apply_action_patch(request: PatchApplyRequest):
    result=apply_patch_proposal(request.proposal_id,request.dry_run,request.metadata)
    runtime.working_memory.add_event(role="aether",content=f"Patch apply attempted: {result['status']}",event_type="patch_apply_attempted",metadata={k:result.get(k) for k in ("id","proposal_id","target_path","status","dry_run","applied","changed","risk_level")})
    return {"name":"Aether","status":runtime.status(),"apply":result}
@app.get("/action/patch-apply/status")
def get_action_patch_apply_status():return {"name":"Aether","status":runtime.status(),"patch_applies":patch_apply_status()}
@app.get("/action/patch-apply/list")
def list_action_patch_applies(proposal_id: str|None=None,limit:int=50):return {"name":"Aether","status":runtime.status(),"applies":list_patch_applies(proposal_id,limit)}
@app.get("/action/patch-apply/{apply_id}")
def get_action_patch_apply(apply_id:str):return {"name":"Aether","status":runtime.status(),"apply":get_patch_apply(apply_id)}
@app.post("/action/patch-rollback/rollback")
def rollback_action_patch(request: PatchRollbackRequest):
 r=rollback_patch_apply(request.apply_id,request.dry_run,request.metadata);runtime.working_memory.add_event(role="aether",content=f"Patch rollback attempted: {r['status']}",event_type="patch_rollback_attempted",metadata={k:r.get(k) for k in ("id","apply_id","proposal_id","target_path","status","dry_run","rolled_back","changed")});return {"name":"Aether","status":runtime.status(),"rollback":r}
@app.get("/action/patch-rollback/status")
def get_action_patch_rollback_status():return {"name":"Aether","status":runtime.status(),"patch_rollbacks":patch_rollback_status()}
@app.get("/action/patch-rollback/list")
def list_action_patch_rollbacks(apply_id:str|None=None,limit:int=50):return {"name":"Aether","status":runtime.status(),"rollbacks":list_patch_rollbacks(apply_id,limit)}
@app.get("/action/patch-rollback/{rollback_id}")
def get_action_patch_rollback(rollback_id:str):return {"name":"Aether","status":runtime.status(),"rollback":get_patch_rollback(rollback_id)}
@app.post("/action/mutation-log/record")
def record_action_mutation(request:MutationRecordRequest):return {"name":"Aether","mutation":record_mutation(request.mutation_type,request.title,request.summary,milestone=request.milestone,target_path=request.target_path,metadata=request.metadata,source="manual")}
@app.post("/action/mutation-log/milestone-completed")
def record_action_milestone(request:MilestoneCompletedRequest):return {"name":"Aether","mutation":record_milestone_completed(request.milestone,request.summary,request.metadata)}
@app.get("/action/mutation-log/status")
def get_action_mutation_status():return {"name":"Aether","mutation_log":mutation_log_status()}
@app.get("/action/mutation-log/list")
def list_action_mutations(mutation_type:str|None=None,milestone:str|None=None,target_path:str|None=None,limit:int=50):return {"name":"Aether","mutations":list_mutations(mutation_type,milestone,target_path,limit)}
@app.get("/action/mutation-log/summary")
def summarize_action_mutations(limit:int=100):return {"name":"Aether","summary":summarize_mutations(limit)}
@app.get("/action/mutation-log/{mutation_id}")
def get_action_mutation(mutation_id:str):return {"name":"Aether","mutation":get_mutation(mutation_id)}
