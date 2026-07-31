"""Repair Family router extracted in 82AM Build.

All 43 Repair Family routes moved from aether/interface/api_server.py.
route -> router -> service -> response boundary preserved.
"""

from fastapi import APIRouter

from aether.interface.api_models import (
    PrivateRepairCycleExportRequest,
    PrivateRepairGuidanceExportRequest,
    PrivateRepairLearningExportRequest,
    PrivateRepairWorkflowExportRequest,
    RepairBridgeSelectionCreateRequest,
    RepairCycleCompletionCreateRequest,
    RepairCycleIndexExportRequest,
    RepairCycleReportExportRequest,
    RepairGuidanceCreateRequest,
    RepairGuidanceIndexExportRequest,
    RepairGuidanceReportExportRequest,
    RepairLearningCreateRequest,
    RepairLearningIndexExportRequest,
    RepairLearningReportExportRequest,
    RepairPlanCreateRequest,
    RepairWorkflowExportRequest,
    RepairWorkflowIndexExportRequest,
    RepairWorkflowTraceRequest,
)

from aether.action.services.repair_bridge_selector_service import (
    handle_create_repair_bridge_selection,
    handle_get_repair_bridge_selection,
    handle_get_repair_bridge_selection_status,
    handle_list_repair_bridge_selections,
    handle_summarize_repair_bridge_selection,
)
from aether.action.services.repair_cycle_completion_service import (
    handle_create_repair_cycle_completion_report,
    handle_export_private_repair_cycle_record,
    handle_export_repair_cycle_index,
    handle_export_repair_cycle_report,
    handle_get_repair_cycle_completion_record,
    handle_get_repair_cycle_completion_status,
    handle_list_repair_cycle_completion_records,
    handle_summarize_repair_cycle_completion,
)
from aether.action.services.repair_guidance_service import (
    handle_create_repair_guidance,
    handle_export_private_repair_guidance_record,
    handle_export_repair_guidance_index,
    handle_export_repair_guidance_report,
    handle_get_repair_guidance_record,
    handle_get_repair_guidance_status,
    handle_list_repair_guidance_records,
    handle_summarize_repair_guidance,
)
from aether.action.services.repair_learning_service import (
    handle_create_repair_learning_record,
    handle_export_private_repair_learning_record,
    handle_export_repair_learning_index,
    handle_export_repair_learning_report,
    handle_get_repair_learning_record,
    handle_get_repair_learning_status,
    handle_list_repair_learning_records,
    handle_summarize_repair_learning_record,
)
from aether.action.services.repair_planner_service import (
    handle_create_repair_plan,
    handle_get_repair_plan,
    handle_get_repair_plan_status,
    handle_list_repair_plans,
    handle_summarize_repair_plan,
)
from aether.action.services.repair_workflow_exporter_service import (
    handle_export_private_repair_workflow_report,
    handle_export_repair_workflow_index,
    handle_export_repair_workflow_report,
    handle_get_repair_workflow_export_status,
)
from aether.action.services.repair_workflow_tracker_service import (
    handle_get_repair_workflow_report,
    handle_get_repair_workflow_status,
    handle_list_repair_workflow_reports,
    handle_summarize_repair_workflow,
    handle_trace_repair_workflow,
)


repair_router = APIRouter()

@repair_router.post("/action/repair-plan/create")
def create_repair_plan_action(request:RepairPlanCreateRequest):return handle_create_repair_plan(request.review_report_id,request.scope,request.include_deferred,request.max_findings,request.metadata)

@repair_router.get("/action/repair-plan/status")
def get_repair_plan_status_action():return handle_get_repair_plan_status()

@repair_router.get("/action/repair-plan/list")
def list_repair_plan_action(status:str|None=None,review_report_id:str|None=None,limit:int=50):return handle_list_repair_plans(status,review_report_id,limit)

@repair_router.get("/action/repair-plan/{plan_id}/summary")
def summarize_repair_plan_action(plan_id:str):return handle_summarize_repair_plan(plan_id)

