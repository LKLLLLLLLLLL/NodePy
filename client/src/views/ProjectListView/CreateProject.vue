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
        <el-form class="create-project-form" label-position="top" @submit.prevent="onCreateProject">
            <el-form-item label="项目名称">
                <input class="name-input" placeholder="请输入项目名称" v-model="projectStore.currentProjectName" @keyup.enter="onCreateProject"></input>
            </el-form-item>
            <!-- <el-form-item label="描述">
                <el-switch></el-switch>
            </el-form-item> -->
        </el-form>
        <div class="button-container">
            <button class='button confirm-button' @click="onCreateProject">创建</button>
            <button class='button cancel' @click="onCancel">取消</button>
        </div>
    </div>
</template>
<style lang="scss" scoped>

    @use "../../common/global.scss" as *;

    .create-project-container {
        display: flex;
        flex-direction: column;
        width: 300px;
        padding-bottom: 5px;
    }

    .create-project-form{
        margin-bottom: 20px;
    }

    .button-container{
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        // gap: 5px;
    }
    
    .name-input {
        @include input-style;
    }

    .name-input:focus {
        @include input-focus-style;
    }

    .button {
        width: 100%;
    }

    .button.cancel{
        margin-top: 10px;
        margin-left: 0;
        @include cancel-button-style;
    }

    .button.cancel:hover{
        @include cancel-button-hover-style;
    }

    .button.confirm-button{
        width: 100%;
        @include confirm-button-style;
    }

    .button.confirm-button:hover{
        @include confirm-button-hover-style;
    }
</style>