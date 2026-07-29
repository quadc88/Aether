from fastapi import APIRouter

from aether.interface.api_models import (
    ApprovalCreateRequest,
    ApprovalDecisionRequest,
    ApprovalDecisionBody,
    ActionValidationBody,
)

from aether.action.services.approval_service import (
    handle_action_approval_create,
    handle_action_approval_status,
    handle_list_action_approvals,
    handle_get_action_approval,
    handle_approve_action_approval,
    handle_reject_action_approval,
    handle_cancel_action_approval,
    handle_list_approvals,
    handle_get_approval,
    handle_approve_approval,
    handle_reject_approval,
    handle_cancel_approval,
    handle_validate_action,
)

approval_router = APIRouter()


@approval_router.post("/action/approval/create")
def create_action_approval(request: ApprovalCreateRequest):
    return handle_action_approval_create(
        request_text=request.request_text,
        proposed_action=request.proposed_action,
        metadata=request.metadata,
    )


@approval_router.get("/action/approval/status")
def get_action_approval_status():
    return handle_action_approval_status()


@approval_router.get("/action/approval/list")
def list_action_approvals(status: str | None = None, limit: int = 50):
    return handle_list_action_approvals(status=status, limit=limit)


@approval_router.get("/action/approval/{approval_id}")
def get_action_approval(approval_id: str):
    return handle_get_action_approval(approval_id)


@approval_router.post("/action/approval/approve")
def approve_action_approval(request: ApprovalDecisionRequest):
    return handle_approve_action_approval(request.approval_id, request.decision_reason)


@approval_router.post("/action/approval/reject")
def reject_action_approval(request: ApprovalDecisionRequest):
    return handle_reject_action_approval(request.approval_id, request.decision_reason)


@approval_router.post("/action/approval/cancel")
def cancel_action_approval(request: ApprovalDecisionRequest):
    return handle_cancel_action_approval(request.approval_id, request.decision_reason)


@approval_router.get("/approvals")
def get_approvals(status: str | None = None, limit: int = 50):
    return handle_list_approvals(status=status, limit=limit)


@approval_router.get("/approvals/{approval_id}")
def get_approval(approval_id: str):
    return handle_get_approval(approval_id)


@approval_router.post("/approvals/{approval_id}/approve")
def approve_approval_record(approval_id: str, request: ApprovalDecisionBody | None = None):
    reviewer = request.reviewer if request else None
    reason = request.reason if request else None
    return handle_approve_approval(approval_id, reviewer, reason)


@approval_router.post("/approvals/{approval_id}/reject")
def reject_approval_record(approval_id: str, request: ApprovalDecisionBody | None = None):
    reviewer = request.reviewer if request else None
    reason = request.reason if request else None
    return handle_reject_approval(approval_id, reviewer, reason)


@approval_router.post("/approvals/{approval_id}/cancel")
def cancel_approval_record(approval_id: str, request: ApprovalDecisionBody | None = None):
    reviewer = request.reviewer if request else None
    reason = request.reason if request else None
    return handle_cancel_approval(approval_id, reviewer, reason)


@approval_router.post("/approvals/{approval_id}/validate-action")
def validate_action_endpoint(approval_id: str, request: ActionValidationBody | None = None):
    requested_action = request.requested_action if request else None
    context = request.context if request else None
    return handle_validate_action(approval_id, requested_action, context)
