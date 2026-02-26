from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    phone = Column(String)
    password_hash = Column(String)
    avatar = Column(String)
    company = Column(String)
    position = Column(String)
    is_root = Column(Boolean, default=False)
    is_approved = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    projects = relationship("Project", back_populates="owner")
    inspirations = relationship("Inspiration", back_populates="owner")
    project_permissions = relationship("ProjectPermission", back_populates="user")

class Project(Base):
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String, index=True)
    address = Column(String)
    area = Column(Float)
    budget = Column(Float)
    status = Column(String, default="进行中")  # 进行中、已完成、暂停
    approval_status = Column(String, default="pending")  # pending(待审批), approved(已批准), rejected(已拒绝)
    description = Column(Text)
    
    # 报价数据
    # 稳定数据（规划条件中的核心指标）
    land_area = Column(Float)  # 用地面积
    floor_area_ratio = Column(Float)  # 容积率
    green_ratio = Column(Float)  # 绿化率
    density = Column(Float)  # 密度
    height = Column(Float)  # 高度
    
    # 其他报价数据
    total_building_area = Column(Float)  # 总建筑面积
    above_ground_area = Column(Float)  # 地上面积
    underground_area = Column(Float)  # 地下面积
    residential_units = Column(Integer)  # 住宅户数
    commercial_units = Column(Integer)  # 商业户数
    supporting_area = Column(Float)  # 配套面积
    basement_estimated_area = Column(Float)  # 地下室预估面积
    parking_area = Column(Float)  # 地下车库面积
    
    # 项目资料
    land_boundary_pdf = Column(String)  # 用地红线PDF
    land_boundary_cad = Column(String)  # 生成的CAD文件
    planning_conditions_pdf = Column(String)  # 规划条件
    client_confirmation_pdf = Column(String)  # 甲方确认函
    special_regulations_pdf = Column(String)  # 特殊规范
    baidu_location = Column(Text)  # 百度地图位置（JSON）
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    owner = relationship("User", back_populates="projects")
    images = relationship("ProjectImage", back_populates="project", cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="project", cascade="all, delete-orphan")
    permissions = relationship("ProjectPermission", back_populates="project", cascade="all, delete-orphan")
    documents = relationship("ProjectDocument", back_populates="project", cascade="all, delete-orphan")

class ProjectImage(Base):
    __tablename__ = "project_images"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    image_url = Column(String)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    project = relationship("Project", back_populates="images")

class Inspiration(Base):
    __tablename__ = "inspirations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String)
    image_url = Column(String)
    description = Column(Text)
    tags = Column(String)  # 逗号分隔的标签
    category = Column(String)  # 外观、室内、景观、细节
    style = Column(String)  # 现代、古典、工业风
    created_at = Column(DateTime, default=datetime.utcnow)
    
    owner = relationship("User", back_populates="inspirations")

class Material(Base):
    __tablename__ = "materials"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    category = Column(String)
    specification = Column(String)
    price = Column(Float)
    unit = Column(String)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"))
    image_url = Column(String)
    description = Column(Text)
    
    supplier = relationship("Supplier", back_populates="materials")

class Supplier(Base):
    __tablename__ = "suppliers"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    contact = Column(String)
    phone = Column(String)
    email = Column(String)
    address = Column(String)
    description = Column(Text)
    
    materials = relationship("Material", back_populates="supplier")

class Team(Base):
    __tablename__ = "teams"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    creator_id = Column(Integer, ForeignKey("users.id"))
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    members = relationship("TeamMember", back_populates="team", cascade="all, delete-orphan")

class TeamMember(Base):
    __tablename__ = "team_members"
    
    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    role = Column(String)  # 管理员、成员
    joined_at = Column(DateTime, default=datetime.utcnow)
    
    team = relationship("Team", back_populates="members")

class Task(Base):
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    title = Column(String)
    description = Column(Text)
    assignee_id = Column(Integer, ForeignKey("users.id"))
    status = Column(String, default="待处理")  # 待处理、进行中、已完成
    due_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    project = relationship("Project", back_populates="tasks")

class ProjectPermission(Base):
    __tablename__ = "project_permissions"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    can_edit = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    project = relationship("Project", back_populates="permissions")
    user = relationship("User", back_populates="project_permissions")

class Contract(Base):
    __tablename__ = "contracts"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    template = Column(Text)  # 合同模板
    content = Column(Text)  # 生成的合同内容
    area = Column(Float)
    location = Column(String)
    ai_provider = Column(String)  # minimax, gemini
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

class AIConfig(Base):
    __tablename__ = "ai_configs"
    
    id = Column(Integer, primary_key=True, index=True)
    provider = Column(String)  # minimax, gemini, banana, chatgpt, coze
    config_type = Column(String, default="llm")  # llm, image
    auth_type = Column(String, default="api_key")  # api_key, oauth
    api_key = Column(String)  # API Key或OAuth Client ID
    api_url = Column(String)  # API URL或OAuth Client Secret
    access_token = Column(String)  # OAuth Access Token
    refresh_token = Column(String)  # OAuth Refresh Token
    token_expires_at = Column(DateTime)  # Token过期时间
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class AIImageGeneration(Base):
    __tablename__ = "ai_image_generations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    base_image_url = Column(String)
    reference_images = Column(Text)  # JSON array of image URLs
    prompt = Column(Text)
    result_image_url = Column(String)
    provider = Column(String)  # banana
    created_at = Column(DateTime, default=datetime.utcnow)

class ProjectDocument(Base):
    __tablename__ = "project_documents"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    doc_type = Column(String)  # 文档类型：
    # communication_catalog(通信目录), schedule(进度计划), phase_documents(阶段文件), 
    # project_log(项目日志), meeting_minutes(会议纪要), file_exchange(文件收发),
    # correspondence(往来函件), approval_review(批复审图), land_boundary(用地红线),
    # planning(规划条件), confirmation(甲方确认函), preliminary_design(扩初阶段),
    # construction_drawing(施工图阶段), construction_phase(施工阶段), work_files(工作文件)
    file_path = Column(String)
    file_name = Column(String)
    file_size = Column(Integer)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    uploaded_by = Column(Integer, ForeignKey("users.id"))
    
    project = relationship("Project", back_populates="documents")

class ProjectStatusChange(Base):
    __tablename__ = "project_status_changes"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    old_status = Column(String)  # 原状态
    new_status = Column(String)  # 新状态
    requested_by = Column(Integer, ForeignKey("users.id"))  # 申请人
    approval_status = Column(String, default="pending")  # pending, approved, rejected
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)  # 审批人
    reason = Column(Text, nullable=True)  # 变更原因
    created_at = Column(DateTime, default=datetime.utcnow)
    approved_at = Column(DateTime, nullable=True)

