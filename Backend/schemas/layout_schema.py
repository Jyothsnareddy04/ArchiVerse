from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class LayoutRequest(BaseModel):
    plot_width: float
    plot_depth: float
    floors: int = 1
    preferences: Dict[str, Any] = Field(default_factory=dict)

class LayoutResponse(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class BlueprintRequest(BaseModel):
    layout_id: str
    layout_data: Dict[str, Any] = Field(default_factory=dict)
    requirements: Dict[str, Any] = Field(default_factory=dict)

class BlueprintResponse(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class GenericResponse(BaseModel):
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
