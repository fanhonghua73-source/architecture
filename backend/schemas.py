from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

# 用户相关
class UserBase(BaseModel):
    username: str
    email: EmailStr
    phone: Optional[str] = None
    company: Optional[str] = None
    position: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(UserBase):
    id: int
    avatar: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

# 项目相关
class ProjectBase(BaseModel):
    name: str
    address: Optional[str] = None
    area: Optional[float] = None
    budget: Optional[float] = None
    status: Optional[str] = "进行中"
    description: Optional[str] = None

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(ProjectBase):
    pass

class ProjectImageResponse(BaseModel):
    id: int
    image_url: str
    description: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class ProjectResponse(ProjectBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    images: List[ProjectImageResponse] = []
    
    class Config:
        from_attributes = True

# 灵感相关
class InspirationBase(BaseModel):
    title: str
    description: Optional[str] = None
    tags: Optional[str] = None
    category: Optional[str] = None
    style: Optional[str] = None

class InspirationCreate(InspirationBase):
    pass

class InspirationResponse(InspirationBase):
    id: int
    user_id: int
    image_url: str
    created_at: datetime
    
    class Config:
        from_attributes = True

# 材料相关
class MaterialBase(BaseModel):
    name: str
    category: Optional[str] = None
    specification: Optional[str] = None
    price: Optional[float] = None
    unit: Optional[str] = None
    supplier_id: Optional[int] = None
    description: Optional[str] = None

class MaterialCreate(MaterialBase):
    pass

class MaterialResponse(MaterialBase):
    id: int
    image_url: Optional[str] = None
    
    class Config:
        from_attributes = True

# 供应商相关
class SupplierBase(BaseModel):
    name: str
    contact: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    address: Optional[str] = None
    description: Optional[str] = None

class SupplierCreate(SupplierBase):
    pass

class SupplierResponse(SupplierBase):
    id: int
    
    class Config:
        from_attributes = True

# 任务相关
class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    assignee_id: Optional[int] = None
    status: Optional[str] = "待处理"
    due_date: Optional[datetime] = None

class TaskCreate(TaskBase):
    project_id: int

class TaskResponse(TaskBase):
    id: int
    project_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

