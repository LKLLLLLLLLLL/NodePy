<template>
    <div class="TextAnnotationNodeLayout nodes-style" :class="[{'nodes-selected': selected}]" @contextmenu="onContextMenu">
        <NodeResizer :min-width="200" :min-height="90"/>
        <template v-if="isEditing">
            <AutosizeTextarea v-model="text"
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
    import {ref, nextTick, watch, defineComponent, h, onMounted} from 'vue'
    import '@vue-flow/node-resizer/dist/style.css'


    const props = defineProps<NodeProps<TextAnnotationNodeData>>()
    const text = ref(props.data.param.text)
    const inputEl = ref<any>(null)
    const isEditing = ref(false)

    // 内联的 AutosizeTextarea（使用 contenteditable），暴露 focus/blur/el/focusEnd
    const AutosizeTextarea = defineComponent({
        name: 'AutosizeTextarea',
        props: {
            modelValue: { type: String, default: '' },
            readonly: { type: Boolean, default: false }
        },
        emits: ['update:modelValue'],
        setup(props, { emit, attrs, expose }) {
            const el = ref<HTMLElement | null>(null)
            const local = ref(props.modelValue)

            watch(() => props.modelValue, (v) => {
                if (v !== local.value) local.value = v
            })

            const setDomFromLocal = () => {
                if (!el.value) return
                if ((el.value as HTMLElement).innerText !== local.value) {
                    el.value.innerText = local.value || ''
                }
            }

            const updateLocalFromDom = () => {
                if (!el.value) return
                const v = (el.value as HTMLElement).innerText || ''
                if (v !== local.value) {
                    local.value = v
                    emit('update:modelValue', v)
                }
            }

            const focusEnd = () => {
                if (!el.value) return
                el.value.focus()
                const range = document.createRange()
                range.selectNodeContents(el.value)
                range.collapse(false)
                const sel = window.getSelection()
                if (sel) {
                    sel.removeAllRanges()
                    sel.addRange(range)
                }
            }

            const onInput = (e: Event) => {
                updateLocalFromDom()
            }

            const onKeydown = (e: KeyboardEvent) => {
                if (e.key === 'Enter') {
                    // Prevent block-level insertion (div/br) to avoid extra newlines
                    e.preventDefault()
                    document.execCommand('insertText', false, '\n')
                    updateLocalFromDom()
                }
            }

            const onPaste = (e: ClipboardEvent) => {
                e.preventDefault()
                const text = e.clipboardData?.getData('text/plain') || ''
                document.execCommand('insertText', false, text)
                updateLocalFromDom()
            }

            onMounted(() => {
                setDomFromLocal()
            })

            expose({ el, focus: () => el.value?.focus(), blur: () => el.value?.blur(), focusEnd })

            return () => h('div', {
                ref: el,
                contenteditable: String(!props.readonly),
                class: attrs.class,
                style: Object.assign({ overflow: 'hidden', whiteSpace: 'pre-wrap' }, attrs.style || {}),
                onInput,
                onKeydown,
                onPaste
            })
        }
    })


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
        // focus and move caret to end using exposed helper
        if (inputEl.value?.focusEnd) {
            inputEl.value.focusEnd()
        } else {
            inputEl.value?.focus()
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
        padding: 4px;
        .inputValue {
            display: block;
            width: 100%;
            height: auto;
            min-height: 90px;
            padding: 2px;
            border:none;
            outline:none;
            color: white;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: pre-wrap;
            word-wrap: break-word;
            box-sizing: border-box;
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
            height: auto;
            min-height: 90px;
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
            box-sizing: border-box;
        }
        background: $annotation-node-body-color;
    }
</style>

<style lang="scss">
    .vue-flow__node-TextAnnotationNode {
        z-index: -1 !important;
        min-height: 90px;
        min-width: 200px;
    }
    .vue-flow__resize-control {
        background: transparent !important;
        border: 1px solid transparent !important;
    }
</style>
