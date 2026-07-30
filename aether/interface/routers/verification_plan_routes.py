from fastapi import APIRouter

from aether.action.services.verification_plan_service import (
    handle_create_verification_plan,
)
from aether.interface.api_models import VerificationRequest


verification_plan_router = APIRouter()


@verification_plan_router.post("/verification/plan")
def create_verification_plan(request: VerificationRequest):
    return handle_create_verification_plan(request.text)
