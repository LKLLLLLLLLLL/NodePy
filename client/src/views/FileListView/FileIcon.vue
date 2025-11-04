<script lang="ts" setup>
    import { computed } from 'vue';
    import { FileItem } from '@/utils/api';

    const props = defineProps<{
        format: FileItem.format;
    }>()

    const iconPath = {
        [FileItem.format.CSV]: `${import.meta.env.BASE_URL}CSV.png`,
        [FileItem.format.JPG]: `${import.meta.env.BASE_URL}JPG.png`,
        [FileItem.format.PDF]: `${import.meta.env.BASE_URL}PDF.png`,
        [FileItem.format.PNG]: `${import.meta.env.BASE_URL}PNG.png`
    };

    const currentIconPath = computed(()=>iconPath[props.format]);
</script>
<template>
    <div class="fileicon-container">
        <img class='fileicon' :src="currentIconPath"></img>
    </div>
</template>
<style lang="scss" scoped>
    @use '../../common/global.scss' as *;
    
    .fileicon-container{
        width: 50px;
        height: 50px;
        display: flex;
        align-items: center;
        justify-content: center;
        background-color: $mix-background-color;
        border-radius: 8px;
        padding: 4px;
    }
    
    .fileicon{
        width: 100%;
        height: 100%;
        object-fit: contain;
        border-radius: 6px;
    }
</style>