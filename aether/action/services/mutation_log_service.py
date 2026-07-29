"""Mutation Log Service — Milestone 82F.

Moves mutation-log endpoint orchestration from api_server.py into this service module.

Behavior-preserving refactor: no endpoint path, response shape, or safety changes.
"""

from aether.action.mutation_log import (
    record_mutation,
    record_milestone_completed,
    mutation_log_status,
    list_mutations,
    summarize_mutations,
    get_mutation,
)


def handle_record_mutation(
    mutation_type: str,
    title: str,
    summary: str,
    milestone: str | None = None,
    target_path: str | None = None,
    metadata: dict | None = None,
) -> dict:
    return {"name": "Aether", "mutation": record_mutation(
        mutation_type, title, summary,
        milestone=milestone, target_path=target_path,
        metadata=metadata, source="manual",
    )}


def handle_record_milestone(
    milestone: str,
    summary: str,
    metadata: dict | None = None,
) -> dict:
    return {"name": "Aether", "mutation": record_milestone_completed(milestone, summary, metadata)}


def handle_mutation_log_status() -> dict:
    return {"name": "Aether", "mutation_log": mutation_log_status()}


def handle_list_mutations(
    mutation_type: str | None = None,
    milestone: str | None = None,
    target_path: str | None = None,
    limit: int = 50,
) -> dict:
    return {"name": "Aether", "mutations": list_mutations(mutation_type, milestone, target_path, limit)}


def handle_summarize_mutations(limit: int = 100) -> dict:
    return {"name": "Aether", "summary": summarize_mutations(limit)}


def handle_get_mutation(mutation_id: str) -> dict:
    return {"name": "Aether", "mutation": get_mutation(mutation_id)}