@repair_router.get("/action/repair-plan/{plan_id}")
def get_repair_plan_action(plan_id:str):return handle_get_repair_plan(plan_id)

@repair_router.post("/action/repair-bridge-selection/create")
def create_repair_bridge_selection_action(request:RepairBridgeSelectionCreateRequest):return handle_create_repair_bridge_selection(request.repair_plan_id,request.finding_id,request.proposed_excerpt,request.original_excerpt,request.proposed_change_summary,request.reason,request.create_approval_if_required,request.metadata)

@repair_router.get("/action/repair-bridge-selection/status")
def get_repair_bridge_selection_status_action():return handle_get_repair_bridge_selection_status()

@repair_router.get("/action/repair-bridge-selection/list")
def list_repair_bridge_selection_action(status:str|None=None,repair_plan_id:str|None=None,limit:int=50):return handle_list_repair_bridge_selections(status,repair_plan_id,limit)

@repair_router.get("/action/repair-bridge-selection/{record_id}/summary")
def summarize_repair_bridge_selection_action(record_id:str):return handle_summarize_repair_bridge_selection(record_id)

@repair_router.get("/action/repair-bridge-selection/{record_id}")
def get_repair_bridge_selection_action(record_id:str):return handle_get_repair_bridge_selection(record_id)

@repair_router.post("/action/repair-workflow/trace")
def trace_repair_workflow_action(request:RepairWorkflowTraceRequest):return handle_trace_repair_workflow(request.root_type,request.root_id,request.metadata)

@repair_router.get("/action/repair-workflow/status")
def get_repair_workflow_status_action():return handle_get_repair_workflow_status()

@repair_router.get("/action/repair-workflow/list")
def list_repair_workflow_action(status:str|None=None,root_type:str|None=None,limit:int=50):return handle_list_repair_workflow_reports(status,root_type,limit)

@repair_router.get("/action/repair-workflow/{report_id}/summary")
def summarize_repair_workflow_action(report_id:str):return handle_summarize_repair_workflow(report_id)

@repair_router.get("/action/repair-workflow/{report_id}")
def get_repair_workflow_action(report_id:str):return handle_get_repair_workflow_report(report_id)

@repair_router.post("/action/repair-workflow-export/export-report")
def export_repair_workflow_report_action(request:RepairWorkflowExportRequest):return handle_export_repair_workflow_report(request.report_id,request.output_dir,request.metadata)

@repair_router.post("/action/repair-workflow-export/export-index")
def export_repair_workflow_index_action(request:RepairWorkflowIndexExportRequest):return handle_export_repair_workflow_index(request.output_path,request.limit,request.metadata)

@repair_router.post("/action/repair-workflow-export/export-private")
def export_private_repair_workflow_report_action(request:PrivateRepairWorkflowExportRequest):return handle_export_private_repair_workflow_report(request.report_id,request.metadata)

@repair_router.get("/action/repair-workflow-export/status")
def get_repair_workflow_export_status_action():return handle_get_repair_workflow_export_status()

@repair_router.post("/action/repair-cycle-completion/create")
def create_repair_cycle_completion_action(request:RepairCycleCompletionCreateRequest):return handle_create_repair_cycle_completion_report(request.source_type,request.source_id,request.export_public,request.export_index,request.export_private,request.metadata)

@repair_router.post("/action/repair-cycle-completion/export-report")
def export_repair_cycle_report_action(request:RepairCycleReportExportRequest):return handle_export_repair_cycle_report(request.completion_record_id,request.output_dir,request.metadata)

@repair_router.post("/action/repair-cycle-completion/export-index")
def export_repair_cycle_index_action(request:RepairCycleIndexExportRequest):return handle_export_repair_cycle_index(request.output_path,request.limit,request.metadata)

@repair_router.post("/action/repair-cycle-completion/export-private")
def export_private_repair_cycle_action(request:PrivateRepairCycleExportRequest):return handle_export_private_repair_cycle_record(request.completion_record_id,request.metadata)

