from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import User, Project, ProjectImage, ProjectStatusChange
from schemas import ProjectCreate, ProjectUpdate, ProjectResponse
from auth import get_current_user
from utils import save_upload_file
from datetime import datetime

router = APIRouter(prefix="/api/projects", tags=["项目管理"])

@router.get("", response_model=List[ProjectResponse])
def get_projects(
    skip: int = 0,
    limit: int = 100,
    status: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取项目列表
    - root用户：可以看到所有项目
    - 项目创建者：可以看到自己创建的所有项目（包括待审批的）
    - 已审批用户：可以看到所有已批准的项目（只读）
    """
    if current_user.is_root:
        # root用户可以看到所有项目
        query = db.query(Project)
    else:
        # 普通用户和已审批用户：看到自己创建的所有项目 + 其他人已批准的项目
        query = db.query(Project).filter(
            (Project.user_id == current_user.id) |  # 自己创建的所有项目
            (Project.approval_status == "approved")  # 或者已批准的项目
        )
    
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
    """
    创建项目
    - root用户创建的项目自动批准
    - 普通用户创建的项目需要等待审批
    """
    # 确定审批状态
    approval_status = "approved" if current_user.is_root else "pending"
    
    db_project = Project(
        **project.dict(),
        user_id=current_user.id,
        approval_status=approval_status
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
    """
    获取项目详情
    - root用户：可以查看所有项目
    - 项目创建者：可以查看自己创建的所有项目（包括待审批的）
    - 已审批用户：可以查看已批准的项目（只读）
    """
    project = db.query(Project).filter(Project.id == project_id).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    
    # 权限检查
    if current_user.is_root:
        # root用户可以查看所有项目
        pass
    elif project.user_id == current_user.id:
        # 项目创建者可以查看自己的所有项目（包括待审批的）
        pass
    elif project.approval_status == "approved":
        # 其他用户只能查看已批准的项目
        pass
    else:
        raise HTTPException(status_code=403, detail="权限不足")
    
    return project

@router.put("/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: int,
    project_update: ProjectUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    更新项目
    - 只有项目创建者和root用户可以编辑
    - 已审批用户只能查看，不能编辑
    """
    project = db.query(Project).filter(Project.id == project_id).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    
    # 权限检查：只有创建者和root可以编辑
    if not (project.user_id == current_user.id or current_user.is_root):
        raise HTTPException(status_code=403, detail="权限不足，只有项目创建者和管理员可以编辑")
    
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
    """
    删除项目
    - 只有项目创建者和root用户可以删除
    """
    project = db.query(Project).filter(Project.id == project_id).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    
    # 权限检查：只有创建者和root可以删除
    if not (project.user_id == current_user.id or current_user.is_root):
        raise HTTPException(status_code=403, detail="权限不足，只有项目创建者和管理员可以删除")
    
    db.delete(project)
    db.commit()
    return {"message": "项目已删除"}

@router.post("/{project_id}/approve")
def approve_project(
    project_id: int,
    approved: bool,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    审批项目（仅root用户）
    """
    if not current_user.is_root:
        raise HTTPException(status_code=403, detail="权限不足，只有管理员可以审批项目")
    
    project = db.query(Project).filter(Project.id == project_id).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    
    project.approval_status = "approved" if approved else "rejected"
    db.commit()
    db.refresh(project)
    
    return {
        "message": f"项目已{'批准' if approved else '拒绝'}",
        "project": project
    }

@router.get("/pending/list", response_model=List[ProjectResponse])
def get_pending_projects(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取待审批项目列表（仅root用户）
    """
    if not current_user.is_root:
        raise HTTPException(status_code=403, detail="权限不足")
    
    projects = db.query(Project).filter(Project.approval_status == "pending").all()
    return projects

@router.post("/{project_id}/request-status-change")
def request_status_change(
    project_id: int,
    new_status: str,
    reason: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    申请变更项目状态
    - Root用户：直接修改，不需要审批
    - 项目创建者：提交审批申请
    new_status: 进行中, 已完成, 暂停
    """
    project = db.query(Project).filter(Project.id == project_id).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    
    # 权限检查：只有项目创建者和root可以修改状态
    if not (project.user_id == current_user.id or current_user.is_root):
        raise HTTPException(status_code=403, detail="权限不足，只有项目创建者和管理员可以修改状态")
    
    # 验证新状态
    valid_statuses = ["进行中", "已完成", "暂停"]
    if new_status not in valid_statuses:
        raise HTTPException(status_code=400, detail="无效的状态")
    
    # 如果状态相同，不需要修改
    if project.status == new_status:
        raise HTTPException(status_code=400, detail="项目已经是该状态")
    
    # Root用户直接修改状态
    if current_user.is_root:
        old_status = project.status
        project.status = new_status
        db.commit()
        db.refresh(project)
        
        return {
            "message": "状态已直接修改",
            "old_status": old_status,
            "new_status": new_status
        }
    
    # 项目创建者需要提交审批申请
    status_change = ProjectStatusChange(
        project_id=project_id,
        old_status=project.status,
        new_status=new_status,
        requested_by=current_user.id,
        reason=reason,
        approval_status="pending"
    )
    
    db.add(status_change)
    db.commit()
    db.refresh(status_change)
    
    return {
        "message": "状态变更申请已提交，等待管理员审批",
        "change_id": status_change.id
    }

@router.get("/status-changes/pending")
def get_pending_status_changes(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取待审批的状态变更列表（仅root用户）
    """
    if not current_user.is_root:
        raise HTTPException(status_code=403, detail="权限不足")
    
    changes = db.query(ProjectStatusChange).filter(
        ProjectStatusChange.approval_status == "pending"
    ).all()
    
    # 关联项目和用户信息
    result = []
    for change in changes:
        project = db.query(Project).filter(Project.id == change.project_id).first()
        user = db.query(User).filter(User.id == change.requested_by).first()
        
        result.append({
            "id": change.id,
            "project_id": change.project_id,
            "project_name": project.name if project else "未知项目",
            "old_status": change.old_status,
            "new_status": change.new_status,
            "requested_by": user.username if user else "未知用户",
            "reason": change.reason,
            "created_at": change.created_at
        })
    
    return result

@router.post("/status-changes/{change_id}/approve")
def approve_status_change(
    change_id: int,
    approved: bool,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    审批状态变更申请（仅root用户）
    """
    if not current_user.is_root:
        raise HTTPException(status_code=403, detail="权限不足")
    
    change = db.query(ProjectStatusChange).filter(ProjectStatusChange.id == change_id).first()
    
    if not change:
        raise HTTPException(status_code=404, detail="状态变更申请不存在")
    
    if change.approval_status != "pending":
        raise HTTPException(status_code=400, detail="该申请已经被处理")
    
    # 更新申请状态
    change.approval_status = "approved" if approved else "rejected"
    change.approved_by = current_user.id
    change.approved_at = datetime.utcnow()
    
    # 如果批准，更新项目状态
    if approved:
        project = db.query(Project).filter(Project.id == change.project_id).first()
        if project:
            project.status = change.new_status
    
    db.commit()
    
    return {
        "message": f"状态变更申请已{'批准' if approved else '拒绝'}",
        "change": change
    }

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

