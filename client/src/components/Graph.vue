<script lang='ts' setup>
import { ref, onMounted, computed, watch, nextTick, onUnmounted } from 'vue'
import { VueFlow, useVueFlow, ConnectionMode } from '@vue-flow/core'
import type { Node, Edge, NodeDragEvent } from '@vue-flow/core'
import { Background } from '@vue-flow/background'
import { MiniMap } from '@vue-flow/minimap'
import { Controls } from '@vue-flow/controls'
import ConstNode from './nodes/ConstNode.vue'
import StringNode from './nodes/StringNode.vue'
import TableNode from './nodes/TableNode.vue'
import NumBinComputeNode from './nodes/NumBinComputeNode.vue'
import { DefaultService } from '@/utils/api'
import { getProject, parseProject } from '@/utils/projectConvert'
import { monitorTask } from '@/utils/task'
import { useGraphStore } from '@/stores/graphStore'

const {project} = useGraphStore()
const { onConnect, onInit, onNodeDragStop, addEdges, onEdgesChange } = useVueFlow('main')
const shouldWatch = ref(false)
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
const listenNodePosition = ref(true)
const intervalId = setInterval(() => {
  listenNodePosition.value = true
  console.log('监听节点位置开始...')
}, 30000)


onUnmounted(() => {
  clearInterval(intervalId)
})

onInit(async (instance) => {
  try {
    console.log('getProjectApiProjectProjectIdGet')
    project.value = await DefaultService.getProjectApiProjectProjectIdGet(1)
    console.log(project.value)
    const graph = parseProject(project.value)
    nodes.value = graph.nodes
    edges.value = graph.edges
    await instance.fitView()

    await nextTick()
    shouldWatch.value = true
  }catch(err) {
    console.error('init error:',err)
  }
})

//add, move, modify nodes
watch(nodesData, async (newValue, oldValue) => {
  console.log("new: ", newValue, "old: ", oldValue, 'shouldWatch:', shouldWatch.value)
  if(!shouldWatch.value) return
  if(project.value) {
    const proj = getProject(project.value.project_name,
      project.value.project_id,
      project.value.user_id,
      nodes.value as Node[],
      edges.value as Edge[],
      project.value.workflow.error_message as string | null
    )
    console.log('@',proj)

    try {
      console.log('syncProjectApiProjectSyncPost')
      const {task_id} = await DefaultService.syncProjectApiProjectSyncPost(proj)
      console.log(task_id)

      if(task_id) {
        try {
          console.log('monitorTask')
          const messages = await monitorTask(project.value, task_id)
          console.log("Done:", messages)
        }catch(err) {
          console.error('@@',err)
        }

      }else {
        console.error('task_id is undefined')
      }

    }catch(err) {
      console.error('@@@',err)
    }

  }else {
    console.error('project is undefined')
  }

}, {deep: true, immediate: false})
onNodeDragStop(async (event: NodeDragEvent) => {
  console.log('节点位置变化:', {
    nodeId: event.node.id,
    nodeType: event.node.type,
    newPosition: event.node.position,
  })
  if(!listenNodePosition.value) return
  if(!shouldWatch.value) return
  listenNodePosition.value = false

  if(project.value) {
    const proj = getProject(project.value.project_name,
      project.value.project_id,
      project.value.user_id,
      nodes.value as Node[],
      edges.value as Edge[],
      project.value.workflow.error_message as string | null
    )
    console.log('@@@@',proj)

    try {
      console.log('syncProjectApiProjectSyncPost')
      const {task_id} = await DefaultService.syncProjectApiProjectSyncPost(proj)
      console.log(task_id)

      if(task_id) {
        try {
          console.log('monitorTask')
          const messages = await monitorTask(project.value, task_id)
          console.log("Done:", messages)
        }catch(err) {
          console.error('@@@@@',err)
        }

      }else {
        console.error('task_id is undefined')
      }

    }catch(err) {
      console.error('@@@@@@',err)
    }

  }else {
    console.error('project is undefined')
  }


})

watch(() => edges.value?.length, async (newValue, oldValue)=> {
  console.log('边改变了:', edges.value, 'shouldWatch:', shouldWatch.value)
  if(!shouldWatch.value) return

  if(project.value) {
    const proj = getProject(project.value.project_name,
      project.value.project_id,
      project.value.user_id,
      nodes.value as Node[],
      edges.value as Edge[],
      project.value.workflow.error_message as string | null
    )
    console.log('@@@@@@@',proj)

    try {
      console.log('syncProjectApiProjectSyncPost')
      const {task_id} = await DefaultService.syncProjectApiProjectSyncPost(proj)
      console.log(task_id)

      if(task_id) {
        try {
          console.log('monitorTask')
          const messages = await monitorTask(project.value, task_id)
          console.log("Done:", messages)
        }catch(err) {
          console.error('@@@@@@@@',err)
        }

      }else {
        console.error('task_id is undefined')
      }

    }catch(err) {
      console.error('@@@@@@@@@',err)
    }

  }else {
    console.error('project is undefined')
  }


})

onConnect((connection) => {
  addEdges(connection)
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
  }
</style>