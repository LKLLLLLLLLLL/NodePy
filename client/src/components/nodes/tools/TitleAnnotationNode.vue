<template>
    <div class="TitleAnnotationNodeLayout nodes-style" :class="[{'nodes-selected': selected}]" @contextmenu="onContextMenu">
        <NodeResizer :min-width="200" :min-height="30"/>
        <NodeTitle node-category='annotation' class="title">
            <template v-if="isEditing">
                <input v-model="title"
                    @blur="commit"
                    @keydown.enter="commit"
                    class="inputValue"
                    ref="inputEl"
                    :readonly="!isEditing"
                    :class="{nodrag: isEditing}"
                />
            </template>
            <template v-else>
                <div class="displayTitle" @dblclick="enableEdit" tabindex="0">{{ title }}</div>
            </template>
        </NodeTitle>
        <div class="nodrag"></div>
    </div>
</template>

<script lang="ts" setup>
    import NodeTitle from '../tools/NodeTitle.vue'
    import type { TitleAnnotationNodeData } from '../../../types/nodeTypes'
    import type { NodeProps } from '@vue-flow/core'
    import { NodeResizer } from '@vue-flow/node-resizer'
    import {ref, nextTick} from 'vue'
    import '@vue-flow/node-resizer/dist/style.css'


    const props = defineProps<NodeProps<TitleAnnotationNodeData>>()
    const title = ref(props.data.param.title)
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
            props.data.param.title = title.value
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
    .TitleAnnotationNodeLayout {
        width: 100%;
        height: 100%;
        .title {
            .inputValue {
                width: 100%;
                height: 100%;
                border:none;
                outline:none;
                color: white;
                padding: 2px 0;
                /* 禁止在非编辑（readonly）状态下选中内容 */
                &[readonly] {
                    -webkit-user-select: none;
                    -moz-user-select: none;
                    -ms-user-select: none;
                    user-select: none;
                    caret-color: transparent;
                }
            }
        }
        .displayTitle {
            width: 100%;
            height: 100%;
            color: white;
            -webkit-user-select: none;
            -moz-user-select: none;
            -ms-user-select: none;
            user-select: none;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
            padding: 2px 0;
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
