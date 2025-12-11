<script lang="ts" setup>
import {computed} from 'vue';
import { Plus, Edit, Delete } from '@element-plus/icons-vue';
import { useProjectStore } from '@/stores/projectStore';
import { useModalStore } from '@/stores/modalStore';
import DeleteProject from './DeleteProject.vue';
import UpdateProjectSetting from './UpdateProjectSetting.vue';
import SvgIcon from '@jamescoyle/vue-icon';
import { mdiPencil, mdiDelete } from '@mdi/js';

const edit_path = mdiPencil;
const delete_path = mdiDelete;

const props = defineProps<{
    id: number,
    title?: string,
    thumb?: string | null,
    created_at?: number | string | null,
    updated_at?: number | string | null,
    handleOpenExistingProject?: (id: number) => void,
    handleCreateNewProject?: () => void,
}>();

// 计算属性：将 Base64 转换为完整的 Data URL
const thumbSrc = computed(() => {
    if (!props.thumb) return null

    // 如果已经是 Data URL，直接返回
    if (props.thumb.startsWith('data:image')) {
        return props.thumb
    }

    // 如果是纯 Base64，添加前缀
    return `data:image/png;base64,${props.thumb}`
})

const projectStore = useProjectStore();
const modalStore = useModalStore();

function parseDate(v: number | string | null | undefined) {
    if (!v) return null;
    const d = typeof v === 'number' ? new Date(v) : new Date(String(v));
    if (isNaN(d.getTime())) return null;
    return d;
}

function formatDate(v: number | string | null | undefined) {
    const d = parseDate(v);
    if (!d) return '';
    return new Intl.DateTimeFormat('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit' }).format(d);
}

function onCardClick() {
    if (props.id != null && props.id !== 0 && props.handleOpenExistingProject) {
        props.handleOpenExistingProject(props.id);
    } else if (props.handleCreateNewProject) {
        props.handleCreateNewProject();
    }
}

async function handleClickDelete(){
    projectStore.toBeDeleted.id = props.id
    const modalWidth = 450;
    const modalHeight = 200;
    modalStore.createModal({
        id: 'delete-modal',
        title: "删除项目",
        isActive: true,
        isDraggable: false,
        isResizable: false,
        position: {
                x: (window.innerWidth - modalWidth) / 2,
                y: (window.innerHeight - modalHeight) / 2
        },
        size:{
            height: modalHeight,
            width: modalWidth
        },
        component: DeleteProject
    })
}

async function handleClickUpdate(){
    await projectStore.getProjectSettings(props.id)
    projectStore.currentProjectId = props.id
    const modalWidth = 300;
    const modalHeight = 400;
    modalStore.createModal({
        id: 'update-modal',
        title: "更新项目",
        isActive: true,
        isDraggable: false,
        isResizable: false,
        position: {
                x: (window.innerWidth - modalWidth) / 2,
                y: (window.innerHeight - modalHeight) / 2
        },
        size:{
            height: modalHeight,
            width: modalWidth
        },
        component: UpdateProjectSetting
    })
}

</script>

