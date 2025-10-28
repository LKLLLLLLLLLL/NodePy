import html2canvas from 'html2canvas'

/**
 * 计算所有节点的边界框，用于居中显示
 */
const calculateNodesBoundingBox = (nodes: NodeListOf<Element>): { minX: number; minY: number; maxX: number; maxY: number; width: number; height: number } => {
  if (nodes.length === 0) {
    return { minX: 0, minY: 0, maxX: 100, maxY: 100, width: 100, height: 100 }
  }

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
  const padding = 50
  return {
    minX: minX - padding,
    minY: minY - padding,
    maxX: maxX + padding,
    maxY: maxY + padding,
    width: (maxX - minX) + padding * 2,
    height: (maxY - minY) + padding * 2
  }
}

/**
 * 在后台调整视图以确保节点居中显示
 */
const adjustViewForCentering = (container: HTMLElement): void => {
  const nodes = container.querySelectorAll('.vue-flow__node')
  if (nodes.length === 0) return

  const boundingBox = calculateNodesBoundingBox(nodes)
  
  // 获取视口元素
  const viewport = container.querySelector('.vue-flow__viewport') as HTMLElement
  if (!viewport) return

  // 计算缩放和平移以使节点居中
  const containerWidth = container.clientWidth
  const containerHeight = container.clientHeight
  
  const scaleX = containerWidth / boundingBox.width
  const scaleY = containerHeight / boundingBox.height
  const scale = Math.min(scaleX, scaleY, 1) // 不超过1倍缩放
  
  // 计算平移量以使内容居中
  const translateX = (containerWidth - boundingBox.width * scale) / 2 - boundingBox.minX * scale
  const translateY = (containerHeight - boundingBox.height * scale) / 2 - boundingBox.minY * scale

  // 应用变换
  viewport.style.transform = `translate(${translateX}px, ${translateY}px) scale(${scale})`
  viewport.style.transformOrigin = '0 0'
}

/**
 * 创建纯白背景的流程图截图 - 只保留节点和边
 */
const createCleanFlowCapture = (vueFlowContainer: HTMLElement): HTMLElement => {
  const hiddenContainer = document.createElement('div')
  hiddenContainer.style.position = 'fixed'
  hiddenContainer.style.left = '-9999px'
  hiddenContainer.style.top = '-9999px'
  hiddenContainer.style.zIndex = '-1000'
  hiddenContainer.style.opacity = '0'
  hiddenContainer.style.pointerEvents = 'none'
  hiddenContainer.style.overflow = 'hidden'
  
  // 设置16:9比例
  const width = 1280 // 16:9 宽度
  const height = 720 // 16:9 高度
  hiddenContainer.style.width = `${width}px`
  hiddenContainer.style.height = `${height}px`
  hiddenContainer.style.backgroundColor = '#ffffff'
  hiddenContainer.style.overflow = 'hidden'
  hiddenContainer.style.border = 'none'
  
  // 深度克隆整个VueFlow容器，确保不影响原始元素
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
  clone.style.overflow = 'hidden'
  
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
  
  // 获取主画布区域并设置为纯白背景
  const viewport = clone.querySelector('.vue-flow__viewport') as HTMLElement
  if (viewport) {
    viewport.style.background = '#ffffff'
    viewport.style.backgroundColor = '#ffffff'
    viewport.style.width = '100%'
    viewport.style.height = '100%'
    viewport.style.border = 'none'
  }
  
  // 移除所有背景图案和网格
  const patterns = clone.querySelectorAll('pattern, defs')
  patterns.forEach(pattern => pattern.remove())
  
  // 处理所有节点，确保它们可见且样式合适
  const nodes = clone.querySelectorAll('.vue-flow__node')
  nodes.forEach(node => {
    const n = node as HTMLElement
    // 确保节点有合适的背景色和边框
    n.style.backgroundColor = '#ffffff'
    n.style.background = '#ffffff'
    n.style.border = '2px solid #333333' // 更粗的边框提高可见性
    n.style.boxShadow = '0 2px 4px rgba(0,0,0,0.2)' // 轻微阴影增强立体感
    
    // 确保节点内容可见
    const nodeContent = n.querySelector('.node-content') as HTMLElement || n
    if (nodeContent && nodeContent.style) {
      nodeContent.style.color = '#333333'
      nodeContent.style.fontSize = '14px'
      nodeContent.style.fontWeight = 'bold' // 加粗文字提高可读性
    }
    
    // 额外处理：确保所有子元素中的文本可见
    const textElements = n.querySelectorAll('span, div, p, label, input, button')
    textElements.forEach(textEl => {
      const element = textEl as HTMLElement
      if (element.style) {
        element.style.color = '#333333'
        element.style.fontWeight = 'bold'
      }
    })
  })
  
  // 处理所有边，确保它们可见
  const edges = clone.querySelectorAll('.vue-flow__edge')
  edges.forEach(edge => {
    const e = edge as HTMLElement
    const path = e.querySelector('path') as SVGPathElement
    if (path) {
      path.setAttribute('stroke', '#333333')
      path.setAttribute('stroke-width', '3') // 更粗的边提高可见性
      path.setAttribute('stroke-linecap', 'round')
    }
    
    // 移除边的标签背景（如果有）
    const edgeLabel = e.querySelector('.vue-flow__edge-textbg')
    if (edgeLabel) edgeLabel.remove()
    
    // 设置边标签文字样式
    const edgeText = e.querySelector('.vue-flow__edge-text') as HTMLElement
    if (edgeText && edgeText.style) {
      edgeText.style.fill = '#333333'
      edgeText.style.fontSize = '14px'
      edgeText.style.fontWeight = 'bold'
    }
  })
  
  // 处理连接点 - 使其更明显
  const handles = clone.querySelectorAll('.vue-flow__handle')
  handles.forEach(handle => {
    const h = handle as HTMLElement
    h.style.backgroundColor = '#333333'
    h.style.border = '2px solid #ffffff'
    h.style.width = '12px'
    h.style.height = '12px'
  })
  
  hiddenContainer.appendChild(clone)
  
  // 在隐藏容器添加到DOM后调整视图
  setTimeout(() => {
    adjustViewForCentering(clone)
  }, 100)
  
  return hiddenContainer
}

