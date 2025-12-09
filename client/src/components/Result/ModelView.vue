<script setup lang="ts">
import { computed } from 'vue';
import type { ResultType } from '@/stores/resultStore';
import type { ModelView as ModelViewType } from '@/utils/api';
import type { server__models__schema__ModelSchema__Type } from '@/utils/api/models/server__models__schema__ModelSchema__Type';
import type { ColType } from '@/utils/api/models/ColType';

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
            <span>加载中...</span>
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

            <!-- 输入列信息 -->
            <div class="model-columns-section">
                <h3>输入列信息</h3>
                <div v-if="modelData.metadata.input_cols && Object.keys(modelData.metadata.input_cols).length > 0" class="columns-container">
                    <div class="columns-grid">
                        <div 
                            v-for="(colType, colName) in modelData.metadata.input_cols" 
                            :key="colName" 
                            class="column-item"
                        >
                            <span class="column-name">{{ colName }}</span>
                            <span class="column-type">{{ getColumnTypeDescription(colType) }}</span>
                        </div>
                    </div>
                </div>
                <div v-else class="no-columns">
                    无输入列信息
                </div>
            </div>

            <!-- 输出列信息 -->
            <div class="model-columns-section">
                <h3>输出列信息</h3>
                <div v-if="modelData.metadata.output_cols && Object.keys(modelData.metadata.output_cols).length > 0" class="columns-container">
                    <div class="columns-grid">
                        <div 
                            v-for="(colType, colName) in modelData.metadata.output_cols" 
                            :key="colName" 
                            class="column-item"
                        >
                            <span class="column-name">{{ colName }}</span>
                            <span class="column-type">{{ getColumnTypeDescription(colType) }}</span>
                        </div>
                    </div>
                </div>
                <div v-else class="no-columns">
                    无输出列信息
                </div>
            </div>
        </div>
    </div>
</template>

<style scoped lang="scss">
.model-view-container {
    display: flex;
    flex-direction: column;
    height: 100%;
    width: 100%;
    padding: 16px;
    box-sizing: border-box;
    background: #fafafa;
    border-radius: 4px;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;

    .model-loading,
    .model-error {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 100%;
        font-size: 16px;
        color: #666;
    }

    .model-error {
        color: #f44336;
    }

    .model-content-wrapper {
        display: flex;
        flex-direction: column;
        gap: 24px;

        .model-info-section,
        .model-columns-section {
            background: white;
            border-radius: 8px;
            padding: 16px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);

            h3 {
                margin-top: 0;
                margin-bottom: 16px;
                color: #333;
                font-size: 18px;
                font-weight: 600;
                border-bottom: 1px solid #eee;
                padding-bottom: 8px;
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

            .columns-container {
                .columns-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
                    gap: 12px;

                    .column-item {
                        display: flex;
                        flex-direction: column;
                        padding: 12px;
                        background: #f5f5f5;
                        border-radius: 6px;
                        transition: all 0.2s ease;

                        &:hover {
                            background: #e9e9e9;
                            transform: translateY(-2px);
                            box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
                        }

                        .column-name {
                            font-weight: 500;
                            color: #333;
                            margin-bottom: 4px;
                            word-break: break-all;
                        }

                        .column-type {
                            font-size: 12px;
                            color: #666;
                            background: #e0e0e0;
                            padding: 2px 6px;
                            border-radius: 4px;
                            align-self: flex-start;
                        }
                    }
                }
            }

            .no-columns {
                color: #999;
                font-style: italic;
                padding: 16px;
                text-align: center;
            }
        }
    }
}
</style>