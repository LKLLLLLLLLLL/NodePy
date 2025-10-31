<script lang="ts" setup>
    import {ref} from 'vue';
    import { useProjectStore } from '@/stores/projectStore';
    import { useModalStore } from '@/stores/modalStore';
    import { onUnmounted } from 'vue';

    const projectStore = useProjectStore();
    const modalStore = useModalStore();

    async function onRenameProject(){
        projectStore.renameProject(projectStore.toBeRenamed.id,projectStore.currentProjectName)
        await projectStore.initializeProjects();
        modalStore.deactivateModal('rename-modal');
        modalStore.destroyModal('rename-modal');
    }

    async function onCancleRenameProject(){
        await projectStore.initializeProjects();
        modalStore.deactivateModal('rename-modal');
        modalStore.destroyModal('rename-modal');
    }

    onUnmounted(()=>{
        projectStore.initializeProjects();
    })

</script>
<template>
    <el-form class="create-project-container">
        <el-form-item>
            原项目名称：{{ projectStore.toBeRenamed.name }}
            原项目ID: {{ projectStore.toBeRenamed.id }}
        </el-form-item>
        <el-form-item label="Project Name">
            <el-input placeholder="Enter new project name" v-model="projectStore.currentProjectName"></el-input>
        </el-form-item>
        <!-- <el-form-item label="Description">
            <el-switch></el-switch>
        </el-form-item> -->
        <el-form-item>
            <el-button type="primary" @click="onRenameProject">Rename Project</el-button>
            <el-button type="primary" @click="onCancleRenameProject">Cancle</el-button>
        </el-form-item>
    </el-form>
</template>
<style lang="scss" scoped>
</style>