<template>
    <div class="SelectColNodeLayout nodes-style" :class="[{'nodes-selected': selected}, {'nodes-dbclicked': data.dbclicked}]">
        <NodeTitle node-category="tableProcess">表格列选择节点</NodeTitle>
        <Timer :node-id="id" :default-time="data.runningtime"/>
        <div class="data">
            <div class="input-table port">
                <div class="input-port-description">
                    表格输入
                </div>
                <Handle id="table" type="target" :position="Position.Left" :class="[`${table_type}-handle-color`, {'node-errhandle': inputTableHasErr.value}]"/>
            </div>
            <div class="selected_cols">
                <div class="param-description" :class="{'node-has-paramerr': selected_colsHasErr.value}">
                    选择的列名
                </div>
                <NodepyMultiSelectMany
                    :options="selected_colsHint"
                    :default-selected="defaultSelectedSelected_cols"
                    @select-change="onSelectChangeSelected_cols"
                    @clear-select="clearSelectSelected_cols"
                    class="nodrag"
                />
            </div>
            <div class="output-selected_table port">
                <div class="output-port-description">
                    选择后的表格
                </div>
                <Handle id="selected_table" type="source" :position="Position.Right" :class="[`${selected_tableSchema_type}-handle-color`, {'node-errhandle': selected_tableHasErr}]"/>
            </div>
            <div class="output-dropped_table port">
                <div class="output-port-description">
                    未选择的表格
                </div>
                <Handle id="dropped_table" type="source" :position="Position.Right" :class="[`${dropped_tableSchema_type}-handle-color`, {'node-errhandle': dropped_tableHasErr}]"/>
            </div>
        </div>
        <ErrorMsg :err-msg="errMsg"/>
    </div>
</template>

<script lang="ts" setup>
    import {ref, computed, watch} from 'vue'
    import type { NodeProps } from '@vue-flow/core'
    import { Position, Handle } from '@vue-flow/core'
    import { getInputType } from '../getInputType'
    import type { Type } from '@/utils/api'
    import { handleValidationError, handleExecError, handleParamError, handleOutputError } from '../handleError'
    import ErrorMsg from '../tools/ErrorMsg.vue'
    import NodeTitle from '../tools/NodeTitle.vue'
    import Timer from '../tools/Timer.vue'
    import NodepyMultiSelectMany from '../tools/Nodepy-multiSelectMany.vue'
    import type { SelectColNodeData } from '@/types/nodeTypes'


    const props = defineProps<NodeProps<SelectColNodeData>>()
    const selected_colsHint = computed(() => {
        if(props.data.hint?.selected_col_choices?.length === 0) return ['']
        return props.data.hint?.selected_col_choices || ['']
    })
    const selected_cols = ref(props.data.param.selected_cols)   //  used for defaultSelectedSelected_cols
    const defaultSelectedSelected_cols = computed(() => {
        const hintArray = selected_colsHint.value
        const selectedArray = selected_cols.value
        return selectedArray.map(item => hintArray.indexOf(item)).filter(idx => idx !== -1)
    })
    const table_type = computed(() => getInputType(props.id, 'table'))
    const selected_tableSchema_type = computed(():Type|'default' => props.data.schema_out?.['selected_table']?.type || 'default')
    const dropped_tableSchema_type = computed(():Type|'default' => props.data.schema_out?.['dropped_table']?.type || 'default')
    const selected_tableHasErr = computed(() => handleOutputError(props.id, 'selected_table'))
    const dropped_tableHasErr = computed(() => handleOutputError(props.id, 'dropped_table'))
    const errMsg = ref<string[]>([])
    const selected_colsHasErr = ref({
        id: 'selected_cols',
        value: false
    })
    const inputTableHasErr = ref({
        handleId: 'table',
        value: false
    })


    const onSelectChangeSelected_cols = (e: any) => {
        props.data.param.selected_cols = e.map((idx: number) => selected_colsHint.value[idx])
    }
    const clearSelectSelected_cols = (resolve: any) => {
        props.data.param.selected_cols = []
        selected_cols.value = props.data.param.selected_cols
        resolve()
    }


    watch(() => JSON.stringify(props.data.error), () => {
        errMsg.value = []
        handleExecError(props.data.error, errMsg)
        handleParamError(props.data.error, errMsg, selected_colsHasErr)
        handleValidationError(props.id, props.data.error, errMsg, inputTableHasErr)
    }, {immediate: true})

</script>

<style lang="scss" scoped>
    @use '../../../common/global.scss' as *;
    @use '../../../common/node.scss' as *;
    .SelectColNodeLayout {
        height: 100%;
        .data {
            padding-top: $node-padding-top;
            padding-bottom: $node-padding-bottom;
            .input-table {
                margin-bottom: $node-margin;
            }
            .selected_cols {
                padding: 0 $node-padding-hor;
                margin-bottom: $node-margin;
            }
            .output-selected_table {
                margin-bottom: $node-margin;
            }
        }
    }
    .all-handle-color {
        background: $table-color;
    }
</style>