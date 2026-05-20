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
          <!-- 暗黑模式切换 -->
          <el-tooltip :content="isDark ? '切换亮色' : '切换暗黑'" placement="bottom">
            <el-button
              :icon="isDark ? Sunny : Moon"
              circle
              class="nav-icon-btn"
              @click="toggleTheme"
            />
          </el-tooltip>

          <el-badge :value="unreadCount" :hidden="unreadCount === 0" class="notif-badge">
            <el-button :icon="Bell" circle class="nav-icon-btn" @click="$router.push('/student/notifications')" />
          </el-badge>
          <el-dropdown trigger="click">
            <span class="user-profile">
              <el-avatar :size="32" class="user-avatar">{{ userName.charAt(0) }}</el-avatar>
              <span class="user-name">{{ userName }}</span>
              <el-icon><ArrowDown /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item class="user-menu-header" disabled>
                  <div class="menu-user-info">
                    <el-avatar :size="36" class="menu-avatar">{{ userName.charAt(0) }}</el-avatar>
                    <div>
                      <div class="menu-user-name">{{ userName }}</div>
                      <div class="menu-user-role">学员</div>
                    </div>
                  </div>
                </el-dropdown-item>
                <el-dropdown-item divided @click="handleLogout">
                  <el-icon><SwitchButton /></el-icon>
                  退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </div>
    </header>

    <!-- 主体内容 -->
    <main class="student-main">
      <router-view v-slot="{ Component }">
        <transition name="page-fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
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
import { Bell, Sunny, Moon, SwitchButton } from '@element-plus/icons-vue'
import axios from 'axios'
import { getToken } from '@/utils/auth'

const route = useRoute()
const router = useRouter()
const currentPath = computed(() => route.path)
const unreadCount = ref(0)
const userInfo = ref(getUser() || {})
const userName = computed(() => userInfo.value?.真实姓名 || userInfo.value?.real_name || '学员')
const isDark = ref(document.documentElement.classList.contains('dark'))

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

const toggleTheme = () => {
  const html = document.documentElement
  isDark.value = !html.classList.contains('dark')
  if (isDark.value) {
    html.classList.add('dark')
    localStorage.setItem('theme-mode', 'dark')
  } else {
    html.classList.remove('dark')
    localStorage.setItem('theme-mode', 'light')
  }
}

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
  background: var(--bg-page);
  transition: background var(--transition-slow);
}

/* ===== Header ===== */
.student-header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 100;
  background: var(--header-bg);
  box-shadow: var(--shadow-xs);
  border-bottom: 1px solid var(--header-border);
  transition: background var(--transition-slow), border-color var(--transition-slow);
}

.header-inner {
  max-width: 1280px;
  margin: 0 auto;
  height: var(--header-height);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 var(--space-6);
}

.header-left {
  display: flex;
  align-items: center;
  gap: var(--space-10);
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
  color: var(--text-primary);
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
  border-radius: var(--radius-md);
  text-decoration: none;
  font-size: 14px;
  font-weight: var(--weight-medium);
  color: var(--text-secondary);
  transition: all var(--transition-fast);
}
.nav-item:hover {
  background: var(--bg-hover);
  color: var(--text-brand);
}
.nav-item.active {
  background: var(--bg-active);
  color: var(--text-brand);
  font-weight: var(--weight-semibold);
}

/* ===== Header right ===== */
.header-right {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.nav-icon-btn {
  --el-button-bg-color: transparent;
  --el-button-border-color: transparent;
  color: var(--text-secondary);
  font-size: 18px;
}
.nav-icon-btn:hover {
  color: var(--text-brand);
  background: var(--bg-hover) !important;
}

.user-profile {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: var(--radius-md);
  transition: background var(--transition-fast);
}
.user-profile:hover {
  background: var(--bg-hover);
}

.user-avatar {
  background: linear-gradient(135deg, var(--brand-500), var(--brand-300));
  font-size: 13px;
  font-weight: var(--weight-semibold);
  color: #fff;
}

.user-name {
  font-size: 14px;
  color: var(--text-primary);
  font-weight: var(--weight-medium);
}

.notif-badge {
  margin-right: 4px;
}

/* Dropdown */
:deep(.el-dropdown-menu__item.user-menu-header) {
  padding: 12px 16px !important;
  cursor: default !important;
}
:deep(.user-menu-header:hover) {
  background: transparent !important;
}

.menu-user-info {
  display: flex;
  align-items: center;
  gap: 12px;
}
.menu-avatar {
  background: linear-gradient(135deg, var(--brand-500), var(--brand-300));
  font-size: 14px;
  font-weight: var(--weight-semibold);
  color: #fff;
}
.menu-user-name {
  font-size: 14px;
  font-weight: var(--weight-semibold);
  color: var(--text-primary);
}
.menu-user-role {
  font-size: 12px;
  color: var(--text-tertiary);
  margin-top: 2px;
}

/* ===== Main ===== */
.student-main {
  padding-top: var(--header-height);
  min-height: 100vh;
  padding: calc(var(--header-height) + var(--space-6)) var(--space-6) var(--space-6);
  max-width: 1280px;
  margin: 0 auto;
  transition: background var(--transition-slow);
}

/* ===== Page transition ===== */
.page-fade-enter-active {
  animation: fadeInUp 0.2s ease-out;
}
.page-fade-leave-active {
  animation: fadeIn 0.15s ease-in reverse;
}

/* ===== Mobile bottom navigation ===== */
.mobile-bottom-nav {
  display: none;
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: 100;
  background: var(--bg-card);
  border-top: 1px solid var(--border-default);
  padding: 6px 0 env(safe-area-inset-bottom);
  justify-content: space-around;
  transition: background var(--transition-slow), border-color var(--transition-slow);
}

.bottom-nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
  padding: 6px 10px;
  text-decoration: none;
  font-size: 11px;
  color: var(--text-tertiary);
  transition: all var(--transition-fast);
  border-radius: var(--radius-md);
}
.bottom-nav-item.active {
  color: var(--text-brand);
}

/* ===== Responsive ===== */
@media (max-width: 1024px) {
  .main-nav {
    gap: 0;
  }
  .nav-item {
    padding: 8px 10px;
  }
  .nav-item span {
    display: none;
  }
}

@media (max-width: 768px) {
  .main-nav {
    display: none;
  }
  .header-inner {
    padding: 0 var(--space-4);
  }
  .student-main {
    padding: calc(var(--header-height) + var(--space-4)) var(--space-4) calc(64px + var(--space-4));
  }
  .mobile-bottom-nav {
    display: flex;
  }
}

/* ===== Reduced motion ===== */
@media (prefers-reduced-motion: reduce) {
  .page-fade-enter-active,
  .page-fade-leave-active {
    animation: none !important;
  }
}
</style>
