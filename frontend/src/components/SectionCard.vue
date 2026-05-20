<template>
  <el-card shadow="never" class="section-card" :class="{ 'card-hover': hoverable }">
    <template v-if="title || $slots.header" #header>
      <div class="section-card-header">
        <div class="section-card-title-wrap">
          <span v-if="icon" class="section-card-icon">{{ icon }}</span>
          <span class="section-card-title">{{ title }}</span>
          <el-tag v-if="tag" size="small" :type="tagType" class="section-card-tag">{{ tag }}</el-tag>
        </div>
        <div v-if="$slots.extra" class="section-card-extra">
          <slot name="extra" />
        </div>
      </div>
    </template>
    <slot />
  </el-card>
</template>

<script setup>
defineProps({
  title: { type: String, default: '' },
  icon: { type: String, default: '' },
  tag: { type: String, default: '' },
  tagType: { type: String, default: 'primary' },
  hoverable: { type: Boolean, default: false }
})
</script>

<style scoped>
.section-card {
  border-radius: var(--radius-lg) !important;
  margin-bottom: var(--space-6);
  background: var(--bg-card);
  transition: box-shadow var(--transition-base), transform var(--transition-base);
}
.section-card.card-hover:hover {
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}
.section-card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.section-card-title-wrap {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}
.section-card-icon {
  font-size: 18px;
  line-height: 1;
}
.section-card-title {
  font-size: var(--text-md);
  font-weight: var(--weight-semibold);
  color: var(--text-primary);
}
.section-card-tag {
  margin-left: var(--space-2);
}
</style>