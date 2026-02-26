<template>
	<view class="container">
		<view class="form-section">
			<view class="form-item">
				<text class="label">用户名</text>
				<input v-model="formData.username" class="input" disabled />
			</view>
			
			<view class="form-item">
				<text class="label">邮箱</text>
				<input v-model="formData.email" class="input" type="email" placeholder="请输入邮箱" />
			</view>
			
			<view class="form-item">
				<text class="label">手机号</text>
				<input v-model="formData.phone" class="input" placeholder="请输入手机号" />
			</view>
			
			<view class="form-item">
				<text class="label">公司</text>
				<input v-model="formData.company" class="input" placeholder="请输入公司名称" />
			</view>
			
			<view class="form-item">
				<text class="label">职位</text>
				<input v-model="formData.position" class="input" placeholder="请输入职位" />
			</view>
		</view>
		
		<view class="btn-section">
			<button class="save-btn" @click="handleSave">保存</button>
		</view>
	</view>
</template>

<script setup>
import { reactive, onMounted } from 'vue'
import { getProfile, updateProfile } from '@/api/auth.js'

const formData = reactive({
	username: '',
	email: '',
	phone: '',
	company: '',
	position: ''
})

const loadUserInfo = async () => {
	try {
		const res = await getProfile()
		Object.assign(formData, res)
	} catch (error) {
		console.error('获取用户信息失败:', error)
	}
}

const handleSave = async () => {
	if (!formData.email) {
		uni.showToast({
			title: '请输入邮箱',
			icon: 'none'
		})
		return
	}
	
	try {
		uni.showLoading({ title: '保存中...' })
		await updateProfile(formData)
		uni.hideLoading()
		
		uni.showToast({
			title: '保存成功',
			icon: 'success'
		})
		
		setTimeout(() => {
			uni.navigateBack()
		}, 1000)
	} catch (error) {
		uni.hideLoading()
		console.error('保存失败:', error)
	}
}

onMounted(() => {
	loadUserInfo()
})
</script>

<style scoped>
.container {
	min-height: 100vh;
	background: #F5F7FA;
	padding: 30rpx;
}

.form-section {
	background: #FFFFFF;
	border-radius: 16rpx;
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

.btn-section {
	margin-top: 40rpx;
}

.save-btn {
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

