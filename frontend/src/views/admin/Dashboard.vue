<template>
  <div class="dashboard">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <h2 class="page-title">系统概览</h2>
        <p class="page-subtitle">欢迎回来，{{ username }}！今天的数据总览</p>
      </div>
      <div class="page-actions">
        <el-button class="action-btn" @click="refreshData" :loading="loading">
          <el-icon><Refresh /></el-icon>
          刷新数据
        </el-button>
      </div>
    </div>

    <!-- Bento Grid Dashboard -->
    <div class="bento-grid" v-loading="loading">
      <!-- Card 1: Big stats summary (2x1) -->
      <div class="bento-card bento-wide stat-summary">
        <div class="bento-card-header">
          <span class="bento-card-title">数据概览</span>
          <el-tag size="small" type="info">实时</el-tag>
        </div>
        <div class="stat-cards-row">
          <div
            v-for="s in statItems"
            :key="s.label"
            class="stat-mini-card"
            @click="$router.push(s.link)"
          >
            <div class="stat-icon" :style="{ background: s.bg, color: s.color }">
              <el-icon :size="18"><component :is="s.icon" /></el-icon>
            </div>
            <div class="stat-info">
              <span class="stat-num">{{ stats[s.key] || 0 }}</span>
              <span class="stat-label">{{ s.label }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Card 2: Quick access (1x1) -->
      <div class="bento-card quick-access">
        <div class="bento-card-header">
          <span class="bento-card-title">⚡ 快速入口</span>
        </div>
        <div class="quick-links-grid">
          <div
            v-for="link in quickLinks"
            :key="link.path"
            class="quick-link-item"
            @click="$router.push(link.path)"
          >
            <el-icon :size="20"><component :is="link.icon" /></el-icon>
            <span>{{ link.label }}</span>
          </div>
        </div>
      </div>

      <!-- Card 3: System status (1x1) -->
      <div class="bento-card system-status">
        <div class="bento-card-header">
          <span class="bento-card-title">系统状态</span>
        </div>
        <div class="status-items">
          <div class="status-item">
            <span class="status-dot online"></span>
            <span class="status-label">服务器</span>
            <el-tag size="small" type="success">运行中</el-tag>
          </div>
          <div class="status-item">
            <span class="status-dot online"></span>
            <span class="status-label">数据库</span>
            <el-tag size="small" type="success">正常</el-tag>
          </div>
          <div class="status-item">
            <span class="status-dot online"></span>
            <span class="status-label">存储服务</span>
            <el-tag size="small" type="success">正常</el-tag>
          </div>
          <div class="status-item">
            <span class="status-dot online"></span>
            <span class="status-label">API</span>
            <el-tag size="small" type="success">正常</el-tag>
          </div>
        </div>
      </div>

      <!-- Card 4: Recent activity (2x1) -->
      <div class="bento-card bento-activity">
        <div class="bento-card-header">
          <span class="bento-card-title">📋 快捷操作</span>
        </div>
        <div class="activity-items">
          <div class="activity-item" @click="$router.push('/admin/courses')">
            <div class="activity-icon create">
              <el-icon><Plus /></el-icon>
            </div>
            <div class="activity-info">
              <span class="activity-title">新建课程</span>
              <span class="activity-desc">添加新的培训课程</span>
            </div>
          </div>
          <div class="activity-item" @click="$router.push('/admin/exams')">
            <div class="activity-icon create">
              <el-icon><EditPen /></el-icon>
            </div>
            <div class="activity-info">
              <span class="activity-title">创建考试</span>
              <span class="activity-desc">发布新的考核任务</span>
            </div>
          </div>
          <div class="activity-item" @click="$router.push('/admin/users')">
            <div class="activity-icon manage">
              <el-icon><User /></el-icon>
            </div>
            <div class="activity-info">
              <span class="activity-title">管理员工</span>
              <span class="activity-desc">查看和编辑员工信息</span>
            </div>
          </div>
          <div class="activity-item" @click="$router.push('/admin/tasks')">
            <div class="activity-icon manage">
              <el-icon><List /></el-icon>
            </div>
            <div class="activity-info">
              <span class="activity-title">分配任务</span>
              <span class="activity-desc">创建培训任务并分配</span>
            </div>
          </div>
          <div class="activity-item" @click="$router.push('/admin/certificate-templates')">
            <div class="activity-icon template">
              <el-icon><CopyDocument /></el-icon>
            </div>
            <div class="activity-info">
              <span class="activity-title">证书模板</span>
              <span class="activity-desc">管理证书样式模板</span>
            </div>
          </div>
          <div class="activity-item" @click="$router.push('/admin/reports')">
            <div class="activity-icon template">
              <el-icon><Download /></el-icon>
            </div>
            <div class="activity-info">
              <span class="activity-title">导出报告</span>
              <span class="activity-desc">生成培训数据报表</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import {
  Reading, EditPen, User, List, Medal, Trophy,
  Plus, Refresh, CopyDocument, Download
} from '@element-plus/icons-vue'
import { getStats } from '@/api/certificates'
import { getUser } from '@/utils/auth'

const loading = ref(false)
const stats = reactive({})
const userInfo = ref(getUser() || {})
const username = computed(() => userInfo.value?.真实姓名 || userInfo.value?.real_name || '管理员')

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
  { label:'题库管理', path:'/admin/questions', icon:Reading },
  { label:'新建考试', path:'/admin/exams', icon:EditPen },
  { label:'新建任务', path:'/admin/tasks', icon:List },
  { label:'证书模板', path:'/admin/certificate-templates', icon:CopyDocument },
]

