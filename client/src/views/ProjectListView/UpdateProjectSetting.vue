<script lang="ts" setup>
    import {ref} from 'vue';
    import { useProjectStore } from '@/stores/projectStore';
    import { useModalStore } from '@/stores/modalStore';
    import { useUserStore } from '@/stores/userStore';
    import { onMounted, onUnmounted } from 'vue';

    const projectStore = useProjectStore();
    const modalStore = useModalStore();
    const userStore = useUserStore()
    const labelPosition = ref<string>('top')

    onMounted( async ()=>{
        await projectStore.getProjectSettings(projectStore.currentProjectId)
    })

    async function onConfirmUpdateProject(){
        await projectStore.updateProjectSetting(projectStore.currentProjectId)
        projectStore.initializeProjects()
        modalStore.deactivateModal('update-modal');
        modalStore.destroyModal('update-modal');
    }

    async function onCancleUpdateProject(){
        modalStore.deactivateModal('update-modal');
        modalStore.destroyModal('update-modal');
    }

    onUnmounted(()=>{
        projectStore.initializeProjects();
        userStore.initializeUserInfo();
    })

</script>
<template>
    <el-form class="update-project-container" :label-position="labelPosition">
        <el-form-item>
            原项目名称：{{ projectStore.toBeUpdated.project_name }}
        </el-form-item>
        <el-form-item label="ProjectName">
            <el-input placeholder="Enter new project name" v-model="projectStore.currentProjectName"></el-input>
        </el-form-item>
        <el-form-item label="Accessible To the Public">
            <el-switch v-model="projectStore.currentWhetherShow"></el-switch>
        </el-form-item>
        <el-form-item>
            <el-button type="primary" @click="onConfirmUpdateProject">Confirm</el-button>
            <el-button type="primary" @click="onCancleUpdateProject">Cancle</el-button>
        </el-form-item>
    </el-form>
</template>
<style lang="scss" scoped>
</style>