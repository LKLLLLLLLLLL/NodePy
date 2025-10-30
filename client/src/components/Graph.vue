<script lang='ts' setup>
import { ref, onMounted, watch, nextTick, onUnmounted, computed } from 'vue'
import { VueFlow, useVueFlow, ConnectionMode, Panel } from '@vue-flow/core'
import type { NodeDragEvent } from '@vue-flow/core'
import { Background } from '@vue-flow/background'
import { MiniMap } from '@vue-flow/minimap'
import { useGraphStore } from '@/stores/graphStore'
import { syncProject } from '@/utils/network'
import RightClickMenu from './tools/RightClickMenu/RightClickMenu.vue'
import GraphControls from './tools/GraphControls.vue'
import GraphInfo from './GraphInfo.vue'
import NodePyEdge from './NodePyEdge.vue'
import NodePyConnectionLine from './NodePyConnectionLine.vue'
import ConstNode from './nodes/ConstNode.vue'
import StringNode from './nodes/StringNode.vue'
import TableNode from './nodes/TableNode.vue'
import NumberBinOpNode from './nodes/NumberBinOpNode.vue'
import { DefaultService } from '@/utils/api'
import { getProject, parseProject } from '@/utils/projectConvert'
import { monitorTask } from '@/utils/task'
import type { BaseNode } from '@/types/nodeTypes'
import { useRoute } from 'vue-router'

const graphStore = useGraphStore()
const {params: {projectId}} = useRoute()
const { onConnect, onInit, onNodeDragStop, addEdges } = useVueFlow('main')
const shouldWatch = ref(false)
const listenNodePosition = ref(true)
const intervalId = setInterval(() => {
  listenNodePosition.value = true
  console.log('监听节点位置开始...')
}, 30000)
const nodes = computed(() => graphStore.project.workflow.nodes)
const edges = computed(() => graphStore.project.workflow.edges)
const is_syncing = ref(false)
const sync_errmsg = ref('')


onUnmounted(() => {
  clearInterval(intervalId)
})

onMounted(async () => {
  try {
    console.log('getProjectApiProjectProjectIdGet')
    const p = await DefaultService.getProjectApiProjectProjectIdGet(Number(projectId))
    console.log(p)
    parseProject(p, graphStore.project)
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
  () => nodes.value.length, // @ts-ignore
  () => nodes.value.map(n => JSON.stringify(n.data.param)).join('|'),
  () => edges.value.length
], async (newValue, oldValue) => {
  console.log("new: ", newValue, "old: ", oldValue, 'shouldWatch:', shouldWatch.value)
  if(!shouldWatch.value) return
  if(graphStore.project) {
    const p = getProject(graphStore.project)
    console.log('@',p)

    try {
      is_syncing.value = true
      const res = await syncProject(p)
      console.log('syncProject response:', res)
      parseProject(p, graphStore.project)
    }catch(err) {
      console.error('@@', err)
      sync_errmsg.value = err instanceof Error ? err.message : String(err)
    }finally {
      is_syncing.value = false
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

  if(graphStore.project) {
    const p = getProject(graphStore.project)
    console.log('@@@',p)

    try {
      is_syncing.value = true
      const res = await syncProject(p)
      console.log('syncProject response:', res)
      parseProject(p, graphStore.project)
    }catch(err) {
      console.error('@@@@',err)
      sync_errmsg.value = err instanceof Error ? err.message : String(err)
    }finally {
      is_syncing.value = false
    }

  }else {
    console.error('project is undefined')
  }

})

onConnect((connection) => {
  const addedEdge = {
    id: Date.now().toString(),
    source: connection.source,
    sourceHandle: connection.sourceHandle,
    target: connection.target,
    targetHandle: connection.targetHandle,
    type: "NodePyEdge"
  }
  addEdges(addedEdge)
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
      v-model:nodes="graphStore.project.workflow.nodes"
      v-model:edges="graphStore.project.workflow.edges"
      :connection-mode="ConnectionMode.Strict"
      id="main"
      >

        <Background color="rgba(50, 50, 50, 0.05)" variant="dots" :gap="20" :size="4"/>

        <MiniMap mask-color="rgba(0,0,0,0.1)" pannable zoomable position="bottom-left" :node-color="nodeColor" class="controller-style set_background_color"/>

        <Panel position="bottom-center">
          <GraphControls :id="`${projectId}`"/>
        </Panel>

        <Panel position="top-left">
          <GraphInfo :is_syncing="is_syncing" :syncing_err_msg="sync_errmsg"/>
        </Panel>


        <template #edge-NodePyEdge="NodePyEdgeProps">
          <NodePyEdge v-bind="NodePyEdgeProps"/>
        </template>

        <template #connection-line="ConnectionLineProps">
          <NodePyConnectionLine v-bind="ConnectionLineProps"/>
        </template>

        <template #node-ConstNode="ConstNodeProps">
          <ConstNode v-bind="ConstNodeProps"/>
        </template>

        <template #node-StringNode="StringNodeProps">
          <StringNode v-bind="StringNodeProps"/>
        </template>

        <template #node-TableNode="TableNodeProps">
          <TableNode v-bind="TableNodeProps"/>
        </template>

        <template #node-NumberBinOpNode="NumberBinOpNodeProps">
          <NumberBinOpNode v-bind="NumberBinOpNodeProps" />
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

.vue-flow__pane {
    cursor: default !important;
}

.vue-flow__panel {
  margin-left: 0;
  margin-right: 0;
  margin-bottom: 20px;
}

.vue-flow__minimap {
  margin-left: 20px;
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
@use '../common/style/global.scss' as *;
.graphLayout {
    flex: 1;
    .vueFlow {
        width: 100%;
        height: 100%;
    }
}
.vue-flow__background {
    background-color: $mix-background-color;
}
</style>