@repair_router.get("/action/repair-cycle-completion/status")
def get_repair_cycle_completion_status_action():return handle_get_repair_cycle_completion_status()

@repair_router.get("/action/repair-cycle-completion/list")
def list_repair_cycle_completion_action(status:str|None=None,proposal_id:str|None=None,limit:int=50):return handle_list_repair_cycle_completion_records(status,proposal_id,limit)

@repair_router.get("/action/repair-cycle-completion/{record_id}/summary")
def summarize_repair_cycle_completion_action(record_id:str):return handle_summarize_repair_cycle_completion(record_id)

@repair_router.get("/action/repair-cycle-completion/{record_id}")
def get_repair_cycle_completion_action(record_id:str):return handle_get_repair_cycle_completion_record(record_id)

@repair_router.post("/action/repair-learning/create")
def create_repair_learning_action(request:RepairLearningCreateRequest):return handle_create_repair_learning_record(request.source_type,request.source_id,request.export_public,request.export_index,request.export_private,request.metadata)

@repair_router.post("/action/repair-learning/export-report")
def export_repair_learning_report_action(request:RepairLearningReportExportRequest):return handle_export_repair_learning_report(request.learning_record_id,request.output_dir,request.metadata)

@repair_router.post("/action/repair-learning/export-index")
def export_repair_learning_index_action(request:RepairLearningIndexExportRequest):return handle_export_repair_learning_index(request.output_path,request.limit,request.metadata)

@repair_router.post("/action/repair-learning/export-private")
def export_private_repair_learning_action(request:PrivateRepairLearningExportRequest):return handle_export_private_repair_learning_record(request.learning_record_id,request.metadata)

@repair_router.get("/action/repair-learning/status")
def get_repair_learning_status_action():return handle_get_repair_learning_status()

@repair_router.get("/action/repair-learning/list")
def list_repair_learning_action(status:str|None=None,learning_category:str|None=None,target_path:str|None=None,limit:int=50):return handle_list_repair_learning_records(status,learning_category,target_path,limit)

@repair_router.get("/action/repair-learning/{record_id}/summary")
def summarize_repair_learning_action(record_id:str):return handle_summarize_repair_learning_record(record_id)

@repair_router.get("/action/repair-learning/{record_id}")
def get_repair_learning_action(record_id:str):return handle_get_repair_learning_record(record_id)

@repair_router.post("/action/repair-guidance/create")
def create_repair_guidance_action(request:RepairGuidanceCreateRequest):return handle_create_repair_guidance(request.request_type,request.requested_scope,request.target_path,request.source_type,request.source_id,request.export_public,request.export_index,request.export_private,request.metadata)

@repair_router.post("/action/repair-guidance/export-report")
def export_repair_guidance_report_action(request:RepairGuidanceReportExportRequest):return handle_export_repair_guidance_report(request.guidance_record_id,request.output_dir,request.metadata)

@repair_router.post("/action/repair-guidance/export-index")
def export_repair_guidance_index_action(request:RepairGuidanceIndexExportRequest):return handle_export_repair_guidance_index(request.output_path,request.limit,request.metadata)

@repair_router.post("/action/repair-guidance/export-private")
def export_private_repair_guidance_action(request:PrivateRepairGuidanceExportRequest):return handle_export_private_repair_guidance_record(request.guidance_record_id,request.metadata)

@repair_router.get("/action/repair-guidance/status")
def get_repair_guidance_status_action():return handle_get_repair_guidance_status()

@repair_router.get("/action/repair-guidance/list")
def list_repair_guidance_action(status:str|None=None,guidance_decision:str|None=None,target_path:str|None=None,limit:int=50):return handle_list_repair_guidance_records(status,guidance_decision,target_path,limit)

@repair_router.get("/action/repair-guidance/{record_id}/summary")
def summarize_repair_guidance_action(record_id:str):return handle_summarize_repair_guidance(record_id)

@repair_router.get("/action/repair-guidance/{record_id}")
def get_repair_guidance_action(record_id:str):return handle_get_repair_guidance_record(record_id)
