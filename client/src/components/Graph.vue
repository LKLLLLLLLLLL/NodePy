<script lang='ts' setup>
import { ref, onMounted, computed, watch } from 'vue'
import { VueFlow, useVueFlow, ConnectionMode } from '@vue-flow/core'
import type { Node, Edge } from '@vue-flow/core'
import { Background } from '@vue-flow/background'
import { MiniMap } from '@vue-flow/minimap'
import { Controls } from '@vue-flow/controls'
import ConstNode from './nodes/ConstNode.vue'
import StringNode from './nodes/StringNode.vue'
import TableNode from './nodes/TableNode.vue'
import NumBinComputeNode from './nodes/NumBinComputeNode.vue'


const { onConnect, onInit, onNodesChange, addEdges, onEdgesChange } = useVueFlow('main')

const nodes = ref([])

const nodesData = computed(() => {
  const result = nodes.value.map((n: Node) => {
    return {
      id: n.id,
      data: n.data
    }
  })
  return result
})

const edges = ref<Edge[]>([])



// any event that is emitted from the `<VueFlow />` component can be listened to using the `onEventName` method
onInit((instance) => {
  // `instance` is the same type as the return of `useVueFlow` (VueFlowStore)
  instance.fitView()
})

onNodesChange(changes => {
  const ARchanges = changes.filter(c => c.type === 'add' || c.type === 'remove')
  ARchanges.forEach(c => {
    if(c.type ==='add') console.log('新增节点:', c.item.id)
    if(c.type === 'remove') console.log('移除节点', c.id)
  })
})
watch(nodesData, (newValue, oldValue) => {
  console.log("new: ", newValue[0]?.data.value, "old: ", oldValue[0]?.data.value)
}, {deep: true})

onEdgesChange(changes => {
  const ARchanges = changes.filter(c => c.type === 'add' || c.type === 'remove')
  ARchanges.forEach(c => {
    if(c.type ==='add') console.log('新增边:', c.item)
    if(c.type === 'remove') console.log('移除边', c)
  })
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
      <Background color="#111" bgColor="rgba(200, 200, 200, 0.1)"/> 

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

.vue-flow__handle {
  width: 10px;   
  height: 10px;
  border-radius: 50%;
}

</style>

<style lang="scss" scoped>
  .box {
    flex: 1;
    border: 1px solid black;
  }
</style>