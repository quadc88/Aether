"""Service boundary for repair bridge selector API responses."""

from aether.action.repair_bridge_selector import (
    create_bridge_from_repair_plan,
    get_repair_bridge_selection,
    list_repair_bridge_selections,
    repair_bridge_selection_status,
    summarize_repair_bridge_selection,
)


def handle_create_repair_bridge_selection(
    repair_plan_id,
    finding_id,
    proposed_excerpt,
    original_excerpt,
    proposed_change_summary,
    reason,
    create_approval_if_required,
    metadata,
):
    return {
        "name": "Aether",
        "record": create_bridge_from_repair_plan(
            repair_plan_id,
            finding_id,
            proposed_excerpt,
            original_excerpt,
            proposed_change_summary,
            reason,
            create_approval_if_required,
            metadata,
        ),
    }


def handle_get_repair_bridge_selection_status():
    return {
        "name": "Aether",
        "repair_bridge_selection": repair_bridge_selection_status(),
    }


def handle_list_repair_bridge_selections(status=None, repair_plan_id=None, limit=50):
    return {
        "name": "Aether",
        "records": list_repair_bridge_selections(status, repair_plan_id, limit),
    }


def handle_summarize_repair_bridge_selection(record_id):
    return {
        "name": "Aether",
        "summary": summarize_repair_bridge_selection(record_id),
    }


def handle_get_repair_bridge_selection(record_id):
    return {
        "name": "Aether",
        "record": get_repair_bridge_selection(record_id),
    }