const loadData = async () => {
  loading.value = true
  try {
    const res = await getStats()
    Object.assign(stats, res.数据 || {})
  } catch {
    // silent
  } finally {
    loading.value = false
  }
}

const refreshData = () => {
  loadData()
}

onMounted(loadData)
</script>

<style scoped>
.dashboard {
  max-width: 1200px;
  animation: fadeIn 0.3s ease-out;
}

/* ===== Page Header ===== */
.page-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: var(--space-6);
}
.page-title {
  font-size: var(--text-3xl);
  font-weight: var(--weight-bold);
  color: var(--text-primary);
  letter-spacing: -0.5px;
}
.page-subtitle {
  font-size: var(--text-sm);
  color: var(--text-tertiary);
  margin-top: 4px;
}
.page-actions {
  display: flex;
  gap: 8px;
}
.action-btn {
  gap: 6px;
}

/* ===== Bento Grid ===== */
.bento-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-5);
}

.bento-wide {
  grid-column: 1 / -1;
}

.bento-activity {
  grid-column: 1 / -1;
}

/* ===== Bento Card ===== */
.bento-card {
  background: var(--bg-card);
  border: 1px solid var(--border-card);
  border-radius: var(--radius-xl);
  padding: var(--space-5);
  transition: all var(--transition-base);
  box-shadow: var(--shadow-card);
}
.bento-card:hover {
  box-shadow: var(--shadow-md);
}

.bento-card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--space-4);
}
.bento-card-title {
  font-size: var(--text-md);
  font-weight: var(--weight-semibold);
  color: var(--text-primary);
}

/* ===== Stats Summary (Bento-wide) ===== */
.stat-cards-row {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(130px, 1fr));
  gap: var(--space-3);
}

.stat-mini-card {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-3);
  border-radius: var(--radius-lg);
  cursor: pointer;
  transition: all var(--transition-fast);
}
.stat-mini-card:hover {
  background: var(--bg-hover);
  transform: translateY(-1px);
}

.stat-icon {
  width: 40px;
  height: 40px;
  border-radius: var(--radius-lg);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.stat-info {
  display: flex;
  flex-direction: column;
}
.stat-num {
  font-size: var(--text-2xl);
  font-weight: var(--weight-bold);
  color: var(--text-primary);
  line-height: 1.2;
  letter-spacing: -0.5px;
}
.stat-label {
  font-size: var(--text-xs);
  color: var(--text-tertiary);
  margin-top: 1px;
}

/* ===== Quick Access ===== */
.quick-links-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-3);
}

.quick-link-item {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-3) var(--space-4);
  border-radius: var(--radius-lg);
  background: var(--bg-hover);
  cursor: pointer;
  transition: all var(--transition-fast);
  color: var(--text-secondary);
  font-size: var(--text-sm);
  font-weight: var(--weight-medium);
}
.quick-link-item:hover {
  background: var(--brand-50);
  color: var(--brand-500);
  transform: translateY(-1px);
}
html.dark .quick-link-item:hover {
  background: rgba(108, 92, 231, 0.1);
}

/* ===== System Status ===== */
.status-items {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.status-item {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-2) var(--space-3);
  border-radius: var(--radius-md);
  transition: background var(--transition-fast);
}
.status-item:hover {
  background: var(--bg-hover);
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}
.status-dot.online {
  background: #10b981;
  box-shadow: 0 0 6px rgba(16, 185, 129, 0.4);
}

.status-label {
  flex: 1;
  font-size: var(--text-sm);
  color: var(--text-primary);
  font-weight: var(--weight-medium);
}

/* ===== Activity ===== */
.activity-items {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: var(--space-3);
}

.activity-item {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-3);
  border-radius: var(--radius-lg);
  cursor: pointer;
  transition: all var(--transition-fast);
}
.activity-item:hover {
  background: var(--bg-hover);
  transform: translateY(-1px);
}

.activity-icon {
  width: 40px;
  height: 40px;
  border-radius: var(--radius-lg);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  color: #fff;
}
.activity-icon.create {
  background: var(--brand-500);
}
.activity-icon.manage {
  background: #10b981;
}
.activity-icon.template {
  background: #f59e0b;
}

.activity-info {
  display: flex;
  flex-direction: column;
}
.activity-title {
  font-size: var(--text-sm);
  font-weight: var(--weight-semibold);
  color: var(--text-primary);
}
.activity-desc {
  font-size: var(--text-xs);
  color: var(--text-tertiary);
  margin-top: 1px;
}

/* ===== Responsive ===== */
@media (max-width: 1024px) {
  .bento-grid {
    gap: var(--space-4);
  }
  .activity-items {
    grid-template-columns: 1fr 1fr;
  }
  .stat-cards-row {
    grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
  }
}

@media (max-width: 640px) {
  .page-header {
    flex-direction: column;
    gap: var(--space-3);
  }
  .bento-grid {
    grid-template-columns: 1fr;
    gap: var(--space-3);
  }
  .activity-items {
    grid-template-columns: 1fr;
  }
  .quick-links-grid {
    grid-template-columns: 1fr;
  }
  .stat-cards-row {
    grid-template-columns: repeat(2, 1fr);
  }
  .stat-num {
    font-size: var(--text-xl);
  }
}

/* ===== Reduced motion ===== */
@media (prefers-reduced-motion: reduce) {
  .dashboard,
  .bento-card,
  .stat-mini-card,
  .quick-link-item,
  .activity-item {
    animation: none !important;
    transition: none !important;
  }
}
</style>
