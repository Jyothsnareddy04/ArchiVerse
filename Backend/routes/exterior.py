from fastapi import APIRouter, Body
from schemas.layout_schema import GenericResponse
from controllers.exterior_controller import exterior_controller

router = APIRouter(prefix="/api/exterior", tags=["Exterior"])

@router.post("/generate", response_model=GenericResponse)
async def generate_exterior(data: dict = Body(...)):
    return await exterior_controller.generate_exterior(data)
