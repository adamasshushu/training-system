<template>
  <el-container class="admin-layout">
    <!-- 顶部导航 -->
    <el-header class="admin-header">
      <div class="header-left">
        <!-- 侧边栏折叠按钮 -->
        <el-icon class="toggle-btn" @click="isMobile ? (drawerVisible = true) : toggleSidebar()">
          <Fold v-if="!isCollapsed && !isMobile" />
          <Expand v-else-if="!isMobile" />
          <Operation v-else />
        </el-icon>
        <div class="brand-logo">
          <svg width="28" height="28" viewBox="0 0 28 28" fill="none">
            <rect width="28" height="28" rx="7" fill="url(#brand-grad)" />
            <path d="M8 17V11l6-3.5 6 3.5v6l-6 3.5L8 17z" stroke="white" stroke-width="1.5" fill="rgba(255,255,255,0.12)"/>
            <path d="M14 13v4.5m-2.5-2.25h5" stroke="white" stroke-width="1.5" stroke-linecap="round"/>
            <defs>
              <linearGradient id="brand-grad" x1="0" y1="0" x2="28" y2="28">
                <stop stop-color="#6C5CE7"/>
                <stop offset="1" stop-color="#a29bfe"/>
              </linearGradient>
            </defs>
          </svg>
        </div>
        <span class="system-title">培训管理系统</span>
      </div>

      <div class="header-right">
        <!-- 暗黑模式切换 -->
        <el-tooltip :content="isDark ? '切换亮色模式' : '切换暗黑模式'" placement="bottom">
          <el-button
            :icon="isDark ? Sunny : Moon"
            circle
            class="theme-toggle"
            @click="toggleTheme"
          />
        </el-tooltip>

        <!-- 用户信息 -->
        <el-dropdown trigger="click" class="user-dropdown">
          <span class="user-info">
            <el-avatar :size="32" class="user-avatar">
              {{ username.charAt(0) }}
            </el-avatar>
            <span class="username">{{ username }}</span>
            <el-icon class="dropdown-arrow"><ArrowDown /></el-icon>
          </span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item class="user-menu-header" disabled>
                <div class="menu-user-info">
                  <el-avatar :size="36" class="menu-avatar">{{ username.charAt(0) }}</el-avatar>
                  <div>
                    <div class="menu-user-name">{{ username }}</div>
                    <div class="menu-user-role">{{ userRole }}</div>
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
    </el-header>

    <el-container class="admin-body">
      <!-- 桌面端侧边栏 -->
      <el-aside v-if="!isMobile" :width="sidebarWidth" class="admin-sidebar">
        <side-menu :is-collapsed="isCollapsed" />
        <!-- 底部折叠按钮 -->
        <div class="sidebar-collapse-btn" @click="toggleSidebar">
          <el-icon :class="{ rotated: isCollapsed }">
            <Fold />
          </el-icon>
        </div>
      </el-aside>

      <!-- 移动端抽屉菜单 -->
      <el-drawer v-model="drawerVisible" direction="ltr" size="260px" :with-header="false" class="mobile-drawer">
        <side-menu :is-collapsed="false" @click="drawerVisible = false" />
        <div class="drawer-footer">
          <el-button text @click="toggleTheme">
            <el-icon><Moon /></el-icon>
            {{ isDark ? '亮色模式' : '暗黑模式' }}
          </el-button>
        </div>
      </el-drawer>

      <!-- 右侧内容 -->
      <el-main class="admin-main">
        <router-view v-slot="{ Component }">
          <transition name="page-fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { removeToken, getUser } from '@/utils/auth'
import { ElMessageBox } from 'element-plus'
import { Sunny, Moon, SwitchButton } from '@element-plus/icons-vue'
import SideMenu from './SideMenu.vue'

const route = useRoute()
const router = useRouter()
const isCollapsed = ref(false)
const drawerVisible = ref(false)
const isMobile = ref(window.innerWidth < 768)
const userInfo = ref(getUser() || {})
const isDark = ref(document.documentElement.classList.contains('dark'))

const username = computed(() => userInfo.value?.真实姓名 || userInfo.value?.real_name || '管理员')
const userRole = computed(() => {
  const role = userInfo.value?.角色
  return { admin: '系统管理员', teacher: '讲师', student: '学员' }[role] || role || '管理员'
})
const sidebarWidth = computed(() => isCollapsed.value ? '64px' : '240px')

const checkMobile = () => {
  isMobile.value = window.innerWidth < 768
}

