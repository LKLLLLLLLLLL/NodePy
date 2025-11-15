<script lang="ts" setup>
    import { ref, onMounted, computed } from 'vue';
    import { useRouter } from 'vue-router';
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
    });

    const sortedProjects = computed(()=>{
        return [...projectStore.projectList.projects].sort((a, b) => {
            const timeB = Number(new Date(b.updated_at))
            const timeA = Number(new Date(a.updated_at))
            return timeB - timeA
        })
    })

    function openAddProjectModal(){
        const modalWidth = 400;
        const modalHeight = 600;
        modalStore.createModal({
            id: 'create-project',
            title: 'Create New Project',
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
        console.log('Opening existing project...')
        const route = router.resolve({
            name: 'editor-project',
            params: { projectId: id }
        });
        window.open(route.href, '_blank');
    }

    function handleCreateNewProject(){
        console.log("Adding new project...");
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
    padding: 28px;
    box-sizing: border-box;
}
/* page background is provided by global .set_background_color */
.projects-grid{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
    gap: 20px;
    align-items: start;
    justify-items: center;
    padding: 20px 6px;
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
