<script setup>
import { ref, onMounted } from 'vue'  
import { VueFlow, useVueFlow, Panel } from '@vue-flow/core'
import CustomNode from './nodes/CustomNode.vue'
const { onConnect } = useVueFlow()

onConnect(({ source, target, sourceHandle, targetHandle }) => {
  console.log('source', source)
  console.log('target', target)
  // these are the handle ids of the source and target node
  // if no id is specified these will be `null`, meaning the first handle of the necessary type will be used
  console.log('sourceHandle', sourceHandle)
  console.log('targetHandle', targetHandle)
})

const nodes = ref([
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

const { removeEdges } = useVueFlow()

function removeOneEdge() {
  removeEdges('e1->2')
}

function removeMultipleEdges() {
  removeEdges(['e1->3', 'e2->3'])
}
</script>

<template>
  <div class="box">
    <VueFlow :nodes="nodes" :edges="edges">
      <template #node-custom="customNodeProps">
        <CustomNode v-bind="customNodeProps"/> 
      </template>
      <Panel>
        <button @click="removeOneEdge">Remove Edge 1</button>
        <button @click="removeMultipleEdges">Remove Edges 2 and 3</button>
      </Panel>
    </VueFlow>
  </div>
</template>

<style lang="scss">
/* import the necessary styles for Vue Flow to work */
@import '@vue-flow/core/dist/style.css';

/* import the default theme, this is optional but generally recommended */
@import '@vue-flow/core/dist/theme-default.css';
</style>

<style lang="scss" scoped>
  .box {
    flex: 1;
    border: 1px solid black;
  }
</style>