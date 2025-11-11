<script lang="ts" setup>
    import {ref,onMounted} from 'vue';
    import { useFileStore } from '@/stores/fileStore';
    import { useModalStore } from '@/stores/modalStore';
    import FileDemoFrame from './FileDemoFrame.vue';
    import { FileItem } from '@/utils/api';

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
        console.log(fileStore.userFileList.files);
    })

</script>
<template>
    <div class="fileview-container">
        <!-- <div class="left-container">

        </div> -->
        <div class="middle-container">
            <div class="file-controlbar">
                <div class="control-header">
                    <div class="header-item header-name">名称</div>
                    <div class="header-item header-info">
                        <div class="header-item header-project">所属项目</div>
                        <div class="header-item header-size">大小</div>
                        <div class="header-item header-modified">修改时间</div>
                    </div>
                    <div class="header-item header-actions">操作</div>
                </div>
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
                <FileDemoFrame :file="default_file">
                </FileDemoFrame>
                <FileDemoFrame :file="default_file">
                </FileDemoFrame>
                <FileDemoFrame :file="default_file">
                </FileDemoFrame>
                <FileDemoFrame :file="default_file">
                </FileDemoFrame>
                <FileDemoFrame :file="default_file">
                </FileDemoFrame>
                <FileDemoFrame :file="default_file">
                </FileDemoFrame>
                <FileDemoFrame :file="default_file">
                </FileDemoFrame>
                <FileDemoFrame :file="default_file">
                </FileDemoFrame>
                <FileDemoFrame :file="default_file">
                </FileDemoFrame>
            </div>
        </div>
        <!-- <div class="right-container">

        </div> -->
    </div>
</template>
<style lang="scss" scoped>
    @use '../../common/global.scss' as *;
    @use "sass:color";
    
    .fileview-container{
        display: flex;
        width: 100%;
        height: 100%;
        background-color: $background-color;
        padding: 20px;
        gap: 20px;
        min-height: 0;
        box-sizing: border-box;
    }
    
    .middle-container{
        display: flex;
        flex-direction: column;
        flex: 1;
        gap: 20px;
        min-height: 0;
        height: 100%;
        overflow: auto;
    }
    
    .file-controlbar{
        height: 60px;
        width: 100%;
        background-color: $stress-background-color;
        border-radius: 10px;
        padding: 0 24px;
        display: flex;
        align-items: center;
        flex-shrink: 0; /* 防止控制栏被压缩 */
    }
    
    .control-header{
        display: flex;
        width: 100%;
        align-items: center;
        font-weight: 600;
        color: #2d3748;
        font-size: 14px;
    }
    
    .header-item{
        padding: 0 16px;
    }
    
    .header-name{
        width: 200px;
        text-align: center;
    }
    
    .header-info{
        flex: 1;
        display: flex;
        justify-content: flex-end;
        gap: 32px;
    }
    
    .header-project{
        width: 200px;
        text-align: center;
    }
    
    .header-size{
        width: 120px;
        text-align: center;
    }
    
    .header-modified{
        width: 200px;
        text-align: center;
    }
    
    .header-actions{
        width: 200px;
        text-align: center;
    }
    
    .filelist-container{
        flex: 1;
        background-color: $stress-background-color;
        border-radius: 10px;
        padding: 24px;
        min-height: 0;
        overflow: auto;
        height: 0; /* 关键：设置高度为0，让flex:1控制实际高度 */
        
        /* 自定义滚动条样式 */
        &::-webkit-scrollbar {
            width: 8px;
        }
        
        &::-webkit-scrollbar-track {
            background: $mix-background-color;
            border-radius: 4px;
        }
        
        &::-webkit-scrollbar-thumb {
            background: color.adjust($mix-background-color, $lightness: -20%);
            border-radius: 4px;
            
            &:hover {
                background: color.adjust($mix-background-color, $lightness: -30%)
            }
        }
        
        /* Firefox 滚动条样式 */
        scrollbar-width: thin;
        scrollbar-color: color.adjust($mix-background-color, $lightness: -20%) $mix-background-color;
    }
</style>
