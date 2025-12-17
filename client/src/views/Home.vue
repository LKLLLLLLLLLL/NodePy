<script lang="ts" setup>
import { useLoginStore } from '@/stores/loginStore';
import { usePageStore } from '@/stores/pageStore';
import { onMounted, computed, ref, markRaw, watch, onUnmounted, nextTick } from 'vue';
import NodePyEdge from '@/components/NodePyEdge.vue';
import NodePyConnectionLine from '@/components/NodePyConnectionLine.vue';
import { useRouter } from 'vue-router';
import { VueFlow } from '@vue-flow/core'
import { useVueFlow } from '@vue-flow/core'
import { Background } from '@vue-flow/background'
import '@vue-flow/core/dist/style.css'
import '@vue-flow/core/dist/theme-default.css'
import AuthenticatedServiceFactory from '@/utils/AuthenticatedServiceFactory';
import type { ExploreListItem } from '@/utils/api';
import ExampleDemoFrame from './ExampleView/ExampleDemoFrame.vue'

import ConstNode from '@/components/nodes/input/ConstNode.vue'
import NumberBinOpNode from '@/components/nodes/compute/NumberBinOpNode.vue'
import DateTimeNode from '@/components/nodes/input/DateTimeNode.vue'
import DatetimeComputeNode from '@/components/nodes/datetimeProcess/DatetimeComputeNode.vue'
import KlineNode from '@/components/nodes/input/KlineNode.vue'
import QuickPlotNode from '@/components/nodes/visualize/QuickPlotNode.vue'
import StatsNode from '@/components/nodes/analysis/StatsNode.vue'
import ToFloatNode from '@/components/nodes/compute/ToFloatNode.vue'
import ToIntNode from '@/components/nodes/compute/ToIntNode.vue'
import LinearRegressionNode from '@/components/nodes/machineLearning/LinearRegressionNode.vue'
import RegressionScoreNode from '@/components/nodes/machineLearning/RegressionScoreNode.vue'
import FilterNode from '@/components/nodes/tableProcess/FilterNode.vue'
import UploadNode from '@/components/nodes/file/UploadNode.vue'
import TableFromFileNode from '@/components/nodes/file/TableFromFileNode.vue'
import DualAxisPlotNode from '@/components/nodes/visualize/DualAxisPlotNode.vue'
import MergeNode from '@/components/nodes/tableProcess/MergeNode.vue'

const pageStore = usePageStore()
const loginStore = useLoginStore()
const router = useRouter()

const nodeTypes = {
  ConstNode: markRaw(ConstNode),
  NumberBinOpNode: markRaw(NumberBinOpNode),
  DateTimeNode: markRaw(DateTimeNode),
  DatetimeComputeNode: markRaw(DatetimeComputeNode),
  KlineNode: markRaw(KlineNode),
  QuickPlotNode: markRaw(QuickPlotNode),
  StatsNode: markRaw(StatsNode),
  ToFloatNode: markRaw(ToFloatNode),
  ToIntNode: markRaw(ToIntNode),
  LinearRegressionNode: markRaw(LinearRegressionNode),
  RegressionScoreNode: markRaw(RegressionScoreNode),
  FilterNode: markRaw(FilterNode),
  UploadNode: markRaw(UploadNode),
  TableFromFileNode: markRaw(TableFromFileNode),
  DualAxisPlotNode: markRaw(DualAxisPlotNode),
  MergeNode: markRaw(MergeNode)
}

