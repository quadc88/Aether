"""Service boundary for repair guidance API responses."""

from aether.action.repair_guidance_engine import (
    create_repair_guidance,
    export_private_repair_guidance_record,
    export_repair_guidance_index,
    export_repair_guidance_report,
    get_repair_guidance_record,
    list_repair_guidance_records,
    repair_guidance_engine_status,
    summarize_repair_guidance,
)


def handle_create_repair_guidance(
    request_type,
    requested_scope,
    target_path,
    source_type,
    source_id,
    export_public,
    export_index,
    export_private,
    metadata,
):
    return {
        "name": "Aether",
        "record": create_repair_guidance(
            request_type,
            requested_scope,
            target_path,
            source_type,
            source_id,
            export_public,
            export_index,
            export_private,
            metadata,
        ),
    }


def handle_export_repair_guidance_report(guidance_record_id, output_dir, metadata):
    return export_repair_guidance_report(guidance_record_id, output_dir, metadata)


def handle_export_repair_guidance_index(output_path, limit, metadata):
    return export_repair_guidance_index(output_path, limit, metadata)


def handle_export_private_repair_guidance_record(guidance_record_id, metadata):
    return export_private_repair_guidance_record(guidance_record_id, metadata)


def handle_get_repair_guidance_status():
    return {
        "name": "Aether",
        "repair_guidance": repair_guidance_engine_status(),
    }


def handle_list_repair_guidance_records(
    status=None, guidance_decision=None, target_path=None, limit=50
):
    return {
        "name": "Aether",
        "records": list_repair_guidance_records(
            status, guidance_decision, target_path, limit
        ),
    }


def handle_summarize_repair_guidance(record_id):
    return {
        "name": "Aether",
        "summary": summarize_repair_guidance(record_id),
    }


def handle_get_repair_guidance_record(record_id):
    return {
        "name": "Aether",
        "record": get_repair_guidance_record(record_id),
    }
