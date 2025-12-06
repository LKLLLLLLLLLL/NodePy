<script lang="ts" setup>
    import { useLoginStore } from '@/stores/loginStore';
    import { useModalStore } from '@/stores/modalStore';
    import notify from './Notification/notify';
    import { useRouter } from 'vue-router';
    const router = useRouter()
    const modalStore = useModalStore()
    const loginStore = useLoginStore()

    function handleLogOut(){
        loginStore.logout()
        router.push({
            name: 'home'
        })
        modalStore.deactivateModal('logout')
        modalStore.destroyModal('logout')
        notify({
            message: '退出登录成功',
            type: 'success'
        })
    }

    function onCancel(){
        modalStore.deactivateModal('logout')
        modalStore.destroyModal('logout')
    }
</script>
<template>
    <div class="logout-container">
        <div class="logout-message">
            <p>确定要退出登录吗？</p>
        </div>
        <div class="logout-buttons">
            <el-button type="primary" @click="handleLogOut">退出</el-button>
            <el-button @click="onCancel">取消</el-button>
        </div>
    </div>
</template>
<style lang="scss" scoped>
    .logout-container{
        display: flex;
        flex-direction: column;
        width: 100%;
        height: 100%;
        padding: 20px;
    }
    
    .logout-message {
        flex: 1;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 20px;
    }
    
    .logout-buttons {
        display: flex;
        justify-content: center;
        gap: 15px;
    }
</style>