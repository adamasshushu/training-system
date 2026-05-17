<template>
  <div class="student-dashboard">
    <div class="welcome-banner">
      <div class="welcome-text">
        <h1>欢迎回来，{{ userName }}</h1>
        <p>继续你的学习之旅吧！</p>
      </div>
      <div class="welcome-stats">
        <div class="stat-item">
          <span class="stat-num">{{ stats.courseCount }}</span>
          <span class="stat-label">可选课程</span>
        </div>
        <div class="stat-item">
          <span class="stat-num">{{ stats.examCount }}</span>
          <span class="stat-label">可考卷</span>
        </div>
        <div class="stat-item">
          <span class="stat-num">{{ stats.taskCount }}</span>
          <span class="stat-label">我的任务</span>
        </div>
        <div class="stat-item">
          <span class="stat-num">{{ stats.certCount }}</span>
          <span class="stat-label">获得证书</span>
        </div>
      </div>
    </div>

    <el-row :gutter="24" v-loading="loading">
      <el-col :xs="24" :lg="16">
        <el-card shadow="never" class="section-card">
          <template #header><div class="section-header"><span class="section-title">可选课程</span><router-link to="/student/courses" class="view-more">查看全部</router-link></div></template>
          <el-empty v-if="courses.length===0" description="暂无课程" :image-size="60" />
          <div v-for="c in courses.slice(0,4)" :key="c.ID" class="course-item" @click="$router.push('/student/courses/'+c.ID)">
            <h4>{{ c.标题 }}</h4>
            <p style="color:#909399;font-size:13px">{{ c.讲师姓名||'待定' }}</p>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :lg="8">
        <el-card shadow="never" class="section-card">
          <template #header><span class="section-title">我的任务</span></template>
          <el-empty v-if="tasks.length===0" description="暂无任务" :image-size="60" />
          <div v-for="t in tasks.slice(0,5)" :key="t.ID" class="task-item" @click="$router.push('/student/tasks')">
            <span>{{ t.标题 }}</span>
            <el-tag size="small" :type="t.模式==='level'?'warning':'info'">{{ t.模式==='level'?'闯关':'自由' }}</el-tag>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { getStudentCourses } from '@/api/courses'
import { getExams } from '@/api/exams'
import { getMyTasks } from '@/api/tasks'
import { getMyCertificates } from '@/api/certificates'

const loading = ref(false)
const userName = ref('学员')
const courses = ref([]); const tasks = ref([])
const stats = reactive({ courseCount:0, examCount:0, taskCount:0, certCount:0 })

onMounted(async () => {
  loading.value = true
  try {
    const [cr, er, tr, ctr] = await Promise.all([
      getStudentCourses(), getExams({is_published:true,page_size:100}),
      getMyTasks(), getMyCertificates()
    ])
    courses.value = cr.数据||[]; tasks.value = tr.数据||[]
    stats.courseCount = courses.value.length
    stats.examCount = (er.数据||[]).length
    stats.taskCount = tasks.value.length
    stats.certCount = (ctr.数据||[]).length

    // Get user name from token/localStorage
    const userInfo = localStorage.getItem('training-system-user')
    if (userInfo) { try { userName.value = JSON.parse(userInfo).真实姓名||'学员' } catch {} }
  } catch {} finally { loading.value = false }
})
</script>

<style scoped>
.student-dashboard { max-width:1200px; margin:0 auto; padding:24px }
.welcome-banner { display:flex; align-items:center; justify-content:space-between; padding:32px; background:linear-gradient(135deg,#409EFF,#337ecc); border-radius:16px; margin-bottom:24px; color:#fff }
.welcome-text h1 { font-size:28px; margin-bottom:8px }
.welcome-text p { font-size:16px; opacity:0.9 }
.welcome-stats { display:flex; gap:32px }
.stat-item { text-align:center }
.stat-num { display:block; font-size:28px; font-weight:700 }
.stat-label { font-size:13px; opacity:0.85 }
.section-card { margin-bottom:20px; border-radius:12px }
.section-header { display:flex; justify-content:space-between; align-items:center }
.section-title { font-size:16px; font-weight:600 }
.view-more { font-size:13px; color:#409EFF; text-decoration:none }
.course-item { padding:12px; border-bottom:1px solid #f0f0f0; cursor:pointer }
.course-item:hover { background:#f5f7fa }
.course-item h4 { font-size:15px; margin-bottom:4px }
.task-item { display:flex; justify-content:space-between; align-items:center; padding:10px; border-bottom:1px solid #f0f0f0; cursor:pointer }
.task-item:hover { background:#f5f7fa }
</style>