onMounted(() => window.addEventListener('resize', checkMobile))
onUnmounted(() => window.removeEventListener('resize', checkMobile))

const toggleSidebar = () => {
  isCollapsed.value = !isCollapsed.value
}

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

const handleLogout = async () => {
  try {
    await ElMessageBox.confirm('确定要退出登录吗？', '提示', { type: 'warning' })
    removeToken()
    router.push('/login')
  } catch {}
}
</script>

<style scoped>
.admin-layout {
  height: 100vh;
  overflow: hidden;
}

/* ===== Header ===== */
.admin-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: var(--header-height);
  padding: 0 var(--space-5);
  background: var(--header-bg);
  border-bottom: 1px solid var(--header-border);
  box-shadow: var(--shadow-xs);
  z-index: 10;
  transition: background var(--transition-slow), border-color var(--transition-slow);
}

.header-left {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.toggle-btn {
  font-size: 20px;
  cursor: pointer;
  color: var(--text-secondary);
  transition: all var(--transition-fast);
  padding: 6px;
  border-radius: var(--radius-md);
}
.toggle-btn:hover {
  color: var(--text-brand);
  background: var(--bg-hover);
}

.brand-logo {
  display: flex;
  align-items: center;
}

.system-title {
  font-size: 18px;
  font-weight: var(--weight-bold);
  color: var(--text-primary);
  white-space: nowrap;
  letter-spacing: -0.3px;
}

/* ===== Header right ===== */
.header-right {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.theme-toggle {
  --el-button-bg-color: transparent;
  --el-button-border-color: transparent;
  color: var(--text-secondary);
  font-size: 18px;
}
.theme-toggle:hover {
  color: var(--text-brand);
  background: var(--bg-hover) !important;
}

.user-dropdown {
  cursor: pointer;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 8px;
  border-radius: var(--radius-md);
  transition: background var(--transition-fast);
}
.user-info:hover {
  background: var(--bg-hover);
}

.user-avatar {
  background: linear-gradient(135deg, var(--brand-500), var(--brand-300));
  font-size: 13px;
  font-weight: var(--weight-semibold);
  color: #fff;
}

.username {
  font-size: 14px;
  color: var(--text-primary);
  font-weight: var(--weight-medium);
}

.dropdown-arrow {
  color: var(--text-tertiary);
  font-size: 14px;
}

/* Dropdown menu */
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

/* ===== Sidebar ===== */
.admin-sidebar {
  background: var(--sidebar-bg);
  width: v-bind(sidebarWidth);
  transition: width 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  border-right: 1px solid rgba(255, 255, 255, 0.04);
  position: relative;
}

.sidebar-collapse-btn {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--sidebar-text);
  cursor: pointer;
  border-top: 1px solid rgba(255, 255, 255, 0.04);
  transition: all var(--transition-fast);
  font-size: 16px;
}
.sidebar-collapse-btn:hover {
  color: var(--sidebar-active-text);
  background: var(--sidebar-hover);
}
.sidebar-collapse-btn .rotated {
  transform: rotate(180deg);
}

/* ===== Main content ===== */
.admin-main {
  background: var(--bg-page);
  padding: var(--space-6);
  overflow-y: auto;
  height: calc(100vh - var(--header-height));
  transition: background var(--transition-slow);
}

/* ===== Page transition ===== */
.page-fade-enter-active {
  animation: fadeInUp 0.2s ease-out;
}
.page-fade-leave-active {
  animation: fadeIn 0.15s ease-in reverse;
}

/* ===== Mobile drawer ===== */
.mobile-drawer :deep(.el-drawer) {
  background: var(--sidebar-bg);
}
.mobile-drawer :deep(.el-drawer__body) {
  padding: 0;
  display: flex;
  flex-direction: column;
}
.drawer-footer {
  margin-top: auto;
  padding: 12px 16px;
  border-top: 1px solid rgba(255, 255, 255, 0.06);
  display: flex;
  justify-content: center;
}
.drawer-footer .el-button {
  color: var(--sidebar-text);
  gap: 8px;
}

/* ===== Responsive ===== */
@media (max-width: 768px) {
  .admin-header {
    padding: 0 var(--space-3);
  }
  .system-title {
    font-size: 15px;
  }
  .admin-main {
    padding: var(--space-3);
  }
  .username {
    display: none;
  }
}

/* ===== Reduced motion ===== */
@media (prefers-reduced-motion: reduce) {
  .admin-sidebar,
  .page-fade-enter-active,
  .page-fade-leave-active {
    animation: none !important;
    transition: none !important;
  }
}
</style>
