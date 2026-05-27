from typing import Optional, Tuple

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from api.auth import verify_api_key

try:
    from agents.Layout_Agent.pipeline import run_pipeline
except ImportError:
    run_pipeline = None

router = APIRouter()


class LayoutRequest(BaseModel):
    # Plot / units
    plot: Optional[Tuple[float, float]] = None
    plot_dimensions: Optional[str] = None
    plot_width: Optional[float] = None
    plot_depth: Optional[float] = None
    area: Optional[float] = None
    area_sq_yards: Optional[float] = None
    area_sq_m: Optional[float] = None
    unit: Optional[str] = None  # "feet" (default) or "meter"
    plot_ratio: Optional[Tuple[float, float]] = None  # e.g. (3,5) for 30x50-ish

    # Regulations
    setback: Optional[dict] = None
    setback_unit: Optional[str] = None  # "ft" (default) or "m"
    road_width: Optional[float] = None
    road_width_unit: Optional[str] = None  # "ft" (default) or "m"

    facing: str = "north"
    house_type: str = "individual"
    floors: int = 1

    bedrooms: int = Field(default=2, ge=1)
    bathrooms: int = Field(default=2, ge=1)
    extras: int = 0

    has_parking: bool = True
    has_stair: bool = True
    has_dining: bool = True
    has_balcony: bool = False
    has_store: bool = False
    has_backyard: bool = False
    has_veranda: Optional[bool] = None

    # Generation controls
    num_layouts: int = Field(default=1, ge=1, le=3)
    use_llm: Optional[bool] = None


@router.post("/generate-layout")
def generate_layout_api(req: LayoutRequest, key: str = Depends(verify_api_key)):
    if run_pipeline is None:
        return {"error": "Layout pipeline not available"}
    payload = req.model_dump() if hasattr(req, "model_dump") else req.dict()
    return run_pipeline(payload, render=False)
