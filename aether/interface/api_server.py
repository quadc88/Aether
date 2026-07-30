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
    EpisodeWriteRequest,
    FinalRealApplyExecuteRequest,
    FinalRealApplyExecutorListRequest,
    FinalRealApplyExecutorOpenRequest,
    GoalRequest,
    GraphEdgeRequest,
    GraphNodeRequest,
    GraphSearchRequest,
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
    MilestoneRequest,
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
    SemanticSearchRequest,
    TimelineSearchRequest,
    ToolExecutionListRequest,
    ToolExecutionRequest,
    ToolPlanListRequest,
    ToolPlanRequest,
    ToolPolicyUpdateRequest,
    ToolRegisterRequest,
    ToolSearchRequest,
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
from aether.action.services.tool_registry_service import (
    handle_disable_action_tool as _handle_disable_tool,
    handle_enable_action_tool as _handle_enable_tool,
    handle_get_action_tool as _handle_get_tool,
    handle_get_tool_registry_status as _handle_tool_registry_status,
    handle_list_action_tools as _handle_list_tools,
    handle_register_action_tool as _handle_register_tool,
    handle_search_action_tools as _handle_search_tools,
    handle_seed_action_tools as _handle_seed_tools,
    handle_update_action_tool_policy as _handle_update_tool_policy,
)
from aether.action.services.tool_plan_service import (
    handle_create_action_tool_plan as _handle_create_tool_plan,
    handle_get_action_tool_plan as _handle_get_tool_plan,
    handle_get_tool_plan_status as _handle_tool_plan_status,
    handle_list_action_tool_plans as _handle_list_tool_plans,
)
from aether.action.services.tool_execution_service import (
    handle_execute_action_tool as _handle_execute_tool,
    handle_get_action_tool_execution as _handle_get_execution,
    handle_get_tool_executor_status as _handle_tool_executor_status,
    handle_list_action_tool_executions as _handle_list_executions,
    handle_seed_action_sandbox_tools as _handle_seed_sandbox_tools,
)
from aether.action.services.verification_plan_service import (
    handle_create_verification_plan,
)
from aether.action.services.runtime_lifecycle_service import (
    handle_awaken,
)
from aether.action.services.memory_service import (
    handle_clear_working_memory as _handle_clear_wm,
    handle_create_graph_edge as _handle_create_graph_edge,
    handle_create_graph_node as _handle_create_graph_node,
    handle_get_working_memory as _handle_get_wm,
    handle_graph_status as _handle_graph_status,
    handle_index_semantic_memory as _handle_index_semantic,
    handle_latest_episodic_memory as _handle_latest_episodic,
    handle_latest_timeline_event as _handle_latest_timeline,
    handle_list_episodic_memory as _handle_list_episodic,
    handle_list_graph_edges as _handle_list_graph_edges,
    handle_list_graph_nodes as _handle_list_graph_nodes,
    handle_list_timeline_events as _handle_list_timeline,
    handle_search_graph as _handle_search_graph,
    handle_search_semantic_memory as _handle_search_semantic,
    handle_search_timeline as _handle_search_timeline,
    handle_seed_graph_memory as _handle_seed_graph,
    handle_semantic_memory_status as _handle_semantic_status,
    handle_set_working_goal as _handle_set_wm_goal,
    handle_set_working_milestone as _handle_set_wm_milestone,
    handle_timeline_status as _handle_timeline_status,
    handle_write_episodic_memory as _handle_write_episodic,
)