const nodes1 = ref([
  {
    id: 'DateTimeNode_1',
    type: 'DateTimeNode',
    position: { x: 20, y: 30 },
    data: { param: { value: '', isNow: true }, dbclicked: false, runningtime: 0.0893150000820242 }
  },
  {
    id: 'DateTimeNode_2',
    type: 'DateTimeNode',
    position: { x: 350, y: 400 },
    data: { param: { value: '', isNow: false }, dbclicked: false, runningtime: 0.04911700000320707 }
  },
  {
    id: 'ConstNode_1',
    type: 'ConstNode',
    position: { x: 20, y: 200 },
    data: { param: { value: 0, data_type: 'int' }, dbclicked: false, runningtime: 0.07266500006153365 }
  },
  {
    id: 'DatetimeComputeNode_1',
    type: 'DatetimeComputeNode',
    position: { x: 350, y: 100 },
    data: { param: {}, dbclicked: false, runningtime: 0.15581699994982046 }
  },
  {
    id: 'KlineNode_1',
    type: 'KlineNode',
    position: { x: 680, y: 150 },
    data: { param: { data_type: 'stock', symbol: '', start_time: null, end_time: null, interval: '1m' }, dbclicked: false, runningtime: 710.2902609999546 }
  }
])

const nodes2 = ref([
  {
    id: 'StatsNode_1',
    type: 'StatsNode',
    position: { x: 20, y: 50 },
    data: { param: {}, dbclicked: false, runningtime: 0.2 }
  },
  {
    id: 'ConstNode_3',
    type: 'ConstNode',
    position: { x: 290, y: 300 },
    data: { param: { value: 10, data_type: 'int' }, dbclicked: false, runningtime: 0.05348499962565256 }
  },
  {
    id: 'NumberBinOpNode_1',
    type: 'NumberBinOpNode',
    position: { x: 560, y: 201 },
    data: { param: { op: 'DIV' }, dbclicked: false, runningtime: 0.0}
  },
  {
    id: 'ToFloatNode_1',
    type: 'ToFloatNode',
    position: { x: 290, y: 170 },
    data: { param: {}, dbclicked: false, runningtime: 0.0 }
  },
  {
    id: 'ToIntNode_1',
    type: 'ToIntNode',
    position: { x: 830, y: 321 },
    data: { param: {}, dbclicked: false, runningtime: 0.0 }
  }
])

const nodes3 = ref([
  {
    id: 'LinearRegressionNode_1',
    type: 'LinearRegressionNode',
    position: { x: 825, y: 300 },
    data: { param: {feature_cols: ['Open', 'Close'],target_col: "Volume"}, dbclicked: false, runningtime: 53.1 }
  },
  {
    id: 'UploadNode_1',
    type: 'UploadNode',
    position: { x: 0, y: 50 },
    data: { param: {}, dbclicked: false, runningtime: 0.05667999994329875 }
  },
  {
    id: 'RegressionScoreNode_1',
    type: 'RegressionScoreNode',
    position: { x: 1100, y: 138 },
    data: { param: {}, dbclicked: false, runningtime: 17.8 }
  },
  {
    id: 'FilterNode_1',
    type: 'FilterNode',
    position: { x: 550, y: 50 },
    data: { param: {}, dbclicked: false, runningtime: 0.5 }
  },
  {
    id: 'TableFromFileNode_1',
    type: 'TableFromFileNode',
    position: { x: 275, y: 75 },
    data: { param: {}, dbclicked: false, runningtime: 19.82704400052171 }
  }
])

const nodes4 = ref([
  {
    id: 'DualAxisPlotNode_1',
    type: 'DualAxisPlotNode',
    position: { x: 950, y: 500 },
    data: { param: {}, dbclicked: false, runningtime: 471.34476699920924 }
  },
  {
    id: 'KlineNode_1',
    type: 'KlineNode',
    position: { x: 50, y: 50 },
    data: { param: { data_type: 'stock', symbol: 'AAPL', start_time: '2023-01-01', end_time: '2023-12-31', interval: '1d' }, dbclicked: false, runningtime: 329.65625900033046 }
  },
  {
    id: 'KlineNode_2',
    type: 'KlineNode',
    position: { x: 50, y: 500 },
    data: { param: { data_type: 'stock', symbol: 'GOOGL', start_time: '2023-01-01', end_time: '2023-12-31', interval: '1d' }, dbclicked: false, runningtime: 176.7138300001534 }
  },
  {
    id: 'MergeNode_1',
    type: 'MergeNode',
    position: { x: 500, y: 400 },
    data: { param: { join_type: 'inner', left_on: [], right_on: [] }, dbclicked: false, runningtime: 1.6944159997365205 }
  },
  {
    id: 'QuickPlotNode_1',
    type: 'QuickPlotNode',
    position: { x: 500, y: 600},
    data: { param: {plot_type: ['line'],title: null,x_col: "Open Time",y_col: ['Open']}, dbclicked: false, runningtime: 435.82994200005487 }
  }
])

