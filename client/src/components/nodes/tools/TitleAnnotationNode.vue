<template>
    <div class="TitleAnnotationNodeLayout nodes-style" :class="[{'nodes-selected': selected}]">
        <NodeResizer :min-width="200" :min-height="30"/>
        <NodeTitle node-category='annotation' class="title draggable">
            <input v-model="title"
                @blur="commit" 
                @keydown.enter="commit" 
                class="inputValue" 
                ref="inputEl" 
                :readonly="!isEditing" 
                @dblclick="enableEdit"
                :class="{nodrag: isEditing}"
             />
        </NodeTitle>
        <div class="nodrag"></div>
    </div>
</template>

<script lang="ts" setup>
    import NodeTitle from '../tools/NodeTitle.vue'
    import type { TitleAnnotationNodeData } from '../../../types/nodeTypes'
    import type { NodeProps } from '@vue-flow/core'
    import { NodeResizer } from '@vue-flow/node-resizer'
    import {ref} from 'vue'
    import '@vue-flow/node-resizer/dist/style.css'
    
    const props = defineProps<NodeProps<TitleAnnotationNodeData>>()
    const title = ref(props.data.param.title)
    const inputEl = ref<HTMLInputElement>()
    const isEditing = ref(false)


    const commit = () => {
        if(isEditing.value) {
            props.data.param.title = title.value
            inputEl.value?.blur()
        }
        isEditing.value = false
    }
    const enableEdit = () => {
        isEditing.value = true
        inputEl.value?.focus()
    }

</script>

<style lang="scss" scoped>
    @use '../../../common/global.scss' as *;
    @use '../../../common/node.scss' as *;
    .TitleAnnotationNodeLayout {
        width: 100%;
        height: 100%;
        .title {
            .inputValue {
                width: 100%;
                border:none;
                outline:none;
                color: white;
            }
        }
        .nodrag {
            width: 100%;
            height: 100%;
        }
        background: $annotation-node-body-color;
    }
</style>

<style lang="scss">
    .vue-flow__node-TitleAnnotationNode {
        z-index: -1 !important;
        width: 500px;
        height: 500px;
        min-height: 30px;
        min-width: 200px;
    }
    .vue-flow__resize-control {
        background: transparent !important;
        border: 1px solid transparent !important;
    }
</style>