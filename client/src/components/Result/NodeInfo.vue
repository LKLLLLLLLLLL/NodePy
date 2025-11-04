<script lang="ts" setup>
    const props = defineProps<{
        data: any
    }>()
</script>
<template>
    <div class="nodeinfo-container">
        NodeInfo:{{ props.data }}
    </div>
</template>
<style lang="scss" scoped>
    .nodeinfo-container{
        height: 100%;
        width: 100%;
        color: black;
    }
</style>