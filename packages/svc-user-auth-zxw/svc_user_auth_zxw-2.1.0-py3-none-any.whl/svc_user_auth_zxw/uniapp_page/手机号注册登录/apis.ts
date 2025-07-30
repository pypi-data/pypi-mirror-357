// 登录后返回值：
// response = {
//   "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxNTA1MjY3MjgxNSIsInVzZXJuYW1lIjoiMTUwNTI2NzI4MTUiLCJuaWNrbmFtZSI6bnVsbCwicm9sZXMiOlt7InJvbGVfbmFtZSI6ImwwIiwiYXBwX25hbWUiOiJhcHAwIiwiYXBwX2lkIjoxfV0sImV4cCI6MTcyNzE3MjAzOX0.bJBRK32126S7qROhnjKGbxNJQufGGMuOalwEnrro2DM",
//   "refresh_token": "760b0b64f567b2bca74ed8255ee69c15f278cd8fd281ceadd1da9bdb0b768899",
//   "user_info": {
//     "sub": "15052672815",
//     "username": "15052672815",
//     "nickname": null,
//     "roles": [
//       {
//         "role_name": "l0",
//         "app_name": "app0",
//         "app_id": 1
//       }
//     ]
//   }
// }

import {buildApiUrl} from '@/config.js'


interface Role {
	role_name : string;
	app_name : string;
	app_id : number;
}

interface UserInfo {
	sub : string;
	username : string;
	nickname : string;
	roles : Role[];
}

interface LoginResponse {
	access_token : string;
	refresh_token : string;
	user_info : UserInfo;
}


// 添加一个通用的请求函数来处理错误
const saveTokenToCookie = (token : string, refresh_token : string, user_info) => {
	uni.setStorageSync('access_token', token);
	uni.setStorageSync('refresh_token', refresh_token);
	uni.setStorageSync('user_info', user_info);
}

// 从 cookie 获取 token
const getTokenFromCookie = () => {
	return uni.getStorageSync('access_token');
}

// 设置header token
const setHeaderToken = () => {
	const token = getTokenFromCookie();
	return token ? { 'Authorization': `Bearer ${token}` } : {}
}
// 修改通用请求函数，自动带上 token
const request = (url, method, data = null) => {
	return new Promise((resolve, reject) => {
		uni.request({
			url: buildApiUrl(url),
			method,
			data,
			header: setHeaderToken(),
			success: (res) => {
				if (res.statusCode >= 200 && res.statusCode < 300) {
					resolve(res.data)
				} else {
					// 安全地访问错误信息
					let errorMessage = `请求失败: HTTP ${res.statusCode}`;
					if (res.data && res.data.detail && res.data.detail.error_code) {
						errorMessage = `请求失败: ${res.data.detail.error_code}, ${res.data.detail.detail || ''}`;
					}
					
					uni.showToast({
						title: errorMessage,
						icon: 'none',
						duration: 3000
					})
					reject(new Error(errorMessage))
				}
			},
			fail: (err) => {
				console.error('网络请求错误:', err)
				uni.showToast({
					title: `网络请求失败，请检查网络连接或服务器地址`,
					icon: 'none',
					duration: 3000
				})
				reject(new Error('网络请求失败，请检查网络连接或服务器地址'))
			}
		})
	})
}



export const sendVerificationCode = (phone: string | number | boolean) => {
	return request(`/user_center/account/phone/send-verification-code/?phone=${encodeURIComponent(phone)}`, 'POST')
}

// export const registerPhone = (data) => {
//   console.log('registerPhone: ', data)
//   return request('/user_center/account/phone/register-phone/', 'POST', data)
//     .then((response) => {
//       const loginResponse = response as LoginResponse;
//       if (loginResponse.access_token) {
//         saveTokenToCookie(loginResponse.access_token, loginResponse.refresh_token, loginResponse.user_info);
//       }
//       return loginResponse;
//     });
// }

export const loginPhone = async (data: { phone: string; sms_code: string; }) => {
	console.log('loginPhone: ', data)
	const response = await request('/user_center/account/phone/register-or-login-phone/', 'POST', data);
	const loginResponse = response as LoginResponse;
	if (loginResponse.access_token) {
		console.log("手机号注册登录，loginResponse.access_token = ",loginResponse.access_token);
		saveTokenToCookie(loginResponse.access_token, loginResponse.refresh_token, loginResponse.user_info);
	}
	return loginResponse;
}

