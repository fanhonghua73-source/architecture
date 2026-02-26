# 项目资料管理和Banana配置修复说明

## 修复内容

### 1. 项目资料管理页面
**问题**: uni-popup组件导入失败
**解决方案**: 
- 安装了 `@dcloudio/uni-ui` 组件库
- 将uni-popup改为自定义模态框实现，不依赖外部组件

**修改文件**:
- `frontend/pages/projects/documents.vue` - 使用自定义modal-mask实现弹窗

### 2. Banana生图API配置
**问题**: AI配置页面没有Banana选项，且config_type字段未正确保存
**解决方案**:
- 在AI配置页面添加Banana生图选项
- 修复后端保存config_type字段的逻辑
- 区分LLM配置和图像生成配置

**修改文件**:
- `frontend/pages/admin/ai-config.vue` - 添加Banana选项和config_type字段
- `backend/routers/contracts.py` - 修复AI配置创建逻辑，正确保存config_type

## 使用说明

### 启动服务

#### 后端
```bash
cd f:\architecture\backend
python main.py
```

#### 前端
```bash
cd f:\architecture\frontend
npm run dev:h5
```

### 配置Banana生图API

1. 登录系统（root/root123456）
2. 进入"我的" -> "AI配置"
3. 点击"添加配置"
4. 选择"Banana生图"
5. 输入API Key和API URL（可选）
6. 点击确定保存

### 使用项目资料管理

1. 进入任意项目详情页
2. 点击"项目资料"或"报价数据"按钮
3. 进入项目资料管理页面

#### 编辑报价数据
- 点击"编辑"按钮
- 填写以下信息：
  - 总建筑面积（㎡）
  - 地上面积（㎡）
  - 地下面积（㎡）
  - 住宅户数
  - 商业户数
  - 配套面积（㎡）
  - 地下室预估面积（㎡）
  - 地下车库面积（㎡）
- 点击"保存"

#### 上传项目文档
支持以下文档类型：
- **用地红线**: PDF格式，可转换为CAD
- **规划条件**: PDF/Word格式
- **甲方确认函**: PDF/Word/图片格式
- **特殊规范**: PDF/Word格式

操作步骤：
1. 点击对应文档的"上传"按钮
2. 选择文件
3. 等待上传完成
4. 可以查看、下载已上传的文档

#### PDF转CAD功能
1. 先上传用地红线PDF
2. 点击"转CAD"按钮
3. 系统自动识别红线轮廓
4. 生成DXF格式CAD文件
5. 自动下载CAD文件

#### 设置项目位置
1. 点击"设置位置"按钮
2. 输入项目地址
3. 输入经纬度（或使用地址解析）
4. 点击"保存"
5. 可以点击"查看地图"在地图上查看位置

### 使用AI生图功能

1. 确保已配置Banana生图API
2. 进入"AI生图"页面
3. 上传基础图片（必需）
4. 可选上传1-3张参考图片
5. 输入提示词（可选，系统会自动生成）
6. 点击"生成"
7. 等待AI生成结果
8. 可以进行二次对话生成

## 测试脚本

运行测试脚本验证配置：
```bash
cd f:\architecture\backend
python test_banana_config.py
```

测试内容：
- ✅ 登录系统
- ✅ 添加Banana配置
- ✅ 获取所有AI配置
- ✅ 验证Banana配置正确保存

## 技术细节

### AI配置类型
- `llm`: 大语言模型（MiniMax, Gemini, ChatGPT）
- `image`: 图像生成（Banana）

### 数据库字段

#### AIConfig表
```sql
- provider: 提供商名称（minimax, gemini, banana等）
- config_type: 配置类型（llm, image）
- api_key: API密钥
- api_url: API地址（可选）
- is_active: 是否启用
```

#### Project表（新增字段）
```sql
- total_building_area: 总建筑面积
- above_ground_area: 地上面积
- underground_area: 地下面积
- residential_units: 住宅户数
- commercial_units: 商业户数
- supporting_area: 配套面积
- basement_estimated_area: 地下室预估面积
- parking_area: 地下车库面积
- land_boundary_pdf: 用地红线PDF路径
- land_boundary_cad: 生成的CAD文件路径
- planning_conditions_pdf: 规划条件路径
- client_confirmation_pdf: 甲方确认函路径
- special_regulations_pdf: 特殊规范路径
- baidu_location: 百度地图位置（JSON）
```

#### ProjectDocument表
```sql
- project_id: 项目ID
- doc_type: 文档类型
- file_path: 文件路径
- file_name: 文件名
- file_size: 文件大小
- uploaded_at: 上传时间
- uploaded_by: 上传人ID
```

### PDF转CAD算法
1. 使用PyMuPDF将PDF转为高清图片
2. 使用OpenCV进行图像预处理（灰度化、高斯模糊）
3. 使用Canny算法进行边缘检测
4. 查找最大轮廓（假设为红线）
5. 使用Douglas-Peucker算法简化轮廓
6. 使用ezdxf生成DXF格式CAD文件

### API端点

#### 项目资料管理
```
POST   /api/projects/{id}/documents/upload        # 上传文档
GET    /api/projects/{id}/documents               # 获取文档列表
POST   /api/projects/{id}/land-boundary/to-cad    # PDF转CAD
POST   /api/projects/{id}/location                # 设置位置
PUT    /api/projects/{id}/quotation               # 更新报价数据
```

#### AI配置
```
POST   /api/contracts/ai-config                   # 添加AI配置
GET    /api/contracts/ai-config                   # 获取AI配置列表
```

#### AI生图
```
POST   /api/ai-image/generate                     # 生成图片
POST   /api/ai-image/regenerate/{id}              # 二次生成
GET    /api/ai-image/history                      # 生成历史
```

## 注意事项

1. **文件大小**: PDF文件建议不超过50MB
2. **CAD精度**: 转换精度取决于PDF图片质量
3. **API Key**: 需要有效的Banana API Key才能使用生图功能
4. **权限**: 只有项目创建者和root用户可以管理项目资料
5. **浏览器兼容**: 建议使用Chrome或Edge浏览器

## 已知问题

1. 百度地图地址解析功能需要申请API Key
2. PDF转CAD对复杂图形的识别精度有限
3. Banana API的实际调用格式需要根据官方文档调整

## 下一步优化

1. 集成百度地图API实现自动地址解析
2. 优化PDF转CAD算法，提高识别精度
3. 添加文档版本管理功能
4. 实现报价单导出（PDF/Excel）
5. 添加在线PDF预览功能
6. 支持更多图像生成API（Stable Diffusion, DALL-E等）

---

**修复日期**: 2026-02-26  
**版本**: v3.3  
**状态**: 已修复，可测试

