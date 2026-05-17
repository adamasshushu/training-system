<template>
  <div class="student-tasks">
    <div class="page-header"><h2>我的培训任务</h2></div>

    <el-empty v-if="tasks.length===0 && !loading" description="暂无指派给你的培训任务" />

    <div v-else v-loading="loading">
      <el-card v-for="task in tasks" :key="task.ID" shadow="hover" class="task-card" @click="showDetail(task)">
        <div class="task-header">
          <h3>{{ task.标题 }}</h3>
          <el-tag :type="task.模式 === 'level' ? 'warning' : 'info'" size="small">
            {{ task.模式 === 'level' ? '闯关模式' : '自由模式' }}
          </el-tag>
        </div>
        <p class="task-desc" v-if="task.描述">{{ task.描述 }}</p>
        <div class="task-meta">
          <span>创建人: {{ task.创建人姓名 }}</span>
          <span v-if="task.截止日期">截止: {{ task.截止日期 }}</span>
        </div>
        <!-- Progress bar -->
        <div v-if="task.进度 !== undefined" class="progress-area">
          <el-progress :percentage="task.进度" :color="task.进度===100?'#67C23A':'#409EFF'" />
          <span class="progress-text">{{ task.已完成数 }}/{{ task.总项目数 }} 完成</span>
        </div>
      </el-card>
    </div>

    <!-- 详情弹窗 -->
    <el-dialog v-model="detailDialog" :title="detailTask.标题" width="600px">
      <div v-loading="detailLoading">
        <p style="color:#909399;margin-bottom:16px">{{ detailTask.描述 || '暂无描述' }}</p>
        <el-progress :percentage="detailProgress.总进度" :color="detailProgress.总进度===100?'#67C23A':'#409EFF'" :stroke-width="20" style="margin-bottom:20px">
          <template #default="{ percentage }">{{ percentage }}%</template>
        </el-progress>

        <h4>📖 课程 ({{ detailProgress.课程进度 ? detailProgress.课程进度.length : 0 }})</h4>
        <div v-for="c in (detailProgress.课程进度||[])" :key="c.课程ID" class="progress-item">
          <div class="progress-item-header">
            <span>{{ c.标题 }}</span>
            <el-tag :type="c.进度===100?'success':'info'" size="small">{{ c.进度 }}%</el-tag>
          </div>
          <el-progress :percentage="c.进度" :stroke-width="8" :color="c.进度===100?'#67C23A':'#409EFF'" />
          <span class="progress-detail">{{ c.已完成 }}/{{ c.总课时 }} 课时</span>
        </div>

        <h4 style="margin-top:20px">📝 考试 ({{ detailProgress.考试进度 ? detailProgress.考试进度.length : 0 }})</h4>
        <div v-for="e in (detailProgress.考试进度||[])" :key="e.考试ID" class="progress-item">
          <div class="progress-item-header">
            <span>{{ e.标题 }}</span>
            <el-tag :type="e.状态==='passed'?'success':e.状态==='failed'?'danger':'info'" size="small">
              {{ e.状态==='passed'?'✅ 通过 ('+e.得分+'分)':e.状态==='failed'?'❌ 未通过':'⬜ 未开始' }}
            </el-tag>
          </div>
        </div>
      </div>
      <template #footer>
        <el-button @click="detailDialog = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getMyTasks, getTaskProgress } from '@/api/tasks'

const loading = ref(false)
const tasks = ref([])

const detailDialog = ref(false)
const detailLoading = ref(false)
const detailTask = ref({})
const detailProgress = ref({})

const loadData = async () => {
  loading.value = true
  try {
    const res = await getMyTasks()
    const rawTasks = res.数据 || []
    // Load progress for each task
    tasks.value = []
    for (const t of rawTasks) {
      try {
        const pr = await getTaskProgress(t.ID)
        t.进度 = pr.数据.总进度
        t.已完成数 = pr.数据.已完成数
        t.总项目数 = pr.数据.总项目数
      } catch {
        t.进度 = 0; t.已完成数 = 0; t.总项目数 = 0
      }
      tasks.value.push(t)
    }
  } catch {} finally { loading.value = false }
}

const showDetail = async (task) => {
  detailTask.value = task; detailDialog.value = true; detailLoading.value = true
  try {
    const pr = await getTaskProgress(task.ID); detailProgress.value = pr.数据
  } catch {} finally { detailLoading.value = false }
}

onMounted(() => loadData())
</script>

<style scoped>
.student-tasks { max-width: 1200px; margin: 0 auto; padding: 24px; }
.page-header { margin-bottom: 24px; }
.page-header h2 { font-size: 24px; font-weight: 700; color: #303133; }
.task-card { margin-bottom: 16px; border-radius: 12px; cursor: pointer; transition: all 0.2s; }
.task-card:hover { transform: translateY(-2px); }
.task-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px; }
.task-header h3 { font-size: 18px; font-weight: 600; color: #303133; }
.task-desc { color: #909399; font-size: 14px; margin-bottom: 12px; }
.task-meta { display: flex; gap: 24px; font-size: 13px; color: #909399; margin-bottom: 12px; }
.progress-area { display: flex; align-items: center; gap: 16px; }
.progress-text { font-size: 13px; color: #606266; white-space: nowrap; }
.progress-item { margin-bottom: 12px; }
.progress-item-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px; font-size: 14px; }
.progress-detail { font-size: 12px; color: #909399; }
</style>
