<template>
	<view class="container">
		<view class="image-upload" @click="chooseImage">
			<image v-if="imageUrl" :src="imageUrl" mode="aspectFill" class="preview-image" />
			<view v-else class="upload-placeholder">
				<text class="upload-icon">📷</text>
				<text class="upload-text">点击上传图片</text>
			</view>
		</view>
		
		<view class="form">
			<view class="form-item">
				<text class="label">标题</text>
				<input v-model="formData.title" placeholder="请输入标题" class="input" />
			</view>
			
			<view class="form-item">
				<text class="label">分类</text>
				<picker :value="categoryIndex" :range="categoryOptions" @change="onCategoryChange">
					<view class="picker">
						{{ categoryOptions[categoryIndex] }}
					</view>
				</picker>
			</view>
			
			<view class="form-item">
				<text class="label">风格</text>
				<picker :value="styleIndex" :range="styleOptions" @change="onStyleChange">
					<view class="picker">
						{{ styleOptions[styleIndex] }}
					</view>
				</picker>
			</view>
			
			<view class="form-item">
				<text class="label">标签</text>
				<input v-model="formData.tags" placeholder="多个标签用逗号分隔" class="input" />
			</view>
			
			<view class="form-item">
				<text class="label">描述</text>
				<textarea 
					v-model="formData.description" 
					placeholder="请输入描述" 
					class="textarea"
					maxlength="500"
				/>
			</view>
		</view>
		
		<view class="footer">
			<button class="submit-btn" @click="handleSubmit">添加灵感</button>
		</view>
	</view>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { createInspiration } from '@/api/inspiration.js'

const categoryOptions = ['外观', '室内', '景观', '细节']
const styleOptions = ['现代', '古典', '工业风', '简约', '奢华']

const categoryIndex = ref(0)
const styleIndex = ref(0)
const imageUrl = ref('')
const imagePath = ref('')

const formData = reactive({
	title: '',
	category: '外观',
	style: '现代',
	tags: '',
	description: ''
})

const onCategoryChange = (e) => {
	categoryIndex.value = e.detail.value
	formData.category = categoryOptions[e.detail.value]
}

const onStyleChange = (e) => {
	styleIndex.value = e.detail.value
	formData.style = styleOptions[e.detail.value]
}

const chooseImage = () => {
	uni.chooseImage({
		count: 1,
		sizeType: ['compressed'],
		sourceType: ['album', 'camera'],
		success: (res) => {
			imageUrl.value = res.tempFilePaths[0]
			imagePath.value = res.tempFilePaths[0]
		}
	})
}

const handleSubmit = async () => {
	if (!imagePath.value) {
		uni.showToast({
			title: '请上传图片',
			icon: 'none'
		})
		return
	}
	
	if (!formData.title) {
		uni.showToast({
			title: '请输入标题',
			icon: 'none'
		})
		return
	}
	
	try {
		uni.showLoading({ title: '上传中...' })
		await createInspiration(imagePath.value, formData)
		uni.hideLoading()
		
		uni.showToast({
			title: '添加成功',
			icon: 'success'
		})
		
		setTimeout(() => {
			uni.navigateBack()
		}, 1000)
	} catch (error) {
		uni.hideLoading()
		console.error('添加灵感失败:', error)
	}
}
</script>

<style scoped>
.container {
	min-height: 100vh;
	background: #F5F7FA;
	padding: 30rpx;
}

.image-upload {
	width: 100%;
	height: 400rpx;
	background: #FFFFFF;
	border-radius: 16rpx;
	margin-bottom: 30rpx;
	overflow: hidden;
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
	background: #F5F7FA;
}

.upload-icon {
	font-size: 80rpx;
	margin-bottom: 20rpx;
}

.upload-text {
	font-size: 28rpx;
	color: #999999;
}

.form {
	background: #FFFFFF;
	border-radius: 16rpx;
	padding: 30rpx;
}

.form-item {
	margin-bottom: 30rpx;
}

.label {
	display: block;
	font-size: 28rpx;
	color: #333333;
	margin-bottom: 15rpx;
}

.input, .picker {
	width: 100%;
	height: 80rpx;
	background: #F5F7FA;
	border-radius: 12rpx;
	padding: 0 20rpx;
	font-size: 28rpx;
	color: #333333;
	line-height: 80rpx;
}

.textarea {
	width: 100%;
	min-height: 200rpx;
	background: #F5F7FA;
	border-radius: 12rpx;
	padding: 20rpx;
	font-size: 28rpx;
	color: #333333;
}

.footer {
	margin-top: 40rpx;
}

.submit-btn {
	width: 100%;
	height: 88rpx;
	background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
	color: #FFFFFF;
	border-radius: 12rpx;
	font-size: 32rpx;
	font-weight: bold;
	border: none;
}
</style>

