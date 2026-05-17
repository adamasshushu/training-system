<template>
  <div class="file-manager">
    <el-card class="page-card">
      <div class="page-header">
        <h2>📁 文件管理</h2>
        <div class="header-actions">
          <el-upload
            :action="uploadUrl"
            :headers="uploadHeaders"
            :on-success="handleUploadSuccess"
            :on-error="handleUploadError"
            :show-file-list="false"
            :multiple="true"
            :limit="10"
          >
            <el-button type="primary" :icon="Upload">上传文件</el-button>
          </el-upload>
        </div>
      </div>

      <!-- 筛选 -->
      <el-row :gutter="16" class="filter-bar">
        <el-col :span="8">
          <el-select v-model="fileTypeFilter" placeholder="全部类型" clearable @change="loadFiles">
            <el-option label="全部类型" value="" />
            <el-option label="图片" value="image" />
            <el-option label="视频" value="video" />
            <el-option label="文档" value="document" />
            <el-option label="网页" value="html" />
            <el-option label="其他" value="other" />
          </el-select>
        </el-col>
      </el-row>

      <!-- 文件列表 -->
      <el-table :data="files" stripe v-loading="loading" style="width: 100%">
        <el-table-column prop="ID" label="ID" width="60" />
        <el-table-column prop="文件名" label="文件名" min-width="300">
          <template #default="{ row }">
            <div class="file-name-cell">
              <el-icon v-if="row.文件类型 === 'image'" color="#409EFF"><Picture /></el-icon>
              <el-icon v-else-if="row.文件类型 === 'video'" color="#E6A23C"><VideoCamera /></el-icon>
              <el-icon v-else-if="row.文件类型 === 'document'" color="#67C23A"><Document /></el-icon>
              <el-icon v-else-if="row.文件类型 === 'html'" color="#909399"><Link /></el-icon>
              <el-icon v-else><Folder /></el-icon>
              <span class="file-name">{{ row.文件名 }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="文件类型" label="类型" width="80" />
        <el-table-column label="大小" width="100">
          <template #default="{ row }">
            {{ formatSize(row.文件大小) }}
          </template>
        </el-table-column>
        <el-table-column prop="创建时间" label="上传时间" width="180" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link :icon="View" @click="previewFile(row)">预览</el-button>
            <el-button type="primary" link :icon="CopyDocument" @click="copyUrl(row)">复制链接</el-button>
            <el-popconfirm title="确定删除？" @confirm="deleteFile(row)">
              <template #reference>
                <el-button type="danger" link :icon="Delete">删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-if="total > 0"
        v-model:current-page="page"
        :page-size="pageSize"
        :total="total"
        layout="prev, pager, next"
        class="pagination"
        @current-change="loadFiles"
      />
    </el-card>

    <!-- 预览对话框 -->
    <el-dialog v-model="previewVisible" :title="previewFileData?.文件名 || '预览'" width="80%" top="5vh">
      <div class="preview-content">
        <img v-if="isImage" :src="previewFileData?.文件地址" class="preview-image" />
        <video v-else-if="isVideo" :src="previewFileData?.文件地址" controls class="preview-video" />
        <iframe v-else-if="isDoc || isHtml" :src="previewFileData?.文件地址" class="preview-iframe" />
        <el-empty v-else description="该类型不支持预览" />
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Upload, View, CopyDocument, Delete, Picture, VideoCamera, Document, Link, Folder } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { getToken } from '@/utils/auth'
import axios from 'axios'

const API = axios.create({ baseURL: '' })
// Auto-wrap with token
API.interceptors.request.use((config) => {
  config.headers.Authorization = `Bearer ${getToken()}`
  return config
})

const loading = ref(false)
const files = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)
const fileTypeFilter = ref('')

const uploadUrl = '/api/uploads'
const uploadHeaders = computed(() => ({
  Authorization: `Bearer ${getToken()}`
}))

const previewVisible = ref(false)
const previewFileData = ref(null)
const isImage = computed(() => previewFileData.value?.文件类型 === 'image')
const isVideo = computed(() => previewFileData.value?.文件类型 === 'video')
const isDoc = computed(() => previewFileData.value?.文件类型 === 'document')
const isHtml = computed(() => previewFileData.value?.文件类型 === 'html')

const loadFiles = async () => {
  loading.value = true
  try {
    const params = { page: page.value, page_size: pageSize.value }
    if (fileTypeFilter.value) params.file_type = fileTypeFilter.value
    const res = await API.get('/api/uploads', { params })
    files.value = res.data.数据 || []
    total.value = res.data.共计 || 0
  } catch (e) {
    ElMessage.error('加载文件列表失败')
  } finally {
    loading.value = false
  }
}

const handleUploadSuccess = (res) => {
  ElMessage.success(`上传成功: ${res.文件名}`)
  loadFiles()
}

const handleUploadError = () => {
  ElMessage.error('上传失败')
}

const formatSize = (bytes) => {
  if (!bytes) return '0 B'
  const units = ['B', 'KB', 'MB', 'GB']
  let i = 0
  let size = bytes
  while (size >= 1024 && i < units.length - 1) {
    size /= 1024
    i++
  }
  return `${size.toFixed(1)} ${units[i]}`
}

const previewFile = (row) => {
  previewFileData.value = row
  previewVisible.value = true
}

const copyUrl = (row) => {
  navigator.clipboard.writeText(row.文件地址).then(() => {
    ElMessage.success('链接已复制')
  })
}

const deleteFile = async (row) => {
  try {
    await API.delete(`/api/uploads/${row.ID}`)
    ElMessage.success('已删除')
    loadFiles()
  } catch {
    ElMessage.error('删除失败')
  }
}

onMounted(loadFiles)
</script>

<style scoped>
.file-manager {
  max-width: 1200px;
  margin: 0 auto;
}
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}
.page-header h2 {
  margin: 0;
  font-size: 18px;
  color: #303133;
}
.filter-bar {
  margin-bottom: 16px;
}
.file-name-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}
.file-name {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.pagination {
  margin-top: 16px;
  display: flex;
  justify-content: center;
}
.preview-image {
  max-width: 100%;
  max-height: 70vh;
  display: block;
  margin: 0 auto;
}
.preview-video {
  width: 100%;
  max-height: 70vh;
}
.preview-iframe {
  width: 100%;
  height: 70vh;
  border: none;
}
.preview-content {
  min-height: 200px;
}
</style>
