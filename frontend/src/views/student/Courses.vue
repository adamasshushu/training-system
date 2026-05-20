<template>
  <div class="student-courses">
    <PageHeader title="课程中心" subtitle="浏览所有培训课程，开始你的学习之旅">
      <template #actions>
        <el-input
          v-model="searchQuery"
          placeholder="搜索课程名称..."
          clearable
          :prefix-icon="Search"
          class="search-input"
          size="large"
        />
      </template>
    </PageHeader>

    <!-- 分类筛选 -->
    <CategoryTags
      :items="categoryItems"
      :active="activeCategory"
      @update:active="activeCategory = $event"
    />

    <!-- 加载态骨架屏 -->
    <div v-if="loading" class="courses-grid">
      <div v-for="i in 8" :key="i" class="course-card-skeleton">
        <div class="skeleton skeleton-cover"></div>
        <div class="skeleton-body">
          <div class="skeleton skeleton-title"></div>
          <div class="skeleton skeleton-text"></div>
          <div class="skeleton skeleton-meta"></div>
        </div>
      </div>
    </div>

    <!-- 课程网格 -->
    <div v-else-if="filteredCourses.length > 0" class="courses-grid">
      <div
        v-for="course in filteredCourses"
        :key="course['ID']"
        class="course-card"
        @click="goToDetail(course)"
      >
        <div class="course-cover">
          <div class="cover-gradient" :style="{ background: coverGradient(course) }">
            <el-icon :size="36" color="rgba(255,255,255,0.7)"><Reading /></el-icon>
          </div>
          <el-tag size="small" class="course-badge" effect="dark">
            {{ course['分类名称'] || '未分类' }}
          </el-tag>
          <div class="course-progress-ring" v-if="course['进度']">
            <el-progress type="circle" :percentage="course['进度']" :width="36" :stroke-width="3" color="#10b981" />
          </div>
        </div>
        <div class="course-body">
          <h3 class="course-title">{{ course['标题'] || course['课程名称'] }}</h3>
          <p class="course-brief">{{ course['简介'] || course['描述'] || '暂无简介' }}</p>
          <div class="course-footer">
            <span class="course-chapters">
              <el-icon :size="12"><Document /></el-icon>
              {{ course['章节数量'] || course['课时数'] || 0 }} 章节
            </span>
            <span class="course-learners" v-if="course['学习人数']">
              <el-icon :size="12"><User /></el-icon>
              {{ course['学习人数'] }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- 空状态 -->
    <EmptyState
      v-else
      :description="searchQuery ? '没有找到匹配的课程' : '暂无可用课程'"
      :action-text="searchQuery ? '' : ''"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Search, Document, User, Reading } from '@element-plus/icons-vue'
import { getStudentCourses, getCategories } from '@/api/courses'
import PageHeader from '@/components/PageHeader.vue'
import CategoryTags from '@/components/CategoryTags.vue'
import EmptyState from '@/components/EmptyState.vue'

const router = useRouter()

const searchQuery = ref('')
const activeCategory = ref('')
const courseList = ref([])
const categories = ref([])
const loading = ref(true)

const categoryItems = computed(() =>
  categories.value.map(c => ({ key: c['ID'], label: c['名称'] }))
)

const filteredCourses = computed(() => {
  let list = courseList.value
  if (activeCategory.value) {
    list = list.filter(c => c['分类ID'] === activeCategory.value)
  }
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    list = list.filter(c => (c['标题'] || c['课程名称'] || '').toLowerCase().includes(q))
  }
  return list
})

const coverGradient = (course) => {
  const colors = [
    'linear-gradient(135deg, #667eea, #764ba2)',
    'linear-gradient(135deg, #6C5CE7, #a29bfe)',
    'linear-gradient(135deg, #00b4d8, #0077b6)',
    'linear-gradient(135deg, #06d6a0, #118ab2)',
    'linear-gradient(135deg, #f093fb, #f5576c)',
    'linear-gradient(135deg, #4facfe, #00f2fe)',
    'linear-gradient(135deg, #43e97b, #38f9d7)',
    'linear-gradient(135deg, #fa709a, #fee140)'
  ]
  const idx = (course['ID'] || 0) % colors.length
  return colors[idx]
}

