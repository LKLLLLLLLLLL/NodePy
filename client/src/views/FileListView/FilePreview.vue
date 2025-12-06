<script lang="ts" setup>
import { ref, computed, watch } from 'vue';
import { useFileStore } from '@/stores/fileStore';
import { type File, type TableView } from '@/utils/api';
import FileView from '@/components/Result/FileView.vue';
import Loading from '@/components/Loading.vue';

const fileStore = useFileStore();

const toBePreviewed = computed(() => {
    return fileStore.currentFile;
});

const previewFile = ref<File | null>(null);
const loading = ref(false);
const error = ref<string>('');

// 监听 toBePreviewed 的变化
watch(toBePreviewed, async (newFile) => {
    // 重置状态
    previewFile.value = null;
    loading.value = false;
    error.value = '';

    // 只有当newFile存在且key非空时才处理
    if (newFile && newFile.key && newFile.key !== 'loading') {
        try {
            loading.value = true;
            // 预加载文件内容到缓存
            await fileStore.getCacheContent(newFile.key);
            // 传递有效的文件对象
            previewFile.value = newFile;
        } catch (err) {
            error.value = '获取文件内容失败';
            console.error('FilePreview: 获取文件内容失败', err);
            // 出错时也传递文件对象，让 FileView 处理错误
            previewFile.value = newFile;
        } finally {
            loading.value = false;
        }
    } else {
        // 如果没有有效的文件，传递 null
        previewFile.value = null;
        loading.value = false;
    }
}, { immediate: true });
</script>

<template>
    <div class="file-preview-container">
        <!-- 显示loading状态 -->
        <div v-if="loading" class="file-loading">
            <Loading></Loading>
            <span>加载中...</span>
        </div>

        <!-- 显示错误信息 -->
        <div v-else-if="error" class="file-error">
            {{ error }}
        </div>

        <!-- 显示文件内容 -->
        <div v-else class="file-content">
            <FileView :value="previewFile"></FileView>
        </div>
    </div>
</template>

<style scoped>
.file-preview-container {
    padding-top: 10px;
    display: flex;
    flex-direction: column;
    height: 100%;
}

.file-content {
    flex: 1;
    border-radius: 10px;
    overflow: hidden;
    background: transparent;
}

.file-loading {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100%;
    gap: 12px;
}

.file-error {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100%;
    color: #f56c6c;
    font-size: 14px;
    padding: 20px;
    text-align: center;
}
</style>