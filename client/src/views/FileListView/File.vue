<script lang="ts" setup>
    import {ref,onMounted, onBeforeUnmount, computed} from 'vue';
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

    type SortType = 'project_a'|'project_z'|'size_big'|'size_small'|'type_a'|'type_z'|'time_new'|'time_old'|'name_a'|'name_z'
    const default_type: SortType = 'time_new'

    const sortType = ref<SortType>(default_type)
    const selectedFiles = ref<Set<string>>(new Set())
    const viewMode = ref<'grid' | 'list'>('grid')

    function toggleFileSelection(fileKey: string) {
        if (selectedFiles.value.has(fileKey)) {
            selectedFiles.value.delete(fileKey)
        } else {
            selectedFiles.value.add(fileKey)
        }
    }

    function isFileSelected(fileKey: string) {
        return selectedFiles.value.has(fileKey)
    }

    // 兼容的卡片点击预览别名（模板里期望 openFilePreview 存在）
    const openFilePreview = async (file: FileItem) => {
        await handlePreview(file)
    }

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

    // 格式化时间的函数（相对时间）
    const formatDateTime = (timestamp: number): string => {
        const now = Date.now();
        const diff = now - timestamp;
        const seconds = Math.floor(diff / 1000);
        const minutes = Math.floor(seconds / 60);
        const hours = Math.floor(minutes / 60);
        const days = Math.floor(hours / 24);

        if (days > 7) {
            const date = new Date(timestamp);
            const month = String(date.getMonth() + 1).padStart(2, '0');
            const day = String(date.getDate()).padStart(2, '0');
            return `${date.getFullYear()}-${month}-${day}`;
        } else if (days > 0) {
            return `${days} 天前`;
        } else if (hours > 0) {
            return `${hours} 小时前`;
        } else if (minutes > 0) {
            return `${minutes} 分钟前`;
        } else {
            return '刚刚';
        }
    }

    const modalStore = useModalStore();
    const previewWidth = 0.8 * window.innerWidth;
    const previewHeight = 0.95 * window.innerHeight;

    function animateButton(e: MouseEvent){
        const el = (e.currentTarget as HTMLElement | null);
        if(!el) return;
        el.classList.add('clicked');
        el.addEventListener('animationend', () => {
            el.classList.remove('clicked');
        }, { once: true });
    }

    async function handlePreview(file :any){
        fileStore.changeCurrentFile(file);
        modalStore.createModal({
            id: 'file-preview',
            title: '预览',
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

    // 排序下拉弹窗状态与外部点击处理
    const showSortMenu = ref(false)
    const sortMenuRef = ref<HTMLElement | null>(null)

    const sortLabelMap: Record<SortType, string> = {
        project_a: '项目 A-Z',
        project_z: '项目 Z-A',
        size_big: '大小 大-小',
        size_small: '大小 小-大',
        type_a: '类型 A-Z',
        type_z: '类型 Z-A',
        time_new: '最近修改',
        time_old: '最早修改',
        name_a: '名称 A-Z',
        name_z: '名称 Z-A'
    }

    const onGlobalClick = (e: MouseEvent) => {
        if (!showSortMenu.value) return
        const el = sortMenuRef.value
        if (!el) return
        const rect = el.getBoundingClientRect()
        const target = e.target as Node
        if (el.contains(target)) return
        showSortMenu.value = false
    }

    onMounted(() => {
        document.addEventListener('click', onGlobalClick)
    })

    onBeforeUnmount(() => {
        document.removeEventListener('click', onGlobalClick)
    })

</script>
<template>
    <div class="fileview-container" v-if="loginStore.loggedIn">
        <!-- 工具栏 -->
        <div class="toolbar">
            <div class="toolbar-left">
                <!-- <h2 class="page-title">文件管理</h2> -->
                <div class="file-count">{{ sortedFiles.length }} 个文件</div>
            </div>
            <div class="toolbar-right">
                <div class="sort-dropdown" ref="sortMenuRef">
                    <button class="sort-btn" type="button" @click="(e) => { animateButton(e); showSortMenu = !showSortMenu }" aria-haspopup="true" :aria-expanded="showSortMenu">
                        <div class="sort-text">{{ sortLabelMap[sortType] }}</div>
                        <SvgIcon type="mdi" :path="showSortMenu ? mdiMenuUp : mdiMenuDown" class="btn-icon" />
                    </button>

                    <div v-if="showSortMenu" class="sort-menu">
                        <ul class="menu-list">
                            <li class="menu-item" @click="() => { handleSort('time_new'); showSortMenu = false }">最近修改</li>
                            <li class="menu-item" @click="() => { handleSort('time_old'); showSortMenu = false }">最早修改</li>
                            <li class="menu-item" @click="() => { handleSort('name_a'); showSortMenu = false }">名称 A-Z</li>
                            <li class="menu-item" @click="() => { handleSort('name_z'); showSortMenu = false }">名称 Z-A</li>
                            <li class="menu-item" @click="() => { handleSort('size_big'); showSortMenu = false }">大小 大-小</li>
                            <li class="menu-item" @click="() => { handleSort('size_small'); showSortMenu = false }">大小 小-大</li>
                            <li class="menu-item" @click="() => { handleSort('type_a'); showSortMenu = false }">类型 A-Z</li>
                            <li class="menu-item" @click="() => { handleSort('type_z'); showSortMenu = false }">类型 Z-A</li>
                        </ul>
                    </div>
                </div>
            </div>
        </div>

        <!-- 卡片网格 -->
        <div class="file-grid">
            <div
                v-for="file in sortedFiles"
                :key="file.key"
                class="file-card"
                :class="{ selected: isFileSelected(file.key) }"
                @click="openFilePreview(file)"
            >
                <!-- 文件预览 -->
                <div class="file-preview">
                    <FileIcon :file="file" class="file-icon-large" />
                </div>

                <!-- 文件信息 -->
                <div class="file-info">
                    <div class="file-name" :title="file.filename">{{ file.filename }}</div>
                    <div class="file-meta">
                        <span class="file-size">{{ formatFileSize(file.size) }}</span>
                        <span class="file-dot">·</span>
                        <span class="file-project" :title="file.project_name">{{ file.project_name }}</span>
                    </div>
                    <div class="file-date">{{ formatDateTime(file.modified_at) }}</div>
                </div>
            </div>
        </div>
    </div>
    <Mask v-else></Mask>
</template>
<style lang="scss" scoped>
    @use '../../common/global.scss' as *;
    @use "sass:color";

    .fileview-container {
        display: flex;
        flex-direction: column;
        width: 100%;
        height: 100%;
        background-color: $background-color;
        overflow: hidden;
    }

    // 工具栏
    .toolbar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 12px 45px;
        background: $background-color;
        // border-bottom: 1px solid rgba(0, 0, 0, 0.08);
        flex-shrink: 0;
    }

    .toolbar-left {
        display: flex;
        align-items: baseline;
        gap: 16px;
    }

    .page-title {
        font-size: 28px;
        font-weight: 600;
        color: rgba(0, 0, 0, 0.87);
        margin: 0;
        letter-spacing: -0.5px;
    }

    .file-count {
        font-size: 14px;
        color: rgba(0, 0, 0, 0.5);
        font-weight: 500;
    }

    .toolbar-right {
        display: flex;
        align-items: center;
        gap: 12px;
    }

    .sort-dropdown {
        position: relative;
    }

    .sort-select {
        padding: 8px 32px 8px 12px;
        // border: 1px solid rgba(0, 0, 0, 0.12);s
        border-radius: 8px;
        background: white;
        font-size: 14px;
        color: rgba(0, 0, 0, 0.75);
        cursor: pointer;
        outline: none;
        transition: all 0.2s ease;
        appearance: none;
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'%3E%3Cpath fill='%23666' d='M6 9L1 4h10z'/%3E%3C/svg%3E");
        background-repeat: no-repeat;
        background-position: right 10px center;
        box-shadow: 5px 5px 50px rgba(128, 128, 128, 0.12);

        &:hover {
            // border-color: rgba(0, 0, 0, 0.24);
            background-color: rgba(0, 0, 0, 0.02);
        }

        // &:focus {
        //     border-color: $stress-color;
        //     box-shadow: 0 0 0 3px rgba($stress-color, 0.1);
        // }
    }

    // 文件网格
    .file-grid {
        flex: 1;
        overflow-y: auto;
        padding: 6px 32px;
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
        gap: 20px;
        align-content: start;

        /* 自定义滚动条 */
        &::-webkit-scrollbar {
            width: 8px;
        }

        &::-webkit-scrollbar-track {
            background: transparent;
        }

        &::-webkit-scrollbar-thumb {
            background: rgba(0, 0, 0, 0.15);
            border-radius: 4px;

            &:hover {
                background: rgba(0, 0, 0, 0.25);
            }
        }

        scrollbar-width: thin;
        scrollbar-color: rgba(0, 0, 0, 0.15) transparent;
    }

    // 文件卡片
    .file-card {
        display: flex;
        flex-direction: column;
        background: white;
        border-radius: 12px;
        overflow: hidden;
        cursor: pointer;
        box-shadow: 0 6px 25px rgba(31, 45, 61, 0.08);
        transition: transform 140ms cubic-bezier(.2, .9, .3, 1), box-shadow 140ms cubic-bezier(.2, .9, .3, 1);
        -webkit-user-select: none;
        -moz-user-select: none;
        -ms-user-select: none;
        user-select: none;

        &:focus {
            outline: 2px solid rgba(26, 115, 190, 0.12);
            outline-offset: 2px;
        }

        &:hover {
            transform: translateY(-4px) scale(1.015);
            box-shadow: 0 12px 28px rgba(31, 45, 61, 0.12);
        }

        &.selected {
            border: 2px solid $stress-color;
            box-shadow: 0 0 0 3px rgba($stress-color, 0.1);
        }
    }

    // 文件预览区域
    .file-preview {
        position: relative;
        width: 100%;
        padding-top: 75%; /* 4:3 ratio */
        background: #f6f9fb;
        overflow: hidden;
    }

    .file-icon-large {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
    }

    // 文件信息
    .file-info {
        padding: 12px;
        display: flex;
        flex-direction: column;
        gap: 4px;
        -webkit-user-select: none;
        -moz-user-select: none;
        -ms-user-select: none;
        user-select: none;
    }

    .file-name {
        font-size: 14px;
        font-weight: 500;
        color: rgba(0, 0, 0, 0.87);
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
        line-height: 1.4;
    }

    .file-meta {
        display: flex;
        align-items: center;
        gap: 6px;
        font-size: 12px;
        color: rgba(0, 0, 0, 0.5);
        line-height: 1.3;
    }

    .file-size {
        font-weight: 500;
    }

    .file-dot {
        opacity: 0.5;
    }

    .file-project {
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
        flex: 1;
        min-width: 0;
    }

    .file-date {
        font-size: 11px;
        color: rgba(0, 0, 0, 0.38);
        line-height: 1.3;
    }

    @keyframes clickPulse {
        0% { transform: scale(1); }
        50% { transform: scale(0.9); }
        100% { transform: scale(1); }
    }

    /* 排序按钮和下拉样式，参考 GraphControls 和 RightClickMenu */
    .sort-btn{
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 6px 10px;
        border-radius: 8px;
        background: white;
        cursor: pointer;
        border: 1px solid rgba(0,0,0,0.06);
        box-shadow: 5px 5px 50px rgba(128,128,128,0.06);
    }

    .sort-btn .btn-icon{
        width: 20px;
        height: 20px;
        color: rgba(0,0,0,0.65);
    }

    .sort-text{
        font-size: 14px;
        color: rgba(0,0,0,0.8);
        font-weight: 500;
    }

    .sort-menu{
        position: absolute;
        right: 0;
        margin-top: 8px;
        z-index: 9999;
        min-width: 180px;
        background: white;
        border-radius: 8px;
        box-shadow: 0 8px 24px rgba(31,45,61,0.12);
        padding: 6px;
        animation: menu-fade-in 160ms cubic-bezier(.2,.8,.2,1) both;
    }

    .sort-menu .menu-list{
        list-style: none;
        margin: 0;
        padding: 0;
    }

    .sort-menu .menu-item{
        padding: 8px 12px;
        cursor: pointer;
        border-radius: 6px;
        font-size: 13px;
        color: rgba(0,0,0,0.8);
    }

    .sort-menu .menu-item:hover{
        background-color: rgba(0,0,0,0.06);
    }
</style>
