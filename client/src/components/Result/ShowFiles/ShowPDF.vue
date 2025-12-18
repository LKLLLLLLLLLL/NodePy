<script lang="ts" setup>
import { ref } from 'vue'
import VuePdfEmbed from 'vue-pdf-embed'

const props = defineProps<{
  src: string
}>()

const pageCount = ref<number>(0)

const handlePdfLoad = (pdf: any) => {
  pageCount.value = pdf.numPages
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
          @loaded="handlePdfLoad"
          @error="handlePdfError"
          class="pdf-embed"
        />
      </div>
    </div>
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
  display: flex;
  justify-content: center;
  align-items: flex-start;
  /* 修复滚动条问题 */
  scrollbar-gutter: stable; /* 保持滚动条空间一致 */
}

.pdf-center {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
  /* 添加最小宽度以确保内容正确显示 */
  min-width: fit-content;
}

.pdf-embed {
  width: 100%;
  /* 确保PDF适应容器 */
  object-fit: contain;
  margin-bottom: 20px;
}
</style>