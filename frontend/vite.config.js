import fs from 'fs'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath } from 'url'

// ============================================
//  端口修改: 改下面的 port 值即可
//  后端地址: 改 proxy target 即可
// ============================================
const BACKEND_PORT = process.env.BACKEND_PORT || '8443'
const FRONTEND_PORT = parseInt(process.env.PORT || '5173')

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  server: {
    host: '0.0.0.0',
    port: FRONTEND_PORT,
    https: {
      cert: fs.readFileSync('./cert.pem'),
      key: fs.readFileSync('./key.pem'),
    },
    proxy: {
      '/api': {
        target: `https://localhost:${BACKEND_PORT}`,
        secure: false,
        changeOrigin: true
      }
    }
  }
})
