import config from '@/config.js'

class Request {
	constructor() {
		this.baseURL = config.baseURL
		this.timeout = config.timeout
	}
	
	// 获取token
	getToken() {
		return uni.getStorageSync('token') || ''
	}
	
	// 请求拦截
	interceptRequest(options) {
		const token = this.getToken()
		if (token) {
			options.header = {
				...options.header,
				'Authorization': `Bearer ${token}`
			}
		}
		return options
	}
	
	// 响应拦截
	interceptResponse(response) {
		const { statusCode, data } = response
		
		if (statusCode === 200) {
			return Promise.resolve(data)
		} else if (statusCode === 401) {
			// token过期，跳转登录
			uni.removeStorageSync('token')
			uni.removeStorageSync('userInfo')
			uni.reLaunch({
				url: '/pages/login/login'
			})
			return Promise.reject(new Error('未授权，请重新登录'))
		} else {
			const error = data.detail || '请求失败'
			uni.showToast({
				title: error,
				icon: 'none',
				duration: 2000
			})
			return Promise.reject(new Error(error))
		}
	}
	
	// 通用请求方法
	request(options) {
		options = this.interceptRequest(options)
		
		return new Promise((resolve, reject) => {
			uni.request({
				url: this.baseURL + options.url,
				method: options.method || 'GET',
				data: options.data || {},
				header: {
					'Content-Type': 'application/json',
					...options.header
				},
				timeout: this.timeout,
				success: (res) => {
					this.interceptResponse(res).then(resolve).catch(reject)
				},
				fail: (err) => {
					uni.showToast({
						title: '网络请求失败',
						icon: 'none'
					})
					reject(err)
				}
			})
		})
	}
	
	// GET请求
	get(url, data = {}) {
		return this.request({
			url,
			method: 'GET',
			data
		})
	}
	
	// POST请求
	post(url, data = {}) {
		return this.request({
			url,
			method: 'POST',
			data
		})
	}
	
	// PUT请求
	put(url, data = {}) {
		return this.request({
			url,
			method: 'PUT',
			data
		})
	}
	
	// DELETE请求
	delete(url, data = {}) {
		return this.request({
			url,
			method: 'DELETE',
			data
		})
	}
	
	// 文件上传
	upload(url, filePath, formData = {}) {
		const token = this.getToken()
		
		return new Promise((resolve, reject) => {
			uni.uploadFile({
				url: this.baseURL + url,
				filePath,
				name: 'file',
				formData,
				header: {
					'Authorization': `Bearer ${token}`
				},
				success: (res) => {
					if (res.statusCode === 200) {
						const data = JSON.parse(res.data)
						resolve(data)
					} else {
						reject(new Error('上传失败'))
					}
				},
				fail: (err) => {
					uni.showToast({
						title: '上传失败',
						icon: 'none'
					})
					reject(err)
				}
			})
		})
	}
}

export default new Request()
