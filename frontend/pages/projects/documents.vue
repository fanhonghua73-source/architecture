<template>
	<view class="container">
		<view class="header">
			<text class="title">项目资料管理</text>
			<text class="project-name">{{ projectName }}</text>
		</view>
		
		<!-- 报价数据 -->
		<view class="section">
			<view class="section-header">
				<text class="section-title">报价数据</text>
				<button v-if="canEdit" class="btn-edit" @click="showQuotationModal = true">编辑</button>
			</view>
			<view class="quotation-grid">
				<view class="quotation-item">
					<text class="label">用地面积</text>
					<text class="value">{{ quotation.land_area || '-' }} ㎡</text>
				</view>
				<view class="quotation-item">
					<text class="label">容积率</text>
					<text class="value">{{ quotation.floor_area_ratio || '-' }}</text>
				</view>
				<view class="quotation-item">
					<text class="label">绿化率</text>
					<text class="value">{{ quotation.green_ratio || '-' }}%</text>
				</view>
				<view class="quotation-item">
					<text class="label">密度</text>
					<text class="value">{{ quotation.density || '-' }}</text>
				</view>
				<view class="quotation-item">
					<text class="label">高度</text>
					<text class="value">{{ quotation.height || '-' }} m</text>
				</view>
				<view class="quotation-item">
					<text class="label">总建筑面积</text>
					<text class="value">{{ quotation.total_building_area || '-' }} ㎡</text>
				</view>
				<view class="quotation-item">
					<text class="label">地上面积</text>
					<text class="value">{{ quotation.above_ground_area || '-' }} ㎡</text>
				</view>
				<view class="quotation-item">
					<text class="label">地下面积</text>
					<text class="value">{{ quotation.underground_area || '-' }} ㎡</text>
				</view>
				<view class="quotation-item">
					<text class="label">住宅户数</text>
					<text class="value">{{ quotation.residential_units || '-' }} 户</text>
				</view>
				<view class="quotation-item">
					<text class="label">商业户数</text>
					<text class="value">{{ quotation.commercial_units || '-' }} 户</text>
				</view>
				<view class="quotation-item">
					<text class="label">配套面积</text>
					<text class="value">{{ quotation.supporting_area || '-' }} ㎡</text>
				</view>
				<view class="quotation-item">
					<text class="label">地下室预估</text>
					<text class="value">{{ quotation.basement_estimated_area || '-' }} ㎡</text>
				</view>
				<view class="quotation-item">
					<text class="label">地下车库</text>
					<text class="value">{{ quotation.parking_area || '-' }} ㎡</text>
				</view>
			</view>
		</view>
		
		<!-- 项目资料 -->
		<view class="section">
			<view class="section-header">
				<text class="section-title">项目资料</text>
			</view>
			
			<!-- 通信目录 -->
			<view class="doc-item">
				<view class="doc-header">
					<text class="doc-icon">📁</text>
					<text class="doc-title">通信目录</text>
				</view>
				<view class="doc-actions">
					<button v-if="!documents.communication_catalog && canEdit" class="btn-upload" @click="uploadDocument('communication_catalog')">上传</button>
					<template v-if="documents.communication_catalog">
						<button class="btn-view" @click="viewDocument(documents.communication_catalog)">查看</button>
						<button class="btn-download" @click="downloadDocument(documents.communication_catalog)">下载</button>
					</template>
					<text v-if="!documents.communication_catalog && !canEdit" class="no-permission">暂无文档</text>
				</view>
			</view>
			
			<!-- 进度计划 -->
			<view class="doc-item">
				<view class="doc-header">
					<text class="doc-icon">📅</text>
					<text class="doc-title">进度计划</text>
				</view>
				<view class="doc-actions">
					<button v-if="!documents.schedule && canEdit" class="btn-upload" @click="uploadDocument('schedule')">上传</button>
					<template v-if="documents.schedule">
						<button class="btn-view" @click="viewDocument(documents.schedule)">查看</button>
						<button class="btn-download" @click="downloadDocument(documents.schedule)">下载</button>
					</template>
					<text v-if="!documents.schedule && !canEdit" class="no-permission">暂无文档</text>
				</view>
			</view>
			
			<!-- 阶段文件 -->
			<view class="doc-item">
				<view class="doc-header">
					<text class="doc-icon">📋</text>
					<text class="doc-title">阶段文件</text>
				</view>
				<view class="doc-actions">
					<button v-if="!documents.phase_documents && canEdit" class="btn-upload" @click="uploadDocument('phase_documents')">上传</button>
					<template v-if="documents.phase_documents">
						<button class="btn-view" @click="viewDocument(documents.phase_documents)">查看</button>
						<button class="btn-download" @click="downloadDocument(documents.phase_documents)">下载</button>
					</template>
					<text v-if="!documents.phase_documents && !canEdit" class="no-permission">暂无文档</text>
				</view>
			</view>
			
			<!-- 项目日志 -->
			<view class="doc-item">
				<view class="doc-header">
					<text class="doc-icon">📝</text>
					<text class="doc-title">项目日志</text>
				</view>
				<view class="doc-actions">
					<button v-if="!documents.project_log && canEdit" class="btn-upload" @click="uploadDocument('project_log')">上传</button>
					<template v-if="documents.project_log">
						<button class="btn-view" @click="viewDocument(documents.project_log)">查看</button>
						<button class="btn-download" @click="downloadDocument(documents.project_log)">下载</button>
					</template>
					<text v-if="!documents.project_log && !canEdit" class="no-permission">暂无文档</text>
				</view>
			</view>
			
			<!-- 会议纪要 -->
			<view class="doc-item">
				<view class="doc-header">
					<text class="doc-icon">📄</text>
					<text class="doc-title">会议纪要</text>
				</view>
				<view class="doc-actions">
					<button v-if="!documents.meeting_minutes && canEdit" class="btn-upload" @click="uploadDocument('meeting_minutes')">上传</button>
					<template v-if="documents.meeting_minutes">
						<button class="btn-view" @click="viewDocument(documents.meeting_minutes)">查看</button>
						<button class="btn-download" @click="downloadDocument(documents.meeting_minutes)">下载</button>
					</template>
					<text v-if="!documents.meeting_minutes && !canEdit" class="no-permission">暂无文档</text>
				</view>
			</view>
			
			<!-- 文件收发 -->
			<view class="doc-item">
				<view class="doc-header">
					<text class="doc-icon">📨</text>
					<text class="doc-title">文件收发</text>
				</view>
				<view class="doc-actions">
					<button v-if="!documents.file_exchange && canEdit" class="btn-upload" @click="uploadDocument('file_exchange')">上传</button>
					<template v-if="documents.file_exchange">
						<button class="btn-view" @click="viewDocument(documents.file_exchange)">查看</button>
						<button class="btn-download" @click="downloadDocument(documents.file_exchange)">下载</button>
					</template>
					<text v-if="!documents.file_exchange && !canEdit" class="no-permission">暂无文档</text>
				</view>
			</view>
			
			<!-- 往来函件 -->
			<view class="doc-item">
				<view class="doc-header">
					<text class="doc-icon">✉️</text>
					<text class="doc-title">往来函件</text>
				</view>
				<view class="doc-actions">
					<button v-if="!documents.correspondence && canEdit" class="btn-upload" @click="uploadDocument('correspondence')">上传</button>
					<template v-if="documents.correspondence">
						<button class="btn-view" @click="viewDocument(documents.correspondence)">查看</button>
						<button class="btn-download" @click="downloadDocument(documents.correspondence)">下载</button>
					</template>
					<text v-if="!documents.correspondence && !canEdit" class="no-permission">暂无文档</text>
				</view>
			</view>
			
			<!-- 批复审图 -->
			<view class="doc-item">
				<view class="doc-header">
					<text class="doc-icon">✅</text>
					<text class="doc-title">批复审图</text>
				</view>
				<view class="doc-actions">
					<button v-if="!documents.approval_review && canEdit" class="btn-upload" @click="uploadDocument('approval_review')">上传</button>
					<template v-if="documents.approval_review">
						<button class="btn-view" @click="viewDocument(documents.approval_review)">查看</button>
						<button class="btn-download" @click="downloadDocument(documents.approval_review)">下载</button>
					</template>
					<text v-if="!documents.approval_review && !canEdit" class="no-permission">暂无文档</text>
				</view>
			</view>
			
			<!-- 用地红线 -->
			<view class="doc-item">
				<view class="doc-header">
					<text class="doc-icon">🗺️</text>
					<text class="doc-title">用地红线</text>
				</view>
				<view class="doc-actions">
					<button v-if="!documents.land_boundary && canEdit" class="btn-upload" @click="uploadDocument('land_boundary')">上传</button>
					<template v-if="documents.land_boundary">
						<button class="btn-view" @click="viewDocument(documents.land_boundary)">查看</button>
						<button class="btn-download" @click="downloadDocument(documents.land_boundary)">下载</button>
						<button v-if="canEdit" class="btn-convert" @click="convertToCAD">转CAD</button>
					</template>
					<text v-if="!documents.land_boundary && !canEdit" class="no-permission">暂无文档</text>
				</view>
			</view>
			
			<!-- 规划条件 -->
			<view class="doc-item">
				<view class="doc-header">
					<text class="doc-icon">📐</text>
					<text class="doc-title">规划条件</text>
				</view>
				<view class="doc-actions">
					<button v-if="!documents.planning && canEdit" class="btn-upload" @click="uploadDocument('planning')">上传</button>
					<template v-if="documents.planning">
						<button class="btn-view" @click="viewDocument(documents.planning)">查看</button>
						<button class="btn-download" @click="downloadDocument(documents.planning)">下载</button>
					</template>
					<text v-if="!documents.planning && !canEdit" class="no-permission">暂无文档</text>
				</view>
			</view>
			
			<!-- 甲方确认函 -->
			<view class="doc-item">
				<view class="doc-header">
					<text class="doc-icon">📜</text>
					<text class="doc-title">甲方确认函</text>
				</view>
				<view class="doc-actions">
					<button v-if="!documents.confirmation && canEdit" class="btn-upload" @click="uploadDocument('confirmation')">上传</button>
					<template v-if="documents.confirmation">
						<button class="btn-view" @click="viewDocument(documents.confirmation)">查看</button>
						<button class="btn-download" @click="downloadDocument(documents.confirmation)">下载</button>
					</template>
					<text v-if="!documents.confirmation && !canEdit" class="no-permission">暂无文档</text>
				</view>
			</view>
			
			<!-- 扩初阶段 -->
			<view class="doc-item">
				<view class="doc-header">
					<text class="doc-icon">📊</text>
					<text class="doc-title">扩初阶段</text>
				</view>
				<view class="doc-actions">
					<button v-if="!documents.preliminary_design && canEdit" class="btn-upload" @click="uploadDocument('preliminary_design')">上传</button>
					<template v-if="documents.preliminary_design">
						<button class="btn-view" @click="viewDocument(documents.preliminary_design)">查看</button>
						<button class="btn-download" @click="downloadDocument(documents.preliminary_design)">下载</button>
					</template>
					<text v-if="!documents.preliminary_design && !canEdit" class="no-permission">暂无文档</text>
				</view>
			</view>
			
			<!-- 施工图阶段 -->
			<view class="doc-item">
				<view class="doc-header">
					<text class="doc-icon">🏗️</text>
					<text class="doc-title">施工图阶段</text>
				</view>
				<view class="doc-actions">
					<button v-if="!documents.construction_drawing && canEdit" class="btn-upload" @click="uploadDocument('construction_drawing')">上传</button>
					<template v-if="documents.construction_drawing">
						<button class="btn-view" @click="viewDocument(documents.construction_drawing)">查看</button>
						<button class="btn-download" @click="downloadDocument(documents.construction_drawing)">下载</button>
					</template>
					<text v-if="!documents.construction_drawing && !canEdit" class="no-permission">暂无文档</text>
				</view>
			</view>
			
			<!-- 施工阶段 -->
			<view class="doc-item">
				<view class="doc-header">
					<text class="doc-icon">🔨</text>
					<text class="doc-title">施工阶段</text>
				</view>
				<view class="doc-actions">
					<button v-if="!documents.construction_phase && canEdit" class="btn-upload" @click="uploadDocument('construction_phase')">上传</button>
					<template v-if="documents.construction_phase">
						<button class="btn-view" @click="viewDocument(documents.construction_phase)">查看</button>
						<button class="btn-download" @click="downloadDocument(documents.construction_phase)">下载</button>
					</template>
					<text v-if="!documents.construction_phase && !canEdit" class="no-permission">暂无文档</text>
				</view>
			</view>
			
			<!-- 工作文件 -->
			<view class="doc-item">
				<view class="doc-header">
					<text class="doc-icon">📂</text>
					<text class="doc-title">工作文件</text>
				</view>
				<view class="doc-actions">
					<button v-if="!documents.work_files && canEdit" class="btn-upload" @click="uploadDocument('work_files')">上传</button>
					<template v-if="documents.work_files">
						<button class="btn-view" @click="viewDocument(documents.work_files)">查看</button>
						<button class="btn-download" @click="downloadDocument(documents.work_files)">下载</button>
					</template>
					<text v-if="!documents.work_files && !canEdit" class="no-permission">暂无文档</text>
				</view>
			</view>
			
			<!-- 百度位置 -->
			<view class="doc-item">
				<view class="doc-header">
					<text class="doc-icon">📍</text>
					<text class="doc-title">百度位置</text>
				</view>
				<view class="doc-actions">
					<button v-if="canEdit" class="btn-upload" @click="showLocationModal = true">设置位置</button>
					<button v-if="location" class="btn-view" @click="viewLocation">查看地图</button>
					<text v-if="!location && !canEdit" class="no-permission">暂无位置</text>
				</view>
			</view>
		</view>
		
		<!-- 报价编辑弹窗 -->
		<view class="modal-mask" v-if="showQuotationModal" @click="showQuotationModal = false">
			<view class="modal" @click.stop>
				<view class="modal-header">
					<text class="modal-title">编辑报价数据</text>
				</view>
				<view class="modal-body">
					<!-- 稳定数据（规划条件核心指标） -->
					<view class="form-section">
						<text class="section-label">规划条件核心指标</text>
						<view class="form-item">
							<text class="form-label">用地面积(㎡)</text>
							<input class="form-input" type="digit" v-model="editQuotation.land_area" placeholder="请输入用地面积" />
						</view>
						<view class="form-item">
							<text class="form-label">容积率</text>
							<input class="form-input" type="digit" v-model="editQuotation.floor_area_ratio" placeholder="请输入容积率" />
						</view>
						<view class="form-item">
							<text class="form-label">绿化率(%)</text>
							<input class="form-input" type="digit" v-model="editQuotation.green_ratio" placeholder="请输入绿化率" />
						</view>
						<view class="form-item">
							<text class="form-label">密度</text>
							<input class="form-input" type="digit" v-model="editQuotation.density" placeholder="请输入密度" />
						</view>
						<view class="form-item">
							<text class="form-label">高度(m)</text>
							<input class="form-input" type="digit" v-model="editQuotation.height" placeholder="请输入高度" />
						</view>
					</view>
					
					<!-- 其他报价数据 -->
					<view class="form-section">
						<text class="section-label">其他报价数据</text>
						<view class="form-item">
							<text class="form-label">总建筑面积(㎡)</text>
							<input class="form-input" type="digit" v-model="editQuotation.total_building_area" placeholder="请输入总建筑面积" />
						</view>
						<view class="form-item">
							<text class="form-label">地上面积(㎡)</text>
							<input class="form-input" type="digit" v-model="editQuotation.above_ground_area" placeholder="请输入地上面积" />
						</view>
						<view class="form-item">
							<text class="form-label">地下面积(㎡)</text>
							<input class="form-input" type="digit" v-model="editQuotation.underground_area" placeholder="请输入地下面积" />
						</view>
						<view class="form-item">
							<text class="form-label">住宅户数</text>
							<input class="form-input" type="number" v-model="editQuotation.residential_units" placeholder="请输入住宅户数" />
						</view>
						<view class="form-item">
							<text class="form-label">商业户数</text>
							<input class="form-input" type="number" v-model="editQuotation.commercial_units" placeholder="请输入商业户数" />
						</view>
						<view class="form-item">
							<text class="form-label">配套面积(㎡)</text>
							<input class="form-input" type="digit" v-model="editQuotation.supporting_area" placeholder="请输入配套面积" />
						</view>
						<view class="form-item">
							<text class="form-label">地下室预估(㎡)</text>
							<input class="form-input" type="digit" v-model="editQuotation.basement_estimated_area" placeholder="请输入地下室预估面积" />
						</view>
						<view class="form-item">
							<text class="form-label">地下车库(㎡)</text>
							<input class="form-input" type="digit" v-model="editQuotation.parking_area" placeholder="请输入地下车库面积" />
						</view>
					</view>
				</view>
				<view class="modal-footer">
					<button class="btn-cancel" @click="showQuotationModal = false">取消</button>
					<button class="btn-confirm" @click="saveQuotation">保存</button>
				</view>
			</view>
		</view>
		
		<!-- 位置设置弹窗 -->
		<view class="modal-mask" v-if="showLocationModal" @click="showLocationModal = false">
			<view class="modal" @click.stop>
				<view class="modal-header">
					<text class="modal-title">设置项目位置</text>
				</view>
				<view class="modal-body">
					<view class="form-item">
						<text class="form-label">项目地址</text>
						<input class="form-input" v-model="editLocation.address" placeholder="请输入项目地址" />
					</view>
					<view class="form-item">
						<text class="form-label">经度</text>
						<input class="form-input" type="digit" v-model="editLocation.longitude" placeholder="自动获取或手动输入" />
					</view>
					<view class="form-item">
						<text class="form-label">纬度</text>
						<input class="form-input" type="digit" v-model="editLocation.latitude" placeholder="自动获取或手动输入" />
					</view>
					<button class="btn-geocode" @click="geocodeAddress">根据地址获取坐标</button>
				</view>
				<view class="modal-footer">
					<button class="btn-cancel" @click="showLocationModal = false">取消</button>
					<button class="btn-confirm" @click="saveLocation">保存</button>
				</view>
			</view>
		</view>
	</view>
