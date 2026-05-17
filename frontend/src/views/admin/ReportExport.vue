<template>
  <div class="report-export">
    <el-card class="page-card">
      <h2 style="margin: 0 0 20px; font-size: 18px">📄 学习报告导出</h2>
      <p class="page-desc">导出Excel格式的学习报告，包含概览统计、学员进度、课程进度三个工作表</p>

      <el-alert title="提示" type="info" :closable="false" style="margin-bottom: 20px">
        报告将包含全部学员和课程的进度数据，建议非高峰期导出
      </el-alert>

      <el-button type="primary" size="large" :icon="Download" @click="exportReport" :loading="exporting">
        {{ exporting ? '生成中...' : '一键导出报告 (Excel)' }}
      </el-button>

      <div v-if="exporting" class="export-hint">
        <el-progress :percentage="99" :stroke-width="8" striped striped-flow style="max-width: 400px; margin-top: 16px" />
        <p>正在生成报告...</p>
      </div>
    </el-card>

    <el-card class="page-card" style="margin-top: 16px">
      <h2 style="margin: 0 0 16px; font-size: 18px">📊 知识图谱（管理端）</h2>
      <p class="page-desc">查看培训内容自动构建的知识关联网络</p>
      <el-button type="primary" @click="$router.push('/admin/knowledge-graph')" :icon="Connection">
        查看知识图谱
      </el-button>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { Download, Connection } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { getToken } from '@/utils/auth'

const exporting = ref(false)

const exportReport = async () => {
  exporting.value = true
  try {
    const token = getToken()
    const res = await fetch('/api/reports/export?type=overview', {
      headers: { Authorization: `Bearer ${token}` },
    })
    if (!res.ok) throw new Error('导出失败')

    const blob = await res.blob()
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `培训报告_${new Date().toISOString().slice(0, 10)}.xlsx`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
    ElMessage.success('报告已下载')
  } catch (e) {
    ElMessage.error('导出失败')
  } finally {
    exporting.value = false
  }
}
</script>

<style scoped>
.report-export { max-width: 800px; margin: 0 auto; }
.page-desc { font-size: 13px; color: #909399; margin: -12px 0 20px; }
.export-hint { margin-top: 16px; }
.export-hint p { font-size: 13px; color: #909399; margin: 8px 0 0; }
</style>
