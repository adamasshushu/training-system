<template>
  <div class="student-dashboard">
    <!-- 头部欢迎区 -->
    <div class="dashboard-header">
      <div class="header-avatar">
        <span class="avatar-emoji">👋</span>
      </div>
      <div class="header-text">
        <h2>欢迎回来，{{ userName }}</h2>
        <p class="subtitle">以下是你的学习进度概览</p>
      </div>
    </div>

    <!-- 学习统计卡片行 -->
    <div class="stats-grid">
      <div v-for="stat in statsData" :key="stat.label" class="stat-card" :style="{ '--stat-color': stat.color }">
        <div class="stat-icon-wrap">
          <span class="stat-icon">{{ stat.icon }}</span>
        </div>
        <div class="stat-info">
          <span class="stat-value">{{ stat.value }}</span>
          <span class="stat-label">{{ stat.label }}</span>
        </div>
        <div class="stat-trend" v-if="stat.trend !== undefined">
          <span :class="['trend-arrow', stat.trend >= 0 ? 'up' : 'down']">
            {{ stat.trend >= 0 ? '↑' : '↓' }} {{ Math.abs(stat.trend) }}%
          </span>
        </div>
      </div>
    </div>

    <!-- 学习统计图表区 -->
    <div class="charts-row">
      <!-- 环形进度图 -->
      <SectionCard title="学习完成度" icon="📊" class="chart-card">
        <div class="chart-content">
          <div class="ring-chart-wrap">
            <svg class="ring-chart" viewBox="0 0 120 120">
              <circle cx="60" cy="60" r="50" fill="none" stroke="var(--border-default)" stroke-width="10" />
              <circle
                cx="60" cy="60" r="50"
                fill="none"
                stroke="var(--brand-500)"
                stroke-width="10"
                stroke-linecap="round"
                :stroke-dasharray="circumference"
                :stroke-dashoffset="ringOffset"
                transform="rotate(-90, 60, 60)"
                class="ring-fill"
              />
            </svg>
            <div class="ring-center">
              <span class="ring-pct">{{ completedPercent }}%</span>
              <span class="ring-label">已完成</span>
            </div>
          </div>
          <div class="ring-legend">
            <div class="legend-item">
              <span class="legend-dot" style="background: var(--brand-500)"></span>
              <span>已完成课时</span>
              <span class="legend-value">{{ statsData[1]?.value || 0 }}</span>
            </div>
            <div class="legend-item">
              <span class="legend-dot" style="background: var(--border-default)"></span>
              <span>未完成课时</span>
              <span class="legend-value">{{ statsData[0]?.value - statsData[1]?.value || 0 }}</span>
            </div>
          </div>
        </div>
      </SectionCard>

      <!-- 柱状图：本周学习时长 -->
      <SectionCard title="本周学习时长" icon="📈" class="chart-card">
        <div class="chart-content">
          <div class="bar-chart-wrap">
            <div class="bar-y-axis">
              <span>10h</span>
              <span>8h</span>
              <span>6h</span>
              <span>4h</span>
              <span>2h</span>
              <span>0</span>
            </div>
            <div class="bar-chart">
              <div
                v-for="(bar, idx) in weeklyData"
                :key="idx"
                class="bar-column"
                :style="{ '--bar-height': bar.height + '%', '--bar-delay': idx * 0.08 + 's' }"
              >
                <span class="bar-value">{{ bar.value }}h</span>
                <div class="bar-track">
                  <div class="bar-fill" :style="{ '--bar-color': bar.color }"></div>
                </div>
                <span class="bar-label">{{ bar.day }}</span>
              </div>
            </div>
          </div>
        </div>
      </SectionCard>
    </div>

    <!-- 甘特图 / 学习时间线 -->
    <SectionCard title="我的学习时间线" icon="📋" :tag="timelineItems.length + ' 项'" tagType="primary">
      <EmptyState v-if="timelineItems.length === 0" description="暂无培训任务，等待管理员分配" />

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
                  '--fill-color': item.颜色
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
    </SectionCard>

    <!-- 学习路径 -->
    <SectionCard title="我的学习路径" icon="🗺️">
      <EmptyState v-if="myPaths.length === 0" description="暂无学习路径" />

      <div v-else class="paths-grid">
        <el-card
          v-for="path in myPaths"
          :key="path.ID"
          shadow="hover"
          class="path-card"
          @click="$router.push('/student/courses')"
        >
          <div class="path-header">
            <h3>{{ path.名称 }}</h3>
            <el-tag :type="path.总进度 >= 100 ? 'success' : 'warning'" size="small">
              {{ path.总进度 >= 100 ? '已完成' : '进行中' }}
            </el-tag>
          </div>
          <p class="path-desc">{{ path.描述 }}</p>
          <div class="path-progress">
            <el-progress :percentage="path.总进度" :stroke-width="12" :color="path.总进度 >= 100 ? '#10b981' : '#6C5CE7'" />
          </div>
          <div class="path-meta">
            <span>{{ path.已完成课程 }}/{{ path.总课程数 }} 课程</span>
          </div>
        </el-card>
      </div>
    </SectionCard>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { getToken } from '@/utils/auth'
