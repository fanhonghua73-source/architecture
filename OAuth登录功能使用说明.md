# OAuth第三方登录功能使用说明

## 功能概述

系统支持通过第三方OAuth提供商登录，用户可以使用GitHub、Google或微信账号快速登录，无需注册。

## 支持的OAuth提供商

### 1. GitHub
- **适用场景**: 开发者、技术人员
- **获取信息**: 用户名、邮箱、头像
- **配置地址**: https://github.com/settings/developers

### 2. Google
- **适用场景**: 通用用户
- **获取信息**: 姓名、邮箱、头像
- **配置地址**: https://console.cloud.google.com/

### 3. 微信
- **适用场景**: 国内用户
- **获取信息**: 昵称、头像
- **配置地址**: https://open.weixin.qq.com/

## 配置步骤

### GitHub OAuth配置

1. **创建OAuth应用**
   - 访问 https://github.com/settings/developers
   - 点击 "New OAuth App"
   - 填写应用信息：
     - Application name: 建筑师助手
     - Homepage URL: http://localhost:8000
     - Authorization callback URL: http://localhost:8000/api/oauth/callback/github

2. **获取凭证**
   - 创建后获得 Client ID
   - 生成 Client Secret

3. **在系统中配置**
   - 登录root账号
   - 进入"我的" -> "OAuth登录配置"
   - 点击"添加OAuth配置"
   - 选择GitHub
   - 输入Client ID和Client Secret
   - 保存

### Google OAuth配置

1. **创建OAuth客户端**
   - 访问 https://console.cloud.google.com/
   - 创建新项目或选择现有项目
   - 启用 Google+ API
   - 创建OAuth 2.0客户端ID
   - 应用类型选择"Web应用"
   - 授权重定向URI: http://localhost:8000/api/oauth/callback/google

2. **获取凭证**
   - 客户端ID
   - 客户端密钥

3. **在系统中配置**
   - 同GitHub配置步骤

### 微信OAuth配置

1. **创建网站应用**
   - 访问 https://open.weixin.qq.com/
   - 注册开发者账号
   - 创建网站应用
   - 填写网站信息和回调域名
   - 授权回调域: localhost:8000

2. **获取凭证**
   - AppID
   - AppSecret

3. **在系统中配置**
   - 同GitHub配置步骤

## 用户使用流程

### 登录流程

1. **访问登录页面**
   - 打开应用登录页面
   - 看到OAuth登录选项

2. **选择登录方式**
   - 点击对应的OAuth提供商按钮
   - 例如：点击"GitHub登录"

3. **授权**
   - 跳转到OAuth提供商页面
   - 登录并授权应用访问基本信息

4. **自动登录**
   - 授权成功后自动跳转回应用
   - 系统自动创建账号（首次登录）
   - 直接进入首页

### 首次登录

- **自动创建账号**: 系统会自动创建用户账号
- **自动审批**: OAuth用户无需等待root审批
- **信息同步**: 自动同步头像、用户名等信息
- **随机密码**: 系统生成随机密码（用户可后续修改）

### 后续登录

- 直接点击对应的OAuth按钮
- 无需输入用户名密码
- 快速登录

## 技术实现

### 后端接口

```
GET  /api/oauth/login/{provider}        # 发起OAuth登录
GET  /api/oauth/callback/{provider}     # OAuth回调处理
POST /api/oauth/config                  # 配置OAuth提供商
GET  /api/oauth/providers               # 获取已配置的提供商列表
```

### 登录流程

1. 用户点击OAuth登录按钮
2. 前端调用 `/api/oauth/login/{provider}`
3. 后端重定向到OAuth提供商授权页面
4. 用户授权后，OAuth提供商回调 `/api/oauth/callback/{provider}`
5. 后端获取用户信息，创建或查找用户
6. 生成JWT Token
7. 重定向到前端，携带Token
8. 前端保存Token，完成登录

### 安全性

- **HTTPS**: 生产环境必须使用HTTPS
- **State参数**: 防止CSRF攻击
- **Token验证**: JWT Token验证
- **密钥保护**: Client Secret安全存储

## 数据库设计

### OAuth配置表

```sql
ai_configs:
  - provider: github/google/wechat
  - config_type: oauth
  - api_key: Client ID
  - api_url: Client Secret
  - is_active: 是否启用
```

### 用户表扩展

OAuth用户特点：
- `is_approved`: 自动设为True
- `email`: 可能为空（微信）
- `avatar`: 自动同步
- `password_hash`: 随机生成

## 注意事项

### 开发环境

1. **回调URL**: 使用 http://localhost:8000
2. **测试账号**: 使用自己的OAuth账号测试
3. **调试**: 查看后端日志

### 生产环境

1. **域名**: 必须使用真实域名
2. **HTTPS**: 必须启用HTTPS
3. **回调URL**: 更新为生产环境URL
4. **密钥管理**: 使用环境变量存储密钥

### 常见问题

**Q: OAuth登录失败怎么办？**
A: 检查以下几点：
- Client ID和Secret是否正确
- 回调URL是否匹配
- OAuth应用是否已审核通过（某些平台需要）
- 网络是否正常

**Q: 微信登录为什么没有邮箱？**
A: 微信不提供邮箱信息，系统会生成一个虚拟邮箱

**Q: OAuth用户如何修改密码？**
A: 在"我的" -> "修改密码"中设置新密码

**Q: 可以绑定多个OAuth账号吗？**
A: 目前通过邮箱关联，相同邮箱会使用同一账号

## 配置示例

### GitHub配置示例

```
Client ID: Iv1.a1b2c3d4e5f6g7h8
Client Secret: 1234567890abcdef1234567890abcdef12345678
Callback URL: http://localhost:8000/api/oauth/callback/github
```

### Google配置示例

```
Client ID: 123456789-abc123def456.apps.googleusercontent.com
Client Secret: GOCSPX-abcdefghijklmnopqrstuvwx
Callback URL: http://localhost:8000/api/oauth/callback/google
```

### 微信配置示例

```
AppID: wx1234567890abcdef
AppSecret: 1234567890abcdef1234567890abcdef
Callback Domain: localhost:8000
```

## 测试步骤

1. **配置OAuth**
   - Root用户登录
   - 配置至少一个OAuth提供商

2. **测试登录**
   - 退出当前账号
   - 点击OAuth登录按钮
   - 完成授权流程
   - 验证是否成功登录

3. **验证信息**
   - 检查用户信息是否正确
   - 检查头像是否同步
   - 检查权限是否正常

## 扩展功能

### 未来可能添加的功能

- 账号绑定：允许用户绑定多个OAuth账号
- 解绑功能：允许用户解绑OAuth账号
- 更多提供商：支持更多OAuth提供商
- 信息同步：定期同步OAuth账号信息

## 技术支持

- API文档: http://localhost:8000/docs
- OAuth测试: http://localhost:8000/api/oauth/providers
- 后端日志: 查看终端输出

---

**版本**: v2.2  
**日期**: 2026-02-26  
**状态**: ✅ 完成

