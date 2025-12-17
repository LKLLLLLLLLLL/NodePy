<script lang="ts" setup>
    import { computed, ref, onMounted, onUnmounted } from 'vue';
    import { useFileStore } from '@/stores/fileStore';
    import { FileItem } from '@/utils/api';
    import SvgIcon from '@jamescoyle/vue-icon';
    import {
        mdiFileDelimited,
        mdiFileDocument,
        mdiCodeJson,
        mdiFilePdfBox,
        mdiFile
    } from '@mdi/js';

    const props = defineProps<{
        file?: FileItem;
    }>()

    const fileStore = useFileStore();
    const thumbUrl = ref<string | null>(null);
    const loading = ref(false);

    // 文件类型图标映射（Material Design Icons）
    const fileTypeIcon = computed(() => {
        if (!props.file) return mdiFile;

        const format = props.file.format;
        const iconMap: Record<string, string> = {
            [FileItem.format.CSV]: mdiFileDelimited,
            [FileItem.format.TXT]: mdiFileDocument,
            [FileItem.format.JSON]: mdiCodeJson,
            [FileItem.format.PDF]: mdiFilePdfBox,
        };

        return iconMap[format] || mdiFile;
    });

    // 文件类型颜色映射
    const fileTypeColor = computed(() => {
        if (!props.file) return '#6B7F8F';

        const format = props.file.format;
        const colorMap: Record<string, string> = {
            [FileItem.format.CSV]: '#4CAF50',  // 绿色
            [FileItem.format.TXT]: '#2196F3',  // 蓝色
            [FileItem.format.JSON]: '#FF9800', // 橙色
            [FileItem.format.PDF]: '#F44336',  // 红色
        };

        return colorMap[format] || '#6B7F8F';
    });

    const fileTypeName = computed(() => {
        if (!props.file) return '';
        return props.file.format?.toUpperCase() || 'FILE';
    });

    const isImage = computed(() => {
        if (!props.file) return false;
        return [FileItem.format.JPG, FileItem.format.PNG].includes(props.file.format as FileItem.format);
    });

    const isPDF = computed(() => {
        return props.file?.format === FileItem.format.PDF;
    });

    const canShowPreview = computed(() => {
        return isImage.value; // 只为图片显示真实预览，PDF显示图标
    });

    let objectUrl: string | null = null;

    onMounted(async () => {
        // 如果是图片或PDF，尝试加载真实预览
        if (props.file && props.file.key && canShowPreview.value) {
            try {
                loading.value = true;
                const content = await fileStore.getCacheContent(props.file.key);
                if (content instanceof Blob) {
                    objectUrl = URL.createObjectURL(content);
                    thumbUrl.value = objectUrl;
                }
            } catch (err) {
                console.error('FileIcon: 生成缩略图失败', err);
            } finally {
                loading.value = false;
            }
        }
    })

    onUnmounted(() => {
        if (objectUrl) {
            URL.revokeObjectURL(objectUrl);
            objectUrl = null;
        }
    })
</script>

<template>
    <div class="fileicon-container">
        <!-- 加载状态 -->
        <div v-if="loading" class="file-loading">
            <div class="loading-spinner"></div>
        </div>

        <!-- 真实预览图（仅图片） -->
        <template v-else-if="thumbUrl && isImage">
            <img class="file-preview-image" :src="thumbUrl" :alt="file?.filename" />
        </template>

        <!-- 文件类型图标（PDF和其他文件） -->
        <template v-else>
            <div class="file-type-icon">
                <SvgIcon
                    type="mdi"
                    :path="fileTypeIcon"
                    :size="64"
                    class="icon-svg"
                    :style="{ color: fileTypeColor }"
                />
                <div class="icon-label">{{ fileTypeName }}</div>
            </div>
        </template>
    </div>
</template>

<style lang="scss" scoped>
    @use '../../common/global.scss' as *;

    .fileicon-container {
        width: 100%;
        height: 100%;
        display: flex;
        align-items: center;
        justify-content: center;
        background: linear-gradient(135deg, rgba(0, 0, 0, 0.02) 0%, rgba(0, 0, 0, 0.04) 100%);
        overflow: hidden;
        position: relative;
    }

    // 加载状态
    .file-loading {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 100%;
        height: 100%;
    }

    .loading-spinner {
        width: 32px;
        height: 32px;
        border: 3px solid rgba(0, 0, 0, 0.1);
        border-top-color: $stress-color;
        border-radius: 50%;
        animation: spin 0.8s linear infinite;
    }

    @keyframes spin {
        to { transform: rotate(360deg); }
    }

    // 真实预览图
    .file-preview-image {
        width: 100%;
        height: 100%;
        object-fit: cover;
        display: block;
    }

    // 文件类型图标
    .file-type-icon {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        gap: 12px;
        padding: 20px;
    }

    .icon-svg {
        filter: drop-shadow(0 2px 8px rgba(0, 0, 0, 0.08));
        transition: transform 0.2s ease;
    }

    .icon-label {
        font-size: 11px;
        font-weight: 600;
        color: rgba(0, 0, 0, 0.5);
        text-transform: uppercase;
        letter-spacing: 0.8px;
        padding: 4px 10px;
        background: rgba(255, 255, 255, 0.9);
        border-radius: 6px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
    }
</style>
