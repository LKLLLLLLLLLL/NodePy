<script lang="ts" setup>
    import { onMounted } from 'vue';
    const props = defineProps<{
        value: any
    }>()

    onMounted(()=>{
        console.log(props.value)
    })
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