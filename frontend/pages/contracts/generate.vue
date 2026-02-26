<template>
	<view class="container">
		<view class="header">
			<text class="title">生成合同</text>
		</view>
		
		<view class="form-section">
			<view class="form-item">
				<text class="label">选择项目</text>
				<picker mode="selector" :range="projects" range-key="name" @change="onProjectChange">
					<view class="picker">
						{{ selectedProject ? selectedProject.name : '请选择项目' }}
					</view>
				</picker>
			</view>
			
			<view class="form-item">
				<text class="label">项目地址</text>
				<input v-model="formData.location" class="input" placeholder="请输入项目地址" />
			</view>
			
			<view class="form-item">
				<text class="label">建筑面积（平方米）</text>
				<input v-model.number="formData.area" class="input" type="number" placeholder="请输入建筑面积" />
			</view>
			
			<view class="form-item">
				<text class="label">AI提供商</text>
				<picker mode="selector" :range="aiProviders" range-key="label" @change="onProviderChange">
					<view class="picker">
						{{ selectedProvider ? selectedProvider.label : '请选择AI提供商' }}
					</view>
				</picker>
			</view>
			
			<view class="form-item">
				<text class="label">合同模板</text>
				<view class="template-options">
					<button class="option-btn" :class="{ active: templateMode === 'text' }" @click="templateMode = 'text'">文本输入</button>
					<button class="option-btn" :class="{ active: templateMode === 'file' }" @click="templateMode = 'file'">上传文件</button>
				</view>
				<textarea v-if="templateMode === 'text'" v-model="formData.template" class="textarea" placeholder="请输入合同模板内容" />
				<view v-else class="upload-area">
					<button v-if="!templateFile" class="upload-btn" @click="chooseTemplateFile">
						<text class="upload-icon">📄</text>
						<text class="upload-text">点击上传Word或PDF模板</text>
					</button>
					<view v-else class="file-info">
						<text class="file-name">{{ templateFile.name }}</text>
						<button class="remove-btn" @click="removeTemplateFile">删除</button>
					</view>
				</view>
			</view>
		</view>
		
		<view class="btn-section">
			<button class="generate-btn" @click="handleGenerate">生成合同</button>
		</view>
		
		<!-- 生成的合同内容 -->
		<view v-if="generatedContract" class="contract-section">
			<view class="section-header">
				<text class="section-title">生成的合同</text>
			</view>
			<view class="contract-content">
				<text class="content-text">{{ generatedContract }}</text>
			</view>
		</view>
	</view>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import request from '@/utils/request.js'

const projects = ref([])
const selectedProject = ref(null)
const selectedProvider = ref(null)
const generatedContract = ref('')
const templateMode = ref('text')  // 'text' 或 'file'
const templateFile = ref(null)

const aiProviders = [
	{ value: 'minimax', label: 'MiniMax' },
	{ value: 'gemini', label: 'Gemini' }
]

const formData = reactive({
	project_id: null,
	location: '',
	area: null,
	ai_provider: '',
	template: `建筑设计合同

甲方（委托方）：
乙方（设计方）：

根据《中华人民共和国合同法》及相关法律法规，甲乙双方在平等、自愿的基础上，就建筑设计事宜达成如下协议：

一、项目概况
项目名称：
项目地址：
建筑面积：
设计周期：

二、设计内容及要求
1. 设计范围：
2. 设计深度：
3. 技术标准：

三、合同价款
设计费总额：
付款方式：

四、双方责任
甲方责任：
乙方责任：

五、违约责任

六、争议解决

七、其他约定

甲方（盖章）：                    乙方（盖章）：
代表签字：                        代表签字：
日期：                            日期：`
})

const loadProjects = async () => {
	try {
		const res = await request.get('/api/projects')
		projects.value = res
	} catch (error) {
		console.error('获取项目列表失败:', error)
	}
}

const onProjectChange = (e) => {
	const index = e.detail.value
	selectedProject.value = projects.value[index]
	formData.project_id = selectedProject.value.id
	formData.location = selectedProject.value.address || ''
	formData.area = selectedProject.value.area || null
}

const onProviderChange = (e) => {
	const index = e.detail.value
	selectedProvider.value = aiProviders[index]
	formData.ai_provider = selectedProvider.value.value
}

const chooseTemplateFile = () => {
	uni.chooseFile({
		count: 1,
		extension: ['.pdf', '.doc', '.docx'],
		success: (res) => {
			templateFile.value = {
				name: res.tempFiles[0].name,
				path: res.tempFilePaths[0]
			}
		}
	})
}

const removeTemplateFile = () => {
	templateFile.value = null
}

