<script lang='ts' setup>
import { ref, onMounted, watch, nextTick, onUnmounted, computed } from 'vue'
import { VueFlow, useVueFlow, ConnectionMode, Panel } from '@vue-flow/core'
import type { NodeDragEvent } from '@vue-flow/core'
import { Background } from '@vue-flow/background'
import { MiniMap } from '@vue-flow/minimap'
import { useGraphStore } from '@/stores/graphStore'
import { useResultStore } from '@/stores/resultStore'
import { useModalStore } from '@/stores/modalStore'
import { sync, syncUiState } from '@/utils/network'
import RightClickMenu from '../RightClickMenu/RightClickMenu.vue'
import GraphControls from './GraphControls.vue'
import GraphInfo from './GraphInfo.vue'
import NodePyEdge from '../NodePyEdge.vue'
import NodePyConnectionLine from '../NodePyConnectionLine.vue'
import ConstNode from '../nodes/ConstNode.vue'
import StringNode from '../nodes/StringNode.vue'
import TableNode from '../nodes/TableNode.vue'
import NumberBinOpNode from '../nodes/NumberBinOpNode.vue'
import { DefaultService } from '@/utils/api'
import { initVueFlowProject } from '@/utils/projectConvert'
import type { BaseNode } from '@/types/nodeTypes'
import { useRoute } from 'vue-router'

const resultStore = useResultStore();
const modalStore = useModalStore();
const graphStore = useGraphStore()

const {params: {projectId}} = useRoute()
const { onNodeClick,findNode,onConnect, onInit, onNodeDragStop, addEdges } = useVueFlow('main')
const shouldWatch = ref(false)
const listenNodePosition = ref(true)
const intervalId = setInterval(() => {
  listenNodePosition.value = true
  console.log('监听节点位置开始...')
}, 30000)
const nodes = computed(() => graphStore.project.workflow.nodes)
const edges = computed(() => graphStore.project.workflow.edges)


onUnmounted(() => {
  clearInterval(intervalId)
})

onMounted(async () => {
  try {
    console.log('getProjectApiProjectProjectIdGet')
    const p = await DefaultService.getProjectApiProjectProjectIdGet(Number(projectId))
    initVueFlowProject(p, graphStore.project)
    console.log(graphStore.project)
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
    sync(graphStore)
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
    syncUiState(graphStore)
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

  const default_url_id: number = 12306
  const url_id = ref<number>(default_url_id)
    
  onNodeClick( async (event) => {
    // 获取节点完整信息
    resultStore.refresh();
    const currentNode = findNode(event.node.id);
    // console.log('完整节点信息:', currentNode);
    // console.log('data.param:',currentNode?.data.param);
    // console.log('data.out:',currentNode?.data.data_out);
    // console.log('currentInfo:',resultStore.currentInfo)
    // console.log('是否存在result:',currentNode?.data.data_out.result)
    // console.log('currentResult:',resultStore.currentResult)
    if(!currentNode?.data.data_out.result){
      resultStore.currentInfo = currentNode?.data.param
      // console.log('没有result,有currentInfo:',resultStore.currentInfo)
    }
    if(currentNode) url_id.value = currentNode.data.data_out.result.data_id;
    resultStore.currentResult = await resultStore.getResultCacheContent(url_id.value);
    if(modalStore.findModal('result')==undefined){
      resultStore.createResultModal();
      modalStore.activateModal('result')
    }
    else{
      modalStore.activateModal('result');
    }
    // console.log(resultStore.cacheStatus);
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

const isValidConnection = (connection: any) => {
  if(connection.source === connection.target) return false
  if(connection.target && connection.targetHandle) {
    const existingConnections = edges.value.filter(e => e.target === connection.target && e.targetHandle === connection.targetHandle)
    if(existingConnections.length > 0) return false
  }

  return true
}

</script>

<template>
  <div class="graphLayout">
    <div class="vueFlow">
      <VueFlow
      v-model:nodes="graphStore.project.workflow.nodes"
      v-model:edges="graphStore.project.workflow.edges"
      :connection-mode="ConnectionMode.Strict"
      :is-valid-connection="isValidConnection"
      id="main"
      >

        <Background color="rgba(50, 50, 50, 0.05)" variant="dots" :gap="20" :size="4"/>

        <MiniMap mask-color="rgba(0,0,0,0.1)" pannable zoomable position="bottom-left" :node-color="nodeColor" class="controller-style set_background_color"/>

        <Panel position="bottom-center">
          <GraphControls :id="`${projectId}`"/>
        </Panel>

        <Panel position="top-left">
          <GraphInfo :is_syncing="graphStore.is_syncing" :syncing_err_msg="graphStore.syncing_err_msg"/>
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
    border: none;
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
@use '../../common/global.scss' as *;
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