const edges1 = ref([
  { id: 'vueflow__edge-DateTimeNode_1datetime-DatetimeComputeNode_1datetime', source: 'DateTimeNode_1', target: 'DatetimeComputeNode_1', sourceHandle: 'datetime', targetHandle: 'datetime', animated: true , type: 'NodePyEdge'},
  { id: 'vueflow__edge-ConstNode_1const-DatetimeComputeNode_1value', source: 'ConstNode_1', target: 'DatetimeComputeNode_1', sourceHandle: 'const', targetHandle: 'value', animated: true , type: 'NodePyEdge'},
  { id: 'vueflow__edge-DatetimeComputeNode_1result-KlineNode_1start_time', source: 'DatetimeComputeNode_1', target: 'KlineNode_1', sourceHandle: 'result', targetHandle: 'start_time', animated: true , type: 'NodePyEdge'},
  { id: 'vueflow__edge-DateTimeNode_2datetime-KlineNode_1end_time', source: 'DateTimeNode_2', target: 'KlineNode_1', sourceHandle: 'datetime', targetHandle: 'end_time', animated: true , type: 'NodePyEdge'}
])

const edges2 = ref([
  { id: 'vueflow__edge-ConstNode_3const-NumberBinOpNode_1y', source: 'ConstNode_3', target: 'NumberBinOpNode_1', sourceHandle: 'const', targetHandle: 'y', animated: true, type: 'NodePyEdge' },
  { id: 'vueflow__edge-StatsNode_1count-ToFloatNode_1input', source: 'StatsNode_1', target: 'ToFloatNode_1', sourceHandle: 'count', targetHandle: 'input', animated: true, type: 'NodePyEdge' },
  { id: 'vueflow__edge-ToFloatNode_1output-NumberBinOpNode_1x', source: 'ToFloatNode_1', target: 'NumberBinOpNode_1', sourceHandle: 'output', targetHandle: 'x', animated: true, type: 'NodePyEdge' },
  { id: 'vueflow__edge-NumberBinOpNode_1result-ToIntNode_1input', source: 'NumberBinOpNode_1', target: 'ToIntNode_1', sourceHandle: 'result', targetHandle: 'input', animated: true, type: 'NodePyEdge' }
])

const edges3 = ref([
  { id: 'vueflow__edge-LinearRegressionNode_1model-RegressionScoreNode_1model', source: 'LinearRegressionNode_1', target: 'RegressionScoreNode_1', sourceHandle: 'model', targetHandle: 'model', animated: true, type: 'NodePyEdge' },
  { id: 'vueflow__edge-FilterNode_1true_table-RegressionScoreNode_1table', source: 'FilterNode_1', target: 'RegressionScoreNode_1', sourceHandle: 'true_table', targetHandle: 'table', animated: true, type: 'NodePyEdge' },
  { id: 'vueflow__edge-FilterNode_1false_table-LinearRegressionNode_1table', source: 'FilterNode_1', target: 'LinearRegressionNode_1', sourceHandle: 'false_table', targetHandle: 'table', animated: true, type: 'NodePyEdge' },
  { id: 'vueflow__edge-UploadNode_1file-TableFromFileNode_1file', source: 'UploadNode_1', target: 'TableFromFileNode_1', sourceHandle: 'file', targetHandle: 'file', animated: true, type: 'NodePyEdge' },
  { id: 'vueflow__edge-TableFromFileNode_1table-FilterNode_1table', source: 'TableFromFileNode_1', target: 'FilterNode_1', sourceHandle: 'table', targetHandle: 'table', animated: true, type: 'NodePyEdge' }
])

