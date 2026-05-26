<template>
  <div class="enterprise-settings">
    <el-card class="page-card">
      <h2 style="margin: 0 0 20px; font-size: 18px">🏢 企业平台对接</h2>
      <p class="page-desc">配置钉钉、飞书、企业微信、LDAP/AD，自动同步组织架构并发送培训通知</p>

      <el-tabs v-model="activeTab" @tab-change="loadConfig">
        <el-tab-pane v-for="p in platforms" :key="p.key" :name="p.key">
          <template #label>
            <span :class="{ 'enabled-tab': configs[p.key]?.启用 }">
              <el-icon v-if="configs[p.key]?.启用" color="var(--success)"><CircleCheck /></el-icon>
              <el-icon v-else color="var(--text-tertiary)"><CircleClose /></el-icon>
              {{ p.label }}
            </span>
          </template>

          <el-form label-position="top" class="config-form">
            <el-form-item>
              <el-switch v-model="configData.is_enabled" active-text="启用" inactive-text="未启用" />
            </el-form-item>

            <template v-for="field in p.fields" :key="field.key">
              <el-form-item :label="field.label" :required="field.required">
                <el-input
                  v-model="configData.config[field.key]"
                  :type="field.secret ? 'password' : 'text'"
                  :placeholder="field.placeholder"
                  :show-password="field.secret"
                  size="large"
                />
              </el-form-item>
            </template>

            <el-form-item>
              <el-button type="primary" size="large" @click="saveConfig(p.key)" :loading="saving">
                保存配置
              </el-button>
              <el-button
                size="large"
                @click="testConnection(p.key)"
                :loading="testing"
                style="margin-left: 12px"
              >
                测试连接
              </el-button>
              <el-button
                size="large"
                @click="syncPlatform(p.key)"
                :loading="syncing"
                :disabled="!configData.is_enabled"
                style="margin-left: 12px"
              >
                立即同步组织架构
              </el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <!-- 同步结果 -->
    <el-dialog v-model="syncResultVisible" title="同步结果" width="500px">
      <el-alert v-if="syncError" type="error" :description="syncError" show-icon />
      <div v-else class="sync-result">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="同步部门">{{ syncStats?.ous_synced || 0 }}</el-descriptions-item>
          <el-descriptions-item label="新增用户">{{ syncStats?.users_added || 0 }}</el-descriptions-item>
          <el-descriptions-item label="更新用户">{{ syncStats?.users_updated || 0 }}</el-descriptions-item>
          <el-descriptions-item label="跳过用户">{{ syncStats?.users_skipped || 0 }}</el-descriptions-item>
        </el-descriptions>
        <el-tag type="success" size="large" style="margin-top: 16px">同步完成 ✅</el-tag>
      </div>
    </el-dialog>

    <!-- 同步历史 -->
    <el-card shadow="never" style="margin-top: 20px" v-if="syncLogs.length > 0">
      <template #header>
        <span style="font-weight: 600">📋 同步历史</span>
        <el-button text size="small" @click="loadSyncLogs" style="float: right">刷新</el-button>
      </template>
      <el-table :data="syncLogs" size="small" stripe>
        <el-table-column prop="时间" label="时间" width="170">
          <template #default="{ row }">{{ row.时间?.slice(0, 19) }}</template>
        </el-table-column>
        <el-table-column prop="平台" label="平台" width="100" />
        <el-table-column label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.状态 === 'success' ? 'success' : 'danger'" size="small">
              {{ row.状态 === 'success' ? '成功' : '失败' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="部门数" label="部门" width="60" />
        <el-table-column prop="新增用户" label="新增" width="60" />
        <el-table-column prop="更新用户" label="更新" width="60" />
        <el-table-column prop="跳过用户" label="跳过" width="60" />
        <el-table-column prop="操作人" label="操作人" width="100" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { CircleCheck, CircleClose } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { getToken } from '@/utils/auth'
import axios from 'axios'

const API = axios.create({ baseURL: '' })
API.interceptors.request.use((c) => { c.headers.Authorization = `Bearer ${getToken()}`; return c })

const activeTab = ref('dingtalk')
const saving = ref(false)
const syncing = ref(false)

const configs = reactive({})
const configData = reactive({ is_enabled: false, config: {} })

const syncResultVisible = ref(false)
const syncStats = ref(null)
const syncError = ref('')
const syncLogs = ref([])

const platforms = [
  {
    key: 'dingtalk', label: '钉钉',
    fields: [
      { key: 'app_key', label: 'AppKey', placeholder: '钉开放平台应用的AppKey', required: true, secret: false },
      { key: 'app_secret', label: 'AppSecret', placeholder: '钉开放平台应用的AppSecret', required: true, secret: true },
      { key: 'agent_id', label: 'AgentId', placeholder: '微应用AgentId', required: true, secret: false },
      { key: 'corp_name', label: '企业名称', placeholder: '企业/组织名称', required: false, secret: false },
    ]
  },
  {
    key: 'feishu', label: '飞书',
    fields: [
      { key: 'app_id', label: 'App ID', placeholder: '飞书开放平台App ID', required: true, secret: false },
      { key: 'app_secret', label: 'App Secret', placeholder: '飞书开放平台App Secret', required: true, secret: true },
    ]
  },
  {
    key: 'wecom', label: '企业微信',
    fields: [
      { key: 'corp_id', label: 'CorpID', placeholder: '企业微信CorpID', required: true, secret: false },
      { key: 'corp_secret', label: 'CorpSecret', placeholder: '企业微信应用的Secret', required: true, secret: true },
      { key: 'agent_id', label: 'AgentId', placeholder: '应用的AgentId', required: true, secret: false },
    ]
  },
  {
    key: 'ldap', label: 'LDAP/AD',
    fields: [
      { key: 'server', label: '服务器地址', placeholder: '192.168.22.222', required: true, secret: false },
      { key: 'port', label: '端口', placeholder: '389', required: false, secret: false },
      { key: 'domain', label: '域名', placeholder: 'cyb-org.cn (自动推导Base DN)', required: false, secret: false },
      { key: 'username', label: '用户名', placeholder: 'Administrator', required: true, secret: false },
      { key: 'password', label: '密码', placeholder: '域管理员密码', required: true, secret: true },
      { key: 'base_dn', label: '搜索Base DN', placeholder: 'DC=cyb-org,DC=cn (留空自动推导)', required: false, secret: false },
    ]
  }
]

const loadConfig = async (platform) => {
  try {
    const res = await API.get(`/api/enterprise/configs/${platform}`)
    const data = res.data.数据 || {}
    configData.is_enabled = data.启用 || false
    configData.config = data.配置 || {}
    configs[platform] = data
  } catch {
    configData.is_enabled = false
    configData.config = {}
  }
}

const saveConfig = async (platform) => {
  saving.value = true
  try {
    // Build clean config object
    const cleanConfig = {}
    const p = platforms.find(x => x.key === platform)
    for (const field of p.fields) {
      if (configData.config[field.key]) {
        cleanConfig[field.key] = configData.config[field.key]
      }
    }
    await API.put(`/api/enterprise/configs/${platform}`, {
      is_enabled: configData.is_enabled,
      config: cleanConfig,
    })
    ElMessage.success('配置已保存')
    await loadAllConfigs()
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '保存失败')
  } finally {
    saving.value = false
  }
}

const syncPlatform = async (platform) => {
  syncing.value = true
  syncResultVisible.value = false
  syncError.value = ''
  syncStats.value = null
  try {
    const res = await API.post('/api/enterprise/sync', { platform })
    syncStats.value = res.data.数据 || {}
    syncResultVisible.value = true
    ElMessage.success('组织架构同步完成')
    loadSyncLogs()  // 刷新日志
  } catch (e) {
    syncError.value = e.response?.data?.detail || '同步失败'
    syncResultVisible.value = true
  } finally {
    syncing.value = false
  }
}

const loadSyncLogs = async () => {
  try {
    const res = await API.get('/api/enterprise/sync-logs?limit=10')
    syncLogs.value = res.data.数据 || []
  } catch { /* silent */ }
}

const loadAllConfigs = async () => {
  try {
    const res = await API.get('/api/enterprise/configs')
    for (const c of res.data.数据 || []) {
      configs[c.平台] = c
    }
  } catch { /* silent */ }
}

onMounted(() => {
  loadAllConfigs()
  loadConfig('dingtalk')
  loadSyncLogs()
})
</script>

<style scoped>
.enterprise-settings { max-width: 900px; margin: 0 auto; }
.page-desc { font-size: 13px; color: var(--text-tertiary); margin: 0 0 20px; }
.config-form { max-width: 700px; }
.enabled-tab { color: var(--success); }
.sync-result { text-align: center; }
</style>
