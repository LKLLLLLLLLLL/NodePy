<script lang="ts" setup>
    import { computed } from 'vue';
    import { useFileStore } from '@/stores/fileStore';
    import type { FileItem } from '@/utils/api';

    const fileStore = useFileStore();

    const props = defineProps<{
        file: FileItem
    }>()

    const content =computed(()=>fileStore.currentContent)

</script>
<template>
    <div class="csv">

    </div>
</template>
<style lang="scss" scoped>

</style>