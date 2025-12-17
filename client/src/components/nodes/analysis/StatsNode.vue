<template>
    <div class="StatsNodeLayout nodes-style" :class="[{'nodes-selected': selected}, {'nodes-dbclicked': data.dbclicked}]">
        <NodeTitle node-category="analysis">统计信息</NodeTitle>
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
                    统计列
                </div>
                <NodepySelectMany
                    :options="colHint"
                    :default-selected="defaultSelectedCol"
                    @select-change="onSelectChangeCol"
                    @clear-select="clearSelectCol"
                    class="nodrag"
                />
            </div>
            <div class="output-mean port">
                <div class="output-port-description">
                    均值
                </div>
                <Handle id="mean" type="source" :position="Position.Right" :class="[`${meanSchema_type}-handle-color`, {'node-errhandle': meanHasErr}]"/>
            </div>
            <div class="output-count port">
                <div class="output-port-description">
                    计数
                </div>
                <Handle id="count" type="source" :position="Position.Right" :class="[`${countSchema_type}-handle-color`, {'node-errhandle': countHasErr}]"/>
            </div>
            <div class="output-std port">
                <div class="output-port-description">
                    标准差
                </div>
                <Handle id="std" type="source" :position="Position.Right" :class="[`${stdSchema_type}-handle-color`, {'node-errhandle': stdHasErr}]"/>
            </div>
            <div class="output-min port">
                <div class="output-port-description">
                    最小值
                </div>
                <Handle id="min" type="source" :position="Position.Right" :class="[`${minSchema_type}-handle-color`, {'node-errhandle': minHasErr}]"/>
            </div>
            <div class="output-max port">
                <div class="output-port-description">
                    最大值
                </div>
                <Handle id="max" type="source" :position="Position.Right" :class="[`${maxSchema_type}-handle-color`, {'node-errhandle': maxHasErr}]"/>
            </div>
            <div class="output-sum port">
                <div class="output-port-description">
                    总和
                </div>
                <Handle id="sum" type="source" :position="Position.Right" :class="[`${sumSchema_type}-handle-color`, {'node-errhandle': sumHasErr}]"/>
            </div>
            <div class="output-quantile_25 port">
                <div class="output-port-description">
                    25%分位数
                </div>
                <Handle id="quantile_25" type="source" :position="Position.Right" :class="[`${quantile_25Schema_type}-handle-color`, {'node-errhandle': quantile_25HasErr}]"/>
            </div>
            <div class="output-quantile_50 port">
                <div class="output-port-description">
                    中位数
                </div>
                <Handle id="quantile_50" type="source" :position="Position.Right" :class="[`${quantile_50Schema_type}-handle-color`, {'node-errhandle': quantile_50HasErr}]"/>
            </div>
            <div class="output-quantile_75 port">
                <div class="output-port-description">
                    75%分位数
                </div>
                <Handle id="quantile_75" type="source" :position="Position.Right" :class="[`${quantile_75Schema_type}-handle-color`, {'node-errhandle': quantile_75HasErr}]"/>
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
    import type { StatsNodeData } from '@/types/nodeTypes'


    const props = defineProps<NodeProps<StatsNodeData>>()
    const colHint = computed(() => {
        if(props.data.hint?.col_choices?.length === 0) return ['']
        return props.data.hint?.col_choices || ['']
    })
    const col = ref(props.data.param.col)   //  used for defaultSelectedCol
    const defaultSelectedCol = computed(() => colHint.value.indexOf(col.value))
    const table_type = computed(() => getInputType(props.id, 'table'))
    const meanSchema_type = computed(():server__models__schema__Schema__Type|'default' => props.data.schema_out?.['mean']?.type || 'default')
    const meanHasErr = computed(() => handleOutputError(props.id, 'mean'))
    const countSchema_type = computed(():server__models__schema__Schema__Type|'default' => props.data.schema_out?.['count']?.type || 'default')
    const countHasErr = computed(() => handleOutputError(props.id, 'count'))
    const stdSchema_type = computed(():server__models__schema__Schema__Type|'default' => props.data.schema_out?.['std']?.type || 'default')
    const stdHasErr = computed(() => handleOutputError(props.id, 'std'))
    const minSchema_type = computed(():server__models__schema__Schema__Type|'default' => props.data.schema_out?.['min']?.type || 'default')
    const minHasErr = computed(() => handleOutputError(props.id, 'min'))
    const maxSchema_type = computed(():server__models__schema__Schema__Type|'default' => props.data.schema_out?.['max']?.type || 'default')
    const maxHasErr = computed(() => handleOutputError(props.id, 'max'))
    const sumSchema_type = computed(():server__models__schema__Schema__Type|'default' => props.data.schema_out?.['sum']?.type || 'default')
    const sumHasErr = computed(() => handleOutputError(props.id, 'sum'))
    const quantile_25Schema_type = computed(():server__models__schema__Schema__Type|'default' => props.data.schema_out?.['quantile_25']?.type || 'default')
    const quantile_25HasErr = computed(() => handleOutputError(props.id, 'quantile_25'))
    const quantile_50Schema_type = computed(():server__models__schema__Schema__Type|'default' => props.data.schema_out?.['quantile_50']?.type || 'default')
    const quantile_50HasErr = computed(() => handleOutputError(props.id, 'quantile_50'))
    const quantile_75Schema_type = computed(():server__models__schema__Schema__Type|'default' => props.data.schema_out?.['quantile_75']?.type || 'default')
    const quantile_75HasErr = computed(() => handleOutputError(props.id, 'quantile_75'))
    const errMsg = ref<string[]>([])
    const colHasErr = ref({
        id: 'col',
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


    watch(() => JSON.stringify(props.data.error), () => {
        errMsg.value = []
        handleExecError(props.data.error, errMsg)
        handleParamError(props.data.error, errMsg, colHasErr)
        handleValidationError(props.id, props.data.error, errMsg, inputTableHasErr)
    }, {immediate: true})

</script>

<style lang="scss" scoped>
    @use '../../../common/global.scss' as *;
    @use '../../../common/node.scss' as *;
    .StatsNodeLayout {
        height: 100%;
        .data {
            padding-top: $node-padding-top;
            padding-bottom: $node-padding-bottom;
            .input-table {
                margin-bottom: $node-margin;
            }
            .col {
                padding: 0 $node-padding-hor;
                margin-bottom: $node-margin;
            }
            .output-mean, .output-count, .output-std, .output-min, .output-max, .output-sum, .output-quantile_25, .output-quantile_50 {
                margin-bottom: $node-margin;
            }
        }
    }
    .all-handle-color {
        background: $table-color;
    }
</style>
