<template>
  <div class="templates-page">
    <div class="page-header">
      <h2 class="page-title">证书模板</h2>
      <el-button type="primary" @click="handleAdd"><el-icon><Plus /></el-icon>新建模板</el-button>
    </div>

    <el-card shadow="never">
      <el-table :data="list" border stripe v-loading="loading">
        <el-table-column type="index" label="#" width="55" />
        <el-table-column prop="名称" label="模板名称" min-width="200" />
        <el-table-column prop="背景图" label="背景图" min-width="200" show-overflow-tooltip />
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.是否激活?'success':'info'" size="small">{{ row.是否激活?'启用':'停用' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="160">
          <template #default="{ row }">
            <el-button text size="small" type="primary" @click="handleEdit(row)">编辑</el-button>
            <el-button text size="small" type="danger" @click="handleDelete(row)" v-if="row.是否激活">停用</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialogVisible" :title="isEdit?'编辑模板':'新建模板'" width="500px" destroy-on-close>
      <el-form ref="formRef" :model="form" :rules="rules" label-width="80px">
        <el-form-item label="模板名称" prop="名称">
          <el-input v-model="form.名称" placeholder="如：毕业证书" />
        </el-form-item>
        <el-form-item label="背景图URL" prop="背景图">
          <el-input v-model="form.背景图" placeholder="http://..." />
        </el-form-item>
        <el-form-item label="样式配置">
          <el-input v-model="form.样式配置" type="textarea" :rows="3" placeholder='{"font":"24px sans-serif","color":"#333"}' />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible=false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { Plus } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getTemplates, createTemplate, updateTemplate, deleteTemplate } from '@/api/certificates'

const loading = ref(false); const list = ref([])
const dialogVisible = ref(false); const isEdit = ref(false)
const submitting = ref(false); const formRef = ref(null); const editId = ref(null)
const form = reactive({ 名称:'', 背景图:'', 样式配置:'' })
const rules = { 名称:[{required:true,message:'请输入名称',trigger:'blur'}] }

const loadData = async () => {
  loading.value = true
  try { const r = await getTemplates(); list.value = r.数据||[] } catch {} finally { loading.value = false }
}

const handleAdd = () => {
  isEdit.value = false; editId.value = null
  form.名称 = ''; form.背景图 = ''; form.样式配置 = ''
  dialogVisible.value = true
}

const handleEdit = (row) => {
  isEdit.value = true; editId.value = row.ID
  form.名称 = row.名称; form.背景图 = row.背景图||''; form.样式配置 = row.样式配置||''
  dialogVisible.value = true
}

const handleSubmit = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  submitting.value = true
  try {
    if (isEdit.value) { await updateTemplate(editId.value, form); ElMessage.success('已更新') }
    else { await createTemplate(form); ElMessage.success('已创建') }
    dialogVisible.value = false; loadData()
  } catch {} finally { submitting.value = false }
}

const handleDelete = (row) => {
  ElMessageBox.confirm('确定停用该模板？','提示',{type:'warning'})
    .then(async () => { await deleteTemplate(row.ID); ElMessage.success('已停用'); loadData() }).catch(()=>{})
}

onMounted(() => loadData())
</script>

<style scoped>
.templates-page { max-width:1200px }
.page-header { display:flex; align-items:center; justify-content:space-between; margin-bottom:20px }
.page-title { font-size:22px; font-weight:600; color:#303133 }
</style>
