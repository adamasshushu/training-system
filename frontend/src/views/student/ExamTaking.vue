<template>
  <div class="exam-taking">
    <!-- 顶部信息栏 -->
    <div class="exam-header">
      <div class="exam-info-left">
        <h2>{{ exam.标题 }}</h2>
        <span class="question-counter">第 {{ currentIndex + 1 }} / {{ questions.length }} 题</span>
      </div>
      <div class="exam-timer" :class="{ 'time-warning': timeLeft < 300 }">
        <el-icon><Timer /></el-icon>
        <span>{{ formattedTime }}</span>
      </div>
    </div>

    <!-- 加载中 -->
    <el-skeleton :rows="8" animated v-if="loading" />

    <!-- 考试内容 -->
    <el-row :gutter="24" v-else-if="!submitted && !loadError">
      <!-- 题目区域 -->
      <el-col :xs="24" :lg="18">
        <el-card shadow="never" class="question-card">
          <div class="question-type">
            <el-tag :type="typeTag(currentQuestion.题型)" size="small">{{ typeLabel(currentQuestion.题型) }}</el-tag>
            <span style="margin-left:8px;color:#909399;font-size:13px">{{ currentQuestion.分值 }} 分</span>
          </div>
          <h3 class="question-text">{{ currentQuestion.题目内容 }}</h3>

          <!-- 选择题 -->
          <div v-if="currentQuestion.题型 === 'single' || currentQuestion.题型 === 'multi'" class="options">
            <div v-for="(opt, idx) in parseOptions(currentQuestion.选项)" :key="idx"
              class="option"
              :class="{ selected: isSelected(opt.标签) }"
              @click="selectChoice(opt.标签)">
              <el-icon class="option-icon">
                <CircleCheck v-if="isSelected(opt.标签)" color="#409EFF" />
                <Circle v-else />
              </el-icon>
              <span class="option-label">{{ opt.标签 }}.</span>
              <span>{{ opt.内容 }}</span>
            </div>
          </div>

          <!-- 判断题 -->
          <div v-else-if="currentQuestion.题型 === 'judge'" class="options">
            <div class="option" :class="{ selected: currentAnswer === 'A' }" @click="selectAnswer('A')">
              <el-icon class="option-icon"><CircleCheck v-if="currentAnswer === 'A'" color="#67C23A" /><Circle v-else /></el-icon>
              <span>✅ 正确</span>
            </div>
            <div class="option" :class="{ selected: currentAnswer === 'B' }" @click="selectAnswer('B')">
              <el-icon class="option-icon"><CircleCheck v-if="currentAnswer === 'B'" color="#F56C6C" /><Circle v-else /></el-icon>
              <span>❌ 错误</span>
            </div>
          </div>

          <!-- 填空题/简答题 -->
          <div v-else class="fill-answer">
            <el-input v-model="currentAnswer" :placeholder="currentQuestion.题型 === 'fill' ? '请输入答案' : '请输入你的回答'" clearable />
          </div>
        </el-card>

        <!-- 导航按钮 -->
        <div class="nav-buttons">
          <el-button :disabled="currentIndex === 0" @click="currentIndex--">
            <el-icon><ArrowLeft /></el-icon>上一题
          </el-button>
          <el-button v-if="currentIndex < questions.length - 1" type="primary" @click="currentIndex++">
            下一题<el-icon><ArrowRight /></el-icon>
          </el-button>
          <el-button v-else type="success" @click="showSubmitDialog">
            <el-icon><Select /></el-icon>提交试卷
          </el-button>
        </div>
      </el-col>

      <!-- 答题卡 -->
      <el-col :xs="24" :lg="6">
        <el-card shadow="never" class="answer-sheet">
          <template #header><span>答题卡</span></template>
          <div class="sheet-grid">
            <div v-for="(q, idx) in questions" :key="idx"
              class="sheet-number"
              :class="{ answered: answers[q.ID], current: currentIndex === idx }"
              @click="currentIndex = idx">
              {{ idx + 1 }}
            </div>
          </div>
          <div class="sheet-legend">
            <span class="legend-dot answered"></span><span>已答</span>
            <span class="legend-dot"></span><span>未答</span>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 提交确认 -->
    <el-dialog v-model="submitDialog" title="确认提交" width="400px">
      <p>你还有 <strong>{{ unansweredCount }}</strong> 道题未作答。</p>
      <p>确定要提交试卷吗？提交后不可修改。</p>
      <template #footer>
        <el-button @click="submitDialog = false">继续作答</el-button>
        <el-button type="primary" @click="confirmSubmit" :loading="submitting">确认提交</el-button>
      </template>
    </el-dialog>

    <!-- 成绩展示 -->
    <div v-if="submitted" class="result-page">
      <el-result :icon="resultPassed ? 'success' : 'error'" :title="resultPassed ? '恭喜通过！' : '未通过'">
        <template #sub-title>
          <div class="result-score">
            <span style="font-size:48px;font-weight:700;color:#303133">{{ resultScore }}</span>
            <span style="font-size:20px;color:#909399"> / {{ resultTotal }} 分</span>
          </div>
        </template>
        <template #extra>
          <el-button type="primary" @click="$router.push('/student/exams')">返回考试列表</el-button>
        </template>
      </el-result>
    </div>

    <!-- 加载错误 -->
    <el-result v-if="loadError" icon="error" title="加载失败" sub-title="请检查网络或联系管理员" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Timer, CircleCheck, Circle, ArrowLeft, ArrowRight, Select } from '@element-plus/icons-vue'
