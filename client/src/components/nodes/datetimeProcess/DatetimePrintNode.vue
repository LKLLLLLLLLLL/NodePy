<template>
    <div class="DatetimePrintNodeLayout nodes-style" :class="[{'nodes-selected': selected}, {'nodes-dbclicked': data.dbclicked}]">
        <NodeTitle node-category='datetimeProcess'>日期格式化</NodeTitle>
        <Timer :node-id="id" :default-time="data.runningtime"/>
        <div class="data">
            <div class="input-datetime port">
                <div class="input-port-description">
                    日期输入
                </div>
                <Handle id="datetime" type="target" :position="Position.Left" :class="[`${datetime_type}-handle-color`, {'node-errhandle': datetimeHasErr.value}]"/>
            </div>
            <div class="format">
                <div class="param-description" :class="{'node-has-paramerr': formatHasErr.value}">
                    格式
                </div>
                <NodepyStringInput
                    v-model="format"
                    @update-value="onUpdateFormat"
                    class="nodrag"
                    placeholder="e.g. %Y-%m-%d %H:%M:%S"
                />
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
    import {computed, ref, watch} from 'vue'
    import type { server__models__schema__Schema__Type } from '@/utils/api'
    import type { NodeProps } from '@vue-flow/core'
    import { Position, Handle } from '@vue-flow/core'
    import { handleValidationError, handleExecError, handleParamError, handleOutputError } from '../handleError'
    import ErrorMsg from '../tools/ErrorMsg.vue'
    import NodeTitle from '../tools/NodeTitle.vue'
    import Timer from '../tools/Timer.vue'
    import { getInputType } from '../getInputType'
    import NodepyStringInput from '../tools/Nodepy-StringInput.vue'
    import type { DatetimePrintNodeData } from '@/types/nodeTypes'


    const props = defineProps<NodeProps<DatetimePrintNodeData>>()
    const format = ref(props.data.param.format)
    const datetime_type = computed(() => getInputType(props.id, 'datetime'))
    const schema_type = computed(():server__models__schema__Schema__Type|'default' => props.data.schema_out?.['output']?.type || 'default')
    const outputHasErr = computed(() => handleOutputError(props.id, 'output'))
    const errMsg = ref<string[]>([])
    const formatHasErr = ref({
        id: 'format',
        value: false
    })
    const datetimeHasErr = ref({
        handleId: 'datetime',
        value: false
    })


    const onUpdateFormat = (e: any) => {
        props.data.param.format = format.value
    }


    watch(() => JSON.stringify(props.data.error), () => {
        errMsg.value = []
        handleExecError(props.data.error, errMsg)
        handleParamError(props.data.error, errMsg, formatHasErr)
        handleValidationError(props.id, props.data.error, errMsg, datetimeHasErr)
    }, {immediate: true})

</script>

<style lang="scss" scoped>
    @use '../../../common/global.scss' as *;
    @use '../../../common/node.scss' as *;
    .DatetimePrintNodeLayout {
        height: 100%;
        .data {
            padding-top: $node-padding-top;
            padding-bottom: $node-padding-bottom;
            .input-datetime {
                margin-bottom: $node-margin;
            }
            .format {
                padding: 0 $node-padding-hor;
                margin-bottom: $node-margin;
            }
        }
    }
    .all-handle-color {
        background: $datetime-color;
    }
</style>
