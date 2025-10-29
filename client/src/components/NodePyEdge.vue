<script setup lang="ts">
import type { EdgeProps } from '@vue-flow/core'
import { BezierEdge } from '@vue-flow/core'
import { dataTypeColor } from '@/types/nodeTypes'


const props = defineProps<EdgeProps>()
console.log('NodePyEdge props:', props)

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
      :style="{ stroke: '#1c6bbf', strokeWidth: 3 }"
  />
</template>
