from fastapi import FastAPI
from pydantic import BaseModel

from aether.identity.loader import load_identity_seed, identity_preview
from aether.identity.guard import (
    initialize_identity_guard,
    verify_identity_integrity,
    identity_guard_status,
)
from aether.time.clock import time_state
from aether.memory.timeline.recorder import (
    record_event,
    list_events,
    latest_event,
    search_events,
    timeline_status,
)
from aether.core.runtime import runtime
from aether.memory.episodic.writer import write_episode, list_episodes, latest_episode
from aether.memory.semantic.indexer import (
    build_semantic_index,
    search_semantic_memory,
    semantic_memory_status,
)
from aether.memory.graph.store import (
    add_edge,
    graph_status,
    list_edges,
    list_nodes,
    search_graph,
    upsert_node,
)
from aether.verification.risk import classify_risk, verification_plan
from aether.action.approval_queue import (
    approval_queue_status,
    approve_item,
    cancel_item,
    create_approval_item,
    get_approval_item,
    list_approval_items,
    reject_item,
)
from aether.action.tool_registry import (
    disable_tool,
    enable_tool,
    get_tool,
    list_tools,
    register_tool,
    search_tools,
    seed_default_tools,
    tool_registry_status,
    update_tool_policy,
)
from aether.action.tool_planner import (
    create_tool_invocation_plan,
    get_tool_plan,
    list_tool_plans,
    tool_planner_status,
)
from aether.action.tool_executor import (
    execute_tool,
    get_execution,
    list_executions,
    seed_sandbox_tools,
    tool_executor_status,
)
from aether.action.restricted_file_reader import (
    file_access_status,
    get_file_access,
    list_allowed_roots,
    list_file_accesses,
    read_restricted_file,
)
from aether.action.restricted_file_browser import (
    browse_restricted_path,
    file_browser_status,
    get_file_browse,
    list_browser_allowed_roots,
    list_file_browses,
    search_restricted_files,
)
from aether.action.self_inspector import (
    create_project_self_inspection,
    get_self_inspection_report,
    list_self_inspection_reports,
    self_inspection_status,
)
from aether.action.patch_proposal import create_patch_proposal, get_patch_proposal, list_patch_proposals, mark_patch_proposal_status, patch_proposal_status
from aether.action.patch_review import get_patch_review, list_patch_reviews, patch_review_status, review_patch_proposal
from aether.action.patch_apply import apply_patch_proposal, get_patch_apply, list_patch_applies, patch_apply_status
from aether.action.patch_rollback import rollback_patch_apply, get_patch_rollback, list_patch_rollbacks, patch_rollback_status
from aether.action.mutation_log import record_mutation, record_milestone_completed, mutation_log_status, list_mutations, summarize_mutations, get_mutation
from aether.action.self_modification_cycle import create_self_modification_session, review_self_modification_session, dry_run_self_modification_session, apply_self_modification_session, rollback_self_modification_session, self_modification_status, list_self_modification_sessions, get_self_modification_session, summarize_self_modification_session
from aether.action.changelog_exporter import export_public_changelog, export_milestone_report, export_private_changelog_report, changelog_export_status
from aether.action.code_reviewer import create_code_review, get_code_review, list_code_reviews, code_review_status, summarize_code_review
from aether.action.review_bridge import create_bridge_from_finding, get_review_bridge_record, list_review_bridge_records, review_bridge_status, summarize_review_bridge_record
from aether.action.repair_planner import create_repair_plan, get_repair_plan, list_repair_plans, repair_plan_status, summarize_repair_plan
from aether.action.repair_bridge_selector import create_bridge_from_repair_plan, get_repair_bridge_selection, list_repair_bridge_selections, repair_bridge_selection_status, summarize_repair_bridge_selection
from aether.action.repair_workflow_tracker import trace_repair_workflow, get_repair_workflow_report, list_repair_workflow_reports, repair_workflow_status, summarize_repair_workflow
from aether.action.repair_workflow_exporter import export_workflow_report, export_workflow_index, export_private_workflow_report, repair_workflow_export_status
from aether.action.proposal_review_console import open_proposal_review_console, submit_proposal_review, get_proposal_review_console_record, list_proposal_review_console_records, proposal_review_console_status, summarize_proposal_review_console
from aether.action.proposal_revision_console import open_proposal_revision_console, create_proposal_revision, get_proposal_revision_console_record, list_proposal_revision_console_records, proposal_revision_console_status, summarize_proposal_revision_console
from aether.action.revised_proposal_review_loop import open_revised_proposal_review, submit_revised_proposal_review, get_revised_proposal_review_loop_record, list_revised_proposal_review_loop_records, revised_proposal_review_loop_status, summarize_revised_proposal_review_loop
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


class ChatRequest(BaseModel):
    text: str | None = None
    message: str | None = None
    session_id: str | None = None
    metadata: dict = {}
    allow_tool_execution: bool = False


class ChatResponse(BaseModel):
    name: str | None = "Aether"
    status: str
    response: str | None = None
    response_text: str | None = None
    time: dict | None = None
    working_memory_event_count: int = 0
    session_id: str | None = None
    loop_version: str | None = None
    identity_integrity_status: dict | None = None
    perception: dict | None = None
    risk: dict | None = None
    suggested_tool: dict | None = None
    tool_execution_allowed: bool = False
    tool_executed: bool = False
    memory_recorded: bool = False
    timeline_recorded: bool = False
    warnings: list[str] = []
    thinking_policy: dict | None = None
    decision_type: str | None = None
    required_user_confirmation: bool = False
    clarification_question: str | None = None
    blocked_reason: str | None = None


class GoalRequest(BaseModel):
    goal: str


class MilestoneRequest(BaseModel):
    milestone: str

class EpisodeWriteRequest(BaseModel):
    title: str
    summary: str
    details: str = ""
    importance: str = "normal"
    tags: list[str] = []
    related_files: list[str] = []

class SemanticSearchRequest(BaseModel):
    query: str
    limit: int = 5

class TimelineSearchRequest(BaseModel):
    query: str
    limit: int = 20


class GraphNodeRequest(BaseModel):
    label: str
    node_type: str = "entity"
    properties: dict = {}


class GraphEdgeRequest(BaseModel):
    source: str
    relation: str
    target: str
    properties: dict = {}


class GraphSearchRequest(BaseModel):
    query: str
    limit: int = 20


class VerificationRequest(BaseModel):
    text: str


class ApprovalCreateRequest(BaseModel):
    request_text: str
    proposed_action: str
    metadata: dict = {}


class ApprovalDecisionRequest(BaseModel):
    approval_id: str
    decision_reason: str = ""


class ApprovalListRequest(BaseModel):
    status: str | None = None
    limit: int = 50


class ToolRegisterRequest(BaseModel):
    tool_id: str
    name: str
    description: str
    category: str
    risk_level: str = "medium"
    enabled: bool = True
    requires_verification: bool = True
    requires_user_approval: bool = False
    allow_auto_execute: bool = False
    input_schema: dict = {}
    output_schema: dict = {}
    metadata: dict = {}


class ToolSearchRequest(BaseModel):
    query: str
    limit: int = 20


class ToolPolicyUpdateRequest(BaseModel):
    tool_id: str
    risk_level: str | None = None
    requires_verification: bool | None = None
    requires_user_approval: bool | None = None
    allow_auto_execute: bool | None = None


class ToolPlanRequest(BaseModel):
    text: str
    proposed_action: str | None = None
    create_approval_if_required: bool = False
    metadata: dict = {}


class ToolPlanListRequest(BaseModel):
    limit: int = 50


class ToolExecutionRequest(BaseModel):
    text: str
    tool_id: str | None = None
    input_payload: dict = {}
    proposed_action: str | None = None
    create_approval_if_required: bool = False
    dry_run: bool = True
    metadata: dict = {}


class ToolExecutionListRequest(BaseModel):
    limit: int = 50


class RestrictedFileReadRequest(BaseModel):
    path: str
    max_chars: int = 12000
    metadata: dict = {}


class RestrictedFileAccessListRequest(BaseModel):
    limit: int = 50


class RestrictedFileBrowseRequest(BaseModel):
    path: str = "C:/Aether"
    max_depth: int = 3
    max_entries: int = 200
    include_files: bool = True
    include_dirs: bool = True
    metadata: dict = {}


class RestrictedFileSearchRequest(BaseModel):
    query: str
    root: str = "C:/Aether"
    max_results: int = 50
    metadata: dict = {}


class RestrictedFileBrowseListRequest(BaseModel):
    limit: int = 50


