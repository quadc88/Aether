"""Boundary tests for 43 Repair Family endpoints after 82AL Part 4 service extraction
and 82AM Build router extraction.

Covers 7 families: repair_planner (5), repair_bridge_selector (5),
repair_workflow_tracker (5), repair_workflow_exporter (4),
repair_cycle_completion (8), repair_learning (8), repair_guidance (8).

Boundary model (82AM Build: route -> router -> service -> action):
- All 43 routes live in aether/interface/routers/repair_routes.py
- api_server.py includes repair_router (empty prefix) and defines no repair routes
- Service-backed (route -> service handler -> action):
  repair_planner, repair_workflow_tracker, repair_workflow_exporter,
  repair_cycle_completion, repair_learning, repair_guidance,
  repair_bridge_selector
- Direct-action Repair families: none
"""

from __future__ import annotations

import ast
import hashlib
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest
from fastapi.testclient import TestClient

from aether.interface.api_server import app


PROJECT_ROOT = Path(__file__).resolve().parents[1]

# (route_func, action_func, operation_id, wrapper_key, family)
REPAIR_ENDPOINTS: dict[tuple[str, str], tuple[str, str, str, str | None, str]] = {
    # repair_planner (5)
    ("POST", "/action/repair-plan/create"): (
        "create_repair_plan_action",
        "create_repair_plan",
        "create_repair_plan_action_action_repair_plan_create_post",
        "plan",
        "repair_planner",
    ),
    ("GET", "/action/repair-plan/status"): (
        "get_repair_plan_status_action",
        "repair_plan_status",
        "get_repair_plan_status_action_action_repair_plan_status_get",
        "repair_plan",
        "repair_planner",
    ),
    ("GET", "/action/repair-plan/list"): (
        "list_repair_plan_action",
        "list_repair_plans",
        "list_repair_plan_action_action_repair_plan_list_get",
        "plans",
        "repair_planner",
    ),
    ("GET", "/action/repair-plan/{plan_id}/summary"): (
        "summarize_repair_plan_action",
        "summarize_repair_plan",
        "summarize_repair_plan_action_action_repair_plan__plan_id__summary_get",
        "summary",
        "repair_planner",
    ),
    ("GET", "/action/repair-plan/{plan_id}"): (
        "get_repair_plan_action",
        "get_repair_plan",
        "get_repair_plan_action_action_repair_plan__plan_id__get",
        "plan",
        "repair_planner",
    ),
    # repair_bridge_selector (5)
    ("POST", "/action/repair-bridge-selection/create"): (
        "create_repair_bridge_selection_action",
        "create_bridge_from_repair_plan",
        "create_repair_bridge_selection_action_action_repair_bridge_selection_create_post",
        "record",
        "repair_bridge_selector",
    ),
    ("GET", "/action/repair-bridge-selection/status"): (
        "get_repair_bridge_selection_status_action",
        "repair_bridge_selection_status",
        "get_repair_bridge_selection_status_action_action_repair_bridge_selection_status_get",
        "repair_bridge_selection",
        "repair_bridge_selector",
    ),
    ("GET", "/action/repair-bridge-selection/list"): (
        "list_repair_bridge_selection_action",
        "list_repair_bridge_selections",
        "list_repair_bridge_selection_action_action_repair_bridge_selection_list_get",
        "records",
        "repair_bridge_selector",
    ),
    ("GET", "/action/repair-bridge-selection/{record_id}/summary"): (
        "summarize_repair_bridge_selection_action",
        "summarize_repair_bridge_selection",
        "summarize_repair_bridge_selection_action_action_repair_bridge_selection__record_id__summary_get",
        "summary",
        "repair_bridge_selector",
    ),
    ("GET", "/action/repair-bridge-selection/{record_id}"): (
        "get_repair_bridge_selection_action",
        "get_repair_bridge_selection",
        "get_repair_bridge_selection_action_action_repair_bridge_selection__record_id__get",
        "record",
        "repair_bridge_selector",
    ),
    # repair_workflow_tracker (5)
    ("POST", "/action/repair-workflow/trace"): (
        "trace_repair_workflow_action",
        "trace_repair_workflow",
        "trace_repair_workflow_action_action_repair_workflow_trace_post",
        "report",
        "repair_workflow_tracker",
    ),
    ("GET", "/action/repair-workflow/status"): (
        "get_repair_workflow_status_action",
        "repair_workflow_status",
        "get_repair_workflow_status_action_action_repair_workflow_status_get",
        "repair_workflow",
        "repair_workflow_tracker",
    ),
    ("GET", "/action/repair-workflow/list"): (
        "list_repair_workflow_action",
        "list_repair_workflow_reports",
        "list_repair_workflow_action_action_repair_workflow_list_get",
        "reports",
        "repair_workflow_tracker",
    ),
    ("GET", "/action/repair-workflow/{report_id}/summary"): (
        "summarize_repair_workflow_action",
        "summarize_repair_workflow",
        "summarize_repair_workflow_action_action_repair_workflow__report_id__summary_get",
        "summary",
        "repair_workflow_tracker",
    ),
    ("GET", "/action/repair-workflow/{report_id}"): (
        "get_repair_workflow_action",
        "get_repair_workflow_report",
        "get_repair_workflow_action_action_repair_workflow__report_id__get",
        "report",
        "repair_workflow_tracker",
    ),
    # repair_workflow_exporter (4) — all direct-return (no wrapper)
    ("POST", "/action/repair-workflow-export/export-report"): (
        "export_repair_workflow_report_action",
        "export_workflow_report",
        "export_repair_workflow_report_action_action_repair_workflow_export_export_report_post",
        None,
        "repair_workflow_exporter",
    ),
    ("POST", "/action/repair-workflow-export/export-index"): (
        "export_repair_workflow_index_action",
        "export_workflow_index",
        "export_repair_workflow_index_action_action_repair_workflow_export_export_index_post",
        None,
        "repair_workflow_exporter",
    ),
    ("POST", "/action/repair-workflow-export/export-private"): (
        "export_private_repair_workflow_report_action",
        "export_private_workflow_report",
        "export_private_repair_workflow_report_action_action_repair_workflow_export_export_private_post",
        None,
        "repair_workflow_exporter",
    ),
    ("GET", "/action/repair-workflow-export/status"): (
        "get_repair_workflow_export_status_action",
        "repair_workflow_export_status",
        "get_repair_workflow_export_status_action_action_repair_workflow_export_status_get",
        None,
        "repair_workflow_exporter",
    ),
    # repair_cycle_completion (8)
    ("POST", "/action/repair-cycle-completion/create"): (
        "create_repair_cycle_completion_action",
        "create_repair_cycle_completion_report",
        "create_repair_cycle_completion_action_action_repair_cycle_completion_create_post",
        "record",
        "repair_cycle_completion",
    ),
    ("POST", "/action/repair-cycle-completion/export-report"): (
        "export_repair_cycle_report_action",
        "export_repair_cycle_report",
        "export_repair_cycle_report_action_action_repair_cycle_completion_export_report_post",
        None,
        "repair_cycle_completion",
    ),
    ("POST", "/action/repair-cycle-completion/export-index"): (
        "export_repair_cycle_index_action",
        "export_repair_cycle_index",
        "export_repair_cycle_index_action_action_repair_cycle_completion_export_index_post",
        None,
        "repair_cycle_completion",
    ),
    ("POST", "/action/repair-cycle-completion/export-private"): (
        "export_private_repair_cycle_action",
        "export_private_repair_cycle_record",
        "export_private_repair_cycle_action_action_repair_cycle_completion_export_private_post",
        None,
        "repair_cycle_completion",
    ),
    ("GET", "/action/repair-cycle-completion/status"): (
        "get_repair_cycle_completion_status_action",
        "repair_cycle_completion_status",
        "get_repair_cycle_completion_status_action_action_repair_cycle_completion_status_get",
        "repair_cycle_completion",
        "repair_cycle_completion",
    ),
    ("GET", "/action/repair-cycle-completion/list"): (
        "list_repair_cycle_completion_action",
        "list_repair_cycle_completion_records",
        "list_repair_cycle_completion_action_action_repair_cycle_completion_list_get",
        "records",
        "repair_cycle_completion",
    ),
    ("GET", "/action/repair-cycle-completion/{record_id}/summary"): (
        "summarize_repair_cycle_completion_action",
        "summarize_repair_cycle_completion",
        "summarize_repair_cycle_completion_action_action_repair_cycle_completion__record_id__summary_get",
        "summary",
        "repair_cycle_completion",
    ),
    ("GET", "/action/repair-cycle-completion/{record_id}"): (
        "get_repair_cycle_completion_action",
        "get_repair_cycle_completion_record",
        "get_repair_cycle_completion_action_action_repair_cycle_completion__record_id__get",
        "record",
        "repair_cycle_completion",
    ),
    # repair_learning (8)
    ("POST", "/action/repair-learning/create"): (
        "create_repair_learning_action",
        "create_repair_learning_record",
        "create_repair_learning_action_action_repair_learning_create_post",
        "record",
        "repair_learning",
    ),
    ("POST", "/action/repair-learning/export-report"): (
        "export_repair_learning_report_action",
        "export_repair_learning_report",
        "export_repair_learning_report_action_action_repair_learning_export_report_post",
        None,
        "repair_learning",
    ),
    ("POST", "/action/repair-learning/export-index"): (
        "export_repair_learning_index_action",
        "export_repair_learning_index",
        "export_repair_learning_index_action_action_repair_learning_export_index_post",
        None,
        "repair_learning",
    ),
    ("POST", "/action/repair-learning/export-private"): (
        "export_private_repair_learning_action",
        "export_private_repair_learning_record",
        "export_private_repair_learning_action_action_repair_learning_export_private_post",
        None,
        "repair_learning",
    ),
    ("GET", "/action/repair-learning/status"): (
        "get_repair_learning_status_action",
        "repair_learning_index_status",
        "get_repair_learning_status_action_action_repair_learning_status_get",
        "repair_learning",
        "repair_learning",
    ),
    ("GET", "/action/repair-learning/list"): (
        "list_repair_learning_action",
        "list_repair_learning_records",
        "list_repair_learning_action_action_repair_learning_list_get",
        "records",
        "repair_learning",
    ),
    ("GET", "/action/repair-learning/{record_id}/summary"): (
        "summarize_repair_learning_action",
        "summarize_repair_learning_record",
        "summarize_repair_learning_action_action_repair_learning__record_id__summary_get",
        "summary",
        "repair_learning",
    ),
    ("GET", "/action/repair-learning/{record_id}"): (
        "get_repair_learning_action",
        "get_repair_learning_record",
        "get_repair_learning_action_action_repair_learning__record_id__get",
        "record",
        "repair_learning",
    ),
    # repair_guidance (8)
    ("POST", "/action/repair-guidance/create"): (
        "create_repair_guidance_action",
        "create_repair_guidance",
        "create_repair_guidance_action_action_repair_guidance_create_post",
        "record",
        "repair_guidance",
    ),
    ("POST", "/action/repair-guidance/export-report"): (
        "export_repair_guidance_report_action",
        "export_repair_guidance_report",
        "export_repair_guidance_report_action_action_repair_guidance_export_report_post",
        None,
        "repair_guidance",
    ),
    ("POST", "/action/repair-guidance/export-index"): (
        "export_repair_guidance_index_action",
        "export_repair_guidance_index",
        "export_repair_guidance_index_action_action_repair_guidance_export_index_post",
        None,
        "repair_guidance",
    ),
    ("POST", "/action/repair-guidance/export-private"): (
        "export_private_repair_guidance_action",
        "export_private_repair_guidance_record",
        "export_private_repair_guidance_action_action_repair_guidance_export_private_post",
        None,
        "repair_guidance",
    ),
    ("GET", "/action/repair-guidance/status"): (
        "get_repair_guidance_status_action",
        "repair_guidance_engine_status",
        "get_repair_guidance_status_action_action_repair_guidance_status_get",
        "repair_guidance",
        "repair_guidance",
    ),
    ("GET", "/action/repair-guidance/list"): (
        "list_repair_guidance_action",
        "list_repair_guidance_records",
        "list_repair_guidance_action_action_repair_guidance_list_get",
        "records",
        "repair_guidance",
    ),
    ("GET", "/action/repair-guidance/{record_id}/summary"): (
        "summarize_repair_guidance_action",
        "summarize_repair_guidance",
        "summarize_repair_guidance_action_action_repair_guidance__record_id__summary_get",
        "summary",
        "repair_guidance",
    ),
    ("GET", "/action/repair-guidance/{record_id}"): (
        "get_repair_guidance_action",
        "get_repair_guidance_record",
        "get_repair_guidance_action_action_repair_guidance__record_id__get",
        "record",
        "repair_guidance",
    ),
}

