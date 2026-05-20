<template>
  <div class="questions-page">
    <AdminTable
      :data="questionList"
      :loading="loading"
      :total="total"
      v-model:model-value="pagination.page"
      v-model:page-size="pagination.page_size"
      :columns="columns"
      :show-search="false"
      :show-pagination="true"
      :actions-width="140"
      :page-sizes="[10, 20, 50]"
      @current-change="loadData"
      @size-change="loadData"
    >
      <template #page-header>
        <div class="page-header">
          <h2 class="page-title">题库管理</h2>
          <el-button type="primary" @click="handleAdd">
            <el-icon><Plus /></el-icon>新增题目
          </el-button>
        </div>
      </template>

      <template #filter>
        <el-card shadow="never" class="filter-bar">
          <el-row :gutter="16" align="middle">
            <el-col :xs="24" :sm="8">
              <el-select v-model="filters.question_type" placeholder="题型筛选" clearable style="width:100%">
                <el-option label="单选题" value="single" />
                <el-option label="多选题" value="multi" />
                <el-option label="判断题" value="judge" />
                <el-option label="填空题" value="fill" />
                <el-option label="简答题" value="short_answer" />
              </el-select>
            </el-col>
            <el-col :xs="24" :sm="8">
              <el-input v-model="filters.keyword" placeholder="搜索题目内容" clearable @clear="loadData" @keyup.enter="loadData" />
            </el-col>
            <el-col :xs="24" :sm="4">
              <el-button type="primary" @click="loadData" :icon="Search">搜索</el-button>
            </el-col>
          </el-row>
        </el-card>
      </template>

      <template #column-题型="{ row }">
        <el-tag :type="typeTag(row.题型)" size="small">{{ typeLabel(row.题型) }}</el-tag>
      </template>

      <template #column-难度="{ row }">
        <el-rate v-model="row.难度" disabled show-score text-color="#ff9900" />
      </template>

      <template #actions="{ row }">
        <el-button text size="small" type="primary" @click="handleEdit(row)">编辑</el-button>
        <el-button text size="small" type="danger" @click="handleDelete(row)">删除</el-button>
      </template>
    </AdminTable>

    <!-- 新增/编辑对话框 -->
    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑题目' : '新增题目'" width="650px" destroy-on-close>
      <el-form ref="formRef" :model="form" :rules="rules" label-width="80px">
        <el-form-item label="题目类型" prop="题型">
          <el-radio-group v-model="form.题型" :disabled="isEdit">
            <el-radio value="single">单选题</el-radio>
            <el-radio value="multi">多选题</el-radio>
            <el-radio value="judge">判断题</el-radio>
            <el-radio value="fill">填空题</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="题目内容" prop="题目内容">
          <el-input v-model="form.题目内容" type="textarea" :rows="3" placeholder="请输入题目内容" />
        </el-form-item>
        <el-form-item label="分值" prop="分值">
          <el-input-number v-model="form.分值" :min="1" :max="100" />
        </el-form-item>
        <el-form-item label="难度" prop="难度">
          <el-rate v-model="form.难度" :max="5" />
        </el-form-item>
        <!-- 选择题选项 -->
        <el-form-item label="选项" v-if="form.题型 === 'single' || form.题型 === 'multi'">
          <div style="display:flex;flex-direction:column;gap:8px;width:100%">
            <div v-for="(opt, idx) in form.options" :key="idx" style="display:flex;align-items:center;gap:8px">
              <span style="font-weight:600;width:24px">{{ opt.标签 }}</span>
              <el-input v-model="opt.内容" :placeholder="'选项' + opt.标签" style="flex:1" />
              <el-button text type="danger" :icon="Delete" @click="form.options.splice(idx,1)" :disabled="form.options.length<=2" />
            </div>
          </div>
          <el-button type="primary" text @click="addOption" style="margin-top:8px">+ 添加选项</el-button>
        </el-form-item>
        <!-- 正确答案 -->
        <el-form-item label="正确答案" prop="正确答案">
          <template v-if="form.题型 === 'single' || form.题型 === 'multi'">
            <el-checkbox-group v-model="form.答案勾选" v-if="form.题型 === 'multi'">
              <el-checkbox v-for="opt in form.options" :key="opt.标签" :label="opt.标签" :value="opt.标签" />
            </el-checkbox-group>
            <el-radio-group v-model="form.答案勾选" v-else>
              <el-radio v-for="opt in form.options" :key="opt.标签" :label="opt.标签" :value="opt.标签" />
            </el-radio-group>
          </template>
          <el-radio-group v-else-if="form.题型 === 'judge'" v-model="form.正确答案">
            <el-radio value="A">正确</el-radio>
            <el-radio value="B">错误</el-radio>
          </el-radio-group>
          <el-input v-else v-model="form.正确答案" placeholder="输入正确答案" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { Plus, Search, Delete } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getQuestions, createQuestion, updateQuestion, deleteQuestion } from '@/api/exams'
