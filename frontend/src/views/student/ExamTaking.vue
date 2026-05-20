<template>
  <div class="exam-taking">
    <!-- 顶部考试导航栏（粘性） -->
    <div class="exam-navbar" v-if="!submitted && !loadError">
      <div class="navbar-inner">
        <div class="navbar-left">
          <h2 class="exam-title">{{ exam.标题 }}</h2>
          <span class="exam-badge">
            第 {{ currentIndex + 1 }}/{{ questions.length }} 题
          </span>
        </div>
        <div class="navbar-center">
          <div class="progress-dots">
            <div
              v-for="(q, idx) in questions"
              :key="idx"
              class="progress-dot"
              :class="{
                answered: answers[q.ID],
                current: currentIndex === idx,
                wrong: submitted && !isCorrect(q)
              }"
              @click="currentIndex = idx"
            ></div>
          </div>
        </div>
        <div class="navbar-right">
          <div class="timer" :class="{ 'timer-warning': timeLeft < 300, 'timer-danger': timeLeft < 60 }">
            <el-icon :size="18"><Timer /></el-icon>
            <span>{{ formattedTime }}</span>
          </div>
          <el-button type="primary" size="small" @click="showSubmitDialog" class="submit-nav-btn">
            <el-icon><Select /></el-icon>
            交卷
          </el-button>
        </div>
      </div>
    </div>

    <!-- 加载态 -->
    <div v-if="loading" class="loading-container">
      <el-skeleton :rows="6" animated />
    </div>

    <!-- 主考试区 -->
    <div class="exam-body" v-else-if="!submitted && !loadError">
      <div class="exam-main">
        <!-- 题目卡片 -->
        <transition name="question-slide" mode="out-in">
          <div class="question-card" :key="currentIndex">
            <div class="question-header">
              <div class="question-type-badge">
                <el-tag :type="typeTag(currentQuestion.题型)" size="small" round>
                  <el-icon :size="12" style="margin-right:3px;vertical-align:-2px">
                    <Select v-if="currentQuestion.题型 === 'single'" />
                    <CircleCheck v-else-if="currentQuestion.题型 === 'multi'" />
                    <SemiSelect v-else-if="currentQuestion.题型 === 'judge'" />
                    <EditPen v-else />
                  </el-icon>
                  {{ typeLabel(currentQuestion.题型) }}
                </el-tag>
                <span class="question-score">{{ currentQuestion.分值 }} 分</span>
              </div>
            </div>

            <h3 class="question-text">{{ currentQuestion.题目内容 }}</h3>

            <!-- 选择题选项 -->
            <div v-if="currentQuestion.题型 === 'single' || currentQuestion.题型 === 'multi'" class="options">
              <div
                v-for="(opt, idx) in parseOptions(currentQuestion.选项)"
                :key="idx"
                class="option"
                :class="{
                  selected: isSelected(opt.标签),
                  correct: submitted && opt.标签 === currentQuestion.正确答案,
                  wrong: submitted && isSelected(opt.标签) && opt.标签 !== currentQuestion.正确答案
                }"
                @click="selectChoice(opt.标签)"
              >
                <div class="option-marker">
                  <div v-if="currentQuestion.题型 === 'single'" class="radio-circle" :class="{ checked: isSelected(opt.标签) }">
                    <div v-if="isSelected(opt.标签)" class="radio-dot"></div>
                  </div>
                  <div v-else class="checkbox-square" :class="{ checked: isSelected(opt.标签) }">
                    <el-icon v-if="isSelected(opt.标签)" :size="12"><Check /></el-icon>
                  </div>
                </div>
                <span class="option-label">{{ opt.标签 }}.</span>
                <span class="option-text">{{ opt.内容 }}</span>
              </div>
            </div>

            <!-- 判断题 -->
            <div v-else-if="currentQuestion.题型 === 'judge'" class="options judge-options">
              <div
                class="option judge-option"
                :class="{
                  selected: currentAnswer === 'A',
                  correct: submitted && 'A' === currentQuestion.正确答案,
                  wrong: submitted && currentAnswer === 'A' && 'A' !== currentQuestion.正确答案
                }"
                @click="selectAnswer('A')"
              >
                <div class="judge-icon correct-icon"><span>✓</span></div>
                <span>正确</span>
              </div>
              <div
                class="option judge-option"
                :class="{
                  selected: currentAnswer === 'B',
                  correct: submitted && 'B' === currentQuestion.正确答案,
                  wrong: submitted && currentAnswer === 'B' && 'B' !== currentQuestion.正确答案
                }"
                @click="selectAnswer('B')"
              >
                <div class="judge-icon wrong-icon"><span>✕</span></div>
                <span>错误</span>
              </div>
            </div>

            <!-- 填空题 -->
            <div v-else class="fill-answer">
              <el-input
                v-model="currentAnswer"
                :placeholder="currentQuestion.题型 === 'fill' ? '请输入答案...' : '请输入你的回答...'"
                :rows="currentQuestion.题型 === 'short_answer' ? 4 : 2"
                :type="currentQuestion.题型 === 'short_answer' ? 'textarea' : 'text'"
                clearable
                size="large"
              />
            </div>
          </div>
        </transition>

        <!-- 导航按钮 -->
        <div class="nav-buttons">
          <el-button
            :disabled="currentIndex === 0"
            @click="prevQuestion"
            class="nav-btn"
          >
            <el-icon><ArrowLeft /></el-icon>
            上一题
          </el-button>

          <div class="nav-center-info">
            <span class="answered-count">已答 <strong>{{ answeredCount }}</strong>/{{ questions.length }}</span>
          </div>

          <el-button
            v-if="currentIndex < questions.length - 1"
            type="primary"
            @click="nextQuestion"
            class="nav-btn"
          >
            下一题
            <el-icon><ArrowRight /></el-icon>
          </el-button>
          <el-button
            v-else
            type="success"
            @click="showSubmitDialog"
            class="nav-btn submit-btn"
          >
            <el-icon><Select /></el-icon>
            提交试卷
          </el-button>
        </div>
      </div>

      <!-- 侧边答题卡 -->
      <div class="exam-sidebar">
        <div class="sidebar-card">
          <div class="sidebar-title">
            <el-icon><Document /></el-icon> 答题卡
          </div>
          <div class="sheet-grid">
            <div
              v-for="(q, idx) in questions"
              :key="idx"
              class="sheet-num"
              :class="{
                answered: answers[q.ID],
                current: currentIndex === idx,
                skipped: !answers[q.ID]
              }"
              @click="currentIndex = idx"
            >
              {{ idx + 1 }}
            </div>
          </div>
          <div class="sheet-legend">
            <span><span class="legend-dot answered"></span>已答</span>
            <span><span class="legend-dot"></span>未答</span>
            <span><span class="legend-dot current-dot"></span>当前</span>
          </div>
          <el-divider />
          <div class="sidebar-stats">
            <div class="stat-row">
              <span>已完成</span>
              <span class="stat-val">{{ Math.round(answeredCount / questions.length * 100) || 0 }}%</span>
            </div>
            <el-progress :percentage="Math.round(answeredCount / questions.length * 100) || 0" :stroke-width="6" />
          </div>
        </div>

        <!-- 快捷键提示 -->
        <div class="shortcuts-hint">
          <span><kbd>←</kbd> <kbd>→</kbd> 切换题目</span>
          <span><kbd>1</kbd>-<kbd>4</kbd> 选择选项</span>
        </div>
      </div>
    </div>

    <!-- 提交确认弹窗 -->
    <el-dialog v-model="submitDialog" title="📝 确认提交" width="460px" class="submit-dialog">
      <div class="submit-summary">
        <div class="summary-grid">
          <div class="summary-item">
            <div class="summary-num">{{ answeredCount }}</div>
            <div class="summary-label">已答题</div>
          </div>
          <div class="summary-item">
            <div class="summary-num">{{ unansweredCount }}</div>
            <div class="summary-label">未答题</div>
          </div>
          <div class="summary-item">
            <div class="summary-num">{{ questions.length }}</div>
            <div class="summary-label">总题数</div>
          </div>
        </div>
        <p class="submit-warning" v-if="unansweredCount > 0">
          <el-icon><WarningFilled /></el-icon>
          你还有 <strong>{{ unansweredCount }}</strong> 道题未作答，确定要提交吗？
        </p>
        <p class="submit-hint">提交后不可修改，请仔细检查。</p>
      </div>
      <template #footer>
        <el-button @click="submitDialog = false">继续作答</el-button>
        <el-button type="primary" @click="confirmSubmit" :loading="submitting">
          {{ submitting ? '提交中...' : '确认提交' }}
        </el-button>
      </template>
    </el-dialog>

    <!-- 成绩展示 -->
    <div v-if="submitted" class="result-page">
      <div class="result-card" :class="{ passed: resultPassed }">
        <div class="result-icon">
          <el-icon v-if="resultPassed" color="#10b981" :size="64"><CircleCheckFilled /></el-icon>
          <el-icon v-else color="#ef4444" :size="64"><CloseBold /></el-icon>
        </div>
        <h2 class="result-title">{{ resultPassed ? '恭喜通过！' : '未通过' }}</h2>
        <div class="result-score">
          <span class="score-num">{{ resultScore }}</span>
          <span class="score-divider">/</span>
          <span class="score-total">{{ resultTotal }}</span>
        </div>
        <div class="result-meta">
          <span>用时：{{ elapsedTime }}</span>
          <span>及格线：{{ exam.及格分 || 60 }} 分</span>
        </div>
        <el-button type="primary" size="large" @click="$router.push('/student/exams')" class="result-btn">
          返回考试列表
        </el-button>
      </div>
    </div>

    <!-- 加载错误 -->
    <el-result v-if="loadError" icon="error" title="加载失败" sub-title="请检查网络或联系管理员">
      <template #extra>
        <el-button type="primary" @click="$router.go(-1)">返回</el-button>
      </template>
    </el-result>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  Timer, CircleCheck, SemiSelect, Select, ArrowLeft, ArrowRight,
  Check, Document, EditPen, WarningFilled, CircleCheckFilled, CloseBold
} from '@element-plus/icons-vue'
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
const startTime = ref(0)
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

