<script setup lang="ts">
import { ref, computed, watch } from 'vue'
// @ts-ignore
import SvgIcon from '@jamescoyle/vue-icon'
import { mdiMenuUp, mdiMenuDown } from '@mdi/js'

const props = defineProps<{
  currentPage: number
  totalPages: number
}>()

const emit = defineEmits<{
  (e: 'update:currentPage', page: number): void
  (e: 'change', page: number): void
}>()

const inputPage = ref<number>(props.currentPage)

// 监听当前页变化，同步输入框
watch(() => props.currentPage, (newVal) => {
  inputPage.value = newVal
})

// 更新输入框的值，但不立即跳转
const updateInputPage = (event: Event) => {
  const target = event.target as HTMLInputElement
  const page = parseInt(target.value) || 1
  inputPage.value = Math.max(1, Math.min(page, props.totalPages))
}

// 点击跳转按钮或按回车键时才真正跳转
const handleGoButtonClick = () => {
  goToPage(inputPage.value)
}

// 处理回车键跳转
const handleInputEnter = (event: KeyboardEvent) => {
  if (event.key === 'Enter') {
    handleGoButtonClick()
  }
}

// 上一页
const prevPage = () => {
  if (props.currentPage > 1) {
    const newPage = props.currentPage - 1
    emit('update:currentPage', newPage)
    emit('change', newPage)
  }
}

// 下一页
const nextPage = () => {
  if (props.currentPage < props.totalPages) {
    const newPage = props.currentPage + 1
    emit('update:currentPage', newPage)
    emit('change', newPage)
  }
}

// 跳转到指定页
const goToPage = (page: number) => {
  if (page >= 1 && page <= props.totalPages && page !== props.currentPage) {
    emit('update:currentPage', page)
    emit('change', page)
  }
}

// 增加页码
const incrementPage = () => {
  const newPage = Math.min(inputPage.value + 1, props.totalPages)
  inputPage.value = newPage
}

// 减少页码
const decrementPage = () => {
  const newPage = Math.max(inputPage.value - 1, 1)
  inputPage.value = newPage
}
</script>

<template>
  <div class="pagination-container">
    <button 
      class="pagination-btn" 
      :disabled="currentPage <= 1" 
      @click="prevPage"
    >
      上一页
    </button>
    <span class="page-info">
      第 {{ currentPage }} 页 / 共 {{ totalPages }} 页
    </span>
    <button 
      class="pagination-btn" 
      :disabled="currentPage >= totalPages" 
      @click="nextPage"
    >
      下一页
    </button>
    <div class="page-input-container">
      <div class="input-wrapper">
        <input 
          type="number" 
          :value="inputPage" 
          min="1" 
          :max="totalPages"
          class="page-input"
          @input="updateInputPage"
          @keyup="handleInputEnter"
        />
      </div>
      <button 
        class="go-btn" 
        @click="handleGoButtonClick"
      >
        跳转
      </button>
    </div>
  </div>
</template>

<style scoped lang="scss">
@use '../../common/global.scss' as *;
.pagination-container {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 12px 0;
  flex-wrap: wrap;
}

.pagination-btn {
  padding: 6px 12px;
  border: 1px solid var(--el-border-color);
  background: var(--el-bg-color);
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s;
  color: var(--el-text-color-primary);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);

  &:hover:not(:disabled) {
    background: var(--el-color-primary-light-9);
    border-color: var(--el-color-primary);
    color: var(--el-color-primary);
    box-shadow: 0 4px 8px rgba(16, 142, 254, 0.1);
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
}

.page-info {
  font-size: 14px;
  color: var(--el-text-color-secondary);
  white-space: nowrap;
}

.page-input-container {
  display: flex;
  align-items: center;
  gap: 8px;
}

.input-wrapper {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.page-input {
  width: 60px;
  padding: 6px 12px;
  border: 1px solid var(--el-border-color);
  border-radius: 4px;
  text-align: center;
  color: var(--el-text-color-primary);
  background: var(--el-bg-color);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);

  &:focus {
    outline: none;
    border-color: var(--el-color-primary);
    box-shadow: 0 0 0 2px rgba(16, 142, 254, 0.2);
  }
}

.go-btn {
  padding: 6px 12px;
  border: 1px solid var(--el-color-primary);
  background: var(--el-color-primary);
  color: white;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: 0 2px 4px rgba(16, 142, 254, 0.2);

  &:hover {
    background: $hover-stress-color;
    border-color: $hover-stress-color;
    box-shadow: 0 4px 8px rgba(16, 142, 254, 0.3);
    transform: translateY(-1px);
  }
}
</style>