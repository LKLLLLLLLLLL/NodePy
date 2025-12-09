<script setup lang="ts">
import { ref, computed, watch, nextTick, onMounted, onUpdated } from 'vue';
import { useTableStore } from '@/stores/tableStore';

const props = defineProps<{
    data: any,
    noC: number,
    noR: number
}>();

const tableStore = useTableStore();

// 单元格引用
const cellRefs = ref<HTMLDivElement[][]>([]);
// 输入框引用
const inputRefs = ref<HTMLInputElement[][]>([]);
// 列宽配置
const columnWidths = ref<number[]>([]);

// 当前编辑的单元格
const editingCell = ref<{ row: number; col: number } | null>(null);
const editValue = ref<string>('');

// 行号列宽
const rowHeaderWidth = 60;
// 列名行高
const colHeaderHeight = 40;

// 计算列宽（根据列名长度）
const calculateColumnWidths = () => {
    if (!tableStore.currentTableData.colNames?.length) return;
    
    const baseWidth = 100; // 基础宽度
    const charWidth = 8; // 每个字符的宽度
    const minWidth = 80; // 最小宽度
    const maxWidth = 300; // 最大宽度
    
    columnWidths.value = tableStore.currentTableData.colNames.map(colName => {
        // 计算基于列名的宽度
        let width = baseWidth + (colName.length * charWidth);
        
        // 考虑列类型标签的宽度
        const colType = tableStore.currentTableData.colTypes[colName] || 'str';
        width += colType.length * 6;
        
        // 添加删除按钮的宽度
        width += 24;
        
        // 限制宽度范围
        return Math.min(Math.max(width, minWidth), maxWidth);
    });
};

/**
 * 开始编辑单元格
 */
function startEditCell(rowIndex: number, colIndex: number) {
    const colName = tableStore.currentTableData.colNames[colIndex];
    const cellValue = tableStore.currentTableData.rows[rowIndex]?.[colName!];
    
    editingCell.value = { row: rowIndex, col: colIndex };
    editValue.value = cellValue !== null && cellValue !== undefined ? String(cellValue) : '';
    
    // 聚焦输入框
    nextTick(() => {
        if (inputRefs.value[rowIndex]?.[colIndex]) {
            inputRefs.value[rowIndex][colIndex].focus();
            inputRefs.value[rowIndex][colIndex].select();
        }
    });
}

/**
 * 结束编辑单元格
 */
function finishEditCell() {
    if (!editingCell.value) return;
    
    const { row, col } = editingCell.value;
    const colName = tableStore.currentTableData.colNames[col]!;
    
    // 转换值类型
    let finalValue: any = editValue.value.trim();
    const colType = tableStore.currentTableData.colTypes[colName];
    
    if (finalValue === '') {
        finalValue = null;
    } else {
        try {
            switch (colType) {
                case 'int':
                    finalValue = parseInt(finalValue, 10);
                    if (isNaN(finalValue)) finalValue = null;
                    break;
                case 'float':
                    finalValue = parseFloat(finalValue);
                    if (isNaN(finalValue)) finalValue = null;
                    break;
                case 'bool':
                    finalValue = finalValue.toLowerCase() === 'true' || finalValue === '1';
                    break;
                case 'str':
                    // 保持字符串
                    break;
                case 'Datetime':
                    // 尝试解析日期
                    const date = new Date(finalValue);
                    if (isNaN(date.getTime())) {
                        finalValue = null;
                    } else {
                        finalValue = date.toISOString();
                    }
                    break;
            }
        } catch (error) {
            console.warn('值转换失败:', error);
            finalValue = null;
        }
    }
    
    tableStore.updateCell(row, colName, finalValue);
    editingCell.value = null;
}

/**
 * 取消编辑单元格
 */
function cancelEditCell() {
    editingCell.value = null;
}

/**
 * 处理按键事件
 */
