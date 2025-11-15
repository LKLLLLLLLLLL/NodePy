<script lang="ts" setup>
    import {ref} from 'vue';
    import { useProjectStore } from '@/stores/projectStore';
    import { useModalStore } from '@/stores/modalStore';
    import { onUnmounted } from 'vue';

    const projectStore = useProjectStore();
    const modalStore = useModalStore();
    const labelPosition = ref<string>('top')

    async function onConfirmUpdateProject(){
        await projectStore.updateProjectSetting(projectStore.currentProjectId)
        await projectStore.initializeProjects();
        modalStore.deactivateModal('update-modal');
        modalStore.destroyModal('update-modal');
    }

    async function onCancleUpdateProject(){
        await projectStore.initializeProjects();
        modalStore.deactivateModal('update-modal');
        modalStore.destroyModal('update-modal');
    }

    onUnmounted(()=>{
        projectStore.initializeProjects();
    })

</script>
<template>
    <el-form class="update-project-container" :label-position="labelPosition">
        <el-form-item>
            原项目名称：{{ projectStore.currentProjectName }}
            原项目ID: {{ projectStore.currentProjectId }}
        </el-form-item>
        <el-form-item label="ProjectName">
            <el-input placeholder="Enter new project name" v-model="projectStore.toBeUpdated.project_name"></el-input>
        </el-form-item>
        <el-form-item label="Accessible To the Public">
            <el-switch v-model="projectStore.toBeUpdated.show_to_explore"></el-switch>
        </el-form-item>
        <el-form-item>
            <el-button type="primary" @click="onConfirmUpdateProject">Confirm</el-button>
            <el-button type="primary" @click="onCancleUpdateProject">Cancle</el-button>
        </el-form-item>
    </el-form>
</template>
<style lang="scss" scoped>
</style>