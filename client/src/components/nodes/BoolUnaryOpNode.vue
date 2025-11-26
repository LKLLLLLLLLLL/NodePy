<template>
    <div class="BoolUnaryOpNodeLayout nodes-style" :class="[{'nodes-selected': selected}, {'nodes-dbclicked': data.dbclicked}]">
        <NodeTitle node-category="compute">布尔非运算节点</NodeTitle>
        <Timer :node-id="id" :default-time="data.runningtime"/>
        <div class="data">
            <div class="input-x port">
                <div class="input-port-description">
                    x输入端口
                </div>
                <Handle id="x" type="target" :position="Position.Left" :class="[`${x_type}-handle-color`, {'node-errhandle': xHasErr.value}]"/>
            </div>
            <div class="output-result port">
                <div class="output-port-description">
                    结果输出端口
                </div>
                <Handle id="result" type="source" :position="Position.Right" :class="[`${schema_type}-handle-color`, {'node-errhandle': resultHasErr}]"/>
            </div>
        </div>
        <ErrorMsg :err-msg="errMsg"/>
    </div>
</template>

<script lang="ts" setup>
    import {ref, computed, watch} from 'vue'
    import type { NodeProps } from '@vue-flow/core'
    import { Position, Handle } from '@vue-flow/core'
    import { getInputType } from './getInputType'
    import type { Type } from '@/utils/api'
    import { handleValidationError, handleExecError, handleOutputError } from './handleError'
    import ErrorMsg from './tools/ErrorMsg.vue'
    import NodeTitle from './tools/NodeTitle.vue'
    import Timer from './tools/Timer.vue'
    import type { BoolUnaryOpNodeData } from '@/types/nodeTypes'


    const props = defineProps<NodeProps<BoolUnaryOpNodeData>>()
    const x_type = computed(() => getInputType(props.id, 'x'))
    const schema_type = computed(():Type|'default' => props.data.schema_out?.['result']?.type || 'default')
    const resultHasErr = computed(() => handleOutputError(props.id, 'result'))
    const errMsg = ref<string[]>([])
    const xHasErr = ref({
        handleId: 'x',
        value: false
    })


    watch(() => JSON.stringify(props.data.error), () => {
        errMsg.value = []
        handleExecError(props.data.error, errMsg)
        handleValidationError(props.id, props.data.error, errMsg, xHasErr)
    }, {immediate: true})

</script>

<style lang="scss" scoped>
    @use '../../common/global.scss' as *;
    @use '../../common/node.scss' as *;
    .BoolUnaryOpNodeLayout {
        height: 100%;
        .data {
            padding-top: $node-padding-top;
            padding-bottom: $node-padding-bottom;
            .input-x {
                margin-bottom: $node-margin;
            }
        }
    }
    .all-handle-color {
        background: $bool-color;
    }
</style>