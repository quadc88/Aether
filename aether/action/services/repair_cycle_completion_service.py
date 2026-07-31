"""Service boundary for repair cycle completion API responses."""

from aether.action.repair_cycle_completion_report import (
    create_repair_cycle_completion_report,
    export_private_repair_cycle_record,
    export_repair_cycle_index,
    export_repair_cycle_report,
    get_repair_cycle_completion_record,
    list_repair_cycle_completion_records,
    repair_cycle_completion_status,
    summarize_repair_cycle_completion,
)


def handle_create_repair_cycle_completion_report(
    source_type, source_id, export_public, export_index, export_private, metadata
):
    return {
        "name": "Aether",
        "record": create_repair_cycle_completion_report(
            source_type, source_id, export_public, export_index, export_private, metadata
        ),
    }


def handle_export_repair_cycle_report(completion_record_id, output_dir, metadata):
    return export_repair_cycle_report(completion_record_id, output_dir, metadata)


def handle_export_repair_cycle_index(output_path, limit, metadata):
    return export_repair_cycle_index(output_path, limit, metadata)


def handle_export_private_repair_cycle_record(completion_record_id, metadata):
    return export_private_repair_cycle_record(completion_record_id, metadata)


def handle_get_repair_cycle_completion_status():
    return {
        "name": "Aether",
        "repair_cycle_completion": repair_cycle_completion_status(),
    }


def handle_list_repair_cycle_completion_records(status=None, proposal_id=None, limit=50):
    return {
        "name": "Aether",
        "records": list_repair_cycle_completion_records(status, proposal_id, limit),
    }


def handle_summarize_repair_cycle_completion(record_id):
    return {
        "name": "Aether",
        "summary": summarize_repair_cycle_completion(record_id),
    }


def handle_get_repair_cycle_completion_record(record_id):
    return {
        "name": "Aether",
        "record": get_repair_cycle_completion_record(record_id),
    }
