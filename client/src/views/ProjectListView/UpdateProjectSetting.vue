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
            <!-- <el-form-item label="原项目名称">
                <div class="current-project-name">
                    {{ projectStore.toBeUpdated.project_name }}
                </div>
            </el-form-item> -->
            <el-form-item label="新项目名称">
                <input class="name-input" placeholder="请输入新的项目名称" v-model="projectStore.currentProjectName"></input>
            </el-form-item>
        </el-form>
        <div class="checkbox-wrapper">
            <span class="checkbox-label">设为公开项目</span>
            <label class="checkbox-container">
                <input 
                    type="checkbox" 
                    class="custom-checkbox" 
                    v-model="projectStore.currentWhetherShow"
                />
                <span class="checkmark"></span>
            </label>
        </div>
        <div class="button-container">
            <button @click="onConfirmUpdateProject" class="confirm-button">修改</button>
            <button @click="onCancelUpdateProject" class="cancel-button">取消</button>
        </div>
    </div>
</template>
<style lang="scss" scoped>
    @use "../../common/global.scss" as *;
    .update-project-container {
        display: flex;
        flex-direction: column;
        width: 300px;
        padding-bottom: 5px;
    }
    
    .current-project-name {
        font-weight: bold;
        color: #409eff;
    }
    
    .button-container {
        display: flex;
        flex-direction: column;
        width: 100%;
        gap: 10px;
    }

    .confirm-button{
        @include confirm-button-style;
    }

    .cancel-button{
        @include cancel-button-style;
    }

    .confirm-button:hover{
        @include confirm-button-hover-style;
    }

    .cancel-button:hover{
        @include cancel-button-hover-style;
    }

    .name-input{
        @include input-style;
    }

    .name-input:focus{
        @include input-focus-style;
    }

    /* 自定义勾选框样式 */
    .checkbox-wrapper {
        display: flex;
        align-items: center;
        justify-content: flex-start;
        margin: 15px 0;
        padding-bottom: 20px;
    }

    .checkbox-label {
        margin-right: 12px;
        font-size: 14px;
        color: #606266;
    }

    .checkbox-container {
        display: flex;
        align-items: center;
        cursor: pointer;
        position: relative;
        user-select: none;
    }

    .custom-checkbox {
        position: absolute;
        opacity: 0;
        cursor: pointer;
        height: 0;
        width: 0;
    }

    .checkmark {
        height: 20px;
        width: 20px;
        background-color: #fff;
        border: 2px solid #dcdfe6;
        border-radius: 4px;
        transition: all 0.3s ease;
        position: relative;
    }

    .checkbox-container:hover .checkmark {
        border-color: $stress-color;
    }

    .custom-checkbox:checked ~ .checkmark {
        background-color: $stress-color;
        border-color: $stress-color;
    }

    .checkmark:after {
        content: "";
        position: absolute;
        display: none;
    }

    .custom-checkbox:checked ~ .checkmark:after {
        display: block;
        left: 6px;
        top: 3px;
        width: 5px;
        height: 9px;
        border: solid white;
        border-width: 0 2px 2px 0;
        transform: rotate(45deg);
    }
</style>