from aether.action.self_modification_cycle import create_self_modification_session, review_self_modification_session, dry_run_self_modification_session, apply_self_modification_session, rollback_self_modification_session, self_modification_status, list_self_modification_sessions, get_self_modification_session, summarize_self_modification_session
from aether.action.changelog_exporter import export_public_changelog, export_milestone_report, export_private_changelog_report, changelog_export_status
from aether.action.repair_planner import create_repair_plan, get_repair_plan, list_repair_plans, repair_plan_status, summarize_repair_plan
from aether.action.repair_bridge_selector import create_bridge_from_repair_plan, get_repair_bridge_selection, list_repair_bridge_selections, repair_bridge_selection_status, summarize_repair_bridge_selection
from aether.action.repair_workflow_tracker import trace_repair_workflow, get_repair_workflow_report, list_repair_workflow_reports, repair_workflow_status, summarize_repair_workflow
from aether.action.repair_workflow_exporter import export_workflow_report, export_workflow_index, export_private_workflow_report, repair_workflow_export_status
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
from aether.action.approved_dry_run_gate import open_approved_dry_run_gate,execute_approved_dry_run,get_approved_dry_run_gate_record,list_approved_dry_run_gate_records,approved_dry_run_gate_status,summarize_approved_dry_run_gate
from aether.action.dry_run_review_gate import open_dry_run_review_gate,submit_dry_run_review,get_dry_run_review_gate_record,list_dry_run_review_gate_records,dry_run_review_gate_status,summarize_dry_run_review_gate
from aether.action.real_apply_approval_gate import open_real_apply_approval_gate,submit_real_apply_final_decision,get_real_apply_approval_gate_record,list_real_apply_approval_gate_records,real_apply_approval_gate_status,summarize_real_apply_approval_gate
from aether.action.final_real_apply_executor import open_final_real_apply_executor,execute_final_real_apply,get_final_real_apply_executor_record,list_final_real_apply_executor_records,final_real_apply_executor_status,summarize_final_real_apply_executor
from aether.action.post_apply_verification_gate import open_post_apply_verification_gate,submit_post_apply_verification,get_post_apply_verification_gate_record,list_post_apply_verification_gate_records,post_apply_verification_gate_status,summarize_post_apply_verification_gate
from aether.action.repair_cycle_completion_report import create_repair_cycle_completion_report,export_repair_cycle_report,export_repair_cycle_index,export_private_repair_cycle_record,get_repair_cycle_completion_record,list_repair_cycle_completion_records,repair_cycle_completion_status,summarize_repair_cycle_completion
from aether.action.repair_learning_index import create_repair_learning_record,export_repair_learning_report,export_repair_learning_index,export_private_repair_learning_record,get_repair_learning_record,list_repair_learning_records,repair_learning_index_status,summarize_repair_learning_record
from aether.action.repair_guidance_engine import create_repair_guidance,export_repair_guidance_report,export_repair_guidance_index,export_private_repair_guidance_record,get_repair_guidance_record,list_repair_guidance_records,repair_guidance_engine_status,summarize_repair_guidance
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


@app.get("/memory/working")
def get_working_memory():
    return _handle_get_wm()


@app.post("/memory/working/goal")
def set_working_goal(request: GoalRequest):
    return _handle_set_wm_goal(goal=request.goal)


@app.post("/memory/working/milestone")
def set_working_milestone(request: MilestoneRequest):
    return _handle_set_wm_milestone(milestone=request.milestone)


@app.post("/memory/working/clear")
def clear_working_memory():
    return _handle_clear_wm()


@app.post("/memory/episodic/write")
def write_episodic_memory(request: EpisodeWriteRequest):
    return _handle_write_episodic(
        title=request.title,
        summary=request.summary,
        details=request.details,
        importance=request.importance,
        tags=request.tags,
        related_files=request.related_files,
    )


@app.get("/memory/episodic/list")
def list_episodic_memory(limit: int = 20):
    return _handle_list_episodic(limit=limit)


@app.get("/memory/episodic/latest")
def get_latest_episodic_memory():
    return _handle_latest_episodic()


@app.post("/memory/semantic/index")
def index_semantic_memory():
    return _handle_index_semantic()


@app.get("/memory/semantic/status")
def get_semantic_memory_status():
    return _handle_semantic_status()


@app.post("/memory/semantic/search")
def search_memory(request: SemanticSearchRequest):
    return _handle_search_semantic(query=request.query, limit=request.limit)


@app.get("/memory/timeline/status")
def get_timeline_status():
    return _handle_timeline_status()


@app.get("/memory/timeline/list")
def list_timeline_events(limit: int = 20):
    return _handle_list_timeline(limit=limit)


@app.get("/memory/timeline/latest")
def get_latest_timeline_event():
    return _handle_latest_timeline()


@app.post("/memory/timeline/search")
def search_timeline_memory(request: TimelineSearchRequest):
    return _handle_search_timeline(query=request.query, limit=request.limit)