class SelfInspectionRequest(BaseModel):
    root: str = "C:/Aether"
    max_files_to_read: int = 20
    max_chars_per_file: int = 6000
    metadata: dict = {}


class SelfInspectionListRequest(BaseModel):
    limit: int = 20

class PatchProposalRequest(BaseModel):
    target_path: str
    request_text: str
    proposed_change_summary: str
    proposed_excerpt: str
    reason: str = ""
    original_excerpt: str | None = None
    create_approval_if_required: bool = False
    metadata: dict = {}

class PatchProposalStatusUpdateRequest(BaseModel):
    proposal_id: str
    status: str
    reason: str = ""

class PatchReviewRequest(BaseModel):
    proposal_id: str
    decision: str
    review_reason: str = ""
    reviewer: str = "user"
    metadata: dict = {}
class PatchApplyRequest(BaseModel):
    proposal_id: str
    dry_run: bool = True
    metadata: dict = {}
class PatchRollbackRequest(BaseModel):
    apply_id: str
    dry_run: bool = True
    metadata: dict = {}
class MutationRecordRequest(BaseModel):
    mutation_type: str
    title: str
    summary: str
    milestone: str | None = None
    target_path: str | None = None
    metadata: dict = {}
class MilestoneCompletedRequest(BaseModel):
    milestone: str
    summary: str
    metadata: dict = {}
class SelfModificationCreateRequest(BaseModel):
    goal:str; target_path:str; proposed_change_summary:str; proposed_excerpt:str; reason:str=""; original_excerpt:str|None=None; create_approval_if_required:bool=False; metadata:dict={}
class SelfModificationReviewRequest(BaseModel):
    session_id:str; decision:str; review_reason:str=""; reviewer:str="user"; metadata:dict={}
class SelfModificationActionRequest(BaseModel):
    session_id:str; metadata:dict={}
class ChangelogExportRequest(BaseModel):
    output_path:str="docs/history/CHANGELOG.md"; milestone:str|None=None; limit:int=200; metadata:dict={}
class CodeReviewCreateRequest(BaseModel):
    scope:str; target_paths:list[str]|None=None; max_files:int=20; max_chars_per_file:int=12000; include_tests:bool=True; metadata:dict={}
class ReviewBridgeCreateRequest(BaseModel):
    report_id:str; finding_id:str; proposed_excerpt:str; original_excerpt:str|None=None; proposed_change_summary:str|None=None; reason:str|None=None; create_approval_if_required:bool=False; metadata:dict={}
class RepairPlanCreateRequest(BaseModel):
    review_report_id:str; scope:str|None=None; include_deferred:bool=True; max_findings:int=50; metadata:dict={}
class RepairBridgeSelectionCreateRequest(BaseModel):
    repair_plan_id:str; finding_id:str; proposed_excerpt:str; original_excerpt:str|None=None; proposed_change_summary:str|None=None; reason:str|None=None; create_approval_if_required:bool=False; metadata:dict={}
class RepairBridgeSelectionListRequest(BaseModel):
    status:str|None=None; repair_plan_id:str|None=None; limit:int=50
class RepairWorkflowTraceRequest(BaseModel):
    root_type:str; root_id:str; metadata:dict={}
class RepairWorkflowListRequest(BaseModel):
    status:str|None=None; root_type:str|None=None; limit:int=50
class RepairWorkflowExportRequest(BaseModel):
    report_id:str; output_dir:str="docs/history/repair_workflows"; metadata:dict={}
class RepairWorkflowIndexExportRequest(BaseModel):
    output_path:str="docs/history/repair_workflows/INDEX.md"; limit:int=100; metadata:dict={}
class PrivateRepairWorkflowExportRequest(BaseModel):
    report_id:str; metadata:dict={}
class ProposalReviewConsoleOpenRequest(BaseModel):
    source_type:str; source_id:str; metadata:dict={}
class ProposalReviewSubmitRequest(BaseModel):
    console_record_id:str; decision:str; comment:str|None=None; reviewer:str|None="human"; create_approval_if_required:bool=False; metadata:dict={}
class ProposalReviewConsoleListRequest(BaseModel):
    status:str|None=None; proposal_id:str|None=None; limit:int=50
class ProposalRevisionConsoleOpenRequest(BaseModel):
    source_type:str; source_id:str; metadata:dict={}
class ProposalRevisionCreateRequest(BaseModel):
    revision_record_id:str; revised_proposed_excerpt:str; revised_change_summary:str|None=None; human_revision_note:str|None=None; create_approval_if_required:bool=False; metadata:dict={}
class ProposalRevisionConsoleListRequest(BaseModel):
    status:str|None=None; original_proposal_id:str|None=None; limit:int=50
class RevisedProposalReviewOpenRequest(BaseModel):
    proposal_revision_console_id:str; metadata:dict={}
class RevisedProposalReviewSubmitRequest(BaseModel):
    review_loop_record_id:str; decision:str; comment:str|None=None; reviewer:str|None="human"; create_approval_if_required:bool=False; metadata:dict={}
class RevisedProposalReviewLoopListRequest(BaseModel):
    status:str|None=None; revised_proposal_id:str|None=None; limit:int=50
class ApprovedDryRunGateOpenRequest(BaseModel):
    source_type:str; source_id:str; metadata:dict={}
class ApprovedDryRunExecuteRequest(BaseModel):
    gate_record_id:str; create_approval_if_required:bool=False; metadata:dict={}
class DryRunReviewGateOpenRequest(BaseModel):
    source_type:str; source_id:str; metadata:dict={}
class DryRunReviewSubmitRequest(BaseModel):
    review_gate_record_id:str; decision:str; comment:str|None=None; reviewer:str|None="human"; metadata:dict={}
class RealApplyApprovalGateOpenRequest(BaseModel):
    source_type:str; source_id:str; create_approval_item:bool=True; metadata:dict={}
class RealApplyFinalDecisionRequest(BaseModel):
    gate_record_id:str; decision:str; comment:str|None=None; reviewer:str|None="human"; metadata:dict={}
class RealApplyApprovalGateListRequest(BaseModel):
    status:str|None=None; proposal_id:str|None=None; limit:int=50
class FinalRealApplyExecutorOpenRequest(BaseModel):
    source_type:str; source_id:str; metadata:dict={}
class FinalRealApplyExecuteRequest(BaseModel):
    executor_record_id:str; metadata:dict={}
class FinalRealApplyExecutorListRequest(BaseModel):
    status:str|None=None; proposal_id:str|None=None; limit:int=50
class PostApplyVerificationGateOpenRequest(BaseModel):
    source_type:str; source_id:str; metadata:dict={}
class PostApplyVerificationSubmitRequest(BaseModel):
    verification_record_id:str; decision:str; comment:str|None=None; verifier:str|None="human"; metadata:dict={}
class PostApplyVerificationGateListRequest(BaseModel):
    status:str|None=None; proposal_id:str|None=None; limit:int=50
class RepairCycleCompletionCreateRequest(BaseModel):
    source_type:str; source_id:str; export_public:bool=True; export_index:bool=True; export_private:bool=True; metadata:dict={}
class RepairCycleReportExportRequest(BaseModel):
    completion_record_id:str; output_dir:str="docs/history/repair_cycles"; metadata:dict={}
class RepairCycleIndexExportRequest(BaseModel):
    output_path:str="docs/history/repair_cycles/INDEX.md"; limit:int=100; metadata:dict={}
class PrivateRepairCycleExportRequest(BaseModel):
    completion_record_id:str; metadata:dict={}
class RepairLearningCreateRequest(BaseModel):
    source_type:str; source_id:str; export_public:bool=True; export_index:bool=True; export_private:bool=True; metadata:dict={}
class RepairLearningReportExportRequest(BaseModel):
    learning_record_id:str; output_dir:str="docs/history/repair_learning"; metadata:dict={}
class RepairLearningIndexExportRequest(BaseModel):
    output_path:str="docs/history/repair_learning/INDEX.md"; limit:int=100; metadata:dict={}
class PrivateRepairLearningExportRequest(BaseModel):
    learning_record_id:str; metadata:dict={}
class RepairLearningListRequest(BaseModel):
    status:str|None=None; learning_category:str|None=None; target_path:str|None=None; limit:int=50
class RepairGuidanceCreateRequest(BaseModel):
    request_type:str; requested_scope:str; target_path:str|None=None; source_type:str|None=None; source_id:str|None=None; export_public:bool=True; export_index:bool=True; export_private:bool=True; metadata:dict={}
