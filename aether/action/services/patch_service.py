"""Patch Lifecycle Service — Milestone 82E.

Moves patch proposal, review, apply, and rollback endpoint orchestration from
api_server.py into this service module.

Behavior-preserving refactor: no endpoint path, response shape, or safety changes.
"""

from aether.core.runtime import runtime

from aether.action.patch_proposal import (
    create_patch_proposal,
    get_patch_proposal,
    list_patch_proposals,
    mark_patch_proposal_status,
    patch_proposal_status,
)
from aether.action.patch_review import (
    get_patch_review,
    list_patch_reviews,
    patch_review_status,
    review_patch_proposal,
)
from aether.action.patch_apply import (
    apply_patch_proposal,
    get_patch_apply,
    list_patch_applies,
    patch_apply_status,
)
from aether.action.patch_rollback import (
    get_patch_rollback,
    list_patch_rollbacks,
    patch_rollback_status,
    rollback_patch_apply,
)


# --------------------------------------------------------------------------- #
# Patch Proposal handlers
# --------------------------------------------------------------------------- #


def handle_patch_proposal_create(
    target_path: str,
    request_text: str,
    proposed_change_summary: str,
    proposed_excerpt: str,
    reason: str,
    original_excerpt: str | None,
    create_approval_if_required: bool,
    metadata: dict,
) -> dict:
    proposal = create_patch_proposal(
        target_path,
        request_text,
        proposed_change_summary,
        proposed_excerpt,
        reason,
        original_excerpt,
        create_approval_if_required,
        metadata,
    )
    runtime.working_memory.add_event(
        role="aether",
        content=f"Patch proposal created: {proposal['target_path']}",
        event_type="patch_proposal_created",
        metadata={
            key: proposal.get(key)
            for key in ("id", "target_path", "status", "risk_level", "requires_user_approval", "approval_id")
        },
    )
    return {"name": "Aether", "status": runtime.status(), "proposal": proposal}


def handle_patch_proposal_status() -> dict:
    return {"name": "Aether", "status": runtime.status(), "patch_proposals": patch_proposal_status()}


def handle_list_patch_proposals(status: str | None = None, limit: int = 50) -> dict:
    return {"name": "Aether", "status": runtime.status(), "proposals": list_patch_proposals(status, limit)}


def handle_get_patch_proposal(proposal_id: str) -> dict:
    return {"name": "Aether", "status": runtime.status(), "proposal": get_patch_proposal(proposal_id)}


def handle_mark_patch_proposal_status(proposal_id: str, status: str, reason: str) -> dict:
    return {
        "name": "Aether",
        "status": runtime.status(),
        "proposal": mark_patch_proposal_status(proposal_id, status, reason),
    }


# --------------------------------------------------------------------------- #
# Patch Review handlers
# --------------------------------------------------------------------------- #


def handle_patch_review(
    proposal_id: str,
    decision: str,
    review_reason: str,
    reviewer: str,
    metadata: dict,
) -> dict:
    review = review_patch_proposal(proposal_id, decision, review_reason, reviewer, metadata)
    runtime.working_memory.add_event(
        role="aether",
        content=f"Patch review created: {decision}",
        event_type="patch_review_created",
        metadata={
            "review_id": review.get("id"),
            "proposal_id": proposal_id,
            "decision": decision,
            "status": review.get("status"),
            "proposal_status_after": review.get("proposal_status_after"),
            "risk_level": review.get("risk_level"),
            "approval_status": review.get("approval_status"),
        },
    )
    return {"name": "Aether", "status": runtime.status(), "review": review}


def handle_patch_review_status() -> dict:
    return {"name": "Aether", "status": runtime.status(), "patch_reviews": patch_review_status()}


def handle_list_patch_reviews(proposal_id: str | None = None, limit: int = 50) -> dict:
    return {"name": "Aether", "status": runtime.status(), "reviews": list_patch_reviews(proposal_id, limit)}


def handle_get_patch_review(review_id: str) -> dict:
    return {"name": "Aether", "status": runtime.status(), "review": get_patch_review(review_id)}


# --------------------------------------------------------------------------- #
# Patch Apply handlers
# --------------------------------------------------------------------------- #


def handle_patch_apply(proposal_id: str, dry_run: bool, metadata: dict) -> dict:
    result = apply_patch_proposal(proposal_id, dry_run, metadata)
    runtime.working_memory.add_event(
        role="aether",
        content=f"Patch apply attempted: {result['status']}",
        event_type="patch_apply_attempted",
        metadata={
            k: result.get(k)
            for k in ("id", "proposal_id", "target_path", "status", "dry_run", "applied", "changed", "risk_level")
        },
    )
    return {"name": "Aether", "status": runtime.status(), "apply": result}


def handle_patch_apply_status() -> dict:
    return {"name": "Aether", "status": runtime.status(), "patch_applies": patch_apply_status()}


def handle_list_patch_applies(proposal_id: str | None = None, limit: int = 50) -> dict:
    return {"name": "Aether", "status": runtime.status(), "applies": list_patch_applies(proposal_id, limit)}


def handle_get_patch_apply(apply_id: str) -> dict:
    return {"name": "Aether", "status": runtime.status(), "apply": get_patch_apply(apply_id)}


# --------------------------------------------------------------------------- #
# Patch Rollback handlers
# --------------------------------------------------------------------------- #


def handle_patch_rollback(apply_id: str, dry_run: bool, metadata: dict) -> dict:
    r = rollback_patch_apply(apply_id, dry_run, metadata)
    runtime.working_memory.add_event(
        role="aether",
        content=f"Patch rollback attempted: {r['status']}",
        event_type="patch_rollback_attempted",
        metadata={
            k: r.get(k)
            for k in ("id", "apply_id", "proposal_id", "target_path", "status", "dry_run", "rolled_back", "changed")
        },
    )
    return {"name": "Aether", "status": runtime.status(), "rollback": r}


def handle_patch_rollback_status() -> dict:
    return {"name": "Aether", "status": runtime.status(), "patch_rollbacks": patch_rollback_status()}


def handle_list_patch_rollbacks(apply_id: str | None = None, limit: int = 50) -> dict:
    return {"name": "Aether", "status": runtime.status(), "rollbacks": list_patch_rollbacks(apply_id, limit)}


def handle_get_patch_rollback(rollback_id: str) -> dict:
    return {"name": "Aether", "status": runtime.status(), "rollback": get_patch_rollback(rollback_id)}
