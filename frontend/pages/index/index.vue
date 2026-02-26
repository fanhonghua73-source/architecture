<template>
	<view class="container">
		<view class="header">
			<view class="user-info">
				<image class="avatar" :src="getAvatarUrl(userInfo.avatar)" mode="aspectFill"></image>
				<view class="info">
					<text class="name">{{ userInfo.username || '建筑师' }}</text>
					<text class="company">{{ userInfo.company || '暂无公司信息' }}</text>
				</view>
			</view>
		</view>
		
		<view class="stats">
			<view class="stat-item">
				<text class="stat-value">{{ stats.projects }}</text>
				<text class="stat-label">项目</text>
			</view>
			<view class="stat-item">
				<text class="stat-value">{{ stats.inspirations }}</text>
				<text class="stat-label">灵感</text>
			</view>
			<view class="stat-item">
				<text class="stat-value">{{ stats.materials }}</text>
				<text class="stat-label">材料</text>
			</view>
		</view>
		
		<!-- 灵感轮播 -->
		<view class="inspiration-carousel">
			<swiper 
				class="swiper" 
				:indicator-dots="true" 
				:autoplay="true" 
				:interval="3000" 
				:duration="500"
				circular
			>
				<swiper-item v-for="inspiration in carouselInspirations" :key="inspiration.id">
					<view class="carousel-item" @click="viewInspiration(inspiration.id)">
						<image class="carousel-image" :src="inspiration.image_url" mode="aspectFill"></image>
						<view class="carousel-info">
							<text class="carousel-title">{{ inspiration.title }}</text>
							<text class="carousel-category">{{ inspiration.category }}</text>
						</view>
					</view>
				</swiper-item>
			</swiper>
		</view>
		
		<view class="quick-actions">
			<text class="section-title">快速操作</text>
			<view class="action-grid">
				<view class="action-item" @click="navigateTo('/pages/ai-image/generate')">
					<view class="action-icon" style="background: #FF6B6B;">
						<text class="icon">🎨</text>
					</view>
					<text class="action-text">AI生图</text>
				</view>
				<view class="action-item" v-if="userInfo.is_root" @click="navigateTo('/pages/contracts/generate')">
					<view class="action-icon" style="background: #FFA500;">
						<text class="icon">📄</text>
					</view>
					<text class="action-text">生成合同</text>
				</view>
				<view class="action-item" @click="navigateTo('/pages/projects/add')">
					<view class="action-icon" style="background: #667eea;">
						<text class="icon">+</text>
					</view>
					<text class="action-text">新建项目</text>
				</view>
				<view class="action-item" @click="navigateTo('/pages/inspirations/add')">
					<view class="action-icon" style="background: #f093fb;">
						<text class="icon">📷</text>
					</view>
					<text class="action-text">添加灵感</text>
				</view>
				<view class="action-item" @click="navigateTo('/pages/projects/projects')">
					<view class="action-icon" style="background: #4facfe;">
						<text class="icon">📊</text>
					</view>
					<text class="action-text">项目管理</text>
				</view>
			</view>
		</view>
		
		<view class="recent-projects">
			<view class="section-header">
				<text class="section-title">最近项目</text>
				<text class="more" @click="navigateTo('/pages/projects/projects')">查看全部</text>
			</view>
			<view class="project-list">
				<view 
					v-for="project in recentProjects" 
					:key="project.id"
					class="project-card"
					@click="navigateTo('/pages/projects/detail?id=' + project.id)"
				>
					<view class="project-info">
						<text class="project-name">{{ project.name }}</text>
						<text class="project-address">{{ project.address }}</text>
					</view>
					<view class="project-status" :class="'status-' + project.status">
						{{ project.status }}
					</view>
				</view>
			</view>
		</view>
	</view>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { getProfile } from '@/api/auth.js'
import { getProjects } from '@/api/project.js'
import { getInspirations } from '@/api/inspiration.js'
import { getMaterials } from '@/api/material.js'
import config from '@/config.js'

const userInfo = reactive({
	username: '',
	company: '',
	avatar: '',
	is_root: false
})

const stats = reactive({
	projects: 0,
	inspirations: 0,
	materials: 0
})

const recentProjects = ref([])
const carouselInspirations = ref([])

const navigateTo = (url) => {
	if (url.includes('pages/projects/projects') || url.includes('pages/materials/materials')) {
		uni.switchTab({ url })
	} else {
		uni.navigateTo({ url })
	}
}

const loadUserInfo = async () => {
	try {
		const res = await getProfile()
		Object.assign(userInfo, res)
	} catch (error) {
		console.error('获取用户信息失败:', error)
	}
}

const loadStats = async () => {
	try {
		const [projects, inspirations, materials] = await Promise.all([
			getProjects({ limit: 100 }),
			getInspirations({ limit: 100 }),
			getMaterials({ limit: 100 })
		])
		
		stats.projects = projects.length
		stats.inspirations = inspirations.length
		stats.materials = materials.length
	} catch (error) {
		console.error('获取统计数据失败:', error)
	}
}

