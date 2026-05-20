<template>
  <div class="login-container">
    <!-- Animated background orbs -->
    <div class="bg-orb bg-orb-1"></div>
    <div class="bg-orb bg-orb-2"></div>
    <div class="bg-orb bg-orb-3"></div>

    <!-- Floating particles grid -->
    <div class="particles">
      <div v-for="i in 20" :key="i" class="particle" :style="particleStyle(i)"></div>
    </div>

    <!-- Brand badge top-right -->
    <div class="brand-badge">
      <span class="badge-dot"></span>
      v2.2
    </div>

    <!-- Main login card -->
    <div class="login-card">
      <div class="login-header">
        <div class="logo">
          <img v-if="branding.logo_url" :src="branding.logo_url" class="logo-img" />
          <div v-else class="logo-icon">
            <svg width="56" height="56" viewBox="0 0 48 48" fill="none">
              <rect width="48" height="48" rx="14" fill="url(#logo-grad)" />
              <path d="M14 30V18l10-6 10 6v12l-10 6-10-6z" stroke="white" stroke-width="2" fill="rgba(255,255,255,0.15)"/>
              <circle cx="24" cy="22" r="3" fill="white" opacity="0.9"/>
              <path d="M24 28v6m-3-3h6" stroke="white" stroke-width="2" stroke-linecap="round"/>
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
            <span v-if="!loading" class="btn-text">登 录</span>
          </el-button>
        </el-form-item>

        <div class="login-footer">
          <span class="hint-text">演示账号：admin / admin123</span>
        </div>
      </el-form>
    </div>

    <!-- Footer -->
    <div class="login-footer-bar">
      <span>培训管理系统</span>
      <span class="footer-dot">·</span>
      <span>企业内部培训平台</span>
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
    // 默认值
  }
}

// Random particle positions (computed once)
const particleStyle = (i) => {
  const seed = i * 37
  return {
    left: `${(seed * 7.3) % 100}%`,
    top: `${(seed * 11.7) % 100}%`,
    width: `${(seed % 3 + 2)}px`,
    height: `${(seed % 3 + 2)}px`,
    animationDelay: `${(seed % 10) * 0.5}s`,
    animationDuration: `${(seed % 8) + 6}s`,
    opacity: 0.15 + (seed % 5) * 0.04
  }
}

const handleLogin = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  loading.value = true
  try {
    const res = await login(loginForm)
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
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #0f0f1a 0%, #1a1240 30%, #2a2166 60%, #6C5CE7 100%);
  position: relative;
  overflow: hidden;
  animation: fadeIn 0.6s ease-out;
}

/* ===== Animated background orbs ===== */
.bg-orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  pointer-events: none;
  animation: orbFloat 20s ease-in-out infinite;
}
.bg-orb-1 {
  width: 500px;
  height: 500px;
  background: rgba(108, 92, 231, 0.2);
  top: -10%;
  left: -5%;
  animation-delay: 0s;
}
.bg-orb-2 {
  width: 400px;
  height: 400px;
  background: rgba(162, 155, 254, 0.15);
  bottom: -15%;
  right: -8%;
  animation-delay: -7s;
}
.bg-orb-3 {
  width: 300px;
  height: 300px;
  background: rgba(124, 58, 237, 0.12);
  top: 40%;
  right: 15%;
  animation-delay: -14s;
}

@keyframes orbFloat {
  0%, 100% { transform: translate(0, 0) scale(1); }
  25% { transform: translate(30px, -40px) scale(1.1); }
  50% { transform: translate(-20px, 20px) scale(0.95); }
  75% { transform: translate(40px, 30px) scale(1.05); }
}

/* ===== Floating particles ===== */
.particles {
  position: absolute;
  inset: 0;
  pointer-events: none;
}
.particle {
  position: absolute;
  background: rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  animation: particleFloat linear infinite;
}
@keyframes particleFloat {
  0% { transform: translateY(0) scale(1); opacity: 0; }
  10% { opacity: 0.6; }
  90% { opacity: 0.6; }
  100% { transform: translateY(-100vh) scale(0.5); opacity: 0; }
}

/* ===== Brand badge ===== */
.brand-badge {
  position: absolute;
  top: 24px;
  right: 24px;
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 12px;
  background: rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: var(--radius-full);
  color: rgba(255, 255, 255, 0.6);
  font-size: 12px;
  font-weight: 500;
}
.badge-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #10b981;
  animation: pulse 2s ease-in-out infinite;
}

