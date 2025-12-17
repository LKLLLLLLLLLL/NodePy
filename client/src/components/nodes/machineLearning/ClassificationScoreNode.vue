<template>
    <div class="ClassificationScoreNodeLayout nodes-style" :class="[{'nodes-selected': selected}, {'nodes-dbclicked': data.dbclicked}]">
        <NodeTitle node-category="machineLearning">分类模型评分</NodeTitle>
        <Timer :node-id="id" :default-time="data.runningtime"/>
        <div class="data">
            <div class="input-table port">
                <div class="input-port-description">
                    表格输入
                </div>
                <Handle id="table" type="target" :position="Position.Left" :class="[`${table_type}-handle-color`, {'node-errhandle': inputTableHasErr.value}]"/>
            </div>
            <div class="input-model port">
                <div class="input-port-description">
                    模型输入
                </div>
                <Handle id="model" type="target" :position="Position.Left" :class="[`${model_type}-handle-color`, {'node-errhandle': modelHasErr.value}]"/>
            </div>
            <div class="metric">
                <div class="param-description" :class="{'node-has-paramerr': metricHasErr.value}">
                    指标
                </div>
                <NodepySelectMany
                    :options="metric"
                    :default-selected="defaultSelected"
                    @select-change="(e:any) => updateSimpleSelectMany(data.param, 'metric', metric, e)"
                    class="nodrag"
                />
            </div>
            <div class="output-score port">
                <div class="output-port-description">
                    评分
                </div>
                <Handle id="score" type="source" :position="Position.Right" :class="[`${schema_type}-handle-color`, {'node-errhandle': scoreHasErr}]"/>
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
    import { updateSimpleSelectMany } from '../updateParam'
    import type { ClassificationScoreNodeData } from '@/types/nodeTypes'


    const props = defineProps<NodeProps<ClassificationScoreNodeData>>()
    const metric = ["accuracy", "f1", "precision", "recall"]
    const defaultSelected = metric.indexOf(props.data.param.metric)
    const table_type = computed(() => getInputType(props.id, 'table'))
    const model_type = computed(() => getInputType(props.id, 'model'))
    const schema_type = computed(():server__models__schema__Schema__Type|'default' => props.data.schema_out?.['score']?.type || 'default')
    const scoreHasErr = computed(() => handleOutputError(props.id, 'score'))
    const errMsg = ref<string[]>([])
    const metricHasErr = ref({
        id: 'metric',
        value: false
    })
    const inputTableHasErr = ref({
        handleId: 'table',
        value: false
    })
    const modelHasErr = ref({
        handleId: 'model',
        value: false
    })


    watch(() => JSON.stringify(props.data.error), () => {
        errMsg.value = []
        handleExecError(props.data.error, errMsg)
        handleParamError(props.data.error, errMsg, metricHasErr)
        handleValidationError(props.id, props.data.error, errMsg, inputTableHasErr, modelHasErr)
    }, {immediate: true})

</script>

<style lang="scss" scoped>
    @use '../../../common/global.scss' as *;
    @use '../../../common/node.scss' as *;
    .ClassificationScoreNodeLayout {
        height: 100%;
        .data {
            padding-top: $node-padding-top;
            padding-bottom: $node-padding-bottom;
            .input-table, .input-model {
                margin-bottom: $node-margin;
            }
            .metric {
                padding: 0 $node-padding-hor;
                margin-bottom: $node-margin;
            }
        }
    }
    .all-handle-color[data-handleid="table"] {
        background: $table-color;
    }
    .all-handle-color[data-handleid="model"] {
        background: $model-color;
    }
</style>