const answeredCount = computed(() => {
  return questions.value.filter(q => {
    const a = answers.value[q.ID]
    if (!a) return false
    if (Array.isArray(a)) return a.length > 0
    return String(a).trim() !== ''
  }).length
})

const unansweredCount = computed(() => questions.value.length - answeredCount.value)

const formattedTime = computed(() => {
  const m = Math.floor(timeLeft.value / 60)
  const s = timeLeft.value % 60
  return String(m).padStart(2, '0') + ':' + String(s).padStart(2, '0')
})

const elapsedTime = computed(() => {
  const elapsed = Math.floor((Date.now() - startTime.value) / 1000)
  const m = Math.floor(elapsed / 60)
  const s = elapsed % 60
  return `${m}分${s}秒`
})

const parseOptions = (opts) => {
  if (!opts) return []
  try {
    const arr = typeof opts === 'string' ? JSON.parse(opts) : opts
    return arr.map((v, i) => ({ 标签: String.fromCharCode(65 + i), 内容: typeof v === 'string' ? v : v.内容 || v }))
  } catch { return [] }
}

const isSelected = (label) => {
  const ans = answers.value[currentQuestion.value.ID]
  if (currentQuestion.value.题型 === 'multi') return Array.isArray(ans) && ans.includes(label)
  return ans === label
}

