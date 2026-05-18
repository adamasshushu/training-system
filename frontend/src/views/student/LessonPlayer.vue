<template>
  <div class="lesson-player">
    <!-- 顶部导航 -->
    <div class="player-header">
      <el-button text @click="goBack">
        <el-icon><ArrowLeft /></el-icon>返回课程
      </el-button>
      <span class="course-title">{{ courseName }}</span>
    </div>

    <div class="player-body">
      <!-- 课时内容区 -->
      <div class="content-area">
        <div class="lesson-title-bar">
          <h2>{{ lessonTitle }}</h2>
          <el-tag size="small" :type="lessonTypeTag(lessonType)" effect="plain">
            {{ lessonTypeLabel }}
          </el-tag>
        </div>

        <!-- 视频类型 - 带禁止加速播放功能 -->
        <div v-if="lessonType === 'video'" class="video-section">
          <div class="video-container">
            <video
              ref="videoRef"
              :src="videoUrl"
              :controlsList="disableFastForward ? 'nofullscreen noremoteplayback' : ''"
              controls
              class="video-player"
              @ratechange="onRateChange"
              @loadedmetadata="onVideoLoaded"
              @error="onVideoError"
              @contextmenu.prevent
            >
              您的浏览器不支持视频播放
            </video>
            <div v-if="!videoUrl" class="video-placeholder">
              <el-icon :size="64" color="#a29bfe"><VideoCameraFilled /></el-icon>
              <p>暂无可播放视频</p>
            </div>
          </div>
          <div class="video-controls">
            <div class="speed-toggle">
              <el-switch
                v-model="disableFastForward"
                active-color="#ef4444"
                inactive-color="#6C5CE7"
                @change="onToggleChange"
              />
              <span class="speed-label" :class="{ locked: disableFastForward }">
                <el-icon :size="16" v-if="disableFastForward"><Lock /></el-icon>
                <el-icon :size="16" v-else><Unlock /></el-icon>
                {{ disableFastForward ? '禁止加速播放' : '允许加速播放' }}
              </span>
            </div>
            <div v-if="videoUrl" class="video-info">
              <span class="video-hint">视频地址：{{ videoUrl }}</span>
            </div>
          </div>
        </div>

        <!-- 文档类型 - PDF/PPT/Word在线预览 -->
        <div v-else-if="lessonType === 'document'" class="document-section">
          <div v-if="isPdf" class="pdf-viewer">
            <iframe
              :src="`/api/uploads/${docPath}?inline=1`"
              class="pdf-frame"
              frameborder="0"
            ></iframe>
          </div>
          <div v-else-if="officeViewerUrl" class="office-viewer">
            <iframe
              :src="officeViewerUrl"
              class="office-frame"
              frameborder="0"
              allowfullscreen
            ></iframe>
          </div>
          <div v-else class="document-placeholder">
            <el-icon :size="64" color="#10b981"><Document /></el-icon>
            <p>暂不支持在线预览此文档类型</p>
            <el-button type="primary" :icon="Download" @click="downloadDoc" class="doc-download-btn">
              下载文件查看
            </el-button>
          </div>
          <div class="doc-info" v-if="fileUrl">
            <el-icon><Link /></el-icon>
            <span class="doc-name">{{ fileUrl.split('/').pop() }}</span>
            <el-button text type="primary" :icon="Download" @click="downloadDoc">下载</el-button>
          </div>
        </div>

        <!-- 图文类型 - Markdown渲染 -->
        <div v-else-if="lessonType === 'text'" class="text-content">
          <div class="text-body markdown-body" v-html="renderedMarkdown"></div>
        </div>

        <div v-else class="unknown-type">
          <p>不支持的课时类型：{{ lessonType }}</p>
        </div>

        <!-- 完成学习按钮 -->
        <div class="action-bar">
          <el-button
            type="primary"
            size="large"
            :loading="submitting"
            :disabled="isCompleted"
            @click="markComplete"
          >
            <el-icon><Check /></el-icon>
            {{ isCompleted ? '已完成' : '完成学习' }}
          </el-button>
        </div>
      </div>

      <!-- 侧边导航 -->
      <div class="lesson-nav">
        <h3>课时列表</h3>
        <div class="nav-chapters">
          <div
            v-for="(chapter, cIdx) in allChapters"
            :key="chapter['ID'] || cIdx"
            class="nav-chapter"
          >
            <div class="nav-chapter-title">第{{ cIdx + 1 }}章 {{ chapter['标题'] }}</div>
            <div
              v-for="(les, lIdx) in chapter['课时列表']"
              :key="les['ID'] || lIdx"
              class="nav-lesson"
              :class="{
                active: les['ID'] === currentLessonId,
                completed: les['是否完成']
              }"
              @click="navigateToLesson(les['ID'])"
            >
              <el-icon v-if="les['是否完成']" color="#10b981" size="14"><SuccessFilled /></el-icon>
              <el-icon v-else size="14">
                <VideoPlay v-if="les['课时类型'] === 'video'" />
                <Document v-else-if="les['课时类型'] === 'document'" />
                <Reading v-else />
              </el-icon>
              <span>{{ les['标题'] }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, onBeforeUnmount } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { marked } from 'marked'
