<template>
    <div class="PredictNodeLayout nodes-style" :class="[{'nodes-selected': selected}, {'nodes-dbclicked': data.dbclicked}]">
        <NodeTitle node-category="machineLearning">预测节点</NodeTitle>
        <Timer :node-id="id" :default-time="data.runningtime"/>
        <div class="data">
            <div class="input-table port">
                <div class="input-port-description">
                    表格输入
                </div>
                <Handle
                    id="table"
                    type="target"
                    :position="Position.Left"
                    :class="[`${table_type}-handle-color`, {'node-errhandle': inputTableHasErr.value}]"
                />
            </div>
            <div class="input-model port">
                <div class="input-port-description">
                    模型输入
                </div>
                <Handle
                    id="model"
                    type="target"
                    :position="Position.Left"
                    :class="[`${model_type}-handle-color`, {'node-errhandle': modelHasErr.value}]"
                />
            </div>
            <div class="output-table port">
                <div class="output-port-description">
                    表格输出
                </div>
                <Handle
                    id="table"
                    type="source"
                    :position="Position.Right"
                    :class="[`${schema_type}-handle-color`, {'node-errhandle': outputTableHasErr}]"
                />
            </div>
        </div>
        <ErrorMsg :err-msg="errMsg"/>
    </div>
</template>

<script lang="ts" setup>
    import type { server__models__schema__Schema__Type } from '@/utils/api'
    import type { NodeProps } from '@vue-flow/core'
    import { Handle, Position } from '@vue-flow/core'
    import { computed, ref, watch } from 'vue'
    import type { BaseData } from '../../../types/nodeTypes'
    import { getInputType } from '../getInputType'
    import { handleExecError, handleValidationError, handleOutputError } from '../handleError'
    import ErrorMsg from '../tools/ErrorMsg.vue'
    import NodeTitle from '../tools/NodeTitle.vue'
    import Timer from '../tools/Timer.vue'


    const props = defineProps<NodeProps<BaseData>>()
    const table_type = computed(() => getInputType(props.id, 'table'))
    const model_type = computed(() => getInputType(props.id, 'model'))
    const schema_type = computed(():server__models__schema__Schema__Type|'default' => props.data.schema_out?.['table']?.type || 'default')
    const outputTableHasErr = computed(() => handleOutputError(props.id, 'table'))
    const errMsg = ref<string[]>([])
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
        handleValidationError(props.id, props.data.error, errMsg, inputTableHasErr, modelHasErr)
    }, {immediate: true})

</script>

<style lang="scss" scoped>
    @use '../../../common/global.scss' as *;
    @use '../../../common/node.scss' as *;
    .PredictNodeLayout {
        height: 100%;
        .data {
            padding-top: $node-padding-top;
            padding-bottom: $node-padding-bottom;
            .input-table, .input-model {
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
