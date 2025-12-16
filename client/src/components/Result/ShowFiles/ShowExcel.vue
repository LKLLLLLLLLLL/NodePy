<script lang="ts" setup>
import { computed, ref, watch, onMounted, onUnmounted, nextTick } from 'vue'

const props = defineProps<{
  sheets: Array<{ name: string; data: any[] }>
}>()

// 添加选中的工作表状态
const selectedSheetIndex = ref(0)

// 计算选中的工作表
const selectedSheet = computed(() => {
  if (props.sheets.length === 0) return null
  return props.sheets[selectedSheetIndex.value] || props.sheets[0]
})

// 虚拟滚动相关状态（单例模式，只跟踪当前选中工作表）
const tableWrapperRef = ref<HTMLElement | null>(null)
let resizeObserver: ResizeObserver | null = null
const scrollTop = ref(0)
const containerHeight = ref(0)
const containerWidth = ref(0)
const rowHeight = ref(38) // 可调整的行高（px）
const buffer = ref(8) // 前后缓冲行数
const minColWidth = ref(120) // 最小列宽（px）

// 获取表格数据 — 返回统一结构以便模板安全使用
interface TableDataShape {
  columns: any[];
  // 使用列映射方式替代二维数组，提高访问效率
  colsMap: Record<string, any[]>;
  rowCount: number;
}

const tableData = computed<TableDataShape>(() => {
  if (!selectedSheet.value) {
    return { columns: [], colsMap: {}, rowCount: 0 }
  }
  
  const sheet = selectedSheet.value
  if (!sheet.data || sheet.data.length === 0) {
    return { columns: [], colsMap: {}, rowCount: 0 }
  }
  
  // 第一行为列标题
  const columns = sheet.data[0] || []
  // 数据从第二行开始
  const dataRows = sheet.data.slice(1) || []
  const rowCount = dataRows.length
  
  // 构建列映射，提高访问效率
  const colsMap: Record<string, any[]> = {}
  columns.forEach((col, colIndex) => {
    colsMap[col] = dataRows.map(row => row[colIndex])
  })
  
  return { columns, colsMap, rowCount }
})

// 虚拟滚动：计算可见区索引范围（使用计算属性提高性能）
const totalRows = computed(() => tableData.value.rowCount || 0)

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