import AdminTable from '@/components/AdminTable.vue'

const loading = ref(false)
const questionList = ref([])
const total = ref(0)
const dialogVisible = ref(false)
const isEdit = ref(false)
const submitting = ref(false)
const formRef = ref(null)
const editId = ref(null)

const filters = reactive({ question_type: '', keyword: '' })
const pagination = reactive({ page: 1, page_size: 20 })

const columns = [
  { slot: 'column-题型', label: '题型', width: 90 },
  { prop: '题目内容', label: '题目内容', minWidth: 280, ellipsis: true },
  { prop: '分值', label: '分值', width: 70, align: 'center' },
  { slot: 'column-难度', label: '难度', width: 80, align: 'center' },
]

const form = reactive({
  题型: 'single', 题目内容: '', 分值: 10, 难度: 1,
  options: [], 正确答案: '', 答案勾选: []
})

const rules = {
  题目内容: [{ required: true, message: '请输入题目内容', trigger: 'blur' }],
  题型: [{ required: true }]
}

const typeTag = (t) => ({ single: 'primary', multi: 'warning', judge: 'success', fill: 'info', short_answer: '' }[t] || 'info')
const typeLabel = (t) => ({ single: '单选', multi: '多选', judge: '判断', fill: '填空', short_answer: '简答' }[t] || t)

const initOptions = () => {
  form.options = [
    { 标签: 'A', 内容: '' }, { 标签: 'B', 内容: '' },
    { 标签: 'C', 内容: '' }, { 标签: 'D', 内容: '' }
  ]
  form.答案勾选 = []
}

const addOption = () => {
  form.options.push({ 标签: String.fromCharCode(65 + form.options.length), 内容: '' })
}

const loadData = async () => {
  loading.value = true
  try {
    const params = { ...filters, page: pagination.page, page_size: pagination.page_size }
    Object.keys(params).forEach(k => { if (!params[k]) delete params[k] })
    const res = await getQuestions(params)
    questionList.value = res.数据 || []
    total.value = res.共计 || 0
  } catch { questionList.value = [] }
  finally { loading.value = false }
}

const handleAdd = () => {
  isEdit.value = false; editId.value = null
  form.题型 = 'single'; form.题目内容 = ''; form.分值 = 10; form.难度 = 1
  form.正确答案 = ''; initOptions()
  dialogVisible.value = true
}

const handleEdit = (row) => {
  isEdit.value = true; editId.value = row.ID
  form.题型 = row.题型; form.题目内容 = row.题目内容
  form.分值 = row.分值; form.难度 = row.难度
  form.正确答案 = row.正确答案 || ''
  const opts = row.选项
  if (opts) {
    try {
      const arr = JSON.parse(opts)
      form.options = arr.map((v, i) => ({ 标签: String.fromCharCode(65 + i), 内容: v }))
    } catch { initOptions() }
  } else {
    initOptions()
  }
  form.答案勾选 = form.题型 === 'multi' ? (row.正确答案 || '').split(',').filter(Boolean) : (row.正确答案 || '')
  dialogVisible.value = true
}

const buildSubmitData = () => {
  const data = { 题型: form.题型, 题目内容: form.题目内容, 分值: form.分值, 难度: form.难度 }
  if (form.题型 === 'single' || form.题型 === 'multi') {
    data.选项 = JSON.stringify(form.options.map(o => o.内容))
    data.正确答案 = Array.isArray(form.答案勾选) ? form.答案勾选.join(',') : form.答案勾选
  } else {
    data.正确答案 = form.正确答案
    data.选项 = form.题型 === 'judge' ? '["正确","错误"]' : ''
  }
  return data
}

const handleSubmit = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  submitting.value = true
  try {
    const data = buildSubmitData()
    if (isEdit.value) {
      await updateQuestion(editId.value, data)
      ElMessage.success('题目更新成功')
    } else {
      await createQuestion(data)
      ElMessage.success('题目创建成功')
    }
    dialogVisible.value = false
    loadData()
  } catch { ElMessage.error('操作失败') }
  finally { submitting.value = false }
}

const handleDelete = (row) => {
  ElMessageBox.confirm(`确定要删除「${row.题目内容.slice(0,30)}...」吗？`, '提示', { type: 'warning' })
    .then(async () => {
      await deleteQuestion(row.ID)
      ElMessage.success('已删除')
      loadData()
    }).catch(() => {})
}

onMounted(() => loadData())
</script>

<style scoped>
.questions-page { max-width: 1200px; }
.page-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px; }
.page-title { font-size: 22px; font-weight: 600; color: var(--text-primary); }
.filter-bar { margin-bottom: var(--space-4); }
</style>
