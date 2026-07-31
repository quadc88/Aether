"""Self-Modification router for Aether thin interface.

Extracted from aether/interface/api_server.py in milestone 82AT.
Contains 9 direct-action pass-through routes for the self-modification family.
"""
from fastapi import APIRouter

from aether.interface.api_models import (
    SelfModificationActionRequest,
    SelfModificationCreateRequest,
    SelfModificationReviewRequest,
)
from aether.action.self_modification_cycle import (
    create_self_modification_session,
    review_self_modification_session,
    dry_run_self_modification_session,
    apply_self_modification_session,
    rollback_self_modification_session,
    self_modification_status,
    list_self_modification_sessions,
    get_self_modification_session,
    summarize_self_modification_session,
)

self_modification_router = APIRouter()


@self_modification_router.post("/action/self-modification/create")
def create_self_modification(request: SelfModificationCreateRequest):
    return {
        "name": "Aether",
        "session": create_self_modification_session(
            request.goal,
            request.target_path,
            request.proposed_change_summary,
            request.proposed_excerpt,
            request.reason,
            request.original_excerpt,
            request.create_approval_if_required,
            request.metadata,
        ),
    }


@self_modification_router.post("/action/self-modification/review")
def review_self_modification(request: SelfModificationReviewRequest):
    return {
        "name": "Aether",
        "session": review_self_modification_session(
            request.session_id,
            request.decision,
            request.review_reason,
            request.reviewer,
            request.metadata,
        ),
    }


@self_modification_router.post("/action/self-modification/dry-run")
def dry_run_self_modification(request: SelfModificationActionRequest):
    return {
        "name": "Aether",
        "session": dry_run_self_modification_session(
            request.session_id,
            request.metadata,
        ),
    }


@self_modification_router.post("/action/self-modification/apply")
def apply_self_modification(request: SelfModificationActionRequest):
    return {
        "name": "Aether",
        "session": apply_self_modification_session(
            request.session_id,
            request.metadata,
        ),
    }


@self_modification_router.post("/action/self-modification/rollback")
def rollback_self_modification(request: SelfModificationActionRequest):
    return {
        "name": "Aether",
        "session": rollback_self_modification_session(
            request.session_id,
            request.metadata,
        ),
    }


@self_modification_router.get("/action/self-modification/status")
def get_self_modification_status():
    return {"name": "Aether", "self_modification": self_modification_status()}


@self_modification_router.get("/action/self-modification/list")
def list_self_modification(
    status: str | None = None,
    target_path: str | None = None,
    limit: int = 50,
):
    return {"name": "Aether", "sessions": list_self_modification_sessions(status, target_path, limit)}


@self_modification_router.get("/action/self-modification/{session_id}/summary")
def summarize_self_modification(session_id: str):
    return {"name": "Aether", "summary": summarize_self_modification_session(session_id)}


@self_modification_router.get("/action/self-modification/{session_id}")
def get_self_modification(session_id: str):
    return {"name": "Aether", "session": get_self_modification_session(session_id)}
