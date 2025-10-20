<template>
    <div ref="info" class="StringNodeLayout">
        <div class="outerTools">
            <NodeResizer :min-height="minH" :min-width="minW" :max-height="maxH" :max-width="maxW" :isVisible="false"/>
            <Handle :id="`Node${props.id}Handle`" type="source" :position="Position.Right"/>
        </div>
        <div class="innerContent">
            <div class="title">StringNode</div>
            <div class="data">
                <span>value: </span>
                <input type="text" v-model="value" class="nodrag" @input="onInput"/>
            </div>
        </div>
    </div>
</template>

<script lang="ts" setup>
    import {ref, onMounted, nextTick } from 'vue'
    import type { NodeProps } from '@vue-flow/core'
    import { useVueFlow, Position, Handle } from '@vue-flow/core'
    import { NodeResizer } from '@vue-flow/node-resizer'
    import type {StringNodeData} from '../../types/nodeTypes'


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
                minH = rect.height / zoom
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
        .innerContent {
            height: 100%;
            width: 100%;
            background: white;
            border-radius: 4px;
            box-shadow: 2px 2px 6px 0px black;
            overflow: hidden;
            .title {
                background: #ccc;
                text-align: left;
                padding-left: 8px;                
            }
            .data {
                display: flex;
                align-items: center;
                justify-content: center;
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
    }
</style>

<style lang="scss">
    @import '@vue-flow/node-resizer/dist/style.css';
</style>