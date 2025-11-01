<script lang="ts" setup>
    import {ref,onMounted} from 'vue';
    import { useFileStore } from '@/stores/fileStore';
    import { useModalStore } from '@/stores/modalStore';
    import FileDemoFrame from './FileDemoFrame.vue';
    import { FileItem } from '@/utils/api';

    const modalStore = useModalStore();
    const fileStore = useFileStore();

    const default_file: FileItem ={
        key: '123',
        filename: 'lkllll',
        format: FileItem.format.PNG,
        size: 100,
        modified_at: 2077,
        project_name: 'default'
    }

    onMounted(()=>{
        fileStore.initializeFiles();
        console.log(fileStore.userFileList);
        console.log(fileStore.userFileList.files)
    })

</script>
<template>
    <div class="fileview-container">
        <div class="left-container">
            我是左侧栏目
        </div>
        <div class="middle-container">
            <div class="file-controlbar">
                我是文件控制栏
            </div>
            <div class="filelist-container">
                <div class="filelist"
                    v-for="file in fileStore.userFileList.files"
                    :key="file.key"
                >
                    <FileDemoFrame :file="file">
                    </FileDemoFrame>
                </div>
                <FileDemoFrame :file="default_file">
                </FileDemoFrame>
                <FileDemoFrame :file="fileStore.default_file">
                </FileDemoFrame>
            </div>
        </div>
        <div class="right-container">
            我是右侧栏目
        </div>
    </div>
</template>
<style lang="scss" scoped>
    .fileview-container{
        display: flex;
        width: 100%;
        height: 100%;
    }
    .left-container{
        width: 100px;
        height: 100%;
        background-color: darkgrey;
    }
    .right-container{
        width: 100px;
        height: 100%;
        background-color: darkgrey;
    }
    .middle-container{
        display: flex;
        flex-direction: column;
        flex: 1;
        background-color: grey;
    }
    .file-controlbar{
        height: 50px;
        width: 100%;
        background-color: red;
    }
    .filelist-container{
        flex: 1;
    }
</style>