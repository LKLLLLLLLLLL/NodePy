<script setup lang="ts">
import { computed, ref, onMounted } from 'vue'
import { Position, Handle, useVueFlow } from '@vue-flow/core'
import type { NodeProps } from '@vue-flow/core'
import { NodeToolbar } from '@vue-flow/node-toolbar'
import { NodeResizer } from '@vue-flow/node-resizer'

const props = defineProps<NodeProps>()
const {removeNodes} = useVueFlow()

const minW = ref(150)
const minH = ref(50)
const info = ref()
const x = computed(() => `${Math.round(props.position.x)}px`)
const y = computed(() => `${Math.round(props.position.y)}px`)

onMounted(()=> {
  if (info.value) {
    const rect = info.value.getBoundingClientRect()
    minW.value = rect.width + 20
    minH.value = rect.height + 20
  }
  console.log('minW', minW.value)
  console.log('minH', minH.value)
})
</script>

<template>
<div ref="info" class="customNodeLayout">
  <div>
    <NodeToolbar :node-id="props.id">
      <button @click="removeNodes(props.id)">🗑</button>
    </NodeToolbar>
    <NodeResizer :min-width="minW" :min-height="minH" />
    <!-- each of these handles needs a unique id since we're using two `source` type handles -->
    <Handle id="source-a" type="source" :position="Position.Right" style="top: 10px;"/>
    <Handle id="source-b" type="source" :position="Position.Right" style="bottom: 10px; top: auto;"/>

    <!-- each of these handles needs a unique id since we're using two `target` type handles -->
    <Handle id="target-a" type="target" :position="Position.Left" style="top: 10px;"/>
    <Handle id="target-b" type="target" :position="Position.Left" style="bottom: 10px; top: auto;"/>
  </div>


  <div class="data">
    <div>{{ data.label }}</div>
    <div>
    {{ x }} {{ y }}
    </div>
  </div>


</div>
</template>

<style lang="scss" scoped>
  .customNodeLayout {
    height: 100%;
    width: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
  }
</style>

<style lang="scss">
// make sure to include the necessary styles!
@import '@vue-flow/node-resizer/dist/style.css';

.vue-flow__node-custom {
  border: 1px solid #ff0000;
  border-radius: 4px;
  background: #fff;
}
</style>