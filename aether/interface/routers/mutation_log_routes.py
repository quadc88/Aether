from fastapi import APIRouter

from aether.interface.api_models import (
    MilestoneCompletedRequest,
    MutationRecordRequest,
)

from aether.action.services.mutation_log_service import (
    handle_record_mutation,
    handle_record_milestone,
    handle_mutation_log_status,
    handle_list_mutations,
    handle_summarize_mutations,
    handle_get_mutation,
)

mutation_log_router = APIRouter()


@mutation_log_router.post("/action/mutation-log/record")
def record_action_mutation(request: MutationRecordRequest):
    return handle_record_mutation(
        request.mutation_type, request.title, request.summary,
        milestone=request.milestone, target_path=request.target_path,
        metadata=request.metadata,
    )


@mutation_log_router.post("/action/mutation-log/milestone-completed")
def record_action_milestone(request: MilestoneCompletedRequest):
    return handle_record_milestone(
        request.milestone, request.summary, request.metadata,
    )


@mutation_log_router.get("/action/mutation-log/status")
def get_action_mutation_status():
    return handle_mutation_log_status()


@mutation_log_router.get("/action/mutation-log/list")
def list_action_mutations(
    mutation_type: str | None = None,
    milestone: str | None = None,
    target_path: str | None = None,
    limit: int = 50,
):
    return handle_list_mutations(mutation_type, milestone, target_path, limit)


@mutation_log_router.get("/action/mutation-log/summary")
def summarize_action_mutations(limit: int = 100):
    return handle_summarize_mutations(limit)


@mutation_log_router.get("/action/mutation-log/{mutation_id}")
def get_action_mutation(mutation_id: str):
    return handle_get_mutation(mutation_id)
