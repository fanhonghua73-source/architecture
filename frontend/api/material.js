import request from '@/utils/request.js'

// 获取材料列表
export const getMaterials = (params) => {
	return request.get('/api/materials', params)
}

// 创建材料
export const createMaterial = (filePath, data) => {
	return request.upload('/api/materials', filePath, data)
}

// 获取材料详情
export const getMaterialDetail = (id) => {
	return request.get(`/api/materials/${id}`)
}

// 更新材料
export const updateMaterial = (id, data) => {
	return request.put(`/api/materials/${id}`, data)
}

// 删除材料
export const deleteMaterial = (id) => {
	return request.delete(`/api/materials/${id}`)
}

// 获取供应商列表
export const getSuppliers = (params) => {
	return request.get('/api/suppliers', params)
}

// 创建供应商
export const createSupplier = (data) => {
	return request.post('/api/suppliers', data)
}

