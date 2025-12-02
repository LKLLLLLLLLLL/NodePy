<template>
    <div class="SliceNodeLayout nodes-style" :class="[{'nodes-selected': selected}, {'nodes-dbclicked': data.dbclicked}]">
        <NodeTitle node-category='stringProcess'>字符串切片节点</NodeTitle>
        <Timer :node-id="id" :default-time="data.runningtime"/>
        <div class="data">
            <div class="input-input port">
                <div class="input-port-description">
                    字符串输入
                </div>
                <Handle id="input" type="target" :position="Position.Left" :class="[`${input_type}-handle-color`, {'node-errhandle': inputHasErr.value}]"/>
            </div>
            <div class="start port">
                <div class="param-description" :class="{'node-has-paramerr': startHasErr.value}">
                    起始索引输入
                </div>
                <NodepyNumberInput
                    v-model="start"
                    class="nodrag"
                    @update-value="onUpdateStart"
                    :disabled="startDisabled"
                    :allow-empty="true"
                 />
                <Handle id="start" type="target" :position="Position.Left" :class="[`${inputStart_type}-handle-color`, {'node-errhandle': inputStartHasErr.value}]"/>
            </div>
            <div class="end port">
                <div class="param-description" :class="{'node-has-paramerr': endHasErr.value}">
                    结束索引输入
                </div>
                <NodepyNumberInput
                    v-model="end"
                    class="nodrag"
                    @update-value="onUpdateEnd"
                    :disabled="endDisabled"
                    :allow-empty="true"
                 />
                <Handle id="end" type="target" :position="Position.Left" :class="[`${inputEnd_type}-handle-color`, {'node-errhandle': inputEndHasErr.value}]"/>
            </div>
            <div class="output-output port">
                <div class="output-port-description">
                    字符串输出
                </div>
                <Handle id="output" type="source" :position="Position.Right" :class="[`${schema_type}-handle-color`, {'node-errhandle': outputHasErr}]"/>
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
    import { hasInputEdge } from '../hasEdge'
    import ErrorMsg from '../tools/ErrorMsg.vue'
    import NodeTitle from '../tools/NodeTitle.vue'
    import Timer from '../tools/Timer.vue'
    import NodepyNumberInput from '../tools/Nodepy-NumberInput/Nodepy-NumberInput.vue'
    import type { SliceNodeData } from '@/types/nodeTypes'


    const props = defineProps<NodeProps<SliceNodeData>>()
    const start = ref(props.data.param.start)
    const startDisabled = computed(() => hasInputEdge(props.id, 'start'))
    const end = ref(props.data.param.end)
    const endDisabled = computed(() => hasInputEdge(props.id, 'end'))
    const input_type = computed(() => getInputType(props.id, 'input'))
    const inputStart_type = computed(() => getInputType(props.id, 'start'))
    const inputEnd_type = computed(() => getInputType(props.id, 'end'))
    const schema_type = computed(():Type|'default' => props.data.schema_out?.['output']?.type || 'default')
    const outputHasErr = computed(() => handleOutputError(props.id, 'output'))
    const errMsg = ref<string[]>([])
    const startHasErr = ref({
        id: 'start',
        value: false
    })
    const endHasErr = ref({
        id: 'end',
        value: false
    })
    const inputHasErr = ref({
        handleId: 'input',
        value: false
    })
    const inputStartHasErr = ref({
        handleId: 'start',
        value: false
    })
    const inputEndHasErr = ref({
        handleId: 'end',
        value: false
    })


    const onUpdateStart = () => {
        props.data.param.start = start.value
    }
    const onUpdateEnd = () => {
        props.data.param.end = end.value
    }


    watch(() => JSON.stringify(props.data.error), () => {
        errMsg.value = []
        handleExecError(props.data.error, errMsg)
        handleParamError(props.data.error, errMsg, startHasErr, endHasErr)
        handleValidationError(props.id, props.data.error, errMsg, inputHasErr, inputStartHasErr, inputEndHasErr)
    }, {immediate: true})

</script>

<style lang="scss" scoped>
    @use '../../../common/global.scss' as *;
    @use '../../../common/node.scss' as *;
    .SliceNodeLayout {
        height: 100%;
        .data {
            padding-top: $node-padding-top;
            padding-bottom: $node-padding-bottom;
            .input-input {
                margin-bottom: $node-margin;
            }
            .start, .end {
                padding: 0 $node-padding-hor;
                margin-bottom: $node-margin;
            }
        }
    }
    .all-handle-color[data-handleid="start"], .all-handle-color[data-handleid="end"] {
        background: $int-color;
    }
    .all-handle-color[data-handleid="input"] {
        background: $str-color;
    }
</style>