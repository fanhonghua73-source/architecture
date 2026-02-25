# 建筑师助手 - 后端API

基于 FastAPI 构建的建筑师助手应用后端服务。

## 功能特性

- 用户认证（JWT Token）
- 项目管理
- 设计灵感库
- 材料管理
- 供应商管理
- 任务管理
- 文件上传

## 技术栈

- FastAPI
- SQLAlchemy
- SQLite
- JWT认证
- Pydantic数据验证

## 安装依赖

```bash
pip install -r requirements.txt
```

## 运行服务

```bash
# 开发模式
python main.py

# 或使用 uvicorn
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## API文档

启动服务后访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 主要接口

### 认证相关
- POST /api/auth/register - 用户注册
- POST /api/auth/login - 用户登录
- GET /api/auth/profile - 获取用户信息
- PUT /api/auth/profile - 更新用户信息

### 项目管理
- GET /api/projects - 获取项目列表
- POST /api/projects - 创建项目
- GET /api/projects/{id} - 获取项目详情
- PUT /api/projects/{id} - 更新项目
- DELETE /api/projects/{id} - 删除项目
- POST /api/projects/{id}/images - 上传项目图片

### 灵感库
- GET /api/inspirations - 获取灵感列表
- POST /api/inspirations - 添加灵感
- GET /api/inspirations/{id} - 获取灵感详情
- PUT /api/inspirations/{id} - 更新灵感
- DELETE /api/inspirations/{id} - 删除灵感

### 材料管理
- GET /api/materials - 获取材料列表
- POST /api/materials - 添加材料
- GET /api/materials/{id} - 获取材料详情
- PUT /api/materials/{id} - 更新材料
- DELETE /api/materials/{id} - 删除材料

### 供应商管理
- GET /api/suppliers - 获取供应商列表
- POST /api/suppliers - 添加供应商
- GET /api/suppliers/{id} - 获取供应商详情

### 任务管理
- GET /api/tasks - 获取任务列表
- POST /api/tasks - 创建任务
- PUT /api/tasks/{id} - 更新任务
- DELETE /api/tasks/{id} - 删除任务

## 环境变量

复制 `.env.example` 为 `.env` 并修改配置：

```
DATABASE_URL=sqlite:///./architect_assistant.db
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
UPLOAD_DIR=./uploads
```

## 项目结构

```
backend/
├── main.py              # 主应用入口
├── config.py            # 配置文件
├── database.py          # 数据库连接
├── models.py            # 数据模型
├── schemas.py           # Pydantic模型
├── auth.py              # 认证相关
├── utils.py             # 工具函数
├── routers/             # 路由模块
│   ├── auth.py
│   ├── projects.py
│   ├── inspirations.py
│   ├── materials.py
│   └── tasks.py
├── requirements.txt     # 依赖包
└── README.md
```

## 开发说明

1. 所有接口都需要JWT认证（除了注册和登录）
2. 文件上传限制为10MB
3. 支持的图片格式：jpg, jpeg, png, gif, webp
4. 数据库使用SQLite，生产环境建议使用PostgreSQL

## 测试

使用 Swagger UI 进行接口测试：http://localhost:8000/docs

