<template>
  <div class="users">
    <div class="page-header">
      <h2 class="page-title">员工管理</h2>
      <div class="header-actions">
        <el-input
          v-model="searchQuery"
          placeholder="搜索姓名/邮箱/用户名"
          clearable
          style="width: 260px"
          :prefix-icon="Search"
          @clear="fetchUsers"
          @keyup.enter="fetchUsers"
        />
        <el-select v-model="filterRole" placeholder="角色筛选" clearable style="width: 130px" @change="fetchUsers">
          <el-option label="全部" value="" />
          <el-option label="学员" value="student" />
          <el-option label="讲师" value="teacher" />
          <el-option label="管理员" value="admin" />
        </el-select>
        <el-select v-model="filterDept" placeholder="部门筛选" clearable style="width: 150px" @change="fetchUsers">
          <el-option label="全部" value="" />
          <el-option v-for="d in departmentOptions" :key="d.id" :label="d.name" :value="d.id" />
        </el-select>
        <el-button type="primary" @click="handleAdd">
          <el-icon><Plus /></el-icon>新增员工
        </el-button>
      </div>
    </div>

    <el-table :data="userList" v-loading="loading" stripe border style="width: 100%">
      <el-table-column prop="真实姓名" label="姓名" min-width="120" />
      <el-table-column prop="用户名" label="用户名" min-width="120" />
      <el-table-column prop="邮箱" label="邮箱" min-width="180" />
      <el-table-column prop="手机号" label="手机号" min-width="130" />
      <el-table-column prop="部门名称" label="部门" min-width="130" />
      <el-table-column label="角色" width="110">
        <template #default="{ row }">
          <el-tag :type="row.角色 === 'admin' ? 'danger' : row.角色 === 'teacher' ? 'warning' : 'success'" size="small">
            {{ row.角色 === 'admin' ? '管理员' : row.角色 === 'teacher' ? '讲师' : '学员' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="状态" width="80">
        <template #default="{ row }">
          <el-tag :type="row.是否激活 ? 'success' : 'info'" size="small">
            {{ row.是否激活 ? '启用' : '停用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="180" fixed="right">
        <template #default="{ row }">
          <el-button text size="small" type="primary" @click="handleEdit(row)">编辑</el-button>
          <el-button text size="small" type="danger" @click="handleDelete(row)">
            {{ row.是否激活 ? '停用' : '启用' }}
          </el-button>
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

    <!-- 新增/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑员工' : '新增员工'"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-form ref="formRef" :model="form" :rules="rules" label-width="90px">
        <el-form-item label="用户名" prop="用户名">
          <el-input v-model="form.用户名" placeholder="登录用的用户名/工号" :disabled="isEdit" />
        </el-form-item>
        <el-form-item label="真实姓名" prop="真实姓名">
          <el-input v-model="form.真实姓名" placeholder="请输入真实姓名" />
        </el-form-item>
        <el-form-item label="邮箱" prop="邮箱">
          <el-input v-model="form.邮箱" placeholder="请输入邮箱" />
        </el-form-item>
        <el-form-item label="手机号" prop="手机号">
          <el-input v-model="form.手机号" placeholder="请输入手机号" />
        </el-form-item>
        <el-form-item label="密码" prop="密码" v-if="!isEdit">
          <el-input v-model="form.密码" type="password" placeholder="请输入密码" show-password />
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
          <el-select v-model="form.角色" placeholder="选择角色">
            <el-option label="学员" value="student" />
            <el-option label="讲师" value="teacher" />
            <el-option label="管理员" value="admin" />
          </el-select>
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
import { Search, Plus } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getUsers, createUser, updateUser, deleteUser } from '@/api/users'
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

// 部门选项（树形 + 扁平）
const deptTreeData = ref([])
const departmentOptions = ref([])

/** 拉平树形部门数据到扁平列表（用于筛选下拉） */
function flattenDepts(nodes, result = []) {
  for (const n of nodes) {
    result.push({ id: n.ID, name: n.名称 })
    if (n.子部门 && n.子部门.length) {
      flattenDepts(n.子部门, result)
    }
  }
  return result
}

/** 加载部门列表 */
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

/** 获取用户列表 */
async function fetchUsers() {
  loading.value = true
  try {
    const params = {
      page: page.value,
      page_size: pageSize.value
    }
    if (searchQuery.value.trim()) {
      params.keyword = searchQuery.value.trim()
    }
    if (filterRole.value) {
      params.role = filterRole.value
    }
    if (filterDept.value) {
      params.department_id = filterDept.value
    }
    const res = await getUsers(params)
    userList.value = res.数据 || []
    total.value = res.共计 || 0
  } catch (e) {
    userList.value = []
    total.value = 0
  } finally {
    loading.value = false
  }
}

const form = reactive({
  用户名: '',
  真实姓名: '',
  邮箱: '',
  手机号: '',
  密码: '',
  部门ID: null,
  角色: 'student'
})

const rules = {
  用户名: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 2, max: 50, message: '用户名长度2-50个字符', trigger: 'blur' }
  ],
  真实姓名: [{ required: true, message: '请输入真实姓名', trigger: 'blur' }],
  邮箱: [
    { pattern: /^$|^[^\s@]+@[^\s@]+\.[^\s@]+$/, message: '邮箱格式不正确', trigger: 'blur' }
  ],
  密码: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码至少6位', trigger: 'blur' }
  ],
  角色: [{ required: true, message: '请选择角色', trigger: 'change' }]
}

