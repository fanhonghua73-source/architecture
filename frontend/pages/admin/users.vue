<template>
	<view class="container">
		<view class="header">
			<text class="title">用户管理</text>
		</view>
		
		<view class="user-list">
			<view class="user-item" v-for="user in users" :key="user.id">
				<view class="user-info">
					<image class="avatar" :src="getAvatarUrl(user.avatar)" mode="aspectFill"></image>
					<view class="info">
						<text class="username">{{ user.username }}</text>
						<text class="email">{{ user.email }}</text>
						<text class="status" :class="user.is_approved ? 'approved' : 'pending'">
							{{ user.is_approved ? '已审批' : '待审批' }}
						</text>
					</view>
				</view>
				
				<view class="actions">
					<button v-if="!user.is_approved" class="approve-btn" @click="approveUser(user.id)">审批</button>
					<button class="edit-btn" @click="editUser(user)">编辑</button>
				</view>
			</view>
		</view>
	</view>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import request from '@/utils/request.js'
import config from '@/config.js'

const users = ref([])

const loadUsers = async () => {
	try {
		const res = await request.get('/api/auth/users')
		users.value = res
	} catch (error) {
		console.error('获取用户列表失败:', error)
	}
}

const approveUser = async (userId) => {
	try {
		uni.showLoading({ title: '审批中...' })
		await request.put(`/api/auth/users/${userId}/approve`)
		uni.hideLoading()
		
		uni.showToast({
			title: '审批成功',
			icon: 'success'
		})
		
		loadUsers()
	} catch (error) {
		uni.hideLoading()
		console.error('审批失败:', error)
	}
}

const editUser = (user) => {
	uni.navigateTo({
		url: `/pages/admin/edit-user?userId=${user.id}`
	})
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

onMounted(() => {
	loadUsers()
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

.user-list {
	display: flex;
	flex-direction: column;
	gap: 20rpx;
}

.user-item {
	background: #FFFFFF;
	border-radius: 16rpx;
	padding: 30rpx;
	display: flex;
	justify-content: space-between;
	align-items: center;
}

.user-info {
	display: flex;
	align-items: center;
	flex: 1;
}

.avatar {
	width: 80rpx;
	height: 80rpx;
	border-radius: 40rpx;
	margin-right: 20rpx;
}

.info {
	display: flex;
	flex-direction: column;
	gap: 8rpx;
}

.username {
	font-size: 28rpx;
	font-weight: bold;
	color: #333333;
}

.email {
	font-size: 24rpx;
	color: #666666;
}

.status {
	font-size: 22rpx;
	padding: 4rpx 12rpx;
	border-radius: 8rpx;
	align-self: flex-start;
}

.status.approved {
	background: #E8F5E9;
	color: #4CAF50;
}

.status.pending {
	background: #FFF3E0;
	color: #FF9800;
}

.actions {
	display: flex;
	gap: 10rpx;
}

.approve-btn, .edit-btn {
	padding: 10rpx 20rpx;
	border-radius: 8rpx;
	font-size: 24rpx;
	border: none;
}

.approve-btn {
	background: #4CAF50;
	color: #FFFFFF;
}

.edit-btn {
	background: #2196F3;
	color: #FFFFFF;
}
</style>

