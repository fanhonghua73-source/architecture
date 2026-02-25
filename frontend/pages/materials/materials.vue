<template>
	<view class="container">
		<view class="header">
			<input 
				v-model="searchKeyword" 
				placeholder="搜索材料" 
				class="search-input"
				@confirm="loadMaterials"
			/>
		</view>
		
		<scroll-view class="material-list" scroll-y>
			<view 
				v-for="item in materials" 
				:key="item.id"
				class="material-card"
			>
				<image 
					v-if="item.image_url"
					:src="baseURL + item.image_url" 
					mode="aspectFill"
					class="material-image"
				/>
				<view class="material-info">
					<text class="material-name">{{ item.name }}</text>
					<text class="material-spec" v-if="item.specification">
						规格：{{ item.specification }}
					</text>
					<view class="material-footer">
						<text class="price" v-if="item.price">
							¥{{ item.price }}/{{ item.unit || '件' }}
						</text>
						<text class="category" v-if="item.category">
							{{ item.category }}
						</text>
					</view>
				</view>
			</view>
			
			<view v-if="materials.length === 0" class="empty">
				<text class="empty-text">暂无材料</text>
			</view>
		</scroll-view>
	</view>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getMaterials } from '@/api/material.js'
import config from '@/config.js'

const baseURL = config.baseURL
const searchKeyword = ref('')
const materials = ref([])

const loadMaterials = async () => {
	try {
		uni.showLoading({ title: '加载中...' })
		const res = await getMaterials()
		materials.value = res
		uni.hideLoading()
	} catch (error) {
		uni.hideLoading()
		console.error('获取材料列表失败:', error)
	}
}

onMounted(() => {
	loadMaterials()
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
	border-bottom: 1rpx solid #F0F0F0;
}

.search-input {
	width: 100%;
	height: 70rpx;
	background: #F5F7FA;
	border-radius: 35rpx;
	padding: 0 30rpx;
	font-size: 28rpx;
}

.material-list {
	flex: 1;
	padding: 20rpx 30rpx;
}

.material-card {
	background: #FFFFFF;
	border-radius: 16rpx;
	padding: 20rpx;
	margin-bottom: 20rpx;
	display: flex;
	gap: 20rpx;
	box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.05);
}

.material-image {
	width: 160rpx;
	height: 160rpx;
	border-radius: 12rpx;
	flex-shrink: 0;
}

.material-info {
	flex: 1;
	display: flex;
	flex-direction: column;
	justify-content: space-between;
}

.material-name {
	font-size: 30rpx;
	font-weight: bold;
	color: #333333;
	margin-bottom: 10rpx;
}

.material-spec {
	font-size: 24rpx;
	color: #999999;
	margin-bottom: 10rpx;
}

.material-footer {
	display: flex;
	justify-content: space-between;
	align-items: center;
}

.price {
	font-size: 28rpx;
	color: #FF6B6B;
	font-weight: bold;
}

.category {
	padding: 6rpx 12rpx;
	background: #F0F0F0;
	border-radius: 6rpx;
	font-size: 22rpx;
	color: #666666;
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
}
</style>