import {
  ArrowLeft,
  VideoCameraFilled,
  Document,
  Check,
  SuccessFilled,
  VideoPlay,
  Reading,
  Lock,
  Unlock,
  Download,
  Link
} from '@element-plus/icons-vue'
import { getCourseDetail, updateProgress } from '@/api/courses'

const route = useRoute()
const router = useRouter()
const courseId = route.params.courseId
const currentLessonId = ref(Number(route.params.lessonId))

const courseName = ref('')
const allChapters = ref([])
const lessonTitle = ref('')
const lessonType = ref('')
const lessonContent = ref('')
const videoUrl = ref('')
const fileUrl = ref('')
const isCompleted = ref(false)
const submitting = ref(false)

// Video player state
const videoRef = ref(null)
const disableFastForward = ref(false)

const lessonTypeLabel = computed(() => {
  const map = { video: '视频', document: '文档', text: '图文' }
  return map[lessonType.value] || lessonType.value
})

const lessonTypeTag = (type) => {
  const map = { video: 'primary', document: 'success', text: 'warning' }
  return map[type] || 'info'
}

// Markdown rendering
const renderedMarkdown = computed(() => {
  if (!lessonContent.value) return '<p style="color:#94a3b8">暂无内容</p>'
  try {
    return marked.parse(lessonContent.value)
  } catch {
    return lessonContent.value
  }
})

// Document viewer
const isPdf = computed(() => {
  return fileUrl.value?.toLowerCase().endsWith('.pdf')
})

