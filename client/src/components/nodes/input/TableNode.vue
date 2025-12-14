<template>
    <div class="TableNodeLayout nodes-style" :class="[{'nodes-selected': selected}, {'nodes-dbclicked': data.dbclicked}]">
        <NodeTitle node-category="input">表格节点</NodeTitle>
        <Timer :node-id="id" :default-time="data.runningtime"/>
        <div class="data">
            <div class="tableParam">
                <div class="param-description" :class="{'node-has-paramerr': tableParamHasErr}">
                    自定义表格
                </div>
                <NodepyButton :handle-click="tableStore.createTableModal">
                    <span class="tableParam-description">编辑</span>
                </NodepyButton>
            </div>
            <div class="output-table port">
                <div class="output-port-description">
                    表格输出
                </div>
                <Handle id="table" type="source" :position="Position.Right" :class="[`${schema_type}-handle-color`, {'node-errhandle': tableHasErr}]"/>
            </div>
        </div>
        <ErrorMsg :err-msg="errMsg"/>
    </div>
</template>

<script lang="ts" setup>
    import NodeTitle from '../tools/NodeTitle.vue'
    import type { server__models__schema__Schema__Type } from '@/utils/api'
    import type { NodeProps } from '@vue-flow/core'
    import { Handle, Position } from '@vue-flow/core'
    import { computed, ref, watch } from 'vue'
    import { handleExecError, handleParamError, handleOutputError } from '../handleError'
    import ErrorMsg from '../tools/ErrorMsg.vue'
    import Timer from '../tools/Timer.vue'
    import NodepyButton from '../tools/Nodepy-button.vue'
    import { useTableStore } from '@/stores/tableStore'
    import type {TableNodeData} from '../../../types/nodeTypes'


    const tableStore = useTableStore()
    const props = defineProps<NodeProps<TableNodeData>>()
    const schema_type = computed(():server__models__schema__Schema__Type|'default' => props.data.schema_out?.['table']?.type || 'default')
    const tableHasErr = computed(() => handleOutputError(props.id, 'table'))
    const errMsg = ref<string[]>([])
    const rowsHasErr = ref({
        id: 'rows',
        value: false
    })
    const col_namesHasErr = ref({
        id: 'col_names',
        value: false
    })
    const col_typesHasErr = ref({
        id: 'col_types',
        value: false
    })
    const tableParamHasErr = computed(() => {
        return rowsHasErr.value.value || col_namesHasErr.value.value || col_typesHasErr.value.value
    })


    const updateTableParam = () => {
        props.data.param.rows = tableStore.currentTableData.rows
        props.data.param.col_names = tableStore.currentTableData.colNames
        props.data.param.col_types = tableStore.currentTableData.colTypes
    }


    watch(() => JSON.stringify(props.data.error), () => {
        errMsg.value = []
        handleExecError(props.data.error, errMsg)
        handleParamError(props.data.error, errMsg, rowsHasErr, col_namesHasErr, col_typesHasErr)
    }, {immediate: true})

</script>

<style lang="scss" scoped>
    @use '../../../common/global.scss' as *;
    @use '../../../common/node.scss' as *;
    .TableNodeLayout {
        height: 100%;
        .data {
            padding-top: $node-padding-top;
            padding-bottom: $node-padding-bottom;
            .tableParam {
                padding: 0 $node-padding-hor;
                margin-bottom: $node-margin;
                .tableParam-description {
                    font-size: 12px;
                    font-weight: bold;
                }
            }
        }
    }
</style>