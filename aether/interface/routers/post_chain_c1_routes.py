"""Post-chain C1 router extracted in 82AN Build.

All 24 C1 post-chain routes moved from aether/interface/api_server.py.
route -> router -> service -> response boundary preserved.
"""

from fastapi import APIRouter

from aether.interface.api_models import (
    ApprovedDryRunExecuteRequest,
    ApprovedDryRunGateOpenRequest,
    DryRunReviewGateOpenRequest,
    DryRunReviewSubmitRequest,
    PostApplyVerificationGateOpenRequest,
    PostApplyVerificationSubmitRequest,
    RealApplyApprovalGateOpenRequest,
    RealApplyFinalDecisionRequest,
)

from aether.action.services.approved_dry_run_gate_service import handle_open_approved_dry_run_gate,handle_execute_approved_dry_run,handle_get_approved_dry_run_gate_status,handle_list_approved_dry_run_gate_records,handle_summarize_approved_dry_run_gate,handle_get_approved_dry_run_gate_record
from aether.action.services.dry_run_review_gate_service import handle_open_dry_run_review_gate,handle_submit_dry_run_review,handle_get_dry_run_review_gate_status,handle_list_dry_run_review_gate_records,handle_summarize_dry_run_review_gate,handle_get_dry_run_review_gate_record
from aether.action.services.real_apply_approval_gate_service import handle_open_real_apply_approval_gate,handle_submit_real_apply_final_decision,handle_get_real_apply_approval_gate_status,handle_list_real_apply_approval_gate_records,handle_summarize_real_apply_approval_gate,handle_get_real_apply_approval_gate_record
from aether.action.services.post_apply_verification_gate_service import handle_open_post_apply_verification_gate,handle_submit_post_apply_verification,handle_get_post_apply_verification_gate_status,handle_list_post_apply_verification_gate_records,handle_summarize_post_apply_verification_gate,handle_get_post_apply_verification_gate_record


post_chain_c1_router = APIRouter()

@post_chain_c1_router.post("/action/approved-dry-run-gate/open")
def open_approved_dry_run_gate_action(request:ApprovedDryRunGateOpenRequest):return handle_open_approved_dry_run_gate(request.source_type,request.source_id,request.metadata)
@post_chain_c1_router.post("/action/approved-dry-run-gate/execute")
def execute_approved_dry_run_gate_action(request:ApprovedDryRunExecuteRequest):return handle_execute_approved_dry_run(request.gate_record_id,request.create_approval_if_required,request.metadata)
@post_chain_c1_router.get("/action/approved-dry-run-gate/status")
def get_approved_dry_run_gate_status_action():return handle_get_approved_dry_run_gate_status()
@post_chain_c1_router.get("/action/approved-dry-run-gate/list")
def list_approved_dry_run_gate_action(status:str|None=None,proposal_id:str|None=None,limit:int=50):return handle_list_approved_dry_run_gate_records(status,proposal_id,limit)
@post_chain_c1_router.get("/action/approved-dry-run-gate/{record_id}/summary")
def summarize_approved_dry_run_gate_action(record_id:str):return handle_summarize_approved_dry_run_gate(record_id)
@post_chain_c1_router.get("/action/approved-dry-run-gate/{record_id}")
def get_approved_dry_run_gate_action(record_id:str):return handle_get_approved_dry_run_gate_record(record_id)
@post_chain_c1_router.post("/action/dry-run-review-gate/open")
def open_dry_run_review_gate_action(request:DryRunReviewGateOpenRequest):return handle_open_dry_run_review_gate(request.source_type,request.source_id,request.metadata)
@post_chain_c1_router.post("/action/dry-run-review-gate/submit")
def submit_dry_run_review_action(request:DryRunReviewSubmitRequest):return handle_submit_dry_run_review(request.review_gate_record_id,request.decision,request.comment,request.reviewer,request.metadata)
@post_chain_c1_router.get("/action/dry-run-review-gate/status")
def get_dry_run_review_gate_status_action():return handle_get_dry_run_review_gate_status()
@post_chain_c1_router.get("/action/dry-run-review-gate/list")
def list_dry_run_review_gate_action(status:str|None=None,proposal_id:str|None=None,limit:int=50):return handle_list_dry_run_review_gate_records(status,proposal_id,limit)
@post_chain_c1_router.get("/action/dry-run-review-gate/{record_id}/summary")
def summarize_dry_run_review_gate_action(record_id:str):return handle_summarize_dry_run_review_gate(record_id)
@post_chain_c1_router.get("/action/dry-run-review-gate/{record_id}")
def get_dry_run_review_gate_action(record_id:str):return handle_get_dry_run_review_gate_record(record_id)
@post_chain_c1_router.post("/action/real-apply-approval-gate/open")
def open_real_apply_approval_gate_action(request:RealApplyApprovalGateOpenRequest):return handle_open_real_apply_approval_gate(request.source_type,request.source_id,request.create_approval_item,request.metadata)
@post_chain_c1_router.post("/action/real-apply-approval-gate/submit")
def submit_real_apply_final_decision_action(request:RealApplyFinalDecisionRequest):return handle_submit_real_apply_final_decision(request.gate_record_id,request.decision,request.comment,request.reviewer,request.metadata)
@post_chain_c1_router.get("/action/real-apply-approval-gate/status")
def get_real_apply_approval_gate_status_action():return handle_get_real_apply_approval_gate_status()
@post_chain_c1_router.get("/action/real-apply-approval-gate/list")
def list_real_apply_approval_gate_action(status:str|None=None,proposal_id:str|None=None,limit:int=50):return handle_list_real_apply_approval_gate_records(status,proposal_id,limit)
@post_chain_c1_router.get("/action/real-apply-approval-gate/{record_id}/summary")
def summarize_real_apply_approval_gate_action(record_id:str):return handle_summarize_real_apply_approval_gate(record_id)
@post_chain_c1_router.get("/action/real-apply-approval-gate/{record_id}")
def get_real_apply_approval_gate_action(record_id:str):return handle_get_real_apply_approval_gate_record(record_id)
@post_chain_c1_router.post("/action/post-apply-verification-gate/open")
def open_post_apply_verification_gate_action(request:PostApplyVerificationGateOpenRequest):return handle_open_post_apply_verification_gate(request.source_type,request.source_id,request.metadata)
@post_chain_c1_router.post("/action/post-apply-verification-gate/submit")
def submit_post_apply_verification_action(request:PostApplyVerificationSubmitRequest):return handle_submit_post_apply_verification(request.verification_record_id,request.decision,request.comment,request.verifier,request.metadata)
@post_chain_c1_router.get("/action/post-apply-verification-gate/status")
def get_post_apply_verification_gate_status_action():return handle_get_post_apply_verification_gate_status()
@post_chain_c1_router.get("/action/post-apply-verification-gate/list")
def list_post_apply_verification_gate_action(status:str|None=None,proposal_id:str|None=None,limit:int=50):return handle_list_post_apply_verification_gate_records(status,proposal_id,limit)
@post_chain_c1_router.get("/action/post-apply-verification-gate/{record_id}/summary")
def summarize_post_apply_verification_gate_action(record_id:str):return handle_summarize_post_apply_verification_gate(record_id)
@post_chain_c1_router.get("/action/post-apply-verification-gate/{record_id}")
def get_post_apply_verification_gate_action(record_id:str):return handle_get_post_apply_verification_gate_record(record_id)
