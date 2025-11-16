<script lang="ts" setup>
    import { useProjectStore } from '@/stores/projectStore';
    import { useModalStore } from '@/stores/modalStore';
    import { onUnmounted } from 'vue';
    const projectStore = useProjectStore();
    const modalStore = useModalStore();

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
    })

</script>
<template>
    <el-form class="delete-project-container">
        <el-form-item>
            <div>R U sure to delete this project (ID:{{ projectStore.toBeDeleted.id }})which is irreversible?</div>
        </el-form-item>
        <el-form-item>
            <el-button type="primary" @click="onEnsureDelete">Ensure</el-button>
            <el-button type="primary" @click="onCancleDelete">Cancle</el-button>
        </el-form-item>
    </el-form>
</template>
<style lang="scss" scoped>
</style>