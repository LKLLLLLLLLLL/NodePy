<script lang="ts" setup>
    import { computed, ref, watch } from 'vue';
    import type { TableView } from '@/utils/api'
    import Loading from '@/components/Loading.vue'
    import type { ResultType } from '@/stores/resultStore';

    const props = defineProps<{
        value: ResultType
    }>()

    // 添加loading和error状态
    const loading = ref(false)
    const error = ref<string>('')

    // 分页相关状态
    const currentPage = ref(1)
    const rowsPerPage = ref(100)
    const inputPage = ref('')

    // 类型守卫：检查是否是 TableView
    const isTableView = computed(() => {
        return (
            typeof props.value === 'object' &&
            props.value !== null &&
            'cols' in props.value &&
            'col_types' in props.value
        )
    })

    // 获取表格数据
    const tableData = computed(() => {
        if (!isTableView.value) {
            return { columns: [], rows: [], indexColumn: null }
        }

        const table = props.value as TableView
        const allColumns = Object.keys(table.cols || {})
        
        // 分离 _index 列和其他列
        const indexColumn = allColumns.find(col => col === '_index') || null
        const columns = allColumns.filter(col => col !== '_index')
        
        // 将列数据转换为行数据
        const rows: Record<string, any>[] = []
        if (columns.length > 0 || indexColumn) {
            // 确定行数（使用第一个有效列或 _index 列）
            const rowCountCol = indexColumn || columns[0]
            const rowCount = (table.cols[rowCountCol as keyof typeof table.cols] as any[])?.length || 0
            
            for (let i = 0; i < rowCount; i++) {
                const row: Record<string, any> = {}
                
                // 处理普通列
                columns.forEach(col => {
                    row[col] = (table.cols[col as keyof typeof table.cols] as any[])?.[i] ?? null
                })
                
                // 处理 _index 列
                if (indexColumn) {
                    row[indexColumn] = (table.cols[indexColumn as keyof typeof table.cols] as any[])?.[i] ?? null
                }
                
                rows.push(row)
            }
        }

        return { columns, rows, indexColumn }
    })

    // 计算分页数据
    const paginatedTableData = computed(() => {
        const startIndex = (currentPage.value - 1) * rowsPerPage.value
        const endIndex = startIndex + rowsPerPage.value
        return {
            ...tableData.value,
            rows: tableData.value.rows.slice(startIndex, endIndex)
        }
    })

    // 总页数
    const totalPages = computed(() => {
        return Math.ceil(tableData.value.rows.length / rowsPerPage.value)
    })

    // 分页方法
    const prevPage = () => {
        if (currentPage.value > 1) {
            currentPage.value--
        }
    }

    const nextPage = () => {
        if (currentPage.value < totalPages.value) {
            currentPage.value++
        }
    }

    const goToPage = (page: number) => {
        if (page >= 1 && page <= totalPages.value) {
            currentPage.value = page
        }
    }

    // 回车跳转页面
    const handlePageInput = () => {
        const page = parseInt(inputPage.value)
        if (!isNaN(page)) {
            goToPage(page)
            inputPage.value = ''
        }
    }

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

    // 监听数据变化，重置到第一页
    watch(tableData, () => {
        currentPage.value = 1
    })
