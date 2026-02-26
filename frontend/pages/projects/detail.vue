<template>
	<view class="container">
		<scroll-view class="content" scroll-y v-if="project.id">
			<view class="project-header">
				<text class="project-name">{{ project.name }}</text>
				<view class="header-badges">
					<view class="status-selector" @click="canEdit ? showStatusPicker = true : null">
						<view class="status-badge" :class="'status-' + project.status">
							{{ project.status }} {{ canEdit ? '▼' : '' }}
						</view>
					</view>
					<view class="approval-badge" :class="'approval-' + project.approval_status" v-if="project.approval_status">
						{{ getApprovalText(project.approval_status) }}
					</view>
				</view>
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
			
			<!-- 快捷入口 -->
			<view class="quick-actions">
				<view class="action-btn" @click="goToDocuments">
					<text class="action-icon">📄</text>
					<text class="action-text">项目资料</text>
				</view>
				<view class="action-btn" @click="goToQuotation">
					<text class="action-icon">💰</text>
					<text class="action-text">报价数据</text>
				</view>
			</view>
			
			<view class="images-section" v-if="project.images && project.images.length > 0">
				<view class="section-title">项目图片</view>
				<swiper class="image-swiper" :indicator-dots="true" :autoplay="false" circular>
					<swiper-item v-for="img in project.images" :key="img.id">
						<image 
							:src="baseURL + img.image_url"
							mode="aspectFit"
							class="swiper-image"
							@click="previewImage(img.image_url)"
						/>
					</swiper-item>
				</swiper>
			</view>
			
			<!-- 权限管理（仅root用户可见） -->
			<view class="permissions-section" v-if="isRoot">
				<view class="section-title">项目权限管理</view>
				<view class="permission-card">
					<view class="permission-item" v-for="perm in permissions" :key="perm.id">
						<text class="user-name">{{ perm.user_name }}</text>
						<text class="permission-text">{{ perm.can_edit ? '可编辑' : '只读' }}</text>
						<button class="remove-btn" @click="removePermission(perm.id)">移除</button>
					</view>
					<button class="add-permission-btn" @click="showAddPermission = true">添加用户</button>
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
		
		<!-- 状态选择弹窗 -->
		<view class="modal-mask" v-if="showStatusPicker" @click="showStatusPicker = false">
			<view class="status-modal" @click.stop>
				<view class="status-modal-header">
					<text class="status-modal-title">选择项目状态</text>
				</view>
				<view class="status-options">
					<view 
						v-for="(status, index) in statusOptions" 
						:key="index"
						class="status-option"
						:class="{ 'selected': project.status === status }"
						@click="selectStatus(status)"
					>
						<text class="status-option-text">{{ status }}</text>
						<text v-if="project.status === status" class="check-icon">✓</text>
					</view>
				</view>
			</view>
		</view>
	</view>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { getProjectDetail, deleteProject, uploadProjectImage, updateProject } from '@/api/project.js'
import request from '@/utils/request.js'
import config from '@/config.js'

const baseURL = config.baseURL
const project = ref({})
const projectId = ref(0)
const isRoot = ref(false)
const permissions = ref([])
const showAddPermission = ref(false)
const showStatusPicker = ref(false)
const canEdit = ref(false)

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
		
		// 检查是否为root用户
		const userInfo = uni.getStorageSync('userInfo')
		isRoot.value = userInfo?.is_root || false
		
		// 判断是否可以编辑：项目创建者或root用户
		canEdit.value = isRoot.value || project.value.user_id === userInfo?.id
		
		// 如果是root用户，加载权限列表
		if (isRoot.value) {
			loadPermissions()
		}
		
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

const loadPermissions = async () => {
	try {
		const res = await request.get(`/api/permissions/project/${projectId.value}`)
		permissions.value = res
	} catch (error) {
		console.error('获取权限列表失败:', error)
	}
}

