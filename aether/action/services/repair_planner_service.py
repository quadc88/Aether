"""Service boundary for repair planner API responses."""

from aether.action.repair_planner import (
    create_repair_plan,
    get_repair_plan,
    list_repair_plans,
    repair_plan_status,
    summarize_repair_plan,
)


def handle_create_repair_plan(
    review_report_id, scope, include_deferred, max_findings, metadata
):
    return {
        "name": "Aether",
        "plan": create_repair_plan(
            review_report_id, scope, include_deferred, max_findings, metadata
        ),
    }


def handle_get_repair_plan_status():
    return {
        "name": "Aether",
        "repair_plan": repair_plan_status(),
    }


def handle_list_repair_plans(status=None, review_report_id=None, limit=50):
    return {
        "name": "Aether",
        "plans": list_repair_plans(status, review_report_id, limit),
    }


def handle_summarize_repair_plan(plan_id):
    return {
        "name": "Aether",
        "summary": summarize_repair_plan(plan_id),
    }


def handle_get_repair_plan(plan_id):
    return {
        "name": "Aether",
        "plan": get_repair_plan(plan_id),
    }
