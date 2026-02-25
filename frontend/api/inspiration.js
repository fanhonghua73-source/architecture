import request from '@/utils/request.js'

// 获取灵感列表
export const getInspirations = (params) => {
	return request.get('/api/inspirations', params)
}

// 创建灵感（文件上传）
export const createInspiration = (filePath, data) => {
	return request.upload('/api/inspirations', filePath, {
		title: data.title,
		description: data.description || '',
		tags: data.tags || '',
		category: data.category || '',
		style: data.style || ''
	})
}

// 获取灵感详情
export const getInspirationDetail = (id) => {
	return request.get(`/api/inspirations/${id}`)
}

// 更新灵感
export const updateInspiration = (id, data) => {
	return request.put(`/api/inspirations/${id}`, data)
}

// 删除灵感
export const deleteInspiration = (id) => {
	return request.delete(`/api/inspirations/${id}`)
}

// 获取标签列表
export const getTags = () => {
	return request.get('/api/inspirations/tags/list')
}