/**
 * 直接截图完整流程图 - 纯白背景，只保留节点和边
 */
const captureCleanFlowDirect = async (vueFlowContainer: HTMLElement): Promise<string | null> => {
  try {
    console.log('开始后台截图完整流程图...')
    
    const canvas = await html2canvas(vueFlowContainer, {
      backgroundColor: '#ffffff',
      scale: 1.5, // 较高缩放以保证文字清晰
      useCORS: true,
      allowTaint: false,
      logging: false, // 关闭日志避免干扰
      width: 1280, // 16:9 宽度
      height: 720, // 16:9 高度
      onclone: (clonedDocument, element) => {
        // 在克隆的文档中优化样式，完全不影响原始元素
        const clonedVueFlow = element as HTMLElement
        
        // 移除所有不需要的UI元素
        const minimap = clonedVueFlow.querySelector('.vue-flow__minimap')
        if (minimap) minimap.remove()
        
        const controls = clonedVueFlow.querySelector('.vue-flow__controls')
        if (controls) controls.remove()
        
        const panel = clonedVueFlow.querySelector('.vue-flow__panel')
        if (panel) panel.remove()
        
        const background = clonedVueFlow.querySelector('.vue-flow__background')
        if (background) background.remove()
        
        // 移除所有背景图案和网格
        const patterns = clonedVueFlow.querySelectorAll('pattern, defs')
        patterns.forEach(pattern => pattern.remove())
        
        // 设置纯白背景
        clonedVueFlow.style.backgroundColor = '#ffffff'
        const viewport = clonedVueFlow.querySelector('.vue-flow__viewport') as HTMLElement
        if (viewport) {
          viewport.style.backgroundColor = '#ffffff'
          viewport.style.background = '#ffffff'
        }
        
        // 优化节点样式
        const nodes = clonedVueFlow.querySelectorAll('.vue-flow__node')
        nodes.forEach(node => {
          const n = node as HTMLElement
          n.style.backgroundColor = '#ffffff'
          n.style.border = '2px solid #333333'
          n.style.boxShadow = '0 2px 4px rgba(0,0,0,0.2)'
          
          // 确保文字可见
          const textElements = n.querySelectorAll('span, div, p, label, input, button')
          textElements.forEach(el => {
            if (el instanceof HTMLElement && el.style) {
              el.style.color = '#333333'
              el.style.fontWeight = 'bold'
              // 确保字体大小合适
              if (el.style.fontSize && parseInt(el.style.fontSize) < 12) {
                el.style.fontSize = '12px'
              }
            }
          })
        })
        
        // 优化边样式
        const edges = clonedVueFlow.querySelectorAll('.vue-flow__edge')
        edges.forEach(edge => {
          const path = edge.querySelector('path')
          if (path) {
            path.setAttribute('stroke', '#333333')
            path.setAttribute('stroke-width', '3')
            path.setAttribute('stroke-linecap', 'round')
          }
          
          // 移除边的标签背景
          const edgeLabel = edge.querySelector('.vue-flow__edge-textbg')
          if (edgeLabel) edgeLabel.remove()
          
          // 设置边标签文字样式
          const edgeText = edge.querySelector('.vue-flow__edge-text') as HTMLElement
          if (edgeText && edgeText.style) {
            edgeText.style.fill = '#333333'
            edgeText.style.fontSize = '14px'
            edgeText.style.fontWeight = 'bold'
          }
        })
        
        // 优化连接点
        const handles = clonedVueFlow.querySelectorAll('.vue-flow__handle')
        handles.forEach(handle => {
          const h = handle as HTMLElement
          h.style.backgroundColor = '#333333'
          h.style.border = '2px solid #ffffff'
          h.style.width = '12px'
          h.style.height = '12px'
        })
        
        // 在克隆的文档中调整视图以使节点居中
        adjustViewForCentering(clonedVueFlow)
      }
    })
    
    console.log('后台截图成功')
    return canvas.toDataURL('image/png')
  } catch (error) {
    console.error('后台截图失败:', error)
    return null
  }
}