const edges4 = ref([
  { id: 'vueflow__edge-KlineNode_1kline_data-MergeNode_1table_1', source: 'KlineNode_1', target: 'MergeNode_1', sourceHandle: 'kline_data', targetHandle: 'table_1', animated: true, type: 'NodePyEdge' },
  { id: 'vueflow__edge-KlineNode_2kline_data-MergeNode_1table_2', source: 'KlineNode_2', target: 'MergeNode_1', sourceHandle: 'kline_data', targetHandle: 'table_2', animated: true, type: 'NodePyEdge' },
  { id: 'vueflow__edge-MergeNode_1merged_table-DualAxisPlotNode_1input', source: 'MergeNode_1', target: 'DualAxisPlotNode_1', sourceHandle: 'merged_table', targetHandle: 'input', animated: true, type: 'NodePyEdge' },
  { id: 'vueflow__edge-KlineNode_2kline_data-QuickPlotNode_1input', source: 'KlineNode_2', target: 'QuickPlotNode_1', sourceHandle: 'kline_data', targetHandle: 'input', animated: true, type: 'NodePyEdge' }
])

// 当前选中的示例索引
const currentExampleIndex = ref(0)

// 自动轮播定时器
const carouselTimer = ref<NodeJS.Timeout | null>(null)


const currentName = computed(()=>{
  switch(currentExampleIndex.value) {
    case 0: return "DataFetch.nodepy"
    case 1: return "DataProcess.nodepy"
    case 2: return "MachineLearning.nodepy"
    case 3: return "DataVisulization.nodepy"
    default: return "DataFetch.nodepy"
  }
})
// 计算当前应该显示的节点和边
const currentNodes = computed(() => {
  switch(currentExampleIndex.value) {
    case 0: return nodes1.value
    case 1: return nodes2.value
    case 2: return nodes3.value
    case 3: return nodes4.value
    default: return nodes1.value
  }
})

const currentEdges = computed(() => {
  switch(currentExampleIndex.value) {
    case 0: return edges1.value
    case 1: return edges2.value
    case 2: return edges3.value
    case 3: return edges4.value
    default: return edges1.value
  }
})

// 特性列表
const features = [
  {
    icon: 'mdi-graph',
    title: '严格类型系统',
    description: '支持 Int, Float, Bool, String, Table, File, Datetime 七大类型，确保数据流转的准确性。',
    nodeType: 'input' // 对应 node.scss 中的颜色分类
  },
  {
    icon: 'mdi-table-large',
    title: 'Pandas 表格处理',
    description: '内置强大的表格处理能力，支持过滤、去重、缺失值处理、列运算等复杂操作。',
    nodeType: 'tableProcess'
  },
  {
    icon: 'mdi-chart-scatter-plot',
    title: '专业可视化',
    description: '支持散点图、折线图、柱状图、面积图、K线图等多种专业金融图表绘制。',
    nodeType: 'visualize'
  },
  {
    icon: 'mdi-function-variant',
    title: 'Python 驱动',
    description: '底层完全由 Python 驱动，兼容 Python 生态，计算结果精准可靠。',
    nodeType: 'compute'
  }
]

// 实例项目列表
const examples = ref<ExploreListItem[]>([])

// 开始自动轮播
const startCarousel = () => {
  if (carouselTimer.value) {
    clearInterval(carouselTimer.value)
  }
  
  carouselTimer.value = setInterval(() => {
    currentExampleIndex.value = (currentExampleIndex.value + 1) % 4
  }, 3000) // 每3秒切换一次
}

