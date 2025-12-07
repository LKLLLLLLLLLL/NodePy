<script lang="ts" setup>
import { ref, computed } from 'vue'

const props = defineProps<{
  data: string
}>()

const txtLinesPerPage = 50
const txtCurrentPage = ref<number>(1)
const inputPage = ref<number>(1) // 用于存储输入框的值

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

// TXT 分页 - 上一页
const txtPrevPage = () => {
  if (txtCurrentPage.value > 1) {
    txtCurrentPage.value--
    inputPage.value = txtCurrentPage.value
  }
}

// TXT 分页 - 下一页
const txtNextPage = () => {
  if (txtCurrentPage.value < txtTotalPages.value) {
    txtCurrentPage.value++
    inputPage.value = txtCurrentPage.value
  }
}

// TXT 分页 - 跳转到指定页
const txtGoToPage = (page: number) => {
  if (page >= 1 && page <= txtTotalPages.value) {
    txtCurrentPage.value = page
  }
}

// 更新输入框的值，但不立即跳转
const updateInputPage = (event: Event) => {
  const target = event.target as HTMLInputElement
  const page = parseInt(target.value) || 1
  inputPage.value = Math.max(1, Math.min(page, txtTotalPages.value))
}

// 点击跳转按钮或按回车键时才真正跳转
const handleGoButtonClick = () => {
  txtGoToPage(inputPage.value)
}

// 处理回车键跳转
const handleInputEnter = (event: KeyboardEvent) => {
  if (event.key === 'Enter') {
    handleGoButtonClick()
  }
}
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
          :value="inputPage" 
          min="1" 
          :max="txtTotalPages"
          class="page-input"
          @input="updateInputPage"
          @keyup="handleInputEnter"
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
.txt-view {
  flex: 1;
  overflow: hidden; /* 改为hidden，让内部控制滚动 */
  background: white;
  border: 1px solid #e4e7ed;
  border-radius: 10px;
  padding: 12px;
  display: flex;
  flex-direction: column;
  height: 100%; /* 确保占满容器高度 */
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
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 12px 0;
  flex-wrap: wrap;
  border-top: 1px solid #e4e7ed;
  margin: 12px -12px -12px -12px;
  padding: 12px;
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
}
</style>