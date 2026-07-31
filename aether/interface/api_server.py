from fastapi import FastAPI
from aether.interface.api_models import (
    ActionValidationBody,
    ApprovalCreateRequest,
    ApprovalDecisionBody,
    ApprovalDecisionRequest,
    ApprovalListRequest,
    ApprovedDryRunExecuteRequest,
    ApprovedDryRunGateOpenRequest,
    ChangelogExportRequest,
    ChatRequest,
    ChatResponse,
    CodeReviewCreateRequest,
    DryRunDecisionBody,
    DryRunReviewGateOpenRequest,
    DryRunReviewSubmitRequest,
    FinalRealApplyExecuteRequest,
    FinalRealApplyExecutorListRequest,
    FinalRealApplyExecutorOpenRequest,
    GuidedBridgeSelectionLaunchRequest,
    GuidedBridgeSelectionLauncherListRequest,
    GuidedProposalDecisionLauncherListRequest,
    GuidedProposalDecisionSubmitRequest,
    GuidedProposalReviewLauncherListRequest,
    GuidedProposalReviewOpenRequest,
    GuidedRepairIntakeDecisionRequest,
    GuidedRepairIntakeIndexExportRequest,
    GuidedRepairIntakeListRequest,
    GuidedRepairIntakeOpenRequest,
    GuidedRepairIntakeReportExportRequest,
    GuidedRepairPlanLaunchRequest,
    GuidedRepairPlanLauncherListRequest,
    IdentityIntegrityStatusResponse,
    InitializeIdentityGuardResponse,
    MilestoneCompletedRequest,
    MilestoneReportExportRequest,
    MutationRecordRequest,
    PostApplyVerificationGateListRequest,
    PostApplyVerificationGateOpenRequest,
    PostApplyVerificationSubmitRequest,
    PrivateGuidedRepairIntakeExportRequest,
    PrivateRepairCycleExportRequest,
    PrivateRepairGuidanceExportRequest,
    PrivateRepairLearningExportRequest,
    PrivateRepairWorkflowExportRequest,
    ProposalReviewConsoleListRequest,
    ProposalReviewConsoleOpenRequest,
    ProposalReviewSubmitRequest,
    ProposalRevisionConsoleListRequest,
    ProposalRevisionConsoleOpenRequest,
    ProposalRevisionCreateRequest,
    RealApplyApprovalGateListRequest,
    RealApplyApprovalGateOpenRequest,
    RealApplyFinalDecisionRequest,
    RepairBridgeSelectionCreateRequest,
    RepairBridgeSelectionListRequest,
    RepairCycleCompletionCreateRequest,
    RepairCycleIndexExportRequest,
    RepairCycleReportExportRequest,
    RepairGuidanceCreateRequest,
    RepairGuidanceIndexExportRequest,
    RepairGuidanceReportExportRequest,
    RepairLearningCreateRequest,
    RepairLearningIndexExportRequest,
    RepairLearningListRequest,
    RepairLearningReportExportRequest,
    RepairPlanCreateRequest,
    RepairWorkflowExportRequest,
    RepairWorkflowIndexExportRequest,
    RepairWorkflowListRequest,
    RepairWorkflowTraceRequest,
    RestrictedFileAccessListRequest,
    RestrictedFileBrowseListRequest,
    RestrictedFileBrowseRequest,
    RestrictedFileReadRequest,
    RestrictedFileSearchRequest,
    ReviewBridgeCreateRequest,
    RevisedProposalReviewLoopListRequest,
    RevisedProposalReviewOpenRequest,
    RevisedProposalReviewSubmitRequest,
    SelfInspectionListRequest,
    SelfInspectionRequest,
    SelfModificationActionRequest,
    SelfModificationCreateRequest,
    SelfModificationReviewRequest,
    ToolExecutionListRequest,
    ToolPlanListRequest,
    VerificationRequest,
    VerifyIdentityIntegrityResponse,
)
from aether.identity.loader import identity_preview
from aether.identity.guard import (
    initialize_identity_guard,
    verify_identity_integrity,
    identity_guard_status,
)
from aether.time.clock import time_state
from aether.memory.timeline.recorder import record_event, search_events
from aether.core.runtime import runtime
from aether.memory.graph.store import add_edge
from aether.verification.risk import classify_risk
from aether.action.services.runtime_lifecycle_service import (
    handle_awaken,
)
from aether.action.self_modification_cycle import create_self_modification_session, review_self_modification_session, dry_run_self_modification_session, apply_self_modification_session, rollback_self_modification_session, self_modification_status, list_self_modification_sessions, get_self_modification_session, summarize_self_modification_session
from aether.action.changelog_exporter import export_public_changelog, export_milestone_report, export_private_changelog_report, changelog_export_status
from aether.interface.routers.code_review_routes import code_review_router
from aether.interface.routers.mutation_log_routes import mutation_log_router
from aether.interface.routers.proposal_console_routes import proposal_console_router
from aether.interface.routers.file_routes import file_router
from aether.interface.routers.patch_routes import patch_router
from aether.interface.routers.approval_routes import approval_router
from aether.interface.routers.dry_run_routes import dry_run_router
from aether.interface.routers.simulation_routes import simulation_router
from aether.interface.routers.verification_apply_gate_routes import verification_apply_gate_router
from aether.interface.routers.authorization_execution_gate_routes import authorization_execution_gate_router
from aether.interface.routers.executor_routes import executor_router
from aether.interface.routers.evidence_routes import evidence_router
from aether.interface.routers.verification_plan_routes import verification_plan_router
from aether.interface.routers.tool_registry_plan_routes import tool_registry_plan_router
from aether.interface.routers.memory_routes import memory_router
from aether.interface.routers.tool_executor_routes import tool_executor_router
from aether.interface.routers.repair_routes import repair_router
from aether.interface.routers.post_chain_c1_routes import post_chain_c1_router
from aether.action.services.final_real_apply_executor_service import handle_open_final_real_apply_executor,handle_execute_final_real_apply,handle_get_final_real_apply_executor_status,handle_list_final_real_apply_executor_records,handle_summarize_final_real_apply_executor,handle_get_final_real_apply_executor_record
from aether.action.guided_repair_intake import open_guided_repair_intake,submit_guided_repair_intake_decision,export_guided_repair_intake_report,export_guided_repair_intake_index,export_private_guided_repair_intake_record,get_guided_repair_intake_record,list_guided_repair_intake_records,guided_repair_intake_status,summarize_guided_repair_intake
from aether.action.guided_repair_plan_launcher import launch_guided_repair_plan,get_guided_repair_plan_launcher_record,list_guided_repair_plan_launcher_records,guided_repair_plan_launcher_status,summarize_guided_repair_plan_launcher
from aether.action.guided_bridge_selection_launcher import launch_guided_bridge_selection,get_guided_bridge_selection_launcher_record,list_guided_bridge_selection_launcher_records,guided_bridge_selection_launcher_status,summarize_guided_bridge_selection_launcher
from aether.action.guided_proposal_review_launcher import open_guided_proposal_review,get_guided_proposal_review_launcher_record,list_guided_proposal_review_launcher_records,guided_proposal_review_launcher_status,summarize_guided_proposal_review_launcher
from aether.action.guided_proposal_decision_launcher import submit_guided_proposal_decision,get_guided_proposal_decision_launcher_record,list_guided_proposal_decision_launcher_records,guided_proposal_decision_launcher_status,summarize_guided_proposal_decision_launcher

