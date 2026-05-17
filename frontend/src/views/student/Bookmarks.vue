<template>
  <div class="bookmarks-page">
    <el-card class="page-card">
      <div class="page-header">
        <h2>🔖 我的收藏</h2>
        <el-tag v-if="total > 0" type="info">{{ total }} 门课程</el-tag>
      </div>

      <div v-if="bookmarks.length === 0" class="empty-state">
        <el-empty description="还没有收藏课程，去课程中心看看吧" />
        <el-button type="primary" @click="$router.push('/student/courses')">去课程中心</el-button>
      </div>

      <el-row v-else :gutter="16" class="bookmarks-grid">
        <el-col v-for="b in bookmarks" :key="b.ID" :xs="24" :sm="12" :md="8" :lg="6">
          <el-card shadow="hover" class="bookmark-card" @click="$router.push(`/student/courses/${b.课程ID}`)">
            <div class="bookmark-cover" :style="{ background: coverBg(b.课程标题) }">
              <el-icon :size="32" color="#fff"><Star /></el-icon>
            </div>
            <div class="bookmark-body">
              <h3>{{ b.课程标题 }}</h3>
              <span class="bookmark-time">收藏于 {{ b.收藏时间?.slice(0, 10) }}</span>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <el-pagination
        v-if="total > pageSize"
        v-model:current-page="page"
        :page-size="pageSize"
        :total="total"
        layout="prev, pager, next"
        class="pagination"
        @current-change="loadBookmarks"
      />
    </el-card>

    <el-card class="page-card" style="margin-top: 16px">
      <div class="page-header">
        <h2>📝 我的笔记</h2>
      </div>

      <el-table :data="notes" v-loading="loadingNotes" stripe @row-click="viewNote">
        <el-table-column prop="课程标题" label="课程" min-width="150" />
        <el-table-column prop="课时标题" label="课时" min-width="150" />
        <el-table-column label="内容" min-width="300">
          <template #default="{ row }">{{ row.内容 }}</template>
        </el-table-column>
        <el-table-column prop="更新时间" label="更新时间" width="180" />
        <el-table-column label="操作" width="80">
          <template #default="{ row }">
            <el-button type="danger" link @click.stop="deleteNote(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-empty v-if="notes.length === 0 && !loadingNotes" description="暂无笔记" />
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Star } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getToken } from '@/utils/auth'
import axios from 'axios'

const API = axios.create({ baseURL: '' })
API.interceptors.request.use((c) => { c.headers.Authorization = `Bearer ${getToken()}`; return c })

const bookmarks = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(24)

const notes = ref([])
const loadingNotes = ref(false)

const colors = ['#409EFF','#67C23A','#E6A23C','#F56C6C','#909399','#B37FEB','#36CFC9']
const coverBg = (title) => {
  const idx = (title?.length || 0) % colors.length
  return `linear-gradient(135deg, ${colors[idx]}, ${colors[(idx + 1) % colors.length]})`
}

const loadBookmarks = async () => {
  try {
    const res = await API.get('/api/bookmarks', { params: { page: page.value, page_size: pageSize.value } })
    bookmarks.value = res.data.数据 || []
    total.value = res.data.共计 || 0
  } catch { /* silent */ }
}

const loadNotes = async () => {
  loadingNotes.value = true
  try {
    const res = await API.get('/api/bookmarks/notes', { params: { page_size: 100 } })
    notes.value = res.data.数据 || []
  } catch { /* silent */ }
  finally { loadingNotes.value = false }
}

const deleteNote = async (row) => {
  try {
    await ElMessageBox.confirm('确定删除这条笔记？', '提示', { type: 'warning' })
    await API.delete(`/api/bookmarks/notes/${row.ID}`)
    ElMessage.success('已删除')
    loadNotes()
  } catch { /* cancelled */ }
}

const viewNote = (row) => {
  ElMessageBox.alert(row.内容全文 || row.内容, `${row.课时标题} - 笔记`, { confirmButtonText: '关闭' })
}

onMounted(() => { loadBookmarks(); loadNotes() })
</script>

<style scoped>
.bookmarks-page { max-width: 1200px; margin: 0 auto; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.page-header h2 { margin: 0; font-size: 18px; }
.empty-state { padding: 60px 0; text-align: center; }
.bookmarks-grid { margin: 0 -8px; }
.bookmark-card { cursor: pointer; margin-bottom: 16px; transition: transform 0.2s; }
.bookmark-card:hover { transform: translateY(-2px); }
.bookmark-cover {
  height: 100px; display: flex; align-items: center;
  justify-content: center; border-radius: 8px 8px 0 0;
}
.bookmark-body { padding: 12px 0 0; }
.bookmark-body h3 { margin: 0 0 4px; font-size: 14px; color: #303133; }
.bookmark-time { font-size: 12px; color: #c0c4cc; }
.pagination { margin-top: 16px; display: flex; justify-content: center; }
</style>