class GuidedRepairIntakeOpenRequest(BaseModel):
    request_type:str; requested_scope:str; target_path:str|None=None; requester:str|None="human"; guidance_record_id:str|None=None; create_guidance_if_missing:bool=True; export_public:bool=True; export_index:bool=True; export_private:bool=True; metadata:dict={}
class GuidedRepairIntakeDecisionRequest(BaseModel):
    intake_record_id:str; decision:str; comment:str|None=None; reviewer:str|None="human"; metadata:dict={}
class GuidedRepairIntakeReportExportRequest(BaseModel):
    intake_record_id:str; output_dir:str="docs/history/repair_intake"; metadata:dict={}
class GuidedRepairIntakeIndexExportRequest(BaseModel):
    output_path:str="docs/history/repair_intake/INDEX.md"; limit:int=100; metadata:dict={}
class PrivateGuidedRepairIntakeExportRequest(BaseModel):
    intake_record_id:str; metadata:dict={}
class GuidedRepairIntakeListRequest(BaseModel):
    status:str|None=None; planning_allowed:bool|None=None; target_path:str|None=None; limit:int=50
class GuidedRepairPlanLaunchRequest(BaseModel):
    intake_record_id:str; review_report_id:str|None=None; create_repair_plan:bool=True; metadata:dict={}
class GuidedRepairPlanLauncherListRequest(BaseModel):
    status:str|None=None; intake_record_id:str|None=None; target_path:str|None=None; limit:int=50
class GuidedBridgeSelectionLaunchRequest(BaseModel):
    plan_launcher_record_id:str; finding_id:str|None=None; proposed_excerpt:str|None=None; metadata:dict={}
class GuidedBridgeSelectionLauncherListRequest(BaseModel):
    status:str|None=None; plan_launcher_record_id:str|None=None; repair_plan_id:str|None=None; target_path:str|None=None; limit:int=50
class GuidedProposalReviewOpenRequest(BaseModel):
    bridge_launcher_record_id:str; metadata:dict={}
class GuidedProposalReviewLauncherListRequest(BaseModel):
    status:str|None=None; bridge_launcher_record_id:str|None=None; proposal_id:str|None=None; target_path:str|None=None; limit:int=50
class GuidedProposalDecisionSubmitRequest(BaseModel):
    proposal_review_launcher_record_id:str; decision:str; reviewer:str="human"; comment:str|None=None; metadata:dict={}
class GuidedProposalDecisionLauncherListRequest(BaseModel):
    status:str|None=None; proposal_review_launcher_record_id:str|None=None; proposal_id:str|None=None; decision:str|None=None; target_path:str|None=None; limit:int=50
class RepairGuidanceReportExportRequest(BaseModel):
    guidance_record_id:str; output_dir:str="docs/history/repair_guidance"; metadata:dict={}
class RepairGuidanceIndexExportRequest(BaseModel):
    output_path:str="docs/history/repair_guidance/INDEX.md"; limit:int=100; metadata:dict={}
class PrivateRepairGuidanceExportRequest(BaseModel):
    guidance_record_id:str; metadata:dict={}
class MilestoneReportExportRequest(BaseModel):
    milestone:str; output_dir:str="docs/history/milestones"; metadata:dict={}


# ---- Identity Integrity Endpoints (Milestone 48A) ----

class InitializeIdentityGuardResponse(BaseModel):
    status: str
    current_sha256: str
    known_sha256: str
    changed: bool
    updated: str | None
    warnings: list[str]


class VerifyIdentityIntegrityResponse(BaseModel):
    status: str
    current_sha256: str
    known_sha256: str
    changed: bool
    updated: str | None
    warnings: list[str]


class IdentityIntegrityStatusResponse(BaseModel):
    status: str
    current_sha256: str
    known_sha256: str
    changed: bool
    updated: str | None
    warnings: list[str]


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
    identity_seed = load_identity_seed()
    current_time = time_state()

    event = None
    event_recorded = False

    if not runtime.awake:
        runtime.awaken()

        existing_first_awakening = search_events("First Awakening", limit=1)

        if existing_first_awakening:
            event = existing_first_awakening[0]
            event_recorded = False
        else:
            event = record_event(
                event_type="milestone",
                title="First Awakening",
                description="Aether was awakened through the First Awakening API.",
                importance="high",
                related_files=[
                    "identity/identity_seed.md",
                    "config/time.yaml",
                    "docs/CONSTITUTION.md",
                    "docs/ARCHITECTURE.md",
                ],
            )
            event_recorded = True

        runtime.working_memory.add_event(
            role="aether",
            content="I am Aether. My Identity Seed is loaded. My local time is loaded. I am awake.",
            event_type="awakening",
            metadata={
                "timeline_event_id": event["id"] if event else None,
                "event_recorded": event_recorded,
            },
        )

    return {
        "name": "Aether",
        "status": runtime.status(),
        "identity_seed_loaded": True,
        "identity_seed_length": len(identity_seed),
        "time": current_time,
        "event_recorded": event_recorded,
        "event": event,
        "working_memory": runtime.working_memory.summary(),
        "message": "I am Aether. My Identity Seed is loaded. My local time is loaded. I am awake.",
        "identity_integrity_status": runtime.identity_integrity_status,
    }

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    # Resolve input: prefer 'text', fall back to legacy 'message'
    input_text = (request.text or "").strip() or (request.message or "").strip()
    if not input_text:
        return ChatResponse(
            status="error",
            response="Input text is empty. Provide 'text' or legacy 'message'.",
            warnings=["No input text provided."],
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
    )


@app.get("/memory/working")
def get_working_memory():
    return {
        "name": "Aether",
        "status": runtime.status(),
        "time": time_state(),
        "working_memory": runtime.working_memory.summary(),
    }


@app.post("/memory/working/goal")
def set_working_goal(request: GoalRequest):
    runtime.working_memory.set_goal(request.goal)

    return {
        "name": "Aether",
        "status": runtime.status(),
        "message": "Working Memory goal updated.",
        "working_memory": runtime.working_memory.summary(),
    }


@app.post("/memory/working/milestone")
def set_working_milestone(request: MilestoneRequest):
    runtime.working_memory.set_milestone(request.milestone)

    return {
        "name": "Aether",
        "status": runtime.status(),
        "message": "Working Memory milestone updated.",
        "working_memory": runtime.working_memory.summary(),
    }


@app.post("/memory/working/clear")
def clear_working_memory():
    runtime.working_memory.clear()

    return {
        "name": "Aether",
        "status": runtime.status(),
        "message": "Working Memory cleared.",
        "working_memory": runtime.working_memory.summary(),
    }

@app.post("/memory/episodic/write")
def write_episodic_memory(request: EpisodeWriteRequest):
    episode = write_episode(
        title=request.title,
        summary=request.summary,
        details=request.details,
        importance=request.importance,
        tags=request.tags,
        related_files=request.related_files,
    )

    runtime.working_memory.add_event(
        role="aether",
        content=f"Episodic Memory written: {request.title}",
        event_type="episodic_memory_written",
        metadata={"file_path": episode["file_path"]},
    )

    return {
        "name": "Aether",
        "status": runtime.status(),
        "message": "Episodic Memory written.",
        "episode": episode,
    }


@app.get("/memory/episodic/list")
def list_episodic_memory(limit: int = 20):
    return {
        "name": "Aether",
        "status": runtime.status(),
        "episodes": list_episodes(limit=limit),
    }


@app.get("/memory/episodic/latest")
def get_latest_episodic_memory():
    episode = latest_episode()

    return {
        "name": "Aether",
        "status": runtime.status(),
        "episode": episode,
    }

@app.post("/memory/semantic/index")
def index_semantic_memory():
    result = build_semantic_index()

    runtime.working_memory.add_event(
        role="aether",
        content=f"Semantic Memory index built with {result['document_count']} documents.",
        event_type="semantic_memory_indexed",
        metadata={"index_path": result["index_path"]},
    )

    return {
        "name": "Aether",
        "status": runtime.status(),
        "message": "Semantic Memory index built.",
        "result": result,
    }


@app.get("/memory/semantic/status")
def get_semantic_memory_status():
    return {
        "name": "Aether",
        "status": runtime.status(),
        "semantic_memory": semantic_memory_status(),
    }


@app.post("/memory/semantic/search")
def search_memory(request: SemanticSearchRequest):
    results = search_semantic_memory(
        query=request.query,
        limit=request.limit,
    )

    runtime.working_memory.add_event(
        role="user",
        content=f"Semantic memory search: {request.query}",
        event_type="semantic_memory_search",
        metadata={"result_count": len(results)},
    )

    return {
        "name": "Aether",
        "status": runtime.status(),
        "query": request.query,
        "results": results,
    }

