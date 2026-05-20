<template>
  <div class="course-detail">
    <!-- Hero Header -->
    <div class="detail-hero">
      <div class="hero-backdrop" :style="{ background: heroGradient }"></div>
      <div class="hero-content">
        <div class="hero-breadcrumb">
          <router-link to="/student/courses">课程中心</router-link>
          <el-icon><ArrowRight /></el-icon>
          <span>{{ course['标题'] || '加载中...' }}</span>
        </div>
        <h1 class="hero-title">{{ course['标题'] || '加载中...' }}</h1>
        <div class="hero-meta">
          <span><el-icon><User /></el-icon>{{ course['讲师名称'] || '未知讲师' }}</span>
          <span><el-icon><Collection /></el-icon>{{ chapterCount }} 章节</span>
          <span v-if="course['学习人数']"><el-icon><UserFilled /></el-icon>{{ course['学习人数'] }} 人学习</span>
        </div>
        <p class="hero-brief">{{ course['简介'] || course['描述'] || '暂无简介' }}</p>
        <div class="hero-progress">
          <span class="hero-progress-label">学习进度</span>
          <el-progress :percentage="progressPercent" :stroke-width="8" :color="progressColor" />
        </div>
      </div>
    </div>

    <!-- Content Grid -->
    <div class="detail-content">
      <!-- Main: Chapter List -->
      <SectionCard title="📖 课程目录" :tag="`${chapterCount} 章`" tag-type="primary">
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
                <el-icon v-if="lesson['是否完成']" color="var(--success)" class="lesson-icon"><SuccessFilled /></el-icon>
                <el-icon v-else class="lesson-icon">
                  <VideoPlay v-if="lesson['课时类型'] === 'video'" />
                  <Document v-else-if="lesson['课时类型'] === 'document'" />
                  <Reading v-else />
                </el-icon>
                <span>{{ lesson['标题'] }}</span>
              </div>
              <el-tag size="small" :type="lessonTypeTag(lesson['课时类型'])" effect="plain" round>
                <el-icon :size="12" style="margin-right:2px;vertical-align:-2px">
                  <VideoPlay v-if="lesson['课时类型'] === 'video'" />
                  <Document v-else-if="lesson['课时类型'] === 'document'" />
                  <Reading v-else />
                </el-icon>
                {{ lesson['课时类型'] === 'video' ? '视频' : lesson['课时类型'] === 'document' ? '文档' : '图文' }}
              </el-tag>
            </div>
          </el-collapse-item>
        </el-collapse>
        <EmptyState v-if="chapters.length === 0" description="暂无章节内容" />
      </SectionCard>

      <!-- Sidebar: Course Info -->
      <div class="detail-sidebar">
        <SectionCard title="📋 课程信息">
          <div class="info-grid">
            <div class="info-item">
              <span class="info-label">分类</span>
              <span class="info-value">{{ course['分类名称'] || '未分类' }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">章节</span>
              <span class="info-value">{{ chapterCount }} 章</span>
            </div>
            <div class="info-item">
              <span class="info-label">讲师</span>
              <span class="info-value">{{ course['讲师名称'] || '未知' }}</span>
            </div>
            <div class="info-item" v-if="course['创建时间']">
              <span class="info-label">更新</span>
              <span class="info-value">{{ course['创建时间'] }}</span>
            </div>
          </div>
        </SectionCard>

        <SectionCard title="ℹ️ 课程简介">
          <p class="desc-text">{{ course['简介'] || course['描述'] || '暂无详细介绍' }}</p>
        </SectionCard>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  User, Collection, UserFilled, SuccessFilled, VideoPlay,
  Document, Reading, ArrowRight
} from '@element-plus/icons-vue'
import { getCourseDetail } from '@/api/courses'
import SectionCard from '@/components/SectionCard.vue'
import EmptyState from '@/components/EmptyState.vue'

const route = useRoute()
const router = useRouter()
const courseId = route.params.id

const course = ref({})
const chapters = ref([])
const activeChapters = ref(null)
const currentLesson = ref(null)