/* ===== Login card ===== */
.login-card {
  width: 420px;
  padding: 40px 36px;
  background: rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(24px);
  -webkit-backdrop-filter: blur(24px);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: var(--radius-xl);
  box-shadow: 0 25px 60px rgba(0, 0, 0, 0.3),
    inset 0 1px 0 rgba(255, 255, 255, 0.1);
  position: relative;
  z-index: 1;
  animation: fadeInUp 0.6s ease-out;
}

.login-header {
  text-align: center;
  margin-bottom: 32px;
}

.logo {
  margin-bottom: 20px;
  display: flex;
  justify-content: center;
  animation: fadeInScale 0.5s ease-out;
}

.logo-img {
  width: 64px;
  height: 64px;
  object-fit: contain;
  border-radius: var(--radius-lg);
}

.logo-icon {
  width: 64px;
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: center;
  filter: drop-shadow(0 4px 12px rgba(108, 92, 231, 0.3));
}

.login-title {
  font-size: 26px;
  font-weight: 700;
  background: linear-gradient(135deg, #ffffff, rgba(255, 255, 255, 0.85));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 8px;
  letter-spacing: -0.3px;
}

.login-subtitle {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.5);
  font-weight: 400;
}

.login-form {
  margin-top: 4px;
}

/* Override input styles for glassmorphism */
.login-form :deep(.el-input__wrapper) {
  background: rgba(255, 255, 255, 0.06) !important;
  box-shadow: 0 0 0 1px rgba(255, 255, 255, 0.1) inset !important;
  border-radius: 10px !important;
  height: 48px;
  transition: all 0.2s ease;
}
.login-form :deep(.el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px rgba(255, 255, 255, 0.2) inset !important;
  background: rgba(255, 255, 255, 0.08) !important;
}
.login-form :deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 1px var(--brand-400) inset, 0 0 0 3px rgba(108, 92, 231, 0.2) !important;
  background: rgba(255, 255, 255, 0.08) !important;
}
.login-form :deep(.el-input__inner) {
  color: #ffffff !important;
  font-size: 15px;
}
.login-form :deep(.el-input__inner::placeholder) {
  color: rgba(255, 255, 255, 0.35) !important;
}
.login-form :deep(.el-input__prefix) {
  color: rgba(255, 255, 255, 0.35) !important;
}
.login-form :deep(.el-input__suffix) {
  color: rgba(255, 255, 255, 0.35) !important;
}

/* Form item spacing */
.login-form :deep(.el-form-item) {
  margin-bottom: 24px;
}

.login-btn {
  width: 100%;
  height: 48px;
  font-size: 16px;
  font-weight: 600;
  border-radius: 10px;
  letter-spacing: 2px;
  background: linear-gradient(135deg, var(--brand-500), var(--brand-400)) !important;
  border: none !important;
  transition: all 0.2s ease;
  box-shadow: 0 4px 16px rgba(108, 92, 231, 0.3);
}
.login-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 6px 24px rgba(108, 92, 231, 0.4);
}
.login-btn:active {
  transform: translateY(0);
}
.login-btn :deep(.el-button__loading) {
  color: #fff !important;
}
.login-btn :deep(.el-icon-loading) {
  color: #fff;
}

.btn-text {
  color: #ffffff;
}

.login-footer {
  text-align: center;
  margin-top: -8px;
}

.hint-text {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.3);
}

/* ===== Footer bar ===== */
.login-footer-bar {
  position: absolute;
  bottom: 24px;
  display: flex;
  align-items: center;
  gap: 8px;
  color: rgba(255, 255, 255, 0.25);
  font-size: 13px;
  z-index: 1;
}
.footer-dot {
  opacity: 0.5;
}

/* ===== Dark mode overrides (login is always dark-themed) ===== */
@media (prefers-color-scheme: light) {
  .login-container {
    background: linear-gradient(135deg, #0f0f1a 0%, #1a1240 30%, #2a2166 60%, #6C5CE7 100%);
  }
}

/* ===== Responsive ===== */
@media (max-width: 480px) {
  .login-card {
    width: calc(100% - 32px);
    padding: 32px 24px;
    margin: 0 16px;
  }
  .login-title {
    font-size: 22px;
  }
  .brand-badge {
    top: 16px;
    right: 16px;
  }
}

/* ===== Accessibility ===== */
@media (prefers-reduced-motion: reduce) {
  .bg-orb,
  .particle,
  .login-card,
  .login-container,
  .logo,
  .badge-dot {
    animation: none !important;
  }
}
</style>