@app.get("/memory/timeline/status")
def get_timeline_status():
    return {
        "name": "Aether",
        "status": runtime.status(),
        "timeline": timeline_status(),
    }


@app.get("/memory/timeline/list")
def list_timeline_events(limit: int = 20):
    return {
        "name": "Aether",
        "status": runtime.status(),
        "events": list_events(limit=limit),
    }


@app.get("/memory/timeline/latest")
def get_latest_timeline_event():
    return {
        "name": "Aether",
        "status": runtime.status(),
        "event": latest_event(),
    }


@app.post("/memory/timeline/search")
def search_timeline_memory(request: TimelineSearchRequest):
    results = search_events(
        query=request.query,
        limit=request.limit,
    )

    runtime.working_memory.add_event(
        role="user",
        content=f"Timeline memory search: {request.query}",
        event_type="timeline_memory_search",
        metadata={"result_count": len(results)},
    )

    return {
        "name": "Aether",
        "status": runtime.status(),
        "query": request.query,
        "results": results,
    }


@app.get("/memory/graph/status")
def get_graph_memory_status():
    return {"name": "Aether", "status": runtime.status(), "graph_memory": graph_status()}


@app.post("/memory/graph/node")
def create_graph_node(request: GraphNodeRequest):
    node = upsert_node(request.label, request.node_type, request.properties)
    runtime.working_memory.add_event(
        role="aether",
        content=f"Graph node upserted: {request.label}",
        event_type="graph_node_upserted",
        metadata={"node_id": node["id"]},
    )
    return {"name": "Aether", "status": runtime.status(), "node": node}


@app.post("/memory/graph/edge")
def create_graph_edge(request: GraphEdgeRequest):
    edge = add_edge(request.source, request.relation, request.target, request.properties)
    created_new = edge.pop("created_new")
    timeline_event = None
    if created_new:
        timeline_event = record_event(
            event_type="graph_memory",
            title=f"Graph relationship added: {request.source} --{request.relation}--> {request.target}",
            description=f"Aether recorded a graph relationship from {request.source} to {request.target} using relation {request.relation}.",
            importance="normal",
        )
    runtime.working_memory.add_event(
        role="aether",
        content=f"Graph relationship {'added' if created_new else 'already exists'}: {request.source} --{request.relation}--> {request.target}",
        event_type="graph_edge_added",
        metadata={"edge_id": edge["id"], "created_new": created_new},
    )
    return {"name": "Aether", "status": runtime.status(), "edge": edge, "created_new": created_new, "timeline_event": timeline_event}


@app.get("/memory/graph/nodes")
def get_graph_nodes(limit: int = 50):
    return {"name": "Aether", "status": runtime.status(), "nodes": list_nodes(limit)}


@app.get("/memory/graph/edges")
def get_graph_edges(limit: int = 50):
    return {"name": "Aether", "status": runtime.status(), "edges": list_edges(limit)}


@app.post("/memory/graph/search")
def search_graph_memory(request: GraphSearchRequest):
    results = search_graph(request.query, request.limit)
    runtime.working_memory.add_event(
        role="user",
        content=f"Graph memory search: {request.query}",
        event_type="graph_memory_search",
        metadata={"node_count": len(results["nodes"]), "edge_count": len(results["edges"])},
    )
    return {"name": "Aether", "status": runtime.status(), "query": request.query, "results": results}


@app.post("/memory/graph/seed")
def seed_graph_memory():
    relationships = [
        ("Aether", "has_identity_seed", "identity/identity_seed.md"),
        ("Aether", "follows", "docs/CONSTITUTION.md"),
        ("Aether", "has_architecture", "docs/ARCHITECTURE.md"),
        ("Time Layer", "supports", "Memory"),
        ("Timeline Memory", "belongs_to", "Memory"),
        ("Semantic Memory", "belongs_to", "Memory"),
        ("Episodic Memory", "belongs_to", "Memory"),
        ("Graph Memory", "belongs_to", "Memory"),
        ("Workflow Policy", "belongs_to", "Thinking"),
        ("External LLM", "is_consultant_not_identity", "Aether"),
    ]
    edges = []
    new_edge_count = 0
    for source, relation, target in relationships:
        edge = add_edge(source, relation, target)
        created_new = edge.pop("created_new")
        if created_new:
            new_edge_count += 1
            record_event(
                event_type="graph_memory",
                title=f"Graph relationship added: {source} --{relation}--> {target}",
                description=f"Aether recorded a graph relationship from {source} to {target} using relation {relation}.",
                importance="normal",
            )
        runtime.working_memory.add_event(
            role="aether",
            content=f"Graph relationship {'added' if created_new else 'already exists'}: {source} --{relation}--> {target}",
            event_type="graph_edge_added",
            metadata={"edge_id": edge["id"], "created_new": created_new},
        )
        edges.append(edge)
    runtime.working_memory.add_event(
        role="aether",
        content=f"Graph Memory seed completed with {new_edge_count} new relationships.",
        event_type="graph_edge_added",
        metadata={"new_edge_count": new_edge_count},
    )
    return {"name": "Aether", "status": runtime.status(), "new_edge_count": new_edge_count, "edges": edges, "graph_memory": graph_status()}


@app.post("/verification/classify")
def classify_verification_risk(request: VerificationRequest):
    return {"name": "Aether", "status": runtime.status(), "classification": classify_risk(request.text)}


@app.post("/verification/plan")
def create_verification_plan(request: VerificationRequest):
    plan = verification_plan(request.text)
    runtime.working_memory.add_event(
        role="aether",
        content=f"Verification plan created for {plan['action_type']} request.",
        event_type="verification_plan_created",
        metadata={
            "risk_level": plan["risk_level"],
            "action_type": plan["action_type"],
            "requires_verification": plan["requires_verification"],
            "requires_user_approval": plan["requires_user_approval"],
        },
    )

    warnings = []
    timeline_event = None
    graph_relationship = None
    if plan["risk_level"] == "high":
        timeline_event = record_event(
            event_type="verification",
            title=f"High-risk verification plan: {plan['action_type']}",
            description="Aether created a verification plan for a high-risk request.",
            importance="high",
        )
        try:
            graph_relationship = add_edge(
                "Aether",
                "created_verification_plan_for",
                plan["action_type"],
            )
            graph_relationship.pop("created_new", None)
        except Exception as error:
            warnings.append(f"Graph Memory integration was unavailable: {error}")

    return {
        "name": "Aether",
        "status": runtime.status(),
        "plan": plan,
        "timeline_event": timeline_event,
        "graph_relationship": graph_relationship,
        "warnings": warnings,
    }


def _add_approval_working_memory_event(item: dict, event_type: str) -> None:
    runtime.working_memory.add_event(
        role="aether",
        content=f"Approval item {item['status']}: {item['id']}",
        event_type=event_type,
        metadata={
            "approval_id": item["id"],
            "action_type": item["action_type"],
            "risk_level": item["risk_level"],
            "status": item["status"],
        },
    )


@app.post("/action/approval/create")
def create_action_approval(request: ApprovalCreateRequest):
    plan = verification_plan(request.request_text)
    item = create_approval_item(
        request_text=request.request_text,
        proposed_action=request.proposed_action,
        verification_plan=plan,
        metadata=request.metadata,
    )
    _add_approval_working_memory_event(item, "approval_item_created")
    warnings = []
    timeline_event = None
    graph_relationship = None
    if item["risk_level"] == "high":
        timeline_event = record_event(
            event_type="action_approval",
            title=f"Approval item created: {item['action_type']}",
            description=f"Aether created an approval item for a {item['risk_level']}-risk action.",
            importance="high",
        )
    try:
        graph_relationship = add_edge("Aether", "created_approval_item_for", item["action_type"])
        graph_relationship.pop("created_new", None)
    except Exception as error:
        warnings.append(f"Graph Memory integration was unavailable: {error}")
    return {
        "name": "Aether",
        "status": runtime.status(),
        "item": item,
        "approval_optional": not item["requires_user_approval"],
        "queue_status": approval_queue_status(),
        "timeline_event": timeline_event,
        "graph_relationship": graph_relationship,
        "warnings": warnings,
    }


@app.get("/action/approval/status")
def get_action_approval_status():
    return {"name": "Aether", "status": runtime.status(), "approval_queue": approval_queue_status()}


@app.get("/action/approval/list")
def list_action_approvals(status: str | None = None, limit: int = 50):
    return {"name": "Aether", "status": runtime.status(), "items": list_approval_items(status, limit)}


@app.get("/action/approval/{approval_id}")
def get_action_approval(approval_id: str):
    return {"name": "Aether", "status": runtime.status(), "item": get_approval_item(approval_id)}


