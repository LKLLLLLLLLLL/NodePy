<script lang="ts" setup>
    import { useRouter } from 'vue-router'
    import { ref, computed, onMounted } from 'vue';
    import AuthenticatedServiceFactory from '@/utils/AuthenticatedServiceFactory';
    import { useLoginStore } from '@/stores/loginStore'
    import Mask from '@/views/Mask.vue'
    import ExampleDemoFrame from './ExampleDemoFrame.vue';
    import type { ExploreList, ExploreListItem } from '@/utils/api';

    const loginStore = useLoginStore();
    const router = useRouter()

    const default_examples: ExploreList = {
        projects: []
    }
    const authService = AuthenticatedServiceFactory.getService()
    const examples = ref<ExploreList>(default_examples)

    onMounted(async ()=>{
        loginStore.checkAuthStatus();
        if(loginStore.loggedIn){
            examples.value = await authService.getExploreProjectsApiExploreExploreProjectsGet();
        }
        else{
            router.replace({
                name: 'login'
            })
        }
    })

    const default_name: string = 'default_name'

</script>
<template>
    <div class="example-container" v-if="loginStore.loggedIn">
        <div v-if="examples.projects.length === 0" class="no-example-container">
            <div class="no-example-info">暂无示例项目</div>
        </div>
        <div v-else class="examples-grid">
            <ExampleDemoFrame
                v-for="example in examples.projects"
                :key="example.project_id"
                :item="example"
            ></ExampleDemoFrame>
        </div>
    </div>
    <Mask v-else></Mask>
</template>
<style lang="scss" scoped>
    .example-container{
        display: flex;
        flex: 1;
        flex-direction: column;
        padding: 14px 28px;
        box-sizing: border-box;
    }
    .no-example-container {
        flex: 1;
        display: flex;
        justify-content: center;
        align-items: center;
    }
    .no-example-info{
        text-align: center;
        color: #909399;
        font-size: 40px;
    }
    .examples-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
        gap: 20px;
        align-items: start;
        justify-items: center;
        padding: 6px;
    }
</style>