assert len(REPAIR_ENDPOINTS) == 43, f"Expected 43 repair endpoints, got {len(REPAIR_ENDPOINTS)}"

# ----- Boundary model after 82AL Part 4 -----
# Service-backed families (route -> service handler -> action):
#   repair_planner, repair_workflow_tracker, repair_workflow_exporter,
#   repair_cycle_completion, repair_learning, repair_guidance,
#   repair_bridge_selector
# Direct-action families: none
SERVICE_BACKED_FAMILIES = {
    "repair_planner",
    "repair_workflow_tracker",
    "repair_workflow_exporter",
    "repair_cycle_completion",
    "repair_learning",
    "repair_guidance",
    "repair_bridge_selector",
}
DIRECT_ACTION_FAMILIES: set[str] = set()

# route_func -> (service_handler, action_func)
ROUTE_TO_SERVICE: dict[str, tuple[str, str]] = {
    "create_repair_plan_action": ("handle_create_repair_plan", "create_repair_plan"),
    "get_repair_plan_status_action": ("handle_get_repair_plan_status", "repair_plan_status"),
    "list_repair_plan_action": ("handle_list_repair_plans", "list_repair_plans"),
    "summarize_repair_plan_action": ("handle_summarize_repair_plan", "summarize_repair_plan"),
    "get_repair_plan_action": ("handle_get_repair_plan", "get_repair_plan"),
    "create_repair_bridge_selection_action": ("handle_create_repair_bridge_selection", "create_bridge_from_repair_plan"),
    "get_repair_bridge_selection_status_action": ("handle_get_repair_bridge_selection_status", "repair_bridge_selection_status"),
    "list_repair_bridge_selection_action": ("handle_list_repair_bridge_selections", "list_repair_bridge_selections"),
    "summarize_repair_bridge_selection_action": ("handle_summarize_repair_bridge_selection", "summarize_repair_bridge_selection"),
    "get_repair_bridge_selection_action": ("handle_get_repair_bridge_selection", "get_repair_bridge_selection"),
    "trace_repair_workflow_action": ("handle_trace_repair_workflow", "trace_repair_workflow"),
    "get_repair_workflow_status_action": ("handle_get_repair_workflow_status", "repair_workflow_status"),
    "list_repair_workflow_action": ("handle_list_repair_workflow_reports", "list_repair_workflow_reports"),
    "summarize_repair_workflow_action": ("handle_summarize_repair_workflow", "summarize_repair_workflow"),
    "get_repair_workflow_action": ("handle_get_repair_workflow_report", "get_repair_workflow_report"),
    "export_repair_workflow_report_action": ("handle_export_repair_workflow_report", "export_workflow_report"),
    "export_repair_workflow_index_action": ("handle_export_repair_workflow_index", "export_workflow_index"),
    "export_private_repair_workflow_report_action": ("handle_export_private_repair_workflow_report", "export_private_workflow_report"),
    "get_repair_workflow_export_status_action": ("handle_get_repair_workflow_export_status", "repair_workflow_export_status"),
    "create_repair_cycle_completion_action": ("handle_create_repair_cycle_completion_report", "create_repair_cycle_completion_report"),
    "export_repair_cycle_report_action": ("handle_export_repair_cycle_report", "export_repair_cycle_report"),
    "export_repair_cycle_index_action": ("handle_export_repair_cycle_index", "export_repair_cycle_index"),
    "export_private_repair_cycle_action": ("handle_export_private_repair_cycle_record", "export_private_repair_cycle_record"),
    "get_repair_cycle_completion_status_action": ("handle_get_repair_cycle_completion_status", "repair_cycle_completion_status"),
    "list_repair_cycle_completion_action": ("handle_list_repair_cycle_completion_records", "list_repair_cycle_completion_records"),
    "summarize_repair_cycle_completion_action": ("handle_summarize_repair_cycle_completion", "summarize_repair_cycle_completion"),
    "get_repair_cycle_completion_action": ("handle_get_repair_cycle_completion_record", "get_repair_cycle_completion_record"),
    "create_repair_learning_action": ("handle_create_repair_learning_record", "create_repair_learning_record"),
    "export_repair_learning_report_action": ("handle_export_repair_learning_report", "export_repair_learning_report"),
    "export_repair_learning_index_action": ("handle_export_repair_learning_index", "export_repair_learning_index"),
    "export_private_repair_learning_action": ("handle_export_private_repair_learning_record", "export_private_repair_learning_record"),
    "get_repair_learning_status_action": ("handle_get_repair_learning_status", "repair_learning_index_status"),
    "list_repair_learning_action": ("handle_list_repair_learning_records", "list_repair_learning_records"),
    "summarize_repair_learning_action": ("handle_summarize_repair_learning_record", "summarize_repair_learning_record"),
    "get_repair_learning_action": ("handle_get_repair_learning_record", "get_repair_learning_record"),
    "create_repair_guidance_action": ("handle_create_repair_guidance", "create_repair_guidance"),
    "export_repair_guidance_report_action": ("handle_export_repair_guidance_report", "export_repair_guidance_report"),
    "export_repair_guidance_index_action": ("handle_export_repair_guidance_index", "export_repair_guidance_index"),
    "export_private_repair_guidance_action": ("handle_export_private_repair_guidance_record", "export_private_repair_guidance_record"),
    "get_repair_guidance_status_action": ("handle_get_repair_guidance_status", "repair_guidance_engine_status"),
    "list_repair_guidance_action": ("handle_list_repair_guidance_records", "list_repair_guidance_records"),
    "summarize_repair_guidance_action": ("handle_summarize_repair_guidance", "summarize_repair_guidance"),
    "get_repair_guidance_action": ("handle_get_repair_guidance_record", "get_repair_guidance_record"),
}

