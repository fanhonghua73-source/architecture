from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import User, Inspiration
from schemas import InspirationCreate, InspirationResponse
from auth import get_current_user
from utils import save_upload_file

router = APIRouter(prefix="/api/inspirations", tags=["灵感库"])

@router.get("", response_model=List[InspirationResponse])
def get_inspirations(
    skip: int = 0,
    limit: int = 100,
    category: str = None,
    style: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Inspiration).filter(Inspiration.user_id == current_user.id)
    if category:
        query = query.filter(Inspiration.category == category)
    if style:
        query = query.filter(Inspiration.style == style)
    inspirations = query.offset(skip).limit(limit).all()
    return inspirations

@router.post("", response_model=InspirationResponse)
async def create_inspiration(
    title: str,
    file: UploadFile = File(...),
    description: str = None,
    tags: str = None,
    category: str = None,
    style: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # 保存图片
    image_url = await save_upload_file(file, "image")
    
    # 创建灵感记录
    db_inspiration = Inspiration(
        user_id=current_user.id,
        title=title,
        image_url=image_url,
        description=description,
        tags=tags,
        category=category,
        style=style
    )
    db.add(db_inspiration)
    db.commit()
    db.refresh(db_inspiration)
    return db_inspiration

@router.get("/{inspiration_id}", response_model=InspirationResponse)
def get_inspiration(
    inspiration_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    inspiration = db.query(Inspiration).filter(
        Inspiration.id == inspiration_id,
        Inspiration.user_id == current_user.id
    ).first()
    if not inspiration:
        raise HTTPException(status_code=404, detail="灵感不存在")
    return inspiration

@router.put("/{inspiration_id}", response_model=InspirationResponse)
def update_inspiration(
    inspiration_id: int,
    inspiration_update: InspirationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    inspiration = db.query(Inspiration).filter(
        Inspiration.id == inspiration_id,
        Inspiration.user_id == current_user.id
    ).first()
    if not inspiration:
        raise HTTPException(status_code=404, detail="灵感不存在")
    
    for key, value in inspiration_update.dict(exclude_unset=True).items():
        setattr(inspiration, key, value)
    
    db.commit()
    db.refresh(inspiration)
    return inspiration

@router.delete("/{inspiration_id}")
def delete_inspiration(
    inspiration_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    inspiration = db.query(Inspiration).filter(
        Inspiration.id == inspiration_id,
        Inspiration.user_id == current_user.id
    ).first()
    if not inspiration:
        raise HTTPException(status_code=404, detail="灵感不存在")
    
    db.delete(inspiration)
    db.commit()
    return {"message": "灵感已删除"}

@router.get("/tags/list")
def get_tags(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    inspirations = db.query(Inspiration).filter(
        Inspiration.user_id == current_user.id
    ).all()
    
    # 收集所有标签
    all_tags = set()
    for inspiration in inspirations:
        if inspiration.tags:
            tags = inspiration.tags.split(",")
            all_tags.update([tag.strip() for tag in tags])
    
    return {"tags": list(all_tags)}

