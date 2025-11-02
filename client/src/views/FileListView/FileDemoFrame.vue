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
                文件名：{{ file.filename }}
            </div>
        </div>
        <div class="file-middle">
            <div class="fileinfo filepname-container">
                所属项目：{{ file.project_name }}
            </div>
            <div class="fileinfo filesize-container">
                文件大小：{{ file.size }}MB
            </div>
            <div class="fileinfo filemodifiedat-container">
                上次修改：{{ file.modified_at }}
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
    .file-container{
        display: flex;
        flex-direction: row;
        height: 75px;
        background-color: white;
        border-radius: 8px;
        border: 2px solid black;
    }
    .file-left{
        display: flex;
        align-items: center;
        justify-content: center;
        width: 200px;
    }
    .file-middle{
        flex: 1;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .file-right{
        display: flex;
        align-items: center;
        justify-content: center;
        width: 200px;
    }
    .fileinfo{
        width: 200px;
    }
    .filename-container{
        flex: 1;
    }
    .file-container-new{
        display: flex;
        align-items: center;
        justify-content: center;
        height: 75px;
        background-color: white;
        border-radius: 8px;
        border: 2px solid black;
    }
</style>