<template>
    <div ref="info" class="StringNodeLayout">
        <div class="outerTools">
            <NodeResizer :min-height="minH" :min-width="minW" :max-height="maxH" :max-width="maxW" :isVisible="false"/>
        </div>
        <div class="innerContent border-radius">
            <div class="title topchild-border-radius">StringNode</div>
            <div class="data">
                <Handle id="string" type="source" :position="Position.Right"/>
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
    const value = ref(props.data.param.value)


    const onInput = (e?: Event) => {
        props.data.param.value = value.value
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
    @use '../../common/style/global.scss';
    .StringNodeLayout{
        height: 100%;
        width: 100%;
        .innerContent {
            height: 100%;
            width: 100%;
            background: white;
            box-shadow: 2px 2px 6px 0px black;
            .title {
                background: #ccc;
                text-align: left;
                padding-left: 8px;                
            }
            .data {
                padding: 10px 0;
                position: relative;
                display: flex;
                justify-content: center;
                input {
                    width: 80%;
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