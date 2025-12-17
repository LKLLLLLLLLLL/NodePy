<script lang="ts" setup>
    import { useProjectStore } from '@/stores/projectStore';
    import { useModalStore } from '@/stores/modalStore';
    import { useUserStore } from '@/stores/userStore';
    import { onUnmounted } from 'vue';
    const projectStore = useProjectStore();
    const modalStore = useModalStore();
    const userStore = useUserStore()

    async function onEnsureDelete(){
        await projectStore.deleteProject(projectStore.toBeDeleted.id);
        modalStore.deactivateModal('delete-modal');
        modalStore.destroyModal('delete-modal');
    }

    async function onCancleDelete(){
        modalStore.deactivateModal('delete-modal');
        modalStore.destroyModal('delete-modal');
    }

    onUnmounted(()=>{
        projectStore.initializeProjects();
        userStore.initializeUserInfo();
    })

</script>
<template>
    <div class="delete-project-container">
        <div class="delete-warning-container">
            <div class="warning-info">确定删除项目 {{ projectStore.projectIdToNameMap.get(projectStore.toBeDeleted.id) }} 吗? <br></br>此操作不可逆。</div>
            <!-- <div class="warning-tip"></div> -->
        </div>
        <div class="button-container">
            <button class='button delete-button' @click="onEnsureDelete">删除</button>
            <button class='button cancel' @click="onCancleDelete">取消</button>
        </div>
    </div>
</template>
<style lang="scss" scoped>
    @use "../../common/global.scss" as *;

    .delete-project-container {
        display: flex;
        flex-direction: column;
        width: 300px;
        padding-bottom: 5px;
    }

    .delete-warning-container{
        display: flex;
        flex-direction: column;
        padding-top: 20px;
        margin-bottom: 20px;
        height: 80px;
        gap: 10px;
    }

    .warning-info{
        font-size: 16px;
    }

    .warning-tip{
        font-size: 14px;
        color: #ff4d4f;
    }

    .button-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        gap: 5px;
    }

    .delete-warning {
        font-size: 14px;
        text-align: center;
        padding: 10px 0;
    }

    .button {
        width: 100%;
    }

    .button.cancel {
        margin-top: 10px;
        margin-left: 0;
        @include cancel-button-style;
    }

    .button.cancel:hover {
        @include cancel-button-hover-style;
    }

    .button.delete-button {
        width: 100%;
        @include delete-button-style;
    }

    .button.delete-button:hover {
        @include delete-button-hover-style;
    }
</style>