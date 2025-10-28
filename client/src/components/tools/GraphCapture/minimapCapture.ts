import html2canvas from 'html2canvas'

/**
 * 创建纯白色背景的小地图副本用于截图，并确保节点居中显示
 */
const createWhiteBackgroundMiniMap = (originalMiniMap: HTMLElement): HTMLElement => {
  const hiddenContainer = document.createElement('div')
  hiddenContainer.style.position = 'fixed'
  hiddenContainer.style.left = '-9999px'
  hiddenContainer.style.top = '-9999px'
  hiddenContainer.style.zIndex = '-1000'
  hiddenContainer.style.opacity = '0'
  hiddenContainer.style.pointerEvents = 'none'
  
  // 设置16:9比例
  const width = 800
  const height = 450
  hiddenContainer.style.width = `${width}px`
  hiddenContainer.style.height = `${height}px`
  hiddenContainer.style.backgroundColor = '#ffffff'
  hiddenContainer.style.overflow = 'hidden'
  hiddenContainer.style.border = 'none'
  hiddenContainer.style.display = 'flex'
  hiddenContainer.style.alignItems = 'center'
  hiddenContainer.style.justifyContent = 'center'
  
  // 克隆小地图
  const clone = originalMiniMap.cloneNode(true) as HTMLElement
  
  // 移除可能影响渲染的类名
  clone.classList.remove('controller-style', 'set_background_color')
  
  // 设置克隆样式 - 纯白色背景，无边框
  clone.style.position = 'relative'
  clone.style.width = '90%' // 缩小容器以创建留白
  clone.style.height = '90%' // 缩小容器以创建留白
  clone.style.backgroundColor = '#ffffff'
  clone.style.background = '#ffffff'
  clone.style.border = 'none'
  clone.style.borderRadius = '0'
  clone.style.margin = '0'
  clone.style.padding = '0'
  clone.style.boxShadow = 'none'
  clone.style.outline = 'none'
  clone.style.overflow = 'visible'
  
  // 获取SVG元素
  const svgElement = clone.querySelector('svg') as SVGSVGElement
  if (svgElement) {
    // 设置SVG样式 - 确保内容居中
    svgElement.style.backgroundColor = '#ffffff'
    svgElement.style.background = '#ffffff'
    svgElement.style.border = 'none'
    svgElement.style.borderRadius = '0'
    svgElement.style.width = '100%'
    svgElement.style.height = '100%'
    svgElement.style.overflow = 'visible'
    svgElement.style.display = 'block'
    
    // 移除所有遮罩和背景元素
    const elementsToRemove = [
      '.vue-flow__minimap-mask',
      '.vue-flow__minimap-background',
      'mask',
      '.vue-flow__minimap-mask-rect'
    ]
    
    elementsToRemove.forEach(selector => {
      const elements = svgElement.querySelectorAll(selector)
      elements.forEach(el => el.remove())
    })
    
    // 设置SVG背景为白色 - 处理所有矩形元素
    const rects = svgElement.querySelectorAll('rect')
    rects.forEach(rect => {
      const r = rect as SVGRectElement
      // 找到背景矩形并设置为白色
      if (r.getAttribute('class')?.includes('background') || 
          !r.getAttribute('id') || 
          r.getAttribute('fill') === 'rgba(0,0,0,0.1)' ||
          r.getAttribute('fill') === 'rgba(240, 240, 240, 0.6)') {
        r.setAttribute('fill', '#ffffff')
        r.style.fill = '#ffffff'
        r.setAttribute('stroke', 'none')
      }
    })
    
    // 确保所有边可见且颜色合适
    const paths = svgElement.querySelectorAll('path')
    paths.forEach(path => {
      const p = path as SVGPathElement
      // 确保边有颜色
      const currentStroke = p.getAttribute('stroke')
      if (!currentStroke || currentStroke === 'none' || currentStroke === '#b1b1b7') {
        p.setAttribute('stroke', '#333333') // 深灰色边
      } else if (currentStroke === '#b1b1b7') {
        p.setAttribute('stroke', '#333333') // 将浅灰色边改为深灰色
      }
      p.style.stroke = p.getAttribute('stroke') || '#333333'
      
      // 确保边有一定宽度
      if (!p.getAttribute('stroke-width') || p.getAttribute('stroke-width') === '1') {
        p.setAttribute('stroke-width', '2')
      }
    })
    
    // 处理节点矩形 - 更彻底的处理
    const nodeRects = svgElement.querySelectorAll('rect')
    nodeRects.forEach(rect => {
      const r = rect as SVGRectElement
      const rectClass = r.getAttribute('class') || ''
      
      // 如果是节点矩形
      if (rectClass.includes('vue-flow_minimap-node') || rectClass.includes('node')) {
        // 设置节点颜色为深色，确保在白色背景下可见
        const currentFill = r.getAttribute('fill')
        if (!currentFill || currentFill === '#ccc' || currentFill === '#d1d1d1' || currentFill === 'rgba(240, 240, 240, 0.6)') {
          r.setAttribute('fill', '#555555') // 深灰色节点
          r.style.fill = '#555555'
        }
        
        // 确保节点有边框
        if (!r.getAttribute('stroke') || r.getAttribute('stroke') === 'transparent' || r.getAttribute('stroke') === 'none') {
          r.setAttribute('stroke', '#222222') // 深灰色边框
        }
        r.style.stroke = r.getAttribute('stroke') || '#222222'
        
        // 确保边框有一定宽度
        if (!r.getAttribute('stroke-width') || r.getAttribute('stroke-width') === '0') {
          r.setAttribute('stroke-width', '1.5')
        }
      }
    })

    // 计算节点边界框并调整视图
    setTimeout(() => {
      try {
        const nodes = svgElement.querySelectorAll('.vue-flow_minimap-node')
        if (nodes.length > 0) {
          let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity
          
          nodes.forEach(node => {
            const rect = node.getBoundingClientRect()
            minX = Math.min(minX, rect.left)
            minY = Math.min(minY, rect.top)
            maxX = Math.max(maxX, rect.right)
            maxY = Math.max(maxY, rect.bottom)
          })
          
          // 计算内容尺寸和中心点
          const contentWidth = maxX - minX
          const contentHeight = maxY - minY
          const centerX = (minX + maxX) / 2
          const centerY = (minY + maxY) / 2
          
          // 计算缩放比例以适应90%的容器
          const containerWidth = clone.clientWidth
          const containerHeight = clone.clientHeight
          const scaleX = (containerWidth * 0.8) / contentWidth // 80%宽度用于内容
          const scaleY = (containerHeight * 0.8) / contentHeight // 80%高度用于内容
          const scale = Math.min(scaleX, scaleY, 1) // 取最小值，不超过1
          
          // 应用变换使内容居中
          const transform = `translate(${containerWidth/2 - centerX * scale}px, ${containerHeight/2 - centerY * scale}px) scale(${scale})`
          svgElement.style.transform = transform
          svgElement.style.transformOrigin = '0 0'
        }
      } catch (error) {
        console.warn('节点居中计算失败:', error)
      }
    }, 100)
  }
  
  hiddenContainer.appendChild(clone)
  return hiddenContainer
}

