<template>
  <div class="feedback-page">
    <el-card class="page-card">
      <h2 style="margin: 0 0 20px; font-size: 18px">⭐ 培训反馈</h2>
      <p class="page-desc">完成培训任务后，请为本次培训内容和系统体验打分</p>

      <el-form label-position="top" class="feedback-form" @submit.prevent="submitFeedback">
        <el-form-item label="关联任务（可选）">
          <el-select v-model="form.task_id" placeholder="选择已完成的培训任务" filterable clearable style="width: 100%">
            <el-option v-for="t in tasks" :key="t.ID" :label="t.标题" :value="t.ID" />
          </el-select>
        </el-form-item>

        <el-form-item label="培训内容评分">
          <el-rate v-model="form.content_rating" :max="5" show-score score-template="{value} 分" />
        </el-form-item>

        <el-form-item label="系统体验评分">
          <el-rate v-model="form.system_rating" :max="5" show-score score-template="{value} 分" />
        </el-form-item>

        <el-form-item label="你的建议（选填）">
          <el-input v-model="form.suggestion" type="textarea" :rows="4" placeholder="说说你的想法..." />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" size="large" @click="submitFeedback" :loading="submitting">提交反馈</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 课程评分 -->
    <el-card class="page-card" style="margin-top: 16px">
      <h2 style="margin: 0 0 16px; font-size: 18px">📚 给课程评分</h2>
      
      <el-table :data="courses" v-loading="loadingCourses" stripe @row-click="rateCourse">
        <el-table-column prop="标题" label="课程名称" min-width="200" />
        <el-table-column label="我的评分" width="200">
          <template #default="{ row }">
            <el-rate v-if="row.我的评分" :model-value="row.我的评分" disabled show-score :score-template="`${row.我的评分}`" />
            <el-tag v-else size="small" type="info">未评价</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100">
          <template #default="{ row }">
            <el-button type="primary" link>{{ row.我的评分 ? '修改' : '评价' }}</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 课程评分对话框 -->
    <el-dialog v-model="rateDialogVisible" :title="rateDialogTitle" width="500px">
      <el-form label-position="top">
        <el-form-item label="评分">
          <el-rate v-model="rateForm.rating" :max="5" show-score score-template="{value} 分" />
        </el-form-item>
        <el-form-item label="评价内容（选填）">
          <el-input v-model="rateForm.content" type="textarea" :rows="3" placeholder="写下你的学习感受..." />
        </el-form-item>
        <el-form-item>
          <el-checkbox v-model="rateForm.is_anonymous">匿名评价</el-checkbox>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="rateDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveRate" :loading="savingRate">提交</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getToken } from '@/utils/auth'
import axios from 'axios'

const API = axios.create({ baseURL: '' })
API.interceptors.request.use((c) => { c.headers.Authorization = `Bearer ${getToken()}`; return c })

const form = reactive({ task_id: null, content_rating: 3, system_rating: 3, suggestion: '' })
const submitting = ref(false)
const tasks = ref([])

// 课程评分
const courses = ref([])
const loadingCourses = ref(false)
const rateDialogVisible = ref(false)
const rateDialogTitle = ref('')
const savingRate = ref(false)
const rateForm = reactive({ course_id: null, rating: 3, content: '', is_anonymous: false })

const loadTasks = async () => {
  try {
    const res = await API.get('/api/tasks/my')
    tasks.value = res.data.数据 || []
  } catch { /* silent */ }
}

const loadCourses = async () => {
  loadingCourses.value = true
  try {
    const res = await API.get('/api/courses/student')
    const courseList = res.data.数据 || []
    // Check if already rated
    for (const c of courseList) {
      try {
        const r = await API.get(`/api/reviews/course/${c.ID}`, { params: { page_size: 100 } })
        const reviews = r.data.数据 || []
        const mine = reviews.find(rv => rv.评价人 !== '匿名用户')
        // We can't easily check "my" review without user info, so just show unrated
        c.我的评分 = null
      } catch { c.我的评分 = null }
    }
    courses.value = courseList
  } catch { /* silent */ }
  finally { loadingCourses.value = false }
}

const rateCourse = (row) => {
  rateForm.course_id = row.ID
  rateForm.rating = 3
  rateForm.content = ''
  rateForm.is_anonymous = false
  rateDialogTitle = `评价: ${row.标题}`
  rateDialogVisible = true
}

const saveRate = async () => {
  savingRate.value = true
  try {
    await API.post('/api/reviews/course', {
      course_id: rateForm.course_id,
      rating: rateForm.rating,
      content: rateForm.content || null,
      is_anonymous: rateForm.is_anonymous,
    })
    ElMessage.success('评价已提交')
    rateDialogVisible.value = false
    // 标记已评
    const c = courses.value.find(x => x.ID === rateForm.course_id)
    if (c) c.我的评分 = rateForm.rating
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '提交失败')
  } finally { savingRate.value = false }
}

const submitFeedback = async () => {
  submitting.value = true
  try {
    await API.post('/api/reviews/feedback', {
      task_id: form.task_id || null,
      content_rating: form.content_rating,
      system_rating: form.system_rating,
      suggestion: form.suggestion || null,
    })
    ElMessage.success('反馈已提交，谢谢！')
    form.task_id = null
    form.content_rating = 3
    form.system_rating = 3
    form.suggestion = ''
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '提交失败')
  } finally { submitting.value = false }
}

onMounted(() => { loadTasks(); loadCourses() })
</script>

<style scoped>
.feedback-page { max-width: 800px; margin: 0 auto; }
.page-desc { font-size: 13px; color: #909399; margin: -12px 0 20px; }
.feedback-form { max-width: 600px; }
</style>
