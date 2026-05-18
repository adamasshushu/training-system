<template>
  <div class="dashboard">
    <div class="page-header">
      <h2 class="page-title">系统概览</h2>
      <p class="page-subtitle">培训系统数据总览</p>
    </div>

    <el-row :gutter="20" class="stat-cards" v-loading="loading">
      <el-col :xs="12" :sm="8" :md="4" v-for="s in statItems" :key="s.label">
        <el-card shadow="never" class="stat-card" @click="$router.push(s.link)">
          <div class="stat-content">
            <div class="stat-info">
              <div class="stat-label">{{ s.label }}</div>
              <div class="stat-value">{{ stats[s.key] || 0 }}</div>
            </div>
            <div class="stat-icon-wrap" :style="{ background: s.bg }">
              <el-icon class="stat-icon" :color="s.color" :size="22"><component :is="s.icon" /></el-icon>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-card shadow="never" class="quick-links-card">
      <template #header>
        <div class="card-header">
          <span class="card-title">⚡ 快速入口</span>
        </div>
      </template>
      <el-row :gutter="12">
        <el-col :span="6" v-for="link in quickLinks" :key="link.path">
          <el-button class="quick-link-btn" @click="$router.push(link.path)">
            {{ link.label }}
          </el-button>
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { Reading, EditPen, User, List, Medal, Trophy } from '@element-plus/icons-vue'
import { getStats } from '@/api/certificates'

const loading = ref(false)
const stats = reactive({})

const statItems = [
  { label:'员工数', key:'员工数量', icon:User, color:'#6C5CE7', bg:'rgba(108,92,231,0.1)', link:'/admin/users' },
  { label:'部门数', key:'部门数量', icon:List, color:'#5e6ad2', bg:'rgba(94,106,210,0.1)', link:'/admin/departments' },
  { label:'课程数', key:'课程数量', icon:Reading, color:'#a29bfe', bg:'rgba(162,155,254,0.1)', link:'/admin/courses' },
  { label:'考试数', key:'考试数量', icon:EditPen, color:'#10b981', bg:'rgba(16,185,129,0.1)', link:'/admin/exams' },
  { label:'通过', key:'考试通过次数', icon:Trophy, color:'#f59e0b', bg:'rgba(245,158,11,0.1)', link:'/admin/exams' },
  { label:'证书', key:'证书数量', icon:Medal, color:'#6C5CE7', bg:'rgba(108,92,231,0.1)', link:'/admin/certificates' },
  { label:'任务', key:'任务数量', icon:List, color:'#ef4444', bg:'rgba(239,68,68,0.1)', link:'/admin/tasks' },
]

const quickLinks = [
  { label:'题库管理', path:'/admin/questions' },
  { label:'新建考试', path:'/admin/exams' },
  { label:'新建任务', path:'/admin/tasks' },
  { label:'证书模板', path:'/admin/certificate-templates' },
]

onMounted(async () => {
  loading.value = true
  try {
    const res = await getStats()
    Object.assign(stats, res.数据 || {})
  } catch {} finally { loading.value = false }
})
</script>

<style scoped>
.dashboard {
  max-width: 1200px;
}

.page-header {
  margin-bottom: 24px;
}

.page-title {
  font-size: 24px;
  font-weight: 700;
  color: #1a1a2e;
  margin-bottom: 4px;
  letter-spacing: -0.3px;
}

.page-subtitle {
  font-size: 14px;
  color: #94a3b8;
  margin: 0;
}

.stat-cards {
  margin-bottom: 0;
}

.stat-card {
  cursor: pointer;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  margin-bottom: 16px;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(108,92,231,0.1);
}

.stat-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.stat-info {
  flex: 1;
}

.stat-label {
  font-size: 13px;
  color: #94a3b8;
  margin-bottom: 6px;
  font-weight: 500;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #1a1a2e;
  letter-spacing: -0.5px;
}

.stat-icon-wrap {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.quick-links-card {
  margin-top: 8px;
}

.card-header {
  display: flex;
  align-items: center;
}

.card-title {
  font-weight: 600;
  font-size: 16px;
  color: #1a1a2e;
}

.quick-link-btn {
  width: 100%;
  margin-bottom: 8px;
  background: #f8f9ff !important;
  border: 1px solid #e2e8f0 !important;
  color: #475569 !important;
  font-weight: 500;
  border-radius: 10px;
  transition: all 0.2s;
}
.quick-link-btn:hover {
  background: #eef0ff !important;
  border-color: #6C5CE7 !important;
  color: #6C5CE7 !important;
}
</style>
