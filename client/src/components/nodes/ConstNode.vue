<template>
    <div ref="info" class="ConstNodeLayout">
        <div class="outerTools">
            <NodeResizer :min-height="minH" :min-width="minW" :max-height="maxH" :max-width="maxW" :isVisible="false"/>
        </div>

        <div class="innerContent border-radius">
            <div class="title topchild-border-radius">ConstNode</div>
            <div class="data">
                <Handle id="const" type="source" :position="Position.Right"/>
                <div class="value">
                    <el-input class="input nodrag" v-model="value" @input="onInput"/>
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
    const value = ref(props.data.param.value)
    const data_type = ref(props.data.param.data_type)
    const data_type_options = ['int', 'float', 'str', 'bool']


    const onInput = (e?: Event) => {
        props.data.param.value = value.value
    }

    const onSelect = (e?: Event) => {
        props.data.param.data_type = data_type.value
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
    .ConstNodeLayout {
        height: 100%;
        width: 100%;
        .innerContent {
            height: 100%;
            width: 100%;
            background: white;
            box-shadow: 2px 2px 6px 0px #aaa;
            .title {
                background: #ccc;
                text-align: left;
                padding-left: 8px;
            }
            .data {
                position: relative;
                padding: 5px 0;
                .data_type {
                    margin-top: 5px;
                    display: flex;
                    justify-content: center;
                    span {
                        margin-right: 10px;
                    }
                    select {
                        background: #ddd;
                        height: 1.5rem;
                        width: 2.5rem;
                    }
                }
                .value {
                    display: flex;
                    justify-content: center;
                    .input {
                        width: 90%;
                        height: 20px !important;
                    }
                }
            }
        }
    }
    
</style>

<style lang="scss">
    @import '@vue-flow/node-resizer/dist/style.css';
</style>