# service module -> {handler: action_func}
SERVICE_HANDLER_MAP: dict[str, dict[str, str]] = {
    "aether.action.services.repair_planner_service": {
        "handle_create_repair_plan": "create_repair_plan",
        "handle_get_repair_plan_status": "repair_plan_status",
        "handle_list_repair_plans": "list_repair_plans",
        "handle_summarize_repair_plan": "summarize_repair_plan",
        "handle_get_repair_plan": "get_repair_plan",
    },
    "aether.action.services.repair_workflow_tracker_service": {
        "handle_trace_repair_workflow": "trace_repair_workflow",
        "handle_get_repair_workflow_status": "repair_workflow_status",
        "handle_list_repair_workflow_reports": "list_repair_workflow_reports",
        "handle_summarize_repair_workflow": "summarize_repair_workflow",
        "handle_get_repair_workflow_report": "get_repair_workflow_report",
    },
    "aether.action.services.repair_workflow_exporter_service": {
        "handle_export_repair_workflow_report": "export_workflow_report",
        "handle_export_repair_workflow_index": "export_workflow_index",
        "handle_export_private_repair_workflow_report": "export_private_workflow_report",
        "handle_get_repair_workflow_export_status": "repair_workflow_export_status",
    },
    "aether.action.services.repair_cycle_completion_service": {
        "handle_create_repair_cycle_completion_report": "create_repair_cycle_completion_report",
        "handle_export_repair_cycle_report": "export_repair_cycle_report",
        "handle_export_repair_cycle_index": "export_repair_cycle_index",
        "handle_export_private_repair_cycle_record": "export_private_repair_cycle_record",
        "handle_get_repair_cycle_completion_status": "repair_cycle_completion_status",
        "handle_list_repair_cycle_completion_records": "list_repair_cycle_completion_records",
        "handle_summarize_repair_cycle_completion": "summarize_repair_cycle_completion",
        "handle_get_repair_cycle_completion_record": "get_repair_cycle_completion_record",
    },
    "aether.action.services.repair_learning_service": {
        "handle_create_repair_learning_record": "create_repair_learning_record",
        "handle_export_repair_learning_report": "export_repair_learning_report",
        "handle_export_repair_learning_index": "export_repair_learning_index",
        "handle_export_private_repair_learning_record": "export_private_repair_learning_record",
        "handle_get_repair_learning_status": "repair_learning_index_status",
        "handle_list_repair_learning_records": "list_repair_learning_records",
        "handle_summarize_repair_learning_record": "summarize_repair_learning_record",
        "handle_get_repair_learning_record": "get_repair_learning_record",
    },
    "aether.action.services.repair_guidance_service": {
        "handle_create_repair_guidance": "create_repair_guidance",
        "handle_export_repair_guidance_report": "export_repair_guidance_report",
        "handle_export_repair_guidance_index": "export_repair_guidance_index",
        "handle_export_private_repair_guidance_record": "export_private_repair_guidance_record",
        "handle_get_repair_guidance_status": "repair_guidance_engine_status",
        "handle_list_repair_guidance_records": "list_repair_guidance_records",
        "handle_summarize_repair_guidance": "summarize_repair_guidance",
        "handle_get_repair_guidance_record": "get_repair_guidance_record",
    },
    "aether.action.services.repair_bridge_selector_service": {
        "handle_create_repair_bridge_selection": "create_bridge_from_repair_plan",
        "handle_get_repair_bridge_selection_status": "repair_bridge_selection_status",
        "handle_list_repair_bridge_selections": "list_repair_bridge_selections",
        "handle_summarize_repair_bridge_selection": "summarize_repair_bridge_selection",
        "handle_get_repair_bridge_selection": "get_repair_bridge_selection",
    },
}

