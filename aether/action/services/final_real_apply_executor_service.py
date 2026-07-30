"""Service boundary for final real-apply executor API responses."""

from aether.action.final_real_apply_executor import (
    execute_final_real_apply,
    final_real_apply_executor_status,
    get_final_real_apply_executor_record,
    list_final_real_apply_executor_records,
    open_final_real_apply_executor,
    summarize_final_real_apply_executor,
)


def handle_open_final_real_apply_executor(source_type, source_id, metadata):
    return {
        "name": "Aether",
        "record": open_final_real_apply_executor(source_type, source_id, metadata),
    }


def handle_execute_final_real_apply(executor_record_id, metadata=None):
    return {
        "name": "Aether",
        "record": execute_final_real_apply(executor_record_id, metadata),
    }


def handle_get_final_real_apply_executor_status():
    return {
        "name": "Aether",
        "final_real_apply_executor": final_real_apply_executor_status(),
    }


def handle_list_final_real_apply_executor_records(
    status=None, proposal_id=None, limit=50
):
    return {
        "name": "Aether",
        "records": list_final_real_apply_executor_records(status, proposal_id, limit),
    }


def handle_summarize_final_real_apply_executor(record_id):
    return {
        "name": "Aether",
        "summary": summarize_final_real_apply_executor(record_id),
    }


def handle_get_final_real_apply_executor_record(record_id):
    return {
        "name": "Aether",
        "record": get_final_real_apply_executor_record(record_id),
    }
