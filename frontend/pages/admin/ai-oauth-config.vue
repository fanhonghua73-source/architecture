<template>
	<view class="container">
		<view class="header">
			<text class="title">AI厂商OAuth授权</text>
			<text class="subtitle">通过OAuth授权，无需手动输入API Key</text>
		</view>
		
		<view class="provider-list">
			<view class="provider-card" v-for="provider in providers" :key="provider.provider">
				<view class="provider-header">
					<view class="provider-info">
						<text class="provider-name">{{ provider.name }}</text>
						<text class="provider-type">{{ getProviderType(provider.provider) }}</text>
					</view>
					<view class="status-badge" :class="provider.authorized ? 'authorized' : 'unauthorized'">
						{{ provider.authorized ? '已授权' : '未授权' }}
					</view>
				</view>
				
				<view class="provider-body" v-if="provider.authorized">
					<view class="info-item">
						<text class="label">Token有效期</text>
						<text class="value" :class="provider.is_expired ? 'expired' : ''">
							{{ formatDate(provider.expires_at) }}
						</text>
					</view>
					
					<view class="action-buttons">
						<button 
							v-if="provider.is_expired && provider.has_refresh_token" 
							class="action-btn refresh"
							@click="refreshToken(provider.provider)"
						>
							刷新Token
						</button>
						<button 
							class="action-btn revoke"
							@click="revokeAuth(provider.provider)"
						>
							撤销授权
						</button>
					</view>
				</view>
				
				<view class="provider-body" v-else>
					<view class="auth-steps">
						<text class="step-text">1. 配置OAuth应用信息</text>
						<button class="step-btn" @click="showConfigDialog(provider.provider)">
							{{ hasOAuthApp(provider.provider) ? '已配置' : '配置' }}
						</button>
					</view>
					<view class="auth-steps">
						<text class="step-text">2. 授权登录</text>
						<button 
							class="step-btn primary" 
							:disabled="!hasOAuthApp(provider.provider)"
							@click="authorizeProvider(provider.provider)"
						>
							授权登录
						</button>
					</view>
				</view>
			</view>
		</view>
		
		<!-- 配置OAuth应用对话框 -->
		<view v-if="showDialog" class="dialog-mask" @click="showDialog = false">
			<view class="dialog" @click.stop>
				<view class="dialog-header">
					<text class="dialog-title">配置{{ currentProviderName }}应用</text>
				</view>
				
				<view class="dialog-content">
					<view class="help-box">
						<text class="help-title">配置说明</text>
						<text class="help-text">{{ getConfigHelp(currentProvider) }}</text>
					</view>
					
					<view class="form-item">
						<text class="label">Client ID</text>
						<input v-model="oauthForm.client_id" class="input" placeholder="请输入Client ID" />
					</view>
					
					<view class="form-item">
						<text class="label">Client Secret</text>
						<input v-model="oauthForm.client_secret" class="input" type="password" placeholder="请输入Client Secret" />
					</view>
					
					<view class="form-item">
						<text class="label">回调URL（复制到厂商平台）</text>
						<view class="callback-url">
							<text class="url-text">{{ getCallbackUrl(currentProvider) }}</text>
							<button class="copy-btn" @click="copyUrl">复制</button>
						</view>
					</view>
				</view>
				
				<view class="dialog-footer">
					<button class="cancel-btn" @click="showDialog = false">取消</button>
					<button class="confirm-btn" @click="saveOAuthApp">保存</button>
				</view>
			</view>
		</view>
	</view>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import request from '@/utils/request.js'
import config from '@/config.js'

const providers = ref([])
const showDialog = ref(false)
const currentProvider = ref('')
const currentProviderName = ref('')
const oauthApps = ref({})

const oauthForm = reactive({
	client_id: '',
	client_secret: ''
})

const providerHelp = {
	minimax: '在 MiniMax 开放平台创建应用，获取 Client ID 和 Secret',
	chatgpt: '在 OpenAI Platform 创建 OAuth 应用，获取凭证',
	coze: '在小龙虾开放平台创建应用，获取 AppID 和 AppSecret',
	gemini: '在 Google Cloud Console 创建 OAuth 客户端',
	banana: '在 Banana.dev 创建应用，获取 OAuth 凭证'
}

const loadStatus = async () => {
	try {
		const res = await request.get('/api/ai-oauth/status')
		providers.value = res
	} catch (error) {
		console.error('获取状态失败:', error)
	}
}

