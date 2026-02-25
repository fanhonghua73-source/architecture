<template>
	<view class="container">
		<view class="header">
			<view class="tabs">
				<view 
					v-for="item in statusTabs" 
					:key="item.value"
					class="tab-item"
					:class="{ active: currentStatus === item.value }"
					@click="changeStatus(item.value)"
				>
					{{ item.label }}
				</view>
			</view>
			<view class="add-btn" @click="navigateTo('/pages/projects/add')">
				<text class="add-icon">+</text>
			</view>
		</view>
		
		<scroll-view class="project-list" scroll-y>
			<view 
				v-for="project in projects" 
				:key="project.id"
				class="project-card"
				@click="navigateTo('/pages/projects/detail?id=' + project.id)"
			>
				<view class="card-header">
					<text class="project-name">{{ project.name }}</text>
					<view class="status-badge" :class="'status-' + project.status">
						{{ project.status }}
					</view>
				</view>
				
				<view class="project-info">
					<view class="info-item">
						<text class="label">地址：</text>
						<text class="value">{{ project.address || '暂无' }}</text>
					</view>
					<view class="info-item">
						<text class="label">面积：</text>
						<text class="value">{{ project.area ? project.area + '㎡' : '暂无' }}</text>
					</view>
					<view class="info-item">
						<text class="label">预算：</text>
						<text class="value">{{ project.budget ? '¥' + project.budget : '暂无' }}</text>
					</view>
				</view>
				
				<view class="project-desc" v-if="project.description">
					{{ project.description }}
				</view>
				
				<view class="card-footer">
					<text class="time">{{ formatTime(project.updated_at) }}</text>
				</view>
			</view>
			
			<view v-if="projects.length === 0" class="empty">
				<text class="empty-text">暂无项目</text>
				<text class="empty-tip">点击右上角添加项目</text>
			</view>
		</scroll-view>
	</view>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getProjects } from '@/api/project.js'

const statusTabs = [
	{ label: '全部', value: '' },
	{ label: '进行中', value: '进行中' },
	{ label: '已完成', value: '已完成' },
	{ label: '暂停', value: '暂停' }
]

const currentStatus = ref('')
const projects = ref([])

const navigateTo = (url) => {
	uni.navigateTo({ url })
}

const changeStatus = (status) => {
	currentStatus.value = status
	loadProjects()
}

const loadProjects = async () => {
	try {
		uni.showLoading({ title: '加载中...' })
		const params = currentStatus.value ? { status: currentStatus.value } : {}
		const res = await getProjects(params)
		projects.value = res
		uni.hideLoading()
	} catch (error) {
		uni.hideLoading()
		console.error('获取项目列表失败:', error)
	}
}

const formatTime = (time) => {
	if (!time) return ''
	const date = new Date(time)
	return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
}

onMounted(() => {
	loadProjects()
})
</script>

<style scoped>
.container {
	height: 100vh;
	display: flex;
	flex-direction: column;
	background: #F5F7FA;
}

.header {
	background: #FFFFFF;
	padding: 20rpx 30rpx;
	display: flex;
	justify-content: space-between;
	align-items: center;
	border-bottom: 1rpx solid #F0F0F0;
}

.tabs {
	display: flex;
	gap: 30rpx;
}

.tab-item {
	font-size: 28rpx;
	color: #666666;
	padding: 10rpx 0;
	position: relative;
}

.tab-item.active {
	color: #667eea;
	font-weight: bold;
}

.tab-item.active::after {
	content: '';
	position: absolute;
	bottom: 0;
	left: 0;
	right: 0;
	height: 4rpx;
	background: #667eea;
	border-radius: 2rpx;
}

.add-btn {
	width: 60rpx;
	height: 60rpx;
	background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
	border-radius: 30rpx;
	display: flex;
	align-items: center;
	justify-content: center;
}

.add-icon {
	font-size: 40rpx;
	color: #FFFFFF;
	line-height: 1;
}

.project-list {
	flex: 1;
	padding: 20rpx 30rpx;
}

.project-card {
	background: #FFFFFF;
	border-radius: 16rpx;
	padding: 30rpx;
	margin-bottom: 20rpx;
	box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.05);
}

.card-header {
	display: flex;
	justify-content: space-between;
	align-items: center;
	margin-bottom: 20rpx;
}

.project-name {
	font-size: 32rpx;
	font-weight: bold;
	color: #333333;
}

.status-badge {
	padding: 8rpx 16rpx;
	border-radius: 8rpx;
	font-size: 22rpx;
}

.status-进行中 {
	background: #E8F5E9;
	color: #4CAF50;
}

.status-已完成 {
	background: #E3F2FD;
	color: #2196F3;
}

.status-暂停 {
	background: #FFF3E0;
	color: #FF9800;
}

.project-info {
	margin-bottom: 20rpx;
}

.info-item {
	display: flex;
	font-size: 26rpx;
	margin-bottom: 10rpx;
}

.label {
	color: #999999;
	width: 120rpx;
}

.value {
	color: #666666;
	flex: 1;
}

.project-desc {
	font-size: 26rpx;
	color: #666666;
	line-height: 1.6;
	margin-bottom: 20rpx;
}

.card-footer {
	border-top: 1rpx solid #F0F0F0;
	padding-top: 20rpx;
}

.time {
	font-size: 24rpx;
	color: #999999;
}

.empty {
	display: flex;
	flex-direction: column;
	align-items: center;
	justify-content: center;
	padding: 200rpx 0;
}

.empty-text {
	font-size: 32rpx;
	color: #999999;
	margin-bottom: 20rpx;
}

.empty-tip {
	font-size: 26rpx;
	color: #CCCCCC;
}
</style>

