<template>
    <div class="RollingNodeLayout nodes-style" :class="[{'nodes-selected': selected}, {'nodes-dbclicked': data.dbclicked}]">
        <NodeTitle node-category="analysis">滑动窗口节点</NodeTitle>
        <Timer :node-id="id" :default-time="data.runningtime"/>
        <div class="data">
            <div class="input-table port">
                <div class="input-port-description">
                    表格输入
                </div>
                <Handle id="table" type="target" :position="Position.Left" :class="[`${table_type}-handle-color`, {'node-errhandle': inputTableHasErr.value}]"/>
            </div>
            <div class="input-window_size port">
                <div class="input-port-description" :class="{'node-has-paramerr': window_sizeHasErr.value}">
                    窗口大小
                </div>
                <!-- <Handle id="window_size" type="target" :position="Position.Left" :class="[`${inputWindow_size_type}-handle-color`, {'node-errhandle': inputWindow_sizeHasErr.value}]"/> -->
            </div>
            <div class="window_size">
                <NodepyNumberInput
                    v-model="window_size"
                    class="nodrag"
                    @update-value="onUpdateWindow_size"
                    :disabled="window_sizeDisabled"
                 />
            </div>
            <div class="input-min_periods port">
                <div class="input-port-description" :class="{'node-has-paramerr': min_periodsHasErr.value}">
                    最小周期
                </div>
                <!-- <Handle id="min_periods" type="target" :position="Position.Left" :class="[`${inputMin_periods_type}-handle-color`, {'node-errhandle': inputMin_periodsHasErr.value}]"/> -->
            </div>
            <div class="min_periods">
                <NodepyNumberInput
                    v-model="min_periods"
                    class="nodrag"
                    @update-value="onUpdateMin_periods"
                    :disabled="min_periodsDisabled"
                 />
            </div>
            <div class="col">
                <div class="param-description" :class="{'node-has-paramerr': colHasErr.value}">
                    计算列名
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
            <div class="method">
                <div class="param-description" :class="{'node-has-paramerr': methodHasErr.value}">
                    方法
                </div>
                <NodepySelectMany
                    :options="methodChinese"
                    :default-selected="defaultSelectedMethod"
                    @select-change="onSelectChangeMethod"
                    class="nodrag"
                />
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
    import type { Type } from '@/utils/api'
    import { handleValidationError, handleExecError, handleParamError, handleOutputError } from '../handleError'
    import ErrorMsg from '../tools/ErrorMsg.vue'
    import NodeTitle from '../tools/NodeTitle.vue'
    import Timer from '../tools/Timer.vue'
    import NodepySelectMany from '../tools/Nodepy-selectMany.vue'
    import NodepyStringInput from '../tools/Nodepy-StringInput.vue'
    import NodepyNumberInput from '../tools/Nodepy-NumberInput/Nodepy-NumberInput.vue'
    import { hasInputEdge } from '../hasEdge'
    import type { RollingNodeData } from '@/types/nodeTypes'


    const props = defineProps<NodeProps<RollingNodeData>>()
    const colHint = computed(() => {
        if(props.data.hint?.col_choices?.length === 0) return ['']
        return props.data.hint?.col_choices || ['']
    })
    const col = ref(props.data.param.col)   //  used for defaultSelectedCol
    const defaultSelectedCol = computed(() => colHint.value.indexOf(col.value))
    const window_size = ref(props.data.param.window_size)
    const window_sizeDisabled = computed(() => hasInputEdge(props.id, 'window_size'))
    const min_periods = ref(props.data.param.min_periods)
    const min_periodsDisabled = computed(() => hasInputEdge(props.id, 'min_periods'))
    const result_col = ref(props.data.param.result_col || '')
    const method = ["mean", "std", "sum", "min", "max"]
    const methodChinese = ['平均值', '标准差', '总和', '最小值', '最大值']
    const defaultSelectedMethod = method.indexOf(props.data.param.method)
    const table_type = computed(() => getInputType(props.id, 'table'))
    const schema_type = computed(():Type|'default' => props.data.schema_out?.['table']?.type || 'default')
    const outputTableHasErr = computed(() => handleOutputError(props.id, 'table'))
    const errMsg = ref<string[]>([])
    const colHasErr = ref({
        id: 'col',
        value: false
    })
    const window_sizeHasErr = ref({
        id: 'window_size',
        value: false
    })
    const min_periodsHasErr = ref({
        id: 'min_periods',
        value: false
    })
    const result_colHasErr = ref({
        id: 'result_col',
        value: false
    })
    const methodHasErr = ref({
        id: 'method',
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
    const onUpdateWindow_size = () => {
        props.data.param.window_size = window_size.value
    }
    const onUpdateMin_periods = () => {
        props.data.param.min_periods = min_periods.value
    }
    const onUpdateResult_col = () => {
        props.data.param.result_col = result_col.value
    }
    const onSelectChangeMethod = (e: any) => {
        const selected_method = method[e] as 'mean' | 'std' | 'sum' | 'min' | 'max'
        props.data.param.method = selected_method
    }


    watch(() => JSON.stringify(props.data.error), () => {
        errMsg.value = []
        handleExecError(props.data.error, errMsg)
        handleParamError(props.data.error, errMsg, colHasErr, window_sizeHasErr, min_periodsHasErr, result_colHasErr, methodHasErr)
        handleValidationError(props.id, props.data.error, errMsg, inputTableHasErr)
    }, {immediate: true})

</script>

<style lang="scss" scoped>
    @use '../../../common/global.scss' as *;
    @use '../../../common/node.scss' as *;
    .RollingNodeLayout {
        height: 100%;
        .data {
            padding-top: $node-padding-top;
            padding-bottom: $node-padding-bottom;
            .input-table {
                margin-bottom: $node-margin;
            }
            .input-window_size, .input-min_periods {
                margin-bottom: 2px;
            }
            .col, .window_size, .min_periods, .result_col, .method {
                padding: 0 $node-padding-hor;
                margin-bottom: $node-margin;
            }
        }
    }
    .all-handle-color {
        background: $table-color;
    }
</style>