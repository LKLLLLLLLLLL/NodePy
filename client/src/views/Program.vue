<script lang="ts" setup>
    import ProjectDemoFrame from '@/components/ProjectDemoFrame.vue';
    import AddProject from './AddProject.vue';
    import { ref } from 'vue';
    import { DefaultService } from '../utils/api/services/DefaultService';
    import { useModalStore } from '@/stores/modalStore';
    import { useProjectStore } from '@/stores/projectStore';

    const modalStore = useModalStore();
    const projectStore = useProjectStore();

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

    function handleClick(){
        openAddProjectModal();
        // handleAdd();
    }

    function handleAdd(){
        console.log("Adding new project...");
    }

    const ids = ['1'];

</script>

<template>
    <div class="program-container">
        <el-row :gutter="20" class="demo-row">
            <el-col 
                :span="6"
                v-for="id in ids"
                :key="id"
                class="demo-column"
            >
                <ProjectDemoFrame 
                    :handleClick="handleClick"
                    :id="id"
                >
                </ProjectDemoFrame>
            </el-col>
            <el-col :span="6" class="demo-column">
                <ProjectDemoFrame :handleClick="handleClick"></ProjectDemoFrame>
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