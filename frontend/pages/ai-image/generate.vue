<template>
	<view class="container">
		<view class="header">
			<text class="title">AI生图</text>
			<text class="subtitle">上传图片，AI帮你生成建筑设计</text>
		</view>
		
		<view class="upload-section">
			<view class="upload-item required">
				<text class="label">基础图片（必需）</text>
				<view class="image-upload" @click="chooseImage('base')">
					<image v-if="images.base" :src="images.base" class="preview-image" mode="aspectFill"></image>
					<view v-else class="upload-placeholder">
						<text class="upload-icon">+</text>
						<text class="upload-text">点击上传</text>
					</view>
				</view>
			</view>
			
			<view class="upload-item">
				<text class="label">参考图片1（可选）</text>
				<view class="image-upload" @click="chooseImage('ref1')">
					<image v-if="images.ref1" :src="images.ref1" class="preview-image" mode="aspectFill"></image>
					<view v-else class="upload-placeholder">
						<text class="upload-icon">+</text>
						<text class="upload-text">点击上传</text>
					</view>
				</view>
			</view>
			
			<view class="upload-item">
				<text class="label">参考图片2（可选）</text>
				<view class="image-upload" @click="chooseImage('ref2')">
					<image v-if="images.ref2" :src="images.ref2" class="preview-image" mode="aspectFill"></image>
					<view v-else class="upload-placeholder">
						<text class="upload-icon">+</text>
						<text class="upload-text">点击上传</text>
					</view>
				</view>
			</view>
			
			<view class="upload-item">
				<text class="label">参考图片3（可选）</text>
				<view class="image-upload" @click="chooseImage('ref3')">
					<image v-if="images.ref3" :src="images.ref3" class="preview-image" mode="aspectFill"></image>
					<view v-else class="upload-placeholder">
						<text class="upload-icon">+</text>
						<text class="upload-text">点击上传</text>
					</view>
				</view>
			</view>
		</view>
		
		<view class="prompt-section">
			<text class="label">提示词（可选）</text>
			<textarea 
				v-model="prompt" 
				class="prompt-input" 
				placeholder="输入设计要求，如果不填写，AI会根据参考图片自动生成提示词"
			></textarea>
		</view>
		
		<view class="btn-section">
			<button class="generate-btn" @click="handleGenerate">生成设计图</button>
		</view>
		
		<!-- 生成结果 -->
		<view v-if="result" class="result-section">
			<view class="section-header">
				<text class="section-title">生成结果</text>
			</view>
			<image :src="result.image" class="result-image" mode="aspectFit" @click="previewResult"></image>
			<view class="result-actions">
				<button class="action-btn" @click="showRegenerateDialog = true">重新生成</button>
				<button class="action-btn primary" @click="saveToInspiration">保存到灵感库</button>
			</view>
		</view>
		
		<!-- 重新生成对话框 -->
		<view v-if="showRegenerateDialog" class="dialog-mask" @click="showRegenerateDialog = false">
			<view class="dialog" @click.stop>
				<view class="dialog-header">
					<text class="dialog-title">调整提示词</text>
				</view>
				<view class="dialog-content">
					<textarea v-model="newPrompt" class="dialog-textarea" placeholder="输入新的提示词"></textarea>
				</view>
				<view class="dialog-footer">
					<button class="cancel-btn" @click="showRegenerateDialog = false">取消</button>
					<button class="confirm-btn" @click="handleRegenerate">重新生成</button>
				</view>
			</view>
		</view>
	</view>
</template>

<script setup>
import { ref, reactive } from 'vue'
import config from '@/config.js'

const images = reactive({
	base: '',
	ref1: '',
	ref2: '',
	ref3: ''
})

const prompt = ref('')
const result = ref(null)
const showRegenerateDialog = ref(false)
const newPrompt = ref('')
const currentGenerationId = ref(null)

const chooseImage = (type) => {
	uni.chooseImage({
		count: 1,
		sizeType: ['compressed'],
		sourceType: ['album', 'camera'],
		success: (res) => {
			images[type] = res.tempFilePaths[0]
		}
	})
}

const handleGenerate = async () => {
	if (!images.base) {
		uni.showToast({
			title: '请上传基础图片',
			icon: 'none'
		})
		return
	}
	
	uni.showLoading({ title: '生成中，请稍候...' })
	
	try {
		const token = uni.getStorageSync('token')
		
		uni.uploadFile({
			url: `${config.baseURL}/api/ai-image/generate`,
			filePath: images.base,
			name: 'base_image',
			formData: {
				prompt: prompt.value,
				reference_image1: images.ref1 || '',
				reference_image2: images.ref2 || '',
				reference_image3: images.ref3 || ''
			},
			header: {
				'Authorization': `Bearer ${token}`
			},
			success: (uploadRes) => {
				const data = JSON.parse(uploadRes.data)
				result.value = {
					id: data.id,
					image: config.baseURL + data.result_image_url
				}
				currentGenerationId.value = data.id
				
				uni.hideLoading()
				uni.showToast({
					title: '生成成功',
					icon: 'success'
				})
			},
			fail: (error) => {
				uni.hideLoading()
				console.error('生成失败:', error)
				uni.showToast({
					title: '生成失败',
					icon: 'none'
				})
			}
		})
	} catch (error) {
		uni.hideLoading()
		console.error('生成失败:', error)
	}
}

