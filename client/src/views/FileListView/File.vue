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
    import SvgIcon from '@jamescoyle/vue-icon';
    import { mdiMenuDown, mdiMenuUp } from '@mdi/js';

    const fileStore = useFileStore();
    const pageStore = usePageStore();
    const loginStore = useLoginStore()

    const router = useRouter()

    const test: boolean = true

    type SortType = 'project_a'|'project_z'|'size_big'|'size_small'|'type_a'|'type_z'|'time_new'|'time_old'|'name_a'|'name_z'
    const default_type: SortType = 'size_big'

    const sortType = ref<SortType>(default_type)

    // 计算属性：确定类型列的排序图标
    const typeSortIcon = computed(() => {
        if (sortType.value === 'type_a') {
            return mdiMenuDown; // A-Z 排序，向下箭头
        } else if (sortType.value === 'type_z') {
            return mdiMenuUp; // Z-A 排序，向上箭头
        }
        // 默认情况下不显示图标
        return null;
    });

    // 计算属性：确定名称列的排序图标
    const nameSortIcon = computed(() => {
        if (sortType.value === 'name_a') {
            return mdiMenuDown; // A-Z 排序，向下箭头
        } else if (sortType.value === 'name_z') {
            return mdiMenuUp; // Z-A 排序，向上箭头
        }
        // 默认情况下不显示图标（或者可以返回 null）
        return null;
    });

    // 计算属性：确定大小列的排序图标
    const sizeSortIcon = computed(() => {
        if (sortType.value === 'size_big') {
            return mdiMenuDown; // 大到小排序，向下箭头
        } else if (sortType.value === 'size_small') {
            return mdiMenuUp; // 小到大排序，向上箭头
        }
        // 默认情况下不显示图标（或者可以返回 null）
        return null;
    });

    // 计算属性：确定项目列的排序图标
    const projectSortIcon = computed(() => {
        if (sortType.value === 'project_a') {
            return mdiMenuDown; // A-Z 排序，向下箭头
        } else if (sortType.value === 'project_z') {
            return mdiMenuUp; // Z-A 排序，向上箭头
        }
        // 默认情况下不显示图标
        return null;
    });

    // 计算属性：确定时间列的排序图标
    const timeSortIcon = computed(() => {
        if (sortType.value === 'time_new') {
            return mdiMenuDown; // 新到旧排序，向下箭头
        } else if (sortType.value === 'time_old') {
            return mdiMenuUp; // 旧到新排序，向上箭头
        }
        // 默认情况下不显示图标
        return null;
    });

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

            case('type_a'):
                return toBeSortedFiles.sort((a, b) => {
                    const typeA = (a.format || '').toLowerCase()
                    const typeB = (b.format || '').toLowerCase()
                    return typeA.localeCompare(typeB)
                })

            case('type_z'):
                return toBeSortedFiles.sort((a, b) => {
                    const typeA = (a.format || '').toLowerCase()
                    const typeB = (b.format || '').toLowerCase()
                    return typeB.localeCompare(typeA)
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
        sortType.value = sort
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
                        <div class="header-item header-type" @click="()=>{
                                if(sortType=='type_a')handleSort('type_z')
                                else handleSort('type_a')
                            }"
                        >
                            类型
                            <svg-icon v-if="typeSortIcon" type="mdi" :path="typeSortIcon" class="sort-icon" />
                        </div>
                        <div class="header-item header-name" @click="()=>{
                                if(sortType=='name_a')handleSort('name_z')
                                else handleSort('name_a')
                            }"
                        >
                            名称
                            <svg-icon v-if="nameSortIcon" type="mdi" :path="nameSortIcon" class="sort-icon" />
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
                            <svg-icon v-if="projectSortIcon" type="mdi" :path="projectSortIcon" class="sort-icon" />
                        </div>
                        <div class="header-item header-size"
                            @click="()=>{
                                if(sortType=='size_big')handleSort('size_small')
                                else handleSort('size_big')
                            }"
                        >
                            大小
                            <svg-icon v-if="sizeSortIcon" type="mdi" :path="sizeSortIcon" class="sort-icon" />
                        </div>
                        <div class="header-item header-modified"
                            @click="()=>{
                                if(sortType=='time_new')handleSort('time_old')
                                else handleSort('time_new')
                            }"
                        >
                            修改时间
                            <svg-icon v-if="timeSortIcon" type="mdi" :path="timeSortIcon" class="sort-icon" />
                        </div>
                    </div>
                    <div class="header-item header-actions">
                        <div class="actions-header-container">
                            操作
                        </div>
                    </div>
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
        display: flex;
        align-items: center;
    }

    .header-type,.header-name,.header-project,.header-size,.header-modified{
        cursor: pointer; /* 添加指针样式表明可点击 */
        position: relative;
    }

    .header-type-name{
        width: 200px;
        text-align: center;
        display: flex;
        // border: 2px solid black;
    }

    .header-type{
        text-align: center;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 5px;
        flex-direction: row;
        white-space: nowrap;
    }

    .header-name{
        text-align: center;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 5px;
        flex-direction: row;
        white-space: nowrap;
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
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 5px;
        flex-direction: row;
        white-space: nowrap;
    }

    .header-size{
        width: 120px;
        text-align: center;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 5px;
        flex-direction: row;
        white-space: nowrap;
    }

    .header-modified{
        width: 200px;
        text-align: center;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 5px;
        flex-direction: row;
        white-space: nowrap;
    }

    .header-actions{
        width: 200px;
        display: flex;
        justify-content: center;
    }

    .actions-header-container{
        margin-right: 40px;
    }

    .header-icon {
        width: 16px;
        height: 16px;
    }

    .sort-icon {
        width: 16px;
        height: 16px;
        margin-left: 5px;
    }

    .filelist-container{
        flex: 1;
        background-color: $stress-background-color;
        border-radius: 10px;
        // padding: 24px;
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
