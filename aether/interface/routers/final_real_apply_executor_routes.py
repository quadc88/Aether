"""C2 final real-apply executor router extracted in 82AO Build.

All 6 C2 final-real-apply executor routes moved from aether/interface/api_server.py.
route -> router -> service -> response boundary preserved.
"""

from fastapi import APIRouter

from aether.interface.api_models import (
    FinalRealApplyExecuteRequest,
    FinalRealApplyExecutorOpenRequest,
)

from aether.action.services.final_real_apply_executor_service import handle_open_final_real_apply_executor,handle_execute_final_real_apply,handle_get_final_real_apply_executor_status,handle_list_final_real_apply_executor_records,handle_summarize_final_real_apply_executor,handle_get_final_real_apply_executor_record


final_real_apply_executor_router = APIRouter()

@final_real_apply_executor_router.post("/action/final-real-apply-executor/open")
def open_final_real_apply_executor_action(request:FinalRealApplyExecutorOpenRequest):return handle_open_final_real_apply_executor(request.source_type,request.source_id,request.metadata)
@final_real_apply_executor_router.post("/action/final-real-apply-executor/execute")
def execute_final_real_apply_action(request:FinalRealApplyExecuteRequest):return handle_execute_final_real_apply(request.executor_record_id,request.metadata)
@final_real_apply_executor_router.get("/action/final-real-apply-executor/status")
def get_final_real_apply_executor_status_action():return handle_get_final_real_apply_executor_status()
@final_real_apply_executor_router.get("/action/final-real-apply-executor/list")
def list_final_real_apply_executor_action(status:str|None=None,proposal_id:str|None=None,limit:int=50):return handle_list_final_real_apply_executor_records(status,proposal_id,limit)
@final_real_apply_executor_router.get("/action/final-real-apply-executor/{record_id}/summary")
def summarize_final_real_apply_executor_action(record_id:str):return handle_summarize_final_real_apply_executor(record_id)
@final_real_apply_executor_router.get("/action/final-real-apply-executor/{record_id}")
def get_final_real_apply_executor_action(record_id:str):return handle_get_final_real_apply_executor_record(record_id)
