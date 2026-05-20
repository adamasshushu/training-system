<template>
  <div class="student-exams">
    <div class="page-header"><h2>我的考试</h2></div>

    <el-tabs v-model="activeTab" @tab-change="loadData">
      <el-tab-pane label="待完成" name="pending">
        <el-empty v-if="pendingExams.length === 0 && !loading" description="暂无待完成的考试" />
        <el-row :gutter="20" v-else>
          <el-col :xs="24" :sm="12" :md="8" v-for="exam in pendingExams" :key="exam.ID" style="margin-bottom:20px">
            <el-card shadow="hover" class="exam-card" @click="startExam(exam)">
              <div class="exam-icon"><el-icon :size="36" color="#E6A23C"><EditPen /></el-icon></div>
              <h3>{{ exam.标题 }}</h3>
              <div class="exam-info">
                <p><el-icon><Timer /></el-icon>{{ exam.考试时长 }} 分钟</p>
                <p><el-icon><QuestionFilled /></el-icon>{{ exam.题目数量 }} 题</p>
                <p><el-icon><Trophy /></el-icon>及格 {{ exam.及格分 }}/{{ exam.总分 }}</p>
              </div>
              <el-button type="primary" class="exam-btn" @click.stop="startExam(exam)">开始考试</el-button>
            </el-card>
          </el-col>
        </el-row>
      </el-tab-pane>

      <el-tab-pane label="已完成" name="completed">
        <el-empty v-if="completedList.length === 0 && !loading" description="暂无已完成考试" />
        <el-table :data="completedList" border stripe v-else>
          <el-table-column prop="试卷标题" label="考试名称" min-width="200" />
          <el-table-column label="得分" width="120" align="center">
            <template #default="{ row }">{{ row.得分 }} / {{ row.总分 }}</template>
          </el-table-column>
          <el-table-column label="结果" width="100" align="center">
            <template #default="{ row }">
              <el-tag :type="row.状态 === 'passed' ? 'success' : 'danger'" size="small">
                {{ row.状态 === 'passed' ? '通过' : '未通过' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="提交时间" label="提交时间" width="180" align="center" />
        </el-table>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { EditPen, Timer, QuestionFilled, Trophy } from '@element-plus/icons-vue'
import { getExams, getExamResults } from '@/api/exams'

const router = useRouter()
const activeTab = ref('pending')
const loading = ref(false)
const pendingExams = ref([])
const completedList = ref([])

const loadData = async () => {
  loading.value = true
  try {
    if (activeTab.value === 'pending') {
      const res = await getExams({ is_published: true, page_size: 100 })
      pendingExams.value = res.数据 || []
    } else {
      // Get all exams, then check results for completed ones
      const examsRes = await getExams({ is_published: true, page_size: 100 })
      const exams = examsRes.数据 || []
      const results = []
      for (const exam of exams) {
        try {
          const r = await getExamResults(exam.ID)
          if (r.数据 && r.数据.length > 0) results.push(...r.数据)
        } catch {}
      }
      completedList.value = results
    }
  } catch {} finally { loading.value = false }
}

const startExam = (exam) => {
  router.push(`/student/exams/${exam.ID}`)
}

onMounted(() => loadData())
</script>

<style scoped>
.student-exams { max-width: 1200px; margin: 0 auto; padding: 24px; }
.page-header { margin-bottom: 24px; }
.page-header h2 { font-size: 24px; font-weight: 700; color: var(--text-primary); }
.exam-card { text-align: center; padding: 20px; border-radius: 12px; cursor: pointer; transition: all 0.2s; }
.exam-card:hover { transform: translateY(-2px); }
.exam-icon { margin-bottom: 16px; }
.exam-card h3 { font-size: 18px; font-weight: 600; color: var(--text-primary); margin-bottom: 12px; }
.exam-info { display: flex; justify-content: center; gap: 16px; margin-bottom: 16px; flex-wrap: wrap; }
.exam-info p { display: flex; align-items: center; gap: 4px; font-size: 13px; color: var(--text-tertiary); }
.exam-btn { width: 100%; }
</style>