// 横向布局计算
const requiredWidth = computed(() => {
  const colCount = (tableData.value.columns?.length || 0) + 1 // 包括行号列
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

const cellCount = computed(() => (tableData.value.columns?.length || 0) + 1)
const cellStyle = computed(() => {
  if (needHorizontalScroll.value) return {}
  return { width: `calc(100% / ${cellCount.value})` }
})

// 格式化日期时间显示的函数
const formatDateTime = (dateTimeString: string): string => {
  try {
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
function formatCellValue(value: any): string {
  if (value === null || value === undefined) {
    return '-'
  }
  if (typeof value === 'boolean') {
    return value ? 'True' : 'False'
  }
  if (typeof value === 'number') {
    // 检查是否为无穷大
    if (!isFinite(value)) {
      return value > 0 ? 'INFINITY' : '-INFINITY';
    }
    // 如果是小数，保留3位小数
    return typeof value === 'number' && value % 1 !== 0
        ? value.toFixed(3)
        : value.toString()
  }
  if (typeof value === 'string') {
    // 检查是否为 Datetime 类型的 ISO 格式字符串
    // ISO 8601 格式通常包含 T 和时区信息
    if (/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}/.test(value)) {
      return formatDateTime(value);
    }
    return value
  }
  // 对于对象类型，检查是否为 Datetime（在传输中会是字符串）
  // 这里处理可能的对象形式（如果有的话）
  if (typeof value === 'object') {
    // 如果是 DataView 对象且类型为 Datetime
    // @ts-ignore - 这是为了处理可能的对象形式
    if (value.type === 'Datetime' && typeof value.value === 'string') {
      // @ts-ignore
      return formatDateTime(value.value);
    }
  }
  return String(value)
}

// 检查是否为布尔值
function isBooleanValue(value: any): boolean {
  return typeof value === 'boolean';
}

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

// 切换工作表
const selectSheet = (index: number) => {
  selectedSheetIndex.value = index
}
</script>

<template>
  <div class="excel-view">
    <!-- 显示选中的工作表 -->
    <div v-if="selectedSheet" class="excel-sheet">
      <div v-if="selectedSheet.data && selectedSheet.data.length > 0" class="excel-table-wrapper">
        <div class="excel-table-container">
          <div 
            class="table-wrapper" 
            ref="tableWrapperRef"
          >
            <table class="result-table" :style="tableStyle">
              <thead>
                <tr>
                  <th class='index-column'>
                    <div class='column-header'>
                      <span class="column-name">行号</span>
                    </div>
                  </th>
                  <th 
                    v-for="(header, colIndex) in tableData.columns" 
                    :key="colIndex" 
                    class='data-column' 
                    :style="cellStyle"
                  >
                    <div class='column-header'>
                      <span class="column-name">{{ header }}</span>
                    </div>
                  </th>
                </tr>
              </thead>
              <tbody>
                <!-- top spacer -->
                <tr :style="{ height: topSpacerHeight + 'px' }">
                  <td :colspan="(tableData.columns.length + 1)" style="padding:0;border:none;height:inherit"></td>
                </tr>

                <!-- visible rows -->
                <tr 
                  v-for="i in visibleIndices" 
                  :key="i" 
                  class='data-row' 
                  :style="{ height: rowHeight + 'px' }"
                >
                  <td class='index-column'>
                    <div class="index-content">
                      <span class="index-value">{{ i + 1 }}</span>
                    </div>
                  </td>
                  <td 
                    v-for="(header, colIndex) in tableData.columns" 
                    :key="colIndex" 
                    class='data-column' 
                    :style="cellStyle"
                  >
                    <span v-if="isBooleanValue((tableData.colsMap[header] || [])[i])" :class="(tableData.colsMap[header] || [])[i] ? 'boolean-true' : 'boolean-false'">
                      {{ formatCellValue((tableData.colsMap[header] || [])[i]) }}
                    </span>
                    <span v-else>{{ formatCellValue((tableData.colsMap[header] || [])[i]) }}</span>
                  </td>
                </tr>

                <!-- bottom spacer -->
                <tr :style="{ height: bottomSpacerHeight + 'px' }">
                  <td :colspan="(tableData.columns.length + 1)" style="padding:0;border:none;height:inherit"></td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
      <div v-else class="excel-empty">
        工作表为空
      </div>
    </div>
    
    <!-- 无工作表提示 -->
    <div v-else class="excel-empty">
      没有可用的工作表
    </div>
    
    <!-- 标签页选择器 -->
    <div v-if="sheets.length > 1" class="tab-selector">
      <div class="tab-list">
        <div 
          v-for="(sheet, index) in sheets" 
          :key="index"
          :class="{ 'tab-item': true, 'active': index === selectedSheetIndex }"
          @click="selectSheet(index)"
        >
          {{ sheet.name }}
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
@use '../../../common/global.scss' as *;

.excel-view {
  display: flex;
  flex-direction: column;
  height: 100%;
  width: 100%;
  overflow: hidden;
  background: $stress-background-color;
  box-sizing: border-box;
}

.tab-selector {
  margin-top: 10px;
  border-top: 1px solid #e0e0e0;
  padding: 0 10px;
  padding-left: 0px;
}

.tab-list {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
  padding-bottom: 5px;
}

.tab-item {
  padding: 8px 16px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  color: #606266;
  border: 1px solid transparent;
  border-top: none;
  border-radius: 0 0 4px 4px;
  background-color: #f5f7fa;
  transition: all 0.3s ease;
  position: relative;
  margin-top: -1px;
}

.tab-item:hover {
  background-color: #e1e6ee;
  color: #303133;
}

.tab-item.active {
  background-color: #ffffff;
  color: #409eff;
  border-color: #dcdfe6;
  border-top: 1px solid #ffffff;
  font-weight: 600;
  margin-top: 0;
  z-index: 2;
}

.tab-item.active::after {
  content: '';
  position: absolute;
  top: -1px;
  left: 0;
  right: 0;
  height: 2px;
  background-color: #409eff;
}

.excel-sheet {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 300px;
}

.excel-table-wrapper {
  flex: 1;
  overflow: hidden;
  border: 1px solid #ebeef5;
  border-radius: 4px 4px 0 0;
}

.excel-table-container {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.table-wrapper {
  flex: 1;
  overflow: auto;
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
  font-weight: 500;
  background-color: rgb(233, 236, 240);
}

.data-column {
  word-break: break-word;
  white-space: normal;
  text-align: center;
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

.boolean-true {
  color: #67c23a;
  font-weight: bold;
}

.boolean-false {
  color: #f56c6c;
  font-weight: bold;
}

.excel-empty {
  flex: 1;
  display: flex;
  justify-content: center;
  color: #909399;
  font-size: 14px;
  padding: 16px;
}
</style>