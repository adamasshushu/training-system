<template>
  <div class="student-courses">
    <div class="page-header">
      <h2>课程中心</h2>
      <el-input
        v-model="searchQuery"
        placeholder="搜索课程..."
        clearable
        :prefix-icon="Search"
        class="search-input"
      />
    </div>

    <!-- 分类筛选标签 -->
    <div class="category-tabs">
      <el-tag
        :type="activeCategory === '' ? 'primary' : 'plain'"
        class="category-tag"
        @click="activeCategory = ''"
      >全部</el-tag>
      <el-tag
        v-for="cat in categories"
        :key="cat['ID']"
        :type="activeCategory === cat['ID'] ? 'primary' : 'plain'"
        class="category-tag"
        @click="activeCategory = cat['ID']"
      >{{ cat['名称'] }}</el-tag>
    </div>

    <!-- 课程卡片网格 -->
    <el-row :gutter="20">
      <el-col
        v-for="course in filteredCourses"
        :key="course['ID']"
        :xs="24"
        :sm="12"
        :md="8"
        :lg="6"
        class="course-col"
      >
        <el-card shadow="hover" class="course-card" @click="goToDetail(course)">
          <div class="course-cover">
            <el-icon :size="48" color="#409EFF"><Reading /></el-icon>
            <span class="course-category">{{ course['分类名称'] }}</span>
          </div>
          <div class="course-body">
            <h3 class="course-title">{{ course['标题'] }}</h3>
            <p class="course-brief">{{ course['简介'] || '暂无简介' }}</p>
            <div class="course-meta">
              <span>{{ course['章节数量'] || 0 }} 章节</span>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <div v-if="loading" class="empty-state">
      <el-icon :size="64" color="#c0c4cc"><Loading /></el-icon>
      <p>加载中...</p>
    </div>
    <div v-else-if="filteredCourses.length === 0" class="empty-state">
      <el-icon :size="64" color="#c0c4cc"><FolderDelete /></el-icon>
      <p>暂无课程</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Search, FolderDelete, Loading } from '@element-plus/icons-vue'
import { getStudentCourses, getCategories } from '@/api/courses'

const router = useRouter()

const searchQuery = ref('')
const activeCategory = ref('')
const courseList = ref([])
const categories = ref([])
const loading = ref(true)

const filteredCourses = computed(() => {
  let list = courseList.value
  if (activeCategory.value) {
    list = list.filter(c => c['分类ID'] === activeCategory.value)
  }
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    list = list.filter(c => (c['课程名称'] || '').toLowerCase().includes(q))
  }
  return list
})

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

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.student-courses {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
  flex-wrap: wrap;
  gap: 12px;
}

.page-header h2 {
  font-size: 24px;
  font-weight: 700;
  color: #303133;
}

.search-input {
  width: 280px;
}

.category-tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 24px;
  flex-wrap: wrap;
}

.category-tag {
  cursor: pointer;
  padding: 4px 16px;
  font-size: 14px;
}

.course-col {
  margin-bottom: 20px;
}

.course-card {
  cursor: pointer;
  border-radius: 12px;
  overflow: hidden;
  transition: transform 0.2s;
}

.course-card:hover {
  transform: translateY(-4px);
}

.course-cover {
  height: 140px;
  background: linear-gradient(135deg, #667eea22 0%, #764ba222 100%);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  position: relative;
}

.course-category {
  position: absolute;
  top: 12px;
  right: 12px;
  background: rgba(64, 158, 255, 0.9);
  color: #fff;
  padding: 2px 10px;
  border-radius: 4px;
  font-size: 12px;
}

.course-body {
  padding: 16px;
}

.course-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 8px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.course-brief {
  font-size: 13px;
  color: #909399;
  margin-bottom: 12px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.course-meta {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #c0c4cc;
  margin-bottom: 12px;
}

.empty-state {
  text-align: center;
  padding: 80px 0;
  color: #909399;
}

.empty-state p {
  margin-top: 16px;
}
</style>
