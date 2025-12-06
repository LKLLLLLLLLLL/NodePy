<script lang="ts" setup>
import { ref, computed } from 'vue'
import VuePdfEmbed from 'vue-pdf-embed'

const props = defineProps<{
  src: string
}>()

const currentPage = ref<number>(1)
const pageCount = ref<number>(0)
const inputPage = ref<number>(1) // 用于存储输入框的值

const handlePdfLoad = (pdf: any) => {
  pageCount.value = pdf.numPages
  // 如果当前页超出范围，则重置为第一页
  if (currentPage.value > pageCount.value) {
    currentPage.value = 1
  }
  // 同步输入框的值
  inputPage.value = currentPage.value
}

const handlePdfError = (error: any) => {
  console.error('PDF加载失败:', error)
}

// 切换到上一页
const prevPage = () => {
  if (currentPage.value > 1) {
    currentPage.value--
    inputPage.value = currentPage.value
  }
}

// 切换到下一页
const nextPage = () => {
  if (currentPage.value < pageCount.value) {
    currentPage.value++
    inputPage.value = currentPage.value
  }
}

// 跳转到指定页
const goToPage = (page: number) => {
  if (page >= 1 && page <= pageCount.value) {
    currentPage.value = page
  }
}

// 更新输入框的值，但不立即跳转
const updateInputPage = (event: Event) => {
  const target = event.target as HTMLInputElement
  const page = parseInt(target.value) || 1
  inputPage.value = Math.max(1, Math.min(page, pageCount.value))
}

// 点击跳转按钮时才真正跳转
const handleGoButtonClick = () => {
  goToPage(inputPage.value)
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
    <!-- PDF 分页控件 -->
    <div v-if="pageCount > 1" class="pdf-pagination">
      <button 
        class="pagination-btn" 
        :disabled="currentPage <= 1" 
        @click="prevPage"
      >
        上一页
      </button>
      <span class="page-info">
        第 {{ currentPage }} 页 / 共 {{ pageCount }} 页
      </span>
      <button 
        class="pagination-btn" 
        :disabled="currentPage >= pageCount" 
        @click="nextPage"
      >
        下一页
      </button>
      <div class="page-input-container">
        <input 
          type="number" 
          :value="inputPage" 
          min="1" 
          :max="pageCount"
          class="page-input"
          @input="updateInputPage"
        />
        <button 
          class="go-btn" 
          @click="handleGoButtonClick"
        >
          跳转
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.pdf-view {
  flex: 1;
  overflow: hidden;
  background: white;
  border: 1px solid #e4e7ed;
  border-radius: 10px;
  padding: 12px;
  display: flex;
  flex-direction: column;
  position: relative;
}

.pdf-content {
  flex: 1;
  overflow: auto;
  margin-bottom: 12px;
  display: flex;
  justify-content: center;
  align-items: flex-start;
}

.pdf-center {
  display: flex;
  flex: 1;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
}

.pdf-embed {
  display: flex;
  flex: 1;
  width: 100%;
  height: 100%;
}

.pdf-pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 12px 0;
  flex-wrap: wrap;
  bottom: 0;
  background: white;
  border-top: 1px solid #e4e7ed;
  margin: 0 -12px -12px -12px;
  padding: 12px;
  z-index: 10;
}

.pagination-btn {
  padding: 6px 12px;
  border: 1px solid #dcdfe6;
  background: white;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s;
}

.pagination-btn:hover:not(:disabled) {
  background: #ecf5ff;
  border-color: #409eff;
  color: #409eff;
}

.pagination-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-info {
  font-size: 14px;
  color: #606266;
  white-space: nowrap;
}

.page-input-container {
  display: flex;
  align-items: center;
  gap: 8px;
}

.page-input {
  width: 60px;
  padding: 6px 12px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  text-align: center;
}

.go-btn {
  padding: 6px 12px;
  border: 1px solid #409eff;
  background: #409eff;
  color: white;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s;
}

.go-btn:hover {
  background: #66b1ff;
  border-color: #66b1ff;
}
</style>