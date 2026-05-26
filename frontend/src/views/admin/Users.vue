<template>
  <div class="users">
    <div class="page-header glass-header">
      <h2 class="page-title">员工管理</h2>
      <div class="header-actions">
        <el-input
          v-model="searchQuery"
          placeholder="搜索姓名/邮箱/用户名"
          clearable
          style="width: 260px"
          :prefix-icon="Search"
          class="glass-input"
          @clear="fetchUsers"
          @keyup.enter="fetchUsers"
        />
        <el-select v-model="filterRole" placeholder="角色筛选" clearable style="width: 130px" @change="fetchUsers" class="glass-select">
          <el-option label="全部" value="" />
          <el-option label="学员" value="student" />
          <el-option label="讲师" value="teacher" />
          <el-option label="管理员" value="admin" />
        </el-select>
        <el-select v-model="filterDept" placeholder="部门筛选" clearable style="width: 150px" @change="fetchUsers" class="glass-select">
          <el-option label="全部" value="" />
          <el-option v-for="d in departmentOptions" :key="d.id" :label="d.name" :value="d.id" />
        </el-select>
        <el-button type="primary" class="glass-btn-primary" @click="handleAdd">
          <el-icon><Plus /></el-icon>新增员工
        </el-button>
      </div>
    </div>

    <div class="glass-card table-card">
      <el-table :data="userList" v-loading="loading" stripe border style="width: 100%" class="glass-table">
        <el-table-column prop="真实姓名" label="姓名" min-width="120" />
        <el-table-column prop="用户名" label="用户名" min-width="120" />
        <el-table-column prop="邮箱" label="邮箱" min-width="180" />
        <el-table-column prop="手机号" label="手机号" min-width="130" />
        <el-table-column prop="部门名称" label="部门" min-width="130" />
        <el-table-column label="角色" width="110">
          <template #default="{ row }">
            <el-tag :type="row.角色 === 'admin' ? 'danger' : row.角色 === 'teacher' ? 'warning' : 'success'" size="small" effect="dark">
              {{ row.角色 === 'admin' ? '管理员' : row.角色 === 'teacher' ? '讲师' : '学员' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="来源" width="80">
          <template #default="{ row }">
            <el-tag :type="row.来源 === 'ldap' ? '' : 'info'" size="small" effect="plain" class="source-tag">
              {{ row.来源 === 'ldap' ? '🔗 LDAP' : '💻 本地' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.是否激活 ? 'success' : 'info'" size="small" effect="dark">
              {{ row.是否激活 ? '启用' : '停用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="280" fixed="right">
          <template #default="{ row }">
            <el-button text size="small" type="primary" @click="handleEdit(row)">编辑</el-button>
            <el-button text size="small" type="warning" @click="handleResetPwd(row)" :disabled="row.来源 === 'ldap'">重置密码</el-button>
            <el-button text size="small" type="danger" @click="handleToggleStatus(row)">
              {{ row.是否激活 ? '停用' : '启用' }}
            </el-button>
            <el-button text size="small" type="danger" @click="handlePermanentDelete(row)" :disabled="row.用户名 === 'admin'">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-wrap" v-if="total > 0">
        <el-pagination
          v-model:current-page="page"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="fetchUsers"
          @current-change="fetchUsers"
        />
      </div>
    </div>

    <!-- 新增/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑员工' : '新增员工'"
      width="500px"
      :close-on-click-modal="false"
      class="glass-dialog"
    >
      <el-form ref="formRef" :model="form" :rules="rules" label-width="90px">
        <el-form-item label="用户名" prop="用户名">
          <el-input v-model="form.用户名" placeholder="登录用的用户名/工号" :disabled="isEdit" class="glass-input" />
        </el-form-item>
        <el-form-item label="真实姓名" prop="真实姓名">
          <el-input v-model="form.真实姓名" placeholder="请输入真实姓名" class="glass-input" />
        </el-form-item>
        <el-form-item label="邮箱" prop="邮箱">
          <el-input v-model="form.邮箱" placeholder="请输入邮箱" class="glass-input" />
        </el-form-item>
        <el-form-item label="手机号" prop="手机号">
          <el-input v-model="form.手机号" placeholder="请输入手机号" class="glass-input" />
        </el-form-item>
        <el-form-item label="密码" prop="密码" v-if="!isEdit">
          <el-input v-model="form.密码" type="password" placeholder="请输入密码" show-password class="glass-input" />
        </el-form-item>
        <el-form-item label="部门" prop="部门ID">
          <el-tree-select
            v-model="form.部门ID"
            :data="deptTreeData"
            :props="{ label: '名称', value: 'ID', children: '子部门' }"
            placeholder="选择部门"
            check-strictly
            clearable
          />
        </el-form-item>
        <el-form-item label="角色" prop="角色">
          <el-select v-model="form.角色" placeholder="选择角色" class="glass-select">
            <el-option label="学员" value="student" />
            <el-option label="讲师" value="teacher" />
            <el-option label="管理员" value="admin" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false" class="glass-btn-cancel">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting" class="glass-btn-primary">确定</el-button>
      </template>
    </el-dialog>

    <!-- 重置密码对话框 -->
    <el-dialog
      v-model="pwdDialogVisible"
      title="重置密码"
      width="420px"
      :close-on-click-modal="false"
      class="glass-dialog"
    >
      <el-alert
        :title="`正在为「${pwdTargetUser}」重置密码`"
        type="info"
        :closable="false"
        show-icon
        style="margin-bottom: 16px"
      />
      <el-form ref="pwdFormRef" :model="pwdForm" :rules="pwdRules" label-width="80px" @submit.prevent>
        <el-form-item label="新密码" prop="新密码">
          <el-input
            v-model="pwdForm.新密码"
            type="password"
            placeholder="请输入新密码（至少6位）"
            show-password
            class="glass-input"
            @keyup.enter="handlePwdSubmit"
          />
        </el-form-item>
        <el-form-item label="确认密码" prop="确认密码">
          <el-input
            v-model="pwdForm.确认密码"
            type="password"
            placeholder="再次输入新密码"
            show-password
            class="glass-input"
            @keyup.enter="handlePwdSubmit"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="pwdDialogVisible = false" class="glass-btn-cancel">取消</el-button>
        <el-button type="primary" @click="handlePwdSubmit" :loading="pwdSubmitting" class="glass-btn-primary">确认重置</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { Search, Plus } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getUsers, createUser, updateUser, deleteUser, resetUserPassword, permanentDeleteUser } from '@/api/users'
import request from '@/api/index'

const userList = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(10)
const loading = ref(false)
const searchQuery = ref('')
const filterRole = ref('')
const filterDept = ref('')
const dialogVisible = ref(false)
const isEdit = ref(false)
const submitting = ref(false)
const formRef = ref(null)
const editId = ref(null)

// 密码重置
const pwdDialogVisible = ref(false)
const pwdSubmitting = ref(false)
const pwdFormRef = ref(null)
const pwdTargetId = ref(null)
const pwdTargetUser = ref('')

const pwdForm = reactive({ 新密码: '', 确认密码: '' })

const validateConfirmPwd = (rule, value, callback) => {
  if (value !== pwdForm.新密码) callback(new Error('两次输入的密码不一致'))
  else callback()
}

const pwdRules = {
  新密码: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码至少6位', trigger: 'blur' }
  ],
  确认密码: [
    { required: true, message: '请再次输入密码', trigger: 'blur' },
    { validator: validateConfirmPwd, trigger: 'blur' }
  ]
}

const deptTreeData = ref([])
const departmentOptions = ref([])

function flattenDepts(nodes, result = []) {
  for (const n of nodes) {
    result.push({ id: n.ID, name: n.名称 })
    if (n.子部门 && n.子部门.length) flattenDepts(n.子部门, result)
  }
  return result
}

async function fetchDepartments() {
  try {
    const res = await request.get('/departments')
    deptTreeData.value = res.数据 || []
    departmentOptions.value = flattenDepts(res.数据 || [])
  } catch {
    deptTreeData.value = []
    departmentOptions.value = []
  }
}

async function fetchUsers() {
  loading.value = true
  try {
    const params = { page: page.value, page_size: pageSize.value }
    if (searchQuery.value.trim()) params.keyword = searchQuery.value.trim()
    if (filterRole.value) params.role = filterRole.value
    if (filterDept.value) params.department_id = filterDept.value
    const res = await getUsers(params)
    userList.value = res.数据 || []
    total.value = res.共计 || 0
  } catch {
    userList.value = []
    total.value = 0
  } finally { loading.value = false }
}

const form = reactive({
  用户名: '', 真实姓名: '', 邮箱: '', 手机号: '',
  密码: '', 部门ID: null, 角色: 'student'
})

const rules = {
  用户名: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 2, max: 50, message: '用户名长度2-50个字符', trigger: 'blur' }
  ],
  真实姓名: [{ required: true, message: '请输入真实姓名', trigger: 'blur' }],
  邮箱: [{ pattern: /^$|^[^\s@]+@[^\s@]+\.[^\s@]+$/, message: '邮箱格式不正确', trigger: 'blur' }],
  密码: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码至少6位', trigger: 'blur' }
  ],
  角色: [{ required: true, message: '请选择角色', trigger: 'change' }]
}

function handleAdd() {
  isEdit.value = false; editId.value = null
  Object.assign(form, { 用户名: '', 真实姓名: '', 邮箱: '', 手机号: '', 密码: '', 部门ID: null, 角色: 'student' })
  dialogVisible.value = true
}

function handleEdit(row) {
  isEdit.value = true; editId.value = row.ID
  Object.assign(form, {
    用户名: row.用户名, 真实姓名: row.真实姓名,
    邮箱: row.邮箱 || '', 手机号: row.手机号 || '',
    密码: '', 部门ID: row.部门ID, 角色: row.角色
  })
  dialogVisible.value = true
}

function handleResetPwd(row) {
  pwdTargetId.value = row.ID
  pwdTargetUser.value = `${row.真实姓名}（${row.用户名}）`
  pwdForm.新密码 = ''; pwdForm.确认密码 = ''
  pwdDialogVisible.value = true
}

async function handlePwdSubmit() {
  const valid = await pwdFormRef.value?.validate().catch(() => false)
  if (!valid) return
  pwdSubmitting.value = true
  try {
    await resetUserPassword(pwdTargetId.value, pwdForm.新密码)
    ElMessage.success('密码重置成功')
    pwdDialogVisible.value = false
  } catch { /* 拦截器已处理 */ }
  finally { pwdSubmitting.value = false }
}

function handleToggleStatus(row) {
  const action = row.是否激活 ? '停用' : '启用'
  const msg = row.是否激活
    ? `确定要停用员工「${row.真实姓名}」吗？停用后将无法登录`
    : `确定要重新启用员工「${row.真实姓名}」吗？`
  ElMessageBox.confirm(msg, '提示', { type: 'warning' })
    .then(async () => {
      if (row.是否激活) {
        await deleteUser(row.ID); ElMessage.success('已停用')
      } else {
        await updateUser(row.ID, { 是否激活: true }); ElMessage.success('已启用')
      }
      fetchUsers()
    }).catch(() => {})
}

function handlePermanentDelete(row) {
  ElMessageBox.confirm(
    `永久删除员工「${row.真实姓名}（${row.用户名}）」？\n此操作不可恢复！`,
    '危险操作',
    { type: 'error', confirmButtonText: '确认删除', cancelButtonText: '取消' }
  ).then(async () => {
    await permanentDeleteUser(row.ID)
    ElMessage.success('已永久删除')
    fetchUsers()
  }).catch(() => {})
}

async function handleSubmit() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return
  submitting.value = true
  try {
    if (isEdit.value) {
      await updateUser(editId.value, {
        真实姓名: form.真实姓名, 邮箱: form.邮箱 || null,
        手机号: form.手机号 || null, 角色: form.角色, 部门ID: form.部门ID || null,
      })
      ElMessage.success('编辑成功')
    } else {
      await createUser({
        用户名: form.用户名, 真实姓名: form.真实姓名, 密码: form.密码,
        邮箱: form.邮箱 || null, 手机号: form.手机号 || null,
        角色: form.角色, 部门ID: form.部门ID || null,
      })
      ElMessage.success('新增成功')
    }
    dialogVisible.value = false; fetchUsers()
  } catch { /* 拦截器已处理 */ }
  finally { submitting.value = false }
}

