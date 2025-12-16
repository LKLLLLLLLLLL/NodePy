<script lang="ts" setup>
import { useLoginStore } from '@/stores/loginStore';
import { usePageStore } from '@/stores/pageStore';
import { ref, onMounted, computed, onBeforeUnmount } from 'vue';
import { useRouter } from 'vue-router';

const pageStore = usePageStore()
const loginStore = useLoginStore()
const router = useRouter()

// 当前页面索引
const currentPage = ref(0)

// 页面总数
const totalPages = 3

// 特性列表
const features = ref([
  {
    icon: 'mdi-nodejs',
    title: '节点式编程',
    description: '通过可视化界面拖拽节点，轻松构建复杂的数据处理工作流',
    color: '#4CAF50'
  },
  {
    icon: 'mdi-chart-bell-curve',
    title: '金融数据分析',
    description: '专业的金融数据处理、分析和可视化功能，满足专业分析需求',
    color: '#2196F3'
  },
  {
    icon: 'mdi-puzzle',
    title: '丰富的节点库',
    description: '涵盖数据导入、清洗、转换、分析和可视化等丰富节点类型',
    color: '#FF9800'
  },
  {
    icon: 'mdi-code-tags',
    title: 'Python 底层',
    description: '基于Python的强大数据处理能力，支持自定义扩展和脚本',
    color: '#9C27B0'
  },
  {
    icon: 'mdi-graph',
    title: '可视化性能',
    description: '极佳的可视化表现，数据结果直观呈现，操作流畅',
    color: '#F44336'
  },
  {
    icon: 'mdi-account-group',
    title: '易于上手',
    description: '适合新手数据分析，也满足开发者的高级功能设计需求',
    color: '#00BCD4'
  }
])

// 动画状态
const animatedFeatures = ref(Array(features.value.length).fill(false))

// 保存目标页面，用于动画过渡
const targetPage = ref(0)

// 页面切换方向
const transitionDirection = ref<'up' | 'down'>('down')

onMounted(() => {
  loginStore.checkAuthStatus()
  pageStore.setCurrentPage('Home')
  
  // 触发特性卡片动画
  setTimeout(() => {
    features.value.forEach((_, index) => {
      setTimeout(() => {
        animatedFeatures.value[index] = true
      }, index * 100)
    })
  }, 500)
  
  // 添加鼠标滚轮事件监听器，设置passive选项为false以允许preventDefault
  window.addEventListener('wheel', handleWheel, { passive: false })
})

// 组件卸载前移除事件监听器
onBeforeUnmount(() => {
  window.removeEventListener('wheel', handleWheel)
})

function handleWheel(event: WheelEvent) {
  // 防止默认滚动行为
  event.preventDefault()
  
  // 根据滚动方向切换页面
  if (event.deltaY > 0) {
    // 向下滚动，切换到下一页
    nextPage()
  } else {
    // 向上滚动，切换到上一页
    prevPage()
  }
}

function jumpToLogin() {
  router.push({
    name: 'login'
  })
}

function jumpToDemo() {
  // 这里可以跳转到演示页面
  console.log('跳转到演示')
}

function jumpToTutorial() {
  // 这里可以跳转到教程页面
  console.log('跳转到教程')
}

// 用户是否已登录
const isLoggedIn = computed(() => loginStore.loggedIn)

// 切换到下一页
function nextPage() {
  if (currentPage.value < totalPages - 1) {
    transitionDirection.value = 'down'
    targetPage.value = currentPage.value + 1
    setTimeout(() => {
      currentPage.value = targetPage.value
    }, 300) // 与CSS动画持续时间保持一致
  }
}

// 切换到上一页
function prevPage() {
  if (currentPage.value > 0) {
    transitionDirection.value = 'up'
    targetPage.value = currentPage.value - 1
    setTimeout(() => {
      currentPage.value = targetPage.value
    }, 300) // 与CSS动画持续时间保持一致
  }
}

// 跳转到GitHub
function jumpToGithub() {
  window.open('https://github.com', '_blank')
}

