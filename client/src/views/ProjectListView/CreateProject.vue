<script lang="ts" setup>
    import {ref} from 'vue';
    import { useProjectStore } from '@/stores/projectStore';
    import { useModalStore } from '@/stores/modalStore';
    import { onUnmounted } from 'vue';

    const projectStore = useProjectStore();
    const modalStore = useModalStore();

    async function onCreateProject(){
        projectStore.createProject();
        await projectStore.initializeProjects();
        modalStore.deactivateModal('create-project');
        modalStore.destroyModal('create-project');
    }

    onUnmounted(()=>{
        projectStore.initializeProjects();
    })

</script>
<template>
    <el-form class="create-project-container">
        <el-form-item label="Project Name">
            <el-input placeholder="Enter project name" v-model="projectStore.currentProjectName"></el-input>
        </el-form-item>
        <!-- <el-form-item label="Description">
            <el-switch></el-switch>
        </el-form-item> -->
        <el-form-item>
            <el-button type="primary" @click="onCreateProject">Create Project</el-button>
        </el-form-item>
    </el-form>
</template>
<style lang="scss" scoped>
</style>