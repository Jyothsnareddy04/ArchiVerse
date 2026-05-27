from fastapi import APIRouter
from schemas.layout_schema import LayoutRequest, LayoutResponse
from controllers.layout_controller import layout_controller

router = APIRouter(prefix="/api/layout", tags=["Layout"])

@router.post("/generate", response_model=LayoutResponse)
async def generate_layout(request: LayoutRequest):
    return await layout_controller.generate_layout(request)
