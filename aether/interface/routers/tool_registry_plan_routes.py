from fastapi import APIRouter

from aether.interface.api_models import (
    ToolPlanRequest,
    ToolPolicyUpdateRequest,
    ToolRegisterRequest,
    ToolSearchRequest,
)
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


tool_registry_plan_router = APIRouter()


@tool_registry_plan_router.get("/action/tools/status")
def get_tool_registry_status():
    return _handle_tool_registry_status()


@tool_registry_plan_router.post("/action/tools/register")
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


@tool_registry_plan_router.post("/action/tools/seed")
def seed_action_tools():
    return _handle_seed_tools()


@tool_registry_plan_router.get("/action/tools/list")
def list_action_tools(category: str | None = None, enabled: bool | None = None, limit: int = 100):
    return _handle_list_tools(category, enabled, limit)


@tool_registry_plan_router.get("/action/tools/{tool_id}")
def get_action_tool(tool_id: str):
    return _handle_get_tool(tool_id)


@tool_registry_plan_router.post("/action/tools/search")
def search_action_tools(request: ToolSearchRequest):
    return _handle_search_tools(request.query, request.limit)


@tool_registry_plan_router.post("/action/tools/enable/{tool_id}")
def enable_action_tool(tool_id: str):
    return _handle_enable_tool(tool_id)


@tool_registry_plan_router.post("/action/tools/disable/{tool_id}")
def disable_action_tool(tool_id: str):
    return _handle_disable_tool(tool_id)


@tool_registry_plan_router.post("/action/tools/policy")
def update_action_tool_policy(request: ToolPolicyUpdateRequest):
    return _handle_update_tool_policy(
        tool_id=request.tool_id,
        risk_level=request.risk_level,
        requires_verification=request.requires_verification,
        requires_user_approval=request.requires_user_approval,
        allow_auto_execute=request.allow_auto_execute,
    )


@tool_registry_plan_router.post("/action/tool-plan/create")
def create_action_tool_plan(request: ToolPlanRequest):
    return _handle_create_tool_plan(
        text=request.text,
        proposed_action=request.proposed_action,
        metadata=request.metadata,
        create_approval_if_required=request.create_approval_if_required,
    )


@tool_registry_plan_router.get("/action/tool-plan/status")
def get_action_tool_plan_status():
    return _handle_tool_plan_status()


@tool_registry_plan_router.get("/action/tool-plan/list")
def list_action_tool_plans(limit: int = 50):
    return _handle_list_tool_plans(limit)


@tool_registry_plan_router.get("/action/tool-plan/{plan_id}")
def get_action_tool_plan(plan_id: str):
    return _handle_get_tool_plan(plan_id)
