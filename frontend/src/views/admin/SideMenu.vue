<template>
  <el-menu
    :default-active="activeMenu"
    :collapse="isCollapsed"
    :router="true"
    :background-color="sidebarBg"
    :text-color="sidebarText"
    :active-text-color="sidebarActiveText"
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
        <template #title>部门管理</template>
      </el-menu-item>
      <el-menu-item index="/admin/users">
        <template #title>员工管理</template>
      </el-menu-item>
      <el-menu-item index="/admin/ad-users">
        <template #title>AD用户中心</template>
      </el-menu-item>
    </el-sub-menu>

    <el-sub-menu index="education">
      <template #title>
        <el-icon><Reading /></el-icon>
        <span>教务管理</span>
      </template>
      <el-menu-item index="/admin/courses">
        <template #title>课程管理</template>
      </el-menu-item>
      <el-menu-item index="/admin/course-categories">
        <template #title>课程分类</template>
      </el-menu-item>
      <el-menu-item index="/admin/exams">
        <template #title>考试管理</template>
      </el-menu-item>
      <el-menu-item index="/admin/questions">
        <template #title>题库管理</template>
      </el-menu-item>
    </el-sub-menu>

    <el-menu-item index="/admin/tasks">
      <el-icon><List /></el-icon>
      <template #title>培训任务</template>
    </el-menu-item>

    <el-menu-item index="/admin/learning-paths">
      <el-icon><MapLocation /></el-icon>
      <template #title>学习路径</template>
    </el-menu-item>

    <el-menu-item index="/admin/progress">
      <el-icon><DataBoard /></el-icon>
      <template #title>学习进度</template>
    </el-menu-item>

    <el-sub-menu index="cert">
      <template #title>
        <el-icon><Medal /></el-icon>
        <span>证书管理</span>
      </template>
      <el-menu-item index="/admin/certificates">
        <template #title>证书管理</template>
      </el-menu-item>
      <el-menu-item index="/admin/certificate-templates">
        <template #title>证书模板</template>
      </el-menu-item>
    </el-sub-menu>

    <el-sub-menu index="content">
      <template #title>
        <el-icon><Folder /></el-icon>
        <span>内容管理</span>
      </template>
      <el-menu-item index="/admin/videos">
        <template #title>视频管理</template>
      </el-menu-item>
      <el-menu-item index="/admin/files">
        <template #title>文件管理</template>
      </el-menu-item>
      <el-menu-item index="/admin/online-editor">
        <template #title>在线编辑</template>
      </el-menu-item>
      <el-menu-item index="/admin/fetch-url">
        <template #title>网址抓取</template>
      </el-menu-item>
    </el-sub-menu>

    <el-menu-item index="/admin/system-settings">
      <el-icon><Setting /></el-icon>
      <template #title>系统设置</template>
    </el-menu-item>

    <el-menu-item index="/admin/enterprise">
      <el-icon><Connection /></el-icon>
      <template #title>企业平台</template>
    </el-menu-item>

    <el-menu-item index="/admin/feedback-manage">
      <el-icon><ChatLineSquare /></el-icon>
      <template #title>反馈管理</template>
    </el-menu-item>

    <el-menu-item index="/admin/reports">
      <el-icon><Download /></el-icon>
      <template #title>报告导出</template>
    </el-menu-item>

    <el-menu-item index="/admin/knowledge-graph">
      <el-icon><Connection /></el-icon>
      <template #title>知识图谱</template>
    </el-menu-item>
  </el-menu>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const props = defineProps({
  isCollapsed: { type: Boolean, default: false }
})
const emit = defineEmits(['click'])

const route = useRoute()
const activeMenu = computed(() => route.path)

const sidebarBg = '#1a1a2e'
const sidebarText = '#a0aec0'
const sidebarActiveText = '#e2e8f0'

const handleItemClick = () => {
  emit('click')
}
</script>

<style scoped>
.sidebar-menu {
  border-right: none;
  height: 100%;
  padding-top: 8px;
  padding-bottom: 48px;
  overflow-y: auto;
  overflow-x: hidden;
}

/* Scrollbar */
.sidebar-menu::-webkit-scrollbar {
  width: 3px;
}
.sidebar-menu::-webkit-scrollbar-thumb {
  background: rgba(255,255,255,0.1);
  border-radius: 10px;
}

/* Menu items */
.sidebar-menu :deep(.el-menu-item),
.sidebar-menu :deep(.el-sub-menu__title) {
  margin: 2px 8px;
  padding: 0 12px;
  border-radius: 8px;
  height: 44px;
  line-height: 44px;
  transition: all 0.2s ease;
  font-size: 14px;
}

.sidebar-menu :deep(.el-menu-item):hover,
.sidebar-menu :deep(.el-sub-menu__title):hover {
  background-color: #16213e !important;
  color: #e2e8f0 !important;
}

.sidebar-menu :deep(.el-menu-item.is-active) {
  background: linear-gradient(135deg, rgba(108,92,231,0.2), rgba(162,155,254,0.1)) !important;
  color: #e2e8f0 !important;
  font-weight: 600;
  position: relative;
}
.sidebar-menu :deep(.el-menu-item.is-active)::after {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 3px;
  height: 20px;
  background: #6C5CE7;
  border-radius: 0 3px 3px 0;
}

.sidebar-menu :deep(.el-sub-menu.is-opened > .el-sub-menu__title) {
  color: #c4bdf7 !important;
}

.sidebar-menu :deep(.el-menu--inline) {
  background-color: transparent !important;
}

.sidebar-menu :deep(.el-menu--inline .el-menu-item) {
  padding-left: 44px !important;
  margin: 1px 4px;
  font-size: 13px;
}

/* Icons */
.sidebar-menu :deep(.el-icon) {
  color: inherit;
}

/* Collapsed mode */
.sidebar-menu :deep(.el-menu--collapse .el-menu-item) {
  margin: 2px 8px;
  padding: 0;
  justify-content: center;
  border-radius: 8px;
}
.sidebar-menu :deep(.el-menu--collapse .el-sub-menu__title) {
  margin: 2px 8px;
  padding: 0;
  justify-content: center;
  border-radius: 8px;
}
</style>
