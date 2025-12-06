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

    async function onCancelUpdateProject(){
        modalStore.deactivateModal('update-modal');
        modalStore.destroyModal('update-modal');
    }

    onUnmounted(()=>{
        projectStore.initializeProjects();
        userStore.initializeUserInfo();
    })

</script>
<template>
    <div class="update-project-container">
        <el-form :label-position="labelPosition">
            <el-form-item label="原项目名称">
                <div class="current-project-name">
                    {{ projectStore.toBeUpdated.project_name }}
                </div>
            </el-form-item>
            <el-form-item label="新项目名称">
                <el-input placeholder="请输入新的项目名称" v-model="projectStore.currentProjectName"></el-input>
            </el-form-item>
            <el-form-item label="公开项目">
                <el-switch v-model="projectStore.currentWhetherShow"></el-switch>
            </el-form-item>
            <el-form-item>
                <div class="form-buttons">
                    <el-button type="primary" @click="onConfirmUpdateProject">修改</el-button>
                    <el-button @click="onCancelUpdateProject">取消</el-button>
                </div>
            </el-form-item>
        </el-form>
    </div>
</template>
<style lang="scss" scoped>
    .update-project-container {
        margin-top: 20px;
    }
    
    .current-project-name {
        font-weight: bold;
        color: #409eff;
    }
    
    .form-buttons {
        display: flex;
        justify-content: center;
        gap: 15px;
    }
</style>