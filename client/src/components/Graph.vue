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
import { DefaultService } from '@/utils/api'
import type { Project } from '@/utils/api'
import { getProject, parseProject } from '@/utils/projectConvert'
import { monitorTask } from '@/utils/task'
import { useGraphStore } from '@/stores/graphStore'

const {project} = useGraphStore()

const { onConnect, onInit, onNodesChange, addEdges, onEdgesChange } = useVueFlow('main')

const nodes = ref<Node[]>()

const nodesData = computed(() => {
  const result = nodes.value?.map((n: Node) => {
    return {
      id: n.id,
      data: n.data
    }
  })
  return result
})

const edges = ref<Edge[]>()


onInit(async (instance) => {
  try {
    project.value = await DefaultService.getProjectApiProjectProjectIdGet(1)
    const graph = parseProject(project.value)
    nodes.value = graph.nodes
    edges.value = graph.edges
    instance.fitView()
  }catch(err) {
    console.error(err)
  }
})

onNodesChange(async (changes) => {
  const ARchanges = changes.filter(c => c.type === 'add' || c.type === 'remove')
  ARchanges.forEach(c => {
    if(c.type ==='add') console.log('新增节点:', c.item)
    if(c.type === 'remove') console.log('移除节点', c)
  })

  if(project.value) {
    const proj = getProject(project.value.project_name,
      project.value.project_id,
      project.value.user_id,
      nodes.value as Node[],
      edges.value as Edge[]
    )

    try {
      const {task_id} = await DefaultService.syncProjectApiProjectSyncPost(proj)

      if(task_id) {
        try {
          const messages = await monitorTask(project.value, task_id)
          console.log("Done:", messages)
        }catch(err) {
          console.error(err)
        }
      }
    
    }catch(err) {
      console.log(err)
    }
  }else {
    console.error('project is undefined')
  }
})
watch(nodesData, (newValue, oldValue) => {
  console.log("new: ", newValue?.[0]?.data.value, "old: ", oldValue?.[0]?.data.value)
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