function handleAdd() {
  isEdit.value = false
  editId.value = null
  form.用户名 = ''
  form.真实姓名 = ''
  form.邮箱 = ''
  form.手机号 = ''
  form.密码 = ''
  form.部门ID = null
  form.角色 = 'student'
  dialogVisible.value = true
}

function handleEdit(row) {
  isEdit.value = true
  editId.value = row.ID
  form.用户名 = row.用户名
  form.真实姓名 = row.真实姓名
  form.邮箱 = row.邮箱 || ''
  form.手机号 = row.手机号 || ''
  form.密码 = ''
  form.部门ID = row.部门ID
  form.角色 = row.角色
  dialogVisible.value = true
}

function handleDelete(row) {
  const action = row.是否激活 ? '停用' : '启用'
  const msg = row.是否激活
    ? `确定要停用员工"${row.真实姓名}"吗？停用后该账号无法登录`
    : `确定要重新启用员工"${row.真实姓名}"吗？`

  ElMessageBox.confirm(msg, '提示', { type: 'warning' })
    .then(async () => {
      try {
        if (row.是否激活) {
          await deleteUser(row.ID)
          ElMessage.success('已停用')
        } else {
          await updateUser(row.ID, { 是否激活: true })
          ElMessage.success('已启用')
        }
        fetchUsers()
      } catch (e) {
        // 错误已在拦截器中处理
      }
    })
    .catch(() => {})
}

async function handleSubmit() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  submitting.value = true
  try {
    if (isEdit.value) {
      const data = {
        真实姓名: form.真实姓名,
        邮箱: form.邮箱 || null,
        手机号: form.手机号 || null,
        角色: form.角色,
        部门ID: form.部门ID || null,
      }
      await updateUser(editId.value, data)
      ElMessage.success('编辑成功')
    } else {
      const data = {
        用户名: form.用户名,
        真实姓名: form.真实姓名,
        密码: form.密码,
        邮箱: form.邮箱 || null,
        手机号: form.手机号 || null,
        角色: form.角色,
        部门ID: form.部门ID || null,
      }
      await createUser(data)
      ElMessage.success('新增成功')
    }
    dialogVisible.value = false
    fetchUsers()
  } catch (e) {
    // 错误已在拦截器中处理
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  fetchDepartments()
  fetchUsers()
})
</script>

<style scoped>
.users {
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
  color: var(--text-primary);
  margin: 0;
}
.header-actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}
.pagination-wrap {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}
</style>
