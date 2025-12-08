<template>
    <div class="MergeNodeLayout nodes-style" :class="[{'nodes-selected': selected}, {'nodes-dbclicked': data.dbclicked}]">
        <NodeTitle node-category='tableProcess'>表格合并节点</NodeTitle>
        <Timer :node-id="id" :default-time="data.runningtime"/>
        <div class="data">
            <div class="input-table_1 port">
                <div class="input-port-description">
                    表格1输入
                </div>
                <Handle id="table_1" type="target" :position="Position.Left" :class="[`${table_1_type}-handle-color`, {'node-errhandle': table_1HasErr.value}]"/>
            </div>
            <div class="input-table_2 port">
                <div class="input-port-description">
                    表格2输入
                </div>
                <Handle id="table_2" type="target" :position="Position.Left" :class="[`${table_2_type}-handle-color`, {'node-errhandle': table_2HasErr.value}]"/>
            </div>
            <div class="output-merged_table port">
                <div class="output-port-description">
                    表格输出
                </div>
                <Handle id="merged_table" type="source" :position="Position.Right" :class="[`${schema_type}-handle-color`, {'node-errhandle': merged_tableHasErr}]"/>
            </div>
        </div>
        <ErrorMsg :err-msg="errMsg"/>
    </div>
</template>

<script lang="ts" setup>
    import type { server__models__schema__Schema__Type } from '@/utils/api'
    import type { NodeProps } from '@vue-flow/core'
    import { Handle, Position } from '@vue-flow/core'
    import { computed, ref, watch } from 'vue'
    import type { BaseData } from '../../../types/nodeTypes'
    import { getInputType } from '../getInputType'
    import { handleExecError, handleValidationError, handleOutputError } from '../handleError'
    import ErrorMsg from '../tools/ErrorMsg.vue'
    import NodeTitle from '../tools/NodeTitle.vue'
    import Timer from '../tools/Timer.vue'


    const props = defineProps<NodeProps<BaseData>>()
    const table_1_type = computed(() => getInputType(props.id, 'table_1'))
    const table_2_type = computed(() => getInputType(props.id, 'table_2'))
    const schema_type = computed(():server__models__schema__Schema__Type|'default' => props.data.schema_out?.['merged_table']?.type || 'default')
    const merged_tableHasErr = computed(() => handleOutputError(props.id, 'merged_table'))
    const errMsg = ref<string[]>([])
    const table_1HasErr = ref({
        handleId: 'table_1',
        value: false
    })
     const table_2HasErr = ref({
        handleId: 'table_2',
        value: false
    })


    watch(() => JSON.stringify(props.data.error), () => {
        errMsg.value = []
        handleExecError(props.data.error, errMsg)
        handleValidationError(props.id, props.data.error, errMsg, table_1HasErr, table_2HasErr)
    }, {immediate: true})

</script>

<style lang="scss" scoped>
    @use '../../../common/global.scss' as *;
    @use '../../../common/node.scss' as *;
    .MergeNodeLayout {
        height: 100%;
        .data {
            padding-top: $node-padding-top;
            padding-bottom: $node-padding-bottom;
            .input-table_1, .input-table_2 {
                margin-bottom: $node-margin;
            }
        }
    }
    .all-handle-color {
        background: $table-color;
    }
</style>
