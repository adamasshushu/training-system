<template>
  <div class="exams-page">
    <AdminTable
      :data="filteredExamList"
      :loading="loading"
      :total="total"
      v-model:model-value="page"
      :page-size="20"
      :columns="columns"
      :show-search="false"
      :actions-width="200"
      :page-sizes="[10, 20, 50]"
      @current-change="loadData"
      @size-change="loadData"
    >
      <template #page-header>
        <div class="page-header">
          <h2 class="page-title">考试管理</h2>
          <div class="header-right">
            <el-input
              v-model="searchQuery"
              placeholder="搜索考试名称..."
              clearable
              style="width: 240px; margin-right: 12px"
              :prefix-icon="Search"
            />
            <el-button type="primary" @click="handleAdd">
              <el-icon><Plus /></el-icon>新建考试
            </el-button>
          </div>
        </div>
      </template>

      <template #column-及格分="{ row }">
        {{ row.及格分 }}/{{ row.总分 }}
      </template>

      <template #column-状态="{ row }">
        <el-tag :type="row.是否发布 ? 'success' : 'info'" size="small">
          {{ row.是否发布 ? '已发布' : '草稿' }}
        </el-tag>
      </template>

      <template #actions="{ row }">
        <el-button text size="small" type="primary" @click="handleEdit(row)">编辑</el-button>
        <el-button text size="small" type="warning" @click="handleToggle(row)">
          {{ row.是否发布 ? '下架' : '发布' }}
        </el-button>
        <el-button text size="small" type="danger" @click="handleDelete(row)">删除</el-button>
      </template>
    </AdminTable>

    <!-- 新建/编辑考试对话框 -->
    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑考试' : '新建考试'" width="750px" destroy-on-close>
      <el-form ref="formRef" :model="form" :rules="rules" label-width="90px">
        <el-form-item label="考试名称" prop="标题">
          <el-input v-model="form.标题" placeholder="请输入考试名称" />
        </el-form-item>
        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item label="时长(分钟)" prop="考试时长">
              <el-input-number v-model="form.考试时长" :min="1" :max="180" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="总分" prop="总分">
              <el-input-number v-model="form.总分" :min="1" :max="500" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="及格分" prop="及格分">
              <el-input-number v-model="form.及格分" :min="0" :max="500" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="考试描述">
          <el-input v-model="form.描述" type="textarea" :rows="2" placeholder="可选的考试说明" />
        </el-form-item>
        <el-form-item label="是否发布" v-if="!isEdit">
          <el-switch v-model="form.是否发布" />
        </el-form-item>

        <!-- 选题区域 -->
        <el-divider content-position="left">选择题目 ({{ form.选题列表.length }} 道)</el-divider>
        <div style="margin-bottom:12px">
          <el-select v-model="questionFilter.type" placeholder="题型" clearable style="width:120px;margin-right:8px" @change="loadQuestions">
            <el-option label="单选题" value="single" /><el-option label="多选题" value="multi" />
            <el-option label="判断题" value="judge" /><el-option label="填空题" value="fill" />
          </el-select>
          <el-input v-model="questionFilter.keyword" placeholder="搜索题目" clearable style="width:200px;margin-right:8px" @keyup.enter="loadQuestions" />
          <el-button type="primary" size="small" @click="loadQuestions">搜索</el-button>
        </div>
        <el-table :data="availableQuestions" border size="small" max-height="300" @selection-change="onSelectQuestions" ref="qTableRef">
          <el-table-column type="selection" width="40" />
          <el-table-column label="题型" width="70">
            <template #default="{ row }"><el-tag :type="typeTag(row.题型)" size="small">{{ typeLabel(row.题型) }}</el-tag></template>
          </el-table-column>
          <el-table-column prop="题目内容" label="题目内容" min-width="250" show-overflow-tooltip />
          <el-table-column prop="分值" label="分值" width="60" align="center" />
        </el-table>
        <el-pagination
          v-model:current-page="qPage" :page-size="10" :total="qTotal"
          layout="prev, pager, next" small @current-change="loadQuestions"
          style="margin-top:8px; justify-content:center"
        />
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { Plus, Search } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getExams, getExamDetail, createExam, updateExam, deleteExam, getQuestions } from '@/api/exams'
import AdminTable from '@/components/AdminTable.vue'

const loading = ref(false)
const examList = ref([])
const total = ref(0)
const page = ref(1)
const dialogVisible = ref(false)
const isEdit = ref(false)
const submitting = ref(false)
const formRef = ref(null)
const editId = ref(null)
const qTableRef = ref(null)

const availableQuestions = ref([])
const qTotal = ref(0)
const qPage = ref(1)
const questionFilter = reactive({ type: '', keyword: '' })
const selectedQuestions = ref([])

