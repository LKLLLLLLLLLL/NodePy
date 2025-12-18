<script lang="ts" setup>
import { computed, ref, onMounted, onUnmounted } from 'vue'

const props = defineProps<{
  data: string
}>()

// 显示所有行，不再分页
const txtLines = computed(() => {
  // 使用 split('\n') 会保留空行
  const lines = props.data.split('\n')
  return lines
})

// 添加防抖定时器
let resizeTimer: number | null = null;

// 处理窗口大小变化 - 使用防抖优化性能
const handleWindowResize = () => {
  // 清除之前的resize定时器
  if (resizeTimer) {
    clearTimeout(resizeTimer);
  }
  
  // 使用防抖延迟来减少resize事件的影响
  resizeTimer = window.setTimeout(() => {
    // 在这里可以执行一些必要的更新操作
    // 但由于我们使用了CSS的pre-wrap，实际上不需要做特殊处理
    console.log('窗口大小已稳定');
  }, 0); // 300ms防抖延迟
};

// 组件挂载时添加事件监听器
onMounted(() => {
  window.addEventListener('resize', handleWindowResize, { passive: true });
});

// 组件卸载时清理
onUnmounted(() => {
  window.removeEventListener('resize', handleWindowResize);
  // 清理定时器
  if (resizeTimer) {
    clearTimeout(resizeTimer);
  }
});
</script>

<template>
  <div class="txt-view">
    <div class="txt-content">
      <!-- 显示所有行 -->
      <div v-for="(line, index) in txtLines" :key="index" class="txt-line">
        <span v-if="line === ''">&nbsp;</span>
        <span v-else>{{ line }}</span>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
@use '../../../common/global.scss' as *;
.txt-view {
  flex: 1;
  overflow: hidden; /* 改为hidden，让内部控制滚动 */
  background: white;
  border-radius: 10px;
  padding: 12px;
  display: flex;
  flex-direction: column;
  height: 100%; /* 确保占满容器高度 */
  @include controller-style;
  /* 优化渲染性能 */
  transform: translateZ(0);
  backface-visibility: hidden;
}

.txt-content {
  flex: 1;
  overflow: auto; /* 让内容区域控制滚动 */
  font-family: 'Courier New', Consolas, Monaco, monospace;
  white-space: pre-wrap; /* 允许自动换行 */
  word-wrap: break-word; /* 允许长单词换行 */
  line-height: 1.5;
  /* 修复滚动条问题 */
  scrollbar-gutter: stable; /* 保持滚动条空间一致 */
  padding: 8px; /* 添加一些内边距 */
  box-sizing: border-box;
  /* 优化渲染性能 */
  transform: translateZ(0);
  backface-visibility: hidden;
  /* 使用contain属性优化渲染性能 */
  contain: layout style paint;
}

.txt-line {
  margin: 0;
  padding: 2px 0;
  font-family: inherit;
  /* 确保空行也能正确显示 */
  min-height: 1.2em;
  /* 不再强制每行占据整行 */
  display: block;
  /* 优化渲染性能 */
  transform: translateZ(0);
  backface-visibility: hidden;
  /* 使用contain属性优化渲染性能 */
  contain: layout style;
}
</style>