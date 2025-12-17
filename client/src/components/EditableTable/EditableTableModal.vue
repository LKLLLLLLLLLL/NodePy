<script setup lang="ts">
import EditableTable from './EditableTable.vue';
import { useTableStore } from '@/stores/tableStore';
import { useModalStore } from '@/stores/modalStore';
import { ref, watch, onMounted, onUnmounted } from 'vue';

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
    tableStore.confirmChanges();
}

/**
 * 取消表格编辑
 */
function cancel() {
    tableStore.cancelChanges();
}

/**
 * 处理键盘事件
 */
function handleKeyDown(event: KeyboardEvent) {
    // 检查是否按下了 Ctrl+S
    if (event.ctrlKey && event.key === 's') {
        event.preventDefault(); // 阻止浏览器默认保存页面的行为
        submit(); // 执行提交操作
    }
    
    // 检查是否按下了 Escape 键
    if (event.key === 'Escape') {
        cancel(); // 取消编辑
    }
}

// 添加键盘事件监听
onMounted(() => {
    document.addEventListener('keydown', handleKeyDown);
});

// 移除键盘事件监听
onUnmounted(() => {
    document.removeEventListener('keydown', handleKeyDown);
});

</script>

<template>
    <div class="editable-table-modal">
        <!-- 表格尺寸控制 -->
        <!-- <div class="size-controls">
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
        </div> -->
        
        <!-- 编辑说明 -->
        <!-- <div class="instructions">
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
        </div> -->
        
        <!-- 可编辑表格 -->
        <div class="table-container">
            <EditableTable 
                :data="tableStore.currentTableData"
                :noC="tableStore.numCols"
                :noR="tableStore.numRows"
            />
        </div>
        
        <!-- 底部操作按钮 -->
        <!-- <div class="modal-footer">
            <div class="footer-left">
                <span class="hint">
                    提示: 修改会在确定后保存到节点参数
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
        </div> -->
    </div>
</template>

<style lang="scss" scoped>
@use "../../common/global.scss" as *;

.editable-table-modal {
    display: flex;
    flex-direction: column;
    overflow: auto;
    height: 100%;
    width: 100%;
    background: $background-color;
    padding: 16px;
    box-sizing: border-box;
}

// .size-controls {
//     display: flex;
//     align-items: center;
//     gap: 12px;
//     margin-bottom: 16px;
//     padding: 12px;
//     background: $stress-background-color;
//     border-radius: 6px;
//     box-shadow: 0 1px 3px rgba(0,0,0,0.1);
//     @include controller-style;
    
//     .control-group {
//         display: flex;
//         align-items: center;
//         gap: 8px;
        
//         label {
//             font-size: 14px;
//             font-weight: 500;
//             color: #495057;
//         }
        
//         .size-input {
//             width: 80px;
//             padding: 6px 8px;
//             border: 1px solid #ced4da;
//             border-radius: 4px;
//             font-size: 14px;
            
//             &:focus {
//                 outline: none;
//                 border-color: #80bdff;
//                 box-shadow: 0 0 0 0.2rem rgba(0,123,255,.25);
//             }
//         }
//     }
    
//     .apply-btn {
//         padding: 6px 12px;
//         border: 1px solid $stress-color;
//         background: $stress-color;
//         color: white;
//         border-radius: 4px;
//         cursor: pointer;
//         font-size: 14px;
//         @include confirm-button-style;
        
//         &:hover:not(:disabled) {
//             background: $hover-stress-color;
//             border-color: $hover-stress-color;
//         }
        
//         &:disabled {
//             opacity: 0.5;
//             cursor: not-allowed;
//         }
//     }
// }

// .instructions {
//     margin-bottom: 16px;
//     padding: 12px;
//     background: $stress-background-color;
//     border-radius: 6px;
//     box-shadow: 0 1px 3px rgba(0,0,0,0.1);
//     @include controller-style;
    
//     .instruction-item {
//         display: flex;
//         align-items: center;
//         margin-bottom: 4px;
//         font-size: 13px;
//         color: #495057;
        
//         &:last-child {
//             margin-bottom: 0;
//         }
        
//         .bullet {
//             margin-right: 8px;
//             color: $stress-color;
//         }
//     }
// }

.table-container {
    display: flex;
    flex-direction: column;
    flex: 1;
    overflow: auto;
    border: 1px solid #dee2e6;
    border-radius: 10px;
    background: white;
    // padding-bottom: 10px;
    // padding-left: 10px;
    // padding-right: 10px;
    @include controller-style;
}

// .modal-footer {
//     display: flex;
//     justify-content: space-between;
//     align-items: center;
//     margin-top: 16px;
    
//     .footer-left {
//         .hint {
//             font-size: 13px;
//             color: #6c757d;
//         }
//     }
    
//     .footer-right {
//         display: flex;
//         gap: 8px;
        
//         .cancel-btn, .submit-btn {
//             padding: 8px 16px;
//             border-radius: 4px;
//             cursor: pointer;
//             font-size: 14px;
//             @include confirm-button-style;
            
//             &:hover:not(:disabled) {
//                 opacity: 0.8;
//             }
            
//             &:disabled {
//                 opacity: 0.5;
//                 cursor: not-allowed;
//             }
//         }
        
//         .cancel-btn {
//             background: #f8f9fa;
//             color: #6c757d;
//             border: 1px solid #e9ecef;
//             @include cancel-button-style;
            
//             &:hover {
//                 @include cancel-button-hover-style;
//             }
//         }
        
//         .submit-btn {
//             background: $stress-color;
//             border-color: $stress-color;
//             color: white;
//             @include confirm-button-style;
            
//             &:hover {
//                 @include confirm-button-hover-style;
//             }
//         }
//     }
// }
</style>