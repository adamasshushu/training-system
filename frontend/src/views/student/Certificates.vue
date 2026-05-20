<template>
  <div class="student-certs">
    <div class="page-header"><h2>我的证书</h2></div>
    <el-empty v-if="list.length===0 && !loading" description="还没有获得证书" />
    <el-row :gutter="20" v-else>
      <el-col :xs="24" :sm="12" :md="8" v-for="c in list" :key="c.ID" style="margin-bottom:20px">
        <el-card shadow="hover" class="cert-card">
          <div class="cert-icon"><el-icon :size="48" color="#E6A23C"><Medal /></el-icon></div>
          <h3>{{ c.模板名称 || '培训证书' }}</h3>
          <p class="cert-number">编号: {{ c.证书编号 }}</p>
          <p class="cert-name">持证人: {{ c.持证人姓名 }}</p>
          <p class="cert-date">发放: {{ c.发放时间 }}</p>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Medal } from '@element-plus/icons-vue'
import { getMyCertificates } from '@/api/certificates'

const loading = ref(false); const list = ref([])

onMounted(async () => {
  loading.value = true
  try { const r = await getMyCertificates(); list.value = r.数据||[] } catch {} finally { loading.value = false }
})
</script>

<style scoped>
.student-certs { max-width:1200px; margin:0 auto; padding:24px }
.page-header { margin-bottom:24px }
.page-header h2 { font-size:24px; font-weight:700; color:var(--text-primary) }
.cert-card { text-align:center; padding:24px; border-radius:12px }
.cert-icon { margin-bottom:12px }
.cert-card h3 { font-size:18px; font-weight:600; color:var(--text-primary); margin-bottom:12px }
.cert-number { font-size:13px; color:var(--text-tertiary); margin-bottom:4px }
.cert-name { font-size:15px; color:var(--text-secondary); margin-bottom:4px }
.cert-date { font-size:12px; color:var(--text-tertiary) }
</style>
