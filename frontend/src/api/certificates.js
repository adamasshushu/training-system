import request from './index'

// ========== 模板 ==========
export function getTemplates() {
  return request.get('/certificates/templates')
}

export function createTemplate(data) {
  return request.post('/certificates/templates', data)
}

export function updateTemplate(id, data) {
  return request.put('/certificates/templates/' + id, data)
}

export function deleteTemplate(id) {
  return request.delete('/certificates/templates/' + id)
}

// ========== 证书 ==========
export function getCertificates() {
  return request.get('/certificates')
}

export function issueCertificate(data) {
  return request.post('/certificates/issue', data)
}

export function getMyCertificates() {
  return request.get('/certificates/my')
}

// ========== 看板 ==========
export function getStats() {
  return request.get('/certificates/stats')
}
