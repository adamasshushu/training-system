<template>
  <div class="departments">
    <div class="page-header">
      <h2 class="page-title">部门管理</h2>
      <el-button type="primary" class="glass-btn-primary" @click="handleAdd">
        <el-icon><Plus /></el-icon>新增部门
      </el-button>
    </div>

    <div class="glass-card" v-loading="loading">
      <el-tree
        v-if="!loading && departmentTree.length > 0"
        :data="departmentTree"
        :props="treeProps"
        node-key="ID"
        default-expand-all
        :expand-on-click-node="false"
        draggable
      >
        <template #default="{ node, data }">
          <span class="tree-node">
            <span class="tree-label">{{ data.名称 }}</span>
            <span class="tree-meta">
              <el-tag size="small" type="info" effect="plain" v-if="data.员工数量 > 0">{{ data.员工数量 }}人</el-tag>
            </span>
            <span class="tree-actions">
              <el-button text size="small" type="primary" @click.stop="handleEdit(data)">编辑</el-button>
              <el-button text size="small" type="danger" @click.stop="handleDelete(data)">删除</el-button>
            </span>
          </span>
        </template>
      </el-tree>
      <el-empty v-else-if="!loading" description="暂无部门数据" />
    </div>

    <!-- 新增/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑部门' : '新增部门'"
      width="480px"
      :close-on-click-modal="false"
      class="glass-dialog"
    >
      <el-form ref="formRef" :model="form" :rules="rules" label-width="90px">
        <el-form-item label="部门名称" prop="名称">
          <el-input v-model="form.名称" placeholder="请输入部门名称" class="glass-input" />
        </el-form-item>
        <el-form-item label="上级部门" prop="上级部门ID">
          <el-tree-select
            v-model="form.上级部门ID"
            :data="departmentTree"
            :props="{ label: '名称', value: 'ID', children: '子部门' }"
            placeholder="选择上级部门（留空为顶级）"
            check-strictly
            clearable
          />
        </el-form-item>
        <el-form-item label="排序" prop="排序">
          <el-input-number v-model="form.排序" :min="0" :max="999" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false" class="glass-btn-cancel">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting" class="glass-btn-primary">
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { Plus } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getDepartments, createDepartment, updateDepartment, deleteDepartment } from '@/api/departments'

const departmentTree = ref([])
const loading = ref(false)
const treeProps = { children: '子部门', label: '名称' }
const dialogVisible = ref(false)
const isEdit = ref(false)
const submitting = ref(false)
const formRef = ref(null)
const editId = ref(null)

const form = reactive({
  名称: '',
  上级部门ID: null,
  排序: 0
})

const rules = {
  名称: [{ required: true, message: '请输入部门名称', trigger: 'blur' }]
}

async function fetchDepartments() {
  loading.value = true
  try {
    const res = await getDepartments()
    departmentTree.value = res.数据 || []
  } catch {
    departmentTree.value = []
  } finally {
    loading.value = false
  }
}

function handleAdd() {
  isEdit.value = false
  editId.value = null
  form.名称 = ''
  form.上级部门ID = null
  form.排序 = 0
  dialogVisible.value = true
}

function handleEdit(data) {
  isEdit.value = true
  editId.value = data.ID
  form.名称 = data.名称
  form.上级部门ID = data.上级部门ID || null
  form.排序 = data.排序 || 0
  dialogVisible.value = true
}

function handleDelete(data) {
  if (data.员工数量 > 0) {
    ElMessage.warning('该部门下还有员工，无法删除')
    return
  }
  ElMessageBox.confirm(`确定要删除部门「${data.名称}」吗？`, '提示', { type: 'warning' })
    .then(async () => {
      try {
        await deleteDepartment(data.ID)
        ElMessage.success('删除成功')
        fetchDepartments()
      } catch { /* 拦截器已处理 */ }
    })
    .catch(() => {})
}

async function handleSubmit() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return
  submitting.value = true
  try {
    if (isEdit.value) {
      await updateDepartment(editId.value, {
        名称: form.名称, 上级部门ID: form.上级部门ID, 排序: form.排序
      })
      ElMessage.success('编辑成功')
    } else {
      await createDepartment({
        名称: form.名称, 上级部门ID: form.上级部门ID, 排序: form.排序
      })
      ElMessage.success('新增成功')
    }
    dialogVisible.value = false
    fetchDepartments()
  } catch { /* 拦截器已处理 */ }
  finally { submitting.value = false }
}

onMounted(() => { fetchDepartments() })
</script>

<style scoped>
/* ═══════════ 毛玻璃主题 ═══════════ */

.departments { max-width: 1000px; }

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
}

.page-title {
  font-size: 22px;
  font-weight: 700;
  background: linear-gradient(135deg, #2d3436, #636e72);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

:global(.dark) .page-title {
  background: linear-gradient(135deg, #dfe6e9, #b2bec3);
  -webkit-background-clip: text;
  background-clip: text;
}

.glass-card {
  background: rgba(255, 255, 255, 0.55);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.4);
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.06);
  padding: 20px;
  transition: all 0.3s ease;
}

.glass-card:hover {
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.1);
}

:global(.dark) .glass-card {
  background: rgba(20, 20, 35, 0.6);
  border-color: rgba(255, 255, 255, 0.08);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
}

.glass-btn-primary {
  border-radius: 12px !important;
  background: linear-gradient(135deg, #6C5CE7, #a29bfe) !important;
  border: none !important;
  transition: all 0.3s ease;
}

.glass-btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(108, 92, 231, 0.35);
}

.glass-btn-cancel {
  border-radius: 12px !important;
  transition: all 0.3s ease;
}

.glass-input :deep(.el-input__wrapper) {
  border-radius: 12px !important;
}

/* ── 树节点 ── */

.tree-node {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex: 1;
  padding: 6px 12px;
  margin: 2px 0;
  border-radius: 10px;
  transition: all 0.2s ease;
  font-size: 14px;
}

.tree-node:hover {
  background: rgba(108, 92, 231, 0.06);
}

.tree-label {
  font-weight: 500;
}

.tree-meta {
  margin-left: auto;
  margin-right: 8px;
}

.tree-actions {
  display: none;
  gap: 4px;
}

.el-tree-node__content:hover .tree-actions {
  display: inline-flex;
}

/* ── 对话框 ── */

.glass-dialog :deep(.el-dialog) {
  border-radius: 20px !important;
  backdrop-filter: blur(20px);
  background: rgba(255, 255, 255, 0.9) !important;
  border: 1px solid rgba(255, 255, 255, 0.5);
  box-shadow: 0 16px 48px rgba(0, 0, 0, 0.12);
}

:global(.dark) .glass-dialog :deep(.el-dialog) {
  background: rgba(25, 25, 45, 0.9) !important;
  border-color: rgba(255, 255, 255, 0.06);
}

/* ── 响应式 ── */

@media (max-width: 768px) {
  .page-header { flex-direction: column; gap: 12px; align-items: flex-start; }
  .page-title { font-size: 18px; }
}
</style>