</script>
<template>
    <div class='table-view-container'>
        <!-- 加载中 -->
        <div v-if="loading" class="table-loading">
            <Loading></Loading>
            <span>加载中...</span>
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
            <div v-if="paginatedTableData.rows.length > 0 || paginatedTableData.columns.length > 0" class='table-wrapper'>
                <table class='result-table'>
                    <thead>
                        <tr>
                            <th class='index-column'>
                                <div class='column-header'>
                                    <span class="column-name">行号</span>
                                    <span v-if="paginatedTableData.indexColumn" class='column-type'>{{ paginatedTableData.indexColumn }}</span>
                                </div>
                            </th>
                            <th v-for="col in paginatedTableData.columns" :key="col" class='data-column'>
                                <div class='column-header'>
                                    <span class="column-name">{{ col }}</span>
                                    <span v-if="columnTypes[col]" class='column-type'>{{ columnTypes[col] }}</span>
                                </div>
                            </th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="(row, rowIndex) in paginatedTableData.rows" :key="(currentPage - 1) * rowsPerPage + rowIndex" class='data-row'>
                            <td class='index-column'>
                                <div class="index-content">
                                    <span class="index-value">{{ paginatedTableData.indexColumn ? formatCellValue(row[paginatedTableData.indexColumn]) : (currentPage - 1) * rowsPerPage + rowIndex + 1 }}</span>
                                </div>
                            </td>
                            <td v-for="col in paginatedTableData.columns" :key="col" class='data-column'>
                                <span 
                                    v-if="isBooleanValue(row[col])" 
                                    :class="row[col] ? 'boolean-true' : 'boolean-false'"
                                >
                                    {{ formatCellValue(row[col]) }}
                                </span>
                                <span v-else>{{ formatCellValue(row[col]) }}</span>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>

            <!-- 空表格 -->
            <div v-else class='table-empty'>
                表格为空（0 行 × {{ paginatedTableData.columns.length }} 列）
            </div>

            <!-- 分页控件 -->
            <div class="pagination-controls" v-if="totalPages > 1">
                <button 
                    class="pagination-btn" 
                    :disabled="currentPage === 1"
                    @click="prevPage"
                >
                    上一页
                </button>
                
                <span class="pagination-info">
                    第 {{ currentPage }} 页，共 {{ totalPages }} 页
                </span>
                
                <button 
                    class="pagination-btn" 
                    :disabled="currentPage === totalPages"
                    @click="nextPage"
                >
                    下一页
                </button>
                
                <div class="pagination-jump">
                    <input 
                        v-model="inputPage" 
                        type="number" 
                        min="1" 
                        :max="totalPages"
                        placeholder="页码"
                        @keyup.enter="handlePageInput"
                    />
                    <button @click="handlePageInput">跳转</button>
                </div>
            </div>
        </div>
    </div>
</template>
<style scoped lang="scss">
    .table-view-container {
        display: flex;
        flex-direction: column;
        height: 100%;
        width: 100%;
        overflow: hidden;
        background: #fafafa;
    }

    .table-content-wrapper {
        display: flex;
        flex-direction: column;
        height: 100%;
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
        background: #fef0f0;
        color: #f56c6c;
        border: 1px solid #fde2e2;
        border-radius: 4px;
        margin: 16px;
    }

    .table-wrapper {
        flex: 1;
        overflow: auto;
        border: 1px solid #ebeef5;
        border-radius: 4px;
        margin: 12px;
    }

    .result-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 13px;
        background: #fff;
    }

    thead {
        position: sticky;
        top: 0;
        background: #f5f7fa;
        z-index: 1;
    }

    th {
        padding: 12px 8px;
        text-align: center; /* 修改为居中 */
        border-bottom: 2px solid #ebeef5;
        font-weight: 600;
        color: #303133;
    }

    td {
        padding: 10px 8px;
        text-align: center; /* 修改为居中 */
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
        text-align: center; /* 添加居中对齐 */
    }

    .column-header {
        display: flex;
        flex-direction: column;
        gap: 4px;
        align-items: center; /* 添加居中对齐 */
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
    
    .boolean-true {
        color: #67c23a; // 绿色表示 True
        font-weight: bold;
    }
    
    .boolean-false {
        color: #f56c6c; // 红色表示 False
        font-weight: bold;
    }

    /* 分页控件样式 */
    .pagination-controls {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 15px;
        padding: 15px;
        border-top: 1px solid #ebeef5;
        background-color: #fff;
        flex-shrink: 0;
    }

    .pagination-btn {
        padding: 6px 12px;
        background-color: #f0f0f0;
        border: 1px solid #dcdfe6;
        border-radius: 4px;
        cursor: pointer;
        transition: all 0.3s;

        &:hover:not(:disabled) {
            background-color: #ecf5ff;
            border-color: #409eff;
            color: #409eff;
        }

        &:disabled {
            color: #a8abb2;
            cursor: not-allowed;
            background-color: #f5f7fa;
        }
    }

    .pagination-info {
        font-size: 14px;
        color: #606266;
        white-space: nowrap;
    }

    .pagination-jump {
        display: flex;
        align-items: center;
        gap: 8px;

        input {
            width: 60px;
            padding: 6px 10px;
            border: 1px solid #dcdfe6;
            border-radius: 4px;
            outline: none;
            transition: border-color 0.3s;

            &:focus {
                border-color: #409eff;
            }
        }

        button {
            padding: 6px 12px;
            background-color: #409eff;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            transition: background-color 0.3s;

            &:hover {
                background-color: #66b1ff;
            }
        }
    }
</style>