// 停止自动轮播
const stopCarousel = () => {
  if (carouselTimer.value) {
    clearInterval(carouselTimer.value)
    carouselTimer.value = null
  }
}

// 手动切换示例
const switchExample = (index: number) => {
  currentExampleIndex.value = index
}

onMounted(async () => {
  loginStore.checkAuthStatus()
  pageStore.setCurrentPage('Home')
  try {
    const authService = AuthenticatedServiceFactory.getService()
    const res = await authService.getExploreProjectsApiExploreExploreProjectsGet()
    examples.value = res.projects
  } catch (e) {
    console.error('Failed to fetch examples:', e)
  }
  
  // 启动自动轮播
  startCarousel()
})

const { onNodeClick, findNode, onConnect, onNodesInitialized, fitView, onNodeDragStop, addEdges, getNodes, onPaneClick, screenToFlowCoordinate } = useVueFlow('main')

onNodesInitialized(() => {
  nextTick(() => {
    fitView({
      padding: 0.1,
      maxZoom: 0.65,
    })
  })
})

// 组件卸载时清理定时器
onUnmounted(() => {
  stopCarousel()
})

function jumpToLogin() {
  router.push({
    name: 'login'
  })
}

function jumpToProject() {
  router.push({
    name: 'project'
  })
}

// 用户是否已登录
const isLoggedIn = computed(() => loginStore.loggedIn)

// 跳转到GitHub
function jumpToGithub() {
  window.open('https://github.com/LKLLLLLLLLLL/NodePy', '_blank')
}
</script>

<template>
  <div class="home-container">
    <!-- 背景装饰元素 -->
    <div class="background-elements">
      <div class="bg-circle circle-1"></div>
      <div class="bg-circle circle-2"></div>
      <div class="bg-circle circle-3"></div>
    </div>

    <!-- 主内容区 -->
    <div class="home-content">

      <!-- 页面内容 -->
      <div class="scroll-content">
        <!-- 第一部分：Hero Section (编辑器与节点展示) -->
        <div class="section hero-section">
          <div class="hero-content">
            <h1 class="hero-title">
              可视化金融数据分析<br>
              <span class="highlight">构建你的量化工作流</span>
            </h1>
            <p class="hero-subtitle">
              NodePy 让数据分析像搭积木一样简单。无需编写复杂代码，通过拖拽节点即可完成从数据获取、清洗、计算到可视化的全过程。
            </p>

            <div class="hero-actions">
              <button  @click="isLoggedIn ? jumpToProject() : jumpToLogin()" class="cta-button">
                <span class="mdi mdi-rocket-launch"></span>
                立即开始
              </button>
              <button  @click="jumpToGithub" class="secondary-button">
                <span class="mdi mdi-github"></span>
                GitHub
              </button>
            </div>
          </div>

          <div class="hero-visual">
            <!-- 模拟的编辑器界面 -->
            <div class="editor-mockup">
              <div class="mockup-header">
                <div class="dots">
                  <span></span><span></span><span></span>
                </div>
                <div class="title">{{currentName}}</div>
              </div>
              <div class="mockup-body">
                <VueFlow
                  :nodes="currentNodes"
                  :edges="currentEdges"
                  :node-types="nodeTypes"
                  :default-viewport="{ zoom: 0.5 }"
                  :min-zoom="0.5"
                  :max-zoom="2"
                  fit-view-on-init
                  class="demo-flow"
                  id="main"
                >
                  <Background color="rgba(50, 50, 50, 0.05)" variant="dots" :gap="20" :size="4"/>

                  <template #edge-NodePyEdge="NodePyEdgeProps">
                    <NodePyEdge v-bind="NodePyEdgeProps"/>
                  </template>

                  <template #connection-line="ConnectionLineProps">
                    <NodePyConnectionLine v-bind="ConnectionLineProps"/>
                  </template>
                </VueFlow>
                <!-- 轮播指示器 -->
                <div class="carousel-indicators">
                  <span 
                    v-for="(_, index) in 4" 
                    :key="index"
                    class="indicator-dot"
                    :class="{ active: currentExampleIndex === index }"
                    @click="switchExample(index)"
                  ></span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 第二部分：核心优势 (Features) -->
        <div class="section features-section">
          <div class="section-header">
            <h2 class="section-title">核心优势</h2>
            <p class="section-subtitle">专为金融数据分析设计的节点式编程环境</p>
          </div>

          <div class="features-grid">
            <div
              v-for="(feature, index) in features"
              :key="index"
              class="feature-card"
              :class="`type-${feature.nodeType}`"
            >
              <div class="feature-icon-wrapper">
                <div class="feature-icon">
                  <span class="mdi" :class="feature.icon"></span>
                </div>
              </div>
              <h3 class="feature-title">{{ feature.title }}</h3>
              <p class="feature-description">{{ feature.description }}</p>
            </div>
          </div>
        </div>

        <!-- 第三部分：实例项目 (Examples) -->
        <div class="section examples-section">
          <div class="section-header">
            <h2 class="section-title">实例项目</h2>
            <p class="section-subtitle">从简单的图表绘制到复杂的策略回测，NodePy 都能轻松搞定</p>
          </div>

          <div class="examples-grid">
            <ExampleDemoFrame
                v-for="example in examples"
                :key="example.project_id"
                :item="example"
            ></ExampleDemoFrame>
          </div>
        </div>

        <!-- 页脚 -->
        <div class="section footer-section">
          <div class="cta-box">
            <h2>准备好开始了吗？</h2>
            <p>立即注册，开启您的可视化金融分析之旅</p>
            <button  @click="isLoggedIn ? jumpToProject() : jumpToLogin()" class="cta-btn">
              {{ isLoggedIn ? '进入工作台' : '免费注册' }}
            </button>
          </div>

          <div class="footer-bottom">
            <div class="footer-logo">
              <h3>NodePy</h3>
            </div>
            <div class="footer-copyright">
              <p>© 2025 NodePy Team. All rights reserved.</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
