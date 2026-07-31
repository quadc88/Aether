"""Service boundary for repair workflow tracker API responses."""

from aether.action.repair_workflow_tracker import (
    get_repair_workflow_report,
    list_repair_workflow_reports,
    repair_workflow_status,
    summarize_repair_workflow,
    trace_repair_workflow,
)


def handle_trace_repair_workflow(root_type, root_id, metadata):
    return {
        "name": "Aether",
        "report": trace_repair_workflow(root_type, root_id, metadata),
    }


def handle_get_repair_workflow_status():
    return {
        "name": "Aether",
        "repair_workflow": repair_workflow_status(),
    }


def handle_list_repair_workflow_reports(status=None, root_type=None, limit=50):
    return {
        "name": "Aether",
        "reports": list_repair_workflow_reports(status, root_type, limit),
    }


def handle_summarize_repair_workflow(report_id):
    return {
        "name": "Aether",
        "summary": summarize_repair_workflow(report_id),
    }


def handle_get_repair_workflow_report(report_id):
    return {
        "name": "Aether",
        "report": get_repair_workflow_report(report_id),
    }
