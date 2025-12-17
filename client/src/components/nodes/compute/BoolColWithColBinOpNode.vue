<template>
    <div class="BoolColWithColBinOpNodeLayout nodes-style" :class="[{'nodes-selected': selected}, {'nodes-dbclicked': data.dbclicked}]">
        <NodeTitle node-category="compute">列间布尔运算</NodeTitle>
        <Timer :node-id="id" :default-time="data.runningtime"/>
        <div class="data">
            <div class="input-table port">
                <div class="input-port-description">
                    表格
                </div>
                <Handle id="table" type="target" :position="Position.Left" :class="[`${table_type}-handle-color`, {'node-errhandle': inputTableHasErr.value}]"/>
            </div>
            <div class="op">
                <div class="param-description" :class="{'node-has-paramerr': opHasErr.value}">
                    运算
                </div>
                <NodepySelectMany
                    :options="opUi"
                    :default-selected="defaultSelectedOP"
                    @select-change="onSelectChangeOP"
                    class="nodrag"
                />
            </div>
            <div class="col1">
                <div class="param-description" :class="{'node-has-paramerr': col1HasErr.value}">
                    操作列1
                </div>
                <NodepySelectMany
                    :options="col1Hint"
                    :default-selected="defaultSelectedCol1"
                    @select-change="onSelectChangeCol1"
                    @clear-select="clearSelectCol1"
                    class="nodrag"
                />
            </div>
            <div class="col2">
                <div class="param-description" :class="{'node-has-paramerr': col2HasErr.value}">
                    操作列2
                </div>
                <NodepySelectMany
                    :options="col2Hint"
                    :default-selected="defaultSelectedCol2"
                    @select-change="onSelectChangeCol2"
                    @clear-select="clearSelectCol2"
                    class="nodrag"
                />
            </div>
            <div class="result_col">
                <div class="param-description" :class="{'node-has-paramerr': result_colHasErr.value}">
                    结果列
                </div>
                <NodepyStringInput v-model="result_col" @update-value="onUpdateResult_col" class="nodrag" placeholder="结果列名"/>
            </div>
            <div class="output-table port">
                <div class="output-port-description">
                    输出
                </div>
                <Handle id="table" type="source" :position="Position.Right" :class="[`${schema_type}-handle-color`, {'node-errhandle': outputTableHasErr}]"/>
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
    import NodepyStringInput from '../tools/Nodepy-StringInput.vue'
    import type { BoolColWithColBinOpNodeData } from '@/types/nodeTypes'


    const props = defineProps<NodeProps<BoolColWithColBinOpNodeData>>()
    const op = ["AND", "OR", "XOR", "SUB"]
    const opUi = ["与", "或", "异或", "减"]
    const defaultSelectedOP = op.indexOf(props.data.param.op)
    const col1Hint = computed(() => {
        if(props.data.hint?.col1_choices?.length === 0) return ['']
        return props.data.hint?.col1_choices || ['']
    })
    const col1 = ref(props.data.param.col1)   //  used for defaultSelectedCol1
    const defaultSelectedCol1 = computed(() => col1Hint.value.indexOf(col1.value))
    const col2Hint = computed(() => {
        if(props.data.hint?.col2_choices?.length === 0) return ['']
        return props.data.hint?.col2_choices || ['']
    })
    const col2 = ref(props.data.param.col2)   //  used for defaultSelectedCol2
    const defaultSelectedCol2 = computed(() => col2Hint.value.indexOf(col2.value))
    const result_col = ref(props.data.param.result_col || '')
    const table_type = computed(() => getInputType(props.id, 'table'))
    const schema_type = computed(():server__models__schema__Schema__Type|'default' => props.data.schema_out?.['table']?.type || 'default')
    const outputTableHasErr = computed(() => handleOutputError(props.id, 'table'))
    const errMsg = ref<string[]>([])
    const opHasErr = ref({
        id: 'op',
        value: false
    })
    const col1HasErr = ref({
        id: 'col1',
        value: false
    })
    const col2HasErr = ref({
        id: 'col2',
        value: false
    })
    const result_colHasErr = ref({
        id: 'result_col',
        value: false
    })
    const inputTableHasErr = ref({
        handleId: 'table',
        value: false
    })


    const onSelectChangeOP = (e: any) => {
        const selected_op = op[e] as 'AND'|'OR'|'XOR'|'SUB'
        props.data.param.op = selected_op
    }
    const onSelectChangeCol1 = (e: any) => {
        props.data.param.col1 = col1Hint.value[e]
    }
    const clearSelectCol1 = (resolve: any) => {
        props.data.param.col1 = ''
        col1.value = props.data.param.col1
        resolve()
    }
    const onSelectChangeCol2 = (e: any) => {
        props.data.param.col2 = col2Hint.value[e]
    }
    const clearSelectCol2 = (resolve: any) => {
        props.data.param.col2 = ''
        col2.value = props.data.param.col2
        resolve()
    }
    const onUpdateResult_col = () => {
        props.data.param.result_col = result_col.value
    }


    watch(() => JSON.stringify(props.data.error), () => {
        errMsg.value = []
        handleExecError(props.data.error, errMsg)
        handleParamError(props.data.error, errMsg, opHasErr, col1HasErr, col2HasErr, result_colHasErr)
        handleValidationError(props.id, props.data.error, errMsg, inputTableHasErr)
    }, {immediate: true})

</script>

<style lang="scss" scoped>
    @use '../../../common/global.scss' as *;
    @use '../../../common/node.scss' as *;
    .BoolColWithColBinOpNodeLayout {
        height: 100%;
        .data {
            padding-top: $node-padding-top;
            padding-bottom: $node-padding-bottom;
            .input-table {
                margin-bottom: $node-margin;
            }
            .op, .col1, .col2, .result_col {
                padding: 0 $node-padding-hor;
                margin-bottom: $node-margin;
            }
        }
    }
    .all-handle-color {
        background: $table-color;
    }
</style>
