<template>
  <div class="category-tags">
    <el-tag
      :type="active === '' ? 'primary' : 'plain'"
      class="category-tag"
      @click="$emit('update:active', '')"
    >全部</el-tag>
    <el-tag
      v-for="item in items"
      :key="item.key || item"
      :type="(active === (item.key || item)) ? 'primary' : 'plain'"
      class="category-tag"
      @click="$emit('update:active', item.key || item)"
    >{{ item.label || item }}</el-tag>
  </div>
</template>

<script setup>
defineProps({
  items: { type: Array, required: true },
  active: { type: [String, Number], default: '' }
})
defineEmits(['update:active'])
</script>

<style scoped>
.category-tags {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
  margin-bottom: var(--space-5);
}
.category-tag {
  cursor: pointer;
  padding: 0 var(--space-3);
  height: 30px;
  line-height: 28px;
  border-radius: var(--radius-full);
  transition: all var(--transition-fast);
}
.category-tag:active {
  transform: scale(0.95);
}
</style>