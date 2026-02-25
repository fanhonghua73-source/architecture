<template>
	<view class="container">
		<view class="form">
			<view class="form-item">
				<text class="label">项目名称</text>
				<input v-model="formData.name" placeholder="请输入项目名称" class="input" />
			</view>
			
			<view class="form-item">
				<text class="label">项目地址</text>
				<input v-model="formData.address" placeholder="请输入项目地址" class="input" />
			</view>
			
			<view class="form-item">
				<text class="label">建筑面积（㎡）</text>
				<input v-model.number="formData.area" type="digit" placeholder="请输入建筑面积" class="input" />
			</view>
			
			<view class="form-item">
				<text class="label">项目预算（元）</text>
				<input v-model.number="formData.budget" type="digit" placeholder="请输入项目预算" class="input" />
			</view>
			
			<view class="form-item">
				<text class="label">项目状态</text>
				<picker :value="statusIndex" :range="statusOptions" @change="onStatusChange">
					<view class="picker">
						{{ statusOptions[statusIndex] }}
					</view>
				</picker>
			</view>
			
			<view class="form-item">
				<text class="label">项目描述</text>
				<textarea 
					v-model="formData.description" 
					placeholder="请输入项目描述" 
					class="textarea"
					maxlength="500"
				/>
			</view>
		</view>
		
		<view class="footer">
			<button class="submit-btn" @click="handleSubmit">创建项目</button>
		</view>
	</view>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { createProject } from '@/api/project.js'

const statusOptions = ['进行中', '已完成', '暂停']
const statusIndex = ref(0)

const formData = reactive({
	name: '',
	address: '',
	area: null,
	budget: null,
	status: '进行中',
	description: ''
})

const onStatusChange = (e) => {
	statusIndex.value = e.detail.value
	formData.status = statusOptions[e.detail.value]
}

const handleSubmit = async () => {
	if (!formData.name) {
		uni.showToast({
			title: '请输入项目名称',
			icon: 'none'
		})
		return
	}
	
	try {
		uni.showLoading({ title: '创建中...' })
		await createProject(formData)
		uni.hideLoading()
		
		uni.showToast({
			title: '创建成功',
			icon: 'success'
		})
		
		setTimeout(() => {
			uni.navigateBack()
		}, 1000)
	} catch (error) {
		uni.hideLoading()
		console.error('创建项目失败:', error)
	}
}
</script>

<style scoped>
.container {
	min-height: 100vh;
	background: #F5F7FA;
	padding: 30rpx;
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

