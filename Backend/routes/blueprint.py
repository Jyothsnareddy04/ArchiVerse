from fastapi import APIRouter
from schemas.layout_schema import BlueprintRequest, BlueprintResponse
from controllers.blueprint_controller import blueprint_controller

router = APIRouter(prefix="/api/blueprint", tags=["Blueprint"])

@router.post("/generate", response_model=BlueprintResponse)
async def generate_blueprint(request: BlueprintRequest):
    return await blueprint_controller.generate_blueprint(request)