</template>

<script>
export default {
	data() {
		return {
			projectId: null,
			projectName: '',
			quotation: {},
			documents: {
				land_boundary: null,
				planning: null,
				confirmation: null,
				regulation: null
			},
			location: null,
			showQuotationModal: false,
			showLocationModal: false,
			editQuotation: {},
			editLocation: {
				address: '',
				longitude: '',
				latitude: ''
			},
			canEdit: false  // 是否可以编辑
		}
	},
	onLoad(options) {
		this.projectId = options.id
		this.loadProjectData()
	},
	watch: {
		showQuotationModal(val) {
			if (val) {
				this.editQuotation = { ...this.quotation }
			}
		},
		showLocationModal(val) {
			if (val) {
				if (this.location) {
					this.editLocation = { ...this.location }
				}
			}
		}
	},
	methods: {
		async loadProjectData() {
			uni.showLoading({ title: '加载中...' })
			try {
				const token = uni.getStorageSync('token')
				const userInfo = uni.getStorageSync('userInfo')
				
				// 获取项目基本信息
				const projectRes = await uni.request({
					url: `http://localhost:8000/api/projects/${this.projectId}`,
					header: { Authorization: `Bearer ${token}` }
				})
				
				if (projectRes.data) {
					this.projectName = projectRes.data.name
					
					// 判断是否可以编辑：项目创建者或root用户
					this.canEdit = userInfo?.is_root || projectRes.data.user_id === userInfo?.id
					
					this.quotation = {
						land_area: projectRes.data.land_area,
						floor_area_ratio: projectRes.data.floor_area_ratio,
						green_ratio: projectRes.data.green_ratio,
						density: projectRes.data.density,
						height: projectRes.data.height,
						total_building_area: projectRes.data.total_building_area,
						above_ground_area: projectRes.data.above_ground_area,
						underground_area: projectRes.data.underground_area,
						residential_units: projectRes.data.residential_units,
						commercial_units: projectRes.data.commercial_units,
						supporting_area: projectRes.data.supporting_area,
						basement_estimated_area: projectRes.data.basement_estimated_area,
						parking_area: projectRes.data.parking_area
					}
					
					this.documents.land_boundary = projectRes.data.land_boundary_pdf
					this.documents.planning = projectRes.data.planning_conditions_pdf
					this.documents.confirmation = projectRes.data.client_confirmation_pdf
					this.documents.regulation = projectRes.data.special_regulations_pdf
					
					if (projectRes.data.baidu_location) {
						this.location = JSON.parse(projectRes.data.baidu_location)
					}
				}
			} catch (error) {
				uni.showToast({ title: '加载失败', icon: 'none' })
			} finally {
				uni.hideLoading()
			}
		},
		
		uploadDocument(docType) {
			uni.chooseFile({
				count: 1,
				extension: ['.pdf', '.doc', '.docx', '.jpg', '.png'],
				success: async (res) => {
					const tempFilePath = res.tempFilePaths[0]
					uni.showLoading({ title: '上传中...' })
					
					try {
						const token = uni.getStorageSync('token')
						const uploadRes = await uni.uploadFile({
							url: `http://localhost:8000/api/projects/${this.projectId}/documents/upload?doc_type=${docType}`,
							filePath: tempFilePath,
							name: 'file',
							header: { Authorization: `Bearer ${token}` }
						})
						
						if (uploadRes.statusCode === 200) {
							uni.showToast({ title: '上传成功', icon: 'success' })
							this.loadProjectData()
						}
					} catch (error) {
						uni.showToast({ title: '上传失败', icon: 'none' })
					} finally {
						uni.hideLoading()
					}
				}
			})
		},
		
		viewDocument(filePath) {
			// 在浏览器中打开文档
			const url = `http://localhost:8000${filePath}`
			// #ifdef H5
			window.open(url, '_blank')
			// #endif
			// #ifndef H5
			uni.downloadFile({
				url: url,
				success: (res) => {
					uni.openDocument({
						filePath: res.tempFilePath,
						showMenu: true
					})
				}
			})
			// #endif
		},
		
		downloadDocument(filePath) {
			const url = `http://localhost:8000${filePath}`
			uni.downloadFile({
				url: url,
				success: (res) => {
					uni.showToast({ title: '下载成功', icon: 'success' })
				}
			})
		},
		
		async convertToCAD() {
			uni.showLoading({ title: '转换中...' })
			try {
				const token = uni.getStorageSync('token')
				const res = await uni.request({
					url: `http://localhost:8000/api/projects/${this.projectId}/land-boundary/to-cad`,
					method: 'POST',
					header: { Authorization: `Bearer ${token}` }
				})
				
				if (res.data.cad_path) {
					uni.showToast({ title: '转换成功', icon: 'success' })
					// 自动下载CAD文件
					this.downloadDocument(res.data.cad_path)
				}
			} catch (error) {
				uni.showToast({ title: '转换失败', icon: 'none' })
			} finally {
				uni.hideLoading()
			}
		},
		
		async saveQuotation() {
			uni.showLoading({ title: '保存中...' })
			try {
				const token = uni.getStorageSync('token')
				await uni.request({
					url: `http://localhost:8000/api/projects/${this.projectId}/quotation`,
					method: 'PUT',
					header: { Authorization: `Bearer ${token}` },
					data: this.editQuotation
				})
				
				uni.showToast({ title: '保存成功', icon: 'success' })
				this.showQuotationModal = false
				this.loadProjectData()
			} catch (error) {
				uni.showToast({ title: '保存失败', icon: 'none' })
			} finally {
				uni.hideLoading()
			}
		},
		
		async geocodeAddress() {
			if (!this.editLocation.address) {
				uni.showToast({ title: '请输入地址', icon: 'none' })
				return
			}
			
			// 这里应该调用百度地图API进行地址解析
			// 简化示例，实际需要申请百度地图API Key
			uni.showToast({ title: '请手动输入经纬度', icon: 'none' })
		},
		
		async saveLocation() {
			if (!this.editLocation.address || !this.editLocation.longitude || !this.editLocation.latitude) {
				uni.showToast({ title: '请填写完整信息', icon: 'none' })
				return
			}
			
			uni.showLoading({ title: '保存中...' })
			try {
				const token = uni.getStorageSync('token')
				await uni.request({
					url: `http://localhost:8000/api/projects/${this.projectId}/location`,
					method: 'POST',
					header: { Authorization: `Bearer ${token}` },
					data: this.editLocation
				})
				
				uni.showToast({ title: '保存成功', icon: 'success' })
				this.showLocationModal = false
				this.loadProjectData()
			} catch (error) {
				uni.showToast({ title: '保存失败', icon: 'none' })
			} finally {
				uni.hideLoading()
			}
		},
		
		viewLocation() {
			if (!this.location) return
			
			// 打开地图查看位置
			uni.openLocation({
				latitude: parseFloat(this.location.latitude),
				longitude: parseFloat(this.location.longitude),
				name: this.projectName,
				address: this.location.address
			})
		}
	}
}
</script>