function handleKeyDown(event: KeyboardEvent, rowIndex: number, colIndex: number) {
    if (!editingCell.value) return;
    
    switch (event.key) {
        case 'Enter':
            finishEditCell();
            // 移动到下一行
            if (rowIndex < tableStore.numRows - 1) {
                startEditCell(rowIndex + 1, colIndex);
            }
            event.preventDefault();
            break;
            
        case 'Tab':
            finishEditCell();
            // 移动到下一列
            if (colIndex < tableStore.numCols - 1) {
                startEditCell(rowIndex, colIndex + 1);
            } else if (rowIndex < tableStore.numRows - 1) {
                // 换行到第一列
                startEditCell(rowIndex + 1, 0);
            }
            event.preventDefault();
            break;
            
        case 'Escape':
            cancelEditCell();
            break;
            
        case 'ArrowUp':
            if (editingCell.value.row > 0) {
                finishEditCell();
                startEditCell(rowIndex - 1, colIndex);
                event.preventDefault();
            }
            break;
            
        case 'ArrowDown':
            if (editingCell.value.row < tableStore.numRows - 1) {
                finishEditCell();
                startEditCell(rowIndex + 1, colIndex);
                event.preventDefault();
            }
            break;
            
        case 'ArrowLeft':
            if (editingCell.value.col > 0) {
                finishEditCell();
                startEditCell(rowIndex, colIndex - 1);
                event.preventDefault();
            }
            break;
            
        case 'ArrowRight':
            if (editingCell.value.col < tableStore.numCols - 1) {
                finishEditCell();
                startEditCell(rowIndex, colIndex + 1);
                event.preventDefault();
            }
            break;
    }
}

/**
 * 选择单元格
 */
function selectCell(rowIndex: number, colIndex: number) {
    tableStore.selectedCell = { row: rowIndex, col: colIndex };
}

/**
 * 修改列（支持同时修改列名和类型）
 */
function modifyColumn(colIndex: number) {
    const colName = tableStore.currentTableData.colNames[colIndex]!;
    const currentType = tableStore.currentTableData.colTypes[colName] || 'str';
    
    // 创建一个对话框来同时修改列名和类型
    const newName = prompt('输入新列名:', colName);
    if (newName === null) return; // 用户取消
    
    if (newName === '') {
        alert('列名不能为空');
        return;
    }
    
    if (newName !== colName) {
        // 检查列名是否已存在
        if (tableStore.currentTableData.colNames.includes(newName) && newName !== colName) {
            alert(`列名 "${newName}" 已存在`);
            return;
        }
    }
    
    const newType = prompt('选择列类型 (int, float, str, bool, Datetime):', currentType);
    if (newType === null) return; // 用户取消
    
    if (!['int', 'float', 'str', 'bool', 'Datetime'].includes(newType)) {
        alert('无效的类型，请选择: int, float, str, bool, Datetime');
        return;
    }
    
    // 更新列名和类型
    if (newName !== colName) {
        tableStore.updateColumnName(colName, newName);
    }
    
    if (newType !== currentType) {
        tableStore.updateColumnType(newName !== colName ? newName : colName, newType as any);
    }
    
    // 重新计算列宽
    calculateColumnWidths();
}

/**
 * 在指定位置添加新列
 */
function addColumnAtPosition(position: number) {
    const colName = prompt('请输入新列名:', `Column_${tableStore.numCols + 1}`);
    if (!colName) return;
    
    if (colName.trim() === '') {
        alert('列名不能为空');
        return;
    }
    
    // 检查列名是否已存在
    if (tableStore.currentTableData.colNames.includes(colName)) {
        alert(`列名 "${colName}" 已存在`);
        return;
    }
    
    const colType = prompt('请选择列类型 (int, float, str, bool, Datetime):', 'str');
    if (!colType) return;
    
    if (!['int', 'float', 'str', 'bool', 'Datetime'].includes(colType)) {
        alert('无效的类型，请选择: int, float, str, bool, Datetime');
        return;
    }
    
    tableStore.addColumn(colName, colType as any, position);
    
    // 重新计算列宽
    nextTick(() => {
        calculateColumnWidths();
    });
}