import { getExamDetail, submitExam } from '@/api/exams'

const route = useRoute()
const examId = route.params.id

const loading = ref(true)
const loadError = ref(false)
const exam = ref({ 标题: '加载中...', 考试时长: 60, 总分: 100, 及格分: 60 })
const questions = ref([])
const currentIndex = ref(0)
const answers = ref({})
const timeLeft = ref(0)
const submitDialog = ref(false)
const submitting = ref(false)
const submitted = ref(false)
const resultScore = ref(0)
const resultTotal = ref(0)
const resultPassed = ref(false)

let timer = null

const currentQuestion = computed(() => questions.value[currentIndex.value] || {})

const currentAnswer = computed({
  get: () => answers.value[currentQuestion.value.ID] || '',
  set: (v) => { answers.value[currentQuestion.value.ID] = v }
})

const formattedTime = computed(() => {
  const m = Math.floor(timeLeft.value / 60)
  const s = timeLeft.value % 60
  return String(m).padStart(2, '0') + ':' + String(s).padStart(2, '0')
})

const unansweredCount = computed(() => {
  let count = 0
  questions.value.forEach(q => {
    const a = answers.value[q.ID]
    if (!a || (Array.isArray(a) && a.length === 0)) count++
  })
  return count
})

const parseOptions = (opts) => {
  if (!opts) return []
  try {
    const arr = JSON.parse(opts)
    return arr.map((v, i) => ({ 标签: String.fromCharCode(65 + i), 内容: v }))
  } catch { return [] }
}

const isSelected = (label) => {
  const ans = answers.value[currentQuestion.value.ID]
  if (currentQuestion.value.题型 === 'multi') return Array.isArray(ans) && ans.includes(label)
  return ans === label
}

const selectChoice = (label) => {
  if (currentQuestion.value.题型 === 'single' || currentQuestion.value.题型 === 'judge') {
    answers.value[currentQuestion.value.ID] = label
  } else if (currentQuestion.value.题型 === 'multi') {
    const cur = answers.value[currentQuestion.value.ID] || []
    const idx = cur.indexOf(label)
    if (idx > -1) cur.splice(idx, 1)
    else cur.push(label)
    answers.value[currentQuestion.value.ID] = [...cur]
  }
}

const selectAnswer = (val) => { answers.value[currentQuestion.value.ID] = val }

const showSubmitDialog = () => { submitDialog.value = true }

