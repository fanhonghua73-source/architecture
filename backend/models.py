from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
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
    created_at = Column(DateTime, default=datetime.utcnow)
    
    projects = relationship("Project", back_populates="owner")
    inspirations = relationship("Inspiration", back_populates="owner")

class Project(Base):
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String, index=True)
    address = Column(String)
    area = Column(Float)
    budget = Column(Float)
    status = Column(String, default="进行中")  # 进行中、已完成、暂停
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    owner = relationship("User", back_populates="projects")
    images = relationship("ProjectImage", back_populates="project", cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="project", cascade="all, delete-orphan")

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

