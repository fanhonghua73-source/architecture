<template>
	<view class="container">
		<view class="header">
			<text class="title">项目审批</text>
			<text class="subtitle">待审批项目：{{ pendingProjects.length }}个</text>
		</view>
		
		<view class="project-list">
			<view class="project-item" v-for="project in pendingProjects" :key="project.id">
				<view class="project-info">
					<text class="project-name">{{ project.name }}</text>
					<text class="project-detail">地址：{{ project.address || '未填写' }}</text>
					<text class="project-detail">面积：{{ project.area || '未填写' }}㎡</text>
					<text class="project-detail">预算：¥{{ project.budget || '未填写' }}</text>
					<text class="project-detail">创建时间：{{ formatDate(project.created_at) }}</text>
				</view>
				<view class="project-actions">
					<button class="btn-approve" @click="approveProject(project.id, true)">批准</button>
					<button class="btn-reject" @click="approveProject(project.id, false)">拒绝</button>
					<button class="btn-detail" @click="viewDetail(project.id)">查看详情</button>
				</view>
			</view>
			
			<view class="empty" v-if="pendingProjects.length === 0">
				<text class="empty-text">暂无待审批项目</text>
			</view>
		</view>
	</view>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import request from '@/utils/request.js'

const pendingProjects = ref([])

const loadPendingProjects = async () => {
	try {
		uni.showLoading({ title: '加载中...' })
		const res = await request.get('/api/projects/pending/list')
		pendingProjects.value = res
		uni.hideLoading()
	} catch (error) {
		uni.hideLoading()
		uni.showToast({
			title: '加载失败',
			icon: 'none'
		})
		console.error('获取待审批项目失败:', error)
	}
}

const approveProject = async (projectId, approved) => {
	const action = approved ? '批准' : '拒绝'
	
	uni.showModal({
		title: '确认',
		content: `确定要${action}这个项目吗？`,
		success: async (res) => {
			if (res.confirm) {
				try {
					uni.showLoading({ title: '处理中...' })
					await request.post(`/api/projects/${projectId}/approve?approved=${approved}`)
					uni.hideLoading()
					uni.showToast({
						title: `${action}成功`,
						icon: 'success'
					})
					loadPendingProjects()
				} catch (error) {
					uni.hideLoading()
					uni.showToast({
						title: `${action}失败`,
						icon: 'none'
					})
					console.error('审批失败:', error)
				}
			}
		}
	})
}

const viewDetail = (projectId) => {
	uni.navigateTo({
		url: `/pages/projects/detail?id=${projectId}`
	})
}

const formatDate = (dateStr) => {
	if (!dateStr) return ''
	const date = new Date(dateStr)
	return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
}

onMounted(() => {
	loadPendingProjects()
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
	display: block;
	margin-bottom: 10rpx;
}

.subtitle {
	font-size: 26rpx;
	color: #666666;
}

.project-list {
	display: flex;
	flex-direction: column;
	gap: 20rpx;
}

.project-item {
	background: #FFFFFF;
	border-radius: 16rpx;
	padding: 30rpx;
}

.project-info {
	margin-bottom: 20rpx;
}

.project-name {
	font-size: 32rpx;
	font-weight: bold;
	color: #333333;
	display: block;
	margin-bottom: 15rpx;
}

.project-detail {
	font-size: 26rpx;
	color: #666666;
	display: block;
	margin-bottom: 8rpx;
}

.project-actions {
	display: flex;
	gap: 15rpx;
}

.btn-approve, .btn-reject, .btn-detail {
	flex: 1;
	height: 70rpx;
	border-radius: 8rpx;
	font-size: 28rpx;
	border: none;
}

.btn-approve {
	background: #10b981;
	color: white;
}

.btn-reject {
	background: #ef4444;
	color: white;
}

.btn-detail {
	background: #3b82f6;
	color: white;
}

.empty {
	padding: 100rpx 0;
	text-align: center;
}

.empty-text {
	font-size: 28rpx;
	color: #999999;
}
</style>

