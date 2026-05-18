<template>
  <el-container class="admin-layout">
    <!-- 顶部导航 -->
    <el-header class="admin-header">
      <div class="header-left">
        <!-- 移动端汉堡菜单 -->
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
        <el-dropdown trigger="click">
          <span class="user-info">
            <el-avatar :size="32" icon="UserFilled" class="user-avatar" />
            <span class="username">{{ username }}</span>
            <el-icon><ArrowDown /></el-icon>
          </span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item divided @click="handleLogout">退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </el-header>

    <el-container class="admin-body">
      <!-- 桌面端侧边栏 -->
      <el-aside v-if="!isMobile" :width="isCollapsed ? '64px' : '230px'" class="admin-sidebar">
        <side-menu :is-collapsed="isCollapsed" />
      </el-aside>

      <!-- 移动端抽屉菜单 -->
      <el-drawer v-model="drawerVisible" direction="ltr" size="260px" :with-header="false" class="mobile-drawer">
        <side-menu :is-collapsed="false" @click="drawerVisible = false" />
      </el-drawer>

      <!-- 右侧内容 -->
      <el-main class="admin-main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { removeToken, getUser } from '@/utils/auth'
import { ElMessageBox } from 'element-plus'
import SideMenu from './SideMenu.vue'

const route = useRoute()
const router = useRouter()
const isCollapsed = ref(false)
const drawerVisible = ref(false)
const isMobile = ref(window.innerWidth < 768)
const userInfo = ref(getUser() || {})
const username = computed(() => userInfo.value?.真实姓名 || userInfo.value?.real_name || '管理员')

const checkMobile = () => {
  isMobile.value = window.innerWidth < 768
}

onMounted(() => window.addEventListener('resize', checkMobile))
onUnmounted(() => window.removeEventListener('resize', checkMobile))

const toggleSidebar = () => {
  isCollapsed.value = !isCollapsed.value
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

.admin-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 60px;
  padding: 0 20px;
  background: #fff;
  border-bottom: 1px solid #e2e8f0;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  z-index: 10;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.brand-logo {
  display: flex;
  align-items: center;
}

.toggle-btn {
  font-size: 20px;
  cursor: pointer;
  color: #64748b;
  transition: color 0.2s;
}
.toggle-btn:hover {
  color: #6C5CE7;
}

.system-title {
  font-size: 18px;
  font-weight: 700;
  color: #1a1a2e;
  white-space: nowrap;
  letter-spacing: -0.3px;
}

.header-right {
  display: flex;
  align-items: center;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.user-avatar {
  background: linear-gradient(135deg, #6C5CE7, #a29bfe);
}

.username {
  font-size: 14px;
  color: #475569;
  font-weight: 500;
}

.admin-sidebar {
  background-color: #1a1a2e;
  transition: width 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
  border-right: 1px solid rgba(255,255,255,0.04);
}

.admin-main {
  background-color: #f0f2f5;
  padding: 20px;
  overflow-y: auto;
  height: calc(100vh - 60px);
}

/* mobile drawer overrides */
.mobile-drawer :deep(.el-drawer) {
  background: #1a1a2e;
}
.mobile-drawer :deep(.el-drawer__body) {
  padding: 0;
}

/* 移动端适配 */
@media (max-width: 768px) {
  .admin-header {
    padding: 0 12px;
  }
  .system-title {
    font-size: 15px;
  }
  .admin-main {
    padding: 12px;
  }
  .username {
    display: none;
  }
}
</style>
