<script lang="ts" setup>
    import { useModalStore } from '@/stores/modalStore';
    import { logout } from '@/utils/AuthHelper';
    import { ElMessage } from 'element-plus';
    import { useRouter } from 'vue-router';
    const router = useRouter()
    const modalStore = useModalStore()

    function handleLogOut(){
        logout()
        router.push({
            name: 'home'
        })
        modalStore.deactivateModal('log-out')
        modalStore.destroyModal('log-out')
        ElMessage('退出登录成功')
    }
</script>
<template>
    <div class="logout-container">
        <div>
            <p>Are you sure to log out?</p>
        </div>
        <div>
            <el-button @click="handleLogOut">Logout</el-button>
        </div>
    </div>
</template>
<style lang="scss" scoped>
    .logout-container{
        flex: 1;
        display: flex;
        flex-direction: column;
    }
</style>