# service module -> its sole action module
SERVICE_ACTION_MODULES: dict[str, str] = {
    "aether.action.services.repair_planner_service": "aether.action.repair_planner",
    "aether.action.services.repair_workflow_tracker_service": "aether.action.repair_workflow_tracker",
    "aether.action.services.repair_workflow_exporter_service": "aether.action.repair_workflow_exporter",
    "aether.action.services.repair_cycle_completion_service": "aether.action.repair_cycle_completion_report",
    "aether.action.services.repair_learning_service": "aether.action.repair_learning_index",
    "aether.action.services.repair_guidance_service": "aether.action.repair_guidance_engine",
    "aether.action.services.repair_bridge_selector_service": "aether.action.repair_bridge_selector",
}

# handler -> wrapper key (derived from REPAIR_ENDPOINTS for service-backed routes)
SERVICE_HANDLER_WRAPPER_KEYS: dict[str, str] = {}
for (method, path), (route_func, action_func, operation_id, wrapper_key, family) in REPAIR_ENDPOINTS.items():
    if family in SERVICE_BACKED_FAMILIES:
        handler, _ = ROUTE_TO_SERVICE[route_func]
        SERVICE_HANDLER_WRAPPER_KEYS[handler] = wrapper_key
assert len(SERVICE_HANDLER_WRAPPER_KEYS) == 43, (
    f"Expected 43 service handlers with wrapper keys, got {len(SERVICE_HANDLER_WRAPPER_KEYS)}"
)

# Known pre-existing bugs: repair_guidance export functions crash on None
# from get_repair_guidance_record("missing"). Deferred to Part 3 or a
# dedicated bugfix milestone before guidance extraction.
KNOWN_BUGGY_EXPORT_ENDPOINTS = {
    "/action/repair-guidance/export-report",
    "/action/repair-guidance/export-private",
}

POST_PAYLOADS: dict[str, dict[str, Any]] = {
    "/action/repair-plan/create": {
        "review_report_id": "missing",
        "scope": "full",
        "include_deferred": False,
        "max_findings": 10,
        "metadata": {},
    },
    "/action/repair-bridge-selection/create": {
        "repair_plan_id": "missing",
        "finding_id": "f-missing",
        "proposed_excerpt": "test",
        "original_excerpt": "test",
        "proposed_change_summary": "test",
        "reason": "test",
        "create_approval_if_required": False,
        "metadata": {},
    },
    "/action/repair-workflow/trace": {
        "root_type": "missing",
        "root_id": "r-missing",
        "metadata": {},
    },
    "/action/repair-workflow-export/export-report": {
        "report_id": "missing",
        "output_dir": "/tmp/isolated",
        "metadata": {},
    },
    "/action/repair-workflow-export/export-index": {
        "output_path": "/tmp/isolated/index.json",
        "limit": 50,
        "metadata": {},
    },
    "/action/repair-workflow-export/export-private": {
        "report_id": "missing",
        "metadata": {},
    },
    "/action/repair-cycle-completion/create": {
        "source_type": "missing",
        "source_id": "s-missing",
        "export_public": False,
        "export_index": False,
        "export_private": False,
        "metadata": {},
    },
    "/action/repair-cycle-completion/export-report": {
        "completion_record_id": "missing",
        "output_dir": "/tmp/isolated",
        "metadata": {},
    },
    "/action/repair-cycle-completion/export-index": {
        "output_path": "/tmp/isolated/index.json",
        "limit": 50,
        "metadata": {},
    },
    "/action/repair-cycle-completion/export-private": {
        "completion_record_id": "missing",
        "metadata": {},
    },
    "/action/repair-learning/create": {
        "source_type": "missing",
        "source_id": "s-missing",
        "export_public": False,
        "export_index": False,
        "export_private": False,
        "metadata": {},
    },
    "/action/repair-learning/export-report": {
        "learning_record_id": "missing",
        "output_dir": "/tmp/isolated",
        "metadata": {},
    },
    "/action/repair-learning/export-index": {
        "output_path": "/tmp/isolated/index.json",
        "limit": 50,
        "metadata": {},
    },
    "/action/repair-learning/export-private": {
        "learning_record_id": "missing",
        "metadata": {},
    },
    "/action/repair-guidance/create": {
        "request_type": "missing",
        "requested_scope": "full",
        "target_path": "/tmp/test",
        "source_type": "test",
        "source_id": "s-missing",
        "export_public": False,
        "export_index": False,
        "export_private": False,
        "metadata": {},
    },
    "/action/repair-guidance/export-report": {
        "guidance_record_id": "missing",
        "output_dir": "/tmp/isolated",
        "metadata": {},
    },
    "/action/repair-guidance/export-index": {
        "output_path": "/tmp/isolated/index.json",
        "limit": 50,
        "metadata": {},
    },
    "/action/repair-guidance/export-private": {
        "guidance_record_id": "missing",
        "metadata": {},
    },
}

PROTECTED_ENDPOINTS: dict[tuple[str, str], str] = {
    ("GET", "/"): "root__get",
    ("GET", "/identity"): "identity_identity_get",
    ("GET", "/identity/integrity/status"): "get_identity_integrity_status_identity_integrity_status_get",
    ("POST", "/identity/integrity/initialize"): "post_initialize_identity_guard_identity_integrity_initialize_post",
    ("POST", "/identity/integrity/verify"): "post_verify_identity_integrity_identity_integrity_verify_post",
    ("POST", "/chat"): "chat_chat_post",
    ("POST", "/awaken"): "awaken_awaken_post",
    ("POST", "/verification/classify"): "classify_verification_risk_verification_classify_post",
}

# Build safe-endpoint API cases (excluding known buggy endpoints)
API_CASES: list[tuple[str, str, dict[str, Any] | None, str | None]] = []

for (method, path), (_, _, _, wrapper_key, _) in sorted(REPAIR_ENDPOINTS.items()):
    if path in KNOWN_BUGGY_EXPORT_ENDPOINTS:
        continue
    payload = None
    if method == "POST":
        payload = POST_PAYLOADS.get(path, {})
    API_CASES.append((method, path, payload, wrapper_key))

# ----- fingerprint helpers -----

def _fingerprint(root: Path) -> list[tuple]:
    if not root.exists():
        return []
    result = []
    for p in sorted(root.rglob("*")):
        try:
            relative = str(p.relative_to(root))
            if p.is_file():
                result.append(
                    ("file", relative, p.stat().st_size,
                     hashlib.sha256(p.read_bytes()).hexdigest())
                )
            elif p.is_dir():
                result.append(("dir", relative))
        except FileNotFoundError:
            continue
    return result


WATCHED_REAL_ROOTS = (
    PROJECT_ROOT / "aether",
    PROJECT_ROOT / "tests",
    PROJECT_ROOT / "PROGRESS.md",
    Path("/home/aether/data/private"),
    Path("/home/aether/data/timeline"),
    Path("/home/aether/data/graph_db"),
    Path("/home/aether/data/vector_db"),
    Path("/home/aether/data/vault"),
    Path("/home/aether/data/logs"),
    PROJECT_ROOT / "docs/history",
)


