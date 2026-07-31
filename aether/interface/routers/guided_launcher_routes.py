"""Guided Launcher router extracted in 82AR Build.

All 29 Guided Launcher routes moved from aether/interface/api_server.py.
route -> direct action -> response boundary preserved.
"""

from fastapi import APIRouter

from aether.interface.api_models import (
    GuidedRepairIntakeOpenRequest,
    GuidedRepairIntakeDecisionRequest,
    GuidedRepairIntakeReportExportRequest,
    GuidedRepairIntakeIndexExportRequest,
    PrivateGuidedRepairIntakeExportRequest,
    GuidedRepairPlanLaunchRequest,
    GuidedBridgeSelectionLaunchRequest,
    GuidedProposalReviewOpenRequest,
    GuidedProposalDecisionSubmitRequest,
)

from aether.action.guided_repair_intake import open_guided_repair_intake,submit_guided_repair_intake_decision,export_guided_repair_intake_report,export_guided_repair_intake_index,export_private_guided_repair_intake_record,get_guided_repair_intake_record,list_guided_repair_intake_records,guided_repair_intake_status,summarize_guided_repair_intake
from aether.action.guided_repair_plan_launcher import launch_guided_repair_plan,get_guided_repair_plan_launcher_record,list_guided_repair_plan_launcher_records,guided_repair_plan_launcher_status,summarize_guided_repair_plan_launcher
from aether.action.guided_bridge_selection_launcher import launch_guided_bridge_selection,get_guided_bridge_selection_launcher_record,list_guided_bridge_selection_launcher_records,guided_bridge_selection_launcher_status,summarize_guided_bridge_selection_launcher
from aether.action.guided_proposal_review_launcher import open_guided_proposal_review,get_guided_proposal_review_launcher_record,list_guided_proposal_review_launcher_records,guided_proposal_review_launcher_status,summarize_guided_proposal_review_launcher
from aether.action.guided_proposal_decision_launcher import submit_guided_proposal_decision,get_guided_proposal_decision_launcher_record,list_guided_proposal_decision_launcher_records,guided_proposal_decision_launcher_status,summarize_guided_proposal_decision_launcher


guided_launcher_router = APIRouter()

