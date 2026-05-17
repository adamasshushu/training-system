<template>
  <div class="courses">
    <div class="page-header">
      <h2 class="page-title">课程管理</h2>
      <div class="header-actions">
        <el-select v-model="categoryFilter" placeholder="分类筛选" clearable style="width: 140px">
          <el-option
            v-for="cat in categories"
            :key="cat['ID']"
            :label="cat['名称']"
            :value="cat['ID']"
          />
        </el-select>
        <el-input
          v-model="searchQuery"
          placeholder="搜索课程名称"
          clearable
          style="width: 200px"
          :prefix-icon="Search"
        />
        <el-button type="primary" @click="handleAdd">
          <el-icon><Plus /></el-icon>新建课程
        </el-button>
      </div>
    </div>

    <el-card shadow="never">
      <el-table :data="courseList" border stripe v-loading="loading" style="width: 100%">
        <el-table-column type="index" label="#" width="60" />
        <el-table-column label="课程名称" min-width="200">
          <template #default="{ row }">{{ row['标题'] }}</template>
        </el-table-column>
        <el-table-column label="分类" width="120">
          <template #default="{ row }">{{ row['分类名称'] }}</template>
        </el-table-column>
        <el-table-column label="讲师" width="120">
          <template #default="{ row }">{{ row['讲师名称'] }}</template>
        </el-table-column>
        <el-table-column label="章节数" width="80" align="center">
          <template #default="{ row }">{{ row['章节数'] || 0 }}</template>
        </el-table-column>
        <el-table-column label="创建时间" width="170">
          <template #default="{ row }">{{ row['创建时间'] }}</template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row['是否发布'] ? 'success' : 'info'" size="small">
              {{ row['是否发布'] ? '已发布' : '草稿' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="260" fixed="right">
          <template #default="{ row }">
            <el-button text size="small" type="primary" @click="handleEdit(row)">编辑</el-button>
            <el-button text size="small" type="success" @click="handleChapter(row)">章节</el-button>
            <el-button
              text
              size="small"
              :type="row['是否发布'] ? 'warning' : 'success'"
              @click="toggleStatus(row)"
            >
              {{ row['是否发布'] ? '下架' : '发布' }}
            </el-button>
            <el-button text size="small" type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="page"
          v-model:page-size="pageSize"
          :total="total"
          layout="total, sizes, prev, pager, next"
          @size-change="fetchCourses"
          @current-change="fetchCourses"
        />
      </div>
    </el-card>

    <!-- 新建/编辑弹窗 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑课程' : '新建课程'"
      width="650px"
    >
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="课程名称" prop="标题">
          <el-input v-model="form['标题']" placeholder="请输入课程名称" />
        </el-form-item>
        <el-form-item label="课程分类" prop="分类ID">
          <el-select v-model="form['分类ID']" placeholder="选择分类" style="width: 100%">
            <el-option
              v-for="cat in categories"
              :key="cat['ID']"
              :label="cat['名称']"
              :value="cat['ID']"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="课程简介" prop="简介">
          <el-input v-model="form['简介']" type="textarea" :rows="3" placeholder="请输入课程简介" />
        </el-form-item>
        <el-form-item label="封面图片" prop="封面">
          <el-input v-model="form['封面']" placeholder="封面图片URL" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">
          {{ isEdit ? '保存' : '创建' }}
        </el-button>
      </template>
    </el-dialog>

    <!-- 管理章节弹窗 -->
    <el-dialog
      v-model="chapterDialogVisible"
      title="管理章节"
      width="600px"
    >
      <div v-if="chapters.length === 0" class="empty-chapters">
        <p>暂无章节，请添加第一章</p>
      </div>
      <div v-for="(ch, cIdx) in chapters" :key="ch['ID'] || cIdx" class="chapter-block">
        <div class="chapter-title-row">
          <el-input v-model="ch['标题']" placeholder="章节标题" style="flex:1" />
        </div>
        <div v-for="(les, lIdx) in ch['课时列表']" :key="les['ID'] || lIdx" class="lesson-row">
          <el-tag size="small" :type="lessonTypeTag(les['课时类型'])">{{ les['课时类型'] }}</el-tag>
          <span class="lesson-title-text">{{ les['标题'] }}</span>
        </div>
      </div>
      <template #footer>
        <el-button type="primary" @click="chapterDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { Search } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  getCategories,
  getCourses,
  createCourse,
  updateCourse,
  deleteCourse,
  getCourseDetail
} from '@/api/courses'

const courseList = ref([])
const categories = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(10)
const loading = ref(false)
const searchQuery = ref('')
const categoryFilter = ref('')
const dialogVisible = ref(false)
const isEdit = ref(false)
const submitting = ref(false)
const formRef = ref(null)
const editId = ref(null)

// 章节弹窗
const chapterDialogVisible = ref(false)
const chapters = ref([])
const currentCourseId = ref(null)

const form = reactive({
  '标题': '',
  '分类ID': '',
  '简介': '',
  '封面': ''
})

const rules = {
  '标题': [{ required: true, message: '请输入课程名称', trigger: 'blur' }],
  '分类ID': [{ required: true, message: '请选择课程分类', trigger: 'change' }]
}

const lessonTypeTag = (type) => {
  const map = { video: 'primary', document: 'success', text: 'warning' }
  return map[type] || 'info'
}

const fetchCategories = async () => {
  try {
    const res = await getCategories()
    categories.value = res['数据'] || []
  } catch {
    // ignore
  }
}

const fetchCourses = async () => {
  loading.value = true
  try {
    const params = { 页码: page.value, 每页数量: pageSize.value }
    if (searchQuery.value) params.keyword = searchQuery.value
    if (categoryFilter.value) params.分类ID = categoryFilter.value
    const res = await getCourses(params)
    courseList.value = res['数据'] || []
    total.value = res['共计'] || 0
  } catch {
    ElMessage.error('获取课程列表失败')
  } finally {
    loading.value = false
  }
}

const handleAdd = () => {
  isEdit.value = false
  editId.value = null
  form['标题'] = ''
  form['分类ID'] = ''
  form['简介'] = ''
  form['封面'] = ''
  dialogVisible.value = true
}

const handleEdit = (row) => {
  isEdit.value = true
  editId.value = row['ID']
  form['标题'] = row['标题']
  form['分类ID'] = ''
  form['简介'] = row['简介'] || ''
  form['封面'] = row['封面'] || ''
  dialogVisible.value = true
}

const handleChapter = async (row) => {
  currentCourseId.value = row['ID']
  try {
    const res = await getCourseDetail(row['ID'])
    chapters.value = res['数据']['章节列表'] || []
  } catch {
    chapters.value = []
  }
  chapterDialogVisible.value = true
}

const toggleStatus = async (row) => {
  const action = row['是否发布'] ? '下架' : '发布'
  try {
    await ElMessageBox.confirm(`确定要${action}该课程吗？`, '提示', { type: 'warning' })
    await updateCourse(row['ID'], { '是否发布': !row['是否发布'] })
    ElMessage.success(`${action}成功`)
    await fetchCourses()
  } catch (e) {
    if (e !== 'cancel') ElMessage.error(`${action}失败`)
  }
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(`确定要删除课程"${row['标题']}"吗？`, '提示', { type: 'warning' })
    await deleteCourse(row['ID'])
    ElMessage.success('删除成功')
    await fetchCourses()
  } catch (e) {
    if (e !== 'cancel') ElMessage.error('删除失败')
  }
}

const handleSubmit = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  submitting.value = true
  try {
    const payload = {
      '标题': form['标题'],
      '分类ID': form['分类ID'],
      '简介': form['简介'] || '',
      '封面': form['封面'] || ''
    }
    if (isEdit.value && editId.value) {
      await updateCourse(editId.value, payload)
    } else {
      await createCourse(payload)
    }
    ElMessage.success(isEdit.value ? '编辑成功' : '创建成功')
    dialogVisible.value = false
    await fetchCourses()
  } catch {
    ElMessage.error('操作失败')
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  fetchCategories()
  fetchCourses()
})
</script>

<style scoped>
.courses {
  max-width: 1200px;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 12px;
}

.page-title {
  font-size: 22px;
  font-weight: 600;
  color: #303133;
}

.header-actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

.pagination-wrapper {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.empty-chapters {
  text-align: center;
  padding: 40px;
  color: #909399;
}

.chapter-block {
  margin-bottom: 16px;
  padding: 12px;
  background: #f5f7fa;
  border-radius: 8px;
}

.chapter-title-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.lesson-row {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 12px;
}

.lesson-title-text {
  font-size: 14px;
  color: #606266;
}
</style>
