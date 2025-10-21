<template>
    <div ref="info" class="TableNodeLayout">
        <div class="outerTools">
            <NodeResizer :min-height="minH" :min-width="minW" :max-height="maxH" :max-width="maxW" :isVisible="false"/>
            <Handle :id="`Node${props.id}Handle`" type="source" :position="Position.Right"/>
        </div>
        <div class="innerContent">
            <div class="title">TableNode</div>
            <div class="data">
                渲染表格的地方
            </div>
        </div>
    </div>
</template>

<script lang="ts" setup>
    import {ref, onMounted, nextTick } from 'vue'
    import type { NodeProps } from '@vue-flow/core'
    import { useVueFlow, Position, Handle } from '@vue-flow/core'
    import { NodeResizer } from '@vue-flow/node-resizer'
    import type {TableNodeData} from '../../types/nodeTypes'


    let minW = 0
    let minH = 0
    let maxW = 0
    let maxH = 0
    const props = defineProps<NodeProps<TableNodeData>>()
    const { viewport } = useVueFlow()
    const info = ref()


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
    .TableNodeLayout{
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
        }
    }
</style>

<style lang="scss">
    @import '@vue-flow/node-resizer/dist/style.css';
</style>