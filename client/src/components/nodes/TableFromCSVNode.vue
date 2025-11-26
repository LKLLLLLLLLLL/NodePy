<template>
    <div class="TableFromCSVNodeLayout nodes-style" :class="[{'nodes-selected': selected}, {'nodes-dbclicked': data.dbclicked}]">
        <NodeTitle node-category="file">CSV表格节点</NodeTitle>
        <Timer :node-id="id" :default-time="data.runningtime"/>
        <div class="data">
            <div class="input-csv_file port">
                <div class="input-port-description">
                    CSV文件输入端口
                </div>
                <Handle
                    id="csv_file"
                    type="target"
                    :position="Position.Left"
                    :class="[`${csv_file_type}-handle-color`, {'node-errhandle': csv_fileHaserr.value}]"
                />
            </div>
            <div class="output-table port">
                <div class="output-port-description">
                    表格输出端口
                </div>
                <Handle
                    id="table"
                    type="source"
                    :position="Position.Right"
                    :class="[`${schema_type}-handle-color`, {'node-errhandle': tableHasErr}]"
                />
            </div>
        </div>
        <ErrorMsg :err-msg="errMsg"/>
    </div>
</template>

<script lang="ts" setup>
    import type { Type } from '@/utils/api'
    import type { NodeProps } from '@vue-flow/core'
    import { Handle, Position } from '@vue-flow/core'
    import { computed, ref, watch } from 'vue'
    import type { BaseData } from '../../types/nodeTypes'
    import { getInputType } from './getInputType'
    import { handleExecError, handleValidationError, handleOutputError } from './handleError'
    import ErrorMsg from './tools/ErrorMsg.vue'
    import NodeTitle from './tools/NodeTitle.vue'
    import Timer from './tools/Timer.vue'


    const props = defineProps<NodeProps<BaseData>>()
    const csv_file_type = computed(() => getInputType(props.id, 'csv_file'))
    const schema_type = computed(():Type|'default' => props.data.schema_out?.['table']?.type || 'default')
    const tableHasErr = computed(() => handleOutputError(props.id, 'table'))
    const errMsg = ref<string[]>([])
    const csv_fileHaserr = ref({
        handleId: 'csv_file',
        value: false
    })


    watch(() => JSON.stringify(props.data.error), () => {
        errMsg.value = []
        handleExecError(props.data.error, errMsg)
        handleValidationError(props.id, props.data.error, errMsg, csv_fileHaserr)
    }, {immediate: true})

</script>

<style lang="scss" scoped>
    @use '../../common/global.scss' as *;
    @use '../../common/node.scss' as *;
    .TableFromCSVNodeLayout {
        height: 100%;
        .data {
            padding-top: $node-padding-top;
            padding-bottom: $node-padding-bottom;
            .output-table {
                margin-top: $node-margin;
            }
        }
    }
    .all-handle-color {
        background: $file-color;
    }
</style>