app = FastAPI(
    title="Aether API",
    description="First Awakening API with Working Memory for Aether",
    version="0.2.0",
)

app.include_router(code_review_router, prefix="")
app.include_router(mutation_log_router, prefix="")
app.include_router(proposal_console_router, prefix="")
app.include_router(file_router, prefix="")
app.include_router(patch_router, prefix="")
app.include_router(approval_router, prefix="")
app.include_router(dry_run_router, prefix="")
app.include_router(simulation_router, prefix="")
app.include_router(verification_apply_gate_router, prefix="")
app.include_router(authorization_execution_gate_router, prefix="")
app.include_router(executor_router, prefix="")
app.include_router(evidence_router, prefix="")
app.include_router(verification_plan_router, prefix="")
app.include_router(tool_registry_plan_router, prefix="")
app.include_router(memory_router, prefix="")
app.include_router(tool_executor_router, prefix="")
app.include_router(repair_router, prefix="")
app.include_router(post_chain_c1_router, prefix="")


# ---- Identity Integrity Endpoints (Milestone 48A) ----


@app.get("/identity/integrity/status", response_model=IdentityIntegrityStatusResponse)
def get_identity_integrity_status():
    return identity_guard_status()


@app.post(
    "/identity/integrity/initialize",
    response_model=InitializeIdentityGuardResponse,
)
def post_initialize_identity_guard():
    state = initialize_identity_guard()
    return {
        "status": state.get("status", "unknown"),
        "current_sha256": (state.get("current_sha256") or "")[:12],
        "known_sha256": (state.get("known_sha256") or "")[:12],
        "changed": False,
        "updated": state.get("updated"),
        "warnings": [],
    }


