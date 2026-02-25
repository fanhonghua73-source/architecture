<template>
	<view class="container">
		<scroll-view class="content" scroll-y v-if="project.id">
			<view class="project-header">
				<text class="project-name">{{ project.name }}</text>
				<picker :value="statusIndex" :range="statusOptions" @change="onStatusChange">
					<view class="status-badge" :class="'status-' + project.status">
						{{ project.status }} ▼
					</view>
				</picker>
			</view>
			
			<view class="info-card">
				<view class="info-item">
					<text class="label">项目地址</text>
					<text class="value">{{ project.address || '暂无' }}</text>
				</view>
				<view class="info-item">
					<text class="label">建筑面积</text>
					<text class="value">{{ project.area ? project.area + '㎡' : '暂无' }}</text>
				</view>
				<view class="info-item">
					<text class="label">项目预算</text>
					<text class="value">{{ project.budget ? '¥' + project.budget : '暂无' }}</text>
				</view>
				<view class="info-item" v-if="project.description">
					<text class="label">项目描述</text>
					<text class="value">{{ project.description }}</text>
				</view>
			</view>
			
			<view class="images-section" v-if="project.images && project.images.length > 0">
				<view class="section-title">项目图片</view>
				<view class="image-grid">
					<image 
						v-for="img in project.images" 
						:key="img.id"
						:src="baseURL + img.image_url"
						mode="aspectFill"
						class="project-image"
						@click="previewImage(img.image_url)"
					/>
				</view>
			</view>
			
			<view class="upload-section">
				<button class="upload-btn" @click="uploadImage">上传图片</button>
			</view>
		</scroll-view>
		
		<view class="loading" v-else>
			<text>加载中...</text>
		</view>
		
		<view class="footer" v-if="project.id">
			<button class="delete-btn" @click="handleDelete">删除项目</button>
		</view>
	</view>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { getProjectDetail, deleteProject, uploadProjectImage, updateProject } from '@/api/project.js'
import config from '@/config.js'

const baseURL = config.baseURL
const project = ref({})
const projectId = ref(0)

const statusOptions = ['进行中', '已完成', '暂停']
const statusIndex = computed(() => {
	return statusOptions.indexOf(project.value.status || '进行中')
})

// 获取URL参数
onMounted(() => {
	const pages = getCurrentPages()
	const currentPage = pages[pages.length - 1]
	projectId.value = currentPage.options.id
	
	if (projectId.value) {
		loadDetail()
	}
})

const loadDetail = async () => {
	try {
		uni.showLoading({ title: '加载中...', mask: true })
		const res = await getProjectDetail(projectId.value)
		project.value = res
		uni.hideLoading()
	} catch (error) {
		uni.hideLoading()
		uni.showToast({
			title: '加载失败',
			icon: 'none'
		})
		console.error('获取项目详情失败:', error)
		setTimeout(() => {
			uni.navigateBack()
		}, 1500)
	}
}

const onStatusChange = async (e) => {
	const newStatus = statusOptions[e.detail.value]
	
	try {
		uni.showLoading({ title: '更新中...' })
		await updateProject(projectId.value, {
			...project.value,
			status: newStatus
		})
		project.value.status = newStatus
		uni.hideLoading()
		uni.showToast({
			title: '状态已更新',
			icon: 'success'
		})
	} catch (error) {
		uni.hideLoading()
		uni.showToast({
			title: '更新失败',
			icon: 'none'
		})
		console.error('更新状态失败:', error)
	}
}

const uploadImage = () => {
	uni.chooseImage({
		count: 1,
		sizeType: ['compressed'],
		sourceType: ['album', 'camera'],
		success: async (res) => {
			try {
				uni.showLoading({ title: '上传中...' })
				await uploadProjectImage(projectId.value, res.tempFilePaths[0])
				uni.hideLoading()
				uni.showToast({
					title: '上传成功',
					icon: 'success'
				})
				loadDetail()
			} catch (error) {
				uni.hideLoading()
				console.error('上传失败:', error)
			}
		}
	})
}

const previewImage = (url) => {
	const urls = project.value.images.map(img => baseURL + img.image_url)
	const current = baseURL + url
	uni.previewImage({
		urls,
		current
	})
}

const handleDelete = () => {
	uni.showModal({
		title: '提示',
		content: '确定要删除这个项目吗？',
		success: async (res) => {
			if (res.confirm) {
				try {
					await deleteProject(projectId.value)
					uni.showToast({
						title: '删除成功',
						icon: 'success'
					})
					setTimeout(() => {
						uni.navigateBack()
					}, 1000)
				} catch (error) {
					console.error('删除失败:', error)
				}
			}
		}
	})
}
</script>

<style scoped>
.container {
	height: 100vh;
	display: flex;
	flex-direction: column;
	background: #F5F7FA;
}

.content {
	flex: 1;
	padding: 30rpx;
}

.loading {
	flex: 1;
	display: flex;
	align-items: center;
	justify-content: center;
	font-size: 28rpx;
	color: #999999;
}

.project-header {
	display: flex;
	justify-content: space-between;
	align-items: center;
	margin-bottom: 30rpx;
}

.project-name {
	font-size: 40rpx;
	font-weight: bold;
	color: #333333;
	flex: 1;
}

.status-badge {
	padding: 10rpx 20rpx;
	border-radius: 8rpx;
	font-size: 24rpx;
	cursor: pointer;
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

.info-card {
	background: #FFFFFF;
	border-radius: 16rpx;
	padding: 30rpx;
	margin-bottom: 30rpx;
}

.info-item {
	margin-bottom: 25rpx;
}

.info-item:last-child {
	margin-bottom: 0;
}

.label {
	display: block;
	font-size: 26rpx;
	color: #999999;
	margin-bottom: 10rpx;
}

.value {
	display: block;
	font-size: 28rpx;
	color: #333333;
	line-height: 1.6;
}

.images-section {
	margin-bottom: 30rpx;
}

.section-title {
	font-size: 32rpx;
	font-weight: bold;
	color: #333333;
	margin-bottom: 20rpx;
}

.image-grid {
	display: grid;
	grid-template-columns: repeat(3, 1fr);
	gap: 15rpx;
}

.project-image {
	width: 100%;
	height: 200rpx;
	border-radius: 12rpx;
}

.upload-section {
	margin-bottom: 30rpx;
}

.upload-btn {
	width: 100%;
	height: 88rpx;
	background: #FFFFFF;
	color: #667eea;
	border: 2rpx solid #667eea;
	border-radius: 12rpx;
	font-size: 28rpx;
}

.footer {
	background: #FFFFFF;
	padding: 20rpx 30rpx;
	border-top: 1rpx solid #F0F0F0;
}

.delete-btn {
	width: 100%;
	height: 88rpx;
	background: #FF6B6B;
	color: #FFFFFF;
	border-radius: 12rpx;
	font-size: 32rpx;
	border: none;
}
</style>
