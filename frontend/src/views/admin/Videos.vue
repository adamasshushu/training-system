<template>
  <div class="video-manager">
    <div class="page-header">
      <div>
        <h2 class="page-title">视频管理</h2>
        <p class="page-subtitle">管理所有教学视频</p>
      </div>
      <div class="page-actions">
        <el-button type="primary" @click="showUploadDialog = true">
          <el-icon><Upload /></el-icon>上传视频
        </el-button>
      </div>
    </div>

    <!-- 搜索与筛选 -->
    <el-card shadow="never" class="filter-card">
      <el-row :gutter="12" align="middle">
        <el-col :span="8">
          <el-input
            v-model="searchKeyword"
            placeholder="搜索视频名称..."
            :prefix-icon="Search"
            clearable
            @input="handleSearch"
          />
        </el-col>
        <el-col :span="12">
          <div class="sort-options">
            <span class="sort-label">排序：</span>
            <el-radio-group v-model="sortOrder" size="small" @change="fetchVideos">
              <el-radio-button value="newest">最新上传</el-radio-button>
              <el-radio-button value="oldest">最早上传</el-radio-button>
              <el-radio-button value="largest">最大文件</el-radio-button>
              <el-radio-button value="smallest">最小文件</el-radio-button>
            </el-radio-group>
          </div>
        </el-col>
        <el-col :span="4" style="text-align: right;">
          <span class="total-count">共 {{ total }} 个视频</span>
        </el-col>
      </el-row>
    </el-card>

    <!-- 视频网格 -->
    <div class="video-grid" v-loading="loading">
      <div v-if="videos.length === 0 && !loading" class="empty-state">
        <el-empty description="暂无视频" />
      </div>

      <div
        v-for="video in videos"
        :key="video.ID"
        class="video-card"
        @click="previewVideo(video)"
      >
        <div class="video-thumbnail">
          <div class="video-thumb-icon">
            <el-icon :size="40"><VideoCameraFilled /></el-icon>
          </div>
          <div class="video-duration-badge" v-if="video.时长">
            {{ video.时长 }}
          </div>
          <div class="video-play-overlay">
            <el-icon :size="48" color="white"><VideoPlay /></el-icon>
          </div>
        </div>
        <div class="video-info">
          <h3 class="video-title" :title="video.文件名">{{ video.文件名 }}</h3>
          <div class="video-meta">
            <span class="video-size">{{ formatSize(video.文件大小) }}</span>
            <span class="video-date">{{ formatDate(video.创建时间) }}</span>
          </div>
        </div>
        <div class="video-actions">
          <el-tooltip content="复制视频链接" placement="top">
            <el-button circle size="small" @click.stop="copyLink(video)">
              <el-icon><Link /></el-icon>
            </el-button>
          </el-tooltip>
          <el-popconfirm
            title="确定要删除这个视频吗？"
            confirm-button-text="删除"
            @confirm="handleDelete(video)"
          >
            <template #reference>
              <el-button circle size="small" type="danger" plain @click.stop>
                <el-icon><Delete /></el-icon>
              </el-button>
            </template>
          </el-popconfirm>
        </div>
      </div>
    </div>

    <!-- 分页 -->
    <div class="pagination-wrapper" v-if="total > pageSize">
      <el-pagination
        v-model:current-page="currentPage"
        :page-size="pageSize"
        :total="total"
        layout="prev, pager, next"
        @current-change="fetchVideos"
      />
    </div>

    <!-- 上传对话框 -->
    <el-dialog
      v-model="showUploadDialog"
      title="上传视频"
      width="520px"
      :close-on-click-modal="false"
    >
      <el-upload
        ref="uploadRef"
        drag
        :auto-upload="false"
        :limit="1"
        :on-change="onFileChange"
        :before-upload="beforeUpload"
        accept="video/*"
        class="upload-area"
      >
        <el-icon class="upload-icon" :size="48"><UploadFilled /></el-icon>
        <div class="upload-text">
          <span>将视频文件拖拽到此处，或<em>点击选择</em></span>
        </div>
        <template #tip>
          <div class="upload-tip">
            支持 MP4, AVI, MOV, WMV, FLV, MKV, WebM 格式，单个文件最大 {{ maxSizeMB }}MB
          </div>
        </template>
      </el-upload>

      <el-form
        v-if="selectedFile"
        :model="uploadForm"
        label-width="80px"
        style="margin-top: 16px;"
      >
        <el-form-item label="视频名称">
          <el-input v-model="uploadForm.title" placeholder="留空则使用文件名" />
        </el-form-item>
        <el-form-item label="文件信息">
          <span class="file-info">{{ selectedFile.name }}（{{ formatSize(selectedFile.size) }}）</span>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showUploadDialog = false">取消</el-button>
        <el-button type="primary" :loading="uploading" @click="handleUpload">
          {{ uploading ? '上传中...' : '开始上传' }}
        </el-button>
      </template>
    </el-dialog>

    <!-- 视频预览对话框 -->
    <el-dialog
      v-model="showPreviewDialog"
      :title="previewVideoTitle"
      width="800px"
      :close-on-click-modal="false"
      top="5vh"
    >
      <div class="preview-container">
        <video
          v-if="previewVideoUrl"
          :src="previewVideoUrl"
          controls
          autoplay
          class="preview-video"
        >
          您的浏览器不支持视频播放
        </video>
        <div v-else class="preview-error">
          <el-icon :size="48" color="#ef4444"><VideoCameraFilled /></el-icon>
          <p>无法加载视频</p>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, Upload, UploadFilled, VideoCameraFilled, VideoPlay, Link, Delete } from '@element-plus/icons-vue'
