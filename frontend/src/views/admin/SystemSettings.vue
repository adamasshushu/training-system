<template>
  <div class="system-settings">
    <el-card class="page-card">
      <h2>⚙️ 系统设置</h2>
      <el-tabs v-model="activeTab" class="settings-tabs">
        <!-- 品牌设置 -->
        <el-tab-pane label="品牌设置" name="branding">
          <el-form label-position="top" class="settings-form">
            <el-form-item label="系统Logo">
              <div class="logo-upload">
                <el-upload
                  v-if="!branding.logo_url"
                  :action="uploadUrl"
                  :headers="uploadHeaders"
                  :on-success="handleLogoSuccess"
                  :show-file-list="false"
                  accept="image/*"
                >
                  <el-button type="primary" :icon="Upload">上传Logo</el-button>
                </el-upload>
                <div v-else class="logo-preview">
                  <img :src="branding.logo_url" class="logo-img" />
                  <el-button type="danger" link @click="removeLogo">移除</el-button>
                </div>
              </div>
            </el-form-item>

            <el-form-item label="系统名称">
              <el-input v-model="branding.system_name" placeholder="培训管理系统" size="large" maxlength="100" />
            </el-form-item>

            <el-form-item label="登录页标语">
              <el-input
                v-model="branding.login_tagline"
                placeholder="企业内部培训管理平台"
                size="large"
                type="textarea"
                :rows="2"
                maxlength="500"
              />
            </el-form-item>

            <el-form-item>
              <el-button type="primary" size="large" @click="saveBranding" :loading="savingBranding">
                保存品牌设置
              </el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <!-- 存储配置 -->
        <el-tab-pane label="存储配置" name="storage">
          <el-alert
            title="当前存储模式"
            :type="storageMode === 'local' ? 'info' : 'success'"
            :description="storageMode === 'local' ? '本地存储：文件保存在服务器 uploads 目录' : '对象存储：文件保存在S3兼容对象存储'"
            show-icon
            :closable="false"
            style="margin-bottom: 20px"
          />

          <el-form label-position="top" class="settings-form">
            <el-form-item label="存储模式">
              <el-radio-group v-model="storage.storage_mode">
                <el-radio value="local">本地存储</el-radio>
                <el-radio value="s3">对象存储 (S3/MinIO/OSS/COS)</el-radio>
              </el-radio-group>
            </el-form-item>

            <template v-if="storage.storage_mode === 's3'">
              <el-form-item label="S3 Endpoint">
                <el-input v-model="storage.s3_endpoint" placeholder="https://oss-cn-hangzhou.aliyuncs.com" size="large" />
              </el-form-item>
              <el-row :gutter="16">
                <el-col :span="12">
                  <el-form-item label="Access Key">
                    <el-input v-model="storage.s3_access_key" placeholder="AKID..." size="large" />
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="Secret Key">
                    <el-input v-model="storage.s3_secret_key" type="password" placeholder="..." size="large" show-password />
                  </el-form-item>
                </el-col>
              </el-row>
              <el-row :gutter="16">
                <el-col :span="12">
                  <el-form-item label="Bucket">
                    <el-input v-model="storage.s3_bucket" placeholder="my-bucket" size="large" />
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="公网访问地址（可选）">
                    <el-input v-model="storage.s3_public_url" placeholder="https://cdn.example.com" size="large" />
                  </el-form-item>
                </el-col>
              </el-row>
              <el-form-item label="Region">
                <el-input v-model="storage.s3_region" placeholder="auto / cn-hangzhou" size="large" />
              </el-form-item>
            </template>

            <el-form-item>
              <el-button type="primary" size="large" @click="saveStorage" :loading="savingStorage">
                保存存储配置
              </el-button>
              <el-tag type="warning" style="margin-left: 12px">修改需重启服务后完全生效</el-tag>
            </el-form-item>
          </el-form>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { Upload } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { getToken } from '@/utils/auth'
import axios from 'axios'

const API = axios.create({ baseURL: '' })
API.interceptors.request.use((config) => {
  config.headers.Authorization = `Bearer ${getToken()}`
  return config
})

const activeTab = ref('branding')
const uploadUrl = '/api/uploads'
const uploadHeaders = { Authorization: `Bearer ${getToken()}` }

// 品牌设置
const branding = reactive({
  logo_url: '',
  system_name: '培训管理系统',
  login_tagline: '企业内部培训管理平台'
})
const savingBranding = ref(false)

// 存储配置
const storage = reactive({
  storage_mode: 'local',
  s3_endpoint: '',
  s3_region: '',
  s3_access_key: '',
  s3_secret_key: '',
  s3_bucket: '',
  s3_public_url: ''
})
const storageMode = ref('local')
const savingStorage = ref(false)

// 加载品牌设置
const loadBranding = async () => {
  try {
    const res = await API.get('/api/system/branding')
    const data = res.data.数据 || {}
    branding.logo_url = data.Logo地址 || ''
    branding.system_name = data.系统名称 || '培训管理系统'
    branding.login_tagline = data.登录页标语 || '企业内部培训管理平台'
  } catch { /* silent */ }
}

// 加载存储配置
const loadStorage = async () => {
  try {
    const res = await API.get('/api/system/storage-config')
    const data = res.data.数据 || {}
    storage.storage_mode = data.存储模式 || 'local'
    storage.s3_endpoint = data.S3地址 || ''
    storage.s3_region = data.S3区域 || ''
    storage.s3_bucket = data.S3存储桶 || ''
    storage.s3_public_url = data.S3公网地址 || ''
    storageMode.value = data.存储模式 || 'local'
  } catch { /* silent */ }
}

// Logo上传成功
const handleLogoSuccess = (res) => {
  branding.logo_url = res.文件地址
  ElMessage.success('Logo已上传')
}

const removeLogo = () => {
  branding.logo_url = ''
}

// 保存品牌设置
const saveBranding = async () => {
  savingBranding.value = true
  try {
    await API.put('/api/system/branding', {
      logo_url: branding.logo_url || null,
      system_name: branding.system_name,
      login_tagline: branding.login_tagline
    })
    ElMessage.success('品牌设置已保存')
  } catch {
    ElMessage.error('保存失败')
  } finally {
    savingBranding.value = false
  }
}

// 保存存储配置
const saveStorage = async () => {
  savingStorage.value = true
  try {
    await API.put('/api/system/storage-config', {
      storage_mode: storage.storage_mode,
      s3_endpoint: storage.s3_endpoint || null,
      s3_region: storage.s3_region || null,
      s3_access_key: storage.s3_access_key || null,
      s3_secret_key: storage.s3_secret_key || null,
      s3_bucket: storage.s3_bucket || null,
      s3_public_url: storage.s3_public_url || null
    })
    ElMessage.success('存储配置已保存，重启后完全生效')
    storageMode.value = storage.storage_mode
  } catch {
    ElMessage.error('保存失败')
  } finally {
    savingStorage.value = false
  }
}

onMounted(() => {
  loadBranding()
  loadStorage()
})
</script>

<style scoped>
.system-settings {
  max-width: 900px;
  margin: 0 auto;
}
.page-card h2 {
  margin: 0 0 20px;
  font-size: 18px;
  color: var(--text-primary);
}
.settings-form {
  max-width: 700px;
}
.logo-upload {
  display: flex;
  align-items: center;
  gap: 12px;
}
.logo-preview {
  display: flex;
  align-items: center;
  gap: 12px;
}
.logo-img {
  max-width: 200px;
  max-height: 80px;
  border: 1px solid var(--border-default);
  border-radius: 4px;
  padding: 4px;
}
</style>
