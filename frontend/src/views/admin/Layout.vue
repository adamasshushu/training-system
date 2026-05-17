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
        <span class="system-title">培训管理系统</span>
      </div>
      <div class="header-right">
        <el-dropdown trigger="click">
          <span class="user-info">
            <el-avatar :size="32" icon="UserFilled" />
            <span class="username">管理员</span>
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
      <el-aside v-if="!isMobile" :width="isCollapsed ? '64px' : '220px'" class="admin-sidebar">
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
import { removeToken } from '@/utils/auth'
import { ElMessageBox } from 'element-plus'
import SideMenu from './SideMenu.vue'

const route = useRoute()
const router = useRouter()
const isCollapsed = ref(false)
const drawerVisible = ref(false)
const isMobile = ref(window.innerWidth < 768)

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
  padding: 0 16px;
  background: #fff;
  border-bottom: 1px solid #e6e6e6;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
  z-index: 10;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.toggle-btn {
  font-size: 20px;
  cursor: pointer;
  color: #606266;
}
.toggle-btn:hover {
  color: #409EFF;
}

.system-title {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  white-space: nowrap;
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

.username {
  font-size: 14px;
  color: #606266;
}

.admin-sidebar {
  background-color: #304156;
  transition: width 0.3s;
  overflow: hidden;
}

.admin-main {
  background-color: #f0f2f5;
  padding: 16px;
  overflow-y: auto;
  height: calc(100vh - 60px);
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
