from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import User, Project, ProjectImage
from schemas import ProjectCreate, ProjectUpdate, ProjectResponse
from auth import get_current_user
from utils import save_upload_file

router = APIRouter(prefix="/api/projects", tags=["项目管理"])

@router.get("", response_model=List[ProjectResponse])
def get_projects(
    skip: int = 0,
    limit: int = 100,
    status: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Project).filter(Project.user_id == current_user.id)
    if status:
        query = query.filter(Project.status == status)
    projects = query.offset(skip).limit(limit).all()
    return projects

@router.post("", response_model=ProjectResponse)
def create_project(
    project: ProjectCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_project = Project(
        **project.dict(),
        user_id=current_user.id
    )
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user.id
    ).first()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    return project

@router.put("/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: int,
    project_update: ProjectUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user.id
    ).first()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    
    for key, value in project_update.dict(exclude_unset=True).items():
        setattr(project, key, value)
    
    db.commit()
    db.refresh(project)
    return project

@router.delete("/{project_id}")
def delete_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user.id
    ).first()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    
    db.delete(project)
    db.commit()
    return {"message": "项目已删除"}

@router.post("/{project_id}/images")
async def upload_project_image(
    project_id: int,
    file: UploadFile = File(...),
    description: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user.id
    ).first()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    
    # 保存图片
    image_url = await save_upload_file(file, "image")
    
    # 创建图片记录
    db_image = ProjectImage(
        project_id=project_id,
        image_url=image_url,
        description=description
    )
    db.add(db_image)
    db.commit()
    db.refresh(db_image)
    
    return {"image_url": image_url, "id": db_image.id}

