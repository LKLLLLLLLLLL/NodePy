<script lang="ts" setup>
    import { computed } from 'vue';
    
    const props = defineProps<{
        value: any
    }>()

    // 格式化值的显示
    const displayValue = computed(() => {
        if (props.value === null || props.value === undefined) {
            return '无值'
        }
        
        if (typeof props.value === 'boolean') {
            return props.value ? '是' : '否'
        }
        
        if (typeof props.value === 'number') {
            // 如果是小数，保留2位小数
            return typeof props.value === 'number' && props.value % 1 !== 0 
                ? props.value.toFixed(2) 
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
</script>
<template>
    <div class='value-view-container'>
        <div class='value-header'>
            <span class='value-type'>{{ valueType }}</span>
        </div>
        <div class='value-content'>
            {{ displayValue }}
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
</style>