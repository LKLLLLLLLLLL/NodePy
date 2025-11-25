<script lang='ts' setup>
import { ref, onMounted, watch, nextTick, onUnmounted, computed } from 'vue'
import { VueFlow, useVueFlow, ConnectionMode, Panel } from '@vue-flow/core'
import type { NodeDragEvent } from '@vue-flow/core'
import { Background } from '@vue-flow/background'
import { MiniMap } from '@vue-flow/minimap'
import { useGraphStore } from '@/stores/graphStore'
import { useResultStore } from '@/stores/resultStore'
import { useModalStore } from '@/stores/modalStore'
import { sync, syncUiState, getProjectFromServer } from '@/utils/network'
import RightClickMenu from '../RightClickMenu/RightClickMenu.vue'
import GraphControls from './GraphControls.vue'
import GraphInfo from './GraphInfo.vue'
import NodePyEdge from '../NodePyEdge.vue'
import NodePyConnectionLine from '../NodePyConnectionLine.vue'
import ConstNode from '../nodes/ConstNode.vue'
import StringNode from '../nodes/StringNode.vue'
import TableNode from '../nodes/TableNode.vue'
import BoolNode from '../nodes/BoolNode.vue'
import TableFromCSVNode from '../nodes/TableFromCSVNode.vue'
import NumberBinOpNode from '../nodes/NumberBinOpNode.vue'
import UploadNode from '../nodes/UploadNode.vue'
import PlotNode from '../nodes/PlotNode.vue'
import { initVueFlowProject } from '@/utils/projectConvert'
import type { BaseNode } from '@/types/nodeTypes'
import { nodeCategoryColor } from '@/types/nodeTypes'
import { useRoute } from 'vue-router'

const resultStore = useResultStore()
const modalStore = useModalStore()
const graphStore = useGraphStore()

const {params: {projectId}} = useRoute()
const { onNodeClick, findNode, onConnect, onInit, onNodeDragStop, addEdges, getNodes, onPaneClick } = useVueFlow('main')
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
    const p = await getProjectFromServer(Number(projectId))
    initVueFlowProject(p, graphStore.project)
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
  if(!listenNodePosition.value || !shouldWatch.value) return
  listenNodePosition.value = false

  if(graphStore.project) {
    syncUiState(graphStore)
  }else {
    console.error('project is undefined')
  }

})  //  sync and sync projectUI

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

watch(()=>graphStore.currentNode?.data.data_out?.result?.data_id,async ()=>{
  graphStore.url_id = graphStore.currentNode?.data.data_out?.result?.data_id!
  resultStore.currentResult = await resultStore.getResultCacheContent(graphStore.url_id)
})

  // 双击检测变量
const lastClickTime = ref<number>(0)
const lastNodeId = ref<string>('default')
// 监听节点点击事件
onNodeClick((event) => {
  const currentTime = Date.now()
  const currentNodeId = event.node.id
  
  // 检查是否是双击（300ms 内点击同一节点）
  if (currentTime - lastClickTime.value < 300 && currentNodeId === lastNodeId.value) {
    // 重置状态
    lastClickTime.value = 0
    // 执行双击处理逻辑
    handleNodeDoubleClick(event)
    lastNodeId.value = 'default'
  } else {
    // 更新状态等待可能的第二次点击
    lastClickTime.value = currentTime
    lastNodeId.value = currentNodeId
  }
})
async function handleNodeDoubleClick(event) {
  // 获取节点完整信息
  resultStore.cacheGarbageRecycle()
  console.log('double click success')
  graphStore.currentNode = findNode(event.node.id)

  getNodes.value.forEach((n) => {
    if(n.data.dbclicked) {
      n.data.dbclicked = false
    }
  })  //  reset dbclicked so that only one node can be dbclicked

  if(graphStore.currentNode) {
    graphStore.currentNode.data.dbclicked = true
  } //  双击状态更新

  if(graphStore.currentNode?.data?.data_out===undefined){
    resultStore.currentInfo = graphStore.currentNode?.data.param
    resultStore.currentResult = resultStore.default_dataview
  }
  else if (graphStore.currentNode?.data?.data_out !== undefined) {
    // 获取第一个包含data_id的子对象
    const dataOut = graphStore.currentNode.data.data_out;
    const dataIdEntry = Object.entries(dataOut).find(([key, value]) => 
      value && typeof value === 'object' && 'data_id' in value
    );
    
    if (dataIdEntry) {
      const [key, value] = dataIdEntry;
      graphStore.url_id = value.data_id; // waiting multi-result nodes
      resultStore.currentResult = await resultStore.getResultCacheContent(graphStore.url_id);
      resultStore.currentInfo = graphStore.currentNode?.data.param;
    }
  }
  if(modalStore.findModal('result')==undefined){
    resultStore.createResultModal()
    modalStore.activateModal('result')
  }
  else{
    modalStore.activateModal('result')
  }

}

const lastPaneClicktime = ref(0)
onPaneClick(() => {
  const currentTime = Date.now()
  if(currentTime - lastPaneClicktime.value < 300) {
    lastClickTime.value = 0
    handlePaneDoubleClick()
  }else {
    lastPaneClicktime.value = currentTime
  }
})
const handlePaneDoubleClick = () => {
  getNodes.value.forEach((n) => {
    if(n.data.dbclicked) {
      n.data.dbclicked = false
    }
  })  //  cancel node dbclick when dbclicking the pane
}


const nodeColor = (node: BaseNode) => {
  switch (node.type) {
    case 'ConstNode':
      return nodeCategoryColor.input
    case 'StringNode':
      return nodeCategoryColor.input
    case 'BoolNode':
      return nodeCategoryColor.input
    case 'TableNode':
      return nodeCategoryColor.input
    case 'TableFromCSVNode':
      return nodeCategoryColor.input
    case 'NumberBinOpNode':
      return nodeCategoryColor.compute
    case 'PlotNode':
      return nodeCategoryColor.visualize
    case 'UploadNode':
      return nodeCategoryColor.file
    default:
      return nodeCategoryColor.default
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
      :zoom-on-double-click="false"
      id="main"
      >

        <Background color="rgba(50, 50, 50, 0.05)" variant="dots" :gap="20" :size="4"/>

        <MiniMap mask-color="rgba(0,0,0,0.1)" pannable zoomable position="bottom-left" :node-color="nodeColor" class="controller-style set_background_color"/>

        <Panel position="bottom-center">
          <GraphControls :id="`${projectId}`"/>
        </Panel>

        <Panel position="top-left" class="graphinfo">
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
        
        <template #node-BoolNode="BoolNodeProps">
          <BoolNode v-bind="BoolNodeProps"/>
        </template>

        <template #node-TableFromCSVNode="TableFromCSVNodeProps">
          <TableFromCSVNode v-bind="TableFromCSVNodeProps"/>
        </template>

        <template #node-NumberBinOpNode="NumberBinOpNodeProps">
          <NumberBinOpNode v-bind="NumberBinOpNodeProps"/>
        </template>

        <template #node-PlotNode="PlotNodeProps">
          <PlotNode v-bind="PlotNodeProps" />
        </template>

        <template #node-UploadNode="UploadNodeProps">
          <UploadNode v-bind="UploadNodeProps"/>
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

.vue-flow__nodesselection-rect{
  display: none;
} //  hide the selection-rect

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
} //  vue-flow__background must be written here since @use must be written here

.graphinfo {
  pointer-events: none !important;
  user-select: none;
}

</style>