const chapterCount = computed(() => chapters.value.length || 0)
const progressPercent = computed(() => {
  let total = 0, completed = 0
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
const progressColor = computed(() => progressPercent.value >= 100 ? '#10b981' : '#6C5CE7')

const heroGradient = computed(() =>
  'linear-gradient(135deg, #1a1a2e 0%, #2a2166 40%, #6C5CE7 100%)'
)

const lessonTypeTag = (type) => {
  const map = { video: 'primary', document: 'success', text: 'warning' }
  return map[type] || 'info'
}

const playLesson = (lesson) => {
  if (lesson['课时类型'] === 'video') {
    router.push(`/student/lesson/${lesson['ID']}?course=${courseId}`)
  }
}

const loadData = async () => {
  try {
    const res = await getCourseDetail(courseId)
    const data = res['数据'] || {}
    course.value = data
    chapters.value = data['章节列表'] || []
    if (chapters.value.length > 0) {
      activeChapters.value = chapters.value[0]['ID']
    }
  } catch { /* silent */ }
}

onMounted(loadData)
</script>

<style scoped>
.course-detail {
  max-width: 1200px;
  margin: 0 auto;
  animation: fadeIn 0.3s ease-out;
}

/* ===== Hero ===== */
.detail-hero {
  position: relative;
  border-radius: var(--radius-xl);
  overflow: hidden;
  margin-bottom: var(--space-6);
}
.hero-backdrop {
  position: absolute;
  inset: 0;
  z-index: 0;
}
.hero-content {
  position: relative;
  z-index: 1;
  padding: var(--space-8) var(--space-6);
  color: #fff;
}
.hero-breadcrumb {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: rgba(255,255,255,0.5);
  margin-bottom: var(--space-4);
}
.hero-breadcrumb a {
  color: rgba(255,255,255,0.7);
  text-decoration: none;
  transition: color 0.2s;
}
.hero-breadcrumb a:hover {
  color: #fff;
}
.hero-title {
  font-size: 28px;
  font-weight: 700;
  margin: 0 0 var(--space-3);
  letter-spacing: -0.5px;
}
.hero-meta {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-4);
  font-size: 14px;
  color: rgba(255,255,255,0.7);
  margin-bottom: var(--space-3);
}
.hero-meta span {
  display: flex;
  align-items: center;
  gap: 4px;
}
.hero-brief {
  font-size: 14px;
  color: rgba(255,255,255,0.55);
  line-height: 1.6;
  margin: 0 0 var(--space-4);
  max-width: 600px;
}
.hero-progress-label {
  font-size: 13px;
  color: rgba(255,255,255,0.5);
  display: block;
  margin-bottom: 4px;
}

/* ===== Content Grid ===== */
.detail-content {
  display: grid;
  grid-template-columns: 1fr 320px;
  gap: var(--space-6);
  align-items: start;
}

/* ===== Lessons ===== */
.lesson-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-3) var(--space-3);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all var(--transition-fast);
  margin-bottom: 2px;
}
.lesson-item:hover {
  background: var(--bg-hover);
}
.lesson-item.active {
  background: var(--bg-active);
  border-left: 3px solid var(--brand-500);
}
.lesson-item.completed .lesson-left span {
  color: var(--text-tertiary);
  text-decoration: line-through;
}
.lesson-left {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  font-size: 14px;
  color: var(--text-primary);
}
.lesson-icon {
  font-size: 16px;
  flex-shrink: 0;
  color: var(--text-tertiary);
}
.lesson-item.completed .lesson-icon {
  color: var(--success);
}

/* ===== Sidebar ===== */
.info-grid {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}
.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.info-label {
  font-size: 13px;
  color: var(--text-tertiary);
}
.info-value {
  font-size: 13px;
  font-weight: var(--weight-medium);
  color: var(--text-primary);
}
.desc-text {
  font-size: 14px;
  color: var(--text-secondary);
  line-height: 1.7;
  margin: 0;
}

/* ===== Empty ===== */
.empty-chapters {
  text-align: center;
  color: var(--text-tertiary);
  padding: var(--space-8) 0;
}

/* ===== Responsive ===== */
@media (max-width: 900px) {
  .detail-content {
    grid-template-columns: 1fr;
  }
  .hero-title {
    font-size: 22px;
  }
  .hero-content {
    padding: var(--space-5);
  }
}
</style>
