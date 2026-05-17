<template>
  <div class="student-layout">
    <!-- 顶部导航 -->
    <header class="student-header">
      <div class="header-inner">
        <div class="header-left">
          <router-link to="/student/dashboard" class="logo">
            <el-icon :size="28" color="#409EFF"><School /></el-icon>
            <span class="logo-text">培训平台</span>
          </router-link>
          <nav class="main-nav">
            <router-link
              v-for="item in navItems"
              :key="item.path"
              :to="item.path"
              class="nav-item"
              :class="{ active: currentPath.startsWith(item.path) }"
            >
              <el-icon :size="18"><component :is="item.icon" /></el-icon>
              <span>{{ item.label }}</span>
            </router-link>
          </nav>
        </div>
        <div class="header-right">
          <el-badge :value="unreadCount" :hidden="unreadCount === 0" class="notif-badge">
            <el-button :icon="Bell" circle @click="$router.push('/student/notifications')" />
          </el-badge>
          <el-dropdown trigger="click">
            <span class="user-profile">
              <el-avatar :size="32" icon="UserFilled" />
              <span class="user-name">学员</span>
              <el-icon><ArrowDown /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item divided @click="handleLogout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </div>
    </header>

    <!-- 主体内容 -->
    <main class="student-main">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { computed, ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { removeToken } from '@/utils/auth'
import { ElMessageBox } from 'element-plus'
import { Bell } from '@element-plus/icons-vue'
import axios from 'axios'
import { getToken } from '@/utils/auth'

const route = useRoute()
const router = useRouter()
const currentPath = computed(() => route.path)
const unreadCount = ref(0)

const API = axios.create({ baseURL: '' })
API.interceptors.request.use((c) => { c.headers.Authorization = `Bearer ${getToken()}`; return c })

const navItems = [
  { path: '/student/dashboard', label: '我的学习', icon: 'HomeFilled' },
  { path: '/student/courses', label: '课程中心', icon: 'Reading' },
  { path: '/student/exams', label: '我的考试', icon: 'EditPen' },
  { path: '/student/tasks', label: '我的任务', icon: 'List' },
  { path: '/student/bookmarks', label: '收藏笔记', icon: 'Star' },
  { path: '/student/knowledge-graph', label: '知识图谱', icon: 'Connection' },
  { path: '/student/feedback', label: '评价反馈', icon: 'ChatLineSquare' },
  { path: '/student/certificates', label: '我的证书', icon: 'Medal' }
]

const loadUnreadCount = async () => {
  try {
    const res = await API.get('/api/notifications/unread-count')
    unreadCount.value = res.data.未读数 || 0
  } catch { /* silent */ }
}

const handleLogout = async () => {
  try {
    await ElMessageBox.confirm('确定要退出登录吗？', '提示', { type: 'warning' })
    removeToken()
    router.push('/login')
  } catch {}
}

onMounted(loadUnreadCount)
</script>

<style scoped>
.student-layout {
  min-height: 100vh;
  background: #f5f7fa;
}

.student-header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 100;
  background: #fff;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
}

.header-inner {
  max-width: 1280px;
  margin: 0 auto;
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 40px;
}

.logo {
  display: flex;
  align-items: center;
  gap: 8px;
  text-decoration: none;
}

.logo-text {
  font-size: 20px;
  font-weight: 700;
  color: #303133;
}

.main-nav {
  display: flex;
  align-items: center;
  gap: 4px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border-radius: 8px;
  text-decoration: none;
  font-size: 15px;
  color: #606266;
  transition: all 0.2s;
}

.nav-item:hover {
  background: #f0f5ff;
  color: #409EFF;
}

.nav-item.active {
  background: #ecf5ff;
  color: #409EFF;
  font-weight: 600;
}

.header-right {
  display: flex;
  align-items: center;
}

.user-profile {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.user-name {
  font-size: 14px;
  color: #606266;
}

.notif-badge {
  margin-right: 16px;
}

.student-main {
  padding-top: 64px;
  min-height: 100vh;
}

@media (max-width: 768px) {
  .main-nav {
    display: none;
  }
}
</style>