// 初始化单元格引用数组和列宽
watch(() => [tableStore.numRows, tableStore.numCols], () => {
    cellRefs.value = Array(tableStore.numRows).fill(null).map(() => 
        Array(tableStore.numCols).fill(null)
    );
    inputRefs.value = Array(tableStore.numRows).fill(null).map(() => 
        Array(tableStore.numCols).fill(null)
    );
    
    // 重新计算列宽
    calculateColumnWidths();
}, { immediate: true });

// 监听列名变化，重新计算列宽
watch(() => tableStore.currentTableData.colNames, () => {
    calculateColumnWidths();
}, { deep: true });

// 组件挂载时计算初始列宽
onMounted(() => {
    calculateColumnWidths();
});
</script>

<template>
    <div class="editable-table">
        <!-- 列操作栏 -->
        <div class="table-toolbar">
            <div class="toolbar-left">
                <button @click="tableStore.addRow()" title="添加行">+ 行</button>
                <button @click="addColumnAtPosition(-1)" title="添加列">+ 列</button>
                <button @click="tableStore.undo" :disabled="!tableStore.canUndo" title="撤销">↶ 撤销</button>
                <button @click="tableStore.redo" :disabled="!tableStore.canRedo" title="重做">↷ 重做</button>
            </div>
            <div class="toolbar-right">
                尺寸: {{ tableStore.numRows }} × {{ tableStore.numCols }}
            </div>
        </div>
        
        <!-- 表格容器 -->
        <div class="table-container">
            <div class="table-wrapper">
                <!-- 列标题行 -->
                <div class="table-row header-row">
                    <!-- 左上角空白单元格 -->
                    <div class="table-cell corner-cell"></div>
                    
                    <!-- 列标题 -->
                    <div 
                        v-for="(colName, colIndex) in tableStore.currentTableData.colNames" 
                        :key="`col-${colIndex}`"
                        class="table-cell header-cell column-header"
                        :style="{ width: columnWidths[colIndex] ? columnWidths[colIndex] + 'px' : '150px' }"
                        :title="`${colName} (${tableStore.currentTableData.colTypes[colName] || 'str'})`"
                        @dblclick="modifyColumn(colIndex)"
                        @contextmenu.prevent="modifyColumn(colIndex)"
                    >
                        <div class="column-header-content">
                            <span class="column-name">{{ colName }}</span>
                            <span class="column-type">{{ tableStore.currentTableData.colTypes[colName] || 'str' }}</span>
                            <button 
                                class="delete-column-btn"
                                @click.stop="tableStore.deleteColumn(colIndex)"
                                :disabled="tableStore.numCols <= 1"
                                title="删除列"
                            >×</button>
                        </div>
                    </div>
                    
                    <!-- 添加列按钮 -->
                    <div class="table-cell add-column-cell">
                        <button @click="addColumnAtPosition(-1)" title="添加列">+</button>
                    </div>
                </div>
                
                <!-- 数据行 -->
                <div 
                    v-for="(row, rowIndex) in tableStore.currentTableData.rows" 
                    :key="`row-${rowIndex}`"
                    class="table-row data-row"
                    :class="{ 'selected-row': tableStore.selectedCell?.row === rowIndex }"
                >
                    <!-- 行号单元格 -->
                    <div class="table-cell row-header" :style="{ width: `${rowHeaderWidth}px` }">
                        <span class="row-number">{{ rowIndex + 1 }}</span>
                        <button 
                            class="delete-row-btn"
                            @click="tableStore.deleteRow(rowIndex)"
                            :disabled="tableStore.numRows <= 1"
                            title="删除行"
                        >×</button>
                    </div>
                    
                    <!-- 数据单元格 -->
                    <div 
                        v-for="(colName, colIndex) in tableStore.currentTableData.colNames" 
                        :key="`cell-${rowIndex}-${colIndex}`"
                        class="table-cell data-cell"
                        :style="{ width: columnWidths[colIndex] ? columnWidths[colIndex] + 'px' : '150px' }"
                        :class="{ 
                            'editing': editingCell?.row === rowIndex && editingCell?.col === colIndex,
                            'selected': tableStore.selectedCell?.row === rowIndex && tableStore.selectedCell?.col === colIndex
                        }"
                        :ref="el => {
                            if (cellRefs[rowIndex]) {
                                cellRefs[rowIndex][colIndex] = el as HTMLDivElement;
                            } else {
                                // 如果第一层不存在，则创建它
                                cellRefs[rowIndex] = [];
                                cellRefs[rowIndex][colIndex] = el as HTMLDivElement;
                            }
                        }"
                        @click="selectCell(rowIndex, colIndex)"
                        @dblclick="startEditCell(rowIndex, colIndex)"
                    >
                        <!-- 显示模式 -->
                        <template v-if="!(editingCell?.row === rowIndex && editingCell?.col === colIndex)">
                            <span class="cell-content">
                                {{ row[colName] !== null && row[colName] !== undefined ? String(row[colName]) : '' }}
                            </span>
                        </template>
                        
                        <!-- 编辑模式 -->
                        <template v-else>
                            <!-- 对于inputRefs的修改 -->
                            <input
                                type="text"
                                v-model="editValue"
                                :ref="el => {
                                    if (inputRefs[rowIndex]) {
                                        inputRefs[rowIndex][colIndex] = el as HTMLInputElement;
                                    } else {
                                        inputRefs[rowIndex] = [];
                                        inputRefs[rowIndex][colIndex] = el as HTMLInputElement;
                                    }
                                }"
                                @blur="finishEditCell"
                                @keydown="(e) => handleKeyDown(e, rowIndex, colIndex)"
                                class="cell-input"
                            />
                        </template>
                    </div>
                </div>
                
                <!-- 添加行按钮 -->
                <div class="table-row add-row">
                    <div class="table-cell row-header add-row-cell">
                        <button @click="tableStore.addRow()" title="添加行">+</button>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- 状态栏 -->
        <div class="table-statusbar">
            <div v-if="tableStore.selectedCell" class="status-selection">
                选中: 行 {{ tableStore.selectedCell.row + 1 }}, 列 {{ tableStore.selectedCell.col + 1 }}
                ({{ tableStore.currentTableData.colNames[tableStore.selectedCell.col] }})
            </div>
            <div v-else class="status-default">
                双击单元格编辑，双击列名修改列名和类型，右键列名也可修改
            </div>
        </div>
    </div>
