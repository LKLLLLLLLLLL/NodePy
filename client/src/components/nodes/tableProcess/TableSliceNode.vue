<template>
    <div class="TableSliceNodeLayout nodes-style" :class="[{'nodes-selected': selected}, {'nodes-dbclicked': data.dbclicked}]">
        <NodeTitle node-category='tableProcess'>表格切片</NodeTitle>
        <Timer :node-id="id" :default-time="data.runningtime"/>
        <div class="data">
            <div class="input-table port">
                <div class="input-port-description">
                    表格输入
                </div>
                <Handle id="table" type="target" :position="Position.Left" :class="[`${table_type}-handle-color`, {'node-errhandle': inputTableHasErr.value}]"/>
            </div>
            <div class="input-begin port">
                <div class="input-port-description" :class="{'node-has-paramerr': beginHasErr.value}">
                     起始行
                </div>
                <!-- <Handle id="begin" type="target" :position="Position.Left" :class="[`${inputBegin_type}-handle-color`, {'node-errhandle': inputBeginHasErr.value}]"/> -->
            </div>
            <div class="begin">
                <NodepyNumberInput
                    v-model="begin"
                    class="nodrag"
                    @update-value="onUpdateBegin"
                    :disabled="beginDisabled"
                    :allow-empty="true"
                 />
            </div>
            <div class="input-end port">
                <div class="input-port-description" :class="{'node-has-paramerr': endHasErr.value}">
                    结束行
                </div>
                <!-- <Handle id="end" type="target" :position="Position.Left" :class="[`${inputEnd_type}-handle-color`, {'node-errhandle': inputEndHasErr.value}]"/> -->
            </div>
            <div class="end">
                <NodepyNumberInput
                    v-model="end"
                    class="nodrag"
                    @update-value="onUpdateEnd"
                    :disabled="endDisabled"
                    :allow-empty="true"
                 />
            </div>
            <div class="input-step port">
                <div class="input-port-description" :class="{'node-has-paramerr': stepHasErr.value}">
                    步长
                </div>
                <!-- <Handle id="step" type="target" :position="Position.Left" :class="[`${inputStep_type}-handle-color`, {'node-errhandle': inputStepHasErr.value}]"/> -->
            </div>
            <div class="step">
                <NodepyNumberInput
                    v-model="step"
                    class="nodrag"
                    @update-value="onUpdateStep"
                    :disabled="stepDisabled"
                    :allow-empty="true"
                 />
            </div>
            <div class="output-sliced_table port">
                <div class="output-port-description">
                    切片表格输出
                </div>
                <Handle id="sliced_table" type="source" :position="Position.Right" :class="[`${sliced_table_type}-handle-color`, {'node-errhandle': sliced_tableHasErr}]"/>
            </div>
            <div class="output-remaining_table port">
                <div class="output-port-description">
                    剩余表格输出
                </div>
                <Handle id="remaining_table" type="source" :position="Position.Right" :class="[`${remaining_table_type}-handle-color`, {'node-errhandle': remaining_tableHasErr}]"/>
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
    import { hasInputEdge } from '../hasEdge'
    import ErrorMsg from '../tools/ErrorMsg.vue'
    import NodeTitle from '../tools/NodeTitle.vue'
    import Timer from '../tools/Timer.vue'
    import NodepyNumberInput from '../tools/Nodepy-NumberInput/Nodepy-NumberInput.vue'
    import type { TableSliceNodeData } from '@/types/nodeTypes'


    const props = defineProps<NodeProps<TableSliceNodeData>>()
    const begin = ref(props.data.param.begin)
    const beginDisabled = computed(() => hasInputEdge(props.id, 'begin'))
    const end = ref(props.data.param.end)
    const endDisabled = computed(() => hasInputEdge(props.id, 'end'))
    const step = ref(props.data.param.step)
    const stepDisabled = computed(() => hasInputEdge(props.id, 'step'))
    const table_type = computed(() => getInputType(props.id, 'table'))
    const sliced_table_type = computed(():server__models__schema__Schema__Type|'default' => props.data.schema_out?.['sliced_table']?.type || 'default')
    const remaining_table_type = computed(():server__models__schema__Schema__Type|'default' => props.data.schema_out?.['remaining_table']?.type || 'default')
    const sliced_tableHasErr = computed(() => handleOutputError(props.id, 'sliced_table'))
    const remaining_tableHasErr = computed(() => handleOutputError(props.id, 'remaining_table'))
    const errMsg = ref<string[]>([])
    const beginHasErr = ref({
        id: 'begin',
        value: false
    })
    const endHasErr = ref({
        id: 'end',
        value: false
    })
    const stepHasErr = ref({
        id: 'step',
        value: false
    })
    const inputTableHasErr = ref({
        handleId: 'table',
        value: false
    })


    const onUpdateBegin = () => {
        props.data.param.begin = begin.value
    }
    const onUpdateEnd = () => {
        props.data.param.end = end.value
    }
    const onUpdateStep = () => {
        props.data.param.step = step.value
    }


    watch(() => JSON.stringify(props.data.error), () => {
        errMsg.value = []
        handleExecError(props.data.error, errMsg)
        handleParamError(props.data.error, errMsg, beginHasErr, endHasErr, stepHasErr)
        handleValidationError(props.id, props.data.error, errMsg, inputTableHasErr)
    }, {immediate: true})

</script>

<style lang="scss" scoped>
    @use '../../../common/global.scss' as *;
    @use '../../../common/node.scss' as *;
    .TableSliceNodeLayout {
        height: 100%;
        .data {
            padding-top: $node-padding-top;
            padding-bottom: $node-padding-bottom;
            .input-table {
                margin-bottom: $node-margin;
            }
            .input-begin, .input-end, .input-step {
                margin-bottom: 2px;
            }
            .begin, .end, .step {
                padding: 0 $node-padding-hor;
                margin-bottom: $node-margin;
            }
            .output-sliced_table {
                margin-bottom: $node-margin;
            }
        }
    }
    .all-handle-color[data-handleid="start"], .all-handle-color[data-handleid="end"], .all-handle-color[data-handleid="step"] {
        background: $int-color;
    }
    .all-handle-color[data-handleid="table"] {
        background: $table-color;
    }
</style>