const selectChoice = (label) => {
  if (currentQuestion.value.题型 === 'single') {
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

const isCorrect = (q) => {
  const a = answers.value[q.ID]
  if (!a) return false
  return String(a) === String(q.正确答案)
}

const nextQuestion = () => {
  if (currentIndex.value < questions.value.length - 1) currentIndex.value++
}
const prevQuestion = () => {
  if (currentIndex.value > 0) currentIndex.value--
}

const showSubmitDialog = () => { submitDialog.value = true }

const confirmSubmit = async () => {
  submitting.value = true
  try {
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
    ElMessage.success('试卷提交成功！')
  } catch {
    ElMessage.error('提交失败，请重试')
  } finally { submitting.value = false }
}

const typeTag = (t) => ({ single: 'primary', multi: 'warning', judge: 'success', fill: 'info', short_answer: '' }[t] || 'info')
const typeLabel = (t) => ({ single: '单选', multi: '多选', judge: '判断', fill: '填空', short_answer: '简答' }[t] || t)

// Keyboard shortcuts
const handleKeydown = (e) => {
  if (submitted.value || loadError.value || submitDialog.value) return
  if (e.key === 'ArrowRight') { e.preventDefault(); nextQuestion() }
  if (e.key === 'ArrowLeft') { e.preventDefault(); prevQuestion() }
  if (['1','2','3','4'].includes(e.key) && currentQuestion.value.题型 !== 'fill' && currentQuestion.value.题型 !== 'short_answer') {
    e.preventDefault()
    const label = String.fromCharCode(64 + parseInt(e.key))
    selectChoice(label)
  }
  if (e.key === 'a' && currentQuestion.value.题型 === 'judge') { e.preventDefault(); selectAnswer('A') }
  if (e.key === 'b' && currentQuestion.value.题型 === 'judge') { e.preventDefault(); selectAnswer('B') }
}

onMounted(async () => {
  window.addEventListener('keydown', handleKeydown)
  startTime.value = Date.now()
  try {
    const res = await getExamDetail(examId)
    const d = res.数据
    exam.value = { 标题: d.标题, 考试时长: d.考试时长, 总分: d.总分, 及格分: d.及格分 }
    questions.value = d.题目列表 || []
    timeLeft.value = (d.考试时长 || 60) * 60
    loading.value = false
  } catch {
    loading.value = false
    loadError.value = true
  }
})

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

onUnmounted(() => {
  clearInterval(timer)
  window.removeEventListener('keydown', handleKeydown)
})
</script>

<style scoped>
.exam-taking {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0;
  min-height: calc(100vh - 64px);
}

/* ===== Top Navbar ===== */
.exam-navbar {
  position: sticky;
  top: 0;
  z-index: 50;
  background: var(--bg-card);
  border-bottom: 1px solid var(--border-default);
  box-shadow: var(--shadow-sm);
  margin-bottom: var(--space-6);
  backdrop-filter: blur(12px);
}
.navbar-inner {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px var(--space-5);
  gap: var(--space-4);
}
.navbar-left {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  min-width: 0;
}
.exam-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.exam-badge {
  font-size: 12px;
  color: var(--text-tertiary);
  background: var(--bg-hover);
  padding: 2px 10px;
  border-radius: var(--radius-full);
  white-space: nowrap;
}
.navbar-center {
  flex: 1;
  max-width: 400px;
  overflow: hidden;
}
.progress-dots {
  display: flex;
  gap: 4px;
  justify-content: center;
  flex-wrap: nowrap;
  overflow-x: auto;
  padding: 4px 0;
}
.progress-dot {
  min-width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--border-default);
  cursor: pointer;
  transition: all 0.2s;
  flex-shrink: 0;
}
.progress-dot.answered { background: var(--brand-500); }
.progress-dot.current { transform: scale(1.4); box-shadow: 0 0 0 2px var(--brand-200); }
.progress-dot.wrong { background: var(--danger); }
.navbar-right {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}
.timer {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 18px;
  font-weight: 700;
  color: var(--text-primary);
  font-variant-numeric: tabular-nums;
  white-space: nowrap;
}
.timer-warning { color: var(--warning) !important; }
.timer-danger { color: var(--danger) !important; animation: pulse 1s ease-in-out infinite; }

/* ===== Exam Body ===== */
.exam-body {
  display: grid;
  grid-template-columns: 1fr 240px;
  gap: var(--space-6);
  padding: 0 var(--space-5) var(--space-10);
  max-width: 1200px;
  margin: 0 auto;
}
.exam-main {
  min-width: 0;
}

/* ===== Question Card ===== */
.question-card {
  background: var(--bg-card);
  border: 1px solid var(--border-card);
  border-radius: var(--radius-xl);
  padding: var(--space-6);
  box-shadow: var(--shadow-card);
  margin-bottom: var(--space-5);
}

.question-header {
  margin-bottom: var(--space-4);
}
.question-type-badge {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}
.question-score {
  font-size: 13px;
  color: var(--text-tertiary);
}
.question-text {
  font-size: 18px;
  font-weight: 500;
  color: var(--text-primary);
  line-height: 1.6;
  margin: 0 0 var(--space-6);
}

/* ===== Options ===== */
.options {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.option {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 18px;
  border: 1.5px solid var(--border-default);
  border-radius: var(--radius-lg);
  cursor: pointer;
  transition: all var(--transition-fast);
  user-select: none;
}
.option:hover {
  border-color: var(--brand-300);
  background: var(--bg-hover);
}
.option.selected {
  border-color: var(--brand-500);
  background: var(--bg-active);
}
.option.correct {
  border-color: var(--success);
  background: rgba(16, 185, 129, 0.05);
}
html.dark .option.correct {
  background: rgba(16, 185, 129, 0.08);
}
.option.wrong {
  border-color: var(--danger);
  background: rgba(239, 68, 68, 0.05);
}
html.dark .option.wrong {
  background: rgba(239, 68, 68, 0.08);
}

.option-marker {
  flex-shrink: 0;
  display: flex;
  align-items: center;
}
.radio-circle {
  width: 20px;
  height: 20px;
  border: 2px solid var(--border-hover);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all var(--transition-fast);
}
.radio-circle.checked {
  border-color: var(--brand-500);
  background: var(--brand-500);
}
.radio-dot {
  width: 8px;
  height: 8px;
  background: #fff;
  border-radius: 50%;
}
.checkbox-square {
  width: 20px;
  height: 20px;
  border: 2px solid var(--border-hover);
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all var(--transition-fast);
  color: #fff;
}
.checkbox-square.checked {
  border-color: var(--brand-500);
  background: var(--brand-500);
}
.option-label {
  font-weight: 600;
  color: var(--text-secondary);
  flex-shrink: 0;
}
.option-text {
  color: var(--text-primary);
  font-size: 14px;
  line-height: 1.5;
}

/* Judge options */
.judge-options {
  flex-direction: row;
  gap: var(--space-4);
}
.judge-option {
  flex: 1;
  justify-content: center;
  font-size: 16px;
  font-weight: 500;
}
.judge-icon {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  font-weight: 700;
  color: #fff;
  flex-shrink: 0;
}
.correct-icon { background: var(--success); }
.wrong-icon { background: var(--danger); }

/* Fill answer */
.fill-answer {
  padding: var(--space-2) 0;
}

/* ===== Nav Buttons ===== */
.nav-buttons {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: var(--space-3);
}
.nav-btn {
  min-width: 120px;
  border-radius: var(--radius-md);
}
.submit-btn {
  font-weight: 600;
}
.nav-center-info {
  font-size: 13px;
  color: var(--text-tertiary);
}
.nav-center-info strong {
  color: var(--text-primary);
}

/* ===== Sidebar ===== */
.exam-sidebar {
  position: sticky;
  top: 84px;
  align-self: start;
}
.sidebar-card {
  background: var(--bg-card);
  border: 1px solid var(--border-card);
  border-radius: var(--radius-xl);
  padding: var(--space-5);
  box-shadow: var(--shadow-card);
}
.sidebar-title {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: var(--space-4);
}
.sheet-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 6px;
  margin-bottom: var(--space-3);
}
.sheet-num {
  width: 100%;
  aspect-ratio: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid var(--border-default);
  border-radius: var(--radius-sm);
  cursor: pointer;
  font-size: 12px;
  color: var(--text-secondary);
  transition: all var(--transition-fast);
}
.sheet-num:hover {
  border-color: var(--brand-300);
  background: var(--bg-hover);
}
.sheet-num.answered {
  background: var(--brand-500);
  color: #fff;
  border-color: var(--brand-500);
}
.sheet-num.current {
  box-shadow: 0 0 0 2px var(--brand-200);
  font-weight: 700;
}
.sheet-num.skipped {
  color: var(--text-tertiary);
}
.sheet-legend {
  display: flex;
  gap: 12px;
  align-items: center;
  font-size: 11px;
  color: var(--text-tertiary);
  margin-bottom: var(--space-3);
}
.legend-dot {
  display: inline-block;
  width: 10px;
  height: 10px;
  border: 1px solid var(--border-default);
  border-radius: 2px;
  vertical-align: middle;
  margin-right: 4px;
}
.legend-dot.answered {
  background: var(--brand-500);
  border-color: var(--brand-500);
}
.current-dot {
  box-shadow: 0 0 0 2px var(--brand-200);
  border-color: var(--brand-300);
}

.sidebar-stats {
  font-size: 12px;
  color: var(--text-tertiary);
}
.stat-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 4px;
}
.stat-val {
  font-weight: 600;
  color: var(--text-primary);
}