@use '@/common/global.scss' as *;
@use '@/common/node.scss' as *;
@use 'sass:color' as color;

// 覆盖 node.scss 中的一些样式以适应展示
.nodes-style {
  position: absolute;
  box-shadow: 0 4px 15px rgba(0,0,0,0.1);
  transition: transform 0.3s ease;

  &:hover {
    transform: scale(1.05);
    z-index: 10;
  }
}

.node-body {
  padding: 10px;
  min-height: 40px;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.home-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  position: relative;
  width: 100%;
  min-height: 0;
  overflow-x: hidden;
  background-color: $background-color;
}

.background-elements {
  position: absolute;
  width: 100%;
  height: 100%;
  z-index: 0;
  overflow: hidden;
  pointer-events: none;

  .bg-circle {
    position: absolute;
    border-radius: 50%;
    filter: blur(60px);
    opacity: 0.6;
  }

  .circle-1 {
    width: 400px;
    height: 400px;
    top: -100px;
    right: -100px;
    background: rgba($stress-color, 0.15);
  }

  .circle-2 {
    width: 300px;
    height: 300px;
    bottom: 100px;
    left: -50px;
    background: rgba($compute-node-color, 0.15);
  }

  .circle-3 {
    width: 200px;
    height: 200px;
    top: 30%;
    left: 20%;
    background: rgba($visualize-node-color, 0.1);
  }
}

.home-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
  z-index: 1;
  position: relative;
  overflow-y: auto;
}

.home-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 40px;
  max-width: 1400px;
  margin: 0 auto;
  width: 100%;
  box-sizing: border-box;

  .logo-container {
    .logo-text {
      h1 {
        margin: 0;
        font-size: 26px;
        font-weight: 800;
        color: #333;
        letter-spacing: -0.5px;
      }
      .logo-tagline {
        font-size: 13px;
        color: #666;
        font-weight: 500;
      }
    }
  }

  .login-btn {
    font-weight: 600;
    border-radius: 8px;
    padding: 10px 24px;
  }
}

