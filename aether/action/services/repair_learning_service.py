"""Service boundary for repair learning API responses."""

from aether.action.repair_learning_index import (
    create_repair_learning_record,
    export_private_repair_learning_record,
    export_repair_learning_index,
    export_repair_learning_report,
    get_repair_learning_record,
    list_repair_learning_records,
    repair_learning_index_status,
    summarize_repair_learning_record,
)


def handle_create_repair_learning_record(
    source_type, source_id, export_public, export_index, export_private, metadata
):
    return {
        "name": "Aether",
        "record": create_repair_learning_record(
            source_type, source_id, export_public, export_index, export_private, metadata
        ),
    }


def handle_export_repair_learning_report(learning_record_id, output_dir, metadata):
    return export_repair_learning_report(learning_record_id, output_dir, metadata)


def handle_export_repair_learning_index(output_path, limit, metadata):
    return export_repair_learning_index(output_path, limit, metadata)


def handle_export_private_repair_learning_record(learning_record_id, metadata):
    return export_private_repair_learning_record(learning_record_id, metadata)


def handle_get_repair_learning_status():
    return {
        "name": "Aether",
        "repair_learning": repair_learning_index_status(),
    }


def handle_list_repair_learning_records(
    status=None, learning_category=None, target_path=None, limit=50
):
    return {
        "name": "Aether",
        "records": list_repair_learning_records(
            status, learning_category, target_path, limit
        ),
    }


def handle_summarize_repair_learning_record(record_id):
    return {
        "name": "Aether",
        "summary": summarize_repair_learning_record(record_id),
    }


def handle_get_repair_learning_record(record_id):
    return {
        "name": "Aether",
        "record": get_repair_learning_record(record_id),
    }
