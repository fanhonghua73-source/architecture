import request from '@/utils/request.js'

// 获取项目列表
export const getProjects = (params) => {
	return request.get('/api/projects', params)
}

// 创建项目
export const createProject = (data) => {
	return request.post('/api/projects', data)
}

// 获取项目详情
export const getProjectDetail = (id) => {
	return request.get(`/api/projects/${id}`)
}

// 更新项目
export const updateProject = (id, data) => {
	return request.put(`/api/projects/${id}`, data)
}

// 删除项目
export const deleteProject = (id) => {
	return request.delete(`/api/projects/${id}`)
}

// 上传项目图片
export const uploadProjectImage = (projectId, filePath, description) => {
	return request.upload(`/api/projects/${projectId}/images`, filePath, { description })
}