import axios from 'axios'
import SectionCard from '@/components/SectionCard.vue'
import EmptyState from '@/components/EmptyState.vue'

const API = axios.create({ baseURL: '' })
API.interceptors.request.use((c) => { c.headers.Authorization = `Bearer ${getToken()}`; return c })

const userName = ref('学员')
const timelineItems = ref([])
const myPaths = ref([])

// --- 从 API 加载真实统计数据 ---
const statsData = ref([
  { icon: '📚', label: '学习课程数', value: 0, color: '#6C5CE7', trend: undefined },
  { icon: '✅', label: '完成课时数', value: 0, color: '#10b981', trend: undefined },
  { icon: '🎯', label: '考试通过率', value: '0%', color: '#f59e0b', trend: undefined },
  { icon: '🏆', label: '证书数', value: 0, color: '#3b82f6', trend: undefined }
])

// --- 本周学习时长 (mock) ---
const weeklyData = ref([
  { day: '周一', value: 2, height: 20, color: 'var(--brand-300)' },
  { day: '周二', value: 3, height: 30, color: 'var(--brand-400)' },
  { day: '周三', value: 5, height: 50, color: 'var(--brand-500)' },
  { day: '周四', value: 4, height: 40, color: 'var(--brand-400)' },
  { day: '周五', value: 6, height: 60, color: 'var(--brand-500)' },
  { day: '周六', value: 8, height: 80, color: 'var(--brand-600)' },
  { day: '周日', value: 3, height: 30, color: 'var(--brand-400)' }
])

// --- SVG 环形图计算 ---
const circumference = 2 * Math.PI * 50 // r=50
const completedPercent = computed(() => {
  const total = statsData.value[0]?.value || 1
  const done = statsData.value[1]?.value || 0
  return Math.round((done / total) * 100)
})
const ringOffset = computed(() => {
  return circumference - (completedPercent.value / 100) * circumference
})

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
/* ===== Layout ===== */
.student-dashboard {
  max-width: 1100px;
  margin: 0 auto;
  padding: var(--space-6);
  animation: fadeInUp 0.3s ease-out;
}

/* ===== Header ===== */
.dashboard-header {
  display: flex;
  align-items: center;
  gap: var(--space-4);
  margin-bottom: var(--space-6);
  padding: var(--space-6) var(--space-8);
  background: linear-gradient(135deg, var(--brand-500), var(--brand-700));
  border-radius: var(--radius-xl);
  position: relative;
  overflow: hidden;
}
.dashboard-header::before {
  content: '';
  position: absolute;
  top: -50%;
  right: -20%;
  width: 300px;
  height: 300px;
  background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
  border-radius: 50%;
}
.dashboard-header::after {
  content: '';
  position: absolute;
  bottom: -30%;
  left: 40%;
  width: 200px;
  height: 200px;
  background: radial-gradient(circle, rgba(255,255,255,0.08) 0%, transparent 70%);
  border-radius: 50%;
}
.header-avatar {
  width: 52px;
  height: 52px;
  background: rgba(255,255,255,0.2);
  border-radius: var(--radius-full);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  position: relative;
  z-index: 1;
}
.avatar-emoji {
  font-size: 28px;
}
.header-text {
  position: relative;
  z-index: 1;
}
.dashboard-header h2 {
  margin: 0;
  font-size: var(--text-2xl);
  color: #fff;
  font-weight: var(--weight-bold);
}
.subtitle {
  margin: var(--space-1) 0 0;
  font-size: var(--text-sm);
  color: rgba(255,255,255,0.7);
}