onMounted(() => {
  fetchDepartments(); fetchUsers()
})
</script>

<style scoped>
/* ═══════════ 毛玻璃主题 ═══════════ */

.users { max-width: 1200px; }

.glass-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 12px;
}

.page-title {
  font-size: 22px;
  font-weight: 700;
  margin: 0;
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

.header-actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

/* ── 毛玻璃卡片 ── */

.glass-card {
  background: rgba(255, 255, 255, 0.55);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.4);
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.06);
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

.table-card {
  padding: 20px;
}

/* ── 按钮 ── */

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

/* ── 输入框 ── */

.glass-input :deep(.el-input__wrapper) {
  border-radius: 12px !important;
  transition: all 0.3s ease;
}

.glass-input :deep(.el-input__wrapper:hover) {
  border-color: var(--brand-400, #6C5CE7);
}

.glass-select :deep(.el-input__wrapper) {
  border-radius: 12px !important;
}

/* ── 表格 ── */

.glass-table :deep(.el-table__inner-wrapper) {
  border-radius: 12px;
}

.glass-table :deep(.el-table th) {
  background: rgba(108, 92, 231, 0.06) !important;
  border-bottom: 2px solid rgba(108, 92, 231, 0.12) !important;
  font-weight: 600;
}

.glass-table :deep(.el-table tbody tr) {
  transition: all 0.2s ease;
}

.glass-table :deep(.el-table tbody tr:hover > td) {
  background: rgba(108, 92, 231, 0.04) !important;
}

.source-tag {
  border-radius: 10px !important;
}

/* ── 对话框 ── */

.glass-dialog :deep(.el-dialog) {
  border-radius: 20px !important;
  backdrop-filter: blur(20px);
  background: rgba(255, 255, 255, 0.92) !important;
  border: 1px solid rgba(255, 255, 255, 0.5);
  box-shadow: 0 16px 48px rgba(0, 0, 0, 0.12);
}

:global(.dark) .glass-dialog :deep(.el-dialog) {
  background: rgba(25, 25, 45, 0.92) !important;
  border-color: rgba(255, 255, 255, 0.06);
}

/* ── 分页 ── */

.pagination-wrap {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}

/* ── 响应式 ── */

@media (max-width: 768px) {
  .glass-header { flex-direction: column; align-items: flex-start; }
  .page-title { font-size: 18px; }
}
</style>
