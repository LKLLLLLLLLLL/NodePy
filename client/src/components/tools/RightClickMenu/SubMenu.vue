<script lang="ts" setup>
import { watch, ref } from 'vue'
import { type MenuNode } from '@/types/menuTypes'

interface Props {
  items: MenuNode[]
  direction: 'left' | 'right'
  onSelect: (value: string) => void
  // 父项 DOMRect，用来把子菜单渲染到 body 并定位
  anchorRect: DOMRect | null
}

const props = defineProps<Props>()

const left = ref<number>(0)
const top = ref<number>(0)
const estimatedWidth = 150 // 估算宽度，用于边界修正

const computePosition = () => {
  const rect = props.anchorRect
  if (!rect) return
  const offset = 0 // 子菜单紧贴主菜单，无间隔
  if (props.direction === 'right') {
    left.value = rect.right + offset
  } else {
    left.value = rect.left - estimatedWidth - offset
  }
  // 优化 top：对齐父项顶端
  top.value = rect.top - 4

  // 边界修正
  const winW = window.innerWidth
  const winH = window.innerHeight
  if (left.value + estimatedWidth > winW - 8) left.value = Math.max(8, winW - estimatedWidth - 8)
  if (left.value < 8) left.value = 8
  if (top.value + 48 * props.items.length > winH - 8) top.value = Math.max(8, winH - 48 * props.items.length - 8)
}

watch(() => props.anchorRect, () => {
  computePosition()
}, { immediate: true })

const handleClick = (value: string) => {
  props.onSelect(value)
}

// 声明 mouseleave 为组件事件以消除警告
defineEmits<{
  (e: 'mouseleave'): void
}>()
</script>

<template>
  <teleport to="body">
    <transition name="fade">
      <ul
        v-if="props.anchorRect"
        class="submenu-portal"
        :class="props.direction"
        :style="{ position: 'fixed', left: left + 'px', top: top + 'px', minWidth: estimatedWidth + 'px', zIndex: 20000 }">
        <li
          v-for="item in props.items"
          :key="item.value"
          class="submenu-item"
          @click.stop="handleClick(item.value)"
        >
          {{ item.label }}
        </li>
      </ul>
    </transition>
  </teleport>
</template>

<style lang="scss">
@use '../../../common/style/global.scss' as *;

.submenu-portal {
  @include controller-style;
  list-style: none;
  margin: 0;
  padding: 4px 0;
  background-color: $stress-background-color;
  overflow: visible; // 确保子菜单可以显示
  /* 进入动画：淡入 + 向左平移 */
  animation: submenu-fade-in-right 150ms cubic-bezier(.2,.8,.2,1) both;
}

.submenu-portal.left {
  transform-origin: right top;
  /* 左侧显示时使用相反方向的平移动画 */
  animation: submenu-fade-in-left 150ms cubic-bezier(.2,.8,.2,1) both;
}

.submenu-item {
  padding: 6px 12px;
  cursor: pointer;
  margin: 0;
  font-size: 14px;
  border-radius: 8px;
  transition: background-color 0.150s ease;
}

.submenu-item:hover {
  background-color: rgba(0, 0, 0, 0.1);
}

@keyframes submenu-fade-in-right {
  from {
    opacity: 0;
    transform: translateX(-5px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

@keyframes submenu-fade-in-left {
  from {
    opacity: 0;
    transform: translateX(5px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

@keyframes submenu-fade-out-right {
  from {
    opacity: 1;
    transform: translateX(0);
  }
  to {
    opacity: 0;
    transform: translateX(-5px);
  }
}

@keyframes submenu-fade-out-left {
  from {
    opacity: 1;
    transform: translateX(0);
  }
  to {
    opacity: 0;
    transform: translateX(5px);
  }
}

</style>

