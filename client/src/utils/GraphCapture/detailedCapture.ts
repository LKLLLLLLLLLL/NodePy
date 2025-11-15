import html2canvas from 'html2canvas'

/**
 * 创建完整的流程图克隆 - 只保留节点和边，确保所有内容可见
 */
const createFlowClone = (vueFlowContainer: HTMLElement): HTMLElement => {
  // 深度克隆整个VueFlow容器
  const clone = vueFlowContainer.cloneNode(true) as HTMLElement
  
  // 设置克隆样式 - 纯白背景
  clone.style.width = '100%'
  clone.style.height = '100%'
  clone.style.backgroundColor = '#ffffff'
  clone.style.background = '#ffffff'
  clone.style.border = 'none'
  clone.style.margin = '0'
  clone.style.padding = '0'
  clone.style.boxShadow = 'none'
  clone.style.outline = 'none'
  clone.style.overflow = 'visible'
  clone.style.position = 'relative'
  
  // 移除所有不需要的UI元素
  const elementsToRemove = [
    '.vue-flow__minimap', // 移除小地图
    '.vue-flow__controls', // 移除控制按钮
    '.vue-flow__panel', // 移除面板
    '.vue-flow__background' // 移除背景图案
  ]
  
  elementsToRemove.forEach(selector => {
    const elements = clone.querySelectorAll(selector)
    elements.forEach(el => el.remove())
  })
  
  // 获取视口元素并重置变换
  const viewport = clone.querySelector('.vue-flow__viewport') as HTMLElement
  if (viewport) {
    // 重置所有变换，确保我们看到原始位置
    viewport.style.transform = 'none'
    viewport.style.transformOrigin = '0 0'
    viewport.style.background = '#ffffff'
    viewport.style.backgroundColor = '#ffffff'
    viewport.style.width = 'auto'
    viewport.style.height = 'auto'
    viewport.style.overflow = 'visible'
    viewport.style.position = 'static'
  }
  
  // 移除所有背景图案和网格
  const patterns = clone.querySelectorAll('pattern, defs')
  patterns.forEach(pattern => pattern.remove())
  
  // 确保所有节点和边在白色背景下可见
  const nodes = clone.querySelectorAll('.vue-flow__node')
  nodes.forEach(node => {
    const n = node as HTMLElement
    n.style.backgroundColor = '#ffffff'
    n.style.background = '#ffffff'
    
    // 确保节点内容可见
    const nodeContent = n.querySelector('.node-content') as HTMLElement || n
    if (nodeContent && nodeContent.style) {
      nodeContent.style.color = '#333333'
    }
    
    // 确保所有子元素中的文本可见
    const textElements = n.querySelectorAll('span, div, p, label')
    textElements.forEach(textEl => {
      const element = textEl as HTMLElement
      if (element.style) {
        element.style.color = '#333333'
      }
    })
  })
  
  // 确保所有边可见
  const edges = clone.querySelectorAll('.vue-flow__edge')
  edges.forEach(edge => {
    const e = edge as HTMLElement
    const path = e.querySelector('path') as SVGPathElement
    if (path) {
      // 确保边有颜色
      if (!path.getAttribute('stroke') || path.getAttribute('stroke') === 'none') {
        path.setAttribute('stroke', '#333333')
      }
      // 确保边有一定宽度
      if (!path.getAttribute('stroke-width') || parseFloat(path.getAttribute('stroke-width') || '1') < 2) {
        path.setAttribute('stroke-width', '2')
      }
    }
  })
  
  return clone
}

/**
 * 计算所有节点的边界框 - 改进版本
 */
const calculateNodesBoundingBox = (nodes: NodeListOf<Element>): { minX: number; minY: number; maxX: number; maxY: number; width: number; height: number } | null => {
  if (nodes.length === 0) return null
  
  let minX = Infinity
  let minY = Infinity
  let maxX = -Infinity
  let maxY = -Infinity
  
  nodes.forEach(node => {
    const rect = node.getBoundingClientRect()
    minX = Math.min(minX, rect.left)
    minY = Math.min(minY, rect.top)
    maxX = Math.max(maxX, rect.right)
    maxY = Math.max(maxY, rect.bottom)
  })
  
  // 添加一些边距
  const margin = 20
  minX -= margin
  minY -= margin
  maxX += margin
  maxY += margin
  
  return {
    minX,
    minY,
    maxX,
    maxY,
    width: maxX - minX,
    height: maxY - minY
  }
}

/**
 * 创建居中显示的流程图容器
 */
