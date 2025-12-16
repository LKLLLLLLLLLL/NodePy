<script lang="ts" setup>
import { computed, ref, watch, onMounted, onUnmounted, nextTick } from 'vue'
import Pagination from '@/components/Pagination/Pagination.vue'

const props = defineProps<{
  data: string
}>()

// 添加loading和error状态
const loading = ref(false)
const error = ref<string>('')

// 虚拟滚动相关状态
const tableWrapperRef = ref<HTMLElement | null>(null)
let resizeObserver: ResizeObserver | null = null
const scrollTop = ref(0)
const containerHeight = ref(0)
const containerWidth = ref(0)
const rowHeight = ref(38) // 可调整的行高（px）
const buffer = ref(8) // 前后缓冲行数
// 最小列宽（px），稍微减小以避免过宽（用户要求）
const minColWidth = ref(120)

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

// 虚拟滚动：计算可见区索引范围
const totalRows = computed(() => csvTable.value.rows.length || 0)

const visibleRange = computed(() => {
    const ch = containerHeight.value || 0
    const rh = rowHeight.value
    const visibleCount = Math.ceil(ch / rh)
    const start = Math.max(0, Math.floor((scrollTop.value || 0) / rh) - buffer.value)
    const end = Math.min(totalRows.value, start + visibleCount + buffer.value * 2)
    return { start, end }
})

const visibleIndices = computed(() => {
    const { start, end } = visibleRange.value
    const arr: number[] = []
    for (let i = start; i < end; i++) arr.push(i)
    return arr
})

const topSpacerHeight = computed(() => visibleRange.value.start * rowHeight.value)
const bottomSpacerHeight = computed(() => Math.max(0, (totalRows.value - visibleRange.value.end) * rowHeight.value))

// 横向布局计算：如果所需最小宽度小于容器宽度，则让表格 100% 平分列宽，否则使用 max-content 启用横向滚动
const requiredWidth = computed(() => {
    const colCount = (csvTable.value.headers?.length || 0) + 1 // 包括行号列
    return colCount * minColWidth.value
})

const needHorizontalScroll = computed(() => {
    // 如果容器宽度尚未测量，默认不滚动（防止闪烁）
    if (!containerWidth.value) return false
    return requiredWidth.value > containerWidth.value
})

const tableStyle = computed(() => {
    // Use camelCase property names to satisfy Vue/TS style typing
    // When horizontal scroll is needed, set the table width to the
    // required pixel width so the parent `.table-wrapper` will overflow
    // and show a horizontal scrollbar instead of compressing columns.
    const styleObj: Record<string, any> = {
        ['--min-col-width']: `${minColWidth.value}px`,
        width: needHorizontalScroll.value ? `${requiredWidth.value}px` : '100%'
    }
    // tableLayout must be camelCase when used as CSSProperties
    styleObj.tableLayout = needHorizontalScroll.value ? 'auto' : 'fixed'
    return styleObj as unknown as Record<string, string>
})

const cellCount = computed(() => (csvTable.value.headers?.length || 0) + 1)
const cellStyle = computed(() => {
    if (needHorizontalScroll.value) return {}
    return { width: `calc(100% / ${cellCount.value})` }
})

// 监听容器高度和滚动
function updateContainerSize() {
    if (tableWrapperRef.value) {
        containerHeight.value = tableWrapperRef.value.clientHeight
        containerWidth.value = tableWrapperRef.value.clientWidth
    }
}

function onScroll() {
    if (tableWrapperRef.value) scrollTop.value = tableWrapperRef.value.scrollTop
}

onMounted(() => {
    nextTick(() => {
        updateContainerSize()
    })
    window.addEventListener('resize', updateContainerSize)
    if (tableWrapperRef.value) tableWrapperRef.value.addEventListener('scroll', onScroll)
    // 使用 ResizeObserver 更可靠地监听容器尺寸变化（处理布局变动导致的宽度变化）
    try {
        if (typeof ResizeObserver !== 'undefined') {
            resizeObserver = new ResizeObserver(() => {
                updateContainerSize()
            })
            if (tableWrapperRef.value) resizeObserver.observe(tableWrapperRef.value)
        }
    } catch (e) {
        // ignore if ResizeObserver not available
    }
})

// 如果 ref 在挂载后才被赋值，观察其变化以便开始监听尺寸
watch(tableWrapperRef, (el, oldEl) => {
    if (oldEl && resizeObserver) {
        try { resizeObserver.unobserve(oldEl) } catch (e) { /* ignore */ }
    }
    if (el && resizeObserver) {
        try { resizeObserver.observe(el) } catch (e) { /* ignore */ }
        // 更新一次尺寸以防最初未测量到
        updateContainerSize()
    }
})

onUnmounted(() => {
    window.removeEventListener('resize', updateContainerSize)
    if (tableWrapperRef.value) tableWrapperRef.value.removeEventListener('scroll', onScroll)
    try {
        if (resizeObserver) {
            resizeObserver.disconnect()
            resizeObserver = null
        }
    } catch (e) {
        // ignore
    }
})
</script>

<template>
  <div class="csv-view">
    <div v-if="csvTable.rows.length > 0" class="csv-table-wrapper">
      <div class="csv-table-container">
        <div class="table-wrapper" ref="tableWrapperRef">
          <table class="result-table" :style="tableStyle">
            <thead>
              <tr>
                <th class='index-column'>
                  <div class='column-header'>
                    <span class="column-name">行号</span>
                  </div>
                </th>
                <th v-for="header in csvTable.headers" :key="header" class='data-column' :style="cellStyle">
                  <div class='column-header'>
                    <span class="column-name">{{ header }}</span>
                  </div>
                </th>
              </tr>
            </thead>
            <tbody>
              <!-- top spacer -->
              <tr :style="{ height: topSpacerHeight + 'px' }">
                <td :colspan="(csvTable.headers.length + 1)" style="padding:0;border:none;height:inherit"></td>
              </tr>

              <!-- visible rows -->
              <tr v-for="i in visibleIndices" :key="i" class='data-row' :style="{ height: rowHeight + 'px' }">
                <td class='index-column'>
                  <div class="index-content">
                    <span class="index-value">{{ i + 1 }}</span>
                  </div>
                </td>
                <td v-for="header in csvTable.headers" :key="header" class='data-column' :style="cellStyle">
                  {{ formatCellValue(csvTable.rows[i]![header]!) }}
                </td>
              </tr>

              <!-- bottom spacer -->
              <tr :style="{ height: bottomSpacerHeight + 'px' }">
                <td :colspan="(csvTable.headers.length + 1)" style="padding:0;border:none;height:inherit"></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
    <div v-else class='table-empty'>
      表格为空（0 行 × {{ csvTable.headers.length }} 列）
    </div>
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
  overflow: hidden;
  // border: 1px solid #ebeef5;
  border-radius: 4px;
  // margin: 12px;
}

.csv-table-container {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.table-wrapper {
  flex: 1;
  overflow: auto;
}

.result-table {
  /* default: fill container; min-width will allow horizontal scroll when needed */
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
  background: #fff;
}

.result-table thead {
  position: sticky;
  top: 0;
  // background: #f5f7fa;
  z-index: 1;
  background-color: rgb(235, 241, 245);
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
  // background: #fafafa;
  font-weight: 500;
  background-color: rgb(233, 236, 240);
}

.data-column {
  word-break: break-word;
  white-space: normal;
  text-align: center;
  /* prevent columns from shrinking too small */
  min-width: var(--min-col-width, 120px);
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
</style>