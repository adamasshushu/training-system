<template>
  <div class="progress-dashboard">
    <h2 style="margin: 0 0 20px; font-size: 18px; color: #303133">📊 学习进度概览</h2>

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
      <el-table :data="deptStats" v-loading="loadingDept" stripe>
        <el-table-column prop="部门名称" label="部门" />
        <el-table-column prop="员工数" label="员工数" width="100" />
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

      <el-table v-if="courseProgressData" :data="courseProgressData.学员列表" v-loading="loadingProgress" stripe>
        <el-table-column prop="姓名" label="学员姓名" />
        <el-table-column prop="部门" label="部门" />
        <el-table-column prop="总课时" label="总课时" width="80" />
        <el-table-column prop="已完成" label="已完成" width="80" />
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

const stats = ref([])
const deptStats = ref([])
const loadingDept = ref(false)
const courses = ref([])
const selectedCourseId = ref(null)
const courseProgressData = ref(null)
const loadingProgress = ref(false)

const loadOverview = async () => {
  try {
    const res = await API.get('/api/progress/overview')
    const d = res.data.数据 || {}
    stats.value = [
      { label: '总员工数', value: d.总员工数 || 0 },
      { label: '总课程数', value: d.总课程数 || 0 },
      { label: '学习记录', value: d.学习记录数 || 0 },
      { label: '考试记录', value: d.考试记录数 || 0 },
    ]
  } catch { /* silent */ }
}

const loadDeptStats = async () => {
  loadingDept.value = true
  try {
    const res = await API.get('/api/progress/by-department')
    deptStats.value = res.data.数据 || []
  } catch { /* silent */ }
  finally { loadingDept.value = false }
}

const loadCourses = async () => {
  try {
    const res = await API.get('/api/courses', { params: { page_size: 200 } })
    courses.value = res.data.数据 || []
  } catch { /* silent */ }
}

const loadCourseProgress = async (courseId) => {
  if (!courseId) return
  loadingProgress.value = true
  try {
    const res = await API.get(`/api/progress/course/${courseId}`)
    courseProgressData.value = res.data.数据 || null
  } catch { ElMessage.error('加载失败') }
  finally { loadingProgress.value = false }
}

onMounted(() => { loadOverview(); loadDeptStats(); loadCourses() })
</script>

<style scoped>
.stat-cards { margin-bottom: 8px; }
.stat-card { text-align: center; }
.stat-value { font-size: 32px; font-weight: 700; color: #409EFF; }
.stat-label { font-size: 13px; color: #909399; margin-top: 4px; }
</style>
