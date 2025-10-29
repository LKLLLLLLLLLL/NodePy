<template>
    <g>
        <path
            class="vue-flow__connection" 
            fill="none" 
            :stroke="`#1c6bbf`"
            :stroke-width="3"
            :d="pathData"
         />
    </g>
</template>

<script lang="ts" setup>
    import { computed } from 'vue'
    import { useConnection, getBezierPath, type Position, useVueFlow } from '@vue-flow/core'
    import { dataTypeColor } from '@/types/nodeTypes'

    const { startHandle } = useConnection()
    const {findNode} = useVueFlow('main')
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
    console.log(startHandle)
    const strokeColor = computed(() => {
        if(startHandle.value) {
            
        }
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