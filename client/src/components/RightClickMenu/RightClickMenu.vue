<script lang="ts" setup>
import { useGraphStore } from '@/stores/graphStore'
import { ref, computed, nextTick, onMounted, onBeforeUnmount } from 'vue'
import { nodeMenuItems, type MenuNode } from '@/components/RightClickMenu/menuTypes'
import { useVueFlow } from '@vue-flow/core'
import SubMenu from './SubMenu.vue'
// 图标
//@ts-ignore
import SvgIcon from '@jamescoyle/vue-icon'
import { mdiAlphabeticalVariant, mdiChartScatterPlot, mdiFileOutline, mdiImport, mdiMathCompass, mdiRulerSquare, mdiTable, mdiTimerOutline, mdiSchoolOutline, mdiSourceFork } from '@mdi/js'

const graphStore = useGraphStore()
const { addNode } = graphStore

// 菜单状态
const showMenu = ref(false)
const menuX = ref(0)
const menuY = ref(0)
const menuRoot = ref<HTMLElement | null>(null)
const openSubmenuIndex = ref<number | null>(null)
const menuItemRefs = ref<Array<HTMLElement | null>>([])
const submenuAnchorRect = ref<DOMRect | null>(null)
const isMenuClosing = ref(false)

const setMenuItemRef = (el: unknown, idx: number) => {
  menuItemRefs.value[idx] = (el as HTMLElement) || null
}

const { onPaneContextMenu, screenToFlowCoordinate } = useVueFlow('main')

// 绑定面板右键事件
onPaneContextMenu((e: MouseEvent) => {
  showContextMenu(e)
})

// 绑定节点右键事件
const onNodeContextMenu = (e: CustomEvent) => {
  const { event, node } = e.detail
  showContextMenu(event, node)
}

// 显示右键菜单
const showContextMenu = (event: MouseEvent, node?: any) => {
  event.preventDefault()
  menuX.value = event.clientX
  menuY.value = event.clientY
  showMenu.value = false
  openSubmenuIndex.value = null

  setTimeout(async () => {
    showMenu.value = true
    await nextTick()
    menuRoot.value?.focus()
  }, 10)
}

// 选择节点
const selectNode = (nodeType: string) => {
  const flowPos = screenToFlowCoordinate({ x: menuX.value, y: menuY.value })
  addNode(nodeType, { x: flowPos.x, y: flowPos.y })
  hideMenu()
}

// 处理菜单项点击
const handleItemClick = (item: MenuNode) => {
  if (!item.children || item.children.length === 0) {
    selectNode(item.value)
  }
}

// 打开子菜单
const openSubmenu = (index: number) => {

  if (nodeMenuItems[index]?.children?.length) {
    openSubmenuIndex.value = index
    const el = menuItemRefs.value[index]
    if (el) {
      submenuAnchorRect.value = el.getBoundingClientRect()
    }
  }
}

// 隐藏菜单
const hideMenu = () => {
  if (menuRoot.value && !isMenuClosing.value) {
    isMenuClosing.value = true
    menuRoot.value.classList.add('closing')
    // 等待退出动画完成后再卸载
    setTimeout(() => {
      showMenu.value = false
      openSubmenuIndex.value = null
      isMenuClosing.value = false
    }, 120)
  }
}

// 子菜单方向
const submenuDirection = computed(() =>
  menuX.value > window.innerWidth - 350 ? 'left' : 'right'
)

// 根据菜单项的 value 映射到图标路径
const getIconPath = (value: string) => {
  switch (value) {
    case 'input':
      return mdiImport
    case 'compute':
      return mdiMathCompass
    case 'control':
      return mdiSourceFork
    case 'file':
      return mdiFileOutline
    case 'stringProcessing':
    case 'stringProcess':
      return mdiAlphabeticalVariant
    case 'tableProcessing':
    case 'tableProcess':
      return mdiTable
    case 'datetimeProcess':
      return mdiTimerOutline
    case 'analysis':
      return mdiRulerSquare
    case 'visualization':
    case 'visualize':
      return mdiChartScatterPlot
    case 'machineLearning':
      return mdiSchoolOutline
    default:
      return null
  }
}

// 菜单样式
const menuStyle = computed(() => {
  const width = 160
  const offsetX = 15
  let left = menuX.value + offsetX
  if (left + width > window.innerWidth) {
    left = menuX.value - width - offsetX // 防止超出屏幕
  }
  let top = menuY.value
  const approxHeight = 36 * nodeMenuItems.length
  if (menuY.value + approxHeight > window.innerHeight) {
    top = Math.max(8, window.innerHeight - approxHeight - 8)
  }
  return `position: fixed; left: ${left}px; top: ${top}px; z-index: 9999; min-width: ${width}px;`
})

