<script lang="ts" setup>
    import { computed, ref, watch, onMounted, onUnmounted, nextTick } from 'vue';
    import type { TableView } from '@/utils/api'
    import Loading from '@/components/Loading.vue'
    import type { ResultType } from '@/stores/resultStore';
    // 改为使用虚拟滚动，不再使用分页组件

    const props = defineProps<{
        value: ResultType
    }>()

    // 添加loading和error状态
    const loading = ref(false)
    const error = ref<string>('')

    // 虚拟滚动相关状态
    const tableWrapperRef = ref<HTMLElement | null>(null)
    const scrollTop = ref(0)
    const containerHeight = ref(0)
    const containerWidth = ref(0)
    const rowHeight = ref(38) // 可调整的行高（px）
    const buffer = ref(8) // 前后缓冲行数
    // 最小列宽（px），稍微减小以避免过宽（用户要求）
    const minColWidth = ref(120)

    // 类型守卫：检查是否是 TableView
    const isTableView = computed(() => {
        return (
            typeof props.value === 'object' &&
            props.value !== null &&
            'cols' in props.value &&
            'col_types' in props.value
        )
    })

    // 获取表格数据 — 返回统一结构以便模板安全使用
    interface TableDataShape {
        columns: string[];
        indexColumn: string | null;
        colsMap: Record<string, any[]>;
        rowCount: number;
    }

    const tableData = computed<TableDataShape>(() => {
        if (!isTableView.value) {
            return { columns: [], indexColumn: null, colsMap: {}, rowCount: 0 }
        }

        const table = props.value as TableView
        const allColumns = Object.keys(table.cols || {})

        // 分离 _index 列和其他列
        const indexColumn = allColumns.find(col => col === '_index') || null
        const columns = allColumns.filter(col => col !== '_index')

        // 不再构造完整的行数组；直接返回列映射与行数以便按需访问
        const colsMap = table.cols || {}
        const rowCountCol = indexColumn || columns[0]
        const rowCount = (colsMap[rowCountCol as keyof typeof colsMap] as any[])?.length || 0
        return { columns, indexColumn, colsMap, rowCount }
    })
        // 虚拟滚动：计算可见区索引范围
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

        // 横向布局计算：如果所需最小宽度小于容器宽度，则让表格 100% 平分列宽，否则使用 max-content 启用横向滚动
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
            const styleObj: Record<string, any> = {
                ['--min-col-width']: `${minColWidth.value}px`,
                width: '100%',
                minWidth: needHorizontalScroll.value ? `${requiredWidth.value}px` : '100%'
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

    const columnTypes = computed(() => {
        if (!isTableView.value) return {}
        const table = props.value as TableView
        return table.col_types || {}
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
    })

    onUnmounted(() => {
        window.removeEventListener('resize', updateContainerSize)
        if (tableWrapperRef.value) tableWrapperRef.value.removeEventListener('scroll', onScroll)
    })
</script>
<template>
    <div class='table-view-container'>
        <!-- 加载中 -->
        <div v-if="loading" class="table-loading">
            <Loading></Loading>
        </div>

        <!-- 错误提示 -->
        <div v-else-if="error" class='table-error'>
            {{ error }}
        </div>

        <!-- 无效数据提示 -->
        <div v-else-if="!isTableView" class='table-error'>
            无效的表格数据
        </div>

        <!-- 表格显示 -->
        <div v-else class="table-content-wrapper">
            <div v-if="(tableData.rowCount ?? 0) > 0 || (tableData.columns?.length ?? 0) > 0" class='table-wrapper' ref="tableWrapperRef">
                <table class='result-table' :style="tableStyle">
                    <thead>
                        <tr>
                            <th class='index-column'>
                                <div class='column-header'>
                                    <span class="column-name">行号</span>
                                    <span v-if="tableData.indexColumn" class='column-type'>{{ tableData.indexColumn }}</span>
                                </div>
                            </th>
                            <th v-for="col in tableData.columns" :key="col" class='data-column' :style="cellStyle">
                                <div class='column-header'>
                                    <span class="column-name">{{ col }}</span>
                                    <span v-if="columnTypes[col]" class='column-type'>{{ columnTypes[col] }}</span>
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
                        <tr v-for="i in visibleIndices" :key="i" class='data-row' :style="{ height: rowHeight + 'px' }">
                            <td class='index-column'>
                                <div class="index-content">
                                    <span class="index-value">
                                        {{ tableData.indexColumn ? formatCellValue((tableData.colsMap[tableData.indexColumn] || [])[i]) : (i + 1) }}
                                    </span>
                                </div>
                            </td>
                            <td v-for="col in tableData.columns" :key="col" class='data-column' :style="cellStyle">
                                <span v-if="isBooleanValue((tableData.colsMap?.[col] || [])[i])" :class="(tableData.colsMap?.[col] || [])[i] ? 'boolean-true' : 'boolean-false'">
                                    {{ formatCellValue((tableData.colsMap?.[col] || [])[i]) }}
                                </span>
                                <span v-else>{{ formatCellValue((tableData.colsMap?.[col] || [])[i]) }}</span>
                            </td>
                        </tr>

                        <!-- bottom spacer -->
                        <tr :style="{ height: bottomSpacerHeight + 'px' }">
                            <td :colspan="(tableData.columns.length + 1)" style="padding:0;border:none;height:inherit"></td>
                        </tr>
                    </tbody>
                </table>
            </div>

            <!-- 空表格 -->
            <div v-else class='table-empty'>
                表格为空（0 行 × {{ tableData.columns.length }} 列）
            </div>
        </div>
    </div>
</template>
<style scoped lang="scss">
@use '@/common/global.scss' as *;

.table-view-container {
    display: flex;
    flex-direction: column;
    height: 100%;
    width: 100%;
    overflow: hidden;
    background: $background-color;
    border-radius: 10px;
    padding: 16px;
    box-sizing: border-box;
}

.table-content-wrapper {
    display: flex;
    flex-direction: column;
    height: 100%;
    background: $stress-background-color;
    border-radius: 10px;
    box-sizing: border-box;
    @include controller-style;
}

.table-loading {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 12px;
    color: #909399;
    font-size: 14px;
    padding: 16px;
}

.table-error,
.table-empty {
    flex: 1;
    display: flex;
    justify-content: center;
    color: #909399;
    font-size: 14px;
    padding: 16px;
}

.table-error {
    color: $error-message-color;
    background: $stress-background-color;
    border-radius: 10px;
    margin: 16px;
    padding: 16px;
    @include controller-style;
}

.table-wrapper {
    flex: 1;
    overflow: auto;
    border: 1px solid #ebeef5;
    border-radius: 4px;
    margin: 12px;
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

.column-type {
    font-size: 11px;
    color: #909399;
    font-weight: normal;
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
    color: #67c23a; // 绿色表示 True
    font-weight: bold;
}

.boolean-false {
    color: #f56c6c; // 红色表示 False
    font-weight: bold;
}
</style>
