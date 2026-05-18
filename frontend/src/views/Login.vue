<template>
  <div class="login-container">
    <div class="login-card">
      <div class="login-header">
        <div class="logo">
          <img v-if="branding.logo_url" :src="branding.logo_url" class="logo-img" />
          <div v-else class="logo-icon">
            <svg width="48" height="48" viewBox="0 0 48 48" fill="none">
              <rect width="48" height="48" rx="12" fill="url(#logo-grad)" />
              <path d="M14 30V18l10-6 10 6v12l-10 6-10-6z" stroke="white" stroke-width="2" fill="rgba(255,255,255,0.15)"/>
              <path d="M24 22v8m-4-4h8" stroke="white" stroke-width="2" stroke-linecap="round"/>
              <defs>
                <linearGradient id="logo-grad" x1="0" y1="0" x2="48" y2="48">
                  <stop stop-color="#6C5CE7"/>
                  <stop offset="1" stop-color="#a29bfe"/>
                </linearGradient>
              </defs>
            </svg>
          </div>
        </div>
        <h2 class="login-title">{{ branding.system_name }}</h2>
        <p class="login-subtitle">{{ branding.login_tagline }}</p>
      </div>

      <el-form
        ref="formRef"
        :model="loginForm"
        :rules="loginRules"
        class="login-form"
        size="large"
        @keyup.enter="handleLogin"
      >
        <el-form-item prop="username">
          <el-input
            v-model="loginForm.username"
            placeholder="请输入用户名"
            :prefix-icon="User"
          />
        </el-form-item>

        <el-form-item prop="password">
          <el-input
            v-model="loginForm.password"
            type="password"
            placeholder="请输入密码"
            :prefix-icon="Lock"
            show-password
          />
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            :loading="loading"
            class="login-btn"
            @click="handleLogin"
          >
            {{ loading ? '登录中...' : '登 录' }}
          </el-button>
        </el-form-item>

        <div class="login-footer">
          <span class="hint-text">演示账号：admin / admin123</span>
        </div>
      </el-form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { User, Lock } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { login } from '@/api/auth'
import { setToken, setUser } from '@/utils/auth'
import axios from 'axios'

const router = useRouter()
const formRef = ref(null)
const loading = ref(false)

const loginForm = reactive({
  username: '',
  password: ''
})

const loginRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码至少6位', trigger: 'blur' }
  ]
}

// 品牌配置（动态从后端加载）
const branding = reactive({
  logo_url: '',
  system_name: '培训管理系统',
  login_tagline: '企业内部培训管理平台'
})

const loadBranding = async () => {
  try {
    const res = await axios.get('/api/system/branding/public')
    const data = res.data.数据 || {}
    branding.logo_url = data.Logo地址 || ''
    branding.system_name = data.系统名称 || '培训管理系统'
    branding.login_tagline = data.登录页标语 || '企业内部培训管理平台'
  } catch {
    // 使用默认值
  }
}

const handleLogin = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  loading.value = true
  try {
    const res = await login(loginForm)
    // Clear any stale data first
    localStorage.removeItem('training-system-user')
    setToken(res.access_token)
    if (res.用户信息) {
      setUser(res.用户信息)
    }
    ElMessage.success('登录成功')

    const role = res.用户信息?.角色
    const redirect = role === 'admin' || role === 'teacher'
      ? '/admin/dashboard'
      : '/student/dashboard'
    router.push(redirect)
  } catch (err) {
    ElMessage.error(err.response?.data?.message || '登录失败，请检查用户名和密码')
  } finally {
    loading.value = false
  }
}

onMounted(loadBranding)
</script>

<style scoped>
.login-container {
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #1a1a2e 0%, #2a2166 40%, #6C5CE7 100%);
  position: relative;
  overflow: hidden;
}

.login-container::before {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle at 30% 50%, rgba(108,92,231,0.15) 0%, transparent 50%),
              radial-gradient(circle at 70% 30%, rgba(162,155,254,0.1) 0%, transparent 40%);
  pointer-events: none;
}

.login-card {
  width: 420px;
  padding: 40px;
  background: rgba(255, 255, 255, 0.98);
  border-radius: 16px;
  box-shadow: 0 25px 60px rgba(0, 0, 0, 0.25);
  position: relative;
  backdrop-filter: blur(20px);
}

.login-header {
  text-align: center;
  margin-bottom: 32px;
}

.logo {
  margin-bottom: 16px;
  display: flex;
  justify-content: center;
}

.logo-img {
  max-width: 80px;
  max-height: 80px;
}

.logo-icon {
  width: 56px;
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.login-title {
  font-size: 24px;
  font-weight: 700;
  color: #1a1a2e;
  margin-bottom: 8px;
  letter-spacing: -0.3px;
}

.login-subtitle {
  font-size: 14px;
  color: #909399;
}

.login-form {
  margin-top: 8px;
}

.login-btn {
  width: 100%;
  height: 44px;
  font-size: 16px;
  font-weight: 600;
  border-radius: 10px;
}

.login-footer {
  text-align: center;
}

.hint-text {
  font-size: 12px;
  color: #c0c4cc;
}
</style>
