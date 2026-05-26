import request from './index'

/** 获取部门树 */
export function getDepartments() {
  return request.get('/departments')
}

/** 创建部门 */
export function createDepartment(data) {
  return request.post('/departments', data)
}

/** 更新部门 */
export function updateDepartment(id, data) {
  return request.put(`/departments/${id}`, data)
}

/** 删除（停用）部门 */
export function deleteDepartment(id) {
  return request.delete(`/departments/${id}`)
}
