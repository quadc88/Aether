from fastapi import APIRouter

from aether.interface.api_models import (
    EpisodeWriteRequest,
    GoalRequest,
    GraphEdgeRequest,
    GraphNodeRequest,
    GraphSearchRequest,
    MilestoneRequest,
    SemanticSearchRequest,
    TimelineSearchRequest,
)
from aether.action.services.memory_service import (
    handle_clear_working_memory as _handle_clear_wm,
    handle_create_graph_edge as _handle_create_graph_edge,
    handle_create_graph_node as _handle_create_graph_node,
    handle_get_working_memory as _handle_get_wm,
    handle_graph_status as _handle_graph_status,
    handle_index_semantic_memory as _handle_index_semantic,
    handle_latest_episodic_memory as _handle_latest_episodic,
    handle_latest_timeline_event as _handle_latest_timeline,
    handle_list_episodic_memory as _handle_list_episodic,
    handle_list_graph_edges as _handle_list_graph_edges,
    handle_list_graph_nodes as _handle_list_graph_nodes,
    handle_list_timeline_events as _handle_list_timeline,
    handle_search_graph as _handle_search_graph,
    handle_search_semantic_memory as _handle_search_semantic,
    handle_search_timeline as _handle_search_timeline,
    handle_seed_graph_memory as _handle_seed_graph,
    handle_semantic_memory_status as _handle_semantic_status,
    handle_set_working_goal as _handle_set_wm_goal,
    handle_set_working_milestone as _handle_set_wm_milestone,
    handle_timeline_status as _handle_timeline_status,
    handle_write_episodic_memory as _handle_write_episodic,
)


memory_router = APIRouter()


@memory_router.get("/memory/working")
def get_working_memory():
    return _handle_get_wm()


@memory_router.post("/memory/working/goal")
def set_working_goal(request: GoalRequest):
    return _handle_set_wm_goal(goal=request.goal)


@memory_router.post("/memory/working/milestone")
def set_working_milestone(request: MilestoneRequest):
    return _handle_set_wm_milestone(milestone=request.milestone)


@memory_router.post("/memory/working/clear")
def clear_working_memory():
    return _handle_clear_wm()


@memory_router.post("/memory/episodic/write")
def write_episodic_memory(request: EpisodeWriteRequest):
    return _handle_write_episodic(
        title=request.title,
        summary=request.summary,
        details=request.details,
        importance=request.importance,
        tags=request.tags,
        related_files=request.related_files,
    )


@memory_router.get("/memory/episodic/list")
def list_episodic_memory(limit: int = 20):
    return _handle_list_episodic(limit=limit)


@memory_router.get("/memory/episodic/latest")
def get_latest_episodic_memory():
    return _handle_latest_episodic()


@memory_router.post("/memory/semantic/index")
def index_semantic_memory():
    return _handle_index_semantic()


@memory_router.get("/memory/semantic/status")
def get_semantic_memory_status():
    return _handle_semantic_status()


@memory_router.post("/memory/semantic/search")
def search_memory(request: SemanticSearchRequest):
    return _handle_search_semantic(query=request.query, limit=request.limit)


@memory_router.get("/memory/timeline/status")
def get_timeline_status():
    return _handle_timeline_status()


@memory_router.get("/memory/timeline/list")
def list_timeline_events(limit: int = 20):
    return _handle_list_timeline(limit=limit)


@memory_router.get("/memory/timeline/latest")
def get_latest_timeline_event():
    return _handle_latest_timeline()


@memory_router.post("/memory/timeline/search")
def search_timeline_memory(request: TimelineSearchRequest):
    return _handle_search_timeline(query=request.query, limit=request.limit)


@memory_router.get("/memory/graph/status")
def get_graph_memory_status():
    return _handle_graph_status()


@memory_router.post("/memory/graph/node")
def create_graph_node(request: GraphNodeRequest):
    return _handle_create_graph_node(
        label=request.label,
        node_type=request.node_type,
        properties=request.properties,
    )


@memory_router.post("/memory/graph/edge")
def create_graph_edge(request: GraphEdgeRequest):
    return _handle_create_graph_edge(
        source=request.source,
        relation=request.relation,
        target=request.target,
        properties=request.properties,
    )


@memory_router.get("/memory/graph/nodes")
def get_graph_nodes(limit: int = 50):
    return _handle_list_graph_nodes(limit=limit)


@memory_router.get("/memory/graph/edges")
def get_graph_edges(limit: int = 50):
    return _handle_list_graph_edges(limit=limit)


@memory_router.post("/memory/graph/search")
def search_graph_memory(request: GraphSearchRequest):
    return _handle_search_graph(query=request.query, limit=request.limit)


@memory_router.post("/memory/graph/seed")
def seed_graph_memory():
    return _handle_seed_graph()
