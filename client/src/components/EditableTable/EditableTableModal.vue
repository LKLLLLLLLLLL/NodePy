<script setup lang="ts">
import EditableTable from './EditableTable.vue';
import { useTableStore } from '@/stores/tableStore';
import { useModalStore } from '@/stores/modalStore';
import { ref, watch } from 'vue';

const tableStore = useTableStore();
const modalStore = useModalStore();

// 表格尺寸输入
const targetRows = ref<number>(tableStore.numRows);
const targetCols = ref<number>(tableStore.numCols);

// 监听表格尺寸变化
watch(() => tableStore.numRows, (newVal) => {
    targetRows.value = newVal;
});

watch(() => tableStore.numCols, (newVal) => {
    targetCols.value = newVal;
});

/**
 * 应用结构调整
 */
function applyStructureChange() {
    const rows = parseInt(String(targetRows.value));
    const cols = parseInt(String(targetCols.value));
    
    if (isNaN(rows) || isNaN(cols) || rows < 1 || cols < 1) {
        alert('请输入有效的行数和列数');
        return;
    }
    
    tableStore.resizeTable(rows, cols);
}

/**
 * 提交表格编辑
 */
function submit() {
    tableStore.applyChanges();
}

/**
 * 取消表格编辑
 */
function cancel() {
    tableStore.cancelEdit();
}

/**
 * 添加新列（在末尾添加）
 */
function addNewColumn() {
    const colName = prompt('请输入新列名:', `Column_${tableStore.numCols + 1}`);
    if (colName) {
        const colType = prompt('请选择列类型 (int, float, str, bool, Datetime):', 'str');
        if (colType && ['int', 'float', 'str', 'bool', 'Datetime'].includes(colType)) {
            tableStore.addColumn(colName, colType as any, -1); // -1 表示在末尾添加
        }
    }
}

/**
 * 在指定位置添加新列
 */
function addColumnAtPosition(position: number) {
    const colName = prompt('请输入新列名:', `Column_${tableStore.numCols + 1}`);
    if (colName) {
        const colType = prompt('请选择列类型 (int, float, str, bool, Datetime):', 'str');
        if (colType && ['int', 'float', 'str', 'bool', 'Datetime'].includes(colType)) {
            tableStore.addColumn(colName, colType as any, position);
        }
    }
}
</script>

<template>
    <div class="editable-table-modal">
        <!-- 顶部工具栏 -->
        <div class="modal-toolbar">
            <div class="toolbar-section">
                <h3>表格编辑器</h3>
                <div class="table-info">
                    当前尺寸: {{ tableStore.numRows }} 行 × {{ tableStore.numCols }} 列
                </div>
            </div>
            
            <div class="toolbar-section">
                <button @click="tableStore.undo" :disabled="!tableStore.canUndo" class="toolbar-btn">
                    ↶ 撤销 (Ctrl+Z)
                </button>
                <button @click="tableStore.redo" :disabled="!tableStore.canRedo" class="toolbar-btn">
                    ↷ 重做 (Ctrl+Y)
                </button>
            </div>
        </div>
        
        <!-- 表格尺寸控制 -->
        <div class="size-controls">
            <div class="control-group">
                <label>行数:</label>
                <input 
                    type="number" 
                    v-model.number="targetRows" 
                    min="1" 
                    max="1000"
                    class="size-input"
                />
            </div>
            
            <div class="control-group">
                <label>列数:</label>
                <input 
                    type="number" 
                    v-model.number="targetCols" 
                    min="1" 
                    max="100"
                    class="size-input"
                />
            </div>
            
            <button @click="applyStructureChange" class="apply-btn">
                应用尺寸
            </button>
            
            <button @click="addNewColumn" class="add-column-btn">
                + 添加列
            </button>
        </div>
        
        <!-- 编辑说明 -->
        <div class="instructions">
            <div class="instruction-item">
                <strong>编辑说明:</strong>
            </div>
            <div class="instruction-item">
                <span class="bullet">•</span>
                双击单元格编辑内容
            </div>
            <div class="instruction-item">
                <span class="bullet">•</span>
                双击列名重命名列
            </div>
            <div class="instruction-item">
                <span class="bullet">•</span>
                右键列名更改列类型
            </div>
            <div class="instruction-item">
                <span class="bullet">•</span>
                鼠标悬停在行号/列名显示删除按钮
            </div>
            <div class="instruction-item">
                <span class="bullet">•</span>
                使用 Tab/Enter 键快速导航
            </div>
        </div>
        
        <!-- 可编辑表格 -->
        <div class="table-container">
            <EditableTable 
                :data="tableStore.currentTableData"
                :noC="tableStore.numCols"
                :noR="tableStore.numRows"
            />
        </div>
        
        <!-- 底部操作按钮 -->
        <div class="modal-footer">
            <div class="footer-left">
                <span class="hint">
                    提示: 修改会实时保存到节点参数
                </span>
            </div>
            
            <div class="footer-right">
                <button @click="cancel" class="cancel-btn">
                    取消
                </button>
                <button @click="submit" class="submit-btn">
                    确定
                </button>
            </div>
        </div>
    </div>
