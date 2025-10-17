<script lang="ts" setup>

    const props = defineProps<{
        data: any
    }>()
</script>
<template>
    <div class = 'value-view-container'>
        ValueView
        {{ data }}
    </div>
</template>
<style scoped lang="scss">
</style>