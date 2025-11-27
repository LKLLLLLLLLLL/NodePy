<script lang="ts" setup>
import { ref, computed } from 'vue'

const props = defineProps<{
  data: string
}>()

const txtLinesPerPage = 50
const txtCurrentPage = ref<number>(1)

const txtLines = computed(() => {
  return props.data.split('\n')
})

const txtTotalPages = computed(() => Math.ceil(txtLines.value.length / txtLinesPerPage))

const txtCurrentPageContent = computed(() => {
  const start = (txtCurrentPage.value - 1) * txtLinesPerPage
  const end = start + txtLinesPerPage
  return txtLines.value.slice(start, end)
})

// TXT 分页 - 上一页
const txtPrevPage = () => {
  if (txtCurrentPage.value > 1) {
    txtCurrentPage.value--
  }
}

// TXT 分页 - 下一页
const txtNextPage = () => {
  if (txtCurrentPage.value < txtTotalPages.value) {
    txtCurrentPage.value++
  }
}

// TXT 分页 - 跳转到指定页
const txtGoToPage = (page: number) => {
  if (page >= 1 && page <= txtTotalPages.value) {
    txtCurrentPage.value = page
  }
}
</script>

<template>
  <div class="txt-view">
    <div class="txt-content">
      <pre v-for="(line, index) in txtCurrentPageContent" :key="index" class="txt-line">{{ line }}</pre>
    </div>
    <!-- TXT 分页控件 -->
    <div v-if="txtTotalPages > 1" class="txt-pagination">
      <button 
        class="pagination-btn" 
        :disabled="txtCurrentPage <= 1" 
        @click="txtPrevPage"
      >
        上一页
      </button>
      <span class="page-info">
        第 {{ txtCurrentPage }} 页 / 共 {{ txtTotalPages }} 页
      </span>
      <button 
        class="pagination-btn" 
        :disabled="txtCurrentPage >= txtTotalPages" 
        @click="txtNextPage"
      >
        下一页
      </button>
      <div class="page-input-container">
        <input 
          type="number" 
          v-model.number="txtCurrentPage" 
          min="1" 
          :max="txtTotalPages"
          class="page-input"
          @change="txtGoToPage(txtCurrentPage)"
        />
        <button 
          class="go-btn" 
          @click="txtGoToPage(txtCurrentPage)"
        >
          跳转
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.txt-view {
  flex: 1;
  overflow: auto;
  background: white;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  padding: 12px;
  margin: 12px;
  display: flex;
  flex-direction: column;
}

.txt-content {
  flex: 1;
  overflow: auto;
  font-family: 'Courier New', Consolas, Monaco, monospace;
  white-space: pre-wrap;
  word-wrap: break-word;
  line-height: 1.5;
}

.txt-line {
  margin: 0;
  padding: 2px 0;
  font-family: inherit;
}

.txt-pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 12px 0;
  flex-wrap: wrap;
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