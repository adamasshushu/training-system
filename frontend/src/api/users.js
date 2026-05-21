import request from './index'

/**
 * 用户管理 API
 * 后端使用中文字段名
 */
export function getUsers(params = {}) {
  return request.get('/users', { params })
}

export function createUser(data) {
  return request.post('/users', data)
}

export function updateUser(id, data) {
  return request.put(`/users/${id}`, data)
}

/** 停用/启用用户 */
export function deleteUser(id) {
  return request.delete(`/users/${id}`)
}

/** 管理员重置用户密码 */
export function resetUserPassword(id, newPassword) {
  return request.put(`/users/${id}/password`, { new_password: newPassword })
}

/** 永久删除用户 */
export function permanentDeleteUser(id) {
  return request.delete(`/users/${id}/permanent`)
}
