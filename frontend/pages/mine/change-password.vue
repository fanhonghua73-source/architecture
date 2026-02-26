<template>
	<view class="container">
		<view class="form-section">
			<view class="form-item">
				<text class="label">旧密码</text>
				<input v-model="formData.oldPassword" class="input" type="password" placeholder="请输入旧密码" />
			</view>
			
			<view class="form-item">
				<text class="label">新密码</text>
				<input v-model="formData.newPassword" class="input" type="password" placeholder="请输入新密码" />
			</view>
			
			<view class="form-item">
				<text class="label">确认新密码</text>
				<input v-model="formData.confirmPassword" class="input" type="password" placeholder="请再次输入新密码" />
			</view>
		</view>
		
		<view class="btn-section">
			<button class="save-btn" @click="handleChangePassword">修改密码</button>
		</view>
	</view>
</template>

<script setup>
import { reactive } from 'vue'
import { changePassword } from '@/api/auth.js'

const formData = reactive({
	oldPassword: '',
	newPassword: '',
	confirmPassword: ''
})

const handleChangePassword = async () => {
	if (!formData.oldPassword || !formData.newPassword || !formData.confirmPassword) {
		uni.showToast({
			title: '请填写完整信息',
			icon: 'none'
		})
		return
	}
	
	if (formData.newPassword !== formData.confirmPassword) {
		uni.showToast({
			title: '两次密码输入不一致',
			icon: 'none'
		})
		return
	}
	
	if (formData.newPassword.length < 6) {
		uni.showToast({
			title: '密码长度至少6位',
			icon: 'none'
		})
		return
	}
	
	try {
		uni.showLoading({ title: '修改中...' })
		await changePassword({
			old_password: formData.oldPassword,
			new_password: formData.newPassword
		})
		uni.hideLoading()
		
		uni.showToast({
			title: '修改成功，请重新登录',
			icon: 'success'
		})
		
		setTimeout(() => {
			uni.removeStorageSync('token')
			uni.reLaunch({
				url: '/pages/login/login'
			})
		}, 1500)
	} catch (error) {
		uni.hideLoading()
		console.error('修改密码失败:', error)
	}
}
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

