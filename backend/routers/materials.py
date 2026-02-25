from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import User, Material, Supplier
from schemas import MaterialCreate, MaterialResponse, SupplierCreate, SupplierResponse
from auth import get_current_user
from utils import save_upload_file

router = APIRouter(prefix="/api/materials", tags=["材料管理"])

# 材料相关接口
@router.get("", response_model=List[MaterialResponse])
def get_materials(
    skip: int = 0,
    limit: int = 100,
    category: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Material)
    if category:
        query = query.filter(Material.category == category)
    materials = query.offset(skip).limit(limit).all()
    return materials

@router.post("", response_model=MaterialResponse)
async def create_material(
    name: str,
    category: str = None,
    specification: str = None,
    price: float = None,
    unit: str = None,
    supplier_id: int = None,
    description: str = None,
    file: UploadFile = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    image_url = None
    if file:
        image_url = await save_upload_file(file, "image")
    
    db_material = Material(
        name=name,
        category=category,
        specification=specification,
        price=price,
        unit=unit,
        supplier_id=supplier_id,
        image_url=image_url,
        description=description
    )
    db.add(db_material)
    db.commit()
    db.refresh(db_material)
    return db_material

@router.get("/{material_id}", response_model=MaterialResponse)
def get_material(
    material_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    material = db.query(Material).filter(Material.id == material_id).first()
    if not material:
        raise HTTPException(status_code=404, detail="材料不存在")
    return material

@router.put("/{material_id}", response_model=MaterialResponse)
def update_material(
    material_id: int,
    material_update: MaterialCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    material = db.query(Material).filter(Material.id == material_id).first()
    if not material:
        raise HTTPException(status_code=404, detail="材料不存在")
    
    for key, value in material_update.dict(exclude_unset=True).items():
        setattr(material, key, value)
    
    db.commit()
    db.refresh(material)
    return material

@router.delete("/{material_id}")
def delete_material(
    material_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    material = db.query(Material).filter(Material.id == material_id).first()
    if not material:
        raise HTTPException(status_code=404, detail="材料不存在")
    
    db.delete(material)
    db.commit()
    return {"message": "材料已删除"}

# 供应商相关接口
supplier_router = APIRouter(prefix="/api/suppliers", tags=["供应商管理"])

@supplier_router.get("", response_model=List[SupplierResponse])
def get_suppliers(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    suppliers = db.query(Supplier).offset(skip).limit(limit).all()
    return suppliers

@supplier_router.post("", response_model=SupplierResponse)
def create_supplier(
    supplier: SupplierCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_supplier = Supplier(**supplier.dict())
    db.add(db_supplier)
    db.commit()
    db.refresh(db_supplier)
    return db_supplier

@supplier_router.get("/{supplier_id}", response_model=SupplierResponse)
def get_supplier(
    supplier_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if not supplier:
        raise HTTPException(status_code=404, detail="供应商不存在")
    return supplier