@guided_launcher_router.post("/action/guided-repair-intake/open")
def open_guided_repair_intake_action(request:GuidedRepairIntakeOpenRequest):return {"name":"Aether","record":open_guided_repair_intake(request.request_type,request.requested_scope,request.target_path,request.requester,request.guidance_record_id,request.create_guidance_if_missing,request.export_public,request.export_index,request.export_private,request.metadata)}
@guided_launcher_router.post("/action/guided-repair-intake/submit-decision")
def submit_guided_repair_intake_action(request:GuidedRepairIntakeDecisionRequest):return {"name":"Aether","record":submit_guided_repair_intake_decision(request.intake_record_id,request.decision,request.comment,request.reviewer,request.metadata)}
@guided_launcher_router.post("/action/guided-repair-intake/export-report")
def export_guided_repair_intake_report_action(request:GuidedRepairIntakeReportExportRequest):return export_guided_repair_intake_report(request.intake_record_id,request.output_dir,request.metadata)
@guided_launcher_router.post("/action/guided-repair-intake/export-index")
def export_guided_repair_intake_index_action(request:GuidedRepairIntakeIndexExportRequest):return export_guided_repair_intake_index(request.output_path,request.limit,request.metadata)
@guided_launcher_router.post("/action/guided-repair-intake/export-private")
def export_private_guided_repair_intake_action(request:PrivateGuidedRepairIntakeExportRequest):return export_private_guided_repair_intake_record(request.intake_record_id,request.metadata)
@guided_launcher_router.get("/action/guided-repair-intake/status")
def guided_repair_intake_status_action():return {"name":"Aether","guided_repair_intake":guided_repair_intake_status()}
@guided_launcher_router.get("/action/guided-repair-intake/list")
def list_guided_repair_intake_action(status:str|None=None,planning_allowed:bool|None=None,target_path:str|None=None,limit:int=50):return {"name":"Aether","records":list_guided_repair_intake_records(status,planning_allowed,target_path,limit)}
@guided_launcher_router.get("/action/guided-repair-intake/{record_id}/summary")
def summarize_guided_repair_intake_action(record_id:str):return {"name":"Aether","summary":summarize_guided_repair_intake(record_id)}
@guided_launcher_router.get("/action/guided-repair-intake/{record_id}")
def get_guided_repair_intake_action(record_id:str):return {"name":"Aether","record":get_guided_repair_intake_record(record_id)}
@guided_launcher_router.post("/action/guided-repair-plan-launcher/launch")
def launch_guided_repair_plan_action(request:GuidedRepairPlanLaunchRequest):return {"name":"Aether","record":launch_guided_repair_plan(request.intake_record_id,request.review_report_id,request.create_repair_plan,request.metadata)}
@guided_launcher_router.get("/action/guided-repair-plan-launcher/status")
def guided_repair_plan_launcher_status_action():return {"name":"Aether","guided_repair_plan_launcher":guided_repair_plan_launcher_status()}
@guided_launcher_router.get("/action/guided-repair-plan-launcher/list")
def list_guided_repair_plan_launcher_action(status:str|None=None,intake_record_id:str|None=None,target_path:str|None=None,limit:int=50):return {"name":"Aether","records":list_guided_repair_plan_launcher_records(status,intake_record_id,target_path,limit)}
@guided_launcher_router.get("/action/guided-repair-plan-launcher/{record_id}/summary")
def summarize_guided_repair_plan_launcher_action(record_id:str):return {"name":"Aether","summary":summarize_guided_repair_plan_launcher(record_id)}
@guided_launcher_router.get("/action/guided-repair-plan-launcher/{record_id}")
def get_guided_repair_plan_launcher_action(record_id:str):return {"name":"Aether","record":get_guided_repair_plan_launcher_record(record_id)}
@guided_launcher_router.post("/action/guided-bridge-selection-launcher/launch")
def launch_guided_bridge_selection_action(request:GuidedBridgeSelectionLaunchRequest):return {"name":"Aether","record":launch_guided_bridge_selection(request.plan_launcher_record_id,request.finding_id,request.proposed_excerpt,request.metadata)}
@guided_launcher_router.get("/action/guided-bridge-selection-launcher/status")
def guided_bridge_selection_launcher_status_action():return {"name":"Aether","guided_bridge_selection_launcher":guided_bridge_selection_launcher_status()}
@guided_launcher_router.get("/action/guided-bridge-selection-launcher/list")
def list_guided_bridge_selection_launcher_action(status:str|None=None,plan_launcher_record_id:str|None=None,repair_plan_id:str|None=None,target_path:str|None=None,limit:int=50):return {"name":"Aether","records":list_guided_bridge_selection_launcher_records(status,plan_launcher_record_id,repair_plan_id,target_path,limit)}
@guided_launcher_router.get("/action/guided-bridge-selection-launcher/{record_id}/summary")
def summarize_guided_bridge_selection_launcher_action(record_id:str):return {"name":"Aether","summary":summarize_guided_bridge_selection_launcher(record_id)}
@guided_launcher_router.get("/action/guided-bridge-selection-launcher/{record_id}")
def get_guided_bridge_selection_launcher_action(record_id:str):return {"name":"Aether","record":get_guided_bridge_selection_launcher_record(record_id)}
@guided_launcher_router.post("/action/guided-proposal-review-launcher/open")
def open_guided_proposal_review_action(request:GuidedProposalReviewOpenRequest):return {"name":"Aether","record":open_guided_proposal_review(request.bridge_launcher_record_id,request.metadata)}
@guided_launcher_router.get("/action/guided-proposal-review-launcher/status")
def guided_proposal_review_launcher_status_action():return {"name":"Aether","guided_proposal_review_launcher":guided_proposal_review_launcher_status()}
@guided_launcher_router.get("/action/guided-proposal-review-launcher/list")
def list_guided_proposal_review_launcher_action(status:str|None=None,bridge_launcher_record_id:str|None=None,proposal_id:str|None=None,target_path:str|None=None,limit:int=50):return {"name":"Aether","records":list_guided_proposal_review_launcher_records(status,bridge_launcher_record_id,proposal_id,target_path,limit)}
@guided_launcher_router.get("/action/guided-proposal-review-launcher/{record_id}/summary")
def summarize_guided_proposal_review_launcher_action(record_id:str):return {"name":"Aether","summary":summarize_guided_proposal_review_launcher(record_id)}
@guided_launcher_router.get("/action/guided-proposal-review-launcher/{record_id}")
def get_guided_proposal_review_launcher_action(record_id:str):return {"name":"Aether","record":get_guided_proposal_review_launcher_record(record_id)}
@guided_launcher_router.post("/action/guided-proposal-decision-launcher/submit")
def submit_guided_proposal_decision_action(request:GuidedProposalDecisionSubmitRequest):return {"name":"Aether","record":submit_guided_proposal_decision(request.proposal_review_launcher_record_id,request.decision,request.reviewer,request.comment,request.metadata)}
@guided_launcher_router.get("/action/guided-proposal-decision-launcher/status")
def guided_proposal_decision_launcher_status_action():return {"name":"Aether","guided_proposal_decision_launcher":guided_proposal_decision_launcher_status()}
@guided_launcher_router.get("/action/guided-proposal-decision-launcher/list")
def list_guided_proposal_decision_launcher_action(status:str|None=None,proposal_review_launcher_record_id:str|None=None,proposal_id:str|None=None,decision:str|None=None,target_path:str|None=None,limit:int=50):return {"name":"Aether","records":list_guided_proposal_decision_launcher_records(status,proposal_review_launcher_record_id,proposal_id,decision,target_path,limit)}
@guided_launcher_router.get("/action/guided-proposal-decision-launcher/{record_id}/summary")
def summarize_guided_proposal_decision_launcher_action(record_id:str):return {"name":"Aether","summary":summarize_guided_proposal_decision_launcher(record_id)}
@guided_launcher_router.get("/action/guided-proposal-decision-launcher/{record_id}")
def get_guided_proposal_decision_launcher_action(record_id:str):return {"name":"Aether","record":get_guided_proposal_decision_launcher_record(record_id)}