<style scoped>
.container {
	min-height: 100vh;
	background: #f5f5f5;
	padding: 20rpx;
}

.header {
	background: white;
	padding: 30rpx;
	border-radius: 16rpx;
	margin-bottom: 20rpx;
}

.title {
	font-size: 36rpx;
	font-weight: bold;
	color: #333;
	display: block;
	margin-bottom: 10rpx;
}

.project-name {
	font-size: 28rpx;
	color: #666;
}

.section {
	background: white;
	border-radius: 16rpx;
	padding: 30rpx;
	margin-bottom: 20rpx;
}

.section-header {
	display: flex;
	justify-content: space-between;
	align-items: center;
	margin-bottom: 30rpx;
}

.section-title {
	font-size: 32rpx;
	font-weight: bold;
	color: #333;
}

.btn-edit {
	background: #007aff;
	color: white;
	border: none;
	padding: 10rpx 30rpx;
	border-radius: 8rpx;
	font-size: 28rpx;
}

.quotation-grid {
	display: grid;
	grid-template-columns: repeat(2, 1fr);
	gap: 20rpx;
}

.quotation-item {
	padding: 20rpx;
	background: #f8f8f8;
	border-radius: 12rpx;
}

.label {
	font-size: 24rpx;
	color: #999;
	display: block;
	margin-bottom: 10rpx;
}

