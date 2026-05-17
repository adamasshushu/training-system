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

        <!-- 视频类型 -->
        <div v-if="lessonType === 'video'" class="video-placeholder">
          <el-icon :size="64" color="#409EFF"><VideoCameraFilled /></el-icon>
          <p>视频播放区域</p>
          <p class="video-hint" v-if="videoUrl">视频地址：{{ videoUrl }}</p>
          <p class="video-hint" v-else>暂无可播放视频</p>
        </div>

        <!-- 文档类型 -->
        <div v-else-if="lessonType === 'document'" class="document-placeholder">
          <el-icon :size="64" color="#67C23A"><Document /></el-icon>
          <p>文档预览区域</p>
          <p class="video-hint">文档类型课时暂不支持在线预览</p>
        </div>

        <!-- 图文类型 -->
        <div v-else-if="lessonType === 'text'" class="text-content">
          <div class="text-body" v-html="lessonContent || '暂无内容'"></div>
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
              <el-icon v-if="les['是否完成']" color="#67C23A" size="14"><SuccessFilled /></el-icon>
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
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  ArrowLeft,
  VideoCameraFilled,
  Document,
  Check,
  SuccessFilled,
  VideoPlay,
  Reading
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
const isCompleted = ref(false)
const submitting = ref(false)

const lessonTypeLabel = computed(() => {
  const map = { video: '视频', document: '文档', text: '图文' }
  return map[lessonType.value] || lessonType.value
})

const lessonTypeTag = (type) => {
  const map = { video: 'primary', document: 'success', text: 'warning' }
  return map[type] || 'info'
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

onMounted(() => {
  fetchData()
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
  border-bottom: 1px solid #ebeef5;
}

.course-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
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
  font-weight: 600;
  color: #303133;
  margin: 0;
}

.video-placeholder,
.document-placeholder,
.unknown-type {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 360px;
  background: #f5f7fa;
  border-radius: 12px;
  color: #909399;
  gap: 12px;
  margin-bottom: 20px;
}

.video-hint {
  font-size: 13px;
  color: #c0c4cc;
}

.text-content {
  background: #fff;
  border-radius: 12px;
  padding: 24px;
  border: 1px solid #ebeef5;
  margin-bottom: 20px;
  min-height: 300px;
}

.text-body {
  line-height: 1.8;
  color: #303133;
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
  border: 1px solid #ebeef5;
  padding: 16px;
  max-height: calc(100vh - 120px);
  overflow-y: auto;
}

.lesson-nav h3 {
  font-size: 15px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid #ebeef5;
}

.nav-chapter {
  margin-bottom: 12px;
}

.nav-chapter-title {
  font-size: 13px;
  font-weight: 600;
  color: #606266;
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
  color: #606266;
  transition: background 0.2s;
}

.nav-lesson:hover {
  background: #f0f5ff;
}

.nav-lesson.active {
  background: #ecf5ff;
  color: #409EFF;
  font-weight: 500;
}

.nav-lesson.completed {
  color: #67C23A;
}
</style>
