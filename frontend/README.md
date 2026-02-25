# 建筑师助手 - UniApp前端

基于 UniApp 开发的建筑师助手应用前端，支持多端发布（微信小程序、H5、App）。

## 功能特性

- 用户登录注册
- 项目管理（创建、查看、编辑、删除）
- 设计灵感库（瀑布流展示、分类筛选）
- 材料管理（材料列表、搜索）
- 个人中心
- 图片上传预览

## 技术栈

- UniApp (Vue 3)
- Pinia 状态管理
- uni-ui 组件库

## 开发环境

推荐使用 HBuilderX 进行开发

## 项目结构

```
frontend/
├── pages/                  # 页面
│   ├── login/             # 登录页
│   ├── index/             # 首页
│   ├── projects/          # 项目管理
│   ├── inspirations/      # 灵感库
│   ├── materials/         # 材料库
│   └── mine/              # 我的
├── api/                   # API接口
│   ├── auth.js
│   ├── project.js
│   ├── inspiration.js
│   └── material.js
├── utils/                 # 工具函数
│   └── request.js         # 网络请求封装
├── static/                # 静态资源
│   ├── tabbar/           # 底部导航图标
│   └── styles/           # 全局样式
├── config.js              # 配置文件
├── pages.json             # 页面配置
├── manifest.json          # 应用配置
├── App.vue                # 应用入口
├── main.js                # 主入口
└── package.json
```

## 配置说明

### 1. 修改API地址

编辑 `config.js` 文件，修改 `baseURL` 为你的后端API地址：

```javascript
export default {
	baseURL: 'http://your-api-domain.com',  // 修改为实际API地址
	timeout: 10000
}
```

### 2. 微信小程序配置

编辑 `manifest.json` 文件，填入你的微信小程序 AppID：

```json
"mp-weixin": {
	"appid": "your-appid-here"
}
```

## 运行项目

### 微信小程序

1. 使用 HBuilderX 打开项目
2. 点击菜单：运行 -> 运行到小程序模拟器 -> 微信开发者工具
3. 首次运行需要配置微信开发者工具路径

### H5

1. 点击菜单：运行 -> 运行到浏览器 -> Chrome
2. 访问 http://localhost:8080

### App

1. 点击菜单：运行 -> 运行到手机或模拟器
2. 选择对应的设备

## 打包发布

### 微信小程序

1. 点击菜单：发行 -> 小程序-微信
2. 填写版本号和项目备注
3. 点击发行，生成小程序代码包
4. 使用微信开发者工具上传代码

### App

1. 点击菜单：发行 -> 原生App-云打包
2. 选择打包类型（Android/iOS）
3. 填写应用信息
4. 提交打包

## 主要页面说明

### 登录页 (pages/login/login.vue)
- 用户登录
- 用户注册
- Token存储

### 首页 (pages/index/index.vue)
- 用户信息展示
- 数据统计
- 快速操作入口
- 最近项目列表

### 项目管理 (pages/projects/)
- projects.vue - 项目列表（支持状态筛选）
- add.vue - 创建项目
- detail.vue - 项目详情（支持图片上传）

### 灵感库 (pages/inspirations/)
- inspirations.vue - 灵感瀑布流（支持分类筛选）
- add.vue - 添加灵感（图片上传）
- detail.vue - 灵感详情

### 材料库 (pages/materials/)
- materials.vue - 材料列表（支持搜索）

### 我的 (pages/mine/mine.vue)
- 个人信息展示
- 退出登录

## API接口说明

所有接口都需要在请求头中携带 Token（登录和注册接口除外）：

```
Authorization: Bearer {token}
```

接口响应格式：
- 成功：返回数据对象或数组
- 失败：返回 { detail: "错误信息" }

## 注意事项

1. 首次运行需要安装依赖（HBuilderX会自动处理）
2. 微信小程序需要配置合法域名（开发时可以在开发者工具中关闭域名校验）
3. 图片上传大小限制为10MB
4. 所有页面都需要登录后才能访问（除登录页）

## 开发建议

1. 使用 HBuilderX 的代码提示功能
2. 使用 uni-app 官方组件库
3. 遵循 Vue 3 Composition API 规范
4. 注意不同平台的兼容性

## 常见问题

### 1. 网络请求失败
- 检查 config.js 中的 baseURL 是否正确
- 检查后端服务是否启动
- 检查网络连接

### 2. 图片上传失败
- 检查图片大小是否超过限制
- 检查图片格式是否支持
- 检查后端上传接口是否正常

### 3. Token过期
- 应用会自动跳转到登录页
- 重新登录即可

## 联系方式

如有问题，请联系开发团队。

