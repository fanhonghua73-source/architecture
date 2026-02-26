<template>
	<view class="container">
		<view class="profile-header">
			<view class="avatar-section">
				<view class="avatar-wrapper" @click="handleUploadAvatar">
					<image class="avatar" :src="getAvatarUrl(userInfo.avatar)" mode="aspectFill"></image>
					<view class="avatar-mask">
						<text class="upload-text">更换头像</text>
					</view>
				</view>
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
			<view class="menu-item" v-if="userInfo.is_root" @click="handleManageUsers">
				<text class="menu-text">用户管理</text>
				<text class="menu-arrow">›</text>
			</view>
			<view class="menu-item" v-if="userInfo.is_root" @click="handleProjectApproval">
				<text class="menu-text">项目审批</text>
				<text class="menu-arrow">›</text>
			</view>
			<view class="menu-item" v-if="userInfo.is_root" @click="handleAIConfig">
				<text class="menu-text">AI配置（手动）</text>
				<text class="menu-arrow">›</text>
			</view>
			<view class="menu-item" v-if="userInfo.is_root" @click="handleAIOAuthConfig">
				<text class="menu-text">AI厂商OAuth授权</text>
				<text class="menu-arrow">›</text>
			</view>
			<view class="menu-item" v-if="userInfo.is_root" @click="handleOAuthConfig">
				<text class="menu-text">用户OAuth登录配置</text>
				<text class="menu-arrow">›</text>
			</view>
			<view class="menu-item" v-if="userInfo.is_root" @click="handleGenerateContract">
				<text class="menu-text">生成合同</text>
				<text class="menu-arrow">›</text>
			</view>
			<view class="menu-item" v-if="userInfo.is_root" @click="handleInspirationImport">
				<text class="menu-text">灵感自动导入</text>
				<text class="menu-arrow">›</text>
			</view>
			<view class="menu-item" @click="handleEditProfile">
				<text class="menu-text">编辑个人信息</text>
				<text class="menu-arrow">›</text>
			</view>
			<view class="menu-item" @click="handleChangePassword">
				<text class="menu-text">修改密码</text>
				<text class="menu-arrow">›</text>
			</view>
			<view class="menu-item" @click="handleLogout">
				<text class="menu-text logout-text">退出登录</text>
				<text class="menu-arrow">›</text>
			</view>
		</view>
	</view>
</template>

<script setup>
import { reactive, onMounted } from 'vue'
import { getProfile, uploadAvatar } from '@/api/auth.js'
import config from '@/config.js'

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

const getAvatarUrl = (avatar) => {
	if (!avatar) {
		return '/static/default-avatar.png'
	}
	// 如果已经是完整URL，直接返回
	if (avatar.startsWith('http')) {
		return avatar
	}
	// 如果是相对路径，加上baseURL
	return `${config.baseURL}${avatar}`
}

const handleUploadAvatar = () => {
	uni.chooseImage({
		count: 1,
		sizeType: ['compressed'],
		sourceType: ['album', 'camera'],
		success: (res) => {
			const tempFilePath = res.tempFilePaths[0]
			
			uni.showLoading({ title: '上传中...' })
			
			uni.uploadFile({
				url: `${config.baseURL}/api/auth/avatar`,
				filePath: tempFilePath,
				name: 'file',
				header: {
					'Authorization': `Bearer ${uni.getStorageSync('token')}`
				},
				success: (uploadRes) => {
					const data = JSON.parse(uploadRes.data)
					if (data.avatar_url) {
						userInfo.avatar = data.avatar_url
						uni.showToast({
							title: '上传成功',
							icon: 'success'
						})
					}
				},
				fail: (error) => {
					console.error('上传失败:', error)
					uni.showToast({
						title: '上传失败',
						icon: 'none'
					})
				},
				complete: () => {
					uni.hideLoading()
				}
			})
		}
	})
}

const handleEditProfile = () => {
	uni.navigateTo({
		url: '/pages/mine/edit'
	})
}

const handleChangePassword = () => {
	uni.navigateTo({
		url: '/pages/mine/change-password'
	})
}

const handleManageUsers = () => {
	uni.navigateTo({
		url: '/pages/admin/users'
	})
}

const handleProjectApproval = () => {
	uni.navigateTo({
		url: '/pages/admin/project-approval'
	})
}

const handleAIConfig = () => {
	uni.navigateTo({
		url: '/pages/admin/ai-config'
	})
}

const handleGenerateContract = () => {
	uni.navigateTo({
		url: '/pages/contracts/generate'
	})
}

const handleInspirationImport = () => {
	uni.navigateTo({
		url: '/pages/admin/inspiration-import'
	})
}

const handleOAuthConfig = () => {
	uni.navigateTo({
		url: '/pages/admin/oauth-config'
	})
}

const handleAIOAuthConfig = () => {
	uni.navigateTo({
		url: '/pages/admin/ai-oauth-config'
	})
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

.avatar-wrapper {
	position: relative;
	width: 120rpx;
	height: 120rpx;
}

.avatar {
	width: 120rpx;
	height: 120rpx;
	border-radius: 60rpx;
	border: 4rpx solid rgba(255, 255, 255, 0.3);
}

.avatar-mask {
	position: absolute;
	top: 0;
	left: 0;
	width: 120rpx;
	height: 120rpx;
	border-radius: 60rpx;
	background: rgba(0, 0, 0, 0.5);
	display: flex;
	align-items: center;
	justify-content: center;
	opacity: 0;
	transition: opacity 0.3s;
}

.avatar-wrapper:active .avatar-mask {
	opacity: 1;
}

.upload-text {
	font-size: 20rpx;
	color: #FFFFFF;
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
	margin-bottom: 20rpx;
}

.menu-item:last-child {
	margin-bottom: 0;
}

.menu-text {
	font-size: 28rpx;
	color: #333333;
}

.logout-text {
	color: #FF6B6B;
}

.menu-arrow {
	font-size: 40rpx;
	color: #CCCCCC;
}
</style>

