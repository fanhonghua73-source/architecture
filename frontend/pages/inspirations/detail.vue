<template>
	<view class="container">
		<scroll-view class="content" scroll-y>
			<image 
				:src="baseURL + inspiration.image_url" 
				mode="widthFix"
				class="main-image"
			/>
			
			<view class="info-section">
				<text class="title">{{ inspiration.title }}</text>
				
				<view class="meta">
					<view class="meta-item" v-if="inspiration.category">
						<text class="meta-label">分类：</text>
						<text class="meta-value">{{ inspiration.category }}</text>
					</view>
					<view class="meta-item" v-if="inspiration.style">
						<text class="meta-label">风格：</text>
						<text class="meta-value">{{ inspiration.style }}</text>
					</view>
				</view>
				
				<view class="tags" v-if="inspiration.tags">
					<text 
						v-for="(tag, index) in inspiration.tags.split(',')" 
						:key="index"
						class="tag"
					>
						{{ tag.trim() }}
					</text>
				</view>
				
				<view class="description" v-if="inspiration.description">
					<text class="desc-title">描述</text>
					<text class="desc-text">{{ inspiration.description }}</text>
				</view>
			</view>
		</scroll-view>
		
		<view class="footer">
			<button class="delete-btn" @click="handleDelete">删除</button>
		</view>
	</view>
</template>

<script setup>
import { ref, onLoad } from '@dcloudio/uni-app'
import { getInspirationDetail, deleteInspiration } from '@/api/inspiration.js'
import config from '@/config.js'

const baseURL = config.baseURL
const inspiration = ref({})
const inspirationId = ref(0)

onLoad((options) => {
	inspirationId.value = options.id
	loadDetail()
})

const loadDetail = async () => {
	try {
		uni.showLoading({ title: '加载中...' })
		const res = await getInspirationDetail(inspirationId.value)
		inspiration.value = res
		uni.hideLoading()
	} catch (error) {
		uni.hideLoading()
		console.error('获取灵感详情失败:', error)
	}
}

const handleDelete = () => {
	uni.showModal({
		title: '提示',
		content: '确定要删除这条灵感吗？',
		success: async (res) => {
			if (res.confirm) {
				try {
					await deleteInspiration(inspirationId.value)
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
}

.main-image {
	width: 100%;
	display: block;
}

.info-section {
	background: #FFFFFF;
	padding: 30rpx;
}

.title {
	display: block;
	font-size: 36rpx;
	font-weight: bold;
	color: #333333;
	margin-bottom: 20rpx;
}

.meta {
	display: flex;
	gap: 30rpx;
	margin-bottom: 20rpx;
}

.meta-item {
	display: flex;
	font-size: 26rpx;
}

.meta-label {
	color: #999999;
}

.meta-value {
	color: #666666;
}

.tags {
	display: flex;
	flex-wrap: wrap;
	gap: 10rpx;
	margin-bottom: 30rpx;
}

.tag {
	padding: 8rpx 16rpx;
	background: #F0F0F0;
	border-radius: 8rpx;
	font-size: 24rpx;
	color: #666666;
}

.description {
	padding-top: 30rpx;
	border-top: 1rpx solid #F0F0F0;
}

.desc-title {
	display: block;
	font-size: 28rpx;
	font-weight: bold;
	color: #333333;
	margin-bottom: 15rpx;
}

.desc-text {
	display: block;
	font-size: 26rpx;
	color: #666666;
	line-height: 1.6;
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

