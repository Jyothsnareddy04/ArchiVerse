from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional, Any
from datetime import datetime

# User Schemas
class UserBase(BaseModel):
    name: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    created_at: datetime
    class Config:
        from_attributes = True

# Auth Schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# Project Schemas
class ProjectBase(BaseModel):
    name: str
    plot_data: Optional[Any] = None

class ProjectCreate(ProjectBase):
    pass

class ProjectResponse(ProjectBase):
    id: int
    user_id: int
    created_at: datetime
    class Config:
        from_attributes = True

# Data Saver Schemas
class DataSaveRequest(BaseModel):
    project_id: int
    data: Any

class ProjectDetailResponse(ProjectResponse):
    layouts: List[Any] = []
    blueprints: List[Any] = []
    interiors: List[Any] = []
    exteriors: List[Any] = []
    costs: List[Any] = []
