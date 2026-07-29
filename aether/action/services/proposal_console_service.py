"""Proposal Console Service — Milestone 82G.

Moves proposal-review-console, proposal-revision-console, and
revised-proposal-review endpoint orchestration from api_server.py
into this service module.

Behavior-preserving refactor: no endpoint path, response shape,
or safety changes.
"""

from aether.action.proposal_review_console import (
    open_proposal_review_console,
    submit_proposal_review,
    get_proposal_review_console_record,
    list_proposal_review_console_records,
    proposal_review_console_status,
    summarize_proposal_review_console,
)
from aether.action.proposal_revision_console import (
    open_proposal_revision_console,
    create_proposal_revision,
    get_proposal_revision_console_record,
    list_proposal_revision_console_records,
    proposal_revision_console_status,
    summarize_proposal_revision_console,
)
from aether.action.revised_proposal_review_loop import (
    open_revised_proposal_review,
    submit_revised_proposal_review,
    get_revised_proposal_review_loop_record,
    list_revised_proposal_review_loop_records,
    revised_proposal_review_loop_status,
    summarize_revised_proposal_review_loop,
)


# --------------------------------------------------------------------------- #
# Proposal Review Console handlers
# --------------------------------------------------------------------------- #


def handle_open_proposal_review_console(
    source_type: str, source_id: str, metadata: dict | None = None
) -> dict:
    return {"name": "Aether", "record": open_proposal_review_console(
        source_type, source_id, metadata,
    )}


def handle_submit_proposal_review(
    console_record_id: str,
    decision: str,
    comment: str | None = None,
    reviewer: str = "human",
    create_approval_if_required: bool = False,
    metadata: dict | None = None,
) -> dict:
    return {"name": "Aether", "record": submit_proposal_review(
        console_record_id, decision, comment, reviewer,
        create_approval_if_required, metadata,
    )}


def handle_proposal_review_console_status() -> dict:
    return {"name": "Aether", "proposal_review_console": proposal_review_console_status()}


def handle_list_proposal_review_console(
    status: str | None = None,
    proposal_id: str | None = None,
    limit: int = 50,
) -> dict:
    return {"name": "Aether", "records": list_proposal_review_console_records(status, proposal_id, limit)}


def handle_summarize_proposal_review_console(record_id: str) -> dict:
    return {"name": "Aether", "summary": summarize_proposal_review_console(record_id)}


def handle_get_proposal_review_console(record_id: str) -> dict:
    return {"name": "Aether", "record": get_proposal_review_console_record(record_id)}


# --------------------------------------------------------------------------- #
# Proposal Revision Console handlers
# --------------------------------------------------------------------------- #


def handle_open_proposal_revision_console(
    source_type: str, source_id: str, metadata: dict | None = None
) -> dict:
    return {"name": "Aether", "record": open_proposal_revision_console(
        source_type, source_id, metadata,
    )}


def handle_create_proposal_revision(
    revision_record_id: str,
    revised_proposed_excerpt: str,
    revised_change_summary: str | None = None,
    human_revision_note: str | None = None,
    create_approval_if_required: bool = False,
    metadata: dict | None = None,
) -> dict:
    return {"name": "Aether", "record": create_proposal_revision(
        revision_record_id, revised_proposed_excerpt,
        revised_change_summary, human_revision_note,
        create_approval_if_required, metadata,
    )}


def handle_proposal_revision_console_status() -> dict:
    return {"name": "Aether", "proposal_revision_console": proposal_revision_console_status()}


def handle_list_proposal_revision_console(
    status: str | None = None,
    original_proposal_id: str | None = None,
    limit: int = 50,
) -> dict:
    return {"name": "Aether", "records": list_proposal_revision_console_records(status, original_proposal_id, limit)}


def handle_summarize_proposal_revision_console(record_id: str) -> dict:
    return {"name": "Aether", "summary": summarize_proposal_revision_console(record_id)}


def handle_get_proposal_revision_console(record_id: str) -> dict:
    return {"name": "Aether", "record": get_proposal_revision_console_record(record_id)}


# --------------------------------------------------------------------------- #
# Revised Proposal Review Loop handlers
# --------------------------------------------------------------------------- #


def handle_open_revised_proposal_review(
    proposal_revision_console_id: str, metadata: dict | None = None
) -> dict:
    return {"name": "Aether", "record": open_revised_proposal_review(
        proposal_revision_console_id, metadata,
    )}


def handle_submit_revised_proposal_review(
    review_loop_record_id: str,
    decision: str,
    comment: str | None = None,
    reviewer: str = "human",
    create_approval_if_required: bool = False,
    metadata: dict | None = None,
) -> dict:
    return {"name": "Aether", "record": submit_revised_proposal_review(
        review_loop_record_id, decision, comment, reviewer,
        create_approval_if_required, metadata,
    )}


def handle_revised_proposal_review_status() -> dict:
    return {"name": "Aether", "revised_proposal_review": revised_proposal_review_loop_status()}


def handle_list_revised_proposal_review(
    status: str | None = None,
    revised_proposal_id: str | None = None,
    limit: int = 50,
) -> dict:
    return {"name": "Aether", "records": list_revised_proposal_review_loop_records(status, revised_proposal_id, limit)}


def handle_summarize_revised_proposal_review(record_id: str) -> dict:
    return {"name": "Aether", "summary": summarize_revised_proposal_review_loop(record_id)}


def handle_get_revised_proposal_review(record_id: str) -> dict:
    return {"name": "Aether", "record": get_revised_proposal_review_loop_record(record_id)}