// 跳转到特定页面
function goToPage(pageIndex: number) {
  if (pageIndex >= 0 && pageIndex < totalPages) {
    transitionDirection.value = pageIndex > currentPage.value ? 'down' : 'up'
    targetPage.value = pageIndex
    setTimeout(() => {
      currentPage.value = targetPage.value
    }, 300) // 与CSS动画持续时间保持一致
  }
}
</script>

<template>
  <div class="home-container">
    <!-- 背景装饰元素 -->
    <div class="background-elements">
      <div class="bg-circle circle-1"></div>
      <div class="bg-circle circle-2"></div>
      <div class="bg-circle circle-3"></div>
      <div class="bg-circle circle-4"></div>
    </div>
    
    <!-- 主内容区 -->
    <div class="home-content">
      <!-- 顶部导航 -->
      <div class="home-header">
        <div class="logo-container">
          <!-- <span class="logo-icon">
            <svg width="40" height="40" viewBox="0 0 24 24">
              <path fill="#2196F3" d="M21,16.5C21,16.88 20.79,17.21 20.47,17.38L12.57,21.82C12.41,21.94 12.21,22 12,22C11.79,22 11.59,21.94 11.43,21.82L3.53,17.38C3.21,17.21 3,16.88 3,16.5V7.5C3,7.12 3.21,6.79 3.53,6.62L11.43,2.18C11.59,2.06 11.79,2 12,2C12.21,2 12.41,2.06 12.57,2.18L20.47,6.62C20.79,6.79 21,7.12 21,7.5V16.5M12,4.15L5,8.09V15.91L12,19.85L19,15.91V8.09L12,4.15M12,6.23L16.9,9.06L12,11.89L7.1,9.06L12,6.23Z" />
            </svg>
          </span>
          <div class="logo-text">
            <h1>NodePy</h1>
            <span class="logo-tagline">节点式金融数据分析平台</span>
          </div>
        </div>
        
        <div class="header-actions" v-if="!isLoggedIn">
          <el-button type="primary" @click="jumpToLogin" class="login-btn">
            <span class="mdi mdi-login"></span>
            登录/注册
          </el-button>
        </div>
        <div class="header-actions" v-else>
          <el-button type="primary" @click="router.push({name: 'workspace'})" class="dashboard-btn">
            <span class="mdi mdi-view-dashboard"></span>
            进入工作台
          </el-button> -->
        </div>
      </div>
      
      <!-- 页面切换容器 -->
      <div class="page-container">
        <!-- 页面内容 -->
        <div class="page-content">
          <!-- 第一页：主标语和介绍 -->
          <div 
            v-show="currentPage === 0 || targetPage === 0" 
            class="page page-1"
            :class="{
              'slide-down': currentPage === 0 && targetPage !== 0 && transitionDirection === 'down',
              'slide-up': currentPage === 0 && targetPage !== 0 && transitionDirection === 'up',
              'slide-from-top': targetPage === 0 && currentPage !== 0 && transitionDirection === 'up',
              'slide-from-bottom': targetPage === 0 && currentPage !== 0 && transitionDirection === 'down'
            }"
          >
            <div class="hero-section">
              <div class="hero-content">
                <h1 class="hero-title">
                  可视化金融数据分析，
                  <span class="highlight">从未如此简单</span>
                </h1>
                <p class="hero-subtitle">
                  NodePy是一个基于节点的金融数据分析平台，通过可视化界面创建和执行复杂的数据处理和分析工作流。基于Python的强大功能，为金融分析提供专业支持。
                </p>
                
                <div class="hero-actions">
                  <el-button type="primary" size="large" @click="isLoggedIn ? router.push({name: 'workspace'}) : jumpToLogin" class="cta-button">
                    <span class="mdi mdi-rocket-launch"></span>
                    立即使用
                  </el-button>
                  <el-button size="large" @click="jumpToDemo" class="secondary-button">
                    <span class="mdi mdi-play-circle-outline"></span>
                    查看案例
                  </el-button>
                </div>
                
                <div class="stats-container">
                  <div class="stat-item">
                    <div class="stat-number">50+</div>
                    <div class="stat-label">预制节点</div>
                  </div>
                  <div class="stat-divider"></div>
                  <div class="stat-item">
                    <div class="stat-number">100%</div>
                    <div class="stat-label">Python兼容</div>
                  </div>
                  <div class="stat-divider"></div>
                  <div class="stat-item">
                    <div class="stat-number">0</div>
                    <div class="stat-label">编程基础要求</div>
                  </div>
                </div>
              </div>
              
              <div class="hero-visual">
                <div class="node-visualization">
                  <div class="node node-1">
                    <span class="node-icon mdi mdi-database"></span>
                    <span class="node-label">数据源</span>
                  </div>
                  <div class="node node-2">
                    <span class="node-icon mdi mdi-filter"></span>
                    <span class="node-label">数据清洗</span>
                  </div>
                  <div class="node node-3">
                    <span class="node-icon mdi mdi-calculator"></span>
                    <span class="node-label">计算分析</span>
                  </div>
                  <div class="node node-4">
                    <span class="node-icon mdi mdi-chart-line"></span>
                    <span class="node-label">可视化</span>
                  </div>
                  <div class="node node-5">
                    <span class="node-icon mdi mdi-file-export"></span>
                    <span class="node-label">导出结果</span>
                  </div>
                  
                  <!-- 连接线 -->
                  <div class="connection connection-1"></div>
                  <div class="connection connection-2"></div>
                  <div class="connection connection-3"></div>
                  <div class="connection connection-4"></div>
                </div>
              </div>
            </div>
          </div>
          
          <!-- 第二页：特性展示 -->
          <div 
            v-show="currentPage === 1 || targetPage === 1" 
            class="page page-2"
            :class="{
              'slide-down': currentPage === 1 && targetPage !== 1 && transitionDirection === 'down',
              'slide-up': currentPage === 1 && targetPage !== 1 && transitionDirection === 'up',
              'slide-from-top': targetPage === 1 && currentPage !== 1 && transitionDirection === 'up',
              'slide-from-bottom': targetPage === 1 && currentPage !== 1 && transitionDirection === 'down'
            }"
          >
            <div class="features-section">
              <div class="section-header">
                <h2 class="section-title">为什么选择 NodePy</h2>
                <p class="section-subtitle">我们为您提供专业、高效、易用的金融数据分析解决方案</p>
              </div>
              
              <div class="features-grid">
                <div 
                  v-for="(feature, index) in features" 
                  :key="index"
                  class="feature-card"
                  :class="{ animated: animatedFeatures[index] }"
                  :style="{ '--card-color': feature.color }"
                >
                  <div class="feature-icon">
                    <span class="mdi" :class="feature.icon"></span>
                  </div>
                  <h3 class="feature-title">{{ feature.title }}</h3>
                  <p class="feature-description">{{ feature.description }}</p>
                </div>
              </div>
            </div>
          </div>
          
          <!-- 第三页：CTA区域和原页脚内容 -->
          <div 
            v-show="currentPage === 2 || targetPage === 2" 
            class="page page-3"
            :class="{
              'slide-down': currentPage === 2 && targetPage !== 2 && transitionDirection === 'down',
              'slide-up': currentPage === 2 && targetPage !== 2 && transitionDirection === 'up',
              'slide-from-top': targetPage === 2 && currentPage !== 2 && transitionDirection === 'up',
              'slide-from-bottom': targetPage === 2 && currentPage !== 2 && transitionDirection === 'down'
            }"
          >
            <div class="cta-section">
              <div class="cta-content">
                <h2 class="cta-title">立即开始您的金融数据分析之旅</h2>
                <p class="cta-subtitle">无需编写复杂代码，拖拽节点即可完成专业级金融分析</p>
                <div class="cta-buttons">
                  <el-button type="primary" size="large" @click="isLoggedIn ? router.push({name: 'workspace'}) : jumpToLogin" class="cta-button-large">
                    <span class="mdi mdi-arrow-right-circle"></span>
                    {{ isLoggedIn ? '进入工作台' : '免费注册' }}
                  </el-button>
                  <el-button size="large" @click="jumpToGithub" class="secondary-button">
                    <span class="mdi mdi-github"></span>
                    获取更多
                  </el-button>
                </div>
              </div>
            </div>
            
            <!-- 原页脚内容（无样式） -->
            <div class="footer-content-wrapper">
              <div class="footer-content">
                <div class="footer-logo">
                  <div class="logo-container">
                    <span class="logo-icon">
                      <svg width="30" height="30" viewBox="0 0 24 24">
                        <path fill="#2196F3" d="M21,16.5C21,16.88 20.79,17.21 20.47,17.38L12.57,21.82C12.41,21.94 12.21,22 12,22C11.79,22 11.59,21.94 11.43,21.82L3.53,17.38C3.21,17.21 3,16.88 3,16.5V7.5C3,7.12 3.21,6.79 3.53,6.62L11.43,2.18C11.59,2.06 11.79,2 12,2C12.21,2 12.41,2.06 12.57,2.18L20.47,6.62C20.79,6.79 21,7.12 21,7.5V16.5M12,4.15L5,8.09V15.91L12,19.85L19,15.91V8.09L12,4.15M12,6.23L16.9,9.06L12,11.89L7.1,9.06L12,6.23Z" />
                      </svg>
                    </span>
                    <div class="logo-text">
                      <h3>NodePy</h3>
                    </div>
                  </div>
                  <p class="footer-tagline">节点式金融数据分析平台</p>
                </div>
              </div>
              
              <div class="footer-bottom">
                <p>© 2025 NodePy. copyrights reserved.</p>
                <div class="footer-social">
                  <span class="mdi mdi-github"></span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 页面指示器 -->
      <div class="page-indicators">
        <span 
          v-for="(_, index) in Array(totalPages)" 
          :key="index"
          class="indicator"
          :class="{ active: currentPage === index }"
          @click="goToPage(index)"
        ></span>
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
@use 'sass:color';

