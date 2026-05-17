<template>
  <div class="learning-paths">
    <el-card class="page-card">
      <div class="page-header">
        <h2>🗺️ 学习路径管理</h2>
        <el-button type="primary" :icon="Plus" @click="showDialog(null)">新建学习路径</el-button>
      </div>

      <el-table :data="paths" v-loading="loading" stripe>
        <el-table-column prop="ID" label="ID" width="60" />
        <el-table-column prop="名称" label="路径名称" min-width="200" />
        <el-table-column prop="描述" label="描述" min-width="250" show-overflow-tooltip />
        <el-table-column prop="课程数量" label="课程数" width="80" />
        <el-table-column label="发布" width="80">
          <template #default="{ row }">
            <el-tag :type="row.是否发布 ? 'success' : 'info'" size="small">
              {{ row.是否发布 ? '已发布' : '草稿' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="创建时间" label="创建时间" width="180" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="showDialog(row)">编辑</el-button>
            <el-button type="primary" link @click="manageCourses(row)">课程</el-button>
            <el-popconfirm title="确定删除？" @confirm="deletePath(row)">
              <template #reference>
                <el-button type="danger" link>删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-if="total > 0"
        v-model:current-page="page"
        :page-size="pageSize"
        :total="total"
        layout="prev, pager, next"
        class="pagination"
        @current-change="loadPaths"
      />
    </el-card>

    <!-- 编辑对话框 -->
    <el-dialog v-model="dialogVisible" :title="editingId ? '编辑学习路径' : '新建学习路径'" width="600px">
      <el-form :model="form" label-position="top">
        <el-form-item label="路径名称" required>
          <el-input v-model="form.名称" placeholder="例如：新员工入职培训" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.描述" type="textarea" :rows="3" placeholder="路径描述..." />
        </el-form-item>
        <el-form-item label="排序">
          <el-input-number v-model="form.排序" :min="0" />
        </el-form-item>
        <el-form-item label="发布状态">
          <el-switch v-model="form.是否发布" active-text="已发布" inactive-text="草稿" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="savePath" :loading="saving">保存</el-button>
      </template>
    </el-dialog>

    <!-- 管理课程对话框 -->
    <el-dialog v-model="courseDialogVisible" :title="`管理课程: ${currentPathName}`" width="700px">
      <div class="course-list">
        <div v-for="(c, idx) in courseList" :key="idx" class="course-item">
          <span class="course-sort">{{ idx + 1 }}</span>
          <span class="course-title">{{ c.标题 }}</span>
          <el-tag size="small" :type="c.必修 ? 'danger' : 'info'">{{ c.必修 ? '必修' : '选修' }}</el-tag>
          <el-button type="danger" link :icon="Delete" @click="courseList.splice(idx, 1)" />
        </div>
        <el-empty v-if="courseList.length === 0" description="暂未添加课程" />
      </div>

      <div class="add-course">
        <el-select v-model="selectedCourseId" placeholder="选择要添加的课程" filterable style="width: 300px">
          <el-option v-for="c in availableCourses" :key="c.ID" :label="c.标题" :value="c.ID" />
        </el-select>
        <el-checkbox v-model="newCourseRequired">必修</el-checkbox>
        <el-button type="primary" :icon="Plus" @click="addCourse">添加</el-button>
      </div>

      <template #footer>
        <el-button @click="courseDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveCourses" :loading="savingCourses">保存课程列表</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { Plus, Delete } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { getToken } from '@/utils/auth'
import axios from 'axios'

const API = axios.create({ baseURL: '' })
API.interceptors.request.use((c) => { c.headers.Authorization = `Bearer ${getToken()}`; return c })

const loading = ref(false)
const paths = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)

const dialogVisible = ref(false)
const editingId = ref(null)
const saving = ref(false)
const form = reactive({ 名称: '', 描述: '', 排序: 0, 是否发布: false })

const courseDialogVisible = ref(false)
const currentPathName = ref('')
const courseList = ref([])
const availableCourses = ref([])
const selectedCourseId = ref(null)
const newCourseRequired = ref(true)
const savingCourses = ref(false)
const currentPathId = ref(null)

const loadPaths = async () => {
  loading.value = true
  try {
    const res = await API.get('/api/learning-paths', { params: { page: page.value, page_size: pageSize.value } })
    paths.value = res.data.数据 || []
    total.value = res.data.共计 || 0
  } catch { ElMessage.error('加载失败') }
  finally { loading.value = false }
}

const showDialog = (row) => {
  if (row) {
    editingId.value = row.ID
    form.名称 = row.名称
    form.描述 = row.描述 || ''
    form.排序 = row.排序 || 0
    form.是否发布 = row.是否发布
  } else {
    editingId.value = null
    form.名称 = ''
    form.描述 = ''
    form.排序 = 0
    form.是否发布 = false
  }
  dialogVisible.value = true
}

const savePath = async () => {
  if (!form.名称.trim()) { ElMessage.warning('请输入路径名称'); return }
  saving.value = true
  try {
    if (editingId.value) {
      await API.put(`/api/learning-paths/${editingId.value}`, form)
      ElMessage.success('已更新')
    } else {
      await API.post('/api/learning-paths', form)
      ElMessage.success('已创建')
    }
    dialogVisible.value = false
    loadPaths()
  } catch { ElMessage.error('保存失败') }
  finally { saving.value = false }
}

const deletePath = async (row) => {
  try {
    await API.delete(`/api/learning-paths/${row.ID}`)
    ElMessage.success('已删除')
    loadPaths()
  } catch { ElMessage.error('删除失败') }
}

const manageCourses = async (row) => {
  currentPathId.value = row.ID
  currentPathName.value = row.名称
  selectedCourseId.value = null
  newCourseRequired.value = true

  // 获取路径详情
  try {
    const res = await API.get(`/api/learning-paths/${row.ID}`)
    courseList.value = res.data.数据?.课程列表 || []
  } catch { courseList.value = [] }

  // 获取可用课程
  try {
    const res = await API.get('/api/courses/student')
    availableCourses.value = (res.data.数据 || []).filter(
      c => !courseList.value.some(cl => cl.课程ID === c.ID)
    )
  } catch { availableCourses.value = [] }

  courseDialogVisible.value = true
}

const addCourse = () => {
  if (!selectedCourseId.value) { ElMessage.warning('请选择课程'); return }
  const course = availableCourses.value.find(c => c.ID === selectedCourseId.value)
  if (course) {
    courseList.value.push({ 课程ID: course.ID, 标题: course.标题, 排序: courseList.value.length, 必修: newCourseRequired.value })
    availableCourses.value = availableCourses.value.filter(c => c.ID !== selectedCourseId.value)
    selectedCourseId.value = null
  }
}

const saveCourses = async () => {
  savingCourses.value = true
  try {
    const payload = courseList.value.map((c, idx) => ({
      course_id: c.课程ID,
      sort: idx,
      required: c.必修 !== false,
      estimated_hours: 0
    }))
    await API.put(`/api/learning-paths/${currentPathId.value}/courses`, payload)
    ElMessage.success('课程列表已更新')
    courseDialogVisible.value = false
    loadPaths()
  } catch { ElMessage.error('保存失败') }
  finally { savingCourses.value = false }
}

onMounted(loadPaths)
</script>

<style scoped>
.learning-paths { max-width: 1200px; margin: 0 auto; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.page-header h2 { margin: 0; font-size: 18px; color: #303133; }
.pagination { margin-top: 16px; display: flex; justify-content: center; }
.course-list { margin-bottom: 16px; }
.course-item {
  display: flex; align-items: center; gap: 12px;
  padding: 10px 12px; border: 1px solid #ebeef5;
  border-radius: 6px; margin-bottom: 6px;
}
.course-sort {
  width: 24px; height: 24px; border-radius: 50%;
  background: #409EFF; color: #fff; display: flex;
  align-items: center; justify-content: center; font-size: 12px;
}
.course-title { flex: 1; font-size: 14px; }
.add-course { display: flex; align-items: center; gap: 12px; }
</style>
