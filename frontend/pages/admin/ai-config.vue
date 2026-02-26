<template>
	<view class="container">
		<view class="header">
			<text class="title">AI配置管理</text>
		</view>
		
		<view class="config-list">
			<view class="config-item" v-for="config in configs" :key="config.id">
				<view class="config-info">
					<text class="provider">{{ getProviderName(config.provider) }}</text>
					<text class="api-key">API Key: {{ maskApiKey(config.api_key) }}</text>
					<text class="status" :class="config.is_active ? 'active' : 'inactive'">
						{{ config.is_active ? '启用中' : '已停用' }}
					</text>
				</view>
			</view>
		</view>
		
		<view class="add-section">
			<button class="add-btn" @click="showAddDialog = true">添加配置</button>
		</view>
		
		<!-- 添加配置弹窗 -->
		<view v-if="showAddDialog" class="dialog-mask" @click="showAddDialog = false">
			<view class="dialog" @click.stop>
				<view class="dialog-header">
					<text class="dialog-title">添加AI配置</text>
				</view>
				
				<view class="dialog-content">
					<view class="form-item">
						<text class="label">AI提供商</text>
						<view class="provider-select">
							<view 
								v-for="(provider, index) in aiProviders" 
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
						<text class="label">{{ formData.provider === 'banana' ? 'API Key' : 'API Key' }}</text>
						<input v-model="formData.api_key" class="input" :placeholder="formData.provider === 'banana' ? '请输入Banana API Key' : '请输入API Key'" />
					</view>
					
					<view class="form-item">
						<text class="label">{{ formData.provider === 'banana' ? 'Model Key（必填）' : 'API URL（可选）' }}</text>
						<input v-model="formData.api_url" class="input" :placeholder="formData.provider === 'banana' ? '请输入Banana Model Key' : '留空使用默认地址'" />
						<text v-if="formData.provider === 'banana'" class="hint">Banana需要同时配置API Key和Model Key</text>
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
const selectedProvider = ref(null)

const aiProviders = [
	{ value: 'minimax', label: 'MiniMax', type: 'llm' },
	{ value: 'gemini', label: 'Gemini', type: 'llm' },
	{ value: 'banana', label: 'Banana生图', type: 'image' }
]

const formData = reactive({
	provider: '',
	api_key: '',
	api_url: '',
	config_type: 'llm'
})

const loadConfigs = async () => {
	try {
		const res = await request.get('/api/contracts/ai-config')
		configs.value = res
	} catch (error) {
		console.error('获取配置失败:', error)
	}
}

const getProviderName = (provider) => {
	const item = aiProviders.find(p => p.value === provider)
	return item ? item.label : provider
}

const maskApiKey = (key) => {
	if (!key || key.length < 8) return '***'
	return key.substring(0, 4) + '***' + key.substring(key.length - 4)
}

const selectProvider = (provider) => {
	selectedProvider.value = provider
	formData.provider = provider.value
	formData.config_type = provider.type
}

const handleAdd = async () => {
	if (!formData.provider || !formData.api_key) {
		uni.showToast({
			title: '请填写完整信息',
			icon: 'none'
		})
		return
	}
	
	// Banana需要同时配置API Key和Model Key
	if (formData.provider === 'banana' && !formData.api_url) {
		uni.showToast({
			title: '请填写Banana Model Key',
			icon: 'none'
		})
		return
	}
	
	try {
		uni.showLoading({ title: '添加中...' })
		await request.post('/api/contracts/ai-config', formData)
		uni.hideLoading()
		
		uni.showToast({
			title: '添加成功',
			icon: 'success'
		})
		
		showAddDialog.value = false
		formData.provider = ''
		formData.api_key = ''
		formData.api_url = ''
		formData.config_type = 'llm'
		selectedProvider.value = null
		
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

.api-key {
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

.hint {
	display: block;
	font-size: 24rpx;
	color: #FF9800;
	margin-top: 10rpx;
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
	transition: all 0.3s;
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

