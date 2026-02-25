<template>
	<view class="container">
		<view class="header">
			<view class="filter-tabs">
				<view 
					v-for="item in categoryTabs" 
					:key="item.value"
					class="tab-item"
					:class="{ active: currentCategory === item.value }"
					@click="changeCategory(item.value)"
				>
					{{ item.label }}
				</view>
			</view>
			<view class="add-btn" @click="navigateTo('/pages/inspirations/add')">
				<text class="add-icon">+</text>
			</view>
		</view>
		
		<scroll-view class="inspiration-list" scroll-y>
			<view class="waterfall">
				<view 
					v-for="item in inspirations" 
					:key="item.id"
					class="inspiration-card"
					@click="navigateTo('/pages/inspirations/detail?id=' + item.id)"
				>
					<image 
						:src="baseURL + item.image_url" 
						mode="widthFix"
						class="inspiration-image"
					/>
					<view class="card-content">
						<text class="title">{{ item.title }}</text>
						<view class="tags" v-if="item.tags">
							<text 
								v-for="(tag, index) in item.tags.split(',')" 
								:key="index"
								class="tag"
							>
								{{ tag.trim() }}
							</text>
						</view>
					</view>
				</view>
			</view>
			
			<view v-if="inspirations.length === 0" class="empty">
				<text class="empty-text">暂无灵感</text>
				<text class="empty-tip">点击右上角添加灵感</text>
			</view>
		</scroll-view>
	</view>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getInspirations } from '@/api/inspiration.js'
import config from '@/config.js'

const baseURL = config.baseURL

const categoryTabs = [
	{ label: '全部', value: '' },
	{ label: '外观', value: '外观' },
	{ label: '室内', value: '室内' },
	{ label: '景观', value: '景观' },
	{ label: '细节', value: '细节' }
]

const currentCategory = ref('')
const inspirations = ref([])

const navigateTo = (url) => {
	uni.navigateTo({ url })
}

const changeCategory = (category) => {
	currentCategory.value = category
	loadInspirations()
}

const loadInspirations = async () => {
	try {
		uni.showLoading({ title: '加载中...' })
		const params = currentCategory.value ? { category: currentCategory.value } : {}
		const res = await getInspirations(params)
		inspirations.value = res
		uni.hideLoading()
	} catch (error) {
		uni.hideLoading()
		console.error('获取灵感列表失败:', error)
	}
}

onMounted(() => {
	loadInspirations()
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

.filter-tabs {
	display: flex;
	gap: 30rpx;
	overflow-x: auto;
}

.tab-item {
	font-size: 28rpx;
	color: #666666;
	padding: 10rpx 0;
	white-space: nowrap;
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
	flex-shrink: 0;
}

.add-icon {
	font-size: 40rpx;
	color: #FFFFFF;
	line-height: 1;
}

.inspiration-list {
	flex: 1;
	padding: 20rpx 30rpx;
}

.waterfall {
	display: grid;
	grid-template-columns: repeat(2, 1fr);
	gap: 20rpx;
}

.inspiration-card {
	background: #FFFFFF;
	border-radius: 16rpx;
	overflow: hidden;
	box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.05);
}

.inspiration-image {
	width: 100%;
	display: block;
}

.card-content {
	padding: 20rpx;
}

.title {
	display: block;
	font-size: 28rpx;
	font-weight: bold;
	color: #333333;
	margin-bottom: 15rpx;
	overflow: hidden;
	text-overflow: ellipsis;
	white-space: nowrap;
}

.tags {
	display: flex;
	flex-wrap: wrap;
	gap: 10rpx;
}

.tag {
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
	margin-bottom: 20rpx;
}

.empty-tip {
	font-size: 26rpx;
	color: #CCCCCC;
}
</style>

