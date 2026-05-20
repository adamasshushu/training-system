<template>
  <div class="course-categories">
    <AdminTable
      :data="categoryList"
      :loading="loading"
      :total="total"
      v-model:model-value="page"
      :page-size="pageSize"
      :show-pagination="false"
      :columns="columns"
      :actions-width="180"
    >
      <template #page-header>
        <div class="page-header">
          <h2 class="page-title">课程分类</h2>
          <el-button type="primary" @click="handleAdd"><el-icon><Plus /></el-icon>新增分类</el-button>
        </div>
      </template>

      <template #column-名称="{ row }">
        {{ row['名称'] }}
      </template>

      <template #column-排序="{ row }">
        {{ row['排序'] }}
      </template>

      <template #column-课程数="{ row }">
        {{ row['课程数量'] || 0 }}
      </template>

      <template #column-状态="{ row }">
        <el-tag :type="row['是否激活'] ? 'success' : 'info'" size="small">
          {{ row['是否激活'] ? '激活' : '停用' }}
        </el-tag>
      </template>

      <template #actions="{ row }">
        <el-button text size="small" type="primary" @click="handleEdit(row)">编辑</el-button>
        <el-button text size="small" type="danger" @click="handleDelete(row)">删除</el-button>
      </template>
    </AdminTable>

    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑分类' : '新增分类'"
      width="500px"
    >
      <el-form ref="formRef" :model="form" :rules="rules" label-width="80px">
        <el-form-item label="分类名称" prop="名称">
          <el-input v-model="form['名称']" placeholder="请输入分类名称" />
        </el-form-item>
        <el-form-item label="排序" prop="排序">
          <el-input-number v-model="form['排序']" :min="0" :max="999" />
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
import { Plus } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getCategories, createCategory, deleteCategory } from '@/api/courses'
import AdminTable from '@/components/AdminTable.vue'

const categoryList = ref([])
const loading = ref(false)
const total = ref(0)
const page = ref(1)
const pageSize = ref(10)
const dialogVisible = ref(false)
const isEdit = ref(false)
const submitting = ref(false)
const formRef = ref(null)
const editId = ref(null)

const form = reactive({ '名称': '', '排序': 0 })
const rules = { '名称': [{ required: true, message: '请输入分类名称', trigger: 'blur' }] }

const columns = [
  { slot: 'column-名称', label: '分类名称', minWidth: 200 },
  { slot: 'column-排序', label: '排序', width: 100, align: 'center' },
  { slot: 'column-课程数', label: '课程数', width: 100, align: 'center' },
  { slot: 'column-状态', label: '状态', width: 100, align: 'center' },
]

const fetchCategories = async () => {
  loading.value = true
  try {
    const res = await getCategories()
    categoryList.value = res['数据'] || []
    total.value = categoryList.value.length
  } catch (e) {
    ElMessage.error('获取分类列表失败')
  } finally {
    loading.value = false
  }
}

const handleAdd = () => {
  isEdit.value = false
  editId.value = null
  form['名称'] = ''
  form['排序'] = 0
  dialogVisible.value = true
}

const handleEdit = (row) => {
  isEdit.value = true
  editId.value = row['ID']
  form['名称'] = row['名称']
  form['排序'] = row['排序']
  dialogVisible.value = true
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(`确定要删除分类"${row['名称']}"吗？`, '提示', { type: 'warning' })
    await deleteCategory(row['ID'])
    ElMessage.success('删除成功')
    await fetchCategories()
  } catch (e) {
    if (e !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const handleSubmit = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  submitting.value = true
  try {
    const payload = { '名称': form['名称'], '上级ID': null, '排序': form['排序'] }
    await createCategory(payload)
    ElMessage.success(isEdit.value ? '编辑成功' : '新增成功')
    dialogVisible.value = false
    await fetchCategories()
  } catch {
    ElMessage.error('操作失败')
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  fetchCategories()
})
</script>

<style scoped>
.course-categories { max-width: 1200px; }
.page-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px; }
.page-title { font-size: 22px; font-weight: 600; color: var(--text-primary); }
</style>
