<template>
	<view class="container">
		<view class="header">
			<text class="title">OAuth登录配置</text>
		</view>
		
		<view class="config-list">
			<view class="config-item" v-for="config in configs" :key="config.id">
				<view class="config-info">
					<text class="provider">{{ getProviderName(config.provider) }}</text>
					<text class="client-id">Client ID: {{ maskKey(config.api_key) }}</text>
					<text class="status" :class="config.is_active ? 'active' : 'inactive'">
						{{ config.is_active ? '启用中' : '已停用' }}
					</text>
				</view>
			</view>
		</view>
		
		<view class="add-section">
			<button class="add-btn" @click="showAddDialog = true">添加OAuth配置</button>
		</view>
		
		<!-- 添加配置弹窗 -->
		<view v-if="showAddDialog" class="dialog-mask" @click="showAddDialog = false">
			<view class="dialog" @click.stop>
				<view class="dialog-header">
					<text class="dialog-title">添加OAuth配置</text>
				</view>
				
				<view class="dialog-content">
					<view class="form-item">
						<text class="label">OAuth提供商</text>
						<view class="provider-select">
							<view 
								v-for="provider in oauthProviders" 
								:key="provider.value"
								class="provider-option"
								:class="{ 'selected': formData.provider === provider.value }"
								@click="selectProvider(provider)"
							>
								<text class="provider-label">{{ provider.label }}</text>
								<text v-if="formData.provider === provider.value" class="check-icon">✓</text>
							</view>
						</view>
					</view>
					
					<view class="form-item">
						<text class="label">Client ID</text>
						<input v-model="formData.client_id" class="input" placeholder="请输入Client ID" />
					</view>
					
					<view class="form-item">
						<text class="label">Client Secret</text>
						<input v-model="formData.client_secret" class="input" type="password" placeholder="请输入Client Secret" />
					</view>
					
					<view class="help-text">
						<text class="help-title">配置说明：</text>
						<text class="help-item">• GitHub: 在 Settings -> Developer settings -> OAuth Apps 创建应用</text>
						<text class="help-item">• Google: 在 Google Cloud Console 创建OAuth客户端</text>
						<text class="help-item">• 微信: 在微信开放平台创建网站应用</text>
					</view>
				</view>
				
				<view class="dialog-footer">
					<button class="cancel-btn" @click="showAddDialog = false">取消</button>
					<button class="confirm-btn" @click="handleAdd">确定</button>
				</view>
			</view>
		</view>
	</view>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import request from '@/utils/request.js'

const configs = ref([])
const showAddDialog = ref(false)

const oauthProviders = [
	{ value: 'github', label: 'GitHub' },
	{ value: 'google', label: 'Google' },
	{ value: 'wechat', label: '微信' }
]

const formData = reactive({
	provider: '',
	client_id: '',
	client_secret: ''
})

const loadConfigs = async () => {
	try {
		const res = await request.get('/api/contracts/ai-config')
		configs.value = res.filter(c => c.config_type === 'oauth')
	} catch (error) {
		console.error('获取配置失败:', error)
	}
}

const getProviderName = (provider) => {
	const item = oauthProviders.find(p => p.value === provider)
	return item ? item.label : provider
}

const maskKey = (key) => {
	if (!key || key.length < 8) return '***'
	return key.substring(0, 4) + '***' + key.substring(key.length - 4)
}

const selectProvider = (provider) => {
	formData.provider = provider.value
}

const handleAdd = async () => {
	if (!formData.provider || !formData.client_id || !formData.client_secret) {
		uni.showToast({
			title: '请填写完整信息',
			icon: 'none'
		})
		return
	}
	
	try {
		uni.showLoading({ title: '添加中...' })
		await request.post('/api/oauth/config', null, {
			params: {
				provider: formData.provider,
				client_id: formData.client_id,
				client_secret: formData.client_secret
			}
		})
		uni.hideLoading()
		
		uni.showToast({
			title: '添加成功',
			icon: 'success'
		})
		
		showAddDialog.value = false
		formData.provider = ''
		formData.client_id = ''
		formData.client_secret = ''
		
		loadConfigs()
	} catch (error) {
		uni.hideLoading()
		console.error('添加配置失败:', error)
	}
}

onMounted(() => {
	loadConfigs()
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
	font-size: 36rpx;
	font-weight: bold;
	color: #333333;
}

.config-list {
	display: flex;
	flex-direction: column;
	gap: 20rpx;
	margin-bottom: 30rpx;
}

.config-item {
	background: #FFFFFF;
	border-radius: 16rpx;
	padding: 30rpx;
}

.config-info {
	display: flex;
	flex-direction: column;
	gap: 10rpx;
}

.provider {
	font-size: 30rpx;
	font-weight: bold;
	color: #333333;
}

.client-id {
	font-size: 24rpx;
	color: #666666;
}

.status {
	font-size: 22rpx;
	padding: 4rpx 12rpx;
	border-radius: 8rpx;
	align-self: flex-start;
}

.status.active {
	background: #E8F5E9;
	color: #4CAF50;
}

.status.inactive {
	background: #EEEEEE;
	color: #999999;
}

.add-section {
	margin-top: 30rpx;
}

.add-btn {
	width: 100%;
	height: 88rpx;
	background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
	color: #FFFFFF;
	border-radius: 12rpx;
	font-size: 32rpx;
	font-weight: bold;
	border: none;
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
	width: 600rpx;
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

.form-item {
	margin-bottom: 30rpx;
}

.form-item:last-child {
	margin-bottom: 0;
}

.label {
	display: block;
	font-size: 28rpx;
	color: #333333;
	margin-bottom: 15rpx;
}

.input {
	width: 100%;
	height: 80rpx;
	background: #F5F7FA;
	border-radius: 12rpx;
	padding: 0 20rpx;
	font-size: 28rpx;
}

.provider-select {
	display: flex;
	flex-direction: column;
	gap: 15rpx;
}

.provider-option {
	display: flex;
	justify-content: space-between;
	align-items: center;
	padding: 20rpx;
	background: #F5F7FA;
	border-radius: 12rpx;
	border: 2rpx solid transparent;
}

.provider-option.selected {
	background: #E8F0FE;
	border-color: #667eea;
}

.provider-label {
	font-size: 28rpx;
	color: #333333;
}

.check-icon {
	font-size: 32rpx;
	color: #667eea;
	font-weight: bold;
}

.help-text {
	background: #FFF9E6;
	border-radius: 12rpx;
	padding: 20rpx;
	margin-top: 20rpx;
}

.help-title {
	display: block;
	font-size: 26rpx;
	font-weight: bold;
	color: #FF9800;
	margin-bottom: 10rpx;
}

.help-item {
	display: block;
	font-size: 24rpx;
	color: #666666;
	line-height: 1.8;
	margin-bottom: 5rpx;
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