const docPath = computed(() => {
  if (!fileUrl.value) return ''
  // fileUrl might be a path like "videos/xxx.mp4" or full URL
  const path = fileUrl.value.replace(/^\/api\/uploads\//, '')
  return path
})

const officeViewerUrl = computed(() => {
  if (!fileUrl.value || isPdf.value) return ''
  const ext = fileUrl.value.toLowerCase().split('.').pop()
  const officeExts = ['doc', 'docx', 'ppt', 'pptx', 'xls', 'xlsx']
  if (!officeExts.includes(ext)) return ''
  // Use Microsoft Office Online viewer
  const fileUrl_full = `${window.location.origin}/api/uploads/${docPath.value}`
  return `https://view.officeapps.live.com/op/view.aspx?src=${encodeURIComponent(fileUrl_full)}`
})

const downloadDoc = () => {
  if (fileUrl.value) {
    window.open(fileUrl.value.startsWith('http') ? fileUrl.value : `/api/uploads/${docPath.value}`, '_blank')
  }
}

const findLesson = () => {
  for (const ch of allChapters.value) {
    const lessons = ch['课时列表'] || []
    for (const les of lessons) {
      if (les['ID'] === currentLessonId.value) {
        return les
      }
    }
  }
  return null
}

const loadLesson = () => {
  const lesson = findLesson()
  if (lesson) {
    lessonTitle.value = lesson['标题'] || ''
    lessonType.value = lesson['课时类型'] || ''
    lessonContent.value = lesson['内容'] || ''
    videoUrl.value = lesson['视频地址'] || ''
    fileUrl.value = lesson['文件地址'] || lesson['file_url'] || ''
    isCompleted.value = !!lesson['是否完成']
  } else {
    lessonTitle.value = '课时未找到'
    lessonType.value = ''
  }
}

const navigateToLesson = (lessonId) => {
  currentLessonId.value = lessonId
  router.push(`/student/courses/${courseId}/lessons/${lessonId}`)
  loadLesson()
}

const goBack = () => {
  router.push(`/student/courses/${courseId}`)
}

const markComplete = async () => {
  submitting.value = true
  try {
    await updateProgress(courseId, {
      '课时ID': currentLessonId.value,
      '进度': 100,
      '是否完成': true
    })
    ElMessage.success('学习进度已保存')
    isCompleted.value = true
    // Update local state
    for (const ch of allChapters.value) {
      const lessons = ch['课时列表'] || []
      for (const les of lessons) {
        if (les['ID'] === currentLessonId.value) {
          les['是否完成'] = true
        }
      }
    }
  } catch {
    ElMessage.error('保存进度失败')
  } finally {
    submitting.value = false
  }
}

const fetchData = async () => {
  try {
    const res = await getCourseDetail(courseId)
    courseName.value = res['数据']['标题'] || ''
    allChapters.value = res['数据']['章节列表'] || []
    loadLesson()
  } catch {
    ElMessage.error('加载课程信息失败')
  }
}

// Video player methods
const onRateChange = () => {
  if (disableFastForward.value && videoRef.value) {
    if (videoRef.value.playbackRate > 1) {
      videoRef.value.playbackRate = 1
    }
  }
}

const onVideoLoaded = () => {
  if (disableFastForward.value && videoRef.value) {
    videoRef.value.playbackRate = 1
  }
}

const onVideoError = () => {
  console.warn('视频加载失败:', videoUrl.value)
}

const onToggleChange = (val) => {
  if (val && videoRef.value) {
    videoRef.value.playbackRate = 1
  }
}

// Keyboard shortcuts to prevent speed changes
const handleKeyDown = (e) => {
  if (!disableFastForward.value) return
  // ArrowUp/ArrowDown for volume is fine, but prevent speed changes
  // '>' and '.' keys for speed increase, '<' and ',' for speed decrease
  if (e.key === '>' || e.key === '.' || e.key === '<' || e.key === ',') {
    e.preventDefault()
  }
}

onMounted(() => {
  fetchData()
  window.addEventListener('keydown', handleKeyDown)
})

onBeforeUnmount(() => {
  window.removeEventListener('keydown', handleKeyDown)
})
</script>

<style scoped>
.lesson-player {
  max-width: 1200px;
  margin: 0 auto;
  padding: 16px 24px;
}

.player-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
  padding-bottom: 12px;
  border-bottom: 1px solid #e2e8f0;
}

.course-title {
  font-size: 16px;
  font-weight: 600;
  color: #1a1a2e;
}

.player-body {
  display: flex;
  gap: 24px;
}

.content-area {
  flex: 1;
  min-width: 0;
}

.lesson-title-bar {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
}

.lesson-title-bar h2 {
  font-size: 22px;
  font-weight: 700;
  color: #1a1a2e;
  margin: 0;
  letter-spacing: -0.3px;
}

/* Video section */
.video-section {
  margin-bottom: 20px;
}

.video-container {
  position: relative;
  width: 100%;
  background: #0f0f1a;
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid #e2e8f0;
}

.video-player {
  width: 100%;
  display: block;
  max-height: 480px;
  background: #0f0f1a;
}

.video-placeholder,
.document-placeholder,
.unknown-type {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 360px;
  background: #f8f9ff;
  border-radius: 12px;
  color: #94a3b8;
  gap: 12px;
  margin-bottom: 20px;
  border: 1px solid #e2e8f0;
}

.document-section {
  margin-bottom: 20px;
}

.pdf-viewer,
.office-viewer {
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid #e2e8f0;
  margin-bottom: 12px;
}

.pdf-frame {
  width: 100%;
  height: 600px;
  display: block;
}

.office-frame {
  width: 100%;
  height: 500px;
  display: block;
}

.doc-info {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  background: #f8f9ff;
  border-radius: 10px;
  border: 1px solid #e2e8f0;
  font-size: 13px;
  color: #64748b;
}

