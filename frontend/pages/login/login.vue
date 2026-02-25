<template>
	<view class="login-container">
		<view class="login-header">
			<text class="app-name">建筑师助手</text>
			<text class="app-slogan">让设计更简单</text>
		</view>
		
		<view class="login-form" v-if="!showRegisterForm">
			<view class="form-item">
				<input 
					v-model="formData.username" 
					placeholder="请输入用户名" 
					class="input"
				/>
			</view>
			
			<view class="form-item">
				<input 
					v-model="formData.password" 
					type="password"
					placeholder="请输入密码" 
					class="input"
				/>
			</view>
			
			<button class="login-btn" @click="handleLogin">登录</button>
			
			<view class="register-link">
				<text>还没有账号？</text>
				<text class="link-text" @click="showRegisterForm = true">立即注册</text>
			</view>
		</view>
		
		<!-- 注册表单 -->
		<view class="login-form" v-else>
			<view class="form-title">注册账号</view>
			
			<view class="form-item">
				<input 
					v-model="registerData.username" 
					placeholder="用户名" 
					class="input"
				/>
			</view>
			
			<view class="form-item">
				<input 
					v-model="registerData.email" 
					placeholder="邮箱" 
					class="input"
				/>
			</view>
			
			<view class="form-item">
				<input 
					v-model="registerData.phone" 
					placeholder="手机号（可选）" 
					class="input"
				/>
			</view>
			
			<view class="form-item">
				<input 
					v-model="registerData.password" 
					type="password"
					placeholder="密码" 
					class="input"
				/>
			</view>
			
			<button class="login-btn" @click="handleRegister">注册</button>
			
			<view class="register-link">
				<text>已有账号？</text>
				<text class="link-text" @click="showRegisterForm = false">返回登录</text>
			</view>
		</view>
	</view>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { login, register } from '@/api/auth.js'

const formData = reactive({
	username: '',
	password: ''
})

const registerData = reactive({
	username: '',
	email: '',
	phone: '',
	password: ''
})

const showRegisterForm = ref(false)

// 登录
const handleLogin = async () => {
	if (!formData.username || !formData.password) {
		uni.showToast({
			title: '请填写完整信息',
			icon: 'none'
		})
		return
	}
	
	try {
		uni.showLoading({ title: '登录中...' })
		const res = await login(formData)
		
		// 保存token
		uni.setStorageSync('token', res.access_token)
		
		uni.hideLoading()
		uni.showToast({
			title: '登录成功',
			icon: 'success'
		})
		
		// 跳转到首页
		setTimeout(() => {
			uni.switchTab({
				url: '/pages/index/index'
			})
		}, 1000)
	} catch (error) {
		uni.hideLoading()
		console.error('登录失败:', error)
	}
}

// 注册
const handleRegister = async () => {
	if (!registerData.username || !registerData.email || !registerData.password) {
		uni.showToast({
			title: '请填写完整信息',
			icon: 'none'
		})
		return
	}
	
	try {
		uni.showLoading({ title: '注册中...' })
		await register(registerData)
		
		uni.hideLoading()
		uni.showToast({
			title: '注册成功',
			icon: 'success'
		})
		
		// 自动填充用户名并返回登录
		formData.username = registerData.username
		showRegisterForm.value = false
	} catch (error) {
		uni.hideLoading()
		console.error('注册失败:', error)
	}
}
</script>

<style scoped>
.login-container {
	min-height: 100vh;
	background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
	padding: 100rpx 60rpx;
}

.login-header {
	text-align: center;
	margin-bottom: 100rpx;
}

.app-name {
	display: block;
	font-size: 56rpx;
	font-weight: bold;
	color: #FFFFFF;
	margin-bottom: 20rpx;
	letter-spacing: 4rpx;
}

.app-slogan {
	display: block;
	font-size: 28rpx;
	color: rgba(255, 255, 255, 0.8);
}

.login-form {
	background: #FFFFFF;
	border-radius: 24rpx;
	padding: 60rpx 40rpx;
	box-shadow: 0 20rpx 60rpx rgba(0, 0, 0, 0.1);
}

.form-title {
	font-size: 36rpx;
	font-weight: bold;
	text-align: center;
	margin-bottom: 40rpx;
	color: #333333;
}

.form-item {
	margin-bottom: 30rpx;
}

.input {
	width: 100%;
	height: 88rpx;
	background: #F5F7FA;
	border-radius: 12rpx;
	padding: 0 30rpx;
	font-size: 28rpx;
}

.login-btn {
	width: 100%;
	height: 88rpx;
	background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
	color: #FFFFFF;
	border-radius: 12rpx;
	font-size: 32rpx;
	font-weight: bold;
	margin-top: 40rpx;
	border: none;
}

.register-link {
	text-align: center;
	margin-top: 40rpx;
	font-size: 26rpx;
	color: #666666;
}

.link-text {
	color: #667eea;
	margin-left: 10rpx;
}
</style>
