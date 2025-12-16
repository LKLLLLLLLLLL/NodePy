<!-- FloatingMenu.vue -->
<template>
  <div class="floating-menu-container">
    <!-- 触发元素插槽 -->
    <div
      ref="triggerRef"
      class="floating-menu-trigger"
      @mouseenter="show"
      @mouseleave="hide"
    >
      <slot name="trigger" />
    </div>

    <!-- 浮动菜单 -->
    <Teleport to="body">
      <Transition name="menu-fade">
        <div
          v-if="isVisible"
          ref="menuRef"
          class="floating-menu controller-style"
          :style="menuPosition"
          @mouseenter="show"
          @mouseleave="hide"
        >
          <!-- 菜单内容 -->
          <div class="floating-menu-content">
            <slot />
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'

// 类型定义
interface MenuPosition {
  top: string
  left: string
  [key: string]: string
}

// Props 定义
interface Props {
  placement?: 'top' | 'bottom' | 'left' | 'right'
  offset?: number
  delay?: number
}

const props = withDefaults(defineProps<Props>(), {
  placement: 'bottom',
  offset: 8,
  delay: 0,
})

// 状态
const isVisible = ref(false)
const triggerRef = ref<HTMLElement>()
const menuRef = ref<HTMLElement>()
let hideTimer: ReturnType<typeof setTimeout> | null = null

// 计算菜单位置
const menuPosition = computed<MenuPosition>(() => {
  if (!triggerRef.value) {
    return { top: '0', left: '0' }
  }

  const trigger = triggerRef.value.getBoundingClientRect()
  const menuWidth = menuRef.value?.offsetWidth || 320
  const menuHeight = menuRef.value?.offsetHeight || 300
  const padding = 16 // 距离屏幕边缘的最小间距

  let top = '0'
  let left = '0'

  switch (props.placement) {
    case 'top':
      top = `${trigger.top - menuHeight - props.offset}px`
      left = `${trigger.left + trigger.width / 2 - menuWidth / 2}px`
      break
    case 'bottom':
      top = `${trigger.bottom + props.offset}px`
      left = `${trigger.left + trigger.width / 2 - menuWidth / 2}px`
      break
    case 'left':
      top = `${trigger.top + trigger.height / 2 - menuHeight / 2}px`
      left = `${trigger.left - menuWidth - props.offset}px`
      break
    case 'right':
      top = `${trigger.top + trigger.height / 2 - menuHeight / 2}px`
      left = `${trigger.right + props.offset}px`
      break
  }

  // 转换为数值进行计算
  let topNum = parseFloat(top)
  let leftNum = parseFloat(left)

  // 检查上下边界
  if (topNum < padding) {
    topNum = padding
  } else if (topNum + menuHeight > window.innerHeight - padding) {
    topNum = window.innerHeight - menuHeight - padding
  }

  // 检查左右边界
  if (leftNum < padding) {
    leftNum = padding
  } else if (leftNum + menuWidth > window.innerWidth - padding) {
    leftNum = window.innerWidth - menuWidth - padding
  }

  return {
    top: `${topNum}px`,
    left: `${leftNum}px`,
  }
})

// 显示菜单
const show = () => {
  if (hideTimer) {
    clearTimeout(hideTimer)
    hideTimer = null
  }
  if (props.delay > 0) {
    setTimeout(() => {
      isVisible.value = true
    }, props.delay)
  } else {
    isVisible.value = true
  }
}

// 隐藏菜单
const hide = () => {
  hideTimer = setTimeout(() => {
    isVisible.value = false
  }, 150) // 稍微增加延迟，避免误触
}

// 生命周期
onMounted(() => {
  window.addEventListener('scroll', hide)
  window.addEventListener('resize', hide)
})

onUnmounted(() => {
  window.removeEventListener('scroll', hide)
  window.removeEventListener('resize', hide)
  if (hideTimer) {
    clearTimeout(hideTimer)
  }
})
</script>

<style scoped lang="scss">
@use '../../common/global.scss' as *;

.floating-menu-container {
  display: inline-block;
  position: relative;
  // @include controller-style;
}

.floating-menu-trigger {
  cursor: pointer;
  display: inline-block;
}

.floating-menu {
  position: fixed;
  z-index: 9999;
  border-radius: 12px;
  padding: 0;
  min-width: 200px;
  max-width: 400px;
  pointer-events: auto;
  transform-origin: top center;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(0, 0, 0, 0.05);
  @include controller-style;
  
  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    border-radius: 12px;
    background: linear-gradient(135deg, rgba($stress-color, 0.02), rgba($stress-color, 0.05));
    pointer-events: none;
  }
}

.floating-menu-content {
  position: relative;
  z-index: 1;
  font-size: 14px;
  color: #333;
}

// 过渡动画
.menu-fade-enter-active {
  animation: menu-fade-in 0.2s cubic-bezier(0.4, 0, 0.2, 1) forwards;
}

.menu-fade-leave-active {
  animation: menu-fade-out 0.15s cubic-bezier(0.4, 0, 0.2, 1) forwards;
}

@keyframes menu-fade-in {
  0% {
    opacity: 0;
    transform: scale(0.95) translateY(-5px);
  }
  100% {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

@keyframes menu-fade-out {
  0% {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
  100% {
    opacity: 0;
    transform: scale(0.95) translateY(-5px);
  }
}
</style>