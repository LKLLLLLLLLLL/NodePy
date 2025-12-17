<script setup lang="ts">
    import { useEditorStore } from '@/stores/editorStore'
    import PyEditor from './PyEditor.vue';
    import { ref, onBeforeUnmount } from 'vue';

    const editorStore = useEditorStore()
    const pyEditorRef = ref<InstanceType<typeof PyEditor> | null>(null)

    // 在点击确定时同步代码到currentScript
    const handleConfirm = () => {
        if (pyEditorRef.value) {
            // 获取PyEditor中的代码
            const code = pyEditorRef.value.getCode();
            // 将代码同步到currentScript
            editorStore.currentScript = code;
        }
        editorStore.confirmChange()
    }

    // 自动在卸载/关闭前保存一次
    onBeforeUnmount(() => {
        handleConfirm();
    })
</script>
<template>
    <div class="pyeditor-modal">
        <div class="pyeditor-container">
            <PyEditor ref="pyEditorRef" :model-value="editorStore.currentScript" @save="handleConfirm"></PyEditor>
        </div>
    </div>
</template>
<style scoped lang="scss">
    .pyeditor-modal {
        display: flex;
        flex: 1 1 auto;
        height: 100%;
        flex-direction: column;
        box-sizing: border-box;
        padding: 10px;
    }

    .pyeditor-container{
        display: flex;
        flex: 1 1 auto;
        min-height: 0; /* 允许子元素收缩并启用内部滚动 */
        overflow: auto; /* 当内容超出时显示滚动条 */
        align-items: stretch;
    }

    /* 让内部编辑器组件填满容器高度 */
    .pyeditor-container > * {
        width: 100%;
        height: 100%;
    }

    .pyeditor-actions{
        display: flex;
        width: 100%;
        height: 50px;
        justify-content: flex-end;
    }

    .cancel-btn, .submit-btn {
            padding: 8px 16px;
            border: 1px solid #6c757d;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;

            &:hover:not(:disabled) {
                opacity: 0.8;
            }

            &:disabled {
                opacity: 0.5;
                cursor: not-allowed;
            }
        }

        .cancel-btn {
            background: white;
            color: #6c757d;
        }

        .submit-btn {
            background: #007bff;
            border-color: #007bff;
            color: white;
        }
</style>