@app.post(
    "/identity/integrity/verify",
    response_model=VerifyIdentityIntegrityResponse,
)
def post_verify_identity_integrity():
    result = verify_identity_integrity()
    return result


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
    return handle_awaken()

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    # Resolve input: prefer 'text', fall back to legacy 'message'
    input_text = (request.text or "").strip() or (request.message or "").strip()
    if not input_text:
        from aether.time.clock import now_iso, time_state
        from aether.core.loop_trace import build_loop_trace, build_stage, generate_trace_id
        error_trace = build_loop_trace(
            trace_id=generate_trace_id("chat"),
            loop_version="0.1.0",
            started_at=now_iso(),
            completed_at=now_iso(),
            duration_ms=0,
            status="error",
            stages=[
                build_stage("input_validation", status="error", summary="Input text is empty"),
                build_stage("response_generation", summary="Response generated"),
            ],
            safety={
                "tool_execution_allowed": False,
                "tool_executed": False,
                "execution_allowed": False,
                "approval_required": False,
            },
            records={
                "working_memory_event_ids": [],
                "timeline_event_id": None,
                "approval_id": None,
            },
            warnings=["No input text provided."],
        )
        return ChatResponse(
            status="error",
            response="Input text is empty. Provide 'text' or legacy 'message'.",
            warnings=["No input text provided."],
            loop_trace=error_trace,
        )

    # Force tool execution to false for this milestone
    result = runtime.process_chat(
        text=input_text,
        session_id=request.session_id,
        metadata=request.metadata,
        allow_tool_execution=False,
    )

    summary = runtime.working_memory.summary()

    return ChatResponse(
        name="Aether",
        status=result.get("status", "completed"),
        response=result.get("response_text", ""),
        response_text=result.get("response_text", ""),
        time=result.get("time"),
        working_memory_event_count=summary["event_count"],
        session_id=result.get("session_id"),
        loop_version=result.get("loop_version"),
        identity_integrity_status=result.get("identity_integrity_status"),
        perception=result.get("perception"),
        risk=result.get("risk"),
        suggested_tool=result.get("suggested_tool"),
        tool_execution_allowed=False,
        tool_executed=result.get("tool_executed", False),
        memory_recorded=result.get("memory_recorded", False),
        timeline_recorded=result.get("timeline_recorded", False),
        warnings=result.get("warnings", []),
        thinking_policy=result.get("thinking_policy"),
        decision_type=result.get("decision_type"),
        required_user_confirmation=result.get("required_user_confirmation", False),
        clarification_question=result.get("clarification_question"),
        blocked_reason=result.get("blocked_reason"),
        # --- Policy Enforcement Gate (Milestone 51A) ---
        policy_gate=result.get("policy_gate"),
        execution_allowed=result.get("execution_allowed", False),
        execution_decision=result.get("execution_decision"),
        execution_reason=result.get("execution_reason"),
        # --- Approval Request (Milestone 52A) ---
        approval_request=result.get("approval_request"),
        approval_required=result.get("approval_required", False),
        approval_status=result.get("approval_status"),
        approval_type=result.get("approval_type"),
        # --- Approval Queue (Milestone 54A) ---
        approval_record=result.get("approval_record"),
        approval_id=result.get("approval_id"),
        # --- Loop Trace (Milestone 81C) ---
        loop_trace=result.get("loop_trace"),
    )


