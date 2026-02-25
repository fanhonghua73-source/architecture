# 建筑师助手应用 - 完整项目

一个面向建筑师的移动端辅助工具，帮助建筑师进行项目管理、设计灵感收集、材料管理和团队协作。

## 项目结构

```
lian/
├── backend/                # 后端 FastAPI
│   ├── routers/           # 路由模块
│   ├── main.py            # 主应用
│   ├── models.py          # 数据模型
│   ├── schemas.py         # Pydantic模型
│   ├── database.py        # 数据库配置
│   ├── auth.py            # 认证模块
│   ├── utils.py           # 工具函数
│   ├── config.py          # 配置文件
│   ├── requirements.txt   # Python依赖
│   └── README.md
│
├── frontend/              # 前端 UniApp
│   ├── pages/            # 页面
│   ├── api/              # API接口
│   ├── utils/            # 工具函数
│   ├── static/           # 静态资源
│   ├── config.js         # 配置文件
│   ├── pages.json        # 页面配置
│   ├── manifest.json     # 应用配置
│   ├── App.vue           # 应用入口
│   ├── main.js           # 主入口
│   ├── package.json      # 依赖配置
│   └── README.md
│
└── 项目需求文档.md        # 详细需求文档
```

## 技术栈

### 后端
- **框架**: FastAPI
- **数据库**: SQLite (可切换到PostgreSQL)
- **ORM**: SQLAlchemy
- **认证**: JWT Token
- **数据验证**: Pydantic

### 前端
- **框架**: UniApp (Vue 3)
- **状态管理**: Pinia
- **UI组件**: uni-ui
- **支持平台**: 微信小程序、H5、iOS、Android

## 快速开始

### 1. 后端启动

```bash
# 进入后端目录
cd backend

# 安装依赖
pip install -r requirements.txt

# 启动服务
python main.py
```

后端服务将在 http://localhost:8000 启动

API文档访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 2. 前端启动

#### 使用 HBuilderX（推荐）

1. 使用 HBuilderX 打开 `frontend` 目录
2. 修改 `config.js` 中的 `baseURL` 为后端地址
3. 运行到微信开发者工具或浏览器

#### 命令行方式

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 运行到微信小程序
npm run dev:mp-weixin