const createCenteredFlowContainer = (flowClone: HTMLElement): HTMLElement => {
  const container = document.createElement('div')
  container.style.position = 'fixed'
  container.style.left = '-9999px'
  container.style.top = '-9999px'
  container.style.zIndex = '-1000'
  container.style.opacity = '0'
  container.style.pointerEvents = 'none'
  container.style.overflow = 'hidden'
  container.style.backgroundColor = '#ffffff'
  
  // 设置16:9比例
  const width = 1280
  const height = 720
  container.style.width = `${width}px`
  container.style.height = `${height}px`
  
  // 创建内部容器用于居中
  const innerContainer = document.createElement('div')
  innerContainer.style.width = '100%'
  innerContainer.style.height = '100%'
  innerContainer.style.display = 'flex'
  innerContainer.style.alignItems = 'center'
  innerContainer.style.justifyContent = 'center'
  innerContainer.style.backgroundColor = '#ffffff'
  innerContainer.style.overflow = 'hidden'
  innerContainer.style.position = 'relative'
  
  // 设置克隆容器的样式
  flowClone.style.position = 'relative'
  flowClone.style.margin = '0'
  flowClone.style.padding = '0'
  flowClone.style.boxSizing = 'border-box'
  flowClone.style.width = '100%'
  flowClone.style.height = '100%'
  
  innerContainer.appendChild(flowClone)
  container.appendChild(innerContainer)
  
  return container
}

/**
 * 调整克隆的流程图以确保所有节点居中显示 - 改进版本
 */
const adjustClonedFlow = (container: HTMLElement): void => {
  const flowClone = container.querySelector('.vue-flow') as HTMLElement
  if (!flowClone) {
    return
  }
  
  const viewport = flowClone.querySelector('.vue-flow__viewport') as HTMLElement
  if (!viewport) {
    return
  }
  
  const nodes = flowClone.querySelectorAll('.vue-flow__node')
  if (nodes.length === 0) {
    return
  }
  
  try {
    // 计算所有节点的边界框
    const nodesBoundingBox = calculateNodesBoundingBox(nodes)
    if (!nodesBoundingBox) {
      return
    }
    
    // 获取容器尺寸
    const containerRect = container.getBoundingClientRect()
    const containerWidth = containerRect.width
    const containerHeight = containerRect.height
    
    // 计算内容尺寸
    const contentWidth = nodesBoundingBox.width
    const contentHeight = nodesBoundingBox.height
    
    // 如果内容尺寸为0，使用默认值
    const validContentWidth = contentWidth > 0 ? contentWidth : 800
    const validContentHeight = contentHeight > 0 ? contentHeight : 600
    
    // 计算缩放比例 - 确保内容完全可见且居中
    const scaleX = (containerWidth * 0.85) / validContentWidth  // 85%宽度用于内容
    const scaleY = (containerHeight * 0.85) / validContentHeight // 85%高度用于内容
    const scale = Math.min(scaleX, scaleY, 1) // 取最小值，不超过1
    
    // 计算内容中心点
    const contentCenterX = nodesBoundingBox.minX + validContentWidth / 2
    const contentCenterY = nodesBoundingBox.minY + validContentHeight / 2
    
    // 计算容器中心点
    const containerCenterX = containerWidth / 2
    const containerCenterY = containerHeight / 2
    
    // 计算平移量 - 使内容中心与容器中心对齐
    const translateX = containerCenterX - contentCenterX * scale
    const translateY = containerCenterY - contentCenterY * scale
    
    // 应用变换到视口
    viewport.style.transform = `translate(${translateX}px, ${translateY}px) scale(${scale})`
    viewport.style.transformOrigin = '0 0'
    viewport.style.width = 'auto'
    viewport.style.height = 'auto'
    
  } catch (error) {

  }
}

/**
 * 备选方案：直接使用Vue Flow的边界框计算
 */
