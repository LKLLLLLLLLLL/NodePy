<script lang="ts" setup>
defineProps<{
  sheets: Array<{ name: string; data: any[] }>
}>()
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
                    <span class="column-name">序号</span>
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
              <tr v-for="(row, rowIndex) in sheet.data.slice(1)" :key="rowIndex" class="excel-row">
                <td class="index-column">
                  <div class="index-content">
                    <span class="index-value">{{ rowIndex + 1 }}</span>
                  </div>
                </td>
                <td v-for="(cell, colIndex) in row" :key="colIndex" class="excel-column">
                  <div class="cell-content">
                    {{ cell || '-' }}
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
    </div>
  </div>
</template>

<style scoped>
.excel-view {
  flex: 1;
  overflow: auto;
  background: white;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  padding: 12px;
  margin: 12px;
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
  text-align: left;
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
</style>