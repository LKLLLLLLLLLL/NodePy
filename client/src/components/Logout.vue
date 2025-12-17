<script lang="ts" setup>
    import { useLoginStore } from '@/stores/loginStore';
    import { useModalStore } from '@/stores/modalStore';
    import { useUserStore } from '@/stores/userStore';
    import notify from './Notification/notify';
    import { useRouter } from 'vue-router';
    const router = useRouter()
    const modalStore = useModalStore()
    const loginStore = useLoginStore()
    const userStore = useUserStore()

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
        userStore.refreshUserInfo();
    }

    function onCancel(){
        modalStore.deactivateModal('logout')
        modalStore.destroyModal('logout')
    }
</script>
<template>
    <div class="logout-wrapper">
        <div class="logout-warning-container">
            <div class="warning-text">确定要退出登录吗？</div>
        </div>
        <div class="action-buttons-container">
            <button class='btn logout-btn' @click="handleLogOut">退出</button>
            <button class='btn cancel-btn' @click="onCancel">取消</button>
        </div>
    </div>
</template>
<style lang="scss" scoped>
    @use "../common/global.scss" as *;

    .logout-wrapper {
        display: flex;
        flex-direction: column;
        width: 300px;
        padding-bottom: 5px;
    }

    .logout-warning-container{
        display: flex;
        flex-direction: column;
        padding-top: 20px;
        margin-bottom: 20px;
        height: 80px;
        gap: 10px;
    }

    .warning-text{
        font-size: 16px;
        text-align: center;
    }

    .action-buttons-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        // gap: 5px;
    }

    .btn {
        width: 100%;
        font-size: 16px;
        font-weight: bold;
        border-radius: 10px;
        box-shadow: 5px 5px 50px rgba(128, 128, 128, 0.12);
        transition: transform 0.12s ease, box-shadow 0.12s ease, background-color 0.12s ease;
    }

    .cancel-btn {
        margin-top: 10px;
        margin-left: 0;
        @include cancel-button-style;
    }

    .cancel-btn:hover {
        @include cancel-button-hover-style;
    }

    .logout-btn {
        width: 100%;
        background-color: #ff4d4f;
        color: white;
        border: none;
    }

    .logout-btn:hover {
        background-color: $error-message-color;
    }
</style>