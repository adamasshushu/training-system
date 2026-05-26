<template>
  <div class="ad-user-center">
    <!-- 左侧: OU 树 -->
    <div class="left-panel glass-card">
      <div class="panel-header">
        <h3>📁 AD 组织结构</h3>
        <el-button text size="small" @click="fetchOuTree" :loading="ouLoading" class="glass-btn">
          <el-icon><Refresh /></el-icon>
        </el-button>
      </div>
      <div class="ou-tree" v-loading="ouLoading">
        <el-tree
          :data="ouTree"
          :props="{ children: '子部门', label: '名称' }"
          node-key="识别名"
          :expand-on-click-node="true"
          highlight-current
          @node-click="onOuClick"
          v-if="ouTree.length > 0"
        >
          <template #default="{ data }">
            <span class="ou-node">
              <span>{{ data.名称 }}</span>
              <el-tag size="small" type="info" effect="plain">{{ data.用户数 || 0 }}</el-tag>
            </span>
          </template>
        </el-tree>
        <el-empty v-else-if="!ouLoading" description="暂无 OU 数据" :image-size="60" />
      </div>
    </div>

    <!-- 右侧: 用户列表 -->
    <div class="right-panel glass-card">
      <!-- 搜索栏 -->
      <div class="search-bar">
        <el-input
          v-model="keyword"
          placeholder="搜索 AD 用户（用户名/显示名/邮箱）"
          clearable
          @clear="searchUsers"
          @keyup.enter="searchUsers"
          :prefix-icon="Search"
          class="glass-input"
          style="width: 380px"
        />
        <el-tag v-if="selectedOu" closable @close="clearOuFilter" type="warning" effect="dark" class="glass-tag">
          {{ selectedOu.名称 }}
        </el-tag>
        <el-button type="primary" @click="searchUsers" class="glass-btn-primary">
          <el-icon><Search /></el-icon>搜索
        </el-button>
        <el-button @click="handleSync" class="glass-btn-accent" style="margin-left: auto">
          <el-icon><Refresh /></el-icon>同步到本地
        </el-button>
      </div>

      <!-- 用户列表 -->
      <el-table
        :data="userList"
        v-loading="userLoading"
        stripe
        style="width: 100%; margin-top: 12px; flex: 1"
        @row-click="showUserDetail"
        highlight-current-row
        max-height="calc(100vh - 280px)"
        class="glass-table"
      >
        <el-table-column prop="用户名" label="用户名" min-width="130" />
        <el-table-column prop="显示名" label="显示名" min-width="120" />
        <el-table-column prop="邮箱" label="邮箱" min-width="180" />
        <el-table-column prop="部门" label="AD部门" min-width="130" />
        <el-table-column prop="职务" label="职务" min-width="100" />
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.启用 ? 'success' : 'danger'" size="small" effect="dark">
              {{ row.启用 ? '启用' : '禁用' }}
            </el-tag>
            <el-tag v-if="row.已锁定" type="warning" size="small" effect="dark" style="margin-left: 4px">锁定</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100" fixed="right">
          <template #default="{ row }">
            <el-button text size="small" type="primary" @click.stop="showUserDetail(row)">详情</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div class="result-count" v-if="userList.length > 0">
        共 {{ userList.length }} 个 AD 用户
      </div>
    </div>

    <!-- 用户详情抽屉 ★ 只读 -->
    <el-drawer
      v-model="drawerVisible"
      :title="`用户详情: ${userDetail.显示名 || ''}`"
      size="480px"
      direction="rtl"
      class="glass-drawer"
    >
      <template v-if="detailLoading">
        <el-skeleton :rows="10" animated />
      </template>
      <template v-else-if="userDetail.用户名">
        <!-- 基本信息 -->
        <el-descriptions title="基本信息" :column="2" border size="small" class="detail-section glass-desc">
          <el-descriptions-item label="用户名">{{ userDetail.用户名 }}</el-descriptions-item>
          <el-descriptions-item label="显示名">{{ userDetail.显示名 }}</el-descriptions-item>
          <el-descriptions-item label="姓">{{ userDetail.姓 || '-' }}</el-descriptions-item>
          <el-descriptions-item label="名">{{ userDetail.名 || '-' }}</el-descriptions-item>
          <el-descriptions-item label="UPN">{{ userDetail.UPN || '-' }}</el-descriptions-item>
          <el-descriptions-item label="邮箱">{{ userDetail.电子邮件 || '-' }}</el-descriptions-item>
          <el-descriptions-item label="描述" :span="2">{{ userDetail.描述 || '-' }}</el-descriptions-item>
        </el-descriptions>

        <!-- 组织 -->
        <el-descriptions title="组织" :column="2" border size="small" class="detail-section glass-desc">
          <el-descriptions-item label="职务">{{ userDetail.职务 || '-' }}</el-descriptions-item>
          <el-descriptions-item label="部门">{{ userDetail.部门 || '-' }}</el-descriptions-item>
          <el-descriptions-item label="公司">{{ userDetail.公司 || '-' }}</el-descriptions-item>
          <el-descriptions-item label="办公室">{{ userDetail.办公室 || '-' }}</el-descriptions-item>
          <el-descriptions-item label="电话">{{ userDetail.电话号码 || '-' }}</el-descriptions-item>
          <el-descriptions-item label="手机">{{ userDetail.手机 || '-' }}</el-descriptions-item>
        </el-descriptions>

        <!-- 账户状态 -->
        <el-descriptions title="账户" :column="2" border size="small" class="detail-section glass-desc">
          <el-descriptions-item label="状态">
            <el-tag :type="userDetail.启用 ? 'success' : 'danger'" size="small" effect="dark">
              {{ userDetail.启用 ? '启用' : '禁用' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="锁定">
            <el-tag :type="userDetail.已锁定 ? 'warning' : 'info'" size="small" effect="dark">
              {{ userDetail.已锁定 ? '已锁定' : '正常' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="密码永不过期">{{ userDetail.密码永不过期 ? '是' : '否' }}</el-descriptions-item>
          <el-descriptions-item label="不能改密码">{{ userDetail.不能更改密码 ? '是' : '否' }}</el-descriptions-item>
          <el-descriptions-item label="创建时间" :span="2">{{ userDetail.创建时间 || '-' }}</el-descriptions-item>
          <el-descriptions-item label="DN" :span="2">
            <span class="dn-text">{{ userDetail.识别名 }}</span>
          </el-descriptions-item>
        </el-descriptions>

        <!-- 注：只读浏览，不允许修改 AD 用户 -->
        <el-alert
          type="info"
          :closable="false"
          show-icon
          style="margin-top: 20px"
          title="AD 用户为只读浏览，修改请前往 AD 域控管理平台"
        />
      </template>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { Search, Refresh } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import request from '@/api/index'

const ouTree = ref([])
const ouLoading = ref(false)
const selectedOu = ref(null)

const userList = ref([])
const userLoading = ref(false)
const keyword = ref('')

const drawerVisible = ref(false)
const detailLoading = ref(false)
const userDetail = reactive({})

// ── OU 树 ──

async function fetchOuTree() {
  ouLoading.value = true
  try {
    const res = await request.get('/ldap/ous')
    ouTree.value = res.数据 || []
  } catch {
    ouTree.value = []
  } finally {
    ouLoading.value = false
  }
}

function onOuClick(data) {
  selectedOu.value = data
  searchUsers()
}

function clearOuFilter() {
  selectedOu.value = null
  searchUsers()
}

// ── 用户搜索 ──

async function searchUsers() {
  userLoading.value = true
  try {
    const params = { keyword: keyword.value.trim() }
    if (selectedOu.value) params.ou_dn = selectedOu.value.识别名
    const res = await request.get('/ldap/users', { params })
    userList.value = res.数据 || []
  } catch {
    userList.value = []
  } finally {
    userLoading.value = false
  }
}

// ── 用户详情 (只读) ──

async function showUserDetail(row) {
  drawerVisible.value = true
  detailLoading.value = true
  Object.assign(userDetail, {})
  try {
    const res = await request.get('/ldap/users/detail', { params: { dn: row.识别名 } })
    Object.assign(userDetail, res.数据 || {})
  } catch {
    ElMessage.error('获取详情失败')
  } finally {
    detailLoading.value = false
  }
}

// ── 同步 ──

async function handleSync() {
  try {
    await request.post('/enterprise/sync', { platform: 'ldap' })
    ElMessage.success('同步完成')
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '同步失败')
  }
}

onMounted(() => {
  fetchOuTree()
  searchUsers()
})
</script>

<style scoped>
/* ═══════════ 毛玻璃主题 ═══════════ */

.ad-user-center {
  display: flex;
  gap: 16px;
  height: calc(100vh - 120px);
  max-width: 1400px;
}

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

/* 暗色模式 */
:global(.dark) .glass-card {
  background: rgba(20, 20, 35, 0.6);
  border-color: rgba(255, 255, 255, 0.08);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
}

/* ── 左侧面板 ── */

.left-panel {
  width: 280px;
  min-width: 240px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 16px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
  flex-shrink: 0;
}

:global(.dark) .panel-header {
  border-bottom-color: rgba(255, 255, 255, 0.06);
}

.panel-header h3 {
  margin: 0;
  font-size: 15px;
  font-weight: 600;
}

.ou-tree {
  flex: 1;
  overflow-y: auto;
  padding: 10px 8px;
}

.ou-node {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex: 1;
  padding-right: 8px;
  font-size: 13px;
}

/* ── 右侧面板 ── */

.right-panel {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  padding: 16px;
}

.search-bar {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-shrink: 0;
}

.glass-input :deep(.el-input__wrapper) {
  background: rgba(255, 255, 255, 0.5) !important;
  backdrop-filter: blur(8px);
  border-radius: 12px !important;
  border: 1px solid rgba(255, 255, 255, 0.3);
  transition: all 0.3s ease;
}

.glass-input :deep(.el-input__wrapper:hover) {
  border-color: var(--brand-400, #6C5CE7);
}

.glass-input :deep(.el-input__wrapper.is-focus) {
  border-color: var(--brand-500, #6C5CE7);
  box-shadow: 0 0 0 1px var(--brand-400, #a29bfe) inset;
}

.glass-btn-primary {
  border-radius: 12px !important;
  background: linear-gradient(135deg, #6C5CE7, #a29bfe) !important;
  border: none !important;
  transition: all 0.3s ease;
}

.glass-btn-primary:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 16px rgba(108, 92, 231, 0.3);
}

.glass-btn-accent {
  border-radius: 12px !important;
  background: rgba(255, 255, 255, 0.4) !important;
  backdrop-filter: blur(8px);
  border: 1px solid rgba(108, 92, 231, 0.2) !important;
  color: #6C5CE7 !important;
  transition: all 0.3s ease;
}

.glass-btn-accent:hover {
  background: rgba(108, 92, 231, 0.1) !important;
  border-color: #6C5CE7 !important;
}

.glass-btn {
  color: var(--text-secondary) !important;
  border-radius: 10px !important;
}

.glass-btn:hover {
  background: rgba(108, 92, 231, 0.08) !important;
  color: #6C5CE7 !important;
}

.glass-tag {
  backdrop-filter: blur(8px);
  border-radius: 10px !important;
}

/* ── 表格 ── */

.glass-table :deep(.el-table__inner-wrapper) {
  border-radius: 12px;
  overflow: hidden;
}

.glass-table :deep(.el-table) {
  background: transparent !important;
}

.glass-table :deep(.el-table th) {
  background: rgba(108, 92, 231, 0.06) !important;
  border-bottom: 2px solid rgba(108, 92, 231, 0.12) !important;
  font-weight: 600;
}

.glass-table :deep(.el-table tr) {
  transition: all 0.2s ease;
}

.glass-table :deep(.el-table tbody tr:hover > td) {
  background: rgba(108, 92, 231, 0.04) !important;
}

.result-count {
  padding: 8px 0;
  color: var(--text-tertiary);
  font-size: 13px;
}

/* ── 详情 ── */

.detail-section {
  margin-bottom: 20px;
}

.glass-desc :deep(.el-descriptions__body) {
  border-radius: 12px;
  overflow: hidden;
}

.glass-desc :deep(.el-descriptions__label) {
  background: rgba(108, 92, 231, 0.04) !important;
}

.dn-text {
  font-size: 12px;
  word-break: break-all;
  color: var(--text-tertiary);
}

/* ── 响应式 ── */

@media (max-width: 768px) {
  .ad-user-center {
    flex-direction: column;
    height: auto;
  }
  .left-panel {
    width: 100%;
    max-height: 300px;
  }
}
</style>