// 全局点击监听：点击菜单外才关闭菜单
const onGlobalClick = (e: MouseEvent) => {
  if (!showMenu.value || isMenuClosing.value) return

  // 检查点击是否在主菜单内
  const menuRect = menuRoot.value?.getBoundingClientRect()
  if (menuRect && e.clientX >= menuRect.left && e.clientX <= menuRect.right && e.clientY >= menuRect.top && e.clientY <= menuRect.bottom) {
    return // 在主菜单内，不关闭
  }

  // 检查点击是否在任何子菜单内
  const portals = document.querySelectorAll('.submenu-portal')
  for (let i = 0; i < portals.length; i++) {
    const portal = portals[i]
    if (portal) {
      const portalRect = portal.getBoundingClientRect()
      if (e.clientX >= portalRect.left && e.clientX <= portalRect.right && e.clientY >= portalRect.top && e.clientY <= portalRect.bottom) {
        return // 在子菜单内，不关闭
      }
    }
  }

  // 点击在菜单外，关闭菜单
  hideMenu()
}

onMounted(() => {
  document.addEventListener('click', onGlobalClick)
  // 添加节点右键事件监听器
  window.addEventListener('node-contextmenu', onNodeContextMenu as EventListener)
})

onBeforeUnmount(() => {
  document.removeEventListener('click', onGlobalClick)
  // 移除节点右键事件监听器
  window.removeEventListener('node-contextmenu', onNodeContextMenu as EventListener)
})
</script>

<template>
  <!-- 菜单容器 -->
  <div
    v-if="showMenu"
    ref="menuRoot"
    class="context-menu"
    :style="menuStyle"
    @keydown.esc="hideMenu"
    tabindex="-1"
  >
    <ul class="menu-list">
      <li
        v-for="(item, index) in nodeMenuItems"
        :key="item.value"
        class="menu-item"
        :ref="el => setMenuItemRef(el, index)"
        @mouseenter="openSubmenu(index)"
      >
        <div
          class="menu-item-content"
          @click="handleItemClick(item)"
        >
          <svg-icon v-if="getIconPath(item.value)" type="mdi" :path="getIconPath(item.value)"class="menu-icon" />
          <span class="menu-label">{{ item.label }}</span>
          <span v-if="item.children?.length" class="submenu-arrow">
              <svg width="10" height="10" viewBox="0 0 8 8">
              <path d="M2 1 L6 4 L2 7" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
          </span>
        </div>

        <!-- 子菜单 -->
        <SubMenu
          v-if="item.children?.length && openSubmenuIndex === index"
          :items="item.children"
          :direction="submenuDirection"
          :on-select="selectNode"
          :anchor-rect="submenuAnchorRect"
          :parent-category="item.value"
        />
      </li>
    </ul>
  </div>
</template>

<style scoped lang="scss">
@use '../../common/global.scss' as *;

.context-menu {
  @include controller-style;
  padding: 4px 4px;
  box-sizing: border-box;
  outline: none;
  /* 进入动画：淡入并轻微向下移动 */
  animation: menu-fade-in 200ms cubic-bezier(.2,.8,.2,1) both;
}

.context-menu.closing {
  animation: menu-fade-out 150ms cubic-bezier(.2,.8,.2,1) both;
}

.menu-list {
  list-style: none;
  margin: 0;
  padding: 0;
}

.menu-item {
  position: relative;
}

.menu-item-content {
  padding: 6px 12px;
  margin: 0;
  cursor: pointer;
  display: flex;
  justify-content: flex-start;
  align-items: center;
  gap: 8px;
  border-radius: 8px;
  transition: background-color 0.15s ease;
}

.menu-icon {
  display: inline-flex;
  width: 20px;
  opacity: 0.7;
  color: inherit;
}

.menu-item-content:hover {
  background-color: rgba(0, 0, 0, 0.1);
}

.menu-label {
  font-size: 14px;
  font-weight: 400;
  flex: 1 1 auto;
  text-align: left;
}

.submenu-arrow {
  display: inline-flex;
  align-items: center;
  margin-left: auto; /* 将箭头推到最右侧 */
  color: inherit; /* 继承文字颜色 */
  width: 9px;
  height: 9px;
}
.submenu-arrow svg {
  display: block;
  width: 100%;
  height: 100%;
}
.submenu-arrow path {
  stroke: currentColor;
  opacity: 0.40;
}

@keyframes menu-fade-in {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
    width: auto;
    height: auto;
  }
}

@keyframes menu-fade-out {
  from {
    opacity: 1;
    transform: translateY(0);
  }
  to {
    opacity: 0;
    transform: translateY(-10px);
  }
}
</style>