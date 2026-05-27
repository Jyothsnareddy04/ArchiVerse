from fastapi import APIRouter
from schemas.blueprint_schema import ValidationRequest, ValidationFixResponse
from controllers.validation_controller import validation_controller

router = APIRouter(prefix="/api/validate", tags=["Validation"])

@router.post("/fix", response_model=ValidationFixResponse)
async def validate_fix(request: ValidationRequest):
    return await validation_controller.validate_and_fix(request)