import { getVideos, uploadVideo, deleteVideo, getVideoStreamUrl } from '@/api/videos'

const loading = ref(false)
const videos = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)
const searchKeyword = ref('')
const sortOrder = ref('newest')

// Upload state
const showUploadDialog = ref(false)
const uploadRef = ref(null)
const selectedFile = ref(null)
const uploadForm = ref({ title: '' })
const uploading = ref(false)
const maxSizeMB = computed(() => Math.floor(500))

// Preview state
const showPreviewDialog = ref(false)
const previewVideoTitle = ref('')
const previewVideoUrl = ref('')

const fetchVideos = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value,
    }
    if (searchKeyword.value) {
      params.keyword = searchKeyword.value
    }
    const res = await getVideos(params)
    videos.value = res.数据 || []
    total.value = res.共计 || 0
  } catch {
    ElMessage.error('加载视频列表失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  currentPage.value = 1
  fetchVideos()
}

const onFileChange = (uploadFile) => {
  selectedFile.value = uploadFile.raw
}

const beforeUpload = (file) => {
  const isVideo = file.type.startsWith('video/')
  if (!isVideo) {
    ElMessage.error('请上传视频文件')
    return false
  }
  const isLt500M = file.size / 1024 / 1024 < 500
  if (!isLt500M) {
    ElMessage.error('视频大小不能超过500MB')
    return false
  }
  return true
}

const handleUpload = async () => {
  if (!selectedFile.value) {
    ElMessage.warning('请选择要上传的视频文件')
    return
  }

  uploading.value = true
  try {
    const title = uploadForm.value.title || selectedFile.value.name
    await uploadVideo(selectedFile.value, title)
    ElMessage.success('视频上传成功')
    showUploadDialog.value = false
    selectedFile.value = null
    uploadForm.value = { title: '' }
    fetchVideos()
  } catch {
    ElMessage.error('视频上传失败')
  } finally {
    uploading.value = false
  }
}

const handleDelete = async (video) => {
  try {
    await deleteVideo(video.ID)
    ElMessage.success('视频已删除')
    fetchVideos()
  } catch {
    ElMessage.error('删除视频失败')
  }
}

const previewVideo = (video) => {
  previewVideoTitle.value = video.文件名
  previewVideoUrl.value = getVideoStreamUrl(video.存储路径)
  showPreviewDialog.value = true
}

const copyLink = (video) => {
  const url = `${window.location.origin}${getVideoStreamUrl(video.存储路径)}`
  navigator.clipboard.writeText(url).then(() => {
    ElMessage.success('视频链接已复制')
  }).catch(() => {
    ElMessage.info(url)
  })
}

const formatSize = (bytes) => {
  if (!bytes) return '未知'
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  if (bytes < 1024 * 1024 * 1024) return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
  return (bytes / (1024 * 1024 * 1024)).toFixed(2) + ' GB'
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  try {
    const date = new Date(dateStr)
    return date.toLocaleDateString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit' })
  } catch {
    return dateStr
  }
}

onMounted(fetchVideos)
</script>

<style scoped>
.video-manager {
  max-width: 1200px;
}

.page-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 20px;
}

