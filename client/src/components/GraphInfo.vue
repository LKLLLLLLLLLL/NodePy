<script lang="ts" setup>
    import { DefaultService } from '@/utils/api';
    import { ref } from 'vue';

    const props = defineProps<{
        id: string
    }>()

    const default_error = 'no error'
    const default_time = 1
    const error = ref<string>(default_error)
    const lastSyncTime = ref<number>(default_time)

    async function getError(id: string){
        const now_id = Number(id);
        const project = await DefaultService.getProjectApiProjectProjectIdGet(now_id);
        await DefaultService.syncProjectApiProjectSyncPost(project);
        if(project.workflow.error_message){
            console.log(project.workflow.error_message)
            return project.workflow.error_message
        }
        else{
            return 'no error'
        }
    }

    async function getLastSyncTime(id: string){
        const now_id = Number(id);
        const project = await DefaultService.getProjectApiProjectProjectIdGet(now_id);
        await DefaultService.syncProjectApiProjectSyncPost(project);
        return 1
    }

    async function getInfo(id: string){
        error.value = await getError(id);
        lastSyncTime.value = await getLastSyncTime(id);
    }

</script>
<template>
    <div class="graphinfo-container">
        <div class="last-sync-time-container">
            LastSyncTime: {{ lastSyncTime }}
        </div>
        <div class="error-message-container">
            Error: {{ error }}
        </div>
    </div>
</template>
<style lang="scss" scoped>
    .graphinfo-container{
        display: flex;
        flex-direction: column;
        width: 100px;
        background-color: grey;
    }
</style>