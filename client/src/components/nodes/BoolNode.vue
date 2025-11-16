<template>
    <div class="BoolNodeLayout nodes-style" :class="{'nodes-selected': selected}">
        <div class="node-title-input nodes-topchild-border-radius">{{`布尔节点${props.id.split('_')[1]}`}}</div>
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
                    布尔输出端口
                </div>
                <Handle id="const" type="source" :position="Position.Right" :class="[`${schema_type}-handle-color`, {'node-errhandle': constHasErr}]"/>
            </div>
        </div>
        <div class="node-err nodrag" @click.stop>
            <div v-for="err in errMsg">
                {{ err }}
            </div>
        </div>
    </div>
</template>

<script lang="ts" setup>
    import { Position, Handle } from '@vue-flow/core'
    import {ref, computed, watch } from 'vue'
    import type { NodeProps } from '@vue-flow/core'
    import type {BoolNodeData} from '../../types/nodeTypes'
    import type { Type } from '@/utils/api'
    import NodepyBoolValue from './tools/Nodepy-boolValue.vue'
    import { handleExecError, handleOutputError } from './handleError'


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
    @use '../../common/global.scss' as *;
    @use '../../common/node.scss' as *;
    .BoolNodeLayout {
        height: 100%;
        .data {
            padding-top: $node-padding;
            padding-bottom: 5px;
            .value {
                display: flex;
                align-items: center;
                padding-left: $node-padding;
            }
        }
    }
</style>