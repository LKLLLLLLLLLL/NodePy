<script lang="ts" setup>
    import { useRouter } from 'vue-router';

    const props = defineProps<{
        name: string
    }>()

    const router = useRouter()

    async function handleOpenExample(){
        const route = router.resolve({
            name: 'editor-example',
            params: { exampleName: props.name }
        });
        window.open(route.href, '_blank');
    }

    function handleCopy(){

    }

</script>
<template>
    <div class="example-frame-container">
        <el-button  @click="handleOpenExample">Click me!</el-button>
    </div>
</template>
<style lang="scss" scoped>
    .example-frame-container{
        display: flex;
        justify-content: center;
        align-items: center;
    }
</style>