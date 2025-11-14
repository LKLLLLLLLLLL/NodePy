<script setup lang="ts">
import { useVueFlow, type EdgeProps, BezierEdge } from '@vue-flow/core'
import { dataTypeColor } from '@/types/nodeTypes'
import {computed} from 'vue'
import type { BaseNode } from '@/types/nodeTypes'


const props = defineProps<EdgeProps>()
const {findNode} = useVueFlow('main')
const sourceNode = computed(():BaseNode|undefined => {
    return findNode(props.source)
})
const strokeColor = computed(() => {
    if(sourceNode.value) {
        const dataType = sourceNode.value.data.schema_out?.[props.sourceHandleId as string]?.type || 'default'
        return dataTypeColor[dataType]
    }
    return 'default'
})
const isErrorEdge = computed(() => props.data === 'error')

</script>


<template>
  <BezierEdge
      :source-x="sourceX"
      :source-y="sourceY"
      :target-x="targetX"
      :target-y="targetY"
      :source-position="sourcePosition"
      :target-position="targetPosition"
      :curvature="0.1"
      :style="{ stroke: strokeColor, strokeWidth: 3, filter: isErrorEdge ? 'drop-shadow(0 0 2px red)': 'none'}"
  />
</template>