const removePermission = async (permId) => {
	try {
		await request.delete(`/api/permissions/${permId}`)
		uni.showToast({
			title: '移除成功',
			icon: 'success'
		})
		loadPermissions()
	} catch (error) {
		console.error('移除权限失败:', error)
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

const selectStatus = async (newStatus) => {
	showStatusPicker.value = false
	
	if (newStatus === project.value.status) {
		return
	}
	
	// 如果是root用户，通过状态变更API直接修改（会自动处理）
	if (isRoot.value) {
		try {
			uni.showLoading({ title: '更新中...' })
			const res = await request.post(`/api/projects/${projectId.value}/request-status-change?new_status=${newStatus}`)
			project.value.status = newStatus
			uni.hideLoading()
			uni.showToast({
				title: res.message || '状态已更新',
				icon: 'success'
			})
			loadDetail()
		} catch (error) {
			uni.hideLoading()
			uni.showToast({
				title: '更新失败',
				icon: 'none'
			})
			console.error('更新状态失败:', error)
		}
	} else {
		// 项目创建者需要申请状态变更
		uni.showModal({
			title: '申请状态变更',
			content: `确定要将项目状态从"${project.value.status}"变更为"${newStatus}"吗？需要管理员审批。`,
			success: async (res) => {
				if (res.confirm) {
					try {
						uni.showLoading({ title: '提交中...' })
						const result = await request.post(`/api/projects/${projectId.value}/request-status-change?new_status=${newStatus}`)
						uni.hideLoading()
						uni.showToast({
							title: result.message || '申请已提交，等待审批',
							icon: 'success'
						})
					} catch (error) {
						uni.hideLoading()
						uni.showToast({
							title: '申请失败',
							icon: 'none'
						})
						console.error('申请状态变更失败:', error)
					}
				}
			}
		})
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

const goToDocuments = () => {
	uni.navigateTo({
		url: `/pages/projects/documents?id=${projectId.value}`
	})
}

const goToQuotation = () => {
	uni.navigateTo({
		url: `/pages/projects/documents?id=${projectId.value}`
	})
}

const getApprovalText = (status) => {
	const map = {
		'pending': '待审批',
		'approved': '已批准',
		'rejected': '已拒绝'
	}
	return map[status] || status
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

.header-badges {
	display: flex;
	gap: 10rpx;
	align-items: center;
}

.status-badge, .approval-badge {
	padding: 10rpx 20rpx;
	border-radius: 8rpx;
	font-size: 24rpx;
	white-space: nowrap;
}

.status-badge {
	cursor: pointer;
	user-select: none;
}

.approval-pending {
	background: #FFF3E0;
	color: #FF9800;
}

.approval-approved {
	background: #E8F5E9;
	color: #4CAF50;
}

.approval-rejected {
	background: #FFEBEE;
	color: #F44336;
}

/* 确保picker下拉选项可见 */
picker {
	display: inline-block;
}

picker ::v-deep .uni-picker-container {
	background: white !important;
}

picker ::v-deep .uni-picker-item {
	color: #333 !important;
	font-size: 28rpx !important;
	line-height: 80rpx !important;
	text-align: center !important;
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

.image-swiper {
	width: 100%;
	height: 500rpx;
	border-radius: 16rpx;
	overflow: hidden;
	background: #FFFFFF;
}

.swiper-image {
	width: 100%;
	height: 100%;
}

.permissions-section {
	margin-bottom: 30rpx;
}

.permission-card {
	background: #FFFFFF;
	border-radius: 16rpx;
	padding: 30rpx;
}

.permission-item {
	display: flex;
	justify-content: space-between;
	align-items: center;
	padding: 20rpx 0;
	border-bottom: 1rpx solid #F0F0F0;
}

.permission-item:last-child {
	border-bottom: none;
}

.user-name {
	font-size: 28rpx;
	color: #333333;
	flex: 1;
}

.permission-text {
	font-size: 24rpx;
	color: #999999;
	margin-right: 20rpx;
}

.remove-btn {
	padding: 10rpx 20rpx;
	background: #FF6B6B;
	color: #FFFFFF;
	border-radius: 8rpx;
	font-size: 24rpx;
	border: none;
}

.add-permission-btn {
	width: 100%;
	height: 80rpx;
	background: #667eea;
	color: #FFFFFF;
	border-radius: 12rpx;
	font-size: 28rpx;
	border: none;
	margin-top: 20rpx;
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

.quick-actions {
	display: flex;
	gap: 20rpx;
	margin-bottom: 30rpx;
}

.action-btn {
	flex: 1;
	background: #FFFFFF;
	border-radius: 16rpx;
	padding: 30rpx;
	display: flex;
	flex-direction: column;
	align-items: center;
	justify-content: center;
	box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.08);
}

.action-icon {
	font-size: 48rpx;
	margin-bottom: 15rpx;
}

.action-text {
	font-size: 28rpx;
	color: #333333;
	font-weight: 500;
}

.modal-mask {
	position: fixed;
	top: 0;
	left: 0;
	right: 0;
	bottom: 0;
	background: rgba(0, 0, 0, 0.5);
	display: flex;
	align-items: center;
	justify-content: center;
	z-index: 9999;
}

.status-modal {
	width: 500rpx;
	background: white;
	border-radius: 16rpx;
	overflow: hidden;
}

.status-modal-header {
	padding: 30rpx;
	border-bottom: 1rpx solid #f0f0f0;
}

.status-modal-title {
	font-size: 32rpx;
	font-weight: bold;
	color: #333;
}

.status-options {
	padding: 20rpx 0;
}

.status-option {
	display: flex;
	justify-content: space-between;
	align-items: center;
	padding: 25rpx 30rpx;
	border-bottom: 1rpx solid #f5f5f5;
}

.status-option:last-child {
	border-bottom: none;
}

.status-option.selected {
	background: #f0f7ff;
}

.status-option-text {
	font-size: 28rpx;
	color: #333;
}

.check-icon {
	font-size: 32rpx;
	color: #3b82f6;
	font-weight: bold;
}
</style>
