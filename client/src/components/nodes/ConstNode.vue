<template>
    <div ref="info" class="ConstNodeLayout">
        <div class="outerTools">
            <NodeResizer :min-height="minH" :min-width="minW" :max-height="maxH" :max-width="maxW" :isVisible="false"/>
            <Handle :id="`Node${props.id}Handle`" type="source" :position="Position.Right"/>
        </div>

        <div class="innerContent">
            <div class="title">ConstNode</div>
            <div class="data">
                <div class="value">
                    <span>value: </span>
                    <input type="text" v-model="value" class="nodrag" @input="onInput"/>
                </div>
                <div class="data_type">
                    <span>data_type:</span>
                    <select v-model="data_type" @change="onSelect">
                        <option v-for="item in data_type_options">{{ item }}</option>
                    </select>
                </div>
            </div>            
        </div>
    </div>
</template>

<script lang="ts" setup>
    import {ref, onMounted, nextTick } from 'vue'
    import type { NodeProps } from '@vue-flow/core'
    import { useVueFlow, Position, Handle } from '@vue-flow/core'
    import { NodeResizer } from '@vue-flow/node-resizer'
    import type {ConstNodeData} from '../../types/nodeTypes'


    let minW = 0
    let minH = 0
    let maxW = 0
    let maxH = 0
    const props = defineProps<NodeProps<ConstNodeData>>()
    const { viewport } = useVueFlow()
    const info = ref()
    const value = ref(props.data.value)
    const data_type = ref(props.data.data_type)
    const data_type_options = ['int', 'float', 'str', 'bool']


    const onInput = (e?: Event) => {
        props.data.value = value.value
    }

    const onSelect = (e?: Event) => {
        props.data.data_type = data_type.value
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
    .ConstNodeLayout {
        height: 100%;
        width: 100%;
        .innerContent {
            height: 100%;
            width: 100%;
            background: white;
            border-radius: 8px;
            box-shadow: 2px 2px 6px 0px black;
            overflow: hidden;
            .title {
                background: #ccc;
                text-align: left;
                padding-left: 8px;
            }
            .data {
                display: flex;
                flex-direction: column;
                align-items: center;
                .data_type {
                    display: flex;
                    align-items: center;
                    span {
                        margin: 4px;
                    }
                    select {
                        background: #ddd;
                        height: 1.5rem;
                        width: 2.5rem;
                        padding: 0.1rem;
                        margin: 4px;
                    }
                }
                .value {
                    display: flex;
                    align-items: center;
                    span {
                        margin: 4px;
                    }
                    input {
                        width: 7rem;
                        height: 1.2rem;
                        border: 1px solid #ccc;
                        margin: 4px;
                    }
                }
            }
        }
    }
    
</style>

<style lang="scss">
    @import '@vue-flow/node-resizer/dist/style.css';
</style>