/* ===== Stats Card Row ===== */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--space-4);
  margin-bottom: var(--space-6);
}
.stat-card {
  background: var(--bg-card);
  border: 1px solid var(--border-card);
  border-radius: var(--radius-lg);
  padding: var(--space-5) var(--space-4);
  display: flex;
  align-items: center;
  gap: var(--space-3);
  position: relative;
  transition: transform var(--transition-base), box-shadow var(--transition-base);
  cursor: default;
}
.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}
.stat-icon-wrap {
  width: 44px;
  height: 44px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  background: color-mix(in srgb, var(--stat-color) 12%, transparent);
  flex-shrink: 0;
}
.stat-icon {
  font-size: 20px;
}
.stat-info {
  display: flex;
  flex-direction: column;
  min-width: 0;
}
.stat-value {
  font-size: var(--text-2xl);
  font-weight: var(--weight-bold);
  color: var(--text-primary);
  line-height: 1.2;
}
.stat-label {
  font-size: var(--text-xs);
  color: var(--text-tertiary);
  white-space: nowrap;
}
.stat-trend {
  position: absolute;
  top: var(--space-2);
  right: var(--space-3);
}
.trend-arrow {
  font-size: var(--text-xs);
  font-weight: var(--weight-semibold);
  padding: 2px 6px;
  border-radius: var(--radius-full);
}
.trend-arrow.up {
  color: var(--success);
  background: var(--success-light);
}
.trend-arrow.down {
  color: var(--danger);
  background: var(--danger-light);
}

/* ===== Charts Row ===== */
.charts-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-4);
  margin-bottom: var(--space-6);
}
.chart-card {
  flex: 1;
}
.chart-content {
  padding: var(--space-2) 0;
}

/* --- Ring Chart (SVG) --- */
.ring-chart-wrap {
  display: flex;
  align-items: center;
  gap: var(--space-6);
}
.ring-chart {
  width: 130px;
  height: 130px;
  flex-shrink: 0;
}
.ring-fill {
  transition: stroke-dashoffset 0.8s ease;
}
.ring-center {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
  pointer-events: none;
}
.ring-pct {
  display: block;
  font-size: var(--text-2xl);
  font-weight: var(--weight-bold);
  color: var(--text-primary);
  line-height: 1.1;
}
.ring-label {
  display: block;
  font-size: var(--text-xs);
  color: var(--text-tertiary);
}
.ring-chart-wrap {
  position: relative;
  display: inline-flex;
}
.ring-legend {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}
.legend-item {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  font-size: var(--text-sm);
  color: var(--text-secondary);
}
.legend-dot {
  width: 10px;
  height: 10px;
  border-radius: var(--radius-full);
  flex-shrink: 0;
}
.legend-value {
  margin-left: auto;
  font-weight: var(--weight-semibold);
  color: var(--text-primary);
}

