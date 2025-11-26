<script lang="ts" setup>
    import {ref} from 'vue';
    import { useProjectStore } from '@/stores/projectStore';
    import { useModalStore } from '@/stores/modalStore';
    import { useUserStore } from '@/stores/userStore';
    import { onUnmounted } from 'vue';

    const projectStore = useProjectStore();
    const modalStore = useModalStore();
    const userStore = useUserStore()

    async function onCreateProject(){
        const success = await projectStore.createProject();
        if (success) {
            // 创建成功后立即刷新项目列表
            await projectStore.initializeProjects();
            await userStore.initializeUserInfo();
        }
        modalStore.deactivateModal('create-project');
        modalStore.destroyModal('create-project');
    }

    onUnmounted(()=>{
        projectStore.initializeProjects();
    })

</script>
<template>
    <el-form class="create-project-container" @submit.prevent="onCreateProject">
        <el-form-item label="Project Name">
            <el-input placeholder="Enter project name" v-model="projectStore.currentProjectName" @keyup.enter="onCreateProject"></el-input>
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