<script lang="ts" setup>
    import Graph from '@/components/Graph/Graph.vue';
    import { onMounted } from 'vue'
    import { useProjectStore } from '@/stores/projectStore';
    import { useModalStore } from '@/stores/modalStore';

</script>
<template>
    <div class="editor-container">
        <Graph></Graph>
    </div>
</template>
<style lang="scss" scoped>
    .editor-container{
        flex: 1;
        display: flex;
        min-height: 0;
        width: 100%;
    }
</style>