@app.get("/memory/graph/status")
def get_graph_memory_status():
    return _handle_graph_status()


@app.post("/memory/graph/node")
def create_graph_node(request: GraphNodeRequest):
    return _handle_create_graph_node(
        label=request.label,
        node_type=request.node_type,
        properties=request.properties,
    )


@app.post("/memory/graph/edge")
def create_graph_edge(request: GraphEdgeRequest):
    return _handle_create_graph_edge(
        source=request.source,
        relation=request.relation,
        target=request.target,
        properties=request.properties,
    )


@app.get("/memory/graph/nodes")
def get_graph_nodes(limit: int = 50):
    return _handle_list_graph_nodes(limit=limit)


@app.get("/memory/graph/edges")
def get_graph_edges(limit: int = 50):
    return _handle_list_graph_edges(limit=limit)


@app.post("/memory/graph/search")
def search_graph_memory(request: GraphSearchRequest):
    return _handle_search_graph(query=request.query, limit=request.limit)


@app.post("/memory/graph/seed")
def seed_graph_memory():
    return _handle_seed_graph()


@app.post("/verification/classify")
def classify_verification_risk(request: VerificationRequest):
    return {"name": "Aether", "status": runtime.status(), "classification": classify_risk(request.text)}


@app.post("/verification/plan")
def create_verification_plan(request: VerificationRequest):
    return handle_create_verification_plan(request.text)






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





@app.get("/action/tools/status")
def get_tool_registry_status():
    return _handle_tool_registry_status()


@app.post("/action/tools/register")
def register_action_tool(request: ToolRegisterRequest):
    return _handle_register_tool(
        tool_id=request.tool_id,
        name=request.name,
        description=request.description,
        category=request.category,
        risk_level=request.risk_level,
        enabled=request.enabled,
        requires_verification=request.requires_verification,
        requires_user_approval=request.requires_user_approval,
        allow_auto_execute=request.allow_auto_execute,
        input_schema=request.input_schema,
        output_schema=request.output_schema,
        metadata=request.metadata,
    )


@app.post("/action/tools/seed")
def seed_action_tools():
    return _handle_seed_tools()


@app.get("/action/tools/list")
def list_action_tools(category: str | None = None, enabled: bool | None = None, limit: int = 100):
    return _handle_list_tools(category, enabled, limit)


@app.get("/action/tools/{tool_id}")
def get_action_tool(tool_id: str):
    return _handle_get_tool(tool_id)


@app.post("/action/tools/search")
def search_action_tools(request: ToolSearchRequest):
    return _handle_search_tools(request.query, request.limit)


@app.post("/action/tools/enable/{tool_id}")
def enable_action_tool(tool_id: str):
    return _handle_enable_tool(tool_id)


@app.post("/action/tools/disable/{tool_id}")
def disable_action_tool(tool_id: str):
    return _handle_disable_tool(tool_id)


@app.post("/action/tools/policy")
def update_action_tool_policy(request: ToolPolicyUpdateRequest):
    return _handle_update_tool_policy(
        tool_id=request.tool_id,
        risk_level=request.risk_level,
        requires_verification=request.requires_verification,
        requires_user_approval=request.requires_user_approval,
        allow_auto_execute=request.allow_auto_execute,
    )


@app.post("/action/tool-plan/create")
def create_action_tool_plan(request: ToolPlanRequest):
    return _handle_create_tool_plan(
        text=request.text,
        proposed_action=request.proposed_action,
        metadata=request.metadata,
        create_approval_if_required=request.create_approval_if_required,
    )


@app.get("/action/tool-plan/status")
def get_action_tool_plan_status():
    return _handle_tool_plan_status()


@app.get("/action/tool-plan/list")
def list_action_tool_plans(limit: int = 50):
    return _handle_list_tool_plans(limit)


@app.get("/action/tool-plan/{plan_id}")
def get_action_tool_plan(plan_id: str):
    return _handle_get_tool_plan(plan_id)


@app.post("/action/tool-executor/seed-sandbox-tools")
def seed_action_sandbox_tools():
    return _handle_seed_sandbox_tools()


