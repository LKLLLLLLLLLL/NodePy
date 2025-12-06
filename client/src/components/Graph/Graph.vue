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
import ConstNode from '../nodes/input/ConstNode.vue'
import StringNode from '../nodes/input/StringNode.vue'
import TableNode from '../nodes/input/TableNode.vue'
import BoolNode from '../nodes/input/BoolNode.vue'
import RandomNode from '../nodes/input/RandomNode.vue'
import RangeNode from '../nodes/input/RangeNode.vue'
import DateTimeNode from '../nodes/input/DateTimeNode.vue'
import KlineNode from '../nodes/input/KlineNode.vue'
import NumberBinOpNode from '../nodes/compute/NumberBinOpNode.vue'
import BoolBinOpNode from '../nodes/compute/BoolBinOpNode.vue'
import NumberUnaryOpNode from '../nodes/compute/NumberUnaryOpNode.vue'
import PrimitiveCompareNode from '../nodes/compute/PrimitiveCompareNode.vue'
import BoolUnaryOpNode from '../nodes/compute/BoolUnaryOpNode.vue'
import ColWithNumberBinOpNode from '../nodes/compute/ColWithNumberBinOpNode.vue'
import ColWithBoolBinOpNode from '../nodes/compute/ColWithBoolBinOpNode.vue'
import NumberColUnaryOpNode from '../nodes/compute/NumberColUnaryOpNode.vue'
import BoolColUnaryOpNode from '../nodes/compute/BoolColUnaryOpNode.vue'
import NumberColWithColBinOpNode from '../nodes/compute/NumberColWithColBinOpNode.vue'
import BoolColWithColBinOpNode from '../nodes/compute/BoolColWithColBinOpNode.vue'
import ColCompareNode from '../nodes/compute/ColCompareNode.vue'
import ToStringNode from '../nodes/compute/ToStringNode.vue'
import ToIntNode from '../nodes/compute/ToIntNode.vue'
import ToFloatNode from '../nodes/compute/ToFloatNode.vue'
import ToBoolNode from '../nodes/compute/ToBoolNode.vue'
import PlotNode from '../nodes/visualize/PlotNode.vue'
import AdvancePlotNode from '../nodes/visualize/AdvancePlotNode.vue'
import WordcloudNode from '../nodes/visualize/WordcloudNode.vue'
import StripNode from '../nodes/stringProcess/StripNode.vue'
import SliceNode from '../nodes/stringProcess/SliceNode.vue'
import ReplaceNode from '../nodes/stringProcess/ReplaceNode.vue'
import LowerOrUpperNode from '../nodes/stringProcess/LowerOrUpperNode.vue'
import ConcatNode from '../nodes/stringProcess/ConcatNode.vue'
import BatchStripNode from '../nodes/stringProcess/BatchStripNode.vue'
import BatchConcatNode from '../nodes/stringProcess/BatchConcatNode.vue'
import RegexMatchNode from '../nodes/stringProcess/RegexMatchNode.vue'
import BatchRegexMatchNode from '../nodes/stringProcess/BatchRegexMatchNode.vue'
import RegexExtractNode from '../nodes/stringProcess/RegexExtractNode.vue'
import InsertConstColNode from '../nodes/tableProcess/InsertConstColNode.vue'
import InsertRangeColNode from '../nodes/tableProcess/InsertRangeColNode.vue'
import InsertRandomColNode from '../nodes/tableProcess/InsertRandomColNode.vue'
import FilterNode from '../nodes/tableProcess/FilterNode.vue'
import DropDuplicatesNode from '../nodes/tableProcess/DropDuplicatesNode.vue'
import DropNaNValueNode from '../nodes/tableProcess/DropNaNValueNode.vue'
import FillNaNValueNode from '../nodes/tableProcess/FillNaNValueNode.vue'
import SortNode from '../nodes/tableProcess/SortNode.vue'
import UploadNode from '../nodes/file/UploadNode.vue'
import TableFromFileNode from '../nodes/file/TableFromFileNode.vue'
import { initVueFlowProject } from '@/utils/projectConvert'
import type { BaseNode } from '@/types/nodeTypes'
import { nodeCategoryColor } from '@/types/nodeTypes'
import { useRoute } from 'vue-router'


const resultStore = useResultStore()
const modalStore = useModalStore()
const graphStore = useGraphStore()