const goToDetail = (course) => {
  router.push(`/student/courses/${course['ID']}`)
}

const fetchData = async () => {
  loading.value = true
  try {
    const [coursesRes, catRes] = await Promise.all([
      getStudentCourses(),
      getCategories()
    ])
    courseList.value = coursesRes['数据'] || []
    categories.value = catRes['数据'] || []
  } catch {
    // silent
  } finally {
    loading.value = false
  }
}

onMounted(fetchData)
</script>

<style scoped>
.student-courses {
  max-width: 1200px;
  margin: 0 auto;
  animation: fadeIn 0.3s ease-out;
}

.search-input {
  width: 280px;
}

.search-input :deep(.el-input__wrapper) {
  border-radius: var(--radius-md) !important;
}

/* ===== Course Grid ===== */
.courses-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: var(--space-5);
}

/* ===== Course Card ===== */
.course-card {
  background: var(--bg-card);
  border: 1px solid var(--border-card);
  border-radius: var(--radius-xl);
  overflow: hidden;
  cursor: pointer;
  transition: all var(--transition-base);
  box-shadow: var(--shadow-sm);
  animation: fadeInUp 0.3s ease-out;
  animation-fill-mode: both;
}
.course-card:nth-child(1) { animation-delay: 0.02s; }
.course-card:nth-child(2) { animation-delay: 0.04s; }
.course-card:nth-child(3) { animation-delay: 0.06s; }
.course-card:nth-child(4) { animation-delay: 0.08s; }
.course-card:nth-child(5) { animation-delay: 0.10s; }
.course-card:nth-child(6) { animation-delay: 0.12s; }

.course-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-lg);
  border-color: var(--brand-200);
}

/* Cover */
.course-cover {
  position: relative;
  height: 120px;
  overflow: hidden;
}
.cover-gradient {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform var(--transition-slow);
}
.course-card:hover .cover-gradient {
  transform: scale(1.05);
}

.course-badge {
  position: absolute;
  top: var(--space-2);
  right: var(--space-2);
  border-radius: var(--radius-full) !important;
  font-size: 11px;
  background: rgba(0,0,0,0.5) !important;
  border: none !important;
  backdrop-filter: blur(4px);
}

.course-progress-ring {
  position: absolute;
  bottom: var(--space-2);
  right: var(--space-2);
}

/* Body */
.course-body {
  padding: var(--space-4);
}

.course-title {
  font-size: var(--text-md);
  font-weight: var(--weight-semibold);
  color: var(--text-primary);
  margin: 0 0 var(--space-1);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  line-height: var(--leading-tight);
}

.course-brief {
  font-size: var(--text-sm);
  color: var(--text-tertiary);
  margin: 0 0 var(--space-3);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  line-height: var(--leading-normal);
}

.course-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: var(--text-xs);
  color: var(--text-tertiary);
  gap: var(--space-2);
}
.course-footer span {
  display: flex;
  align-items: center;
  gap: 4px;
}

/* ===== Skeleton Loading ===== */
.course-card-skeleton {
  background: var(--bg-card);
  border: 1px solid var(--border-card);
  border-radius: var(--radius-xl);
  overflow: hidden;
  animation: fadeIn 0.3s ease-out;
}
.skeleton-cover {
  height: 120px;
  background: var(--border-default);
}
.skeleton-body {
  padding: var(--space-4);
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}
.skeleton-title {
  height: 18px;
  width: 70%;
}
.skeleton-text {
  height: 14px;
  width: 90%;
}
.skeleton-meta {
  height: 12px;
  width: 40%;
  margin-top: var(--space-1);
}

/* ===== Responsive ===== */
@media (max-width: 768px) {
  .courses-grid {
    grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
    gap: var(--space-3);
  }
  .course-cover {
    height: 100px;
  }
  .course-body {
    padding: var(--space-3);
  }
  .course-title {
    font-size: var(--text-sm);
  }
  .search-input {
    width: 100%;
  }
}

@media (max-width: 480px) {
  .courses-grid {
    grid-template-columns: 1fr 1fr;
  }
}
</style>