const searchQuery = ref('')
const filteredExamList = computed(() => {
  if (!searchQuery.value) return examList.value
  const kw = searchQuery.value.toLowerCase()
  return examList.value.filter(item => (item.标题 || '').toLowerCase().includes(kw))
})

const columns = [
  { prop: '标题', label: '考试名称', minWidth: 200 },
  { prop: '考试时长', label: '时长(分)', width: 90, align: 'center' },
  { slot: 'column-及格分', label: '及格分', width: 80, align: 'center' },
  { prop: '题目数量', label: '题目数', width: 80, align: 'center' },
  { slot: 'column-状态', label: '状态', width: 90 },
]

const form = reactive({
  标题: '', 描述: '', 考试时长: 60, 总分: 100, 及格分: 60, 是否发布: false,
  选题列表: []
})

const rules = {
  标题: [{ required: true, message: '请输入考试名称', trigger: 'blur' }],
  考试时长: [{ required: true }], 总分: [{ required: true }], 及格分: [{ required: true }]
}

const typeTag = (t) => ({ single: 'primary', multi: 'warning', judge: 'success', fill: 'info' }[t] || 'info')
const typeLabel = (t) => ({ single: '单选', multi: '多选', judge: '判断', fill: '填空' }[t] || t)

const loadData = async () => {
  loading.value = true
  try {
    const res = await getExams({ page: page.value, page_size: 20 })
    examList.value = res.数据 || []
    total.value = res.共计 || 0
  } catch { examList.value = [] } finally { loading.value = false }
}

const loadQuestions = async () => {
  const params = { page: qPage.value, page_size: 10 }
  if (questionFilter.type) params.question_type = questionFilter.type
  if (questionFilter.keyword) params.keyword = questionFilter.keyword
  try {
    const res = await getQuestions(params)
    availableQuestions.value = res.数据 || []
    qTotal.value = res.共计 || 0
  } catch { availableQuestions.value = [] }
}

const onSelectQuestions = (rows) => { selectedQuestions.value = rows }

const handleAdd = () => {
  isEdit.value = false; editId.value = null
  form.标题 = ''; form.描述 = ''; form.考试时长 = 60; form.总分 = 100; form.及格分 = 60
  form.是否发布 = false; form.选题列表 = []
  qPage.value = 1; questionFilter.type = ''; questionFilter.keyword = ''
  loadQuestions()
  dialogVisible.value = true
}

const handleEdit = async (row) => {
  isEdit.value = true; editId.value = row.ID
  dialogVisible.value = true
  try {
    const res = await getExamDetail(row.ID)
    const d = res.数据
    form.标题 = d.标题; form.描述 = d.描述 || ''
    form.考试时长 = d.考试时长; form.总分 = d.总分; form.及格分 = d.及格分
    form.选题列表 = (d.题目列表 || []).map(q => ({ 题目ID: q.ID, 分值: q.分值, 排序: 0 }))
    qPage.value = 1; questionFilter.type = ''; questionFilter.keyword = ''
    loadQuestions()
  } catch { ElMessage.error('加载失败') }
}

const handleToggle = async (row) => {
  try {
    await updateExam(row.ID, { 是否发布: !row.是否发布 })
    ElMessage.success(row.是否发布 ? '已下架' : '已发布')
    loadData()
  } catch { ElMessage.error('操作失败') }
}

const handleDelete = (row) => {
  ElMessageBox.confirm(`确定删除「${row.标题}」？`, '警告', { type: 'warning' })
    .then(async () => {
      await deleteExam(row.ID)
      ElMessage.success('已删除')
      loadData()
    }).catch(() => {})
}

const handleSubmit = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  submitting.value = true
  try {
    const qs = selectedQuestions.value.map(q => ({ 题目ID: q.ID, 分值: q.分值 || 10, 排序: 0 }))
    const allQs = [...form.选题列表, ...qs]
    const seen = new Set()
    const deduped = allQs.filter(q => {
      if (seen.has(q.题目ID)) return false
      seen.add(q.题目ID)
      return true
    })

    const data = {
      标题: form.标题, 描述: form.描述, 考试时长: form.考试时长,
      总分: form.总分, 及格分: form.及格分, 选题列表: deduped
    }
    if (!isEdit.value) data.是否发布 = form.是否发布

    if (isEdit.value) {
      await updateExam(editId.value, data)
      ElMessage.success('考试更新成功')
    } else {
      await createExam(data)
      ElMessage.success('考试创建成功')
    }
    dialogVisible.value = false
    loadData()
  } catch { ElMessage.error('操作失败') } finally { submitting.value = false }
}

onMounted(() => loadData())
</script>

<style scoped>
.exams-page { max-width: 1200px; }
.page-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px; }
.header-right { display: flex; align-items: center; }
.page-title { font-size: 22px; font-weight: 600;  color: var(--text-primary);}
</style>
