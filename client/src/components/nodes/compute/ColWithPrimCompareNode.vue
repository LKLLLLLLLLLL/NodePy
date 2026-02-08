<template>
    <div class="ColWithPrimCompareNodeLayout nodes-style" :class="[{'nodes-selected': selected}, {'nodes-dbclicked': data.dbclicked}]">
        <NodeTitle node-category="compute">列与常量比较</NodeTitle>
        <Timer :node-id="id" :default-time="data.runningtime"/>
        <div class="data">
            <div class="input-table port">
                <div class="input-port-description">
                    表格
                </div>
                <Handle id="table" type="target" :position="Position.Left" :class="[`${table_type}-handle-color`, {'node-errhandle': inputTableHasErr.value}]"/>
            </div>
            <div class="input-const port">
                <div class="input-port-description" :class="{'node-has-paramerr': constHasErr.value}">
                    常量
                </div>
                <Handle id="const" type="target" :position="Position.Left" :class="[`${inputConst_type}-handle-color`, {'node-errhandle': inputConstHasErr.value}]"/>
            </div>
            <div class="const">
                <NodepyNumberInput
                    v-model="constValue"
                    class="nodrag"
                    @update-value="() => updateSimpleStringNumberBoolValue(data.param, 'const', constValue)"
                    :disabled="constDisabled"
                    :allow-empty="true"
                 />
            </div>
            <div class="op">
                <div class="param-description" :class="{'node-has-paramerr': opHasErr.value}">
                    运算
                </div>
                <NodepySelectMany
                    :options="opUi"
                    :default-selected="defaultSelectedOP"
                    @select-change="(e: any) => updateSimpleSelectMany(data.param, 'op', op, e)"
                    class="nodrag"
                />
            </div>
            <div class="col">
                <div class="param-description" :class="{'node-has-paramerr': colHasErr.value}">
                    操作列
                </div>
                <NodepySelectMany
                    :options="colHint"
                    :default-selected="defaultSelectedCol"
                    @select-change="(e: any) => updateSimpleSelectMany(data.param, 'col', colHint, e)"
                    @clear-select="clearSelectCol"
                    class="nodrag"
                />
            </div>
            <div class="result_col">
                <div class="param-description" :class="{'node-has-paramerr': result_colHasErr.value}">
                    结果列
                </div>
                <NodepyStringInput v-model="result_col" @update-value="() => updateSimpleStringNumberBoolValue(data.param, 'result_col', result_col)" class="nodrag" placeholder="结果列名"/>
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
    import NodepyNumberInput from '../tools/Nodepy-NumberInput/Nodepy-NumberInput.vue'
    import { hasInputEdge } from '../hasEdge'
    import { updateSimpleStringNumberBoolValue, updateSimpleSelectMany } from '../updateParam'
    import type { ColWithPrimCompareNodeData } from '@/types/nodeTypes'


    const props = defineProps<NodeProps<ColWithPrimCompareNodeData>>()
    const op = ["EQ", "NEQ", "LT", "LTE", "GT", "GTE"]
    const opUi = ['等于', '不等于', '小于', '小于等于', '大于', '大于等于']
    const defaultSelectedOP = op.indexOf(props.data.param.op)
    const colHint = computed(() => {
        if(props.data.hint?.col1_choices?.length === 0) return ['']
        return props.data.hint?.col1_choices || ['']
    })
    const col1 = ref(props.data.param.col)   //  used for defaultSelectedCol
    const defaultSelectedCol = computed(() => colHint.value.indexOf(col1.value))
    const result_col = ref(props.data.param.result_col)
    const constValue = ref(props.data.param.const)
    const constDisabled = computed(() => hasInputEdge(props.id, 'const'))
    const table_type = computed(() => getInputType(props.id, 'table'))
    const inputConst_type = computed(() => getInputType(props.id, 'const'))
    const schema_type = computed(():server__models__schema__Schema__Type|'default' => props.data.schema_out?.['table']?.type || 'default')
    const outputTableHasErr = computed(() => handleOutputError(props.id, 'table'))
    const errMsg = ref<string[]>([])
    const opHasErr = ref({
        id: 'op',
        value: false
    })
    const colHasErr = ref({
        id: 'col',
        value: false
    })
    const constHasErr = ref({
        id: 'const',
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
    const inputConstHasErr = ref({
        handleId: 'const',
        value: false
    })


    const clearSelectCol = (resolve: any) => {
        props.data.param.col = ''
        col1.value = props.data.param.col
        resolve()
    }


    watch(() => JSON.stringify(props.data.error), () => {
        errMsg.value = []
        handleExecError(props.data.error, errMsg)
        handleParamError(props.data.error, errMsg, opHasErr, colHasErr, constHasErr, result_colHasErr)
        handleValidationError(props.id, props.data.error, errMsg, inputTableHasErr, inputConstHasErr)
    }, {immediate: true})

</script>

<style lang="scss" scoped>
    @use '../../../common/global.scss' as *;
    @use '../../../common/node.scss' as *;
    .ColWithPrimCompareNodeLayout {
        height: 100%;
        .data {
            padding-top: $node-padding-top;
            padding-bottom: $node-padding-bottom;
            .input-table {
                margin-bottom: $node-margin;
            }
            .input-const {
                margin-bottom: 2px;
            }
            .op, .col, .const, .result_col {
                padding: 0 $node-padding-hor;
                margin-bottom: $node-margin;
            }
        }
    }
    .all-handle-color {
        background: $table-color;
    }
</style>