</template>

<style lang="scss" scoped>
@use '@/common/global.scss' as *;

.editable-table {
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

.table-toolbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px 12px;
    background: $stress-background-color;
    border-radius: 4px;
    margin-bottom: 12px;
    @include controller-style;
    
    .toolbar-left {
        display: flex;
        gap: 8px;
        
        button {
            padding: 6px 12px;
            border: 1px solid #dcdfe6;
            background: white;
            border-radius: 4px;
            cursor: pointer;
            font-size: 12px;
            color: #606266;
            transition: all 0.2s;
            
            &:hover {
                background: #f5f7fa;
                border-color: #c0c4cc;
                color: #303133;
            }
            
            &:active {
                background: #e9ebee;
            }
            
            &:disabled {
                opacity: 0.5;
                cursor: not-allowed;
            }
        }
    }
    
    .toolbar-right {
        font-size: 12px;
        color: #666;
    }
}

.table-container {
    flex: 1;
    overflow: auto;
    border: 1px solid #ebeef5;
    border-radius: 4px;
    background: #fff;
}

.table-wrapper {
    display: inline-block;
    min-width: 100%;
}

.table-row {
    display: flex;
    
    &.header-row {
        position: sticky;
        top: 0;
        z-index: 10;
        background: #f5f7fa;
    }
    
    &.data-row {
        &:hover {
            background: #f9f9f9;
        }
        
        &.selected-row {
            background: #e3f2fd;
        }
    }
}

