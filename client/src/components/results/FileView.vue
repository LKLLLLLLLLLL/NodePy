<script lang="ts" setup>
    const props = defineProps<{
        value: any
    }>()
</script>
<template>
    <div class = 'file-view-container'>
        FileView:{{props.value}}
    </div>
</template>
<style scoped lang="scss">
</style>