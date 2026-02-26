from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import User, Inspiration
from auth import get_current_user
from config import settings
import os
import shutil
import uuid

router = APIRouter(prefix="/api/inspirations", tags=["灵感自动导入"])

@router.post("/import-from-folder")
async def import_inspirations_from_folder(
    folder_path: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    从指定文件夹自动导入灵感
    文件夹结构：
    - image1.jpg
    - image1.txt (包含标题、描述、分类、风格等信息)
    - image2.png
    - image2.txt
    """
    if not os.path.exists(folder_path):
        raise HTTPException(status_code=400, detail="文件夹不存在")
    
    imported_count = 0
    errors = []
    
    # 获取所有图片文件
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
    files = os.listdir(folder_path)
    
    for filename in files:
        # 只处理图片文件
        file_ext = os.path.splitext(filename)[1].lower()
        if file_ext not in image_extensions:
            continue
        
        image_path = os.path.join(folder_path, filename)
        base_name = os.path.splitext(filename)[0]
        txt_path = os.path.join(folder_path, f"{base_name}.txt")
        
        try:
            # 读取配置文件
            info = {
                'title': base_name,
                'description': '',
                'category': '其他',
                'style': '',
                'tags': ''
            }
            
            if os.path.exists(txt_path):
                with open(txt_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    for line in lines:
                        line = line.strip()
                        if ':' in line or '：' in line:
                            key, value = line.replace('：', ':').split(':', 1)
                            key = key.strip().lower()
                            value = value.strip()
                            
                            if key in ['title', '标题']:
                                info['title'] = value
                            elif key in ['description', '描述']:
                                info['description'] = value
                            elif key in ['category', '分类']:
                                info['category'] = value
                            elif key in ['style', '风格']:
                                info['style'] = value
                            elif key in ['tags', '标签']:
                                info['tags'] = value
            
            # 复制图片到上传目录
            new_filename = f"{uuid.uuid4()}{file_ext}"
            dest_path = os.path.join(settings.UPLOAD_DIR, "images", new_filename)
            shutil.copy2(image_path, dest_path)
            
            # 创建灵感记录
            inspiration = Inspiration(
                user_id=current_user.id,
                title=info['title'],
                description=info['description'],
                category=info['category'],
                style=info['style'],
                tags=info['tags'],
                image_url=f"/uploads/images/{new_filename}"
            )
            
            db.add(inspiration)
            imported_count += 1
            
        except Exception as e:
            errors.append(f"{filename}: {str(e)}")
    
    db.commit()
    
    return {
        "message": f"成功导入 {imported_count} 个灵感",
        "imported_count": imported_count,
        "errors": errors
    }

@router.get("/auto-import-config")
def get_auto_import_config(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取自动导入配置"""
    # 这里可以从数据库读取配置，暂时返回默认值
    return {
        "enabled": True,
        "folder_path": "F:/architecture/inspirations_import",
        "auto_scan_interval": 3600  # 秒
    }

@router.post("/set-auto-import-config")
def set_auto_import_config(
    folder_path: str,
    enabled: bool = True,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """设置自动导入配置"""
    if not current_user.is_root:
        raise HTTPException(status_code=403, detail="权限不足")
    
    # 这里可以保存到数据库
    return {
        "message": "配置已保存",
        "folder_path": folder_path,
        "enabled": enabled
    }

