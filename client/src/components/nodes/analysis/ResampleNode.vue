<template>
    <div class="ResampleNodeLayout nodes-style" :class="[{'nodes-selected': selected}, {'nodes-dbclicked': data.dbclicked}]">
        <NodeTitle node-category="analysis">日期重采样</NodeTitle>
        <Timer :node-id="id" :default-time="data.runningtime"/>
        <div class="data">
            <div class="input-table port">
                <div class="input-port-description">
                    表格输入
                </div>
                <Handle id="table" type="target" :position="Position.Left" :class="[`${table_type}-handle-color`, {'node-errhandle': inputTableHasErr.value}]"/>
            </div>
            <div class="col">
                <div class="param-description" :class="{'node-has-paramerr': colHasErr.value}">
                    重采样列
                </div>
                <NodepySelectMany
                    :options="colHint"
                    :default-selected="defaultSelectedCol"
                    @select-change="onSelectChangeCol"
                    @clear-select="clearSelectCol"
                    class="nodrag"
                />
            </div>
            <div class="frequency">
                <div class="param-description" :class="{'node-has-paramerr': frequencyHasErr.value}">
                    频率
                </div>
                <NodepySelectMany
                    :options="frequencyChinese"
                    :default-selected="defaultSelectedFrequency"
                    @select-change="onSelectChangeFrequency"
                    class="nodrag"
                />
            </div>
            <div class="method">
                <div class="param-description" :class="{'node-has-paramerr': methodHasErr.value}">
                    算法
                </div>
                <NodepySelectMany
                    :options="methodChinese"
                    :default-selected="defaultSelectedMethod"
                    @select-change="onSelectChangeMethod"
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
                    表格输出
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
    import type { ResampleNodeData } from '@/types/nodeTypes'


    const props = defineProps<NodeProps<ResampleNodeData>>()
    const colHint = computed(() => {
        if(props.data.hint?.col_choices?.length === 0) return ['']
        return props.data.hint?.col_choices || ['']
    })
    const col = ref(props.data.param.col)   //  used for defaultSelectedCol
    const defaultSelectedCol = computed(() => colHint.value.indexOf(col.value))
    const frequency = ["D", "H", "T", "S"]
    const frequencyChinese = ['天', '小时', '分钟', '秒']
    const defaultSelectedFrequency = frequency.indexOf(props.data.param.frequency)
    const method = ["mean", "sum", "max", "min", "count"]
    const methodChinese = ['平均值', '总和', '最大值', '最小值', '计数']
    const defaultSelectedMethod = method.indexOf(props.data.param.method)
    const result_col = ref(props.data.param.result_col || '')
    const table_type = computed(() => getInputType(props.id, 'table'))
    const schema_type = computed(():server__models__schema__Schema__Type|'default' => props.data.schema_out?.['table']?.type || 'default')
    const outputTableHasErr = computed(() => handleOutputError(props.id, 'table'))
    const errMsg = ref<string[]>([])
    const colHasErr = ref({
        id: 'col',
        value: false
    })
    const frequencyHasErr = ref({
        id: 'frequency',
        value: false
    })
    const methodHasErr = ref({
        id: 'method',
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


    const onSelectChangeCol = (e: any) => {
        props.data.param.col = colHint.value[e]
    }
    const clearSelectCol = (resolve: any) => {
        props.data.param.col = ''
        col.value = props.data.param.col
        resolve()
    }
    const onSelectChangeFrequency = (e: any) => {
        const selected_frequency = frequency[e] as 'D' | 'H' | 'T' | 'S'
        props.data.param.frequency = selected_frequency
    }
    const onSelectChangeMethod = (e: any) => {
        const selected_method = method[e] as 'mean' | 'sum' | 'max' | 'min' | 'count'
        props.data.param.method = selected_method
    }
    const onUpdateResult_col = () => {
        props.data.param.result_col = result_col.value
    }


    watch(() => JSON.stringify(props.data.error), () => {
        errMsg.value = []
        handleExecError(props.data.error, errMsg)
        handleParamError(props.data.error, errMsg, colHasErr, frequencyHasErr, methodHasErr, result_colHasErr)
        handleValidationError(props.id, props.data.error, errMsg, inputTableHasErr)
    }, {immediate: true})

</script>

<style lang="scss" scoped>
    @use '../../../common/global.scss' as *;
    @use '../../../common/node.scss' as *;
    .ResampleNodeLayout {
        height: 100%;
        .data {
            padding-top: $node-padding-top;
            padding-bottom: $node-padding-bottom;
            .input-table {
                margin-bottom: $node-margin;
            }
            .col, .frequency, .method, .result_col {
                padding: 0 $node-padding-hor;
                margin-bottom: $node-margin;
            }
        }
    }
    .all-handle-color {
        background: $table-color;
    }
</style>
