<template>
	<view class="login-container">
		<view class="logo-area">
			<image class="logo" src="/static/logo.png" mode="aspectFit" />
		</view>

		<view class="form-area">
			<view class="input-group">
				<uni-icons type="phone-filled" size="24" color="#999" />
				<input type="number" v-model="phone" placeholder="请输入手机号" maxlength="11" />
			</view>

			<view class="input-group">
				<uni-icons type="locked-filled" size="24" color="#999" />
				<input type="number" v-model="code" placeholder="请输入验证码" maxlength="6" />
				<button class="code-btn" @click="getCode" :disabled="codeBtnDisabled">
					{{ codeBtnText }}
				</button>
			</view>

			<button class="login-btn" @click="login" :disabled="!isFormValid">
				登录
			</button>
		</view>
		<!-- 
		<view class="other-login">
			<text>其他登录方式</text>
			<view class="icon-group">
				<uni-icons type="weixin" size="32" color="#07c160" />
				<uni-icons type="qq" size="32" color="#12b7f5" />
			</view>
		</view> -->
	</view>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { sendVerificationCode, loginPhone } from './apis.ts'
import { updateTeacherInfo } from './api_after_register.ts'
import { getAndStoreReferrerId } from '@/src/utils/request/refererID.ts'

const phone = ref('')
const code = ref('')
const codeBtnText = ref('获取验证码')
const codeBtnDisabled = ref(false)

const isFormValid = computed(() => {
	return phone.value.length === 11 && code.value.length === 4
})

const referrerId = ref(null)

onMounted(() => {
	const pages = getCurrentPages()
	const currentPage = pages[pages.length - 1]
	const fullPath = currentPage.$page.fullPath
	getAndStoreReferrerId(fullPath).then(id => {
		referrerId.value = id
	})
})

const getCode = async () => {
	if (phone.value.length !== 11) {
		uni.showToast({
			title: '请输入正确的手机号',
			icon: 'none'
		})
		return
	}

	codeBtnDisabled.value = true
	try {
		await sendVerificationCode(phone.value)
		uni.showToast({
			title: '验证码已发送',
			icon: 'success'
		})
		let countdown = 60
		const timer = setInterval(() => {
			codeBtnText.value = `${countdown}秒后重试`
			countdown--
			if (countdown < 0) {
				clearInterval(timer)
				codeBtnText.value = '获取验证码'
				codeBtnDisabled.value = false
			}
		}, 1000)
	} catch (error) {
		uni.showToast({
			title: '发送验证码失败',
			icon: 'none'
		})
		codeBtnDisabled.value = false
	}
}

const login = async () => {
	if (!isFormValid.value) {
		uni.showToast({
			title: '请填写完整信息',
			icon: 'none'
		})
		return
	}

	try {
		const result = await loginPhone({
			phone: phone.value,
			sms_code: code.value
		})

		if (result.access_token) {
			uni.showToast({
				title: '登录成功',
				icon: 'success'
			})
			// 调用首次注册api
			console.log("首次注册成功，执行调用首次注册api");
			await updateTeacherInfo(referrerId.value);
			console.log("首次注册api调用完毕...");
			// 这里可以添加登录成功后的逻辑，比如跳转到首页
			uni.switchTab({
				url:"/pages/p6_personal-center/p1-index"
			})
			// uni.navigateBack()
		}
	} catch (error) {

	}
}
</script>

<style scoped>
.login-container {
	padding: 40rpx;
	display: flex;
	flex-direction: column;
	min-height: 89vh;
	background-color: #f8f8f8;
}

.logo-area {
	text-align: center;
	margin-bottom: 60rpx;
}

.logo {
	width: 200rpx;
	height: 200rpx;
}

.form-area {
	background-color: #fff;
	border-radius: 16rpx;
	padding: 40rpx;
	box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.05);
}

.input-group {
	display: flex;
	align-items: center;
	border-bottom: 1rpx solid #eee;
	padding: 20rpx 0;
	margin-bottom: 30rpx;
}

.input-group input {
	flex: 1;
	margin-left: 20rpx;
	font-size: 28rpx;
}

.code-btn {
	font-size: 24rpx;
	background-color: #007aff;
	color: #fff;
	padding: 10rpx 20rpx;
	border-radius: 30rpx;
}

.login-btn {
	width: 100%;
	background-color: #007aff;
	color: #fff;
	font-size: 32rpx;
	padding: 20rpx 0;
	border-radius: 40rpx;
	margin-top: 40rpx;
}

.other-login {
	margin-top: auto;
	text-align: center;
}

.other-login text {
	font-size: 24rpx;
	color: #999;
	margin-bottom: 20rpx;
	display: block;
}

.icon-group {
	display: flex;
	justify-content: center;
	gap: 40rpx;
}
</style>