</template>

<style lang="scss" scoped>
.editable-table-modal {
    display: flex;
    flex-direction: column;
    height: 100%;
    background: #f8f9fa;
    padding: 16px;
}

.modal-toolbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;
    padding-bottom: 12px;
    border-bottom: 1px solid #dee2e6;
    
    .toolbar-section {
        display: flex;
        align-items: center;
        gap: 16px;
        
        h3 {
            margin: 0;
            color: #343a40;
        }
        
        .table-info {
            font-size: 14px;
            color: #6c757d;
            background: #e9ecef;
            padding: 4px 8px;
            border-radius: 4px;
        }
    }
    
    .toolbar-btn {
        padding: 6px 12px;
        border: 1px solid #ced4da;
        background: white;
        border-radius: 4px;
        cursor: pointer;
        font-size: 13px;
        
        &:hover:not(:disabled) {
            background: #e9ecef;
        }
        
        &:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
    }
}

.size-controls {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 16px;
    padding: 12px;
    background: white;
    border-radius: 6px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    
    .control-group {
        display: flex;
        align-items: center;
        gap: 8px;
        
        label {
            font-size: 14px;
            font-weight: 500;
            color: #495057;
        }
        
        .size-input {
            width: 80px;
            padding: 6px 8px;
            border: 1px solid #ced4da;
            border-radius: 4px;
            font-size: 14px;
            
            &:focus {
                outline: none;
                border-color: #80bdff;
                box-shadow: 0 0 0 0.2rem rgba(0,123,255,.25);
            }
        }
    }
    
    .apply-btn, .add-column-btn {
        padding: 6px 12px;
        border: 1px solid #007bff;
        background: #007bff;
        color: white;
        border-radius: 4px;
        cursor: pointer;
        font-size: 14px;
        
        &:hover:not(:disabled) {
            background: #0069d9;
            border-color: #0062cc;
        }
        
        &:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
    }
    
    .add-column-btn {
        background: #28a745;
        border-color: #28a745;
        
        &:hover:not(:disabled) {
            background: #218838;
            border-color: #1e7e34;
        }
    }
}

.instructions {
    margin-bottom: 16px;
    padding: 12px;
    background: white;
    border-radius: 6px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    
    .instruction-item {
        display: flex;
        align-items: center;
        margin-bottom: 4px;
        font-size: 13px;
        color: #495057;
        
        &:last-child {
            margin-bottom: 0;
        }
        
        .bullet {
            margin-right: 8px;
            color: #007bff;
        }
    }
}

.table-container {
    flex: 1;
    overflow: hidden;
    border: 1px solid #dee2e6;
    border-radius: 6px;
    background: white;
}

.modal-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 16px;
    
    .footer-left {
        .hint {
            font-size: 13px;
            color: #6c757d;
        }
    }
    
    .footer-right {
        display: flex;
        gap: 8px;
        
        .cancel-btn, .submit-btn {
            padding: 8px 16px;
            border: 1px solid #6c757d;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
            
            &:hover:not(:disabled) {
                opacity: 0.8;
            }
            
            &:disabled {
                opacity: 0.5;
                cursor: not-allowed;
            }
        }
        
        .cancel-btn {
            background: white;
            color: #6c757d;
        }
        
        .submit-btn {
            background: #007bff;
            border-color: #007bff;
            color: white;
        }
    }
}
</style>