<script lang="ts" setup>
    import { useLoginStore } from '@/stores/loginStore';
    import { usePageStore } from '@/stores/pageStore';
    import { ref, onMounted } from 'vue';
    import { useRouter } from 'vue-router';

    const pageStore = usePageStore()
    const loginStore = useLoginStore()

    const router = useRouter()

    onMounted(()=>{
        loginStore.checkAuthStatus()
        pageStore.setCurrentPage('Home')
    })

    function jumpToLogin(){
        router.push({
            name: 'login'
        })
    }
</script>
<template>
    <div class="home-container">
        <div class="home-content">
            <div class="home-info">
                <h1>Welcome to NodePy!</h1>
            </div>
            <div class="home-controls" v-if="!loginStore.loggedIn">
                <el-button @click="jumpToLogin">Login</el-button>
            </div>
        </div>
    </div>
</template>
<style lang="scss" scoped>
    .home-container{
        flex: 1;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .home-content{
        width: 800px;
        height:800px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    }
    .home-controls{
        display: flex;
        align-items: center;
        justify-content: center;
    }
</style>