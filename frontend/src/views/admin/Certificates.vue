<template>
  <div class="certs-page">
    <AdminTable
      :data="list"
      :loading="loading"
      :show-pagination="false"
      :columns="columns"
      :actions-width="0"
    >
      <template #page-header>
        <div class="page-header">
          <h2 class="page-title">证书管理</h2>
          <el-button type="primary" @click="issueDialog=true"><el-icon><Plus /></el-icon>发放证书</el-button>
        </div>
      </template>
    </AdminTable>

    <el-dialog v-model="issueDialog" title="发放证书" width="450px" destroy-on-close>
      <el-form ref="formRef" :model="form" :rules="rules" label-width="80px">
        <el-form-item label="用户" prop="用户ID">
          <el-select v-model="form.用户ID" filterable placeholder="选择用户" style="width:100%">
            <el-option v-for="u in users" :key="u.ID" :label="u.真实姓名+' ('+u.角色+')'" :value="u.ID" />
          </el-select>
        </el-form-item>
        <el-form-item label="模板">
          <el-select v-model="form.模板ID" clearable placeholder="选择模板" style="width:100%">
            <el-option v-for="t in templates" :key="t.ID" :label="t.名称" :value="t.ID" />
          </el-select>
        </el-form-item>
        <el-form-item label="证书编号">
          <el-input v-model="form.证书编号" placeholder="留空自动生成" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="issueDialog=false">取消</el-button>
        <el-button type="primary" @click="handleIssue" :loading="issuing">确认发放</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { Plus } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { getCertificates, issueCertificate, getTemplates } from '@/api/certificates'
import request from '@/api/index'
import AdminTable from '@/components/AdminTable.vue'

const loading = ref(false); const list = ref([])
const issueDialog = ref(false); const issuing = ref(false)
const formRef = ref(null)
const users = ref([]); const templates = ref([])

const form = reactive({ 用户ID:null, 模板ID:null, 证书编号:'' })
const rules = { 用户ID:[{required:true,message:'请选择用户',trigger:'change'}] }

const columns = [
  { prop: '证书编号', label: '证书编号', width: 160 },
  { prop: '持证人姓名', label: '持证人', width: 100 },
  { prop: '用户姓名', label: '系统用户', width: 100 },
  { prop: '模板名称', label: '模板', minWidth: 140 },
  { prop: '发放时间', label: '发放时间', width: 170 },
]

const loadData = async () => {
  loading.value = true
  try { const r = await getCertificates(); list.value = r.数据||[] } catch {} finally { loading.value = false }
}

const handleIssue = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  issuing.value = true
  try {
    await issueCertificate(form)
    ElMessage.success('证书已发放'); issueDialog.value = false; loadData()
  } catch {} finally { issuing.value = false }
}

onMounted(async () => {
  loadData()
  try {
    const [ur, tr] = await Promise.all([
      request.get('/users?page_size=100'), getTemplates()
    ])
    users.value = ur.数据||[]; templates.value = tr.数据||[]
  } catch {}
})
</script>

<style scoped>
.certs-page { max-width:1200px }
.page-header { display:flex; align-items:center; justify-content:space-between; margin-bottom:20px }
.page-title { font-size:22px; font-weight:600; color:var(--text-primary) }
</style>