@app.post("/action/tool-executor/execute")
def execute_action_tool(request: ToolExecutionRequest):
    return _handle_execute_tool(
        text=request.text,
        tool_id=request.tool_id,
        input_payload=request.input_payload,
        proposed_action=request.proposed_action,
        create_approval_if_required=request.create_approval_if_required,
        dry_run=request.dry_run,
        metadata=request.metadata,
    )


@app.get("/action/tool-executor/status")
def get_action_tool_executor_status():
    return _handle_tool_executor_status()


@app.get("/action/tool-executor/list")
def list_action_tool_executions(limit: int = 50):
    return _handle_list_executions(limit)


@app.get("/action/tool-executor/{execution_id}")
def get_action_tool_execution(execution_id: str):
    return _handle_get_execution(execution_id)


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
@app.post("/action/repair-plan/create")
def create_repair_plan_action(request:RepairPlanCreateRequest):return {"name":"Aether","plan":create_repair_plan(request.review_report_id,request.scope,request.include_deferred,request.max_findings,request.metadata)}
@app.get("/action/repair-plan/status")
def get_repair_plan_status_action():return {"name":"Aether","repair_plan":repair_plan_status()}
@app.get("/action/repair-plan/list")
def list_repair_plan_action(status:str|None=None,review_report_id:str|None=None,limit:int=50):return {"name":"Aether","plans":list_repair_plans(status,review_report_id,limit)}
@app.get("/action/repair-plan/{plan_id}/summary")
def summarize_repair_plan_action(plan_id:str):return {"name":"Aether","summary":summarize_repair_plan(plan_id)}
@app.get("/action/repair-plan/{plan_id}")
def get_repair_plan_action(plan_id:str):return {"name":"Aether","plan":get_repair_plan(plan_id)}
@app.post("/action/repair-bridge-selection/create")
def create_repair_bridge_selection_action(request:RepairBridgeSelectionCreateRequest):return {"name":"Aether","record":create_bridge_from_repair_plan(request.repair_plan_id,request.finding_id,request.proposed_excerpt,request.original_excerpt,request.proposed_change_summary,request.reason,request.create_approval_if_required,request.metadata)}
@app.get("/action/repair-bridge-selection/status")
def get_repair_bridge_selection_status_action():return {"name":"Aether","repair_bridge_selection":repair_bridge_selection_status()}
@app.get("/action/repair-bridge-selection/list")
def list_repair_bridge_selection_action(status:str|None=None,repair_plan_id:str|None=None,limit:int=50):return {"name":"Aether","records":list_repair_bridge_selections(status,repair_plan_id,limit)}
@app.get("/action/repair-bridge-selection/{record_id}/summary")
def summarize_repair_bridge_selection_action(record_id:str):return {"name":"Aether","summary":summarize_repair_bridge_selection(record_id)}
@app.get("/action/repair-bridge-selection/{record_id}")
def get_repair_bridge_selection_action(record_id:str):return {"name":"Aether","record":get_repair_bridge_selection(record_id)}
@app.post("/action/repair-workflow/trace")
def trace_repair_workflow_action(request:RepairWorkflowTraceRequest):return {"name":"Aether","report":trace_repair_workflow(request.root_type,request.root_id,request.metadata)}
@app.get("/action/repair-workflow/status")
def get_repair_workflow_status_action():return {"name":"Aether","repair_workflow":repair_workflow_status()}
@app.get("/action/repair-workflow/list")
def list_repair_workflow_action(status:str|None=None,root_type:str|None=None,limit:int=50):return {"name":"Aether","reports":list_repair_workflow_reports(status,root_type,limit)}
@app.get("/action/repair-workflow/{report_id}/summary")
def summarize_repair_workflow_action(report_id:str):return {"name":"Aether","summary":summarize_repair_workflow(report_id)}
@app.get("/action/repair-workflow/{report_id}")
def get_repair_workflow_action(report_id:str):return {"name":"Aether","report":get_repair_workflow_report(report_id)}
@app.post("/action/repair-workflow-export/export-report")
def export_repair_workflow_report_action(request:RepairWorkflowExportRequest):return export_workflow_report(request.report_id,request.output_dir,request.metadata)
@app.post("/action/repair-workflow-export/export-index")
def export_repair_workflow_index_action(request:RepairWorkflowIndexExportRequest):return export_workflow_index(request.output_path,request.limit,request.metadata)
@app.post("/action/repair-workflow-export/export-private")
def export_private_repair_workflow_report_action(request:PrivateRepairWorkflowExportRequest):return export_private_workflow_report(request.report_id,request.metadata)
@app.get("/action/repair-workflow-export/status")
def get_repair_workflow_export_status_action():return repair_workflow_export_status()
@app.post("/action/approved-dry-run-gate/open")
def open_approved_dry_run_gate_action(request:ApprovedDryRunGateOpenRequest):return {"name":"Aether","record":open_approved_dry_run_gate(request.source_type,request.source_id,request.metadata)}
@app.post("/action/approved-dry-run-gate/execute")
def execute_approved_dry_run_gate_action(request:ApprovedDryRunExecuteRequest):return {"name":"Aether","record":execute_approved_dry_run(request.gate_record_id,request.create_approval_if_required,request.metadata)}
@app.get("/action/approved-dry-run-gate/status")
def get_approved_dry_run_gate_status_action():return {"name":"Aether","approved_dry_run_gate":approved_dry_run_gate_status()}
@app.get("/action/approved-dry-run-gate/list")
def list_approved_dry_run_gate_action(status:str|None=None,proposal_id:str|None=None,limit:int=50):return {"name":"Aether","records":list_approved_dry_run_gate_records(status,proposal_id,limit)}
@app.get("/action/approved-dry-run-gate/{record_id}/summary")
def summarize_approved_dry_run_gate_action(record_id:str):return {"name":"Aether","summary":summarize_approved_dry_run_gate(record_id)}
@app.get("/action/approved-dry-run-gate/{record_id}")
def get_approved_dry_run_gate_action(record_id:str):return {"name":"Aether","record":get_approved_dry_run_gate_record(record_id)}
@app.post("/action/dry-run-review-gate/open")
def open_dry_run_review_gate_action(request:DryRunReviewGateOpenRequest):return {"name":"Aether","record":open_dry_run_review_gate(request.source_type,request.source_id,request.metadata)}
@app.post("/action/dry-run-review-gate/submit")
def submit_dry_run_review_action(request:DryRunReviewSubmitRequest):return {"name":"Aether","record":submit_dry_run_review(request.review_gate_record_id,request.decision,request.comment,request.reviewer,request.metadata)}
@app.get("/action/dry-run-review-gate/status")
def get_dry_run_review_gate_status_action():return {"name":"Aether","dry_run_review_gate":dry_run_review_gate_status()}
@app.get("/action/dry-run-review-gate/list")
def list_dry_run_review_gate_action(status:str|None=None,proposal_id:str|None=None,limit:int=50):return {"name":"Aether","records":list_dry_run_review_gate_records(status,proposal_id,limit)}
@app.get("/action/dry-run-review-gate/{record_id}/summary")
def summarize_dry_run_review_gate_action(record_id:str):return {"name":"Aether","summary":summarize_dry_run_review_gate(record_id)}
@app.get("/action/dry-run-review-gate/{record_id}")
def get_dry_run_review_gate_action(record_id:str):return {"name":"Aether","record":get_dry_run_review_gate_record(record_id)}
@app.post("/action/real-apply-approval-gate/open")
def open_real_apply_approval_gate_action(request:RealApplyApprovalGateOpenRequest):return {"name":"Aether","record":open_real_apply_approval_gate(request.source_type,request.source_id,request.create_approval_item,request.metadata)}
@app.post("/action/real-apply-approval-gate/submit")
def submit_real_apply_final_decision_action(request:RealApplyFinalDecisionRequest):return {"name":"Aether","record":submit_real_apply_final_decision(request.gate_record_id,request.decision,request.comment,request.reviewer,request.metadata)}
@app.get("/action/real-apply-approval-gate/status")
def get_real_apply_approval_gate_status_action():return {"name":"Aether","real_apply_approval_gate":real_apply_approval_gate_status()}
@app.get("/action/real-apply-approval-gate/list")
def list_real_apply_approval_gate_action(status:str|None=None,proposal_id:str|None=None,limit:int=50):return {"name":"Aether","records":list_real_apply_approval_gate_records(status,proposal_id,limit)}
@app.get("/action/real-apply-approval-gate/{record_id}/summary")
def summarize_real_apply_approval_gate_action(record_id:str):return {"name":"Aether","summary":summarize_real_apply_approval_gate(record_id)}
@app.get("/action/real-apply-approval-gate/{record_id}")
def get_real_apply_approval_gate_action(record_id:str):return {"name":"Aether","record":get_real_apply_approval_gate_record(record_id)}
@app.post("/action/final-real-apply-executor/open")
def open_final_real_apply_executor_action(request:FinalRealApplyExecutorOpenRequest):return {"name":"Aether","record":open_final_real_apply_executor(request.source_type,request.source_id,request.metadata)}
@app.post("/action/final-real-apply-executor/execute")
def execute_final_real_apply_action(request:FinalRealApplyExecuteRequest):return {"name":"Aether","record":execute_final_real_apply(request.executor_record_id,request.metadata)}
@app.get("/action/final-real-apply-executor/status")
def get_final_real_apply_executor_status_action():return {"name":"Aether","final_real_apply_executor":final_real_apply_executor_status()}
@app.get("/action/final-real-apply-executor/list")
def list_final_real_apply_executor_action(status:str|None=None,proposal_id:str|None=None,limit:int=50):return {"name":"Aether","records":list_final_real_apply_executor_records(status,proposal_id,limit)}
@app.get("/action/final-real-apply-executor/{record_id}/summary")
def summarize_final_real_apply_executor_action(record_id:str):return {"name":"Aether","summary":summarize_final_real_apply_executor(record_id)}
@app.get("/action/final-real-apply-executor/{record_id}")
def get_final_real_apply_executor_action(record_id:str):return {"name":"Aether","record":get_final_real_apply_executor_record(record_id)}
@app.post("/action/post-apply-verification-gate/open")
def open_post_apply_verification_gate_action(request:PostApplyVerificationGateOpenRequest):return {"name":"Aether","record":open_post_apply_verification_gate(request.source_type,request.source_id,request.metadata)}
@app.post("/action/post-apply-verification-gate/submit")
def submit_post_apply_verification_action(request:PostApplyVerificationSubmitRequest):return {"name":"Aether","record":submit_post_apply_verification(request.verification_record_id,request.decision,request.comment,request.verifier,request.metadata)}
@app.get("/action/post-apply-verification-gate/status")
def get_post_apply_verification_gate_status_action():return {"name":"Aether","post_apply_verification_gate":post_apply_verification_gate_status()}
@app.get("/action/post-apply-verification-gate/list")
def list_post_apply_verification_gate_action(status:str|None=None,proposal_id:str|None=None,limit:int=50):return {"name":"Aether","records":list_post_apply_verification_gate_records(status,proposal_id,limit)}
@app.get("/action/post-apply-verification-gate/{record_id}/summary")
def summarize_post_apply_verification_gate_action(record_id:str):return {"name":"Aether","summary":summarize_post_apply_verification_gate(record_id)}
@app.get("/action/post-apply-verification-gate/{record_id}")
def get_post_apply_verification_gate_action(record_id:str):return {"name":"Aether","record":get_post_apply_verification_gate_record(record_id)}
@app.post("/action/repair-cycle-completion/create")
def create_repair_cycle_completion_action(request:RepairCycleCompletionCreateRequest):return {"name":"Aether","record":create_repair_cycle_completion_report(request.source_type,request.source_id,request.export_public,request.export_index,request.export_private,request.metadata)}
@app.post("/action/repair-cycle-completion/export-report")
def export_repair_cycle_report_action(request:RepairCycleReportExportRequest):return export_repair_cycle_report(request.completion_record_id,request.output_dir,request.metadata)
@app.post("/action/repair-cycle-completion/export-index")
def export_repair_cycle_index_action(request:RepairCycleIndexExportRequest):return export_repair_cycle_index(request.output_path,request.limit,request.metadata)
@app.post("/action/repair-cycle-completion/export-private")
def export_private_repair_cycle_action(request:PrivateRepairCycleExportRequest):return export_private_repair_cycle_record(request.completion_record_id,request.metadata)
@app.get("/action/repair-cycle-completion/status")
def get_repair_cycle_completion_status_action():return {"name":"Aether","repair_cycle_completion":repair_cycle_completion_status()}
@app.get("/action/repair-cycle-completion/list")
def list_repair_cycle_completion_action(status:str|None=None,proposal_id:str|None=None,limit:int=50):return {"name":"Aether","records":list_repair_cycle_completion_records(status,proposal_id,limit)}
@app.get("/action/repair-cycle-completion/{record_id}/summary")
def summarize_repair_cycle_completion_action(record_id:str):return {"name":"Aether","summary":summarize_repair_cycle_completion(record_id)}
@app.get("/action/repair-cycle-completion/{record_id}")
def get_repair_cycle_completion_action(record_id:str):return {"name":"Aether","record":get_repair_cycle_completion_record(record_id)}
@app.post("/action/repair-learning/create")
def create_repair_learning_action(request:RepairLearningCreateRequest):return {"name":"Aether","record":create_repair_learning_record(request.source_type,request.source_id,request.export_public,request.export_index,request.export_private,request.metadata)}
@app.post("/action/repair-learning/export-report")
def export_repair_learning_report_action(request:RepairLearningReportExportRequest):return export_repair_learning_report(request.learning_record_id,request.output_dir,request.metadata)
@app.post("/action/repair-learning/export-index")
def export_repair_learning_index_action(request:RepairLearningIndexExportRequest):return export_repair_learning_index(request.output_path,request.limit,request.metadata)
@app.post("/action/repair-learning/export-private")
def export_private_repair_learning_action(request:PrivateRepairLearningExportRequest):return export_private_repair_learning_record(request.learning_record_id,request.metadata)
@app.get("/action/repair-learning/status")
def get_repair_learning_status_action():return {"name":"Aether","repair_learning":repair_learning_index_status()}
@app.get("/action/repair-learning/list")
def list_repair_learning_action(status:str|None=None,learning_category:str|None=None,target_path:str|None=None,limit:int=50):return {"name":"Aether","records":list_repair_learning_records(status,learning_category,target_path,limit)}
@app.get("/action/repair-learning/{record_id}/summary")
def summarize_repair_learning_action(record_id:str):return {"name":"Aether","summary":summarize_repair_learning_record(record_id)}
@app.get("/action/repair-learning/{record_id}")
def get_repair_learning_action(record_id:str):return {"name":"Aether","record":get_repair_learning_record(record_id)}
@app.post("/action/repair-guidance/create")
def create_repair_guidance_action(request:RepairGuidanceCreateRequest):return {"name":"Aether","record":create_repair_guidance(request.request_type,request.requested_scope,request.target_path,request.source_type,request.source_id,request.export_public,request.export_index,request.export_private,request.metadata)}
@app.post("/action/repair-guidance/export-report")
def export_repair_guidance_report_action(request:RepairGuidanceReportExportRequest):return export_repair_guidance_report(request.guidance_record_id,request.output_dir,request.metadata)
@app.post("/action/repair-guidance/export-index")
def export_repair_guidance_index_action(request:RepairGuidanceIndexExportRequest):return export_repair_guidance_index(request.output_path,request.limit,request.metadata)
@app.post("/action/repair-guidance/export-private")
def export_private_repair_guidance_action(request:PrivateRepairGuidanceExportRequest):return export_private_repair_guidance_record(request.guidance_record_id,request.metadata)
@app.get("/action/repair-guidance/status")
def get_repair_guidance_status_action():return {"name":"Aether","repair_guidance":repair_guidance_engine_status()}
@app.get("/action/repair-guidance/list")
def list_repair_guidance_action(status:str|None=None,guidance_decision:str|None=None,target_path:str|None=None,limit:int=50):return {"name":"Aether","records":list_repair_guidance_records(status,guidance_decision,target_path,limit)}
@app.get("/action/repair-guidance/{record_id}/summary")
def summarize_repair_guidance_action(record_id:str):return {"name":"Aether","summary":summarize_repair_guidance(record_id)}
@app.get("/action/repair-guidance/{record_id}")
def get_repair_guidance_action(record_id:str):return {"name":"Aether","record":get_repair_guidance_record(record_id)}
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