const {params: {projectId}} = useRoute()
const { onNodeClick, findNode, onConnect, onNodesInitialized, fitView, onNodeDragStop, addEdges, getNodes, onPaneClick, screenToFlowCoordinate } = useVueFlow('main')
const shouldWatch = ref(false)
const nodeFirstInit = ref(true)
const listenNodePosition = ref(true)
const intervalId = setInterval(() => {
  listenNodePosition.value = true
}, 30000)
const nodes = computed(() => graphStore.project.workflow.nodes)
const edges = computed(() => graphStore.project.workflow.edges)
const mousePosition = ref({x: 0, y: 0})


onUnmounted(() => {
  clearInterval(intervalId)
  window.removeEventListener('keydown', handleKeyDown)
  window.removeEventListener('mousemove', handleMouseMove)
})

onMounted(async () => {
  try {
    const p = await getProjectFromServer(Number(projectId))
    initVueFlowProject(p, graphStore.project)
    await nextTick()  //  waiting for node initialization
    if(nodes.value.length === 0) {
      nodeFirstInit.value = false
    }
    shouldWatch.value = true
  }catch(err) {
    console.error('init error:', err)
  }
  window.addEventListener('keydown', handleKeyDown)
  window.addEventListener('mousemove', handleMouseMove)
})

onNodesInitialized(() => {
  if(nodeFirstInit.value) {
    nodeFirstInit.value = false
    nextTick(() => {
      fitView({
        padding: 0.1,
        maxZoom: 1,
      })
    })
  } // fitView when first loading nodes
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
    source: connection.source,
    sourceHandle: connection.sourceHandle,
    target: connection.target,
    targetHandle: connection.targetHandle,
    type: "NodePyEdge"
  }
  addEdges(addedEdge)
})

