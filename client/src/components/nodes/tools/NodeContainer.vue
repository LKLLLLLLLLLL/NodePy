<template>
    <div class="NodeContainerLayout" ref="NodeContainerRef"></div>
</template>

<script lang="ts" setup>
</script>

<style lang="scss" scoped>
    .NodeContainerLayout {
        min-height: 500px;
        min-width: 1000px;
        background: rgba(148, 193, 252, 0.2);
    }
</style>

<style lang="scss">
    .vue-flow__node-NodeContainer {
        pointer-events: none !important;
        z-index: -1 !important;
    }
</style>