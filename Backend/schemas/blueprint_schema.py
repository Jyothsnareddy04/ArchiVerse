from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class ValidationRequest(BaseModel):
    blueprint_json: Dict[str, Any]

class ValidationFixResponse(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None
    original_errors: Optional[List[Dict[str, Any]]] = None
    error: Optional[str] = None
