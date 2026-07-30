"""Service boundary for approved dry-run gate API responses."""

from aether.action.approved_dry_run_gate import (
    approved_dry_run_gate_status,
    execute_approved_dry_run,
    get_approved_dry_run_gate_record,
    list_approved_dry_run_gate_records,
    open_approved_dry_run_gate,
    summarize_approved_dry_run_gate,
)


def handle_open_approved_dry_run_gate(source_type, source_id, metadata):
    return {
        "name": "Aether",
        "record": open_approved_dry_run_gate(source_type, source_id, metadata),
    }


def handle_execute_approved_dry_run(
    gate_record_id, create_approval_if_required=False, metadata=None
):
    return {
        "name": "Aether",
        "record": execute_approved_dry_run(
            gate_record_id, create_approval_if_required, metadata
        ),
    }


def handle_get_approved_dry_run_gate_status():
    return {
        "name": "Aether",
        "approved_dry_run_gate": approved_dry_run_gate_status(),
    }


def handle_list_approved_dry_run_gate_records(
    status=None, proposal_id=None, limit=50
):
    return {
        "name": "Aether",
        "records": list_approved_dry_run_gate_records(status, proposal_id, limit),
    }


def handle_summarize_approved_dry_run_gate(record_id):
    return {
        "name": "Aether",
        "summary": summarize_approved_dry_run_gate(record_id),
    }


def handle_get_approved_dry_run_gate_record(record_id):
    return {
        "name": "Aether",
        "record": get_approved_dry_run_gate_record(record_id),
    }
