from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from database import get_db
from models import User, Project
from auth import get_current_user
import os
import uuid

router = APIRouter(prefix="/api/projects", tags=["项目批量导入"])

@router.post("/import-from-file")
async def import_projects_from_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    从txt或md文件批量导入项目
    文件格式：
    ---
    项目名称: XXX
    地址: XXX
    面积: 100
    预算: 1000000
    状态: 进行中
    描述: XXX
    ---
    项目名称: YYY
    ...
    """
    
    if not file.filename.endswith(('.txt', '.md')):
        raise HTTPException(status_code=400, detail="只支持txt或md文件")
    
    # 读取文件内容
    content = await file.read()
    text = content.decode('utf-8')
    
    # 解析项目
    projects_data = []
    current_project = {}
    
    for line in text.split('\n'):
        line = line.strip()
        
        if line == '---':
            if current_project:
                projects_data.append(current_project)
                current_project = {}
        elif ':' in line or '：' in line:
            key, value = line.replace('：', ':').split(':', 1)
            key = key.strip()
            value = value.strip()
            
            if key in ['项目名称', 'name', '名称']:
                current_project['name'] = value
            elif key in ['地址', 'address']:
                current_project['address'] = value
            elif key in ['面积', 'area']:
                try:
                    current_project['area'] = float(value)
                except:
                    current_project['area'] = None
            elif key in ['预算', 'budget']:
                try:
                    current_project['budget'] = float(value)
                except:
                    current_project['budget'] = None
            elif key in ['状态', 'status']:
                current_project['status'] = value
            elif key in ['描述', 'description']:
                current_project['description'] = value
    
    # 添加最后一个项目
    if current_project:
        projects_data.append(current_project)
    
    # 创建项目
    imported_count = 0
    errors = []
    
    for project_data in projects_data:
        try:
            if not project_data.get('name'):
                errors.append(f"项目缺少名称: {project_data}")
                continue
            
            project = Project(
                user_id=current_user.id,
                name=project_data.get('name'),
                address=project_data.get('address', ''),
                area=project_data.get('area'),
                budget=project_data.get('budget'),
                status=project_data.get('status', '进行中'),
                description=project_data.get('description', '')
            )
            
            db.add(project)
            imported_count += 1
            
        except Exception as e:
            errors.append(f"{project_data.get('name', 'Unknown')}: {str(e)}")
    
    db.commit()
    
    return {
        "message": f"成功导入 {imported_count} 个项目",
        "imported_count": imported_count,
        "errors": errors
    }

@router.get("/export-template")
def export_project_template():
    """导出项目导入模板"""
    template = """---
项目名称: 示例项目1
地址: 北京市朝阳区
面积: 1000
预算: 5000000
状态: 进行中
描述: 这是一个示例项目
---
项目名称: 示例项目2
地址: 上海市浦东新区
面积: 2000
预算: 10000000
状态: 进行中
描述: 这是另一个示例项目
---
"""
    
    return {
        "template": template,
        "instructions": "复制此模板，修改项目信息后保存为txt或md文件，然后上传导入"
    }

