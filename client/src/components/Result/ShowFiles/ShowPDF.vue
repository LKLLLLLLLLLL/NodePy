<script lang="ts" setup>
import { ref, computed } from 'vue'
import VuePdfEmbed from 'vue-pdf-embed'
import Pagination from '@/components/Pagination/Pagination.vue'

const props = defineProps<{
  src: string
}>()

const currentPage = defineModel<number>('currentPage', { default: 1 })
const pageCount = ref<number>(0)

const handlePdfLoad = (pdf: any) => {
  pageCount.value = pdf.numPages
  // 如果当前页超出范围，则重置为第一页
  if (currentPage.value > pageCount.value) {
    currentPage.value = 1
  }
}

const handlePdfError = (error: any) => {
  console.error('PDF加载失败:', error)
}
</script>

<template>
  <div class="pdf-view">
    <div class="pdf-content">
      <div class="pdf-center">
        <VuePdfEmbed
          :source="src"
          :page="currentPage"
          @loaded="handlePdfLoad"
          @error="handlePdfError"
          class="pdf-embed"
        />
      </div>
    </div>
    
    <!-- 使用统一的分页组件 -->
    <Pagination 
      v-if="pageCount > 1"
      v-model:currentPage="currentPage"
      :total-pages="pageCount"
      class="pdf-pagination"
    />
  </div>
</template>

<style scoped lang="scss">
@use '../../../common/global.scss' as *;
.pdf-view {
  flex: 1;
  overflow: hidden;
  background: white;
  border-radius: 10px;
  padding: 12px;
  display: flex;
  flex-direction: column;
  position: relative;
  height: 100%; /* 确保占满容器高度 */
  @include controller-style;
}

.pdf-content {
  flex: 1;
  overflow: auto;
  margin-bottom: 12px;
  display: flex;
  justify-content: center;
  align-items: flex-start;
  /* 修复滚动条问题 */
  scrollbar-gutter: stable; /* 保持滚动条空间一致 */
}

.pdf-center {
  display: flex;
  flex: 1;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
  /* 添加最小宽度以确保内容正确显示 */
  min-width: fit-content;
}

.pdf-embed {
  display: flex;
  flex: 1;
  width: 100%;
  height: 100%;
  /* 确保PDF适应容器 */
  object-fit: contain;
}

.pdf-pagination {
  margin: 0;
  padding: 12px 0 0 0;
  border-top: 1px solid #ebeef5;
}
</style>