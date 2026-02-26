from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import User, Project, ProjectDocument
from auth import get_current_user
from utils import save_upload_file
import os

router = APIRouter(prefix="/api/projects", tags=["项目资料"])

def check_project_edit_permission(project: Project, current_user: User):
    """
    检查项目编辑权限
    - Root用户：可以编辑所有项目
    - 项目创建者：可以编辑自己的项目
    - 其他用户：无编辑权限
    """
    if current_user.is_root:
        return True
    if project.user_id == current_user.id:
        return True
    return False

def check_project_view_permission(project: Project, current_user: User):
    """
    检查项目查看权限
    - Root用户：可以查看所有项目
    - 项目创建者：可以查看自己的所有项目（包括待审批的）
    - 已审批用户：可以查看已批准的项目
    """
    if current_user.is_root:
        return True
    if project.user_id == current_user.id:
        return True
    if project.approval_status == "approved":
        return True
    return False

@router.post("/{project_id}/documents/upload")
async def upload_document(
    project_id: int,
    doc_type: str,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    上传项目资料
    - Root用户：可以上传所有项目的资料
    - 项目创建者：可以上传自己项目的资料
    """
    project = db.query(Project).filter(Project.id == project_id).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    
    # 检查编辑权限
    if not check_project_edit_permission(project, current_user):
        raise HTTPException(status_code=403, detail="权限不足，只有项目创建者和管理员可以上传资料")
    
    # 保存文件
    file_path = await save_upload_file(file, f"projects/{project_id}/documents")
    
    # 检查是否已存在该类型的文档
    existing_doc = db.query(ProjectDocument).filter(
        ProjectDocument.project_id == project_id,
        ProjectDocument.doc_type == doc_type
    ).first()
    
    if existing_doc:
        # 删除旧文件
        if os.path.exists(existing_doc.file_path):
            os.remove(existing_doc.file_path)
        # 更新记录
        existing_doc.file_path = file_path
        existing_doc.file_name = file.filename
        existing_doc.file_size = file.size
        existing_doc.uploaded_by = current_user.id
    else:
        # 创建新记录
        doc = ProjectDocument(
            project_id=project_id,
            doc_type=doc_type,
            file_path=file_path,
            file_name=file.filename,
            file_size=file.size,
            uploaded_by=current_user.id
        )
        db.add(doc)
    
    db.commit()
    
    return {"message": "文件上传成功", "file_path": file_path}

@router.get("/{project_id}/documents")
def get_documents(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取项目资料列表
    """
    project = db.query(Project).filter(Project.id == project_id).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    
    # 检查查看权限
    if not check_project_view_permission(project, current_user):
        raise HTTPException(status_code=403, detail="权限不足")
    
    documents = db.query(ProjectDocument).filter(
        ProjectDocument.project_id == project_id
    ).all()
    
    # 转换为字典格式
    result = {}
    for doc in documents:
        result[doc.doc_type] = {
            "id": doc.id,
            "file_name": doc.file_name,
            "file_path": doc.file_path,
            "file_size": doc.file_size,
            "uploaded_at": doc.uploaded_at
        }
    
    return result

@router.get("/{project_id}/quotation")
def get_quotation(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取项目报价数据
    """
    project = db.query(Project).filter(Project.id == project_id).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    
    # 检查查看权限
    if not check_project_view_permission(project, current_user):
        raise HTTPException(status_code=403, detail="权限不足")
    
    return {
        "land_area": project.land_area,
        "floor_area_ratio": project.floor_area_ratio,
        "green_ratio": project.green_ratio,
        "density": project.density,
        "height": project.height,
        "total_building_area": project.total_building_area,
        "above_ground_area": project.above_ground_area,
        "underground_area": project.underground_area,
        "residential_units": project.residential_units,
        "commercial_units": project.commercial_units,
        "supporting_area": project.supporting_area,
        "basement_estimated_area": project.basement_estimated_area,
        "parking_area": project.parking_area
    }

@router.put("/{project_id}/quotation")
def update_quotation(
    project_id: int,
    quotation_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    更新项目报价数据
    - Root用户：可以编辑所有项目
    - 项目创建者：可以编辑自己的项目
    """
    project = db.query(Project).filter(Project.id == project_id).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    
    # 检查编辑权限
    if not check_project_edit_permission(project, current_user):
        raise HTTPException(status_code=403, detail="权限不足，只有项目创建者和管理员可以编辑")
    
    # 更新报价数据
    allowed_fields = [
        "land_area", "floor_area_ratio", "green_ratio", "density", "height",
        "total_building_area", "above_ground_area", "underground_area",
        "residential_units", "commercial_units", "supporting_area",
        "basement_estimated_area", "parking_area"
    ]
    
    for field in allowed_fields:
        if field in quotation_data:
            setattr(project, field, quotation_data[field])
    
    db.commit()
    db.refresh(project)
    
    return {"message": "报价数据已更新"}

@router.post("/{project_id}/convert-to-cad")
async def convert_pdf_to_cad(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    将用地红线PDF转换为CAD格式
    """
    project = db.query(Project).filter(Project.id == project_id).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    
    # 检查编辑权限
    if not check_project_edit_permission(project, current_user):
        raise HTTPException(status_code=403, detail="权限不足")
    
    # 查找用地红线文档
    land_boundary_doc = db.query(ProjectDocument).filter(
        ProjectDocument.project_id == project_id,
        ProjectDocument.doc_type == "land_boundary"
    ).first()
    
    if not land_boundary_doc:
        raise HTTPException(status_code=404, detail="未找到用地红线文档")
    
    # TODO: 实现PDF转CAD功能
    # 这里需要使用OpenCV和ezdxf库进行转换
    
    return {"message": "PDF转CAD功能开发中"}