.doc-name {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.doc-download-btn {
  margin-top: 4px;
}

.video-controls {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 12px;
  padding: 10px 16px;
  background: #f8f9ff;
  border-radius: 10px;
  border: 1px solid #e2e8f0;
}

.speed-toggle {
  display: flex;
  align-items: center;
  gap: 10px;
}

.speed-label {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  font-weight: 500;
  color: #64748b;
}

.speed-label.locked {
  color: #ef4444;
}

.video-info {
  font-size: 12px;
  color: #94a3b8;
  max-width: 50%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.video-hint {
  font-size: 13px;
  color: #94a3b8;
}

.text-content {
  background: #fff;
  border-radius: 12px;
  padding: 24px;
  border: 1px solid #e2e8f0;
  margin-bottom: 20px;
  min-height: 300px;
}

.text-body {
  line-height: 1.8;
  color: #1a1a2e;
}

/* Markdown 样式 */
.markdown-body h1 { font-size: 24px; font-weight: 700; margin: 24px 0 12px; color: #1a1a2e; border-bottom: 1px solid #e2e8f0; padding-bottom: 8px; }
.markdown-body h2 { font-size: 20px; font-weight: 700; margin: 20px 0 10px; color: #1a1a2e; }
.markdown-body h3 { font-size: 17px; font-weight: 600; margin: 16px 0 8px; color: #334155; }
.markdown-body h4 { font-size: 15px; font-weight: 600; margin: 12px 0 6px; color: #475569; }
.markdown-body p { margin: 8px 0; line-height: 1.8; }
.markdown-body ul, .markdown-body ol { margin: 8px 0; padding-left: 24px; }
.markdown-body li { margin: 4px 0; line-height: 1.7; }
.markdown-body code {
  background: #f1f5f9;
  color: #6C5CE7;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 0.9em;
  font-family: 'JetBrains Mono', 'SF Mono', monospace;
}
.markdown-body pre {
  background: #1a1a2e;
  color: #e2e8f0;
  padding: 16px;
  border-radius: 10px;
  overflow-x: auto;
  margin: 12px 0;
  font-size: 14px;
  line-height: 1.6;
}
.markdown-body pre code {
  background: transparent;
  color: inherit;
  padding: 0;
  font-size: inherit;
}
.markdown-body blockquote {
  border-left: 4px solid #6C5CE7;
  padding: 8px 16px;
  margin: 12px 0;
  background: #f8f9ff;
  border-radius: 0 8px 8px 0;
  color: #475569;
}
.markdown-body table {
  width: 100%;
  border-collapse: collapse;
  margin: 12px 0;
}
.markdown-body th, .markdown-body td {
  padding: 8px 12px;
  border: 1px solid #e2e8f0;
  text-align: left;
}
.markdown-body th {
  background: #f8fafc;
  font-weight: 600;
  color: #334155;
}
.markdown-body img {
  max-width: 100%;
  border-radius: 8px;
  margin: 12px 0;
}
.markdown-body a {
  color: #6C5CE7;
  text-decoration: none;
}
.markdown-body a:hover {
  text-decoration: underline;
}
.markdown-body hr {
  border: none;
  border-top: 1px solid #e2e8f0;
  margin: 24px 0;
}

.action-bar {
  display: flex;
  justify-content: center;
  padding: 20px 0;
}

.lesson-nav {
  width: 280px;
  flex-shrink: 0;
  background: #fff;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  padding: 16px;
  max-height: calc(100vh - 120px);
  overflow-y: auto;
}

.lesson-nav h3 {
  font-size: 15px;
  font-weight: 600;
  color: #1a1a2e;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid #e2e8f0;
}

.nav-chapter {
  margin-bottom: 12px;
}

.nav-chapter-title {
  font-size: 13px;
  font-weight: 600;
  color: #475569;
  margin-bottom: 6px;
  padding-left: 4px;
}

.nav-lesson {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 8px;
  cursor: pointer;
  border-radius: 6px;
  font-size: 13px;
  color: #64748b;
  transition: background 0.2s;
}

.nav-lesson:hover {
  background: #f8f9ff;
}

.nav-lesson.active {
  background: #eef0ff;
  color: #6C5CE7;
  font-weight: 500;
}

.nav-lesson.completed {
  color: #10b981;
}

/* Mobile responsive */
@media (max-width: 768px) {
  .player-body {
    flex-direction: column;
  }
  .lesson-nav {
    width: 100%;
    max-height: none;
  }
  .video-controls {
    flex-direction: column;
    gap: 8px;
  }
  .video-info {
    max-width: 100%;
  }
}
</style>
