<script lang='ts' setup>
import { ref, onMounted, watch, nextTick, onUnmounted } from 'vue'
import { VueFlow, useVueFlow, ConnectionMode, Panel } from '@vue-flow/core'
import type { NodeDragEvent } from '@vue-flow/core'
import { Background } from '@vue-flow/background'
import { MiniMap } from '@vue-flow/minimap'
import RightClickMenu from './tools/RightClickMenu.vue'
import GraphControls from './tools/GraphControls.vue'
import ConstNode from './nodes/ConstNode.vue'
import StringNode from './nodes/StringNode.vue'
import TableNode from './nodes/TableNode.vue'
import NumBinComputeNode from './nodes/NumBinComputeNode.vue'
import { DefaultService } from '@/utils/api'
import { getProject, parseProject } from '@/utils/projectConvert'
import { monitorTask } from '@/utils/task'
import type { BaseNode } from '@/types/nodeTypes'
import type { vueFlowProject } from '@/types/vueFlowProject'
import { useRoute } from 'vue-router'
import { useModalStore } from '@/stores/modalStore'


const modalStore = useModalStore()
const {params: {projectId}} = useRoute()
const project: vueFlowProject = ({
  project_id: -1,
  project_name: "undefined",
  user_id: -1,
  workflow: {
    nodes: ref([]),
    edges: ref([])
  }
})
const { onConnect, onInit, onNodeDragStop, addEdges, onPaneContextMenu  } = useVueFlow('main')
const shouldWatch = ref(false)
const listenNodePosition = ref(true)
const intervalId = setInterval(() => {
  listenNodePosition.value = true
  console.log('监听节点位置开始...')
}, 30000)


onUnmounted(() => {
  clearInterval(intervalId)
})

onMounted(async () => {
  try {
    console.log('getProjectApiProjectProjectIdGet')
    const p = await DefaultService.getProjectApiProjectProjectIdGet(Number(projectId))
    console.log(p)
    parseProject(p, project)
    await nextTick()
    shouldWatch.value = true
  }catch(err) {
    console.error('init error:', err)
  }
})

onInit((instance) => {
  instance.fitView()
})

watch([
  () => project.workflow.nodes.value.length, 
  () => project.workflow.nodes.value.map(n => JSON.stringify(n.data.param)).join('|'),
  () => project.workflow.edges.value.length
], async (newValue, oldValue) => {
  console.log("new: ", newValue, "old: ", oldValue, 'shouldWatch:', shouldWatch.value)
  if(!shouldWatch.value) return
  if(project) {
    const p = getProject(project)
    console.log('@',p)

    try {
      console.log('syncProjectApiProjectSyncPost')
      const taskResponse = await DefaultService.syncProjectApiProjectSyncPost(p)
      console.log(taskResponse)
      if(!taskResponse) return
      const {task_id} = taskResponse

      if(task_id) {
        try {
          console.log('monitorTask')
          const messages = await monitorTask(p, task_id)
          console.log("Done:", messages)
          parseProject(p, project)
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

}, {deep: false, immediate: false})
onNodeDragStop(async (event: NodeDragEvent) => {
  console.log('节点位置变化:', {
    nodeId: event.node.id,
    nodeType: event.node.type,
    newPosition: event.node.position,
  }, 'listenNodePosition:', listenNodePosition.value)
  if(!listenNodePosition.value || !shouldWatch.value) return
  listenNodePosition.value = false

  if(project) {
    const p = getProject(project)
    console.log('@@@@',p)

    try {
      console.log('syncProjectApiProjectSyncPost')
      const taskResponse = await DefaultService.syncProjectApiProjectSyncPost(p)
      console.log(taskResponse)
      if(!taskResponse) return
      const {task_id} = taskResponse

      if(task_id) {
        try {
          console.log('monitorTask')
          const messages = await monitorTask(p, task_id)
          console.log("Done:", messages)
          parseProject(p, project)
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

onConnect((connection) => {
  addEdges(connection)
})


const nodeColor = (node: BaseNode) => {
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
  <div class="graphLayout">
    <div class="vueFlow">
      <VueFlow
      v-model:nodes="project.workflow.nodes.value"
      v-model:edges="project.workflow.edges.value"
      :connection-mode="ConnectionMode.Strict"
      id="main"
      >
        <Background color="rgba(50, 50, 50, 0.05)" variant="dots" :gap="20" :size="4" bgColor="rgba(245, 247, 250, 0.05)"/>

        <MiniMap mask-color="rgba(0,0,0,0.1)" pannable zoomable position="bottom-left" :node-color="nodeColor" class="controller-style set_background_color"/>

        <Panel position="bottom-center">
          <GraphControls :id="`${projectId}`"/>
        </Panel>


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
    <div>
      <RightClickMenu />
    </div>
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

/* Remove white border bottom in minimap */
.vue-flow__minimap > svg,
.vue-flow__minimap svg {
  display: block;
  width: 100%;
  height: 100%;
}

</style>

<style lang="scss" scoped>
@use '../common/style/global.scss';
  .graphLayout {
    flex: 1;
    .vueFlow {
      width: 100%;
      height: 100%;
    }
  }
</style>
