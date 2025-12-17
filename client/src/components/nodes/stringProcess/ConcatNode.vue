<template>
    <div class="ConcatNodeLayout nodes-style" :class="[{'nodes-selected': selected}, {'nodes-dbclicked': data.dbclicked}]">
        <NodeTitle node-category='stringProcess'>字符串拼接</NodeTitle>
        <Timer :node-id="id" :default-time="data.runningtime"/>
        <div class="data">
            <div class="input-input1 port">
                <div class="input-port-description">
                    字符串1
                </div>
                <Handle id="input1" type="target" :position="Position.Left" :class="[`${input1_type}-handle-color`, {'node-errhandle': input1HasErr.value}]"/>
            </div>
            <div class="input-input2 port">
                <div class="input-port-description">
                    字符串2
                </div>
                <Handle id="input2" type="target" :position="Position.Left" :class="[`${input2_type}-handle-color`, {'node-errhandle': input2HasErr.value}]"/>
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
    const input1_type = computed(() => getInputType(props.id, 'input1'))
    const input2_type = computed(() => getInputType(props.id, 'input2'))
    const schema_type = computed(():server__models__schema__Schema__Type|'default' => props.data.schema_out?.['output']?.type || 'default')
    const outputHasErr = computed(() => handleOutputError(props.id, 'output'))
    const errMsg = ref<string[]>([])
    const input1HasErr = ref({
        handleId: 'input1',
        value: false
    })
    const input2HasErr = ref({
        handleId: 'input2',
        value: false
    })


    watch(() => JSON.stringify(props.data.error), () => {
        errMsg.value = []
        handleExecError(props.data.error, errMsg)
        handleValidationError(props.id, props.data.error, errMsg, input1HasErr, input2HasErr)
    }, {immediate: true})

</script>

<style lang="scss" scoped>
    @use '../../../common/global.scss' as *;
    @use '../../../common/node.scss' as *;
    .ConcatNodeLayout {
        height: 100%;
        .data {
            padding-top: $node-padding-top;
            padding-bottom: $node-padding-bottom;
            .input-input1, .input-input2 {
                margin-bottom: $node-margin;
            }
        }
    }
    .all-handle-color {
        background: $str-color;
    }
</style>
