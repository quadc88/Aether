from fastapi import APIRouter

from aether.interface.api_models import (
    PatchApplyRequest,
    PatchProposalRequest,
    PatchProposalStatusUpdateRequest,
    PatchReviewRequest,
    PatchRollbackRequest,
)

from aether.action.services.patch_service import (
    handle_patch_proposal_create,
    handle_patch_proposal_status,
    handle_list_patch_proposals,
    handle_get_patch_proposal,
    handle_mark_patch_proposal_status,
    handle_patch_review,
    handle_patch_review_status,
    handle_list_patch_reviews,
    handle_get_patch_review,
    handle_patch_apply,
    handle_patch_apply_status,
    handle_list_patch_applies,
    handle_get_patch_apply,
    handle_patch_rollback,
    handle_patch_rollback_status,
    handle_list_patch_rollbacks,
    handle_get_patch_rollback,
)

patch_router = APIRouter()


@patch_router.post("/action/patch-proposal/create")
def create_action_patch_proposal(request: PatchProposalRequest):
    return handle_patch_proposal_create(request.target_path, request.request_text, request.proposed_change_summary, request.proposed_excerpt, request.reason, request.original_excerpt, request.create_approval_if_required, request.metadata)


@patch_router.get("/action/patch-proposal/status")
def get_action_patch_proposal_status():
    return handle_patch_proposal_status()


@patch_router.get("/action/patch-proposal/list")
def list_action_patch_proposals(status: str | None = None, limit: int = 50):
    return handle_list_patch_proposals(status, limit)


@patch_router.get("/action/patch-proposal/{proposal_id}")
def get_action_patch_proposal(proposal_id: str):
    return handle_get_patch_proposal(proposal_id)


@patch_router.post("/action/patch-proposal/mark-status")
def mark_action_patch_proposal_status(request: PatchProposalStatusUpdateRequest):
    return handle_mark_patch_proposal_status(request.proposal_id, request.status, request.reason)


@patch_router.post("/action/patch-review/review")
def review_action_patch_proposal(request: PatchReviewRequest):
    return handle_patch_review(request.proposal_id, request.decision, request.review_reason, request.reviewer, request.metadata)


@patch_router.get("/action/patch-review/status")
def get_action_patch_review_status(): return handle_patch_review_status()
@patch_router.get("/action/patch-review/list")
def list_action_patch_reviews(proposal_id: str | None = None, limit: int = 50): return handle_list_patch_reviews(proposal_id, limit)
@patch_router.get("/action/patch-review/{review_id}")
def get_action_patch_review(review_id: str): return handle_get_patch_review(review_id)


@patch_router.post("/action/patch-apply/apply")
def apply_action_patch(request: PatchApplyRequest):
    return handle_patch_apply(request.proposal_id, request.dry_run, request.metadata)
@patch_router.get("/action/patch-apply/status")
def get_action_patch_apply_status():return handle_patch_apply_status()
@patch_router.get("/action/patch-apply/list")
def list_action_patch_applies(proposal_id: str|None=None,limit:int=50):return handle_list_patch_applies(proposal_id,limit)
@patch_router.get("/action/patch-apply/{apply_id}")
def get_action_patch_apply(apply_id:str):return handle_get_patch_apply(apply_id)
@patch_router.post("/action/patch-rollback/rollback")
def rollback_action_patch(request: PatchRollbackRequest):
    return handle_patch_rollback(request.apply_id, request.dry_run, request.metadata)
@patch_router.get("/action/patch-rollback/status")
def get_action_patch_rollback_status():return handle_patch_rollback_status()
@patch_router.get("/action/patch-rollback/list")
def list_action_patch_rollbacks(apply_id:str|None=None,limit:int=50):return handle_list_patch_rollbacks(apply_id,limit)
@patch_router.get("/action/patch-rollback/{rollback_id}")
def get_action_patch_rollback(rollback_id:str):return handle_get_patch_rollback(rollback_id)
