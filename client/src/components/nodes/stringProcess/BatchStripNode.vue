<template>
    <div class="BatchStripNodeLayout nodes-style" :class="[{'nodes-selected': selected}, {'nodes-dbclicked': data.dbclicked}]">
        <NodeTitle node-category='stringProcess'>批量首尾字符清洗节点</NodeTitle>
        <Timer :node-id="id" :default-time="data.runningtime"/>
        <div class="data">
            <div class="input-input port">
                <div class="input-port-description">
                    表格输入
                </div>
                <Handle id="input" type="target" :position="Position.Left" :class="[`${input_type}-handle-color`, {'node-errhandle': inputHasErr.value}]"/>
            </div>
            <div class="input-strip_chars port">
                <div class="input-port-description" :class="{'node-has-paramerr': strip_charsHasErr.value}">
                    清洗字符集合输入
                </div>
                <Handle id="strip_chars" type="target" :position="Position.Left" :class="[`${inputStrip_chars_type}-handle-color`, {'node-errhandle': inputStrip_charsHasErr.value}]"/>
            </div>
            <div class="strip_chars">
                <NodepyStringInput
                    v-model="strip_chars"
                    @update-value="onUpdateStrip_chars"
                    :disabled="strip_charsDisabled"
                    class="nodrag"
                    placeholder="清洗字符集合"
                />
            </div>
            <div class="col">
                <div class="param-description" :class="{'node-has-paramerr': colHasErr.value}">
                    操作列名
                </div>
                <NodepySelectMany
                    :options="colHint"
                    :default-selected="defaultSelectedCol"
                    @select-change="onSelectChangeCol"
                    @clear-select="clearSelectCol"
                    class="nodrag"
                />
            </div>
            <div class="result_col">
                <div class="param-description" :class="{'node-has-paramerr': result_colHasErr.value}">
                    结果列名
                </div>
                <NodepyStringInput v-model="result_col" @update-value="onUpdateResult_col" class="nodrag" placeholder="结果列名"/>
            </div>
            <div class="output-output port">
                <div class="output-port-description">
                    结果表格输出
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
    import type { Type } from '@/utils/api'
    import { handleValidationError, handleExecError, handleParamError, handleOutputError } from '../handleError'
    import { hasInputEdge } from '../hasEdge'
    import ErrorMsg from '../tools/ErrorMsg.vue'
    import NodeTitle from '../tools/NodeTitle.vue'
    import Timer from '../tools/Timer.vue'
    import NodepySelectMany from '../tools/Nodepy-selectMany.vue'
    import NodepyStringInput from '../tools/Nodepy-StringInput.vue'
    import type { BatchStripNodeData } from '@/types/nodeTypes'


    const props = defineProps<NodeProps<BatchStripNodeData>>()
    const strip_chars = ref(props.data.param.strip_chars || '')
    const strip_charsDisabled = computed(() => hasInputEdge(props.id, 'strip_chars'))
    const colHint = computed(() => props.data.hint?.col_choices || [''])
    const col = ref(props.data.param.col)   //  used for defaultSelectedCol
    const defaultSelectedCol = computed(() => colHint.value.indexOf(col.value))
    const result_col = ref(props.data.param.result_col || '')
    const input_type = computed(() => getInputType(props.id, 'input'))
    const inputStrip_chars_type = computed(() => getInputType(props.id, 'strip_chars'))
    const schema_type = computed(():Type|'default' => props.data.schema_out?.['output']?.type || 'default')
    const outputHasErr = computed(() => handleOutputError(props.id, 'output'))
    const errMsg = ref<string[]>([])
    const strip_charsHasErr = ref({
        id: 'strip_chars',
        value: false
    })
    const colHasErr = ref({
        id: 'col',
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
    const inputStrip_charsHasErr = ref({
        handleId: 'strip_chars',
        value: false
    })


    const onUpdateStrip_chars = (e?: Event) => {
        props.data.param.strip_chars = strip_chars.value
    }
    const onSelectChangeCol = (e: any) => {
        props.data.param.col = colHint.value[e]
    }
    const clearSelectCol = (resolve: any) => {
        props.data.param.col = ''
        col.value = props.data.param.col
        resolve()
    }
    const onUpdateResult_col = () => {
        props.data.param.result_col = result_col.value
    }


    watch(() => JSON.stringify(props.data.error), () => {
        errMsg.value = []
        handleExecError(props.data.error, errMsg)
        handleParamError(props.data.error, errMsg, strip_charsHasErr, colHasErr, result_colHasErr)
        handleValidationError(props.id, props.data.error, errMsg, inputHasErr, inputStrip_charsHasErr)
    }, {immediate: true})
</script>

<style lang="scss" scoped>
    @use '../../../common/global.scss' as *;
    @use '../../../common/node.scss' as *;
    .BatchStripNodeLayout {
        height: 100%;
        .data {
            padding-top: $node-padding-top;
            padding-bottom: $node-padding-bottom;
            .input-input {
                margin-bottom: $node-margin;
            }
            .input-strip_chars {
                margin-bottom: 2px;
            }
            .strip_chars, .col, .result_col {
                padding: 0 $node-padding-hor;
                margin-bottom: $node-margin;
            }
        }
    }
    .all-handle-color[data-handleid="input"] {
        background: $table-color;
    }
    .all-handle-color[data-handleid="strip_chars"] {
        background: $bool-color;
    }
</style>