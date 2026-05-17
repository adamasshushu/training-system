<template>
  <div class="login-container">
    <div class="login-card">
      <div class="login-header">
        <div class="logo">
          <img v-if="branding.logo_url" :src="branding.logo_url" class="logo-img" />
          <el-icon v-else :size="36" color="#409EFF"><School /></el-icon>
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
import { User, Lock, School } from '@element-plus/icons-vue'
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
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-card {
  width: 420px;
  padding: 40px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
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

.login-title {
  font-size: 24px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 8px;
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
}

.login-footer {
  text-align: center;
}

.hint-text {
  font-size: 12px;
  color: #c0c4cc;
}
</style>
