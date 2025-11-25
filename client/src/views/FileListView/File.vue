<script lang="ts" setup>
    import {ref,onMounted, computed} from 'vue';
    import { useRouter } from 'vue-router';
    import { useFileStore } from '@/stores/fileStore';
    import { useModalStore } from '@/stores/modalStore';
    import FileDemoFrame from './FileDemoFrame.vue';
    import { FileItem } from '@/utils/api';
    import { usePageStore } from '@/stores/pageStore';
    import Mask from '../Mask.vue';
    import { useLoginStore } from '@/stores/loginStore';

    const fileStore = useFileStore();
    const pageStore = usePageStore();
    const loginStore = useLoginStore()

    const router = useRouter()
    
    const test: boolean = true

    type SortType = 'project_a'|'project_z'|'size_big'|'size_small'|'type'|'time_new'|'time_old'|'name_a'|'name_z'
    const default_type: SortType = 'size_big'

    const sortType = ref<SortType>(default_type)
    const typeSortOrder = ref<number>(0) // 0-3 表示四种排序顺序
    const cycleTypeSort = () => {
        typeSortOrder.value = (typeSortOrder.value + 1) % 4
        sortType.value = 'type'
    }

    const sortedFiles = computed(() => {
        const toBeSortedFiles = [...fileStore.userFileList.files]
        switch(sortType.value) {
            case('project_a'):
                return toBeSortedFiles.sort((a, b) => {
                    const projectA = (a.project_name || '').toLowerCase()
                    const projectB = (b.project_name || '').toLowerCase()
                    return projectA.localeCompare(projectB)
                })
            
            case('project_z'):
                return toBeSortedFiles.sort((a, b) => {
                    const projectA = (a.project_name || '').toLowerCase()
                    const projectB = (b.project_name || '').toLowerCase()
                    return projectB.localeCompare(projectA)
                })
            
            case('size_big'):
                return toBeSortedFiles.sort((a, b) => {
                    return b.size - a.size
                })
            
            case('size_small'):
                return toBeSortedFiles.sort((a, b) => {
                    return a.size - b.size
                })
            
            case('type'):
                return toBeSortedFiles.sort((a, b) => {
                    const baseOrder = [FileItem.format.PNG, FileItem.format.JPG, FileItem.format.CSV, FileItem.format.PDF]
                    const currentOrder = [...baseOrder]
                    
                    for (let i = 0; i < typeSortOrder.value; i++) {
                        const first = currentOrder.shift()
                        if (first) currentOrder.push(first)
                    }
                    
                    const getTypeOrder = (file: FileItem) => {
                        const index = currentOrder.indexOf(file.format)
                        return index === -1 ? currentOrder.length : index
                    }
                    
                    return getTypeOrder(a) - getTypeOrder(b)
                })
                
            case('time_new'):
                return toBeSortedFiles.sort((a, b) => {
                    return b.modified_at - a.modified_at
                })
            
            case('time_old'):
                return toBeSortedFiles.sort((a, b) => {
                    return a.modified_at - b.modified_at
                })
            
            case('name_a'):
                return toBeSortedFiles.sort((a, b) => {
                    const nameA = (a.filename || '').toLowerCase()
                    const nameB = (b.filename || '').toLowerCase()
                    return nameA.localeCompare(nameB)
                })

            case('name_z'):
                return toBeSortedFiles.sort((a, b) => {
                    const nameA = (a.filename || '').toLowerCase()
                    const nameB = (b.filename || '').toLowerCase()
                    return nameB.localeCompare(nameA)
                })
            
            default:
                return toBeSortedFiles
        }
    })

    onMounted(()=>{
        loginStore.checkAuthStatus();
        if(loginStore.loggedIn){
            fileStore.initializeFiles();
        }
        else{
            router.replace({
                name: 'login'
            })
        }
    })

    function handleSort(sort: SortType){
        if(sort=='type'){
            cycleTypeSort()
        }
        else{
            sortType.value = sort
        }
    }

</script>
<template>
    <div class="fileview-container" v-if="loginStore.loggedIn">
        <!-- <div class="left-container">

        </div> -->
        <div class="middle-container">
            <div class="file-controlbar">
                <div class="control-header">
                    <div class="header-item header-type-name">
                        <div class="header-item header-type" @click="handleSort('type')">类型</div>
                        <div class="header-item header-name" @click="()=>{
                                if(sortType=='name_a')handleSort('name_z')
                                else handleSort('name_a')
                            }"
                        >
                            名称
                        </div>
                    </div>
                    <div class="header-item header-info">
                        <div class="header-item header-project" 
                            @click="()=>{
                                if(sortType=='project_a')handleSort('project_z')
                                else handleSort('project_a')
                            }"
                        >
                            所属项目
                        </div>
                        <div class="header-item header-size" 
                            @click="()=>{
                                if(sortType=='size_big')handleSort('size_small')
                                else handleSort('size_big')
                            }"
                        >
                            大小
                        </div>
                        <div class="header-item header-modified" 
                            @click="()=>{
                                if(sortType=='time_new')handleSort('time_old')
                                else handleSort('time_new')
                            }"
                        >
                            修改时间
                        </div>
                    </div>
                    <div class="header-item header-actions">操作</div>
                </div>
            </div>
            <div class="filelist-container">
                <div class="filelist"
                    v-for="file in sortedFiles"
                    :key="file.key"
                >
                    <FileDemoFrame :file="file">
                    </FileDemoFrame>
                </div>
            </div>
        </div>
        <!-- <div class="right-container">

        </div> -->
    </div>
    <Mask v-else></Mask>
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
        padding: 0 20px;
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
        // border: 2px solid black;
    }

    .header-type,.header-name,.header-project,.header-size,.header-modified{
        cursor: pointer; /* 添加指针样式表明可点击 */
    }
    
    .header-type-name{
        width: 200px;
        text-align: center;
        display: flex;
        // border: 2px solid black;
    }

    .header-type{
        text-align: center;
    }

    .header-name{
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
