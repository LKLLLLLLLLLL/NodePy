<script setup lang="ts">
    import { type ResultType } from '@/stores/resultStore';
    const props = defineProps<{
        value: ResultType
    }>()
</script>
<template>
    <div class='model-view-container'>
        {{ props.value }}
    </div>
</template>
<style scoped lang="scss">
    .model-view-container {
        display: flex;
        flex-direction: column;
        height: 100%;
        width: 100%;
        padding: 16px;
        box-sizing: border-box;
        background: #fafafa;
        border-radius: 4px;
    }
</style>
