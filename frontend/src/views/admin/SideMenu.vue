<template>
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
        <el-icon><Trophy /></el-icon>
        <template #title>证书管理</template>
      </el-menu-item>
      <el-menu-item index="/admin/certificate-templates">
        <el-icon><CopyDocument /></el-icon>
        <template #title>证书模板</template>
      </el-menu-item>
    </el-sub-menu>

    <el-sub-menu index="content">
      <template #title>
        <el-icon><Folder /></el-icon>
        <span>内容管理</span>
      </template>
      <el-menu-item index="/admin/files">
        <el-icon><Upload /></el-icon>
        <template #title>文件管理</template>
      </el-menu-item>
      <el-menu-item index="/admin/online-editor">
        <el-icon><Edit /></el-icon>
        <template #title>在线编辑</template>
      </el-menu-item>
      <el-menu-item index="/admin/fetch-url">
        <el-icon><Link /></el-icon>
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

const handleItemClick = () => {
  emit('click')
}
</script>

<style scoped>
.sidebar-menu {
  border-right: none;
  height: 100%;
}
</style>
