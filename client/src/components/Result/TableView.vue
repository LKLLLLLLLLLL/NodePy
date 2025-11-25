<script lang="ts" setup>
    import { computed, ref } from 'vue';
    import type { TableView } from '@/utils/api'
    import Loading from '@/components/Loading.vue'

    const props = defineProps<{
        value: any
    }>()

    // 添加loading和error状态
    const loading = ref(false)
    const error = ref<string>('')

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
            return { columns: [], rows: [] }
        }

        const table = props.value as TableView
        const columns = Object.keys(table.cols || {})
        
        // 将列数据转换为行数据
        const rows: Record<string, any>[] = []
        if (columns.length > 0) {
            const firstCol = columns[0]
            const rowCount = (table.cols[firstCol as keyof typeof table.cols] as any[])?.length || 0
            for (let i = 0; i < rowCount; i++) {
                const row: Record<string, any> = {}
                columns.forEach(col => {
                    row[col] = (table.cols[col as keyof typeof table.cols] as any[])?.[i] ?? null
                })
                rows.push(row)
            }
        }

        return { columns, rows }
    })

    // 获取列类型
    const columnTypes = computed(() => {
        if (!isTableView.value) return {}
        const table = props.value as TableView
        return table.col_types || {}
    })

    // 格式化单元格值
    function formatCellValue(value: any): string {
        if (value === null || value === undefined) {
            return '-'
        }
        if (typeof value === 'boolean') {
            return value ? '是' : '否'
        }
        if (typeof value === 'number') {
            return value.toString()
        }
        return String(value)
    }
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
        <div v-else-if="tableData.rows.length > 0" class='table-wrapper'>
            <table class='result-table'>
                <thead>
                    <tr>
                        <th class='index-column'>序号</th>
                        <th v-for="col in tableData.columns" :key="col" class='data-column'>
                            <div class='column-header'>
                                <span class='column-name'>{{ col }}</span>
                                <span v-if="columnTypes[col]" class='column-type'>{{ columnTypes[col] }}</span>
                            </div>
                        </th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="(row, rowIndex) in tableData.rows" :key="rowIndex" class='data-row'>
                        <td class='index-column'>{{ rowIndex + 1 }}</td>
                        <td v-for="col in tableData.columns" :key="col" class='data-column'>
                            {{ formatCellValue(row[col]) }}
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>

        <!-- 空表格 -->
        <div v-else class='table-empty'>
            表格为空（0 行 × {{ tableData.columns.length }} 列）
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
        align-items: center;
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
        text-align: left;
        border-bottom: 2px solid #ebeef5;
        font-weight: 600;
        color: #303133;
    }

    td {
        padding: 10px 8px;
        border-bottom: 1px solid #ebeef5;
        color: #606266;
    }

    .index-column {
        width: 50px;
        min-width: 50px;
        text-align: center;
        background: #fafafa;
        font-weight: 500;
    }

    .data-column {
        word-break: break-word;
        white-space: normal;
    }

    .column-header {
        display: flex;
        flex-direction: column;
        gap: 4px;
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

    tr:hover td:not(.index-column) {
        background: #f0f9ff;
    }
</style>