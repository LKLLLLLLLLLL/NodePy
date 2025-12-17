<template>
    <div class="BatchConcatNodeLayout nodes-style" :class="[{'nodes-selected': selected}, {'nodes-dbclicked': data.dbclicked}]">
        <NodeTitle node-category='stringProcess'>批量字符串拼接</NodeTitle>
        <Timer :node-id="id" :default-time="data.runningtime"/>
        <div class="data">
            <div class="input-input port">
                <div class="input-port-description">
                    表格输入
                </div>
                <Handle id="input" type="target" :position="Position.Left" :class="[`${input_type}-handle-color`, {'node-errhandle': inputHasErr.value}]"/>
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
                <NodepyStringInput v-model="result_col" @update-value="onUpdateResult_col" class="nodrag" placeholder="结果列"/>
            </div>
            <div class="output-output port">
                <div class="output-port-description">
                    结果表格
                </div>
                <Handle id="output" type="source" :position="Position.Right" :class="[`${schema_type}-handle-color`, {'node-errhandle': outputHasErr}]"/>
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
    import type { BatchConcatNodeData } from '@/types/nodeTypes'


    const props = defineProps<NodeProps<BatchConcatNodeData>>()
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
    const input_type = computed(() => getInputType(props.id, 'input'))
    const schema_type = computed(():server__models__schema__Schema__Type|'default' => props.data.schema_out?.['output']?.type || 'default')
    const outputHasErr = computed(() => handleOutputError(props.id, 'output'))
    const errMsg = ref<string[]>([])
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
    const inputHasErr = ref({
        handleId: 'input',
        value: false
    })


    const onSelectChangeCol1 = (e: any) => {
        props.data.param.col1 = col1Hint.value[e]
    }
    const onSelectChangeCol2 = (e: any) => {
        props.data.param.col2 = col2Hint.value[e]
    }
    const clearSelectCol1 = (resolve: any) => {
        props.data.param.col1 = ''
        col1.value = props.data.param.col1
        resolve()
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
        handleParamError(props.data.error, errMsg, col1HasErr, col2HasErr, result_colHasErr)
        handleValidationError(props.id, props.data.error, errMsg, inputHasErr)
    }, {immediate: true})

</script>

<style lang="scss" scoped>
    @use '../../../common/global.scss' as *;
    @use '../../../common/node.scss' as *;
    .BatchConcatNodeLayout {
        height: 100%;
        .data {
            padding-top: $node-padding-top;
            padding-bottom: $node-padding-bottom;
            .input-input {
                margin-bottom: $node-margin;
            }
            .col1, .col2, .result_col {
                padding: 0 $node-padding-hor;
                margin-bottom: $node-margin;
            }
        }
    }
    .all-handle-color {
        background: $table-color;
    }
</style>
