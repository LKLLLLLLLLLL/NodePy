<script lang="ts" setup>
    import ProjectDemoFrame from '@/components/ProjectDemoFrame.vue';
    import AddProject from './AddProject.vue';
    import { ref,onMounted } from 'vue';
    import { DefaultService } from '../utils/api/services/DefaultService';
    import { useModalStore } from '@/stores/modalStore';
    import { useProjectStore } from '@/stores/projectStore';
    import { useRouter } from 'vue-router';

    const modalStore = useModalStore();
    const projectStore = useProjectStore();
    const router = useRouter()

    onMounted(()=>{
        projectStore.initializeProjects()
    });

    function openAddProjectModal(){
        const modalWidth = 400;
        const modalHeight = 600;
        modalStore.createModal({
            id: 'add-project',
            title: 'Create New Project',
            isActive: true,
            isDraggable: true,
            isResizable: false,
            component: AddProject,
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
        const success = await projectStore.openProject(id);
        if(success){
            const route = router.resolve({
                name: 'editor',
                params: { projectId: id }
            });
        window.open(route.href, '_blank');
    }
}

    function handleCreateNewProject(){
        console.log("Adding new project...");
        openAddProjectModal();
    }


</script>

<template>
    <div class="program-container">
        <el-row :gutter="20" class="demo-row">
            <el-col 
                :span="6"
                v-for="project in projectStore.projectList.projects"
                :key="project.project_id"
                class="demo-column"
            >
                <ProjectDemoFrame
                    :id="project.project_id"
                    @click="()=>handleOpenExistingProject(project.project_id)"
                >
                    <template #picture>
                        picture
                    </template>
                    <template #info>
                        {{ project.project_id }}
                    </template>
                </ProjectDemoFrame>
            </el-col>
            <el-col :span="6" class="demo-column">
                <ProjectDemoFrame
                    :handleCreateNewProject="handleCreateNewProject"
                    :id="114514"
                >
                </ProjectDemoFrame>
            </el-col>
        </el-row>
    </div>
</template>

<style lang="scss" scoped>
.program-container{
    min-height: 0;
    width: 100%;
    gap: 40px;
    margin: 20px 20px 20px 20px;
    flex-shrink: 0;
}
.demo-column{
    padding: 30px;
}
.demo-row{
    width: 100%;
}
</style>