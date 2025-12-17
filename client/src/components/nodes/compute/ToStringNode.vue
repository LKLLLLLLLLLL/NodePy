<template>
    <div class="ToStringNodeLayout nodes-style" :class="[{'nodes-selected': selected}, {'nodes-dbclicked': data.dbclicked}]">
        <NodeTitle node-category="compute">转为字符串</NodeTitle>
        <Timer :node-id="id" :default-time="data.runningtime"/>
        <div class="data">
            <div class="input-input port">
                <div class="input-port-description">
                    输入
                </div>
                <Handle
                    id="input"
                    type="target"
                    :position="Position.Left"
                    :class="[`${input_type}-handle-color`, {'node-errhandle': inputHaserr.value}]"
                />
            </div>
            <div class="output-output port">
                <div class="output-port-description">
                    字符串输出
                </div>
                <Handle
                    id="output"
                    type="source"
                    :position="Position.Right"
                    :class="[`${schema_type}-handle-color`, {'node-errhandle': outputHasErr}]"
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
    const input_type = computed(() => getInputType(props.id, 'input'))
    const schema_type = computed(():server__models__schema__Schema__Type|'default' => props.data.schema_out?.['output']?.type || 'default')
    const outputHasErr = computed(() => handleOutputError(props.id, 'output'))
    const errMsg = ref<string[]>([])
    const inputHaserr = ref({
        handleId: 'input',
        value: false
    })


    watch(() => JSON.stringify(props.data.error), () => {
        errMsg.value = []
        handleExecError(props.data.error, errMsg)
        handleValidationError(props.id, props.data.error, errMsg, inputHaserr)
    }, {immediate: true})

</script>

<style lang="scss" scoped>
    @use '../../../common/global.scss' as *;
    @use '../../../common/node.scss' as *;
    .ToStringNodeLayout {
        height: 100%;
        .data {
            padding-top: $node-padding-top;
            padding-bottom: $node-padding-bottom;
            .input-input {
                margin-bottom: $node-margin;
            }
        }
    }
    .all-handle-color {
        background: conic-gradient(
            $int-color 0 120deg,
            $float-color 0 240deg,
            $bool-color 0 360deg
        );
    }
</style>