/* ===== Shortcuts ===== */
.shortcuts-hint {
  margin-top: var(--space-3);
  font-size: 11px;
  color: var(--text-tertiary);
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 0 var(--space-2);
}
.shortcuts-hint kbd {
  background: var(--bg-hover);
  border: 1px solid var(--border-default);
  border-radius: 3px;
  padding: 1px 6px;
  font-size: 11px;
  font-family: inherit;
}

/* ===== Submit Dialog ===== */
.submit-dialog :deep(.el-dialog__body) {
  padding-top: var(--space-4);
}
.submit-summary {
  text-align: center;
}
.summary-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--space-4);
  margin-bottom: var(--space-5);
}
.summary-item {
  text-align: center;
}
.summary-num {
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary);
}
.summary-label {
  font-size: 12px;
  color: var(--text-tertiary);
  margin-top: 2px;
}
.submit-warning {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  color: var(--warning);
  font-size: 14px;
  margin-bottom: var(--space-2);
}
.submit-hint {
  font-size: 13px;
  color: var(--text-tertiary);
  margin: 0;
}

/* ===== Result Page ===== */
.result-page {
  display: flex;
  justify-content: center;
  padding: var(--space-16) var(--space-5);
}
.result-card {
  text-align: center;
  max-width: 420px;
  width: 100%;
  background: var(--bg-card);
  border: 1px solid var(--border-card);
  border-radius: var(--radius-2xl);
  padding: var(--space-10) var(--space-8);
  box-shadow: var(--shadow-lg);
  animation: fadeInScale 0.4s ease-out;
}
.result-icon {
  margin-bottom: var(--space-4);
}
.result-title {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 var(--space-4);
}
.result-score {
  margin-bottom: var(--space-5);
}
.score-num {
  font-size: 56px;
  font-weight: 800;
  color: var(--text-primary);
  letter-spacing: -2px;
}
.score-divider {
  font-size: 24px;
  color: var(--text-tertiary);
  margin: 0 4px;
  vertical-align: 12px;
}
.score-total {
  font-size: 24px;
  color: var(--text-tertiary);
  vertical-align: 12px;
}
.result-meta {
  display: flex;
  justify-content: center;
  gap: var(--space-6);
  font-size: 13px;
  color: var(--text-tertiary);
  margin-bottom: var(--space-6);
}
.result-btn {
  min-width: 200px;
}
.result-card.passed {
  border-color: rgba(16, 185, 129, 0.2);
}

