<template>
	<view class="container">
		<view class="profile-header">
			<view class="avatar-section">
				<image class="avatar" :src="userInfo.avatar || '/static/default-avatar.png'" mode="aspectFill"></image>
				<view class="user-info">
					<text class="username">{{ userInfo.username || '未登录' }}</text>
					<text class="email">{{ userInfo.email || '' }}</text>
				</view>
			</view>
		</view>
		
		<view class="info-section">
			<view class="section-title">个人信息</view>
			<view class="info-list">
				<view class="info-item">
					<text class="label">公司</text>
					<text class="value">{{ userInfo.company || '未设置' }}</text>
				</view>
				<view class="info-item">
					<text class="label">职位</text>
					<text class="value">{{ userInfo.position || '未设置' }}</text>
				</view>
				<view class="info-item">
					<text class="label">手机</text>
					<text class="value">{{ userInfo.phone || '未设置' }}</text>
				</view>
			</view>
		</view>
		
		<view class="menu-section">
			<view class="menu-item" @click="handleLogout">
				<text class="menu-text">退出登录</text>
				<text class="menu-arrow">›</text>
			</view>
		</view>
	</view>
</template>

<script setup>
import { reactive, onMounted } from 'vue'
import { getProfile } from '@/api/auth.js'

const userInfo = reactive({
	username: '',
	email: '',
	company: '',
	position: '',
	phone: '',
	avatar: ''
})

const loadUserInfo = async () => {
	try {
		const res = await getProfile()
		Object.assign(userInfo, res)
	} catch (error) {
		console.error('获取用户信息失败:', error)
	}
}

const handleLogout = () => {
	uni.showModal({
		title: '提示',
		content: '确定要退出登录吗？',
		success: (res) => {
			if (res.confirm) {
				uni.removeStorageSync('token')
				uni.removeStorageSync('userInfo')
				uni.reLaunch({
					url: '/pages/login/login'
				})
			}
		}
	})
}

onMounted(() => {
	loadUserInfo()
})
</script>

<style scoped>
.container {
	min-height: 100vh;
	background: #F5F7FA;
}

.profile-header {
	background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
	padding: 60rpx 40rpx 40rpx;
}

.avatar-section {
	display: flex;
	align-items: center;
}

.avatar {
	width: 120rpx;
	height: 120rpx;
	border-radius: 60rpx;
	border: 4rpx solid rgba(255, 255, 255, 0.3);
}

.user-info {
	margin-left: 30rpx;
	flex: 1;
}

.username {
	display: block;
	font-size: 36rpx;
	font-weight: bold;
	color: #FFFFFF;
	margin-bottom: 10rpx;
}

.email {
	display: block;
	font-size: 26rpx;
	color: rgba(255, 255, 255, 0.8);
}

.info-section {
	margin: 30rpx;
	background: #FFFFFF;
	border-radius: 16rpx;
	padding: 30rpx;
}

.section-title {
	font-size: 28rpx;
	font-weight: bold;
	color: #333333;
	margin-bottom: 20rpx;
}

.info-list {
	display: flex;
	flex-direction: column;
	gap: 20rpx;
}

.info-item {
	display: flex;
	justify-content: space-between;
	align-items: center;
	padding: 20rpx 0;
	border-bottom: 1rpx solid #F0F0F0;
}

.info-item:last-child {
	border-bottom: none;
}

.label {
	font-size: 28rpx;
	color: #666666;
}

.value {
	font-size: 28rpx;
	color: #333333;
}

.menu-section {
	margin: 30rpx;
}

.menu-item {
	background: #FFFFFF;
	border-radius: 16rpx;
	padding: 30rpx;
	display: flex;
	justify-content: space-between;
	align-items: center;
}

.menu-text {
	font-size: 28rpx;
	color: #FF6B6B;
}

.menu-arrow {
	font-size: 40rpx;
	color: #CCCCCC;
}
</style>

