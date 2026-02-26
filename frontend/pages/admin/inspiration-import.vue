<template>
	<view class="container">
		<view class="header">
			<text class="title">灵感自动导入</text>
		</view>
		
		<view class="config-section">
			<view class="section-title">导入配置</view>
			
			<view class="form-item">
				<text class="label">文件夹路径</text>
				<input v-model="config.folder_path" class="input" placeholder="请输入灵感文件夹路径" />
				<text class="hint">例如: F:/architecture/inspirations_import</text>
			</view>
			
			<view class="form-item">
				<view class="switch-row">
					<text class="label">启用自动导入</text>
					<switch :checked="config.enabled" @change="onSwitchChange" color="#667eea" />
				</view>
			</view>
			
			<button class="save-btn" @click="saveConfig">保存配置</button>
		</view>
		
		<view class="info-section">
			<view class="section-title">文件格式说明</view>
			<view class="info-content">
				<text class="info-text">在指定文件夹中放置图片和对应的txt配置文件：</text>
				
				<view class="example">
					<text class="example-title">示例文件结构：</text>
					<text class="example-text">📁 inspirations_import/</text>
					<text class="example-text">  ├─ 现代建筑.jpg</text>
					<text class="example-text">  ├─ 现代建筑.txt</text>
					<text class="example-text">  ├─ 室内设计.png</text>
					<text class="example-text">  └─ 室内设计.txt</text>
				</view>
				
				<view class="example">
					<text class="example-title">txt文件内容格式：</text>
					<text class="example-text">标题: 现代建筑外观</text>
					<text class="example-text">描述: 简约现代风格的建筑设计</text>
					<text class="example-text">分类: 外观</text>
					<text class="example-text">风格: 现代</text>
					<text class="example-text">标签: 简约,玻璃幕墙</text>
				</view>
			</view>
		</view>
		
		<view class="action-section">
			<button class="import-btn" @click="manualImport">立即导入</button>
		</view>
	</view>
</template>

<script setup>
import { reactive, onMounted } from 'vue'
import request from '@/utils/request.js'

const config = reactive({
	folder_path: '',
	enabled: true
})

const loadConfig = async () => {
	try {
		const res = await request.get('/api/inspirations/auto-import-config')
		Object.assign(config, res)
	} catch (error) {
		console.error('获取配置失败:', error)
	}
}

const saveConfig = async () => {
	try {
		uni.showLoading({ title: '保存中...' })
		await request.post('/api/inspirations/set-auto-import-config', null, {
			params: {
				folder_path: config.folder_path,
				enabled: config.enabled
			}
		})
		uni.hideLoading()
		
		uni.showToast({
			title: '保存成功',
			icon: 'success'
		})
	} catch (error) {
		uni.hideLoading()
		console.error('保存配置失败:', error)
	}
}

const manualImport = async () => {
	if (!config.folder_path) {
		uni.showToast({
			title: '请先设置文件夹路径',
			icon: 'none'
		})
		return
	}
	
	try {
		uni.showLoading({ title: '导入中...' })
		const res = await request.post('/api/inspirations/import-from-folder', null, {
			params: {
				folder_path: config.folder_path
			}
		})
		uni.hideLoading()
		
		uni.showModal({
			title: '导入完成',
			content: `成功导入 ${res.imported_count} 个灵感${res.errors.length > 0 ? '\n部分文件导入失败' : ''}`,
			showCancel: false
		})
	} catch (error) {
		uni.hideLoading()
		console.error('导入失败:', error)
	}
}

const onSwitchChange = (e) => {
	config.enabled = e.detail.value
}

onMounted(() => {
	loadConfig()
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

.config-section, .info-section, .action-section {
	background: #FFFFFF;
	border-radius: 16rpx;
	padding: 30rpx;
	margin-bottom: 30rpx;
}

.section-title {
	font-size: 30rpx;
	font-weight: bold;
	color: #333333;
	margin-bottom: 30rpx;
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
	font-weight: 500;
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
	color: #999999;
	margin-top: 10rpx;
}

.switch-row {
	display: flex;
	justify-content: space-between;
	align-items: center;
}

.save-btn, .import-btn {
	width: 100%;
	height: 88rpx;
	background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
	color: #FFFFFF;
	border-radius: 12rpx;
	font-size: 32rpx;
	font-weight: bold;
	border: none;
	margin-top: 30rpx;
}

.info-content {
	display: flex;
	flex-direction: column;
	gap: 20rpx;
}

.info-text {
	font-size: 26rpx;
	color: #666666;
	line-height: 1.6;
}

.example {
	background: #F9FAFB;
	border-radius: 12rpx;
	padding: 20rpx;
	border-left: 4rpx solid #667eea;
}

.example-title {
	display: block;
	font-size: 26rpx;
	font-weight: bold;
	color: #333333;
	margin-bottom: 15rpx;
}

.example-text {
	display: block;
	font-size: 24rpx;
	color: #666666;
	line-height: 1.8;
	font-family: monospace;
}
</style>

