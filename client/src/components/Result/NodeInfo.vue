<script lang="ts" setup>
    import { computed } from 'vue';

    const props = defineProps<{
        data: any
    }>()

    // 获取节点信息
    const nodeInfo = computed(() => {
        if (!props.data) {
            return null
        }
        return props.data
    })

    // 获取数据输出信息
    const dataOutInfo = computed(() => {
        if (!props.data?.data_out) {
            return []
        }

        const dataOut = props.data.data_out
        const info: Array<{ key: string; value: any; dataId: number | null }> = []

        // 遍历所有可能的输出类型
        const outputTypes = ['plot', 'const', 'file', 'table']
        outputTypes.forEach(type => {
            if (dataOut[type]) {
                info.push({
                    key: type,
                    value: dataOut[type],
                    dataId: dataOut[type].data_id || null
                })
            }
        })

        return info
    })

    // 获取节点类型
    const nodeType = computed(() => {
        return props.data?.type || 'Unknown'
    })

    // 获取节点 ID
    const nodeId = computed(() => {
        return props.data?.id || 'N/A'
    })

    // 获取执行状态
    const executionStatus = computed(() => {
        if (!props.data?.data_out) {
            return 'pending'
        }
        return 'executed'
    })

    // 格式化输出信息
    function formatOutputInfo(info: any): string {
        if (!info) return '-'
        return JSON.stringify(info, null, 2)
    }
</script>
<template>
    <div class="nodeinfo-container" v-if="nodeInfo">
        <!-- 节点基本信息 -->
        <div class='info-section'>
            <div class='section-title'>节点信息</div>
            <div class='info-item'>
                <span class='info-label'>类型:</span>
                <span class='info-value'>{{ nodeType }}</span>
            </div>
            <div class='info-item'>
                <span class='info-label'>ID:</span>
                <span class='info-value info-id'>{{ nodeId }}</span>
            </div>
            <div class='info-item'>
                <span class='info-label'>状态:</span>
                <span class='info-value' :class="'status-' + executionStatus">{{ executionStatus === 'executed' ? '已执行' : '待执行' }}</span>
            </div>
        </div>

        <!-- 数据输出信息 -->
        <div class='info-section' v-if="dataOutInfo.length > 0">
            <div class='section-title'>数据输出</div>
            <div v-for="output in dataOutInfo" :key="output.key" class='output-item'>
                <div class='output-header'>
                    <span class='output-type'>{{ output.key }}</span>
                    <span v-if="output.dataId" class='output-id'>数据ID: {{ output.dataId }}</span>
                </div>
                <div class='output-details'>
                    <pre>{{ formatOutputInfo(output.value) }}</pre>
                </div>
            </div>
        </div>

        <!-- 无数据提示 -->
        <div v-else class='no-data'>
            节点尚未执行，暂无数据输出
        </div>
    </div>
    <div v-else class='nodeinfo-container no-data'>
        无节点信息
    </div>
</template>
<style lang="scss" scoped>
    .nodeinfo-container {
        height: 100%;
        width: 100%;
        padding: 12px;
        box-sizing: border-box;
        overflow-y: auto;
        background: #fafafa;
        color: #303133;
        font-size: 13px;
    }

    .info-section {
        margin-bottom: 16px;
        padding: 12px;
        background: #fff;
        border-radius: 4px;
        border: 1px solid #ebeef5;
    }

    .section-title {
        font-weight: 600;
        color: #303133;
        margin-bottom: 8px;
        padding-bottom: 8px;
        border-bottom: 2px solid #f0f0f0;
    }

    .info-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 6px 0;
        line-height: 1.6;
    }

    .info-label {
        font-weight: 500;
        color: #606266;
        min-width: 60px;
    }

    .info-value {
        color: #303133;
        word-break: break-all;
        margin-left: 8px;
    }

    .info-id {
        font-family: 'Courier New', monospace;
        background: #f0f0f0;
        padding: 2px 6px;
        border-radius: 2px;
        font-size: 12px;
    }

    .status-executed {
        color: #67c23a;
        font-weight: 500;
    }

    .status-pending {
        color: #e6a23c;
        font-weight: 500;
    }

    .output-item {
        margin-bottom: 12px;
        padding: 10px;
        background: #f9f9f9;
        border-left: 3px solid #409eff;
        border-radius: 2px;
    }

    .output-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 8px;
    }

    .output-type {
        font-weight: 600;
        color: #409eff;
        text-transform: uppercase;
    }

    .output-id {
        font-size: 12px;
        color: #909399;
    }

    .output-details {
        overflow-x: auto;
    }

    pre {
        margin: 0;
        padding: 8px;
        background: #fff;
        border: 1px solid #ebeef5;
        border-radius: 2px;
        font-size: 11px;
        font-family: 'Courier New', monospace;
        color: #606266;
        white-space: pre-wrap;
        word-break: break-word;
    }

    .no-data {
        display: flex;
        align-items: center;
        justify-content: center;
        min-height: 100px;
        color: #909399;
        text-align: center;
        background: #fff;
        border: 1px dashed #ebeef5;
        border-radius: 4px;
        margin: 12px;
    }

    // 滚动条样式
    ::-webkit-scrollbar {
        width: 6px;
        height: 6px;
    }

    ::-webkit-scrollbar-track {
        background: #f1f1f1;
    }

    ::-webkit-scrollbar-thumb {
        background: #ccc;
        border-radius: 3px;

        &:hover {
            background: #999;
        }
    }
</style>