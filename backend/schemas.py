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

class UserSimple(BaseModel):
    id: int
    username: str
    avatar: Optional[str] = None
    
    class Config:
        from_attributes = True

class UserResponse(UserBase):
    id: int
    avatar: Optional[str] = None
    is_root: Optional[bool] = False
    is_approved: Optional[bool] = False
    created_at: datetime
    
    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    position: Optional[str] = None

class PasswordChange(BaseModel):
    old_password: str
    new_password: str

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
    
    # 稳定数据（规划条件核心指标）
    land_area: Optional[float] = None
    floor_area_ratio: Optional[float] = None
    green_ratio: Optional[float] = None
    density: Optional[float] = None
    height: Optional[float] = None
    
    # 其他报价数据
    total_building_area: Optional[float] = None
    above_ground_area: Optional[float] = None
    underground_area: Optional[float] = None
    residential_units: Optional[int] = None
    commercial_units: Optional[int] = None
    supporting_area: Optional[float] = None
    basement_estimated_area: Optional[float] = None
    parking_area: Optional[float] = None

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
    approval_status: str
    created_at: datetime
    updated_at: datetime
    images: List[ProjectImageResponse] = []
    owner: Optional[UserSimple] = None  # 项目创建者信息
    
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

# 合同相关
class ContractBase(BaseModel):
    project_id: int
    template: str
    area: float
    location: str
    ai_provider: str

class ContractCreate(ContractBase):
    pass

class ContractResponse(ContractBase):
    id: int
    content: str
    created_by: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# AI配置相关
class AIConfigBase(BaseModel):
    provider: str
    config_type: str = "llm"  # llm, image
    api_key: str
    api_url: Optional[str] = None

class AIConfigCreate(AIConfigBase):
    pass

class AIConfigResponse(AIConfigBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# AI生图相关
class AIImageGenerationCreate(BaseModel):
    base_image: str  # base64 or url
    reference_images: Optional[List[str]] = []
    prompt: str
    provider: str = "banana"

class AIImageGenerationResponse(BaseModel):
    id: int
    base_image_url: str
    reference_images: str
    prompt: str
    result_image_url: str
    provider: str
    created_at: datetime
    
    class Config:
        from_attributes = True

# 项目权限相关
class ProjectPermissionBase(BaseModel):
    project_id: int
    user_id: int
    can_edit: bool = False

class ProjectPermissionCreate(ProjectPermissionBase):
    pass

class ProjectPermissionResponse(ProjectPermissionBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

