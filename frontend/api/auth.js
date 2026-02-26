import request from '@/utils/request.js'

// 用户注册
export const register = (data) => {
	return request.post('/api/auth/register', data)
}

// 用户登录
export const login = (data) => {
	return request.post('/api/auth/login', data)
}

// 获取用户信息
export const getProfile = () => {
	return request.get('/api/auth/profile')
}

// 更新用户信息
export const updateProfile = (data) => {
	return request.put('/api/auth/profile', data)
}

// 修改密码
export const changePassword = (data) => {
	return request.post('/api/auth/change-password', data)
}

// 上传头像
export const uploadAvatar = (file) => {
	return request.upload('/api/auth/avatar', file)
}

