from typing import Literal as _L

from pydantic import BaseModel, Field as _F, StrictInt, field_validator


# ===================================================================== #
# Chat & Core API Models
# ===================================================================== #

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
    # --- Policy Enforcement Gate (Milestone 51A) ---
    policy_gate: dict | None = None
    execution_allowed: bool = False
    execution_decision: str | None = None
    execution_reason: str | None = None
    # --- Approval Request (Milestone 52A) ---
    approval_request: dict | None = None
    approval_required: bool = False
    approval_status: str | None = None
    approval_type: str | None = None
    # --- Approval Queue (Milestone 54A) ---
    approval_record: dict | None = None
    approval_id: str | None = None
    # --- Loop Trace (Milestone 81C) ---
    loop_trace: dict | None = None


# ===================================================================== #
# Working Memory Models
# ===================================================================== #

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


# ===================================================================== #
# Memory & Search Models
# ===================================================================== #

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


# ===================================================================== #
# Approval Models
# ===================================================================== #

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


# ===================================================================== #
# Tool Registry & Plan Models
# ===================================================================== #

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


# ===================================================================== #
# Tool Execution Models
# ===================================================================== #

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


# ===================================================================== #
# Restricted File Models
# ===================================================================== #

class RestrictedFileReadRequest(BaseModel):
    path: str
    max_chars: int = 12000
    metadata: dict = {}


class ApprovedReadExecutionAttemptRequest(BaseModel):
    approval_id: str
    request_text: str
    capability_id: _L["file.restricted_read"]
    target: str
    permission_class: _L["read_only"]
    max_chars: StrictInt = _F(default=12000, ge=0, le=12000)
    session_id: str | None = None

    @field_validator("request_text", "target")
    @classmethod
    def _non_empty(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("must not be empty")
        return value


class RestrictedFileReadExecutionAttemptResponse(BaseModel):
    name: str = "Aether"
    status: _L["completed", "denied", "error"]
    approval_id: str | None = None
    execution_attempt_status: _L[
        "NOT_ATTEMPTED", "REJECTED", "AUTHORIZED", "CLAIMED",
        "DISPATCHED", "COMPLETED", "FAILED",
    ]
    verification_status: _L[
        "VERIFIED_SUCCESS", "VERIFIED_PARTIAL", "DENIED", "NOT_FOUND",
        "CHANGED_DURING_READ", "INTERNAL_ERROR",
    ]
    action_dispatched: bool = False
    content: str | None = None
    truncated: bool = False
    reason: str | None = None
    warnings: list[str] = []
    tool_execution_allowed: bool = False


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


# ===================================================================== #
# Patch Proposal & Self-Modification Models
# ===================================================================== #

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


# ===================================================================== #
# Identity Integrity Models
# ===================================================================== #

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


# ===================================================================== #
# Approval Queue & Decision Gate Models
# ===================================================================== #

class ApprovalDecisionBody(BaseModel):
    reviewer: str | None = None
    reason: str | None = None


class ActionValidationBody(BaseModel):
    requested_action: dict | None = None
    context: dict | None = None


class DryRunDecisionBody(BaseModel):
    reviewer: str | None = None
    reason: str | None = None


class SandboxContextBody(BaseModel):
    context: dict | None = None


class SimResultBody(BaseModel):
    context: dict | None = None


class SimResultDecisionBody(BaseModel):
    reviewer: str | None = None
    reason: str | None = None


class VerdictContextBody(BaseModel):
    context: dict | None = None


class VerdictDecisionBody(BaseModel):
    reviewer: str | None = None
    reason: str | None = None


class ApplyGateContextBody(BaseModel):
    context: dict | None = None


class ApplyGateDecisionBody(BaseModel):
    reviewer: str | None = None
    reason: str | None = None


class HumanAuthContextBody(BaseModel):
    context: dict | None = None


class HumanAuthDecisionBody(BaseModel):
    reviewer: str | None = None
    reason: str | None = None
    confirmations: list[str] | None = None


class ApplyExecGateDecisionBody(BaseModel):
    reviewer: str | None = None
    reason: str | None = None
    confirmations: list[str] | None = None


class EvidenceContractBody(BaseModel):
    context: dict | None = None


class EvidenceContractDecisionBody(BaseModel):
    reviewer: str | None = None
    reason: str | None = None


class EvidenceContractApproveBody(BaseModel):
    reviewer: str
    reason: str | None = None
    confirmations: list[str]


class PlanDecisionBody(BaseModel):
    reviewer: str | None = None
    reason: str | None = None


class ApprovalIntentBody(BaseModel):
    reviewer: str | None = None
    reason: str | None = None
    confirmations: list[str] | None = None


class SimPlanDecisionBody(BaseModel):
    reviewer: str | None = None
    reason: str | None = None


# ===================================================================== #
# Observation Record Store API Models (Milestone 83B)
# ===================================================================== #


class ObservationRecordCreateRequest(BaseModel):
    plan_step_id: str | None = None
    evidence_item_id: str | None = None
    target: str
    observed_value: object | None = None
    expected_value: object | None = None
    status: str = "pending"
    collector_contract_id: str | None = None
    metadata: dict | None = None


class ObservationRecordResponse(BaseModel):
    observation_id: str
    observation_type: str = "observation_record"
    plan_step_id: str | None = None
    evidence_item_id: str | None = None
    collector_contract_id: str | None = None
    target: str
    observed_value: object | None = None
    expected_value: object | None = None
    status: str
    observed_at: str
    metadata: dict = {}
    safety_flags: dict = {}


class ObservationRecordListResponse(BaseModel):
    records: list["ObservationRecordResponse"] = []
    total: int = 0
    limit: int = 50
    offset: int = 0


class ObservationRecordUpdateStatusRequest(BaseModel):
    new_status: str
    reviewer: str
    reason: str | None = None


class ObservationRecordCancelRequest(BaseModel):
    reviewer: str
    reason: str | None = None
