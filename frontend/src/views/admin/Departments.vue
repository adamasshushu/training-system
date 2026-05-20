<template>
  <div class="departments">
    <div class="page-header">
      <h2 class="page-title">部门管理</h2>
      <el-button type="primary" @click="handleAdd">
        <el-icon><Plus /></el-icon>新增部门
      </el-button>
    </div>

    <el-card shadow="never">
      <el-tree
        :data="departmentTree"
        :props="treeProps"
        node-key="id"
        default-expand-all
        :expand-on-click-node="false"
        draggable
      >
        <template #default="{ node, data }">
          <span class="tree-node">
            <span>{{ node.label }}</span>
            <span class="tree-actions">
              <el-button text size="small" type="primary" @click="handleEdit(data)">
                编辑
              </el-button>
              <el-button text size="small" type="danger" @click="handleDelete(data)">
                删除
              </el-button>
            </span>
          </span>
        </template>
      </el-tree>
    </el-card>

    <!-- 新增/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑部门' : '新增部门'"
      width="500px"
    >
      <el-form ref="formRef" :model="form" :rules="rules" label-width="80px">
        <el-form-item label="部门名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入部门名称" />
        </el-form-item>
        <el-form-item label="上级部门" prop="parent_id">
          <el-tree-select
            v-model="form.parent_id"
            :data="departmentTree"
            :props="{ label: 'name', value: 'id' }"
            placeholder="选择上级部门"
            check-strictly
            clearable
          />
        </el-form-item>
        <el-form-item label="排序" prop="sort">
          <el-input-number v-model="form.sort" :min="0" :max="999" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const departmentTree = ref([
  {
    id: 1,
    name: '总公司',
    sort: 0,
    children: [
      { id: 2, name: '技术部', sort: 1, children: [] },
      { id: 3, name: '产品部', sort: 2, children: [] },
      { id: 4, name: '市场部', sort: 3, children: [] }
    ]
  }
])

const treeProps = { children: 'children', label: 'name' }
const dialogVisible = ref(false)
const isEdit = ref(false)
const submitting = ref(false)
const formRef = ref(null)
const editId = ref(null)

const form = reactive({
  name: '',
  parent_id: null,
  sort: 0
})

const rules = {
  name: [{ required: true, message: '请输入部门名称', trigger: 'blur' }]
}

const handleAdd = () => {
  isEdit.value = false
  editId.value = null
  form.name = ''
  form.parent_id = null
  form.sort = 0
  dialogVisible.value = true
}

const handleEdit = (data) => {
  isEdit.value = true
  editId.value = data.id
  form.name = data.name
  form.parent_id = data.parent_id || null
  form.sort = data.sort || 0
  dialogVisible.value = true
}

const handleDelete = (data) => {
  ElMessageBox.confirm(`确定要删除部门"${data.name}"吗？`, '提示', {
    type: 'warning'
  }).then(() => {
    ElMessage.success('删除成功')
  }).catch(() => {})
}

const handleSubmit = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  submitting.value = true
  try {
    ElMessage.success(isEdit.value ? '编辑成功' : '新增成功')
    dialogVisible.value = false
  } catch {
    // 错误处理
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.departments {
  max-width: 1200px;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
}

.page-title {
  font-size: 22px;
  font-weight: 600;
  color: var(--text-primary);
}

.tree-node {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex: 1;
  padding-right: 16px;
  font-size: 14px;
}

.tree-actions {
  display: none;
}

.el-tree-node__content:hover .tree-actions {
  display: inline-flex;
  gap: 4px;
}
</style>