// 监听当前节点的数据变化
watch(() => graphStore.currentNode?.data, (newData, oldData) => {
  if (graphStore.currentNode && newData?.data_out !== undefined) {
    // 当节点数据发生变化时，更新currentTypeDataID
    const dataOut = newData.data_out;
    const dataOutDict = resultStore.convertDataOutToDict(dataOut);
    resultStore.currentTypeDataID = dataOutDict;
  }
  else{
    resultStore.currentTypeDataID = resultStore.default_typedataid
  }
}, { deep: true });

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
  graphStore.currentNode = findNode(event.node.id)

  getNodes.value.forEach((n) => {
    if(n.data.dbclicked) {
      n.data.dbclicked = false
    }
  })  //  reset dbclicked so that only one node can be dbclicked

  if(graphStore.currentNode) {
    graphStore.currentNode.data.dbclicked = true
  } //  双击状态更新

  if(modalStore.findModal('result')===undefined){
    resultStore.createResultModal()
    modalStore.activateModal('result')
  }
  else{
    modalStore.activateModal('result')
  }

  if(graphStore.currentNode?.data?.data_out===undefined){
    resultStore.currentInfo = graphStore.currentNode?.data.param
    resultStore.currentResult = resultStore.default_dataview
    resultStore.currentTypeDataID = resultStore.default_typedataid
  }
  else if (graphStore.currentNode?.data?.data_out !== undefined) {
    // 获取第一个包含data_id的子对象
    const dataOut = graphStore.currentNode.data.data_out;
    const dataOutDict = resultStore.convertDataOutToDict(dataOut)
    resultStore.currentTypeDataID = dataOutDict
    console.log("@@@@@currentTypeDataID",resultStore.currentTypeDataID)
    
    // 只需要设置currentTypeDataID，Result.vue中的watcher会自动处理结果获取
    // 不需要在这里手动调用getResultCacheContent
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
    case 'StringNode':
    case 'BoolNode':
    case 'TableNode':
    case 'RandomNode':
    case 'RangeNode':
    case 'DateTimeNode':
    case 'KlineNode':
      return nodeCategoryColor.input
    case 'NumberBinOpNode':
    case 'NumberUnaryOpNode':
    case 'PrimitiveCompareNode':
    case 'BoolBinOpNode':
    case 'BoolUnaryOpNode':
    case 'ColWithNumberBinOpNode':
    case 'ColWithBoolBinOpNode':
    case 'NumberColUnaryOpNode':
    case 'BoolColUnaryOpNode':
    case 'NumberColWithColBinOpNode':
    case 'BoolColWithColBinOpNode':
    case 'ColCompareNode':
    case 'ToStringNode':
    case 'ToIntNode':
    case 'ToFloatNode':
    case 'ToBoolNode':
      return nodeCategoryColor.compute
    case 'PlotNode':
    case 'AdvancePlotNode':
    case 'WordcloudNode':
      return nodeCategoryColor.visualize
    case 'StripNode':
    case 'SliceNode':
    case 'ReplaceNode':
    case 'LowerOrUpperNode':
    case 'ConcatNode':
    case 'BatchStripNode':
    case 'BatchConcatNode':
    case 'RegexMatchNode':
    case 'BatchRegexMatchNode':
    case 'RegexExtractNode':
      return nodeCategoryColor.str
    case 'InsertConstColNode':
    case 'InsertRangeColNode':
    case 'InsertRandomColNode':
    case 'FilterNode':
    case 'DropDuplicatesNode':
    case 'DropNaNValueNode':
    case 'FillNaNValueNode':
    case 'SortNode':
      return nodeCategoryColor.table
    case 'UploadNode':
    case 'TableFromFileNode':
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

const handleKeyDown = (e: KeyboardEvent) => {
  if(e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement) return // ignore input and textarea
  if((e.ctrlKey || e.metaKey) && e.key === 'c') {
    e.preventDefault()
    graphStore.copySelectedNodes()
  }
  if ((e.ctrlKey || e.metaKey) && e.key === 'v') {
    e.preventDefault()
    graphStore.pasteNodes(mousePosition.value)
  }
}

const handleMouseMove = (e: MouseEvent) => {
  mousePosition.value = screenToFlowCoordinate({
    x: e.clientX,
    y: e.clientY
  })
}

const editableStyle = computed(() => graphStore.project.editable ? 'auto' : 'none')

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
      :nodes-draggable="graphStore.project.editable"
      :nodes-connectable="graphStore.project.editable"
      :edges-updatable="graphStore.project.editable"
      :delete-key-code="graphStore.project.editable ? ['Backspace', 'Delete'] : null"
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

        <template #node-TableFromFileNode="TableFromFileNodeProps">
          <TableFromFileNode v-bind="TableFromFileNodeProps"/>
        </template>

        <template #node-RandomNode="RandomNodeProps">
          <RandomNode v-bind="RandomNodeProps"/>
        </template>

        <template #node-RangeNode="RangeNodeProps">
          <RangeNode v-bind="RangeNodeProps"/>
        </template>

        <template #node-DateTimeNode="DateTimeNodeProps">
          <DateTimeNode v-bind="DateTimeNodeProps"/>
        </template>

        <template #node-KlineNode="KlineNodeProps">
          <KlineNode v-bind="KlineNodeProps"/>
        </template>

        <template #node-NumberBinOpNode="NumberBinOpNodeProps">
          <NumberBinOpNode v-bind="NumberBinOpNodeProps"/>
        </template>

        <template #node-NumberUnaryOpNode="NumberUnaryOpNodeProps">
          <NumberUnaryOpNode v-bind="NumberUnaryOpNodeProps"/>
        </template>

        <template #node-PrimitiveCompareNode="PrimitiveCompareNodeProps">
          <PrimitiveCompareNode v-bind="PrimitiveCompareNodeProps"/>
        </template>

        <template #node-BoolBinOpNode="BoolBinOpNodeProps">
          <BoolBinOpNode v-bind="BoolBinOpNodeProps"/>
        </template>

        <template #node-BoolUnaryOpNode="BoolUnaryOpNodeProps">
          <BoolUnaryOpNode v-bind="BoolUnaryOpNodeProps"/>
        </template>

        <template #node-ColWithNumberBinOpNode="ColWithNumberBinOpNodeProps">
          <ColWithNumberBinOpNode v-bind="ColWithNumberBinOpNodeProps"/>
        </template>

        <template #node-ColWithBoolBinOpNode="ColWithBoolBinOpNodeProps">
          <ColWithBoolBinOpNode v-bind="ColWithBoolBinOpNodeProps"/>
        </template>

        <template #node-NumberColUnaryOpNode="NumberColUnaryOpNodeProps">
          <NumberColUnaryOpNode v-bind="NumberColUnaryOpNodeProps"/>
        </template>

        <template #node-BoolColUnaryOpNode="BoolColUnaryOpNodeProps">
          <BoolColUnaryOpNode v-bind="BoolColUnaryOpNodeProps"/>
        </template>

        <template #node-NumberColWithColBinOpNode="NumberColWithColBinOpNodeProps">
          <NumberColWithColBinOpNode v-bind="NumberColWithColBinOpNodeProps"/>
        </template>

        <template #node-BoolColWithColBinOpNode="BoolColWithColBinOpNodeProps">
          <BoolColWithColBinOpNode v-bind="BoolColWithColBinOpNodeProps"/>
        </template>

        <template #node-ColCompareNode="ColCompareNodeProps">
          <ColCompareNode v-bind="ColCompareNodeProps"/>
        </template>

        <template #node-ToStringNode="ToStringNodeProps">
          <ToStringNode v-bind="ToStringNodeProps"/>
        </template>

        <template #node-ToIntNode="ToIntNodeProps">
          <ToIntNode v-bind="ToIntNodeProps"/>
        </template>

        <template #node-ToFloatNode="ToFloatNodeProps">
          <ToFloatNode v-bind="ToFloatNodeProps"/>
        </template>

        <template #node-ToBoolNode="ToBoolNodeProps">
          <ToBoolNode v-bind="ToBoolNodeProps"/>
        </template>

        <template #node-PlotNode="PlotNodeProps">
          <PlotNode v-bind="PlotNodeProps" />
        </template>

        <template #node-AdvancePlotNode="AdvancePlotNodeProps">
          <AdvancePlotNode v-bind="AdvancePlotNodeProps" />
        </template>

        <template #node-WordcloudNode="WordcloudNodeProps">
          <WordcloudNode v-bind="WordcloudNodeProps" />
        </template>

        <template #node-StripNode="StripNodeProps">
          <StripNode v-bind="StripNodeProps"/>
        </template>

        <template #node-SliceNode="SliceNodeProps">
          <SliceNode v-bind="SliceNodeProps"/>
        </template>

        <template #node-ReplaceNode="ReplaceNodeProps">
          <ReplaceNode v-bind="ReplaceNodeProps"/>
        </template>

        <template #node-LowerOrUpperNode="LowerOrUpperNodeProps">
          <LowerOrUpperNode v-bind="LowerOrUpperNodeProps"/>
        </template>

        <template #node-ConcatNode="ConcatNodeProps">
          <ConcatNode v-bind="ConcatNodeProps"/>
        </template>

        <template #node-BatchStripNode="BatchStripNodeProps">
          <BatchStripNode v-bind="BatchStripNodeProps"/>
        </template>

        <template #node-BatchConcatNode="BatchConcatNodeProps">
          <BatchConcatNode v-bind="BatchConcatNodeProps"/>
        </template>

        <template #node-RegexMatchNode="RegexMatchNodeProps">
          <RegexMatchNode v-bind="RegexMatchNodeProps"/>
        </template>

        <template #node-BatchRegexMatchNode="BatchRegexMatchNodeProps">
          <BatchRegexMatchNode v-bind="BatchRegexMatchNodeProps"/>
        </template>

        <template #node-RegexExtractNode="RegexExtractNodeProps">
          <RegexExtractNode v-bind="RegexExtractNodeProps"/>
        </template>

        <template #node-InsertConstColNode="InsertConstColNodeProps">
          <InsertConstColNode v-bind="InsertConstColNodeProps"/>
        </template>

        <template #node-InsertRangeColNode="InsertRangeColNodeProps">
          <InsertRangeColNode v-bind="InsertRangeColNodeProps"/>
        </template>

        <template #node-InsertRandomColNode="InsertRandomColNodeProps">
          <InsertRandomColNode v-bind="InsertRandomColNodeProps"/>
        </template>

        <template #node-FilterNode="FilterNodeProps">
          <FilterNode v-bind="FilterNodeProps"/>
        </template>

        <template #node-DropDuplicatesNode="DropDuplicatesNodeProps">
          <DropDuplicatesNode v-bind="DropDuplicatesNodeProps"/>
        </template>

        <template #node-DropNaNValueNode="DropNaNValueNodeProps">
          <DropNaNValueNode v-bind="DropNaNValueNodeProps"/>
        </template>

        <template #node-FillNaNValueNode="FillNaNValueNodeProps">
          <FillNaNValueNode v-bind="FillNaNValueNodeProps"/>
        </template>

        <template #node-SortNode="SortNodeProps">
          <SortNode v-bind="SortNodeProps"/>
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

.vue-flow__node {
  .nodes-style {
    pointer-events: v-bind(editableStyle);
  }
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
} //  vue-flow__background must be written here since @use must be written here

.graphinfo {
  pointer-events: none !important;
  user-select: none;
}

</style>