# 运行到H5
npm run dev:h5
```

## 核心功能

### 1. 用户管理
- ✅ 用户注册
- ✅ 用户登录
- ✅ JWT认证
- ✅ 个人信息管理

### 2. 项目管理
- ✅ 创建项目
- ✅ 项目列表（支持状态筛选）
- ✅ 项目详情
- ✅ 项目编辑
- ✅ 项目删除
- ✅ 项目图片上传

### 3. 设计灵感库
- ✅ 添加灵感（图片上传）
- ✅ 灵感列表（瀑布流展示）
- ✅ 分类筛选（外观、室内、景观、细节）
- ✅ 风格标签
- ✅ 灵感详情
- ✅ 灵感删除

### 4. 材料管理
- ✅ 材料列表
- ✅ 材料搜索
- ✅ 材料详情
- ✅ 供应商管理

### 5. 任务管理
- ✅ 任务创建
- ✅ 任务列表
- ✅ 任务状态更新
- ✅ 任务删除

## API接口

### 认证相关
```
POST   /api/auth/register       # 用户注册
POST   /api/auth/login          # 用户登录
GET    /api/auth/profile        # 获取用户信息
PUT    /api/auth/profile        # 更新用户信息
```

### 项目管理
```
GET    /api/projects            # 获取项目列表
POST   /api/projects            # 创建项目
GET    /api/projects/{id}       # 获取项目详情
PUT    /api/projects/{id}       # 更新项目
DELETE /api/projects/{id}       # 删除项目
POST   /api/projects/{id}/images # 上传项目图片
```

### 灵感库
```
GET    /api/inspirations        # 获取灵感列表
POST   /api/inspirations        # 添加灵感
GET    /api/inspirations/{id}   # 获取灵感详情
PUT    /api/inspirations/{id}   # 更新灵感
DELETE /api/inspirations/{id}   # 删除灵感
GET    /api/inspirations/tags/list # 获取标签列表
```

### 材料管理
```
GET    /api/materials           # 获取材料列表
POST   /api/materials           # 添加材料
GET    /api/materials/{id}      # 获取材料详情
PUT    /api/materials/{id}      # 更新材料
DELETE /api/materials/{id}      # 删除材料
GET    /api/suppliers           # 获取供应商列表
POST   /api/suppliers           # 添加供应商
```

### 任务管理
```
GET    /api/tasks               # 获取任务列表
POST   /api/tasks               # 创建任务
PUT    /api/tasks/{id}          # 更新任务
DELETE /api/tasks/{id}          # 删除任务
```

## 数据库设计

主要数据表：
- `users` - 用户表
- `projects` - 项目表
- `project_images` - 项目图片表
- `inspirations` - 灵感表
- `materials` - 材料表
- `suppliers` - 供应商表
- `teams` - 团队表
- `team_members` - 团队成员表
- `tasks` - 任务表

## 配置说明

### 后端配置 (backend/.env)

```env
DATABASE_URL=sqlite:///./architect_assistant.db
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
UPLOAD_DIR=./uploads
```

### 前端配置 (frontend/config.js)

```javascript
export default {
	baseURL: 'http://localhost:8000',  // 后端API地址
	timeout: 10000
}
```

## 开发说明

### 后端开发

1. 所有接口都需要JWT认证（除了注册和登录）
2. 文件上传限制为10MB
3. 支持的图片格式：jpg, jpeg, png, gif, webp
4. 数据库使用SQLite，生产环境建议使用PostgreSQL

### 前端开发

1. 使用 Vue 3 Composition API
2. 遵循 UniApp 开发规范
3. 注意不同平台的兼容性
4. 图片上传使用 uni.chooseImage 和 uni.uploadFile

## 部署建议

### 后端部署

1. 使用 Docker 容器化部署
2. 配置 Nginx 反向代理
3. 使用 PostgreSQL 替代 SQLite
4. 配置 HTTPS
5. 设置文件上传目录权限

### 前端部署

#### 微信小程序
1. 在微信公众平台注册小程序
2. 配置服务器域名（必须是HTTPS）
3. 使用 HBuilderX 打包上传
4. 提交审核

#### H5
1. 打包生成静态文件
2. 部署到Web服务器
3. 配置域名和HTTPS

#### App
1. 使用 HBuilderX 云打包
2. 生成 APK/IPA 文件
3. 发布到应用商店

## 测试账号

首次使用需要注册账号，或使用以下测试数据：

```
用户名: test_user
密码: test123456
邮箱: test@example.com
```

## 注意事项

1. 首次运行后端会自动创建数据库表
2. 上传目录会自动创建
3. Token有效期为24小时
4. 微信小程序需要配置合法域名
5. 开发时可以关闭域名校验

## 后续扩展功能

- [ ] AI设计建议
- [ ] 3D模型查看
- [ ] AR实景预览
- [ ] 项目成本计算器
- [ ] 施工进度管理
- [ ] 客户管理系统
- [ ] 团队协作功能完善
- [ ] 消息推送
- [ ] 数据统计分析

## 常见问题

### 1. 后端启动失败
- 检查Python版本（需要3.8+）
- 检查依赖是否安装完整
- 检查端口8000是否被占用

### 2. 前端无法连接后端
- 检查后端是否启动
- 检查 config.js 中的 baseURL
- 检查网络连接

### 3. 图片上传失败
- 检查图片大小（不超过10MB）
- 检查图片格式
- 检查后端上传目录权限

### 4. Token过期
- 重新登录即可
- 可以在后端配置中调整过期时间

## 技术支持

如有问题，请查看：
- 后端文档: `backend/README.md`
- 前端文档: `frontend/README.md`
- 需求文档: `项目需求文档.md`

## 开源协议

MIT License

---

**祝您使用愉快！** 🎉

