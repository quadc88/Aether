from fastapi import APIRouter

from aether.interface.api_models import (
    CodeReviewCreateRequest,
    ReviewBridgeCreateRequest,
)

from aether.action.services.code_review_service import (
    handle_code_review_create,
    handle_code_review_status,
    handle_list_code_reviews,
    handle_summarize_code_review,
    handle_get_code_review,
    handle_create_review_bridge,
    handle_review_bridge_status,
    handle_list_review_bridges,
    handle_summarize_review_bridge,
    handle_get_review_bridge,
)

code_review_router = APIRouter()


@code_review_router.post("/action/code-review/create")
def create_code_review_action(request: CodeReviewCreateRequest):
    return handle_code_review_create(
        request.scope, request.target_paths, request.max_files,
        request.max_chars_per_file, request.include_tests,
        request.metadata,
    )


@code_review_router.get("/action/code-review/status")
def get_code_review_status_action():
    return handle_code_review_status()


@code_review_router.get("/action/code-review/list")
def list_code_review_action(status: str | None = None, limit: int = 50):
    return handle_list_code_reviews(status, limit)


@code_review_router.get("/action/code-review/{report_id}/summary")
def summarize_code_review_action(report_id: str):
    return handle_summarize_code_review(report_id)


@code_review_router.get("/action/code-review/{report_id}")
def get_code_review_action(report_id: str):
    return handle_get_code_review(report_id)


@code_review_router.post("/action/review-bridge/create")
def create_review_bridge_action(request: ReviewBridgeCreateRequest):
    return handle_create_review_bridge(
        request.report_id, request.finding_id,
        request.proposed_excerpt, request.original_excerpt,
        request.proposed_change_summary, request.reason,
        request.create_approval_if_required, request.metadata,
    )


@code_review_router.get("/action/review-bridge/status")
def get_review_bridge_status_action():
    return handle_review_bridge_status()


@code_review_router.get("/action/review-bridge/list")
def list_review_bridge_action(
    status: str | None = None,
    review_report_id: str | None = None,
    limit: int = 50,
):
    return handle_list_review_bridges(status, review_report_id, limit)


@code_review_router.get("/action/review-bridge/{record_id}/summary")
def summarize_review_bridge_action(record_id: str):
    return handle_summarize_review_bridge(record_id)


@code_review_router.get("/action/review-bridge/{record_id}")
def get_review_bridge_action(record_id: str):
    return handle_get_review_bridge(record_id)
