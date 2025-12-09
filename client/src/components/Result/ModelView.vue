<script setup lang="ts">
import { computed } from 'vue';
import type { ResultType } from '@/stores/resultStore';
import type { ModelView as ModelViewType } from '@/utils/api';
import type { server__models__schema__ModelSchema__Type } from '@/utils/api/models/server__models__schema__ModelSchema__Type';
import type { ColType } from '@/utils/api/models/ColType';
import { ElDivider } from 'element-plus';
import Loading from '@/components/Loading.vue';

const props = defineProps<{
    value: ResultType
}>()

// 类型守卫：检查是否是 ModelView
const isModelView = computed(() => {
    return (
        typeof props.value === 'object' &&
        props.value !== null &&
        'model' in props.value &&
        'metadata' in props.value
    )
})

// 获取模型数据
const modelData = computed<ModelViewType | null>(() => {
    if (!isModelView.value) {
        return null;
    }
    return props.value as ModelViewType;
})

// 获取模型类型描述
const modelTypeDescription = computed(() => {
    const modelType = modelData.value!.metadata?.model_type;
    switch (modelType) {
        case 'Regression':
            return '回归模型';
        case 'Classification':
            return '分类模型';
        case undefined:
            return '未知类型';
        default:
            return modelType;
    }
})

// 获取列类型描述
const getColumnTypeDescription = (colType: ColType) => {
    switch (colType) {
        case 'int':
            return '整数';
        case 'float':
            return '浮点数';
        case 'str':
            return '字符串';
        case 'bool':
            return '布尔值';
        case 'Datetime':
            return '日期时间';
        default:
            return colType;
    }
}
</script>

<template>
    <div class='model-view-container'>
        <!-- 加载中 -->
        <div v-if="!modelData" class="model-loading">
            <Loading></Loading>
        </div>

        <!-- 无效数据提示 -->
        <div v-else-if="!isModelView" class='model-error'>
            无效的模型数据
        </div>

        <!-- 模型信息展示 -->
        <div v-else class="model-content-wrapper">
            <!-- 模型基本信息 -->
            <div class="model-info-section">
                <h3>模型信息</h3>
                <div class="info-item">
                    <span class="info-label">模型类型:</span>
                    <span class="info-value">{{ modelTypeDescription }}</span>
                </div>
            </div>

            <ElDivider />

            <!-- 输入列信息 -->
            <div class="model-columns-section">
                <h3>输入列信息</h3>
                <table v-if="modelData.metadata.input_cols && Object.keys(modelData.metadata.input_cols).length > 0" class="columns-table">
                    <thead>
                        <tr>
                            <th>列名</th>
                            <th>类型</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="(colType, colName) in modelData.metadata.input_cols" :key="colName">
                            <td>{{ colName }}</td>
                            <td>{{ getColumnTypeDescription(colType) }}</td>
                        </tr>
                    </tbody>
                </table>
                <div v-else class="no-columns">
                    无输入列信息
                </div>
            </div>

            <ElDivider />

            <!-- 输出列信息 -->
            <div class="model-columns-section">
                <h3>输出列信息</h3>
                <table v-if="modelData.metadata.output_cols && Object.keys(modelData.metadata.output_cols).length > 0" class="columns-table">
                    <thead>
                        <tr>
                            <th>列名</th>
                            <th>类型</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="(colType, colName) in modelData.metadata.output_cols" :key="colName">
                            <td>{{ colName }}</td>
                            <td>{{ getColumnTypeDescription(colType) }}</td>
                        </tr>
                    </tbody>
                </table>
                <div v-else class="no-columns">
                    无输出列信息
                </div>
            </div>
        </div>
    </div>
</template>

<style scoped lang="scss">
@use '@/common/global.scss' as *;

.model-view-container {
    display: flex;
    flex-direction: column;
    height: 100%;
    width: 100%;
    padding: 16px;
    box-sizing: border-box;
    background: $background-color;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
    border-radius: 10px;
}

.model-loading {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100%;
    gap: 12px;
    color: #909399;
    font-size: 14px;
}

.model-error {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100%;
    font-size: 16px;
    color: #666;
}

.model-error {
    color: $error-message-color;
    background: $stress-background-color;
    border-radius: 10px;
    margin: 16px;
    padding: 16px;
    @include controller-style;
}

.model-content-wrapper {
    display: flex;
    flex-direction: column;
    background: $stress-background-color;
    border-radius: 10px;
    padding: 16px;
    box-sizing: border-box;
    @include controller-style;
}

.model-info-section {
    padding: 16px 0;

    h3 {
        margin-top: 0;
        margin-bottom: 16px;
        color: #333;
        font-size: 18px;
        font-weight: 600;
    }

    .info-item {
        display: flex;
        align-items: center;
        margin-bottom: 8px;

        .info-label {
            font-weight: 500;
            color: #555;
            width: 100px;
            margin-right: 16px;
        }

        .info-value {
            color: #333;
            font-weight: 400;
        }
    }
}

.model-columns-section {
    padding: 16px 0;

    h3 {
        margin-top: 0;
        margin-bottom: 16px;
        color: #333;
        font-size: 18px;
        font-weight: 600;
    }

    .columns-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 13px;
        background: #fff;
        border: 1px solid #ebeef5;
        border-radius: 4px;
        overflow: hidden;
        margin: 12px 0;

        thead {
            background: #f5f7fa;
        }

        th {
            padding: 12px 8px;
            text-align: center;
            border-bottom: 2px solid #ebeef5;
            font-weight: 600;
            color: #303133;
        }

        td {
            padding: 10px 8px;
            text-align: center;
            background: #fafafa;
            border-bottom: 1px solid #ebeef5;
            color: #606266;
        }

        /* 移除最后一行的下边框 */
        tr:last-child td {
            border-bottom: none;
        }

        tr:hover {
            background-color: #f5f7fa;
        }
    }

    .no-columns {
        color: #999;
        font-style: italic;
        padding: 16px;
        text-align: center;
    }
}

:deep(.el-divider) {
    margin: 16px 0;
}
</style>