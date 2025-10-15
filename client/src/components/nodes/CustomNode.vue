<script setup lang="ts">
import { computed } from 'vue'
import { Position, Handle, useVueFlow } from '@vue-flow/core'
import type { NodeProps } from '@vue-flow/core'
import { NodeToolbar } from '@vue-flow/node-toolbar'
import { NodeResizer } from '@vue-flow/node-resizer'

const props = defineProps<NodeProps>()
const {removeNodes} = useVueFlow()

const x = computed(() => `${Math.round(props.position.x)}px`)
const y = computed(() => `${Math.round(props.position.y)}px`)
</script>

<template>
  <!-- 节点内容 -->
  <div class="custom-node" style="position:relative">
    <NodeToolbar :node-id="props.id">
      <button @click="removeNodes(props.id)">🗑</button>
    </NodeToolbar>

    <!-- 左边一个 target 把手 -->
    <Handle
    id="target-1"
    type="target"
    :position="Position.Left"
    style="top: 5px"
    />
    <Handle
    id="target-2"
    type="target"
    :position="Position.Left"
    style="bottom: -5px; top: auto;"
    />
    <Handle
    id="target-3"
    type="target"
    :position="Position.Left"
    />


    <div>{{ data.label }}</div>

    <div>
      {{ x }} {{ y }}
    </div>

    <!-- 右边一个 source 把手 -->
    <Handle id="source-1" type="source" :position="Position.Right" style="top: 5px; opacity: 0;" :connectable="false"/>
    <Handle id="source-2" type="source" :position="Position.Right" style="bottom: 5px"/>
  </div>
</template>

<style lang="scss" scoped>
.custom-node {
  padding: 8px 16px;
  border: 1px solid #999;
  border-radius: 4px;
  background: #fff;
  display: inline-flex;
  align-items: center;
  gap: 6px;
}
</style>

<style lang="scss">
  // make sure to include the necessary styles!
  @import '@vue-flow/node-resizer/dist/style.css';
</style>