<template>
  <div class="admin-table-wrapper">
    <!-- Search & Filter Bar -->
    <div v-if="showSearch || showFilter || $slots.search || $slots.filter" class="admin-table-toolbar">
      <div class="toolbar-left">
        <el-input
          v-if="showSearch"
          v-model="searchModel"
          :placeholder="searchPlaceholder"
          clearable
          :prefix-icon="SearchIcon"
          class="table-search"
          @clear="onSearchClear"
          @keyup.enter="onSearch"
        />
        <slot v-if="$slots.filter" name="filter" />
        <slot v-if="$slots.search" name="search" />
      </div>
      <div v-if="$slots.actions" class="toolbar-right">
        <slot name="actions" />
      </div>
    </div>

    <!-- Extra top content -->
    <slot name="top" />

    <!-- Table -->
    <el-card shadow="never" class="table-card">
      <el-table
        ref="tableRef"
        :data="data"
        border
        stripe
        v-loading="loading"
        :style="tableStyle"
        :max-height="maxHeight"
        :default-sort="defaultSort"
        :row-key="rowKey"
        @selection-change="onSelectionChange"
        @sort-change="onSortChange"
      >
        <!-- Selection column -->
        <el-table-column
          v-if="selectable"
          type="selection"
          :width="selectionWidth"
          :reserve-selection="reserveSelection"
        />

        <!-- Index column -->
        <el-table-column
          v-if="showIndex"
          type="index"
          :label="indexLabel"
          :width="indexWidth"
          :index="indexFormatter || indexMethod"
        />

        <!-- Dynamic columns -->
        <el-table-column
          v-for="col in columns"
          :key="col.prop || col.label"
          :prop="col.prop"
          :label="col.label"
          :width="col.width"
          :min-width="col.minWidth"
          :align="col.align || 'left'"
          :fixed="col.fixed"
          :sortable="col.sortable"
          :show-overflow-tooltip="col.ellipsis !== false"
          :formatter="col.formatter"
        >
          <template v-if="col.slot || col.template" #default="{ row, column, $index }">
            <slot :name="col.slot || `column-${col.prop}`" :row="row" :column="column" :index="$index" />
          </template>
        </el-table-column>

        <!-- Actions column -->
        <el-table-column
          v-if="$slots.actions || $slots['action-row']"
          :label="actionsLabel"
          :width="actionsWidth"
          :fixed="actionsFixed"
          align="center"
        >
          <template #default="{ row, $index }">
            <slot name="actions" :row="row" :index="$index" />
            <slot name="action-row" :row="row" :index="$index" />
          </template>
        </el-table-column>

        <!-- Default fallback slot for custom columns -->
        <slot name="default" />

      </el-table>

      <!-- Pagination -->
      <div v-if="showPagination && total > 0" class="pagination-wrapper">
        <el-pagination
          v-model:current-page="pageModel"
          v-model:page-size="pageSizeModel"
          :total="total"
          :page-sizes="pageSizes"
          :layout="paginationLayout"
          :small="paginationSmall"
          :disabled="paginationDisabled"
          :hide-on-single-page="hideOnSinglePage"
          :background="paginationBackground"
          @size-change="onSizeChange"
          @current-change="onCurrentChange"
        />
      </div>
    </el-card>

    <!-- Extra bottom content -->
    <slot name="bottom" />
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { Search as SearchIcon } from '@element-plus/icons-vue'

const props = defineProps({
  // Data
  data: { type: Array, default: () => [] },
  total: { type: Number, default: 0 },
  loading: { type: Boolean, default: false },

  // Column configuration
  columns: { type: Array, default: () => [] },
  showIndex: { type: Boolean, default: true },
  indexLabel: { type: String, default: '#' },
  indexWidth: { type: Number, default: 55 },
  indexFormatter: { type: Function, default: null },

  // Selection
  selectable: { type: Boolean, default: false },
  selectionWidth: { type: Number, default: 40 },
  reserveSelection: { type: Boolean, default: false },

  // Actions column
  actionsLabel: { type: String, default: '操作' },
  actionsWidth: { type: Number, default: 200 },
  actionsFixed: { type: [Boolean, String], default: 'right' },

  // Search
  showSearch: { type: Boolean, default: false },
  showFilter: { type: Boolean, default: false },
  searchPlaceholder: { type: String, default: '搜索...' },

  // Pagination
  showPagination: { type: Boolean, default: true },
  pageSizes: { type: Array, default: () => [10, 20, 50] },
  paginationLayout: { type: String, default: 'total, sizes, prev, pager, next' },
  paginationSmall: { type: Boolean, default: false },
  paginationDisabled: { type: Boolean, default: false },
  hideOnSinglePage: { type: Boolean, default: false },
  paginationBackground: { type: Boolean, default: false },

  // v-model
  modelValue: { type: Number, default: 1 },
  pageSize: { type: Number, default: 10 },

  // Table options
  maxHeight: { type: [Number, String], default: null },
  defaultSort: { type: Object, default: null },
  rowKey: { type: String, default: null },
  tableStyle: { type: [Object, String], default: () => ({ width: '100%' }) },
})

const emit = defineEmits([
  'update:modelValue',
  'update:pageSize',
  'search',
  'search-clear',
  'selection-change',
  'sort-change',
  'size-change',
  'current-change',
])

const tableRef = ref(null)
const searchModel = ref('')
const pageModel = computed({
  get: () => props.modelValue,
  set: (v) => emit('update:modelValue', v),
})
const pageSizeModel = computed({
  get: () => props.pageSize,
  set: (v) => emit('update:pageSize', v),
})

const indexMethod = (idx) => (pageModel.value - 1) * pageSizeModel.value + idx + 1

const onSearch = () => emit('search', searchModel.value)
const onSearchClear = () => {
  searchModel.value = ''
  emit('search-clear')
  emit('search', '')
}
const onSelectionChange = (rows) => emit('selection-change', rows)
const onSortChange = (sort) => emit('sort-change', sort)
const onSizeChange = (size) => {
  pageModel.value = 1
  emit('size-change', size)
}
const onCurrentChange = (page) => emit('current-change', page)

// Expose for parent access
defineExpose({ tableRef })
</script>

<style scoped>
.admin-table-wrapper {
  max-width: 1200px;
}

.admin-table-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--space-4);
  flex-wrap: wrap;
  gap: var(--space-3);
}

.toolbar-left {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  flex-wrap: wrap;
  flex: 1;
}

.toolbar-right {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.table-search {
  width: 240px;
}

.table-card {
  margin-bottom: 0;
}

.pagination-wrapper {
  margin-top: var(--space-5);
  display: flex;
  justify-content: flex-end;
}

:deep(.el-button + .el-button) {
  margin-left: 6px;
}
</style>
