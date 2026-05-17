import request from './index'

export function login(data) {
  return request.post('/auth/login', data)
}

export function logout() {
  return request.post('/auth/logout')
}

export function getUserInfo() {
  return request.get('/auth/user-info')
}

export function refreshToken(refreshToken) {
  return request.post('/auth/refresh', { refresh_token: refreshToken })
}
