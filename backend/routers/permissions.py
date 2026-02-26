from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import User, ProjectPermission, Project
from schemas import ProjectPermissionCreate, ProjectPermissionResponse
from auth import get_current_user

router = APIRouter(prefix="/api/permissions", tags=["权限管理"])

@router.post("/", response_model=ProjectPermissionResponse)
def create_permission(
    permission: ProjectPermissionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # 只有root用户或项目所有者可以分配权限
    project = db.query(Project).filter(Project.id == permission.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    
    if not current_user.is_root and project.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="权限不足")
    
    # 检查用户是否存在
    user = db.query(User).filter(User.id == permission.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 检查权限是否已存在
    existing = db.query(ProjectPermission).filter(
        ProjectPermission.project_id == permission.project_id,
        ProjectPermission.user_id == permission.user_id
    ).first()
    
    if existing:
        # 更新权限
        existing.can_edit = permission.can_edit
        db.commit()
        db.refresh(existing)
        return existing
    
    # 创建新权限
    db_permission = ProjectPermission(
        project_id=permission.project_id,
        user_id=permission.user_id,
        can_edit=permission.can_edit
    )
    db.add(db_permission)
    db.commit()
    db.refresh(db_permission)
    return db_permission

@router.get("/project/{project_id}", response_model=list[ProjectPermissionResponse])
def get_project_permissions(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    
    if not current_user.is_root and project.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="权限不足")
    
    permissions = db.query(ProjectPermission).filter(
        ProjectPermission.project_id == project_id
    ).all()
    return permissions

@router.delete("/{permission_id}")
def delete_permission(
    permission_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    permission = db.query(ProjectPermission).filter(ProjectPermission.id == permission_id).first()
    if not permission:
        raise HTTPException(status_code=404, detail="权限不存在")
    
    project = db.query(Project).filter(Project.id == permission.project_id).first()
    if not current_user.is_root and project.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="权限不足")
    
    db.delete(permission)
    db.commit()
    return {"message": "权限已删除"}

