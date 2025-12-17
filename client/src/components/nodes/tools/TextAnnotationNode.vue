<template>
    <div class="TextAnnotationNodeLayout nodes-style" :class="[{'nodes-selected': selected}]" @contextmenu="onContextMenu">
        <NodeResizer :min-width="200" :min-height="30"/>
        <template v-if="isEditing">
            <textarea v-model="text" 
                @blur="commit"
                class="inputValue"
                ref="inputEl"
                :readonly="!isEditing"
                :class="{nodrag: isEditing}"
            />
        </template>
        <template v-else>
            <div class="displayText" @dblclick="enableEdit" tabindex="0">{{ text }}</div>
        </template>
    </div>
</template>

<script lang="ts" setup>
    import type { TextAnnotationNodeData } from '../../../types/nodeTypes'
    import type { NodeProps } from '@vue-flow/core'
    import { NodeResizer } from '@vue-flow/node-resizer'
    import {ref, nextTick} from 'vue'
    import '@vue-flow/node-resizer/dist/style.css'


    const props = defineProps<NodeProps<TextAnnotationNodeData>>()
    const text = ref(props.data.param.text)
    const inputEl = ref<HTMLInputElement | null>(null)
    const isEditing = ref(false)


    // 定义右键事件处理函数
    const onContextMenu = (event: MouseEvent) => {
        // 阻止默认右键菜单
        event.preventDefault()
        // 创建自定义事件，传递给父级处理
        const customEvent = new CustomEvent('node-contextmenu', {
            detail: {
                event,
                node: props
            }
        })
        window.dispatchEvent(customEvent)
    }
    const commit = () => {
        if(isEditing.value) {
            props.data.param.text = text.value
            inputEl.value?.blur()
        }
        isEditing.value = false
    }
    const enableEdit = async () => {
        isEditing.value = true
        await nextTick()
        inputEl.value?.focus()
        // move caret to end
        const el = inputEl.value
        if (el) {
            const len = el.value.length
            el.setSelectionRange(len, len)
        }
    }
    
</script>

<style lang="scss" scoped>
    @use '../../../common/global.scss' as *;
    @use '../../../common/node.scss' as *;
    .TextAnnotationNodeLayout {
        width: 100%;
        height: auto;
        min-height: 90px;
        .inputValue {
            width: 100%;
            height: 100%;
            padding: 2px;
            border:none;
            outline:none;
            color: white;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: pre-wrap;
            word-wrap: break-word;
            /* 禁止在非编辑（readonly）状态下选中内容 */
            &[readonly] {
                -webkit-user-select: none;
                -moz-user-select: none;
                -ms-user-select: none;
                user-select: none;
                caret-color: transparent;
            }
        }
        .displayText {
            width: 100%;
            height: 100%;
            color: white;
            -webkit-user-select: none;
            -moz-user-select: none;
            -ms-user-select: none;
            user-select: none;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: pre-wrap;
            word-wrap: break-word;
            padding: 2px;
        }
        background: $annotation-node-body-color;
    }
</style>

<style lang="scss">
    .vue-flow__node-TextAnnotationNode {
        z-index: -1 !important;
        width: 200px;
        height: 500px;
        min-height: 300px;
        min-width: 90px;
    }
    .vue-flow__resize-control {
        background: transparent !important;
        border: 1px solid transparent !important;
    }
</style>