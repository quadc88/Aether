"""File and Self-Inspection Service — Milestone 82D.

Moves file read, file browse, and self-inspection endpoint orchestration from
api_server.py into this service module.

Behavior-preserving refactor: no endpoint path, response shape, or safety changes.
"""

from aether.core.runtime import runtime
from aether.memory.timeline.recorder import record_event
from aether.memory.graph.store import add_edge

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
from aether.action.services.tool_execution_service import (
    record_restricted_file_access,
    record_self_inspection_report,
)


# --------------------------------------------------------------------------- #
# Helper (moved from api_server.py)
# --------------------------------------------------------------------------- #


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


# --------------------------------------------------------------------------- #
# File Read handlers
# --------------------------------------------------------------------------- #


def handle_file_read(path: str, max_chars: int, metadata: dict) -> dict:
    access = read_restricted_file(path, max_chars, metadata)
    timeline_event, graph_relationships, warnings = record_restricted_file_access(access)
    return {"name": "Aether", "status": runtime.status(), "access": access, "timeline_event": timeline_event, "graph_relationships": graph_relationships, "warnings": warnings}


def handle_file_allowed_roots() -> dict:
    return {"name": "Aether", "status": runtime.status(), "allowed_roots": list_allowed_roots()}


def handle_file_access_status() -> dict:
    return {"name": "Aether", "status": runtime.status(), "file_access": file_access_status()}


def handle_list_file_accesses(limit: int = 50) -> dict:
    return {"name": "Aether", "status": runtime.status(), "accesses": list_file_accesses(limit)}


def handle_get_file_access(access_id: str) -> dict:
    return {"name": "Aether", "status": runtime.status(), "access": get_file_access(access_id)}


# --------------------------------------------------------------------------- #
# File Browse handlers
# --------------------------------------------------------------------------- #


def handle_file_browse(path: str, max_depth: int, max_entries: int, include_files: bool, include_dirs: bool, metadata: dict) -> dict:
    browse = browse_restricted_path(path, max_depth, max_entries, include_files, include_dirs, metadata)
    timeline_event, graph_relationships, warnings = _record_restricted_file_browse(browse)
    return {"name": "Aether", "status": runtime.status(), "browse": browse, "timeline_event": timeline_event, "graph_relationships": graph_relationships, "warnings": warnings}


def handle_file_search(query: str, root: str, max_results: int, metadata: dict) -> dict:
    browse = search_restricted_files(query, root, max_results, metadata)
    timeline_event, graph_relationships, warnings = _record_restricted_file_browse(browse)
    return {"name": "Aether", "status": runtime.status(), "search": browse, "timeline_event": timeline_event, "graph_relationships": graph_relationships, "warnings": warnings}


def handle_file_browser_allowed_roots() -> dict:
    return {"name": "Aether", "status": runtime.status(), "allowed_roots": list_browser_allowed_roots()}


def handle_file_browser_status() -> dict:
    return {"name": "Aether", "status": runtime.status(), "file_browser": file_browser_status()}


def handle_list_file_browses(limit: int = 50) -> dict:
    return {"name": "Aether", "status": runtime.status(), "browses": list_file_browses(limit)}


def handle_get_file_browse(browse_id: str) -> dict:
    return {"name": "Aether", "status": runtime.status(), "browse": get_file_browse(browse_id)}


# --------------------------------------------------------------------------- #
# Self-Inspection handlers
# --------------------------------------------------------------------------- #


def handle_self_inspection_create(root: str, max_files_to_read: int, max_chars_per_file: int, metadata: dict) -> dict:
    report = create_project_self_inspection(root, max_files_to_read, max_chars_per_file, metadata)
    timeline_event, graph_relationships, warnings = record_self_inspection_report(report)
    return {"name": "Aether", "status": runtime.status(), "report": report, "timeline_event": timeline_event, "graph_relationships": graph_relationships, "warnings": warnings}


def handle_self_inspection_status() -> dict:
    return {"name": "Aether", "status": runtime.status(), "self_inspection": self_inspection_status()}


def handle_list_self_inspections(limit: int = 20) -> dict:
    return {"name": "Aether", "status": runtime.status(), "reports": list_self_inspection_reports(limit)}


def handle_get_self_inspection(report_id: str) -> dict:
    return {"name": "Aether", "status": runtime.status(), "report": get_self_inspection_report(report_id)}
