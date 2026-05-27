from fastapi import APIRouter, Body
from schemas.layout_schema import GenericResponse
from controllers.interior_controller import interior_controller

router = APIRouter(prefix="/api/interior", tags=["Interior"])

@router.post("/generate", response_model=GenericResponse)
async def generate_interior(data: dict = Body(...)):
    return await interior_controller.generate_interior(data)
