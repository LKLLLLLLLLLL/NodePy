import { defineStore } from 'pinia'
import { useModalStore } from './modalStore';
import { useGraphStore } from './graphStore';
import { ref, computed } from 'vue';
import EditableTableModal from '@/components/EditableTable/EditableTableModal.vue';
import { useVueFlow } from '@vue-flow/core';

// 表格单元格数据类型
export type TableCellValue = string | number | boolean | null;

// 表格行数据类型
export interface TableRowData {
  [key: string]: TableCellValue;
}

// 表格数据结构
export interface TableData {
  rows: TableRowData[];
  colNames: string[];
  colTypes: { [key: string]: 'int' | 'float' | 'str' | 'bool' | 'Datetime' };
}

export const useTableStore = defineStore('table', () => {
    const modalStore = useModalStore();
    const graphStore = useGraphStore();
    const { findNode } = useVueFlow('main');

    // 模态框尺寸
    const modalWidth = 800;
    const modalHeight = 600;

    // 默认表格数据
    const defaultTableData: TableData = {
        rows: [
            { "A": 1, "B": 2, "C": 3 },
            { "A": 4, "B": 5, "C": 6 },
            { "A": 7, "B": 8, "C": 9 }
        ],
        colNames: ['A', 'B', 'C'],
        colTypes: {
            'A': 'int',
            'B': 'int',
            'C': 'int'
        }
    };

    // 当前编辑的表格数据
    const currentTableData = ref<TableData>({ ...defaultTableData });
    
    // 正在编辑的表格节点ID
    const editingNodeId = ref<string>('');
    
    // 表格的临时修改（用于撤销/重做）
    const historyStack = ref<TableData[]>([]);
    const redoStack = ref<TableData[]>([]);
    const maxHistorySize = 20;

    // 当前选中的单元格位置
    const selectedCell = ref<{ row: number; col: number } | null>(null);
    
    // 是否正在编辑单元格
    const isEditingCell = ref<boolean>(false);

    /**
     * 初始化表格编辑
     * @param nodeId 节点ID
     * @param initialData 初始表格数据
     */
    function initTableEdit(nodeId: string, initialData?: TableData) {
        editingNodeId.value = nodeId;
        
        if (initialData) {
            currentTableData.value = { ...initialData };
        } else {
            // 获取节点当前数据
            const node = findNode(nodeId);
            if (node?.data?.param) {
                try {
                    // 解析节点参数中的表格数据
                    const param = node.data.param;
                    currentTableData.value = {
                        rows: param.rows || defaultTableData.rows,
                        colNames: param.col_names || defaultTableData.colNames,
                        colTypes: param.col_types || defaultTableData.colTypes
                    };
                } catch (error) {
                    console.error('解析表格数据失败:', error);
                    currentTableData.value = { ...defaultTableData };
                }
            } else {
                currentTableData.value = { ...defaultTableData };
            }
        }
        
        // 清空历史记录
        historyStack.value = [];
        redoStack.value = [];
        saveToHistory();
        
        // 打开编辑模态框
        createTableModal();
    }

    /**
     * 保存当前状态到历史记录
     */
    function saveToHistory() {
        historyStack.value.push(JSON.parse(JSON.stringify(currentTableData.value)));
        if (historyStack.value.length > maxHistorySize) {
            historyStack.value.shift();
        }
        redoStack.value = []; // 清除重做栈
    }

    /**
     * 撤销操作
     */
    function undo() {
        if (historyStack.value.length > 1) {
            redoStack.value.push(JSON.parse(JSON.stringify(currentTableData.value)));
            historyStack.value.pop();
            currentTableData.value = JSON.parse(JSON.stringify(historyStack.value[historyStack.value.length - 1]));
        }
    }

    /**
     * 重做操作
     */
    function redo() {
        if (redoStack.value.length > 0) {
            const state = redoStack.value.pop()!;
            historyStack.value.push(JSON.parse(JSON.stringify(state)));
            currentTableData.value = JSON.parse(JSON.stringify(state));
        }
    }

    /**
     * 添加新行
     * @param position 插入位置（-1表示末尾）
     */
    function addRow(position: number = -1) {
        saveToHistory();
        
        const newRow: TableRowData = {};
        currentTableData.value.colNames.forEach(colName => {
            newRow[colName] = null;
        });
        
        if (position === -1 || position >= currentTableData.value.rows.length) {
            currentTableData.value.rows.push(newRow);
        } else {
            currentTableData.value.rows.splice(position, 0, newRow);
        }
    }

    /**
     * 删除行
     * @param rowIndex 行索引
     */
    function deleteRow(rowIndex: number) {
        if (currentTableData.value.rows.length <= 1) return;
        
        saveToHistory();
        currentTableData.value.rows.splice(rowIndex, 1);
    }

    /**
     * 添加新列
     * @param colName 列名
     * @param colType 列类型
     * @param position 插入位置（-1表示末尾）
     */
    function addColumn(colName: string, colType: 'int' | 'float' | 'str' | 'bool' | 'Datetime' = 'str', position: number = -1) {
        saveToHistory();
        
        // 确保列名唯一
        let uniqueColName = colName;
        let counter = 1;
        while (currentTableData.value.colNames.includes(uniqueColName)) {
            uniqueColName = `${colName}_${counter}`;
            counter++;
        }
        
        // 添加列名和类型
        if (position === -1 || position >= currentTableData.value.colNames.length) {
            currentTableData.value.colNames.push(uniqueColName);
            currentTableData.value.colTypes[uniqueColName] = colType;
        } else {
            currentTableData.value.colNames.splice(position, 0, uniqueColName);
            currentTableData.value.colTypes[uniqueColName] = colType;
        }
        
        // 为每一行添加新列
        currentTableData.value.rows.forEach(row => {
            row[uniqueColName] = null;
        });
    }

    /**
     * 删除列
     * @param colIndex 列索引
     */
    function deleteColumn(colIndex: number) {
        if (currentTableData.value.colNames.length <= 1) return;
        
        saveToHistory();
        const colName = currentTableData.value.colNames[colIndex];
        
        // 从列名列表中删除
        currentTableData.value.colNames.splice(colIndex, 1);
        
        // 从列类型中删除
        delete currentTableData.value.colTypes[colName!];
        
        // 从每一行中删除该列
        currentTableData.value.rows.forEach(row => {
            delete row[colName!];
        });
    }

    /**
     * 更新单元格值
     * @param rowIndex 行索引
     * @param colName 列名
     * @param value 新值
     */
    function updateCell(rowIndex: number, colName: string, value: TableCellValue) {
        if (rowIndex < 0 || rowIndex >= currentTableData.value.rows.length) return;
        if (!currentTableData.value.colNames.includes(colName)) return;
        
        saveToHistory();
        currentTableData.value.rows[rowIndex]![colName] = value;
    }

    /**
     * 更新列名
     * @param oldColName 旧列名
     * @param newColName 新列名
     */
    function updateColumnName(oldColName: string, newColName: string) {
        if (!currentTableData.value.colNames.includes(oldColName)) return;
        if (oldColName === newColName) return;
        
        // 确保新列名唯一
        let uniqueNewName = newColName;
        let counter = 1;
        while (currentTableData.value.colNames.includes(uniqueNewName)) {
            uniqueNewName = `${newColName}_${counter}`;
            counter++;
        }
        
        saveToHistory();
        
        // 更新列名列表
        const colIndex = currentTableData.value.colNames.indexOf(oldColName);
        currentTableData.value.colNames[colIndex] = uniqueNewName;
        
        // 更新列类型映射
        currentTableData.value.colTypes[uniqueNewName] = currentTableData.value.colTypes[oldColName]!;
        delete currentTableData.value.colTypes[oldColName];
        
        // 更新每一行中的数据
        currentTableData.value.rows.forEach(row => {
            row[uniqueNewName] = row[oldColName]!;
            delete row[oldColName];
        });
    }

    /**
     * 更新列类型
     * @param colName 列名
     * @param colType 新类型
     */
    function updateColumnType(colName: string, colType: 'int' | 'float' | 'str' | 'bool' | 'Datetime') {
        if (!currentTableData.value.colNames.includes(colName)) return;
        
        saveToHistory();
        currentTableData.value.colTypes[colName] = colType;
        
        // 根据新类型转换现有数据
        currentTableData.value.rows.forEach(row => {
            const value = row[colName];
            if (value !== null) {
                try {
                    switch (colType) {
                        case 'int':
                            row[colName] = parseInt(String(value), 10);
                            break;
                        case 'float':
                            row[colName] = parseFloat(String(value));
                            break;
                        case 'bool':
                            row[colName] = Boolean(value);
                            break;
                        case 'str':
                            row[colName] = String(value);
                            break;
                        case 'Datetime':
                            // 保持原样或尝试解析日期
                            row[colName] = value!;
                            break;
                    }
                } catch (error) {
                    console.warn(`转换列 ${colName} 的值失败:`, error);
                    row[colName] = null;
                }
            }
        });
    }

    /**
     * 调整表格大小
     * @param numRows 目标行数
     * @param numCols 目标列数
     */
    function resizeTable(numRows: number, numCols: number) {
        if (numRows < 1 || numCols < 1) return;
        
        saveToHistory();
        
        // 调整行数
        const currentRows = currentTableData.value.rows.length;
        if (numRows > currentRows) {
            // 添加新行
            for (let i = currentRows; i < numRows; i++) {
                addRow();
            }
        } else if (numRows < currentRows) {
            // 删除多余行（从末尾开始删除）
            for (let i = currentRows - 1; i >= numRows; i--) {
                deleteRow(i);
            }
        }
        
        // 调整列数
        const currentCols = currentTableData.value.colNames.length;
        if (numCols > currentCols) {
            // 添加新列
            for (let i = currentCols; i < numCols; i++) {
                addColumn(`Column_${i + 1}`);
            }
        } else if (numCols < currentCols) {
            // 删除多余列（从末尾开始删除）
            for (let i = currentCols - 1; i >= numCols; i--) {
                deleteColumn(i);
            }
        }
    }

    /**
     * 应用表格修改到节点
     */
    function applyChanges() {
        
    }

    /**
     * 取消表格编辑
     */
    function cancelEdit() {
        modalStore.deactivateModal('table-modal');
        modalStore.destroyModal('table-modal');
        
        // 重置状态
        editingNodeId.value = '';
        currentTableData.value = { ...defaultTableData };
        historyStack.value = [];
        redoStack.value = [];
    }

    /**
     * 创建表格编辑模态框
     */
    function createTableModal() {
        modalStore.createModal({
            component: EditableTableModal,
            title: '编辑表格',
            isActive: true,
            isResizable: true,
            isDraggable: true,
            position: {
                x: window.innerWidth / 2 - modalWidth / 2,
                y: window.innerHeight / 2 - modalHeight / 2
            },
            size: {
                width: modalWidth,
                height: modalHeight
            },
            minSize: {
                width: 600,
                height: 400
            },
            id: 'table-modal',
        });
    }
    
    /**
     * 获取表格的二维数组表示（用于显示）
     */
    const tableArray = computed(() => {
        const result: TableCellValue[][] = [];
        
        // 第一行是列名
        result.push([...currentTableData.value.colNames]);
        
        // 后续行是数据
        currentTableData.value.rows.forEach(row => {
            const rowData: TableCellValue[] = [];
            currentTableData.value.colNames.forEach(colName => {
                rowData.push(row[colName]!);
            });
            result.push(rowData);
        });
        
        return result;
    });
    
    /**
     * 获取列类型列表
     */
    const columnTypes = computed(() => {
        return currentTableData.value.colNames.map(colName => 
            currentTableData.value.colTypes[colName] || 'str'
        );
    });
    
    return {
        // 状态
        currentTableData,
        editingNodeId,
        selectedCell,
        isEditingCell,
        tableArray,
        columnTypes,
        
        // 计算属性
        numRows: computed(() => currentTableData.value.rows.length),
        numCols: computed(() => currentTableData.value.colNames.length),
        canUndo: computed(() => historyStack.value.length > 1),
        canRedo: computed(() => redoStack.value.length > 0),
        
        // 方法
        initTableEdit,
        saveToHistory,
        undo,
        redo,
        addRow,
        deleteRow,
        addColumn,
        deleteColumn,
        updateCell,
        updateColumnName,
        updateColumnType,
        resizeTable,
        applyChanges,
        cancelEdit,
        createTableModal
    }
});