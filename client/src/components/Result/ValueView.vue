<script lang="ts" setup>
    import { onMounted } from 'vue';
    const props = defineProps<{
        value: any
    }>()

</script>
<template>
    <div class = 'value-view-container'>
        ValueView:{{ value }}
    </div>
</template>
<style scoped lang="scss">
    .value-view-container{
        color: black;
    }
</style>