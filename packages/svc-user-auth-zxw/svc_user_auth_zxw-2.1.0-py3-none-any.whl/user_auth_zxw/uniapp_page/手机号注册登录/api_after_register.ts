import request from '@/utils/request'

// 定义API根地址
const API_BASE_URL = 'http://192.168.10.102:8109';

// 定义接口返回数据类型
interface UpdateTeacherInfoResponse {
	message : string
	status : string
}

/**
 * 首次注册增加默认权限
 * @param referrerId 邀请人id (可选)
 */
export const updateTeacherInfo = async (referrerId ?: number) : Promise<UpdateTeacherInfoResponse> => {
	let url = `${API_BASE_URL}/user_center/update-teacher-info`;

	if (referrerId) {
		url = `${url}?referrer_id=${referrerId}`;
	}

	const req = await request({
		url: url,
		method: 'GET'
	})
	console.log("首次注册后，添加教师信息成功，返回= ", req)
	return req['data'] as UpdateTeacherInfoResponse
}