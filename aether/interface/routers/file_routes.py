from fastapi import APIRouter

from aether.interface.api_models import (
    RestrictedFileReadRequest,
    RestrictedFileBrowseRequest,
    RestrictedFileSearchRequest,
    SelfInspectionRequest,
)

from aether.action.services.file_service import (
    handle_file_read,
    handle_file_allowed_roots,
    handle_file_access_status,
    handle_list_file_accesses,
    handle_get_file_access,
    handle_file_browse,
    handle_file_search,
    handle_file_browser_allowed_roots,
    handle_file_browser_status,
    handle_list_file_browses,
    handle_get_file_browse,
    handle_self_inspection_create,
    handle_self_inspection_status,
    handle_list_self_inspections,
    handle_get_self_inspection,
)

file_router = APIRouter()


@file_router.post("/action/file/read")
def read_action_file(request: RestrictedFileReadRequest):
    return handle_file_read(request.path, request.max_chars, request.metadata)


@file_router.get("/action/file/allowed-roots")
def get_action_file_allowed_roots():
    return handle_file_allowed_roots()


@file_router.get("/action/file/access/status")
def get_action_file_access_status():
    return handle_file_access_status()


@file_router.get("/action/file/access/list")
def list_action_file_accesses(limit: int = 50):
    return handle_list_file_accesses(limit)


@file_router.get("/action/file/access/{access_id}")
def get_action_file_access(access_id: str):
    return handle_get_file_access(access_id)


@file_router.post("/action/file/browse")
def browse_action_file(request: RestrictedFileBrowseRequest):
    return handle_file_browse(
        request.path, request.max_depth, request.max_entries,
        request.include_files, request.include_dirs, request.metadata,
    )


@file_router.post("/action/file/search")
def search_action_file(request: RestrictedFileSearchRequest):
    return handle_file_search(
        request.query, request.root, request.max_results, request.metadata,
    )


@file_router.get("/action/file/browser/allowed-roots")
def get_action_file_browser_allowed_roots():
    return handle_file_browser_allowed_roots()


@file_router.get("/action/file/browser/status")
def get_action_file_browser_status():
    return handle_file_browser_status()


@file_router.get("/action/file/browser/list")
def list_action_file_browses(limit: int = 50):
    return handle_list_file_browses(limit)


@file_router.get("/action/file/browser/{browse_id}")
def get_action_file_browse(browse_id: str):
    return handle_get_file_browse(browse_id)


@file_router.post("/action/self-inspection/create")
def create_action_self_inspection(request: SelfInspectionRequest):
    return handle_self_inspection_create(
        request.root, request.max_files_to_read,
        request.max_chars_per_file, request.metadata,
    )


@file_router.get("/action/self-inspection/status")
def get_action_self_inspection_status():
    return handle_self_inspection_status()


@file_router.get("/action/self-inspection/list")
def list_action_self_inspections(limit: int = 20):
    return handle_list_self_inspections(limit)


@file_router.get("/action/self-inspection/{report_id}")
def get_action_self_inspection(report_id: str):
    return handle_get_self_inspection(report_id)
