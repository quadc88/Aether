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
from aether.interface.routers.final_real_apply_executor_routes import final_real_apply_executor_router
from aether.interface.routers.changelog_routes import changelog_router
from aether.interface.routers.guided_launcher_routes import guided_launcher_router
from aether.interface.routers.self_modification_routes import self_modification_router

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
app.include_router(final_real_apply_executor_router, prefix="")
app.include_router(changelog_router, prefix="")
app.include_router(guided_launcher_router, prefix="")
app.include_router(self_modification_router, prefix="")


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
