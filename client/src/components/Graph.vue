<script lang='ts' setup>
import { ref, onMounted } from 'vue'  
import { VueFlow, useVueFlow, Panel, ConnectionMode } from '@vue-flow/core'
import type { Node, Edge } from '@vue-flow/core'  
import { Background } from '@vue-flow/background'
import { MiniMap, MiniMapNode } from '@vue-flow/minimap'
import { Controls } from '@vue-flow/controls'
import ConstNode from './nodes/ConstNode.vue'
import StringNode from './nodes/StringNode.vue'
import TableNode from './nodes/TableNode.vue'
import NumBinComputeNode from './nodes/NumBinComputeNode.vue'
import {addNode} from '../stores/graphStore'


const { onConnect, onInit, onNodesChange, addEdges, viewport } = useVueFlow('main')
console.log(viewport)

const nodes = ref<Node[]>([])

const edges = ref<Edge[]>([])

const selected = ref()

let count = nodes.value.length


// any event that is emitted from the `<VueFlow />` component can be listened to using the `onEventName` method
onInit((instance) => {
  // `instance` is the same type as the return of `useVueFlow` (VueFlowStore)
  instance.fitView()
})

// onAddNodes
onNodesChange(changes => {
  changes = changes.filter(c => c.type === 'add')
  if(changes.length > 0) {
    count += changes.length
    console.log(`增加${changes.length}个节点, 现在还有${count}个节点`)
    console.log(nodes.value)
  }
})

//onRemoveNodes
onNodesChange(changes => {
  changes = changes.filter(c => c.type === 'remove')
  if(changes.length > 0){
    count -= changes.length
    console.log(`减少${changes.length}个节点， 现在还有${count}个节点`)
    console.log(nodes.value)
  }
})

onConnect((connection) => {
  addEdges(connection)
  console.log(edges.value)
})


const nodeColor = (node: Node) => {
  switch (node.type) {
    case 'ConstNode':
      return '#ccc'
    case 'StringNode':
      return '#ccc'
    case 'TableNode':
      return '#ccc'
    case 'NumBinComputeNode':
      return '#ccc'
    default:
      return '#ff0072'
  }
}


</script>

<template>
  <div class="box">
    <VueFlow
    v-model:nodes="nodes"
    v-model:edges="edges"
    :connection-mode="ConnectionMode.Strict"
    id="main"
    >
      <Background bgColor="#999"/>

      <MiniMap mask-color="rgba(0,0,0,0.1)" pannable zoomable position="bottom-left" :node-color="nodeColor"/>

      <Controls position="bottom-right"/>


      <template #node-ConstNode="ConstNodeProps">
        <ConstNode v-bind="ConstNodeProps"/>
      </template>

      <template #node-StringNode="StringNodeProps">
        <StringNode v-bind="StringNodeProps"/>
      </template>

      <template #node-TableNode="TableNodeProps">
        <TableNode v-bind="TableNodeProps"/>
      </template>

      <template #node-NumBinComputeNode="NumBinComputeNodeProps">
        <NumBinComputeNode v-bind="NumBinComputeNodeProps" />
      </template>


      <Panel position="top-left">
        <label for="selectNode">请选择要添加的节点：</label>
        <select id="selectNode" style="background: #eee; padding: 0px 8px" v-model="selected">
          <option value="ConstNode">ConstNode</option>
          <option value="StringNode">StringNode</option>
          <option value="TableNode">TableNode</option>
          <option value="NumBinComputeNode">NumBinComputeNode</option>
        </select>
        <button style="background: #eee; padding: 0px 8px; margin: 10px" @click="addNode(selected)">确认</button>
      </Panel>
    </VueFlow>
  </div>
</template>

<style lang="scss">
/*import default minimap styles*/
@import '@vue-flow/minimap/dist/style.css' ;

/* import the necessary styles for Vue Flow to work */
@import '@vue-flow/core/dist/style.css';

/* import the default theme, this is optional but generally recommended */
@import '@vue-flow/core/dist/theme-default.css';

// import default controls styles
@import '@vue-flow/controls/dist/style.css';

</style>

<style lang="scss" scoped>
  .box {
    flex: 1;
    border: 1px solid black;
  }
</style>