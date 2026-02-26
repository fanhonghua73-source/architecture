# AI厂商OAuth授权需求整理

## 需求说明

用户在配置AI接口时，不需要手动输入API Key，而是通过OAuth授权的方式，直接在AI厂商官网登录授权，系统自动获取API访问权限。

## 支持的AI厂商

### 1. MiniMax
- **官网**: https://api.minimax.chat
- **OAuth授权**: 支持
- **用途**: 文本生成、合同生成

### 2. ChatGPT (OpenAI)
- **官网**: https://platform.openai.com
- **OAuth授权**: 支持
- **用途**: 文本生成、对话

### 3. 小龙虾 (Coze)
- **官网**: https://www.coze.cn
- **OAuth授权**: 支持
- **用途**: 文本生成、智能对话

### 4. Gemini (Google)
- **官网**: https://ai.google.dev
- **OAuth授权**: 支持
- **用途**: 文本生成

### 5. Banana (生图)
- **官网**: https://banana.dev
- **OAuth授权**: 支持
- **用途**: AI图片生成

## 功能流程

### 配置流程

1. **Root用户进入AI配置页面**
   - 点击"添加AI配置"
   - 选择AI厂商（MiniMax/ChatGPT/小龙虾等）

2. **OAuth授权**
   - 点击"授权登录"按钮
   - 跳转到AI厂商官网
   - 使用厂商账号登录
   - 授权应用访问API

3. **自动配置**
   - 系统自动获取Access Token
   - 保存到数据库
   - 配置完成

4. **使用API**
   - 生成合同时自动使用已授权的API
   - AI生图时自动使用已授权的API
   - 无需手动输入API Key

### 使用流程

1. **合同生成**
   - 选择项目
   - 上传模板
   - 选择AI厂商（已OAuth授权的）
   - 生成合同

2. **AI生图**
   - 上传图片
   - 输入提示词
   - 自动使用已授权的Banana API
   - 生成设计图

## 技术实现

### OAuth授权流程

```
1. 用户点击"授权登录MiniMax"
   ↓
2. 跳转到 MiniMax OAuth授权页面
   ↓
3. 用户登录MiniMax账号并授权
   ↓
4. MiniMax回调我们的系统
   ↓
5. 系统获取Access Token
   ↓
6. 保存Token到数据库
   ↓
7. 配置完成
```

### 数据库设计

```sql
ai_configs:
  - provider: minimax/chatgpt/coze/gemini/banana
  - config_type: llm/image
  - auth_type: oauth/api_key  # 新增：授权类型
  - access_token: OAuth Token
  - refresh_token: 刷新Token
  - token_expires_at: Token过期时间
  - api_key: API Key（兼容手动配置）
  - api_url: API地址
```

### API接口

```
# AI厂商OAuth授权
GET  /api/ai-oauth/authorize/{provider}     # 发起授权
GET  /api/ai-oauth/callback/{provider}      # 授权回调
POST /api/ai-oauth/refresh/{provider}       # 刷新Token
GET  /api/ai-oauth/status/{provider}        # 查看授权状态
DELETE /api/ai-oauth/revoke/{provider}      # 撤销授权
```

## 界面设计

### AI配置页面

```
┌─────────────────────────────────────┐
│  AI配置管理                          │
├─────────────────────────────────────┤
│                                     │
│  [MiniMax]  ✓ 已授权               │
│  Token有效期: 2026-03-26            │
│  [撤销授权] [刷新Token]             │
│                                     │
│  [ChatGPT]  ✗ 未授权               │
│  [授权登录]                         │
│                                     │
│  [小龙虾]   ✓ 已授权               │
│  Token有效期: 2026-04-01            │
│  [撤销授权] [刷新Token]             │
│                                     │
│  [Banana]   ✗ 未授权               │
│  [授权登录]                         │
│                                     │
│  [+ 添加其他AI厂商]                 │
└─────────────────────────────────────┘
```

### 授权按钮

- **未授权**: 显示"授权登录"按钮
- **已授权**: 显示Token有效期和"撤销授权"按钮
- **即将过期**: 显示"刷新Token"按钮

## 优势

### 1. 安全性
- 不需要手动复制粘贴API Key
- Token自动管理
- 支持自动刷新

### 2. 便捷性
- 一键授权
- 自动配置
- 无需记忆API Key

### 3. 可靠性
- Token过期自动刷新
- 授权状态实时显示
- 错误提示清晰

## 兼容性

### 支持两种配置方式

1. **OAuth授权**（推荐）
   - 适合有OAuth支持的AI厂商
   - 更安全便捷

2. **手动配置API Key**（备选）
   - 适合不支持OAuth的厂商
   - 兼容旧版本

## 实现优先级

### Phase 1（核心功能）
- [x] MiniMax OAuth授权
- [x] ChatGPT OAuth授权
- [x] 小龙虾 OAuth授权
- [x] Token自动刷新

### Phase 2（增强功能）
- [ ] Gemini OAuth授权
- [ ] Banana OAuth授权
- [ ] 授权状态监控
- [ ] Token过期提醒

### Phase 3（扩展功能）
- [ ] 更多AI厂商支持
- [ ] 批量授权管理
- [ ] 使用统计
- [ ] 费用监控

## 注意事项

1. **OAuth配置**: 需要在各AI厂商平台注册应用
2. **回调URL**: 必须配置正确的回调地址
3. **Token管理**: 定期检查Token有效期
4. **错误处理**: 授权失败时的友好提示

## 测试计划

1. **MiniMax授权测试**
   - 授权流程
   - Token获取
   - API调用
   - Token刷新

2. **ChatGPT授权测试**
   - 同上

3. **小龙虾授权测试**
   - 同上

4. **异常测试**
   - 授权失败
   - Token过期
   - 网络错误
   - 撤销授权

---

**需求版本**: v3.0  
**更新日期**: 2026-02-26  
**状态**: 待实现

