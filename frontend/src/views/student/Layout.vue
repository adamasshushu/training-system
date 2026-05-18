<template>
  <div class="student-layout">
    <!-- 顶部导航 -->
    <header class="student-header">
      <div class="header-inner">
        <div class="header-left">
          <router-link to="/student/dashboard" class="logo">
            <svg width="32" height="32" viewBox="0 0 32 32" fill="none">
              <rect width="32" height="32" rx="8" fill="url(#student-brand)" />
              <path d="M9 19V12l7-4 7 4v7l-7 4-7-4z" stroke="white" stroke-width="1.5" fill="rgba(255,255,255,0.12)"/>
              <path d="M16 14v5.5m-3-2.75h6" stroke="white" stroke-width="1.5" stroke-linecap="round"/>
              <defs>
                <linearGradient id="student-brand" x1="0" y1="0" x2="32" y2="32">
                  <stop stop-color="#6C5CE7"/>
                  <stop offset="1" stop-color="#a29bfe"/>
                </linearGradient>
              </defs>
            </svg>
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
            <el-button :icon="Bell" circle @click="$router.push('/student/notifications')" class="notif-btn" />
          </el-badge>
          <el-dropdown trigger="click">
            <span class="user-profile">
              <el-avatar :size="32" icon="UserFilled" class="user-avatar" />
              <span class="user-name">{{ userName }}</span>
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

    <!-- 移动端底部导航 -->
    <nav class="mobile-bottom-nav">
      <router-link
        v-for="item in bottomNavItems"
        :key="item.path"
        :to="item.path"
        class="bottom-nav-item"
        :class="{ active: currentPath.startsWith(item.path) }"
      >
        <el-icon :size="22"><component :is="item.icon" /></el-icon>
        <span>{{ item.label }}</span>
      </router-link>
    </nav>
  </div>
</template>

<script setup>
import { computed, ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { removeToken, getUser } from '@/utils/auth'
import { ElMessageBox } from 'element-plus'
import { Bell } from '@element-plus/icons-vue'
import axios from 'axios'
import { getToken } from '@/utils/auth'

const route = useRoute()
const router = useRouter()
const currentPath = computed(() => route.path)
const unreadCount = ref(0)
const userInfo = ref(getUser() || {})
const userName = computed(() => userInfo.value?.真实姓名 || userInfo.value?.real_name || '学员')

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

const bottomNavItems = [
  { path: '/student/dashboard', label: '学习', icon: 'HomeFilled' },
  { path: '/student/courses', label: '课程', icon: 'Reading' },
  { path: '/student/exams', label: '考试', icon: 'EditPen' },
  { path: '/student/tasks', label: '任务', icon: 'List' },
  { path: '/student/certificates', label: '证书', icon: 'Medal' }
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
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  border-bottom: 1px solid #e2e8f0;
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
  gap: 10px;
  text-decoration: none;
}

.logo-text {
  font-size: 20px;
  font-weight: 800;
  color: #1a1a2e;
  letter-spacing: -0.5px;
}

.main-nav {
  display: flex;
  align-items: center;
  gap: 2px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  border-radius: 8px;
  text-decoration: none;
  font-size: 14px;
  font-weight: 500;
  color: #64748b;
  transition: all 0.2s;
}

.nav-item:hover {
  background: #f8f9ff;
  color: #6C5CE7;
}

.nav-item.active {
  background: #eef0ff;
  color: #6C5CE7;
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

.user-avatar {
  background: linear-gradient(135deg, #6C5CE7, #a29bfe);
}

.user-name {
  font-size: 14px;
  color: #475569;
  font-weight: 500;
}

.notif-badge {
  margin-right: 16px;
}

.notif-btn {
  --el-button-bg-color: transparent;
  --el-button-border-color: transparent;
  color: #64748b;
}
.notif-btn:hover {
  color: #6C5CE7;
  background: #eef0ff;
}

.student-main {
  padding-top: 64px;
  min-height: 100vh;
  padding-bottom: 0;
}

/* Mobile bottom navigation */
.mobile-bottom-nav {
  display: none;
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: 100;
  background: #fff;
  border-top: 1px solid #e2e8f0;
  padding: 6px 0 env(safe-area-inset-bottom);
  justify-content: space-around;
}

.bottom-nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
  padding: 6px 10px;
  text-decoration: none;
  font-size: 11px;
  color: #94a3b8;
  transition: all 0.2s;
  border-radius: 8px;
}

.bottom-nav-item.active {
  color: #6C5CE7;
}

@media (max-width: 768px) {
  .main-nav {
    display: none;
  }
  .student-main {
    padding-bottom: 64px;
  }
  .mobile-bottom-nav {
    display: flex;
  }
}
</style>
