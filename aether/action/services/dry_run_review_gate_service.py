"""Service boundary for dry-run review gate API responses."""

from aether.action.dry_run_review_gate import (
    dry_run_review_gate_status,
    get_dry_run_review_gate_record,
    list_dry_run_review_gate_records,
    open_dry_run_review_gate,
    submit_dry_run_review,
    summarize_dry_run_review_gate,
)


def handle_open_dry_run_review_gate(source_type, source_id, metadata):
    return {
        "name": "Aether",
        "record": open_dry_run_review_gate(source_type, source_id, metadata),
    }


def handle_submit_dry_run_review(
    review_gate_record_id,
    decision,
    comment=None,
    reviewer="human",
    metadata=None,
):
    return {
        "name": "Aether",
        "record": submit_dry_run_review(
            review_gate_record_id, decision, comment, reviewer, metadata
        ),
    }


def handle_get_dry_run_review_gate_status():
    return {
        "name": "Aether",
        "dry_run_review_gate": dry_run_review_gate_status(),
    }


def handle_list_dry_run_review_gate_records(
    status=None, proposal_id=None, limit=50
):
    return {
        "name": "Aether",
        "records": list_dry_run_review_gate_records(status, proposal_id, limit),
    }


def handle_summarize_dry_run_review_gate(record_id):
    return {
        "name": "Aether",
        "summary": summarize_dry_run_review_gate(record_id),
    }


def handle_get_dry_run_review_gate_record(record_id):
    return {
        "name": "Aether",
        "record": get_dry_run_review_gate_record(record_id),
    }
