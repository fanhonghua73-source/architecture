import os
import shutil
from datetime import datetime
from typing import Optional
from fastapi import UploadFile, HTTPException
from config import settings

# 确保上传目录存在
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(f"{settings.UPLOAD_DIR}/images", exist_ok=True)
os.makedirs(f"{settings.UPLOAD_DIR}/documents", exist_ok=True)

ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
ALLOWED_DOCUMENT_EXTENSIONS = {".pdf", ".doc", ".docx", ".dwg", ".dxf"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

def get_file_extension(filename: str) -> str:
    return os.path.splitext(filename)[1].lower()

def generate_unique_filename(original_filename: str) -> str:
    ext = get_file_extension(original_filename)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    return f"{timestamp}{ext}"

async def save_upload_file(file: UploadFile, file_type: str = "image") -> str:
    """
    保存上传的文件
    file_type: "image" 或 "document"
    返回文件的相对路径
    """
    # 验证文件扩展名
    ext = get_file_extension(file.filename)
    if file_type == "image" and ext not in ALLOWED_IMAGE_EXTENSIONS:
        raise HTTPException(status_code=400, detail="不支持的图片格式")
    elif file_type == "document" and ext not in ALLOWED_DOCUMENT_EXTENSIONS:
        raise HTTPException(status_code=400, detail="不支持的文档格式")
    
    # 生成唯一文件名
    unique_filename = generate_unique_filename(file.filename)
    file_path = f"{settings.UPLOAD_DIR}/{file_type}s/{unique_filename}"
    
    # 保存文件
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件保存失败: {str(e)}")
    
    # 返回相对路径（包含 /uploads 前缀）
    return f"/uploads/{file_type}s/{unique_filename}"

def delete_file(file_path: str):
    """删除文件"""
    full_path = f"{settings.UPLOAD_DIR}{file_path}"
    if os.path.exists(full_path):
        os.remove(full_path)

