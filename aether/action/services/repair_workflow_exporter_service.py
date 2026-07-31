"""Service boundary for repair workflow exporter API responses."""

from aether.action.repair_workflow_exporter import (
    export_private_workflow_report,
    export_workflow_index,
    export_workflow_report,
    repair_workflow_export_status,
)


def handle_export_repair_workflow_report(report_id, output_dir, metadata):
    return export_workflow_report(report_id, output_dir, metadata)


def handle_export_repair_workflow_index(output_path, limit, metadata):
    return export_workflow_index(output_path, limit, metadata)


def handle_export_private_repair_workflow_report(report_id, metadata):
    return export_private_workflow_report(report_id, metadata)


def handle_get_repair_workflow_export_status():
    return repair_workflow_export_status()
