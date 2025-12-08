<template>
    <div class="LinearRegressionNodeLayout nodes-style" :class="[{'nodes-selected': selected}, {'nodes-dbclicked': data.dbclicked}]">
        <NodeTitle node-category="machineLearning">线性回归节点</NodeTitle>
        <Timer :node-id="id" :default-time="data.runningtime"/>
        <div class="data">
            <div class="input-table port">
                <div class="input-port-description">
                    表格输入
                </div>
                <Handle id="table" type="target" :position="Position.Left" :class="[`${table_type}-handle-color`, {'node-errhandle': inputTableHasErr.value}]"/>
            </div>
            <div class="feature_cols">
                <div class="param-description" :class="{'node-has-paramerr': feature_colsHasErr.value}">
                    特征列名
                </div>
                <NodepyMultiSelectMany
                    :options="feature_colsHint"
                    :default-selected="defaultSelectedFeature_cols"
                    @select-change="onSelectChangeFeature_cols"
                    @clear-select="clearSelectFeature_cols"
                    class="nodrag"
                />
            </div>
            <div class="target_col">
                <div class="param-description" :class="{'node-has-paramerr': target_colHasErr.value}">
                    目标列名
                </div>
                <NodepySelectMany
                    :options="target_colHint"
                    :default-selected="defaultSelectedTarget_col"
                    @select-change="onSelectChangeTarget_col"
                    @clear-select="clearSelectTarget_col"
                    class="nodrag"
                />
            </div>
            <div class="output-model port">
                <div class="output-port-description">
                    模型输出
                </div>
                <Handle id="model" type="source" :position="Position.Right" :class="[`${schema_type}-handle-color`, {'node-errhandle': modelHasErr}]"/>
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
    import NodepyMultiSelectMany from '../tools/Nodepy-multiSelectMany.vue'
    import NodepySelectMany from '../tools/Nodepy-selectMany.vue'
    import type { LinearRegressionNodeData } from '@/types/nodeTypes'


    const props = defineProps<NodeProps<LinearRegressionNodeData>>()
    const feature_colsHint = computed(() => {
        if(props.data.hint?.feature_col_choices?.length === 0) return ['']
        return props.data.hint?.feature_col_choices || ['']
    })
    const feature_cols = ref(props.data.param.feature_cols)   //  used for defaultSelectedFeature_cols
    const defaultSelectedFeature_cols = computed(() => {
        const hintArray = feature_colsHint.value
        const selectedArray = feature_cols.value
        return selectedArray.map(item => hintArray.indexOf(item)).filter(idx => idx !== -1)
    })
    const target_colHint = computed(() => {
        if(props.data.hint?.target_col_choices?.length === 0) return ['']
        return props.data.hint?.target_col_choices || ['']
    })
    const target_col = ref(props.data.param.target_col)   //  used for defaultSelectedTarget_col
    const defaultSelectedTarget_col = computed(() => target_colHint.value.indexOf(target_col.value))
    const table_type = computed(() => getInputType(props.id, 'table'))
    const schema_type = computed(():server__models__schema__Schema__Type|'default' => props.data.schema_out?.['model']?.type || 'default')
    const modelHasErr = computed(() => handleOutputError(props.id, 'model'))
    const errMsg = ref<string[]>([])
    const feature_colsHasErr = ref({
        id: 'feature_cols',
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


    const onSelectChangeFeature_cols = (e: any) => {
        props.data.param.feature_cols = e.map((idx: number) => feature_colsHint.value[idx])
    }
    const clearSelectFeature_cols = (resolve: any) => {
        props.data.param.feature_cols = []
        feature_cols.value = props.data.param.feature_cols
        resolve()
    }
    const onSelectChangeTarget_col = (e: any) => {
        props.data.param.target_col = target_colHint.value[e]
    }
    const clearSelectTarget_col = (resolve: any) => {
        props.data.param.target_col = ''
        target_col.value = props.data.param.target_col
        resolve()
    }


    watch(() => JSON.stringify(props.data.error), () => {
        errMsg.value = []
        handleExecError(props.data.error, errMsg)
        handleParamError(props.data.error, errMsg, feature_colsHasErr, target_colHasErr)
        handleValidationError(props.id, props.data.error, errMsg, inputTableHasErr)
    }, {immediate: true})

</script>

<style lang="scss" scoped>
    @use '../../../common/global.scss' as *;
    @use '../../../common/node.scss' as *;
    .LinearRegressionNodeLayout {
        height: 100%;
        .data {
            padding-top: $node-padding-top;
            padding-bottom: $node-padding-bottom;
            .input-table {
                margin-bottom: $node-margin;
            }
            .feature_cols, .target_col {
                padding: 0 $node-padding-hor;
                margin-bottom: $node-margin;
            }
        }
    }
    .all-handle-color {
        background: $table-color;
    }
</style>
