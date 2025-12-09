<script lang="ts" setup>
import { ref, computed } from 'vue'
import Pagination from '@/components/Pagination/Pagination.vue'

const props = defineProps<{
  data: string
}>()

const txtLinesPerPage = 50
const txtCurrentPage = defineModel<number>('currentPage', { default: 1 })

// 修改这里以保留空行
const txtLines = computed(() => {
  // 使用 split('\n') 会保留空行，但我们还需要处理末尾的空行情况
  const lines = props.data.split('\n')
  return lines
})

const txtTotalPages = computed(() => Math.ceil(txtLines.value.length / txtLinesPerPage))

const txtCurrentPageContent = computed(() => {
  const start = (txtCurrentPage.value - 1) * txtLinesPerPage
  const end = start + txtLinesPerPage
  return txtLines.value.slice(start, end)
})
</script>

<template>
  <div class="txt-view">
    <div class="txt-content">
      <!-- 修改这里以更好地显示空行，并取消每段占据一行 -->
      <div v-for="(line, index) in txtCurrentPageContent" :key="index" class="txt-line">
        <span v-if="line === ''">&nbsp;</span>
        <span v-else>{{ line }}</span>
      </div>
    </div>
    
    <!-- 使用统一的分页组件 -->
    <Pagination 
      v-if="txtTotalPages > 1"
      v-model:currentPage="txtCurrentPage"
      :total-pages="txtTotalPages"
      class="txt-pagination"
    />
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
}

.txt-line {
  margin: 0;
  padding: 2px 0;
  font-family: inherit;
  /* 确保空行也能正确显示 */
  min-height: 1.2em;
  /* 不再强制每行占据整行 */
  display: block;
}

.txt-pagination {
  margin: 12px 0 0 0;
  padding: 12px 0 0 0;
  border-top: 1px solid #ebeef5;
}
</style>