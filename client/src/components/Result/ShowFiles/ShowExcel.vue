<script lang="ts" setup>
import { ref, computed } from 'vue'
import Pagination from '@/components/Pagination/Pagination.vue'

// 格式化单元格值
const formatCellValue = (cell: any): string => {
  if (cell === null || cell === undefined) {
    return '-';
  }
  
  // 检查是否为数字并是否为无穷大
  if (typeof cell === 'number') {
    if (!isFinite(cell)) {
      return cell > 0 ? 'INFINITY' : '-INFINITY';
    }
    return String(cell);
  }
  
  // 其他情况直接转为字符串
  return String(cell);
};

const props = defineProps<{
  sheets: Array<{ name: string; data: any[] }>
}>()

// 为每个工作表维护独立的分页状态
const currentPageMap = ref<Record<string, number>>({})

const getPaginatedSheetData = (sheet: { name: string; data: any[] }) => {
  const currentPage = currentPageMap.value[sheet.name] || 1
  const rowsPerPage = 100
  const totalRows = sheet.data.length
  
  const totalPages = Math.ceil(totalRows / rowsPerPage)
  const start = (currentPage - 1) * rowsPerPage
  const end = start + rowsPerPage
  const paginatedData = sheet.data.slice(start, end)
  
  return {
    data: paginatedData,
    currentPage,
    totalPages
  }
}

const updatePage = (sheetName: string, page: number) => {
  currentPageMap.value[sheetName] = page
}
</script>

<template>
  <div class="excel-view">
    <div v-for="(sheet, index) in sheets" :key="index" class="excel-sheet">
      <h3 class="sheet-title">{{ sheet.name }}</h3>
      <div v-if="sheet.data && sheet.data.length > 0" class="excel-table-wrapper">
        <div class="excel-table-container">
          <table class="excel-table">
            <thead>
              <tr>
                <th class="index-column">
                  <div class="column-header">
                    <span class="column-name">行号</span>
                  </div>
                </th>
                <th v-for="(header, colIndex) in sheet.data[0]" :key="colIndex" class="excel-column">
                  <div class="column-header">
                    <span class="column-name">{{ header }}</span>
                  </div>
                </th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(row, rowIndex) in getPaginatedSheetData(sheet).data.slice(1)" 
                  :key="(getPaginatedSheetData(sheet).currentPage - 1) * 100 + rowIndex" 
                  class="excel-row">
                <td class="index-column">
                  <div class="index-content">
                    <span class="index-value">{{ (getPaginatedSheetData(sheet).currentPage - 1) * 100 + rowIndex + 1 }}</span>
                  </div>
                </td>
                <td v-for="(cell, colIndex) in row" :key="colIndex" class="excel-column">
                  <div class="cell-content">
                    {{ formatCellValue(cell) }}
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
      <div v-else class="excel-empty">
        工作表为空
      </div>
      
      <!-- 使用统一的分页组件 -->
      <Pagination 
        v-if="getPaginatedSheetData(sheet).totalPages > 1"
        :current-page="getPaginatedSheetData(sheet).currentPage"
        :total-pages="getPaginatedSheetData(sheet).totalPages"
        @update:currentPage="(page) => updatePage(sheet.name, page)"
        class="excel-pagination"
      />
    </div>
  </div>
</template>

<style scoped lang="scss">
@use '../../../common/global.scss' as *;
.excel-view {
  flex: 1;
  overflow: auto;
  background: white;
  border-radius: 10px;
  padding: 12px;
  @include controller-style;
}

.excel-sheet {
  margin-bottom: 24px;
}

.excel-sheet:last-child {
  margin-bottom: 0;
}

.sheet-title {
  font-size: 18px;
  font-weight: 500;
  color: #303133;
  margin: 0 0 16px 0;
  padding-bottom: 8px;
  border-bottom: 1px solid #ebeef5;
}

.excel-table-wrapper {
  overflow: auto;
  max-height: 100%;
}

.excel-table-container {
  min-width: 100%;
}

.excel-table {
  width: 100%;
  border-collapse: collapse;
  table-layout: fixed;
}

.excel-column {
  border-bottom: 1px solid #ebeef5;
  padding: 0;
}

.index-column {
  width: 60px;
  border-bottom: 1px solid #ebeef5;
  padding: 0;
  background-color: #fafafa;
}

.column-header {
  padding: 12px 10px;
  text-align: center; /* 修改为居中 */
  font-weight: 500;
  color: #606266;
  background-color: #f5f7fa;
  position: sticky;
  top: 0;
  z-index: 2;
}

.column-name {
  display: block;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.excel-row:hover {
  background-color: #f5f7fa;
}

.cell-content {
  padding: 12px 10px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  text-align: center; /* 添加居中 */
}

.index-content {
  padding: 12px 10px;
  text-align: center;
  color: #909399;
}

.index-value {
  display: block;
}

.excel-empty {
  text-align: center;
  padding: 40px 20px;
  color: #909399;
}

.excel-pagination {
  margin: 12px 0 0 0;
  padding: 12px 0 0 0;
  border-top: 1px solid #ebeef5;
}
</style>