.table-cell {
    border: 1px solid #ebeef5;
    min-height: 36px;
    box-sizing: border-box;
    padding: 6px 8px;
    overflow: hidden;
    display: flex;
    align-items: center;
    
    &.corner-cell {
        width: 60px;
        background: #f5f7fa;
        border-right: 2px solid #dcdfe6;
        border-bottom: 2px solid #dcdfe6;
        font-weight: 500;
        justify-content: center;
    }
    
    &.header-cell {
        font-weight: 600;
        text-align: center;
        background: #f5f7fa;
        border-bottom: 2px solid #dcdfe6;
        user-select: none;
        cursor: pointer;
        position: relative;
        
        .column-header-content {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 4px;
            width: 100%;
            
            .column-name {
                flex: 1;
                overflow: hidden;
                text-overflow: ellipsis;
                white-space: nowrap;
                color: #303133;
            }
            
            .column-type {
                font-size: 10px;
                color: #909399;
                background: #e9ecef;
                padding: 2px 4px;
                border-radius: 2px;
                flex-shrink: 0;
            }
            
            .delete-column-btn {
                opacity: 0;
                padding: 0 4px;
                font-size: 16px;
                border: none;
                background: transparent;
                color: #909399;
                cursor: pointer;
                flex-shrink: 0;
                width: 20px;
                height: 20px;
                display: flex;
                align-items: center;
                justify-content: center;
                border-radius: 50%;
                transition: all 0.2s;
                
                &:hover {
                    color: #f56c6c;
                    background: #fef0f0;
                }
                
                &:disabled {
                    opacity: 0.2;
                    cursor: not-allowed;
                }
            }
        }
        
        &:hover {
            background: #e9ecef;
            
            .delete-column-btn {
                opacity: 1;
            }
        }
    }
    
    &.row-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        background: #f5f7fa;
        border-right: 2px solid #dcdfe6;
        user-select: none;
        flex-shrink: 0;
        font-weight: 500;
        color: #606266;
        
        .row-number {
            font-weight: 500;
        }
        
        .delete-row-btn {
            opacity: 0;
            padding: 0;
            font-size: 16px;
            border: none;
            background: transparent;
            color: #909399;
            cursor: pointer;
            width: 20px;
            height: 20px;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 50%;
            transition: all 0.2s;
            
            &:hover {
                color: #f56c6c;
                background: #fef0f0;
            }
            
            &:disabled {
                opacity: 0.2;
                cursor: not-allowed;
            }
        }
        
        &:hover .delete-row-btn {
            opacity: 1;
        }
    }
    
    &.data-cell {
        position: relative;
        cursor: pointer;
        word-break: break-word;
        white-space: normal;
        text-align: center;
        
        .cell-content {
            width: 100%;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        
        .cell-input {
            width: 100%;
            height: 100%;
            border: 1px solid #409eff;
            border-radius: 2px;
            padding: 4px 6px;
            font-size: inherit;
            box-sizing: border-box;
            outline: none;
            background: #fff;
        }
        
        &.editing {
            padding: 0;
        }
        
        &.selected {
            outline: 2px solid #409eff;
            outline-offset: -2px;
            z-index: 1;
        }
        
        &:hover {
            background: #f5f7fa;
        }
    }
    
    &.add-column-cell,
    &.add-row-cell {
        display: flex;
        align-items: center;
        justify-content: center;
        background: #f5f7fa;
        cursor: pointer;
        flex-shrink: 0;
        
        button {
            width: 24px;
            height: 24px;
            border: 1px solid #dcdfe6;
            background: white;
            border-radius: 50%;
            font-size: 16px;
            cursor: pointer;
            color: #909399;
            transition: all 0.2s;
            
            &:hover {
                background: #ecf5ff;
                border-color: #b3d8ff;
                color: #409eff;
            }
        }
    }
}

.add-row {
    .add-row-cell {
        width: 60px;
        border-right: 2px solid #dcdfe6;
    }
}

.table-statusbar {
    padding: 6px 12px;
    background: $stress-background-color;
    border-radius: 4px;
    margin-top: 12px;
    font-size: 12px;
    color: #666;
    @include controller-style;
}
</style>