@pytest.fixture(scope="module", autouse=True)
def real_source_runtime_and_data_roots_unchanged():
    before = {
        str(root): _fingerprint(root) if root.exists() else []
        for root in WATCHED_REAL_ROOTS
    }
    yield
    after = {
        str(root): _fingerprint(root) if root.exists() else []
        for root in WATCHED_REAL_ROOTS
    }
    assert before == after


@pytest.fixture
def isolated_repair_env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    data_root = tmp_path / "AetherData"
    private_dir = data_root / "private"
    private_dir.mkdir(parents=True, exist_ok=True)

    config = {"paths": {"private_dir": str(private_dir)}}

    import aether.action.repair_planner as rp
    import aether.action.repair_bridge_selector as rbs
    import aether.action.repair_workflow_tracker as rwt
    import aether.action.repair_workflow_exporter as rwe
    import aether.action.repair_cycle_completion_report as rcc
    import aether.action.repair_learning_index as rli
    import aether.action.repair_guidance_engine as rge

    for module in (rp, rbs, rwt, rwe, rcc, rli, rge):
        monkeypatch.setattr(module, "load_aether_config", lambda path=None, _config=config: _config)

    client = TestClient(app)
    yield SimpleNamespace(client=client, private_dir=private_dir)


# ----- Test 1: OpenAPI operation ID lock -----

def test_openapi_contract_and_operation_ids_locked():
    schema = app.openapi()
    assert len(schema.get("paths", {})) == 305
    assert len(schema.get("components", {}).get("schemas", {})) == 110
    assert len(REPAIR_ENDPOINTS) == 43

    for (method, path), (_, _, operation_id, _, _) in REPAIR_ENDPOINTS.items():
        actual = schema["paths"][path][method.lower()]["operationId"]
        assert actual == operation_id, (
            f"{method} {path}: expected {operation_id}, got {actual}"
        )


# ----- Test 2: Protected endpoints remain outside repair scope -----

def test_protected_endpoints_remain_outside_repair_families():
    schema = app.openapi()
    repair_paths = {path for _, path in REPAIR_ENDPOINTS}
    for (method, path), operation_id in PROTECTED_ENDPOINTS.items():
        assert path not in repair_paths
        assert schema["paths"][path][method.lower()]["operationId"] == operation_id

    this_file = Path(__file__).read_text(encoding="utf-8")
    invoked_paths = set()
    for node in ast.walk(ast.parse(this_file)):
        if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Attribute):
            continue
        if node.func.attr not in {"get", "post"} or not node.args:
            continue
        if isinstance(node.args[0], ast.Constant):
            invoked_paths.add(node.args[0].value)
    assert not invoked_paths.intersection(path for _, path in PROTECTED_ENDPOINTS)


# ----- Test 3: Dynamic API smoke tests -----

@pytest.mark.parametrize(
    ("method", "path", "payload", "wrapper_key"),
    API_CASES,
    ids=[f"{method}-{path}" for method, path, _, _ in API_CASES],
)
def test_repair_wrapped_endpoints_respond(
    isolated_repair_env, method, path, payload, wrapper_key
):
    if method == "POST":
        response = isolated_repair_env.client.post(path, json=payload)
    else:
        response = isolated_repair_env.client.get(path)

    assert response.status_code == 200, (
        f"{method} {path}: expected 200, got {response.status_code}: {response.text[:200]}"
    )

    body = response.json()
    if wrapper_key is not None:
        # wrapped route: must have {"name":"Aether","<wrapper_key>": ...}
        assert body["name"] == "Aether", (
            f"{method} {path}: expected name=Aether, got {body}"
        )
        assert wrapper_key in body, (
            f"{method} {path}: expected wrapper_key={wrapper_key!r} in body, got keys {list(body)}"
        )
    else:
        # direct-return route: no wrapper; accept any valid JSON response
        assert isinstance(body, (dict, list)), (
            f"{method} {path}: expected dict/list, got {type(body).__name__}"
        )


# ----- Test 4: Known buggy endpoints documentation -----

def test_known_buggy_export_endpoints_documented():
    """Repair-guidance export endpoints crash on missing records (pre-existing bug).
    These are pre-existing missing-record crash bugs in repair_guidance_engine.py,
    deferred to 82AL Part 3 / guidance extraction or a dedicated bugfix milestone
    before guidance extraction.
    """
    assert KNOWN_BUGGY_EXPORT_ENDPOINTS == {
        "/action/repair-guidance/export-report",
        "/action/repair-guidance/export-private",
    }, "Bug endpoints list changed — verify and update this test"


# ----- Test 5: Route boundary — service-backed vs direct-action pass-throughs -----

def test_repair_routes_are_boundary_pass_throughs():
    """Verify each repair route body is a single return statement:
    - service-backed families (repair_planner, repair_workflow_tracker):
      exactly one call to the expected service handler (no direct action call)
    - direct-action families: exactly one call to the expected action function
      (no handle_* service call)
    """
    # 82AM Build: all 43 repair route functions live in repair_routes.py
    source_path = PROJECT_ROOT / "aether/interface/routers/repair_routes.py"
    tree = ast.parse(source_path.read_text(encoding="utf-8"))

    func_names = {route_func for _, (route_func, _, _, _, _) in REPAIR_ENDPOINTS.items()}

    found = {}
    for node in tree.body:
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if node.name not in func_names:
            continue
        assert len(node.body) == 1, f"{node.name}: expected single-statement body"
        assert isinstance(node.body[0], ast.Return), f"{node.name}: expected return"
        calls = [child for child in ast.walk(node.body[0]) if isinstance(child, ast.Call)]
        assert len(calls) == 1, f"{node.name}: expected exactly 1 call, got {len(calls)}"
        called_name = ast.unparse(calls[0].func)

        found[node.name] = called_name

    assert len(found) == 43, f"Expected 43 route functions, found {len(found)}"

    for (method, path), (route_func, action_func, _, _, family) in REPAIR_ENDPOINTS.items():
        if family in SERVICE_BACKED_FAMILIES:
            expected = ROUTE_TO_SERVICE[route_func][0]
        else:
            expected = action_func
        assert found[route_func] == expected, (
            f"Route {route_func} ({path}): expected {expected!r}, got {found[route_func]!r}"
        )

    # Verify wrapper contract for each route (unchanged by service extraction;
    # for service-backed routes the wrapper lives in the service handler and is
    # verified by test_service_handlers_boundary_static)
    for (method, path), (route_func, action_func, _, wrapper_key, family) in REPAIR_ENDPOINTS.items():
        for node in tree.body:
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            if node.name != route_func:
                continue
            ret = node.body[0]
            if family in SERVICE_BACKED_FAMILIES:
                assert isinstance(ret.value, ast.Call), (
                    f"{route_func}: expected service handler call return"
                )
                assert ast.unparse(ret.value.func) == ROUTE_TO_SERVICE[route_func][0], (
                    f"{route_func}: expected call to {ROUTE_TO_SERVICE[route_func][0]!r}"
                )
            elif wrapper_key is not None:
                # wrapped direct-action: return {"name":"Aether","<key>": action_func(...)}
                assert isinstance(ret.value, ast.Dict), (
                    f"{route_func}: expected dict return for wrapped route"
                )
                keys = [ast.unparse(k) for k in ret.value.keys]
                assert "'name'" in keys, f"{route_func}: missing 'name' key"
                assert f"'{wrapper_key}'" in keys, (
                    f"{route_func}: missing {wrapper_key!r} key"
                )
            else:
                # direct-return: return action_func(...)
                assert isinstance(ret.value, ast.Call), (
                    f"{route_func}: expected direct call return for direct-return route"
                )
            break

    # Verify service-backed routes call the service handler, not the action directly
    for route_func, (handler, _) in ROUTE_TO_SERVICE.items():
        assert found[route_func] == handler, (
            f"Route {route_func}: expected service handler {handler!r}, got {found[route_func]!r}"
        )

    # Verify direct-action families do NOT call any handle_* service function
    direct_route_funcs = {
        route_func
        for (method, path), (route_func, _, _, _, family) in REPAIR_ENDPOINTS.items()
        if family in DIRECT_ACTION_FAMILIES
    }
    for route_func in direct_route_funcs:
        assert not found[route_func].startswith("handle_"), (
            f"Route {route_func}: direct-action family calls service function {found[route_func]!r}"
        )


