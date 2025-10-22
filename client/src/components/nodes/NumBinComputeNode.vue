<template>
    <div ref="info" class="NumBinComputeNodeLayout">
        <div class="outerTools">
            <NodeResizer :min-height="minH" :min-width="minW" :max-height="maxH" :max-width="maxW" :isVisible="false"/>
        </div>
        <div class="innerContent border-radius">
            <div class="title topchild-border-radius">NumBinComputeNode</div>
            <div class="data">
                <Handle :id="`Node${props.id}Handle1`" type="target" :position="Position.Left" style="top: 25%"/>
                <Handle :id="`Node${props.id}Handle2`" type="target" :position="Position.Left" style="top: 75%"/>
                <Handle :id="`Node${props.id}Handle3`" type="source" :position="Position.Right"/>
                <div class="op">
                    <select v-model="selected_op" @change="onSelect">
                        <option v-for="item in op">{{ item }}</option>
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
    import type {NumBinComputeNodeData} from '../../types/nodeTypes'


    let minW = 0
    let minH = 0
    let maxW = 0
    let maxH = 0
    const props = defineProps<NodeProps<NumBinComputeNodeData>>()
    const { viewport } = useVueFlow()
    const info = ref()
    const x = ref()
    const y = ref()
    const op = ['ADD', 'SUB', 'MUL', 'DIV', 'POW']
    const selected_op = ref(props.data.op)


    const onSelect = (e?: Event) => {
        props.data.op = selected_op.value
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
    .NumBinComputeNodeLayout {
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
                display: flex;
                flex-direction: column;
                align-items: center;
                position: relative;
                padding: 10px 0;
                .op {
                    select {
                        background: #ddd;
                        height: 1.5rem;
                        width: 2.5rem;
                    }
                }
            }
        }
    }
</style>

<style lang="scss">
    @import '@vue-flow/node-resizer/dist/style.css';
</style>