const captureFlowWithViewport = async (vueFlowContainer: HTMLElement): Promise<string | null> => {
  try {
    
    // 创建临时容器
    const tempContainer = document.createElement('div')
    tempContainer.style.position = 'fixed'
    tempContainer.style.left = '-9999px'
    tempContainer.style.top = '-9999px'
    tempContainer.style.width = '1280px'
    tempContainer.style.height = '720px'
    tempContainer.style.backgroundColor = '#ffffff'
    tempContainer.style.display = 'flex'
    tempContainer.style.alignItems = 'center'
    tempContainer.style.justifyContent = 'center'
    tempContainer.style.overflow = 'hidden'
    
    const clone = vueFlowContainer.cloneNode(true) as HTMLElement
    
    // 移除不需要的元素
    const elementsToRemove = [
      '.vue-flow__minimap',
      '.vue-flow__controls', 
      '.vue-flow__panel',
      '.vue-flow__background'
    ]
    
    elementsToRemove.forEach(selector => {
      const elements = clone.querySelectorAll(selector)
      elements.forEach(el => el.remove())
    })
    
    // 设置克隆样式
    clone.style.width = '100%'
    clone.style.height = '100%'
    clone.style.background = '#ffffff'
    clone.style.backgroundColor = '#ffffff'
    
    tempContainer.appendChild(clone)
    document.body.appendChild(tempContainer)
    
    const canvas = await html2canvas(tempContainer, {
      backgroundColor: '#ffffff',
      scale: 1.5,
      useCORS: true,
      allowTaint: false,
      logging: false,
      width: 1280,
      height: 720,
      onclone: (clonedDocument, element) => {
        // 在克隆的文档中确保所有内容可见
        const clonedVueFlow = element.querySelector('.vue-flow') as HTMLElement
        if (clonedVueFlow) {
          clonedVueFlow.style.background = '#ffffff'
          clonedVueFlow.style.backgroundColor = '#ffffff'
          
          // 重置视口变换
          const viewport = clonedVueFlow.querySelector('.vue-flow__viewport') as HTMLElement
          if (viewport) {
            viewport.style.transform = 'none'
          }
          
          // 确保节点和边可见
          const nodes = clonedVueFlow.querySelectorAll('.vue-flow__node')
          nodes.forEach(node => {
            const n = node as HTMLElement
            n.style.backgroundColor = '#ffffff'
            
            const textElements = n.querySelectorAll('span, div, p, label')
            textElements.forEach(textEl => {
              const element = textEl as HTMLElement
              element.style.color = '#333333'
            })
          })
          
          const edges = clonedVueFlow.querySelectorAll('.vue-flow__edge path')
          edges.forEach(edge => {
            const e = edge as SVGPathElement
            if (!e.getAttribute('stroke') || e.getAttribute('stroke') === 'none') {
              e.setAttribute('stroke', '#333333')
            }
            e.setAttribute('stroke-width', '2')
          })
        }
      }
    })
    
    document.body.removeChild(tempContainer)

    return canvas.toDataURL('image/png')
  } catch (error) {

    return null
  }
}

/**
 * 完整流程图截图功能 - 纯白背景，只显示节点和边，所有节点居中显示
 */
export const captureDetailed = async (vueFlowRef: any): Promise<string | null> => {
  if (!vueFlowRef) {

    return null
  }
  
  try {
    // 尝试多种方式查找VueFlow容器元素
    let vueFlowContainer: HTMLElement | null = null
    
    // 方式1: 直接查找.vue-flow类
    vueFlowContainer = vueFlowRef.querySelector('.vue-flow') as HTMLElement
    
    // 方式2: 如果方式1失败，尝试查找包含VueFlow内容的元素
    if (!vueFlowContainer) {
      vueFlowContainer = vueFlowRef.querySelector('.vueFlow') as HTMLElement
    }
    
    // 方式3: 如果前两种方式都失败，使用vueFlowRef自身
    if (!vueFlowContainer) {
      vueFlowContainer = vueFlowRef as HTMLElement
    }
    
    if (!vueFlowContainer) {

      return null
    }


    
    let imageData: string | null = null
    
    // 先尝试视口边界框方法
    imageData = await captureFlowWithViewport(vueFlowContainer)
    
    // 如果视口边界框方法失败，尝试克隆方法
    if (!imageData) {

      
      // 创建流程图克隆
      const flowClone = createFlowClone(vueFlowContainer)
      
      // 创建居中容器
      const centeredContainer = createCenteredFlowContainer(flowClone)
      document.body.appendChild(centeredContainer)
      
      // 等待DOM更新
      await new Promise(resolve => setTimeout(resolve, 200))
      
      // 调整克隆的流程图以确保居中
      adjustClonedFlow(centeredContainer)
      
      // 等待调整完成
      await new Promise(resolve => setTimeout(resolve, 200))
      
      try {
        const canvas = await html2canvas(centeredContainer, {
          backgroundColor: '#ffffff',
          scale: 1.5,
          useCORS: true,
          allowTaint: false,
          logging: false,
          width: 1280,
          height: 720
        })
        
        imageData = canvas.toDataURL('image/png')

      } catch (error) {

      } finally {
        // 清理容器
        if (document.body.contains(centeredContainer)) {
          document.body.removeChild(centeredContainer)
        }
      }
    }

    if (imageData) {
      const base64String = imageData.replace(/^data:image\/\w+;base64,/, '')
      return base64String
    }
    
    return null
    
  } catch (error) {

    return null
  }
}

/**
 * 保存截图到本地
 */
export const saveDetailedScreenshot = (imageData: string, projectId: string): void => {
  try {
    const link = document.createElement('a')
    link.href = imageData
    link.download = `detailed-capture-${projectId}-${Date.now()}.png`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)

  } catch (error) {

  }
}

/**
 * 自动截图并返回 Base64 字符串
 */
export const autoCaptureDetailed = async (vueFlowRef: any): Promise<string | null> => {
  try {

    const base64String = await captureDetailed(vueFlowRef)
    if (base64String) {

      return base64String
    } else {

      return null
    }
  } catch (error) {
    console.error('自动截图失败:', error)
    return null
  }
}