const handleGenerate = async () => {
	if (!formData.project_id) {
		uni.showToast({
			title: '请选择项目',
			icon: 'none'
		})
		return
	}
	
	if (!formData.ai_provider) {
		uni.showToast({
			title: '请选择AI提供商',
			icon: 'none'
		})
		return
	}
	
	if (templateMode.value === 'text' && !formData.template) {
		uni.showToast({
			title: '请输入合同模板',
			icon: 'none'
		})
		return
	}
	
	if (templateMode.value === 'file' && !templateFile.value) {
		uni.showToast({
			title: '请上传模板文件',
			icon: 'none'
		})
		return
	}
	
	try {
		uni.showLoading({ title: '生成中...' })
		
		let res
		if (templateMode.value === 'file') {
			// 使用文件上传方式
			const token = uni.getStorageSync('token')
			const uploadRes = await uni.uploadFile({
				url: `http://localhost:8000/api/contracts/generate-pdf?project_id=${formData.project_id}&area=${formData.area}&location=${formData.location}&ai_provider=${formData.ai_provider}`,
				filePath: templateFile.value.path,
				name: 'template_file',
				header: { Authorization: `Bearer ${token}` }
			})
			res = JSON.parse(uploadRes.data)
		} else {
			// 使用文本模板方式
			res = await request.post('/api/contracts/generate-pdf', {
				...formData,
				template_text: formData.template
			})
		}
		
		uni.hideLoading()
		
		generatedContract.value = res.content
		
		uni.showToast({
			title: '生成成功',
			icon: 'success'
		})
	} catch (error) {
		uni.hideLoading()
		console.error('生成合同失败:', error)
	}
}

onMounted(() => {
	loadProjects()
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

.form-section {
	background: #FFFFFF;
	border-radius: 16rpx;
	padding: 30rpx;
	margin-bottom: 30rpx;
}

.form-item {
	margin-bottom: 30rpx;
}

.form-item:last-child {
	margin-bottom: 0;
}

.label {
	display: block;
	font-size: 28rpx;
	color: #333333;
	margin-bottom: 15rpx;
	font-weight: 500;
}

.input, .picker {
	width: 100%;
	height: 80rpx;
	background: #F5F7FA;
	border-radius: 12rpx;
	padding: 0 20rpx;
	font-size: 28rpx;
	display: flex;
	align-items: center;
}

.textarea {
	width: 100%;
	min-height: 300rpx;
	background: #F5F7FA;
	border-radius: 12rpx;
	padding: 20rpx;
	font-size: 26rpx;
	line-height: 1.6;
}

.template-options {
	display: flex;
	gap: 20rpx;
	margin-bottom: 20rpx;
}

.option-btn {
	flex: 1;
	height: 70rpx;
	background: #F5F7FA;
	color: #666;
	border: 2rpx solid transparent;
	border-radius: 12rpx;
	font-size: 28rpx;
}

.option-btn.active {
	background: #E8F0FE;
	color: #667eea;
	border-color: #667eea;
}

.upload-area {
	min-height: 200rpx;
	display: flex;
	align-items: center;
	justify-content: center;
}

.upload-btn {
	width: 100%;
	height: 200rpx;
	background: #F5F7FA;
	border: 2rpx dashed #D0D0D0;
	border-radius: 12rpx;
	display: flex;
	flex-direction: column;
	align-items: center;
	justify-content: center;
	gap: 15rpx;
}

.upload-icon {
	font-size: 60rpx;
}

.upload-text {
	font-size: 26rpx;
	color: #999;
}

.file-info {
	width: 100%;
	padding: 30rpx;
	background: #F5F7FA;
	border-radius: 12rpx;
	display: flex;
	justify-content: space-between;
	align-items: center;
}

.file-name {
	font-size: 28rpx;
	color: #333;
	flex: 1;
}

.remove-btn {
	padding: 10rpx 25rpx;
	background: #FF6B6B;
	color: white;
	border: none;
	border-radius: 8rpx;
	font-size: 26rpx;
}

.btn-section {
	margin-bottom: 30rpx;
}

.generate-btn {
	width: 100%;
	height: 88rpx;
	background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
	color: #FFFFFF;
	border-radius: 12rpx;
	font-size: 32rpx;
	font-weight: bold;
	border: none;
}

.contract-section {
	background: #FFFFFF;
	border-radius: 16rpx;
	padding: 30rpx;
}

.section-header {
	margin-bottom: 20rpx;
	padding-bottom: 20rpx;
	border-bottom: 2rpx solid #F0F0F0;
}

.section-title {
	font-size: 30rpx;
	font-weight: bold;
	color: #333333;
}

.contract-content {
	padding: 20rpx;
	background: #F9FAFB;
	border-radius: 12rpx;
}

.content-text {
	font-size: 26rpx;
	line-height: 1.8;
	color: #333333;
	white-space: pre-wrap;
}
</style>

