from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from database import get_db
from models import User, Project, ProjectDocument
from auth import get_current_user
from config import settings
import os
import uuid
import fitz  # PyMuPDF
import cv2
import numpy as np
import ezdxf
from PIL import Image

router = APIRouter(prefix="/api/projects", tags=["项目资料管理"])

@router.post("/{project_id}/documents/upload")
async def upload_project_document(
    project_id: int,
    doc_type: str,  # land_boundary, planning, confirmation, regulation
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    上传项目文档
    doc_type: land_boundary(用地红线), planning(规划条件), 
              confirmation(甲方确认函), regulation(特殊规范)
    
    权限：只有项目创建者和root用户可以上传
    """
    # 检查项目是否存在
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    
    # 权限检查：只有创建者和root可以上传
    if not (project.user_id == current_user.id or current_user.is_root):
        raise HTTPException(status_code=403, detail="权限不足，只有项目创建者和管理员可以上传文档")
    
    # 验证文件类型
    allowed_types = ["application/pdf", "application/msword", 
                     "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                     "image/jpeg", "image/png"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="不支持的文件类型")
    
    # 保存文件
    file_ext = os.path.splitext(file.filename)[1]
    filename = f"{uuid.uuid4()}{file_ext}"
    file_path = os.path.join(settings.UPLOAD_DIR, "documents", filename)
    
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)
    
    # 保存文档记录
    document = ProjectDocument(
        project_id=project_id,
        doc_type=doc_type,
        file_path=f"/uploads/documents/{filename}",
        file_name=file.filename,
        file_size=len(content),
        uploaded_by=current_user.id
    )
    db.add(document)
    
    # 更新项目对应字段
    if doc_type == "land_boundary":
        project.land_boundary_pdf = f"/uploads/documents/{filename}"
    elif doc_type == "planning":
        project.planning_conditions_pdf = f"/uploads/documents/{filename}"
    elif doc_type == "confirmation":
        project.client_confirmation_pdf = f"/uploads/documents/{filename}"
    elif doc_type == "regulation":
        project.special_regulations_pdf = f"/uploads/documents/{filename}"
    
    db.commit()
    db.refresh(document)
    
    return {
        "message": "上传成功",
        "document_id": document.id,
        "file_path": document.file_path
    }

@router.post("/{project_id}/land-boundary/to-cad")
async def convert_pdf_to_cad(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """将用地红线PDF转换为CAD文件"""
    
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    
    if not project.land_boundary_pdf:
        raise HTTPException(status_code=400, detail="请先上传用地红线PDF")
    
    # PDF文件路径
    pdf_path = os.path.join(settings.UPLOAD_DIR.replace("/uploads", ""), 
                           project.land_boundary_pdf.replace("/uploads/", ""))
    
    if not os.path.exists(pdf_path):
        raise HTTPException(status_code=404, detail="PDF文件不存在")
    
    try:
        # 转换PDF到CAD
        cad_filename = f"{uuid.uuid4()}.dxf"
        cad_path = os.path.join(settings.UPLOAD_DIR, "documents", cad_filename)
        
        # 执行转换
        convert_pdf_boundary_to_cad(pdf_path, cad_path)
        
        # 更新项目记录
        project.land_boundary_cad = f"/uploads/documents/{cad_filename}"
        db.commit()
        
        return {
            "message": "转换成功",
            "cad_path": project.land_boundary_cad
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"转换失败: {str(e)}")

@router.get("/{project_id}/documents")
def get_project_documents(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取项目文档列表"""
    
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    
    documents = db.query(ProjectDocument).filter(
        ProjectDocument.project_id == project_id
    ).all()
    
    return documents

@router.post("/{project_id}/location")
def set_project_location(
    project_id: int,
    longitude: float,
    latitude: float,
    address: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    设置项目百度地图位置
    权限：只有项目创建者和root用户可以设置
    """
    
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    
    # 权限检查：只有创建者和root可以设置
    if not (project.user_id == current_user.id or current_user.is_root):
        raise HTTPException(status_code=403, detail="权限不足，只有项目创建者和管理员可以设置位置")
    
    import json
    location_data = {
        "longitude": longitude,
        "latitude": latitude,
        "address": address
    }
    
    project.baidu_location = json.dumps(location_data, ensure_ascii=False)
    db.commit()
    
    return {"message": "位置已保存", "location": location_data}

@router.put("/{project_id}/quotation")
def update_project_quotation(
    project_id: int,
    total_building_area: float = None,
    above_ground_area: float = None,
    underground_area: float = None,
    residential_units: int = None,
    commercial_units: int = None,
    supporting_area: float = None,
    basement_estimated_area: float = None,
    parking_area: float = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    更新项目报价数据
    权限：只有项目创建者和root用户可以更新
    """
    
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    
    # 权限检查：只有创建者和root可以更新
    if not (project.user_id == current_user.id or current_user.is_root):
        raise HTTPException(status_code=403, detail="权限不足，只有项目创建者和管理员可以更新报价数据")
    
    if total_building_area is not None:
        project.total_building_area = total_building_area
    if above_ground_area is not None:
        project.above_ground_area = above_ground_area
    if underground_area is not None:
        project.underground_area = underground_area
    if residential_units is not None:
        project.residential_units = residential_units
    if commercial_units is not None:
        project.commercial_units = commercial_units
    if supporting_area is not None:
        project.supporting_area = supporting_area
    if basement_estimated_area is not None:
        project.basement_estimated_area = basement_estimated_area
    if parking_area is not None:
        project.parking_area = parking_area
    
    db.commit()
    db.refresh(project)
    
    return {"message": "报价数据已更新", "project": project}

def convert_pdf_boundary_to_cad(pdf_path: str, cad_path: str):
    """
    将PDF红线图转换为CAD文件
    使用图像处理技术提取红线轮廓
    """
    # 打开PDF
    doc = fitz.open(pdf_path)
    page = doc[0]  # 取第一页
    
    # 转换为图片
    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2倍缩放提高精度
    img_data = pix.tobytes("png")
    
    # 转换为numpy数组
    nparr = np.frombuffer(img_data, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    # 图像预处理
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, 50, 150)
    
    # 查找轮廓
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # 找到最大轮廓（假设是红线）
    if not contours:
        raise ValueError("未找到红线轮廓")
    
    largest_contour = max(contours, key=cv2.contourArea)
    
    # 创建DXF文档
    dwg = ezdxf.new('R2010')
    msp = dwg.modelspace()
    
    # 将轮廓点转换为CAD坐标
    # 简化轮廓以减少点数
    epsilon = 0.01 * cv2.arcLength(largest_contour, True)
    approx = cv2.approxPolyDP(largest_contour, epsilon, True)
    
    # 添加多段线
    points = [(float(pt[0][0]), float(pt[0][1])) for pt in approx]
    if len(points) > 2:
        msp.add_lwpolyline(points, close=True)
    
    # 保存DXF文件
    dwg.saveas(cad_path)
    doc.close()

