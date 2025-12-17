<template>
    <div class="KMeansClusteringNodeLayout nodes-style" :class="[{'nodes-selected': selected}, {'nodes-dbclicked': data.dbclicked}]">
        <NodeTitle node-category="machineLearning">K-Means聚类</NodeTitle>
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
            <div class="n_clusters">
                <div class="param-description" :class="{'node-has-paramerr': n_clustersHasErr.value}">
                    聚类数量
                </div>
                <NodepyNumberInput
                    v-model="n_clusters"
                    class="nodrag"
                    @update-value="() => updateSimpleStringNumberBoolValue(data.param, 'n_clusters', n_clusters)"
                 />
            </div>
            <div class="output-table port">
                <div class="output-port-description">
                    表格输出
                </div>
                <Handle id="table" type="source" :position="Position.Right" :class="[`${tableSchema_type}-handle-color`, {'node-errhandle': tableHasErr}]"/>
            </div>
            <div class="output-model port">
                <div class="output-port-description">
                    模型输出
                </div>
                <Handle id="model" type="source" :position="Position.Right" :class="[`${modelSchema_type}-handle-color`, {'node-errhandle': modelHasErr}]"/>
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
    import NodepyNumberInput from '../tools/Nodepy-NumberInput/Nodepy-NumberInput.vue'
    import { updateSimpleMultiSelectMany, updateSimpleStringNumberBoolValue } from '../updateParam'
    import type { KMeansClusteringNodeData } from '@/types/nodeTypes'


    const props = defineProps<NodeProps<KMeansClusteringNodeData>>()
    const feature_colsHint = computed(() => {
        if(props.data.hint?.feature_cols_choices?.length === 0) return ['']
        return props.data.hint?.feature_cols_choices || ['']
    })
    const defaultSelectedFeature_cols = ref(props.data.param.feature_cols.map(item => feature_colsHint.value.indexOf(item)).filter(idx => idx !== -1))
    const n_clusters = ref(props.data.param.n_clusters)
    const table_type = computed(() => getInputType(props.id, 'table'))
    const tableSchema_type = computed(():server__models__schema__Schema__Type|'default' => props.data.schema_out?.['table']?.type || 'default')
    const tableHasErr = computed(() => handleOutputError(props.id, 'table'))
    const modelSchema_type = computed(():server__models__schema__Schema__Type|'default' => props.data.schema_out?.['model']?.type || 'default')
    const modelHasErr = computed(() => handleOutputError(props.id, 'model'))
    const errMsg = ref<string[]>([])
    const feature_colsHasErr = ref({
        id: 'feature_cols',
        value: false
    })
    const n_clustersHasErr = ref({
        id: 'n_clusters',
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


    watch(() => JSON.stringify(props.data.error), () => {
        errMsg.value = []
        handleExecError(props.data.error, errMsg)
        handleParamError(props.data.error, errMsg, feature_colsHasErr, n_clustersHasErr)
        handleValidationError(props.id, props.data.error, errMsg, inputTableHasErr)
    }, {immediate: true})

</script>

<style lang="scss" scoped>
    @use '../../../common/global.scss' as *;
    @use '../../../common/node.scss' as *;
    .KMeansClusteringNodeLayout {
        height: 100%;
        .data {
            padding-top: $node-padding-top;
            padding-bottom: $node-padding-bottom;
            .input-table {
                margin-bottom: $node-margin;
            }
            .feature_cols, .n_clusters {
                padding: 0 $node-padding-hor;
                margin-bottom: $node-margin;
            }
            .output-table {
                margin-bottom: $node-margin;
            }
        }
    }
    .all-handle-color {
        background: $table-color;
    }
</style>