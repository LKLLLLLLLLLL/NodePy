<template>
    <div ref="info" class="ConstNodeLayout">
        <div class="outerTools">
            <NodeResizer :min-height="minH" :min-width="minW" :max-height="maxH" :max-width="maxW" :isVisible="false"/>
        </div>

        <div class="innerContent nodes-style" :class="{'nodes-selected': selected}">
            <div class="title nodes-topchild-border-radius">ConstNode</div>
            <div class="data">
                <Handle id="const" type="source" :position="Position.Right"/>
                <div class="value">
                     <input class="nodrag border-radius" v-model="value" @input="onInput"/>
                     <NodepyNumberInput v-model="value"/>
                </div>
                <div class="data_type">
                    <select v-model="data_type" @change="onSelect" class="border-radius nodrag">
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
    import NodepyNumberInput from '../tools/Nodepy-NumberInput/Nodepy-NumberInput.vue'


    let minW = 0
    let minH = 0
    let maxW = 0
    let maxH = 0
    const props = defineProps<NodeProps<ConstNodeData>>()
    const { viewport } = useVueFlow()
    const info = ref()
    const value = ref(props.data.param.value)
    const data_type = ref(props.data.param.data_type)
    const data_type_options = ['int', 'float']


    const onInput = (e?: Event) => {
        const v = value.value
        props.data.param.value = Number(v)
    }

    const onSelect = (e?: Event) => {
        props.data.param.data_type = data_type.value
        const v = value.value
        props.data.param.value = Number(v)
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
    @use '../../common/style/global.scss' as *;
    .ConstNodeLayout {
        height: 100%;
        width: 100%;
        .innerContent {
            height: 100%;
            width: 100%;
            background: white;
            .title {
                background: #ccc;
                text-align: left;
                padding-left: 8px;
                height: 30px;
            }
            .data {
                position: relative;
                padding: 5px 0;
                .value {
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: center;
                    input {
                        border: 1px solid #ccc;
                        text-align: center;
                        height: 24px;
                        width: 160px;
                        margin: 0 5px;
                    }
                }
                .data_type {
                    margin-top: 5px;
                    display: flex;
                    justify-content: center;
                    select {
                        border: 1px solid #ccc;
                        appearance: auto;
                        padding-left: 10px;
                        height: 24px;
                    }
                }
            }
        }
    }

</style>

<style lang="scss">
  @use '../../common/style/global.scss';
  @import '@vue-flow/node-resizer/dist/style.css';
</style>