/**
 * 备选方案：直接截图小地图并处理样式（使用onclone不修改原始元素）
 */
const captureMiniMapDirect = async (miniMapElement: HTMLElement): Promise<string | null> => {
  try {
    console.log('尝试直接截图方法...')
    
    // 创建临时容器用于居中显示
    const tempContainer = document.createElement('div')
    tempContainer.style.position = 'fixed'
    tempContainer.style.left = '-9999px'
    tempContainer.style.top = '-9999px'
    tempContainer.style.width = '800px'
    tempContainer.style.height = '450px'
    tempContainer.style.backgroundColor = '#ffffff'
    tempContainer.style.display = 'flex'
    tempContainer.style.alignItems = 'center'
    tempContainer.style.justifyContent = 'center'
    tempContainer.style.overflow = 'hidden'
    
    const clone = miniMapElement.cloneNode(true) as HTMLElement
    clone.style.width = '90%'
    clone.style.height = '90%'
    clone.style.margin = '0'
    clone.style.padding = '0'
    
    tempContainer.appendChild(clone)
    document.body.appendChild(tempContainer)
    
    const canvas = await html2canvas(tempContainer, {
      backgroundColor: '#ffffff',
      scale: 2,
      useCORS: true,
      allowTaint: false,
      logging: true,
      width: 800,
      height: 450,
      onclone: (clonedDocument, element) => {
        // 在克隆的文档中修改样式，不影响原始元素
        const clonedMiniMap = element.querySelector('.vue-flow__minimap') as HTMLElement
        const clonedSvg = clonedMiniMap?.querySelector('svg') as SVGSVGElement
        
        if (clonedMiniMap) {
          clonedMiniMap.style.background = '#ffffff'
          clonedMiniMap.style.backgroundColor = '#ffffff'
          clonedMiniMap.style.border = 'none'
          clonedMiniMap.style.boxShadow = 'none'
          clonedMiniMap.style.width = '100%'
          clonedMiniMap.style.height = '100%'
        }
        
        if (clonedSvg) {
          clonedSvg.style.background = '#ffffff'
          clonedSvg.style.backgroundColor = '#ffffff'
          
          // 移除遮罩元素
          const mask = clonedSvg.querySelector('.vue-flow__minimap-mask')
          if (mask) mask.remove()
          
          const background = clonedSvg.querySelector('.vue-flow__minimap-background')
          if (background) background.remove()
          
          // 增强节点和边的可见性
          const nodes = clonedSvg.querySelectorAll('.vue-flow_minimap-node')
          nodes.forEach(node => {
            const n = node as SVGRectElement
            const currentFill = n.getAttribute('fill')
            if (!currentFill || currentFill === '#ccc' || currentFill === '#d1d1d1') {
              n.setAttribute('fill', '#555555')
            }
            if (!n.getAttribute('stroke') || n.getAttribute('stroke') === 'transparent') {
              n.setAttribute('stroke', '#222222')
              n.setAttribute('stroke-width', '1.5')
            }
          })
          
          const paths = clonedSvg.querySelectorAll('path')
          paths.forEach(path => {
            const p = path as SVGPathElement
            const currentStroke = p.getAttribute('stroke')
            if (!currentStroke || currentStroke === '#b1b1b7') {
              p.setAttribute('stroke', '#333333')
            }
            if (!p.getAttribute('stroke-width') || p.getAttribute('stroke-width') === '1') {
              p.setAttribute('stroke-width', '2')
            }
          })
        }
      }
    })
    
    document.body.removeChild(tempContainer)
    console.log('直接截图方法成功')
    return canvas.toDataURL('image/png')
  } catch (error) {
    console.error('直接截图方法失败:', error)
    return null
  }
}

