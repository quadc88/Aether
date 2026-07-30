"""Service boundary for post-apply verification gate API responses."""

from aether.action.post_apply_verification_gate import (
    get_post_apply_verification_gate_record,
    list_post_apply_verification_gate_records,
    open_post_apply_verification_gate,
    post_apply_verification_gate_status,
    submit_post_apply_verification,
    summarize_post_apply_verification_gate,
)


def handle_open_post_apply_verification_gate(source_type, source_id, metadata):
    return {
        "name": "Aether",
        "record": open_post_apply_verification_gate(
            source_type, source_id, metadata
        ),
    }


def handle_submit_post_apply_verification(
    verification_record_id,
    decision,
    comment=None,
    verifier="human",
    metadata=None,
):
    return {
        "name": "Aether",
        "record": submit_post_apply_verification(
            verification_record_id, decision, comment, verifier, metadata
        ),
    }


def handle_get_post_apply_verification_gate_status():
    return {
        "name": "Aether",
        "post_apply_verification_gate": post_apply_verification_gate_status(),
    }


def handle_list_post_apply_verification_gate_records(
    status=None, proposal_id=None, limit=50
):
    return {
        "name": "Aether",
        "records": list_post_apply_verification_gate_records(
            status, proposal_id, limit
        ),
    }


def handle_summarize_post_apply_verification_gate(record_id):
    return {
        "name": "Aether",
        "summary": summarize_post_apply_verification_gate(record_id),
    }


def handle_get_post_apply_verification_gate_record(record_id):
    return {
        "name": "Aether",
        "record": get_post_apply_verification_gate_record(record_id),
    }