// 添加页面切换动画
.slide-down {
  animation: slideDown 0.3s ease forwards;
}

.slide-up {
  animation: slideUp 0.3s ease forwards;
}

.slide-from-top {
  animation: slideFromTop 0.3s ease forwards;
}

.slide-from-bottom {
  animation: slideFromBottom 0.3s ease forwards;
}

@keyframes slideDown {
  from {
    transform: translateY(0);
    opacity: 1;
  }
  to {
    transform: translateY(100%);
    opacity: 0;
  }
}

@keyframes slideUp {
  from {
    transform: translateY(0);
    opacity: 1;
  }
  to {
    transform: translateY(-100%);
    opacity: 0;
  }
}

@keyframes slideFromTop {
  from {
    transform: translateY(-100%);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

@keyframes slideFromBottom {
  from {
    transform: translateY(100%);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

.home-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  position: relative;
  width: 100%;
  min-height: 0;
  overflow-x: hidden;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e8f0 100%);
}

.background-elements {
  position: absolute;
  width: 100%;
  height: 100%;
  z-index: 0;
  overflow: hidden;
  
  .bg-circle {
    position: absolute;
    border-radius: 50%;
    background: linear-gradient(135deg, rgba(33, 150, 243, 0.1) 0%, rgba(33, 150, 243, 0.05) 100%);
    filter: blur(20px);
  }
  
  .circle-1 {
    width: 300px;
    height: 300px;
    top: -100px;
    right: -100px;
    animation: float 20s infinite ease-in-out;
  }
  
  .circle-2 {
    width: 200px;
    height: 200px;
    bottom: 100px;
    left: -50px;
    background: linear-gradient(135deg, rgba(76, 175, 80, 0.1) 0%, rgba(76, 175, 80, 0.05) 100%);
    animation: float 25s infinite ease-in-out reverse;
  }
  
  .circle-3 {
    width: 150px;
    height: 150px;
    top: 200px;
    left: 10%;
    background: linear-gradient(135deg, rgba(156, 39, 176, 0.1) 0%, rgba(156, 39, 176, 0.05) 100%);
    animation: float 15s infinite ease-in-out;
  }
  
  .circle-4 {
    width: 250px;
    height: 250px;
    bottom: -100px;
    right: 10%;
    background: linear-gradient(135deg, rgba(255, 152, 0, 0.1) 0%, rgba(255, 152, 0, 0.05) 100%);
    animation: float 18s infinite ease-in-out reverse;
  }
}

@keyframes float {
  0%, 100% {
    transform: translateY(0) translateX(0);
  }
  25% {
    transform: translateY(-20px) translateX(10px);
  }
  50% {
    transform: translateY(-40px) translateX(0);
  }
  75% {
    transform: translateY(-20px) translateX(-10px);
  }
}

.home-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
  z-index: 1;
  position: relative;
}

.home-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 40px; /* 恢复header的padding */
  margin-bottom: 20px; /* 恢复header的margin */
  
  .logo-container {
    display: flex;
    align-items: center;
    gap: 15px;
    
    .logo-icon {
      display: flex;
      align-items: center;
      justify-content: center;
    }
    
    .logo-text {
      h1 {
        margin: 0;
        font-size: 28px; /* 恢复字体大小 */
        font-weight: 700;
        color: #2c3e50;
        background: linear-gradient(135deg, #2196F3, #21CBF3);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
      }
      
      .logo-tagline {
        font-size: 14px; /* 恢复tagline字体大小 */
        color: #7f8c8d;
      }
    }
  }
  
  .header-actions {
    .el-button {
      border-radius: 8px;
      padding: 10px 20px; /* 恢复按钮padding */
      font-weight: 600;
      transition: all 0.3s ease;
      
      &:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
      }
    }
    
    .login-btn {
      background: linear-gradient(135deg, #2196F3, #21CBF3);
      border: none;
      color: white;
    }
    
    .dashboard-btn {
      background: white;
      border: 1px solid #ddd;
      color: #2196F3;
    }
  }
}

.page-container {
  flex: 1;
  display: flex;
  position: relative;
  min-height: 0;
  margin-bottom: 40px; /* 增加底部margin */
  padding: 0 30px; /* 增加水平padding */
}

.page-content {
  flex: 1;
  display: flex;
  overflow: hidden;
  min-height: 0;
  position: relative; /* 添加相对定位 */
}

.page {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
  position: absolute; /* 使用绝对定位 */
  width: 100%;
  height: 100%;
  top: 0;
  left: 0;
  transition: transform 0.3s ease; /* 添加过渡效果 */
}

// /* 添加隐藏类以更好地控制显示 */
// .page:not(.slide-down):not(.slide-up):not(.slide-from-top):not(.slide-from-bottom) {
//   display: none;
// }

.hero-section {
  flex: 1;
  display: flex;
  align-items: center;
  padding: 60px 30px; /* 增加padding */
  
  .hero-content {
    max-width: 600px;
    
    .hero-title {
      font-size: 42px; /* 增大标题字体大小 */
      font-weight: 800;
      line-height: 1.2;
      color: #2c3e50;
      margin-bottom: 20px; /* 增加margin */
      
      .highlight {
        background: linear-gradient(135deg, #2196F3, #21CBF3);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
      }
    }
    
    .hero-subtitle {
      font-size: 18px; /* 增大副标题字体大小 */
      line-height: 1.6;
      color: #5a6c7d;
      margin-bottom: 30px; /* 增加margin */
    }
    
    .hero-actions {
      display: flex;
      gap: 15px; /* 增加按钮间距 */
      margin-bottom: 40px; /* 增加margin */
      flex-wrap: wrap;
      
      .el-button {
        border-radius: 8px;
        padding: 12px 24px; /* 调整按钮padding */
        font-size: 16px; /* 增大字体大小 */
        font-weight: 600;
        transition: all 0.3s ease;
        
        &:hover {
          transform: translateY(-3px);
          box-shadow: 0 6px 16px rgba(0, 0, 0, 0.15);
        }
      }
      
      .cta-button {
        background: linear-gradient(135deg, #2196F3, #21CBF3);
        border: none;
        color: white;
      }
      
      .secondary-button {
        background: white;
        border: 1px solid #ddd;
        color: #2196F3;
      }
    }
    
    .stats-container {
      display: flex;
      align-items: center;
      gap: 25px; /* 增加间距 */
      
      .stat-item {
        text-align: center;
        
        .stat-number {
          font-size: 32px; /* 增大数字字体大小 */
          font-weight: 700;
          color: #2196F3;
          margin-bottom: 6px;
        }
        
        .stat-label {
          font-size: 14px; /* 增大标签字体大小 */
          color: #7f8c8d;
        }
      }
      
      .stat-divider {
        width: 1px;
        height: 40px; /* 增大分割线高度 */
        background: #ddd;
      }
    }
  }
  
  .hero-visual {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 30px; /* 增加padding */
    
    .node-visualization {
      position: relative;
      width: 100%;
      max-width: 500px;
      height: 300px; /* 增加高度 */
    }
    
    .node {
      position: absolute;
      width: 80px; /* 增加节点宽度 */
      height: 80px; /* 增加节点高度 */
      background: white;
      border-radius: 16px;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
      transition: all 0.3s ease;
      z-index: 2;
      
      &:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 32px rgba(0, 0, 0, 0.15);
      }
      
      .node-icon {
        font-size: 24px; /* 增大图标大小 */
        margin-bottom: 8px; /* 增加margin */
      }
      
      .node-label {
        font-size: 12px; /* 增大标签字体大小 */
        font-weight: 600;
        color: #2c3e50;
      }
    }
    
    .node-1 {
      top: 20%;
      left: 10%;
      color: #2196F3;
    }
    
    .node-2 {
      top: 20%;
      right: 10%;
      color: #4CAF50;
    }
    
    .node-3 {
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      color: #FF9800;
    }
    
    .node-4 {
      bottom: 20%;
      left: 10%;
      color: #2196F3;
    }
    
    .node-5 {
      bottom: 20%;
      right: 10%;
      color: #4CAF50;
    }
    
    .connection {
      position: absolute;
      background: linear-gradient(135deg, #2196F3, #4CAF50);
      z-index: 1;
    }
    
    .connection-1 {
      top: 25%;
      left: 20%;
      width: 60%;
      height: 4px;
      border-radius: 2px;
    }
    
    .connection-2 {
      top: 25%;
      right: 20%;
      width: 4px;
      height: 25%;
      border-radius: 2px;
    }
    
    .connection-3 {
      top: 50%;
      left: 20%;
      width: 60%;
      height: 4px;
      border-radius: 2px;
    }
    
    .connection-4 {
      bottom: 25%;
      left: 20%;
      width: 4px;
      height: 25%;
      border-radius: 2px;
    }
  }
}

.features-section {
  flex: 1;
  display: flex;
  flex-direction: column;
//   padding: 40px 0; /* 增加padding */
    padding-top: 40px;
  
  .section-header {
    text-align: center;
    margin-bottom: 40px; /* 增加margin */
    
    .section-title {
      font-size: 32px; /* 增大标题字体大小 */
      font-weight: 800;
      color: #2c3e50;
      margin-bottom: 15px; /* 增加margin */
    }
    
    .section-subtitle {
      font-size: 18px; /* 增大副标题字体大小 */
      color: #5a6c7d;
      max-width: 600px;
      margin: 0 auto;
    }
  }
  
  .features-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); /* 调整网格列宽 */
    gap: 30px; /* 增加间距 */
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 30px; /* 增加水平padding确保内容不被遮挡 */
  }
  
  .feature-card {
    background: white;
    border-radius: 16px;
    padding: 25px; /* 增加padding */
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.05);
    transition: all 0.3s ease;
    border-top: 4px solid  #2196F3;
    opacity: 0;
    transform: translateY(20px);
    
    &.animated {
      opacity: 1;
      transform: translateY(0);
    }
    
    .feature-icon {
      width: 60px; /* 增加图标容器大小 */
      height: 60px; /* 增加图标容器大小 */
      border-radius: 16px;
      display: flex;
      align-items: center;
      justify-content: center;
      margin-bottom: 20px; /* 增加margin */
      
      .mdi {
        font-size: 28px; /* 增大图标大小 */
        color: white;
        display: flex;
        align-items: center;
        justify-content: center;
      }
    }
    
    .feature-title {
      font-size: 20px; /* 增大标题字体大小 */
      font-weight: 700;
      color: #2c3e50;
      margin-bottom: 12px; /* 增加margin */
    }
    
    .feature-description {
      font-size: 16px; /* 增大描述字体大小 */
      line-height: 1.5;
      color: #5a6c7d;
    }
  }
}