const hasOAuthApp = (provider) => {
	return oauthApps.value[provider] === true
}

const showConfigDialog = (provider) => {
	currentProvider.value = provider
	const providerData = providers.value.find(p => p.provider === provider)
	currentProviderName.value = providerData?.name || provider
	showDialog.value = true
}

const saveOAuthApp = async () => {
	if (!oauthForm.client_id || !oauthForm.client_secret) {
		uni.showToast({
			title: '请填写完整信息',
			icon: 'none'
		})
		return
	}
	
	try {
		uni.showLoading({ title: '保存中...' })
		await request.post(`/api/ai-oauth/config-app/${currentProvider.value}`, null, {
			params: {
				client_id: oauthForm.client_id,
				client_secret: oauthForm.client_secret
			}
		})
		uni.hideLoading()
		
		oauthApps.value[currentProvider.value] = true
		
		uni.showToast({
			title: '保存成功',
			icon: 'success'
		})
		
		showDialog.value = false
		oauthForm.client_id = ''
		oauthForm.client_secret = ''
	} catch (error) {
		uni.hideLoading()
		console.error('保存失败:', error)
	}
}

const authorizeProvider = (provider) => {
	const authUrl = `${config.baseURL}/api/ai-oauth/authorize/${provider}`
	// 在新窗口打开授权页面
	window.open(authUrl, '_blank')
	
	uni.showToast({
		title: '请在新窗口完成授权',
		icon: 'none',
		duration: 3000
	})
}

const refreshToken = async (provider) => {
	try {
		uni.showLoading({ title: '刷新中...' })
		await request.post(`/api/ai-oauth/refresh/${provider}`)
		uni.hideLoading()
		
		uni.showToast({
			title: '刷新成功',
			icon: 'success'
		})
		
		loadStatus()
	} catch (error) {
		uni.hideLoading()
		console.error('刷新失败:', error)
	}
}

const revokeAuth = (provider) => {
	uni.showModal({
		title: '确认撤销',
		content: '撤销后需要重新授权才能使用，确定要撤销吗？',
		success: async (res) => {
			if (res.confirm) {
				try {
					await request.delete(`/api/ai-oauth/revoke/${provider}`)
					uni.showToast({
						title: '已撤销授权',
						icon: 'success'
					})
					loadStatus()
				} catch (error) {
					console.error('撤销失败:', error)
				}
			}
		}
	})
}

const getProviderType = (provider) => {
	if (provider === 'banana') return '生图'
	return '文本生成'
}

const formatDate = (dateStr) => {
	if (!dateStr) return '未知'
	const date = new Date(dateStr)
	return date.toLocaleString('zh-CN')
}

const getConfigHelp = (provider) => {
	return providerHelp[provider] || '请在厂商平台创建OAuth应用'
}

const getCallbackUrl = (provider) => {
	return `${config.baseURL}/api/ai-oauth/callback/${provider}`
}

const copyUrl = () => {
	const url = getCallbackUrl(currentProvider.value)
	// 复制到剪贴板
	uni.setClipboardData({
		data: url,
		success: () => {
			uni.showToast({
				title: '已复制',
				icon: 'success'
			})
		}
	})
}

// 检查URL参数（OAuth回调）
const checkOAuthCallback = () => {
	const pages = getCurrentPages()
	const currentPage = pages[pages.length - 1]
	const success = currentPage.options.success
	
	if (success === 'true') {
		uni.showToast({
			title: '授权成功',
			icon: 'success'
		})
		loadStatus()
	}
}

onMounted(() => {
	loadStatus()
	checkOAuthCallback()
})
</script>

<style scoped>
.container {
	min-height: 100vh;
	background: #F5F7FA;
	padding: 30rpx;
}

.header {
	margin-bottom: 30rpx;
}

.title {
	display: block;
	font-size: 36rpx;
	font-weight: bold;
	color: #333333;
	margin-bottom: 10rpx;
}

.subtitle {
	display: block;
	font-size: 26rpx;
	color: #999999;
}

.provider-list {
	display: flex;
	flex-direction: column;
	gap: 20rpx;
}

.provider-card {
	background: #FFFFFF;
	border-radius: 16rpx;
	padding: 30rpx;
}

.provider-header {
	display: flex;
	justify-content: space-between;
	align-items: center;
	margin-bottom: 20rpx;
	padding-bottom: 20rpx;
	border-bottom: 2rpx solid #F0F0F0;
}