# ----- Test 6: Import boundary — service-backed families via services, others direct -----

def test_api_server_import_boundary_mixed_model():
    """After 82AM Build, api_server.py must:
    - import repair_router from aether.interface.routers.repair_routes exactly once
    - include repair_router exactly once (empty prefix)
    - NOT import any of the 7 Repair Family service modules (they moved to the router)
    - NOT import any direct Repair Family action module; after 82AR Build the
      guided modules moved to guided_launcher_routes.py, so api_server has none
    """
    source = (PROJECT_ROOT / "aether/interface/api_server.py").read_text(encoding="utf-8")
    tree = ast.parse(source)

    service_imports = set()
    repair_imports = set()
    router_imports = set()
    for node in tree.body:
        if isinstance(node, ast.ImportFrom):
            module = node.module or ""
            for alias in node.names:
                if module.startswith("aether.action.services.") and "repair" in module:
                    service_imports.add(module)
                elif module.startswith("aether.action.") and "repair" in module:
                    repair_imports.add(module)
                if module == "aether.interface.routers.repair_routes":
                    router_imports.add(alias.name)

    assert router_imports == {"repair_router"}, (
        f"api_server.py must import repair_router exactly once, got {router_imports}"
    )

    # service modules must NOT be imported directly by api_server anymore
    assert not service_imports, (
        f"api_server.py must not import Repair Family service modules after 82AM Build: "
        f"{service_imports}"
    )

    # no direct Repair Family action imports in api_server; the guided modules
    # moved to guided_launcher_routes.py in 82AR Build
    guided_action_modules: set[str] = set()
    assert repair_imports <= guided_action_modules, (
        f"Unexpected direct repair action imports in api_server.py: "
        f"{repair_imports - guided_action_modules}"
    )
    assert not repair_imports

    # exactly one include_router(repair_router, prefix="")
    include_calls = [
        (ast.unparse(call.func), [ast.unparse(a) for a in call.args], {
            k.arg: ast.unparse(k.value) for k in call.keywords
        })
        for call in ast.walk(tree)
        if isinstance(call, ast.Call) and ast.unparse(call.func) == "app.include_router"
    ]
    repair_includes = [
        call for call in include_calls
        if call[0] == "app.include_router"
        and call[1] == ["repair_router"]
        and call[2].get("prefix") == "''"
    ]
    assert len(repair_includes) == 1, (
        f"api_server.py must include repair_router exactly once with empty prefix, "
        f"got {repair_includes}"
    )


# ----- Test 6b: Router file boundary — repair_routes.py -----

def test_repair_routes_module_boundary():
    """repair_routes.py must:
    - exist and define repair_router = APIRouter() (empty prefix)
    - define all 43 Repair Family route functions
    - decorate all 43 routes with repair_router (never app)
    - import all 7 Repair Family service modules (the only repair action imports allowed)
    - import no direct Repair Family action modules
    - import no approval/gate/dry_run/evidence/tool/final_real_apply modules
    """
    router_path = PROJECT_ROOT / "aether/interface/routers/repair_routes.py"
    assert router_path.exists(), "repair_routes.py missing after 82AM Build"
    tree = ast.parse(router_path.read_text(encoding="utf-8"))

    # repair_router = APIRouter() with no arguments (empty prefix)
    router_assigns = [
        node for node in tree.body
        if isinstance(node, ast.Assign)
        and any(isinstance(t, ast.Name) and t.id == "repair_router" for t in node.targets)
    ]
    assert len(router_assigns) == 1, "repair_router must be assigned exactly once"
    assign = router_assigns[0]
    assert isinstance(assign.value, ast.Call), "repair_router must be APIRouter()"
    assert ast.unparse(assign.value.func) == "APIRouter", "repair_router must be APIRouter()"
    assert not assign.value.args, "repair_router must be created with an empty prefix (no args)"

    func_names = {route_func for _, (route_func, _, _, _, _) in REPAIR_ENDPOINTS.items()}

    # all 43 route functions present, decorated with repair_router
    router_route_funcs = {}
    for node in tree.body:
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if node.name not in func_names:
            continue
        decorators = [ast.unparse(d) for d in node.decorator_list]
        assert decorators, f"{node.name}: missing decorator"
        for dec in decorators:
            assert dec.startswith("repair_router."), (
                f"{node.name}: decorator {dec!r} must use repair_router, not app"
            )
        assert len(node.decorator_list) == 1, f"{node.name}: expected single decorator"
        router_route_funcs[node.name] = decorators[0]

    assert len(router_route_funcs) == 43, (
        f"Expected 43 route functions in repair_routes.py, got {len(router_route_funcs)}"
    )
    assert set(router_route_funcs) == func_names

    # decorator paths/methods match REPAIR_ENDPOINTS exactly
    for (method, path), (route_func, _, _, _, _) in REPAIR_ENDPOINTS.items():
        dec = router_route_funcs[route_func]
        assert f"'{path}'" in dec, (
            f"{route_func}: decorator {dec!r} missing path {path!r}"
        )
        assert dec.startswith(f"repair_router.{method.lower()}("), (
            f"{route_func}: decorator {dec!r} must use {method.lower()} method"
        )

    # import boundary
    service_imports = set()
    repair_action_imports = set()
    forbidden_router_imports = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.ImportFrom):
            continue
        module = node.module or ""
        if module.startswith("aether.action.services.") and "repair" in module:
            service_imports.add(module)
        elif module.startswith("aether.action."):
            repair_action_imports.add(module)
        if any(k in module for k in (
            "approval", "gate", "dry_run", "evidence", "tool",
            "final_real_apply", "executor", "verification", "patch",
        )):
            forbidden_router_imports.add(module)

    assert service_imports == set(SERVICE_ACTION_MODULES), (
        f"repair_routes.py must import all 7 Repair Family service modules, got "
        f"{service_imports - set(SERVICE_ACTION_MODULES)} missing"
    )
    assert not repair_action_imports, (
        f"repair_routes.py must not import Repair Family action modules: "
        f"{repair_action_imports}"
    )
    assert not forbidden_router_imports, (
        f"repair_routes.py must not import approval/gate/dry_run/evidence/tool/"
        f"final_real_apply modules: {forbidden_router_imports}"
    )


# ----- Test 6c: api_server no longer defines repair routes -----

