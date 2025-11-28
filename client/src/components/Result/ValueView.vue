<script lang="ts" setup>
    import { computed, ref } from 'vue';
    import Loading from '@/components/Loading.vue'
    import type { ResultType } from '@/stores/resultStore';
    
    const props = defineProps<{
        value: ResultType
    }>()

    // 添加loading和error状态
    const loading = ref(false)
    const error = ref<string>('')

    // 格式化值的显示
    const displayValue = computed(() => {
        if (props.value === null || props.value === undefined) {
            return '无值'
        }
        
        if (typeof props.value === 'boolean') {
            return props.value ? 'True' : 'False'
        }
        
        if (typeof props.value === 'number') {
            // 如果是小数，保留3位小数
            return typeof props.value === 'number' && props.value % 1 !== 0 
                ? props.value.toFixed(3) 
                : String(props.value)
        }
        
        if (typeof props.value === 'string') {
            return props.value
        }
        
        // 其他类型转为字符串
        return String(props.value)
    })

    // 获取值的类型标签
    const valueType = computed(() => {
        if (props.value === null || props.value === undefined) {
            return 'null'
        }
        if (typeof props.value === 'boolean') {
            return 'bool'
        }
        if (typeof props.value === 'number') {
            return Number.isInteger(props.value) ? 'int' : 'float'
        }
        return typeof props.value
    })
    
    // 检查是否为布尔值
    const isBoolean = computed(() => {
        return typeof props.value === 'boolean';
    });
</script>
<template>
    <div class='value-view-container'>
        <!-- 加载中 -->
        <div v-if="loading" class="value-loading">
            <Loading></Loading>
            <span>加载中...</span>
        </div>

        <!-- 错误提示 -->
        <div v-else-if="error" class='value-error'>
            {{ error }}
        </div>

        <!-- 正常显示 -->
        <div v-else>
            <div class='value-header'>
                <span class='value-type'>{{ valueType }}</span>
            </div>
            <div class='value-content' :class="{ 'boolean-true': isBoolean && value === true, 'boolean-false': isBoolean && value === false }">
                {{ displayValue }}
            </div>
        </div>
    </div>
</template>
<style scoped lang="scss">
    .value-view-container {
        display: flex;
        flex-direction: column;
        height: 100%;
        width: 100%;
        padding: 16px;
        box-sizing: border-box;
        background: #fafafa;
        border-radius: 4px;
    }

    .value-loading {
        flex: 1;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        gap: 12px;
        color: #909399;
        font-size: 14px;
    }

    .value-error {
        flex: 1;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #f56c6c;
        background: #fef0f0;
        border: 1px solid #fde2e2;
        border-radius: 4px;
        font-size: 14px;
        padding: 16px;
        margin: 16px;
    }

    .value-header {
        margin-bottom: 12px;
        font-size: 12px;
        color: #909399;
    }

    .value-type {
        display: inline-block;
        padding: 2px 8px;
        background: #e4e7eb;
        border-radius: 2px;
        font-weight: 500;
    }

    .value-content {
        flex: 1;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 32px;
        font-weight: 500;
        color: #303133;
        word-break: break-all;
        text-align: center;
        line-height: 1.6;
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