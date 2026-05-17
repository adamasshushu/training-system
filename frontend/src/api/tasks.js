import request from './index'

// ========== 任务 ==========
export function getTasks(params) {
  return request.get('/tasks', { params })
}

export function getTaskDetail(id) {
  return request.get('/tasks/' + id)
}

export function createTask(data) {
  return request.post('/tasks', data)
}

export function updateTask(id, data) {
  return request.put('/tasks/' + id, data)
}

export function deleteTask(id) {
  return request.delete('/tasks/' + id)
}

// ========== 我的任务 ==========
export function getMyTasks() {
  return request.get('/tasks/my')
}

export function getTaskProgress(taskId) {
  return request.get('/tasks/' + taskId + '/progress')
}

// ========== 指派 ==========
export function assignTask(taskId, data) {
  return request.post('/tasks/' + taskId + '/assign', data)
}

export function removeAssignment(taskId, assignmentId) {
  return request.delete('/tasks/' + taskId + '/assign/' + assignmentId)
}