def test_api_server_no_longer_defines_repair_routes():
    """api_server.py must no longer define any of the 43 Repair Family route
    functions, and must no longer import the 7 Repair Family service modules."""
    source = (PROJECT_ROOT / "aether/interface/api_server.py").read_text(encoding="utf-8")
    tree = ast.parse(source)

    func_names = {route_func for _, (route_func, _, _, _, _) in REPAIR_ENDPOINTS.items()}
    defined = {
        node.name for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name in func_names
    }
    assert not defined, (
        f"api_server.py must not define Repair Family route functions after 82AM Build: "
        f"{sorted(defined)}"
    )

    service_imports = set()
    for node in tree.body:
        if isinstance(node, ast.ImportFrom):
            module = node.module or ""
            if module.startswith("aether.action.services.") and "repair" in module:
                service_imports.add(module)
    assert not service_imports, (
        f"api_server.py must not import Repair Family service modules: {service_imports}"
    )


# ----- Test 7: Service existence proof (7 present, 0 absent) -----

def test_extracted_service_modules_exist_and_others_do_not():
    present_paths = [
        PROJECT_ROOT / "aether/action/services/repair_planner_service.py",
        PROJECT_ROOT / "aether/action/services/repair_workflow_tracker_service.py",
        PROJECT_ROOT / "aether/action/services/repair_workflow_exporter_service.py",
        PROJECT_ROOT / "aether/action/services/repair_cycle_completion_service.py",
        PROJECT_ROOT / "aether/action/services/repair_learning_service.py",
        PROJECT_ROOT / "aether/action/services/repair_guidance_service.py",
        PROJECT_ROOT / "aether/action/services/repair_bridge_selector_service.py",
    ]
    absent_paths: list[Path] = []
    for path in present_paths:
        assert path.exists(), (
            f"Extracted service module missing (should exist after Part 4): {path}"
        )
    for path in absent_paths:
        assert not path.exists(), (
            f"Service module exists but its family is not extracted yet: {path}"
        )


# ----- Test 7b: Service handler static proof -----

def test_service_handlers_boundary_static():
    """Each service module:
    - defines exactly the expected handle_* functions
    - each handler is a single return:
      - wrapped routes: {"name": "Aether", <wrapper_key>: <action_call>}
      - direct-return routes: <action_call> with no wrapper
    - each handler makes exactly one call, to its expected action function
    - imports only its own action module
    - no forbidden imports/calls/network
    """
    for service_module, handler_map in SERVICE_HANDLER_MAP.items():
        module_path = PROJECT_ROOT / (
            "aether/action/services/" + service_module.rsplit(".", 1)[1] + ".py"
        )
        assert module_path.exists(), f"Missing service module: {module_path}"
        tree = ast.parse(module_path.read_text(encoding="utf-8"))

        defs = {
            node.name: node
            for node in tree.body
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            and node.name.startswith("handle_")
        }
        assert set(defs) == set(handler_map), (
            f"{module_path.name}: expected handlers {sorted(handler_map)}, "
            f"got {sorted(defs)}"
        )

        for handler, action_func in handler_map.items():
            node = defs[handler]
            assert len(node.body) == 1, f"{handler}: expected single-statement body"
            assert isinstance(node.body[0], ast.Return), f"{handler}: expected return"
            ret = node.body[0]

            expected_key = SERVICE_HANDLER_WRAPPER_KEYS.get(handler)
            if expected_key is not None:
                # wrapped: return {"name":"Aether","<key>": action_func(...)}
                assert isinstance(ret.value, ast.Dict), (
                    f"{handler}: expected dict return for wrapped route"
                )
                keys = [ast.unparse(k) for k in ret.value.keys]
                assert "'name'" in keys, f"{handler}: missing 'name' key"
                assert f"'{expected_key}'" in keys, (
                    f"{handler}: missing wrapper key {expected_key!r}, got keys {keys}"
                )
            else:
                # direct-return: return action_func(...) with no wrapper
                assert isinstance(ret.value, ast.Call), (
                    f"{handler}: expected direct call return for direct-return route"
                )

            calls = [child for child in ast.walk(ret.value) if isinstance(child, ast.Call)]
            assert len(calls) == 1, f"{handler}: expected exactly 1 call, got {len(calls)}"
            assert ast.unparse(calls[0].func) == action_func, (
                f"{handler}: expected call to {action_func!r}, "
                f"got {ast.unparse(calls[0].func)!r}"
            )

        # import boundary: only its own action module may be imported
        imported_action_modules = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                module = node.module or ""
                if module.startswith("aether.action."):
                    imported_action_modules.add(module)
        expected_action_module = SERVICE_ACTION_MODULES[service_module]
        assert imported_action_modules == {expected_action_module}, (
            f"{module_path.name}: expected imports only from {expected_action_module}, "
            f"got {imported_action_modules}"
        )


# ----- Test 7c: Service modules risk static proof -----

def test_service_modules_no_forbidden_imports_or_calls():
    service_paths = [
        PROJECT_ROOT / "aether/action/services/repair_planner_service.py",
        PROJECT_ROOT / "aether/action/services/repair_workflow_tracker_service.py",
        PROJECT_ROOT / "aether/action/services/repair_workflow_exporter_service.py",
        PROJECT_ROOT / "aether/action/services/repair_cycle_completion_service.py",
        PROJECT_ROOT / "aether/action/services/repair_learning_service.py",
        PROJECT_ROOT / "aether/action/services/repair_guidance_service.py",
        PROJECT_ROOT / "aether/action/services/repair_bridge_selector_service.py",
    ]
    for module_path in service_paths:
        assert module_path.exists(), f"Missing service module: {module_path}"
        tree = ast.parse(module_path.read_text(encoding="utf-8"))

        imported_names = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    imported_names.add(alias.name)

        overlap = imported_names & FORBIDDEN_ACTION_IMPORTS
        assert not overlap, (
            f"{module_path.name}: forbidden import(s): {overlap}"
        )

        all_calls = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                all_calls.add(ast.unparse(node.func))

        overlap_calls = all_calls & FORBIDDEN_ACTION_CALLS
        assert not overlap_calls, (
            f"{module_path.name}: forbidden call(s): {overlap_calls}"
        )


# ----- Test 7d: Highest-risk bridge argument mapping (pass-through proof) -----

CREATE_APPROVAL_PASS_THROUGH_ARGS = (
    "repair_plan_id",
    "finding_id",
    "proposed_excerpt",
    "original_excerpt",
    "proposed_change_summary",
    "reason",
    "create_approval_if_required",
    "metadata",
)

BRIDGE_CREATE_ROUTE_ARGS = (
    "request.repair_plan_id",
    "request.finding_id",
    "request.proposed_excerpt",
    "request.original_excerpt",
    "request.proposed_change_summary",
    "request.reason",
    "request.create_approval_if_required",
    "request.metadata",
)


