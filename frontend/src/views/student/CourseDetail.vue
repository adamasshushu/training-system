<template>
  <div class="course-detail">
    <div class="detail-header">
      <div class="header-content">
        <h1>{{ course['标题'] || '课程加载中...' }}</h1>
        <div class="course-meta">
          <span><el-icon><User /></el-icon>讲师：{{ course['讲师名称'] || '未知' }}</span>
          <span><el-icon><Collection /></el-icon>{{ chapterCount }} 章节</span>
        </div>
        <p class="course-brief">{{ course['简介'] || '暂无简介' }}</p>
        <div class="progress-section">
          <span class="progress-label">学习进度</span>
          <el-progress :percentage="progressPercent" :stroke-width="10" />
        </div>
      </div>
    </div>

    <!-- 章节列表 -->
    <el-card shadow="never" class="chapter-card">
      <template #header>
        <span class="section-title">课程目录</span>
      </template>
      <el-collapse v-model="activeChapters" accordion>
        <el-collapse-item
          v-for="(chapter, idx) in chapters"
          :key="chapter['ID']"
          :title="`第${idx + 1}章 ${chapter['标题']}`"
          :name="chapter['ID']"
        >
          <div
            v-for="lesson in chapter['课时列表']"
            :key="lesson['ID']"
            class="lesson-item"
            :class="{ completed: lesson['是否完成'], active: currentLesson === lesson['ID'] }"
            @click="playLesson(lesson)"
          >
            <div class="lesson-left">
              <el-icon v-if="lesson['是否完成']" color="#67C23A"><SuccessFilled /></el-icon>
              <el-icon v-else>
                <VideoPlay v-if="lesson['课时类型'] === 'video'" />
                <Document v-else-if="lesson['课时类型'] === 'document'" />
                <Reading v-else />
              </el-icon>
              <span>{{ lesson['标题'] }}</span>
            </div>
            <el-tag size="small" :type="lessonTypeTag(lesson['课时类型'])" effect="plain">
              {{ lesson['课时类型'] }}
            </el-tag>
          </div>
        </el-collapse-item>
      </el-collapse>
      <div v-if="chapters.length === 0" class="empty-chapters">
        <p>暂无章节内容</p>
      </div>
    </el-card>

    <!-- 课程简介 -->
    <el-card shadow="never" class="desc-card">
      <template #header>
        <span class="section-title">课程简介</span>
      </template>
      <p>{{ course['简介'] || '暂无详细介绍' }}</p>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { User, Collection, SuccessFilled, VideoPlay, Document, Reading } from '@element-plus/icons-vue'
import { getCourseDetail } from '@/api/courses'

const route = useRoute()
const router = useRouter()
const courseId = route.params.id

const course = ref({})
const chapters = ref([])
const activeChapters = ref(null)
const currentLesson = ref(null)

const chapterCount = computed(() => chapters.value.length || 0)
const progressPercent = computed(() => {
  let total = 0
  let completed = 0
  chapters.value.forEach(ch => {
    if (ch['课时列表']) {
      ch['课时列表'].forEach(les => {
        total++
        if (les['是否完成']) completed++
      })
    }
  })
  return total > 0 ? Math.round((completed / total) * 100) : 0
})

const lessonTypeTag = (type) => {
  const map = { video: 'primary', document: 'success', text: 'warning' }
  return map[type] || 'info'
}

const playLesson = (lesson) => {
  currentLesson.value = lesson['ID']
  router.push(`/student/courses/${courseId}/lessons/${lesson['ID']}`)
}

const fetchDetail = async () => {
  try {
    const res = await getCourseDetail(courseId)
    course.value = res['数据']
    chapters.value = res['数据']['章节列表'] || []
    if (chapters.value.length > 0) {
      activeChapters.value = chapters.value[0]['ID']
    }
  } catch {
    course.value = { '标题': '课程加载失败' }
  }
}

onMounted(() => {
  fetchDetail()
})
</script>

<style scoped>
.course-detail {
  max-width: 1000px;
  margin: 0 auto;
  padding: 24px;
}

.detail-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 16px;
  padding: 32px 40px;
  color: #fff;
  margin-bottom: 24px;
}

.header-content h1 {
  font-size: 28px;
  font-weight: 700;
  margin-bottom: 16px;
}

.course-meta {
  display: flex;
  gap: 24px;
  margin-bottom: 16px;
  font-size: 14px;
  opacity: 0.9;
}

.course-meta span {
  display: flex;
  align-items: center;
  gap: 6px;
}

.course-brief {
  font-size: 15px;
  opacity: 0.85;
  margin-bottom: 20px;
  line-height: 1.6;
}

.progress-section {
  margin-top: 16px;
}

.progress-label {
  font-size: 14px;
  margin-bottom: 8px;
  display: block;
  opacity: 0.9;
}

.chapter-card, .desc-card {
  margin-bottom: 24px;
  border-radius: 12px;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.lesson-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 16px;
  cursor: pointer;
  border-radius: 8px;
  transition: background 0.2s;
}

.lesson-item:hover {
  background: #f0f5ff;
}

.lesson-item.active {
  background: #ecf5ff;
  color: #409EFF;
}

.lesson-item.completed {
  opacity: 0.85;
}

.lesson-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.empty-chapters {
  text-align: center;
  padding: 40px;
  color: #909399;
}
</style>
