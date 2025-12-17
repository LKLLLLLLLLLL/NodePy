<script lang="ts" setup>
    import type { FileItem } from '@/utils/api';
    import FileIcon from './FileIcon.vue';
    import { useFileStore } from '@/stores/fileStore';
    import { useModalStore } from '@/stores/modalStore';
    import FilePreview from './FilePreview.vue';
    import FileUpload from './FileUpload.vue';

    const modalStore = useModalStore();
    const fileStore = useFileStore();

    const props = defineProps<{
        file: FileItem;
    }>()

    const previewWidth = 600;
    const previewHeight = 800;
    const uploadWidth = 400;
    const uploadHeight = 600;

    // 格式化文件大小的函数
    const formatFileSize = (bytes: number): string => {
        if (bytes < 1024) {
            return bytes + ' B';
        } else if (bytes < 1024 * 1024) {
            return (bytes / 1024).toFixed(2) + ' KB';
        } else if (bytes < 1024 * 1024 * 1024) {
            return (bytes / (1024 * 1024)).toFixed(2) + ' MB';
        } else {
            return (bytes / (1024 * 1024 * 1024)).toFixed(2) + ' GB';
        }
    }

    // 格式化时间的函数
    const formatDateTime = (timestamp: number): string => {
        const date = new Date(timestamp);
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        const hours = String(date.getHours()).padStart(2, '0');
        const minutes = String(date.getMinutes()).padStart(2, '0');
        const seconds = String(date.getSeconds()).padStart(2, '0');
        return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
    }

    // async function handleDelete(key: string){
    //     fileStore.deleteFile(key)
    // }

    async function handleUpload(){
        modalStore.createModal({
            id: 'upload-file',
            title: '上传文件',
            isActive: true,
            isResizable: false,
            isDraggable: true,
            isModal: true,
            position:{
                x: window.innerWidth / 2 - uploadWidth / 2,
                y: window.innerHeight / 2 - uploadHeight / 2
            },
            size:{
                width: uploadWidth,
                height: uploadHeight
            },
            component: FileUpload
        })
    }

    async function handlePreview(file :any){
        fileStore.changeCurrentFile(file);
        modalStore.createModal({
            id: 'file-preview',
            title: '文件预览',
            isActive: true,
            isResizable: true,
            isDraggable: true,
            isModal: true,
            position:{
                x: window.innerWidth / 2 - previewWidth / 2,
                y: window.innerHeight / 2 - previewHeight / 2
            },
            size:{
                width: previewWidth,
                height: previewHeight
            },
            minSize:{
                width: previewWidth,
                height: previewHeight
            },
            component: FilePreview
        })
    }

    async function handleDownload(file :any){
        // 使用 downloadFile 函数，传入文件的 key 和文件名
        await fileStore.downloadFile(file.key, file.filename);
    }

</script>
<template>
    <div class="file-container" v-if="props.file!=fileStore.default_file">
        <div class="file-left">
            <FileIcon :format="file.format"></FileIcon>
            <div class="filename-container">
                {{ file.filename }}
            </div>
        </div>
        <div class="file-middle">
            <div class="fileinfo filepname-container">
                {{ file.project_name }}
            </div>
            <div class="fileinfo filesize-container">
                {{ formatFileSize(file.size) }}
            </div>
            <div class="fileinfo filemodifiedat-container">
                {{ formatDateTime(file.modified_at) }}
            </div>
        </div>
        <div class="file-right">
            <el-button @click="()=>handlePreview(file)">预览</el-button>
            <el-button @click="()=>handleDownload(file)">下载</el-button>
            <!-- <el-button @click="handleDelete(file.key)">删除</el-button> -->
        </div>
    </div>
    <!-- <div class="file-container-new" v-else @click="handleUpload">
        <el-icon><Plus></Plus></el-icon>
    </div> -->
</template>
<style lang="scss" scoped>
    @use '../../common/global.scss' as *;
    
    .file-container{
        display: flex;
        flex-direction: row;
        height: 75px;
        background-color: $stress-background-color;
        border-radius: 10px;
        margin-bottom: 12px;
        padding: 0 16px;
        align-items: center;
        @include controller-style;
        
        &:hover {
            transform: translateY(-2px);
            box-shadow: 5px 8px 60px rgba(128, 128, 128, 0.15);
            transition: all 0.3s ease;
        }
    }
    
    .file-left{
        display: flex;
        align-items: center;
        justify-content: flex-start;
        width: 200px;
        gap: 16px;
    }
    
    .file-middle{
        flex: 1;
        display: flex;
        align-items: center;
        justify-content: flex-end;
        gap: 32px;
    }
    
    .file-right{
        display: flex;
        align-items: center;
        justify-content: center;
        width: 190px;
    }
    
    .fileinfo{
        color: #4a5568;
        font-size: 14px;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 5px;
    }
    
    .filepname-container{
        width: 200px;
        text-align: center;
    }
    
    .filesize-container{
        width: 120px;
        text-align: center;
    }
    
    .filemodifiedat-container{
        width: 200px;
        text-align: center;
    }
    
    .filename-container{
        flex: 1;
        font-weight: 600;
        color: #2d3748;
        font-size: 16px;
        display: flex;
        align-items: center;
        gap: 5px;
    }
    
    .file-icon {
        width: 16px;
        height: 16px;
    }
    
    .file-container-new{
        display: flex;
        align-items: center;
        justify-content: center;
        height: 75px;
        background-color: $stress-background-color;
        border-radius: 10px;
        border: 2px dashed $stress-color;
        cursor: pointer;
        @include controller-style;
        
        &:hover {
            background-color: rgba($stress-color, 0.05);
            transition: all 0.3s ease;
        }
    }
</style>