.section {
  width: 100%;
  padding: 80px 20px 20px 40px;
  box-sizing: border-box;
  max-width: 1500px;
  margin: 0 auto;

  @media (max-width: 768px) {
    padding: 50px 20px;
  }
}

.section-header {
  text-align: center;
  margin-bottom: 60px;

  .section-title {
    font-size: 32px;
    font-weight: 800;
    color: #333;
    margin-bottom: 16px;
  }

  .section-subtitle {
    font-size: 18px;
    color: #666;
  }
}

// Hero Section
.hero-section {
  display: flex;
  align-items: center;
  justify-content: space-between;
  min-height: 70vh;
  gap: 60px;

  @media (max-width: 992px) {
    flex-direction: column;
    text-align: center;
    gap: 40px;
  }

  .hero-content {
    flex: 1;
    max-width: 550px;

    .hero-title {
      font-size: 48px;
      font-weight: 900;
      line-height: 1.2;
      color: #1a1a1a;
      margin-bottom: 24px;

      .highlight {
        color: $stress-color;
      }
    }

    .hero-subtitle {
      font-size: 18px;
      line-height: 1.6;
      color: #555;
      margin-bottom: 40px;
    }

    .hero-actions {
      display: flex;
      justify-content: space-between;

      @media (max-width: 992px) {
        justify-content: center;
      }

      .button {
        border-radius: 8px;
        font-weight: 600;
        padding: 12px 28px;
      }

      .secondary-button{
        @include cancel-button-style;
        width: 200px;
        height: 48px;
        &:hover{
          @include cancel-button-hover-style;
        }
      }

      .cta-button {
        @include confirm-button-style;
        width: 200px;
        height: 48px;
        background-color: $stress-color;
        border-color: $stress-color;

        &:hover {
          // transform: translateY(-2px);
          @include confirm-button-hover-style;
        }
      }
    }
  }

  .hero-visual {
    flex: 1.9;
    display: flex;
    justify-content: center;

    .editor-mockup {
      width: 100%;
      max-width: 900px;
      height: 620px;
      background: white;
      border-radius: 12px;
      box-shadow: 0 20px 60px rgba(0,0,0,0.12);
      border: 1px solid rgba(0,0,0,0.05);
      display: flex;
      flex-direction: column;
      overflow: hidden;
      transition: transform 0.5s ease;
      position: relative;
      margin-top: 20px;

      .mockup-header {
        height: 36px;
        background: #f5f5f5;
        border-bottom: 1px solid #e0e0e0;
        display: flex;
        align-items: center;
        padding: 0 16px;

        .dots {
          display: flex;
          gap: 6px;

          span {
            width: 10px;
            height: 10px;
            border-radius: 50%;
            background: #ddd;
            &:nth-child(1) { background: #ff5f56; }
            &:nth-child(2) { background: #ffbd2e; }
            &:nth-child(3) { background: #27c93f; }
          }
        }

        .title {
          flex: 1;
          text-align: center;
          font-size: 12px;
          font-weight: bold;
          color: #999;
        }
      }

      .mockup-body {
        flex: 1;
        background-color: #fafafa;
        position: relative;
        overflow: hidden;
        
        // 轮播指示器样式
        .carousel-indicators {
          position: absolute;
          bottom: 15px;
          left: 50%;
          transform: translateX(-50%);
          display: flex;
          gap: 10px;
          z-index: 10;
          
          .indicator-dot {
            width: 10px;
            height: 10px;
            border-radius: 50%;
            background-color: #cbd5e1; // 蓝色系浅色
            cursor: pointer;
            transition: all 0.3s ease;
            
            &.active {
              background-color: $stress-color; // 使用项目主色调
              transform: scale(1.2);
            }
            
            &:hover:not(.active) {
              background-color: #94a3b8; // 悬停时加深颜色
            }
          }
        }
      }
    }
  }
}

// Features Section
.features-section {
  .features-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
    gap: 30px;
  }

  .feature-card {
    background: white;
    border-radius: 12px;
    padding: 30px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.04);
    transition: all 0.3s ease;
    border: 1px solid transparent;

    &:hover {
      transform: translateY(-5px);
      box-shadow: 0 10px 30px rgba(0,0,0,0.08);
    }

    .feature-icon-wrapper {
      margin-bottom: 20px;
      .feature-icon {
        width: 50px;
        height: 50px;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;

        .mdi {
          font-size: 24px;
          color: white;
        }
      }
    }

    // 根据类型设置颜色
    &.type-input {
      .feature-icon { background: $input-node-color; }
      &:hover { border-color: rgba($input-node-color, 0.3); }
    }
    &.type-tableProcess {
      .feature-icon { background: $table-node-color; }
      &:hover { border-color: rgba($table-node-color, 0.3); }
    }
    &.type-visualize {
      .feature-icon { background: $visualize-node-color; }
      &:hover { border-color: rgba($visualize-node-color, 0.3); }
    }
    &.type-compute {
      .feature-icon { background: $compute-node-color; }
      &:hover { border-color: rgba($compute-node-color, 0.3); }
    }

    .feature-title {
      font-size: 18px;
      font-weight: 700;
      color: #333;
      margin-bottom: 10px;
    }

    .feature-description {
      font-size: 14px;
      line-height: 1.6;
      color: #666;
    }
  }
}

// Examples Section
.examples-section {
  background: white; // 区分背景
  width: 100%;
  max-width: 100%; // 全宽背景

  .section-header, .examples-grid {
    max-width: 1500px;
    margin: 0 auto;
  }

  .examples-grid {
    display: grid;
    grid-template-rows: repeat(2, auto);
    grid-auto-flow: column;
    grid-auto-columns: 300px; // 固定列宽，确保一致性
    gap: 30px;
    overflow-x: auto;
    overflow-y: hidden;
    padding: 60px;
    justify-content: start; // 从左侧开始

    // 隐藏滚动条但保持功能 (可选)
    &::-webkit-scrollbar {
      height: 8px;
    }
    &::-webkit-scrollbar-track {
      background: #f1f1f1;
      border-radius: 4px;
    }
    &::-webkit-scrollbar-thumb {
      background: #ccc;
      border-radius: 4px;
      &:hover { background: #bbb; }
    }
  }
}

// Footer Section
.footer-section {
  padding-bottom: 40px;

  .cta-box {
    background: linear-gradient(135deg, $stress-color, color.adjust($stress-color, $lightness: 10%));
    border-radius: 20px;
    padding: 60px;
    text-align: center;
    color: white;
    margin-bottom: 60px;
    box-shadow: 0 20px 40px rgba($stress-color, 0.2);

    h2 {
      font-size: 32px;
      font-weight: 800;
      margin-bottom: 16px;
    }

    p {
      font-size: 18px;
      opacity: 0.9;
      margin-bottom: 32px;
    }

    .cta-btn {
      @include cancel-button-style;
      background: white;
      color: $stress-color;
      border: none;
      font-weight: 700;
      padding: 12px 36px;
      height: auto;
      font-size: 16px;

      &:hover {
        // transform: scale(1.05);
        @include cancel-button-hover-style;
      }
    }
  }

  .footer-bottom {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding-top: 30px;
    // border-top: 1px solid #eee;

    .footer-logo {
      h3 {
        font-size: 20px;
        font-weight: 700;
        color: #333;
        margin-bottom: 4px;
      }
      p {
        font-size: 12px;
        color: #999;
      }
    }

    .footer-copyright{
      p {
        font-size: 12px;
        color: #999;
      }
    }
  }
}
</style>