.page-title {
  font-size: 24px;
  font-weight: 700;
  color: #1a1a2e;
  margin-bottom: 4px;
  letter-spacing: -0.3px;
}

.page-subtitle {
  font-size: 14px;
  color: #94a3b8;
  margin: 0;
}

.page-actions {
  display: flex;
  gap: 8px;
}

.filter-card {
  margin-bottom: 20px;
}

.sort-options {
  display: flex;
  align-items: center;
  gap: 8px;
}

.sort-label {
  font-size: 14px;
  color: #64748b;
  white-space: nowrap;
}

.total-count {
  font-size: 14px;
  color: #94a3b8;
}

/* Video Grid */
.video-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
  min-height: 200px;
}

.video-card {
  background: #fff;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  overflow: hidden;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  position: relative;
}

.video-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 25px rgba(108,92,231,0.1);
  border-color: #c4bdf7;
}

.video-thumbnail {
  position: relative;
  height: 170px;
  background: linear-gradient(135deg, #1a1a2e, #2a2166);
  display: flex;
  align-items: center;
  justify-content: center;
}

.video-thumb-icon {
  color: rgba(162, 155, 254, 0.4);
}

.video-play-overlay {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(26, 26, 46, 0.4);
  opacity: 0;
  transition: opacity 0.3s;
}

.video-card:hover .video-play-overlay {
  opacity: 1;
}

.video-duration-badge {
  position: absolute;
  bottom: 8px;
  right: 8px;
  background: rgba(0, 0, 0, 0.7);
  color: #fff;
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 4px;
}

.video-info {
  padding: 12px 14px;
}

.video-title {
  font-size: 14px;
  font-weight: 600;
  color: #1a1a2e;
  margin: 0 0 6px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.video-meta {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #94a3b8;
}

.video-actions {
  position: absolute;
  top: 8px;
  right: 8px;
  display: flex;
  gap: 4px;
  opacity: 0;
  transition: opacity 0.2s;
}

.video-card:hover .video-actions {
  opacity: 1;
}

.empty-state {
  grid-column: 1 / -1;
  display: flex;
  justify-content: center;
  padding: 60px 0;
}

/* Pagination */
.pagination-wrapper {
  display: flex;
  justify-content: center;
  margin-top: 24px;
}

/* Upload area */
.upload-area {
  width: 100%;
}

.upload-icon {
  color: #6C5CE7;
  margin-bottom: 8px;
}

.upload-text {
  font-size: 14px;
  color: #64748b;
}
.upload-text em {
  color: #6C5CE7;
  font-style: normal;
  font-weight: 600;
}

.upload-tip {
  font-size: 12px;
  color: #94a3b8;
  margin-top: 8px;
  text-align: center;
}

.file-info {
  font-size: 13px;
  color: #64748b;
}

/* Preview */
.preview-container {
  background: #0f0f1a;
  border-radius: 8px;
  overflow: hidden;
}

.preview-video {
  width: 100%;
  display: block;
  max-height: 60vh;
}

.preview-error {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px;
  color: #94a3b8;
  gap: 12px;
}
</style>
