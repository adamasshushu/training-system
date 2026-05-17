<template>
  <div class="tasks-page">
    <div class="page-header">
      <h2 class="page-title">培训任务</h2>
      <el-button type="primary" @click="handleAdd"><el-icon><Plus /></el-icon>新建任务</el-button>
    </div>

    <el-card shadow="never">
      <el-table :data="taskList" border stripe v-loading="loading">
        <el-table-column type="index" label="#" width="55" />
        <el-table-column prop="标题" label="任务名称" min-width="200" />
        <el-table-column label="模式" width="80" align="center">
          <template #default="{ row }">
            <el-tag :type="row.模式 === 'level' ? 'warning' : 'info'" size="small">
              {{ row.模式 === 'level' ? '闯关' : '自由' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="内容" width="140" align="center">
          <template #default="{ row }">{{ row.课程数量 }}课 {{ row.考试数量 }}考</template>
        </el-table-column>
        <el-table-column label="状态" width="80" align="center">
          <template #default="{ row }">
            <el-tag :type="row.是否发布 ? 'success' : 'info'" size="small">
              {{ row.是否发布 ? '发布' : '草稿' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="创建人姓名" label="创建人" width="90" align="center" />
        <el-table-column label="操作" width="260" fixed="right">
          <template #default="{ row }">
            <el-button text size="small" type="primary" @click="handleEdit(row)">编辑</el-button>
            <el-button text size="small" type="success" @click="handleAssign(row)">指派</el-button>
            <el-button text size="small" type="warning" @click="togglePublish(row)">
              {{ row.是否发布 ? '下架' : '发布' }}
            </el-button>
            <el-button text size="small" type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination v-model:current-page="page" :page-size="20" :total="total"
        layout="total, prev, pager, next" @current-change="loadData"
        style="margin-top:16px; justify-content:center" />
    </el-card>

    <!-- 新建/编辑任务 -->
    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑任务' : '新建任务'" width="750px" destroy-on-close>
      <el-form ref="formRef" :model="form" :rules="rules" label-width="90px">
        <el-form-item label="任务名称" prop="标题">
          <el-input v-model="form.标题" placeholder="请输入任务名称" />
        </el-form-item>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="模式" prop="模式">
              <el-radio-group v-model="form.模式">
                <el-radio value="free">自由模式（顺序不限）</el-radio>
                <el-radio value="level">闯关模式（按序完成）</el-radio>
              </el-radio-group>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="截止日期">
              <el-date-picker v-model="form.截止日期" type="date" placeholder="可选" value-format="YYYY-MM-DD" style="width:100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="描述">
          <el-input v-model="form.描述" type="textarea" :rows="2" placeholder="任务说明" />
        </el-form-item>
        <el-form-item label="发布">
          <el-switch v-model="form.是否发布" />
        </el-form-item>

        <el-divider content-position="left">关联课程 ({{ form.课程列表.length }} 门)</el-divider>
        <el-select v-model="form.课程列表" multiple filterable placeholder="选择课程" style="width:100%"
          value-key="课程ID">
          <el-option v-for="c in availableCourses" :key="c.ID" :label="c.标题" :value="{ 课程ID: c.ID, 排序: 0 }" />
        </el-select>

        <el-divider content-position="left">关联考试 ({{ form.考试列表.length }} 场)</el-divider>
        <el-select v-model="form.考试列表" multiple filterable placeholder="选择考试" style="width:100%"
          value-key="考试ID">
          <el-option v-for="e in availableExams" :key="e.ID" :label="e.标题" :value="{ 考试ID: e.ID, 排序: 0 }" />
        </el-select>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>

    <!-- 指派对话框 -->
    <el-dialog v-model="assignDialog" title="任务指派" width="550px" destroy-on-close>
      <div v-loading="assignLoading">
        <h4 style="margin-bottom:12px">当前指派</h4>
        <el-tag v-for="a in currentAssignments" :key="a.ID" closable
          :type="a.指派类型 === '部门' ? 'warning' : 'primary'"
          style="margin:4px" @close="handleRemoveAssign(a)">
          {{ a.指派类型 === '部门' ? '🏢' : '👤' }} {{ a.指派对象名称 }}
        </el-tag>
        <el-empty v-if="currentAssignments.length===0" description="暂无指派" :image-size="60" />

        <el-divider />
        <h4 style="margin-bottom:12px">新增指派</h4>
        <el-radio-group v-model="assignType" style="margin-bottom:12px">
          <el-radio value="department">指派部门</el-radio>
          <el-radio value="user">指派个人</el-radio>
        </el-radio-group>
        <el-select v-model="assignTarget" filterable :placeholder="assignType==='department'?'选择部门':'选择员工'" style="width:100%">
          <el-option v-for="item in assignOptions" :key="item.id" :label="item.name" :value="item.id" />
        </el-select>
        <el-button type="primary" style="margin-top:12px" @click="confirmAssign" :loading="assigning" :disabled="!assignTarget">
          确认指派
        </el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { Plus } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getTasks, getTaskDetail, createTask, updateTask, deleteTask, assignTask, removeAssignment } from '@/api/tasks'
import { getCourses } from '@/api/courses'
import { getExams } from '@/api/exams'
import request from '@/api/index'

const loading = ref(false)
const taskList = ref([]); const total = ref(0); const page = ref(1)
const dialogVisible = ref(false); const isEdit = ref(false)
const submitting = ref(false); const formRef = ref(null); const editId = ref(null)
const availableCourses = ref([]); const availableExams = ref([])

const form = reactive({ 标题:'', 描述:'', 模式:'free', 截止日期:null, 是否发布:false, 课程列表:[], 考试列表:[] })
const rules = { 标题: [{ required: true, message:'请输入任务名称', trigger:'blur' }] }

// Assign dialog
const assignDialog = ref(false); const assignTaskId = ref(null)
const assignType = ref('department'); const assignTarget = ref(null)
const assignOptions = ref([]); const assigning = ref(false); const assignLoading = ref(false)
const currentAssignments = ref([])

const loadData = async () => {
  loading.value = true
  try {
    const res = await getTasks({ page: page.value })
    taskList.value = res.数据 || []; total.value = res.共计 || 0
  } catch {} finally { loading.value = false }
}

const handleAdd = async () => {
  isEdit.value = false; editId.value = null
  form.标题 = ''; form.描述 = ''; form.模式 = 'free'; form.截止日期 = null
  form.是否发布 = false; form.课程列表 = []; form.考试列表 = []
  try {
    const [cr, er] = await Promise.all([getCourses({page_size:100}), getExams({page_size:100})])
    availableCourses.value = cr.数据 || []; availableExams.value = er.数据 || []
  } catch {}
  dialogVisible.value = true
}

const handleEdit = async (row) => {
  isEdit.value = true; editId.value = row.ID
  try {
    const [detail, cr, er] = await Promise.all([
      getTaskDetail(row.ID), getCourses({page_size:100}), getExams({page_size:100})
    ])
    availableCourses.value = cr.数据 || []
    availableExams.value = er.数据 || []
    const d = detail.数据
    form.标题 = d.标题; form.描述 = d.描述 || ''; form.模式 = d.模式
    form.截止日期 = d.截止日期; form.是否发布 = d.是否发布
    form.课程列表 = (d.关联课程 || []).map(c => ({ 课程ID: c.课程ID, 排序: 0 }))
    form.考试列表 = (d.关联考试 || []).map(e => ({ 考试ID: e.考试ID, 排序: 0 }))
    dialogVisible.value = true
  } catch { ElMessage.error('加载失败') }
}

const handleSubmit = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  submitting.value = true
  try {
    const data = {
      标题: form.标题, 描述: form.描述, 模式: form.模式,
      截止日期: form.截止日期, 是否发布: form.是否发布,
      课程列表: form.课程列表, 考试列表: form.考试列表
    }
    if (isEdit.value) {
      await updateTask(editId.value, data); ElMessage.success('更新成功')
    } else {
      await createTask(data); ElMessage.success('创建成功')
    }
    dialogVisible.value = false; loadData()
  } catch { ElMessage.error('操作失败') } finally { submitting.value = false }
}

const togglePublish = async (row) => {
  await updateTask(row.ID, { 是否发布: !row.是否发布 })
  ElMessage.success(row.是否发布 ? '已下架' : '已发布'); loadData()
}

const handleDelete = (row) => {
  ElMessageBox.confirm(`确定删除「${row.标题}」？`, '警告', { type: 'warning' })
    .then(async () => { await deleteTask(row.ID); ElMessage.success('已删除'); loadData() }).catch(() => {})
}

// Assign
const handleAssign = async (row) => {
  assignTaskId.value = row.ID; assignDialog.value = true; assignTarget.value = null
  assignLoading.value = true
  try {
    const detail = await getTaskDetail(row.ID)
    currentAssignments.value = detail.数据.指派记录 || []
    // Load options
    if (assignType.value === 'department') {
      const r = await request.get('/departments'); assignOptions.value = (r.数据||[]).map(d=>({id:d.ID,name:d.名称}))
    } else {
      const r = await request.get('/users?page_size=100'); assignOptions.value = (r.数据||[]).map(u=>({id:u.ID,name:u.真实姓名}))
    }
  } catch {} finally { assignLoading.value = false }
}

const confirmAssign = async () => {
  assigning.value = true
  try {
    await assignTask(assignTaskId.value, { 指派类型: assignType.value, 指派对象ID: assignTarget.value })
    ElMessage.success('指派成功')
    // Reload
    const detail = await getTaskDetail(assignTaskId.value)
    currentAssignments.value = detail.数据.指派记录 || []
    assignTarget.value = null
  } catch { ElMessage.error('指派失败') } finally { assigning.value = false }
}

const handleRemoveAssign = async (row) => {
  try {
    await removeAssignment(assignTaskId.value, row.ID)
    ElMessage.success('已取消'); currentAssignments.value = currentAssignments.value.filter(a => a.ID !== row.ID)
  } catch { ElMessage.error('取消失败') }
}

onMounted(() => loadData())
</script>

<style scoped>
.tasks-page { max-width: 1200px; }
.page-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px; }
.page-title { font-size: 22px; font-weight: 600; color: #303133; }
</style>
