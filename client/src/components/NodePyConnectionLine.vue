<template>
    <g>
        <path
            class="vue-flow__connection" 
            fill="none" 
            :stroke="strokeColor"
            :stroke-width="3"
            :d="pathData"
         />
    </g>
</template>

<script lang="ts" setup>
    import { computed } from 'vue'
    import { useConnection, getBezierPath, type Position, useVueFlow } from '@vue-flow/core'
    import { dataTypeColor } from '@/types/nodeTypes'
    import type { BaseNode } from '@/types/nodeTypes'

    const { startHandle } = useConnection()
    const {findNode} = useVueFlow()
    const pathData = computed(() =>
        getBezierPath({
            sourceX: props.sourceX,
            sourceY: props.sourceY,
            sourcePosition: props.sourcePosition,
            targetX: props.targetX,
            targetY: props.targetY,
            targetPosition: props.targetPosition,
            curvature: 0.1
        })[0]
    )
    const startNode = computed(():BaseNode|undefined|null => {
        if(startHandle.value?.nodeId) {
            return findNode(startHandle.value.nodeId) 
        }
        return null
    })
    const strokeColor = computed(() => {
        if(startNode.value) {
            const dataType = startNode.value.data.schema_out?.[startHandle.value?.id as string]?.type || 'default'
            return dataTypeColor[dataType]
        }
        return dataTypeColor['default']
    })
    const props = defineProps({
      sourceX: {
        type: Number,
        required: true,
      },
      sourceY: {
        type: Number,
        required: true,
      },
      targetX: {
        type: Number,
        required: true,
      },
      targetY: {
        type: Number,
        required: true,
      },
      sourcePosition: {
        type: String as () => Position,
        required: true,
      },
      targetPosition: {
        type: String as () => Position,
        required: true,
      },
    })
</script>

<style lang="scss" scoped>

</style>