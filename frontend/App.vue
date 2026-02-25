<script>
export default {
	onLaunch: function() {
		console.log('App Launch')
		
		// 检查登录状态
		const token = uni.getStorageSync('token')
		if (!token) {
			uni.reLaunch({
				url: '/pages/login/login'
			})
		}
	},
	onShow: function() {
		console.log('App Show')
	},
	onHide: function() {
		console.log('App Hide')
	}
}
</script>

<style>
@import url('./static/styles/common.css');

page {
	background-color: #F5F7FA;
}
</style>

