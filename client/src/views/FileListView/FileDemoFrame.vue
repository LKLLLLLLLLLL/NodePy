<script lang="ts" setup>
    import type { FileItem } from '@/utils/api';
    import { Plus, Edit, Delete, Files } from '@element-plus/icons-vue';
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

    async function handleDelete(key: string){
        fileStore.deleteFile(key)
    }

    async function handleUpload(){
        modalStore.createModal({
            id: 'upload-file',
            title: 'upload-file',
            isActive: true,
            isResizable: false,
            isDraggable: true,
            position:{
                x: 200,
                y: 200
            },
            size:{
                width: 400,
                height: 600
            },
            component: FileUpload
        })
    }

    async function handlePreview(file :any){
        fileStore.changeCurrentFile(file);
        const content = await fileStore.getFileContent(file.key);
        fileStore.addCacheContent(file.key,content);
        console.log(fileStore.getCacheStatus)
        modalStore.createModal({
            id: 'file-preview',
            title: 'flie-preview',
            isActive: true,
            isResizable: false,
            isDraggable: true,
            position:{
                x: 400,
                y: 400
            },
            size:{
                width: 400,
                height: 600
            },
            component: FilePreview
        })
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
                {{ file.size }}MB
            </div>
            <div class="fileinfo filemodifiedat-container">
                {{ file.modified_at }}
            </div>
        </div>
        <div class="file-right">
            <el-button @click="handlePreview(file)">预览</el-button>
            <el-button @click="handleDelete(file.key)">删除</el-button>
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
        justify-content: flex-end;
        width: 200px;
        gap: 8px;
    }
    
    .fileinfo{
        color: #4a5568;
        font-size: 14px;
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