.provider-info {
	flex: 1;
}

.provider-name {
	display: block;
	font-size: 30rpx;
	font-weight: bold;
	color: #333333;
	margin-bottom: 5rpx;
}

.provider-type {
	display: block;
	font-size: 24rpx;
	color: #999999;
}

.status-badge {
	padding: 8rpx 16rpx;
	border-radius: 8rpx;
	font-size: 24rpx;
}

.status-badge.authorized {
	background: #E8F5E9;
	color: #4CAF50;
}

.status-badge.unauthorized {
	background: #FFF3E0;
	color: #FF9800;
}

.provider-body {
	display: flex;
	flex-direction: column;
	gap: 15rpx;
}

.info-item {
	display: flex;
	justify-content: space-between;
	align-items: center;
}

.label {
	font-size: 26rpx;
	color: #666666;
}

.value {
	font-size: 26rpx;
	color: #333333;
}

.value.expired {
	color: #FF6B6B;
}

.action-buttons {
	display: flex;
	gap: 15rpx;
}

.action-btn {
	flex: 1;
	height: 70rpx;
	border-radius: 12rpx;
	font-size: 26rpx;
	border: none;
}

.action-btn.refresh {
	background: #2196F3;
	color: #FFFFFF;
}

.action-btn.revoke {
	background: #FF6B6B;
	color: #FFFFFF;
}

.auth-steps {
	display: flex;
	justify-content: space-between;
	align-items: center;
	padding: 15rpx 0;
}

.step-text {
	font-size: 26rpx;
	color: #666666;
}

.step-btn {
	padding: 10rpx 30rpx;
	background: #F5F7FA;
	color: #666666;
	border-radius: 8rpx;
	font-size: 24rpx;
	border: none;
}

.step-btn.primary {
	background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
	color: #FFFFFF;
}

.step-btn:disabled {
	opacity: 0.5;
}

.dialog-mask {
	position: fixed;
	top: 0;
	left: 0;
	right: 0;
	bottom: 0;
	background: rgba(0, 0, 0, 0.5);
	display: flex;
	align-items: center;
	justify-content: center;
	z-index: 1000;
}

.dialog {
	width: 650rpx;
	max-height: 80vh;
	background: #FFFFFF;
	border-radius: 16rpx;
	overflow: hidden;
}

.dialog-header {
	padding: 30rpx;
	border-bottom: 2rpx solid #F0F0F0;
}

.dialog-title {
	font-size: 32rpx;
	font-weight: bold;
	color: #333333;
}

.dialog-content {
	padding: 30rpx;
	max-height: 60vh;
	overflow-y: auto;
}

.help-box {
	background: #E8F0FE;
	border-radius: 12rpx;
	padding: 20rpx;
	margin-bottom: 30rpx;
}

.help-title {
	display: block;
	font-size: 26rpx;
	font-weight: bold;
	color: #667eea;
	margin-bottom: 10rpx;
}

.help-text {
	display: block;
	font-size: 24rpx;
	color: #666666;
	line-height: 1.6;
}

.form-item {
	margin-bottom: 30rpx;
}

.form-item:last-child {
	margin-bottom: 0;
}

.input {
	width: 100%;
	height: 80rpx;
	background: #F5F7FA;
	border-radius: 12rpx;
	padding: 0 20rpx;
	font-size: 26rpx;
	margin-top: 10rpx;
}

.callback-url {
	display: flex;
	align-items: center;
	gap: 10rpx;
	margin-top: 10rpx;
}

.url-text {
	flex: 1;
	font-size: 22rpx;
	color: #666666;
	background: #F5F7FA;
	padding: 15rpx;
	border-radius: 8rpx;
	word-break: break-all;
}

.copy-btn {
	padding: 10rpx 20rpx;
	background: #667eea;
	color: #FFFFFF;
	border-radius: 8rpx;
	font-size: 24rpx;
	border: none;
}

.dialog-footer {
	display: flex;
	border-top: 2rpx solid #F0F0F0;
}

.cancel-btn, .confirm-btn {
	flex: 1;
	height: 88rpx;
	border: none;
	font-size: 28rpx;
}

.cancel-btn {
	background: #FFFFFF;
	color: #666666;
}

.confirm-btn {
	background: #667eea;
	color: #FFFFFF;
}
</style>

