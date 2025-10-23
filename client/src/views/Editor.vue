<script lang="ts" setup>
    import Graph from '@/components/Graph.vue';
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