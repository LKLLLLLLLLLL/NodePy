<template>
    <div class="GetCellNodeLayout nodes-style" :class="[{'nodes-selected': selected}, {'nodes-dbclicked': data.dbclicked}]">
        <NodeTitle node-category="control">单元格提取</NodeTitle>
        <Timer :node-id="id" :default-time="data.runningtime"/>
        <div class="data">
            <div class="input-table port">
                <div class="input-port-description">
                    表格输入
                </div>
                <Handle id="table" type="target" :position="Position.Left" :class="[`${table_type}-handle-color`, {'node-errhandle': inputTableHasErr.value}]"/>
            </div>
            <div class="input-row port">
                <div class="input-port-description" :class="{'node-has-paramerr': rowHasErr.value}">
                    行号
                </div>
                <Handle id="row" type="target" :position="Position.Left" :class="[`${row_type}-handle-color`, {'node-errhandle': inputRowHasErr.value}]"/>
            </div>
            <div class="row">
                <NodepyNumberInput
                    v-model="row"
                    class="nodrag"
                    @update-value="() => updateSimpleStringNumberBoolValue(data.param, 'row', row)"
                    :disabled="rowDisabled"
                 />
            </div>
            <div class="col">
                <div class="param-description" :class="{'node-has-paramerr': colHasErr.value}">
                    列
                </div>
                <NodepySelectMany
                    :options="colHint"
                    :default-selected="defaultSelectedCol"
                    @select-change="(e: any) => updateSimpleSelectMany(data.param, 'col', colHint, e)"
                    @clear-select="clearSelectCol"
                    class="nodrag"
                />
            </div>
            <div class="output-value port">
                <div class="output-port-description">
                    单元格值
                </div>
                <Handle id="value" type="source" :position="Position.Right" :class="[`${schema_type}-handle-color`, {'node-errhandle': valueHasErr}]"/>
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
    import type { server__models__schema__Schema__Type } from '@/utils/api'
    import { handleValidationError, handleExecError, handleParamError, handleOutputError } from '../handleError'
    import ErrorMsg from '../tools/ErrorMsg.vue'
    import NodeTitle from '../tools/NodeTitle.vue'
    import Timer from '../tools/Timer.vue'
    import NodepySelectMany from '../tools/Nodepy-selectMany.vue'
    import NodepyNumberInput from '../tools/Nodepy-NumberInput/Nodepy-NumberInput.vue'
    import { updateSimpleStringNumberBoolValue, updateSimpleSelectMany } from '../updateParam'
    import { hasInputEdge } from '../hasEdge'
    import type { GetCellNodeData } from '@/types/nodeTypes'


    const props = defineProps<NodeProps<GetCellNodeData>>()
    const colHint = computed(() => {
        if(props.data.hint?.col_choices?.length === 0) return ['']
        return props.data.hint?.col_choices || ['']
    })
    const defaultSelectedCol = ref(colHint.value.indexOf(props.data.param.col))
    const row = ref(props.data.param.row)
    const rowDisabled = computed(() => hasInputEdge(props.id, 'row'))
    const table_type = computed(() => getInputType(props.id, 'table'))
    const row_type = computed(() => getInputType(props.id, 'row'))
    const schema_type = computed(():server__models__schema__Schema__Type|'default' => props.data.schema_out?.['value']?.type || 'default')
    const valueHasErr = computed(() => handleOutputError(props.id, 'value'))
    const errMsg = ref<string[]>([])
    const colHasErr = ref({
        id: 'col',
        value: false
    })
    const rowHasErr = ref({
        id: 'row',
        value: false
    })
    const inputTableHasErr = ref({
        handleId: 'table',
        value: false
    })
    const inputRowHasErr = ref({
        handleId: 'row',
        value: false
    })


    const clearSelectCol = (resolve: any) => {
        props.data.param.col = ''
        defaultSelectedCol.value = -1
        resolve()
    }


    watch(() => JSON.stringify(props.data.error), () => {
        errMsg.value = []
        handleExecError(props.data.error, errMsg)
        handleParamError(props.data.error, errMsg, colHasErr, rowHasErr)
        handleValidationError(props.id, props.data.error, errMsg, inputTableHasErr, inputRowHasErr)
    }, {immediate: true})

</script>

<style lang="scss" scoped>
    @use '../../../common/global.scss' as *;
    @use '../../../common/node.scss' as *;
    .GetCellNodeLayout {
        height: 100%;
        .data {
            padding-top: $node-padding-top;
            padding-bottom: $node-padding-bottom;
            .input-table {
                margin-bottom: $node-margin;
            }
            .input-row {
                margin-bottom: 2px;
            }
            .row, .col {
                padding: 0 $node-padding-hor;
                margin-bottom: $node-margin;
            }
        }
    }
    .all-handle-color[data-handleid="table"] {
        background: $table-color;
    }
    .all-handle-color[data-handleid="row"] {
        background: $int-color;
    }
</style>