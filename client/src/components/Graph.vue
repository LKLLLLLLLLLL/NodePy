<script lang='ts' setup>
import { ref, onMounted } from 'vue'  
import { VueFlow, useVueFlow, Panel } from '@vue-flow/core'
import type { Node, Edge } from '@vue-flow/core'  
import { Background } from '@vue-flow/background'
import { MiniMap, MiniMapNode } from '@vue-flow/minimap'
import { Controls } from '@vue-flow/controls'
import CustomNode from './nodes/CustomNode.vue'
import ConstNode from './nodes/ConstNode.vue'
import {useGraphStore} from '../stores/graphStore'
import type * as Nodetypes from './nodes/type'

const graphStore = useGraphStore()
graphStore.vueFlowInstance = useVueFlow()
const { onConnect, onInit, addNodes, onNodesChange } = useVueFlow()

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
    id: '-1',
    position: { x: 50, y: 50 },
    data: { label: 'Node 1', },
  },
  {
    id: '-2',
    position: { x: 50, y: 250 },
    data: { label: 'Node 2',
      resultType: 'table'
     },
  },
  {
    id: '-3',
    position: { x: 250, y: 50 },
    data: { label: 'Node 3', },
  },
  {
    id: '-4',
    position: { x: 250, y: 250 },
    data: { label: 'Node 4', },
  },
  {
    id: '-5',
    position: { x: 450, y: 150 },
    data: { label: 'Node 5', },
    type: 'custom',
  }
])

const edges = ref([
  {
    id: 'e-1->-2',
    source: '-1',
    target: '-2',
  },
  {
    id: 'e1->3',
    source: '-1',
    target: '-3',
  },
  {
    id: 'e-2->-3',
    source: '-2',
    target: '-3',
  },
  {
    id: 'e-2->-4',
    source: '-2',
    target: '-4',
  },
])

const selected = ref()
let count = 0

// any event that is emitted from the `<VueFlow />` component can be listened to using the `onEventName` method
onInit((instance) => {
  // `instance` is the same type as the return of `useVueFlow` (VueFlowStore)
  instance.fitView()
})

onNodesChange(changes => {
  changes = changes.filter(c => c.type === 'add')
  if(changes.length > 0) {
    count += changes.length
    console.log(`现在增加了${count}个节点`)
    console.log(nodes.value)
  }
})


const nodeColor = (node: Node) => {
  switch (node.type) {
    case 'input':
      return '#6ede87'
    case 'output':
      return '#6865A5'
    case 'custom':
      return '#ccc'
    case 'ConstNode':
      return '#aaa'
    default:
      return '#ff0072'
  }
}

const addNode = (e?: MouseEvent) => {
  switch(selected.value){
    case 'ConstNode':
      const added: Nodetypes.ConstNode = {
        id: `${count}`,
        position: { x: 100, y: 100 + Math.floor(Math.random() * 101 - 50)},
        type: 'ConstNode',
        data: {
          value: 0,
          data_type: 'int'
        }
      }
      addNodes(added)
      break

    

    default:
      console.log(selected.value)
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

      <template #node-ConstNode="ConstNodeProps">
        <ConstNode v-bind="ConstNodeProps"/>
      </template>

      <Panel position="top-left">
        <label for="selectNode">请选择要添加的节点：</label>
        <select id="selectNode" style="background: #eee; padding: 0px 8px" v-model="selected">
          <option value="ConstNode">ConstNode</option>
        </select>
        <button style="background: #eee; padding: 0px 8px; margin: 10px" @click="addNode">确认</button>
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