/* --- Bar Chart --- */
.bar-chart-wrap {
  display: flex;
  gap: var(--space-3);
  height: 160px;
  align-items: flex-end;
}
.bar-y-axis {
  display: flex;
  flex-direction: column-reverse;
  justify-content: space-between;
  height: 140px;
  padding-right: var(--space-2);
  flex-shrink: 0;
}
.bar-y-axis span {
  font-size: 10px;
  color: var(--text-tertiary);
  line-height: 1;
}
.bar-chart {
  display: flex;
  align-items: flex-end;
  gap: var(--space-2);
  height: 140px;
  flex: 1;
}
.bar-column {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-1);
  height: 100%;
  justify-content: flex-end;
}
.bar-value {
  font-size: 10px;
  color: var(--text-secondary);
  font-weight: var(--weight-semibold);
  opacity: 0;
  animation: fadeIn 0.3s ease forwards;
  animation-delay: var(--bar-delay);
}
.bar-track {
  width: 100%;
  max-width: 36px;
  height: 100%;
  max-height: 110px;
  border-radius: var(--radius-sm) var(--radius-sm) 0 0;
  background: var(--bg-hover);
  position: relative;
  overflow: hidden;
}
.bar-fill {
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  height: var(--bar-height);
  background: var(--bar-color);
  border-radius: var(--radius-sm) var(--radius-sm) 0 0;
  transition: height 0.6s cubic-bezier(0.34, 1.56, 0.64, 1);
  animation: barGrow 0.5s ease-out forwards;
  transform-origin: bottom;
}
@keyframes barGrow {
  from { transform: scaleY(0); }
  to { transform: scaleY(1); }
}
.bar-label {
  font-size: 10px;
  color: var(--text-tertiary);
  white-space: nowrap;
}

/* ===== Gantt Chart (beautified) ===== */
.gantt-chart {
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  overflow: hidden;
}
.gantt-header, .gantt-row {
  display: grid;
  grid-template-columns: 2fr 2fr 100px 100px 160px;
  gap: var(--space-2);
  align-items: center;
  padding: var(--space-3) var(--space-4);
}
.gantt-header {
  background: var(--bg-hover);
  font-size: var(--text-xs);
  color: var(--text-tertiary);
  font-weight: var(--weight-semibold);
  text-transform: uppercase;
  letter-spacing: 0.3px;
}
.gantt-row {
  border-top: 1px solid var(--border-default);
  transition: background var(--transition-fast);
}
.gantt-row:hover {
  background: var(--bg-hover);
}
.item-title {
  font-size: var(--text-base);
  color: var(--text-primary);
  font-weight: var(--weight-medium);
}
.progress-bar-wrapper {
  width: 100%;
  height: 20px;
  background: var(--border-default);
  border-radius: var(--radius-full);
  overflow: hidden;
}
.progress-bar-fill {
  height: 100%;
  border-radius: var(--radius-full);
  background: var(--fill-color, var(--brand-500));
  transition: width 0.5s ease;
  min-width: 4px;
  position: relative;
}
.progress-bar-fill::after {
  content: '';
  position: absolute;
  top: 2px;
  right: 4px;
  width: 6px;
  height: 6px;
  background: rgba(255,255,255,0.4);
  border-radius: 50%;
}
.progress-text {
  font-size: var(--text-sm);
  font-weight: var(--weight-semibold);
}
.deadline-text {
  font-size: var(--text-sm);
  color: var(--text-secondary);
}
.no-deadline {
  color: var(--text-tertiary);
  font-size: var(--text-sm);
}

/* ===== Path Cards (beautified) ===== */
.paths-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: var(--space-4);
}
.path-card {
  cursor: pointer;
  border: 1px solid var(--border-card);
  transition: transform var(--transition-base), box-shadow var(--transition-base), border-color var(--transition-base);
  background: var(--bg-card);
  border-radius: var(--radius-lg);
}
.path-card:hover {
  transform: translateY(-3px);
  box-shadow: var(--shadow-lg);
  border-color: var(--brand-200);
}
.path-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--space-2);
}
.path-header h3 {
  margin: 0;
  font-size: var(--text-lg);
  color: var(--text-primary);
  font-weight: var(--weight-semibold);
}
.path-desc {
  font-size: var(--text-sm);
  color: var(--text-tertiary);
  margin: 0 0 var(--space-3);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.path-progress {
  margin-bottom: var(--space-2);
}
.path-meta {
  font-size: var(--text-xs);
  color: var(--text-tertiary);
}

/* ===== Responsive ===== */
@media (max-width: 900px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  .charts-row {
    grid-template-columns: 1fr;
  }
}
@media (max-width: 600px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }
  .gantt-header, .gantt-row {
    grid-template-columns: 1.5fr 1.5fr 70px 80px 120px;
    font-size: var(--text-xs);
    padding: var(--space-2) var(--space-3);
  }
  .dashboard-header {
    padding: var(--space-4);
  }
}
</style>