.value {
	font-size: 28rpx;
	color: #333;
	font-weight: bold;
}

.doc-item {
	padding: 30rpx 0;
	border-bottom: 1px solid #f0f0f0;
}

.doc-item:last-child {
	border-bottom: none;
}

.doc-header {
	display: flex;
	align-items: center;
	margin-bottom: 20rpx;
}

.doc-icon {
	font-size: 40rpx;
	margin-right: 15rpx;
}

.doc-title {
	font-size: 30rpx;
	color: #333;
	font-weight: 500;
}

.doc-actions {
	display: flex;
	gap: 15rpx;
}

.btn-upload, .btn-view, .btn-download, .btn-convert {
	padding: 10rpx 25rpx;
	border-radius: 8rpx;
	font-size: 26rpx;
	border: none;
}

.btn-upload {
	background: #007aff;
	color: white;
}

.btn-view {
	background: #10b981;
	color: white;
}

.btn-download {
	background: #8b5cf6;
	color: white;
}

.btn-convert {
	background: #f59e0b;
	color: white;
}

.no-permission {
	font-size: 26rpx;
	color: #999;
}

.modal {
	width: 600rpx;
	background: white;
	border-radius: 16rpx;
	overflow: hidden;
}

.modal-header {
	padding: 30rpx;
	border-bottom: 1px solid #f0f0f0;
}