@app.post("/verification/classify")
def classify_verification_risk(request: VerificationRequest):
    return {"name": "Aether", "status": runtime.status(), "classification": classify_risk(request.text)}


# ===================================================================== #
# Approval Queue Endpoints (Milestone 54A)
# ===================================================================== #





# ===================================================================== #
# Approval Decision Gate (Milestone 55A)
# ===================================================================== #





# ===================================================================== #
# Dry-Run Endpoints (Milestone 56A, 57A)
# ===================================================================== #





# ===================================================================== #
# Dry-Run Sandbox Contract Endpoint (Milestone 58A)
# ===================================================================== #





@app.post("/action/self-modification/create")
def create_self_modification(request:SelfModificationCreateRequest):return {"name":"Aether","session":create_self_modification_session(request.goal,request.target_path,request.proposed_change_summary,request.proposed_excerpt,request.reason,request.original_excerpt,request.create_approval_if_required,request.metadata)}
@app.post("/action/self-modification/review")
def review_self_modification(request:SelfModificationReviewRequest):return {"name":"Aether","session":review_self_modification_session(request.session_id,request.decision,request.review_reason,request.reviewer,request.metadata)}
@app.post("/action/self-modification/dry-run")
def dry_run_self_modification(request:SelfModificationActionRequest):return {"name":"Aether","session":dry_run_self_modification_session(request.session_id,request.metadata)}
@app.post("/action/self-modification/apply")
def apply_self_modification(request:SelfModificationActionRequest):return {"name":"Aether","session":apply_self_modification_session(request.session_id,request.metadata)}
@app.post("/action/self-modification/rollback")
def rollback_self_modification(request:SelfModificationActionRequest):return {"name":"Aether","session":rollback_self_modification_session(request.session_id,request.metadata)}
@app.get("/action/self-modification/status")
def get_self_modification_status():return {"name":"Aether","self_modification":self_modification_status()}
@app.get("/action/self-modification/list")
def list_self_modification(status:str|None=None,target_path:str|None=None,limit:int=50):return {"name":"Aether","sessions":list_self_modification_sessions(status,target_path,limit)}
@app.get("/action/self-modification/{session_id}/summary")
def summarize_self_modification(session_id:str):return {"name":"Aether","summary":summarize_self_modification_session(session_id)}
@app.get("/action/self-modification/{session_id}")
def get_self_modification(session_id:str):return {"name":"Aether","session":get_self_modification_session(session_id)}
@app.post("/action/changelog/export-public")
def export_public_changelog_action(request:ChangelogExportRequest):return export_public_changelog(request.output_path,request.milestone,request.limit,request.metadata)
@app.post("/action/changelog/export-milestone")
def export_milestone_changelog_action(request:MilestoneReportExportRequest):return export_milestone_report(request.milestone,request.output_dir,request.metadata)
@app.post("/action/changelog/export-private")
def export_private_changelog_action(request:ChangelogExportRequest):return export_private_changelog_report(request.milestone,request.limit,request.metadata)
@app.get("/action/changelog/status")
def get_changelog_status():return changelog_export_status()
@app.post("/action/final-real-apply-executor/open")
def open_final_real_apply_executor_action(request:FinalRealApplyExecutorOpenRequest):return handle_open_final_real_apply_executor(request.source_type,request.source_id,request.metadata)
@app.post("/action/final-real-apply-executor/execute")
def execute_final_real_apply_action(request:FinalRealApplyExecuteRequest):return handle_execute_final_real_apply(request.executor_record_id,request.metadata)
@app.get("/action/final-real-apply-executor/status")
def get_final_real_apply_executor_status_action():return handle_get_final_real_apply_executor_status()
@app.get("/action/final-real-apply-executor/list")
def list_final_real_apply_executor_action(status:str|None=None,proposal_id:str|None=None,limit:int=50):return handle_list_final_real_apply_executor_records(status,proposal_id,limit)
@app.get("/action/final-real-apply-executor/{record_id}/summary")
def summarize_final_real_apply_executor_action(record_id:str):return handle_summarize_final_real_apply_executor(record_id)
@app.get("/action/final-real-apply-executor/{record_id}")
def get_final_real_apply_executor_action(record_id:str):return handle_get_final_real_apply_executor_record(record_id)
@app.post("/action/guided-repair-intake/open")
def open_guided_repair_intake_action(request:GuidedRepairIntakeOpenRequest):return {"name":"Aether","record":open_guided_repair_intake(request.request_type,request.requested_scope,request.target_path,request.requester,request.guidance_record_id,request.create_guidance_if_missing,request.export_public,request.export_index,request.export_private,request.metadata)}
@app.post("/action/guided-repair-intake/submit-decision")
def submit_guided_repair_intake_action(request:GuidedRepairIntakeDecisionRequest):return {"name":"Aether","record":submit_guided_repair_intake_decision(request.intake_record_id,request.decision,request.comment,request.reviewer,request.metadata)}
@app.post("/action/guided-repair-intake/export-report")
def export_guided_repair_intake_report_action(request:GuidedRepairIntakeReportExportRequest):return export_guided_repair_intake_report(request.intake_record_id,request.output_dir,request.metadata)
@app.post("/action/guided-repair-intake/export-index")
def export_guided_repair_intake_index_action(request:GuidedRepairIntakeIndexExportRequest):return export_guided_repair_intake_index(request.output_path,request.limit,request.metadata)
@app.post("/action/guided-repair-intake/export-private")
def export_private_guided_repair_intake_action(request:PrivateGuidedRepairIntakeExportRequest):return export_private_guided_repair_intake_record(request.intake_record_id,request.metadata)
@app.get("/action/guided-repair-intake/status")
def guided_repair_intake_status_action():return {"name":"Aether","guided_repair_intake":guided_repair_intake_status()}
@app.get("/action/guided-repair-intake/list")
def list_guided_repair_intake_action(status:str|None=None,planning_allowed:bool|None=None,target_path:str|None=None,limit:int=50):return {"name":"Aether","records":list_guided_repair_intake_records(status,planning_allowed,target_path,limit)}
@app.get("/action/guided-repair-intake/{record_id}/summary")
def summarize_guided_repair_intake_action(record_id:str):return {"name":"Aether","summary":summarize_guided_repair_intake(record_id)}
@app.get("/action/guided-repair-intake/{record_id}")
def get_guided_repair_intake_action(record_id:str):return {"name":"Aether","record":get_guided_repair_intake_record(record_id)}
@app.post("/action/guided-repair-plan-launcher/launch")
def launch_guided_repair_plan_action(request:GuidedRepairPlanLaunchRequest):return {"name":"Aether","record":launch_guided_repair_plan(request.intake_record_id,request.review_report_id,request.create_repair_plan,request.metadata)}
@app.get("/action/guided-repair-plan-launcher/status")
def guided_repair_plan_launcher_status_action():return {"name":"Aether","guided_repair_plan_launcher":guided_repair_plan_launcher_status()}
@app.get("/action/guided-repair-plan-launcher/list")
def list_guided_repair_plan_launcher_action(status:str|None=None,intake_record_id:str|None=None,target_path:str|None=None,limit:int=50):return {"name":"Aether","records":list_guided_repair_plan_launcher_records(status,intake_record_id,target_path,limit)}
@app.get("/action/guided-repair-plan-launcher/{record_id}/summary")
def summarize_guided_repair_plan_launcher_action(record_id:str):return {"name":"Aether","summary":summarize_guided_repair_plan_launcher(record_id)}
@app.get("/action/guided-repair-plan-launcher/{record_id}")
def get_guided_repair_plan_launcher_action(record_id:str):return {"name":"Aether","record":get_guided_repair_plan_launcher_record(record_id)}
@app.post("/action/guided-bridge-selection-launcher/launch")
def launch_guided_bridge_selection_action(request:GuidedBridgeSelectionLaunchRequest):return {"name":"Aether","record":launch_guided_bridge_selection(request.plan_launcher_record_id,request.finding_id,request.proposed_excerpt,request.metadata)}
@app.get("/action/guided-bridge-selection-launcher/status")
def guided_bridge_selection_launcher_status_action():return {"name":"Aether","guided_bridge_selection_launcher":guided_bridge_selection_launcher_status()}
@app.get("/action/guided-bridge-selection-launcher/list")
def list_guided_bridge_selection_launcher_action(status:str|None=None,plan_launcher_record_id:str|None=None,repair_plan_id:str|None=None,target_path:str|None=None,limit:int=50):return {"name":"Aether","records":list_guided_bridge_selection_launcher_records(status,plan_launcher_record_id,repair_plan_id,target_path,limit)}
@app.get("/action/guided-bridge-selection-launcher/{record_id}/summary")
def summarize_guided_bridge_selection_launcher_action(record_id:str):return {"name":"Aether","summary":summarize_guided_bridge_selection_launcher(record_id)}
@app.get("/action/guided-bridge-selection-launcher/{record_id}")
def get_guided_bridge_selection_launcher_action(record_id:str):return {"name":"Aether","record":get_guided_bridge_selection_launcher_record(record_id)}
@app.post("/action/guided-proposal-review-launcher/open")
def open_guided_proposal_review_action(request:GuidedProposalReviewOpenRequest):return {"name":"Aether","record":open_guided_proposal_review(request.bridge_launcher_record_id,request.metadata)}
@app.get("/action/guided-proposal-review-launcher/status")
def guided_proposal_review_launcher_status_action():return {"name":"Aether","guided_proposal_review_launcher":guided_proposal_review_launcher_status()}
@app.get("/action/guided-proposal-review-launcher/list")
def list_guided_proposal_review_launcher_action(status:str|None=None,bridge_launcher_record_id:str|None=None,proposal_id:str|None=None,target_path:str|None=None,limit:int=50):return {"name":"Aether","records":list_guided_proposal_review_launcher_records(status,bridge_launcher_record_id,proposal_id,target_path,limit)}
@app.get("/action/guided-proposal-review-launcher/{record_id}/summary")
def summarize_guided_proposal_review_launcher_action(record_id:str):return {"name":"Aether","summary":summarize_guided_proposal_review_launcher(record_id)}
@app.get("/action/guided-proposal-review-launcher/{record_id}")
def get_guided_proposal_review_launcher_action(record_id:str):return {"name":"Aether","record":get_guided_proposal_review_launcher_record(record_id)}
@app.post("/action/guided-proposal-decision-launcher/submit")
def submit_guided_proposal_decision_action(request:GuidedProposalDecisionSubmitRequest):return {"name":"Aether","record":submit_guided_proposal_decision(request.proposal_review_launcher_record_id,request.decision,request.reviewer,request.comment,request.metadata)}
@app.get("/action/guided-proposal-decision-launcher/status")
def guided_proposal_decision_launcher_status_action():return {"name":"Aether","guided_proposal_decision_launcher":guided_proposal_decision_launcher_status()}
@app.get("/action/guided-proposal-decision-launcher/list")
def list_guided_proposal_decision_launcher_action(status:str|None=None,proposal_review_launcher_record_id:str|None=None,proposal_id:str|None=None,decision:str|None=None,target_path:str|None=None,limit:int=50):return {"name":"Aether","records":list_guided_proposal_decision_launcher_records(status,proposal_review_launcher_record_id,proposal_id,decision,target_path,limit)}
@app.get("/action/guided-proposal-decision-launcher/{record_id}/summary")
def summarize_guided_proposal_decision_launcher_action(record_id:str):return {"name":"Aether","summary":summarize_guided_proposal_decision_launcher(record_id)}
@app.get("/action/guided-proposal-decision-launcher/{record_id}")
def get_guided_proposal_decision_launcher_action(record_id:str):return {"name":"Aether","record":get_guided_proposal_decision_launcher_record(record_id)}