const handleRegenerate = async () => {
	if (!newPrompt.value) {
		uni.showToast({
			title: '请输入提示词',
			icon: 'none'
		})
		return
	}
	
	showRegenerateDialog.value = false
	uni.showLoading({ title: '重新生成中...' })
	
	try {
		const token = uni.getStorageSync('token')
		const res = await fetch(`${config.baseURL}/api/ai-image/regenerate/${currentGenerationId.value}`, {
			method: 'POST',
			headers: {
				'Authorization': `Bearer ${token}`,
				'Content-Type': 'application/json'
			},
			body: JSON.stringify({
				new_prompt: newPrompt.value
			})
		})
		
		const data = await res.json()
		result.value = {
			id: data.id,
			image: config.baseURL + data.result_image_url
		}
		currentGenerationId.value = data.id
		
		uni.hideLoading()
		uni.showToast({
			title: '重新生成成功',
			icon: 'success'
		})
	} catch (error) {
		uni.hideLoading()
		console.error('重新生成失败:', error)
	}
}

const previewResult = () => {
	if (result.value) {
		uni.previewImage({
			urls: [result.value.image],
			current: 0
		})
	}
}

const saveToInspiration = () => {
	uni.navigateTo({
		url: `/pages/inspirations/add?imageUrl=${encodeURIComponent(result.value.image)}`
	})
}
</script>

<style scoped>
.container {
	min-height: 100vh;
	background: #F5F7FA;
	padding: 30rpx;
}

.header {
	text-align: center;
	margin-bottom: 40rpx;
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

.upload-section {
	display: grid;
	grid-template-columns: repeat(2, 1fr);
	gap: 20rpx;
	margin-bottom: 30rpx;
}

.upload-item {
	display: flex;
	flex-direction: column;
}

.upload-item.required .label::after {
	content: '*';
	color: #FF6B6B;
	margin-left: 5rpx;
}

.label {
	font-size: 26rpx;
	color: #666666;
	margin-bottom: 10rpx;
}

.image-upload {
	width: 100%;
	height: 300rpx;
	border-radius: 12rpx;
	overflow: hidden;
	background: #FFFFFF;
}

.preview-image {
	width: 100%;
	height: 100%;
}

.upload-placeholder {
	width: 100%;
	height: 100%;
	display: flex;
	flex-direction: column;
	align-items: center;
	justify-content: center;
	border: 2rpx dashed #DDDDDD;
	border-radius: 12rpx;
}

.upload-icon {
	font-size: 60rpx;
	color: #CCCCCC;
	margin-bottom: 10rpx;
}

.upload-text {
	font-size: 24rpx;
	color: #999999;
}

.prompt-section {
	background: #FFFFFF;
	border-radius: 16rpx;
	padding: 30rpx;
	margin-bottom: 30rpx;
}

.prompt-input {
	width: 100%;
	min-height: 200rpx;
	background: #F5F7FA;
	border-radius: 12rpx;
	padding: 20rpx;
	font-size: 26rpx;
	margin-top: 15rpx;
}

.generate-btn {
	width: 100%;
	height: 88rpx;
	background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
	color: #FFFFFF;
	border-radius: 12rpx;
	font-size: 32rpx;
	font-weight: bold;
	border: none;
}

.result-section {
	background: #FFFFFF;
	border-radius: 16rpx;
	padding: 30rpx;
	margin-top: 30rpx;
}

.section-header {
	margin-bottom: 20rpx;
}

.section-title {
	font-size: 30rpx;
	font-weight: bold;
	color: #333333;
}

.result-image {
	width: 100%;
	min-height: 400rpx;
	border-radius: 12rpx;
	margin-bottom: 20rpx;
}

.result-actions {
	display: flex;
	gap: 20rpx;
}

.action-btn {
	flex: 1;
	height: 80rpx;
	background: #F5F7FA;
	color: #666666;
	border-radius: 12rpx;
	font-size: 28rpx;
	border: none;
}

.action-btn.primary {
	background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
	color: #FFFFFF;
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

.dialog-textarea {
	width: 100%;
	min-height: 200rpx;
	background: #F5F7FA;
	border-radius: 12rpx;
	padding: 20rpx;
	font-size: 26rpx;
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