.modal-title {
	font-size: 32rpx;
	font-weight: bold;
	color: #333;
}

.modal-body {
	padding: 30rpx;
	max-height: 800rpx;
	overflow-y: auto;
}

.form-section {
	margin-bottom: 40rpx;
}

.form-section:last-child {
	margin-bottom: 0;
}

.section-label {
	font-size: 30rpx;
	font-weight: bold;
	color: #007aff;
	display: block;
	margin-bottom: 20rpx;
	padding-bottom: 10rpx;
	border-bottom: 2px solid #007aff;
}

.form-item {
	margin-bottom: 30rpx;
}

.form-label {
	font-size: 28rpx;
	color: #666;
	display: block;
	margin-bottom: 15rpx;
}

.form-input {
	width: 100%;
	padding: 20rpx;
	border: 1px solid #e0e0e0;
	border-radius: 8rpx;
	font-size: 28rpx;
}

.btn-geocode {
	width: 100%;
	background: #10b981;
	color: white;
	border: none;
	padding: 20rpx;
	border-radius: 8rpx;
	font-size: 28rpx;
	margin-top: 20rpx;
}

.modal-footer {
	display: flex;
	padding: 20rpx 30rpx;
	border-top: 1px solid #f0f0f0;
	gap: 20rpx;
}

.btn-cancel, .btn-confirm {
	flex: 1;
	padding: 20rpx;
	border-radius: 8rpx;
	font-size: 28rpx;
	border: none;
}

.btn-cancel {
	background: #f0f0f0;
	color: #666;
}

.btn-confirm {
	background: #007aff;
	color: white;
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

.modal-mask .modal {
	margin: 0;
}
</style>

