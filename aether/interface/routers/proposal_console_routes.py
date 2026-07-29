from fastapi import APIRouter

from aether.interface.api_models import (
    ProposalReviewConsoleOpenRequest,
    ProposalReviewSubmitRequest,
    ProposalRevisionConsoleOpenRequest,
    ProposalRevisionCreateRequest,
    RevisedProposalReviewOpenRequest,
    RevisedProposalReviewSubmitRequest,
)

from aether.action.services.proposal_console_service import (
    handle_open_proposal_review_console,
    handle_submit_proposal_review,
    handle_proposal_review_console_status,
    handle_list_proposal_review_console,
    handle_summarize_proposal_review_console,
    handle_get_proposal_review_console,
    handle_open_proposal_revision_console,
    handle_create_proposal_revision,
    handle_proposal_revision_console_status,
    handle_list_proposal_revision_console,
    handle_summarize_proposal_revision_console,
    handle_get_proposal_revision_console,
    handle_open_revised_proposal_review,
    handle_submit_revised_proposal_review,
    handle_revised_proposal_review_status,
    handle_list_revised_proposal_review,
    handle_summarize_revised_proposal_review,
    handle_get_revised_proposal_review,
)

proposal_console_router = APIRouter()


@proposal_console_router.post("/action/proposal-review-console/open")
def open_proposal_review_console_action(request: ProposalReviewConsoleOpenRequest):
    return handle_open_proposal_review_console(
        request.source_type, request.source_id, request.metadata,
    )


@proposal_console_router.post("/action/proposal-review-console/submit")
def submit_proposal_review_action(request: ProposalReviewSubmitRequest):
    return handle_submit_proposal_review(
        request.console_record_id, request.decision, request.comment,
        request.reviewer, request.create_approval_if_required,
        request.metadata,
    )


@proposal_console_router.get("/action/proposal-review-console/status")
def get_proposal_review_console_status_action():
    return handle_proposal_review_console_status()


@proposal_console_router.get("/action/proposal-review-console/list")
def list_proposal_review_console_action(
    status: str | None = None,
    proposal_id: str | None = None,
    limit: int = 50,
):
    return handle_list_proposal_review_console(status, proposal_id, limit)


@proposal_console_router.get("/action/proposal-review-console/{record_id}/summary")
def summarize_proposal_review_console_action(record_id: str):
    return handle_summarize_proposal_review_console(record_id)


@proposal_console_router.get("/action/proposal-review-console/{record_id}")
def get_proposal_review_console_action(record_id: str):
    return handle_get_proposal_review_console(record_id)


@proposal_console_router.post("/action/proposal-revision-console/open")
def open_proposal_revision_console_action(request: ProposalRevisionConsoleOpenRequest):
    return handle_open_proposal_revision_console(
        request.source_type, request.source_id, request.metadata,
    )


@proposal_console_router.post("/action/proposal-revision-console/create-revision")
def create_proposal_revision_action(request: ProposalRevisionCreateRequest):
    return handle_create_proposal_revision(
        request.revision_record_id, request.revised_proposed_excerpt,
        request.revised_change_summary, request.human_revision_note,
        request.create_approval_if_required, request.metadata,
    )


@proposal_console_router.get("/action/proposal-revision-console/status")
def get_proposal_revision_console_status_action():
    return handle_proposal_revision_console_status()


@proposal_console_router.get("/action/proposal-revision-console/list")
def list_proposal_revision_console_action(
    status: str | None = None,
    original_proposal_id: str | None = None,
    limit: int = 50,
):
    return handle_list_proposal_revision_console(status, original_proposal_id, limit)


@proposal_console_router.get("/action/proposal-revision-console/{record_id}/summary")
def summarize_proposal_revision_console_action(record_id: str):
    return handle_summarize_proposal_revision_console(record_id)


@proposal_console_router.get("/action/proposal-revision-console/{record_id}")
def get_proposal_revision_console_action(record_id: str):
    return handle_get_proposal_revision_console(record_id)


@proposal_console_router.post("/action/revised-proposal-review/open")
def open_revised_proposal_review_action(request: RevisedProposalReviewOpenRequest):
    return handle_open_revised_proposal_review(
        request.proposal_revision_console_id, request.metadata,
    )


@proposal_console_router.post("/action/revised-proposal-review/submit")
def submit_revised_proposal_review_action(request: RevisedProposalReviewSubmitRequest):
    return handle_submit_revised_proposal_review(
        request.review_loop_record_id, request.decision, request.comment,
        request.reviewer, request.create_approval_if_required,
        request.metadata,
    )


@proposal_console_router.get("/action/revised-proposal-review/status")
def get_revised_proposal_review_status_action():
    return handle_revised_proposal_review_status()


@proposal_console_router.get("/action/revised-proposal-review/list")
def list_revised_proposal_review_action(
    status: str | None = None,
    revised_proposal_id: str | None = None,
    limit: int = 50,
):
    return handle_list_revised_proposal_review(status, revised_proposal_id, limit)


@proposal_console_router.get("/action/revised-proposal-review/{record_id}/summary")
def summarize_revised_proposal_review_action(record_id: str):
    return handle_summarize_revised_proposal_review(record_id)


@proposal_console_router.get("/action/revised-proposal-review/{record_id}")
def get_revised_proposal_review_action(record_id: str):
    return handle_get_revised_proposal_review(record_id)
