<template>
    <div ref="info" class="StringNodeLayout">
        <div class="tools">
            <NodeResizer :min-height="minH" :min-width="minW" :max-height="maxH" :max-width="maxW" :isVisible="false"/>
            <Handle :id="`Node${props.id}Handle`" type="source" :position="Position.Right"/>
        </div>
        <div class="data">
            <span>value: </span>
            <input type="text" v-model="value" class="nodrag" @input="onInput"/>
        </div>
    </div>
</template>

<script lang="ts" setup>
    import {ref, onMounted, nextTick } from 'vue'
    import type { NodeProps } from '@vue-flow/core'
    import { useVueFlow, Position, Handle } from '@vue-flow/core'
    import { NodeResizer } from '@vue-flow/node-resizer'
    import type {StringNodeData} from './type'


    let minW = 0
    let minH = 0
    let maxW = 0
    let maxH = 0
    const props = defineProps<NodeProps<StringNodeData>>()
    const { viewport } = useVueFlow()
    const info = ref()
    const value = ref(props.data.value)


    const onInput = (e?: Event) => {
        props.data.value = value.value
    }


    onMounted(()=> {
        nextTick(() => {
            if (minW == 0 || minH == 0) {
                const rect = info.value.getBoundingClientRect()
                const zoom = viewport.value.zoom
                minW = rect.width / zoom + 10
                minH = rect.height / zoom + 10
                maxH = 2 * minH
                maxW = 2 * minW
                console.log('minW:',minW, 'minH:', minH, 'zoom:', zoom)
            }
        })
    })
        
</script>

<style lang="scss" scoped>
    .StringNodeLayout{
        height: 100%;
        width: 100%;
        display: flex;
        justify-content: center;
        align-items: center;
        .data {
            display: flex;
            align-items: center;
            span {
                margin: 4px;
            }
            input {
                margin: 4px;
                width: 7rem;
                height: 1.2rem;
                border: 1px solid #ccc
            }
        }
    }
</style>

<style lang="scss">
    @import '@vue-flow/node-resizer/dist/style.css';

    .vue-flow__node-StringNode {
        border-radius: 4px;
        background: #fff;
        border: 1px solid #000;
    }
</style>