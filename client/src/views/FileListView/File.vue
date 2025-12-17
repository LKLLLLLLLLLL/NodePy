<script lang="ts" setup>
    import {ref,onMounted, computed} from 'vue';
    import { useRouter } from 'vue-router';
    import { useFileStore } from '@/stores/fileStore';
    import { useModalStore } from '@/stores/modalStore';
    import FileIcon from './FileIcon.vue';
    import { FileItem } from '@/utils/api';
    import { usePageStore } from '@/stores/pageStore';
    import Mask from '../Mask.vue';
    import { useLoginStore } from '@/stores/loginStore';
    import SvgIcon from '@jamescoyle/vue-icon';
    import { mdiMenuDown, mdiMenuUp, mdiEye, mdiDownload } from '@mdi/js';
    import FilePreview from './FilePreview.vue';

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

    const modalStore = useModalStore();
    const previewWidth = 600;
    const previewHeight = 800;
    const uploadWidth = 400;
    const uploadHeight = 600;

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
        <div class="middle-container">
            <div class="file-table-container">
                <table class="file-table">
                    <thead>
                        <tr class="table-header">
                            <th class="header-cell header-type" @click="()=>{
                                    if(sortType=='type_a')handleSort('type_z')
                                    else handleSort('type_a')
                                }"
                            >
                                <div class="header-content">
                                    类型
                                    <svg-icon v-if="typeSortIcon" type="mdi" :path="typeSortIcon" class="sort-icon" />
                                </div>
                            </th>
                            <th class="header-cell header-name" @click="()=>{
                                    if(sortType=='name_a')handleSort('name_z')
                                    else handleSort('name_a')
                                }"
                            >
                                <div class="header-content">
                                    名称
                                    <svg-icon v-if="nameSortIcon" type="mdi" :path="nameSortIcon" class="sort-icon" />
                                </div>
                            </th>
                            <th class="header-cell header-project"
                                @click="()=>{
                                    if(sortType=='project_a')handleSort('project_z')
                                    else handleSort('project_a')
                                }"
                            >
                                <div class="header-content">
                                    所属项目
                                    <svg-icon v-if="projectSortIcon" type="mdi" :path="projectSortIcon" class="sort-icon" />
                                </div>
                            </th>
                            <th class="header-cell header-size"
                                @click="()=>{
                                    if(sortType=='size_big')handleSort('size_small')
                                    else handleSort('size_big')
                                }"
                            >
                                <div class="header-content">
                                    大小
                                    <svg-icon v-if="sizeSortIcon" type="mdi" :path="sizeSortIcon" class="sort-icon" />
                                </div>
                            </th>
                            <th class="header-cell header-modified"
                                @click="()=>{
                                    if(sortType=='time_new')handleSort('time_old')
                                    else handleSort('time_new')
                                }"
                            >
                                <div class="header-content">
                                    修改时间
                                    <svg-icon v-if="timeSortIcon" type="mdi" :path="timeSortIcon" class="sort-icon" />
                                </div>
                            </th>
                            <th class="header-cell header-actions">
                                <div class="header-content">
                                    操作
                                </div>
                            </th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr 
                            class="file-row"
                            v-for="file in sortedFiles"
                            :key="file.key"
                        >
                            <td class="cell cell-type">
                                <div class="cell-content">
                                    <FileIcon :format="file.format"></FileIcon>
                                </div>
                            </td>
                            <td class="cell cell-name">
                                <div class="cell-content filename-container">
                                    {{ file.filename }}
                                </div>
                            </td>
                            <td class="cell cell-project">
                                <div class="cell-content">
                                    {{ file.project_name }}
                                </div>
                            </td>
                            <td class="cell cell-size">
                                <div class="cell-content">
                                    {{ formatFileSize(file.size) }}
                                </div>
                            </td>
                            <td class="cell cell-modified">
                                <div class="cell-content">
                                    {{ formatDateTime(file.modified_at) }}
                                </div>
                            </td>
                            <td class="cell cell-actions">
                                <div class="cell-content actions-container">
                                    <button @click="()=>handlePreview(file)" size="small" circle>
                                        <svg-icon type="mdi" :path="mdiEye" class="actions-icon"/>
                                    </button>
                                    <button @click="()=>handleDownload(file)" size="small" circle>
                                        <svg-icon type="mdi" :path="mdiDownload" class="actions-icon"/>
                                    </button>
                                </div>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
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
        // padding: 20px;
        gap: 20px;
        min-height: 0;
        box-sizing: border-box;
    }

    .middle-container{
        padding-top: 20px;
        padding-bottom: 20px;
        padding-left: 5px;
        padding-right: 5px;
        display: flex;
        flex-direction: column;
        flex: 1;
        gap: 20px;
        min-height: 0;
        height: 100%;
        overflow: hidden;
    }

    .file-table-container {
        flex: 1;
        border-radius: 10px;
        min-height: 0;
        overflow: auto;
        height: 0;
        // @include controller-style;

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

    .file-table {
        width: 100%;
        border-collapse: collapse;
        table-layout: fixed;
    }

    .table-header {
        height: 60px;
        background-color: $background-color;
        position: sticky;
        top: 0;
        z-index: 10;
    }

    .header-cell {
        padding: 0 16px;
        text-align: center;
        font-weight: 600;
        color: #2d3748;
        font-size: 16px;
        cursor: pointer;
        position: relative;
        border-bottom: 1px solid #e2e8f0;

        &:hover {
            background-color: rgba($stress-color, 0.05);
        }
    }

    .header-content {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 5px;
    }

    .header-type {
        width: 80px;
    }

    .header-name {
        width: 200px;
    }

    .header-project {
        width: 200px;
    }

    .header-size {
        width: 120px;
    }

    .header-modified {
        width: 200px;
    }

    .header-actions {
        width: 100px;
    }

    .sort-icon {
        width: 16px;
        height: 16px;
    }

    .file-row {
        height: 62px;
        border-bottom: 1px solid #e2e8f0;

        &:hover {
            background-color: rgba($stress-color, 0.03);
            transform: translateY(-1px);
            box-shadow: 0 4px 6px rgba(128, 128, 128, 0.1);
            transition: all 0.3s ease;
        }
    }

    .cell {
        padding: 0 16px;
        text-align: center;
    }

    .cell-content {
        display: flex;
        align-items: center;
        justify-content: center;
        height: 100%;
        font-size: 15px;
    }

    .cell-type .cell-content {
        gap: 16px;
    }

    .filename-container {
        font-weight: bold;
        color: #2d3748;
        font-size: 15px;
    }

    .actions-container {
        gap: 20px;
    }

    .file-icon {
        width: 32px;
        height: 32px;
    }

    .actions-icon {
        width: 22px;
        height: 22px;
        color: #808080;
    }
</style>