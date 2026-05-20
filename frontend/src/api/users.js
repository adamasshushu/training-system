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

export function deleteUser(id) {
  return request.delete(`/users/${id}`)
}
