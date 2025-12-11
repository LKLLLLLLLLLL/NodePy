<script lang="ts" setup>
    import { ref, onMounted, computed, watch, onBeforeUnmount } from 'vue';
    import { useRouter, useRoute } from 'vue-router';
    import { useModalStore } from '@/stores/modalStore';
    import { useProjectStore } from '@/stores/projectStore';
    import { usePageStore } from '@/stores/pageStore';
    import { useLoginStore } from '@/stores/loginStore';
    import ProjectDemoFrame from './ProjectDemoFrame.vue';
    import CreateProject from './CreateProject.vue';
    import Mask from '../Mask.vue';

    const modalStore = useModalStore();
    const projectStore = useProjectStore();
    const pageStore = usePageStore();
    const loginStore = useLoginStore();
    const router = useRouter();
    const route = useRoute();

    // 定时器引用
    const refreshTimer = ref<number | null>(null);

    onMounted(()=>{
        loginStore.checkAuthStatus()
        if(loginStore.loggedIn==true){
            projectStore.initializeProjects()
        }
        else{
            router.replace({
                name: 'login'
            })
        }

        // 设置定时刷新，每3分钟刷新一次
        refreshTimer.value = window.setInterval(() => {
            if (loginStore.loggedIn) {
                projectStore.initializeProjects()
            }
        }, 3 * 60 * 1000); // 3分钟 = 3 * 60 * 1000毫秒
    });

    // 清理定时器，避免内存泄漏
    onBeforeUnmount(() => {
        if (refreshTimer.value) {
            window.clearInterval(refreshTimer.value);
            refreshTimer.value = null;
        }
    });

    // 监听路由变化，当进入项目列表页面时刷新数据
    watch(() => route.name, (newRoute) => {
        if (newRoute === 'project' && loginStore.loggedIn) {
            projectStore.initializeProjects()
        }
    });

    const sortedProjects = computed(()=>{
        return [...projectStore.projectList.projects].sort((a, b) => {
            const timeB = Number(new Date(b.updated_at))
            const timeA = Number(new Date(a.updated_at))
            return timeB - timeA
        })
    })

    function openAddProjectModal(){
        const modalWidth = 300;
        const modalHeight = 250;
        modalStore.createModal({
            id: 'create-project',
            title: '创建项目',
            isActive: true,
            isDraggable: true,
            isResizable: false,
            component: CreateProject,
            size: {
                width: modalWidth,
                height: modalHeight
            },
            position: {
                x: (window.innerWidth - modalWidth) / 2,
                y: (window.innerHeight - modalHeight) / 2
            }
        });
    }

    async function handleOpenExistingProject(id:number){
        const route = router.resolve({
            name: 'editor-project',
            params: { projectId: id }
        });
        window.open(route.href, '_blank');
    }

    function handleCreateNewProject(){
        openAddProjectModal();
    }

</script>

<template>
    <div class="project-container set_background_color" v-if="loginStore.loggedIn">
        <div class="projects-grid">
            <!-- Existing projects -->
            <ProjectDemoFrame
                v-for="project in sortedProjects"
                :key="project.project_id"
                :id="project.project_id"
                :title="project.project_name || `Project ${project.project_id}`"
                :thumb="(project as any).thumb"
                :created_at="project.created_at"
                :updated_at="project.updated_at"
                :handleOpenExistingProject="handleOpenExistingProject"
            />

            <!-- New project card -->
                    <ProjectDemoFrame
                        :handleCreateNewProject="handleCreateNewProject"
                        :title="'Create New'"
                        :id="0" />
        </div>
    </div>
    <Mask v-else></Mask>
</template>

<style lang="scss" scoped>
.project-container{
    width: 100%;
    padding: 14px 28px;
    box-sizing: border-box;
}
/* page background is provided by global .set_background_color */
.projects-grid{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
    gap: 20px;
    align-items: start;
    justify-items: center;
    padding: 6px;
}
.thumb-img{
    width: 100%;
    height: 100%;
    object-fit: cover;
}
.thumb-placeholder{
    width: 100%;
    height: 100%;
    display:flex;
    align-items:center;
    justify-content:center;
    font-weight:700;
    font-size:28px;
    color: #6b7f8f;
}
.title{
    color: #102335;
    font-weight:600;
}

@media (max-width: 640px){
    .projects-grid{ grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); }
}
</style>
