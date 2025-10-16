<script lang='ts' setup>
import { ref, onMounted } from 'vue'  
import { VueFlow, useVueFlow, Panel } from '@vue-flow/core'
import type { Node, Edge } from '@vue-flow/core'  
import { Background } from '@vue-flow/background'
import { MiniMap, MiniMapNode } from '@vue-flow/minimap'
import { Controls } from '@vue-flow/controls'
import CustomNode from './nodes/CustomNode.vue'
import {useGraphStore} from '../stores/graphStore'

const graphStore = useGraphStore()
graphStore.vueFlowInstance = useVueFlow()
const { onConnect, onInit, removeEdges } = useVueFlow()

onConnect(({ source, target, sourceHandle, targetHandle }) => {
  console.log('source', source)
  console.log('target', target)
  // these are the handle ids of the source and target node
  // if no id is specified these will be `null`, meaning the first handle of the necessary type will be used
  console.log('sourceHandle', sourceHandle)
  console.log('targetHandle', targetHandle)
})

const nodes = ref<Node[]>([
  {
    id: '1',
    position: { x: 50, y: 50 },
    data: { label: 'Node 1', },
  },
  {
    id: '2',
    position: { x: 50, y: 250 },
    data: { label: 'Node 2', },
  },
  {
    id: '3',
    position: { x: 250, y: 50 },
    data: { label: 'Node 3', },
  },
  {
    id: '4',
    position: { x: 250, y: 250 },
    data: { label: 'Node 4', },
  },
  {
    id: '5',
    position: { x: 450, y: 150 },
    data: { label: 'Node 5', },
    type: 'custom',
  }
])

const edges = ref([
  {
    id: 'e1->2',
    source: '1',
    target: '2',
  },
  {
    id: 'e1->3',
    source: '1',
    target: '3',
  },
  {
    id: 'e2->3',
    source: '2',
    target: '3',
  },
  {
    id: 'e2->4',
    source: '2',
    target: '4',
  },
])


// any event that is emitted from the `<VueFlow />` component can be listened to using the `onEventName` method
onInit((instance) => {
  // `instance` is the same type as the return of `useVueFlow` (VueFlowStore)
  instance.fitView()
})

function removeOneEdge() {
  removeEdges('e1->2')
}

function removeMultipleEdges() {
  removeEdges(['e1->3', 'e2->3'])
  console.log(edges.value)
}

const nodeColor = (node: Node) => {
  switch (node.type) {
    case 'input':  return '#6ede87'
    case 'output': return '#6865A5'
    case 'custom': return '#ccc'
    default:       return '#ff0072'
  }
}

</script>

<template>
  <div class="box">
    <VueFlow
    v-model:nodes="nodes"
    v-model:edges="edges"
    >
      <Background color="#111" bgColor="rgba(0,0,0,0.5)"/>

      <MiniMap mask-color="rgba(0,0,0,0.1)" pannable zoomable position="bottom-left" :node-color="nodeColor"/>

      <Controls position="bottom-right"/>

      <template #node-custom="customNodeProps">
        <CustomNode v-bind="customNodeProps"/> 
      </template>

      <Panel position="top-left">
        <button @click="removeOneEdge">Remove Edge 1</button>
        <button @click="removeMultipleEdges">Remove Edges 2 and 3</button>
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
    background: #fff;
  }
</style>