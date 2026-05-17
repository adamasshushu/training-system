<template>
  <div class="notifications-page">
    <el-card class="page-card">
      <div class="page-header">
        <h2>🔔 我的通知</h2>
        <el-button v-if="unreadCount > 0" size="small" @click="markAllRead">全部已读</el-button>
      </div>

      <el-tabs v-model="filterTab" @tab-change="loadNotifications">
        <el-tab-pane label="全部" name="all" />
        <el-tab-pane :label="`未读 (${unreadCount})`" name="unread" />
      </el-tabs>

      <div v-if="notifications.length === 0" class="empty-state">
        <el-empty description="暂无通知" />
      </div>

      <div v-else class="notif-list">
        <div
          v-for="item in notifications"
          :key="item.ID"
          class="notif-item"
          :class="{ unread: !item.已读 }"
          @click="markRead(item)"
        >
          <div class="notif-dot" v-if="!item.已读" />
          <div class="notif-body">
            <div class="notif-title">{{ item.标题 }}</div>
            <div class="notif-content">{{ item.内容 }}</div>
            <div class="notif-time">{{ item.创建时间 }}</div>
          </div>
        </div>
      </div>

      <el-pagination
        v-if="total > pageSize"
        v-model:current-page="page"
        :page-size="pageSize"
        :total="total"
        layout="prev, pager, next"
        class="pagination"
        @current-change="loadNotifications"
      />
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getToken } from '@/utils/auth'
import axios from 'axios'

const API = axios.create({ baseURL: '' })
API.interceptors.request.use((c) => { c.headers.Authorization = `Bearer ${getToken()}`; return c })

const notifications = ref([])
const total = ref(0)
const unreadCount = ref(0)
const page = ref(1)
const pageSize = ref(20)
const filterTab = ref('all')

const loadNotifications = async () => {
  try {
    const params = { page: page.value, page_size: pageSize.value }
    if (filterTab.value === 'unread') params.unread_only = true
    const res = await API.get('/api/notifications', { params })
    notifications.value = res.data.数据 || []
    total.value = res.data.共计 || 0
    unreadCount.value = res.data.未读数 || 0
  } catch { /* silent */ }
}

const markRead = async (item) => {
  if (item.已读) return
  try {
    await API.put(`/api/notifications/${item.ID}/read`)
    item.已读 = true
    unreadCount.value = Math.max(0, unreadCount.value - 1)
  } catch { /* silent */ }
}

const markAllRead = async () => {
  try {
    await API.put('/api/notifications/read-all')
    ElMessage.success('全部已读')
    loadNotifications()
  } catch { /* silent */ }
}

onMounted(loadNotifications)
</script>

<style scoped>
.notifications-page { max-width: 800px; margin: 0 auto; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
.page-header h2 { margin: 0; font-size: 18px; }
.empty-state { padding: 60px 0; display: flex; justify-content: center; }
.notif-list { display: flex; flex-direction: column; gap: 2px; }
.notif-item {
  display: flex; align-items: flex-start; gap: 12px;
  padding: 16px; border-radius: 8px; cursor: pointer;
  transition: background 0.2s;
}
.notif-item:hover { background: #f5f7fa; }
.notif-item.unread { background: #ecf5ff; }
.notif-item.unread:hover { background: #d9ecff; }
.notif-dot {
  width: 8px; height: 8px; border-radius: 50%;
  background: #409EFF; flex-shrink: 0; margin-top: 6px;
}
.notif-body { flex: 1; min-width: 0; }
.notif-title { font-size: 14px; font-weight: 600; color: #303133; margin-bottom: 4px; }
.notif-content { font-size: 13px; color: #606266; margin-bottom: 4px; white-space: pre-wrap; }
.notif-time { font-size: 12px; color: #c0c4cc; }
.pagination { margin-top: 16px; display: flex; justify-content: center; }
</style>
