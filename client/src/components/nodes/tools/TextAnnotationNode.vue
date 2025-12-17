<template>
    <div class="TextAnnotationNodeLayout nodes-style" :class="[{'nodes-selected': selected}]">
        <NodeResizer :min-width="200" :min-height="30"/>
        <div class="text">
            <textarea v-model="text" class="textarea" @blur=""></textarea>
        </div>
    </div>
</template>

<script lang="ts" setup>
    import type { TextAnnotationNodeData} from '../../../types/nodeTypes'
    import type { NodeProps } from '@vue-flow/core'
    import { NodeResizer } from '@vue-flow/node-resizer'
    import {ref} from 'vue'
    import '@vue-flow/node-resizer/dist/style.css'


    const props = defineProps<NodeProps<TextAnnotationNodeData>>()
    const text = ref(props.data.param.text)
    
</script>

<style lang="scss" scoped>
    @use '../../../common/global.scss' as *;
    @use '../../../common/node.scss' as *;
    .TextAnnotationNodeLayout {
        width: 100%;
        height: 100%;
        .text {
            width: 100%;
            height: 100%;
            .textarea {
                width: 100%;
                height: 100%;
            }
        }
        background: $annotation-node-body-color;
    }
</style>

<style lang="scss">
    .vue-flow__node-TextAnnotationNode {
        z-index: -1 !important;
        width: 200px;
        height: 500px;
        min-height: 30px;
        min-width: 200px;
    }
    .vue-flow__resize-control {
        background: transparent !important;
        border: 1px solid transparent !important;
    }
</style>