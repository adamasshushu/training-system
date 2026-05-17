<template>
  <div class="admin-feedback">
    <el-card class="page-card">
      <h2 style="margin: 0 0 20px; font-size: 18px">📊 培训反馈管理</h2>

      <el-row :gutter="16" style="margin-bottom: 20px">
        <el-col :span="6">
          <el-card shadow="never" class="stat-small">
            <div class="stat-num">{{ avgContent }}</div>
            <div class="stat-label">平均内容评分</div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card shadow="never" class="stat-small">
            <div class="stat-num">{{ avgSystem }}</div>
            <div class="stat-label">平均系统评分</div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card shadow="never" class="stat-small">
            <div class="stat-num">{{ total }}</div>
            <div class="stat-label">反馈总数</div>
          </el-card>
        </el-col>
      </el-row>

      <el-table :data="feedbackList" v-loading="loading" stripe>
        <el-table-column prop="用户" label="提交人" width="120" />
        <el-table-column label="内容评分" width="120">
          <template #default="{ row }">
            <el-rate :model-value="row.内容评分" disabled show-score :score-template="`${row.内容评分}`" />
          </template>
        </el-table-column>
        <el-table-column label="系统评分" width="120">
          <template #default="{ row }">
            <el-rate :model-value="row.系统评分" disabled show-score :score-template="`${row.系统评分}`" />
          </template>
        </el-table-column>
        <el-table-column prop="建议" label="建议" min-width="300" show-overflow-tooltip />
        <el-table-column prop="创建时间" label="提交时间" width="180" />
      </el-table>

      <el-pagination
        v-if="total > pageSize"
        v-model:current-page="page"
        :page-size="pageSize"
        :total="total"
        layout="prev, pager, next"
        class="pagination"
        @current-change="loadFeedback"
      />
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getToken } from '@/utils/auth'
import axios from 'axios'

const API = axios.create({ baseURL: '' })
API.interceptors.request.use((c) => { c.headers.Authorization = `Bearer ${getToken()}`; return c })

const loading = ref(false)
const feedbackList = ref([])
const total = ref(0)
const avgContent = ref(0)
const avgSystem = ref(0)
const page = ref(1)
const pageSize = ref(20)

const loadFeedback = async () => {
  loading.value = true
  try {
    const res = await API.get('/api/reviews/feedback', { params: { page: page.value, page_size: pageSize.value } })
    feedbackList.value = res.data.数据 || []
    total.value = res.data.共计 || 0
    avgContent.value = res.data.平均内容评分 || 0
    avgSystem.value = res.data.平均系统评分 || 0
  } catch { /* silent */ }
  finally { loading.value = false }
}

onMounted(loadFeedback)
</script>

<style scoped>
.admin-feedback { max-width: 1000px; margin: 0 auto; }
.stat-small { text-align: center; }
.stat-num { font-size: 28px; font-weight: 700; color: #409EFF; }
.stat-label { font-size: 12px; color: #909399; margin-top: 2px; }
.pagination { margin-top: 16px; display: flex; justify-content: center; }
</style>