const loadRecentProjects = async () => {
	try {
		const res = await getProjects({ limit: 5 })
		recentProjects.value = res
	} catch (error) {
		console.error('获取最近项目失败:', error)
	}
}

const loadCarouselInspirations = async () => {
	try {
		const res = await getInspirations({ limit: 5 })
		carouselInspirations.value = res
	} catch (error) {
		console.error('获取轮播灵感失败:', error)
	}
}

const viewInspiration = (id) => {
	uni.navigateTo({
		url: `/pages/inspirations/detail?id=${id}`
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
	loadUserInfo()
	loadStats()
	loadRecentProjects()
	loadCarouselInspirations()
})
</script>

<style scoped>
.container {
	min-height: 100vh;
	background: #F5F7FA;
	padding-bottom: 20rpx;
}

.inspiration-carousel {
	margin: 30rpx;
	border-radius: 20rpx;
	overflow: hidden;
	box-shadow: 0 10rpx 30rpx rgba(0, 0, 0, 0.1);
}

.swiper {
	height: 400rpx;
}

.carousel-item {
	position: relative;
	width: 100%;
	height: 100%;
}

.carousel-image {
	width: 100%;
	height: 100%;
}

.carousel-info {
	position: absolute;
	bottom: 0;
	left: 0;
	right: 0;
	background: linear-gradient(to top, rgba(0, 0, 0, 0.7), transparent);
	padding: 40rpx 30rpx 30rpx;
}

.carousel-title {
	display: block;
	font-size: 32rpx;
	font-weight: bold;
	color: #FFFFFF;
	margin-bottom: 10rpx;
}

.carousel-category {
	display: block;
	font-size: 24rpx;
	color: rgba(255, 255, 255, 0.8);
}

.header {
	background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
	padding: 60rpx 40rpx 40rpx;
}

.user-info {
	display: flex;
	align-items: center;
}

.avatar {
	width: 120rpx;
	height: 120rpx;
	border-radius: 60rpx;
	border: 4rpx solid rgba(255, 255, 255, 0.3);
}

.info {
	margin-left: 30rpx;
	flex: 1;
}

.name {
	display: block;
	font-size: 36rpx;
	font-weight: bold;
	color: #FFFFFF;
	margin-bottom: 10rpx;
}

.company {
	display: block;
	font-size: 26rpx;
	color: rgba(255, 255, 255, 0.8);
}

.stats {
	display: flex;
	background: #FFFFFF;
	margin: -40rpx 30rpx 30rpx;
	border-radius: 20rpx;
	padding: 40rpx 0;
	box-shadow: 0 10rpx 30rpx rgba(0, 0, 0, 0.05);
}

.stat-item {
	flex: 1;
	text-align: center;
	border-right: 1rpx solid #F0F0F0;
}

.stat-item:last-child {
	border-right: none;
}

.stat-value {
	display: block;
	font-size: 48rpx;
	font-weight: bold;
	color: #667eea;
	margin-bottom: 10rpx;
}

.stat-label {
	display: block;
	font-size: 26rpx;
	color: #999999;
}

.quick-actions {
	padding: 0 30rpx;
	margin-bottom: 30rpx;
}

.section-title {
	display: block;
	font-size: 32rpx;
	font-weight: bold;
	color: #333333;
	margin-bottom: 30rpx;
}

.action-grid {
	display: grid;
	grid-template-columns: repeat(5, 1fr);
	gap: 20rpx;
}

.action-item {
	display: flex;
	flex-direction: column;
	align-items: center;
}

.action-icon {
	width: 100rpx;
	height: 100rpx;
	border-radius: 20rpx;
	display: flex;
	align-items: center;
	justify-content: center;
	margin-bottom: 15rpx;
}

.icon {
	font-size: 40rpx;
	color: #FFFFFF;
}

.action-text {
	font-size: 24rpx;
	color: #666666;
}

.recent-projects {
	padding: 0 30rpx;
}

.section-header {
	display: flex;
	justify-content: space-between;
	align-items: center;
	margin-bottom: 30rpx;
}

.more {
	font-size: 26rpx;
	color: #667eea;
}

.project-list {
	display: flex;
	flex-direction: column;
	gap: 20rpx;
}

.project-card {
	background: #FFFFFF;
	border-radius: 16rpx;
	padding: 30rpx;
	display: flex;
	justify-content: space-between;
	align-items: center;
}

.project-info {
	flex: 1;
}

.project-name {
	display: block;
	font-size: 30rpx;
	font-weight: bold;
	color: #333333;
	margin-bottom: 10rpx;
}

.project-address {
	display: block;
	font-size: 24rpx;
	color: #999999;
}

.project-status {
	padding: 10rpx 20rpx;
	border-radius: 8rpx;
	font-size: 24rpx;
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
</style>

