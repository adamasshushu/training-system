<template>
  <router-view />
</template>

<style>
/* Global Element Plus overrides using design tokens */
html {
  transition: background var(--transition-slow);
}

/* Button */
.el-button--primary {
  --el-button-bg-color: var(--brand-500);
  --el-button-border-color: var(--brand-500);
  --el-button-hover-bg-color: var(--brand-600);
  --el-button-hover-border-color: var(--brand-600);
  --el-button-active-bg-color: var(--brand-700);
  --el-button-active-border-color: var(--brand-700);
}
.el-button--primary.is-plain {
  --el-button-plain-bg-color: var(--brand-50);
  --el-button-plain-border-color: var(--brand-200);
  --el-button-plain-hover-bg-color: var(--brand-500);
  --el-button-plain-hover-border-color: var(--brand-500);
}
html.dark .el-button--primary.is-plain {
  --el-button-plain-bg-color: rgba(108, 92, 231, 0.1);
  --el-button-plain-border-color: rgba(108, 92, 231, 0.3);
}

/* Tag */
.el-tag--primary {
  --el-tag-primary-bg-color: var(--brand-50);
  --el-tag-primary-border-color: var(--brand-200);
  --el-tag-primary-color: var(--brand-500);
}
html.dark .el-tag--primary {
  --el-tag-primary-bg-color: rgba(108, 92, 231, 0.15);
  --el-tag-primary-border-color: rgba(108, 92, 231, 0.3);
  --el-tag-primary-color: var(--brand-300);
}
.el-tag--success {
  --el-tag-success-bg-color: var(--success-light);
  --el-tag-success-color: #059669;
}
html.dark .el-tag--success {
  --el-tag-success-bg-color: rgba(16, 185, 129, 0.15);
  --el-tag-success-color: #34d399;
}
.el-tag--warning {
  --el-tag-warning-bg-color: var(--warning-light);
  --el-tag-warning-color: #d97706;
}
html.dark .el-tag--warning {
  --el-tag-warning-bg-color: rgba(245, 158, 11, 0.15);
  --el-tag-warning-color: #fbbf24;
}
.el-tag--danger {
  --el-tag-danger-bg-color: var(--danger-light);
  --el-tag-danger-color: #dc2626;
}
html.dark .el-tag--danger {
  --el-tag-danger-bg-color: rgba(239, 68, 68, 0.15);
  --el-tag-danger-color: #f87171;
}

/* Card */
.el-card {
  border-radius: var(--radius-lg) !important;
  border: 1px solid var(--border-card) !important;
  background: var(--bg-card) !important;
  transition: background var(--transition-slow), border-color var(--transition-slow), box-shadow var(--transition-slow);
}
.el-card__header {
  border-bottom: 1px solid var(--border-card) !important;
  padding: var(--space-4) var(--space-5) !important;
}
.el-card__body {
  padding: var(--space-5) !important;
}

/* Table */
.el-table {
  --el-table-bg-color: var(--bg-card);
  --el-table-tr-bg-color: var(--bg-card);
  --el-table-header-bg-color: var(--bg-hover);
  --el-table-row-hover-bg-color: var(--bg-hover);
  --el-table-border-color: var(--border-default);
  --el-table-text-color: var(--text-primary);
  --el-table-header-text-color: var(--text-secondary);
  font-size: var(--text-base);
}
html.dark .el-table {
  --el-table-bg-color: var(--bg-card);
  --el-table-tr-bg-color: var(--bg-card);
  --el-table-header-bg-color: var(--bg-hover);
  --el-table-row-hover-bg-color: var(--bg-hover);
  --el-table-border-color: var(--border-default);
  --el-table-text-color: var(--text-primary);
  --el-table-header-text-color: var(--text-secondary);
}
.el-table th.el-table__cell {
  font-weight: var(--weight-semibold);
}

/* Input */
.el-input__wrapper {
  border-radius: var(--radius-md) !important;
  box-shadow: 0 0 0 1px var(--border-default) inset !important;
  background: var(--bg-input) !important;
  transition: box-shadow var(--transition-fast), background var(--transition-slow);
}
.el-input__wrapper:hover {
  box-shadow: 0 0 0 1px var(--border-hover) inset !important;
}
.el-input__wrapper.is-focus {
  box-shadow: 0 0 0 1px var(--border-focus) inset, 0 0 0 3px rgba(108, 92, 231, 0.1) !important;
}
.el-input__inner {
  color: var(--text-primary) !important;
}
.el-input__inner::placeholder {
  color: var(--text-tertiary) !important;
}
html.dark .el-input__wrapper {
  background: var(--bg-input) !important;
}
html.dark .el-input__inner {
  color: var(--text-primary) !important;
}

/* Select */
.el-select-dropdown {
  --el-select-dropdown-bg-color: var(--bg-elevated);
  border: 1px solid var(--border-default) !important;
  border-radius: var(--radius-md) !important;
  box-shadow: var(--shadow-lg) !important;
}
html.dark .el-select-dropdown__item {
  color: var(--text-primary);
}
.el-select-dropdown__item.hover {
  background: var(--bg-hover) !important;
}

/* Dialog / Modal */
.el-overlay {
  background: var(--bg-overlay) !important;
}
.el-dialog {
  --el-dialog-bg-color: var(--bg-elevated);
  border-radius: var(--radius-xl) !important;
  box-shadow: var(--shadow-modal) !important;
}
html.dark .el-dialog {
  --el-dialog-bg-color: var(--bg-elevated);
}

/* Menu (sidebar) */
.el-menu {
  border-right: none !important;
}

/* Pagination */
.el-pagination {
  --el-pagination-button-bg-color: var(--bg-surface);
  --el-pagination-hover-color: var(--brand-500);
}
html.dark .el-pagination {
  --el-pagination-button-bg-color: var(--bg-surface);
}

/* Empty */
html.dark .el-empty__description {
  color: var(--text-secondary);
}

/* Message / Notification */
.el-message {
  border-radius: var(--radius-md) !important;
  box-shadow: var(--shadow-lg) !important;
}
html.dark .el-message {
  background: var(--bg-elevated) !important;
  border-color: var(--border-default) !important;
}
html.dark .el-message .el-message__content {
  color: var(--text-primary) !important;
}

/* Loading */
html.dark .el-loading-mask {
  background: rgba(15, 15, 17, 0.6) !important;
}

/* Divider */
html.dark .el-divider {
  --el-divider-border-color: var(--border-default);
}

/* Collapse */
html.dark .el-collapse {
  --el-collapse-header-bg-color: var(--bg-card);
  --el-collapse-content-bg-color: var(--bg-card);
  border-color: var(--border-default);
}

/* Tabs */
html.dark .el-tabs__item {
  color: var(--text-secondary);
}
html.dark .el-tabs__item.is-active {
  color: var(--brand-300);
}
html.dark .el-tabs__active-bar {
  background: var(--brand-400);
}

/* Drawer */
html.dark .el-drawer {
  background: var(--bg-elevated) !important;
}

/* Descriptions */
html.dark .el-descriptions__title {
  color: var(--text-primary);
}
html.dark .el-descriptions__label {
  color: var(--text-secondary);
}
html.dark .el-descriptions__content {
  color: var(--text-primary);
}
</style>