/**
 * 完整流程图截图功能 - 纯白背景，只显示节点和边，居中显示
 */
export const captureCleanFlow = async (vueFlowRef: any): Promise<string | null> => {
  if (!vueFlowRef) {
    console.error('未找到VueFlow容器')
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
      console.error('未找到VueFlow容器元素')
      return null
    }

    console.log('开始后台截图完整流程图...')
    
    let imageData: string | null = null
    
    // 优先使用直接截图方法，使用onclone确保不影响原始元素
    imageData = await captureCleanFlowDirect(vueFlowContainer)
    
    // 如果直接截图失败，尝试克隆方法
    if (!imageData) {
      console.log('直接截图失败，尝试克隆方法...')
      const hiddenContainer = createCleanFlowCapture(vueFlowContainer)
      document.body.appendChild(hiddenContainer)
      
      // 等待渲染和视图调整
      await new Promise(resolve => setTimeout(resolve, 300))
      
      try {
        const canvas = await html2canvas(hiddenContainer, {
          backgroundColor: '#ffffff',
          scale: 1.5,
          useCORS: true,
          allowTaint: false,
          logging: false, // 关闭日志避免干扰
          width: 1280, // 16:9 宽度
          height: 720  // 16:9 高度
        })
        
        imageData = canvas.toDataURL('image/png')
        console.log('克隆方法截图成功')
      } catch (error) {
        console.error('克隆方法也失败:', error)
      } finally {
        // 清理隐藏容器
        if (document.body.contains(hiddenContainer)) {
          document.body.removeChild(hiddenContainer)
        }
      }
    }
    
    return imageData
    
  } catch (error) {
    console.error('完整流程图截图失败:', error)
    return null
  }
}

/**
 * 保存截图到本地
 */
export const saveCleanScreenshot = (imageData: string, projectId: string): void => {
  try {
    const link = document.createElement('a')
    link.href = imageData
    link.download = `clean-flow-diagram-${projectId}-${Date.now()}.png`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    console.log('简洁流程图截图已保存')
  } catch (error) {
    console.error('保存简洁截图失败:', error)
  }
}

/**
 * 自动截图完整流程图并保存 - 纯白背景，只显示节点和边，居中显示
 */
export const autoCaptureDetailedAndSave = async (vueFlowRef: any, projectId: string): Promise<void> => {
  try {
    console.log('开始自动后台截图...')
    const imageData = await captureCleanFlow(vueFlowRef)
    if (imageData) {
      saveCleanScreenshot(imageData, projectId)
      console.log('自动后台截图完成')
    } else {
      console.error('后台截图失败，返回的imageData为null')
    }
  } catch (error) {
    console.error('自动后台截图失败:', error)
  }
}