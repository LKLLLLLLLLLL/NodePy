<template>
<div ref="info" class="TableNodeLayout">
        <div class="tools">
            <NodeResizer :min-height="minH" :min-width="minW" :max-height="maxH" :max-width="maxW" :isVisible="false"/>
            <Handle :id="`Node${props.id}Handle`" type="source" :position="Position.Right"/>
        </div>
        <div class="data">
            以后用来渲染表格的地方
        </div>
    </div>
</template>

<script lang="ts" setup>
    import {ref, onMounted, nextTick } from 'vue'
    import type { NodeProps } from '@vue-flow/core'
    import { useVueFlow, Position, Handle } from '@vue-flow/core'
    import { NodeResizer } from '@vue-flow/node-resizer'
    import type {TableNodeData} from './type'


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
                minH = rect.height / zoom + 10
                maxH = 2 * minH
                maxW = 2 * minW
                console.log('minW:',minW, 'minH:', minH, 'zoom:', zoom)
            }
        })
    })

</script>

<style lang="scss" scoped>

</style>

<style lang="scss">
    @import '@vue-flow/node-resizer/dist/style.css';

    .vue-flow__node-TableNode {
        border-radius: 4px;
        background: #fff;
        border: 1px solid #000;
    }
</style>