/* ===== Loading ===== */
.loading-container {
  max-width: 800px;
  margin: 0 auto;
  padding: var(--space-10);
}

/* ===== Question transition ===== */
.question-slide-enter-active {
  animation: slideInRight 0.25s ease-out;
}
.question-slide-leave-active {
  animation: slideInLeft 0.2s ease-in reverse;
}

/* ===== Mobile ===== */
@media (max-width: 900px) {
  .exam-body {
    grid-template-columns: 1fr;
  }
  .exam-sidebar {
    position: static;
    order: -1;
  }
  .sidebar-card {
    display: grid;
    grid-template-columns: 1fr auto;
    gap: var(--space-3);
    align-items: center;
  }
  .sidebar-title { margin-bottom: 0; grid-column: 1; }
  .sheet-grid { grid-column: 1; }
  .sheet-legend { grid-column: 1; }
  .sidebar-stats { grid-column: 2; grid-row: 1 / 5; width: 120px; }
  .shortcuts-hint { display: none; }
  .navbar-center { display: none; }
  .submit-nav-btn { display: none; }
}

@media (max-width: 640px) {
  .exam-title { font-size: 14px; }
  .timer { font-size: 16px; }
  .question-text { font-size: 16px; }
  .judge-options { flex-direction: column; }
  .result-score .score-num { font-size: 42px; }
}

/* ===== Reduced motion ===== */
@media (prefers-reduced-motion: reduce) {
  .question-slide-enter-active,
  .question-slide-leave-active {
    animation: none !important;
  }
  .timer.timer-danger {
    animation: none !important;
  }
}
</style>
