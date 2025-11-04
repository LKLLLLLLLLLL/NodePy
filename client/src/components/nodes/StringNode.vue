<template>
    <div class="StringNodeLayout nodes-style" :class="{'nodes-selected': selected}">
        <div class="node-title nodes-topchild-border-radius">字符串节点</div>
        <div class="data">
            <Handle id="string" type="source" :position="Position.Right" class="str-handle-color"/>
            <div class="value">
                <NodepyStringInput 
                    v-model="value" 
                    :disabled="false" 
                    @update-value="onUpdateValue" 
                    class="nodrag"
                />
            </div>
        </div>
    </div>
</template>

<script lang="ts" setup>
    import {ref} from 'vue'
    import type { NodeProps } from '@vue-flow/core'
    import { Position, Handle } from '@vue-flow/core'
    import type {StringNodeData} from '../../types/nodeTypes'
    import NodepyStringInput from './tools/Nodepy-StringInput.vue'


    const props = defineProps<NodeProps<StringNodeData>>()
    const value = ref(props.data.param.value)


    const onUpdateValue = (e?: Event) => {
        props.data.param.value = value.value
    }

</script>

<style lang="scss" scoped>
    @use '../../common/global.scss' as *;
    @use '../../common/node.scss' as *;
    .StringNodeLayout{
        height: 100%;
        width: $node-width;
        background: white;
        .data {
            padding: 5px 0;
            position: relative;
            .value {
                padding: 0 10px;
            }
        }
    }
</style>