/**
 * 小地图截图功能 - 纯白色背景，节点居中显示
 */
export const captureMiniMap = async (vueFlowRef: any): Promise<string | null> => {
  if (!vueFlowRef) {
    console.error('未找到VueFlow容器')
    return null
  }
  
  try {
    // 获取小地图元素
    const miniMapElement = vueFlowRef.querySelector('.vue-flow__minimap') as HTMLElement
    if (!miniMapElement) {
      console.error('未找到小地图元素')
      return null
    }

    console.log('开始截图小地图...')
    
    let imageData: string | null = null
    
    // 先尝试直接截图方法（不修改原始元素）
    imageData = await captureMiniMapDirect(miniMapElement)
    
    // 如果直接截图失败，尝试克隆方法
    if (!imageData) {
      console.log('直接截图失败，尝试克隆方法...')
      const hiddenContainer = createWhiteBackgroundMiniMap(miniMapElement)
      document.body.appendChild(hiddenContainer)
      
      // 等待渲染和变换应用
      await new Promise(resolve => setTimeout(resolve, 300))
      
      try {
        const canvas = await html2canvas(hiddenContainer, {
          backgroundColor: '#ffffff',
          scale: 2,
          useCORS: true,
          allowTaint: false,
          logging: true,
          width: 800,
          height: 450
        })
        
        imageData = canvas.toDataURL('image/png')
        console.log('克隆方法截图成功')
      } catch (error) {
        console.error('克隆方法也失败:', error)
      } finally {
        // 清理
        if (document.body.contains(hiddenContainer)) {
          document.body.removeChild(hiddenContainer)
        }
      }
    }
    
    return imageData
    
  } catch (error) {
    console.error('小地图截图失败:', error)
    return null
  }
}

/**
 * 保存截图到本地
 */
export const saveScreenshot = (imageData: string, projectId: string): void => {
  try {
    const link = document.createElement('a')
    link.href = imageData
    link.download = `flow-diagram-${projectId}-${Date.now()}.png`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    console.log('流程图截图已保存')
  } catch (error) {
    console.error('保存截图失败:', error)
  }
}

/**
 * 自动截图并保存
 */
export const autoCaptureMinimapAndSave = async (vueFlowRef: any, projectId: string): Promise<void> => {
  try {
    console.log('开始自动截图...')
    const imageData = await captureMiniMap(vueFlowRef)
    if (imageData) {
      saveScreenshot(imageData, projectId)
      console.log('自动截图完成')
    } else {
      console.error('截图失败，返回的imageData为null')
    }
  } catch (error) {
    console.error('自动截图失败:', error)
  }
}