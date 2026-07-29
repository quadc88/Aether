"""Code Review and Review Bridge Service — Milestone 82H.

Moves code-review and review-bridge endpoint orchestration from api_server.py
into this service module.

Behavior-preserving refactor: no endpoint path, response shape,
or safety changes.
"""

from aether.action.code_reviewer import (
    create_code_review,
    get_code_review,
    list_code_reviews,
    code_review_status,
    summarize_code_review,
)
from aether.action.review_bridge import (
    create_bridge_from_finding,
    get_review_bridge_record,
    list_review_bridge_records,
    review_bridge_status,
    summarize_review_bridge_record,
)


# --------------------------------------------------------------------------- #
# Code Review handlers
# --------------------------------------------------------------------------- #


def handle_code_review_create(
    scope: str,
    target_paths: list[str] | None = None,
    max_files: int = 20,
    max_chars_per_file: int = 12000,
    include_tests: bool = True,
    metadata: dict | None = None,
) -> dict:
    return {"name": "Aether", "report": create_code_review(
        scope, target_paths, max_files, max_chars_per_file,
        include_tests, metadata,
    )}


def handle_code_review_status() -> dict:
    return {"name": "Aether", "code_review": code_review_status()}


def handle_list_code_reviews(status: str | None = None, limit: int = 50) -> dict:
    return {"name": "Aether", "reports": list_code_reviews(status, limit)}


def handle_summarize_code_review(report_id: str) -> dict:
    return {"name": "Aether", "summary": summarize_code_review(report_id)}


def handle_get_code_review(report_id: str) -> dict:
    return {"name": "Aether", "report": get_code_review(report_id)}


# --------------------------------------------------------------------------- #
# Review Bridge handlers
# --------------------------------------------------------------------------- #


def handle_create_review_bridge(
    report_id: str,
    finding_id: str,
    proposed_excerpt: str,
    original_excerpt: str | None = None,
    proposed_change_summary: str | None = None,
    reason: str | None = None,
    create_approval_if_required: bool = False,
    metadata: dict | None = None,
) -> dict:
    return {"name": "Aether", "record": create_bridge_from_finding(
        report_id, finding_id, proposed_excerpt, original_excerpt,
        proposed_change_summary, reason, create_approval_if_required,
        metadata,
    )}


def handle_review_bridge_status() -> dict:
    return {"name": "Aether", "review_bridge": review_bridge_status()}


def handle_list_review_bridges(
    status: str | None = None,
    review_report_id: str | None = None,
    limit: int = 50,
) -> dict:
    return {"name": "Aether", "records": list_review_bridge_records(status, review_report_id, limit)}


def handle_summarize_review_bridge(record_id: str) -> dict:
    return {"name": "Aether", "summary": summarize_review_bridge_record(record_id)}


def handle_get_review_bridge(record_id: str) -> dict:
    return {"name": "Aether", "record": get_review_bridge_record(record_id)}
