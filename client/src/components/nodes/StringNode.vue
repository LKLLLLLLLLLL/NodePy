<template>
    <div class="StringNodeLayout nodes-style" :class="{'nodes-selected': selected}">
        <div class="node-title-input nodes-topchild-border-radius">字符串节点</div>
        <div class="data" :class="{'node-has-paramerr': hasParamerr}">
            <div class="value">
                <div class="value-description">
                    字符串
                </div>
                <NodepyStringInput 
                    v-model="value" 
                    :disabled="false" 
                    @update-value="onUpdateValue" 
                    class="nodrag"
                />
            </div>
            <div class="output-string port">
                <div class="output-port-description">
                    字符串输出端口
                </div>
                <Handle id="string" type="source" :position="Position.Right" class="str-handle-color"/>
            </div>
        </div>
        <div class="node-err nodrag">
            <div v-for="err in errMsg">
                {{ err }}
            </div>
        </div>
    </div>
</template>

<script lang="ts" setup>
    import {ref, watch} from 'vue'
    import type { NodeProps } from '@vue-flow/core'
    import { Position, Handle } from '@vue-flow/core'
    import type {StringNodeData} from '../../types/nodeTypes'
    import NodepyStringInput from './tools/Nodepy-StringInput.vue'
    import { handleExecError, handleParamError } from './handleError'


    const props = defineProps<NodeProps<StringNodeData>>()
    const value = ref(props.data.param.value)
    const errMsg = ref<string[]>([])
    const hasParamerr = ref(false)


    const onUpdateValue = (e?: Event) => {
        props.data.param.value = value.value
    }


    watch(() => JSON.stringify(props.data.error), () => {
        errMsg.value = []
        handleExecError(props.data.error, errMsg)
        handleParamError(hasParamerr, props.data.error, errMsg)
    }, {immediate: true})

</script>

<style lang="scss" scoped>
    @use '../../common/global.scss' as *;
    @use '../../common/node.scss' as *;
    .StringNodeLayout{
        height: 100%;
        .data {
            padding-top: $node-padding;
            padding-bottom: 5px;
            .value {
                padding: 0 $node-padding;
            }
            .output-string {
                margin-top: $node-margin;
            }
        }
    }
</style>