.cta-section {
  flex: 1;
  display: flex;
  align-items: center;
  background: linear-gradient(135deg, #2196F3, #21CBF3);
  border-radius: 24px;
  padding: 50px 40px; /* 增加padding */
  text-align: center;
  margin-bottom: 40px; /* 增加margin */
  box-shadow: 0 10px 40px rgba(33, 150, 243, 0.3);
  
  .cta-content {
    max-width: 600px;
    margin: 0 auto;
    width: 100%;
    
    .cta-title {
      font-size: 32px; /* 增大标题字体大小 */
      font-weight: 700;
      color: white;
      margin-bottom: 15px; /* 增加margin */
    }
    
    .cta-subtitle {
      font-size: 18px; /* 增大副标题字体大小 */
      color: rgba(255, 255, 255, 0.9);
      margin-bottom: 30px; /* 增加margin */
    }
    
    .cta-buttons {
      display: flex;
      gap: 15px; /* 增加按钮间距 */
      justify-content: center;
      flex-wrap: wrap;
    }
    
    .cta-button-large, .secondary-button {
      display: flex;
      align-items: center;
      gap: 8px; /* 增加图标和文字间距 */
      padding: 15px 35px; /* 增加按钮padding */
      font-size: 18px; /* 增大字体大小 */
      font-weight: 600;
      border-radius: 12px;
      margin: 0 auto;
      transition: all 0.3s ease;
      
      &:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
      }
    }
    
    .cta-button-large {
      background: white;
      color: #2196F3;
      border: none;
    }
    
    .secondary-button {
      background: transparent;
      color: white;
      border: 2px solid white;
    }
  }
}

