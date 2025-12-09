<script lang="ts" setup>
import { computed } from 'vue'
import Pagination from '@/components/Pagination/Pagination.vue'

const props = defineProps<{
  data: string
}>()

// 格式化日期时间显示的函数
const formatDateTime = (dateTimeString: string): string => {
  try {
    // 检查是否为 Datetime 类型的 ISO 格式字符串
    if (!/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}/.test(dateTimeString)) {
      return dateTimeString; // 如果不是日期时间格式，直接返回原始字符串
    }
    
    const date = new Date(dateTimeString);
    // 检查日期是否有效
    if (isNaN(date.getTime())) {
      return dateTimeString; // 如果无效，返回原始字符串
    }

    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    const seconds = String(date.getSeconds()).padStart(2, '0');
    
    return `${year}/${month}/${day} ${hours}:${minutes}:${seconds}`;
  } catch (e) {
    // 如果解析失败，返回原始字符串
    return dateTimeString;
  }
}

// 格式化单元格值
const formatCellValue = (value: string): string => {
  if (value === null || value === undefined || value === '') {
    return '-'
  }
  
  // 尝试将字符串转换为数字并检查是否为无穷大
  const numValue = Number(value);
  if (!isNaN(numValue) && !isFinite(numValue)) {
    return numValue > 0 ? 'INFINITY' : '-INFINITY';
  }
  
  // 尝试格式化日期时间
  return formatDateTime(value)
}

// 解析 CSV 数据为表格
const csvTable = computed(() => {
  if (!props.data) {
    return { headers: [], rows: [] }
  }

  // 处理 CSV 数据，正确解析包含逗号和引号的字段
  const lines = props.data.trim().split('\n')
  if (lines.length === 0) {
    return { headers: [], rows: [] }
  }

  // 更健壮的 CSV 解析函数
  function parseCSVLine(line: string): string[] {
    const result: string[] = []
    let current = ''
    let inQuotes = false
    
    for (let i = 0; i < line.length; i++) {
      const char = line[i]
      
      if (char === '"' && !inQuotes) {
        inQuotes = true
      } else if (char === '"' && inQuotes) {
        // 检查下一个字符是否也是引号（转义引号）
        if (i + 1 < line.length && line[i + 1] === '"') {
          current += '"'
          i++ // 跳过下一个引号
        } else {
          inQuotes = false
        }
      } else if (char === ',' && !inQuotes) {
        result.push(current.trim())
        current = ''
      } else {
        current += char
      }
    }
    
    result.push(current.trim())
    return result
  }

  const headerLine = lines[0]
  if (!headerLine) {
    return { headers: [], rows: [] }
  }

  const headers = parseCSVLine(headerLine)
  const rows = lines.slice(1).map(line => {
    const cells = parseCSVLine(line)
    const row: Record<string, string> = {}
    headers.forEach((header, index) => {
      row[header] = cells[index] || ''
    })
    return row
  })

  return { headers, rows }
})

// 分页相关
const currentPage = defineModel<number>('currentPage', { default: 1 })
const rowsPerPage = 100
const totalPages = computed(() => Math.ceil(csvTable.value.rows.length / rowsPerPage))

const paginatedRows = computed(() => {
  const start = (currentPage.value - 1) * rowsPerPage
  const end = start + rowsPerPage
  return csvTable.value.rows.slice(start, end)
})
</script>

<template>
  <div class="csv-view">
    <div v-if="paginatedRows.length > 0" class="csv-table-wrapper">
      <div class="csv-table-container">
        <table class="result-table">
          <thead>
            <tr>
              <th class='index-column'>
                <div class='column-header'>
                  <span class="column-name">行号</span>
                </div>
              </th>
              <th v-for="header in csvTable.headers" :key="header" class='data-column'>
                <div class='column-header'>
                  <span class="column-name">{{ header }}</span>
                </div>
              </th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(row, rowIndex) in paginatedRows" :key="(currentPage - 1) * rowsPerPage + rowIndex" class='data-row'>
              <td class='index-column'>
                <div class="index-content">
                  <span class="index-value">{{ (currentPage - 1) * rowsPerPage + rowIndex + 1 }}</span>
                </div>
              </td>
              <td v-for="header in csvTable.headers" :key="header" class='data-column'>
                {{ formatCellValue(row[header]!) }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    <div v-else class='table-empty'>
      表格为空（0 行 × {{ csvTable.headers.length }} 列）
    </div>
    
    <!-- 使用统一的分页组件 -->
    <Pagination 
      v-if="totalPages > 1"
      v-model:currentPage="currentPage"
      :total-pages="totalPages"
      class="csv-pagination"
    />
  </div>
</template>

<style scoped lang="scss">
@use '../../../common/global.scss' as *;
.csv-view {
  flex: 1;
  display: flex;
  flex-direction: column;
  height: 100%;
  width: 100%;
  overflow: hidden;
  background: #fafafa;
  border-radius: 10px;
  @include controller-style;
}

.csv-table-wrapper {
  flex: 1;
  overflow: auto;
  border: 1px solid #ebeef5;
  border-radius: 4px;
  margin: 12px;
}

.csv-table-container {
  min-width: 100%;
}

.result-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
  background: #fff;
}

.result-table thead {
  position: sticky;
  top: 0;
  background: #f5f7fa;
  z-index: 1;
}

.result-table th {
  padding: 12px 8px;
  text-align: center;
  border-bottom: 2px solid #ebeef5;
  font-weight: 600;
  color: #303133;
}

.result-table td {
  padding: 10px 8px;
  text-align: center;
  border-bottom: 1px solid #ebeef5;
  color: #606266;
}

.index-column {
  width: 80px;
  min-width: 80px;
  text-align: center;
  background: #fafafa;
  font-weight: 500;
}

.data-column {
  word-break: break-word;
  white-space: normal;
  text-align: center;
}

.column-header {
  display: flex;
  flex-direction: column;
  gap: 4px;
  align-items: center;
}

.column-name {
  font-weight: 600;
  color: #303133;
}

.index-content {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.index-value {
  font-weight: 500;
}

.data-row:hover {
  background-color: #f5f7fa;
}

.table-empty {
  flex: 1;
  display: flex;
  justify-content: center;
  color: #909399;
  font-size: 14px;
  padding: 16px;
  background: #fafafa;
  border: 1px solid #ebeef5;
  border-radius: 4px;
  margin: 12px;
}

.csv-pagination {
  margin: 0 12px 12px 12px;
  padding: 12px 0;
}
</style>