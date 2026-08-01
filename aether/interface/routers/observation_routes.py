"""Thin API router for the Observation Record feature line (Milestone 83D/83E).

Exposes create/get/list observation record endpoints backed by the 83C
service, plus the 83E update-status/cancel lifecycle endpoints. Endpoints
return pure 83B model shapes; the service envelope is stripped here.

The list handler is imported under an alias so this module never calls
store functions directly; all persistence stays inside the service/store.
"""

from fastapi import APIRouter, HTTPException, Request

from aether.interface.api_models import (
    ObservationRecordCancelRequest,
    ObservationRecordCreateRequest,
    ObservationRecordListResponse,
    ObservationRecordResponse,
    ObservationRecordUpdateStatusRequest,
)
from aether.action.services.observation_record_service import (
    handle_cancel_observation_record,
    handle_create_observation_record,
    handle_get_observation_record,
    handle_list_observation_records as list_observation_records_service,
    handle_update_observation_record_status,
)


observation_router = APIRouter()

_FORBIDDEN_CREATE_KEYS = {
    "observation_id",
    "observation_type",
    "observed_at",
    "safety_flags",
}

_FORBIDDEN_LIFECYCLE_KEYS = {
    "created_at",
    "updated_at",
    "decision",
    "decided_at",
    "decision_reason",
    "warnings",
    "context_metadata",
}

_FORBIDDEN_UPDATE_STATUS_KEYS = _FORBIDDEN_CREATE_KEYS | _FORBIDDEN_LIFECYCLE_KEYS | {
    "status",
}

_FORBIDDEN_CANCEL_KEYS = _FORBIDDEN_UPDATE_STATUS_KEYS | {"new_status"}


def _model_to_dict(model):
    if hasattr(model, "model_dump"):
        return model.model_dump()
    return model.dict()


async def _reject_forbidden_keys(raw_request: Request, forbidden_keys: set[str]) -> None:
    """Reject raw JSON payloads that supply generated/internal/lifecycle fields.

    The Pydantic request models ignore unknown fields by default, so the raw
    body must be inspected here to reject forbidden keys instead of silently
    dropping them.
    """
    try:
        raw_payload = await raw_request.json()
    except Exception:
        raw_payload = {}
    if isinstance(raw_payload, dict):
        forbidden = sorted(forbidden_keys & set(raw_payload))
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
    await _reject_forbidden_keys(raw_request, _FORBIDDEN_CREATE_KEYS)
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


@observation_router.patch(
    "/observation-records/{observation_id}/status",
    response_model=ObservationRecordResponse,
    operation_id="update_observation_record_status",
)
async def update_observation_record_status(
    observation_id: str,
    raw_request: Request,
    request: ObservationRecordUpdateStatusRequest,
):
    await _reject_forbidden_keys(raw_request, _FORBIDDEN_UPDATE_STATUS_KEYS)
    try:
        payload = _model_to_dict(request)
        result = handle_update_observation_record_status(
            observation_id, payload, context={}
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    if not result["found"]:
        raise HTTPException(status_code=404, detail="observation record not found")
    return result["observation_record"]


@observation_router.post(
    "/observation-records/{observation_id}/cancel",
    response_model=ObservationRecordResponse,
    operation_id="cancel_observation_record",
)
async def cancel_observation_record(
    observation_id: str,
    raw_request: Request,
    request: ObservationRecordCancelRequest,
):
    await _reject_forbidden_keys(raw_request, _FORBIDDEN_CANCEL_KEYS)
    try:
        payload = _model_to_dict(request)
        result = handle_cancel_observation_record(observation_id, payload, context={})
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    if not result["found"]:
        raise HTTPException(status_code=404, detail="observation record not found")
    return result["observation_record"]
