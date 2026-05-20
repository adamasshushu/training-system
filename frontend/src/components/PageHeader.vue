<template>
  <div class="page-header">
    <div class="page-header-content">
      <div>
        <h2 class="page-header-title">{{ title }}</h2>
        <p v-if="subtitle" class="page-header-subtitle">{{ subtitle }}</p>
      </div>
      <div v-if="$slots.actions" class="page-header-actions">
        <slot name="actions" />
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  title: { type: String, required: true },
  subtitle: { type: String, default: '' }
})
</script>

<style scoped>
.page-header {
  margin-bottom: var(--space-6);
}
.page-header-content {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: var(--space-4);
}
.page-header-title {
  font-size: var(--text-3xl);
  font-weight: var(--weight-bold);
  color: var(--text-primary);
  letter-spacing: -0.5px;
  margin: 0;
}
.page-header-subtitle {
  font-size: var(--text-sm);
  color: var(--text-tertiary);
  margin-top: 4px;
}

@media (max-width: 640px) {
  .page-header-content {
    flex-direction: column;
  }
}
</style>