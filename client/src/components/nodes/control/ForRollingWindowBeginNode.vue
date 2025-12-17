<template>
    <div class="ForRollingWindowBeginNodeLayout nodes-style" :class="[{'nodes-selected': selected}, {'nodes-dbclicked': data.dbclicked}]">
        <NodeTitle node-category='control'>滑动窗口循环起始</NodeTitle>
        <Timer :node-id="id" :default-time="data.runningtime"/>
        <div class="data">
            <div class="input-table port">
                <div class="input-port-description">
                    表格输入
                </div>
                <Handle id="table" type="target" :position="Position.Left" :class="[`${table_type}-handle-color`, {'node-errhandle': inputTableHasErr.value}]"/>
            </div>
            <div class="window_size">
                <div class="param-description" :class="{'node-has-paramerr': window_sizeHasErr.value}">
                    窗口大小
                </div>
                <NodepyNumberInput
                    v-model="windowSize"
                    class="nodrag"
                    @update-value="() => updateSimpleStringNumberBoolValue(data.param, 'window_size', windowSize)"
                 />
            </div>
            <div class="output-window port">
                <div class="output-port-description">
                    当前窗口
                </div>
                <Handle id="window" type="source" :position="Position.Right" :class="[`${schema_type}-handle-color`, {'node-errhandle': windowHasErr}]"/>
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
    import NodepyNumberInput from '../tools/Nodepy-NumberInput/Nodepy-NumberInput.vue'
    import { updateSimpleStringNumberBoolValue } from '../updateParam'
    import type { ForRollingWindowBeginNodeData } from '@/types/nodeTypes'


    const props = defineProps<NodeProps<ForRollingWindowBeginNodeData>>()
    const windowSize = ref(props.data.param.window_size)
    const table_type = computed(() => getInputType(props.id, 'table'))
    const schema_type = computed(():server__models__schema__Schema__Type|'default' => props.data.schema_out?.['window']?.type || 'default')
    const windowHasErr = computed(() => handleOutputError(props.id, 'window'))
    const errMsg = ref<string[]>([])
    const window_sizeHasErr = ref({
        id: 'window_size',
        value: false
    })
    const inputTableHasErr = ref({
        handleId: 'table',
        value: false
    })


    watch(() => JSON.stringify(props.data.error), () => {
        errMsg.value = []
        handleExecError(props.data.error, errMsg)
        handleParamError(props.data.error, errMsg, window_sizeHasErr)
        handleValidationError(props.id, props.data.error, errMsg, inputTableHasErr)
    }, {immediate: true})

</script>

<style lang="scss" scoped>
    @use '../../../common/global.scss' as *;
    @use '../../../common/node.scss' as *;
    .ForRollingWindowBeginNodeLayout {
        height: 100%;
        .data {
            padding-top: $node-padding-top;
            padding-bottom: $node-padding-bottom;
            .input-table {
                margin-bottom: $node-margin;
            }
            .window_size {
                padding: 0 $node-padding-hor;
                margin-bottom: $node-margin;
            }
        }
    }
    .all-handle-color {
        background: $table-color;
    }
</style>