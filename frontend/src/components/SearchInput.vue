<template>
  <el-input
    v-model="model"
    :placeholder="placeholder"
    clearable
    :prefix-icon="Search"
    class="search-input"
    size="large"
    @clear="$emit('clear')"
  />
</template>

<script setup>
import { Search } from '@element-plus/icons-vue'
import { computed } from 'vue'

const props = defineProps({
  modelValue: { type: String, default: '' },
  placeholder: { type: String, default: '搜索...' }
})
const emit = defineEmits(['update:modelValue', 'clear'])
const model = computed({
  get: () => props.modelValue,
  set: (v) => emit('update:modelValue', v)
})
</script>

<style scoped>
.search-input {
  max-width: 320px;
}
.search-input :deep(.el-input__wrapper) {
  border-radius: var(--radius-md) !important;
}
</style>