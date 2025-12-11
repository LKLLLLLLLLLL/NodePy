<template>
    <div class="LagFeatureNodeLayout nodes-style" :class="[{'nodes-selected': selected}, {'nodes-dbclicked': data.dbclicked}]">
        <NodeTitle node-category='machineLearning'>滞后特征节点</NodeTitle>
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
            <div class="lag_cols">
                <div class="param-description" :class="{'node-has-paramerr': lag_colsHasErr.value}">
                    特征列名
                </div>
                <NodepyMultiSelectMany
                    :options="lag_colsHint"
                    :default-selected="defaultSelectedLag_cols"
                    @select-change="onSelectChangeLag_cols"
                    @clear-select="clearSelectLag_cols"
                    class="nodrag"
                />
            </div>
            <div class="generate_target">
                <NodepyBoolValue
                    v-model="generate_target"
                    @update-value="onUpdateGenerate_target"
                    width="20px"
                    height="20px"
                >
                    是否生成预测列
                </NodepyBoolValue>
            </div>
            <div class="input-horizon port" v-show="data.param.generate_target">
                <div class="input-port-description" :class="{'node-has-paramerr': horizonHasErr.value}">
                    预测步长
                </div>
                <!-- <Handle id="horizon" type="target" :position="Position.Left" :class="[`${inputHorizon_type}-handle-color`, {'node-errhandle': inputHorizonHasErr.value}]"/> -->
            </div>
            <div class="horizon" v-show="data.param.generate_target">
                <NodepyNumberInput
                    v-model="horizon"
                    class="nodrag"
                    @update-value="onUpdateHorizon"
                    :disabled="horizonDisabled"
                 />
            </div>
            <div class="target_col" v-show="data.param.generate_target">
                <div class="param-description" :class="{'node-has-paramerr': target_colHasErr.value}">
                    预测列名
                </div>
                <NodepySelectMany
                    :options="target_colHint"
                    :default-selected="defaultSelectedTarget_col"
                    @select-change="onSelectChangeTarget_col"
                    @clear-select="clearSelectTarget_col"
                    class="nodrag"
                />
            </div>
            <div class="drop_nan">
                <NodepyBoolValue
                    v-model="drop_nan"
                    @update-value="onUpdateDrop_nan"
                    width="20px"
                    height="20px"
                >
                    是否删除NaN行
                </NodepyBoolValue>
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
    import NodepyBoolValue from '../tools/Nodepy-boolValue.vue'
    import NodepyMultiSelectMany from '../tools/Nodepy-multiSelectMany.vue'
    import NodepyNumberInput from '../tools/Nodepy-NumberInput/Nodepy-NumberInput.vue'
    import { hasInputEdge } from '../hasEdge'
    import type { LagFeatureNodeData } from '@/types/nodeTypes'


    const props = defineProps<NodeProps<LagFeatureNodeData>>()
    const window_size = ref(props.data.param.window_size)
    const window_sizeDisabled = computed(() => hasInputEdge(props.id, 'window_size'))
    const horizon = ref(props.data.param.horizon)
    const horizonDisabled = computed(() => hasInputEdge(props.id, 'horizon'))
    const lag_colsHint = computed(() => {
        if(props.data.hint?.lag_col_choices?.length === 0) return ['']
        return props.data.hint?.lag_col_choices || ['']
    })
    const lag_cols = ref(props.data.param.lag_cols)   //  used for defaultSelectedLag_cols
    const defaultSelectedLag_cols = computed(() => {
        const hintArray = lag_colsHint.value
        const selectedArray = lag_cols.value
        return selectedArray.map(item => hintArray.indexOf(item)).filter(idx => idx !== -1)
    })
    const generate_target = ref(props.data.param.generate_target)
    const target_colHint = computed(() => {
        if(props.data.hint?.target_col_choices?.length === 0) return ['']
        return props.data.hint?.target_col_choices || ['']
    })
    const target_col = ref(props.data.param.target_col)   //  used for defaultSelectedTarget_col
    const defaultSelectedTarget_col = computed(() => target_colHint.value.indexOf(target_col.value))
    const drop_nan = ref(props.data.param.drop_nan)
    const table_type = computed(() => getInputType(props.id, 'table'))
    const schema_type = computed(():server__models__schema__Schema__Type|'default' => props.data.schema_out?.['table']?.type || 'default')
    const outputTableHasErr = computed(() => handleOutputError(props.id, 'table'))
    const errMsg = ref<string[]>([])
    const window_sizeHasErr = ref({
        id: 'window_size',
        value: false
    })
    const horizonHasErr = ref({
        id: 'horizon',
        value: false
    })
    const lag_colsHasErr = ref({
        id: 'lag_cols',
        value: false
    })
    const target_colHasErr = ref({
        id: 'target_col',
        value: false
    })
    const inputTableHasErr = ref({
        handleId: 'table',
        value: false
    })


    const onUpdateWindow_size = () => {
        props.data.param.window_size = window_size.value
    }
    const onUpdateHorizon = () => {
        props.data.param.horizon = horizon.value
    }
    const onSelectChangeLag_cols = (e: any) => {
        props.data.param.lag_cols = e.map((idx: number) => lag_colsHint.value[idx])
    }
    const clearSelectLag_cols = (resolve: any) => {
        props.data.param.lag_cols = []
        lag_cols.value = props.data.param.lag_cols
        resolve()
    }
    const onUpdateGenerate_target = () => {
        props.data.param.generate_target = generate_target.value
    }
    const onSelectChangeTarget_col = (e: any) => {
        props.data.param.target_col = target_colHint.value[e]
    }
    const clearSelectTarget_col = (resolve: any) => {
        props.data.param.target_col = ''
        target_col.value = props.data.param.target_col
        resolve()
    }
    const onUpdateDrop_nan = () => {
        props.data.param.drop_nan = drop_nan.value
    }


    watch(() => JSON.stringify(props.data.error), () => {
        errMsg.value = []
        handleExecError(props.data.error, errMsg)
        handleParamError(props.data.error, errMsg, window_sizeHasErr, horizonHasErr, lag_colsHasErr, target_colHasErr)
        handleValidationError(props.id, props.data.error, errMsg, inputTableHasErr)
    }, {immediate: true})

</script>

<style lang="scss" scoped>
    @use '../../../common/global.scss' as *;
    @use '../../../common/node.scss' as *;
    .LagFeatureNodeLayout {
        height: 100%;
        .data {
            padding-top: $node-padding-top;
            padding-bottom: $node-padding-bottom;
            .input-table {
                margin-bottom: $node-margin;
            }
            .input-window_size, .input-horizon {
                margin-bottom: 2px;
            }
            .window_size, .horizon, .lag_cols, .generate_target, .target_col, .drop_nan {
                padding: 0 $node-padding-hor;
                margin-bottom: $node-margin;
            }
        }
    }
    .all-handle-color {
        background: $table-color;
    }
</style>