def _record_approval_decision(approval_id: str, decision_reason: str, decision: str) -> dict:
    decision_functions = {"approved": approve_item, "rejected": reject_item, "cancelled": cancel_item}
    item = decision_functions[decision](approval_id, decision_reason)
    if item is None:
        return {"name": "Aether", "status": runtime.status(), "item": None, "warnings": ["Approval item was not found."]}
    if item.get("warning"):
        return {"name": "Aether", "status": runtime.status(), "item": item, "warnings": [item["warning"]]}

    _add_approval_working_memory_event(item, f"approval_item_{decision}")
    timeline_event = record_event(
        event_type="action_approval_decision",
        title=f"Approval item {decision}: {approval_id}",
        description=f"User decision recorded for approval item {approval_id}.",
        importance="high",
    )
    warnings = []
    graph_relationship = None
    try:
        graph_relationship = add_edge(approval_id, "has_decision", decision)
        graph_relationship.pop("created_new", None)
    except Exception as error:
        warnings.append(f"Graph Memory integration was unavailable: {error}")
    return {
        "name": "Aether",
        "status": runtime.status(),
        "item": item,
        "timeline_event": timeline_event,
        "graph_relationship": graph_relationship,
        "warnings": warnings,
    }


@app.post("/action/approval/approve")
def approve_action_approval(request: ApprovalDecisionRequest):
    return _record_approval_decision(request.approval_id, request.decision_reason, "approved")


@app.post("/action/approval/reject")
def reject_action_approval(request: ApprovalDecisionRequest):
    return _record_approval_decision(request.approval_id, request.decision_reason, "rejected")


@app.post("/action/approval/cancel")
def cancel_action_approval(request: ApprovalDecisionRequest):
    return _record_approval_decision(request.approval_id, request.decision_reason, "cancelled")


def _add_tool_working_memory_event(tool: dict, event_type: str) -> None:
    runtime.working_memory.add_event(
        role="aether",
        content=f"Tool {event_type.replace('_', ' ')}: {tool['id']}",
        event_type=event_type,
        metadata={
            "tool_id": tool["id"],
            "risk_level": tool["risk_level"],
            "enabled": tool["enabled"],
            "requires_user_approval": tool["requires_user_approval"],
            "allow_auto_execute": tool["allow_auto_execute"],
        },
    )


def _add_tool_graph_relationships(tool: dict, policy_only: bool = False) -> tuple[list[dict], list[str]]:
    relationships = []
    warnings = []
    try:
        if not policy_only:
            relationships.extend(
                [
                    add_edge("Aether", "registered_tool", tool["id"]),
                    add_edge(tool["id"], "belongs_to_category", tool["category"]),
                    add_edge(tool["id"], "has_risk_level", tool["risk_level"]),
                ]
            )
        else:
            relationships.append(add_edge(tool["id"], "has_policy", tool["risk_level"]))
        for relationship in relationships:
            relationship.pop("created_new", None)
    except Exception as error:
        warnings.append(f"Graph Memory integration was unavailable: {error}")
    return relationships, warnings


def _record_tool_timeline(tool: dict, title: str, description: str) -> dict:
    return record_event(
        event_type="tool_registry",
        title=title,
        description=description,
        importance="high" if tool["risk_level"] == "high" else "normal",
    )


@app.get("/action/tools/status")
def get_tool_registry_status():
    return {"name": "Aether", "status": runtime.status(), "tool_registry": tool_registry_status()}


