import request from './index'

/**
 * 视频管理 API
 */

// 获取视频列表
export function getVideos(params = {}) {
  return request.get('/videos', { params })
}

// 获取单个视频
export function getVideo(id) {
  return request.get(`/videos/${id}`)
}

// 获取视频流地址（直接播放URL）
export function getVideoStreamUrl(filePath) {
  return `/api/videos/stream/${filePath}`
}

// 上传视频
export function uploadVideo(file, title) {
  const formData = new FormData()
  formData.append('file', file)
  if (title) {
    formData.append('title', title)
  }
  return request.post('/videos', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: 120000 // 2分钟超时
  })
}

// 删除视频
export function deleteVideo(id) {
  return request.delete(`/videos/${id}`)
}
