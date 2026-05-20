<template>
  <div class="fetch-url">
    <el-card class="page-card">
      <div class="page-header">
        <h2>🔗 网址抓取</h2>
        <p class="page-desc">输入网页地址，自动抓取内容并保存为HTML副本到本地</p>
      </div>

      <el-form label-position="top" @submit.prevent="fetchUrl">
        <el-row :gutter="16">
          <el-col :span="18">
            <el-form-item label="网页地址">
              <el-input
                v-model="url"
                placeholder="https://example.com"
                size="large"
                clearable
              >
                <template #prefix>
                  <el-icon><Link /></el-icon>
                </template>
              </el-input>
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="自定义标题（可选）">
              <el-input v-model="customTitle" placeholder="留空自动获取" size="large" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item>
          <el-button type="primary" size="large" @click="fetchUrl" :loading="fetching" :icon="Link">
            {{ fetching ? '抓取中...' : '开始抓取' }}
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 历史抓取记录 -->
    <el-card class="history-card" style="margin-top: 16px">
      <template #header>
        <span>📋 抓取历史</span>
      </template>

      <el-table :data="history" v-loading="loadingHistory" border stripe>
        <el-table-column prop="ID" label="ID" width="60" />
        <el-table-column label="标题" min-width="250">
          <template #default="{ row }">
            <div class="title-cell">
              <el-icon><Link /></el-icon>
              <span>{{ row.来源网址 ? extractTitleFrom(row) : '未命名' }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="来源" min-width="250">
          <template #default="{ row }">
            <a :href="row.来源网址" target="_blank" class="source-link">
              {{ row.来源网址 }}
            </a>
          </template>
        </el-table-column>
        <el-table-column prop="文件大小" label="大小" width="100">
          <template #default="{ row }">
            {{ formatSize(row.文件大小) }}
          </template>
        </el-table-column>
        <el-table-column prop="创建时间" label="抓取时间" width="180" />
        <el-table-column label="操作" width="160" fixed="right">
          <template #default="{ row }">
            <el-button text size="small" type="primary" @click="openFile(row)">查看</el-button>
            <el-button text size="small" type="primary" @click="copyUrl(row)">复制链接</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Link } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { getToken } from '@/utils/auth'
import axios from 'axios'

const API = axios.create({ baseURL: '' })
API.interceptors.request.use((config) => {
  config.headers.Authorization = `Bearer ${getToken()}`
  return config
})

const url = ref('')
const customTitle = ref('')
const fetching = ref(false)
const history = ref([])
const loadingHistory = ref(false)

const fetchUrl = async () => {
  if (!url.value.trim()) {
    ElMessage.warning('请输入网址')
    return
  }

  // 检查URL格式
  let targetUrl = url.value.trim()
  if (!targetUrl.startsWith('http://') && !targetUrl.startsWith('https://')) {
    targetUrl = 'https://' + targetUrl
  }

  fetching.value = true
  try {
    const res = await API.post('/api/fetch-url', {
      url: targetUrl,
      title: customTitle.value || undefined
    })
    ElMessage.success(`抓取成功: ${res.data.标题}`)
    url.value = ''
    customTitle.value = ''
    loadHistory()
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '抓取失败，请检查网址')
  } finally {
    fetching.value = false
  }
}

const loadHistory = async () => {
  loadingHistory.value = true
  try {
    const res = await API.get('/api/uploads', { params: { file_type: 'html', page_size: 50 } })
    history.value = res.data.数据 || []
  } catch {
    // silent
  } finally {
    loadingHistory.value = false
  }
}

const extractTitleFrom = (row) => {
  const name = row.文件名 || ''
  return name.replace(/\.html$/i, '').split('_')[0] || row.文件名
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

const openFile = (row) => {
  window.open(row.文件地址, '_blank')
}

const copyUrl = (row) => {
  navigator.clipboard.writeText(row.文件地址).then(() => {
    ElMessage.success('链接已复制')
  })
}

onMounted(loadHistory)
</script>

<style scoped>
.fetch-url {
  max-width: 1200px;
  margin: 0 auto;
}
.page-header {
  margin-bottom: 16px;
}
.page-header h2 {
  margin: 0;
  font-size: 18px;
  color: var(--text-primary);
}
.page-desc {
  font-size: 13px;
  color: var(--text-tertiary);
  margin-top: 6px;
}
.title-cell {
  display: flex;
  align-items: center;
  gap: 6px;
}
.source-link {
  color: var(--text-link);
  text-decoration: none;
  font-size: 13px;
}
.source-link:hover {
  text-decoration: underline;
}
</style>