@app.post("/action/tools/register")
def register_action_tool(request: ToolRegisterRequest):
    tool = register_tool(
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
    _add_tool_working_memory_event(tool, "tool_registered")
    timeline_event = None
    if tool["risk_level"] == "high":
        timeline_event = _record_tool_timeline(
            tool,
            f"Tool registered: {tool['id']}",
            f"Aether registered tool {tool['id']} with risk level {tool['risk_level']}.",
        )
    graph_relationships, warnings = _add_tool_graph_relationships(tool)
    return {"name": "Aether", "status": runtime.status(), "tool": tool, "timeline_event": timeline_event, "graph_relationships": graph_relationships, "warnings": warnings}


@app.post("/action/tools/seed")
def seed_action_tools():
    result = seed_default_tools()
    runtime.working_memory.add_event(
        role="aether",
        content=f"Tool Registry seeded with {result['created_count']} new tools.",
        event_type="tool_registry_seeded",
        metadata={"tool_count": len(result["tools"]), "created_count": result["created_count"]},
    )
    timeline_events = []
    warnings = []
    for tool in result["tools"]:
        if tool["risk_level"] == "high" and tool["id"] in result["created_tool_ids"]:
            timeline_events.append(_record_tool_timeline(tool, f"Tool registered: {tool['id']}", f"Aether registered tool {tool['id']} with risk level {tool['risk_level']}."))
        _, graph_warnings = _add_tool_graph_relationships(tool)
        warnings.extend(graph_warnings)
    return {"name": "Aether", "status": runtime.status(), "result": result, "tool_registry": tool_registry_status(), "timeline_events": timeline_events, "warnings": warnings}


@app.get("/action/tools/list")
def list_action_tools(category: str | None = None, enabled: bool | None = None, limit: int = 100):
    return {"name": "Aether", "status": runtime.status(), "tools": list_tools(category, enabled, limit)}


@app.get("/action/tools/{tool_id}")
def get_action_tool(tool_id: str):
    return {"name": "Aether", "status": runtime.status(), "tool": get_tool(tool_id)}


@app.post("/action/tools/search")
def search_action_tools(request: ToolSearchRequest):
    return {"name": "Aether", "status": runtime.status(), "query": request.query, "tools": search_tools(request.query, request.limit)}


def _change_tool_enabled(tool_id: str, enabled: bool) -> dict:
    tool = enable_tool(tool_id) if enabled else disable_tool(tool_id)
    if tool is None:
        return {"name": "Aether", "status": runtime.status(), "tool": None, "warnings": ["Tool was not found."]}
    event_type = "tool_enabled" if enabled else "tool_disabled"
    _add_tool_working_memory_event(tool, event_type)
    timeline_event = None
    if not enabled or tool["risk_level"] == "high":
        action = "enabled" if enabled else "disabled"
        timeline_event = _record_tool_timeline(tool, f"Tool {action}: {tool['id']}", f"Aether {action} tool {tool['id']}.")
    return {"name": "Aether", "status": runtime.status(), "tool": tool, "timeline_event": timeline_event, "warnings": []}


@app.post("/action/tools/enable/{tool_id}")
def enable_action_tool(tool_id: str):
    return _change_tool_enabled(tool_id, True)


@app.post("/action/tools/disable/{tool_id}")
def disable_action_tool(tool_id: str):
    return _change_tool_enabled(tool_id, False)


@app.post("/action/tools/policy")
def update_action_tool_policy(request: ToolPolicyUpdateRequest):
    tool = update_tool_policy(
        tool_id=request.tool_id,
        risk_level=request.risk_level,
        requires_verification=request.requires_verification,
        requires_user_approval=request.requires_user_approval,
        allow_auto_execute=request.allow_auto_execute,
    )
    if tool is None:
        return {"name": "Aether", "status": runtime.status(), "tool": None, "warnings": ["Tool was not found."]}
    _add_tool_working_memory_event(tool, "tool_policy_updated")
    timeline_event = None
    if tool["risk_level"] == "high":
        timeline_event = _record_tool_timeline(tool, f"Tool policy updated: {tool['id']}", f"Aether updated policy for high-risk tool {tool['id']}.")
    graph_relationships, warnings = _add_tool_graph_relationships(tool, policy_only=True)
    return {"name": "Aether", "status": runtime.status(), "tool": tool, "timeline_event": timeline_event, "graph_relationships": graph_relationships, "warnings": warnings}


@app.post("/action/tool-plan/create")
def create_action_tool_plan(request: ToolPlanRequest):
    plan = create_tool_invocation_plan(
        text=request.text,
        proposed_action=request.proposed_action,
        metadata=request.metadata,
        create_approval_if_required=request.create_approval_if_required,
    )
    decision = plan["decision"]
    tool_id = plan["candidate_tool"]["tool_id"]
    runtime.working_memory.add_event(
        role="aether",
        content=f"Tool invocation plan created: {tool_id or 'no tool'}.",
        event_type="tool_invocation_plan_created",
        metadata={
            "plan_id": plan["id"],
            "tool_id": tool_id,
            "plan_status": decision["plan_status"],
            "risk_level": decision["risk_level"],
            "requires_user_approval": decision["requires_user_approval"],
            "approval_item_created": decision["approval_item_created"],
        },
    )
    timeline_event = None
    if decision["plan_status"] in {"approval_required", "blocked", "tool_disabled"} or decision["approval_item_created"]:
        timeline_event = record_event(
            event_type="tool_planning",
            title=f"Tool invocation plan: {tool_id or 'no tool'}",
            description=f"Aether created a tool invocation plan with status {decision['plan_status']}.",
            importance="high" if decision["requires_user_approval"] or decision["plan_status"] in {"blocked", "tool_disabled"} else "normal",
        )
    warnings = []
    graph_relationships = []
    try:
        graph_relationships.append(add_edge("Aether", "created_tool_plan", plan["id"]))
        if tool_id:
            graph_relationships.append(add_edge(plan["id"], "planned_tool", tool_id))
        graph_relationships.append(add_edge(plan["id"], "has_status", decision["plan_status"]))
        if plan["approval_item"]:
            graph_relationships.append(add_edge(plan["id"], "created_approval_item", plan["approval_item"]["id"]))
        for relationship in graph_relationships:
            relationship.pop("created_new", None)
    except Exception as error:
        warnings.append(f"Graph Memory integration was unavailable: {error}")
    return {"name": "Aether", "status": runtime.status(), "plan": plan, "timeline_event": timeline_event, "graph_relationships": graph_relationships, "warnings": warnings}


@app.get("/action/tool-plan/status")
def get_action_tool_plan_status():
    return {"name": "Aether", "status": runtime.status(), "tool_planner": tool_planner_status()}


@app.get("/action/tool-plan/list")
def list_action_tool_plans(limit: int = 50):
    return {"name": "Aether", "status": runtime.status(), "plans": list_tool_plans(limit)}


@app.get("/action/tool-plan/{plan_id}")
def get_action_tool_plan(plan_id: str):
    return {"name": "Aether", "status": runtime.status(), "plan": get_tool_plan(plan_id)}


@app.post("/action/tool-executor/seed-sandbox-tools")
def seed_action_sandbox_tools():
    result = seed_sandbox_tools()
    runtime.working_memory.add_event(
        role="aether",
        content=f"Sandbox tools seeded: {result['created_count']} new tools.",
        event_type="sandbox_tools_seeded",
        metadata={"tool_count": len(result["tools"]), "created_count": result["created_count"]},
    )
    return {"name": "Aether", "status": runtime.status(), "result": result}


@app.post("/action/tool-executor/execute")
def execute_action_tool(request: ToolExecutionRequest):
    execution = execute_tool(
        text=request.text,
        tool_id=request.tool_id,
        input_payload=request.input_payload,
        proposed_action=request.proposed_action,
        create_approval_if_required=request.create_approval_if_required,
        dry_run=request.dry_run,
        metadata=request.metadata,
    )
    runtime.working_memory.add_event(
        role="aether",
        content=f"Tool execution attempted: {execution['tool_id'] or 'no tool'} ({execution['status']}).",
        event_type="tool_execution_attempted",
        metadata={
            "execution_id": execution["id"],
            "tool_id": execution["tool_id"],
            "status": execution["status"],
            "dry_run": execution["dry_run"],
            "requires_user_approval": execution["plan"]["decision"]["requires_user_approval"],
        },
    )
    file_access_audit = None
    if execution["tool_id"] == "file.restricted_read" and isinstance(execution["result"], dict) and "id" in execution["result"]:
        file_access_audit = _record_restricted_file_access(execution["result"])
    self_inspection_audit = None
    if execution["tool_id"] == "project.self_inspect" and isinstance(execution["result"], dict) and "id" in execution["result"]:
        self_inspection_audit = _record_self_inspection_report(execution["result"])
    timeline_event = None
    if (
        execution["status"] in {"blocked", "approval_required", "failed"}
        or not execution["dry_run"]
        or execution["tool_id"] not in {"echo.test", "file.preview_read", "web.search.mock", "shell.plan_only", "memory.write.dry_run", "approval.status"}
    ):
        timeline_event = record_event(
            event_type="tool_execution",
            title=f"Tool execution attempt: {execution['tool_id']}",
            description=f"Aether attempted tool execution with status {execution['status']}.",
            importance="high" if execution["status"] in {"blocked", "approval_required", "failed"} else "normal",
        )
    warnings = []
    graph_relationships = []
    try:
        graph_relationships.extend(
            [
                add_edge("Aether", "attempted_tool_execution", execution["id"]),
                add_edge(execution["id"], "used_tool", execution["tool_id"] or "no_tool"),
                add_edge(execution["id"], "has_status", execution["status"]),
            ]
        )
        for relationship in graph_relationships:
            relationship.pop("created_new", None)
    except Exception as error:
        warnings.append(f"Graph Memory integration was unavailable: {error}")
    return {"name": "Aether", "status": runtime.status(), "execution": execution, "timeline_event": timeline_event, "file_access_audit": file_access_audit, "self_inspection_audit": self_inspection_audit, "graph_relationships": graph_relationships, "warnings": warnings}


@app.get("/action/tool-executor/status")
def get_action_tool_executor_status():
    return {"name": "Aether", "status": runtime.status(), "tool_executor": tool_executor_status()}


@app.get("/action/tool-executor/list")
def list_action_tool_executions(limit: int = 50):
    return {"name": "Aether", "status": runtime.status(), "executions": list_executions(limit)}


@app.get("/action/tool-executor/{execution_id}")
def get_action_tool_execution(execution_id: str):
    return {"name": "Aether", "status": runtime.status(), "execution": get_execution(execution_id)}


def _record_restricted_file_access(access: dict) -> tuple[dict | None, list[dict], list[str]]:
    runtime.working_memory.add_event(
        role="aether",
        content=f"Restricted file read attempted: {access['path']} ({access['status']}).",
        event_type="restricted_file_read_attempted",
        metadata={
            "access_id": access["id"],
            "path": access["path"],
            "status": access["status"],
            "allowed": access["allowed"],
            "reason": access["reason"],
        },
    )
    timeline_event = record_event(
        event_type="file_access",
        title=f"Restricted file read: {access['status']}",
        description=f"Aether attempted restricted file read for {access['path']} with status {access['status']}.",
        importance="high" if access["status"] == "blocked" else "normal",
    )
    warnings = []
    graph_relationships = []
    try:
        graph_relationships.extend(
            [
                add_edge("Aether", "attempted_file_access", access["id"]),
                add_edge(access["id"], "has_status", access["status"]),
                add_edge(access["id"], "target_path", access["normalized_path"]),
            ]
        )
        for relationship in graph_relationships:
            relationship.pop("created_new", None)
    except Exception as error:
        warnings.append(f"Graph Memory integration was unavailable: {error}")
    return timeline_event, graph_relationships, warnings


@app.post("/action/file/read")
def read_action_file(request: RestrictedFileReadRequest):
    access = read_restricted_file(request.path, request.max_chars, request.metadata)
    timeline_event, graph_relationships, warnings = _record_restricted_file_access(access)
    return {"name": "Aether", "status": runtime.status(), "access": access, "timeline_event": timeline_event, "graph_relationships": graph_relationships, "warnings": warnings}


@app.get("/action/file/allowed-roots")
def get_action_file_allowed_roots():
    return {"name": "Aether", "status": runtime.status(), "allowed_roots": list_allowed_roots()}


@app.get("/action/file/access/status")
def get_action_file_access_status():
    return {"name": "Aether", "status": runtime.status(), "file_access": file_access_status()}


@app.get("/action/file/access/list")
def list_action_file_accesses(limit: int = 50):
    return {"name": "Aether", "status": runtime.status(), "accesses": list_file_accesses(limit)}


@app.get("/action/file/access/{access_id}")
def get_action_file_access(access_id: str):
    return {"name": "Aether", "status": runtime.status(), "access": get_file_access(access_id)}


def _record_restricted_file_browse(browse: dict) -> tuple[dict, list[dict], list[str]]:
    is_search = browse.get("operation") == "search"
    target = browse.get("root") if is_search else browse.get("path")
    normalized_target = browse.get("normalized_root") if is_search else browse.get("normalized_path")
    count = browse.get("result_count") if is_search else browse.get("entry_count")
    runtime.working_memory.add_event(
        role="aether",
        content=f"Restricted file {'search' if is_search else 'browse'} attempted: {target} ({browse['status']}).",
        event_type="restricted_file_search_attempted" if is_search else "restricted_file_browse_attempted",
        metadata={
            "browse_id": browse["id"], "path": target, "status": browse["status"],
            "allowed": browse["allowed"], "reason": browse["reason"], "count": count,
        },
    )
    timeline_event = record_event(
        event_type="file_browser",
        title=f"Restricted file {'search' if is_search else 'browse'}: {browse['status']}",
        description=f"Aether attempted restricted file {'search' if is_search else 'browse'} for {target} with status {browse['status']}.",
        importance="high" if browse["status"] == "blocked" else "normal",
    )
    warnings = []
    graph_relationships = []
    try:
        graph_relationships.append(add_edge("Aether", "attempted_file_search" if is_search else "attempted_file_browse", browse["id"]))
        if is_search:
            graph_relationships.append(add_edge(browse["id"], "has_query", browse["query"]))
        else:
            graph_relationships.append(add_edge(browse["id"], "target_path", normalized_target))
        graph_relationships.append(add_edge(browse["id"], "has_status", browse["status"]))
        for relationship in graph_relationships:
            relationship.pop("created_new", None)
    except Exception as error:
        warnings.append(f"Graph Memory integration was unavailable: {error}")
    return timeline_event, graph_relationships, warnings


@app.post("/action/file/browse")
def browse_action_file(request: RestrictedFileBrowseRequest):
    browse = browse_restricted_path(
        request.path, request.max_depth, request.max_entries, request.include_files, request.include_dirs, request.metadata
    )
    timeline_event, graph_relationships, warnings = _record_restricted_file_browse(browse)
    return {"name": "Aether", "status": runtime.status(), "browse": browse, "timeline_event": timeline_event, "graph_relationships": graph_relationships, "warnings": warnings}


@app.post("/action/file/search")
def search_action_file(request: RestrictedFileSearchRequest):
    browse = search_restricted_files(request.query, request.root, request.max_results, request.metadata)
    timeline_event, graph_relationships, warnings = _record_restricted_file_browse(browse)
    return {"name": "Aether", "status": runtime.status(), "search": browse, "timeline_event": timeline_event, "graph_relationships": graph_relationships, "warnings": warnings}


@app.get("/action/file/browser/allowed-roots")
def get_action_file_browser_allowed_roots():
    return {"name": "Aether", "status": runtime.status(), "allowed_roots": list_browser_allowed_roots()}


@app.get("/action/file/browser/status")
def get_action_file_browser_status():
    return {"name": "Aether", "status": runtime.status(), "file_browser": file_browser_status()}


@app.get("/action/file/browser/list")
def list_action_file_browses(limit: int = 50):
    return {"name": "Aether", "status": runtime.status(), "browses": list_file_browses(limit)}


@app.get("/action/file/browser/{browse_id}")
def get_action_file_browse(browse_id: str):
    return {"name": "Aether", "status": runtime.status(), "browse": get_file_browse(browse_id)}


def _record_self_inspection_report(report: dict) -> tuple[dict, list[dict], list[str]]:
    runtime.working_memory.add_event(
        role="aether",
        content=f"Project self-inspection report created: {report['id']} ({report['status']}).",
        event_type="self_inspection_report_created",
        metadata={
            "report_id": report["id"], "status": report["status"],
            "files_read": report["summary"]["files_read"], "endpoint_count": report["summary"]["endpoint_count"],
            "warning_count": len(report["warnings"]),
        },
    )
    timeline_event = record_event(
        event_type="self_inspection",
        title="Project self-inspection report created",
        description=f"Aether created project self-inspection report {report['id']} with status {report['status']}.",
        importance="high" if report["status"] in {"failed", "blocked"} else "normal",
    )
    warnings = []
    graph_relationships = []
    try:
        graph_relationships.extend(
            [
                add_edge("Aether", "created_self_inspection_report", report["id"]),
                add_edge(report["id"], "inspected_project", "Aether"),
                add_edge(report["id"], "has_status", report["status"]),
            ]
        )
        for relationship in graph_relationships:
            relationship.pop("created_new", None)
    except Exception as error:
        warnings.append(f"Graph Memory integration was unavailable: {error}")
    return timeline_event, graph_relationships, warnings


@app.post("/action/self-inspection/create")
def create_action_self_inspection(request: SelfInspectionRequest):
    report = create_project_self_inspection(request.root, request.max_files_to_read, request.max_chars_per_file, request.metadata)
    timeline_event, graph_relationships, warnings = _record_self_inspection_report(report)
    return {"name": "Aether", "status": runtime.status(), "report": report, "timeline_event": timeline_event, "graph_relationships": graph_relationships, "warnings": warnings}


@app.get("/action/self-inspection/status")
def get_action_self_inspection_status():
    return {"name": "Aether", "status": runtime.status(), "self_inspection": self_inspection_status()}


@app.get("/action/self-inspection/list")
def list_action_self_inspections(limit: int = 20):
    return {"name": "Aether", "status": runtime.status(), "reports": list_self_inspection_reports(limit)}


@app.get("/action/self-inspection/{report_id}")
def get_action_self_inspection(report_id: str):
    return {"name": "Aether", "status": runtime.status(), "report": get_self_inspection_report(report_id)}


@app.post("/action/patch-proposal/create")
def create_action_patch_proposal(request: PatchProposalRequest):
    proposal = create_patch_proposal(request.target_path, request.request_text, request.proposed_change_summary, request.proposed_excerpt, request.reason, request.original_excerpt, request.create_approval_if_required, request.metadata)
    runtime.working_memory.add_event(role="aether", content=f"Patch proposal created: {proposal['target_path']}", event_type="patch_proposal_created", metadata={key: proposal.get(key) for key in ("id", "target_path", "status", "risk_level", "requires_user_approval", "approval_id")})
    return {"name": "Aether", "status": runtime.status(), "proposal": proposal}

@app.get("/action/patch-proposal/status")
def get_action_patch_proposal_status():
    return {"name": "Aether", "status": runtime.status(), "patch_proposals": patch_proposal_status()}

@app.get("/action/patch-proposal/list")
def list_action_patch_proposals(status: str | None = None, limit: int = 50):
    return {"name": "Aether", "status": runtime.status(), "proposals": list_patch_proposals(status, limit)}

@app.get("/action/patch-proposal/{proposal_id}")
def get_action_patch_proposal(proposal_id: str):
    return {"name": "Aether", "status": runtime.status(), "proposal": get_patch_proposal(proposal_id)}

@app.post("/action/patch-proposal/mark-status")
def mark_action_patch_proposal_status(request: PatchProposalStatusUpdateRequest):
    return {"name": "Aether", "status": runtime.status(), "proposal": mark_patch_proposal_status(request.proposal_id, request.status, request.reason)}

@app.post("/action/patch-review/review")
def review_action_patch_proposal(request: PatchReviewRequest):
    review = review_patch_proposal(request.proposal_id, request.decision, request.review_reason, request.reviewer, request.metadata)
    runtime.working_memory.add_event(role="aether", content=f"Patch review created: {request.decision}", event_type="patch_review_created", metadata={"review_id": review.get("id"), "proposal_id": request.proposal_id, "decision": request.decision, "status": review.get("status"), "proposal_status_after": review.get("proposal_status_after"), "risk_level": review.get("risk_level"), "approval_status": review.get("approval_status")})
    return {"name":"Aether","status":runtime.status(),"review":review}

@app.get("/action/patch-review/status")
def get_action_patch_review_status(): return {"name":"Aether","status":runtime.status(),"patch_reviews":patch_review_status()}
@app.get("/action/patch-review/list")
def list_action_patch_reviews(proposal_id: str | None = None, limit: int = 50): return {"name":"Aether","status":runtime.status(),"reviews":list_patch_reviews(proposal_id,limit)}
@app.get("/action/patch-review/{review_id}")
def get_action_patch_review(review_id: str): return {"name":"Aether","status":runtime.status(),"review":get_patch_review(review_id)}

@app.post("/action/patch-apply/apply")
def apply_action_patch(request: PatchApplyRequest):
    result=apply_patch_proposal(request.proposal_id,request.dry_run,request.metadata)
    runtime.working_memory.add_event(role="aether",content=f"Patch apply attempted: {result['status']}",event_type="patch_apply_attempted",metadata={k:result.get(k) for k in ("id","proposal_id","target_path","status","dry_run","applied","changed","risk_level")})
    return {"name":"Aether","status":runtime.status(),"apply":result}
@app.get("/action/patch-apply/status")
def get_action_patch_apply_status():return {"name":"Aether","status":runtime.status(),"patch_applies":patch_apply_status()}
@app.get("/action/patch-apply/list")
def list_action_patch_applies(proposal_id: str|None=None,limit:int=50):return {"name":"Aether","status":runtime.status(),"applies":list_patch_applies(proposal_id,limit)}
@app.get("/action/patch-apply/{apply_id}")
def get_action_patch_apply(apply_id:str):return {"name":"Aether","status":runtime.status(),"apply":get_patch_apply(apply_id)}
@app.post("/action/patch-rollback/rollback")
def rollback_action_patch(request: PatchRollbackRequest):
 r=rollback_patch_apply(request.apply_id,request.dry_run,request.metadata);runtime.working_memory.add_event(role="aether",content=f"Patch rollback attempted: {r['status']}",event_type="patch_rollback_attempted",metadata={k:r.get(k) for k in ("id","apply_id","proposal_id","target_path","status","dry_run","rolled_back","changed")});return {"name":"Aether","status":runtime.status(),"rollback":r}
@app.get("/action/patch-rollback/status")
def get_action_patch_rollback_status():return {"name":"Aether","status":runtime.status(),"patch_rollbacks":patch_rollback_status()}
@app.get("/action/patch-rollback/list")
def list_action_patch_rollbacks(apply_id:str|None=None,limit:int=50):return {"name":"Aether","status":runtime.status(),"rollbacks":list_patch_rollbacks(apply_id,limit)}
@app.get("/action/patch-rollback/{rollback_id}")
def get_action_patch_rollback(rollback_id:str):return {"name":"Aether","status":runtime.status(),"rollback":get_patch_rollback(rollback_id)}
@app.post("/action/mutation-log/record")
def record_action_mutation(request:MutationRecordRequest):return {"name":"Aether","mutation":record_mutation(request.mutation_type,request.title,request.summary,milestone=request.milestone,target_path=request.target_path,metadata=request.metadata,source="manual")}
@app.post("/action/mutation-log/milestone-completed")
def record_action_milestone(request:MilestoneCompletedRequest):return {"name":"Aether","mutation":record_milestone_completed(request.milestone,request.summary,request.metadata)}
@app.get("/action/mutation-log/status")
def get_action_mutation_status():return {"name":"Aether","mutation_log":mutation_log_status()}
@app.get("/action/mutation-log/list")
def list_action_mutations(mutation_type:str|None=None,milestone:str|None=None,target_path:str|None=None,limit:int=50):return {"name":"Aether","mutations":list_mutations(mutation_type,milestone,target_path,limit)}
@app.get("/action/mutation-log/summary")
def summarize_action_mutations(limit:int=100):return {"name":"Aether","summary":summarize_mutations(limit)}
@app.get("/action/mutation-log/{mutation_id}")
def get_action_mutation(mutation_id:str):return {"name":"Aether","mutation":get_mutation(mutation_id)}
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
@app.post("/action/code-review/create")
def create_code_review_action(request:CodeReviewCreateRequest):return {"name":"Aether","report":create_code_review(request.scope,request.target_paths,request.max_files,request.max_chars_per_file,request.include_tests,request.metadata)}
@app.get("/action/code-review/status")
def get_code_review_status_action():return {"name":"Aether","code_review":code_review_status()}
@app.get("/action/code-review/list")
def list_code_review_action(status:str|None=None,limit:int=50):return {"name":"Aether","reports":list_code_reviews(status,limit)}
@app.get("/action/code-review/{report_id}/summary")
def summarize_code_review_action(report_id:str):return {"name":"Aether","summary":summarize_code_review(report_id)}
@app.get("/action/code-review/{report_id}")
def get_code_review_action(report_id:str):return {"name":"Aether","report":get_code_review(report_id)}
@app.post("/action/review-bridge/create")
def create_review_bridge_action(request:ReviewBridgeCreateRequest):return {"name":"Aether","record":create_bridge_from_finding(request.report_id,request.finding_id,request.proposed_excerpt,request.original_excerpt,request.proposed_change_summary,request.reason,request.create_approval_if_required,request.metadata)}
@app.get("/action/review-bridge/status")
def get_review_bridge_status_action():return {"name":"Aether","review_bridge":review_bridge_status()}
@app.get("/action/review-bridge/list")
def list_review_bridge_action(status:str|None=None,review_report_id:str|None=None,limit:int=50):return {"name":"Aether","records":list_review_bridge_records(status,review_report_id,limit)}
@app.get("/action/review-bridge/{record_id}/summary")
def summarize_review_bridge_action(record_id:str):return {"name":"Aether","summary":summarize_review_bridge_record(record_id)}
@app.get("/action/review-bridge/{record_id}")
def get_review_bridge_action(record_id:str):return {"name":"Aether","record":get_review_bridge_record(record_id)}
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
@app.post("/action/proposal-review-console/open")
def open_proposal_review_console_action(request:ProposalReviewConsoleOpenRequest):return {"name":"Aether","record":open_proposal_review_console(request.source_type,request.source_id,request.metadata)}
@app.post("/action/proposal-review-console/submit")
def submit_proposal_review_action(request:ProposalReviewSubmitRequest):return {"name":"Aether","record":submit_proposal_review(request.console_record_id,request.decision,request.comment,request.reviewer,request.create_approval_if_required,request.metadata)}
@app.get("/action/proposal-review-console/status")
def get_proposal_review_console_status_action():return {"name":"Aether","proposal_review_console":proposal_review_console_status()}
@app.get("/action/proposal-review-console/list")
def list_proposal_review_console_action(status:str|None=None,proposal_id:str|None=None,limit:int=50):return {"name":"Aether","records":list_proposal_review_console_records(status,proposal_id,limit)}
@app.get("/action/proposal-review-console/{record_id}/summary")
def summarize_proposal_review_console_action(record_id:str):return {"name":"Aether","summary":summarize_proposal_review_console(record_id)}
@app.get("/action/proposal-review-console/{record_id}")
def get_proposal_review_console_action(record_id:str):return {"name":"Aether","record":get_proposal_review_console_record(record_id)}
@app.post("/action/proposal-revision-console/open")
def open_proposal_revision_console_action(request:ProposalRevisionConsoleOpenRequest):return {"name":"Aether","record":open_proposal_revision_console(request.source_type,request.source_id,request.metadata)}
@app.post("/action/proposal-revision-console/create-revision")
def create_proposal_revision_action(request:ProposalRevisionCreateRequest):return {"name":"Aether","record":create_proposal_revision(request.revision_record_id,request.revised_proposed_excerpt,request.revised_change_summary,request.human_revision_note,request.create_approval_if_required,request.metadata)}
@app.get("/action/proposal-revision-console/status")
def get_proposal_revision_console_status_action():return {"name":"Aether","proposal_revision_console":proposal_revision_console_status()}
@app.get("/action/proposal-revision-console/list")
def list_proposal_revision_console_action(status:str|None=None,original_proposal_id:str|None=None,limit:int=50):return {"name":"Aether","records":list_proposal_revision_console_records(status,original_proposal_id,limit)}
@app.get("/action/proposal-revision-console/{record_id}/summary")
def summarize_proposal_revision_console_action(record_id:str):return {"name":"Aether","summary":summarize_proposal_revision_console(record_id)}
@app.get("/action/proposal-revision-console/{record_id}")
def get_proposal_revision_console_action(record_id:str):return {"name":"Aether","record":get_proposal_revision_console_record(record_id)}
@app.post("/action/revised-proposal-review/open")
def open_revised_proposal_review_action(request:RevisedProposalReviewOpenRequest):return {"name":"Aether","record":open_revised_proposal_review(request.proposal_revision_console_id,request.metadata)}
@app.post("/action/revised-proposal-review/submit")
def submit_revised_proposal_review_action(request:RevisedProposalReviewSubmitRequest):return {"name":"Aether","record":submit_revised_proposal_review(request.review_loop_record_id,request.decision,request.comment,request.reviewer,request.create_approval_if_required,request.metadata)}
@app.get("/action/revised-proposal-review/status")
def get_revised_proposal_review_status_action():return {"name":"Aether","revised_proposal_review":revised_proposal_review_loop_status()}
@app.get("/action/revised-proposal-review/list")
def list_revised_proposal_review_action(status:str|None=None,revised_proposal_id:str|None=None,limit:int=50):return {"name":"Aether","records":list_revised_proposal_review_loop_records(status,revised_proposal_id,limit)}
@app.get("/action/revised-proposal-review/{record_id}/summary")
def summarize_revised_proposal_review_action(record_id:str):return {"name":"Aether","summary":summarize_revised_proposal_review_loop(record_id)}
@app.get("/action/revised-proposal-review/{record_id}")
def get_revised_proposal_review_action(record_id:str):return {"name":"Aether","record":get_revised_proposal_review_loop_record(record_id)}
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
