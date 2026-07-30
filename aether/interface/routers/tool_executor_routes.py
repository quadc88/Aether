from fastapi import APIRouter

from aether.interface.api_models import ToolExecutionRequest
from aether.action.services.tool_execution_service import (
    handle_execute_action_tool as _handle_execute_tool,
    handle_get_action_tool_execution as _handle_get_execution,
    handle_get_tool_executor_status as _handle_tool_executor_status,
    handle_list_action_tool_executions as _handle_list_executions,
    handle_seed_action_sandbox_tools as _handle_seed_sandbox_tools,
)


tool_executor_router = APIRouter()


@tool_executor_router.post("/action/tool-executor/seed-sandbox-tools")
def seed_action_sandbox_tools():
    return _handle_seed_sandbox_tools()


@tool_executor_router.post("/action/tool-executor/execute")
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


@tool_executor_router.get("/action/tool-executor/status")
def get_action_tool_executor_status():
    return _handle_tool_executor_status()


@tool_executor_router.get("/action/tool-executor/list")
def list_action_tool_executions(limit: int = 50):
    return _handle_list_executions(limit)


@tool_executor_router.get("/action/tool-executor/{execution_id}")
def get_action_tool_execution(execution_id: str):
    return _handle_get_execution(execution_id)
