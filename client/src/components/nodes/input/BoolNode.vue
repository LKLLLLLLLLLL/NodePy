<template>
    <div class="BoolNodeLayout nodes-style" :class="[{'nodes-selected': selected}, {'nodes-dbclicked': data.dbclicked}]">
        <NodeTitle node-category="input">布尔节点</NodeTitle>
        <Timer :node-id="id" :default-time="data.runningtime"/>
        <div class="data">
            <div class="value">
                <NodepyBoolValue
                    v-model="value"
                    @update-value="onUpdateValue"
                    width="20px"
                    height="20px"
                >
                布尔
                </NodepyBoolValue>
            </div>
            <div class="output-const port">
                <div class="output-port-description">
                    布尔输出
                </div>
                <Handle id="const" type="source" :position="Position.Right" :class="[`${schema_type}-handle-color`, {'node-errhandle': constHasErr}]"/>
            </div>
        </div>
        <ErrorMsg :err-msg="errMsg"/>
    </div>
</template>

<script lang="ts" setup>
    import { Position, Handle } from '@vue-flow/core'
    import {ref, computed, watch } from 'vue'
    import type { NodeProps } from '@vue-flow/core'
    import type {BoolNodeData} from '../../../types/nodeTypes'
    import type { Type } from '@/utils/api'
    import NodepyBoolValue from '../tools/Nodepy-boolValue.vue'
    import { handleExecError, handleOutputError } from '../handleError'
    import ErrorMsg from '../tools/ErrorMsg.vue'
    import NodeTitle from '../tools/NodeTitle.vue'
    import Timer from '../tools/Timer.vue'


    const props = defineProps<NodeProps<BoolNodeData>>()
    const value = ref(props.data.param.value)
    const schema_type = computed(():Type|'default' => props.data.schema_out?.['const']?.type || 'default')
    const constHasErr = computed(() => handleOutputError(props.id, 'const'))
    const errMsg = ref<string[]>([])


    const onUpdateValue = () => {
        props.data.param.value = value.value
    }


    watch(() => JSON.stringify(props.data.error), () => {
        errMsg.value = []   //  reset errMsg
        handleExecError(props.data.error, errMsg)
    }, {immediate: true})

</script>

<style lang="scss" scoped>
    @use '../../../common/global.scss' as *;
    @use '../../../common/node.scss' as *;
    .BoolNodeLayout {
        height: 100%;
        .data {
            padding-top: $node-padding-top;
            padding-bottom: $node-padding-bottom;
            .value {
                display: flex;
                align-items: center;
                padding-left: $node-padding-hor;
            }
        }
    }
</style>