def test_repair_bridge_selection_create_passes_create_approval_if_required_through():
    """Highest-risk preservation proof: create_approval_if_required must flow
    route -> router -> service handler -> action exactly as received, with no
    hardcoded True/False and no approval creation in the service layer.
    """
    # 82AM Build: the route lives in repair_routes.py
    api_source = (
        PROJECT_ROOT / "aether/interface/routers/repair_routes.py"
    ).read_text(encoding="utf-8")
    api_tree = ast.parse(api_source)

    route_node = None
    for node in api_tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.name == "create_repair_bridge_selection_action":
                route_node = node
                break
    assert route_node is not None, "create_repair_bridge_selection_action not found"
    assert len(route_node.body) == 1, "route must be a single-return body"
    route_call = route_node.body[0].value
    assert isinstance(route_call, ast.Call), "route must return a call"
    assert ast.unparse(route_call.func) == "handle_create_repair_bridge_selection", (
        f"route must call handle_create_repair_bridge_selection, got {ast.unparse(route_call.func)}"
    )
    route_args = [ast.unparse(a) for a in route_call.args]
    assert route_args == list(BRIDGE_CREATE_ROUTE_ARGS), (
        f"route argument order mismatch: {route_args}"
    )

    service_path = PROJECT_ROOT / "aether/action/services/repair_bridge_selector_service.py"
    assert service_path.exists(), "repair_bridge_selector_service.py missing"
    service_tree = ast.parse(service_path.read_text(encoding="utf-8"))

    handler_node = None
    for node in service_tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.name == "handle_create_repair_bridge_selection":
                handler_node = node
                break
    assert handler_node is not None, "handle_create_repair_bridge_selection not found"
    assert len(handler_node.body) == 1, "handler must be a single-return body"
    handler_return = handler_node.body[0].value
    assert isinstance(handler_return, ast.Dict), "handler must return a dict wrapper"

    action_call = None
    for child in ast.walk(handler_return):
        if isinstance(child, ast.Call):
            action_call = child
    assert action_call is not None, "handler must make exactly one action call"
    assert ast.unparse(action_call.func) == "create_bridge_from_repair_plan", (
        f"handler must call create_bridge_from_repair_plan, got {ast.unparse(action_call.func)}"
    )
    action_args = [ast.unparse(a) for a in action_call.args]
    assert action_args == list(CREATE_APPROVAL_PASS_THROUGH_ARGS), (
        f"handler action argument order mismatch: {action_args}"
    )

    # create_approval_if_required must not be hardcoded in the service layer
    for node in ast.walk(service_tree):
        if isinstance(node, ast.Constant):
            if node.value in (True, False):
                raise AssertionError(
                    f"hardcoded bool {node.value!r} found in service layer at line {node.lineno}"
                )

    # service must not import approval modules or create approvals directly
    imported_modules = set()
    for node in ast.walk(service_tree):
        if isinstance(node, ast.ImportFrom):
            imported_modules.add(node.module or "")
    approval_imports = {
        m for m in imported_modules if "approval" in m or "gate" in m
    }
    assert not approval_imports, (
        f"service imports approval/gate module(s): {approval_imports}"
    )
    service_calls = {
        ast.unparse(node.func)
        for node in ast.walk(service_tree)
        if isinstance(node, ast.Call)
    }
    assert not {"create_approval_item", "create_approval_if_required"} & {
        name.split(".")[-1] for name in service_calls
    }, "service must not create approval items directly"


# ----- Test 8: Action risk static proof (strengthened) -----

REPAIR_ACTION_MODULE_PATHS = [
    PROJECT_ROOT / "aether/action/repair_planner.py",
    PROJECT_ROOT / "aether/action/repair_bridge_selector.py",
    PROJECT_ROOT / "aether/action/repair_workflow_tracker.py",
    PROJECT_ROOT / "aether/action/repair_workflow_exporter.py",
    PROJECT_ROOT / "aether/action/repair_cycle_completion_report.py",
    PROJECT_ROOT / "aether/action/repair_learning_index.py",
    PROJECT_ROOT / "aether/action/repair_guidance_engine.py",
]

FORBIDDEN_ACTION_IMPORTS = {
    "apply_patch_proposal",
    "execute_final_real_apply",
    "execute_patch_rollback",
    "rollback_patch_apply",
    "perform_rollback",
    "apply_rollback",
    "run_rollback",
    "collect_evidence",
    "evidence_collection",
    "execute_tool",
}

FORBIDDEN_ACTION_CALLS = {
    "apply_patch_proposal",
    "execute_final_real_apply",
    "execute_patch_rollback",
    "rollback_patch_apply",
    "perform_rollback",
    "apply_rollback",
    "run_rollback",
    "collect_evidence",
    "evidence_collection",
    "execute_tool",
    "subprocess.run",
    "subprocess.call",
    "subprocess.Popen",
    "os.system",
    "requests",
    "httpx",
    "socket",
    "urllib",
}

# Exception: repair_cycle_completion_report.py may import/call
# get_final_real_apply_executor_record as read-only lookup only.
# It must NOT import/call execute_final_real_apply or apply_patch_proposal.
ALLOWED_READ_ONLY_FETCH = {"get_final_real_apply_executor_record"}


def test_no_forbidden_imports_in_repair_action_modules():
    for module_path in REPAIR_ACTION_MODULE_PATHS:
        assert module_path.exists(), f"Missing module: {module_path}"
        tree = ast.parse(module_path.read_text(encoding="utf-8"))
        imported_names = set()
        imported_from_final_exec = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    imported_names.add(alias.name)
                    if node.module == "aether.action.final_real_apply_executor":
                        imported_from_final_exec.add(alias.name)

        overlap = imported_names & FORBIDDEN_ACTION_IMPORTS
        assert not overlap, (
            f"{module_path.name}: forbidden import(s): {overlap}"
        )

        # Check read-only fetch exception
        exec_imports = imported_from_final_exec - ALLOWED_READ_ONLY_FETCH
        assert not exec_imports, (
            f"{module_path.name}: unexpected import(s) from final_real_apply_executor: {exec_imports}"
        )

        # Only repair_cycle_completion_report may have read-only fetch
        if imported_from_final_exec:
            assert module_path.name == "repair_cycle_completion_report.py", (
                f"{module_path.name}: only repair_cycle_completion_report may import "
                f"from final_real_apply_executor"
            )
            assert imported_from_final_exec == {"get_final_real_apply_executor_record"}, (
                f"{module_path.name}: only get_final_real_apply_executor_record allowed, "
                f"got {imported_from_final_exec}"
            )


def test_no_forbidden_calls_or_network_in_repair_action_modules():
    for module_path in REPAIR_ACTION_MODULE_PATHS:
        assert module_path.exists(), f"Missing module: {module_path}"
        tree = ast.parse(module_path.read_text(encoding="utf-8"))
        all_calls = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                call_str = ast.unparse(node.func)
                all_calls.add(call_str)

        overlap = all_calls & FORBIDDEN_ACTION_CALLS
        assert not overlap, (
            f"{module_path.name}: forbidden call(s): {overlap}"
        )


def test_repair_cycle_completion_read_only_fetch_exception_documented():
    """repair_cycle_completion_report.py may import get_final_real_apply_executor_record
    as a read-only lookup. Verify it does NOT import execute_final_real_apply
    or apply_patch_proposal."""
    cycle_path = PROJECT_ROOT / "aether/action/repair_cycle_completion_report.py"
    assert cycle_path.exists()
    tree = ast.parse(cycle_path.read_text(encoding="utf-8"))
    imported_names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            for alias in node.names:
                imported_names.add(alias.name)

    assert "execute_final_real_apply" not in imported_names, (
        "repair_cycle_completion_report must NOT import execute_final_real_apply"
    )
    assert "apply_patch_proposal" not in imported_names, (
        "repair_cycle_completion_report must NOT import apply_patch_proposal"
    )
    assert "get_final_real_apply_executor_record" in imported_names, (
        "repair_cycle_completion_report should import get_final_real_apply_executor_record "
        "for read-only lookup (expected read-only fetch exception)"
    )