/* 移除footer样式，只保留内容结构 */
.footer-content-wrapper {
  padding: 30px 0;
  
  .footer-content {
    max-width: 1200px;
    margin: 0 auto 20px;
    padding: 0 30px;
    display: flex;
    flex-direction: column;
    gap: 25px;
    
    @media (min-width: 768px) {
      flex-direction: row;
      justify-content: space-between;
    }
  }
  
  .footer-logo {
    .logo-container {
      display: flex;
      align-items: center;
      gap: 12px;
      margin-bottom: 12px;
      
      h3 {
        margin: 0;
        font-size: 24px;
        color: #2c3e50;
      }
    }
    
    .footer-tagline {
      color: #7f8c8d;
      font-size: 14px;
    }
  }
  
  .footer-bottom {
    max-width: 1200px;
    margin: 25px auto 0;
    padding: 15px 30px 0;
    border-top: 1px solid #ddd;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 15px;
    
    @media (min-width: 768px) {
      flex-direction: row;
      justify-content: space-between;
    }
    
    p {
      color: #7f8c8d;
      font-size: 14px;
      margin: 0;
    }
    
    .footer-social {
      display: flex;
      gap: 20px;
      
      .mdi {
        font-size: 20px;
        color: #7f8c8d;
        cursor: pointer;
        transition: color 0.3s;
        display: flex;
        align-items: center;
        justify-content: center;
        
        &:hover {
          color: #2196F3;
        }
      }
    }
  }
}

.page-indicators {
  display: flex;
  justify-content: center;
  gap: 15px; /* 增加间距 */
  margin-bottom: 30px; /* 增加margin */
  
  .indicator {
    width: 12px; /* 增大指示器大小 */
    height: 12px; /* 增大指示器大小 */
    border-radius: 50%;
    background: #ccc;
    cursor: pointer;
    transition: all 0.3s ease;
    
    &.active {
      background: #2196F3;
      transform: scale(1.2);
    }
  }
}
</style>