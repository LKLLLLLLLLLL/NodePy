<script lang="ts" setup>
    import { useRouter } from 'vue-router';

    const router = useRouter()

    function jumpToLogin(){
        router.push({
            name: 'login'
        })
    }
</script>
<template>
    <div class="mask-container">
        <div class="mask-content">
            <div class="mask-info">
                <h1>You have not logged in yet.</h1>
                <h1>Click the Button or the Avatar to log in.</h1>
            </div>
            <div class="mask-controls">
                <el-button @click="jumpToLogin">
                    Login
                </el-button>
            </div>
        </div>
    </div>
</template>
<style lang="scss" scoped>
    .mask-container{
        display: flex;
        flex: 1;
        justify-content: center;
        align-items: center;
    }
    .mask-content{
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        width: 800px;
        height: 400px;
    }
    .mask-info{
        color: black;
        text-align: center;
    }
    .mask-controls{
        align-items: center;
        justify-content: center;
    }
</style>