const confirmSubmit = async () => {
  submitting.value = true
  try {
    // Build submit payload: { 答案: { questionId: answerString } }
    const answerMap = {}
    questions.value.forEach(q => {
      const a = answers.value[q.ID]
      answerMap[String(q.ID)] = Array.isArray(a) ? a.join(',') : (a || '')
    })
    const res = await submitExam(examId, { 答案: answerMap })
    resultScore.value = res.得分
    resultTotal.value = res.总分
    resultPassed.value = res.状态 === '及格'
    submitted.value = true
    submitDialog.value = false
    clearInterval(timer)
    ElMessage.success('试卷提交成功')
  } catch { ElMessage.error('提交失败') } finally { submitting.value = false }
}

const typeTag = (t) => ({ single: 'primary', multi: 'warning', judge: 'success', fill: 'info', short_answer: '' }[t] || 'info')
const typeLabel = (t) => ({ single: '单选', multi: '多选', judge: '判断', fill: '填空', short_answer: '简答' }[t] || t)

// Load exam data
onMounted(async () => {
  try {
    const res = await getExamDetail(examId)
    const d = res.数据
    exam.value = { 标题: d.标题, 考试时长: d.考试时长, 总分: d.总分, 及格分: d.及格分 }
    questions.value = d.题目列表 || []
    timeLeft.value = d.考试时长 * 60
    loading.value = false
  } catch {
    loading.value = false
    loadError.value = true
  }
})

// Timer
watch(() => exam.value.考试时长, () => {
  if (timer) clearInterval(timer)
  timer = setInterval(() => {
    if (timeLeft.value > 0 && !submitted.value) {
      timeLeft.value--
      if (timeLeft.value <= 0) {
        clearInterval(timer)
        ElMessage.warning('考试时间到，自动提交')
        confirmSubmit()
      }
    }
  }, 1000)
})

onUnmounted(() => clearInterval(timer))
</script>

<style scoped>
.exam-taking { max-width: 1200px; margin: 0 auto; padding: 24px; }
.exam-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 24px; padding: 16px 24px; background: #fff; border-radius: 12px; box-shadow: 0 1px 4px rgba(0,0,0,0.08); }
.exam-info-left { display: flex; align-items: center; gap: 16px; }
.exam-info-left h2 { font-size: 20px; font-weight: 600; color: #303133; }
.question-counter { font-size: 14px; color: #909399; }
.exam-timer { display: flex; align-items: center; gap: 8px; font-size: 20px; font-weight: 700; color: #303133; }
.time-warning { color: #F56C6C !important; }
.question-card { margin-bottom: 20px; border-radius: 12px; padding: 8px; }
.question-type { margin-bottom: 16px; display: flex; align-items: center; }
.question-text { font-size: 18px; color: #303133; margin-bottom: 24px; line-height: 1.6; }
.options { display: flex; flex-direction: column; gap: 12px; }
.option { display: flex; align-items: center; gap: 12px; padding: 14px 20px; border: 1px solid #e4e7ed; border-radius: 8px; cursor: pointer; transition: all 0.2s; }
.option:hover { border-color: #409EFF; background: #f0f5ff; }
.option.selected { border-color: #409EFF; background: #ecf5ff; }
.option-icon { font-size: 18px; }
.option-label { font-weight: 600; color: #606266; }
.fill-answer { padding: 12px 0; }
.nav-buttons { display: flex; justify-content: space-between; margin-bottom: 24px; }
.answer-sheet { border-radius: 12px; position: sticky; top: 88px; }
.sheet-grid { display: grid; grid-template-columns: repeat(5, 1fr); gap: 8px; margin-bottom: 16px; }
.sheet-number { width: 36px; height: 36px; display: flex; align-items: center; justify-content: center; border: 1px solid #e4e7ed; border-radius: 6px; cursor: pointer; font-size: 13px; color: #606266; transition: all 0.2s; }
.sheet-number.answered { background: #ecf5ff; border-color: #409EFF; color: #409EFF; }
.sheet-number.current { background: #409EFF; color: #fff; border-color: #409EFF; }
.sheet-legend { display: flex; gap: 12px; align-items: center; font-size: 12px; color: #909399; }
.legend-dot { width: 12px; height: 12px; border: 1px solid #e4e7ed; border-radius: 2px; }
.legend-dot.answered { background: #ecf5ff; border-color: #409EFF; }
.result-page { padding: 60px 0; text-align: center; }
.result-score { margin: 16px 0; }
</style>
