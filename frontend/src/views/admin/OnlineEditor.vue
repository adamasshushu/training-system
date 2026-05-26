<template>
  <div class="online-editor">
    <el-card class="page-card">
      <div class="page-header">
        <h2>✏️ 在线编辑</h2>
        <div class="header-actions">
          <el-button type="primary" @click="saveContent" :loading="saving">
            <el-icon style="margin-right: 4px"><Upload /></el-icon>保存文档
          </el-button>
        </div>
      </div>

      <el-form label-position="top">
        <el-form-item label="文档标题">
          <el-input v-model="title" placeholder="输入文档标题" size="large" />
        </el-form-item>

        <el-form-item label="编辑模式">
          <el-radio-group v-model="mode">
            <el-radio value="markdown">Markdown</el-radio>
            <el-radio value="html">HTML</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>

      <!-- 编辑器 -->
      <div class="editor-area">
        <div class="editor-pane">
          <div class="pane-header">编辑区</div>
          <el-input
            v-model="content"
            :type="'textarea'"
            :rows="20"
            :placeholder="mode === 'markdown' ? '# 在这里写Markdown...' : '<!-- 在这里写HTML... -->'"
            class="code-editor"
          />
        </div>

        <div class="preview-pane">
          <div class="pane-header">预览区</div>
          <div class="preview-box">
            <div v-if="mode === 'markdown'" class="markdown-preview" v-html="renderedMarkdown"></div>
            <iframe v-else :srcdoc="content" class="html-preview" />
          </div>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { Upload } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { getToken } from '@/utils/auth'
import axios from 'axios'
import DOMPurify from 'dompurify'

const API = axios.create({ baseURL: '' })
API.interceptors.request.use((config) => {
  config.headers.Authorization = `Bearer ${getToken()}`
  return config
})

const title = ref('')
const content = ref('')
const mode = ref('markdown')
const saving = ref(false)

// Simple markdown -> HTML rendering (client-side)
const renderedMarkdown = computed(() => {
  if (!content.value) return '<p style="color:#999">等待输入...</p>'
  let html = content.value
    // Headers
    .replace(/^### (.+)$/gm, '<h3>$1</h3>')
    .replace(/^## (.+)$/gm, '<h2>$1</h2>')
    .replace(/^# (.+)$/gm, '<h1>$1</h1>')
    // Bold & italic
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.+?)\*/g, '<em>$1</em>')
    // Code blocks
    .replace(/```(\w*)\n([\s\S]*?)```/g, '<pre><code>$2</code></pre>')
    .replace(/`(.+?)`/g, '<code>$1</code>')
    // Links
    .replace(/\[(.+?)\]\((.+?)\)/g, '<a href="$2" target="_blank">$1</a>')
    // Images
    .replace(/!\[(.+?)\]\((.+?)\)/g, '<img src="$2" alt="$1" style="max-width:100%"/>')
    // Horizontal rule
    .replace(/^---$/gm, '<hr/>')
    // Unordered lists
    .replace(/^- (.+)$/gm, '<li>$1</li>')
    // Paragraphs
    .split('\n\n').map(p => {
      if (p.trim().startsWith('<')) return p
      if (p.trim().startsWith('<li>')) return `<ul>${p}</ul>`
      return `<p>${p.replace(/\n/g, '<br/>')}</p>`
    }).join('\n')
  return DOMPurify.sanitize(html)
})

const saveContent = async () => {
  if (!title.value.trim()) {
    ElMessage.warning('请输入文档标题')
    return
  }
  if (!content.value.trim()) {
    ElMessage.warning('请输入文档内容')
    return
  }

  saving.value = true
  try {
    // Create a Blob and upload via the upload API
    const ext = mode.value === 'markdown' ? 'md' : 'html'
    const mime = mode.value === 'markdown' ? 'text/markdown' : 'text/html'
    const filename = `${title.value}.${ext}`
    const blob = new Blob([content.value], { type: mime })
    const file = new File([blob], filename, { type: mime })

    const formData = new FormData()
    formData.append('file', file)
    formData.append('subdir', 'documents')

    const res = await API.post('/api/uploads', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })

    ElMessage.success(`文档已保存: ${filename}`)
  } catch (e) {
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.online-editor {
  max-width: 1200px;
  margin: 0 auto;
}
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}
.page-header h2 {
  margin: 0;
  font-size: 18px;
  color: #303133;
}
.editor-area {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin-top: 16px;
}
.editor-pane, .preview-pane {
  border: 1px solid #dcdfe6;
  border-radius: 8px;
  overflow: hidden;
}
.pane-header {
  padding: 8px 12px;
  background: var(--bg-page);
  font-size: 13px;
  color: #909399;
  border-bottom: 1px solid #dcdfe6;
}
.code-editor textarea {
  font-family: 'Menlo', 'Monaco', monospace !important;
  font-size: 14px;
  line-height: 1.6;
}
.preview-box {
  padding: 16px;
  min-height: 500px;
  overflow-y: auto;
}
.markdown-preview {
  line-height: 1.8;
  color: #303133;
}
.markdown-preview h1, .markdown-preview h2, .markdown-preview h3 {
  margin: 16px 0 8px;
}
.markdown-preview pre {
  background: var(--bg-page);
  padding: 12px;
  border-radius: 6px;
  overflow-x: auto;
}
.markdown-preview code {
  background: var(--bg-page);
  padding: 2px 6px;
  border-radius: 3px;
  font-size: 13px;
}
.markdown-preview img {
  max-width: 100%;
}
.html-preview {
  width: 100%;
  height: 500px;
  border: none;
}
@media (max-width: 900px) {
  .editor-area {
    grid-template-columns: 1fr;
  }
}
</style>
