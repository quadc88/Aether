"""Sandbox Contract Service — Thin Interface Refactor Phase 6 (Milestone 80G).

Moves Milestone 58A orchestration out of api_server.py into this service module.

This module handles:
- Sandbox contract creation (build from dry-run record + response shaping)

Behavior-preserving refactor: no endpoint path, response shape, or safety changes.
"""

from aether.core.runtime import runtime

from aether.action.dry_run_queue import (
    get_dry_run_record as _get_dr,
)
from aether.action.dry_run_sandbox_contract import (
    build_dry_run_sandbox_contract as _build_contract,
)


def handle_sandbox_contract_create(
    dry_run_id: str,
    context: dict | None = None,
) -> dict:
    """Build a sandbox contract from a dry-run record."""
    dr_record = _get_dr(dry_run_id) if dry_run_id else None
    contract = _build_contract(dr_record, context)
    return {
        "name": "Aether",
        "status": runtime.status(),
        **contract,
    }
