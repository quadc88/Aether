"""Service boundary for real-apply approval gate API responses."""

from aether.action.real_apply_approval_gate import (
    get_real_apply_approval_gate_record,
    list_real_apply_approval_gate_records,
    open_real_apply_approval_gate,
    real_apply_approval_gate_status,
    submit_real_apply_final_decision,
    summarize_real_apply_approval_gate,
)


def handle_open_real_apply_approval_gate(
    source_type, source_id, create_approval_item=True, metadata=None
):
    return {
        "name": "Aether",
        "record": open_real_apply_approval_gate(
            source_type, source_id, create_approval_item, metadata
        ),
    }


def handle_submit_real_apply_final_decision(
    gate_record_id,
    decision,
    comment=None,
    reviewer="human",
    metadata=None,
):
    return {
        "name": "Aether",
        "record": submit_real_apply_final_decision(
            gate_record_id, decision, comment, reviewer, metadata
        ),
    }


def handle_get_real_apply_approval_gate_status():
    return {
        "name": "Aether",
        "real_apply_approval_gate": real_apply_approval_gate_status(),
    }


def handle_list_real_apply_approval_gate_records(
    status=None, proposal_id=None, limit=50
):
    return {
        "name": "Aether",
        "records": list_real_apply_approval_gate_records(
            status, proposal_id, limit
        ),
    }


def handle_summarize_real_apply_approval_gate(record_id):
    return {
        "name": "Aether",
        "summary": summarize_real_apply_approval_gate(record_id),
    }


def handle_get_real_apply_approval_gate_record(record_id):
    return {
        "name": "Aether",
        "record": get_real_apply_approval_gate_record(record_id),
    }
