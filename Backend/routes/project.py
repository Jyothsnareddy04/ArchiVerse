from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import List
from database.db import get_db
from database.models import User, Project, Layout, Blueprint, Interior, Exterior, Cost
from database.schemas import ProjectCreate, ProjectResponse, ProjectDetailResponse, DataSaveRequest
from auth.auth_utils import get_current_user

router = APIRouter(prefix="/api/project", tags=["Projects"])

@router.post("/create", response_model=ProjectResponse)
async def create_project(
    project_data: ProjectCreate, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    new_project = Project(
        user_id=current_user.id,
        name=project_data.name,
        plot_data=project_data.plot_data
    )
    db.add(new_project)
    await db.commit()
    await db.refresh(new_project)
    return new_project

@router.get("/list", response_model=List[ProjectResponse])
async def list_projects(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(select(Project).where(Project.user_id == current_user.id))
    return result.scalars().all()

@router.get("/{project_id}", response_model=ProjectDetailResponse)
async def get_project(
    project_id: int, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(Project)
        .where(Project.id == project_id, Project.user_id == current_user.id)
        .options(
            selectinload(Project.layouts),
            selectinload(Project.blueprints),
            selectinload(Project.interiors),
            selectinload(Project.exteriors),
            selectinload(Project.costs)
        )
    )
    project = result.scalars().first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@router.post("/save-layout")
async def save_layout(req: DataSaveRequest, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    new_data = Layout(project_id=req.project_id, data=req.data)
    db.add(new_data)
    await db.commit()
    return {"success": True, "message": "Layout saved"}

@router.post("/save-blueprint")
async def save_blueprint(req: DataSaveRequest, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    new_data = Blueprint(project_id=req.project_id, data=req.data)
    db.add(new_data)
    await db.commit()
    return {"success": True, "message": "Blueprint saved"}

@router.post("/save-interior")
async def save_interior(req: DataSaveRequest, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    new_data = Interior(project_id=req.project_id, data=req.data)
    db.add(new_data)
    await db.commit()
    return {"success": True, "message": "Interior saved"}

@router.post("/save-exterior")
async def save_exterior(req: DataSaveRequest, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    new_data = Exterior(project_id=req.project_id, data=req.data)
    db.add(new_data)
    await db.commit()
    return {"success": True, "message": "Exterior saved"}

@router.post("/save-cost")
async def save_cost(req: DataSaveRequest, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    new_data = Cost(project_id=req.project_id, data=req.data)
    db.add(new_data)
    await db.commit()
    return {"success": True, "message": "Cost saved"}
