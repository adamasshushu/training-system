<template>
  <el-container class="admin-layout">
    <!-- 顶部导航 -->
    <el-header class="admin-header">
      <div class="header-left">
        <el-icon class="toggle-btn" @click="toggleSidebar">
          <Fold v-if="!isCollapsed" />
          <Expand v-else />
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
              <el-dropdown-item @click="handleProfile">个人中心</el-dropdown-item>
              <el-dropdown-item divided @click="handleLogout">退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </el-header>

    <el-container class="admin-body">
      <!-- 左侧菜单 -->
      <el-aside :width="isCollapsed ? '64px' : '220px'" class="admin-sidebar">
        <el-menu
          :default-active="activeMenu"
          :collapse="isCollapsed"
          :router="true"
          background-color="#304156"
          text-color="#bfcbd9"
          active-text-color="#409EFF"
          class="sidebar-menu"
        >
          <el-menu-item index="/admin/dashboard">
            <el-icon><DataAnalysis /></el-icon>
            <template #title>仪表盘</template>
          </el-menu-item>

          <el-sub-menu index="organization">
            <template #title>
              <el-icon><Management /></el-icon>
              <span>组织管理</span>
            </template>
            <el-menu-item index="/admin/departments">
              <el-icon><FolderOpened /></el-icon>
              <template #title>部门管理</template>
            </el-menu-item>
            <el-menu-item index="/admin/users">
              <el-icon><User /></el-icon>
              <template #title>员工管理</template>
            </el-menu-item>
          </el-sub-menu>

          <el-sub-menu index="education">
            <template #title>
              <el-icon><Reading /></el-icon>
              <span>教务管理</span>
            </template>
            <el-menu-item index="/admin/courses">
              <el-icon><VideoCamera /></el-icon>
              <template #title>课程管理</template>
            </el-menu-item>
            <el-menu-item index="/admin/course-categories">
              <el-icon><Collection /></el-icon>
              <template #title>课程分类</template>
            </el-menu-item>
            <el-menu-item index="/admin/exams">
              <el-icon><EditPen /></el-icon>
              <template #title>考试管理</template>
            </el-menu-item>
            <el-menu-item index="/admin/questions">
              <el-icon><QuestionFilled /></el-icon>
              <template #title>题库管理</template>
            </el-menu-item>
          </el-sub-menu>

          <el-menu-item index="/admin/tasks">
            <el-icon><List /></el-icon>
            <template #title>培训任务</template>
          </el-menu-item>

          <el-sub-menu index="cert">
            <template #title>
              <el-icon><Medal /></el-icon>
              <span>证书管理</span>
            </template>
            <el-menu-item index="/admin/certificates">
              <el-icon><Trophy /></el-icon>
              <template #title>证书管理</template>
            </el-menu-item>
            <el-menu-item index="/admin/certificate-templates">
              <el-icon><CopyDocument /></el-icon>
              <template #title>证书模板</template>
            </el-menu-item>
          </el-sub-menu>
        </el-menu>
      </el-aside>

      <!-- 右侧内容 -->
      <el-main class="admin-main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { removeToken } from '@/utils/auth'
import { ElMessageBox } from 'element-plus'

const route = useRoute()
const router = useRouter()
const isCollapsed = ref(false)

const activeMenu = computed(() => route.path)

const toggleSidebar = () => {
  isCollapsed.value = !isCollapsed.value
}

const handleProfile = () => {
  // TODO: 跳转个人中心
}

const handleLogout = async () => {
  try {
    await ElMessageBox.confirm('确定要退出登录吗？', '提示', {
      type: 'warning'
    })
    removeToken()
    router.push('/login')
  } catch {
    // 取消操作
  }
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

.sidebar-menu {
  border-right: none;
  height: 100%;
}

.admin-main {
  background-color: #f0f2f5;
  padding: 20px;
  overflow-y: auto;
  height: calc(100vh - 60px);
}
</style>
