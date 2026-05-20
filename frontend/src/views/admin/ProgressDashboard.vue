<template>
  <div class="progress-dashboard">
    <h2 style="margin: 0 0 20px; font-size: 18px; color: var(--text-primary)">📊 学习进度概览</h2>

    <!-- 统计卡片 -->
    <el-row :gutter="16" class="stat-cards">
      <el-col :xs="12" :sm="6" v-for="stat in stats" :key="stat.label">
        <el-card shadow="never" class="stat-card">
          <div class="stat-value">{{ stat.value }}</div>
          <div class="stat-label">{{ stat.label }}</div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 按部门统计 -->
    <el-card class="section-card" style="margin-top: 16px">
      <template #header>按部门统计</template>
      <el-table :data="deptStats" v-loading="loadingDept" border stripe>
        <el-table-column type="index" label="#" width="55" />
        <el-table-column prop="部门名称" label="部门" min-width="200" />
        <el-table-column prop="员工数" label="员工数" width="100" align="center" />
        <el-table-column label="平均进度" width="200">
          <template #default="{ row }">
            <el-progress :percentage="row.平均进度" :stroke-width="16" />
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 课程进度查询 -->
    <el-card class="section-card" style="margin-top: 16px">
      <template #header>课程进度查询</template>
      <el-form :inline="true">
        <el-form-item label="选择课程">
          <el-select v-model="selectedCourseId" placeholder="请选择课程" filterable style="width: 300px" @change="loadCourseProgress">
            <el-option v-for="c in courses" :key="c.ID" :label="c.标题" :value="c.ID" />
          </el-select>
        </el-form-item>
      </el-form>

      <el-table v-if="courseProgressData" :data="courseProgressData.学员列表" v-loading="loadingProgress" border stripe>
        <el-table-column type="index" label="#" width="55" />
        <el-table-column prop="姓名" label="学员姓名" min-width="120" />
        <el-table-column prop="部门" label="部门" width="120" />
        <el-table-column prop="总课时" label="总课时" width="80" align="center" />
        <el-table-column prop="已完成" label="已完成" width="80" align="center" />
        <el-table-column label="进度" width="200">
          <template #default="{ row }">
            <el-progress :percentage="row.进度" :stroke-width="16" />
          </template>
        </el-table-column>
      </el-table>
      <el-empty v-else-if="selectedCourseId" description="暂无学习记录" />
      <el-empty v-else description="请先选择课程" />
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getToken } from '@/utils/auth'
import axios from 'axios'

const API = axios.create({ baseURL: '' })
API.interceptors.request.use((c) => { c.headers.Authorization = `Bearer ${getToken()}`; return c })

const loadingDept = ref(false)
const loadingProgress = ref(false)
const deptStats = ref([])
const courses = ref([])
const selectedCourseId = ref(null)
const courseProgressData = ref(null)

const stats = ref([
  { label: '总学员', value: '--' },
  { label: '课程总数', value: '--' },
  { label: '完成率', value: '--%' },
  { label: '活跃学员', value: '--' },
])

const loadDeptStats = async () => {
  loadingDept.value = true
  try {
    const res = await API.get('/api/reports/department-progress')
    deptStats.value = res.data.数据 || []
  } catch { /* silent */ }
  finally { loadingDept.value = false }
}

const loadCourses = async () => {
  try {
    const res = await API.get('/api/courses/student')
    courses.value = res.data.数据 || []
  } catch { /* silent */ }
}

const loadCourseProgress = async (courseId) => {
  if (!courseId) { courseProgressData.value = null; return }
  loadingProgress.value = true
  try {
    const res = await API.get(`/api/courses/${courseId}/progress`)
    courseProgressData.value = res.data
  } catch { ElMessage.error('加载课程进度失败') }
  finally { loadingProgress.value = false }
}

onMounted(() => {
  loadDeptStats()
  loadCourses()
})
</script>

<style scoped>
.progress-dashboard { max-width: 1200px; }
.stat-card { text-align: center; }
.stat-value { font-size: 28px; font-weight: 700; color: var(--text-primary); }
.stat-label { font-size: 12px; color: var(--text-tertiary); margin-top: 2px; }
</style>
