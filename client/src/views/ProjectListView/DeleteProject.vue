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
    <el-form class="delete-project-container">
        <el-form-item>
            <div>确定删除此项目吗？ (项目名称:{{ projectStore.projectIdToNameMap.get(projectStore.toBeDeleted.id) }})<br></br>该操作不可逆。</div>
        </el-form-item>
        <el-form-item>
            <el-button type="primary" @click="onEnsureDelete">删除</el-button>
            <el-button type="plain" @click="onCancleDelete">取消</el-button>
        </el-form-item>
    </el-form>
</template>
<style lang="scss" scoped>
    .delete-project-container {
    }
</style>