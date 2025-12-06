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

    function onCancel(){
        modalStore.deactivateModal('create-project');
        modalStore.destroyModal('create-project');
    }

    onUnmounted(()=>{
        projectStore.initializeProjects();
    })

</script>
<template>
     <div class="create-project-container">
        <el-form @submit.prevent="onCreateProject">
            <el-form-item label="项目名称">
                <el-input placeholder="请输入项目名称" v-model="projectStore.currentProjectName" @keyup.enter="onCreateProject"></el-input>
            </el-form-item>
            <!-- <el-form-item label="描述">
                <el-switch></el-switch>
            </el-form-item> -->
            <el-form-item>
                <div class="form-buttons">
                    <el-button type="primary" @click="onCreateProject">创建</el-button>
                    <el-button @click="onCancel">取消</el-button>
                </div>
            </el-form-item>
        </el-form>
    </div>
</template>
<style lang="scss" scoped>
    .create-project-container {
    }
    
    .form-buttons {
        display: flex;
        justify-content: center;
        gap: 15px;
    }
</style>