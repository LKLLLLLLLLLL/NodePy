<script lang="ts" setup>
    import { useModalStore } from '@/stores/modalStore';
    const modalStore = useModalStore();

    function handlePreview(){
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
            }
        })
    }
</script>
<template>
    <div class="fileview-container">
        <div class="left-container">
            我是左侧栏目
        </div>
        <div class="middle-container">
            <div class="file-controlbar">
                我是文件控制栏
                <el-button @click="handlePreview" type=primary></el-button>
            </div>
            <div class="filelist-container">
                我是文件列表
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