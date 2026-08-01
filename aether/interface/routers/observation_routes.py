"""Thin API router for the Observation Record feature line (Milestone 83D).

Exposes create/get/list observation record endpoints backed by the 83C
service. Endpoints return pure 83B model shapes; the service envelope is
stripped here. The update and cancel lifecycle endpoints are intentionally
deferred to a later milestone and are not exposed.

The list handler is imported under an alias so this module never calls
store functions directly; all persistence stays inside the service/store.
"""

from fastapi import APIRouter, HTTPException, Request

from aether.interface.api_models import (
    ObservationRecordCreateRequest,
    ObservationRecordListResponse,
    ObservationRecordResponse,
)
from aether.action.services.observation_record_service import (
    handle_create_observation_record,
    handle_get_observation_record,
    handle_list_observation_records as list_observation_records_service,
)


observation_router = APIRouter()

_FORBIDDEN_CREATE_KEYS = {
    "observation_id",
    "observation_type",
    "observed_at",
    "safety_flags",
}


def _model_to_dict(model):
    if hasattr(model, "model_dump"):
        return model.model_dump()
    return model.dict()


async def _reject_forbidden_create_keys(raw_request: Request) -> None:
    """Reject raw JSON create payloads that supply generated/internal fields.

    The Pydantic request model ignores unknown fields by default, so the raw
    body must be inspected here to reject generated/internal keys instead of
    silently dropping them.
    """
    try:
        raw_payload = await raw_request.json()
    except Exception:
        raw_payload = {}
    if isinstance(raw_payload, dict):
        forbidden = sorted(_FORBIDDEN_CREATE_KEYS & set(raw_payload))
        if forbidden:
            raise HTTPException(
                status_code=400,
                detail="generated/internal fields are not accepted: "
                + ", ".join(forbidden),
            )


@observation_router.post(
    "/observation-records",
    response_model=ObservationRecordResponse,
    operation_id="create_observation_record",
)
async def create_observation_record(
    raw_request: Request,
    request: ObservationRecordCreateRequest,
):
    await _reject_forbidden_create_keys(raw_request)
    try:
        payload = _model_to_dict(request)
        result = handle_create_observation_record(payload, context={})
        return result["observation_record"]
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@observation_router.get(
    "/observation-records/{observation_id}",
    response_model=ObservationRecordResponse,
    operation_id="get_observation_record",
)
def get_observation_record(observation_id: str):
    try:
        result = handle_get_observation_record(observation_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    if not result["found"]:
        raise HTTPException(status_code=404, detail="observation record not found")
    return result["observation_record"]


@observation_router.get(
    "/observation-records",
    response_model=ObservationRecordListResponse,
    operation_id="list_observation_records",
)
def list_observation_records_endpoint(
    status: str | None = None,
    limit: int = 50,
    offset: int = 0,
):
    try:
        result = list_observation_records_service(status=status, limit=limit, offset=offset)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return {
        "records": result["observation_records"],
        "total": result["total"],
        "limit": result["limit"],
        "offset": result["offset"],
    }
