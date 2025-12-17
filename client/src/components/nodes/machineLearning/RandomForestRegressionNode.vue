<template>
    <div class="RandomForestRegressionNodeLayout nodes-style" :class="[{'nodes-selected': selected}, {'nodes-dbclicked': data.dbclicked}]">
        <NodeTitle node-category="machineLearning">随机森林回归</NodeTitle>
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
                    特征列
                </div>
                <NodepyMultiSelectMany
                    :options="feature_colsHint"
                    :default-selected="defaultSelectedFeature_cols"
                    @select-change="(e: any) => updateSimpleMultiSelectMany(data.param, 'feature_cols', feature_colsHint, e)"
                    @clear-select="clearSelectFeature_cols"
                    class="nodrag"
                />
            </div>
            <div class="target_col">
                <div class="param-description" :class="{'node-has-paramerr': target_colHasErr.value}">
                    目标列
                </div>
                <NodepySelectMany
                    :options="target_colHint"
                    :default-selected="defaultSelectedTarget_col"
                    @select-change="(e: any) => updateSimpleSelectMany(data.param, 'target_col', target_colHint, e)"
                    @clear-select="clearSelectTarget_col"
                    class="nodrag"
                />
            </div>
            <div class="n_estimators">
                <div class="param-description" :class="{'node-has-paramerr': n_estimatorsHasErr.value}">
                    树的数量
                </div>
                <NodepyNumberInput
                    v-model="n_estimators"
                    class="nodrag"
                    @update-value="() => updateSimpleStringNumberBoolValue(data.param, 'n_estimators', n_estimators)"
                 />
            </div>
            <div class="limit_max_depth">
                <NodepyBoolValue
                    v-model="limit_max_depth"
                    @update-value="() => updateSimpleStringNumberBoolValue(data.param, 'limit_max_depth', limit_max_depth)"
                    width="20px"
                    height="20px"
                >
                    限制最大深度
                </NodepyBoolValue>
            </div>
            <div class="max_depth" v-show="limit_max_depth">
                <div class="param-description" :class="{'node-has-paramerr': max_depthHasErr.value}">
                    最大深度
                </div>
                <NodepyNumberInput
                    v-model="max_depth"
                    class="nodrag"
                    @update-value="() => updateSimpleStringNumberBoolValue(data.param, 'max_depth', max_depth)"
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
    import NodepyNumberInput from '../tools/Nodepy-NumberInput/Nodepy-NumberInput.vue'
    import NodepyBoolValue from '../tools/Nodepy-boolValue.vue'
    import { updateSimpleStringNumberBoolValue, updateSimpleSelectMany, updateSimpleMultiSelectMany } from '../updateParam'
    import type { RandomForestRegressionNodeData } from '@/types/nodeTypes'


    const props = defineProps<NodeProps<RandomForestRegressionNodeData>>()
    const feature_colsHint = computed(() => {
        if(props.data.hint?.feature_col_choices?.length === 0) return ['']
        return props.data.hint?.feature_col_choices || ['']
    })
    const defaultSelectedFeature_cols = ref(props.data.param.feature_cols.map(item => feature_colsHint.value.indexOf(item)).filter(idx => idx !== -1))
    const target_colHint = computed(() => {
        if(props.data.hint?.target_col_choices?.length === 0) return ['']
        return props.data.hint?.target_col_choices || ['']
    })
    const defaultSelectedTarget_col = ref(target_colHint.value.indexOf(props.data.param.target_col))
    const n_estimators = ref(props.data.param.n_estimators)
    const limit_max_depth = ref(props.data.param.limit_max_depth)
    const max_depth = ref(props.data.param.max_depth)
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
    const n_estimatorsHasErr = ref({
        id: 'n_estimators',
        value: false
    })
    const max_depthHasErr = ref({
        id: 'max_depth',
        value: false
    })
    const inputTableHasErr = ref({
        handleId: 'table',
        value: false
    })


    const clearSelectFeature_cols = (resolve: any) => {
        props.data.param.feature_cols = []
        defaultSelectedFeature_cols.value = []
        resolve()
    }
    const clearSelectTarget_col = (resolve: any) => {
        props.data.param.target_col = ''
        defaultSelectedTarget_col.value = -1
        resolve()
    }


    watch(() => JSON.stringify(props.data.error), () => {
        errMsg.value = []
        handleExecError(props.data.error, errMsg)
        handleParamError(props.data.error, errMsg, feature_colsHasErr, target_colHasErr, n_estimatorsHasErr, max_depthHasErr)
        handleValidationError(props.id, props.data.error, errMsg, inputTableHasErr)
    }, {immediate: true})

</script>

<style lang="scss" scoped>
    @use '../../../common/global.scss' as *;
    @use '../../../common/node.scss' as *;
    .RandomForestRegressionNodeLayout {
        height: 100%;
        .data {
            padding-top: $node-padding-top;
            padding-bottom: $node-padding-bottom;
            .input-table {
                margin-bottom: $node-margin;
            }
            .feature_cols, .target_col, .n_estimators, .limit_max_depth, .max_depth {
                padding: 0 $node-padding-hor;
                margin-bottom: $node-margin;
            }
        }
    }
    .all-handle-color {
        background: $table-color;
    }
</style>