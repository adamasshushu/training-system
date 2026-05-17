<template>
  <div class="dashboard">
    <h2 class="page-title">系统概览</h2>

    <el-row :gutter="20" class="stat-cards" v-loading="loading">
      <el-col :xs="12" :sm="8" :md="4" v-for="s in statItems" :key="s.label">
        <el-card shadow="hover" class="stat-card" @click="$router.push(s.link)">
          <div class="stat-content">
            <div class="stat-info">
              <div class="stat-label">{{ s.label }}</div>
              <div class="stat-value">{{ stats[s.key] || 0 }}</div>
            </div>
            <el-icon class="stat-icon" :color="s.color" :size="40"><component :is="s.icon" /></el-icon>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-card shadow="never" style="margin-top:20px">
      <template #header><span class="card-title">快速入口</span></template>
      <el-row :gutter="12">
        <el-col :span="6" v-for="link in quickLinks" :key="link.path">
          <el-button style="width:100%;margin-bottom:8px" @click="$router.push(link.path)">{{ link.label }}</el-button>
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
  { label:'员工数', key:'员工数量', icon:User, color:'#409EFF', link:'/admin/users' },
  { label:'部门数', key:'部门数量', icon:List, color:'#67C23A', link:'/admin/departments' },
  { label:'课程数', key:'课程数量', icon:Reading, color:'#E6A23C', link:'/admin/courses' },
  { label:'考试数', key:'考试数量', icon:EditPen, color:'#F56C6C', link:'/admin/exams' },
  { label:'通过', key:'考试通过次数', icon:Trophy, color:'#409EFF', link:'/admin/exams' },
  { label:'证书', key:'证书数量', icon:Medal, color:'#E6A23C', link:'/admin/certificates' },
  { label:'任务', key:'任务数量', icon:List, color:'#F56C6C', link:'/admin/tasks' },
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
.dashboard { max-width: 1200px; }
.page-title { font-size: 24px; font-weight: 700; color: #303133; margin-bottom: 24px; }
.stat-cards { margin-bottom: 0; }
.stat-card { cursor: pointer; border-radius: 12px; }
.stat-content { display: flex; align-items: center; justify-content: space-between; }
.stat-label { font-size: 14px; color: #909399; margin-bottom: 8px; }
.stat-value { font-size: 32px; font-weight: 700; color: #303133; }
.card-title { font-weight: 600; }
</style>
