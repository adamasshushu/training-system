<template>
  <div class="student-dashboard">
    <div class="dashboard-header">
      <h2>👋 欢迎回来，{{ userName }}</h2>
      <p class="subtitle">以下是你的学习进度概览</p>
    </div>

    <!-- 甘特图看板 -->
    <el-card class="section-card">
      <template #header>
        <div class="card-header">
          <span>📋 我的学习时间线</span>
          <el-tag type="info" size="small">{{ timelineItems.length }} 项</el-tag>
        </div>
      </template>

      <div v-if="timelineItems.length === 0" class="empty-state">
        <el-empty description="暂无培训任务，等待管理员分配" />
      </div>

      <div v-else class="gantt-chart">
        <!-- 表头 -->
        <div class="gantt-header">
          <span class="gantt-col-name">任务/路径</span>
          <span class="gantt-col-bar">进度</span>
          <span class="gantt-col-pct">完成</span>
          <span class="gantt-col-status">状态</span>
          <span class="gantt-col-deadline">截止日期</span>
        </div>

        <!-- 行 -->
        <div
          v-for="item in timelineItems"
          :key="`${item.类型}-${item.ID}`"
          class="gantt-row"
        >
          <span class="gantt-col-name">
            <span class="item-title">{{ item.标题 }}</span>
          </span>

          <span class="gantt-col-bar">
            <div class="progress-bar-wrapper">
              <div
                class="progress-bar-fill"
                :style="{
                  width: item.当前进度 + '%',
                  backgroundColor: item.颜色
                }"
              />
            </div>
          </span>

          <span class="gantt-col-pct">
            <span class="progress-text" :style="{ color: item.颜色 }">
              {{ item.已完成数 }}/{{ item.总项目数 }}
            </span>
          </span>

          <span class="gantt-col-status">
            <el-tag :color="item.颜色" effect="dark" size="small" style="color:#fff;border:none">
              {{ item.状态 }}
            </el-tag>
          </span>

          <span class="gantt-col-deadline">
            <span v-if="item.截止日期" class="deadline-text">
              {{ item.截止日期 }}
            </span>
            <span v-else class="no-deadline">--</span>
          </span>
        </div>
      </div>
    </el-card>

    <!-- 学习路径 -->
    <el-card class="section-card" style="margin-top: 16px">
      <template #header>
        <div class="card-header">
          <span>🗺️ 我的学习路径</span>
        </div>
      </template>

      <div v-if="myPaths.length === 0" class="empty-state">
        <el-empty description="暂无学习路径" />
      </div>

      <div v-else class="paths-grid">
        <el-card v-for="path in myPaths" :key="path.ID" shadow="hover" class="path-card" @click="$router.push('/student/courses')">
          <div class="path-header">
            <h3>{{ path.名称 }}</h3>
            <el-tag :type="path.总进度 >= 100 ? 'success' : 'warning'" size="small">
              {{ path.总进度 >= 100 ? '已完成' : '进行中' }}
            </el-tag>
          </div>
          <p class="path-desc">{{ path.描述 }}</p>
          <div class="path-progress">
            <el-progress :percentage="path.总进度" :stroke-width="12" />
          </div>
          <div class="path-meta">
            <span>{{ path.已完成课程 }}/{{ path.总课程数 }} 课程</span>
          </div>
        </el-card>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getToken } from '@/utils/auth'
import axios from 'axios'

const API = axios.create({ baseURL: '' })
API.interceptors.request.use((c) => { c.headers.Authorization = `Bearer ${getToken()}`; return c })

const userName = ref('学员')
const timelineItems = ref([])
const myPaths = ref([])

const loadDashboard = async () => {
  try {
    const me = await API.get('/api/auth/me')
    userName.value = me.data.真实姓名 || '学员'
  } catch { /* silent */ }

  try {
    const res = await API.get('/api/dashboard/gantt')
    timelineItems.value = res.data.数据 || []
  } catch { /* silent */ }

  try {
    const res = await API.get('/api/learning-paths/my-paths')
    myPaths.value = res.data.数据 || []
  } catch { /* silent */ }
}

onMounted(loadDashboard)
</script>

<style scoped>
.student-dashboard {
  max-width: 1100px;
  margin: 0 auto;
  padding: 24px;
}
.dashboard-header {
  margin-bottom: 24px;
}
.dashboard-header h2 {
  margin: 0;
  font-size: 22px;
  color: #303133;
}
.subtitle {
  margin: 4px 0 0;
  font-size: 14px;
  color: #909399;
}
.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

/* Gantt Chart */
.gantt-chart {
  border: 1px solid #ebeef5;
  border-radius: 8px;
  overflow: hidden;
}
.gantt-header, .gantt-row {
  display: grid;
  grid-template-columns: 2fr 2fr 100px 100px 160px;
  gap: 8px;
  align-items: center;
  padding: 12px 16px;
}
.gantt-header {
  background: #f5f7fa;
  font-size: 13px;
  color: #909399;
  font-weight: 600;
}
.gantt-row {
  border-top: 1px solid #f0f0f0;
  transition: background 0.2s;
}
.gantt-row:hover {
  background: #f5faff;
}
.item-title {
  font-size: 14px;
  color: #303133;
  font-weight: 500;
}
.progress-bar-wrapper {
  width: 100%;
  height: 20px;
  background: #f0f0f0;
  border-radius: 10px;
  overflow: hidden;
}
.progress-bar-fill {
  height: 100%;
  border-radius: 10px;
  transition: width 0.5s ease;
  min-width: 4px;
}
.progress-text {
  font-size: 13px;
  font-weight: 600;
}
.deadline-text {
  font-size: 13px;
  color: #606266;
}
.no-deadline {
  color: #c0c4cc;
  font-size: 13px;
}

/* Paths */
.paths-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 16px;
}
.path-card {
  cursor: pointer;
}
.path-card:hover {
  border-color: #409EFF;
}
.path-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}
.path-header h3 {
  margin: 0;
  font-size: 16px;
  color: #303133;
}
.path-desc {
  font-size: 13px;
  color: #909399;
  margin: 0 0 12px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.path-progress {
  margin-bottom: 8px;
}
.path-meta {
  font-size: 12px;
  color: #909399;
}
.empty-state {
  display: flex;
  justify-content: center;
  padding: 40px 0;
}
</style>
