<script lang="ts" setup>
    import { usePageStore } from '@/stores/pageStore';
    import { onMounted } from 'vue';

    const pageStore = usePageStore()

    onMounted(()=>{
        pageStore.setCurrentPage('Visitor')
    })
</script>
<template>
    <div>
        Visitor View
    </div>
</template>
<style lang="scss" scoped>
</style>