<template>
    <div
        :class="['project-card', { 'new-card': props.id === 0 && props.handleCreateNewProject, 'placeholder-large': !props.thumb && !(props.id === 0 && props.handleCreateNewProject) } ]"
        role="button"
        :aria-label="props.title ?? (props.id ? `Project ${props.id}` : 'Create Project')"
        tabindex="0"
        @click="onCardClick"
        @keyup.enter="onCardClick"
    >
        <div class="project-thumb">
            <slot name="picture">
                <div class="thumb-content">
                    <template v-if="thumbSrc">
                        <img :src="thumbSrc" alt="thumb" class="thumb-img" />
                    </template>
                    <template v-else>
                        <div v-if="props.id === 0 && props.handleCreateNewProject" class="thumb-new">
                            <el-icon :size="40" color="#2c98da"><Plus/></el-icon>
                        </div>
                        <div v-else class="thumb-placeholder-large">{{ (props.title || '').charAt(0) || 'P' }}</div>
                    </template>
                </div>
            </slot>
            <div v-if="props.id !== 0" class="card-actions">
                <div @click.stop="handleClickUpdate" title="编辑" class="project-edit-btn project-action-btn">
                    <svg-icon type="mdi" :path="edit_path"></svg-icon>
                </div>
                <div @click.stop="handleClickDelete" title="删除" class="project-delete-btn project-action-btn">
                    <svg-icon type="mdi" :path="delete_path"></svg-icon>
                </div>
            </div>
        </div>

        <div class="project-info">
            <div class="project-title">{{ props.title ?? (props.id ? `Project ${props.id}` : 'New') }}</div>
            <div v-if="!(props.id === 0 && props.handleCreateNewProject)" class="project-meta">
                <span class="meta-item">修改: {{ formatDate(props.updated_at) }}</span>
                <span class="meta-item">创建: {{ formatDate(props.created_at) }}</span>
            </div>
        </div>
    </div>
</template>

<style lang="scss" scoped>
.project-card{
    width: 100%;
    max-width: 420px;
    background: #ffffff;
    border-radius: 12px;
    color: #1f2d3d;
    display: flex;
    flex-direction: column;
    overflow: hidden;
    cursor: pointer;
    box-shadow: 0 6px 25px rgba(31,45,61,0.08);
    transition: transform 140ms cubic-bezier(.2,.9,.3,1), box-shadow 140ms cubic-bezier(.2,.9,.3,1);
}
.project-card:focus{
    outline: 2px solid rgba(26,115,190,0.12);
    outline-offset: 2px;
}
.project-card:hover{
    transform: translateY(-4px) scale(1.015);
    box-shadow: 0 12px 28px rgba(31,45,61,0.12);
}
.project-thumb{
    position: relative;
    width: 100%;
    padding-top: 56.25%; /* 16:9 */
    display: block;
    background: #f6f9fb;
}
.thumb-content{
    position: absolute;
    left: 0;
    top: 0;
    width: 100%;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
}
.thumb-content > img.thumb-img{
    position: absolute;
    left: 0;
    top: 0;
    width: 100%;
    height: 100%;
    object-fit: cover;
}
.card-actions{
    position: absolute;
    right: 8px;
    top: 8px;
    display: flex;
    gap: 4px;
    z-index: 5;
}
.action-btn{
    padding: 4px;
    color: rgba(16,35,53,0.75);
}
.thumb-img{
    width:100%;
    height:100%;
    object-fit:cover;
}
.thumb-placeholder-large{
    width:100%;
    height:100%;
    display:flex;
    align-items:center;
    justify-content:center;
    color: #4b5d6a;
    font-size:48px;
    font-weight:700;
}
.thumb-new{
    width:100%;
    height:100%;
    display:flex;
    align-items:center;
    justify-content:center;
}
.project-info{
    padding: 14px 16px;
    display:flex;
    flex-direction:column;
    gap:6px;
    min-height: 75px; /* ensure new-card height matches cards with meta */
}
.project-title{
    font-weight:700;
    font-size:15px;
    color:#102335;
    white-space:nowrap;
    overflow:hidden;
    text-overflow:ellipsis;
}
.project-meta{
    display:flex;
    gap:10px;
    font-size:12px;
    color:#6b7f8f;
}
.new-card{ border: 1px solid rgba(28,128,199,0.06); }
.meta-item{opacity:0.95}

@media (max-width: 480px){
    .project-card{ max-width: 100%; }
}

.project-action-btn{
    cursor: pointer;
    padding: 6px;
    border-radius: 6px;
    height: 100%;
    width: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    svg{
        width: 18px;
        height: 18px;
        color: rgba(0, 0, 0, 0.60);
    }
    &:hover {
        background-color: rgba(0, 0, 0, 0.05);
    }
}
</style>
