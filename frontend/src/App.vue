<template>
  <router-view />
</template>

<style>
:root {
  --sidebar-bg: #1a1a2e;
  --sidebar-hover: #16213e;
  --sidebar-active: #2a2166;
  --sidebar-text: #a0aec0;
  --sidebar-accent: #6C5CE7;
  --sidebar-active-text: #e2e8f0;
  --brand: #6C5CE7;
  --brand-light: #eef0ff;
  --brand-gradient: linear-gradient(135deg, #6C5CE7, #a29bfe);
  --brand-dark: #5e6ad2;
  --success: #10b981;
  --warning: #f59e0b;
  --danger: #ef4444;
  --card-border: #e2e8f0;
  --card-radius: 12px;
  --bg-page: #f0f2f5;
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body, #app {
  height: 100%;
  width: 100%;
  font-family: 'Inter', 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB',
    'Microsoft YaHei', '微软雅黑', Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

/* Element Plus overrides for brand color */
.el-button--primary {
  --el-button-bg-color: #6C5CE7;
  --el-button-border-color: #6C5CE7;
  --el-button-hover-bg-color: #5a4bd1;
  --el-button-hover-border-color: #5a4bd1;
  --el-button-active-bg-color: #4e3fbe;
  --el-button-active-border-color: #4e3fbe;
}

.el-button--primary.is-plain {
  --el-button-plain-bg-color: #eef0ff;
  --el-button-plain-border-color: #c4bdf7;
  --el-button-plain-hover-bg-color: #6C5CE7;
  --el-button-plain-hover-border-color: #6C5CE7;
}

.el-tag--primary {
  --el-tag-primary-bg-color: #eef0ff;
  --el-tag-primary-border-color: #c4bdf7;
  --el-tag-primary-color: #6C5CE7;
}

.el-select-dropdown__item.selected {
  color: #6C5CE7 !important;
}

.el-menu-item.is-active {
  background-color: var(--sidebar-active) !important;
}

/* Card default styling */
.el-card {
  border-radius: var(--card-radius) !important;
  border: 1px solid var(--card-border) !important;
}

.el-card__header {
  border-bottom: 1px solid var(--card-border) !important;
  padding: 16px 20px !important;
}
</style>
